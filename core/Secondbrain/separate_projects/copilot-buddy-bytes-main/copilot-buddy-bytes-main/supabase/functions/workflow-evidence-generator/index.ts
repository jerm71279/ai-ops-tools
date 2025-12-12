import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.58.0';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface WorkflowExecutionData {
  workflow_id: string;
  workflow_name: string;
  customer_id: string;
  triggered_by: string;
  execution_id: string;
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { workflow_id, workflow_name, customer_id, triggered_by, execution_id }: WorkflowExecutionData = await req.json();

    console.log('Generating evidence for workflow:', workflow_name);

    // Map workflows to relevant compliance controls
    const workflowControlMapping: Record<string, { frameworks: string[], controls: string[], category: string }> = {
      'User Access Provisioning': {
        frameworks: ['0ec74d49-a739-45da-93e5-4bfa9de1c045'], // ISO 27001
        controls: ['A.9.2'],
        category: 'access_control'
      },
      'Employee Access Revocation': {
        frameworks: ['0ec74d49-a739-45da-93e5-4bfa9de1c045'],
        controls: ['A.9.2'],
        category: 'access_control'
      },
      'Daily Database Backup': {
        frameworks: ['0ec74d49-a739-45da-93e5-4bfa9de1c045'],
        controls: ['A.12.4'],
        category: 'monitoring'
      },
      'Security Incident Response': {
        frameworks: ['0ec74d49-a739-45da-93e5-4bfa9de1c045'],
        controls: ['A.16.1'],
        category: 'incident_response'
      },
      'Production Change Approval': {
        frameworks: ['0ec74d49-a739-45da-93e5-4bfa9de1c045'],
        controls: ['A.12.4', 'A.18.1'],
        category: 'monitoring'
      },
      'GDPR Subject Access Request': {
        frameworks: ['0ec74d49-a739-45da-93e5-4bfa9de1c045'],
        controls: ['A.18.1'],
        category: 'compliance'
      },
      'Automated Log Archival': {
        frameworks: ['0ec74d49-a739-45da-93e5-4bfa9de1c045'],
        controls: ['A.12.4'],
        category: 'monitoring'
      },
      'Weekly Compliance Report': {
        frameworks: ['0ec74d49-a739-45da-93e5-4bfa9de1c045'],
        controls: ['A.18.1'],
        category: 'compliance'
      },
      'Evidence Validation Workflow': {
        frameworks: ['0ec74d49-a739-45da-93e5-4bfa9de1c045'],
        controls: ['A.18.1'],
        category: 'compliance'
      },
      'Control Gap Analysis': {
        frameworks: ['0ec74d49-a739-45da-93e5-4bfa9de1c045'],
        controls: ['A.5.1', 'A.18.1'],
        category: 'governance'
      }
    };

    const mapping = workflowControlMapping[workflow_name];
    
    if (!mapping) {
      console.log('No control mapping found for workflow:', workflow_name);
      return new Response(
        JSON.stringify({ success: false, message: 'No control mapping for this workflow' }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Generate evidence for each control
    const evidenceRecords = [];
    const timestamp = new Date().toISOString().split('T')[0];

    for (const framework_id of mapping.frameworks) {
      for (const control_id of mapping.controls) {
        const fileName = `${workflow_name.toLowerCase().replace(/\s+/g, '_')}_${control_id.replace('.', '')}_${timestamp}.json`;
        const evidenceData = {
          workflow_execution_id: execution_id,
          workflow_name,
          control_id,
          timestamp: new Date().toISOString(),
          status: 'completed',
          evidence_type: 'automated_workflow',
          metadata: {
            triggered_by,
            execution_time: new Date().toISOString()
          }
        };

        const { data: evidence, error: evidenceError } = await supabase
          .from('evidence_files')
          .insert({
            customer_id,
            framework_id,
            control_id,
            file_name: fileName,
            file_type: 'application/json',
            file_size: JSON.stringify(evidenceData).length,
            storage_path: `/evidence/${framework_id}/${fileName}`,
            description: `Automated evidence generated from workflow execution: ${workflow_name}`,
            uploaded_by: triggered_by,
            compliance_tags: ['automated', mapping.category, control_id.toLowerCase()]
          })
          .select()
          .single();

        if (evidenceError) {
          console.error('Error creating evidence:', evidenceError);
        } else {
          evidenceRecords.push(evidence);
          console.log('Evidence created:', fileName);
        }
      }
    }

    return new Response(
      JSON.stringify({ 
        success: true, 
        evidence_count: evidenceRecords.length,
        evidence: evidenceRecords 
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error in workflow-evidence-generator:', error);
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
