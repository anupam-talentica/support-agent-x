import ReactMarkdown from "react-markdown";
import { Bot } from "lucide-react";

export interface AssistantMessageProps {
  text: string;
  timestamp: Date;
}

const markdownComponents = {
  p: ({ children }: { children?: React.ReactNode }) => (
    <p className="text-sm mb-2 last:mb-0">{children}</p>
  ),
  strong: ({ children }: { children?: React.ReactNode }) => (
    <strong className="font-semibold">{children}</strong>
  ),
  ul: ({ children }: { children?: React.ReactNode }) => (
    <ul className="list-disc list-inside mb-2 space-y-0.5 text-sm">
      {children}
    </ul>
  ),
  ol: ({ children }: { children?: React.ReactNode }) => (
    <ol className="list-decimal list-inside mb-2 space-y-0.5 text-sm">
      {children}
    </ol>
  ),
  li: ({ children }: { children?: React.ReactNode }) => (
    <li className="text-sm">{children}</li>
  ),
  code: ({ children }: { children?: React.ReactNode }) => (
    <code className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">
      {children}
    </code>
  ),
  pre: ({ children }: { children?: React.ReactNode }) => (
    <pre className="bg-muted rounded p-2 overflow-x-auto text-xs my-2">
      {children}
    </pre>
  ),
  a: ({ href, children }: { href?: string; children?: React.ReactNode }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-primary underline hover:no-underline"
    >
      {children}
    </a>
  ),
  h1: ({ children }: { children?: React.ReactNode }) => (
    <h1 className="text-base font-semibold mt-2 mb-1 first:mt-0">{children}</h1>
  ),
  h2: ({ children }: { children?: React.ReactNode }) => (
    <h2 className="text-sm font-semibold mt-2 mb-1 first:mt-0">{children}</h2>
  ),
  h3: ({ children }: { children?: React.ReactNode }) => (
    <h3 className="text-sm font-semibold mt-1.5 mb-0.5">{children}</h3>
  ),
};

const AssistantMessage = ({ text, timestamp }: AssistantMessageProps) => {
  return (
    <div className="flex gap-3 justify-start">
      <div className="flex gap-3 max-w-[85%] flex-row">
        <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-secondary">
          <Bot className="h-4 w-4 text-secondary-foreground" />
        </div>
        <div className="rounded-lg px-4 py-2 bg-card border overflow-hidden">
          <div className="text-sm [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
            <ReactMarkdown components={markdownComponents}>
              {text}
            </ReactMarkdown>
          </div>
          <span className="text-xs opacity-70 mt-1 block">
            {timestamp.toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  );
};

export default AssistantMessage;
