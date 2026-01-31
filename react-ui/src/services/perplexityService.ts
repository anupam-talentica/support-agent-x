interface PerplexityResponse {
  response: string;
  sources?: string[];
  timestamp: number;
}

interface CachedResponse {
  response: string;
  sources?: string[];
  timestamp: number;
}

class PerplexityService {
  private apiKey: string | null = null;
  private readonly CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours
  private readonly CACHE_KEY = 'perplexity_search_cache';
  private readonly USAGE_KEY = 'perplexity_usage_count';

  setApiKey(apiKey: string) {
    this.apiKey = apiKey;
  }

  private getCacheKey(query: string): string {
    return `${this.CACHE_KEY}_${btoa(query.toLowerCase().trim())}`;
  }

  private getFromCache(query: string): PerplexityResponse | null {
    try {
      const cacheKey = this.getCacheKey(query);
      const cached = localStorage.getItem(cacheKey);
      if (cached) {
        const parsedCache: CachedResponse = JSON.parse(cached);
        if (Date.now() - parsedCache.timestamp < this.CACHE_DURATION) {
          return {
            response: parsedCache.response,
            sources: parsedCache.sources,
            timestamp: parsedCache.timestamp
          };
        }
        localStorage.removeItem(cacheKey);
      }
    } catch (error) {
      console.warn('Perplexity cache read error:', error);
    }
    return null;
  }

  private saveToCache(query: string, response: string, sources?: string[]) {
    try {
      const cacheKey = this.getCacheKey(query);
      const cacheData: CachedResponse = {
        response,
        sources,
        timestamp: Date.now()
      };
      localStorage.setItem(cacheKey, JSON.stringify(cacheData));
    } catch (error) {
      console.warn('Perplexity cache save error:', error);
    }
  }

  private incrementUsage() {
    try {
      const current = parseInt(localStorage.getItem(this.USAGE_KEY) || '0');
      localStorage.setItem(this.USAGE_KEY, (current + 1).toString());
    } catch (error) {
      console.warn('Perplexity usage tracking error:', error);
    }
  }

  getUsageCount(): number {
    try {
      return parseInt(localStorage.getItem(this.USAGE_KEY) || '0');
    } catch {
      return 0;
    }
  }

  // Detect if query needs real-time web search
  needsWebSearch(query: string): boolean {
    const webSearchKeywords = [
      'service schedule', 'maintenance schedule', 'km wise', 'ola scooter', 'ather', 'bajaj',
      'bounce', 'price', 'latest', 'current', 'warranty', 'specifications', 'model',
      'launch', 'new', 'update', 'official', 'website', 'dealer', 'showroom'
    ];
    
    const lowercaseQuery = query.toLowerCase();
    return webSearchKeywords.some(keyword => lowercaseQuery.includes(keyword));
  }

  async searchWeb(userQuery: string, retryCount = 0): Promise<PerplexityResponse> {
    // Check cache first
    const cachedResponse = this.getFromCache(userQuery);
    if (cachedResponse) {
      return cachedResponse;
    }

    // Check if API key is set
    if (!this.apiKey) {
      throw new Error('Perplexity API key not configured');
    }

    try {
      const response = await fetch('https://api.perplexity.ai/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'llama-3.1-sonar-small-128k-online',
          messages: [
            {
              role: 'system',
              content: 'You are an electric scooter support assistant. Search for current, official information about electric scooters from manufacturer websites. Focus on service schedules, maintenance intervals, specifications, and official policies. Provide accurate, up-to-date information with sources.'
            },
            {
              role: 'user',
              content: userQuery
            }
          ],
          temperature: 0.2,
          top_p: 0.9,
          max_tokens: 800,
          return_images: false,
          return_related_questions: false,
          search_domain_filter: ['olascooter.com', 'atherenergy.com', 'bajaj.com', 'bounce.bike'],
          search_recency_filter: 'month',
          frequency_penalty: 1,
          presence_penalty: 0
        }),
      });

      if (!response.ok) {
        throw new Error(`Perplexity API error: ${response.status}`);
      }

      const data = await response.json();
      const responseText = data.choices[0]?.message?.content || "I couldn't find current information. Please try again.";
      
      // Extract sources if available (Perplexity doesn't return sources in the API response directly,
      // but we can parse citations from the response text)
      const sources = this.extractSources(responseText);
      
      // Cache the response and increment usage
      this.saveToCache(userQuery, responseText, sources);
      this.incrementUsage();
      
      return {
        response: responseText,
        sources,
        timestamp: Date.now()
      };
    } catch (error) {
      console.error('Perplexity API error:', error);
      
      // Retry once on failure
      if (retryCount < 1) {
        return this.searchWeb(userQuery, retryCount + 1);
      }
      
      throw error;
    }
  }

  private extractSources(responseText: string): string[] {
    // Extract URLs from the response text (basic implementation)
    const urlRegex = /https?:\/\/[^\s)]+/g;
    const urls = responseText.match(urlRegex) || [];
    return [...new Set(urls)]; // Remove duplicates
  }
}

export const perplexityService = new PerplexityService();