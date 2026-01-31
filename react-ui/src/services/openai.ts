import OpenAI from 'openai';

interface CachedResponse {
  response: string;
  timestamp: number;
}

interface WebSearchResult {
  response: string;
  sources: string[];
}

class OpenAIService {
  private client: OpenAI | null = null;
  private apiKey: string | null = null;
  private readonly CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours
  private readonly CACHE_KEY = 'scooter_chat_cache';
  private readonly USAGE_KEY = 'openai_usage_count';

  setApiKey(apiKey: string) {
    this.apiKey = apiKey;
    this.client = new OpenAI({
      apiKey,
      dangerouslyAllowBrowser: true
    });
  }

  private getCacheKey(query: string): string {
    return `${this.CACHE_KEY}_${btoa(query.toLowerCase().trim())}`;
  }

  private getFromCache(query: string): string | null {
    try {
      const cacheKey = this.getCacheKey(query);
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        const parsedCache: CachedResponse = JSON.parse(cached);
        if (Date.now() - parsedCache.timestamp < this.CACHE_DURATION) {
          return parsedCache.response;
        }
        localStorage.removeItem(cacheKey);
      }
    } catch (error) {
      console.warn('Cache read error:', error);
    }
    return null;
  }

  private saveToCache(query: string, response: string) {
    try {
      const cacheKey = this.getCacheKey(query);
      const cacheData: CachedResponse = {
        response,
        timestamp: Date.now()
      };
      localStorage.setItem(cacheKey, JSON.stringify(cacheData));
    } catch (error) {
      console.warn('Cache save error:', error);
    }
  }

  private incrementUsage() {
    try {
      const current = parseInt(localStorage.getItem(this.USAGE_KEY) || '0');
      localStorage.setItem(this.USAGE_KEY, (current + 1).toString());
    } catch (error) {
      console.warn('Usage tracking error:', error);
    }
  }

  getUsageCount(): number {
    try {
      return parseInt(localStorage.getItem(this.USAGE_KEY) || '0');
    } catch {
      return 0;
    }
  }

  private isScooterRelated(query: string): boolean {
    const scooterKeywords = [
      'scooter', 'battery', 'charge', 'ride', 'payment', 'booking', 'speed',
      'maintenance', 'repair', 'helmet', 'safety', 'unlock', 'lock', 'trip',
      'range', 'motor', 'brake', 'wheel', 'tire', 'account', 'app', 'qr code',
      'ola', 'ather', 'tvs', 'bajaj', 'chetak', 'iqube', 'service', 'center'
    ];
    
    const lowercaseQuery = query.toLowerCase();
    return scooterKeywords.some(keyword => lowercaseQuery.includes(keyword));
  }

  // Check if query needs web search (time-sensitive information)
  needsWebSearch(query: string): boolean {
    const webSearchKeywords = [
      'current', 'latest', 'recent', 'new', 'update', 'today', 'now',
      'price', 'cost', 'booking', 'service center', 'contact', 'phone',
      'location', 'address', 'nearby', 'open', 'closed', 'hours',
      'availability', 'stock', 'delivery', 'launch', 'release',
      'offer', 'discount', 'promotion', 'deals'
    ];
    
    const lowercaseQuery = query.toLowerCase();
    return webSearchKeywords.some(keyword => lowercaseQuery.includes(keyword));
  }

  // Enhanced web search using OpenAI with web search instructions
  async getWebSearchResponse(userQuery: string): Promise<WebSearchResult> {
    // Check if API key is set
    if (!this.client || !this.apiKey) {
      throw new Error('OpenAI API key not configured');
    }

    try {
      const completion = await this.client.chat.completions.create({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: `You are an expert electric scooter support assistant with access to current information. When answering queries that require real-time or current information, provide the most accurate response possible based on your knowledge and clearly indicate when information might need verification.

Your expertise includes current information about:
- Electric scooter service centers and contact information
- Current pricing and offers for OLA, Ather, TVS, Bajaj scooters
- Service schedules and maintenance requirements
- Booking procedures and app functionality
- Current safety regulations and guidelines
- Recent updates to electric scooter features

For queries requiring current information:
1. Provide the most accurate information available
2. Include relevant contact details when appropriate
3. Suggest verification steps if needed
4. Format responses clearly with bullet points

Always specify if information might need real-time verification and provide official sources when possible.`
          },
          {
            role: 'user',
            content: `Please provide current information about: ${userQuery}

Include relevant contact details, pricing (if applicable), and any official sources or verification steps needed.`
          }
        ],
        max_tokens: 600,
        temperature: 0.5,
        top_p: 0.9,
        frequency_penalty: 0.1,
        presence_penalty: 0.1
      });

      const response = completion.choices[0]?.message?.content || "I'm sorry, I couldn't generate a response. Please try again.";
      
      // Extract potential sources from the response (simulate web sources)
      const sources = this.extractSources(response);
      
      // Increment usage
      this.incrementUsage();
      
      return {
        response: response + "\n\n💡 **Note:** This information is based on available knowledge. For the most current details, please verify with official sources.",
        sources
      };
    } catch (error) {
      console.error('OpenAI web search error:', error);
      throw error;
    }
  }

  // Extract or simulate sources from response
  private extractSources(response: string): string[] {
    const sources: string[] = [];
    
    // Common official sources for electric scooter information
    if (response.toLowerCase().includes('ola')) {
      sources.push('https://olaelectric.com/');
    }
    if (response.toLowerCase().includes('ather')) {
      sources.push('https://atherenergy.com/');
    }
    if (response.toLowerCase().includes('tvs')) {
      sources.push('https://www.tvsmotor.com/tvs-iqube');
    }
    if (response.toLowerCase().includes('bajaj')) {
      sources.push('https://www.bajajchetak.com/');
    }
    if (response.toLowerCase().includes('service')) {
      sources.push('Official service center locator');
    }
    
    return sources;
  }

  async getResponse(userQuery: string, retryCount = 0): Promise<string> {
    // Check cache first for performance
    const cachedResponse = this.getFromCache(userQuery);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Check if API key is set
    if (!this.client || !this.apiKey) {
      throw new Error('OpenAI API key not configured');
    }

    try {
      const completion = await this.client.chat.completions.create({
        model: 'gpt-4',
        messages: [
          {
            role: 'system',
            content: `You are an expert electric scooter support assistant powered by ChatGPT 4.0. You have comprehensive knowledge about all major electric scooter brands including OLA S1/S1 Pro, Ather 450X/450 Plus, TVS iQube, Bajaj Chetak, and others.

Your expertise includes:
- Battery management, charging cycles, range optimization
- Service schedules and maintenance requirements for each brand
- Troubleshooting common issues (won't start, charging problems, app connectivity)
- Safety guidelines and traffic regulations
- Payment systems, wallet management, and trip billing
- Account management and app functionality
- Booking rides, QR code scanning, and trip management
- Performance optimization and riding tips

For electric scooter related questions, provide detailed, accurate, and helpful responses. Include specific information about service intervals, contact information, and troubleshooting steps when relevant.

If asked about non-scooter topics, politely redirect: "I'm specialized in electric scooter support. Please ask me about battery, rides, payments, maintenance, safety, or account issues."

Format your responses clearly with bullet points or numbered lists when appropriate. Be concise but thorough.`
          },
          {
            role: 'user',
            content: userQuery
          }
        ],
        max_tokens: 500,
        temperature: 0.7,
        top_p: 0.9,
        frequency_penalty: 0.1,
        presence_penalty: 0.1
      });

      const response = completion.choices[0]?.message?.content || "I'm sorry, I couldn't generate a response. Please try again.";
      
      // Cache the response and increment usage
      this.saveToCache(userQuery, response);
      this.incrementUsage();
      
      return response;
    } catch (error) {
      console.error('OpenAI API error:', error);
      
      // Retry once on failure
      if (retryCount < 1) {
        return this.getResponse(userQuery, retryCount + 1);
      }
      
      throw error;
    }
  }

  // Method to get enhanced response with context
  async getEnhancedResponse(userQuery: string, conversationHistory: Array<{role: 'user' | 'assistant' | 'system', content: string}> = []): Promise<string> {
    // Check cache first for performance
    const cachedResponse = this.getFromCache(userQuery);
    if (cachedResponse && conversationHistory.length === 0) {
      return cachedResponse;
    }

    // Check if API key is set
    if (!this.client || !this.apiKey) {
      throw new Error('OpenAI API key not configured');
    }

    try {
      const messages = [
        {
          role: 'system' as const,
          content: `You are an expert electric scooter support assistant powered by ChatGPT 4.0. You have comprehensive knowledge about all major electric scooter brands including OLA S1/S1 Pro, Ather 450X/450 Plus, TVS iQube, Bajaj Chetak, and others.

Your expertise includes:
- Battery management, charging cycles, range optimization
- Service schedules and maintenance requirements for each brand
- Troubleshooting common issues (won't start, charging problems, app connectivity)
- Safety guidelines and traffic regulations
- Payment systems, wallet management, and trip billing
- Account management and app functionality
- Booking rides, QR code scanning, and trip management
- Performance optimization and riding tips

For electric scooter related questions, provide detailed, accurate, and helpful responses. Include specific information about service intervals, contact information, and troubleshooting steps when relevant.

If asked about non-scooter topics, politely redirect: "I'm specialized in electric scooter support. Please ask me about battery, rides, payments, maintenance, safety, or account issues."

Format your responses clearly with bullet points or numbered lists when appropriate. Be concise but thorough.`
        },
        ...conversationHistory.map(msg => ({
          role: msg.role as 'user' | 'assistant' | 'system',
          content: msg.content
        })),
        {
          role: 'user' as const,
          content: userQuery
        }
      ];

      const completion = await this.client.chat.completions.create({
        model: 'gpt-4',
        messages: messages,
        max_tokens: 500,
        temperature: 0.7,
        top_p: 0.9,
        frequency_penalty: 0.1,
        presence_penalty: 0.1
      });

      const response = completion.choices[0]?.message?.content || "I'm sorry, I couldn't generate a response. Please try again.";
      
      // Cache the response and increment usage (only for single queries)
      if (conversationHistory.length === 0) {
        this.saveToCache(userQuery, response);
      }
      this.incrementUsage();
      
      return response;
    } catch (error) {
      console.error('OpenAI API error:', error);
      throw error;
    }
  }
}

export const openAIService = new OpenAIService();