import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.58.0';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface FlowLog {
  timestamp: string;
  table: string;
  operation: 'INSERT' | 'UPDATE' | 'DELETE' | 'SELECT';
  record_count: number;
  user_id?: string;
  customer_id?: string;
  duration_ms?: number;
  related_tables?: string[];
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { action } = await req.json();

    console.log('Database flow logger - Action:', action);

    if (action === 'trace_workflow') {
      // Trace a complete workflow execution flow
      const flowLogs: FlowLog[] = [];

      // 1. Workflow Execution Started
      const { data: execution } = await supabase
        .from('workflow_executions')
        .select('id, workflow_id, customer_id, created_at')
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      if (execution) {
        flowLogs.push({
          timestamp: execution.created_at,
          table: 'workflow_executions',
          operation: 'INSERT',
          record_count: 1,
          customer_id: execution.customer_id
        });

        // 2. Check if workflow generated audit logs
        const { data: auditLogs, count: auditCount } = await supabase
          .from('audit_logs')
          .select('*', { count: 'exact', head: false })
          .eq('customer_id', execution.customer_id)
          .gte('created_at', execution.created_at);

        if (auditCount && auditCount > 0) {
          flowLogs.push({
            timestamp: new Date().toISOString(),
            table: 'audit_logs',
            operation: 'INSERT',
            record_count: auditCount,
            customer_id: execution.customer_id,
            related_tables: ['workflow_executions']
          });
        }

        // 3. Check if evidence was generated
        const { data: evidence, count: evidenceCount } = await supabase
          .from('evidence_files')
          .select('*', { count: 'exact', head: false })
          .eq('customer_id', execution.customer_id)
          .gte('uploaded_at', execution.created_at);

        if (evidenceCount && evidenceCount > 0) {
          flowLogs.push({
            timestamp: new Date().toISOString(),
            table: 'evidence_files',
            operation: 'INSERT',
            record_count: evidenceCount,
            customer_id: execution.customer_id,
            related_tables: ['workflow_executions', 'compliance_controls']
          });
        }

        // 4. Check for MCP execution logs
        const { data: mcpLogs, count: mcpCount } = await supabase
          .from('mcp_execution_logs')
          .select('*', { count: 'exact', head: false })
          .eq('customer_id', execution.customer_id)
          .gte('timestamp', execution.created_at);

        if (mcpCount && mcpCount > 0) {
          flowLogs.push({
            timestamp: new Date().toISOString(),
            table: 'mcp_execution_logs',
            operation: 'INSERT',
            record_count: mcpCount,
            customer_id: execution.customer_id,
            related_tables: ['workflow_executions', 'mcp_tools']
          });
        }

        return new Response(
          JSON.stringify({
            flow: 'workflow_execution',
            steps: flowLogs,
            summary: {
              total_operations: flowLogs.length,
              tables_affected: [...new Set(flowLogs.map(l => l.table))],
              total_records: flowLogs.reduce((sum, l) => sum + l.record_count, 0)
            }
          }),
          { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
    }

    if (action === 'trace_compliance') {
      // Trace compliance evidence flow
      const flowLogs: FlowLog[] = [];

      // 1. Get latest evidence upload
      const { data: evidence } = await supabase
        .from('evidence_files')
        .select('id, framework_id, control_id, customer_id, uploaded_at')
        .order('uploaded_at', { ascending: false })
        .limit(1)
        .single();

      if (evidence) {
        flowLogs.push({
          timestamp: evidence.uploaded_at,
          table: 'evidence_files',
          operation: 'INSERT',
          record_count: 1,
          customer_id: evidence.customer_id
        });

        // 2. Check framework
        if (evidence.framework_id) {
          const { data: framework } = await supabase
            .from('compliance_frameworks')
            .select('id, framework_name')
            .eq('id', evidence.framework_id)
            .single();

          if (framework) {
            flowLogs.push({
              timestamp: new Date().toISOString(),
              table: 'compliance_frameworks',
              operation: 'SELECT',
              record_count: 1,
              related_tables: ['evidence_files']
            });
          }
        }

        // 3. Check control
        if (evidence.control_id) {
          const { data: control } = await supabase
            .from('compliance_controls')
            .select('id, control_name')
            .eq('control_id', evidence.control_id)
            .eq('framework_id', evidence.framework_id)
            .single();

          if (control) {
            flowLogs.push({
              timestamp: new Date().toISOString(),
              table: 'compliance_controls',
              operation: 'SELECT',
              record_count: 1,
              related_tables: ['evidence_files', 'compliance_frameworks']
            });
          }
        }

        // 4. Check if audit log was created
        const { data: auditLog, count: auditCount } = await supabase
          .from('audit_logs')
          .select('*', { count: 'exact', head: false })
          .eq('customer_id', evidence.customer_id)
          .eq('system_name', 'evidence_management')
          .gte('created_at', evidence.uploaded_at);

        if (auditCount && auditCount > 0) {
          flowLogs.push({
            timestamp: new Date().toISOString(),
            table: 'audit_logs',
            operation: 'INSERT',
            record_count: auditCount,
            customer_id: evidence.customer_id,
            related_tables: ['evidence_files']
          });
        }

        return new Response(
          JSON.stringify({
            flow: 'compliance_evidence',
            steps: flowLogs,
            summary: {
              total_operations: flowLogs.length,
              tables_affected: [...new Set(flowLogs.map(l => l.table))],
              total_records: flowLogs.reduce((sum, l) => sum + l.record_count, 0)
            }
          }),
          { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
    }

    if (action === 'trace_knowledge') {
      // Trace knowledge article creation flow
      const flowLogs: FlowLog[] = [];

      // 1. Get latest article
      const { data: article } = await supabase
        .from('knowledge_articles')
        .select('id, customer_id, category_id, created_by, created_at')
        .order('created_at', { ascending: false })
        .limit(1)
        .single();

      if (article) {
        flowLogs.push({
          timestamp: article.created_at,
          table: 'knowledge_articles',
          operation: 'INSERT',
          record_count: 1,
          customer_id: article.customer_id,
          user_id: article.created_by
        });

        // 2. Check category
        if (article.category_id) {
          const { data: category } = await supabase
            .from('knowledge_categories')
            .select('id, name')
            .eq('id', article.category_id)
            .single();

          if (category) {
            flowLogs.push({
              timestamp: new Date().toISOString(),
              table: 'knowledge_categories',
              operation: 'SELECT',
              record_count: 1,
              related_tables: ['knowledge_articles']
            });
          }
        }

        // 3. Check access logs
        const { data: accessLogs, count: accessCount } = await supabase
          .from('knowledge_access_logs')
          .select('*', { count: 'exact', head: false })
          .eq('article_id', article.id);

        if (accessCount && accessCount > 0) {
          flowLogs.push({
            timestamp: new Date().toISOString(),
            table: 'knowledge_access_logs',
            operation: 'SELECT',
            record_count: accessCount,
            customer_id: article.customer_id,
            related_tables: ['knowledge_articles']
          });
        }

        // 4. Check AI interactions
        const { data: interactions, count: interactionCount } = await supabase
          .from('ai_interactions')
          .select('*', { count: 'exact', head: false })
          .eq('customer_id', article.customer_id)
          .gte('created_at', article.created_at)
          .limit(5);

        if (interactionCount && interactionCount > 0) {
          flowLogs.push({
            timestamp: new Date().toISOString(),
            table: 'ai_interactions',
            operation: 'INSERT',
            record_count: interactionCount,
            customer_id: article.customer_id,
            related_tables: ['knowledge_articles']
          });
        }

        return new Response(
          JSON.stringify({
            flow: 'knowledge_article',
            steps: flowLogs,
            summary: {
              total_operations: flowLogs.length,
              tables_affected: [...new Set(flowLogs.map(l => l.table))],
              total_records: flowLogs.reduce((sum, l) => sum + l.record_count, 0)
            }
          }),
          { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
    }

    return new Response(
      JSON.stringify({ error: 'Invalid action or no data found' }),
      { 
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );

  } catch (error) {
    console.error('Error in database-flow-logger:', error);
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
