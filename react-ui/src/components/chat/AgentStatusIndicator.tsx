import { Bot, Loader2 } from "lucide-react";

export interface AgentStatusIndicatorProps {
  /** Status text from the backend (e.g. server-sent events). Shown as-is; empty shows fallback. */
  status: string;
}

const DEFAULT_STATUS = "Processing...";

const AgentStatusIndicator = ({ status }: AgentStatusIndicatorProps) => {
  const displayText = status.trim() || DEFAULT_STATUS;

  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="h-4 w-4 text-secondary-foreground" />
      </div>
      <div className="bg-card border rounded-lg px-4 py-3 flex items-center gap-3 min-w-[200px]">
        <Loader2 className="h-4 w-4 animate-spin text-muted-foreground flex-shrink-0" />
        <span className="text-sm text-foreground">{displayText}</span>
      </div>
    </div>
  );
};

export default AgentStatusIndicator;
