-- =====================================================
-- PROPER RBAC ROLE HIERARCHY WITH GRANULAR PERMISSIONS
-- =====================================================

-- Create comprehensive department-specific roles
INSERT INTO roles (name, description) VALUES
  ('SOC Engineer', 'Full access to network infrastructure, security configurations, and monitoring systems'),
  ('IT Support Analyst', 'Read-only access to systems for troubleshooting customer issues'),
  ('Compliance Analyst', 'Full access to compliance frameworks, controls, and evidence management'),
  ('Finance Analyst', 'Access to financial data, invoicing, and revenue tracking'),
  ('HR Coordinator', 'Access to employee profiles, onboarding, and role assignments'),
  ('Sales Representative', 'Access to customer relationships, opportunities, and pipeline'),
  ('Operations Coordinator', 'Access to workflows, change management, and service requests'),
  ('Executive Leadership', 'Read-only access to high-level metrics and insights across all departments')
ON CONFLICT (name) DO NOTHING;

-- SOC Engineer Permissions (Full CRUD on security/network)
INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'network_devices', 'admin'
FROM roles r WHERE r.name = 'SOC Engineer'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'network_alerts', 'admin'
FROM roles r WHERE r.name = 'SOC Engineer'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'security_baselines', 'admin'
FROM roles r WHERE r.name = 'SOC Engineer'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'cipp_policies', 'admin'
FROM roles r WHERE r.name = 'SOC Engineer'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'syslog_messages', 'admin'
FROM roles r WHERE r.name = 'SOC Engineer'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'dashboard', 'soc', 'admin'
FROM roles r WHERE r.name = 'SOC Engineer'
ON CONFLICT DO NOTHING;

-- IT Support Analyst Permissions (Read-only troubleshooting)
INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'network_devices', 'view'
FROM roles r WHERE r.name = 'IT Support Analyst'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'network_alerts', 'view'
FROM roles r WHERE r.name = 'IT Support Analyst'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'syslog_messages', 'view'
FROM roles r WHERE r.name = 'IT Support Analyst'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'configuration_items', 'view'
FROM roles r WHERE r.name = 'IT Support Analyst'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'client_tickets', 'edit'
FROM roles r WHERE r.name = 'IT Support Analyst'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'dashboard', 'it', 'edit'
FROM roles r WHERE r.name = 'IT Support Analyst'
ON CONFLICT DO NOTHING;

-- Compliance Analyst Permissions
INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'compliance_frameworks', 'edit'
FROM roles r WHERE r.name = 'Compliance Analyst'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'compliance_controls', 'edit'
FROM roles r WHERE r.name = 'Compliance Analyst'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'compliance_evidence', 'admin'
FROM roles r WHERE r.name = 'Compliance Analyst'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'compliance_reports', 'admin'
FROM roles r WHERE r.name = 'Compliance Analyst'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'dashboard', 'compliance', 'admin'
FROM roles r WHERE r.name = 'Compliance Analyst'
ON CONFLICT DO NOTHING;

-- Finance Analyst Permissions
INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'customer_revenue', 'admin'
FROM roles r WHERE r.name = 'Finance Analyst'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'invoices', 'admin'
FROM roles r WHERE r.name = 'Finance Analyst'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'dashboard', 'finance', 'admin'
FROM roles r WHERE r.name = 'Finance Analyst'
ON CONFLICT DO NOTHING;

-- HR Coordinator Permissions
INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'user_profiles', 'edit'
FROM roles r WHERE r.name = 'HR Coordinator'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'client_onboardings', 'admin'
FROM roles r WHERE r.name = 'HR Coordinator'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'user_roles', 'admin'
FROM roles r WHERE r.name = 'HR Coordinator'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'dashboard', 'hr', 'admin'
FROM roles r WHERE r.name = 'HR Coordinator'
ON CONFLICT DO NOTHING;

-- Sales Representative Permissions
INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'sales_opportunities', 'admin'
FROM roles r WHERE r.name = 'Sales Representative'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'sales_quotes', 'admin'
FROM roles r WHERE r.name = 'Sales Representative'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'customers', 'view'
FROM roles r WHERE r.name = 'Sales Representative'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'dashboard', 'sales', 'admin'
FROM roles r WHERE r.name = 'Sales Representative'
ON CONFLICT DO NOTHING;

-- Operations Coordinator Permissions
INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'workflows', 'admin'
FROM roles r WHERE r.name = 'Operations Coordinator'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'change_requests', 'admin'
FROM roles r WHERE r.name = 'Operations Coordinator'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'service_requests', 'admin'
FROM roles r WHERE r.name = 'Operations Coordinator'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'dashboard', 'operations', 'admin'
FROM roles r WHERE r.name = 'Operations Coordinator'
ON CONFLICT DO NOTHING;

-- Executive Leadership Permissions (Read-only across all systems)
INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'dashboard', 'executive', 'view'
FROM roles r WHERE r.name = 'Executive Leadership'
ON CONFLICT DO NOTHING;

INSERT INTO role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'system', 'all_metrics', 'view'
FROM roles r WHERE r.name = 'Executive Leadership'
ON CONFLICT DO NOTHING;

-- Update views to use roles instead of departments
DROP VIEW IF EXISTS soc_network_devices CASCADE;
DROP VIEW IF EXISTS it_network_devices_readonly CASCADE;
DROP VIEW IF EXISTS executive_dashboard_metrics CASCADE;
DROP VIEW IF EXISTS finance_revenue_data CASCADE;
DROP VIEW IF EXISTS hr_employee_profiles CASCADE;
DROP VIEW IF EXISTS sales_customers CASCADE;
DROP VIEW IF EXISTS operations_workflows CASCADE;
DROP VIEW IF EXISTS compliance_all_frameworks CASCADE;

-- Create helper function to check if user has specific permission
CREATE OR REPLACE FUNCTION has_resource_permission(
  _user_id uuid, 
  _resource_type text, 
  _resource_name text,
  _min_permission text DEFAULT 'view'
)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM user_roles ur
    JOIN role_permissions rp ON rp.role_id = ur.role_id
    WHERE ur.user_id = _user_id
      AND rp.resource_type = _resource_type
      AND rp.resource_name = _resource_name
      AND (
        (_min_permission = 'view') OR
        (_min_permission = 'edit' AND rp.permission_level IN ('edit', 'admin')) OR
        (_min_permission = 'admin' AND rp.permission_level = 'admin')
      )
  );
$$;

-- Update RLS policies to use role-based permissions
DROP POLICY IF EXISTS "SOC engineers can manage network devices" ON network_devices;
CREATE POLICY "Users with network_devices permission can access"
ON network_devices
FOR ALL
USING (has_resource_permission(auth.uid(), 'system', 'network_devices', 'view'))
WITH CHECK (has_resource_permission(auth.uid(), 'system', 'network_devices', 'admin'));

DROP POLICY IF EXISTS "SOC engineers can manage alert rules" ON network_alert_rules;
CREATE POLICY "Users with network_alerts permission can access"
ON network_alert_rules
FOR ALL
USING (has_resource_permission(auth.uid(), 'system', 'network_alerts', 'view'))
WITH CHECK (has_resource_permission(auth.uid(), 'system', 'network_alerts', 'admin'));