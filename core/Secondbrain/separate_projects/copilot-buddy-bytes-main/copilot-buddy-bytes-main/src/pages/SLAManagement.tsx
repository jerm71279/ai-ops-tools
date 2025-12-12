import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { AlertTriangle, CheckCircle, Clock, TrendingUp, AlertCircle } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const SLAManagement = () => {
  const { toast } = useToast();
  const [selectedTab, setSelectedTab] = useState("overview");

  // Fetch SLA definitions
  const { data: slaDefinitions } = useQuery({
    queryKey: ["sla-definitions"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("sla_definitions" as any)
        .select("*")
        .eq("is_active", true)
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data as any[];
    },
  });

  // Fetch active SLA metrics
  const { data: activeMetrics } = useQuery({
    queryKey: ["sla-metrics-active"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("sla_metrics" as any)
        .select("*")
        .eq("status", "active")
        .order("start_time", { ascending: false })
        .limit(20);
      if (error) throw error;
      return data as any[];
    },
  });

  // Fetch recent breaches
  const { data: recentBreaches } = useQuery({
    queryKey: ["sla-breaches-recent"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("sla_breaches" as any)
        .select("*")
        .order("breach_start", { ascending: false })
        .limit(10);
      if (error) throw error;
      return data as any[];
    },
  });

  // Calculate SLA compliance rate
  const complianceRate = activeMetrics
    ? ((activeMetrics.filter(m => !m.is_breached).length / activeMetrics.length) * 100).toFixed(1)
    : 0;

  const activeBreaches = recentBreaches?.filter(b => !b.resolved_at).length || 0;

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">SLA Management</h1>
            <p className="text-muted-foreground">Track service level agreements and performance metrics</p>
          </div>
          <Button>
            <Clock className="mr-2 h-4 w-4" />
            New SLA Definition
          </Button>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Compliance Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{complianceRate}%</div>
              <Progress value={Number(complianceRate)} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Active SLAs</CardTitle>
              <CheckCircle className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{slaDefinitions?.length || 0}</div>
              <p className="text-xs text-muted-foreground mt-1">Definitions configured</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Active Breaches</CardTitle>
              <AlertTriangle className="h-4 w-4 text-destructive" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">{activeBreaches}</div>
              <p className="text-xs text-muted-foreground mt-1">Require attention</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Tracking Now</CardTitle>
              <Clock className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{activeMetrics?.length || 0}</div>
              <p className="text-xs text-muted-foreground mt-1">Active timers</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs value={selectedTab} onValueChange={setSelectedTab}>
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="definitions">SLA Definitions</TabsTrigger>
            <TabsTrigger value="active">Active Tracking</TabsTrigger>
            <TabsTrigger value="breaches">Breaches</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent SLA Activity</CardTitle>
                <CardDescription>Latest SLA metrics and breach events</CardDescription>
              </CardHeader>
              <CardContent>
                {activeMetrics && activeMetrics.length > 0 ? (
                  <div className="space-y-3">
                    {activeMetrics.slice(0, 5).map((metric) => (
                      <div key={metric.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          {metric.is_breached ? (
                            <AlertCircle className="h-5 w-5 text-destructive" />
                          ) : (
                            <CheckCircle className="h-5 w-5 text-success" />
                          )}
                          <div>
                            <p className="font-medium">SLA Metric #{metric.id.slice(0, 8)}</p>
                            <p className="text-sm text-muted-foreground">
                              Target: {metric.target_value} min | Actual: {metric.actual_value || "In progress"}
                            </p>
                          </div>
                        </div>
                        <Badge variant={metric.is_breached ? "destructive" : "default"}>
                          {metric.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">No active SLA metrics</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="definitions" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>SLA Definitions</CardTitle>
                <CardDescription>Configured service level agreements and targets</CardDescription>
              </CardHeader>
              <CardContent>
                {slaDefinitions && slaDefinitions.length > 0 ? (
                  <div className="space-y-3">
                    {slaDefinitions.map((sla) => (
                      <div key={sla.id} className="p-4 border rounded-lg">
                        <div className="flex items-start justify-between">
                          <div>
                            <h3 className="font-semibold text-lg">{sla.sla_name}</h3>
                            <p className="text-sm text-muted-foreground mt-1">Type: {sla.sla_type}</p>
                            <div className="flex items-center gap-2 mt-2">
                              <Badge>{sla.priority}</Badge>
                              <span className="text-sm">Target: {sla.target_value} {sla.sla_type === 'uptime' ? '%' : 'min'}</span>
                            </div>
                          </div>
                          <Button variant="outline" size="sm">Edit</Button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">No SLA definitions configured</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="active" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Active SLA Tracking</CardTitle>
                <CardDescription>Currently monitoring these service levels</CardDescription>
              </CardHeader>
              <CardContent>
                {activeMetrics && activeMetrics.length > 0 ? (
                  <div className="space-y-3">
                    {activeMetrics.map((metric) => {
                      const elapsed = metric.actual_value || 0;
                      const percentage = (elapsed / metric.target_value) * 100;
                      
                      return (
                        <div key={metric.id} className="p-4 border rounded-lg space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="font-medium">Metric #{metric.id.slice(0, 8)}</span>
                            <Badge variant={metric.is_breached ? "destructive" : "default"}>
                              {metric.status}
                            </Badge>
                          </div>
                          <Progress value={Math.min(percentage, 100)} />
                          <div className="flex justify-between text-sm text-muted-foreground">
                            <span>Elapsed: {elapsed} min</span>
                            <span>Target: {metric.target_value} min</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">No active tracking</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="breaches" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>SLA Breaches</CardTitle>
                <CardDescription>Service level violations and corrective actions</CardDescription>
              </CardHeader>
              <CardContent>
                {recentBreaches && recentBreaches.length > 0 ? (
                  <div className="space-y-3">
                    {recentBreaches.map((breach) => (
                      <div key={breach.id} className="p-4 border border-destructive/50 rounded-lg bg-destructive/5">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <AlertTriangle className="h-5 w-5 text-destructive" />
                            <div>
                              <p className="font-semibold">{breach.breach_type.toUpperCase()} Breach</p>
                              <p className="text-sm text-muted-foreground">
                                {new Date(breach.breach_start).toLocaleString()}
                              </p>
                            </div>
                          </div>
                          <Badge variant="destructive">{breach.severity}</Badge>
                        </div>
                        <div className="space-y-1 text-sm">
                          <p>Target: {breach.target_value} | Actual: {breach.actual_value}</p>
                          <p className="text-destructive font-medium">Over by: {breach.breach_amount} ({breach.breach_percentage?.toFixed(1)}%)</p>
                          {breach.root_cause && <p className="text-muted-foreground">Cause: {breach.root_cause}</p>}
                        </div>
                        {!breach.resolved_at && (
                          <Button variant="outline" size="sm" className="mt-3">
                            Acknowledge
                          </Button>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-muted-foreground py-8">No breaches recorded</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default SLAManagement;
