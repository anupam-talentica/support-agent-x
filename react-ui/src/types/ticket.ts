export interface SupportTicket {
  id: string;
  title: string;
  description: string;
  status: "open" | "in-progress" | "resolved";
  priority: "low" | "medium" | "high";
  category: "payment" | "technical" | "account" | "other";
  createdAt: Date;
  updatedAt: Date;
  userEmail: string;
  userPhone?: string;
  /** Name or id of the agent/support person assigned to this ticket */
  assignee?: string;
  originalMessage?: string;
}

export interface TicketFilters {
  status?: SupportTicket["status"];
  category?: SupportTicket["category"];
  priority?: SupportTicket["priority"];
}
