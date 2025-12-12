/**
 * WorkflowExecutionHistory Component
 * 
 * Displays historical workflow execution data with real-time status updates.
 * Shows execution details, step-by-step logs, duration, and error messages.
 * 
 * Features:
 * - Real-time execution status (running, completed, failed)
 * - Step-by-step execution logs with timing data
 * - Error message display for failed executions
 * - Manual refresh capability
 * - Duration calculations
 * 
 * Data Source:
 * - workflow_executions table (joined with workflows for name)
 * - Ordered by most recent first
 * - Limited to last 50 executions
 * 
 * Integration Points:
 * - Operations Dashboard: Embedded in "Execution History" tab
 * - WorkflowExecutor: Execution logs are created by edge function
 * 
 * @module WorkflowExecutionHistory
 */

import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { supabase } from "@/integrations/supabase/client";
import { toast } from "sonner";
import { RefreshCw, CheckCircle, XCircle, Clock } from "lucide-react";

/**
 * Represents a single workflow execution record from the database
 * Includes execution metadata and step-by-step logs
 */
interface WorkflowExecution {
  id: string;                           // Unique execution ID
  workflow_id: string;                  // Reference to parent workflow
  triggered_by: string;                 // How it was initiated (manual, webhook, schedule)
  status: string;                       // running, completed, failed
  started_at: string;                   // ISO timestamp of execution start
  completed_at: string | null;          // ISO timestamp of completion (null if still running)
  error_message: string | null;         // Error details if status is failed
  execution_log: any[];                 // Array of step execution results
  workflows: {
    workflow_name: string;              // Joined workflow name for display
  };
}

export const WorkflowExecutionHistory = ({ customerId }: { customerId: string }) => {
  const navigate = useNavigate();
  const [executions, setExecutions] = useState<WorkflowExecution[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const isDemoMode = customerId === "demo-customer";

  /**
   * Load execution history on component mount and when customer changes
   */
  useEffect(() => {
    fetchExecutions();
  }, [customerId]);

  /**
   * Fetches workflow execution history from database
   * Joins with workflows table to get workflow names
   * Orders by most recent first, limits to 50 records
   * 
   * Error Handling:
   * - Shows toast notification on fetch error
   * - Logs error to console for debugging
   * - Sets empty array as fallback
   */
  const fetchExecutions = async () => {
    // Skip database queries in demo mode
    if (isDemoMode) {
      setIsLoading(false);
      return;
    }

    try {
      const { data, error } = await supabase
        .from("workflow_executions")
        .select(`
          *,
          workflows(workflow_name)
        `)
        .eq("customer_id", customerId)
        .order("started_at", { ascending: false })  // Most recent first
        .limit(50);                                 // Pagination limit

      if (error) throw error;

      // Cast to our interface type (needed due to JSONB fields)
      setExecutions((data || []) as any);
    } catch (error: any) {
      console.error("Error fetching executions:", error);
      toast.error("Failed to load execution history");
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Returns appropriate status icon based on execution status
   * 
   * @param status - The execution status (running, completed, failed)
   * @returns React icon component with appropriate color
   */
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "running":
        // Animated pulse for running state
        return <Clock className="h-4 w-4 text-blue-500 animate-pulse" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  /**
   * Returns appropriate badge variant based on execution status
   * 
   * @param status - The execution status
   * @returns Badge component with appropriate styling
   */
  const getStatusBadge = (status: string) => {
    const variants: Record<string, any> = {
      completed: "default",
      failed: "destructive",
      running: "secondary"
    };
    return <Badge variant={variants[status] || "outline"}>{status}</Badge>;
  };

  /**
   * Calculates and formats execution duration
   * 
   * @param started - ISO timestamp of execution start
   * @param completed - ISO timestamp of completion (null if still running)
   * @returns Formatted duration string (ms, s, or m)
   */
  const formatDuration = (started: string, completed: string | null) => {
    if (!completed) return "Running...";
    
    const start = new Date(started).getTime();
    const end = new Date(completed).getTime();
    const durationMs = end - start;
    
    // Format based on duration
    if (durationMs < 1000) return `${durationMs}ms`;
    if (durationMs < 60000) return `${(durationMs / 1000).toFixed(1)}s`;
    return `${(durationMs / 60000).toFixed(1)}m`;
  };

  // Loading state
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Execution History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Execution History</CardTitle>
            <CardDescription>Recent workflow executions</CardDescription>
          </div>
          {/* Manual refresh button */}
          <Button variant="outline" size="sm" onClick={fetchExecutions}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Empty state when no executions */}
        {executions.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            No executions yet. Create and run a workflow to see results here.
          </div>
        ) : (
          /* List of execution records */
          <div className="space-y-4">
            {executions.map((execution) => (
              <Card 
                key={execution.id} 
                className="cursor-pointer hover:shadow-lg transition-shadow"
                onClick={() => navigate(`/workflow/execution/${execution.id}`)}
              >
                <CardContent className="pt-6">
                  {/* Execution Header: Status, name, timing */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(execution.status)}
                        <h4 className="font-semibold text-lg">
                          {execution.workflows?.workflow_name || "Unknown Workflow"}
                        </h4>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        <p className="font-medium">
                          {execution.triggered_by === 'manual' && '👤 Manual execution'}
                          {execution.triggered_by === 'webhook' && '🔗 Triggered by webhook'}
                          {execution.triggered_by === 'schedule' && '⏰ Scheduled execution'}
                          {!['manual', 'webhook', 'schedule'].includes(execution.triggered_by) && `Triggered by: ${execution.triggered_by}`}
                        </p>
                        <p className="mt-1">
                          Started: {new Date(execution.started_at).toLocaleString()} • Duration: {formatDuration(execution.started_at, execution.completed_at)}
                        </p>
                        {execution.execution_log && execution.execution_log.length > 0 && (
                          <p className="mt-1 text-xs">
                            Completed {execution.execution_log.length} step{execution.execution_log.length !== 1 ? 's' : ''}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {/* Show current status */}
                      {getStatusBadge(execution.status)}
                    </div>
                  </div>

                  {/* Error Message (only shown if execution failed) */}
                  {execution.error_message && (
                    <div className="p-3 bg-destructive/10 border border-destructive/20 rounded text-sm text-destructive mb-4">
                      <strong>Error:</strong> {execution.error_message}
                    </div>
                  )}

                  {/* Step-by-Step Execution Log */}
                  {execution.execution_log && execution.execution_log.length > 0 && (
                    <div className="space-y-2">
                      <div className="text-sm font-medium">Execution Steps:</div>
                      <div className="space-y-1">
                        {execution.execution_log.map((log: any, index: number) => (
                          <div
                            key={index}
                            className="flex items-center justify-between text-sm p-2 bg-muted/50 rounded"
                          >
                            <div className="flex items-center gap-2">
                              {/* Success/failure icon for each step */}
                              {log.result?.success ? (
                                <CheckCircle className="h-3 w-3 text-green-500" />
                              ) : (
                                <XCircle className="h-3 w-3 text-red-500" />
                              )}
                              {/* Step name and type */}
                              <span className="font-mono text-xs">{log.step_name}</span>
                              <Badge variant="outline" className="text-xs">
                                {log.step_type}
                              </Badge>
                            </div>
                            {/* Step execution duration */}
                            <span className="text-xs text-muted-foreground">
                              {log.duration_ms}ms
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
