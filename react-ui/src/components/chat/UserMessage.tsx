import { User } from "lucide-react";

export interface UserMessageProps {
  text: string;
  timestamp: Date;
}

const UserMessage = ({ text, timestamp }: UserMessageProps) => {
  return (
    <div className="flex gap-3 justify-end">
      <div className="flex gap-3 max-w-[85%] flex-row-reverse">
        <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 bg-primary">
          <User className="h-4 w-4 text-primary-foreground" />
        </div>
        <div className="rounded-lg px-4 py-2 bg-primary text-primary-foreground">
          <p className="text-sm whitespace-pre-wrap">{text}</p>
          <span className="text-xs opacity-70 mt-1 block">
            {timestamp.toLocaleTimeString()}
          </span>
        </div>
      </div>
    </div>
  );
};

export default UserMessage;
