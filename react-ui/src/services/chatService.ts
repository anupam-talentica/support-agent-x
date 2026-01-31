/**
 * Chat service – talks to the support chat backend.
 * Currently uses a mock API; replace sendMessage with a real HTTP call when the backend is ready.
 */

export interface ChatMessagePayload {
  role: "user" | "assistant";
  content: string;
}

export interface SendMessageResponse {
  response: string;
}

/**
 * Callback for agent status updates from the backend (e.g. Server-Sent Events).
 * Called whenever the backend sends a new status; status text is free-form from the server.
 *
 * Example with SSE:
 *   const eventSource = new EventSource(`/api/chat/stream?message=...`);
 *   eventSource.addEventListener('status', (e) => onStatusChange?.(e.data));
 *   eventSource.addEventListener('message', (e) => { ... final response ... });
 */
export type OnAgentStatusChange = (status: string) => void;

const MOCK_DELAY_MS = 600;

/**
 * Mock implementation: simulates a network call and returns a simple support-style reply.
 * Real implementation: use SSE or similar, parse status events from the stream,
 * and call onStatusChange(status) whenever the backend sends a status update.
 */
async function mockSendMessage(
  message: string,
  _conversationHistory?: ChatMessagePayload[],
  onStatusChange?: OnAgentStatusChange
): Promise<SendMessageResponse> {
  // Mock does not emit status events. Backend will call onStatusChange when it sends status (e.g. via SSE).
  await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY_MS));

  const lower = message.toLowerCase();
  if (
    lower.includes("hello") ||
    lower.includes("hi") ||
    lower.includes("hey")
  ) {
    return {
      response: `Hello! **How can I help you today?**

Here are some things I can help with:
- **Billing** – invoices, refunds, payment methods
- **Account** – login, profile, security
- **General support** – questions and troubleshooting

Just type your question below.`,
    };
  }
  if (lower.includes("help") || lower.includes("support")) {
    return {
      response: `## Support options

I'm here to help. You can ask about:

1. **Billing** – payments, refunds, invoices
2. **Account** – profile, login, password reset
3. **Tickets** – check status or create a new request
4. **General** – FAQs and how-to guides

Use \`/ticket\` to create a support ticket, or describe your issue and I'll guide you.`,
    };
  }
  if (lower.includes("thank")) {
    return {
      response: "You're welcome! **Is there anything else I can help with?**",
    };
  }
  if (lower.includes("bye") || lower.includes("goodbye")) {
    return {
      response: "**Goodbye!** Feel free to come back if you need more help.",
    };
  }

  return {
    response: `Thanks for your message. This is a **mock response**—when connected to your backend API, you'll get real support here.

**You said:** "${message.slice(0, 80)}${message.length > 80 ? "…" : ""}"

Need help? Try asking about \`billing\`, \`account\`, or \`support\`.`,
  };
}

export const chatService = {
  /**
   * Send a user message and get an assistant response.
   * - conversationHistory: optional context for your backend.
   * - onStatusChange: called whenever the backend sends an agent status update (e.g. via Server-Sent Events).
   *   Status is a free-form string from the server (e.g. "Thinking...", "Delegating to billing agent", "Waiting for support").
   */
  async sendMessage(
    message: string,
    conversationHistory?: ChatMessagePayload[],
    onStatusChange?: OnAgentStatusChange
  ): Promise<SendMessageResponse> {
    // TODO: Replace with real API (e.g. fetch + SSE). On each status event from the server, call onStatusChange(event.status).
    return mockSendMessage(message, conversationHistory, onStatusChange);
  },
};
