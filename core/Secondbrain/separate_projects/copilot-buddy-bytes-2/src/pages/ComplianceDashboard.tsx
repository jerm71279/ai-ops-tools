import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { Shield, CheckCircle, AlertTriangle, FileText, FileCheck, ChevronDown, ClipboardList, FolderOpen, Server } from "lucide-react";
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
 * Compliance Dashboard Data Flow
 * 
 * ```mermaid
 * graph TD
 *     A[User] -->|Visits /compliance-dashboard| B[ComplianceDashboard Component]
 *     B -->|useEffect| C[checkAccess & fetchStats]
 *     C -->|Auth Check| D[supabase.auth.getSession]
 *     D -->|Get Profile| E[user_profiles Table]
 *     
 *     C -->|Parallel Queries| F[fetchStats]
 *     F -->|Count| G[compliance_frameworks Table]
 *     F -->|Count| H[compliance_controls Table]
 *     F -->|Count| I[compliance_reports Table]
 *     F -->|Count| J[evidence_files Table]
 *     
 *     G -->|Set State| K[stats.frameworks]
 *     H -->|Set State| L[stats.controls]
 *     I -->|Set State| M[stats.reports]
 *     J -->|Set State| N[stats.evidenceFiles]
 *     
 *     K -->|Render| O[Framework Cards]
 *     L -->|Render| P[Control Stats]
 *     M -->|Render| Q[Report Count]
 *     N -->|Render| R[Evidence Count]
 *     
 *     S[Click Framework Card] -->|Navigate| T[/workflow/compliance-score]
 *     T -->|AI Processing| U[workflow-executor Edge Function]
 *     U -->|Generate Evidence| V[workflow-evidence-generator]
 *     V -->|Store| J
 *     
 *     W[MCP Servers Menu] -->|Query| X[mcp_servers Table]
 *     X -->|Filter by Type| Y[server_type = 'compliance']
 *     Y -->|Display| Z[Server Dropdown]
 *     
 *     AA[AI Assistant] -->|Query| AB[department-assistant Edge Function]
 *     AB -->|Compliance Context| AC[AI Response]
 *     
 *     style A fill:#e1f5ff
 *     style U fill:#fff4e6
 *     style V fill:#fff4e6
 *     style AB fill:#fff4e6
 *     style G fill:#e6f7ff
 *     style H fill:#e6f7ff
 *     style I fill:#e6f7ff
 *     style J fill:#e6f7ff
 * ```
 */

const ComplianceDashboard = () => {
  const navigate = useNavigate();
  const isPreviewMode = useDemoMode();
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [stats, setStats] = useState({
    frameworks: 0,
    controls: 0,
    reports: 0,
    evidenceFiles: 0,
    complianceScore: 92
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
      .eq("server_type", "compliance")
      .eq("status", "active")
      .order("server_name");
    
    if (data) setMcpServers(data);
  };

  const checkAccess = async () => {
    // Skip authentication in preview mode
    if (isPreviewMode) {
      setUserProfile({ full_name: "Demo User", department: "compliance" });
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
    const [frameworks, controls, reports, evidence] = await Promise.all([
      supabase.from("compliance_frameworks").select("*", { count: "exact", head: true }),
      supabase.from("compliance_controls").select("*", { count: "exact", head: true }),
      supabase.from("compliance_reports").select("*", { count: "exact", head: true }),
      supabase.from("evidence_files").select("*", { count: "exact", head: true })
    ]);

    setStats({
      frameworks: frameworks.count || 0,
      controls: controls.count || 0,
      reports: reports.count || 0,
      evidenceFiles: evidence.count || 0,
      complianceScore: 92
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
          <h1 className="text-2xl font-bold">Compliance Dashboard</h1>
          <DashboardSettingsMenu dashboardName="Compliance" />
        </div>
        
        
        {/* Primary Compliance Frameworks - ISO27001 & SOC 2 */}
        <div className="grid gap-4 md:grid-cols-2 mb-6">
          <Card className="border-primary">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                ISO 27001
              </CardTitle>
              <CardDescription>Information Security Management</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold">94%</span>
                  <Badge variant="default">Compliant</Badge>
                </div>
                <Progress value={94} className="h-2" />
                <p className="text-xs text-muted-foreground mt-2">
                  All workflows tagged with ISO27001 compliance
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-primary">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-primary" />
                SOC 2 Type II
              </CardTitle>
              <CardDescription>Service Organization Controls</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold">95%</span>
                  <Badge variant="default">Compliant</Badge>
                </div>
                <Progress value={95} className="h-2" />
                <p className="text-xs text-muted-foreground mt-2">
                  All workflows tagged with SOC2 compliance
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/compliance-score?metric=Compliance Score&department=compliance`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.complianceScore}%</div>
              <Progress value={stats.complianceScore} className="mt-2" />
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/frameworks?metric=Active Frameworks&department=compliance`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Frameworks</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.frameworks}</div>
              <p className="text-xs text-muted-foreground mt-1">ISO27001, SOC 2, GDPR</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/controls?metric=Controls&department=compliance`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Controls</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.controls}</div>
              <p className="text-xs text-muted-foreground mt-1">Active monitoring</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/evidence?metric=Evidence Files&department=compliance`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Evidence Files</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.evidenceFiles}</div>
              <p className="text-xs text-muted-foreground mt-1">{stats.reports} reports</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Additional Framework Coverage</CardTitle>
            <CardDescription>Other compliance frameworks status</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium">GDPR</span>
                <Badge>88% Complete</Badge>
              </div>
              <Progress value={88} />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium">HIPAA</span>
                <Badge variant="secondary">In Progress</Badge>
              </div>
              <Progress value={72} />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium">PCI DSS</span>
                <Badge variant="secondary">In Progress</Badge>
              </div>
              <Progress value={65} />
            </div>
          </CardContent>
        </Card>

        <DepartmentAIAssistant 
          department="compliance" 
          departmentLabel="Compliance & GRC" 
        />
      </div>
    </div>
  );
};

export default ComplianceDashboard;
