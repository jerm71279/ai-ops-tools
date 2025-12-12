-- Fix Security Definer Views by setting them to SECURITY INVOKER
-- This ensures views execute with the querying user's privileges and respect RLS policies
-- instead of bypassing them with the view creator's elevated privileges

-- SOC Engineer Alert Rules View
ALTER VIEW soc_engineer_alert_rules SET (security_invoker = on);

-- SOC Engineer Device Metrics View
ALTER VIEW soc_engineer_device_metrics SET (security_invoker = on);

-- SOC Engineer Network Alerts View
ALTER VIEW soc_engineer_network_alerts SET (security_invoker = on);

-- SOC Engineer Network Devices View
ALTER VIEW soc_engineer_network_devices SET (security_invoker = on);

-- SOC Engineer Network Monitoring View
ALTER VIEW soc_engineer_network_monitoring SET (security_invoker = on);

-- Verify the fix by checking view options
COMMENT ON VIEW soc_engineer_alert_rules IS 'Security Invoker enabled - respects RLS policies of querying user';
COMMENT ON VIEW soc_engineer_device_metrics IS 'Security Invoker enabled - respects RLS policies of querying user';
COMMENT ON VIEW soc_engineer_network_alerts IS 'Security Invoker enabled - respects RLS policies of querying user';
COMMENT ON VIEW soc_engineer_network_devices IS 'Security Invoker enabled - respects RLS policies of querying user';
COMMENT ON VIEW soc_engineer_network_monitoring IS 'Security Invoker enabled - respects RLS policies of querying user';
