-- Create Products and Customer Subscriptions System
-- This enables tiered service levels and feature access control integrated with Revio billing

-- Create products table for service catalog
CREATE TABLE IF NOT EXISTS products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_code TEXT NOT NULL UNIQUE,
  product_name TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL DEFAULT 'service',
  service_tier TEXT, -- 'basic', 'professional', 'enterprise', etc.
  base_price DECIMAL(10,2),
  billing_frequency TEXT DEFAULT 'monthly', -- 'monthly', 'annual', 'one-time'
  enabled_features TEXT[] DEFAULT '{}',
  enabled_integrations TEXT[] DEFAULT '{}',
  feature_limits JSONB DEFAULT '{}',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create customer subscriptions table
CREATE TABLE IF NOT EXISTS customer_subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
  status TEXT NOT NULL DEFAULT 'active', -- 'active', 'suspended', 'cancelled', 'expired'
  
  -- Revio integration fields
  revio_subscription_id TEXT,
  revio_customer_id TEXT,
  
  -- Subscription dates
  start_date DATE NOT NULL DEFAULT CURRENT_DATE,
  end_date DATE,
  renewal_date DATE,
  
  -- Pricing
  current_price DECIMAL(10,2),
  currency TEXT DEFAULT 'USD',
  
  -- Metadata
  notes TEXT,
  metadata JSONB DEFAULT '{}',
  
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  
  UNIQUE(customer_id, product_id, status)
);

-- Create service tier packages table
CREATE TABLE IF NOT EXISTS service_tier_packages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tier_name TEXT NOT NULL UNIQUE, -- 'Basic', 'Professional', 'Enterprise'
  tier_level INTEGER NOT NULL, -- 1, 2, 3 for ordering
  description TEXT,
  included_products UUID[] DEFAULT '{}',
  max_users INTEGER,
  max_storage_gb INTEGER,
  included_integrations TEXT[] DEFAULT '{}',
  support_level TEXT DEFAULT 'standard', -- 'basic', 'standard', 'premium', '24/7'
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create feature access log for auditing
CREATE TABLE IF NOT EXISTS feature_access_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  feature_name TEXT NOT NULL,
  integration_name TEXT,
  access_granted BOOLEAN NOT NULL,
  denial_reason TEXT,
  accessed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS on all tables
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE service_tier_packages ENABLE ROW LEVEL SECURITY;
ALTER TABLE feature_access_log ENABLE ROW LEVEL SECURITY;

-- RLS Policies for products table
CREATE POLICY "Admins can manage products"
  ON products FOR ALL
  USING (has_role(auth.uid(), 'admin'));

CREATE POLICY "Authenticated users can view active products"
  ON products FOR SELECT
  USING (is_active = true);

-- RLS Policies for customer_subscriptions table
CREATE POLICY "Admins can manage all subscriptions"
  ON customer_subscriptions FOR ALL
  USING (has_role(auth.uid(), 'admin'));

CREATE POLICY "Users can view their organization subscriptions"
  ON customer_subscriptions FOR SELECT
  USING (
    customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    )
  );

-- RLS Policies for service_tier_packages table
CREATE POLICY "Admins can manage tier packages"
  ON service_tier_packages FOR ALL
  USING (has_role(auth.uid(), 'admin'));

CREATE POLICY "Authenticated users can view active tier packages"
  ON service_tier_packages FOR SELECT
  USING (is_active = true);

-- RLS Policies for feature_access_log table
CREATE POLICY "System can insert access logs"
  ON feature_access_log FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Admins can view all access logs"
  ON feature_access_log FOR SELECT
  USING (has_role(auth.uid(), 'admin'));

CREATE POLICY "Users can view their own access logs"
  ON feature_access_log FOR SELECT
  USING (user_id = auth.uid());

-- Create function to check if customer has a specific feature
CREATE OR REPLACE FUNCTION customer_has_feature(
  _customer_id UUID,
  _feature_name TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN EXISTS (
    SELECT 1
    FROM customer_subscriptions cs
    JOIN products p ON p.id = cs.product_id
    WHERE cs.customer_id = _customer_id
      AND cs.status = 'active'
      AND (
        cs.end_date IS NULL OR cs.end_date >= CURRENT_DATE
      )
      AND p.is_active = true
      AND _feature_name = ANY(p.enabled_features)
  );
END;
$$;

-- Create indexes for performance
CREATE INDEX idx_customer_subscriptions_customer ON customer_subscriptions(customer_id);
CREATE INDEX idx_customer_subscriptions_product ON customer_subscriptions(product_id);
CREATE INDEX idx_customer_subscriptions_status ON customer_subscriptions(status);
CREATE INDEX idx_customer_subscriptions_revio ON customer_subscriptions(revio_subscription_id);
CREATE INDEX idx_feature_access_log_customer ON feature_access_log(customer_id);
CREATE INDEX idx_feature_access_log_user ON feature_access_log(user_id);
CREATE INDEX idx_products_tier ON products(service_tier);

-- Create updated_at triggers
CREATE TRIGGER update_products_updated_at
  BEFORE UPDATE ON products
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customer_subscriptions_updated_at
  BEFORE UPDATE ON customer_subscriptions
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_tier_packages_updated_at
  BEFORE UPDATE ON service_tier_packages
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Insert sample service tier packages
INSERT INTO service_tier_packages (tier_name, tier_level, description, support_level) VALUES
  ('Basic', 1, 'Essential features for small teams', 'standard'),
  ('Professional', 2, 'Advanced features for growing businesses', 'premium'),
  ('Enterprise', 3, 'Full suite with dedicated support', '24/7')
ON CONFLICT (tier_name) DO NOTHING;

-- Insert sample products
INSERT INTO products (product_code, product_name, description, category, service_tier, base_price, enabled_features) VALUES
  ('CMDB_BASIC', 'CMDB Basic', 'Configuration Management Database - Basic tier', 'infrastructure', 'basic', 49.99, ARRAY['cmdb_view', 'ci_tracking']),
  ('CMDB_PRO', 'CMDB Professional', 'CMDB with advanced automation', 'infrastructure', 'professional', 149.99, ARRAY['cmdb_view', 'ci_tracking', 'auto_discovery', 'health_monitoring']),
  ('COMPLIANCE_BASIC', 'Compliance Basic', 'Basic compliance monitoring', 'compliance', 'basic', 99.99, ARRAY['compliance_dashboard', 'basic_reports']),
  ('COMPLIANCE_PRO', 'Compliance Professional', 'Advanced compliance with automation', 'compliance', 'professional', 299.99, ARRAY['compliance_dashboard', 'basic_reports', 'auto_remediation', 'evidence_collection'])
ON CONFLICT (product_code) DO NOTHING;