import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { ticketService } from "@/services/ticketService";
import { userService } from "@/services/userService";
import type { SupportTicket } from "@/types/ticket";
import {
  Phone,
  LogOut,
  MessageCircle,
  FileText,
  HelpCircle,
  Settings,
  Zap,
  Ticket,
  BookOpen,
} from "lucide-react";

const Dashboard = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userPhone, setUserPhone] = useState<string>("");
  const [tickets, setTickets] = useState<SupportTicket[]>([]);
  const [ticketFilter, setTicketFilter] = useState<
    "all" | "open" | "in-progress" | "resolved"
  >("all");
  const [isAdmin, setIsAdmin] = useState(true);
  const [ticketsLoading, setTicketsLoading] = useState(false);
  const [ticketsError, setTicketsError] = useState<string | null>(null);
  const ticketsCardRef = useRef<HTMLDivElement>(null);
  const [selectedTicket, setSelectedTicket] = useState<SupportTicket | null>(
    null
  );

  useEffect(() => {
    const user = userService.getCurrentUser();
    console.log("Dashboard - Current user:", user);

    if (user) {
      setIsAuthenticated(true);
      setUserPhone(user.phone);
      setIsAdmin(user.role === "admin");
      console.log("Dashboard - Is admin:", user.role === "admin");
      console.log("Dashboard - User role:", user.role);
      // Load tickets based on user role
      loadTickets();
    } else {
      console.log("Dashboard - No user found, redirecting to login");
      navigate("/");
    }
  }, [navigate]);

  const loadTickets = async () => {
    const user = userService.getCurrentUser();
    if (!user) return;
    setTicketsLoading(true);
    setTicketsError(null);
    try {
      const userTickets = await ticketService.fetchTicketsForUser(
        user.phone,
        user.role === "admin"
      );
      setTickets(userTickets);
    } catch (err) {
      console.error("Error loading tickets:", err);
      const message =
        err instanceof Error ? err.message : "Failed to load tickets";
      setTicketsError(message);
      setTickets([]);
      toast({
        title: "Could not load tickets",
        description: message,
        variant: "destructive",
      });
    } finally {
      setTicketsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("userPhone");
    navigate("/");
    toast({
      title: "Logged out successfully",
      description: "You have been logged out.",
    });
  };

  const quickActions = [
    {
      title: "Start Chat Support",
      description: "Get instant help with AI assistance",
      icon: MessageCircle,
      color: "bg-primary/10 text-primary",
      action: () => navigate("/chat"),
    },
    {
      title: "View All Tickets",
      description: "Check all your support requests",
      icon: FileText,
      color: "bg-blue/10 text-blue",
      action: () => {
        ticketsCardRef.current?.scrollIntoView({ behavior: "smooth" });
        toast({
          title: "All tickets",
          description: "Scrolled to tickets section",
        });
      },
    },
    {
      title: "Emergency Contact",
      description: "Get immediate assistance",
      icon: Phone,
      color: "bg-destructive/10 text-destructive",
      action: () =>
        toast({
          title: "Emergency",
          description: "Call 1800-123-4567 for immediate help",
        }),
    },
    {
      title: "FAQ & Help",
      description: "Find answers to common questions",
      icon: HelpCircle,
      color: "bg-warning/10 text-warning",
      action: () =>
        toast({ title: "Help", description: "Check the FAQ section below" }),
    },
  ];

  const filteredTickets = tickets.filter((ticket) => {
    if (ticketFilter === "all") return true;
    return ticket.status === ticketFilter;
  });

  const recentTickets = filteredTickets.slice(0, 5);

  const handleStatusChange = (
    ticketId: string,
    newStatus: SupportTicket["status"]
  ) => {
    ticketService.updateTicketStatus(ticketId, newStatus);
    setTickets((prev) =>
      prev.map((t) =>
        t.id === ticketId
          ? { ...t, status: newStatus, updatedAt: new Date() }
          : t
      )
    );
    toast({
      title: "Ticket updated",
      description: `Status changed to ${newStatus}`,
    });
  };

  const getStatusBadge = (status: SupportTicket["status"]) => {
    switch (status) {
      case "resolved":
        return (
          <Badge className="bg-success/10 text-success border-success/20">
            Resolved
          </Badge>
        );
      case "open":
        return (
          <Badge className="bg-warning/10 text-warning border-warning/20">
            Open
          </Badge>
        );
      case "in-progress":
        return (
          <Badge className="bg-primary/10 text-primary border-primary/20">
            In Progress
          </Badge>
        );
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getCategoryIcon = (category: SupportTicket["category"]) => {
    switch (category) {
      case "payment":
        return <FileText className="h-4 w-4" />;
      case "technical":
        return <Settings className="h-4 w-4" />;
      case "account":
        return <Settings className="h-4 w-4" />;
      default:
        return <HelpCircle className="h-4 w-4" />;
    }
  };

  const getPriorityColor = (priority: SupportTicket["priority"]) => {
    switch (priority) {
      case "high":
        return "text-destructive";
      case "medium":
        return "text-warning";
      case "low":
        return "text-muted-foreground";
      default:
        return "text-muted-foreground";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border px-4 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-foreground">Support Agent X</h1>
            <div className="flex items-center gap-2">
              <p className="text-sm text-muted-foreground">
                Welcome, +91 {userPhone}
              </p>
              {isAdmin && (
                <Badge variant="destructive" className="text-xs">
                  Admin
                </Badge>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {isAdmin && (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate("/admin/queries")}
                >
                  <Ticket className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate("/admin/knowledge")}
                >
                  <BookOpen className="h-4 w-4" />
                </Button>
              </>
            )}
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <div className="p-4 space-y-6">
        {/* Quick Actions */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {quickActions.map((action, index) => (
              <Card
                key={index}
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={action.action}
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div
                      className={`w-10 h-10 rounded-full flex items-center justify-center ${action.color}`}
                    >
                      <action.icon className="h-5 w-5" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold">{action.title}</h3>
                      <p className="text-sm text-muted-foreground">
                        {action.description}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Support Tickets */}
        <div ref={ticketsCardRef}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 mb-4">
                <Ticket className="h-5 w-5" />
                {isAdmin
                  ? `All Support Tickets (${tickets.length})`
                  : `My Support Tickets (${tickets.length})`}
              </CardTitle>
              <div className="flex gap-2 mt-2">
                <Button
                  variant={ticketFilter === "all" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setTicketFilter("all")}
                >
                  All
                </Button>
                <Button
                  variant={ticketFilter === "open" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setTicketFilter("open")}
                >
                  Open
                </Button>
                <Button
                  variant={
                    ticketFilter === "in-progress" ? "default" : "outline"
                  }
                  size="sm"
                  onClick={() => setTicketFilter("in-progress")}
                >
                  In Progress
                </Button>
                <Button
                  variant={ticketFilter === "resolved" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setTicketFilter("resolved")}
                >
                  Resolved
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {ticketsLoading ? (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">Loading tickets...</p>
                </div>
              ) : ticketsError ? (
                <div className="text-center py-8 space-y-2">
                  <p className="text-destructive">{ticketsError}</p>
                  <Button variant="outline" onClick={loadTickets}>
                    Retry
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {recentTickets.map((ticket) => (
                    <div
                      key={ticket.id}
                      role="button"
                      tabIndex={0}
                      onClick={() => setSelectedTicket(ticket)}
                      onKeyDown={(e) =>
                        e.key === "Enter" && setSelectedTicket(ticket)
                      }
                      className="border rounded-lg p-4 space-y-3 cursor-pointer hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            {getCategoryIcon(ticket.category)}
                            <p className="font-medium">{ticket.title}</p>
                            <span
                              className={`text-xs px-2 py-1 rounded ${getPriorityColor(
                                ticket.priority
                              )}`}
                            >
                              {ticket.priority.toUpperCase()}
                            </span>
                          </div>
                          <p className="text-sm text-muted-foreground mb-2">
                            {ticket.description}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground flex-wrap">
                            <span>ID: {ticket.id}</span>
                            <span>Category: {ticket.category}</span>
                            <span>
                              Assigned to: {ticket.assignee ?? "Unassigned"}
                            </span>
                            {isAdmin && ticket.userPhone && (
                              <span>User: +91 {ticket.userPhone}</span>
                            )}
                            <span>{ticket.createdAt.toLocaleDateString()}</span>
                          </div>
                        </div>
                        <div
                          className="text-right space-y-2"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {getStatusBadge(ticket.status)}
                          {isAdmin && ticket.status !== "resolved" && (
                            <div className="flex gap-1">
                              {ticket.status === "open" && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() =>
                                    handleStatusChange(ticket.id, "in-progress")
                                  }
                                >
                                  Start
                                </Button>
                              )}
                              {ticket.status === "in-progress" && (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() =>
                                    handleStatusChange(ticket.id, "resolved")
                                  }
                                >
                                  Resolve
                                </Button>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                  {recentTickets.length === 0 && (
                    <div className="text-center py-8">
                      <Ticket className="h-12 w-12 text-muted-foreground mx-auto mb-3" />
                      <p className="text-muted-foreground">
                        {ticketFilter === "all"
                          ? "No support tickets yet"
                          : `No ${ticketFilter} tickets`}
                      </p>
                      <Button
                        variant="outline"
                        className="mt-2"
                        onClick={() => navigate("/chat")}
                      >
                        Start a conversation to create tickets
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Ticket details modal */}
        <Dialog
          open={!!selectedTicket}
          onOpenChange={(open) => !open && setSelectedTicket(null)}
        >
          <DialogContent className="max-w-md sm:max-w-lg">
            {selectedTicket && (
              <>
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2">
                    <Ticket className="h-5 w-5" />
                    Ticket details
                  </DialogTitle>
                </DialogHeader>
                <div className="space-y-4 pt-2">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Title
                    </p>
                    <p className="font-medium">{selectedTicket.title}</p>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Description
                    </p>
                    <p className="text-sm">{selectedTicket.description}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="font-medium text-muted-foreground">ID</p>
                      <p>{selectedTicket.id}</p>
                    </div>
                    <div>
                      <p className="font-medium text-muted-foreground">
                        Status
                      </p>
                      <div className="mt-0.5">
                        {getStatusBadge(selectedTicket.status)}
                      </div>
                    </div>
                    <div>
                      <p className="font-medium text-muted-foreground">
                        Priority
                      </p>
                      <p className="capitalize">{selectedTicket.priority}</p>
                    </div>
                    <div>
                      <p className="font-medium text-muted-foreground">
                        Category
                      </p>
                      <p className="capitalize">{selectedTicket.category}</p>
                    </div>
                    <div>
                      <p className="font-medium text-muted-foreground">
                        Assigned to
                      </p>
                      <p>{selectedTicket.assignee ?? "Unassigned"}</p>
                    </div>
                    <div>
                      <p className="font-medium text-muted-foreground">
                        Created
                      </p>
                      <p>
                        {selectedTicket.createdAt.toLocaleDateString()}{" "}
                        {selectedTicket.createdAt.toLocaleTimeString()}
                      </p>
                    </div>
                    <div>
                      <p className="font-medium text-muted-foreground">
                        Updated
                      </p>
                      <p>
                        {selectedTicket.updatedAt.toLocaleDateString()}{" "}
                        {selectedTicket.updatedAt.toLocaleTimeString()}
                      </p>
                    </div>
                    {isAdmin && selectedTicket.userPhone && (
                      <div className="col-span-2">
                        <p className="font-medium text-muted-foreground">
                          User phone
                        </p>
                        <p>+91 {selectedTicket.userPhone}</p>
                      </div>
                    )}
                    {selectedTicket.userEmail && (
                      <div className="col-span-2">
                        <p className="font-medium text-muted-foreground">
                          User email
                        </p>
                        <p>{selectedTicket.userEmail}</p>
                      </div>
                    )}
                  </div>
                  {selectedTicket.originalMessage && (
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">
                        Original message
                      </p>
                      <p className="text-sm whitespace-pre-wrap">
                        {selectedTicket.originalMessage}
                      </p>
                    </div>
                  )}
                  {isAdmin && selectedTicket.status !== "resolved" && (
                    <div className="flex gap-2 pt-2 border-t">
                      {selectedTicket.status === "open" && (
                        <Button
                          variant="outline"
                          onClick={() => {
                            handleStatusChange(
                              selectedTicket.id,
                              "in-progress"
                            );
                            setSelectedTicket({
                              ...selectedTicket,
                              status: "in-progress",
                              updatedAt: new Date(),
                            });
                          }}
                        >
                          Start
                        </Button>
                      )}
                      {selectedTicket.status === "in-progress" && (
                        <Button
                          variant="outline"
                          onClick={() => {
                            handleStatusChange(selectedTicket.id, "resolved");
                            setSelectedTicket({
                              ...selectedTicket,
                              status: "resolved",
                              updatedAt: new Date(),
                            });
                          }}
                        >
                          Resolve
                        </Button>
                      )}
                    </div>
                  )}
                </div>
              </>
            )}
          </DialogContent>
        </Dialog>

        {/* FAQ Quick Links */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageCircle className="h-5 w-5" />
              Frequently Asked Questions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <Button
                variant="ghost"
                className="w-full justify-start h-auto p-3"
                onClick={() =>
                  toast({
                    title: "FAQ",
                    description:
                      "To start a ride, scan the QR code on the scooter and follow app instructions.",
                  })
                }
              >
                <div className="text-left">
                  <p className="font-medium">How to start a ride?</p>
                  <p className="text-sm text-muted-foreground">
                    Learn about starting your electric scooter ride
                  </p>
                </div>
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start h-auto p-3"
                onClick={() =>
                  toast({
                    title: "FAQ",
                    description:
                      "Battery range is typically 15-25 km per charge depending on terrain and rider weight.",
                  })
                }
              >
                <div className="text-left">
                  <p className="font-medium">What's the battery range?</p>
                  <p className="text-sm text-muted-foreground">
                    Check battery performance and range
                  </p>
                </div>
              </Button>
              <Button
                variant="ghost"
                className="w-full justify-start h-auto p-3"
                onClick={() =>
                  toast({
                    title: "FAQ",
                    description:
                      "Payment is processed automatically after each ride. You can add money to wallet or link cards.",
                  })
                }
              >
                <div className="text-left">
                  <p className="font-medium">How does payment work?</p>
                  <p className="text-sm text-muted-foreground">
                    Understand payment processing
                  </p>
                </div>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
