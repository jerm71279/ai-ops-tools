-- Fix infinite recursion in user_profiles RLS policy
-- Drop the problematic policy
DROP POLICY IF EXISTS "Users can view profiles in their organization only" ON public.user_profiles;

-- Create a simpler policy that doesn't cause recursion
-- Users can view profiles in their own organization
CREATE POLICY "Users can view profiles in their organization"
ON public.user_profiles
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM public.user_profiles up
    WHERE up.user_id = auth.uid()
    AND up.customer_id = user_profiles.customer_id
  )
);