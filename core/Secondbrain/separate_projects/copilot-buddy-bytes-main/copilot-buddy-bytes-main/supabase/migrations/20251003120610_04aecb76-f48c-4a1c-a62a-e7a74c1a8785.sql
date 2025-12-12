-- Create MCP servers table
CREATE TABLE public.mcp_servers (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  server_name TEXT NOT NULL,
  server_type TEXT NOT NULL, -- 'compliance', 'workflow', 'integration', 'analytics'
  description TEXT,
  endpoint_url TEXT,
  status TEXT NOT NULL DEFAULT 'inactive', -- 'active', 'inactive', 'error'
  capabilities JSONB NOT NULL DEFAULT '[]'::jsonb, -- list of capabilities
  config JSONB DEFAULT '{}'::jsonb,
  last_health_check TIMESTAMP WITH TIME ZONE,
  error_message TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create MCP tools table (tools exposed by MCP servers)
CREATE TABLE public.mcp_tools (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  server_id UUID NOT NULL REFERENCES public.mcp_servers(id) ON DELETE CASCADE,
  tool_name TEXT NOT NULL,
  description TEXT NOT NULL,
  input_schema JSONB NOT NULL, -- JSON schema for tool inputs
  output_schema JSONB, -- JSON schema for tool outputs
  is_enabled BOOLEAN NOT NULL DEFAULT true,
  execution_count INTEGER NOT NULL DEFAULT 0,
  avg_execution_time_ms INTEGER,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create MCP resources table (data resources available through MCP)
CREATE TABLE public.mcp_resources (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  server_id UUID NOT NULL REFERENCES public.mcp_servers(id) ON DELETE CASCADE,
  resource_type TEXT NOT NULL, -- 'compliance_data', 'workflow_metrics', 'audit_logs', 'behavioral_patterns'
  resource_uri TEXT NOT NULL,
  description TEXT,
  access_count INTEGER NOT NULL DEFAULT 0,
  last_accessed TIMESTAMP WITH TIME ZONE,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create MCP execution logs table
CREATE TABLE public.mcp_execution_logs (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  server_id UUID NOT NULL REFERENCES public.mcp_servers(id) ON DELETE CASCADE,
  tool_id UUID REFERENCES public.mcp_tools(id) ON DELETE SET NULL,
  customer_id UUID NOT NULL,
  user_id UUID,
  tool_name TEXT NOT NULL,
  input_data JSONB NOT NULL,
  output_data JSONB,
  status TEXT NOT NULL, -- 'success', 'error', 'timeout'
  execution_time_ms INTEGER,
  error_message TEXT,
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.mcp_servers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mcp_tools ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mcp_resources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mcp_execution_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for mcp_servers
CREATE POLICY "Admins can manage MCP servers"
  ON public.mcp_servers
  FOR ALL
  USING (has_role(auth.uid(), 'admin'::app_role));

CREATE POLICY "Admins can view MCP servers"
  ON public.mcp_servers
  FOR SELECT
  USING (has_role(auth.uid(), 'admin'::app_role));

-- RLS Policies for mcp_tools
CREATE POLICY "Admins can manage MCP tools"
  ON public.mcp_tools
  FOR ALL
  USING (has_role(auth.uid(), 'admin'::app_role));

CREATE POLICY "Admins can view MCP tools"
  ON public.mcp_tools
  FOR SELECT
  USING (has_role(auth.uid(), 'admin'::app_role));

-- RLS Policies for mcp_resources
CREATE POLICY "Admins can manage MCP resources"
  ON public.mcp_resources
  FOR ALL
  USING (has_role(auth.uid(), 'admin'::app_role));

CREATE POLICY "Admins can view MCP resources"
  ON public.mcp_resources
  FOR SELECT
  USING (has_role(auth.uid(), 'admin'::app_role));

-- RLS Policies for mcp_execution_logs
CREATE POLICY "Admins can view all execution logs"
  ON public.mcp_execution_logs
  FOR SELECT
  USING (has_role(auth.uid(), 'admin'::app_role));

CREATE POLICY "System can insert execution logs"
  ON public.mcp_execution_logs
  FOR INSERT
  WITH CHECK (true); -- Allow system to log executions

-- Create indexes
CREATE INDEX idx_mcp_servers_customer ON public.mcp_servers(customer_id);
CREATE INDEX idx_mcp_servers_status ON public.mcp_servers(status);
CREATE INDEX idx_mcp_tools_server ON public.mcp_tools(server_id);
CREATE INDEX idx_mcp_resources_server ON public.mcp_resources(server_id);
CREATE INDEX idx_mcp_execution_logs_server ON public.mcp_execution_logs(server_id);
CREATE INDEX idx_mcp_execution_logs_timestamp ON public.mcp_execution_logs(timestamp DESC);

-- Create trigger for updated_at
CREATE TRIGGER update_mcp_servers_updated_at
  BEFORE UPDATE ON public.mcp_servers
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Insert default MCP servers for compliance and workflow monitoring
INSERT INTO public.mcp_servers (customer_id, server_name, server_type, description, status, capabilities) 
SELECT 
  id,
  'Compliance Intelligence Server',
  'compliance',
  'AI-powered compliance monitoring and prediction using real-time audit logs and behavioral patterns',
  'active',
  '["query_compliance_status", "predict_violations", "analyze_control_gaps", "generate_evidence_reports"]'::jsonb
FROM public.customers
WHERE status = 'active'
LIMIT 1;

INSERT INTO public.mcp_servers (customer_id, server_name, server_type, description, status, capabilities)
SELECT 
  id,
  'Workflow Optimization Server',
  'workflow',
  'ML-powered workflow analysis and bottleneck detection across integrated systems',
  'active',
  '["analyze_workflow_efficiency", "detect_bottlenecks", "predict_completion_times", "recommend_optimizations"]'::jsonb
FROM public.customers
WHERE status = 'active'
LIMIT 1;