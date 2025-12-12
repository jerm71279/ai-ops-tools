-- Fix critical multi-tenant security issues
-- Issue 1: Ensure customers table blocks all anonymous access
-- Issue 2: Prevent cross-customer data access in audit_logs

-- First, verify RLS is enabled (should already be, but ensuring)
ALTER TABLE public.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Drop and recreate customers policies with explicit anon blocking
DROP POLICY IF EXISTS "Authenticated admins can view all customers" ON public.customers;
DROP POLICY IF EXISTS "Authenticated users can view their own customer record" ON public.customers;
DROP POLICY IF EXISTS "Authenticated admins can update all customers" ON public.customers;
DROP POLICY IF EXISTS "Authenticated users can update their own customer record" ON public.customers;
DROP POLICY IF EXISTS "Authenticated admins can insert customers" ON public.customers;
DROP POLICY IF EXISTS "Authenticated admins can delete customers" ON public.customers;

-- Recreate customers policies - explicitly blocking anon access
CREATE POLICY "Authenticated admins view customers"
  ON public.customers
  FOR SELECT
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
  );

CREATE POLICY "Authenticated users view own customer"
  ON public.customers
  FOR SELECT
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND auth.uid() = user_id
  );

CREATE POLICY "Authenticated admins update customers"
  ON public.customers
  FOR UPDATE
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
  );

CREATE POLICY "Authenticated users update own customer"
  ON public.customers
  FOR UPDATE
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND auth.uid() = user_id
  );

CREATE POLICY "Authenticated admins insert customers"
  ON public.customers
  FOR INSERT
  TO authenticated
  WITH CHECK (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
  );

CREATE POLICY "Authenticated admins delete customers"
  ON public.customers
  FOR DELETE
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
  );

-- Block all anon access explicitly
CREATE POLICY "Block anonymous access to customers"
  ON public.customers
  FOR ALL
  TO anon
  USING (false);

-- CRITICAL FIX: Fix audit_logs cross-customer access vulnerability
DROP POLICY IF EXISTS "Admins can view all audit logs" ON public.audit_logs;
DROP POLICY IF EXISTS "Users can view their own audit logs" ON public.audit_logs;
DROP POLICY IF EXISTS "System can insert audit logs" ON public.audit_logs;

-- Create helper function to get user's customer_id
CREATE OR REPLACE FUNCTION public.get_user_customer_id(_user_id uuid)
RETURNS uuid
LANGUAGE sql
STABLE SECURITY DEFINER
SET search_path = public
AS $$
  SELECT customer_id 
  FROM user_profiles 
  WHERE user_id = _user_id 
  LIMIT 1;
$$;

-- Admins can ONLY view audit logs for THEIR OWN customer
CREATE POLICY "Admins view own customer audit logs"
  ON public.audit_logs
  FOR SELECT
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
    AND customer_id = public.get_user_customer_id(auth.uid())
  );

-- Users can ONLY view their own audit logs
CREATE POLICY "Users view own audit logs"
  ON public.audit_logs
  FOR SELECT
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND auth.uid() = user_id
  );

-- System/service can insert audit logs
CREATE POLICY "System insert audit logs"
  ON public.audit_logs
  FOR INSERT
  TO authenticated
  WITH CHECK (
    auth.uid() = user_id
    OR auth.jwt() ->> 'role' = 'service_role'
  );

-- Block anonymous access to audit logs
CREATE POLICY "Block anonymous access to audit logs"
  ON public.audit_logs
  FOR ALL
  TO anon
  USING (false);

-- Add comments explaining the security model
COMMENT ON TABLE public.customers IS 
'SECURITY: Multi-tenant table. RLS enforces customer isolation. 
Admins can only manage customers. Users can only view their own customer record. 
Anonymous access is explicitly blocked.';

COMMENT ON TABLE public.audit_logs IS 
'SECURITY: CRITICAL - Multi-tenant audit trail. RLS enforces strict customer isolation. 
Admins can ONLY view logs for their own customer_id to prevent cross-customer data leaks.
All access requires authentication. Anonymous access blocked.';