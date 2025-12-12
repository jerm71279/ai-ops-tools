import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.58.0';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    console.log('Batch generating evidence for all workflow executions...');

    // Get all workflow executions
    const { data: executions, error: executionsError } = await supabase
      .from('workflow_executions')
      .select(`
        id,
        workflow_id,
        customer_id,
        triggered_by,
        workflows!inner(workflow_name)
      `)
      .eq('status', 'completed')
      .order('created_at', { ascending: false });

    if (executionsError) {
      throw executionsError;
    }

    console.log(`Found ${executions?.length || 0} workflow executions`);

    let successCount = 0;
    let errorCount = 0;

    for (const execution of executions || []) {
      try {
        const workflowName = (execution.workflows as any).workflow_name;
        
        console.log(`Generating evidence for: ${workflowName}`);

        // Call the workflow evidence generator function
        const { data, error } = await supabase.functions.invoke('workflow-evidence-generator', {
          body: {
            workflow_id: execution.workflow_id,
            workflow_name: workflowName,
            customer_id: execution.customer_id,
            triggered_by: execution.triggered_by || 'system',
            execution_id: execution.id
          }
        });

        if (error) {
          console.error(`Error for ${workflowName}:`, error);
          errorCount++;
        } else {
          console.log(`Success for ${workflowName}:`, data);
          successCount++;
        }
      } catch (err) {
        console.error('Error processing execution:', err);
        errorCount++;
      }
    }

    return new Response(
      JSON.stringify({ 
        success: true, 
        total_executions: executions?.length || 0,
        evidence_generated: successCount,
        errors: errorCount
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error in batch-evidence-generator:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    return new Response(
      JSON.stringify({ error: errorMessage }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    );
  }
});
