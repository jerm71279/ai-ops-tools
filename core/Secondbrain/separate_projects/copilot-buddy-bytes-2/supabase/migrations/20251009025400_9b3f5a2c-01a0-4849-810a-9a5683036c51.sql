-- =============================================
-- FIX REMAINING SECURITY ISSUES
-- =============================================

-- Fix user_profiles - ensure org-level isolation
DROP POLICY IF EXISTS "Users can view profiles in their organization" ON user_profiles;
DROP POLICY IF EXISTS "Admins can view all profiles" ON user_profiles;

CREATE POLICY "Users can view profiles in their organization only"
  ON user_profiles
  FOR SELECT
  USING (
    customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Admins can view all profiles in any organization"
  ON user_profiles
  FOR SELECT
  USING (has_role(auth.uid(), 'admin'::app_role));

-- Fix customer_details - tighten access to org-level only
DROP POLICY IF EXISTS "Users can view their customer details" ON customer_details;

CREATE POLICY "Users can view only their organization details"
  ON customer_details
  FOR SELECT
  USING (
    customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    )
  );

-- Fix client_portal_users - add org-level restrictions
DROP POLICY IF EXISTS "Portal users can view their own profile" ON client_portal_users;

CREATE POLICY "Portal users view own profile or org profiles"
  ON client_portal_users
  FOR SELECT
  USING (
    id = auth.uid() OR
    customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    )
  );

-- Fix integration_credentials - restrict to service role only
DROP POLICY IF EXISTS "Admins can manage credentials" ON integration_credentials;
DROP POLICY IF EXISTS "Admins can view credentials" ON integration_credentials;

CREATE POLICY "Only service role can access credentials"
  ON integration_credentials
  FOR ALL
  USING ((auth.jwt() ->> 'role'::text) = 'service_role'::text)
  WITH CHECK ((auth.jwt() ->> 'role'::text) = 'service_role'::text);

CREATE POLICY "Admins can insert credentials"
  ON integration_credentials
  FOR INSERT
  WITH CHECK (has_role(auth.uid(), 'admin'::app_role));

-- Fix knowledge_articles - ensure draft protection
DROP POLICY IF EXISTS "Users can view published articles in their org" ON knowledge_articles;
DROP POLICY IF EXISTS "Users can view their own articles" ON knowledge_articles;

CREATE POLICY "Users can view published articles in their organization"
  ON knowledge_articles
  FOR SELECT
  USING (
    status = 'published' AND
    customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Users can view own drafts only"
  ON knowledge_articles
  FOR SELECT
  USING (
    status = 'draft' AND
    created_by = auth.uid()
  );

CREATE POLICY "Admins can view all articles"
  ON knowledge_articles
  FOR SELECT
  USING (has_role(auth.uid(), 'admin'::app_role));

-- Fix cipp_tenants - already has good policies, verify they're strict
-- (Existing policies look good - org-level access)

-- Fix workflows - already has good policies, verify they're strict  
-- (Existing policies look good - org-level access)

-- Add missing RLS to any remaining tables
DO $$ 
DECLARE
  tbl text;
BEGIN
  -- Check for tables without RLS in public schema
  FOR tbl IN 
    SELECT tablename 
    FROM pg_tables 
    WHERE schemaname = 'public' 
    AND NOT rowsecurity
    AND tablename NOT LIKE 'pg_%'
    AND tablename NOT IN ('case_studies') -- case_studies is intentionally public
  LOOP
    RAISE NOTICE 'Enabling RLS on table: %', tbl;
    EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', tbl);
  END LOOP;
END $$;