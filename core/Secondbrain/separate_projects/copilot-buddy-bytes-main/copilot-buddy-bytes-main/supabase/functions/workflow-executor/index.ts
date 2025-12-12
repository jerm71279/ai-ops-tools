/**
 * Workflow Executor Edge Function
 * 
 * Core workflow execution engine that orchestrates multi-step automated workflows.
 * Executes workflow steps sequentially, handles conditional logic, logs execution details,
 * and manages execution state (running, completed, failed).
 * 
 * Features:
 * - Sequential step execution
 * - Multiple step types (API calls, data transforms, conditions, database ops, delays)
 * - Detailed execution logging
 * - Error handling and recovery
 * - Execution time tracking
 * - State management (workflow_executions table)
 * 
 * Step Types Supported:
 * - api_call: HTTP requests to external APIs
 * - data_transform: JSON data mapping/transformation
 * - condition: Conditional evaluation (equals, greater_than, contains, etc.)
 * - notification: Send notifications (placeholder for integration)
 * - database_operation: CRUD operations on database tables
 * - delay: Wait/sleep operations
 * 
 * Integration Points:
 * - workflow-webhook: Called by webhook triggers
 * - WorkflowBuilder: Workflows created in UI are executed here
 * - workflow_executions: Execution logs stored here
 * 
 * Security:
 * - Uses service role key for database access (bypasses RLS)
 * - Validates workflow existence and active status
 * - Creates audit trail in execution logs
 * 
 * @module workflow-executor
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { z } from "https://deno.land/x/zod@v3.22.4/mod.ts";

/**
 * CORS headers for cross-origin requests from web app
 * Allows workflow execution from browser
 */
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

// Input validation schema
const executeWorkflowSchema = z.object({
  workflow_id: z.string().uuid('Invalid workflow ID format'),
  trigger_data: z.record(z.any()).optional(),
  triggered_by: z.string().max(50, 'Triggered by value too long').optional(),
});

// Maximum payload size (1MB)
const MAX_PAYLOAD_SIZE = 1024 * 1024;

serve(async (req) => {
  // Handle preflight OPTIONS request
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    // Check payload size
    const contentLength = req.headers.get('content-length');
    if (contentLength && parseInt(contentLength) > MAX_PAYLOAD_SIZE) {
      return new Response(
        JSON.stringify({ error: 'Payload too large. Maximum size is 1MB' }),
        { status: 413, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Initialize Supabase client with service role (full access)
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Parse and validate request payload
    const requestBody = await req.json();
    const validatedInput = executeWorkflowSchema.parse(requestBody);
    const { workflow_id, trigger_data, triggered_by = 'manual' } = validatedInput;

    // Validation: workflow_id is required
    if (!workflow_id) {
      return new Response(
        JSON.stringify({ error: 'workflow_id is required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    console.log(`Executing workflow ${workflow_id}, triggered by: ${triggered_by}`);

    // Step 1: Fetch workflow definition from database
    const { data: workflow, error: workflowError } = await supabase
      .from('workflows')
      .select('*')
      .eq('id', workflow_id)
      .single();

    if (workflowError || !workflow) {
      return new Response(
        JSON.stringify({ error: 'Workflow not found' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Validation: workflow must be active
    if (!workflow.is_active) {
      return new Response(
        JSON.stringify({ error: 'Workflow is not active' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Step 2: Create execution record (status: running)
    // This provides audit trail and allows monitoring in UI
    const { data: execution, error: executionError } = await supabase
      .from('workflow_executions')
      .insert({
        workflow_id: workflow_id,
        customer_id: workflow.customer_id,
        triggered_by: triggered_by,       // manual, webhook, schedule, event
        trigger_data: trigger_data,        // Original payload (for data transforms)
        status: 'running'
      })
      .select()
      .single();

    if (executionError) {
      console.error('Failed to create execution record:', executionError);
      return new Response(
        JSON.stringify({ error: 'Failed to start execution' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Step 3: Execute workflow steps sequentially
    const executionLog: any[] = [];            // Accumulate step results
    const steps = workflow.steps as any[];     // Workflow steps from JSONB column

    try {
      // Loop through steps in order
      for (const step of steps) {
        console.log(`Executing step: ${step.name} (${step.type})`);
        
        const stepStartTime = Date.now();
        let stepResult: any = {};

        // Execute step based on type
        switch (step.type) {
          case 'api_call':
            stepResult = await executeApiCall(step.config);
            break;
          case 'data_transform':
            stepResult = await executeDataTransform(step.config, trigger_data);
            break;
          case 'condition':
            stepResult = await evaluateCondition(step.config, trigger_data);
            break;
          case 'notification':
            stepResult = await sendNotification(step.config, workflow.customer_id);
            break;
          case 'database_operation':
            stepResult = await executeDatabaseOperation(step.config, supabase);
            break;
          case 'delay':
            stepResult = await executeDelay(step.config);
            break;
          default:
            // Unknown step type - log warning but don't fail
            stepResult = { success: true, message: `Skipped unknown step type: ${step.type}` };
        }

        // Log step execution details
        executionLog.push({
          step_id: step.id,
          step_name: step.name,
          step_type: step.type,
          duration_ms: Date.now() - stepStartTime,
          result: stepResult,
          timestamp: new Date().toISOString()
        });

        // Check if step failed - stop execution if no error handling defined
        if (!stepResult.success) {
          throw new Error(`Step "${step.name}" failed: ${stepResult.error || 'Unknown error'}`);
        }
      }

      // Step 4: Mark execution as completed
      await supabase
        .from('workflow_executions')
        .update({
          status: 'completed',
          completed_at: new Date().toISOString(),
          execution_log: executionLog            // Store step logs in JSONB column
        })
        .eq('id', execution.id);

      console.log(`Workflow ${workflow_id} completed successfully`);

      // Return success response with execution details
      return new Response(
        JSON.stringify({
          success: true,
          execution_id: execution.id,
          message: 'Workflow completed successfully',
          execution_log: executionLog
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );

    } catch (error: any) {
      // Execution failed - log error and update execution record
      console.error('Workflow execution error:', error);

      // Step 5: Mark execution as failed
      await supabase
        .from('workflow_executions')
        .update({
          status: 'failed',
          completed_at: new Date().toISOString(),
          error_message: error.message,
          execution_log: executionLog            // Include partial logs for debugging
        })
        .eq('id', execution.id);

      // Return error response with partial logs
      return new Response(
        JSON.stringify({
          success: false,
          execution_id: execution.id,
          error: error.message,
          execution_log: executionLog
        }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

  } catch (error: any) {
    // Top-level error (parsing, validation, etc.)
    console.error('Request error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

/**
 * Executes an HTTP API call step
 * 
 * Config format:
 * {
 *   "url": "https://api.example.com/endpoint",
 *   "method": "GET" | "POST" | "PUT" | "DELETE",
 *   "headers": { "Authorization": "Bearer token" },
 *   "body": { "key": "value" }
 * }
 * 
 * @param config - Step configuration from workflow definition
 * @returns { success: boolean, data?: any, status?: number, error?: string }
 */
async function executeApiCall(config: any) {
  try {
    const { url, method = 'GET', headers = {}, body } = config;
    
    const response = await fetch(url, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined
    });

    const data = await response.json();
    
    return {
      success: response.ok,
      data,
      status: response.status
    };
  } catch (error: any) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Transforms data using JSON path mapping
 * Maps input data to output format based on configuration
 * 
 * Config format:
 * {
 *   "mapping": {
 *     "output_field": "input.nested.path"
 *   }
 * }
 * 
 * Example:
 * Input: { "user": { "name": "John" } }
 * Mapping: { "userName": "user.name" }
 * Output: { "userName": "John" }
 * 
 * @param config - Mapping configuration
 * @param inputData - Data to transform (usually trigger_data)
 * @returns { success: boolean, data?: object, error?: string }
 */
async function executeDataTransform(config: any, inputData: any) {
  try {
    const { mapping } = config;
    const result: any = {};

    if (mapping) {
      // Map each output field to input path
      for (const [key, path] of Object.entries(mapping)) {
        result[key] = getNestedValue(inputData, path as string);
      }
    }

    return {
      success: true,
      data: result
    };
  } catch (error: any) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Evaluates a conditional expression
 * Supports multiple comparison operators for branching logic
 * 
 * Config format:
 * {
 *   "field": "data.status",
 *   "operator": "equals" | "not_equals" | "greater_than" | "less_than" | "contains",
 *   "value": "active"
 * }
 * 
 * @param config - Condition configuration
 * @param data - Data to evaluate condition against
 * @returns { success: boolean, condition_met: boolean, field_value: any, error?: string }
 */
async function evaluateCondition(config: any, data: any) {
  try {
    const { field, operator, value } = config;
    const fieldValue = getNestedValue(data, field);

    let result = false;

    // Evaluate based on operator
    switch (operator) {
      case 'equals':
        result = fieldValue === value;
        break;
      case 'not_equals':
        result = fieldValue !== value;
        break;
      case 'greater_than':
        result = fieldValue > value;
        break;
      case 'less_than':
        result = fieldValue < value;
        break;
      case 'contains':
        result = String(fieldValue).includes(value);
        break;
      default:
        result = false;
    }

    return {
      success: true,
      condition_met: result,
      field_value: fieldValue
    };
  } catch (error: any) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Sends a notification (placeholder implementation)
 * TODO: Integrate with actual notification system (email, Slack, etc.)
 * 
 * Config format:
 * {
 *   "type": "email" | "slack" | "webhook",
 *   "recipient": "user@example.com",
 *   "message": "Workflow completed"
 * }
 * 
 * @param config - Notification configuration
 * @param customer_id - Customer context for notification
 * @returns { success: boolean, message: string, error?: string }
 */
async function sendNotification(config: any, customer_id: string) {
  try {
    // TODO: Implement actual notification sending
    console.log('Sending notification:', config);
    
    return {
      success: true,
      message: 'Notification sent'
    };
  } catch (error: any) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Executes a database operation (CRUD)
 * Uses Supabase client for database access
 * 
 * Config format:
 * {
 *   "table": "table_name",
 *   "operation": "insert" | "update" | "delete",
 *   "data": { "column": "value" },
 *   "filters": { "id": "123" }
 * }
 * 
 * Note: Filters only used for update/delete operations
 * 
 * @param config - Database operation configuration
 * @param supabase - Supabase client instance
 * @returns { success: boolean, data?: any, error?: string }
 */
async function executeDatabaseOperation(config: any, supabase: any) {
  try {
    const { table, operation, data, filters } = config;

    let query = supabase.from(table);

    switch (operation) {
      case 'insert':
        query = query.insert(data);
        break;
      case 'update':
        query = query.update(data);
        // Apply filters for update
        if (filters) {
          Object.entries(filters).forEach(([key, value]) => {
            query = query.eq(key, value);
          });
        }
        break;
      case 'delete':
        // Apply filters for delete
        if (filters) {
          Object.entries(filters).forEach(([key, value]) => {
            query = query.eq(key, value);
          });
        }
        query = query.delete();
        break;
      default:
        throw new Error(`Unknown operation: ${operation}`);
    }

    const { data: result, error } = await query;

    if (error) throw error;

    return {
      success: true,
      data: result
    };
  } catch (error: any) {
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Executes a delay/wait operation
 * Pauses workflow execution for specified duration
 * Useful for rate limiting or waiting for external processes
 * 
 * Config format:
 * {
 *   "duration_ms": 5000
 * }
 * 
 * @param config - Delay configuration
 * @returns { success: boolean, message: string }
 */
async function executeDelay(config: any) {
  const { duration_ms = 1000 } = config;
  await new Promise(resolve => setTimeout(resolve, duration_ms));
  
  return {
    success: true,
    message: `Delayed for ${duration_ms}ms`
  };
}

/**
 * Gets a nested value from an object using dot notation path
 * Safely handles missing intermediate properties
 * 
 * Example:
 * obj = { "user": { "profile": { "name": "John" } } }
 * path = "user.profile.name"
 * returns: "John"
 * 
 * @param obj - Object to extract value from
 * @param path - Dot-separated path (e.g., "user.profile.name")
 * @returns The value at the path, or undefined if not found
 */
function getNestedValue(obj: any, path: string) {
  return path.split('.').reduce((acc, part) => acc?.[part], obj);
}
