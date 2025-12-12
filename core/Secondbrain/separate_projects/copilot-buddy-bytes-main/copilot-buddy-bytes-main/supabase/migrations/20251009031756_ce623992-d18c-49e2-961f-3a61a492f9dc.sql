-- Remove duplicate/conflicting policies that may still reference user_profiles table recursively
DROP POLICY IF EXISTS "Admins can view all profiles in any organization" ON public.user_profiles;

-- Verify we only have the two simple policies now:
-- 1. "View own profile" - users can see their own profile
-- 2. "Admins view all" - admins can see all profiles