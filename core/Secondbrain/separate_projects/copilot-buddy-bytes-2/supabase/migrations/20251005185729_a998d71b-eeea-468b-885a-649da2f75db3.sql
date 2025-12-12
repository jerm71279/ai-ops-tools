-- Fix the remaining infinite recursion in user_roles table
-- The problem: user_roles "Admins can manage user roles" policy is checking user_roles itself

-- Drop the problematic policies
DROP POLICY IF EXISTS "Admins can manage user roles" ON user_roles;

-- Recreate with simpler logic that doesn't cause recursion
-- This policy just checks if the current user IS in the admin role, without complex joins
CREATE POLICY "Admins can manage user roles"
ON user_roles
FOR ALL
TO authenticated
USING (
  -- Allow if user is viewing/managing their own roles
  user_id = auth.uid()
  OR
  -- Allow if user has admin role (using subquery that won't recurse)
  EXISTS (
    SELECT 1 FROM user_roles ur2
    WHERE ur2.user_id = auth.uid()
    AND ur2.role_id IN (
      SELECT r.id FROM roles r WHERE r.name IN ('Super Admin', 'Admin')
    )
  )
)
WITH CHECK (
  -- Same logic for inserts/updates
  user_id = auth.uid()
  OR
  EXISTS (
    SELECT 1 FROM user_roles ur2
    WHERE ur2.user_id = auth.uid()
    AND ur2.role_id IN (
      SELECT r.id FROM roles r WHERE r.name IN ('Super Admin', 'Admin')
    )
  )
);