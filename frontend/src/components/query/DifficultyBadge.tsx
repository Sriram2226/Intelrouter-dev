import { cn } from "@/lib/utils";

type Difficulty = "EASY" | "MEDIUM" | "HARD";

interface DifficultyBadgeProps {
  difficulty: Difficulty;
  size?: "sm" | "md" | "lg";
}

const difficultyConfig = {
  EASY: {
    bg: "bg-easy/15",
    text: "text-easy",
    border: "border-easy/30",
    dot: "bg-easy",
  },
  MEDIUM: {
    bg: "bg-medium/15",
    text: "text-medium",
    border: "border-medium/30",
    dot: "bg-medium",
  },
  HARD: {
    bg: "bg-hard/15",
    text: "text-hard",
    border: "border-hard/30",
    dot: "bg-hard",
  },
};

const sizeConfig = {
  sm: "text-xs px-2 py-0.5",
  md: "text-xs px-2.5 py-1",
  lg: "text-sm px-3 py-1.5",
};

export const DifficultyBadge = ({ difficulty, size = "md" }: DifficultyBadgeProps) => {
  const config = difficultyConfig[difficulty];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border font-medium",
        config.bg,
        config.text,
        config.border,
        sizeConfig[size]
      )}
    >
      <span className={cn("w-1.5 h-1.5 rounded-full", config.dot)} />
      {difficulty}
    </span>
  );
};
