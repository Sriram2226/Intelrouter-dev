import { cn } from "@/lib/utils";

interface OverrideWidgetProps {
  remaining: number;
  total?: number;
}

export const OverrideWidget = ({ remaining, total = 3 }: OverrideWidgetProps) => {
  const used = total - remaining;

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs text-muted-foreground">Overrides:</span>
      <div className="flex gap-1">
        {Array.from({ length: total }).map((_, i) => (
          <div
            key={i}
            className={cn(
              "w-2 h-2 rounded-full transition-colors",
              i < used ? "bg-muted" : "bg-primary"
            )}
          />
        ))}
      </div>
      <span className="text-xs text-muted-foreground">{remaining}/{total}</span>
    </div>
  );
};
