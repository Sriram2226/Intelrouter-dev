import { Copy, Check, Bot, Cpu, Route, Coins } from "lucide-react";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
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
        <div className="prose prose-sm dark:prose-invert max-w-none prose-headings:font-semibold prose-p:text-foreground prose-strong:text-foreground prose-code:text-foreground prose-pre:bg-muted prose-pre:border prose-pre:border-border">
          <ReactMarkdown
            components={{
              // Custom styling for inline code
              code: ({ node, inline, className, children, ...props }) => {
                return inline ? (
                  <code className="bg-muted px-1.5 py-0.5 rounded text-sm font-mono text-foreground" {...props}>
                    {children}
                  </code>
                ) : (
                  <code className="block bg-muted p-4 rounded-lg overflow-x-auto text-sm font-mono text-foreground border border-border" {...props}>
                    {children}
                  </code>
                );
              },
              // Custom styling for headings
              h1: ({ node, ...props }) => <h1 className="text-2xl font-semibold mt-6 mb-4 text-foreground" {...props} />,
              h2: ({ node, ...props }) => <h2 className="text-xl font-semibold mt-5 mb-3 text-foreground" {...props} />,
              h3: ({ node, ...props }) => <h3 className="text-lg font-semibold mt-4 mb-2 text-foreground" {...props} />,
              // Custom styling for paragraphs
              p: ({ node, ...props }) => <p className="text-foreground leading-relaxed my-2" {...props} />,
              // Custom styling for lists
              ul: ({ node, ...props }) => <ul className="list-disc list-inside my-2 space-y-1 text-foreground" {...props} />,
              ol: ({ node, ...props }) => <ol className="list-decimal list-inside my-2 space-y-1 text-foreground" {...props} />,
              li: ({ node, ...props }) => <li className="text-foreground" {...props} />,
              // Custom styling for links
              a: ({ node, ...props }) => (
                <a className="text-primary underline hover:text-primary/80" {...props} />
              ),
              // Custom styling for blockquotes
              blockquote: ({ node, ...props }) => (
                <blockquote className="border-l-4 border-muted-foreground/30 pl-4 italic my-2 text-muted-foreground" {...props} />
              ),
              // Custom styling for horizontal rules
              hr: ({ node, ...props }) => (
                <hr className="border-border my-4" {...props} />
              ),
            }}
          >
            {response.answer}
          </ReactMarkdown>
        </div>
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
