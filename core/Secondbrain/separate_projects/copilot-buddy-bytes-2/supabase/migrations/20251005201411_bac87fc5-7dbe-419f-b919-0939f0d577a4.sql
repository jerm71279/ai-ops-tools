-- Fix infinite recursion in roles table RLS policies
-- The issue is that the "Only admins can manage roles" policy queries the roles table
-- while checking permissions on the roles table itself, creating a circular dependency

-- Drop the problematic policy
DROP POLICY IF EXISTS "Only admins can manage roles" ON public.roles;

-- Create a simpler policy that uses the has_role function which is already defined
-- This function uses user_roles and roles table, but is marked as SECURITY DEFINER
-- so it bypasses RLS checks
CREATE POLICY "Admins can manage roles"
ON public.roles
FOR ALL
USING (has_role(auth.uid(), 'admin'::app_role));

-- Ensure roles table has RLS enabled
ALTER TABLE public.roles ENABLE ROW LEVEL SECURITY;