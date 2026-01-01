import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { QueryInput } from "@/components/query/QueryInput";
import { ResponseCard } from "@/components/query/ResponseCard";
import { TokenUsageWidget } from "@/components/query/TokenUsageWidget";
import { Sparkles } from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";

type Difficulty = "EASY" | "MEDIUM" | "HARD" | null;

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

const Index = () => {
  const [response, setResponse] = useState<ResponseData | null>(null);
  const queryClient = useQueryClient();

  // Fetch usage and override status
  const { data: usageData } = useQuery({
    queryKey: ['usageToday'],
    queryFn: api.getUsageToday,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const { data: overrideStatus } = useQuery({
    queryKey: ['overrideStatus'],
    queryFn: api.getOverrideStatus,
  });

  // Submit query mutation
  const submitQueryMutation = useMutation({
    mutationFn: ({ query, difficulty }: { query: string; difficulty: Difficulty }) =>
      api.submitQuery(query, difficulty || undefined),
    onSuccess: (data: ResponseData) => {
      setResponse(data);
      // Invalidate and refetch usage data
      queryClient.invalidateQueries({ queryKey: ['usageToday'] });
      queryClient.invalidateQueries({ queryKey: ['overrideStatus'] });
      queryClient.invalidateQueries({ queryKey: ['queryHistory'] });
      toast.success('Query processed successfully!');
    },
    onError: (error: Error) => {
      toast.error(error.message || 'Failed to process query');
    },
  });

  const handleSubmit = async (query: string, difficulty: Difficulty) => {
    submitQueryMutation.mutate({ query, difficulty });
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-semibold text-foreground">Query Interface</h1>
            <p className="text-xs sm:text-sm text-muted-foreground mt-1">
              Send queries to be routed to the optimal LLM model
            </p>
          </div>
          <div className="w-full sm:w-64">
            <TokenUsageWidget 
              used={(usageData?.total_tokens || 0)} 
              limit={100000} 
            />
          </div>
        </div>

        {/* Query Input */}
        <QueryInput 
          onSubmit={handleSubmit} 
          isLoading={submitQueryMutation.isPending}
          remainingOverrides={overrideStatus?.remaining || 0}
        />

        {/* Response or Empty State */}
        {response ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-medium text-muted-foreground">Response</h2>
              <button
                onClick={() => setResponse(null)}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors"
              >
                Clear & New Query
              </button>
            </div>
            <ResponseCard response={response} />
          </div>
        ) : !submitQueryMutation.isPending && (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center mb-4">
              <Sparkles className="w-8 h-8 text-primary" />
            </div>
            <h3 className="text-lg font-medium text-foreground mb-2">
              Ready to route your query
            </h3>
            <p className="text-sm text-muted-foreground max-w-md">
              Enter your question above and IntelRouter will automatically select 
              the best model based on query complexity.
            </p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default Index;
