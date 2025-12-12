import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { BarChart3, TrendingUp, Shield, Users, AlertCircle, CheckCircle, ChevronDown, FileText, Building, Server } from "lucide-react";
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
 * Executive Dashboard Data Flow
 * 
 * ```mermaid
 * graph TD
 *     A[User/Executive] -->|Visits /dashboard/executive| B[ExecutiveDashboard Component]
 *     B -->|useEffect| C[checkAccess & fetchStats]
 *     C -->|Auth Check| D[supabase.auth.getSession]
 *     D -->|Get Profile| E[user_profiles Table]
 *     
 *     C -->|Parallel Queries| F[fetchStats]
 *     F -->|Count| G[customers Table]
 *     F -->|Count| H[ml_insights Table]
 *     F -->|Count| I[anomaly_detections Table]
 *     
 *     G -->|Set State| J[stats.customers]
 *     H -->|Set State| K[stats.mlInsights]
 *     I -->|Set State| L[stats.anomalies]
 *     
 *     B -->|Fetch MCP Servers| M[fetchMcpServers]
 *     M -->|Query by Type| N[mcp_servers Table]
 *     M -->|Filter: server_type=executive| O[Executive MCP Servers]
 *     O -->|Display| P[MCP Dropdown Menu]
 *     
 *     Q[Click Revenue Metric] -->|Navigate| R[/workflow/revenue-analysis]
 *     R -->|Invoke| S[workflow-executor Edge Function]
 *     S -->|Process| T[AI Analysis]
 *     T -->|Generate Insights| H
 *     
 *     U[Click Compliance Score] -->|Navigate| V[/compliance-dashboard]
 *     
 *     W[Reports Menu] -->|Navigate| X[Various Report Pages]
 *     
 *     Y[AI Assistant] -->|Invoke| Z[department-assistant Edge Function]
 *     Z -->|Context: Executive| AA[Strategic Insights]
 *     
 *     AB[MCP Server Status] -->|Monitor| AC[Real-time Health]
 *     
 *     style A fill:#e1f5ff
 *     style S fill:#fff4e6
 *     style Z fill:#fff4e6
 *     style G fill:#e6f7ff
 *     style H fill:#e6f7ff
 *     style I fill:#e6f7ff
 *     style N fill:#e6f7ff
 * ```
 */

const ExecutiveDashboard = () => {
  const navigate = useNavigate();
  const isPreviewMode = useDemoMode();
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [stats, setStats] = useState({
    customers: 0,
    complianceScore: 92,
    workflowEfficiency: 87,
    mlInsights: 0,
    anomalies: 0
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
      .eq("server_type", "executive")
      .eq("status", "active")
      .order("server_name");
    
    if (data) setMcpServers(data);
  };

  const checkAccess = async () => {
    if (isPreviewMode) {
      setUserProfile({ full_name: "Demo User", department: "executive" });
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
    const [customers, insights, anomalies] = await Promise.all([
      supabase.from("customers").select("*", { count: "exact", head: true }),
      supabase.from("ml_insights").select("*", { count: "exact", head: true }),
      supabase.from("anomaly_detections").select("*", { count: "exact", head: true })
    ]);

    setStats({
      customers: customers.count || 0,
      complianceScore: 92,
      workflowEfficiency: 87,
      mlInsights: insights.count || 0,
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
          <h1 className="text-2xl font-bold">Executive Dashboard</h1>
          <DashboardSettingsMenu dashboardName="Executive" />
        </div>
        
        
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          <Card
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/customers?metric=Total Customers&department=executive`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.customers}</div>
              <p className="text-xs text-green-600 mt-1">+12% this month</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/compliance?metric=Compliance Score&department=executive`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Compliance</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.complianceScore}%</div>
              <Badge variant="outline" className="mt-1">Excellent</Badge>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/efficiency?metric=Workflow Efficiency&department=executive`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Workflow Efficiency</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.workflowEfficiency}%</div>
              <p className="text-xs text-muted-foreground mt-1">Cross-system</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/insights?metric=ML Insights&department=executive`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">ML Insights</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.mlInsights}</div>
              <p className="text-xs text-muted-foreground mt-1">Actionable</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/risks?metric=Risk Alerts&department=executive`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Risk Alerts</CardTitle>
              <AlertCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.anomalies}</div>
              <p className="text-xs text-muted-foreground mt-1">Requires attention</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Overview</CardTitle>
              <CardDescription>Framework adherence and coverage</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">SOC 2 Type II</span>
                  <Badge variant="outline">95%</Badge>
                </div>
                <Progress value={95} />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">GDPR</span>
                  <Badge variant="outline">88%</Badge>
                </div>
                <Progress value={88} />
              </div>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">HIPAA</span>
                  <Badge variant="outline">72%</Badge>
                </div>
                <Progress value={72} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Business Metrics</CardTitle>
              <CardDescription>Key performance indicators</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Monthly Recurring Revenue</p>
                  <p className="text-2xl font-bold">$45,200</p>
                </div>
                <Badge className="bg-green-500">+12.3%</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Customer Retention</p>
                  <p className="text-2xl font-bold">94%</p>
                </div>
                <Badge variant="outline">Stable</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">System Uptime</p>
                  <p className="text-2xl font-bold">99.8%</p>
                </div>
                <Badge variant="outline">Excellent</Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        <DepartmentAIAssistant 
          department="executive" 
          departmentLabel="Executive Leadership" 
        />
      </div>
    </div>
  );
};

export default ExecutiveDashboard;
