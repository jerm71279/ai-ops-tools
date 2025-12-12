-- Fix infinite recursion in user_roles table RLS policies
-- The "Admins can manage user roles" policy queries user_roles table itself, causing recursion

-- Drop the problematic policy
DROP POLICY IF EXISTS "Admins can manage user roles" ON public.user_roles;

-- Create a new policy using the existing has_role function which is SECURITY DEFINER
-- This function bypasses RLS checks and prevents recursion
CREATE POLICY "Admins can manage all user roles"
ON public.user_roles
FOR ALL
TO authenticated
USING (
  has_role(auth.uid(), 'admin'::app_role)
);

-- Also ensure users can still update their own roles
CREATE POLICY "Users can view and manage their own roles"
ON public.user_roles
FOR ALL
TO authenticated
USING (user_id = auth.uid())
WITH CHECK (user_id = auth.uid());