import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { Loader2, Brain, TrendingUp, Database, Activity } from "lucide-react";
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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

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

const MLPipeline = () => {
  const { data, isLoading, error } = useQuery({
    queryKey: ['mlPipeline'],
    queryFn: () => api.getMLPipelineInfo(),
  });

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="max-w-7xl mx-auto space-y-6">
          <div className="flex items-center justify-center min-h-[400px]">
            <div className="text-center space-y-4">
              <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
              <p className="text-muted-foreground">Loading ML pipeline info...</p>
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
              Failed to load ML pipeline info. Please try again.
            </AlertDescription>
          </Alert>
        </div>
      </DashboardLayout>
    );
  }

  const pipelineData = data || {};
  const activeModel = pipelineData.active_model;
  const allModels = pipelineData.all_models || [];
  const trainingData = pipelineData.training_data || {};
  const routingStats = pipelineData.routing_stats || {};

  // Format date
  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  // Model version history chart
  const modelHistoryData = {
    labels: allModels.map((m: any) => m.version || 'Unknown'),
    datasets: [
      {
        label: 'Accuracy',
        data: allModels.map((m: any) => (m.accuracy || 0) * 100),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        yAxisID: 'y',
      },
      {
        label: 'F1 Score',
        data: allModels.map((m: any) => (m.f1_score || 0) * 100),
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        yAxisID: 'y',
      },
    ],
  };

  // Training data growth
  const growthData = trainingData.growth_over_time || [];
  const trainingGrowthData = {
    labels: growthData.map((item: any) => {
      const date = new Date(item.date);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }),
    datasets: [
      {
        label: 'Training Samples Added',
        data: growthData.map((item: any) => item.count),
        borderColor: 'rgb(168, 85, 247)',
        backgroundColor: 'rgba(168, 85, 247, 0.1)',
        tension: 0.4,
        fill: true,
      },
    ],
  };

  // Training data by difficulty
  const difficultyData = trainingData.by_difficulty || {};
  const difficultyDoughnutData = {
    labels: ['Easy', 'Medium', 'Hard'],
    datasets: [
      {
        data: [
          difficultyData.EASY || 0,
          difficultyData.MEDIUM || 0,
          difficultyData.HARD || 0,
        ],
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

  // Routing source distribution
  const routingSources = routingStats.by_source || {};
  const routingData = {
    labels: Object.keys(routingSources),
    datasets: [
      {
        label: 'Queries',
        data: Object.values(routingSources),
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',
          'rgba(34, 197, 94, 0.8)',
          'rgba(251, 191, 36, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(168, 85, 247, 0.8)',
        ],
        borderWidth: 2,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function(value: any) {
            return value + '%';
          },
        },
      },
    },
  };

  return (
    <DashboardLayout>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-semibold text-foreground flex items-center gap-2">
            <Brain className="w-6 h-6" />
            ML Model Pipeline
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Overview of ML model training, performance, and routing statistics
          </p>
        </div>

        {/* Active Model Card */}
        {activeModel && (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="w-5 h-5" />
                    Active Model
                  </CardTitle>
                  <CardDescription>
                    Currently deployed model version
                  </CardDescription>
                </div>
                <Badge variant="default" className="bg-green-500">
                  Active
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Version</p>
                  <p className="text-lg font-semibold">{activeModel.version}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Accuracy</p>
                  <p className="text-lg font-semibold">
                    {(activeModel.accuracy * 100).toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">F1 Score</p>
                  <p className="text-lg font-semibold">
                    {(activeModel.f1_score * 100).toFixed(2)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Confidence Threshold</p>
                  <p className="text-lg font-semibold">
                    {activeModel.confidence_threshold}
                  </p>
                </div>
                <div className="col-span-2 md:col-span-4">
                  <p className="text-sm text-muted-foreground">Trained On</p>
                  <p className="text-sm">
                    {formatDate(activeModel.training_timestamp)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Summary Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Training Samples</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Database className="w-5 h-5 text-muted-foreground" />
                <p className="text-2xl font-semibold">
                  {trainingData.total || 0}
                </p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Model Versions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Brain className="w-5 h-5 text-muted-foreground" />
                <p className="text-2xl font-semibold">
                  {allModels.length}
                </p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Queries Routed</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-muted-foreground" />
                <p className="text-2xl font-semibold">
                  {routingStats.total_queries || 0}
                </p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>ML Routing Rate</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-muted-foreground" />
                <p className="text-2xl font-semibold">
                  {routingStats.total_queries > 0
                    ? ((routingSources.ml || 0) / routingStats.total_queries * 100).toFixed(1)
                    : 0}%
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Model Performance History */}
          <Card>
            <CardHeader>
              <CardTitle>Model Performance History</CardTitle>
              <CardDescription>Accuracy and F1 Score by version</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <Line data={modelHistoryData} options={chartOptions} />
              </div>
            </CardContent>
          </Card>

          {/* Training Data Growth */}
          <Card>
            <CardHeader>
              <CardTitle>Training Data Growth</CardTitle>
              <CardDescription>Samples added over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <Line data={trainingGrowthData} options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  plugins: {
                    legend: {
                      position: 'top' as const,
                    },
                  },
                }} />
              </div>
            </CardContent>
          </Card>

          {/* Training Data Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Training Data Distribution</CardTitle>
              <CardDescription>By difficulty level</CardDescription>
            </CardHeader>
            <CardContent>
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
            </CardContent>
          </Card>

          {/* Routing Source Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Routing Source Distribution</CardTitle>
              <CardDescription>ML vs Algorithmic routing</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-64">
                <Bar 
                  data={routingData} 
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                      legend: {
                        display: false,
                      },
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                      },
                    },
                  }} 
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Model Versions Table */}
        {allModels.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>All Model Versions</CardTitle>
              <CardDescription>Complete training history</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b">
                      <th className="text-left p-2">Version</th>
                      <th className="text-left p-2">Accuracy</th>
                      <th className="text-left p-2">F1 Score</th>
                      <th className="text-left p-2">Status</th>
                      <th className="text-left p-2">Trained On</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allModels.map((model: any, idx: number) => (
                      <tr key={idx} className="border-b">
                        <td className="p-2 font-mono text-sm">{model.version}</td>
                        <td className="p-2">{(model.accuracy * 100).toFixed(2)}%</td>
                        <td className="p-2">{(model.f1_score * 100).toFixed(2)}%</td>
                        <td className="p-2">
                          {model.is_active ? (
                            <Badge variant="default" className="bg-green-500">Active</Badge>
                          ) : (
                            <Badge variant="secondary">Inactive</Badge>
                          )}
                        </td>
                        <td className="p-2 text-sm text-muted-foreground">
                          {formatDate(model.training_timestamp)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
};

export default MLPipeline;

