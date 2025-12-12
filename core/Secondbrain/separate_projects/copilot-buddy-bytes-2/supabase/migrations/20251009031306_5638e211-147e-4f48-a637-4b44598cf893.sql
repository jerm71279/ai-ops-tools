-- Fix infinite recursion in user_profiles by creating a non-recursive policy
-- Drop the problematic policy
DROP POLICY IF EXISTS "Users can view profiles in their organization" ON public.user_profiles;

-- Create a simple, non-recursive policy for user_profiles
-- Users can view their own profile
CREATE POLICY "Users can view own profile"
ON public.user_profiles
FOR SELECT
USING (user_id = auth.uid());

-- Admins can view all profiles in their organization
-- This uses a subquery to the user's OWN profile only, avoiding recursion
CREATE POLICY "Admins view all profiles"
ON public.user_profiles
FOR SELECT
USING (
  has_role(auth.uid(), 'admin'::app_role)
  AND customer_id IN (
    SELECT customer_id 
    FROM user_profiles 
    WHERE user_id = auth.uid()
  )
);

-- Update onboarding_templates policy to use security definer function
DROP POLICY IF EXISTS "Users can view templates" ON public.onboarding_templates;
CREATE POLICY "Users can view templates"
ON public.onboarding_templates
FOR SELECT
USING (
  is_active = true 
  AND customer_id = get_user_customer_id(auth.uid())
);

-- Update client_onboardings policies to use security definer function
DROP POLICY IF EXISTS "Users can view onboardings from their customer" ON public.client_onboardings;
CREATE POLICY "Users can view onboardings from their customer"
ON public.client_onboardings
FOR SELECT
USING (customer_id = get_user_customer_id(auth.uid()));

DROP POLICY IF EXISTS "Users can update onboardings from their customer" ON public.client_onboardings;
CREATE POLICY "Users can update onboardings from their customer"
ON public.client_onboardings
FOR UPDATE
USING (customer_id = get_user_customer_id(auth.uid()));

DROP POLICY IF EXISTS "Users can delete onboardings from their customer" ON public.client_onboardings;
CREATE POLICY "Users can delete onboardings from their customer"
ON public.client_onboardings
FOR DELETE
USING (customer_id = get_user_customer_id(auth.uid()));

DROP POLICY IF EXISTS "Users can create onboardings for their customer" ON public.client_onboardings;
CREATE POLICY "Users can create onboardings for their customer"
ON public.client_onboardings
FOR INSERT
WITH CHECK (
  customer_id = get_user_customer_id(auth.uid())
  AND created_by = auth.uid()
);