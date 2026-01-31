import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Bot, ArrowLeft, Send, RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { userService } from "@/services/userService";
import { chatService } from "@/services/chatService";
import UserMessage from "@/components/chat/UserMessage";
import AssistantMessage from "@/components/chat/AssistantMessage";
import AgentStatusIndicator from "@/components/chat/AgentStatusIndicator";

interface Message {
  id: string;
  text: string;
  sender: "user" | "bot";
  timestamp: Date;
}

const Chat = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [agentStatus, setAgentStatus] = useState<string>("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const WELCOME_MESSAGE_TEXT = `Hello! I'm your **Support Assistant**. How can I help you today?

You can ask about:
- **Billing** – payments, refunds, invoices
- **Account** – login, profile, security
- **Tickets** – check status or create a new request

Just type your question below.`;

  useEffect(() => {
    const currentUser = userService.getCurrentUser();
    if (!currentUser) {
      toast({
        title: "Please log in",
        description: "You need to be logged in to use chat.",
        variant: "destructive",
      });
      navigate("/login");
      return;
    }

    const welcomeMessage: Message = {
      id: Date.now().toString(),
      text: WELCOME_MESSAGE_TEXT,
      sender: "bot",
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, [navigate, toast]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleResetChat = () => {
    // Reset conversation on the backend
    chatService.startNewConversation();

    const welcomeMessage: Message = {
      id: Date.now().toString(),
      text: WELCOME_MESSAGE_TEXT,
      sender: "bot",
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
    setInputText("");
    setAgentStatus("");
    toast({
      title: "Chat reset",
      description: "Starting a new conversation.",
    });
  };

  const handleSendMessage = async () => {
    const text = inputText.trim();
    if (!text) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: "user",
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsTyping(true);
    setAgentStatus("");

    try {
      const conversationHistory = messages
        .filter((m) => m.sender === "user" || m.sender === "bot")
        .slice(-10)
        .map((m) => ({
          role: (m.sender === "bot" ? "assistant" : "user") as
            | "user"
            | "assistant",
          content: m.text,
        }));

      const { response } = await chatService.sendMessage(
        text,
        conversationHistory,
        (status) => setAgentStatus(status)
      );

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: response,
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Chat error:", error);
      toast({
        title: "Something went wrong",
        description: "Please try again.",
        variant: "destructive",
      });
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: "Sorry, I couldn't get a response. Please try again.",
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
      setAgentStatus("");
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <div className="border-b bg-card px-4 py-3 flex items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate("/dashboard")}
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex items-center gap-3 flex-1">
          <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
            <Bot className="h-4 w-4 text-primary-foreground" />
          </div>
          <div>
            <h1 className="font-semibold">Support Chat</h1>
            <p className="text-sm text-muted-foreground">We're here to help</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleResetChat}
            disabled={isTyping}
            title="Reset chat"
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
          <span className="text-xs text-muted-foreground">Online</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.map((message) =>
          message.sender === "user" ? (
            <UserMessage
              key={message.id}
              text={message.text}
              timestamp={message.timestamp}
            />
          ) : (
            <AssistantMessage
              key={message.id}
              text={message.text}
              timestamp={message.timestamp}
            />
          )
        )}

        {isTyping && <AgentStatusIndicator status={agentStatus} />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t bg-card px-4 py-3">
        <div className="flex gap-2">
          <Input
            placeholder="Type your message..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            className="flex-1"
            disabled={isTyping}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isTyping}
            size="icon"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default Chat;
