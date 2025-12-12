import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface SyslogMessage {
  sourceIp: string;
  hostname?: string;
  facility?: number;
  severity?: number;
  timestamp?: string;
  appName?: string;
  procId?: string;
  msgId?: string;
  message: string;
  structuredData?: any;
  customerId?: string;
}

// Security-related syslog patterns
const SECURITY_PATTERNS = [
  /authentication failed/i,
  /unauthorized access/i,
  /login failure/i,
  /intrusion/i,
  /firewall block/i,
  /malware detected/i,
  /virus/i,
  /denied by acl/i,
  /port scan/i,
  /brute force/i,
];

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    const syslogData: SyslogMessage = await req.json();
    
    console.log('Received syslog message:', syslogData.sourceIp, syslogData.message.substring(0, 100));

    // Find matching device by IP
    const { data: device } = await supabase
      .from('network_devices')
      .select('id, customer_id')
      .eq('ip_address', syslogData.sourceIp)
      .maybeSingle();

    const customerId = device?.customer_id || syslogData.customerId;
    if (!customerId) {
      console.error('No customer ID found for syslog from', syslogData.sourceIp);
      return new Response(
        JSON.stringify({ error: 'Customer ID required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Check if message matches security patterns
    const isSecurityEvent = SECURITY_PATTERNS.some(pattern => 
      pattern.test(syslogData.message)
    );

    // Calculate priority
    const facility = syslogData.facility || 16; // Default to local0
    const severity = syslogData.severity || 6; // Default to info
    const priority = facility * 8 + severity;

    // Store syslog message
    const { data: syslogMsg, error: syslogError } = await supabase
      .from('syslog_messages')
      .insert({
        customer_id: customerId,
        device_id: device?.id,
        source_ip: syslogData.sourceIp,
        hostname: syslogData.hostname,
        facility,
        severity,
        priority,
        timestamp: syslogData.timestamp || new Date().toISOString(),
        app_name: syslogData.appName,
        proc_id: syslogData.procId,
        msg_id: syslogData.msgId,
        message: syslogData.message,
        structured_data: syslogData.structuredData,
        is_security_event: isSecurityEvent,
      })
      .select()
      .single();

    if (syslogError) throw syslogError;

    // Check if message matches any alert rules
    const { data: rules } = await supabase
      .from('network_alert_rules')
      .select('*')
      .eq('customer_id', customerId)
      .eq('is_enabled', true)
      .eq('rule_type', 'syslog_pattern');

    if (rules && rules.length > 0) {
      for (const rule of rules) {
        const conditions = rule.conditions as any;
        
        // Check if message matches rule pattern
        let matches = false;
        if (conditions.pattern) {
          const regex = new RegExp(conditions.pattern, 'i');
          matches = regex.test(syslogData.message);
        }
        if (conditions.severity && severity <= conditions.severity) {
          matches = matches || true;
        }

        if (matches) {
          // Create network alert
          await supabase.from('network_alerts').insert({
            customer_id: customerId,
            device_id: device?.id,
            alert_type: 'syslog_pattern',
            severity: rule.severity,
            title: `Syslog Alert: ${rule.rule_name}`,
            description: syslogData.message.substring(0, 200),
            source_data: { syslog_id: syslogMsg.id, message: syslogData.message },
          });

          console.log('Created alert for syslog matching rule:', rule.rule_name);
        }
      }
    }

    // Create anomaly detection for security events
    if (isSecurityEvent && severity <= 4) { // Warning or higher
      await supabase.from('anomaly_detections').insert({
        customer_id: customerId,
        anomaly_type: 'security_event',
        system_name: device ? `Network Device ${device.id}` : syslogData.sourceIp,
        description: syslogData.message,
        severity: severity <= 2 ? 'critical' : 'high',
        detection_method: 'syslog_analysis',
        raw_data: { syslog_id: syslogMsg.id, message: syslogData },
        compliance_tags: ['security', 'network'],
      });
    }

    // Update device last_syslog_at
    if (device?.id) {
      await supabase
        .from('network_devices')
        .update({ last_syslog_at: new Date().toISOString() })
        .eq('id', device.id);
    }

    return new Response(
      JSON.stringify({ success: true, syslog_id: syslogMsg.id, is_security_event: isSecurityEvent }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error processing syslog message:', error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});