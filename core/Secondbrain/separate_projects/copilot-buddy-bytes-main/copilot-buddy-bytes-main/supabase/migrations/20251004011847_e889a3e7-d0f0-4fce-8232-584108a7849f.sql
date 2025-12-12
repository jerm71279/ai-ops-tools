-- Security Fix: Restrict department_permissions access to authenticated users only
-- Remove overly permissive policy that allows unauthenticated access

DROP POLICY IF EXISTS "Everyone can view department permissions" ON public.department_permissions;

-- Create new policy requiring authentication
CREATE POLICY "Authenticated users can view department permissions"
  ON public.department_permissions
  FOR SELECT
  TO authenticated
  USING (auth.uid() IS NOT NULL);

-- Add comment explaining the security model
COMMENT ON TABLE public.department_permissions IS 
'Department permission definitions. Access restricted to authenticated users only to prevent organizational structure exposure.';