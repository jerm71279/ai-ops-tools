import { useState, useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  Save, 
  Play, 
  ArrowLeft,
  Plus,
  Trash2
} from "lucide-react";
import { toast } from "sonner";

export default function VisualWorkflowBuilder() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const workflowId = searchParams.get('id');
  const queryClient = useQueryClient();

  const [workflowName, setWorkflowName] = useState("");
  const [workflowDescription, setWorkflowDescription] = useState("");
  const [workflowCategory, setWorkflowCategory] = useState("automation");
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);

  // Fetch existing workflow if editing
  useQuery({
    queryKey: ["workflow-edit", workflowId],
    enabled: !!workflowId,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("workflow_templates" as any)
        .select("*")
        .eq("id", workflowId)
        .single();

      if (error) throw error;
      if (!data) throw new Error("Workflow not found");
      
      const workflow = data as any;
      setWorkflowName(workflow.name || "");
      setWorkflowDescription(workflow.description || "");
      setWorkflowCategory(workflow.category || "automation");
      setNodes(workflow.nodes || []);
      setEdges(workflow.edges || []);
      
      return data;
    },
  });

  // Save workflow mutation
  const saveWorkflowMutation = useMutation({
    mutationFn: async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) throw new Error("No customer ID");

      const workflowData = {
        name: workflowName,
        description: workflowDescription,
        category: workflowCategory,
        nodes: nodes,
        edges: edges,
        customer_id: profile.customer_id,
        created_by: user.id,
        updated_by: user.id
      };

      if (workflowId) {
        const { error } = await supabase
          .from("workflow_templates" as any)
          .update(workflowData)
          .eq("id", workflowId);
        if (error) throw error;
      } else {
        const { error } = await supabase
          .from("workflow_templates" as any)
          .insert(workflowData);
        if (error) throw error;
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["workflow-templates"] });
      toast.success("Workflow saved successfully");
      navigate('/workflow-orchestration');
    },
    onError: (error: any) => {
      toast.error(`Failed to save: ${error.message}`);
    },
  });

  const addNode = useCallback((type: string) => {
    const newNode = {
      id: `node_${Date.now()}`,
      type,
      position: { x: 100, y: nodes.length * 100 + 100 },
      data: { label: `${type} node` }
    };
    setNodes([...nodes, newNode]);
  }, [nodes]);

  const removeNode = useCallback((nodeId: string) => {
    setNodes(nodes.filter(n => n.id !== nodeId));
    setEdges(edges.filter(e => e.source !== nodeId && e.target !== nodeId));
  }, [nodes, edges]);

  return (
    <div className="container mx-auto px-4 pt-56 pb-8 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" size="icon" onClick={() => navigate('/workflow-orchestration')}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Visual Workflow Builder</h1>
            <p className="text-muted-foreground">
              {workflowId ? 'Edit' : 'Create'} your workflow with drag-and-drop
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Play className="mr-2 h-4 w-4" />
            Test
          </Button>
          <Button onClick={() => saveWorkflowMutation.mutate()} disabled={saveWorkflowMutation.isPending}>
            <Save className="mr-2 h-4 w-4" />
            Save
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {/* Sidebar - Node Palette */}
        <Card className="col-span-1">
          <CardHeader>
            <CardTitle>Components</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={() => addNode('trigger')}
            >
              <Plus className="mr-2 h-4 w-4" />
              Trigger
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={() => addNode('action')}
            >
              <Plus className="mr-2 h-4 w-4" />
              Action
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={() => addNode('condition')}
            >
              <Plus className="mr-2 h-4 w-4" />
              Condition
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={() => addNode('loop')}
            >
              <Plus className="mr-2 h-4 w-4" />
              Loop
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={() => addNode('delay')}
            >
              <Plus className="mr-2 h-4 w-4" />
              Delay
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start"
              onClick={() => addNode('api_call')}
            >
              <Plus className="mr-2 h-4 w-4" />
              API Call
            </Button>
          </CardContent>
        </Card>

        {/* Main Canvas Area */}
        <div className="col-span-3 space-y-4">
          {/* Workflow Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Workflow Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Name</Label>
                <Input
                  value={workflowName}
                  onChange={(e) => setWorkflowName(e.target.value)}
                  placeholder="Enter workflow name"
                />
              </div>
              <div>
                <Label>Description</Label>
                <Input
                  value={workflowDescription}
                  onChange={(e) => setWorkflowDescription(e.target.value)}
                  placeholder="Enter description"
                />
              </div>
              <div>
                <Label>Category</Label>
                <Select value={workflowCategory} onValueChange={setWorkflowCategory}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="automation">Automation</SelectItem>
                    <SelectItem value="integration">Integration</SelectItem>
                    <SelectItem value="notification">Notification</SelectItem>
                    <SelectItem value="data_processing">Data Processing</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Canvas */}
          <Card>
            <CardHeader>
              <CardTitle>Workflow Canvas</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="min-h-[500px] border-2 border-dashed rounded-lg p-4 bg-muted/20">
                {nodes.length === 0 ? (
                  <div className="flex items-center justify-center h-full text-muted-foreground">
                    Add nodes from the left panel to build your workflow
                  </div>
                ) : (
                  <div className="space-y-4">
                    {nodes.map((node, index) => (
                      <div
                        key={node.id}
                        className="flex items-center gap-2 p-4 border rounded-lg bg-background"
                      >
                        <div className="flex-1">
                          <div className="font-medium">{node.data.label}</div>
                          <div className="text-sm text-muted-foreground">
                            Type: {node.type}
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => removeNode(node.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}