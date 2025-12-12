-- Add compliance_tags to workflows table
ALTER TABLE workflows 
ADD COLUMN compliance_tags text[] DEFAULT '{}';

COMMENT ON COLUMN workflows.compliance_tags IS 'Compliance frameworks applicable to this workflow (e.g., SOC2, HIPAA, ISO27001, GDPR)';

-- Add compliance_tags to behavioral_events table
ALTER TABLE behavioral_events 
ADD COLUMN compliance_tags text[] DEFAULT '{}';

COMMENT ON COLUMN behavioral_events.compliance_tags IS 'Compliance categories for user behavior tracking';

-- Add compliance_tags to ai_interactions table  
ALTER TABLE ai_interactions 
ADD COLUMN compliance_tags text[] DEFAULT '{}';

COMMENT ON COLUMN ai_interactions.compliance_tags IS 'Compliance tags for AI usage and data processing';

-- Add compliance_tags to mcp_execution_logs table
ALTER TABLE mcp_execution_logs 
ADD COLUMN compliance_tags text[] DEFAULT '{}';

COMMENT ON COLUMN mcp_execution_logs.compliance_tags IS 'Compliance tracking for MCP tool executions';

-- Add compliance_tags to knowledge_access_logs table
ALTER TABLE knowledge_access_logs 
ADD COLUMN compliance_tags text[] DEFAULT '{}';

COMMENT ON COLUMN knowledge_access_logs.compliance_tags IS 'Compliance tags for knowledge base access tracking';

-- Add compliance_tags to system_access_logs table
ALTER TABLE system_access_logs 
ADD COLUMN compliance_tags text[] DEFAULT '{}';

COMMENT ON COLUMN system_access_logs.compliance_tags IS 'Compliance frameworks for system access tracking';

-- Add compliance_tags to anomaly_detections table
ALTER TABLE anomaly_detections 
ADD COLUMN compliance_tags text[] DEFAULT '{}';

COMMENT ON COLUMN anomaly_detections.compliance_tags IS 'Compliance tags for security incident tracking';

-- Add compliance_tags to integration_credentials table
ALTER TABLE integration_credentials 
ADD COLUMN compliance_tags text[] DEFAULT '{}';

COMMENT ON COLUMN integration_credentials.compliance_tags IS 'Compliance tracking for credential access (HIGH SECURITY)';

-- Add compliance_tags to evidence_files table
ALTER TABLE evidence_files 
ADD COLUMN compliance_tags text[] DEFAULT '{}';

COMMENT ON COLUMN evidence_files.compliance_tags IS 'Compliance frameworks this evidence supports';

-- Add compliance_tags to workflow_executions table
ALTER TABLE workflow_executions 
ADD COLUMN compliance_tags text[] DEFAULT '{}';

COMMENT ON COLUMN workflow_executions.compliance_tags IS 'Compliance tracking for automated workflow runs';

-- Update existing workflows to have compliance tags based on their current tags
UPDATE workflows 
SET compliance_tags = CASE 
  WHEN 'compliance' = ANY(tags) THEN ARRAY['SOC2', 'general']
  WHEN 'hipaa' = ANY(tags) THEN ARRAY['HIPAA', 'PHI']
  ELSE ARRAY['general']
END
WHERE compliance_tags = '{}';

-- Set default compliance tags for high-risk credential access
UPDATE integration_credentials
SET compliance_tags = ARRAY['SOC2', 'security', 'credential_access', 'privileged_access']
WHERE compliance_tags = '{}';

-- Set default compliance tags for evidence files
UPDATE evidence_files
SET compliance_tags = ARRAY['audit_evidence', 'compliance_documentation']
WHERE compliance_tags = '{}';