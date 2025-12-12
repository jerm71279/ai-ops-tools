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

    const { action, customerId, data } = await req.json();
    console.log('Customer management:', { action, customerId });

    let result;

    switch (action) {
      case 'calculate_health':
        result = await calculateCustomerHealth(supabase, customerId);
        break;
      case 'track_usage':
        result = await trackCustomerUsage(supabase, customerId, data);
        break;
      case 'generate_invoice':
        result = await generateInvoice(supabase, customerId, data);
        break;
      case 'toggle_feature':
        result = await toggleFeature(supabase, customerId, data);
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
    console.error('Customer management error:', error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

async function calculateCustomerHealth(supabase: any, customerId: string) {
  const now = new Date();
  const thirtyDaysAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);

  // Get user activity
  const { data: users } = await supabase
    .from('user_profiles')
    .select('user_id, full_name')
    .eq('customer_id', customerId);

  const activeUsers = users?.length || 0;

  // Get recent activity
  const { data: activities } = await supabase
    .from('customer_activity_log')
    .select('*')
    .eq('customer_id', customerId)
    .gte('created_at', thirtyDaysAgo.toISOString());

  // Get support tickets
  const { data: tickets } = await supabase
    .from('support_tickets')
    .select('*')
    .eq('customer_id', customerId)
    .gte('created_at', thirtyDaysAgo.toISOString());

  const openTickets = tickets?.filter((t: any) => t.status === 'open').length || 0;
  const criticalTickets = tickets?.filter((t: any) => t.priority === 'critical').length || 0;

  // Calculate scores
  const engagementScore = Math.min(100, (activities?.length || 0) * 2);
  const adoptionScore = Math.min(100, activeUsers * 20);
  const satisfactionScore = Math.max(0, 100 - (openTickets * 10) - (criticalTickets * 20));

  const healthScore = Math.round(
    (engagementScore * 0.4) + 
    (adoptionScore * 0.3) + 
    (satisfactionScore * 0.3)
  );

  let riskLevel = 'low';
  if (healthScore < 40) riskLevel = 'critical';
  else if (healthScore < 60) riskLevel = 'high';
  else if (healthScore < 80) riskLevel = 'medium';

  const healthFactors = {
    active_users: activeUsers,
    activities_last_30d: activities?.length || 0,
    open_tickets: openTickets,
    critical_tickets: criticalTickets,
  };

  const recommendations = [];
  if (engagementScore < 50) recommendations.push('Low engagement - consider outreach campaign');
  if (adoptionScore < 50) recommendations.push('Low user adoption - schedule training session');
  if (openTickets > 5) recommendations.push('High ticket volume - prioritize support');
  if (criticalTickets > 0) recommendations.push('Critical tickets pending - immediate action required');

  // Store health score
  const { data: health } = await supabase
    .from('customer_health')
    .insert({
      customer_id: customerId,
      health_score: healthScore,
      engagement_score: engagementScore,
      adoption_score: adoptionScore,
      satisfaction_score: satisfactionScore,
      risk_level: riskLevel,
      health_factors: healthFactors,
      recommendations,
      last_activity_at: activities?.[0]?.created_at || null,
    })
    .select()
    .single();

  return { success: true, health };
}

async function trackCustomerUsage(supabase: any, customerId: string, data: any) {
  const today = new Date().toISOString().split('T')[0];

  // Aggregate usage metrics
  const metrics = {
    users: 0,
    changes: 0,
    workflows: 0,
    ci_items: 0,
    api_calls: 0,
  };

  // Count users
  const { count: userCount } = await supabase
    .from('user_profiles')
    .select('*', { count: 'exact', head: true })
    .eq('customer_id', customerId);
  metrics.users = userCount || 0;

  // Count changes
  const { count: changeCount } = await supabase
    .from('change_requests')
    .select('*', { count: 'exact', head: true })
    .eq('customer_id', customerId)
    .gte('created_at', today);
  metrics.changes = changeCount || 0;

  // Count workflows
  const { count: workflowCount } = await supabase
    .from('workflow_executions')
    .select('*', { count: 'exact', head: true })
    .eq('customer_id', customerId)
    .gte('started_at', today);
  metrics.workflows = workflowCount || 0;

  // Count CI items
  const { count: ciCount } = await supabase
    .from('configuration_items')
    .select('*', { count: 'exact', head: true })
    .eq('customer_id', customerId);
  metrics.ci_items = ciCount || 0;

  // Store usage data
  const usageRecords = [];
  for (const [metricType, metricValue] of Object.entries(metrics)) {
    usageRecords.push({
      customer_id: customerId,
      usage_date: today,
      metric_type: metricType,
      metric_value: metricValue,
      usage_details: data?.details || {},
    });
  }

  await supabase
    .from('customer_usage')
    .upsert(usageRecords, { onConflict: 'customer_id,usage_date,metric_type' });

  return { success: true, metrics };
}

async function generateInvoice(supabase: any, customerId: string, data: any) {
  const { period_start, period_end } = data;

  // Get usage for the period
  const { data: usage } = await supabase
    .from('customer_usage')
    .select('*')
    .eq('customer_id', customerId)
    .gte('usage_date', period_start)
    .lte('usage_date', period_end);

  // Calculate line items based on usage
  const lineItems = [];
  let totalAmount = 0;

  // Base subscription fee
  lineItems.push({
    description: 'Platform Subscription',
    quantity: 1,
    unit_price: 99.00,
    amount: 99.00,
  });
  totalAmount += 99.00;

  // Additional user fees (if over 5 users)
  const avgUsers = usage
    ?.filter((u: any) => u.metric_type === 'users')
    .reduce((sum: number, u: any) => sum + parseFloat(u.metric_value), 0) / (usage?.length || 1);
  
  if (avgUsers > 5) {
    const additionalUsers = Math.ceil(avgUsers - 5);
    const userFee = additionalUsers * 10;
    lineItems.push({
      description: `Additional Users (${additionalUsers})`,
      quantity: additionalUsers,
      unit_price: 10.00,
      amount: userFee,
    });
    totalAmount += userFee;
  }

  const invoiceNumber = `INV-${new Date().getFullYear()}${(new Date().getMonth() + 1).toString().padStart(2, '0')}-${Math.random().toString(36).substring(2, 7).toUpperCase()}`;

  const { data: invoice } = await supabase
    .from('customer_billing')
    .insert({
      customer_id: customerId,
      billing_period_start: period_start,
      billing_period_end: period_end,
      total_amount: totalAmount,
      invoice_number: invoiceNumber,
      line_items: lineItems,
      status: 'pending',
      due_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    })
    .select()
    .single();

  return { success: true, invoice };
}

async function toggleFeature(supabase: any, customerId: string, data: any) {
  const { feature_name, is_enabled, created_by } = data;

  const { data: feature } = await supabase
    .from('customer_features')
    .upsert({
      customer_id: customerId,
      feature_name,
      is_enabled,
      enabled_at: is_enabled ? new Date().toISOString() : null,
      disabled_at: !is_enabled ? new Date().toISOString() : null,
      created_by,
    }, { onConflict: 'customer_id,feature_name' })
    .select()
    .single();

  // Log activity
  await supabase
    .from('customer_activity_log')
    .insert({
      customer_id: customerId,
      activity_type: 'feature_toggle',
      activity_description: `Feature "${feature_name}" ${is_enabled ? 'enabled' : 'disabled'}`,
      user_id: created_by,
      metadata: { feature_name, is_enabled },
    });

  return { success: true, feature };
}