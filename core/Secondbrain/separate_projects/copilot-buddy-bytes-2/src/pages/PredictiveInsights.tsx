import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  Shield, 
  Lightbulb,
  CheckCircle,
  XCircle,
  Clock,
  RefreshCw
} from "lucide-react";
import { toast } from "sonner";

export default function PredictiveInsights() {
  const [selectedType, setSelectedType] = useState<string>("all");
  const queryClient = useQueryClient();

  // Fetch insights
  const { data: insights, isLoading } = useQuery({
    queryKey: ["ai-insights"],
    queryFn: async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) throw new Error("No customer ID");

      const { data, error } = await supabase
        .from("ai_insights" as any)
        .select("*")
        .eq("customer_id", profile.customer_id)
        .order("created_at", { ascending: false })
        .limit(50);

      if (error) throw error;
      return data;
    },
  });

  // Generate new insights mutation
  const generateInsightsMutation = useMutation({
    mutationFn: async (analysisType: string) => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) throw new Error("No customer ID");

      const { data, error } = await supabase.functions.invoke('predictive-insights', {
        body: { 
          analysisType,
          customerId: profile.customer_id
        }
      });

      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-insights"] });
      toast.success("AI analysis completed successfully");
    },
    onError: (error: any) => {
      toast.error(`Analysis failed: ${error.message}`);
    },
  });

  // Update insight status mutation
  const updateInsightMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) => {
      const { data: { user } } = await supabase.auth.getUser();
      const { error } = await supabase
        .from("ai_insights" as any)
        .update({ 
          status,
          acknowledged_by: status === 'acknowledged' ? user?.id : undefined,
          acknowledged_at: status === 'acknowledged' ? new Date().toISOString() : undefined,
          resolved_at: status === 'resolved' ? new Date().toISOString() : undefined
        })
        .eq("id", id);

      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-insights"] });
      toast.success("Insight updated");
    },
    onError: (error: any) => {
      toast.error(`Failed to update: ${error.message}`);
    },
  });

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-destructive" />;
      case 'medium':
        return <Clock className="h-5 w-5 text-warning" />;
      default:
        return <Lightbulb className="h-5 w-5 text-primary" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'destructive';
      case 'high':
        return 'destructive';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'risk_prediction':
        return <AlertTriangle className="h-4 w-4" />;
      case 'anomaly_detection':
        return <Shield className="h-4 w-4" />;
      case 'optimization_suggestion':
        return <Lightbulb className="h-4 w-4" />;
      case 'trend_analysis':
        return <TrendingUp className="h-4 w-4" />;
      default:
        return <Brain className="h-4 w-4" />;
    }
  };

  const filteredInsights = insights?.filter(
    (insight: any) => selectedType === "all" || insight.insight_type === selectedType
  );

  const activeInsights = filteredInsights?.filter((i: any) => i.status === 'active');
  const criticalCount = activeInsights?.filter((i: any) => i.severity === 'critical').length || 0;
  const highCount = activeInsights?.filter((i: any) => i.severity === 'high').length || 0;

  return (
    <div className="container mx-auto px-4 pt-56 pb-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Predictive Insights</h1>
          <p className="text-muted-foreground">
            Machine learning-powered analytics and recommendations
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Active Insights</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeInsights?.length || 0}</div>
            <p className="text-xs text-muted-foreground">Requiring attention</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Critical</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-destructive">{criticalCount}</div>
            <p className="text-xs text-muted-foreground">High priority</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">High Risk</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-warning">{highCount}</div>
            <p className="text-xs text-muted-foreground">Needs review</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Avg Confidence</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {insights?.length 
                ? Math.round(insights.reduce((acc: number, i: any) => acc + (i.confidence_score || 0), 0) / insights.length)
                : 0}%
            </div>
            <p className="text-xs text-muted-foreground">Prediction accuracy</p>
          </CardContent>
        </Card>
      </div>

      {/* Generate Insights Section */}
      <Card>
        <CardHeader>
          <CardTitle>Generate New Insights</CardTitle>
          <CardDescription>
            Run AI analysis on different aspects of your infrastructure
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button
              onClick={() => generateInsightsMutation.mutate('change_risk')}
              disabled={generateInsightsMutation.isPending}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Change Risk Analysis
            </Button>
            <Button
              onClick={() => generateInsightsMutation.mutate('cmdb_health')}
              disabled={generateInsightsMutation.isPending}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              CMDB Health Check
            </Button>
            <Button
              onClick={() => generateInsightsMutation.mutate('anomaly_detection')}
              disabled={generateInsightsMutation.isPending}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Anomaly Detection
            </Button>
            <Button
              onClick={() => generateInsightsMutation.mutate('compliance_risk')}
              disabled={generateInsightsMutation.isPending}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Compliance Risk Scan
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Insights List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Insights</CardTitle>
              <CardDescription>AI-generated predictions and recommendations</CardDescription>
            </div>
            <Tabs value={selectedType} onValueChange={setSelectedType}>
              <TabsList>
                <TabsTrigger value="all">All</TabsTrigger>
                <TabsTrigger value="risk_prediction">Risk</TabsTrigger>
                <TabsTrigger value="anomaly_detection">Anomalies</TabsTrigger>
                <TabsTrigger value="optimization_suggestion">Optimize</TabsTrigger>
              </TabsList>
            </Tabs>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p>Loading insights...</p>
          ) : filteredInsights && filteredInsights.length > 0 ? (
            <div className="space-y-4">
              {filteredInsights.map((insight: any) => (
                <Alert key={insight.id} className="relative">
                  <div className="flex items-start gap-4">
                    <div className="mt-1">{getSeverityIcon(insight.severity)}</div>
                    <div className="flex-1 space-y-2">
                      <div className="flex items-start justify-between">
                        <div>
                          <AlertTitle className="flex items-center gap-2">
                            {insight.title}
                            <Badge variant={getSeverityColor(insight.severity) as any}>
                              {insight.severity}
                            </Badge>
                            <Badge variant="outline" className="gap-1">
                              {getTypeIcon(insight.insight_type)}
                              {insight.insight_type.replace(/_/g, ' ')}
                            </Badge>
                          </AlertTitle>
                          <div className="text-xs text-muted-foreground mt-1">
                            {insight.confidence_score}% confidence • {new Date(insight.created_at).toLocaleString()}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          {insight.status === 'active' && (
                            <>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => updateInsightMutation.mutate({ 
                                  id: insight.id, 
                                  status: 'acknowledged' 
                                })}
                              >
                                <CheckCircle className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => updateInsightMutation.mutate({ 
                                  id: insight.id, 
                                  status: 'dismissed' 
                                })}
                              >
                                <XCircle className="h-4 w-4" />
                              </Button>
                            </>
                          )}
                          {insight.status !== 'active' && (
                            <Badge variant="secondary">{insight.status}</Badge>
                          )}
                        </div>
                      </div>
                      <AlertDescription className="text-sm">
                        {insight.description}
                      </AlertDescription>
                      {insight.recommendations && insight.recommendations.length > 0 && (
                        <div className="mt-3 space-y-1">
                          <div className="text-sm font-medium">Recommendations:</div>
                          <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                            {insight.recommendations.map((rec: string, idx: number) => (
                              <li key={idx}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                </Alert>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              <Brain className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No insights yet. Generate your first AI analysis above.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}