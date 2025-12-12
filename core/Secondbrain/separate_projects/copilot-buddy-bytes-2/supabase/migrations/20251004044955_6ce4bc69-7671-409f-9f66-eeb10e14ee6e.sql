-- Allow viewing demo MCP servers (customer_id all zeros)
CREATE POLICY "Anyone can view demo MCP servers"
ON mcp_servers
FOR SELECT
USING (customer_id = '00000000-0000-0000-0000-000000000000'::uuid);

-- Allow viewing tools from demo MCP servers
CREATE POLICY "Anyone can view demo MCP tools"
ON mcp_tools
FOR SELECT
USING (
  server_id IN (
    SELECT id FROM mcp_servers 
    WHERE customer_id = '00000000-0000-0000-0000-000000000000'::uuid
  )
);