import { useState } from "react";
import { ThumbsUp, ThumbsDown, Check, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { DifficultyBadge } from "./DifficultyBadge";
import { api } from "@/lib/api";
import { toast } from "sonner";
import { useMutation } from "@tanstack/react-query";

interface FeedbackWidgetProps {
  query: string;
  difficulty: "EASY" | "MEDIUM" | "HARD";
  onFeedbackSubmitted?: () => void;
}

export const FeedbackWidget = ({
  query,
  difficulty,
  onFeedbackSubmitted,
}: FeedbackWidgetProps) => {
  const [showCorrectionDialog, setShowCorrectionDialog] = useState(false);
  const [selectedDifficulty, setSelectedDifficulty] = useState<
    "EASY" | "MEDIUM" | "HARD" | null
  >(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const feedbackMutation = useMutation({
    mutationFn: ({
      isCorrect,
      correctDifficulty,
    }: {
      isCorrect: boolean;
      correctDifficulty?: string;
    }) =>
      api.submitFeedback(
        query,
        difficulty,
        isCorrect,
        correctDifficulty || undefined
      ),
    onSuccess: (data) => {
      setFeedbackSubmitted(true);
      toast.success(data.message || "Feedback submitted successfully!");
      onFeedbackSubmitted?.();
      if (showCorrectionDialog) {
        setShowCorrectionDialog(false);
        setSelectedDifficulty(null);
      }
    },
    onError: (error: Error) => {
      toast.error(error.message || "Failed to submit feedback");
    },
  });

  const handleCorrect = () => {
    feedbackMutation.mutate({ isCorrect: true });
  };

  const handleIncorrect = () => {
    setShowCorrectionDialog(true);
  };

  const handleSubmitCorrection = () => {
    if (!selectedDifficulty) {
      toast.error("Please select the correct difficulty");
      return;
    }
    feedbackMutation.mutate({
      isCorrect: false,
      correctDifficulty: selectedDifficulty,
    });
  };

  if (feedbackSubmitted) {
    return (
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <Check className="w-4 h-4 text-easy" />
        <span>Feedback submitted</span>
      </div>
    );
  }

  return (
    <>
      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground">Was this routing correct?</span>
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCorrect}
            disabled={feedbackMutation.isPending}
            className="h-7 px-2 gap-1.5"
          >
            <ThumbsUp className="w-3.5 h-3.5" />
            <span className="text-xs">Yes</span>
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleIncorrect}
            disabled={feedbackMutation.isPending}
            className="h-7 px-2 gap-1.5"
          >
            <ThumbsDown className="w-3.5 h-3.5" />
            <span className="text-xs">No</span>
          </Button>
        </div>
      </div>

      <Dialog open={showCorrectionDialog} onOpenChange={setShowCorrectionDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Select Correct Difficulty</DialogTitle>
            <DialogDescription>
              The routing was incorrect. Please select the difficulty level this
              query should have been routed to.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="text-sm text-muted-foreground">
              Current routing: <DifficultyBadge difficulty={difficulty} size="sm" />
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium text-foreground">
                Select correct difficulty:
              </div>
              <div className="flex flex-wrap gap-2">
                {(["EASY", "MEDIUM", "HARD"] as const).map((diff) => (
                  <button
                    key={diff}
                    onClick={() => setSelectedDifficulty(diff)}
                    className={`
                      px-4 py-2 rounded-md border transition-colors
                      ${
                        selectedDifficulty === diff
                          ? "border-primary bg-primary/10 text-primary"
                          : "border-border bg-background hover:bg-muted text-foreground"
                      }
                    `}
                  >
                    <DifficultyBadge difficulty={diff} size="sm" />
                  </button>
                ))}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowCorrectionDialog(false);
                setSelectedDifficulty(null);
              }}
              disabled={feedbackMutation.isPending}
            >
              <X className="w-4 h-4 mr-2" />
              Cancel
            </Button>
            <Button
              onClick={handleSubmitCorrection}
              disabled={!selectedDifficulty || feedbackMutation.isPending}
            >
              {feedbackMutation.isPending ? "Submitting..." : "Submit Feedback"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

