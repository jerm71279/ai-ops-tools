import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { action, period = 'daily', customerId } = await req.json();
    console.log('Analytics processor:', { action, period, customerId });

    if (!customerId) {
      return new Response(
        JSON.stringify({ error: 'Customer ID is required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    let result;

    switch (action) {
      case 'aggregate_metrics':
        result = await aggregateMetrics(supabase, customerId, period);
        break;
      case 'generate_report':
        result = await generateReport(supabase, customerId);
        break;
      case 'check_benchmarks':
        result = await checkBenchmarks(supabase, customerId);
        break;
      case 'create_alerts':
        result = await createAlerts(supabase, customerId);
        break;
      default:
        return new Response(
          JSON.stringify({ error: 'Invalid action' }),
          { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
    }

    return new Response(
      JSON.stringify(result),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  } catch (error) {
    console.error('Analytics processor error:', error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

async function aggregateMetrics(supabase: any, customerId: string, period: string) {
  const now = new Date();
  const periodStart = new Date(now);
  periodStart.setHours(0, 0, 0, 0);
  
  if (period === 'weekly') {
    periodStart.setDate(periodStart.getDate() - 7);
  } else if (period === 'monthly') {
    periodStart.setMonth(periodStart.getMonth() - 1);
  }

  // Aggregate change request metrics
  const { data: changes } = await supabase
    .from('change_requests')
    .select('change_status, risk_level, priority')
    .eq('customer_id', customerId)
    .gte('created_at', periodStart.toISOString());

  const changeMetrics = {
    total: changes?.length || 0,
    approved: changes?.filter((c: any) => c.change_status === 'approved').length || 0,
    rejected: changes?.filter((c: any) => c.change_status === 'rejected').length || 0,
    high_risk: changes?.filter((c: any) => c.risk_level === 'high').length || 0,
  };

  // Aggregate CMDB metrics
  const { data: cis } = await supabase
    .from('configuration_items')
    .select('ci_status, criticality')
    .eq('customer_id', customerId);

  const cmdbMetrics = {
    total: cis?.length || 0,
    active: cis?.filter((ci: any) => ci.ci_status === 'active').length || 0,
    critical: cis?.filter((ci: any) => ci.criticality === 'critical').length || 0,
  };

  // Aggregate workflow metrics
  const { data: workflows } = await supabase
    .from('workflow_executions')
    .select('status')
    .eq('customer_id', customerId)
    .gte('started_at', periodStart.toISOString());

  const workflowMetrics = {
    total: workflows?.length || 0,
    success: workflows?.filter((w: any) => w.status === 'completed').length || 0,
    failed: workflows?.filter((w: any) => w.status === 'failed').length || 0,
    success_rate: workflows?.length ? 
      ((workflows.filter((w: any) => w.status === 'completed').length / workflows.length) * 100).toFixed(1) : 
      0,
  };

  // Store aggregated metrics
  const metrics = [
    { metric_type: 'change_management', metric_name: 'total_changes', metric_value: changeMetrics.total },
    { metric_type: 'change_management', metric_name: 'approval_rate', metric_value: changeMetrics.total ? (changeMetrics.approved / changeMetrics.total * 100) : 0 },
    { metric_type: 'cmdb', metric_name: 'total_assets', metric_value: cmdbMetrics.total },
    { metric_type: 'cmdb', metric_name: 'critical_assets', metric_value: cmdbMetrics.critical },
    { metric_type: 'workflow', metric_name: 'total_executions', metric_value: workflowMetrics.total },
    { metric_type: 'workflow', metric_name: 'success_rate', metric_value: parseFloat(workflowMetrics.success_rate as string) },
  ];

  for (const metric of metrics) {
    await supabase.from('system_metrics').upsert({
      customer_id: customerId,
      ...metric,
      metric_unit: metric.metric_name.includes('rate') ? '%' : 'count',
      aggregation_period: period,
      period_start: periodStart.toISOString(),
      period_end: now.toISOString(),
    });
  }

  return { success: true, metrics: { change: changeMetrics, cmdb: cmdbMetrics, workflow: workflowMetrics } };
}

async function generateReport(supabase: any, customerId: string) {
  const now = new Date();
  const periodStart = new Date(now);
  periodStart.setDate(periodStart.getDate() - 30);

  const { data: metrics } = await supabase
    .from('system_metrics')
    .select('*')
    .eq('customer_id', customerId)
    .gte('period_start', periodStart.toISOString())
    .order('period_start', { ascending: false });

  const reportData = {
    summary: {
      total_metrics: metrics?.length || 0,
      period: '30 days',
      generated_at: now.toISOString(),
    },
    metrics: metrics || [],
  };

  const { data: report } = await supabase
    .from('generated_reports')
    .insert({
      customer_id: customerId,
      report_name: `System Report - ${now.toLocaleDateString()}`,
      report_type: 'system_performance',
      report_period_start: periodStart.toISOString(),
      report_period_end: now.toISOString(),
      report_data: reportData,
      generated_by: customerId,
      status: 'completed',
    })
    .select()
    .single();

  return { success: true, report };
}

async function checkBenchmarks(supabase: any, customerId: string) {
  const { data: benchmarks } = await supabase
    .from('performance_benchmarks')
    .select('*')
    .eq('customer_id', customerId);

  if (!benchmarks || benchmarks.length === 0) {
    return { success: true, checked: 0, message: 'No benchmarks configured' };
  }

  const updates = [];
  for (const benchmark of benchmarks) {
    // Get current metric value
    const { data: metrics } = await supabase
      .from('system_metrics')
      .select('metric_value')
      .eq('customer_id', customerId)
      .eq('metric_name', benchmark.benchmark_name)
      .order('period_start', { ascending: false })
      .limit(1);

    if (metrics && metrics.length > 0) {
      const currentValue = metrics[0].metric_value;
      const targetValue = benchmark.target_value;
      const operator = benchmark.comparison_operator;

      let status = 'met';
      if (operator === 'gte' && currentValue < targetValue) status = 'not_met';
      if (operator === 'lte' && currentValue > targetValue) status = 'not_met';
      if (operator === 'eq' && currentValue !== targetValue) status = 'not_met';

      updates.push({
        id: benchmark.id,
        current_value: currentValue,
        status,
        last_measured_at: new Date().toISOString(),
      });
    }
  }

  for (const update of updates) {
    await supabase
      .from('performance_benchmarks')
      .update(update)
      .eq('id', update.id);
  }

  return { success: true, checked: updates.length, updates };
}

async function createAlerts(supabase: any, customerId: string) {
  // Check for high-risk changes
  const { data: highRiskChanges } = await supabase
    .from('change_requests')
    .select('*')
    .eq('customer_id', customerId)
    .eq('risk_level', 'critical')
    .eq('change_status', 'pending');

  const alerts = [];
  
  if (highRiskChanges && highRiskChanges.length > 0) {
    for (const change of highRiskChanges) {
      alerts.push({
        customer_id: customerId,
        alert_type: 'change_risk',
        alert_severity: 'critical',
        alert_title: 'Critical Risk Change Pending',
        alert_message: `Change "${change.title}" requires immediate attention`,
        alert_data: { change_id: change.id, change_number: change.change_number },
        affected_resource_id: change.id,
        affected_resource_type: 'change_request',
      });
    }
  }

  // Check for failed workflows
  const { data: failedWorkflows } = await supabase
    .from('workflow_executions')
    .select('*')
    .eq('customer_id', customerId)
    .eq('status', 'failed')
    .gte('started_at', new Date(Date.now() - 3600000).toISOString());

  if (failedWorkflows && failedWorkflows.length > 0) {
    alerts.push({
      customer_id: customerId,
      alert_type: 'workflow_failure',
      alert_severity: 'high',
      alert_title: `${failedWorkflows.length} Workflow(s) Failed`,
      alert_message: `${failedWorkflows.length} workflow execution(s) failed in the last hour`,
      alert_data: { failed_count: failedWorkflows.length },
    });
  }

  if (alerts.length > 0) {
    await supabase.from('real_time_alerts').insert(alerts);
  }

  return { success: true, alerts_created: alerts.length };
}