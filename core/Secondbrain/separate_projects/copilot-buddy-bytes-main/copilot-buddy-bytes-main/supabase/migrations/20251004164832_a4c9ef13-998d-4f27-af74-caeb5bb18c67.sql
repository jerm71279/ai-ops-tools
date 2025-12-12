-- Fix MCP server types to match dashboard filters
UPDATE mcp_servers SET server_type = 'finance' WHERE server_type IN ('financial', 'finance_intelligence');
UPDATE mcp_servers SET server_type = 'it' WHERE server_type IN ('infrastructure', 'security_intelligence');
UPDATE mcp_servers SET server_type = 'executive' WHERE server_type IN ('analytics', 'executive_intelligence');
UPDATE mcp_servers SET server_type = 'hr' WHERE server_type = 'hr_intelligence';