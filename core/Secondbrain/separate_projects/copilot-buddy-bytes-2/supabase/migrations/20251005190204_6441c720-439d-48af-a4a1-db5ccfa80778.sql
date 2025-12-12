-- Final fix for infinite recursion - completely eliminate joins in roles policies
-- The issue: when querying user_roles with roles join, the roles policy tries to check user_roles

-- Drop ALL existing policies on roles table
DROP POLICY IF EXISTS "Authenticated users can view roles" ON roles;
DROP POLICY IF EXISTS "Admins can manage roles" ON roles;

-- Create completely non-recursive policies for roles table
-- Allow ALL authenticated users to SELECT roles (no admin check)
CREATE POLICY "Anyone authenticated can view roles"
ON roles
FOR SELECT
TO authenticated
USING (true);

-- Only allow service_role to manage roles (not regular users)
-- This prevents the recursion issue entirely
CREATE POLICY "Only service role can manage roles"
ON roles
FOR ALL
TO service_role
USING (true)
WITH CHECK (true);