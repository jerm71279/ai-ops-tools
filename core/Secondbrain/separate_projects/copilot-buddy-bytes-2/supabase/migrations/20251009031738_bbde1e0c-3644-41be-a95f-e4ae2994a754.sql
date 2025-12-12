-- Completely fix infinite recursion in user_profiles
-- The issue is ANY query to user_profiles from within a user_profiles policy creates recursion

-- Drop ALL existing SELECT policies on user_profiles
DROP POLICY IF EXISTS "Users can view own profile" ON public.user_profiles;
DROP POLICY IF EXISTS "Admins view all profiles" ON public.user_profiles;

-- Create single, simple policies that don't query user_profiles at all
-- Policy 1: Users can always view their own profile (no recursion)
CREATE POLICY "View own profile"
ON public.user_profiles
FOR SELECT
USING (user_id = auth.uid());

-- Policy 2: Admins can view all profiles (uses function that doesn't reference user_profiles)
CREATE POLICY "Admins view all"
ON public.user_profiles
FOR SELECT
USING (has_role(auth.uid(), 'admin'::app_role));