-- Fix Critical Security Issue #1: Restrict case_studies RLS policies
DROP POLICY IF EXISTS "Everyone can view published case studies" ON case_studies;

CREATE POLICY "Authenticated users can view published case studies"
ON case_studies
FOR SELECT
TO authenticated
USING (is_published = true);

-- Fix High Priority #1: Restrict compliance_frameworks RLS policies
DROP POLICY IF EXISTS "Everyone can view active frameworks" ON compliance_frameworks;

CREATE POLICY "Authenticated users can view active frameworks"
ON compliance_frameworks
FOR SELECT
TO authenticated
USING (is_active = true);

-- Fix High Priority #2: Restrict compliance_controls RLS policies
DROP POLICY IF EXISTS "Everyone can view controls" ON compliance_controls;

CREATE POLICY "Authenticated users can view controls"
ON compliance_controls
FOR SELECT
TO authenticated
USING (true);

-- Fix High Priority #4: Add search_path to database functions
CREATE OR REPLACE FUNCTION public.validate_uuid_not_undefined(uuid_value uuid)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
SECURITY DEFINER
SET search_path = public
AS $function$
BEGIN
  RETURN uuid_value IS NOT NULL;
END;
$function$;

CREATE OR REPLACE FUNCTION public.generate_change_number()
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $function$
BEGIN
  RETURN 'CHG' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('change_number_seq')::TEXT, 4, '0');
END;
$function$;

CREATE OR REPLACE FUNCTION public.set_change_number()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $function$
BEGIN
  IF NEW.change_number IS NULL THEN
    NEW.change_number := generate_change_number();
  END IF;
  RETURN NEW;
END;
$function$;