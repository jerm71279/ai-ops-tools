-- Fix infinite recursion in roles table RLS policies
-- Drop all existing policies on roles table
DROP POLICY IF EXISTS "Authenticated users can view roles" ON public.roles;
DROP POLICY IF EXISTS "Service role can manage roles" ON public.roles;
DROP POLICY IF EXISTS "Everyone can view roles" ON public.roles;
DROP POLICY IF EXISTS "Admins can manage roles" ON public.roles;

-- Create simple, non-recursive policies for roles table
-- Allow all authenticated users to SELECT roles (no recursion)
CREATE POLICY "Anyone can view roles"
  ON public.roles
  FOR SELECT
  TO authenticated
  USING (true);

-- Only service role can modify roles
CREATE POLICY "Service role can insert roles"
  ON public.roles
  FOR INSERT
  TO service_role
  WITH CHECK (true);

CREATE POLICY "Service role can update roles"
  ON public.roles
  FOR UPDATE
  TO service_role
  USING (true);

CREATE POLICY "Service role can delete roles"
  ON public.roles
  FOR DELETE
  TO service_role
  USING (true);