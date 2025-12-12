-- Populate MCP tools for Compliance Intelligence Server
INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema, output_schema)
SELECT 
  id,
  'query_compliance_status',
  'Query real-time compliance status across frameworks and controls',
  '{"type":"object","properties":{"framework_code":{"type":"string","description":"Framework code (e.g., ISO27001, SOC2)"},"control_id":{"type":"string","description":"Specific control ID to query"},"time_range":{"type":"string","description":"Time range for historical data"}},"required":[]}'::jsonb,
  '{"type":"object","properties":{"compliance_score":{"type":"number"},"active_controls":{"type":"integer"},"violations":{"type":"array"},"trend":{"type":"string"}}}'::jsonb
FROM public.mcp_servers
WHERE server_type = 'compliance'
LIMIT 1;

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema, output_schema)
SELECT 
  id,
  'predict_violations',
  'Use ML models to predict potential compliance violations based on behavioral patterns',
  '{"type":"object","properties":{"user_id":{"type":"string","description":"User ID to analyze"},"system_name":{"type":"string","description":"System to analyze"},"lookback_days":{"type":"integer","description":"Days to analyze historical data"}},"required":[]}'::jsonb,
  '{"type":"object","properties":{"risk_score":{"type":"number"},"predicted_violations":{"type":"array"},"recommendations":{"type":"array"},"confidence":{"type":"number"}}}'::jsonb
FROM public.mcp_servers
WHERE server_type = 'compliance'
LIMIT 1;

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema, output_schema)
SELECT 
  id,
  'analyze_control_gaps',
  'Analyze gaps in compliance controls and suggest improvements',
  '{"type":"object","properties":{"framework_id":{"type":"string","description":"Framework UUID"},"include_recommendations":{"type":"boolean","description":"Include AI recommendations"}},"required":["framework_id"]}'::jsonb,
  '{"type":"object","properties":{"gaps":{"type":"array"},"missing_controls":{"type":"array"},"recommendations":{"type":"array"},"priority_score":{"type":"number"}}}'::jsonb
FROM public.mcp_servers
WHERE server_type = 'compliance'
LIMIT 1;

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema, output_schema)
SELECT 
  id,
  'generate_evidence_report',
  'Generate comprehensive evidence report for audit preparation',
  '{"type":"object","properties":{"framework_code":{"type":"string","description":"Framework code"},"start_date":{"type":"string","format":"date"},"end_date":{"type":"string","format":"date"},"control_ids":{"type":"array","items":{"type":"string"}}},"required":["framework_code","start_date","end_date"]}'::jsonb,
  '{"type":"object","properties":{"report_id":{"type":"string"},"total_evidence":{"type":"integer"},"coverage_percentage":{"type":"number"},"findings":{"type":"array"},"download_url":{"type":"string"}}}'::jsonb
FROM public.mcp_servers
WHERE server_type = 'compliance'
LIMIT 1;

-- Populate MCP tools for Workflow Optimization Server
INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema, output_schema)
SELECT 
  id,
  'analyze_workflow_efficiency',
  'Analyze cross-system workflow efficiency and identify patterns',
  '{"type":"object","properties":{"workflow_id":{"type":"string","description":"Workflow UUID"},"time_period":{"type":"string","description":"Analysis time period"},"include_ml_predictions":{"type":"boolean","description":"Include ML-powered predictions"}},"required":[]}'::jsonb,
  '{"type":"object","properties":{"efficiency_score":{"type":"number"},"avg_completion_time":{"type":"integer"},"success_rate":{"type":"number"},"bottlenecks":{"type":"array"},"predictions":{"type":"object"}}}'::jsonb
FROM public.mcp_servers
WHERE server_type = 'workflow'
LIMIT 1;

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema, output_schema)
SELECT 
  id,
  'detect_bottlenecks',
  'Detect workflow bottlenecks using behavioral event analysis',
  '{"type":"object","properties":{"system_names":{"type":"array","items":{"type":"string"},"description":"Systems to analyze"},"threshold_ms":{"type":"integer","description":"Minimum duration to flag as bottleneck"},"min_occurrences":{"type":"integer","description":"Minimum occurrences to qualify"}},"required":[]}'::jsonb,
  '{"type":"object","properties":{"bottlenecks":{"type":"array"},"affected_workflows":{"type":"array"},"estimated_impact":{"type":"object"},"recommendations":{"type":"array"}}}'::jsonb
FROM public.mcp_servers
WHERE server_type = 'workflow'
LIMIT 1;

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema, output_schema)
SELECT 
  id,
  'predict_completion_times',
  'Predict workflow completion times using ML models trained on historical data',
  '{"type":"object","properties":{"workflow_name":{"type":"string","description":"Workflow name"},"systems_involved":{"type":"array","items":{"type":"string"}},"current_step":{"type":"string","description":"Current step in workflow"}},"required":["workflow_name"]}'::jsonb,
  '{"type":"object","properties":{"predicted_time_ms":{"type":"integer"},"confidence_interval":{"type":"object"},"factors":{"type":"array"},"similar_executions":{"type":"integer"}}}'::jsonb
FROM public.mcp_servers
WHERE server_type = 'workflow'
LIMIT 1;

INSERT INTO public.mcp_tools (server_id, tool_name, description, input_schema, output_schema)
SELECT 
  id,
  'recommend_optimizations',
  'AI-powered recommendations for workflow optimization based on patterns',
  '{"type":"object","properties":{"workflow_id":{"type":"string"},"optimization_goals":{"type":"array","items":{"type":"string"},"description":"Goals like speed, reliability, cost"},"max_recommendations":{"type":"integer","description":"Maximum number of recommendations"}},"required":["workflow_id"]}'::jsonb,
  '{"type":"object","properties":{"recommendations":{"type":"array"},"expected_improvement":{"type":"object"},"implementation_effort":{"type":"string"},"priority_order":{"type":"array"}}}'::jsonb
FROM public.mcp_servers
WHERE server_type = 'workflow'
LIMIT 1;

-- Populate MCP resources
INSERT INTO public.mcp_resources (server_id, resource_type, resource_uri, description, metadata)
SELECT 
  id,
  'compliance_data',
  'mcp://compliance/frameworks',
  'Access to all compliance frameworks, controls, and compliance status',
  '{"data_sources":["compliance_frameworks","compliance_controls","compliance_reports"],"refresh_rate":"real-time"}'::jsonb
FROM public.mcp_servers
WHERE server_type = 'compliance'
LIMIT 1;

INSERT INTO public.mcp_resources (server_id, resource_type, resource_uri, description, metadata)
SELECT 
  id,
  'audit_logs',
  'mcp://compliance/audit-logs',
  'Complete audit log history with compliance tagging',
  '{"data_sources":["audit_logs","system_access_logs"],"retention_days":365}'::jsonb
FROM public.mcp_servers
WHERE server_type = 'compliance'
LIMIT 1;

INSERT INTO public.mcp_resources (server_id, resource_type, resource_uri, description, metadata)
SELECT 
  id,
  'workflow_metrics',
  'mcp://workflows/metrics',
  'Real-time workflow execution metrics and efficiency data',
  '{"data_sources":["workflows","behavioral_events"],"aggregation":"5min"}'::jsonb
FROM public.mcp_servers
WHERE server_type = 'workflow'
LIMIT 1;

INSERT INTO public.mcp_resources (server_id, resource_type, resource_uri, description, metadata)
SELECT 
  id,
  'behavioral_patterns',
  'mcp://workflows/behavioral-patterns',
  'ML-analyzed behavioral patterns across systems',
  '{"data_sources":["behavioral_events","ml_insights"],"model_version":"v2.1"}'::jsonb
FROM public.mcp_servers
WHERE server_type = 'workflow'
LIMIT 1;