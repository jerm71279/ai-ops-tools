import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Activity, Server, Zap, CheckCircle2, XCircle } from "lucide-react";
import { toast } from "sonner";

type MCPServer = {
  id: string;
  server_name: string;
  server_type: string;
  description: string;
  status: string;
  capabilities: any; // JSON from database
  last_health_check: string | null;
};

type MCPTool = {
  id: string;
  tool_name: string;
  description: string;
  execution_count: number;
  avg_execution_time_ms: number | null;
};

type MCPServerStatusProps = { 
  customerId?: string;
  filterByServerType?: string; // e.g., "compliance", "it", "finance", "hr", "operations"
};

export default function MCPServerStatus({ customerId, filterByServerType }: MCPServerStatusProps) {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [tools, setTools] = useState<Record<string, MCPTool[]>>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchMCPServers();
  }, [filterByServerType]);

  const fetchMCPServers = async () => {
    try {
      let query = supabase
        .from("mcp_servers")
        .select("*")
        .order("created_at", { ascending: false });

      // Apply server_type filter if provided
      if (filterByServerType) {
        query = query.eq("server_type", filterByServerType);
      }

      const { data: serversData, error: serversError } = await query;

      if (serversError) throw serversError;

      setServers(serversData || []);

      // Fetch tools for each server
      if (serversData) {
        const toolsPromises = serversData.map(async (server) => {
          const { data: toolsData } = await supabase
            .from("mcp_tools")
            .select("*")
            .eq("server_id", server.id)
            .eq("is_enabled", true);
          
          return { serverId: server.id, tools: toolsData || [] };
        });

        const toolsResults = await Promise.all(toolsPromises);
        const toolsMap: Record<string, MCPTool[]> = {};
        toolsResults.forEach(({ serverId, tools }) => {
          toolsMap[serverId] = tools;
        });
        setTools(toolsMap);
      }
    } catch (error) {
      console.error("Error fetching MCP servers:", error);
      toast.error("Failed to load MCP servers");
    } finally {
      setIsLoading(false);
    }
  };

  const testMCPTool = async (serverId: string, toolName: string) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) {
        toast.error("Authentication required");
        return;
      }

      // Resolve customer_id: use prop if provided, else lookup from profile
      let resolvedCustomerId = customerId;

      if (!resolvedCustomerId) {
        const { data: profile } = await supabase
          .from("user_profiles")
          .select("customer_id")
          .eq("user_id", session.user.id)
          .maybeSingle();
        resolvedCustomerId = profile?.customer_id || undefined;
      }

      if (!resolvedCustomerId) {
        toast.error("Customer profile not found");
        return;
      }

      toast.info(`Testing ${toolName}...`);

      const { data, error } = await supabase.functions.invoke("mcp-server", {
        body: {
          server_id: serverId,
          tool_name: toolName,
          customer_id: resolvedCustomerId,
          user_id: session.user.id,
          input_data: {},
        },
      });

      if (error) throw error;

      if (data.success) {
        toast.success(`${toolName} executed successfully in ${data.execution_time_ms}ms`);
      } else {
        toast.error(`${toolName} failed: ${data.error}`);
      }
    } catch (error) {
      console.error("Error testing MCP tool:", error);
      toast.error("Failed to execute tool");
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      active: { variant: "default" as const, icon: CheckCircle2, color: "text-green-500" },
      inactive: { variant: "secondary" as const, icon: XCircle, color: "text-gray-500" },
      error: { variant: "destructive" as const, icon: XCircle, color: "text-red-500" },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.inactive;
    const Icon = config.icon;

    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className={`h-3 w-3 ${config.color}`} />
        {status}
      </Badge>
    );
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            MCP Servers
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">Loading MCP servers...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            MCP Servers
          </CardTitle>
          <CardDescription>
            Model Context Protocol servers connecting AI to your data
          </CardDescription>
        </CardHeader>
        <CardContent>
          {servers.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No MCP servers configured
            </div>
          ) : (
            <div className="space-y-4">
              {servers.map((server) => (
                <Card key={server.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Activity className="h-5 w-5 text-primary" />
                        <div>
                          <CardTitle className="text-lg">{server.server_name}</CardTitle>
                          <CardDescription className="text-sm">
                            {server.description}
                          </CardDescription>
                        </div>
                      </div>
                      {getStatusBadge(server.status)}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-semibold mb-2 flex items-center gap-2">
                          <Zap className="h-4 w-4" />
                          Capabilities
                        </h4>
                        <div className="flex flex-wrap gap-2">
                          {(Array.isArray(server.capabilities) ? server.capabilities : []).map((cap: string) => (
                            <Badge key={cap} variant="outline">
                              {cap.replace(/_/g, " ")}
                            </Badge>
                          ))}
                        </div>
                      </div>

                      {tools[server.id] && tools[server.id].length > 0 && (
                        <div>
                          <h4 className="text-sm font-semibold mb-2">Available Tools</h4>
                          <div className="space-y-2">
                            {tools[server.id].map((tool) => (
                              <div
                                key={tool.id}
                                className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
                              >
                                <div className="flex-1">
                                  <p className="font-medium text-sm">{tool.tool_name}</p>
                                  <p className="text-xs text-muted-foreground">
                                    {tool.description}
                                  </p>
                                  {tool.execution_count > 0 && (
                                    <p className="text-xs text-muted-foreground mt-1">
                                      Executed {tool.execution_count} times
                                      {tool.avg_execution_time_ms && 
                                        ` • Avg: ${tool.avg_execution_time_ms}ms`
                                      }
                                    </p>
                                  )}
                                </div>
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => testMCPTool(server.id, tool.tool_name)}
                                >
                                  Test
                                </Button>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {server.last_health_check && (
                        <p className="text-xs text-muted-foreground">
                          Last health check:{" "}
                          {new Date(server.last_health_check).toLocaleString()}
                        </p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}