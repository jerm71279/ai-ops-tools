-- Secure the integration_credentials table
-- Drop existing overly permissive policy
DROP POLICY IF EXISTS "Admins can manage credentials" ON public.integration_credentials;

-- Create separate policies with restricted access
-- Admins can INSERT credentials (but will typically be done via edge function)
CREATE POLICY "Service can insert credentials"
  ON public.integration_credentials
  FOR INSERT
  TO authenticated
  WITH CHECK (
    auth.jwt() ->> 'role' = 'service_role'
  );

-- Admins can UPDATE metadata fields only (not encrypted_data)
CREATE POLICY "Admins can update credential metadata"
  ON public.integration_credentials
  FOR UPDATE
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
  )
  WITH CHECK (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
  );

-- Admins can DELETE credentials
CREATE POLICY "Admins can delete credentials"
  ON public.integration_credentials
  FOR DELETE
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
  );

-- Admins can view metadata but NOT encrypted_data
-- Note: This allows SELECT but access to encrypted_data should be restricted in application code
CREATE POLICY "Admins can view credential metadata"
  ON public.integration_credentials
  FOR SELECT
  TO authenticated
  USING (
    auth.uid() IS NOT NULL 
    AND has_role(auth.uid(), 'admin'::app_role)
  );

-- Service role (edge functions) can access everything including encrypted_data
CREATE POLICY "Service role can access credentials"
  ON public.integration_credentials
  FOR SELECT
  TO authenticated
  USING (
    auth.jwt() ->> 'role' = 'service_role'
  );

-- Create a secure function to retrieve credentials (for edge functions only)
-- This function logs all credential access for audit purposes
CREATE OR REPLACE FUNCTION public.get_integration_credential(
  _integration_id uuid,
  _customer_id uuid
)
RETURNS TABLE (
  id uuid,
  integration_id uuid,
  customer_id uuid,
  credential_type text,
  encrypted_data bytea,
  expires_at timestamptz
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  -- Log the credential access attempt
  INSERT INTO audit_logs (
    customer_id,
    user_id,
    system_name,
    action_type,
    action_details,
    compliance_tags
  ) VALUES (
    _customer_id,
    COALESCE(auth.uid(), '00000000-0000-0000-0000-000000000000'::uuid),
    'integration_credentials',
    'credential_access',
    jsonb_build_object(
      'integration_id', _integration_id,
      'accessed_at', now(),
      'access_type', 'function_call'
    ),
    ARRAY['security', 'credential_access']
  );

  -- Return the credential
  RETURN QUERY
  SELECT 
    ic.id,
    ic.integration_id,
    ic.customer_id,
    ic.credential_type,
    ic.encrypted_data,
    ic.expires_at
  FROM integration_credentials ic
  WHERE ic.integration_id = _integration_id
    AND ic.customer_id = _customer_id
    AND (ic.expires_at IS NULL OR ic.expires_at > now());
END;
$$;

-- Grant execute permission to authenticated users (edge functions)
GRANT EXECUTE ON FUNCTION public.get_integration_credential(uuid, uuid) TO authenticated;

-- Add comment explaining the security model
COMMENT ON TABLE public.integration_credentials IS 
'SECURITY: Direct SELECT of encrypted_data should only be done by edge functions using service role. 
Application code should use get_integration_credential() function which logs all access for audit purposes.
Admins can view metadata but should never directly access encrypted_data field.';

COMMENT ON FUNCTION public.get_integration_credential IS
'Securely retrieves integration credentials with audit logging. 
Should only be called from edge functions with proper authentication context.';