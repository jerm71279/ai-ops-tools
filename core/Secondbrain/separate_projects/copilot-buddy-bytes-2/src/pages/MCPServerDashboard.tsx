import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { LogOut, Server } from "lucide-react";
import { useDemoMode } from "@/hooks/useDemoMode";
import DashboardNavigation from "@/components/DashboardNavigation";
import MCPServerStatus from "@/components/MCPServerStatus";
import { MCPServerConfig } from "@/components/MCPServerConfig";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

/**
 * MCP Server Dashboard Data Flow
 * 
 * ```mermaid
 * graph TD
 *     A[User] -->|Visits /mcp-servers| B[MCPServerDashboard Component]
 *     B -->|useEffect| C[checkAccess]
 *     C -->|Auth Check| D[supabase.auth.getSession]
 *     D -->|Get Profile| E[user_profiles Table]
 *     E -->|Get customer_id| F[setUserCustomerId]
 *     
 *     G[MCPServerStatus Component] -->|Query| H[mcp_servers Table]
 *     H -->|Filter by customer_id| I[Customer MCP Servers]
 *     I -->|Display List| J[Server Cards with Status]
 *     
 *     J -->|Real-time Updates| K[Server Health Monitoring]
 *     K -->|Status: active/inactive/error| L[Badge Colors]
 *     
 *     M[MCPServerConfig Component] -->|Create Server| N[Server Configuration Form]
 *     N -->|Submit| O[Insert Server]
 *     O -->|Store| H
 *     
 *     P[AI MCP Generator Tab] -->|User Input| Q[Describe Server Purpose]
 *     Q -->|Invoke| R[ai-mcp-generator Edge Function]
 *     R -->|AI Processing| S[Generate MCP Configuration]
 *     S -->|Return Config| T[Server Setup Form]
 *     T -->|Save| H
 *     
 *     U[Edit Server] -->|Click| V[Load Configuration]
 *     V -->|Update| H
 *     
 *     W[Delete Server] -->|Confirm| X[Remove from DB]
 *     X -->|Delete| H
 *     
 *     Y[Execution Logs Tab] -->|Display| Z[MCPExecutionLogs Component]
 *     Z -->|Query| AA[mcp_execution_logs Table]
 *     AA -->|Filter by server| AB[Server Activity Logs]
 *     
 *     AC[Test Server] -->|Invoke| AD[mcp-server Edge Function]
 *     AD -->|Test Connection| AE[Server Response]
 *     
 *     style A fill:#e1f5ff
 *     style R fill:#fff4e6
 *     style AD fill:#fff4e6
 *     style H fill:#e6f7ff
 *     style AA fill:#e6f7ff
 * ```
 */

const MCPServerDashboard = () => {
  const navigate = useNavigate();
  const isPreviewMode = useDemoMode();
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [userCustomerId, setUserCustomerId] = useState<string>("");

  useEffect(() => {
    checkAccess();
  }, []);

  const checkAccess = async () => {
    if (isPreviewMode) {
      setUserProfile({ full_name: "Demo User" });
      setUserCustomerId("demo-customer");
      setIsLoading(false);
      return;
    }

    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      navigate("/auth");
      return;
    }

    const { data: profile } = await supabase
      .from("user_profiles")
      .select("*, customers(id)")
      .eq("user_id", session.user.id)
      .maybeSingle();

    setUserProfile(profile);
    setUserCustomerId(profile?.customer_id || profile?.customers?.id || "");
    setIsLoading(false);
  };

  const handleSignOut = async () => {
    if (isPreviewMode) {
      navigate("/demo");
      return;
    }
    await supabase.auth.signOut();
    navigate("/auth");
  };

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b bg-card" style={{ marginTop: 'var(--lanes-height, 0px)' }}>
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Server className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold">MCP Server Management</h1>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">{userProfile?.full_name}</span>
            {isPreviewMode && <Badge variant="outline">Preview Mode</Badge>}
            <Button onClick={handleSignOut} variant="outline" size="sm">
              <LogOut className="h-4 w-4 mr-2" />
              {isPreviewMode ? "Back to Demos" : "Sign Out"}
            </Button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 pt-56 pb-8 space-y-6">
        <DashboardNavigation 
          title="MCP Server Management"
          dashboards={[
            { name: "Admin Dashboard", path: "/admin" },
            { name: "Employee Portal", path: "/portal" },
            { name: "Analytics Portal", path: "/analytics" },
            { name: "Compliance Portal", path: "/compliance" },
            { name: "Change Management", path: "/change-management" },
            { name: "Executive Dashboard", path: "/dashboard/executive" },
            { name: "Finance Dashboard", path: "/dashboard/finance" },
            { name: "HR Dashboard", path: "/dashboard/hr" },
            { name: "IT Dashboard", path: "/dashboard/it" },
            { name: "Operations Dashboard", path: "/dashboard/operations" },
            { name: "Sales Dashboard", path: "/dashboard/sales" },
            { name: "SOC Dashboard", path: "/dashboard/soc" },
            { name: "MCP Servers", path: "/mcp-servers" },
          ]}
        />

        <Tabs defaultValue="all" className="space-y-4">
          <div className="bg-card border-b border-border -mx-4 px-4 mb-4">
            <TabsList className="w-full justify-start overflow-x-auto flex-nowrap h-auto p-0 bg-transparent border-0">
              <TabsTrigger value="all" className="whitespace-nowrap shrink-0">All Servers</TabsTrigger>
              <TabsTrigger value="compliance" className="whitespace-nowrap shrink-0">Compliance</TabsTrigger>
              <TabsTrigger value="executive" className="whitespace-nowrap shrink-0">Executive</TabsTrigger>
              <TabsTrigger value="finance" className="whitespace-nowrap shrink-0">Finance</TabsTrigger>
              <TabsTrigger value="hr" className="whitespace-nowrap shrink-0">HR</TabsTrigger>
              <TabsTrigger value="it" className="whitespace-nowrap shrink-0">IT</TabsTrigger>
              <TabsTrigger value="operations" className="whitespace-nowrap shrink-0">Operations</TabsTrigger>
              <TabsTrigger value="sales" className="whitespace-nowrap shrink-0">Sales</TabsTrigger>
              <TabsTrigger value="security" className="whitespace-nowrap shrink-0">Security</TabsTrigger>
              <TabsTrigger value="configure" className="whitespace-nowrap shrink-0">Configure New</TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="all" className="space-y-4">
            <MCPServerStatus customerId={userCustomerId} />
          </TabsContent>

          <TabsContent value="compliance" className="space-y-4">
            <MCPServerStatus filterByServerType="compliance" />
          </TabsContent>

          <TabsContent value="executive" className="space-y-4">
            <MCPServerStatus filterByServerType="executive" />
          </TabsContent>

          <TabsContent value="finance" className="space-y-4">
            <MCPServerStatus filterByServerType="finance" />
          </TabsContent>

          <TabsContent value="hr" className="space-y-4">
            <MCPServerStatus filterByServerType="hr" />
          </TabsContent>

          <TabsContent value="it" className="space-y-4">
            <MCPServerStatus filterByServerType="it" />
          </TabsContent>

          <TabsContent value="operations" className="space-y-4">
            <MCPServerStatus filterByServerType="operations" />
          </TabsContent>

          <TabsContent value="sales" className="space-y-4">
            <MCPServerStatus filterByServerType="sales" />
          </TabsContent>

          <TabsContent value="security" className="space-y-4">
            <MCPServerStatus filterByServerType="security" />
          </TabsContent>

          <TabsContent value="configure" className="space-y-4">
            <MCPServerConfig customerId={userCustomerId} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default MCPServerDashboard;