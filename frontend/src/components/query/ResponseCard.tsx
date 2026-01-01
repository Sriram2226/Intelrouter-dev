import { Copy, Check, Bot, Cpu, Route, Coins } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { DifficultyBadge } from "./DifficultyBadge";
import { cn } from "@/lib/utils";

interface ResponseData {
  answer: string;
  model_name: string;
  difficulty: "EASY" | "MEDIUM" | "HARD";
  routing_source: "algorithmic" | "ml" | "user_override";
  usage: {
    tokens_in: number;
    tokens_out: number;
    total_tokens: number;
  };
}

interface ResponseCardProps {
  response: ResponseData;
}

const routingSourceLabels = {
  algorithmic: "Algorithmic",
  ml: "ML Model",
  user_override: "User Override",
};

export const ResponseCard = ({ response }: ResponseCardProps) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(response.answer);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  return (
    <div className="bg-card border border-border rounded-xl overflow-hidden animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 px-4 sm:px-6 py-3 sm:py-4 border-b border-border bg-muted/30">
        <div className="flex items-center gap-3 sm:gap-4 flex-wrap">
          <DifficultyBadge difficulty={response.difficulty} size="sm" />
          <div className="flex items-center gap-2 text-xs sm:text-sm text-muted-foreground">
            <Bot className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
            <span className="font-mono text-xs truncate max-w-[150px] sm:max-w-none">{response.model_name}</span>
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleCopy}
          className="gap-2 self-end sm:self-auto"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-easy" />
              <span className="text-xs sm:text-sm">Copied</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span className="text-xs sm:text-sm">Copy</span>
            </>
          )}
        </Button>
      </div>

      {/* Response Body */}
      <div className="p-4 sm:p-6">
        <p className="text-sm sm:text-base text-foreground leading-relaxed whitespace-pre-wrap">
          {response.answer}
        </p>
      </div>

      {/* Metadata Footer */}
      <div className="px-4 sm:px-6 py-3 sm:py-4 border-t border-border bg-muted/20">
        <div className="flex flex-col sm:flex-row sm:flex-wrap sm:items-center gap-3 sm:gap-6 text-xs sm:text-sm">
          <div className="flex items-center gap-2">
            <Route className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-muted-foreground" />
            <span className="text-muted-foreground">Routing:</span>
            <span className={cn(
              "font-medium",
              response.routing_source === "user_override" ? "text-primary" : "text-foreground"
            )}>
              {routingSourceLabels[response.routing_source]}
            </span>
          </div>
          
          <div className="flex items-center gap-2 flex-wrap">
            <Coins className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-muted-foreground" />
            <span className="text-muted-foreground">Tokens:</span>
            <span className="font-mono text-foreground">
              {formatNumber(response.usage.tokens_in)} in / {formatNumber(response.usage.tokens_out)} out
            </span>
            <span className="text-muted-foreground">
              ({formatNumber(response.usage.total_tokens)} total)
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
