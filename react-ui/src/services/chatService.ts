/**
 * Chat service – talks to the Host Agent backend using Server-Sent Events (SSE).
 * Provides real-time status updates as the agent processes requests through multiple sub-agents.
 */

import { userService } from "@/services/userService";

// Configuration - update this to match your backend URL
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8083";

/** Header sent to backend for Langfuse user tracing (mobile number). */
const USER_PHONE_HEADER = "X-User-Phone";

/** Maps agent names (from backend) to user-facing generic status messages. Agent names are never shown. */
const AGENT_TO_GENERIC_STATUS: Record<string, string> = {
  "Ingestion Agent": "Processing your request...",
  "Planner Agent": "Planning your response...",
  "Intent Classification Agent": "Analyzing your request...",
  "Intent Classification": "Analyzing your request...",
  "RAG Agent": "Gathering relevant information...",
  "Response Agent": "Preparing your response...",
};

function getGenericStatusForAgent(agentName: string): string {
  return AGENT_TO_GENERIC_STATUS[agentName] ?? "Preparing your response...";
}

export interface ChatMessagePayload {
  role: "user" | "assistant";
  content: string;
}

export interface SendMessageResponse {
  response: string;
  success?: boolean;
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

/** Parse SSE stream manually for reliable handling of custom event types (EventSource can be flaky). */
async function sendMessageWithSSE(
  message: string,
  onStatusChange?: OnAgentStatusChange
): Promise<SendMessageResponse> {
  const params = new URLSearchParams({ message });
  if (currentConversationId) {
    params.append("conversation_id", currentConversationId);
  }

  const headers: Record<string, string> = { Accept: "text/event-stream" };
  const userPhone = userService.getCurrentUser()?.phone;
  if (userPhone) {
    headers[USER_PHONE_HEADER] = userPhone;
  }

  const response = await fetch(
    `${API_BASE_URL}/api/chat/stream?${params.toString()}`,
    { headers }
  );

  if (!response.ok) {
    throw new Error(`Stream failed: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("No response body");
  }

  const decoder = new TextDecoder();
  let buffer = "";
  let agentsUsed: string[] = [];
  let resolved = false;
  let result: SendMessageResponse | null = null;

  const parseAndDispatch = (eventType: string, data: string) => {
    try {
      const parsed = JSON.parse(data);
      if (eventType === "status") {
        const msg = parsed.message || parsed.status || "Processing...";
        onStatusChange?.(msg);
      } else if (eventType === "agent") {
        const agentName = parsed.agent || "";
        if (agentName && !agentsUsed.includes(agentName)) {
          agentsUsed.push(agentName);
        }
        onStatusChange?.(getGenericStatusForAgent(agentName));
      } else if (eventType === "message") {
        if (parsed.conversation_id)
          currentConversationId = parsed.conversation_id;
        if (parsed.agents_used) agentsUsed = parsed.agents_used;
        resolved = true;
        result = {
          response: parsed.response || "No response received",
          conversation_id: parsed.conversation_id,
          agents_used: agentsUsed,
        };
      } else if (eventType === "error") {
        throw new Error(parsed.error || "Server error occurred");
      }
    } catch (e) {
      if (e instanceof SyntaxError) {
        if (eventType === "status" || eventType === "agent") {
          onStatusChange?.(data || "Processing...");
        }
      } else {
        throw e;
      }
    }
  };

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    let eventType = "message";
    let dataBuffer = "";

    for (const line of lines) {
      if (line.startsWith("event:")) {
        eventType = line.slice(6).trim();
      } else if (line.startsWith("data:")) {
        const value = line.slice(5);
        dataBuffer += (value.startsWith(" ") ? value.slice(1) : value) + "\n";
      } else if (line.trim() === "" && dataBuffer) {
        parseAndDispatch(eventType, dataBuffer.trim());
        dataBuffer = "";
        if (resolved) break;
      }
    }
    if (resolved) break;
  }

  if (!resolved || !result) {
    throw new Error("Stream ended without response");
  }
  return result;
}

/**
 * Fallback: Send a message using regular HTTP POST (no streaming).
 * Use this if SSE is not available or for simpler integration.
 */
async function sendMessageHttp(message: string): Promise<SendMessageResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const userPhone = userService.getCurrentUser()?.phone;
  if (userPhone) {
    headers[USER_PHONE_HEADER] = userPhone;
  }

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers,
    body: JSON.stringify({
      message,
      conversation_id: currentConversationId,
    }),
  });

  if (!response.ok) {
    let reason = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body.detail) {
        reason = typeof body.detail === "string" ? body.detail : body.detail.message || reason;
      }
    } catch {
      const text = await response.text();
      if (text) reason = text;
    }
    throw new Error(reason);
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
      // // Fallback to HTTP if SSE fails
      // onStatusChange?.("Processing...");
      // return await sendMessageHttp(message);
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
