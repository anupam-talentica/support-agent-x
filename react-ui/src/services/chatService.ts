/**
 * Chat service – talks to the Host Agent backend using Server-Sent Events (SSE).
 * Provides real-time status updates as the agent processes requests through multiple sub-agents.
 */

// Configuration - update this to match your backend URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8083";

export interface ChatMessagePayload {
  role: "user" | "assistant";
  content: string;
}

export interface SendMessageResponse {
  response: string;
  conversation_id?: string;
  agents_used?: string[];
}

/**
 * Callback for agent status updates from the backend (Server-Sent Events).
 * Called whenever the backend sends a new status update.
 */
export type OnAgentStatusChange = (status: string) => void;

// Store conversation ID for multi-turn conversations
let currentConversationId: string | null = null;

/**
 * Send a message using Server-Sent Events (SSE) for real-time status updates.
 * This provides live updates as the host agent delegates to sub-agents.
 */
function sendMessageWithSSE(
  message: string,
  onStatusChange?: OnAgentStatusChange
): Promise<SendMessageResponse> {
  return new Promise((resolve, reject) => {
    // Build query params
    const params = new URLSearchParams({ message });
    if (currentConversationId) {
      params.append("conversation_id", currentConversationId);
    }

    const eventSource = new EventSource(
      `${API_BASE_URL}/api/chat/stream?${params.toString()}`
    );

    let agentsUsed: string[] = [];

    // Handle status events (processing updates)
    eventSource.addEventListener("status", (event) => {
      try {
        const data = JSON.parse(event.data);
        const statusMessage = data.message || data.status || "Processing...";
        onStatusChange?.(statusMessage);
      } catch {
        // If not JSON, use raw data
        onStatusChange?.(event.data);
      }
    });

    // Handle agent delegation events
    eventSource.addEventListener("agent", (event) => {
      try {
        const data = JSON.parse(event.data);
        const agentName = data.agent || "Agent";
        if (!agentsUsed.includes(agentName)) {
          agentsUsed.push(agentName);
        }
        onStatusChange?.(`Delegating to ${agentName}...`);
      } catch {
        onStatusChange?.("Delegating to agent...");
      }
    });

    // Handle final message event
    eventSource.addEventListener("message", (event) => {
      try {
        const data = JSON.parse(event.data);

        // Store conversation ID for subsequent messages
        if (data.conversation_id) {
          currentConversationId = data.conversation_id;
        }

        // Update agents used from response
        if (data.agents_used) {
          agentsUsed = data.agents_used;
        }

        resolve({
          response: data.response || "No response received",
          conversation_id: data.conversation_id,
          agents_used: agentsUsed,
        });
      } catch (e) {
        reject(new Error(`Failed to parse response: ${e}`));
      }
      eventSource.close();
    });

    // Handle error events from the server
    eventSource.addEventListener("error", (event) => {
      // Check if it's a custom error event with data
      if (event instanceof MessageEvent && event.data) {
        try {
          const data = JSON.parse(event.data);
          reject(new Error(data.error || "Server error occurred"));
        } catch {
          reject(new Error("Connection error occurred"));
        }
      } else {
        // Connection error
        reject(new Error("Failed to connect to server"));
      }
      eventSource.close();
    });

    // Handle stream completion
    eventSource.addEventListener("done", () => {
      eventSource.close();
    });

    // Handle connection errors
    eventSource.onerror = (error) => {
      console.error("SSE connection error:", error);
      // Only reject if we haven't already resolved
      if (eventSource.readyState === EventSource.CLOSED) {
        return; // Already handled
      }
      eventSource.close();
      reject(new Error("Connection to server lost"));
    };
  });
}

/**
 * Fallback: Send a message using regular HTTP POST (no streaming).
 * Use this if SSE is not available or for simpler integration.
 */
async function sendMessageHttp(
  message: string
): Promise<SendMessageResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      conversation_id: currentConversationId,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error: ${response.status} - ${errorText}`);
  }

  const data = await response.json();

  // Store conversation ID for subsequent messages
  if (data.conversation_id) {
    currentConversationId = data.conversation_id;
  }

  return {
    response: data.response,
    conversation_id: data.conversation_id,
    agents_used: data.agents_used,
  };
}

/**
 * Check if the backend is healthy.
 */
async function checkHealth(): Promise<{
  status: string;
  agents_connected: number;
  agents: string[];
}> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.status}`);
  }
  return response.json();
}

/**
 * List all connected remote agents.
 */
async function listAgents(): Promise<
  Array<{ name: string; description: string | null; url: string | null }>
> {
  const response = await fetch(`${API_BASE_URL}/api/agents`);
  if (!response.ok) {
    throw new Error(`Failed to list agents: ${response.status}`);
  }
  return response.json();
}

/**
 * Start a new conversation (clears the current conversation ID).
 */
function startNewConversation(): void {
  currentConversationId = null;
}

/**
 * Get the current conversation ID.
 */
function getConversationId(): string | null {
  return currentConversationId;
}

export const chatService = {
  /**
   * Send a user message and get an assistant response.
   * Uses Server-Sent Events for real-time status updates.
   *
   * @param message - The user's message
   * @param conversationHistory - Optional conversation history (not used in current implementation)
   * @param onStatusChange - Callback for real-time status updates
   * @returns Promise with the response
   */
  async sendMessage(
    message: string,
    _conversationHistory?: ChatMessagePayload[],
    onStatusChange?: OnAgentStatusChange
  ): Promise<SendMessageResponse> {
    try {
      // Always use SSE for real-time updates
      return await sendMessageWithSSE(message, onStatusChange);
    } catch (error) {
      console.error("SSE failed, falling back to HTTP:", error);
      // Fallback to HTTP if SSE fails
      onStatusChange?.("Processing...");
      return await sendMessageHttp(message);
    }
  },

  /**
   * Send message without streaming (simple HTTP POST).
   */
  sendMessageSync: sendMessageHttp,

  /**
   * Check backend health status.
   */
  checkHealth,

  /**
   * List all connected remote agents.
   */
  listAgents,

  /**
   * Start a new conversation (resets conversation context).
   */
  startNewConversation,

  /**
   * Get the current conversation ID.
   */
  getConversationId,
};
