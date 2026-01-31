import { Bot, Loader2 } from "lucide-react";

const TypingIndicator = () => {
  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="h-4 w-4 text-secondary-foreground" />
      </div>
      <div className="bg-card border rounded-lg px-4 py-3 flex items-center gap-2">
        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        <span className="text-sm text-muted-foreground">Typing...</span>
      </div>
    </div>
  );
};

export default TypingIndicator;
