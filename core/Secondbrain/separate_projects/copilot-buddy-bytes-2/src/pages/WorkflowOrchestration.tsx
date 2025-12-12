import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { 
  Workflow, 
  Plus, 
  Play, 
  Pause, 
  Archive,
  Copy,
  GitBranch,
  Clock,
  CheckCircle,
  XCircle,
  TrendingUp
} from "lucide-react";
import { toast } from "sonner";
import { useNavigate } from "react-router-dom";

export default function WorkflowOrchestration() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("all");
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  // Fetch workflows
  const { data: workflows, isLoading } = useQuery({
    queryKey: ["workflow-templates"],
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
        .from("workflow_templates" as any)
        .select("*")
        .eq("customer_id", profile.customer_id)
        .order("created_at", { ascending: false });

      if (error) throw error;
      return data;
    },
  });

  // Fetch workflow analytics
  const { data: analytics } = useQuery({
    queryKey: ["workflow-analytics"],
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
        .from("workflow_analytics" as any)
        .select("*")
        .eq("customer_id", profile.customer_id)
        .gte("date", new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString());

      if (error) throw error;
      return data;
    },
  });

  // Update workflow status mutation
  const updateStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: string }) => {
      const { error } = await supabase
        .from("workflow_templates" as any)
        .update({ status })
        .eq("id", id);

      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflow-templates"] });
      toast.success("Workflow status updated");
    },
    onError: (error: any) => {
      toast.error(`Failed to update status: ${error.message}`);
    },
  });

  // Clone workflow mutation
  const cloneWorkflowMutation = useMutation({
    mutationFn: async (workflowId: string) => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      const workflow = workflows?.find((w: any) => w.id === workflowId) as any;
      if (!workflow) throw new Error("Workflow not found");

      const { error } = await supabase
        .from("workflow_templates" as any)
        .insert({
          customer_id: profile?.customer_id,
          name: `${workflow?.name || 'Workflow'} (Copy)`,
          description: workflow?.description || "",
          category: workflow?.category || "automation",
          nodes: workflow?.nodes || [],
          edges: workflow?.edges || [],
          variables: workflow?.variables || {},
          settings: workflow?.settings || {},
          created_by: user.id,
          status: 'draft'
        });

      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflow-templates"] });
      toast.success("Workflow cloned successfully");
    },
    onError: (error: any) => {
      toast.error(`Failed to clone: ${error.message}`);
    },
  });

  const filteredWorkflows = workflows?.filter((w: any) => {
    const matchesSearch = w.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === "all" || w.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-success" />;
      case 'paused':
        return <Pause className="h-4 w-4 text-warning" />;
      case 'draft':
        return <Clock className="h-4 w-4 text-muted-foreground" />;
      case 'archived':
        return <Archive className="h-4 w-4 text-muted-foreground" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'default';
      case 'paused':
        return 'secondary';
      case 'draft':
        return 'outline';
      case 'archived':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const totalExecutions = analytics?.reduce((sum: number, a: any) => sum + a.execution_count, 0) || 0;
  const totalSuccesses = analytics?.reduce((sum: number, a: any) => sum + a.success_count, 0) || 0;
  const avgSuccessRate = totalExecutions > 0 ? Math.round((totalSuccesses / totalExecutions) * 100) : 0;

  return (
    <div className="container mx-auto px-4 pt-56 pb-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Workflow Orchestration</h1>
          <p className="text-muted-foreground">
            Advanced workflow automation with visual builder
          </p>
        </div>
        <Button onClick={() => navigate('/workflows/visual-builder')}>
          <Plus className="mr-2 h-4 w-4" />
          Create Workflow
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Total Workflows</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{workflows?.length || 0}</div>
            <p className="text-xs text-muted-foreground">
              {workflows?.filter((w: any) => w.status === 'active').length || 0} active
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Executions (30d)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalExecutions}</div>
            <p className="text-xs text-muted-foreground">
              {totalSuccesses} successful
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{avgSuccessRate}%</div>
            <p className="text-xs text-muted-foreground">Last 30 days</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">Avg Execution Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {workflows?.reduce((sum: number, w: any) => sum + (w.avg_execution_time || 0), 0) / (workflows?.length || 1) || 0}ms
            </div>
            <p className="text-xs text-muted-foreground">Average duration</p>
          </CardContent>
        </Card>
      </div>

      {/* Workflows List */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Workflows</CardTitle>
              <CardDescription>Manage your automated workflows</CardDescription>
            </div>
            <div className="flex gap-2">
              <Input
                placeholder="Search workflows..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-64"
              />
              <Tabs value={selectedStatus} onValueChange={setSelectedStatus}>
                <TabsList>
                  <TabsTrigger value="all">All</TabsTrigger>
                  <TabsTrigger value="active">Active</TabsTrigger>
                  <TabsTrigger value="draft">Draft</TabsTrigger>
                  <TabsTrigger value="paused">Paused</TabsTrigger>
                </TabsList>
              </Tabs>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p>Loading workflows...</p>
          ) : filteredWorkflows && filteredWorkflows.length > 0 ? (
            <div className="space-y-4">
              {filteredWorkflows.map((workflow: any) => (
                <Card key={workflow.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4">
                        <div className="p-2 rounded-lg bg-primary/10">
                          <Workflow className="h-6 w-6 text-primary" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <CardTitle className="text-lg">{workflow.name}</CardTitle>
                            <Badge variant={getStatusColor(workflow.status) as any} className="gap-1">
                              {getStatusIcon(workflow.status)}
                              {workflow.status}
                            </Badge>
                            <Badge variant="outline">v{workflow.version}</Badge>
                          </div>
                          <CardDescription className="mt-1">
                            {workflow.description || "No description"}
                          </CardDescription>
                          <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <TrendingUp className="h-3 w-3" />
                              {workflow.usage_count || 0} runs
                            </span>
                            {workflow.success_rate && (
                              <span>{workflow.success_rate}% success</span>
                            )}
                            {workflow.avg_execution_time && (
                              <span className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {workflow.avg_execution_time}ms avg
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        {workflow.status === 'active' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => updateStatusMutation.mutate({ id: workflow.id, status: 'paused' })}
                          >
                            <Pause className="h-4 w-4" />
                          </Button>
                        )}
                        {workflow.status === 'paused' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => updateStatusMutation.mutate({ id: workflow.id, status: 'active' })}
                          >
                            <Play className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => cloneWorkflowMutation.mutate(workflow.id)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => navigate(`/workflows/visual-builder?id=${workflow.id}`)}
                        >
                          <GitBranch className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-muted-foreground">
              <Workflow className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No workflows found. Create your first workflow to get started.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}