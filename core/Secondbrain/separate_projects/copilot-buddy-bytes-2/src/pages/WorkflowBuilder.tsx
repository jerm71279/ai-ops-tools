import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, Plus, Trash2, Settings } from "lucide-react";

interface WorkflowStep {
  id: string;
  type: string;
  config: Record<string, any>;
  sequence: number;
}

export default function WorkflowBuilder() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [workflowName, setWorkflowName] = useState("");
  const [description, setDescription] = useState("");
  const [workflowType, setWorkflowType] = useState("custom");
  const [steps, setSteps] = useState<WorkflowStep[]>([]);
  const [isSaving, setIsSaving] = useState(false);

  const addStep = (type: string) => {
    const newStep: WorkflowStep = {
      id: crypto.randomUUID(),
      type,
      config: {},
      sequence: steps.length
    };
    setSteps([...steps, newStep]);
  };

  const removeStep = (id: string) => {
    setSteps(steps.filter(step => step.id !== id).map((step, idx) => ({
      ...step,
      sequence: idx
    })));
  };

  const handleSave = async () => {
    if (!workflowName.trim()) {
      toast({
        title: "Validation Error",
        description: "Please enter a workflow name",
        variant: "destructive"
      });
      return;
    }

    setIsSaving(true);
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { data: profile } = await supabase
        .from('user_profiles')
        .select('customer_id')
        .eq('user_id', user.id)
        .single();

      if (!profile?.customer_id) throw new Error("No customer profile found");

      const { error } = await supabase
        .from('workflows')
        .insert({
          workflow_name: workflowName,
          description,
          workflow_type: workflowType,
          customer_id: profile.customer_id,
          is_active: true,
          steps: steps as any
        } as any);

      if (error) throw error;

      toast({
        title: "Success",
        description: "Workflow created successfully"
      });

      navigate('/workflows');
    } catch (error) {
      console.error('Error saving workflow:', error);
      toast({
        title: "Error",
        description: "Failed to save workflow",
        variant: "destructive"
      });
    } finally {
      setIsSaving(false);
    }
  };

  const getStepIcon = (type: string) => {
    return "📋";
  };

  const availableStepTypes = [
    { value: "trigger", label: "Trigger Event", description: "Start the workflow" },
    { value: "condition", label: "Condition", description: "Check if condition is met" },
    { value: "action", label: "Action", description: "Perform an action" },
    { value: "notification", label: "Notification", description: "Send a notification" },
    { value: "api_call", label: "API Call", description: "Call external API" },
    { value: "delay", label: "Delay", description: "Wait before next step" }
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 pt-56 pb-8">
        <DashboardNavigation 
          title="Workflow Builder"
          dashboards={[
            { name: "Admin Dashboard", path: "/admin" },
            { name: "Employee Portal", path: "/portal" },
            { name: "Analytics Portal", path: "/analytics" },
            { name: "Compliance Portal", path: "/compliance" },
            { name: "Change Management", path: "/change-management" },
            { name: "Executive Dashboard", path: "/dashboard/executive" },
            { name: "Finance Dashboard", path: "/dashboard/finance" },
            { name: "HR Dashboard", path: "/dashboard/hr" },
            { name: "IT Dashboard", path: "/dashboard/it" },
            { name: "Operations Dashboard", path: "/dashboard/operations" },
            { name: "Sales Dashboard", path: "/dashboard/sales" },
            { name: "SOC Dashboard", path: "/dashboard/soc" },
          ]}
        />
        
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-4 mb-6">
            <Button variant="ghost" size="sm" onClick={() => navigate('/workflows')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
            <div>
              <h1 className="text-4xl font-bold">Workflow Builder</h1>
              <p className="text-muted-foreground">Create automated workflows</p>
            </div>
          </div>

          <div className="space-y-6">
            {/* Workflow Details */}
            <Card>
              <CardHeader>
                <CardTitle>Workflow Details</CardTitle>
                <CardDescription>Configure your workflow settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="workflowName">Workflow Name</Label>
                  <Input
                    id="workflowName"
                    value={workflowName}
                    onChange={(e) => setWorkflowName(e.target.value)}
                    placeholder="e.g., New Client Onboarding Automation"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe what this workflow does"
                    rows={3}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="workflowType">Workflow Type</Label>
                  <Select value={workflowType} onValueChange={setWorkflowType}>
                    <SelectTrigger id="workflowType">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="custom">Custom</SelectItem>
                      <SelectItem value="onboarding">Client Onboarding</SelectItem>
                      <SelectItem value="compliance">Compliance</SelectItem>
                      <SelectItem value="monitoring">Monitoring</SelectItem>
                      <SelectItem value="approval">Approval Process</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Workflow Steps */}
            <Card>
              <CardHeader>
                <CardTitle>Workflow Steps</CardTitle>
                <CardDescription>Add and configure workflow steps</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {steps.length === 0 ? (
                  <div className="text-center py-12 border-2 border-dashed rounded-lg">
                    <p className="text-muted-foreground mb-4">No steps added yet</p>
                    <p className="text-sm text-muted-foreground">Add your first step to get started</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {steps.map((step, index) => (
                      <Card key={step.id}>
                        <CardContent className="py-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <div className="text-2xl">{getStepIcon(step.type)}</div>
                              <div>
                                <p className="font-medium">Step {index + 1}: {step.type}</p>
                                <p className="text-sm text-muted-foreground capitalize">
                                  {step.type.replace('_', ' ')}
                                </p>
                              </div>
                            </div>
                            <div className="flex gap-2">
                              <Button variant="ghost" size="sm">
                                <Settings className="h-4 w-4" />
                              </Button>
                              <Button 
                                variant="ghost" 
                                size="sm"
                                onClick={() => removeStep(step.id)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}

                <div className="pt-4">
                  <Label className="mb-2 block">Add Step</Label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {availableStepTypes.map((stepType) => (
                      <Button
                        key={stepType.value}
                        variant="outline"
                        className="h-auto py-3 px-4 flex flex-col items-start gap-1"
                        onClick={() => addStep(stepType.value)}
                      >
                        <span className="font-medium">{stepType.label}</span>
                        <span className="text-xs text-muted-foreground">{stepType.description}</span>
                      </Button>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex gap-3 justify-end">
              <Button variant="outline" onClick={() => navigate('/workflows')}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? "Saving..." : "Save Workflow"}
              </Button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
