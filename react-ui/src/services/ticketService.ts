import { SupportTicket } from "@/types/ticket";

/** Mock tickets returned when API is not used. Replace fetchTicketsForUser with real API when ready. */
const MOCK_TICKETS: SupportTicket[] = [
  {
    id: "SCT-MOCK-001",
    title: "Billing inquiry",
    description: "Need help with my last invoice.",
    status: "open",
    priority: "medium",
    category: "payment",
    createdAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    userEmail: "user@example.com",
    userPhone: "9876543210",
    assignee: "Unassigned",
  },
  {
    id: "SCT-MOCK-002",
    title: "Account access issue",
    description: "Cannot log in to my account.",
    status: "in-progress",
    priority: "high",
    category: "account",
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(),
    userEmail: "user@example.com",
    userPhone: "9876543210",
    assignee: "Priya S.",
  },
  {
    id: "SCT-MOCK-003",
    title: "General support request",
    description: "Question about my subscription.",
    status: "resolved",
    priority: "low",
    category: "other",
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000),
    updatedAt: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000),
    userEmail: "user@example.com",
    userPhone: "9876543210",
    assignee: "Amit K.",
  },
];

class TicketService {
  /**
   * Fetch tickets for display. Returns mock data for now.
   * Replace with real API: GET /api/tickets?userId=... (or GET /api/tickets for admin).
   */
  async fetchTicketsForUser(
    _userId: string,
    _isAdmin: boolean
  ): Promise<SupportTicket[]> {
    await new Promise((r) => setTimeout(r, 300));
    return [...MOCK_TICKETS];
  }

  /** No-op when using mock. With real API, call PATCH/PUT to update status. */
  updateTicketStatus(_id: string, _status: SupportTicket["status"]): void {}

  /** For creating tickets from chat. Remove when backend supports create. */
  createTicket(data: Partial<SupportTicket>): SupportTicket {
    const ticket: SupportTicket = {
      id: `SCT-${Date.now()}-${Math.random()
        .toString(36)
        .slice(2, 6)
        .toUpperCase()}`,
      title: data.title ?? "Support Request",
      description: data.description ?? "",
      status: "open",
      priority: data.priority ?? "medium",
      category: data.category ?? "other",
      createdAt: new Date(),
      updatedAt: new Date(),
      userEmail: data.userEmail ?? "",
      userPhone: data.userPhone,
      assignee: data.assignee,
      originalMessage: data.originalMessage,
    };
    return ticket;
  }
}

export const ticketService = new TicketService();
