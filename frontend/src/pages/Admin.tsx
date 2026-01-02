import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Progress } from "@/components/ui/progress";
import { 
  Users, 
  MessageSquare, 
  Coins, 
  DollarSign,
  TrendingUp,
  PieChart,
  Route,
  Loader2
} from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Alert, AlertDescription } from "@/components/ui/alert";

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
  // Fetch data from backend
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useQuery({
    queryKey: ['adminMetrics'],
    queryFn: () => api.getAdminMetrics(),
  });

  const { data: costs, isLoading: costsLoading, error: costsError } = useQuery({
    queryKey: ['adminCosts'],
    queryFn: () => api.getAdminCosts(),
  });

  const { data: routingStats, isLoading: routingLoading, error: routingError } = useQuery({
    queryKey: ['adminRoutingStats'],
    queryFn: () => api.getAdminRoutingStats(),
  });

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

  // Transform cost data for display
  const costBreakdown = costs ? (() => {
    const totalCost = (costs.EASY?.cost || 0) + (costs.MEDIUM?.cost || 0) + (costs.HARD?.cost || 0);
    const easyCost = costs.EASY?.cost || 0;
    const mediumCost = costs.MEDIUM?.cost || 0;
    const hardCost = costs.HARD?.cost || 0;
    
    return [
      { 
        label: "EASY", 
        cost: easyCost, 
        percentage: totalCost > 0 ? Math.round((easyCost / totalCost) * 100) : 0, 
        color: "bg-easy" 
      },
      { 
        label: "MEDIUM", 
        cost: mediumCost, 
        percentage: totalCost > 0 ? Math.round((mediumCost / totalCost) * 100) : 0, 
        color: "bg-medium" 
      },
      { 
        label: "HARD", 
        cost: hardCost, 
        percentage: totalCost > 0 ? Math.round((hardCost / totalCost) * 100) : 0, 
        color: "bg-hard" 
      },
    ];
  })() : [];

  // Transform routing stats for display
  const routingStatsDisplay = routingStats ? (() => {
    const totalQueries = (routingStats.routing_sources?.algorithmic || 0) + 
                        (routingStats.routing_sources?.ml || 0) + 
                        (routingStats.routing_sources?.user_override || 0);
    
    const algorithmic = routingStats.routing_sources?.algorithmic || 0;
    const ml = routingStats.routing_sources?.ml || 0;
    const userOverride = routingStats.routing_sources?.user_override || 0;
    
    return [
      { 
        label: "Algorithmic", 
        count: algorithmic, 
        percentage: totalQueries > 0 ? Math.round((algorithmic / totalQueries) * 100) : 0, 
        color: "bg-primary" 
      },
      { 
        label: "ML Model", 
        count: ml, 
        percentage: totalQueries > 0 ? Math.round((ml / totalQueries) * 100) : 0, 
        color: "bg-secondary" 
      },
      { 
        label: "User Override", 
        count: userOverride, 
        percentage: totalQueries > 0 ? Math.round((userOverride / totalQueries) * 100) : 0, 
        color: "bg-accent" 
      },
    ];
  })() : [];

  const isLoading = metricsLoading || costsLoading || routingLoading;
  const hasError = metricsError || costsError || routingError;

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="max-w-6xl mx-auto space-y-4 sm:space-y-8">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center space-y-4">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
              <p className="text-muted-foreground">Loading admin data...</p>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (hasError) {
    return (
      <DashboardLayout>
        <div className="max-w-6xl mx-auto space-y-4 sm:space-y-8">
          <Alert variant="destructive">
            <AlertDescription>
              Failed to load admin data. Please check your connection and try again.
              {metricsError && <div className="mt-2">Metrics: {metricsError.message}</div>}
              {costsError && <div className="mt-2">Costs: {costsError.message}</div>}
              {routingError && <div className="mt-2">Routing Stats: {routingError.message}</div>}
            </AlertDescription>
          </Alert>
        </div>
      </DashboardLayout>
    );
  }

  const totalCost = metrics?.total_cost || 0;

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
            value={formatNumber(metrics?.total_users || 0)}
            icon={<Users className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />}
          />
          <MetricCard
            title="Total Queries"
            value={formatNumber(metrics?.total_queries || 0)}
            icon={<MessageSquare className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />}
          />
          <MetricCard
            title="Total Tokens"
            value={formatNumber(metrics?.total_tokens || 0)}
            icon={<Coins className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />}
            description="All time usage"
          />
          <MetricCard
            title="Total Revenue"
            value={formatCurrency(totalCost)}
            icon={<DollarSign className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />}
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
              {costBreakdown.length > 0 ? (
                costBreakdown.map((item) => (
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
                ))
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">No cost data available</p>
              )}
            </div>

            <div className="mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-border">
              <div className="flex items-center justify-between">
                <span className="text-xs sm:text-sm text-muted-foreground">Total Cost</span>
                <span className="text-base sm:text-lg font-semibold text-foreground">
                  {formatCurrency(totalCost)}
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
              {routingStatsDisplay.length > 0 ? (
                routingStatsDisplay.map((item) => (
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
                ))
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">No routing data available</p>
              )}
            </div>

            <div className="mt-4 sm:mt-6 pt-3 sm:pt-4 border-t border-border">
              <div className="flex items-center justify-between">
                <span className="text-xs sm:text-sm text-muted-foreground">Total Queries</span>
                <span className="text-base sm:text-lg font-semibold text-foreground">
                  {formatNumber(metrics?.total_queries || 0)}
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
