import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Server, Activity, AlertCircle, Zap, Shield, ChevronDown, FileText, Database, Settings } from "lucide-react";
import MCPServerStatus from "@/components/MCPServerStatus";
import { DepartmentAIAssistant } from "@/components/DepartmentAIAssistant";
import { useDemoMode } from "@/hooks/useDemoMode";


import { DashboardSettingsMenu } from "@/components/DashboardSettingsMenu";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  DropdownMenuSub,
  DropdownMenuSubTrigger,
  DropdownMenuSubContent,
} from "@/components/ui/dropdown-menu";

/**
 * IT Dashboard Data Flow
 * 
 * ```mermaid
 * graph TD
 *     A[User] -->|Visits /dashboard/it| B[ITDashboard Component]
 *     B -->|useEffect| C[checkAccess & fetchStats]
 *     C -->|Auth Check| D[supabase.auth.getSession]
 *     D -->|Get Profile| E[user_profiles Table]
 *     
 *     C -->|Parallel Queries| F[fetchStats]
 *     F -->|Count| G[integrations Table]
 *     F -->|Count| H[mcp_servers Table]
 *     F -->|Count| I[anomaly_detections Table]
 *     
 *     G -->|Filter Active| J[activeIntegrations]
 *     J -->|Set State| K[stats.activeIntegrations]
 *     H -->|Set State| L[stats.mcpServers]
 *     I -->|Set State| M[stats.anomalies]
 *     
 *     B -->|Fetch MCP List| N[fetchMcpServersList]
 *     N -->|Query by Type| H
 *     N -->|Filter: server_type=it| O[IT MCP Servers]
 *     O -->|Render| P[MCP Dropdown Menu]
 *     
 *     Q[Integrations Menu] -->|Navigate| R[/integrations]
 *     
 *     S[CMDB Menu] -->|Navigate| T[/cmdb]
 *     T -->|Load CI Data| U[configuration_items Table]
 *     
 *     V[Change Management] -->|Navigate| W[/change-management]
 *     
 *     X[AI Assistant] -->|Invoke| Y[department-assistant Edge Function]
 *     Y -->|Context: IT| Z[AI Response]
 *     
 *     AA[MCP Server Status] -->|Real-time| AB[Server Health Monitoring]
 *     
 *     style A fill:#e1f5ff
 *     style Y fill:#fff4e6
 *     style G fill:#e6f7ff
 *     style H fill:#e6f7ff
 *     style I fill:#e6f7ff
 *     style U fill:#e6f7ff
 * ```
 */

const ITDashboard = () => {
  const navigate = useNavigate();
  const isPreviewMode = useDemoMode();
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [stats, setStats] = useState({
    integrations: 0,
    activeIntegrations: 0,
    mcpServers: 0,
    anomalies: 0
  });
  const [mcpServersList, setMcpServersList] = useState<any[]>([]);

  useEffect(() => {
    checkAccess();
    fetchMcpServersList();
  }, []);

  const fetchMcpServersList = async () => {
    const { data } = await supabase
      .from("mcp_servers")
      .select("id, server_name, server_type")
      .eq("server_type", "it")
      .eq("status", "active")
      .order("server_name");
    
    if (data) setMcpServersList(data);
  };

  const checkAccess = async () => {
    if (isPreviewMode) {
      setUserProfile({ full_name: "Demo User", department: "it" });
      await fetchStats();
      setIsLoading(false);
      return;
    }

    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      navigate("/auth");
      return;
    }

    // Get user profile
    const { data: profile } = await supabase
      .from("user_profiles")
      .select("*")
      .eq("user_id", session.user.id)
      .maybeSingle();

    setUserProfile(profile);
    await fetchStats();
    setIsLoading(false);
  };

  const fetchStats = async () => {
    const [integrations, mcpServers, anomalies] = await Promise.all([
      supabase.from("integrations").select("*"),
      supabase.from("mcp_servers").select("*", { count: "exact", head: true }),
      supabase.from("anomaly_detections").select("*", { count: "exact", head: true })
    ]);

    const activeIntegrations = integrations.data?.filter(i => i.status === "active").length || 0;

    setStats({
      integrations: integrations.data?.length || 0,
      activeIntegrations,
      mcpServers: mcpServers.count || 0,
      anomalies: anomalies.count || 0
    });
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

      <div className="container mx-auto px-4 pb-8 space-y-6" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>

        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">IT Dashboard</h1>
          <DashboardSettingsMenu dashboardName="IT" />
        </div>
        
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/integrations?metric=Total Integrations&department=it`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Integrations</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.integrations}</div>
              <p className="text-xs text-muted-foreground mt-1">{stats.activeIntegrations} active</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/mcp-servers?metric=MCP Servers&department=it`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">MCP Servers</CardTitle>
              <Server className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.mcpServers}</div>
              <Badge variant="outline" className="mt-1">AI-Powered</Badge>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/system-health?metric=System Health&department=it`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">System Health</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">98.5%</div>
              <p className="text-xs text-muted-foreground mt-1">Uptime</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/anomalies?metric=Anomalies Detected&department=it`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Anomalies Detected</CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.anomalies}</div>
              <p className="text-xs text-muted-foreground mt-1">Requires review</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Security Operations</CardTitle>
            <CardDescription>Access advanced security monitoring and threat detection</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/dashboard/soc">
              <Button className="w-full" variant="outline" size="lg">
                <Shield className="h-5 w-5 mr-2" />
                Open Security Operations Center (SOC)
              </Button>
            </Link>
          </CardContent>
        </Card>

        <DepartmentAIAssistant 
          department="it" 
          departmentLabel="IT & Security" 
        />
      </div>
    </div>
  );
};

export default ITDashboard;
