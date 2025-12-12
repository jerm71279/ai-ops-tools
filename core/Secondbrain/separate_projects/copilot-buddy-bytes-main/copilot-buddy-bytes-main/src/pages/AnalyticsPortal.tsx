import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { DashboardSettingsMenu } from "@/components/DashboardSettingsMenu";

import { toast } from "sonner";
import { 
  BarChart3, 
  TrendingUp, 
  AlertCircle, 
  Activity, 
  FileText,
  RefreshCw,
  Bell,
  Target
} from "lucide-react";

export default function AnalyticsPortal() {
  const [period, setPeriod] = useState("daily");
  const [customerId, setCustomerId] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (user) {
        const { data: profile } = await supabase
          .from('user_profiles')
          .select('customer_id')
          .eq('user_id', user.id)
          .single();
        
        if (profile?.customer_id) {
          setCustomerId(profile.customer_id);
        }
      }
    };
    fetchUser();
  }, []);

  const { data: metrics, refetch: refetchMetrics } = useQuery({
    queryKey: ['system-metrics', customerId, period],
    enabled: !!customerId,
    queryFn: async () => {
      const { data, error } = await supabase
        .from('system_metrics' as any)
        .select('*')
        .eq('customer_id', customerId)
        .eq('aggregation_period', period)
        .order('period_start', { ascending: false })
        .limit(100);
      if (error) throw error;
      return data;
    },
  });

  const { data: alerts } = useQuery({
    queryKey: ['network-alerts', customerId],
    enabled: !!customerId,
    refetchInterval: 30000,
    queryFn: async () => {
      const { data, error } = await supabase
        .from('network_alerts' as any)
        .select('*')
        .eq('customer_id', customerId)
        .eq('is_resolved', false)
        .order('created_at', { ascending: false })
        .limit(50);
      if (error) throw error;
      return data;
    },
  });

  const { data: benchmarks } = useQuery({
    queryKey: ['performance-benchmarks', customerId],
    enabled: !!customerId,
    queryFn: async () => {
      const { data, error } = await supabase
        .from('performance_benchmarks' as any)
        .select('*')
        .eq('customer_id', customerId)
        .order('benchmark_category');
      if (error) throw error;
      return data;
    },
  });

  const { data: reports } = useQuery({
    queryKey: ['generated-reports', customerId],
    enabled: !!customerId,
    queryFn: async () => {
      const { data, error } = await supabase
        .from('generated_reports' as any)
        .select('*')
        .eq('customer_id', customerId)
        .order('generated_at', { ascending: false })
        .limit(20);
      if (error) throw error;
      return data;
    },
  });

  const aggregateMetricsMutation = useMutation({
    mutationFn: async () => {
      const { data, error } = await supabase.functions.invoke('analytics-processor', {
        body: { action: 'aggregate_metrics', period, customerId }
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      toast.success('Metrics aggregated successfully');
      refetchMetrics();
    },
    onError: (error) => {
      toast.error(`Failed to aggregate metrics: ${error.message}`);
    },
  });

  const generateReportMutation = useMutation({
    mutationFn: async () => {
      const { data, error } = await supabase.functions.invoke('analytics-processor', {
        body: { action: 'generate_report', customerId }
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      toast.success('Report generated successfully');
    },
    onError: (error) => {
      toast.error(`Failed to generate report: ${error.message}`);
    },
  });

  const checkBenchmarksMutation = useMutation({
    mutationFn: async () => {
      const { data, error } = await supabase.functions.invoke('analytics-processor', {
        body: { action: 'check_benchmarks', customerId }
      });
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      toast.success('Benchmarks checked successfully');
    },
    onError: (error) => {
      toast.error(`Failed to check benchmarks: ${error.message}`);
    },
  });

  const acknowledgeAlertMutation = useMutation({
    mutationFn: async (alertId: string) => {
      const { data: { user } } = await supabase.auth.getUser();
      const { error } = await supabase
        .from('real_time_alerts' as any)
        .update({
          is_acknowledged: true,
          acknowledged_by: user?.id,
          acknowledged_at: new Date().toISOString(),
        })
        .eq('id', alertId);
      if (error) throw error;
    },
    onSuccess: () => {
      toast.success('Alert acknowledged');
    },
  });

  const getMetricsByType = (type: string) => {
    return metrics?.filter((m: any) => m.metric_type === type) || [];
  };

  const criticalAlerts = alerts?.filter((a: any) => a.alert_severity === 'critical').length || 0;
  const unmetBenchmarks = benchmarks?.filter((b: any) => b.status === 'not_met').length || 0;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 pb-8" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold">Analytics Portal</h1>
            <p className="text-muted-foreground mt-2">
              Real-time monitoring and comprehensive reporting
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Select value={period} onValueChange={setPeriod}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="daily">Daily</SelectItem>
                <SelectItem value="weekly">Weekly</SelectItem>
                <SelectItem value="monthly">Monthly</SelectItem>
              </SelectContent>
            </Select>
            <DashboardSettingsMenu dashboardName="Analytics" />
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Metrics</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics?.length || 0}</div>
              <p className="text-xs text-muted-foreground">Tracked data points</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Active Alerts</CardTitle>
              <Bell className="h-4 w-4 text-destructive" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{alerts?.length || 0}</div>
              <p className="text-xs text-muted-foreground">
                {criticalAlerts} critical
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Benchmarks</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{benchmarks?.length || 0}</div>
              <p className="text-xs text-muted-foreground">
                {unmetBenchmarks} not met
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Reports</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{reports?.length || 0}</div>
              <p className="text-xs text-muted-foreground">Generated</p>
            </CardContent>
          </Card>
        </div>

        {/* Actions */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Run analytics operations</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-4">
            <Button
              onClick={() => {
                if (!customerId) {
                  toast.error('Please assign a customer to your profile first');
                  return;
                }
                aggregateMetricsMutation.mutate();
              }}
              disabled={aggregateMetricsMutation.isPending}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Aggregate Metrics
            </Button>
            <Button
              onClick={() => {
                if (!customerId) {
                  toast.error('Please assign a customer to your profile first');
                  return;
                }
                generateReportMutation.mutate();
              }}
              disabled={generateReportMutation.isPending}
              variant="outline"
            >
              <FileText className="h-4 w-4 mr-2" />
              Generate Report
            </Button>
            <Button
              onClick={() => {
                if (!customerId) {
                  toast.error('Please assign a customer to your profile first');
                  return;
                }
                checkBenchmarksMutation.mutate();
              }}
              disabled={checkBenchmarksMutation.isPending}
              variant="outline"
            >
              <Target className="h-4 w-4 mr-2" />
              Check Benchmarks
            </Button>
          </CardContent>
        </Card>

        <Tabs defaultValue="metrics" className="space-y-6">
          <TabsList>
            <TabsTrigger value="metrics">Metrics</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
            <TabsTrigger value="benchmarks">Benchmarks</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
          </TabsList>

          <TabsContent value="metrics">
            <Card>
              <CardHeader>
                <CardTitle>System Metrics</CardTitle>
                <CardDescription>Aggregated performance metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {['change_management', 'cmdb', 'workflow'].map((type) => {
                    const typeMetrics = getMetricsByType(type);
                    if (typeMetrics.length === 0) return null;

                    return (
                      <div key={type} className="space-y-2">
                        <h3 className="font-semibold capitalize">{type.replace('_', ' ')}</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          {typeMetrics.map((metric: any) => (
                            <Card key={metric.id}>
                              <CardContent className="pt-6">
                                <div className="flex items-center justify-between">
                                  <div>
                                    <p className="text-sm text-muted-foreground">
                                      {metric.metric_name.replace(/_/g, ' ')}
                                    </p>
                                    <p className="text-2xl font-bold">
                                      {metric.metric_value.toFixed(1)}
                                      {metric.metric_unit && <span className="text-sm ml-1">{metric.metric_unit}</span>}
                                    </p>
                                  </div>
                                  <Activity className="h-8 w-8 text-muted-foreground" />
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="alerts">
            <Card>
              <CardHeader>
                <CardTitle>Real-Time Alerts</CardTitle>
                <CardDescription>Active system alerts</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {alerts && alerts.length > 0 ? (
                    alerts.map((alert: any) => (
                      <Card key={alert.id}>
                        <CardContent className="pt-6">
                          <div className="flex items-start justify-between">
                            <div className="flex items-start gap-4">
                              <AlertCircle className={`h-5 w-5 mt-1 ${
                                alert.alert_severity === 'critical' ? 'text-destructive' :
                                alert.alert_severity === 'high' ? 'text-orange-500' :
                                'text-yellow-500'
                              }`} />
                              <div>
                                <div className="flex items-center gap-2 mb-2">
                                  <h4 className="font-semibold">{alert.alert_title}</h4>
                                  <Badge variant={
                                    alert.alert_severity === 'critical' ? 'destructive' : 'secondary'
                                  }>
                                    {alert.alert_severity}
                                  </Badge>
                                </div>
                                <p className="text-sm text-muted-foreground mb-2">
                                  {alert.alert_message}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  {new Date(alert.created_at).toLocaleString()}
                                </p>
                              </div>
                            </div>
                            {!alert.is_acknowledged && (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => acknowledgeAlertMutation.mutate(alert.id)}
                              >
                                Acknowledge
                              </Button>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    <p className="text-center text-muted-foreground py-8">
                      No active alerts
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="benchmarks">
            <Card>
              <CardHeader>
                <CardTitle>Performance Benchmarks</CardTitle>
                <CardDescription>Track performance targets</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {benchmarks && benchmarks.length > 0 ? (
                    benchmarks.map((benchmark: any) => (
                      <Card key={benchmark.id}>
                        <CardContent className="pt-6">
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-semibold">{benchmark.benchmark_name}</h4>
                              <p className="text-sm text-muted-foreground">
                                Category: {benchmark.benchmark_category}
                              </p>
                              <div className="flex items-center gap-4 mt-2">
                                <span className="text-sm">
                                  Target: {benchmark.target_value} {benchmark.unit}
                                </span>
                                {benchmark.current_value && (
                                  <span className="text-sm">
                                    Current: {benchmark.current_value} {benchmark.unit}
                                  </span>
                                )}
                              </div>
                            </div>
                            <Badge variant={benchmark.status === 'met' ? 'default' : 'destructive'}>
                              {benchmark.status}
                            </Badge>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    <p className="text-center text-muted-foreground py-8">
                      No benchmarks configured
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reports">
            <Card>
              <CardHeader>
                <CardTitle>Generated Reports</CardTitle>
                <CardDescription>Historical reports</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {reports && reports.length > 0 ? (
                    reports.map((report: any) => (
                      <Card key={report.id}>
                        <CardContent className="pt-6">
                          <div className="flex items-start justify-between">
                            <div>
                              <h4 className="font-semibold">{report.report_name}</h4>
                              <p className="text-sm text-muted-foreground">
                                Type: {report.report_type}
                              </p>
                              <p className="text-xs text-muted-foreground mt-1">
                                Generated: {new Date(report.generated_at).toLocaleString()}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                Period: {new Date(report.report_period_start).toLocaleDateString()} - {new Date(report.report_period_end).toLocaleDateString()}
                              </p>
                            </div>
                            <Badge>{report.status}</Badge>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    <p className="text-center text-muted-foreground py-8">
                      No reports generated yet
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}