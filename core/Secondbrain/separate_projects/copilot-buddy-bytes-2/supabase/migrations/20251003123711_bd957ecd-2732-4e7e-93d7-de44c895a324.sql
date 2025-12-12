-- Create department_permissions table to define what each department can access
CREATE TABLE public.department_permissions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  department TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  accessible_tables JSONB NOT NULL DEFAULT '[]'::jsonb,
  accessible_features JSONB NOT NULL DEFAULT '[]'::jsonb,
  dashboard_widgets JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.department_permissions ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Everyone can view department permissions"
ON public.department_permissions
FOR SELECT
USING (true);

CREATE POLICY "Admins can manage department permissions"
ON public.department_permissions
FOR ALL
USING (has_role(auth.uid(), 'admin'::app_role));

-- Insert default department configurations
INSERT INTO public.department_permissions (department, display_name, accessible_tables, accessible_features, dashboard_widgets) VALUES
('compliance', 'Compliance & GRC', 
 '["compliance_frameworks", "compliance_controls", "compliance_reports", "evidence_files", "audit_logs", "compliance_tags"]'::jsonb,
 '["frameworks", "controls", "evidence", "reports", "audit_logs"]'::jsonb,
 '["compliance_score", "framework_coverage", "evidence_tracking", "audit_trail"]'::jsonb),

('it', 'IT & Security',
 '["integrations", "system_access_logs", "mcp_servers", "mcp_tools", "workflows", "behavioral_events", "anomaly_detections"]'::jsonb,
 '["integrations", "mcp_servers", "system_logs", "workflows", "anomaly_detection"]'::jsonb,
 '["system_health", "integration_status", "mcp_status", "security_alerts"]'::jsonb),

('hr', 'Human Resources',
 '["user_profiles", "user_sessions", "behavioral_events", "notifications"]'::jsonb,
 '["user_management", "session_tracking", "notifications"]'::jsonb,
 '["active_users", "department_breakdown", "user_activity"]'::jsonb),

('finance', 'Finance',
 '["customers", "subscription_plans", "audit_logs"]'::jsonb,
 '["customer_management", "billing", "financial_reports"]'::jsonb,
 '["revenue_metrics", "subscription_status", "customer_growth"]'::jsonb),

('operations', 'Operations',
 '["workflows", "integrations", "system_access_logs", "ml_insights", "prediction_history"]'::jsonb,
 '["workflow_optimization", "cross_system_analytics", "ml_insights"]'::jsonb,
 '["workflow_efficiency", "bottleneck_detection", "ml_predictions"]'::jsonb),

('executive', 'Executive Leadership',
 '["customers", "compliance_reports", "workflows", "ml_insights", "anomaly_detections"]'::jsonb,
 '["executive_dashboard", "reports", "strategic_insights"]'::jsonb,
 '["kpi_overview", "compliance_summary", "business_insights", "risk_overview"]'::jsonb);

-- Add trigger for updated_at
CREATE TRIGGER update_department_permissions_updated_at
BEFORE UPDATE ON public.department_permissions
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();