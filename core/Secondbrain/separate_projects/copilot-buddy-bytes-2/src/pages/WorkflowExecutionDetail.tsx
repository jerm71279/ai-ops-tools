import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ArrowLeft, CheckCircle, XCircle, Clock, AlertTriangle, Activity } from "lucide-react";
import { toast } from "sonner";

interface WorkflowExecution {
  id: string;
  workflow_id: string;
  triggered_by: string;
  status: string;
  started_at: string;
  completed_at: string | null;
  error_message: string | null;
  execution_log: any[];
  customer_id: string;
  workflows: {
    workflow_name: string;
    description: string | null;
    workflow_type: string;
  };
}

export default function WorkflowExecutionDetail() {
  const { executionId } = useParams();
  const navigate = useNavigate();
  const [execution, setExecution] = useState<WorkflowExecution | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadExecutionDetail();
  }, [executionId]);

  const loadExecutionDetail = async () => {
    try {
      const { data, error } = await supabase
        .from("workflow_executions")
        .select(`
          *,
          workflows(workflow_name, description, workflow_type)
        `)
        .eq("id", executionId)
        .single();

      if (error) throw error;
      setExecution(data as any);
    } catch (error) {
      console.error("Error loading execution detail:", error);
      toast.error("Failed to load execution details");
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-6 w-6 text-green-500" />;
      case "failed":
        return <XCircle className="h-6 w-6 text-red-500" />;
      case "running":
        return <Activity className="h-6 w-6 text-blue-500 animate-pulse" />;
      default:
        return <Clock className="h-6 w-6" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      completed: "default",
      failed: "destructive",
      running: "secondary"
    };
    return <Badge variant={variants[status] || "outline"} className="text-base px-3 py-1">{status}</Badge>;
  };

  const formatDuration = (started: string, completed: string | null) => {
    if (!completed) return "Running...";
    
    const start = new Date(started).getTime();
    const end = new Date(completed).getTime();
    const durationMs = end - start;
    
    if (durationMs < 1000) return `${durationMs}ms`;
    if (durationMs < 60000) return `${(durationMs / 1000).toFixed(2)}s`;
    return `${(durationMs / 60000).toFixed(2)}m`;
  };

  const getTriggerDisplay = (trigger: string) => {
    switch (trigger) {
      case 'manual': return '👤 Manual Execution';
      case 'webhook': return '🔗 Webhook Triggered';
      case 'schedule': return '⏰ Scheduled Run';
      default: return `Triggered: ${trigger}`;
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 pt-56 pb-8">
          <div className="flex items-center justify-center py-12">
            <Activity className="h-8 w-8 animate-spin text-primary" />
          </div>
        </main>
      </div>
    );
  }

  if (!execution) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 pt-56 pb-8">
          <Card>
            <CardContent className="py-12 text-center">
              <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h2 className="text-xl font-semibold mb-2">Execution Not Found</h2>
              <p className="text-muted-foreground mb-4">The execution you're looking for doesn't exist.</p>
              <Button onClick={() => navigate(-1)}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Go Back
              </Button>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 pt-56 pb-8">
        <Button 
          onClick={() => navigate(-1)} 
          variant="ghost" 
          className="mb-6"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Executions
        </Button>

        {/* Header */}
        <div className="mb-6">
          <div className="flex items-start gap-4 mb-4">
            {getStatusIcon(execution.status)}
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-2">
                {execution.workflows?.workflow_name || "Unknown Workflow"}
              </h1>
              {execution.workflows?.description && (
                <p className="text-muted-foreground">{execution.workflows.description}</p>
              )}
            </div>
            {getStatusBadge(execution.status)}
          </div>
        </div>

        {/* Error Alert */}
        {execution.error_message && (
          <Alert variant="destructive" className="mb-6">
            <XCircle className="h-5 w-5" />
            <AlertTitle className="text-lg font-semibold">Execution Failed</AlertTitle>
            <AlertDescription className="mt-2">
              <div className="bg-background/50 p-4 rounded-md font-mono text-sm">
                {execution.error_message}
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Execution Overview */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Execution Overview</CardTitle>
            <CardDescription>Metadata and timing information</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">Trigger Method</h4>
                <p className="text-lg">{getTriggerDisplay(execution.triggered_by)}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">Workflow Type</h4>
                <p className="text-lg capitalize">{execution.workflows?.workflow_type?.replace('_', ' ')}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">Started At</h4>
                <p className="text-lg">{new Date(execution.started_at).toLocaleString()}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">Duration</h4>
                <p className="text-lg font-semibold">{formatDuration(execution.started_at, execution.completed_at)}</p>
              </div>
              {execution.completed_at && (
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Completed At</h4>
                  <p className="text-lg">{new Date(execution.completed_at).toLocaleString()}</p>
                </div>
              )}
              <div>
                <h4 className="text-sm font-medium text-muted-foreground mb-2">Execution ID</h4>
                <p className="text-sm font-mono">{execution.id}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Execution Steps */}
        {execution.execution_log && execution.execution_log.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Execution Steps</CardTitle>
              <CardDescription>Detailed step-by-step execution log</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {execution.execution_log.map((log: any, index: number) => (
                  <Card key={index} className={log.result?.success === false ? 'border-destructive' : ''}>
                    <CardContent className="pt-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          {log.result?.success !== false ? (
                            <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
                          ) : (
                            <XCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                          )}
                          <div>
                            <h4 className="font-semibold text-lg">{log.step_name}</h4>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge variant="outline">{log.step_type}</Badge>
                              <span className="text-sm text-muted-foreground">
                                Step {index + 1} of {execution.execution_log.length}
                              </span>
                            </div>
                          </div>
                        </div>
                        <Badge variant="secondary">{log.duration_ms}ms</Badge>
                      </div>

                      {/* Step Input */}
                      {log.input && Object.keys(log.input).length > 0 && (
                        <div className="mb-4">
                          <h5 className="text-sm font-medium mb-2">Input:</h5>
                          <pre className="bg-muted p-3 rounded-md text-xs overflow-x-auto">
                            {JSON.stringify(log.input, null, 2)}
                          </pre>
                        </div>
                      )}

                      {/* Step Output/Result */}
                      {log.result && (
                        <div>
                          <h5 className="text-sm font-medium mb-2">
                            {log.result.success ? 'Output:' : 'Error Details:'}
                          </h5>
                          <pre className={`p-3 rounded-md text-xs overflow-x-auto ${
                            log.result.success ? 'bg-muted' : 'bg-destructive/10 text-destructive'
                          }`}>
                            {JSON.stringify(log.result, null, 2)}
                          </pre>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
