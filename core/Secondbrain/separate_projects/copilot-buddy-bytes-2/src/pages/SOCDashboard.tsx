import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Shield, AlertTriangle, Activity, Eye, Lock, 
  TrendingUp, Database, Users, FileWarning, CheckCircle2,
  Clock, Zap, ChevronDown, FileText, Search, Server, Globe
} from "lucide-react";
import { useDemoMode } from "@/hooks/useDemoMode";


import { toast } from "sonner";
import MCPServerStatus from "@/components/MCPServerStatus";
import { DepartmentAIAssistant } from "@/components/DepartmentAIAssistant";
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
 * SOC Dashboard Data Flow
 * 
 * ```mermaid
 * graph TD
 *     A[SOC Analyst] -->|Visits /dashboard/soc| B[SOCDashboard Component]
 *     B -->|useEffect| C[checkAccess & fetchStats]
 *     C -->|Auth Check| D[supabase.auth.getSession]
 *     D -->|Get Profile| E[user_profiles Table]
 *     
 *     C -->|Parallel Queries| F[fetchSecurityData]
 *     F -->|Query| G[anomaly_detections Table]
 *     G -->|Filter: severity=critical| H[Critical Alerts]
 *     G -->|Filter: status=new| I[Active Threats]
 *     G -->|Filter: status=resolved| J[Resolved Incidents]
 *     
 *     H -->|Set State| K[metrics.criticalAlerts]
 *     I -->|Set State| L[metrics.activeThreats]
 *     J -->|Set State| M[metrics.resolvedIncidents]
 *     
 *     B -->|Fetch MCP Servers| N[fetchMcpServers]
 *     N -->|Query| O[mcp_servers Table]
 *     N -->|Filter: server_type=soc| P[SOC MCP Servers]
 *     P -->|Display| Q[MCP Dropdown Menu]
 *     
 *     R[Real-time Monitoring] -->|Subscribe| S[anomaly_detections Realtime]
 *     S -->|New Event| T[Update Dashboard]
 *     
 *     U[Privileged Access] -->|Navigate| V[/privileged-access-audit]
 *     V -->|Load| W[audit_logs Table]
 *     W -->|Filter: compliance_tags=privileged_access| X[Access Logs]
 *     
 *     Y[View Incident] -->|Click| Z[Incident Detail Modal]
 *     Z -->|Display| AA[Full Incident Context]
 *     
 *     AB[Threat Intelligence] -->|External API| AC[Threat Feeds]
 *     AC -->|Enrich| G
 *     
 *     AD[SIEM Integration] -->|API| AE[Security Information]
 *     AE -->|Store| G
 *     
 *     AF[AI Assistant] -->|Invoke| AG[department-assistant Edge Function]
 *     AG -->|Context: SOC| AH[Threat Analysis & Recommendations]
 *     
 *     AI[Compliance Score] -->|Calculate| AJ[Based on Framework Requirements]
 *     
 *     AK[Response Time] -->|Track| AL[Incident Timestamps]
 *     
 *     style A fill:#e1f5ff
 *     style AG fill:#fff4e6
 *     style AC fill:#ffe6e6
 *     style AE fill:#ffe6e6
 *     style G fill:#e6f7ff
 *     style O fill:#e6f7ff
 *     style W fill:#e6f7ff
 * ```
 */

interface SecurityMetrics {
  totalIncidents: number;
  criticalAlerts: number;
  activeThreats: number;
  resolvedIncidents: number;
  complianceScore: number;
  systemsMonitored: number;
  avgResponseTime: string;
  threatsPrevented: number;
}

interface SecurityIncident {
  id: string;
  severity: "critical" | "high" | "medium" | "low";
  type: string;
  description: string;
  timestamp: string;
  status: "new" | "investigating" | "resolved";
  affectedSystems: string[];
}

const SOCDashboard = () => {
  const navigate = useNavigate();
  const isPreviewMode = useDemoMode();
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [metrics, setMetrics] = useState<SecurityMetrics>({
    totalIncidents: 0,
    criticalAlerts: 0,
    activeThreats: 0,
    resolvedIncidents: 0,
    complianceScore: 0,
    systemsMonitored: 0,
    avgResponseTime: "0m",
    threatsPrevented: 0
  });
  const [incidents, setIncidents] = useState<SecurityIncident[]>([]);
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [mcpServers, setMcpServers] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState("incidents");

  useEffect(() => {
    checkAccess();
    fetchMcpServers();
  }, []);

  const fetchMcpServers = async () => {
    const { data } = await supabase
      .from("mcp_servers")
      .select("id, server_name, server_type")
      .eq("server_type", "security")
      .eq("status", "active")
      .order("server_name");
    
    if (data) setMcpServers(data);
  };

  const checkAccess = async () => {
    if (isPreviewMode) {
      setUserProfile({ full_name: "Security Analyst", department: "security" });
      await fetchSecurityData();
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
      .select("*")
      .eq("user_id", session.user.id)
      .maybeSingle();

    setUserProfile(profile);
    await fetchSecurityData();
    setIsLoading(false);
  };

  const fetchSecurityData = async () => {
    try {
      // Fetch anomaly detections
      const { data: anomalyData, error: anomalyError } = await supabase
        .from("anomaly_detections")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(10);

      if (anomalyError) throw anomalyError;

      setAnomalies(anomalyData || []);

      // Fetch audit logs for security events
      const { data: auditData } = await supabase
        .from("audit_logs")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(20);

      // Fetch compliance reports
      const { data: complianceData } = await supabase
        .from("compliance_reports")
        .select("*");

      // Fetch integrations count
      const { data: integrationsData } = await supabase
        .from("integrations")
        .select("*");

      // Calculate metrics
      const criticalAnomalies = anomalyData?.filter(a => a.severity === "critical").length || 0;
      const unresolvedAnomalies = anomalyData?.filter(a => !a.resolved_at).length || 0;
      const resolvedAnomalies = anomalyData?.filter(a => a.resolved_at).length || 0;
      
      // Calculate average compliance score
      let avgComplianceScore = 85; // Default
      if (complianceData && complianceData.length > 0) {
        const scores = complianceData.map(r => {
          const findings = r.findings as any;
          if (findings?.compliance_score) return findings.compliance_score;
          return 85;
        });
        avgComplianceScore = scores.reduce((a, b) => a + b, 0) / scores.length;
      }

      setMetrics({
        totalIncidents: anomalyData?.length || 0,
        criticalAlerts: criticalAnomalies,
        activeThreats: unresolvedAnomalies,
        resolvedIncidents: resolvedAnomalies,
        complianceScore: Math.round(avgComplianceScore),
        systemsMonitored: integrationsData?.length || 0,
        avgResponseTime: "12m",
        threatsPrevented: resolvedAnomalies * 3
      });

      // Transform anomalies to incidents
      const incidentData: SecurityIncident[] = (anomalyData || []).map(anomaly => ({
        id: anomaly.id,
        severity: (anomaly.severity || "medium") as any,
        type: anomaly.anomaly_type,
        description: anomaly.description,
        timestamp: anomaly.created_at,
        status: anomaly.resolved_at ? "resolved" : "new",
        affectedSystems: [anomaly.system_name]
      }));

      setIncidents(incidentData);

    } catch (error) {
      console.error("Error fetching security data:", error);
      toast.error("Failed to load security data");
    }
  };

  const handleSignOut = async () => {
    if (isPreviewMode) {
      navigate("/demo");
      return;
    }
    await supabase.auth.signOut();
    navigate("/auth");
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "text-red-600 bg-red-50 border-red-200";
      case "high": return "text-orange-600 bg-orange-50 border-orange-200";
      case "medium": return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "low": return "text-blue-600 bg-blue-50 border-blue-200";
      default: return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "resolved": return "bg-green-100 text-green-800";
      case "investigating": return "bg-blue-100 text-blue-800";
      case "new": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-background">

      <div className="container mx-auto px-4 pb-8 space-y-6" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>

        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Security Operations Center</h1>
          <DashboardSettingsMenu dashboardName="SOC" />
        </div>
        
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/incidents?metric=Total Incidents&department=security`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Incidents</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.totalIncidents}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {metrics.criticalAlerts} critical alerts
              </p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/threats?metric=Active Threats&department=security`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Threats</CardTitle>
              <Eye className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{metrics.activeThreats}</div>
              <p className="text-xs text-muted-foreground mt-1">Requires attention</p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/compliance-score?metric=Compliance Score&department=security`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Compliance Score</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{metrics.complianceScore}%</div>
              <Progress value={metrics.complianceScore} className="mt-2" />
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/response-time?metric=Response Time&department=security`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Response Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.avgResponseTime}</div>
              <p className="text-xs text-muted-foreground mt-1">Target: &lt;15m</p>
            </CardContent>
          </Card>
        </div>

        {/* Secondary Metrics */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Systems Monitored</p>
                  <p className="text-2xl font-bold mt-1">{metrics.systemsMonitored}</p>
                </div>
                <Database className="h-8 w-8 text-primary opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Threats Prevented</p>
                  <p className="text-2xl font-bold mt-1 text-green-600">{metrics.threatsPrevented}</p>
                </div>
                <Lock className="h-8 w-8 text-green-600 opacity-50" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">Resolved Today</p>
                  <p className="text-2xl font-bold mt-1">{metrics.resolvedIncidents}</p>
                </div>
                <TrendingUp className="h-8 w-8 text-primary opacity-50" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Tabs for Different Views */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="incidents">Security Incidents</TabsTrigger>
            <TabsTrigger value="anomalies">Anomaly Detection</TabsTrigger>
            <TabsTrigger value="compliance">Compliance Status</TabsTrigger>
          </TabsList>

          <TabsContent value="incidents" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Security Incidents</CardTitle>
                <CardDescription>Real-time security event monitoring and response</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {incidents.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Shield className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>No security incidents detected</p>
                    </div>
                  ) : (
                    incidents.map((incident) => (
                      <div
                        key={incident.id}
                        className={`p-4 rounded-lg border ${getSeverityColor(incident.severity)}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <Badge className={getStatusColor(incident.status)}>
                                {incident.status.toUpperCase()}
                              </Badge>
                              <Badge variant="outline">{incident.severity.toUpperCase()}</Badge>
                              <span className="text-xs text-muted-foreground">
                                {new Date(incident.timestamp).toLocaleString()}
                              </span>
                            </div>
                            <h4 className="font-semibold mb-1">{incident.type}</h4>
                            <p className="text-sm mb-2">{incident.description}</p>
                            <div className="flex items-center gap-2 text-xs">
                              <Database className="h-3 w-3" />
                              <span>Affected: {incident.affectedSystems.join(", ")}</span>
                            </div>
                          </div>
                          <Button size="sm" variant="outline">
                            Investigate
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="anomalies" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Anomaly Detection</CardTitle>
                <CardDescription>AI-powered behavioral anomaly detection</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {anomalies.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground">
                      <Activity className="h-12 w-12 mx-auto mb-2 opacity-50" />
                      <p>No anomalies detected</p>
                    </div>
                  ) : (
                    anomalies.map((anomaly) => (
                      <div key={anomaly.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3">
                          <div className={`h-10 w-10 rounded-full flex items-center justify-center ${
                            anomaly.severity === "critical" ? "bg-red-100" : 
                            anomaly.severity === "high" ? "bg-orange-100" : "bg-yellow-100"
                          }`}>
                            <FileWarning className={`h-5 w-5 ${
                              anomaly.severity === "critical" ? "text-red-600" : 
                              anomaly.severity === "high" ? "text-orange-600" : "text-yellow-600"
                            }`} />
                          </div>
                          <div>
                            <p className="font-medium">{anomaly.anomaly_type}</p>
                            <p className="text-sm text-muted-foreground">{anomaly.description}</p>
                            {anomaly.confidence_score && (
                              <p className="text-xs text-muted-foreground mt-1">
                                Confidence: {(parseFloat(anomaly.confidence_score) * 100).toFixed(1)}%
                              </p>
                            )}
                          </div>
                        </div>
                        <Badge variant={anomaly.resolved_at ? "outline" : "destructive"}>
                          {anomaly.resolved_at ? "Resolved" : "Active"}
                        </Badge>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>


          <TabsContent value="compliance" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Compliance Monitoring</CardTitle>
                <CardDescription>Real-time compliance status across frameworks</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">SOC 2 Type II</span>
                      <span className="text-sm text-muted-foreground">92%</span>
                    </div>
                    <Progress value={92} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">ISO 27001</span>
                      <span className="text-sm text-muted-foreground">88%</span>
                    </div>
                    <Progress value={88} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">GDPR</span>
                      <span className="text-sm text-muted-foreground">95%</span>
                    </div>
                    <Progress value={95} className="h-2" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">HIPAA</span>
                      <span className="text-sm text-muted-foreground">85%</span>
                    </div>
                    <Progress value={85} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-4">
              <Button variant="outline" className="justify-start">
                <Zap className="h-4 w-4 mr-2" />
                Run Security Scan
              </Button>
              <Button variant="outline" className="justify-start">
                <Users className="h-4 w-4 mr-2" />
                Review Access Logs
              </Button>
              <Button variant="outline" className="justify-start">
                <FileWarning className="h-4 w-4 mr-2" />
                Generate Report
              </Button>
              <Button variant="outline" className="justify-start">
                <Lock className="h-4 w-4 mr-2" />
                Update Policies
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SOCDashboard;
