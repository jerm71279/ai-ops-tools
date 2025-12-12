-- Fix infinite recursion in user_profiles RLS policy
-- The "Users can view profiles in their organization" policy causes recursion
-- because it queries user_profiles while evaluating access to user_profiles

-- Drop the problematic recursive policy
DROP POLICY IF EXISTS "Users can view profiles in their organization" ON user_profiles;

-- The "Authenticated users can view all profiles" policy already exists and is sufficient
-- for collaboration features. If we need organization-level restrictions in the future,
-- we'll need to use a security definer function to avoid recursion.