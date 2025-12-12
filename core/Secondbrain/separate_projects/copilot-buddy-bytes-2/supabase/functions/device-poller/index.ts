import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

// Standard SNMP OIDs for common metrics
const STANDARD_OIDS = {
  sysUpTime: '1.3.6.1.2.1.1.3.0',
  sysName: '1.3.6.1.2.1.1.5.0',
  sysDescr: '1.3.6.1.2.1.1.1.0',
  // CPU metrics
  hrProcessorLoad: '1.3.6.1.2.1.25.3.3.1.2',
  // Memory metrics
  hrStorageUsed: '1.3.6.1.2.1.25.2.3.1.6',
  hrStorageSize: '1.3.6.1.2.1.25.2.3.1.5',
  // Interface metrics
  ifOperStatus: '1.3.6.1.2.1.2.2.1.8',
  ifInOctets: '1.3.6.1.2.1.2.2.1.10',
  ifOutOctets: '1.3.6.1.2.1.2.2.1.16',
  ifInErrors: '1.3.6.1.2.1.2.2.1.14',
  ifOutErrors: '1.3.6.1.2.1.2.2.1.20',
};

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const { device_id } = await req.json();

    // Get device details
    const { data: device, error: deviceError } = await supabase
      .from('network_devices')
      .select('*')
      .eq('id', device_id)
      .single();

    if (deviceError || !device) {
      return new Response(
        JSON.stringify({ error: 'Device not found' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    if (!device.polling_enabled) {
      return new Response(
        JSON.stringify({ error: 'Polling disabled for this device' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    console.log('Polling device:', device.device_name, device.ip_address);

    // In a real implementation, this would use an SNMP library
    // For now, we'll simulate polling with mock data
    const metrics = [];
    const polledAt = new Date().toISOString();

    // Simulate CPU metrics
    const cpuUsage = Math.random() * 100;
    metrics.push({
      customer_id: device.customer_id,
      device_id: device.id,
      metric_type: 'cpu',
      metric_name: 'CPU Usage',
      metric_value: cpuUsage,
      metric_unit: 'percent',
      oid: STANDARD_OIDS.hrProcessorLoad,
      polled_at: polledAt,
    });

    // Simulate memory metrics
    const memoryUsed = Math.random() * 16 * 1024 * 1024 * 1024; // Random GB in bytes
    const memoryTotal = 16 * 1024 * 1024 * 1024; // 16 GB
    const memoryPercent = (memoryUsed / memoryTotal) * 100;
    metrics.push({
      customer_id: device.customer_id,
      device_id: device.id,
      metric_type: 'memory',
      metric_name: 'Memory Usage',
      metric_value: memoryPercent,
      metric_unit: 'percent',
      oid: STANDARD_OIDS.hrStorageUsed,
      additional_data: {
        used_bytes: memoryUsed,
        total_bytes: memoryTotal,
      },
      polled_at: polledAt,
    });

    // Simulate interface metrics
    const interfaceNames = ['eth0', 'eth1', 'eth2'];
    for (const ifName of interfaceNames) {
      metrics.push({
        customer_id: device.customer_id,
        device_id: device.id,
        metric_type: 'interface',
        metric_name: 'Interface Traffic In',
        metric_value: Math.random() * 1000000000,
        metric_unit: 'bytes',
        oid: STANDARD_OIDS.ifInOctets,
        interface_name: ifName,
        polled_at: polledAt,
      });
    }

    // Store metrics
    const { error: metricsError } = await supabase
      .from('device_metrics')
      .insert(metrics);

    if (metricsError) throw metricsError;

    // Check for threshold alerts
    const { data: thresholdRules } = await supabase
      .from('network_alert_rules')
      .select('*')
      .eq('customer_id', device.customer_id)
      .eq('is_enabled', true)
      .eq('rule_type', 'metric_threshold');

    if (thresholdRules && thresholdRules.length > 0) {
      for (const rule of thresholdRules) {
        const conditions = rule.conditions as any;
        
        // Check if any metric exceeds threshold
        for (const metric of metrics) {
          if (metric.metric_type === conditions.metric_type) {
            const threshold = conditions.threshold || 90;
            if (metric.metric_value > threshold) {
              // Create alert
              await supabase.from('network_alerts').insert({
                customer_id: device.customer_id,
                device_id: device.id,
                alert_type: 'metric_threshold',
                severity: rule.severity,
                title: `${metric.metric_name} exceeded threshold`,
                description: `${metric.metric_name} is at ${metric.metric_value.toFixed(2)}${metric.metric_unit}, threshold is ${threshold}${metric.metric_unit}`,
                source_data: { metric, threshold },
              });
            }
          }
        }
      }
    }

    // Update device status and last_poll_at
    await supabase
      .from('network_devices')
      .update({ 
        status: 'active',
        last_poll_at: polledAt 
      })
      .eq('id', device.id);

    return new Response(
      JSON.stringify({ 
        success: true, 
        device: device.device_name,
        metrics_collected: metrics.length 
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error polling device:', error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});