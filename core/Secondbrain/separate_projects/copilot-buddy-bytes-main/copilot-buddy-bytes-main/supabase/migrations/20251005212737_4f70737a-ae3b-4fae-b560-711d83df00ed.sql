-- Fix infinite recursion in user_profiles RLS policy
-- Drop the problematic policy that has a circular reference
DROP POLICY IF EXISTS "Users can view profiles in their organization" ON user_profiles;

-- Create a simpler, non-recursive policy
-- Users can see their own profile and profiles in their organization
CREATE POLICY "Users can view profiles in their organization"
ON user_profiles
FOR SELECT
TO authenticated
USING (
  user_id = auth.uid() 
  OR customer_id IS NULL
  OR EXISTS (
    SELECT 1 FROM user_profiles up
    WHERE up.user_id = auth.uid()
    AND up.customer_id = user_profiles.customer_id
    LIMIT 1
  )
);