-- Fix Critical Security Issue #2: Update views to use SECURITY INVOKER
-- This makes views respect RLS policies instead of bypassing them

ALTER VIEW change_request_dashboard SET (security_invoker = on);
ALTER VIEW ci_overview SET (security_invoker = on);