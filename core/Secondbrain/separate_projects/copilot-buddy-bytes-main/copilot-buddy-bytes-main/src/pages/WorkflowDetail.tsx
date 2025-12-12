import { useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ArrowLeft, TrendingUp, AlertTriangle, Lightbulb, Activity, CheckCircle, XCircle, Clock } from "lucide-react";
import { toast } from "sonner";
import { useDemoMode } from "@/hooks/useDemoMode";

interface WorkflowExecution {
  id: string;
  workflow_id: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  execution_log: any;
  triggered_by: string;
  error_message: string | null;
  workflows?: {
    workflow_name: string;
    description: string | null;
  };
}

interface AIInsight {
  prediction: string;
  confidence: number;
  recommendations: string[];
  risk_factors: string[];
  optimization_opportunities: string[];
}

const WorkflowDetail = () => {
  const navigate = useNavigate();
  const { workflowType } = useParams();
  const [searchParams] = useSearchParams();
  const metricName = searchParams.get("metric") || workflowType;
  const department = searchParams.get("department") || "operations";
  
  const isPreviewMode = useDemoMode();
  const [isLoading, setIsLoading] = useState(true);
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [aiInsights, setAIInsights] = useState<AIInsight | null>(null);
  const [isLoadingInsights, setIsLoadingInsights] = useState(false);

  useEffect(() => {
    console.log("🔍 WorkflowDetail mounted:", { workflowType, metricName, department });
    loadWorkflowData();
    generateAIInsights();
  }, [workflowType]);

  const loadWorkflowData = async () => {
    console.log("📊 Loading workflow executions...");
    try {
      const { data, error } = await supabase
        .from("workflow_executions")
        .select(`
          *,
          workflows(workflow_name, description)
        `)
        .order("started_at", { ascending: false })
        .limit(20);

      if (error) {
        console.error("❌ Error loading workflow data:", error);
        throw error;
      }
      console.log("✅ Loaded workflow executions:", data?.length || 0, "executions");
      setExecutions(data || []);
    } catch (error) {
      console.error("Error loading workflow data:", error);
      toast.error("Failed to load workflow data");
    } finally {
      setIsLoading(false);
    }
  };

  const generateAIInsights = async () => {
    console.log("🤖 Generating AI insights for:", { workflowType, metricName, department });
    setIsLoadingInsights(true);
    try {
      const { data, error } = await supabase.functions.invoke("workflow-insights", {
        body: {
          workflowType,
          metricName,
          department
        }
      });

      if (error) {
        console.error("❌ Error from workflow-insights function:", error);
        throw error;
      }
      console.log("✅ AI insights generated successfully:", data);
      setAIInsights(data.insights);
    } catch (error) {
      console.error("Error generating insights:", error);
      toast.error("Failed to generate AI insights");
    } finally {
      setIsLoadingInsights(false);
    }
  };

  const getSuccessRate = () => {
    if (executions.length === 0) return 0;
    const successful = executions.filter(e => e.status === "completed").length;
    return Math.round((successful / executions.length) * 100);
  };

  const getAvgExecutionTime = () => {
    const completed = executions.filter(e => e.completed_at);
    if (completed.length === 0) return "N/A";
    
    const avgMs = completed.reduce((sum, e) => {
      const duration = new Date(e.completed_at!).getTime() - new Date(e.started_at).getTime();
      return sum + duration;
    }, 0) / completed.length;

    return `${(avgMs / 1000 / 60).toFixed(1)} min`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed": return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "failed": return <XCircle className="h-4 w-4 text-red-500" />;
      case "running": return <Activity className="h-4 w-4 text-blue-500 animate-pulse" />;
      default: return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <Button 
            variant="ghost" 
            onClick={() => navigate(-1)}
            className="mb-2"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Dashboard
          </Button>
          <div className="flex items-center gap-2">
            <Activity className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold">{metricName} Workflow Details</h1>
            <Badge variant="outline" className="ml-2">{department}</Badge>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8 space-y-6">
        {/* Key Metrics */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{getSuccessRate()}%</div>
              <Progress value={getSuccessRate()} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Executions</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{executions.length}</div>
              <p className="text-xs text-muted-foreground mt-1">Last 30 days</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Duration</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{getAvgExecutionTime()}</div>
              <p className="text-xs text-muted-foreground mt-1">Per execution</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Failed Executions</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {executions.filter(e => e.status === "failed").length}
              </div>
              <p className="text-xs text-muted-foreground mt-1">Requires attention</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="insights" className="space-y-4">
          <TabsList>
            <TabsTrigger value="insights">AI Insights</TabsTrigger>
            <TabsTrigger value="history">Execution History</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          <TabsContent value="insights" className="space-y-4">
            {isLoadingInsights ? (
              <Card>
                <CardContent className="py-8 text-center">
                  <Activity className="h-8 w-8 animate-spin mx-auto mb-2 text-primary" />
                  <p>Generating AI-powered insights...</p>
                </CardContent>
              </Card>
            ) : aiInsights ? (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Lightbulb className="h-5 w-5 text-yellow-500" />
                      Predictive Analysis
                    </CardTitle>
                    <CardDescription>AI-powered forecast and trend analysis</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <p className="text-lg mb-2">{aiInsights.prediction}</p>
                    <div className="flex items-center gap-2 mt-4">
                      <Badge variant="outline">Confidence: {aiInsights.confidence}%</Badge>
                      <Progress value={aiInsights.confidence} className="flex-1" />
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      Recommendations
                    </CardTitle>
                    <CardDescription>Actionable steps to improve workflow performance</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3">
                      {aiInsights.recommendations.map((rec, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <CheckCircle className="h-4 w-4 text-green-500 mt-1 flex-shrink-0" />
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                <div className="grid gap-4 md:grid-cols-2">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-orange-500" />
                        Risk Factors
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {aiInsights.risk_factors.map((risk, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <AlertTriangle className="h-4 w-4 text-orange-500 mt-1 flex-shrink-0" />
                            <span className="text-sm">{risk}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-blue-500" />
                        Optimization Opportunities
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ul className="space-y-2">
                        {aiInsights.optimization_opportunities.map((opp, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <TrendingUp className="h-4 w-4 text-blue-500 mt-1 flex-shrink-0" />
                            <span className="text-sm">{opp}</span>
                          </li>
                        ))}
                      </ul>
                    </CardContent>
                  </Card>
                </div>
              </>
            ) : (
              <Card>
                <CardContent className="py-8 text-center">
                  <p>No insights available. Click refresh to generate new insights.</p>
                  <Button onClick={generateAIInsights} className="mt-4">
                    Generate Insights
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="history" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Executions</CardTitle>
                <CardDescription>Detailed execution history and logs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {executions.slice(0, 10).map((execution) => (
                    <div key={execution.id} className="border rounded-lg p-4 space-y-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-3 flex-1">
                          {getStatusIcon(execution.status)}
                          <div className="flex-1">
                            <h4 className="font-semibold text-base">
                              {execution.workflows?.workflow_name || "Unknown Workflow"}
                            </h4>
                            {execution.workflows?.description && (
                              <p className="text-sm text-muted-foreground mt-1">
                                {execution.workflows.description}
                              </p>
                            )}
                          </div>
                        </div>
                        <Badge variant={execution.status === "completed" ? "default" : "destructive"}>
                          {execution.status}
                        </Badge>
                      </div>
                      
                      <div className="bg-muted/50 p-3 rounded-md space-y-2">
                        <div className="flex items-center gap-2 text-sm">
                          <span className="font-medium">
                            {execution.triggered_by === 'manual' && '👤 Manual Execution'}
                            {execution.triggered_by === 'webhook' && '🔗 Webhook Triggered'}
                            {execution.triggered_by === 'schedule' && '⏰ Scheduled Run'}
                            {!['manual', 'webhook', 'schedule'].includes(execution.triggered_by) && `Triggered: ${execution.triggered_by}`}
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground space-y-1">
                          <p>Started: {new Date(execution.started_at).toLocaleString()}</p>
                          {execution.completed_at && (
                            <p>Duration: {((new Date(execution.completed_at).getTime() - new Date(execution.started_at).getTime()) / 1000 / 60).toFixed(2)} min</p>
                          )}
                          {execution.execution_log && Array.isArray(execution.execution_log) && execution.execution_log.length > 0 && (
                            <p>Steps completed: {execution.execution_log.length}</p>
                          )}
                        </div>
                      </div>
                      
                      {execution.error_message && (
                        <div className="bg-destructive/10 text-destructive p-3 rounded text-sm border border-destructive/20">
                          <strong>Error:</strong> {execution.error_message}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Trend Analysis</CardTitle>
                <CardDescription>Performance trends over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <h4 className="font-medium mb-2">Success Rate Trend</h4>
                    <Progress value={getSuccessRate()} className="h-2" />
                    <p className="text-sm text-muted-foreground mt-1">
                      {getSuccessRate() >= 90 ? "Excellent performance" : getSuccessRate() >= 70 ? "Good performance" : "Needs improvement"}
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="font-medium mb-2">Execution Volume</h4>
                    <div className="grid grid-cols-7 gap-2">
                      {[...Array(7)].map((_, i) => (
                        <div key={i} className="space-y-1">
                          <div className="h-20 bg-primary/20 rounded" style={{ height: `${Math.random() * 80 + 20}px` }} />
                          <p className="text-xs text-center text-muted-foreground">
                            {new Date(Date.now() - i * 86400000).toLocaleDateString('en-US', { weekday: 'short' })}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default WorkflowDetail;
