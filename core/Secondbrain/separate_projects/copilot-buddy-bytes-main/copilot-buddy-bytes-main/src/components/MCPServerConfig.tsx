import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { supabase } from "@/integrations/supabase/client";
import { Plus, X, Server } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";

interface Tool {
  tool_name: string;
  description: string;
  input_schema: Record<string, any>;
}

export function MCPServerConfig({ customerId }: { customerId: string }) {
  const [serverName, setServerName] = useState("");
  const [description, setDescription] = useState("");
  const [serverType, setServerType] = useState("");
  const [endpointUrl, setEndpointUrl] = useState("");
  const [selectedCapabilities, setSelectedCapabilities] = useState<string[]>([]);
  const [tools, setTools] = useState<Tool[]>([]);
  const [currentTool, setCurrentTool] = useState({ name: "", description: "", schema: "{}" });
  const [showToolForm, setShowToolForm] = useState(false);

  const isDemoMode = customerId === "demo-customer";

  const serverTypes = [
    { value: "database", label: "Database Context" },
    { value: "api", label: "API Integration" },
    { value: "filesystem", label: "File System" },
    { value: "analytics", label: "Analytics" },
    { value: "custom", label: "Custom" }
  ];

  const availableCapabilities = [
    "data_retrieval",
    "data_transformation",
    "query_execution",
    "file_operations",
    "api_calls",
    "notifications",
    "analytics",
    "monitoring"
  ];

  const toggleCapability = (capability: string) => {
    setSelectedCapabilities(prev =>
      prev.includes(capability)
        ? prev.filter(c => c !== capability)
        : [...prev, capability]
    );
  };

  const addTool = () => {
    if (!currentTool.name || !currentTool.description) {
      toast.error("Tool name and description are required");
      return;
    }

    try {
      JSON.parse(currentTool.schema);
    } catch {
      toast.error("Invalid JSON schema");
      return;
    }

    setTools([...tools, {
      tool_name: currentTool.name,
      description: currentTool.description,
      input_schema: JSON.parse(currentTool.schema)
    }]);
    setCurrentTool({ name: "", description: "", schema: "{}" });
    setShowToolForm(false);
    toast.success("Tool added");
  };

  const removeTool = (index: number) => {
    setTools(tools.filter((_, i) => i !== index));
  };

  const saveServer = async () => {
    if (isDemoMode) {
      toast.error("Cannot save MCP servers in demo mode");
      return;
    }

    if (!serverName || !serverType) {
      toast.error("Server name and type are required");
      return;
    }

    if (selectedCapabilities.length === 0) {
      toast.error("Please select at least one capability");
      return;
    }

    try {
      // Insert MCP server
      const { data: server, error: serverError } = await supabase
        .from("mcp_servers")
        .insert({
          customer_id: customerId,
          server_name: serverName,
          description: description || null,
          server_type: serverType,
          endpoint_url: endpointUrl || null,
          capabilities: selectedCapabilities,
          status: "inactive",
          config: {}
        })
        .select()
        .single();

      if (serverError) throw serverError;

      // Insert tools if any
      if (tools.length > 0 && server) {
        const toolsToInsert = tools.map(tool => ({
          server_id: server.id,
          tool_name: tool.tool_name,
          description: tool.description,
          input_schema: tool.input_schema,
          is_enabled: true
        }));

        const { error: toolsError } = await supabase
          .from("mcp_tools")
          .insert(toolsToInsert);

        if (toolsError) throw toolsError;
      }

      toast.success("MCP server created successfully!");
      
      // Reset form
      setServerName("");
      setDescription("");
      setServerType("");
      setEndpointUrl("");
      setSelectedCapabilities([]);
      setTools([]);
    } catch (error: any) {
      console.error("Error saving MCP server:", error);
      toast.error(error.message || "Failed to save MCP server");
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Server className="h-5 w-5" />
          Configure New MCP Server
        </CardTitle>
        <CardDescription>
          Add a new Model Context Protocol server to extend AI capabilities
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Basic Information */}
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="server-name">Server Name</Label>
            <Input
              id="server-name"
              placeholder="e.g., Customer Data Context"
              value={serverName}
              onChange={(e) => setServerName(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="Describe what this MCP server provides..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="server-type">Server Type</Label>
              <Select value={serverType} onValueChange={setServerType}>
                <SelectTrigger id="server-type">
                  <SelectValue placeholder="Select server type" />
                </SelectTrigger>
                <SelectContent>
                  {serverTypes.map(type => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="endpoint">Endpoint URL (Optional)</Label>
              <Input
                id="endpoint"
                placeholder="https://api.example.com/mcp"
                value={endpointUrl}
                onChange={(e) => setEndpointUrl(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Capabilities */}
        <div className="space-y-3">
          <Label>Capabilities</Label>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {availableCapabilities.map(capability => (
              <div key={capability} className="flex items-center space-x-2">
                <Checkbox
                  id={capability}
                  checked={selectedCapabilities.includes(capability)}
                  onCheckedChange={() => toggleCapability(capability)}
                />
                <label
                  htmlFor={capability}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  {capability.replace(/_/g, " ")}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Tools */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label>Tools</Label>
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowToolForm(!showToolForm)}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Tool
            </Button>
          </div>

          {/* Tool Form */}
          {showToolForm && (
            <Card>
              <CardContent className="pt-4 space-y-3">
                <div className="space-y-2">
                  <Label htmlFor="tool-name">Tool Name</Label>
                  <Input
                    id="tool-name"
                    placeholder="e.g., query_customer_data"
                    value={currentTool.name}
                    onChange={(e) => setCurrentTool({ ...currentTool, name: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="tool-description">Description</Label>
                  <Input
                    id="tool-description"
                    placeholder="What does this tool do?"
                    value={currentTool.description}
                    onChange={(e) => setCurrentTool({ ...currentTool, description: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="tool-schema">Input Schema (JSON)</Label>
                  <Textarea
                    id="tool-schema"
                    placeholder='{"type": "object", "properties": {}}'
                    value={currentTool.schema}
                    onChange={(e) => setCurrentTool({ ...currentTool, schema: e.target.value })}
                    className="font-mono text-sm"
                    rows={4}
                  />
                </div>

                <div className="flex gap-2">
                  <Button size="sm" onClick={addTool}>Add Tool</Button>
                  <Button size="sm" variant="outline" onClick={() => setShowToolForm(false)}>
                    Cancel
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Tools List */}
          {tools.length > 0 && (
            <div className="space-y-2">
              {tools.map((tool, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-muted rounded-lg"
                >
                  <div>
                    <p className="font-medium text-sm">{tool.tool_name}</p>
                    <p className="text-xs text-muted-foreground">{tool.description}</p>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => removeTool(index)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Save Button */}
        <div className="flex justify-end gap-2 pt-4 border-t">
          <Button onClick={saveServer}>
            Save MCP Server
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
