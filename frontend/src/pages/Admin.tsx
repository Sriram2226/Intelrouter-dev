import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Progress } from "@/components/ui/progress";
import { 
  Users, 
  MessageSquare, 
  Coins, 
  DollarSign,
  TrendingUp,
  PieChart,
  Route
} from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  trend?: number;
  description?: string;
}

const MetricCard = ({ title, value, icon, trend, description }: MetricCardProps) => (
  <div className="bg-card border border-border rounded-xl p-4 sm:p-6">
    <div className="flex items-start justify-between">
      <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-primary/10 flex items-center justify-center">
        {icon}
      </div>
      {trend !== undefined && (
        <div className={`flex items-center gap-1 text-xs font-medium ${trend >= 0 ? 'text-easy' : 'text-hard'}`}>
          <TrendingUp className={`w-3 h-3 ${trend < 0 ? 'rotate-180' : ''}`} />
          {trend > 0 ? '+' : ''}{trend}%
        </div>
      )}
    </div>
    <div className="mt-3 sm:mt-4">
      <p className="text-xl sm:text-3xl font-semibold text-foreground">{value}</p>
      <p className="text-xs sm:text-sm text-muted-foreground mt-1">{title}</p>
      {description && (
        <p className="text-xs text-muted-foreground mt-0.5 hidden sm:block">{description}</p>
      )}
    </div>
  </div>
);

const Admin = () => {
  // Mock metrics data
  const metrics = {
    total_users: 1247,
    total_queries: 45892,
    total_tokens: 12450000,
    total_cost: 124.50,
  };

  // Mock cost breakdown
  const costBreakdown = [
    { label: "EASY", cost: 12.40, percentage: 10, color: "bg-easy" },
    { label: "MEDIUM", cost: 49.80, percentage: 40, color: "bg-medium" },
    { label: "HARD", cost: 62.30, percentage: 50, color: "bg-hard" },
  ];

  // Mock routing stats
  const routingStats = [
    { label: "Algorithmic", count: 32124, percentage: 70, color: "bg-primary" },
    { label: "ML Model", count: 11018, percentage: 24, color: "bg-secondary" },
    { label: "User Override", count: 2750, percentage: 6, color: "bg-accent" },
  ];

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
  };

  const formatCurrency = (num: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(num);
  };

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto space-y-4 sm:space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-xl sm:text-2xl font-semibold text-foreground">Admin Dashboard</h1>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            System-wide metrics and analytics
          </p>
        </div>

        {/* Main Metrics */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <MetricCard
            title="Total Users"
            value={formatNumber(metrics.total_users)}
            icon={<Users className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />}
            trend={8}
          />
          <MetricCard
            title="Total Queries"
            value={formatNumber(metrics.total_queries)}
            icon={<MessageSquare className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />}
            trend={15}
          />
          <MetricCard
            title="Total Tokens"
            value={formatNumber(metrics.total_tokens)}
            icon={<Coins className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />}
            description="All time usage"
          />
          <MetricCard
            title="Total Revenue"
            value={formatCurrency(metrics.total_cost)}
            icon={<DollarSign className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />}
            trend={12}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
          {/* Cost Breakdown */}
          <div className="bg-card border border-border rounded-xl p-4 sm:p-6">
            <div className="flex items-center gap-3 mb-4 sm:mb-6">
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-primary/10 flex items-center justify-center">
                <PieChart className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />
              </div>
              <div>
                <h3 className="text-base sm:text-lg font-medium text-foreground">Cost by Difficulty</h3>
                <p className="text-xs sm:text-sm text-muted-foreground hidden sm:block">Breakdown of costs per difficulty level</p>
              </div>
            </div>

            <div className="space-y-3 sm:space-y-4">
              {costBreakdown.map((item) => (
                <div key={item.label} className="space-y-2">
                  <div className="flex items-center justify-between text-xs sm:text-sm">
                    <span className="font-medium text-foreground">{item.label}</span>
                    <span className="text-muted-foreground">
                      {formatCurrency(item.cost)} ({item.percentage}%)
                    </span>
                  </div>
                  <Progress 
                    value={item.percentage} 
                    className="h-2"
                    style={{ 
                      '--progress-background': `var(--${item.label.toLowerCase()})` 
                    } as React.CSSProperties}
                  />
                </div>
              ))}
            </div>

            <div className="mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-border">
              <div className="flex items-center justify-between">
                <span className="text-xs sm:text-sm text-muted-foreground">Total Cost</span>
                <span className="text-base sm:text-lg font-semibold text-foreground">
                  {formatCurrency(metrics.total_cost)}
                </span>
              </div>
            </div>
          </div>

          {/* Routing Statistics */}
          <div className="bg-card border border-border rounded-xl p-4 sm:p-6">
            <div className="flex items-center gap-3 mb-4 sm:mb-6">
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-primary/10 flex items-center justify-center">
                <Route className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />
              </div>
              <div>
                <h3 className="text-base sm:text-lg font-medium text-foreground">Routing Statistics</h3>
                <p className="text-xs sm:text-sm text-muted-foreground hidden sm:block">How queries are being routed</p>
              </div>
            </div>

            <div className="space-y-3 sm:space-y-4">
              {routingStats.map((item) => (
                <div key={item.label} className="space-y-2">
                  <div className="flex items-center justify-between text-xs sm:text-sm">
                    <span className="font-medium text-foreground">{item.label}</span>
                    <span className="text-muted-foreground">
                      {formatNumber(item.count)} ({item.percentage}%)
                    </span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${item.color} transition-all duration-500`}
                      style={{ width: `${item.percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-border">
              <div className="flex items-center justify-between">
                <span className="text-xs sm:text-sm text-muted-foreground">Total Queries</span>
                <span className="text-base sm:text-lg font-semibold text-foreground">
                  {formatNumber(metrics.total_queries)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Admin;
