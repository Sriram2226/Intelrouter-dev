import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Loader2, TrendingUp, Calendar } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const AdminMetrics = () => {
  const [days, setDays] = useState(30);

  const { data, isLoading, error } = useQuery({
    queryKey: ['adminUsageOverTime', days],
    queryFn: () => api.getAdminUsageOverTime(days),
  });

  const formatCurrency = (num: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num);
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toLocaleString();
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="max-w-7xl mx-auto space-y-6">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center space-y-4">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
              <p className="text-muted-foreground">Loading usage metrics...</p>
            </div>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="max-w-7xl mx-auto space-y-6">
          <Alert variant="destructive">
            <AlertDescription>
              Failed to load usage metrics. Please try again.
            </AlertDescription>
          </Alert>
        </div>
      </DashboardLayout>
    );
  }

  const usageData = data?.data || [];
  
  // Prepare chart data
  const labels = usageData.map((item: any) => {
    const date = new Date(item.date);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  });

  const tokensData = usageData.map((item: any) => item.tokens);
  const costData = usageData.map((item: any) => item.cost);
  const queriesData = usageData.map((item: any) => item.queries);
  const easyData = usageData.map((item: any) => item.easy);
  const mediumData = usageData.map((item: any) => item.medium);
  const hardData = usageData.map((item: any) => item.hard);

  // Calculate totals for doughnut chart
  const totalEasy = usageData.reduce((sum: number, item: any) => sum + item.easy, 0);
  const totalMedium = usageData.reduce((sum: number, item: any) => sum + item.medium, 0);
  const totalHard = usageData.reduce((sum: number, item: any) => sum + item.hard, 0);

  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        beginAtZero: true,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
    },
  };

  // Tokens over time
  const tokensChartData = {
    labels,
    datasets: [
      {
        label: 'Tokens Used',
        data: tokensData,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  // Cost over time
  const costChartData = {
    labels,
    datasets: [
      {
        label: 'Cost ($)',
        data: costData,
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  // Queries over time
  const queriesChartData = {
    labels,
    datasets: [
      {
        label: 'Queries',
        data: queriesData,
        borderColor: 'rgb(168, 85, 247)',
        backgroundColor: 'rgba(168, 85, 247, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  // Difficulty distribution over time
  const difficultyChartData = {
    labels,
    datasets: [
      {
        label: 'Easy',
        data: easyData,
        backgroundColor: 'rgba(34, 197, 94, 0.8)',
      },
      {
        label: 'Medium',
        data: mediumData,
        backgroundColor: 'rgba(251, 191, 36, 0.8)',
      },
      {
        label: 'Hard',
        data: hardData,
        backgroundColor: 'rgba(239, 68, 68, 0.8)',
      },
    ],
  };

  // Difficulty distribution pie chart
  const difficultyDoughnutData = {
    labels: ['Easy', 'Medium', 'Hard'],
    datasets: [
      {
        data: [totalEasy, totalMedium, totalHard],
        backgroundColor: [
          'rgba(34, 197, 94, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(239, 68, 68, 0.8)',
        ],
        borderColor: [
          'rgb(34, 197, 94)',
          'rgb(251, 191, 36)',
          'rgb(239, 68, 68)',
        ],
        borderWidth: 2,
      },
    ],
  };

  // Calculate summary stats
  const totalTokens = tokensData.reduce((a: number, b: number) => a + b, 0);
  const totalCost = costData.reduce((a: number, b: number) => a + b, 0);
  const totalQueries = queriesData.reduce((a: number, b: number) => a + b, 0);
  const avgTokensPerDay = totalTokens / (days || 1);
  const avgCostPerDay = totalCost / (days || 1);
  const avgQueriesPerDay = totalQueries / (days || 1);

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold text-foreground">Usage Metrics</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Visualize usage statistics and trends over time
            </p>
          </div>
          
          {/* Time Range Selector */}
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 text-muted-foreground" />
            <div className="flex gap-1 bg-muted rounded-lg p-1">
              {[7, 30, 90].map((d) => (
                <Button
                  key={d}
                  variant={days === d ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setDays(d)}
                  className={cn(
                    "text-xs",
                    days === d && "bg-primary text-primary-foreground"
                  )}
                >
                  {d}d
                </Button>
              ))}
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-card border border-border rounded-xl p-4">
            <p className="text-sm text-muted-foreground">Total Tokens</p>
            <p className="text-2xl font-semibold text-foreground mt-1">
              {formatNumber(totalTokens)}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Avg: {formatNumber(avgTokensPerDay)}/day
            </p>
          </div>
          <div className="bg-card border border-border rounded-xl p-4">
            <p className="text-sm text-muted-foreground">Total Cost</p>
            <p className="text-2xl font-semibold text-foreground mt-1">
              {formatCurrency(totalCost)}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Avg: {formatCurrency(avgCostPerDay)}/day
            </p>
          </div>
          <div className="bg-card border border-border rounded-xl p-4">
            <p className="text-sm text-muted-foreground">Total Queries</p>
            <p className="text-2xl font-semibold text-foreground mt-1">
              {formatNumber(totalQueries)}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Avg: {formatNumber(avgQueriesPerDay)}/day
            </p>
          </div>
          <div className="bg-card border border-border rounded-xl p-4">
            <p className="text-sm text-muted-foreground">Avg Cost/Query</p>
            <p className="text-2xl font-semibold text-foreground mt-1">
              {totalQueries > 0 ? formatCurrency(totalCost / totalQueries) : '$0.00'}
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Per query average
            </p>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Tokens Over Time */}
          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Tokens Usage Over Time</h3>
            <div className="h-64">
              <Line data={tokensChartData} options={chartOptions} />
            </div>
          </div>

          {/* Cost Over Time */}
          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Cost Over Time</h3>
            <div className="h-64">
              <Line data={costChartData} options={chartOptions} />
            </div>
          </div>

          {/* Queries Over Time */}
          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Queries Over Time</h3>
            <div className="h-64">
              <Line data={queriesChartData} options={chartOptions} />
            </div>
          </div>

          {/* Difficulty Distribution */}
          <div className="bg-card border border-border rounded-xl p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4">Difficulty Distribution</h3>
            <div className="h-64">
              <Doughnut 
                data={difficultyDoughnutData} 
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'bottom' as const,
                    },
                  },
                }} 
              />
            </div>
          </div>
        </div>

        {/* Difficulty Over Time (Full Width) */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Difficulty Distribution Over Time</h3>
          <div className="h-80">
            <Bar data={difficultyChartData} options={chartOptions} />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default AdminMetrics;

