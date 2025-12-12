-- =============================================
-- CRITICAL SECURITY FIX: Lock Down Public Data
-- =============================================

-- Fix user_profiles - restrict to same organization only
DROP POLICY IF EXISTS "Authenticated users can view all profiles" ON user_profiles;
CREATE POLICY "Users can view profiles in their organization"
  ON user_profiles
  FOR SELECT
  USING (
    customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    ) OR has_role(auth.uid(), 'admin'::app_role)
  );

-- Fix customers table - remove redundant block policy, tighten access
DROP POLICY IF EXISTS "Block anonymous access to customers" ON customers;

-- Fix customer_details - already has good policies, no change needed

-- Fix support_tickets - add RLS if not exists
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' AND tablename = 'support_tickets'
  ) THEN
    ALTER TABLE support_tickets ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "Users can view tickets in their organization"
      ON support_tickets FOR SELECT
      USING (customer_id IN (
        SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
      ));
    
    CREATE POLICY "Users can create tickets for their organization"
      ON support_tickets FOR INSERT
      WITH CHECK (customer_id IN (
        SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
      ));
    
    CREATE POLICY "Users can update tickets in their organization"
      ON support_tickets FOR UPDATE
      USING (customer_id IN (
        SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
      ));
  END IF;
END $$;

-- Fix incidents - add RLS if not exists
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' AND tablename = 'incidents'
  ) THEN
    ALTER TABLE incidents ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "Users can view incidents in their organization"
      ON incidents FOR SELECT
      USING (customer_id IN (
        SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
      ));
    
    CREATE POLICY "Security team can manage incidents"
      ON incidents FOR ALL
      USING (has_role(auth.uid(), 'admin'::app_role));
  END IF;
END $$;

-- Fix network_devices - add RLS if not exists
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' AND tablename = 'network_devices'
  ) THEN
    ALTER TABLE network_devices ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "Users can view network devices in their organization"
      ON network_devices FOR SELECT
      USING (customer_id IN (
        SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
      ));
    
    CREATE POLICY "Admins can manage network devices"
      ON network_devices FOR ALL
      USING (has_role(auth.uid(), 'admin'::app_role));
  END IF;
END $$;

-- Fix customer_billing - add RLS if not exists
DO $$ 
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_policies 
    WHERE schemaname = 'public' AND tablename = 'customer_billing'
  ) THEN
    ALTER TABLE customer_billing ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "Users can view billing in their organization"
      ON customer_billing FOR SELECT
      USING (customer_id IN (
        SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
      ) OR has_role(auth.uid(), 'admin'::app_role));
    
    CREATE POLICY "Admins can manage billing"
      ON customer_billing FOR ALL
      USING (has_role(auth.uid(), 'admin'::app_role));
  END IF;
END $$;

-- Remove redundant audit_logs block policy
DROP POLICY IF EXISTS "Block anonymous access to audit logs" ON audit_logs;

-- Ensure all new CI tables have proper RLS
DO $$ 
BEGIN
  -- ci_audit_log is already protected (created in previous migration)
  -- ci_health_metrics is already protected (created in previous migration)
  
  -- Double-check they're enabled
  ALTER TABLE ci_audit_log ENABLE ROW LEVEL SECURITY;
  ALTER TABLE ci_health_metrics ENABLE ROW LEVEL SECURITY;
END $$;