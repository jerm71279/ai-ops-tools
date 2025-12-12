import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Users, UserCheck, Clock, TrendingUp, ChevronDown, FileText, ClipboardList, UserPlus, Server } from "lucide-react";
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
 * HR Dashboard Data Flow
 * 
 * ```mermaid
 * graph TD
 *     A[HR User] -->|Visits /dashboard/hr| B[HRDashboard Component]
 *     B -->|useEffect| C[checkAccess & fetchStats]
 *     C -->|Auth Check| D[supabase.auth.getSession]
 *     D -->|Get Profile| E[user_profiles Table]
 *     
 *     C -->|Parallel Queries| F[fetchStats]
 *     F -->|Count| G[user_profiles Table]
 *     F -->|Count| H[client_onboardings Table]
 *     
 *     G -->|Set State| I[stats.totalUsers]
 *     H -->|Set State| J[Onboarding Stats]
 *     
 *     B -->|Fetch MCP Servers| K[fetchMcpServers]
 *     K -->|Query| L[mcp_servers Table]
 *     K -->|Filter: server_type=hr| M[HR MCP Servers]
 *     M -->|Display| N[MCP Dropdown Menu]
 *     
 *     O[Onboarding Menu] -->|Navigate| P[/onboarding-dashboard]
 *     P -->|Load| Q[client_onboardings Table]
 *     Q -->|Join| R[client_onboarding_tasks Table]
 *     
 *     S[Templates Menu] -->|Navigate| T[/onboarding-templates]
 *     T -->|Load| U[onboarding_templates Table]
 *     
 *     V[Click User Metric] -->|Navigate| W[/workflow/employee-data]
 *     W -->|Invoke| X[workflow-executor Edge Function]
 *     X -->|Process| Y[User Analytics]
 *     
 *     Z[AI Assistant] -->|Invoke| AA[department-assistant Edge Function]
 *     AA -->|Context: HR| AB[HR Insights & Recommendations]
 *     
 *     AC[MCP Server Status] -->|Monitor| AD[Real-time Health]
 *     
 *     style A fill:#e1f5ff
 *     style X fill:#fff4e6
 *     style AA fill:#fff4e6
 *     style G fill:#e6f7ff
 *     style H fill:#e6f7ff
 *     style L fill:#e6f7ff
 *     style Q fill:#e6f7ff
 *     style R fill:#e6f7ff
 * ```
 */

const HRDashboard = () => {
  const navigate = useNavigate();
  const isPreviewMode = useDemoMode();
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeSessions: 0,
    notifications: 0,
    avgSessionTime: "4.2 hrs"
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
      .eq("server_type", "hr")
      .eq("status", "active")
      .order("server_name");
    
    if (data) setMcpServers(data);
  };

  const checkAccess = async () => {
    if (isPreviewMode) {
      setUserProfile({ full_name: "Demo User", department: "hr" });
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
    const [profiles, sessions, notifications] = await Promise.all([
      supabase.from("user_profiles").select("*", { count: "exact", head: true }),
      supabase.from("user_sessions").select("*").eq("status", "active"),
      supabase.from("notifications").select("*", { count: "exact", head: true })
    ]);

    setStats({
      totalUsers: profiles.count || 0,
      activeSessions: sessions.data?.length || 0,
      notifications: notifications.count || 0,
      avgSessionTime: "4.2 hrs"
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
          <h1 className="text-2xl font-bold">HR Dashboard</h1>
          <DashboardSettingsMenu dashboardName="HR" />
        </div>
        
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/employees?metric=Total Employees&department=hr`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Employees</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalUsers}</div>
              <p className="text-xs text-muted-foreground mt-1">Across all departments</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/sessions?metric=Active Sessions&department=hr`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
              <UserCheck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeSessions}</div>
              <Badge variant="outline" className="mt-1">Currently Online</Badge>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/session-time?metric=Avg Session Time&department=hr`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Session Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.avgSessionTime}</div>
              <p className="text-xs text-muted-foreground mt-1">Per employee</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/notifications?metric=Notifications&department=hr`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Notifications</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.notifications}</div>
              <p className="text-xs text-muted-foreground mt-1">Total sent</p>
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate('/hr/employee-onboarding')}
          >
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <UserPlus className="h-5 w-5" />
                Employee Onboarding
              </CardTitle>
              <CardDescription>Manage new employee onboarding processes</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full">
                View Dashboard
              </Button>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate('/employees')}
          >
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Employee Directory
              </CardTitle>
              <CardDescription>View and manage all employees</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full">
                View Directory
              </Button>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate('/leave-management')}
          >
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ClipboardList className="h-5 w-5" />
                Leave Management
              </CardTitle>
              <CardDescription>Manage employee leave requests</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full">
                View Requests
              </Button>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Department Breakdown</CardTitle>
            <CardDescription>Employee distribution across departments</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="font-medium">Compliance</span>
                <Badge>8 employees</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium">IT & Security</span>
                <Badge>12 employees</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium">Operations</span>
                <Badge>15 employees</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium">Finance</span>
                <Badge>6 employees</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <DepartmentAIAssistant 
          department="hr" 
          departmentLabel="Human Resources" 
        />
      </div>
    </div>
  );
};

export default HRDashboard;
