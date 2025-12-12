import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.3";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const { workflowId, inputData, customerId } = await req.json();
    console.log('Executing workflow:', { workflowId, customerId });

    // Fetch workflow template
    const { data: workflow, error: workflowError } = await supabaseClient
      .from('workflow_templates')
      .select('*')
      .eq('id', workflowId)
      .single();

    if (workflowError || !workflow) {
      throw new Error('Workflow not found');
    }

    // Create execution record
    const { data: execution, error: executionError } = await supabaseClient
      .from('workflow_execution_queue')
      .insert({
        workflow_id: workflowId,
        customer_id: customerId,
        status: 'running',
        input_data: inputData,
        started_at: new Date().toISOString()
      })
      .select()
      .single();

    if (executionError) throw executionError;

    console.log('Created execution:', execution.id);

    // Execute workflow nodes
    const nodes = workflow.nodes || [];
    const edges = workflow.edges || [];
    const nodeResults: any = {};

    try {
      // Sort nodes by execution order (topological sort would be ideal)
      const sortedNodes = [...nodes].sort((a: any, b: any) => {
        const aPos = a.position?.y || 0;
        const bPos = b.position?.y || 0;
        return aPos - bPos;
      });

      for (const node of sortedNodes) {
        console.log('Executing node:', node.id, node.type);

        // Create step record
        const { data: step, error: stepError } = await supabaseClient
          .from('workflow_execution_steps')
          .insert({
            execution_id: execution.id,
            node_id: node.id,
            node_type: node.type,
            status: 'running',
            started_at: new Date().toISOString(),
            input_data: { ...inputData, previousResults: nodeResults }
          })
          .select()
          .single();

        if (stepError) throw stepError;

        const startTime = Date.now();
        let output: any = {};
        let stepStatus = 'completed';
        let errorMessage = null;

        try {
          // Execute node based on type
          switch (node.type) {
            case 'trigger':
              output = { triggered: true, timestamp: new Date().toISOString() };
              break;

            case 'action':
              output = await executeAction(node, inputData, nodeResults);
              break;

            case 'condition':
              output = await evaluateCondition(node, inputData, nodeResults);
              break;

            case 'api_call':
              output = await executeApiCall(node, inputData, nodeResults);
              break;

            case 'delay':
              const delayMs = node.data?.delayMs || 1000;
              await new Promise(resolve => setTimeout(resolve, delayMs));
              output = { delayed: delayMs };
              break;

            case 'transform':
              output = await transformData(node, inputData, nodeResults);
              break;

            default:
              output = { executed: true };
          }

          nodeResults[node.id] = output;
        } catch (nodeError: any) {
          console.error('Node execution error:', nodeError);
          stepStatus = 'failed';
          errorMessage = nodeError.message;
        }

        // Update step
        await supabaseClient
          .from('workflow_execution_steps')
          .update({
            status: stepStatus,
            output_data: output,
            error_message: errorMessage,
            completed_at: new Date().toISOString(),
            duration_ms: Date.now() - startTime
          })
          .eq('id', step.id);

        if (stepStatus === 'failed' && !node.data?.continueOnError) {
          throw new Error(`Node ${node.id} failed: ${errorMessage}`);
        }
      }

      // Update execution as completed
      await supabaseClient
        .from('workflow_execution_queue')
        .update({
          status: 'completed',
          completed_at: new Date().toISOString()
        })
        .eq('id', execution.id);

      // Update workflow analytics
      await updateWorkflowAnalytics(supabaseClient, workflowId, customerId, true, Date.now() - new Date(execution.created_at).getTime());

      console.log('Workflow execution completed successfully');

      return new Response(
        JSON.stringify({ 
          success: true, 
          executionId: execution.id,
          results: nodeResults
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );

    } catch (executionError: any) {
      console.error('Workflow execution error:', executionError);

      // Update execution as failed
      await supabaseClient
        .from('workflow_execution_queue')
        .update({
          status: 'failed',
          error_message: executionError.message,
          completed_at: new Date().toISOString()
        })
        .eq('id', execution.id);

      // Update workflow analytics
      await updateWorkflowAnalytics(supabaseClient, workflowId, customerId, false, Date.now() - new Date(execution.created_at).getTime());

      throw executionError;
    }

  } catch (error: any) {
    console.error('Error in workflow-orchestrator:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    );
  }
});

async function executeAction(node: any, inputData: any, previousResults: any): Promise<any> {
  console.log('Executing action:', node.data);
  return { actionExecuted: true, ...node.data };
}

async function evaluateCondition(node: any, inputData: any, previousResults: any): Promise<any> {
  console.log('Evaluating condition:', node.data);
  const condition = node.data?.condition || 'true';
  return { conditionMet: true, condition };
}

async function executeApiCall(node: any, inputData: any, previousResults: any): Promise<any> {
  console.log('Executing API call:', node.data);
  const url = node.data?.url;
  const method = node.data?.method || 'GET';
  
  if (!url) throw new Error('API URL not configured');

  const response = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: method !== 'GET' ? JSON.stringify(node.data?.body || {}) : undefined
  });

  return await response.json();
}

async function transformData(node: any, inputData: any, previousResults: any): Promise<any> {
  console.log('Transforming data:', node.data);
  return { transformed: true, data: { ...inputData, ...previousResults } };
}

async function updateWorkflowAnalytics(
  client: any, 
  workflowId: string, 
  customerId: string, 
  success: boolean,
  duration: number
) {
  const today = new Date().toISOString().split('T')[0];

  const { data: existing } = await client
    .from('workflow_analytics')
    .select('*')
    .eq('workflow_id', workflowId)
    .eq('customer_id', customerId)
    .eq('date', today)
    .single();

  if (existing) {
    await client
      .from('workflow_analytics')
      .update({
        execution_count: existing.execution_count + 1,
        success_count: success ? existing.success_count + 1 : existing.success_count,
        failure_count: success ? existing.failure_count : existing.failure_count + 1,
        total_duration_ms: existing.total_duration_ms + duration,
        avg_duration_ms: Math.round((existing.total_duration_ms + duration) / (existing.execution_count + 1))
      })
      .eq('id', existing.id);
  } else {
    await client
      .from('workflow_analytics')
      .insert({
        workflow_id: workflowId,
        customer_id: customerId,
        date: today,
        execution_count: 1,
        success_count: success ? 1 : 0,
        failure_count: success ? 0 : 1,
        total_duration_ms: duration,
        avg_duration_ms: duration
      });
  }
}