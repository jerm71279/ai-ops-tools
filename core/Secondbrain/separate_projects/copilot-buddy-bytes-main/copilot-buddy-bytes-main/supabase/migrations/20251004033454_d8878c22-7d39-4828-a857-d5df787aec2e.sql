-- Add customer-specific RLS policies for MCP tables

-- MCP Servers: Allow customers to manage their own servers
CREATE POLICY "Customers can view own MCP servers"
ON mcp_servers FOR SELECT
USING (
  customer_id = get_user_customer_id(auth.uid())
);

CREATE POLICY "Customers can insert own MCP servers"
ON mcp_servers FOR INSERT
WITH CHECK (
  customer_id = get_user_customer_id(auth.uid())
);

CREATE POLICY "Customers can update own MCP servers"
ON mcp_servers FOR UPDATE
USING (
  customer_id = get_user_customer_id(auth.uid())
);

CREATE POLICY "Customers can delete own MCP servers"
ON mcp_servers FOR DELETE
USING (
  customer_id = get_user_customer_id(auth.uid())
);

-- MCP Tools: Allow customers to manage tools for their own servers
CREATE POLICY "Customers can view own MCP tools"
ON mcp_tools FOR SELECT
USING (
  server_id IN (
    SELECT id FROM mcp_servers 
    WHERE customer_id = get_user_customer_id(auth.uid())
  )
);

CREATE POLICY "Customers can insert own MCP tools"
ON mcp_tools FOR INSERT
WITH CHECK (
  server_id IN (
    SELECT id FROM mcp_servers 
    WHERE customer_id = get_user_customer_id(auth.uid())
  )
);

CREATE POLICY "Customers can update own MCP tools"
ON mcp_tools FOR UPDATE
USING (
  server_id IN (
    SELECT id FROM mcp_servers 
    WHERE customer_id = get_user_customer_id(auth.uid())
  )
);

CREATE POLICY "Customers can delete own MCP tools"
ON mcp_tools FOR DELETE
USING (
  server_id IN (
    SELECT id FROM mcp_servers 
    WHERE customer_id = get_user_customer_id(auth.uid())
  )
);

-- MCP Resources: Allow customers to view resources for their own servers
CREATE POLICY "Customers can view own MCP resources"
ON mcp_resources FOR SELECT
USING (
  server_id IN (
    SELECT id FROM mcp_servers 
    WHERE customer_id = get_user_customer_id(auth.uid())
  )
);

CREATE POLICY "Customers can manage own MCP resources"
ON mcp_resources FOR ALL
USING (
  server_id IN (
    SELECT id FROM mcp_servers 
    WHERE customer_id = get_user_customer_id(auth.uid())
  )
);

-- MCP Execution Logs: Allow customers to view their own execution logs
CREATE POLICY "Customers can view own execution logs"
ON mcp_execution_logs FOR SELECT
USING (
  customer_id = get_user_customer_id(auth.uid())
);