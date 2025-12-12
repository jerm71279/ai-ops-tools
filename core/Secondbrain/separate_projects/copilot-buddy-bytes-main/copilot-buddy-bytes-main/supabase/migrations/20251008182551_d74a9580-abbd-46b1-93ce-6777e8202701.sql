-- SNMP & Syslog Infrastructure Tables

-- Network devices table (SNMP-enabled devices)
CREATE TABLE IF NOT EXISTS public.network_devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  device_name TEXT NOT NULL,
  ip_address INET NOT NULL,
  device_type TEXT NOT NULL, -- 'switch', 'router', 'firewall', 'server', 'other'
  vendor TEXT,
  model TEXT,
  snmp_version TEXT DEFAULT 'v2c', -- 'v1', 'v2c', 'v3'
  snmp_community TEXT, -- for v1/v2c
  snmp_port INTEGER DEFAULT 161,
  polling_enabled BOOLEAN DEFAULT true,
  polling_interval_seconds INTEGER DEFAULT 300,
  syslog_enabled BOOLEAN DEFAULT true,
  location TEXT,
  description TEXT,
  ci_id UUID, -- Link to CMDB
  status TEXT DEFAULT 'active', -- 'active', 'inactive', 'unreachable'
  last_poll_at TIMESTAMP WITH TIME ZONE,
  last_syslog_at TIMESTAMP WITH TIME ZONE,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  created_by UUID NOT NULL,
  CONSTRAINT unique_device_ip UNIQUE(customer_id, ip_address)
);

-- SNMP traps table
CREATE TABLE IF NOT EXISTS public.snmp_traps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  device_id UUID REFERENCES public.network_devices(id) ON DELETE SET NULL,
  source_ip INET NOT NULL,
  trap_oid TEXT NOT NULL,
  trap_type TEXT, -- 'coldStart', 'warmStart', 'linkDown', 'linkUp', 'authenticationFailure', 'enterpriseSpecific'
  severity TEXT DEFAULT 'info', -- 'critical', 'warning', 'info'
  varbinds JSONB, -- Array of OID/value pairs
  raw_data JSONB,
  is_acknowledged BOOLEAN DEFAULT false,
  acknowledged_by UUID,
  acknowledged_at TIMESTAMP WITH TIME ZONE,
  created_incident_id UUID,
  received_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  processed BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Syslog messages table
CREATE TABLE IF NOT EXISTS public.syslog_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  device_id UUID REFERENCES public.network_devices(id) ON DELETE SET NULL,
  source_ip INET NOT NULL,
  hostname TEXT,
  facility INTEGER, -- 0-23 (standard syslog facility codes)
  severity INTEGER, -- 0-7 (standard syslog severity codes)
  priority INTEGER, -- facility * 8 + severity
  timestamp TIMESTAMP WITH TIME ZONE,
  app_name TEXT,
  proc_id TEXT,
  msg_id TEXT,
  message TEXT NOT NULL,
  structured_data JSONB,
  tags TEXT[],
  is_security_event BOOLEAN DEFAULT false,
  is_acknowledged BOOLEAN DEFAULT false,
  acknowledged_by UUID,
  acknowledged_at TIMESTAMP WITH TIME ZONE,
  created_incident_id UUID,
  received_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create index for full-text search on syslog messages
CREATE INDEX IF NOT EXISTS idx_syslog_message_search ON public.syslog_messages USING gin(to_tsvector('english', message));
CREATE INDEX IF NOT EXISTS idx_syslog_timestamp ON public.syslog_messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_syslog_severity ON public.syslog_messages(severity);
CREATE INDEX IF NOT EXISTS idx_syslog_source_ip ON public.syslog_messages(source_ip);
CREATE INDEX IF NOT EXISTS idx_syslog_customer ON public.syslog_messages(customer_id);

-- Device metrics table (time-series SNMP polling data)
CREATE TABLE IF NOT EXISTS public.device_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  device_id UUID NOT NULL REFERENCES public.network_devices(id) ON DELETE CASCADE,
  metric_type TEXT NOT NULL, -- 'cpu', 'memory', 'interface', 'disk', 'temperature', 'uptime'
  metric_name TEXT NOT NULL,
  metric_value NUMERIC,
  metric_unit TEXT, -- 'percent', 'bytes', 'celsius', 'seconds', 'packets', 'errors'
  oid TEXT,
  interface_name TEXT, -- for interface metrics
  additional_data JSONB,
  polled_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Indexes for time-series queries
CREATE INDEX IF NOT EXISTS idx_device_metrics_device ON public.device_metrics(device_id, polled_at DESC);
CREATE INDEX IF NOT EXISTS idx_device_metrics_type ON public.device_metrics(metric_type, polled_at DESC);
CREATE INDEX IF NOT EXISTS idx_device_metrics_customer ON public.device_metrics(customer_id);

-- Network alerts table (derived from traps/logs/metrics)
CREATE TABLE IF NOT EXISTS public.network_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  device_id UUID REFERENCES public.network_devices(id) ON DELETE SET NULL,
  alert_type TEXT NOT NULL, -- 'snmp_trap', 'syslog_pattern', 'metric_threshold', 'device_unreachable'
  severity TEXT NOT NULL, -- 'critical', 'high', 'medium', 'low', 'info'
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  source_data JSONB, -- Reference to trap/log/metric that triggered alert
  status TEXT DEFAULT 'open', -- 'open', 'investigating', 'resolved', 'false_positive'
  assigned_to UUID,
  incident_id UUID, -- Link to incidents table if escalated
  correlation_id UUID, -- Group related alerts
  auto_remediation_triggered BOOLEAN DEFAULT false,
  remediation_action TEXT,
  notes TEXT,
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolved_by UUID,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Alert rules table (define alerting conditions)
CREATE TABLE IF NOT EXISTS public.network_alert_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  rule_name TEXT NOT NULL,
  rule_type TEXT NOT NULL, -- 'snmp_trap', 'syslog_pattern', 'metric_threshold'
  is_enabled BOOLEAN DEFAULT true,
  conditions JSONB NOT NULL, -- Pattern matching, threshold values, etc.
  severity TEXT NOT NULL,
  notification_channels TEXT[], -- 'email', 'sms', 'webhook', 'ticket'
  auto_remediation_workflow_id UUID,
  description TEXT,
  created_by UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Row Level Security Policies

ALTER TABLE public.network_devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.snmp_traps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.syslog_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.device_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.network_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.network_alert_rules ENABLE ROW LEVEL SECURITY;

-- Network devices policies
CREATE POLICY "Users can view devices in their organization"
  ON public.network_devices FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage devices in their organization"
  ON public.network_devices FOR ALL
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- SNMP traps policies
CREATE POLICY "Users can view traps in their organization"
  ON public.snmp_traps FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "System can insert traps"
  ON public.snmp_traps FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Users can update traps in their organization"
  ON public.snmp_traps FOR UPDATE
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Syslog messages policies
CREATE POLICY "Users can view syslog in their organization"
  ON public.syslog_messages FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "System can insert syslog"
  ON public.syslog_messages FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Users can update syslog in their organization"
  ON public.syslog_messages FOR UPDATE
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Device metrics policies
CREATE POLICY "Users can view metrics in their organization"
  ON public.device_metrics FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "System can insert metrics"
  ON public.device_metrics FOR INSERT
  WITH CHECK (true);

-- Network alerts policies
CREATE POLICY "Users can view alerts in their organization"
  ON public.network_alerts FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage alerts in their organization"
  ON public.network_alerts FOR ALL
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Alert rules policies
CREATE POLICY "Users can view alert rules in their organization"
  ON public.network_alert_rules FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage alert rules in their organization"
  ON public.network_alert_rules FOR ALL
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Triggers for updated_at
CREATE TRIGGER update_network_devices_updated_at
  BEFORE UPDATE ON public.network_devices
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_network_alerts_updated_at
  BEFORE UPDATE ON public.network_alerts
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_network_alert_rules_updated_at
  BEFORE UPDATE ON public.network_alert_rules
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();