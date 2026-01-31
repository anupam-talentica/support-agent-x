import { Bot, Loader2, ArrowRight } from "lucide-react";

export interface AgentStatusIndicatorProps {
  /** Status text from the backend (e.g. server-sent events). Shown as-is; empty shows fallback. */
  status: string;
}

const DEFAULT_STATUS = "Processing...";

const AgentStatusIndicator = ({ status }: AgentStatusIndicatorProps) => {
  const displayText = status.trim() || DEFAULT_STATUS;
  
  // Check if status indicates agent delegation
  const isDelegating = displayText.toLowerCase().includes("delegating");
  
  // Extract agent name if delegating (e.g., "Delegating to Ingestion Agent...")
  const agentMatch = displayText.match(/delegating to (.+?)\.{0,3}$/i);
  const agentName = agentMatch ? agentMatch[1] : null;

  return (
    <div className="flex gap-3">
      <div className="w-8 h-8 bg-secondary rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="h-4 w-4 text-secondary-foreground" />
      </div>
      <div className="bg-card border rounded-lg px-4 py-3 min-w-[200px]">
        <div className="flex items-center gap-3">
          <Loader2 className="h-4 w-4 animate-spin text-primary flex-shrink-0" />
          {isDelegating && agentName ? (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-muted-foreground">Delegating to</span>
              <ArrowRight className="h-3 w-3 text-muted-foreground" />
              <span className="font-medium text-primary">{agentName}</span>
            </div>
          ) : (
            <span className="text-sm text-foreground">{displayText}</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default AgentStatusIndicator;
