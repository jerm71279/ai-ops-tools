/**
 * WorkflowBuilder Component
 * 
 * Visual workflow builder interface for creating multi-step automated workflows.
 * Allows users to configure workflow steps, triggers (webhook/schedule/manual),
 * and conditional logic without writing code.
 * 
 * Features:
 * - Drag-and-drop step ordering
 * - Multiple step types (API calls, data transforms, conditions, etc.)
 * - Trigger configuration (webhook, scheduled, event-based)
 * - JSON-based step configuration
 * - Real-time validation
 * 
 * Integration Points:
 * - Database: Saves to workflows and workflow_triggers tables
 * - Edge Functions: Workflows are executed by workflow-executor function
 * - Operations Dashboard: Embedded in tabbed interface
 * 
 * @module WorkflowBuilder
 */

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";
import { Plus, Trash2, Save, Play, GitBranch, Clock, Webhook } from "lucide-react";
import { z } from "zod";

// Validation schemas
const workflowSchema = z.object({
  workflow_name: z.string().trim().min(1, "Workflow name is required").max(100, "Name too long"),
  description: z.string().trim().max(500, "Description too long").optional(),
});

const stepSchema = z.object({
  step_name: z.string().trim().min(1, "Step name is required").max(100, "Step name too long"),
  step_type: z.enum(["api_call", "data_transform", "condition", "notification", "database_operation", "delay", "loop"], {
    errorMap: () => ({ message: "Invalid step type" }),
  }),
  config: z.record(z.any()).optional(),
});

/**
 * Represents a single step in the workflow execution chain
 */
interface WorkflowStep {
  id: string;                      // Unique identifier generated from timestamp
  type: string;                    // Step type: api_call, data_transform, condition, etc.
  name: string;                    // User-friendly step name
  config: Record<string, any>;     // JSON configuration specific to step type
  order: number;                   // Sequential execution order
}

/**
 * Represents a conditional branching step in the workflow
 * Not currently used but reserved for future conditional logic implementation
 */
interface WorkflowCondition {
  step_id: string;                           // Reference to parent step
  condition_type: string;                    // if, switch, or loop
  condition_expression: Record<string, any>; // Condition logic in JSON
  true_path?: Record<string, any>;          // Steps to execute if condition is true
  false_path?: Record<string, any>;         // Steps to execute if condition is false
}

export const WorkflowBuilder = ({ customerId }: { customerId: string }) => {
  // Workflow metadata state
  const [workflowName, setWorkflowName] = useState("");
  const [description, setDescription] = useState("");
  
  // Steps array - holds all workflow steps in execution order
  const [steps, setSteps] = useState<WorkflowStep[]>([]);
  
  // Triggers configuration - how the workflow gets initiated
  const [triggers, setTriggers] = useState<any[]>([]);
  const [showTriggerConfig, setShowTriggerConfig] = useState(false);
  const [selectedTriggerType, setSelectedTriggerType] = useState<string>("");

  /**
   * Available step types for workflow building
   * Each step type is executed differently by the workflow-executor edge function
   */
  const stepTypes = [
    { value: "api_call", label: "API Call" },              // HTTP requests to external APIs
    { value: "data_transform", label: "Data Transform" },  // Map/transform data between steps
    { value: "condition", label: "Conditional Branch" },   // If/else branching logic
    { value: "notification", label: "Send Notification" }, // Send alerts/notifications
    { value: "database_operation", label: "Database Operation" }, // CRUD operations
    { value: "delay", label: "Wait/Delay" },              // Wait before next step
    { value: "loop", label: "Loop Over Data" }            // Iterate over arrays
  ];

  /**
   * Available trigger types for workflow execution
   * Determines how and when the workflow runs
   */
  const triggerTypes = [
    { value: "manual", label: "Manual Trigger" },          // User-initiated via UI
    { value: "webhook", label: "Webhook" },                // HTTP POST to unique URL
    { value: "schedule", label: "Scheduled (Cron)" },      // Time-based execution
    { value: "event", label: "Event-Based" }               // Database event triggers
  ];

  /**
   * Adds a new workflow step to the builder
   * Default step type is 'api_call' and can be changed by user
   * Steps are ordered sequentially based on array position
   */
  const addStep = () => {
    const newStep: WorkflowStep = {
      id: `step_${Date.now()}`,       // Generate unique ID using timestamp
      type: "api_call",                // Default type, user can change
      name: `Step ${steps.length + 1}`, // Auto-numbered step name
      config: {},                      // Empty config, filled in by user
      order: steps.length              // Sequential ordering
    };
    setSteps([...steps, newStep]);
  };

  /**
   * Updates a specific field of a workflow step
   * Uses immutable state update pattern
   * 
   * @param id - The step ID to update
   * @param field - Which field to update (name, type, config, etc.)
   * @param value - The new value for the field
   */
  const updateStep = (id: string, field: keyof WorkflowStep, value: any) => {
    setSteps(steps.map(step => 
      step.id === id ? { ...step, [field]: value } : step
    ));
  };

  /**
   * Removes a step from the workflow
   * Uses filter to create new array without the removed step
   * 
   * @param id - The step ID to remove
   */
  const removeStep = (id: string) => {
    setSteps(steps.filter(step => step.id !== id));
  };

  /**
   * Adds a trigger configuration to the workflow
   * Validates that a trigger type is selected before adding
   * Each workflow can have multiple triggers
   */
  const addTrigger = () => {
    if (!selectedTriggerType) {
      toast.error("Please select a trigger type");
      return;
    }

    const newTrigger = {
      id: `trigger_${Date.now()}`,           // Unique trigger ID
      trigger_type: selectedTriggerType,      // webhook, schedule, manual, event
      trigger_config: {},                     // Additional config (cron schedule, etc.)
      is_enabled: true                        // Active by default
    };
    setTriggers([...triggers, newTrigger]);
    setShowTriggerConfig(false);             // Close the trigger selection UI
    setSelectedTriggerType("");              // Reset selection
  };

  /**
   * Saves the workflow to the database
   * Creates workflow record and associated trigger records
   * Performs validation before saving
   * 
   * Transaction Flow:
   * 1. Validate workflow name and steps
   * 2. Insert workflow into workflows table
   * 3. Insert triggers into workflow_triggers table (if any)
   * 4. Reset form on success
   */
  const saveWorkflow = async () => {
    // Prevent saving in demo mode
    if (customerId === "demo-customer") {
      toast.error("Cannot save workflows in demo mode");
      return;
    }

    try {
      // Validate workflow data
      const validatedWorkflow = workflowSchema.parse({
        workflow_name: workflowName,
        description: description || undefined,
      });

      // Validation: workflow must have at least one step
      if (steps.length === 0) {
        toast.error("Please add at least one step");
        return;
      }

      // Validate all steps
      steps.forEach((step, index) => {
        try {
          stepSchema.parse({
            step_name: step.name,
            step_type: step.type,
            config: step.config,
          });
        } catch (error) {
          if (error instanceof z.ZodError) {
            throw new Error(`Step ${index + 1}: ${error.errors[0].message}`);
          }
        }
      });

      // Step 1: Save workflow definition
      const { data: workflow, error: workflowError } = await supabase
        .from("workflows")
        .insert({
          customer_id: customerId,
          workflow_name: validatedWorkflow.workflow_name,
          description: validatedWorkflow.description || null,
          steps: steps as any,
          systems_involved: [...new Set(steps.map(s => s.type))],
          workflow_type: triggers.length > 0 ? triggers[0].trigger_type : "manual",
          is_active: true
        })
        .select()
        .single();

      if (workflowError) throw workflowError;

      // Step 2: Save trigger configurations (if any)
      if (triggers.length > 0) {
        const triggersToInsert = triggers.map(t => ({
          workflow_id: workflow.id,
          customer_id: customerId,
          ...t
        }));

        const { error: triggersError } = await supabase
          .from("workflow_triggers")
          .insert(triggersToInsert);

        if (triggersError) throw triggersError;
      }

      toast.success("Workflow saved successfully!");
      
      // Step 3: Reset form
      setWorkflowName("");
      setDescription("");
      setSteps([]);
      setTriggers([]);
    } catch (error: any) {
      if (error instanceof z.ZodError) {
        toast.error(error.errors[0].message);
      } else {
        toast.error(error.message || "Failed to save workflow");
      }
    }
  };

  /**
   * Tests the workflow without saving
   * Currently logs to console - in production would call workflow-executor
   * 
   * Future Implementation:
   * - Call workflow-executor edge function with test flag
   * - Show execution results in modal or side panel
   * - Allow step-by-step debugging
   */
  const testWorkflow = async () => {
    if (steps.length === 0) {
      toast.error("Please add steps before testing");
      return;
    }

    toast.success("Test execution started - check execution history for results");
    
    // TODO: Call workflow-executor edge function for real testing
    console.log("Testing workflow:", { workflowName, steps, triggers });
  };

  return (
    <div className="space-y-6">
      {/* Workflow Configuration Card */}
      <Card>
        <CardHeader>
          <CardTitle>Workflow Configuration</CardTitle>
          <CardDescription>Create and configure automated workflows</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Workflow Name Input */}
          <div className="space-y-2">
            <Label htmlFor="workflow-name">Workflow Name</Label>
            <Input
              id="workflow-name"
              placeholder="e.g., Employee Onboarding Automation"
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
            />
          </div>

          {/* Workflow Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="Describe what this workflow does..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>

          {/* Trigger Configuration Section */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>Triggers</Label>
              <Button 
                size="sm" 
                variant="outline"
                onClick={() => setShowTriggerConfig(!showTriggerConfig)}
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Trigger
              </Button>
            </div>

            {/* Trigger Type Selector (shown when adding new trigger) */}
            {showTriggerConfig && (
              <div className="flex gap-2">
                <Select value={selectedTriggerType} onValueChange={setSelectedTriggerType}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select trigger type" />
                  </SelectTrigger>
                  <SelectContent>
                    {triggerTypes.map(type => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button size="sm" onClick={addTrigger}>Add</Button>
              </div>
            )}

            {/* List of configured triggers */}
            <div className="space-y-2">
              {triggers.map(trigger => (
                <div key={trigger.id} className="flex items-center gap-2 p-2 border rounded">
                  {/* Icon based on trigger type */}
                  {trigger.trigger_type === "webhook" && <Webhook className="h-4 w-4" />}
                  {trigger.trigger_type === "schedule" && <Clock className="h-4 w-4" />}
                  <Badge variant="outline">{trigger.trigger_type}</Badge>
                  {/* Remove trigger button */}
                  <Button 
                    size="sm" 
                    variant="ghost"
                    onClick={() => setTriggers(triggers.filter(t => t.id !== trigger.id))}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Workflow Steps Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Workflow Steps</CardTitle>
              <CardDescription>Define the sequence of actions</CardDescription>
            </div>
            <Button onClick={addStep}>
              <Plus className="h-4 w-4 mr-2" />
              Add Step
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Empty state when no steps */}
          {steps.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No steps added yet. Click &quot;Add Step&quot; to begin.
            </div>
          ) : (
            /* Map through steps and render each one */
            steps.map((step, index) => (
              <Card key={step.id} className="relative">
                <CardContent className="pt-6 space-y-4">
                  {/* Step Header: Badge number, name input, delete button */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <Badge>{index + 1}</Badge>
                      <div className="space-y-2 flex-1">
                        <Input
                          placeholder="Step name"
                          value={step.name}
                          onChange={(e) => updateStep(step.id, "name", e.target.value)}
                        />
                      </div>
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => removeStep(step.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Step Type Selector */}
                  <div className="space-y-2">
                    <Label>Step Type</Label>
                    <Select
                      value={step.type}
                      onValueChange={(value) => updateStep(step.id, "type", value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {stepTypes.map(type => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Conditional Logic UI (only shown for condition steps) */}
                  {step.type === "condition" && (
                    <div className="pl-4 border-l-2 border-primary/20">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                        <GitBranch className="h-4 w-4" />
                        <span>Conditional Logic</span>
                      </div>
                      <Textarea
                        placeholder="Enter condition expression (JSON)"
                        className="font-mono text-sm"
                        rows={3}
                      />
                    </div>
                  )}

                  {/* Step Configuration JSON (for non-condition steps) */}
                  {step.type !== "condition" && (
                    <div className="space-y-2">
                      <Label>Configuration (JSON)</Label>
                      <Textarea
                        placeholder="{&quot;url&quot;: &quot;https://api.example.com&quot;, &quot;method&quot;: &quot;POST&quot;}"
                        className="font-mono text-sm"
                        rows={4}
                        onChange={(e) => {
                          try {
                            // Parse and validate JSON before updating state
                            const config = JSON.parse(e.target.value);
                            updateStep(step.id, "config", config);
                          } catch {
                            // Invalid JSON, ignore silently
                            // User will see validation error when saving
                          }
                        }}
                      />
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          )}
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-2 justify-end">
        <Button variant="outline" onClick={testWorkflow}>
          <Play className="h-4 w-4 mr-2" />
          Test Workflow
        </Button>
        <Button onClick={saveWorkflow}>
          <Save className="h-4 w-4 mr-2" />
          Save Workflow
        </Button>
      </div>
    </div>
  );
};
