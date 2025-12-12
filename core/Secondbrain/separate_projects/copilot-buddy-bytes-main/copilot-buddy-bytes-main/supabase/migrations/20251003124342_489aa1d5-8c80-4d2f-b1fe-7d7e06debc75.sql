-- Add MCP servers for remaining departments
INSERT INTO public.mcp_servers (server_name, server_type, description, status, capabilities, customer_id) VALUES
(
  'IT Security MCP Server',
  'security_intelligence',
  'AI-powered IT security monitoring, integration health checks, and system diagnostics',
  'active',
  '["integration_health", "anomaly_detection", "system_diagnostics", "security_scoring"]'::jsonb,
  (SELECT id FROM public.customers LIMIT 1)
),
(
  'HR Analytics MCP Server',
  'hr_intelligence',
  'Employee metrics, session analysis, and department insights powered by ML',
  'active',
  '["employee_metrics", "session_analysis", "department_insights", "engagement_scoring"]'::jsonb,
  (SELECT id FROM public.customers LIMIT 1)
),
(
  'Finance Intelligence MCP Server',
  'finance_intelligence',
  'Revenue forecasting, customer lifetime value prediction, and churn analysis',
  'active',
  '["revenue_forecasting", "clv_prediction", "churn_analysis", "financial_insights"]'::jsonb,
  (SELECT id FROM public.customers LIMIT 1)
),
(
  'Executive Insights MCP Server',
  'executive_intelligence',
  'Strategic insights, KPI aggregation, and cross-department analytics',
  'active',
  '["kpi_aggregation", "strategic_insights", "cross_department_analytics", "executive_summary"]'::jsonb,
  (SELECT id FROM public.customers LIMIT 1)
);

-- Add tools for IT Security MCP Server
INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'check_integration_health',
  'Analyzes health status and performance metrics of system integrations',
  '{"type": "object", "properties": {"integration_id": {"type": "string"}, "metrics": {"type": "array"}}, "required": ["integration_id"]}'::jsonb
FROM public.mcp_servers WHERE server_name = 'IT Security MCP Server';

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'detect_security_anomalies',
  'Detects unusual patterns and security threats across systems',
  '{"type": "object", "properties": {"system_name": {"type": "string"}, "time_range": {"type": "string"}}, "required": ["system_name"]}'::jsonb
FROM public.mcp_servers WHERE server_name = 'IT Security MCP Server';

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'diagnose_system_issues',
  'Performs AI-powered diagnostics on system performance and errors',
  '{"type": "object", "properties": {"system_name": {"type": "string"}, "error_logs": {"type": "array"}}, "required": ["system_name"]}'::jsonb
FROM public.mcp_servers WHERE server_name = 'IT Security MCP Server';

-- Add tools for HR Analytics MCP Server
INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'analyze_employee_metrics',
  'Analyzes employee performance, engagement, and activity patterns',
  '{"type": "object", "properties": {"department": {"type": "string"}, "time_period": {"type": "string"}}, "required": []}'::jsonb
FROM public.mcp_servers WHERE server_name = 'HR Analytics MCP Server';

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'track_session_patterns',
  'Analyzes user session patterns and identifies productivity insights',
  '{"type": "object", "properties": {"user_id": {"type": "string"}, "date_range": {"type": "string"}}, "required": []}'::jsonb
FROM public.mcp_servers WHERE server_name = 'HR Analytics MCP Server';

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'generate_department_insights',
  'Generates insights on department health, turnover risk, and team dynamics',
  '{"type": "object", "properties": {"department": {"type": "string"}}, "required": ["department"]}'::jsonb
FROM public.mcp_servers WHERE server_name = 'HR Analytics MCP Server';

-- Add tools for Finance Intelligence MCP Server
INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'forecast_revenue',
  'Predicts future revenue based on historical data and trends',
  '{"type": "object", "properties": {"time_horizon": {"type": "string"}, "confidence_level": {"type": "number"}}, "required": ["time_horizon"]}'::jsonb
FROM public.mcp_servers WHERE server_name = 'Finance Intelligence MCP Server';

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'predict_customer_ltv',
  'Calculates predicted lifetime value for customers',
  '{"type": "object", "properties": {"customer_id": {"type": "string"}, "include_churn_risk": {"type": "boolean"}}, "required": ["customer_id"]}'::jsonb
FROM public.mcp_servers WHERE server_name = 'Finance Intelligence MCP Server';

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'analyze_churn_risk',
  'Identifies customers at risk of churning and recommends retention strategies',
  '{"type": "object", "properties": {"segment": {"type": "string"}, "risk_threshold": {"type": "number"}}, "required": []}'::jsonb
FROM public.mcp_servers WHERE server_name = 'Finance Intelligence MCP Server';

-- Add tools for Executive Insights MCP Server
INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'aggregate_kpis',
  'Aggregates key performance indicators across all departments',
  '{"type": "object", "properties": {"departments": {"type": "array"}, "time_period": {"type": "string"}}, "required": []}'::jsonb
FROM public.mcp_servers WHERE server_name = 'Executive Insights MCP Server';

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'generate_strategic_insights',
  'Generates strategic recommendations based on cross-department data',
  '{"type": "object", "properties": {"focus_areas": {"type": "array"}, "priority": {"type": "string"}}, "required": []}'::jsonb
FROM public.mcp_servers WHERE server_name = 'Executive Insights MCP Server';

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'analyze_cross_department',
  'Analyzes correlations and dependencies across departments',
  '{"type": "object", "properties": {"departments": {"type": "array"}, "metric_type": {"type": "string"}}, "required": ["departments"]}'::jsonb
FROM public.mcp_servers WHERE server_name = 'Executive Insights MCP Server';

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema)
SELECT 
  id,
  'create_executive_summary',
  'Creates comprehensive executive summary with actionable insights',
  '{"type": "object", "properties": {"report_type": {"type": "string"}, "time_period": {"type": "string"}}, "required": ["report_type"]}'::jsonb
FROM public.mcp_servers WHERE server_name = 'Executive Insights MCP Server';