import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { DifficultyBadge } from "@/components/query/DifficultyBadge";
import { ChevronDown, ChevronUp, Clock, Bot, Route } from "lucide-react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";

interface HistoryItem {
  id: string;
  final_label: "EASY" | "MEDIUM" | "HARD";
  routing_source: "algorithmic" | "ml" | "user_override";
  model_name: string;
  created_at: string;
}

const routingSourceLabels = {
  algorithmic: "Algorithmic",
  ml: "ML Model",
  user_override: "Override",
};

interface HistoryRowProps {
  item: HistoryItem;
  isExpanded: boolean;
  onToggle: () => void;
}

const HistoryRow = ({ item, isExpanded, onToggle }: HistoryRowProps) => {
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  return (
    <div className="border-b border-border last:border-b-0">
      <button
        onClick={onToggle}
        className="w-full px-4 sm:px-6 py-3 sm:py-4 flex items-start sm:items-center gap-3 sm:gap-4 hover:bg-muted/30 transition-colors text-left"
      >
        <div className="flex-shrink-0 mt-1 sm:mt-0">
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="w-4 h-4 text-muted-foreground" />
          )}
        </div>

        {/* Mobile Layout */}
        <div className="flex-1 min-w-0 sm:hidden">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-muted-foreground">{formatDate(item.created_at)}</span>
            <DifficultyBadge difficulty={item.final_label} size="sm" />
          </div>
        </div>

        {/* Desktop Layout */}
        <div className="hidden sm:flex items-center gap-2 text-xs text-muted-foreground w-20 flex-shrink-0">
          <Clock className="w-3.5 h-3.5" />
          {formatDate(item.created_at)}
        </div>

        <div className="hidden sm:block flex-1 min-w-0">
          <DifficultyBadge difficulty={item.final_label} size="sm" />
        </div>

        <div className="hidden sm:flex items-center gap-4 flex-shrink-0">
          <DifficultyBadge difficulty={item.final_label} size="sm" />
          
          <span className={cn(
            "text-xs px-2 py-1 rounded-md",
            item.routing_source === "user_override" 
              ? "bg-primary/10 text-primary" 
              : "bg-muted text-muted-foreground"
          )}>
            {routingSourceLabels[item.routing_source]}
          </span>
        </div>
      </button>

      {isExpanded && (
        <div className="px-4 sm:px-6 pb-4 pl-10 sm:pl-14 animate-fade-in">
          <div className="bg-muted/30 rounded-lg p-3 sm:p-4 space-y-3">
            <div className="flex flex-wrap gap-3 sm:gap-4 text-xs text-muted-foreground">
              <div className="flex items-center gap-1.5">
                <Bot className="w-3.5 h-3.5" />
                <span className="font-mono truncate max-w-[120px] sm:max-w-none">{item.model_name}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Route className="w-3.5 h-3.5" />
                <span>{routingSourceLabels[item.routing_source]}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const History = () => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data: history, isLoading } = useQuery({
    queryKey: ['queryHistory'],
    queryFn: api.getQueryHistory,
  });

  const handleToggle = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="max-w-5xl mx-auto space-y-4 sm:space-y-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-96 w-full" />
        </div>
      </DashboardLayout>
    );
  }

  const historyList = history || [];

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto space-y-4 sm:space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h1 className="text-xl sm:text-2xl font-semibold text-foreground">Query History</h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-1">
              View your past queries and routing decisions
            </p>
          </div>
          <div className="text-xs sm:text-sm text-muted-foreground">
            {historyList.length} queries
          </div>
        </div>

        {/* History Table */}
        <div className="bg-card border border-border rounded-xl overflow-hidden">
          {/* Header - Hidden on mobile */}
          <div className="hidden sm:flex px-6 py-3 border-b border-border bg-muted/30 items-center gap-4 text-xs font-medium text-muted-foreground uppercase tracking-wider">
            <div className="w-4" />
            <div className="w-20">Time</div>
            <div className="flex-1">Difficulty</div>
            <div className="w-32 text-center">Model</div>
            <div className="w-24 text-center">Source</div>
          </div>

          {/* Rows */}
          <div>
            {historyList.map((item: HistoryItem) => (
              <HistoryRow
                key={item.id}
                item={item}
                isExpanded={expandedId === item.id}
                onToggle={() => handleToggle(item.id)}
              />
            ))}
          </div>
        </div>

        {/* Empty State */}
        {historyList.length === 0 && (
          <div className="text-center py-16">
            <p className="text-muted-foreground">No queries yet</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default History;
