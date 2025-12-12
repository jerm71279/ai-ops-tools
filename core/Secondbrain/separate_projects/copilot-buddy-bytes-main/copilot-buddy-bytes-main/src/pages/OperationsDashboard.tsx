import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { TrendingUp, Workflow, AlertTriangle, Lightbulb, ChevronDown, FileText, Settings, GitBranch, Server } from "lucide-react";
import { DepartmentAIAssistant } from "@/components/DepartmentAIAssistant";
import { useDemoMode } from "@/hooks/useDemoMode";


import MCPServerStatus from "@/components/MCPServerStatus";
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
 * Operations Dashboard Data Flow
 * 
 * ```mermaid
 * graph TD
 *     A[Operations User] -->|Visits /dashboard/operations| B[OperationsDashboard Component]
 *     B -->|useEffect| C[checkAccess & fetchStats]
 *     C -->|Auth Check| D[supabase.auth.getSession]
 *     D -->|Get Profile| E[user_profiles Table]
 *     
 *     C -->|Parallel Queries| F[fetchStats]
 *     F -->|Count| G[workflows Table]
 *     F -->|Count| H[ml_insights Table]
 *     
 *     G -->|Set State| I[stats.workflows]
 *     H -->|Set State| J[stats.mlInsights]
 *     
 *     B -->|Fetch MCP Servers| K[fetchMcpServers]
 *     K -->|Query| L[mcp_servers Table]
 *     K -->|Filter: server_type=operations| M[Operations MCP Servers]
 *     M -->|Display| N[MCP Dropdown Menu]
 *     
 *     O[Workflow Menu] -->|Navigate| P[/workflow-automation]
 *     P -->|Load| Q[workflows Table]
 *     Q -->|Join| R[workflow_steps Table]
 *     R -->|Join| S[workflow_executions Table]
 *     
 *     T[View Workflow] -->|Click| U[/workflow/:id]
 *     U -->|Load Detail| V[Workflow Configuration]
 *     
 *     W[Execute Workflow] -->|Invoke| X[workflow-executor Edge Function]
 *     X -->|Process Steps| Y[Step-by-Step Execution]
 *     Y -->|Generate Evidence| Z[workflow-evidence-generator]
 *     Z -->|Store| AA[evidence_files Table]
 *     
 *     AB[ML Insights] -->|Query| H
 *     AB -->|Analyze| AC[workflow-insights Edge Function]
 *     AC -->|Generate| AD[Optimization Recommendations]
 *     
 *     AE[AI Assistant] -->|Invoke| AF[department-assistant Edge Function]
 *     AF -->|Context: Operations| AG[Operational Insights]
 *     
 *     AH[Efficiency Score] -->|Calculate| AI[Avg Execution Time & Success Rate]
 *     
 *     style A fill:#e1f5ff
 *     style X fill:#fff4e6
 *     style Z fill:#fff4e6
 *     style AC fill:#fff4e6
 *     style AF fill:#fff4e6
 *     style G fill:#e6f7ff
 *     style H fill:#e6f7ff
 *     style Q fill:#e6f7ff
 *     style S fill:#e6f7ff
 * ```
 */

const OperationsDashboard = () => {
  const navigate = useNavigate();
  const isPreviewMode = useDemoMode();
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [stats, setStats] = useState({
    workflows: 0,
    mlInsights: 0,
    efficiency: 87,
    bottlenecks: 3
  });
  const [mcpServers, setMcpServers] = useState<any[]>([]);

  useEffect(() => {
    checkAccess();
    fetchMcpServers();
  }, []);

  const fetchMcpServers = async () => {
    const { data } = await supabase
      .from("mcp_servers")
      .select("id, server_name, server_type")
      .eq("server_type", "operations")
      .eq("status", "active")
      .order("server_name");
    
    if (data) setMcpServers(data);
  };

  const checkAccess = async () => {
    if (isPreviewMode) {
      setUserProfile({ full_name: "Demo User", department: "operations" });
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
    const [workflows, insights] = await Promise.all([
      supabase.from("workflows").select("*", { count: "exact", head: true }),
      supabase.from("ml_insights").select("*", { count: "exact", head: true })
    ]);

    setStats({
      workflows: workflows.count || 0,
      mlInsights: insights.count || 0,
      efficiency: 87,
      bottlenecks: 3
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
          <h1 className="text-2xl font-bold">Operations Dashboard</h1>
          <DashboardSettingsMenu dashboardName="Operations" />
        </div>
        
        
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => {
              console.log("🔗 Navigating to workflow detail:", { metric: "Workflow Efficiency", department: "operations" });
              navigate(`/workflow/efficiency?metric=Workflow Efficiency&department=operations`);
            }}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Workflow Efficiency</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.efficiency}%</div>
              <Progress value={stats.efficiency} className="mt-2" />
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/active?metric=Active Workflows&department=operations`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Workflows</CardTitle>
              <Workflow className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.workflows}</div>
              <p className="text-xs text-muted-foreground mt-1">Cross-system</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/insights?metric=ML Insights&department=operations`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">ML Insights</CardTitle>
              <Lightbulb className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.mlInsights}</div>
              <Badge variant="outline" className="mt-1">AI-Powered</Badge>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/bottlenecks?metric=Bottlenecks&department=operations`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Bottlenecks</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.bottlenecks}</div>
              <p className="text-xs text-muted-foreground mt-1">Detected</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Cross-System Workflow Efficiency</CardTitle>
            <CardDescription>Performance metrics across integrated systems</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium">Employee Onboarding</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">2.3 days avg</span>
                  <Badge variant="outline">92% efficiency</Badge>
                </div>
              </div>
              <Progress value={92} />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium">Compliance Approval</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">4.1 hours avg</span>
                  <Badge variant="outline">85% efficiency</Badge>
                </div>
              </div>
              <Progress value={85} />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium">Access Provisioning</span>
                <div className="flex items-center gap-2">
                  <span className="text-sm text-muted-foreground">1.2 hours avg</span>
                  <Badge variant="destructive">Issue Detected</Badge>
                </div>
              </div>
              <Progress value={65} className="bg-destructive/20" />
            </div>
          </CardContent>
        </Card>

        <DepartmentAIAssistant 
          department="operations" 
          departmentLabel="Operations" 
        />
      </div>
    </div>
  );
};

export default OperationsDashboard;
