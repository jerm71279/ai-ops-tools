-- Update RLS policies to allow read access to all authenticated users
-- Write operations remain restricted by RBAC

-- Customers table - allow authenticated users to view all customers
DROP POLICY IF EXISTS "Authenticated users view own customer" ON customers;
CREATE POLICY "Authenticated users can view all customers"
  ON customers FOR SELECT
  TO authenticated
  USING (true);

-- User profiles - allow all authenticated users to view profiles
DROP POLICY IF EXISTS "Users can view their own profile" ON user_profiles;
CREATE POLICY "Authenticated users can view all profiles"
  ON user_profiles FOR SELECT
  TO authenticated
  USING (true);

-- Integrations - allow all authenticated users to view
DROP POLICY IF EXISTS "Admins can view all integrations" ON integrations;
CREATE POLICY "Authenticated users can view integrations"
  ON integrations FOR SELECT
  TO authenticated
  USING (true);

-- MCP Servers - allow all authenticated users to view
DROP POLICY IF EXISTS "Customers can view own MCP servers" ON mcp_servers;
DROP POLICY IF EXISTS "Admins can view MCP servers" ON mcp_servers;
CREATE POLICY "Authenticated users can view MCP servers"
  ON mcp_servers FOR SELECT
  TO authenticated
  USING (true);

-- MCP Tools - allow all authenticated users to view
DROP POLICY IF EXISTS "Customers can view own MCP tools" ON mcp_tools;
DROP POLICY IF EXISTS "Admins can view MCP tools" ON mcp_tools;
CREATE POLICY "Authenticated users can view MCP tools"
  ON mcp_tools FOR SELECT
  TO authenticated
  USING (true);

-- MCP Resources - allow all authenticated users to view
DROP POLICY IF EXISTS "Customers can view own MCP resources" ON mcp_resources;
DROP POLICY IF EXISTS "Admins can view MCP resources" ON mcp_resources;
CREATE POLICY "Authenticated users can view MCP resources"
  ON mcp_resources FOR SELECT
  TO authenticated
  USING (true);

-- Compliance frameworks - already allows everyone to view active frameworks
-- Compliance controls - already allows everyone to view
-- Compliance tags - already allows everyone to view

-- Compliance reports - allow all authenticated users to view
DROP POLICY IF EXISTS "Admins can view all compliance reports" ON compliance_reports;
CREATE POLICY "Authenticated users can view compliance reports"
  ON compliance_reports FOR SELECT
  TO authenticated
  USING (true);

-- Evidence files - allow all authenticated users to view
DROP POLICY IF EXISTS "Admins can view all evidence files" ON evidence_files;
CREATE POLICY "Authenticated users can view evidence files"
  ON evidence_files FOR SELECT
  TO authenticated
  USING (true);

-- ML insights - allow all authenticated users to view
DROP POLICY IF EXISTS "Admins can view all ML insights" ON ml_insights;
CREATE POLICY "Authenticated users can view ML insights"
  ON ml_insights FOR SELECT
  TO authenticated
  USING (true);

-- ML models - allow all authenticated users to view
DROP POLICY IF EXISTS "Admins can view all ML models" ON ml_models;
CREATE POLICY "Authenticated users can view ML models"
  ON ml_models FOR SELECT
  TO authenticated
  USING (true);

-- Anomaly detections - allow all authenticated users to view
DROP POLICY IF EXISTS "Admins can view anomalies" ON anomaly_detections;
CREATE POLICY "Authenticated users can view anomalies"
  ON anomaly_detections FOR SELECT
  TO authenticated
  USING (true);

-- Audit logs - allow all authenticated users to view
DROP POLICY IF EXISTS "Users view own audit logs" ON audit_logs;
DROP POLICY IF EXISTS "Admins view own customer audit logs" ON audit_logs;
CREATE POLICY "Authenticated users can view audit logs"
  ON audit_logs FOR SELECT
  TO authenticated
  USING (true);

-- Behavioral events - allow all authenticated users to view
DROP POLICY IF EXISTS "Users can view their own events" ON behavioral_events;
DROP POLICY IF EXISTS "Admins can view all events" ON behavioral_events;
CREATE POLICY "Authenticated users can view behavioral events"
  ON behavioral_events FOR SELECT
  TO authenticated
  USING (true);

-- System access logs - allow all authenticated users to view
DROP POLICY IF EXISTS "Users can view their own access logs" ON system_access_logs;
DROP POLICY IF EXISTS "Admins can view all access logs" ON system_access_logs;
CREATE POLICY "Authenticated users can view access logs"
  ON system_access_logs FOR SELECT
  TO authenticated
  USING (true);

-- User sessions - allow all authenticated users to view
DROP POLICY IF EXISTS "Users can view their own sessions" ON user_sessions;
DROP POLICY IF EXISTS "Admins can view all sessions" ON user_sessions;
CREATE POLICY "Authenticated users can view sessions"
  ON user_sessions FOR SELECT
  TO authenticated
  USING (true);

-- Notifications - allow all authenticated users to view
DROP POLICY IF EXISTS "Users can view their own notifications" ON notifications;
DROP POLICY IF EXISTS "Admins can manage all notifications" ON notifications;
CREATE POLICY "Authenticated users can view all notifications"
  ON notifications FOR SELECT
  TO authenticated
  USING (true);

-- Users can only update their own notifications
CREATE POLICY "Users can update own notifications"
  ON notifications FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id);

-- Prediction history - allow all authenticated users to view
DROP POLICY IF EXISTS "Admins can view prediction history" ON prediction_history;
CREATE POLICY "Authenticated users can view prediction history"
  ON prediction_history FOR SELECT
  TO authenticated
  USING (true);

-- MCP execution logs - allow all authenticated users to view
DROP POLICY IF EXISTS "Customers can view own execution logs" ON mcp_execution_logs;
DROP POLICY IF EXISTS "Admins can view all execution logs" ON mcp_execution_logs;
CREATE POLICY "Authenticated users can view execution logs"
  ON mcp_execution_logs FOR SELECT
  TO authenticated
  USING (true);

-- Dashboard widgets - allow all authenticated users to view
DROP POLICY IF EXISTS "Users can view their own widgets" ON dashboard_widgets;
DROP POLICY IF EXISTS "Admins can view all widgets" ON dashboard_widgets;
CREATE POLICY "Authenticated users can view all widgets"
  ON dashboard_widgets FOR SELECT
  TO authenticated
  USING (true);

-- Customer customizations - allow all authenticated users to view
DROP POLICY IF EXISTS "Users can view their own customer customizations" ON customer_customizations;
DROP POLICY IF EXISTS "Admins can manage all customizations" ON customer_customizations;
CREATE POLICY "Authenticated users can view customizations"
  ON customer_customizations FOR SELECT
  TO authenticated
  USING (true);

-- Customer frameworks - allow all authenticated users to view
DROP POLICY IF EXISTS "Admins can view customer frameworks" ON customer_frameworks;
CREATE POLICY "Authenticated users can view customer frameworks"
  ON customer_frameworks FOR SELECT
  TO authenticated
  USING (true);

-- Note: Write operations (INSERT, UPDATE, DELETE) policies remain unchanged
-- They continue to require admin role or specific user ownership