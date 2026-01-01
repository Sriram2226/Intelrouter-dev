import { useState } from "react";
import { Send, ChevronDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { OverrideWidget } from "./OverrideWidget";
import { DifficultyBadge } from "./DifficultyBadge";
import { cn } from "@/lib/utils";

type Difficulty = "EASY" | "MEDIUM" | "HARD" | null;

interface QueryInputProps {
  onSubmit: (query: string, difficulty: Difficulty) => void;
  isLoading?: boolean;
  remainingOverrides?: number;
}

export const QueryInput = ({ 
  onSubmit, 
  isLoading = false,
  remainingOverrides = 3 
}: QueryInputProps) => {
  const [query, setQuery] = useState("");
  const [selectedDifficulty, setSelectedDifficulty] = useState<Difficulty>(null);

  const handleSubmit = () => {
    if (query.trim()) {
      onSubmit(query, selectedDifficulty);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && e.metaKey) {
      handleSubmit();
    }
  };

  const difficulties: Difficulty[] = ["EASY", "MEDIUM", "HARD"];

  return (
    <div className="bg-card border border-border rounded-xl p-4 sm:p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-base sm:text-lg font-semibold text-foreground">New Query</h2>
        <OverrideWidget remaining={remainingOverrides} />
      </div>

      <Textarea
        placeholder="Ask anything... The router will automatically select the best model for your query."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        className="min-h-[100px] sm:min-h-[120px] bg-muted/50 border-border focus:border-primary/50 resize-none text-foreground placeholder:text-muted-foreground text-sm sm:text-base"
      />

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button 
                variant="outline" 
                size="sm"
                disabled={remainingOverrides === 0}
                className={cn(
                  "gap-2 text-xs sm:text-sm",
                  selectedDifficulty && "border-primary/50"
                )}
              >
                {selectedDifficulty ? (
                  <DifficultyBadge difficulty={selectedDifficulty} size="sm" />
                ) : (
                  <>
                    <span className="hidden sm:inline">Override Difficulty</span>
                    <span className="sm:hidden">Override</span>
                    <ChevronDown className="w-3.5 h-3.5" />
                  </>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-40">
              <DropdownMenuItem onClick={() => setSelectedDifficulty(null)}>
                <span className="text-muted-foreground">Auto (Default)</span>
              </DropdownMenuItem>
              {difficulties.map((diff) => (
                <DropdownMenuItem 
                  key={diff} 
                  onClick={() => setSelectedDifficulty(diff)}
                >
                  <DifficultyBadge difficulty={diff} size="sm" />
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
          
          {selectedDifficulty && (
            <button
              onClick={() => setSelectedDifficulty(null)}
              className="text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              Clear
            </button>
          )}
        </div>

        <div className="flex items-center justify-between sm:justify-end gap-3">
          <span className="text-xs text-muted-foreground hidden sm:block">⌘ + Enter to send</span>
          <Button 
            onClick={handleSubmit}
            disabled={!query.trim() || isLoading}
            className="gap-2 flex-1 sm:flex-none"
          >
            {isLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
                <span className="hidden sm:inline">Processing...</span>
                <span className="sm:hidden">...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Send</span>
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};
