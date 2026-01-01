import { useQuery } from "@tanstack/react-query";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Progress } from "@/components/ui/progress";
import { 
  Coins, 
  TrendingUp, 
  MessageSquare,
  Zap,
  DollarSign
} from "lucide-react";
import { api } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: {
    value: number;
    label: string;
  };
}

const StatCard = ({ title, value, subtitle, icon, trend }: StatCardProps) => (
  <div className="bg-card border border-border rounded-xl p-4 sm:p-6">
    <div className="flex items-start justify-between mb-3 sm:mb-4">
      <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-primary/10 flex items-center justify-center">
        {icon}
      </div>
      {trend && (
        <div className="flex items-center gap-1 text-easy text-xs font-medium">
          <TrendingUp className="w-3 h-3" />
          +{trend.value}%
        </div>
      )}
    </div>
    <div>
      <p className="text-lg sm:text-2xl font-semibold text-foreground">{value}</p>
      <p className="text-xs sm:text-sm text-muted-foreground mt-1">{title}</p>
      {subtitle && (
        <p className="text-xs text-muted-foreground mt-0.5 hidden sm:block">{subtitle}</p>
      )}
    </div>
  </div>
);

const Usage = () => {
  const { data: usageData, isLoading } = useQuery({
    queryKey: ['usageToday'],
    queryFn: api.getUsageToday,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  const daily_limit = 100000;
  const percentage = usageData 
    ? (usageData.total_tokens / daily_limit) * 100 
    : 0;

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatCurrency = (num: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 3,
    }).format(num);
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="max-w-5xl mx-auto space-y-4 sm:space-y-8">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-48 w-full" />
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
            {[1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-32 w-full" />
            ))}
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (!usageData) {
    return (
      <DashboardLayout>
        <div className="max-w-5xl mx-auto">
          <p className="text-muted-foreground">Failed to load usage data</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto space-y-4 sm:space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-xl sm:text-2xl font-semibold text-foreground">Usage Statistics</h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            Monitor your daily token usage and costs
          </p>
        </div>

        {/* Main Usage Card */}
        <div className="bg-card border border-border rounded-xl p-4 sm:p-8">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
            <div>
              <h2 className="text-base sm:text-lg font-medium text-foreground">Today's Usage</h2>
              <p className="text-xs sm:text-sm text-muted-foreground">
                {formatNumber(usageData.total_tokens)} of {formatNumber(daily_limit)} tokens used
              </p>
            </div>
            <div className="text-left sm:text-right">
              <p className="text-2xl sm:text-3xl font-semibold text-primary">
                {formatNumber(usageData.remaining_tokens)}
              </p>
              <p className="text-xs sm:text-sm text-muted-foreground">tokens remaining</p>
            </div>
          </div>

          <Progress value={percentage} className="h-2 sm:h-3 mb-4" />

          <div className="flex items-center justify-between text-xs sm:text-sm">
            <span className="text-muted-foreground">{percentage.toFixed(1)}% used</span>
            <span className="text-muted-foreground">Resets at midnight UTC</span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <StatCard
            title="Total Tokens"
            value={formatNumber(usageData.total_tokens)}
            subtitle="Input + Output"
            icon={<Coins className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />}
          />
          <StatCard
            title="Total Cost"
            value={formatCurrency(usageData.total_cost)}
            subtitle="Based on model usage"
            icon={<DollarSign className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />}
          />
          <StatCard
            title="Requests"
            value={usageData.request_count}
            subtitle="Queries processed"
            icon={<MessageSquare className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />}
          />
          <StatCard
            title="Remaining"
            value={formatNumber(usageData.remaining_tokens)}
            subtitle="Tokens available"
            icon={<Zap className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />}
          />
        </div>

      </div>
    </DashboardLayout>
  );
};

export default Usage;
