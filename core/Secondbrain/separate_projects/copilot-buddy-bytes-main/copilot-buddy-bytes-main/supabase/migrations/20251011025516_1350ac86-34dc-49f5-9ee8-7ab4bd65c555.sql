-- Add enabled modules and portals tracking to customer_customizations
ALTER TABLE customer_customizations
ADD COLUMN IF NOT EXISTS enabled_portals jsonb DEFAULT '["employee", "client", "admin", "sales", "compliance", "analytics", "data_flow"]'::jsonb,
ADD COLUMN IF NOT EXISTS enabled_modules jsonb DEFAULT '{
  "it_services": true,
  "compliance_security": true,
  "operations": true,
  "finance": true,
  "hr": true,
  "sales_marketing": true,
  "engineering": true,
  "executive": true
}'::jsonb;

-- Add comment explaining the structure
COMMENT ON COLUMN customer_customizations.enabled_portals IS 'Array of enabled portal slugs: employee, client, admin, sales, compliance, analytics, data_flow';
COMMENT ON COLUMN customer_customizations.enabled_modules IS 'JSON object mapping category slugs to boolean enabled status';