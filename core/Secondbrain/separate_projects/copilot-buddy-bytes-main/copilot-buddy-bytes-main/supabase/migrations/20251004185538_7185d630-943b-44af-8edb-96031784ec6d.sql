-- Fix infinite recursion in roles table RLS policies
-- Drop existing policies that cause recursion
DROP POLICY IF EXISTS "Admins can manage roles" ON public.roles;
DROP POLICY IF EXISTS "Authenticated users can view roles" ON public.roles;

-- Create security definer function to check roles without triggering RLS
CREATE OR REPLACE FUNCTION public.can_manage_roles(_user_id uuid)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.user_roles ur
    JOIN public.roles r ON r.id = ur.role_id
    WHERE ur.user_id = _user_id
      AND r.name IN ('Super Admin', 'Admin')
  );
$$;

-- Recreate policies using the security definer function
CREATE POLICY "Authenticated users can view roles"
  ON public.roles FOR SELECT
  USING (true);  -- Allow all authenticated users to view roles for the join query

CREATE POLICY "Admins can manage roles"
  ON public.roles FOR ALL
  USING (public.can_manage_roles(auth.uid()));