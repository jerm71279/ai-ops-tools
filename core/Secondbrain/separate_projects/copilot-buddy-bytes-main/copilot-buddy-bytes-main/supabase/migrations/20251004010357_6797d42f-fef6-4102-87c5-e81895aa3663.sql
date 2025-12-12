-- Fix RLS policies for customers table to prevent unauthorized access
-- Drop existing policies
DROP POLICY IF EXISTS "Admins can view all customers" ON public.customers;
DROP POLICY IF EXISTS "Users can view their own customer record" ON public.customers;
DROP POLICY IF EXISTS "Admins can update all customers" ON public.customers;
DROP POLICY IF EXISTS "Users can update their own customer record" ON public.customers;
DROP POLICY IF EXISTS "Admins can insert customers" ON public.customers;
DROP POLICY IF EXISTS "Admins can delete customers" ON public.customers;

-- Create new policies with explicit authentication requirements
-- SELECT policies
CREATE POLICY "Authenticated admins can view all customers"
  ON public.customers
  FOR SELECT
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
  );

CREATE POLICY "Authenticated users can view their own customer record"
  ON public.customers
  FOR SELECT
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND auth.uid() = user_id
  );

-- UPDATE policies
CREATE POLICY "Authenticated admins can update all customers"
  ON public.customers
  FOR UPDATE
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
  );

CREATE POLICY "Authenticated users can update their own customer record"
  ON public.customers
  FOR UPDATE
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND auth.uid() = user_id
  );

-- INSERT policies
CREATE POLICY "Authenticated admins can insert customers"
  ON public.customers
  FOR INSERT
  TO authenticated
  WITH CHECK (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
  );

-- DELETE policies
CREATE POLICY "Authenticated admins can delete customers"
  ON public.customers
  FOR DELETE
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
  );