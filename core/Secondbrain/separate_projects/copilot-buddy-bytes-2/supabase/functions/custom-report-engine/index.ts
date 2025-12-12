import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.38.0";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const { action, reportId, customerId } = await req.json();

    switch (action) {
      case 'execute_report': {
        const startTime = Date.now();
        
        // Get report definition
        const { data: report, error: reportError } = await supabase
          .from('custom_reports')
          .select('*')
          .eq('id', reportId)
          .single();

        if (reportError) throw reportError;

        try {
          let resultData: any[] = [];
          let resultCount = 0;

          // Execute queries based on data sources
          for (const source of report.data_sources) {
            const { table, columns, joins, filters } = source;
            
            let query = supabase.from(table).select(columns.join(', '));

            // Apply filters
            if (filters && Object.keys(filters).length > 0) {
              Object.entries(filters).forEach(([key, value]) => {
                if (Array.isArray(value)) {
                  query = query.in(key, value);
                } else {
                  query = query.eq(key, value);
                }
              });
            }

            // Apply customer filter
            query = query.eq('customer_id', customerId);

            const { data, error } = await query;
            if (error) throw error;

            resultData = resultData.concat(data || []);
            resultCount += data?.length || 0;
          }

          // Record execution
          const { error: execError } = await supabase
            .from('report_executions')
            .insert({
              report_id: reportId,
              customer_id: customerId,
              execution_type: 'manual',
              status: 'completed',
              result_count: resultCount,
              execution_time_ms: Date.now() - startTime
            });

          if (execError) console.error('Failed to record execution:', execError);

          // Update report last run time
          await supabase
            .from('custom_reports')
            .update({ last_run_at: new Date().toISOString() })
            .eq('id', reportId);

          return new Response(
            JSON.stringify({ 
              success: true, 
              data: resultData,
              count: resultCount,
              executionTime: Date.now() - startTime
            }),
            { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
          );
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown error';
          // Record failed execution
          await supabase
            .from('report_executions')
            .insert({
              report_id: reportId,
              customer_id: customerId,
              execution_type: 'manual',
              status: 'failed',
              error_message: errorMessage,
              execution_time_ms: Date.now() - startTime
            });

          throw error;
        }
      }

      case 'get_available_tables': {
        // Return available tables for report builder
        const tables = [
          { name: 'change_requests', label: 'Change Requests', columns: ['id', 'title', 'status', 'priority', 'created_at'] },
          { name: 'configuration_items', label: 'Configuration Items', columns: ['id', 'ci_name', 'ci_type', 'ci_status', 'criticality'] },
          { name: 'incidents', label: 'Incidents', columns: ['id', 'title', 'severity', 'status', 'detected_at'] },
          { name: 'workflows', label: 'Workflows', columns: ['id', 'name', 'status', 'created_at'] },
          { name: 'compliance_frameworks', label: 'Compliance Frameworks', columns: ['id', 'framework_name', 'industry'] },
          { name: 'audit_logs', label: 'Audit Logs', columns: ['id', 'action_type', 'system_name', 'timestamp'] }
        ];

        return new Response(
          JSON.stringify({ success: true, tables }),
          { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      case 'preview_report': {
        const { dataSources, filters } = await req.json();
        
        // Execute preview with limit
        let previewData: any[] = [];
        
        for (const source of dataSources) {
          const { table, columns } = source;
          const { data } = await supabase
            .from(table)
            .select(columns.join(', '))
            .eq('customer_id', customerId)
            .limit(10);
          
          previewData = previewData.concat(data || []);
        }

        return new Response(
          JSON.stringify({ success: true, preview: previewData }),
          { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      case 'schedule_report': {
        const { scheduleCron, recipients } = await req.json();
        
        // Update report with schedule
        const { error } = await supabase
          .from('custom_reports')
          .update({
            is_scheduled: true,
            schedule_cron: scheduleCron,
            recipients: recipients
          })
          .eq('id', reportId);

        if (error) throw error;

        return new Response(
          JSON.stringify({ success: true, message: 'Report scheduled successfully' }),
          { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }

      default:
        throw new Error('Invalid action');
    }
  } catch (error) {
    console.error('Custom report engine error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return new Response(
      JSON.stringify({ error: errorMessage }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});
