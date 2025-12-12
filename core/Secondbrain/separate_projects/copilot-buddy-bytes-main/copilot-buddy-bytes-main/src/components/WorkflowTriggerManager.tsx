/**
 * WorkflowTriggerManager Component
 * 
 * Manages workflow triggers - webhook URLs, scheduled executions, and event-based triggers.
 * Provides UI for creating, enabling/disabling, and testing triggers.
 * 
 * Features:
 * - Webhook trigger creation with auto-generated URLs
 * - Webhook URL copying to clipboard
 * - Webhook testing functionality
 * - Enable/disable toggle for each trigger
 * - Last triggered timestamp display
 * - Scheduled trigger configuration display
 * 
 * Security:
 * - Webhook URLs are unique per trigger
 * - Optional webhook signature verification (configured per trigger)
 * - Triggers can be disabled without deletion
 * 
 * Integration Points:
 * - Operations Dashboard: Embedded in "Triggers" tab
 * - workflow-webhook edge function: Receives webhook POST requests
 * - workflow_triggers table: Stores trigger configurations
 * 
 * @module WorkflowTriggerManager
 */

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";
import { Copy, Webhook, Clock, RefreshCw } from "lucide-react";

/**
 * Simplified workflow data for trigger creation
 * Only includes fields needed for the trigger management UI
 */
interface Workflow {
  id: string;
  workflow_name: string;
}

/**
 * Trigger configuration with workflow details
 * Includes joined workflow name for display purposes
 */
interface Trigger {
  id: string;
  workflow_id: string;
  trigger_type: string;                  // webhook, schedule, event, manual
  trigger_config: any;                   // Type-specific config (cron schedule, etc.)
  webhook_url: string | null;            // Auto-generated webhook URL
  is_enabled: boolean;                   // Whether trigger is active
  last_triggered_at: string | null;      // Last execution timestamp
  workflows: {
    workflow_name: string;               // Joined from workflows table
  };
}

export const WorkflowTriggerManager = ({ customerId }: { customerId: string }) => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [triggers, setTriggers] = useState<Trigger[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const isDemoMode = customerId === "demo-customer";

  /**
   * Load workflows and triggers on component mount and when customer changes
   */
  useEffect(() => {
    fetchData();
  }, [customerId]);

  /**
   * Fetches active workflows and their triggers from database
   * Uses Promise.all for parallel fetching to improve performance
   * 
   * Workflows Query:
   * - Only fetches active workflows (is_active = true)
   * - Only includes minimal fields needed for UI
   * 
   * Triggers Query:
   * - Fetches all triggers for customer
   * - Joins with workflows table to get workflow names
   * - Includes all trigger types (webhook, schedule, event)
   * 
   * Error Handling:
   * - Shows toast notification on error
   * - Logs error to console for debugging
   * - Sets empty arrays as fallback
   */
  const fetchData = async () => {
    // Skip database queries in demo mode
    if (isDemoMode) {
      setIsLoading(false);
      return;
    }

    try {
      const [workflowsData, triggersData] = await Promise.all([
        supabase
          .from("workflows")
          .select("id, workflow_name")
          .eq("customer_id", customerId)
          .eq("is_active", true),
        supabase
          .from("workflow_triggers")
          .select(`
            *,
            workflows(workflow_name)
          `)
          .eq("customer_id", customerId)
      ]);

      if (workflowsData.error) throw workflowsData.error;
      if (triggersData.error) throw triggersData.error;

      setWorkflows(workflowsData.data || []);
      setTriggers((triggersData.data || []) as any);
    } catch (error: any) {
      console.error("Error fetching data:", error);
      toast.error("Failed to load workflows and triggers");
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Creates a new webhook trigger for a workflow
   * 
   * Process:
   * 1. Insert trigger record into database
   * 2. Generate unique webhook URL using trigger ID
   * 3. Update trigger record with webhook URL
   * 4. Refresh data to show new trigger
   * 
   * Webhook URL Format:
   * {SUPABASE_URL}/functions/v1/workflow-webhook?id={trigger_id}
   * 
   * @param workflowId - The workflow to create a trigger for
   */
  const createWebhookTrigger = async (workflowId: string) => {
    try {
      // Step 1: Create trigger record
      const { data, error } = await supabase
        .from("workflow_triggers")
        .insert({
          workflow_id: workflowId,
          customer_id: customerId,
          trigger_type: "webhook",
          trigger_config: {},           // Empty config for now
          is_enabled: true              // Active by default
        })
        .select()
        .single();

      if (error) throw error;

      // Step 2: Generate unique webhook URL using trigger ID
      const webhookUrl = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/workflow-webhook?id=${data.id}`;
      
      // Step 3: Update trigger with webhook URL
      await supabase
        .from("workflow_triggers")
        .update({ webhook_url: webhookUrl })
        .eq("id", data.id);

      toast.success("Webhook trigger created!");
      
      // Step 4: Refresh UI
      fetchData();
    } catch (error: any) {
      console.error("Error creating webhook:", error);
      toast.error(`Failed to create webhook: ${error.message}`);
    }
  };

  /**
   * Toggles a trigger's enabled/disabled state
   * When disabled, webhook will still exist but won't execute workflows
   * 
   * @param triggerId - The trigger to toggle
   * @param currentState - Current enabled state (will be inverted)
   */
  const toggleTrigger = async (triggerId: string, currentState: boolean) => {
    try {
      const { error } = await supabase
        .from("workflow_triggers")
        .update({ is_enabled: !currentState })
        .eq("id", triggerId);

      if (error) throw error;

      toast.success(`Trigger ${!currentState ? "enabled" : "disabled"}`);
      fetchData();  // Refresh to show updated state
    } catch (error: any) {
      console.error("Error toggling trigger:", error);
      toast.error("Failed to update trigger");
    }
  };

  /**
   * Copies webhook URL to clipboard for easy sharing
   * Uses Clipboard API for modern browsers
   * 
   * @param url - The webhook URL to copy
   */
  const copyWebhookUrl = (url: string) => {
    navigator.clipboard.writeText(url);
    toast.success("Webhook URL copied to clipboard!");
  };

  /**
   * Tests a webhook by sending a POST request to it
   * Sends test payload with timestamp for identification
   * 
   * Test Payload:
   * {
   *   "test": true,
   *   "timestamp": "2024-01-01T12:00:00.000Z"
   * }
   * 
   * @param webhookUrl - The webhook URL to test
   */
  const testWebhook = async (webhookUrl: string) => {
    try {
      const response = await fetch(webhookUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          test: true,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      toast.success("Test webhook triggered successfully!");
    } catch (error: any) {
      console.error("Error testing webhook:", error);
      toast.error(`Failed to test webhook: ${error.message}`);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Workflow Triggers</CardTitle>
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
    <div className="space-y-6">
      {/* Active Triggers List */}
      <Card>
        <CardHeader>
          <CardTitle>Active Triggers</CardTitle>
          <CardDescription>Manage webhook and scheduled triggers for your workflows</CardDescription>
        </CardHeader>
        <CardContent>
          {/* Empty state when no triggers configured */}
          {triggers.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No triggers configured yet. Create a workflow with triggers to see them here.
            </div>
          ) : (
            /* List of configured triggers */
            <div className="space-y-4">
              {triggers.map((trigger) => (
                <Card key={trigger.id}>
                  <CardContent className="pt-6">
                    <div className="space-y-4">
                      {/* Trigger Header: Icon, name, enable/disable toggle */}
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            {/* Icon based on trigger type */}
                            {trigger.trigger_type === "webhook" ? (
                              <Webhook className="h-4 w-4" />
                            ) : (
                              <Clock className="h-4 w-4" />
                            )}
                            <h4 className="font-semibold">
                              {trigger.workflows?.workflow_name || "Unknown Workflow"}
                            </h4>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{trigger.trigger_type}</Badge>
                            {/* Show last triggered timestamp if available */}
                            {trigger.last_triggered_at && (
                              <span className="text-xs text-muted-foreground">
                                Last: {new Date(trigger.last_triggered_at).toLocaleString()}
                              </span>
                            )}
                          </div>
                        </div>
                        {/* Enable/disable toggle */}
                        <div className="flex items-center gap-2">
                          <Label htmlFor={`trigger-${trigger.id}`} className="text-sm">
                            Enabled
                          </Label>
                          <Switch
                            id={`trigger-${trigger.id}`}
                            checked={trigger.is_enabled}
                            onCheckedChange={() => toggleTrigger(trigger.id, trigger.is_enabled)}
                          />
                        </div>
                      </div>

                      {/* Webhook-specific UI: URL display, copy, and test buttons */}
                      {trigger.trigger_type === "webhook" && trigger.webhook_url && (
                        <div className="space-y-2">
                          <Label>Webhook URL</Label>
                          <div className="flex gap-2">
                            {/* Read-only URL input */}
                            <Input
                              value={trigger.webhook_url}
                              readOnly
                              className="font-mono text-xs"
                            />
                            {/* Copy to clipboard button */}
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => copyWebhookUrl(trigger.webhook_url!)}
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                            {/* Test webhook button */}
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => testWebhook(trigger.webhook_url!)}
                            >
                              Test
                            </Button>
                          </div>
                          <p className="text-xs text-muted-foreground">
                            Send POST requests to this URL to trigger the workflow
                          </p>
                        </div>
                      )}

                      {/* Schedule-specific UI: Cron config display */}
                      {trigger.trigger_type === "schedule" && (
                        <div className="space-y-2">
                          <Label>Schedule Configuration</Label>
                          <div className="p-3 bg-muted rounded font-mono text-sm">
                            {JSON.stringify(trigger.trigger_config, null, 2)}
                          </div>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions: Add webhook triggers for existing workflows */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Create new triggers for your workflows</CardDescription>
        </CardHeader>
        <CardContent>
          {/* Empty state when no workflows exist */}
          {workflows.length === 0 ? (
            <div className="text-center py-4 text-muted-foreground">
              Create a workflow first to add triggers
            </div>
          ) : (
            /* List of workflows with add webhook button */
            <div className="space-y-3">
              {workflows.map((workflow) => (
                <div
                  key={workflow.id}
                  className="flex items-center justify-between p-3 border rounded"
                >
                  <span className="font-medium">{workflow.workflow_name}</span>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => createWebhookTrigger(workflow.id)}
                  >
                    <Webhook className="h-4 w-4 mr-2" />
                    Add Webhook
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
