import { Zap } from "lucide-react";
import { Progress } from "@/components/ui/progress";

interface TokenUsageWidgetProps {
  used: number;
  limit: number;
}

export const TokenUsageWidget = ({ used, limit }: TokenUsageWidgetProps) => {
  const percentage = (used / limit) * 100;
  const remaining = limit - used;
  
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  return (
    <div className="bg-card border border-border rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
            <Zap className="w-4 h-4 text-primary" />
          </div>
          <span className="text-sm font-medium text-foreground">Token Usage</span>
        </div>
        <span className="text-xs text-muted-foreground">Today</span>
      </div>
      
      <div className="space-y-3">
        <Progress value={percentage} className="h-2" />
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">
            {formatNumber(used)} / {formatNumber(limit)} tokens
          </span>
          <span className="text-primary font-medium">
            {formatNumber(remaining)} remaining
          </span>
        </div>
      </div>
    </div>
  );
};
