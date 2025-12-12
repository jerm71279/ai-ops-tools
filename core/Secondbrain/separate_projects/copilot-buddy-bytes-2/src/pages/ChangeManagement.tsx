import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  FileEdit,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  TrendingUp,
  Calendar,
  Plus,
  RefreshCw,
} from "lucide-react";
import { toast } from "sonner";

/**
 * Change Management Dashboard Data Flow
 * 
 * ```mermaid
 * graph TD
 *     A[User] -->|Visits /change-management| B[ChangeManagement Component]
 *     B -->|useEffect| C[checkAccess & loadChangeData]
 *     C -->|Auth Check| D[supabase.auth.getUser]
 *     
 *     D -->|Authenticated| E[Query Changes]
 *     E -->|Select All| F[change_requests Table]
 *     F -->|Order by created_at| G[setChanges State]
 *     
 *     G -->|Calculate Stats| H[Status Counts]
 *     H -->|Update UI| I[6 Stats Cards]
 *     I -->|Display| J[Total, Pending, Approved, Scheduled, Completed, Failed]
 *     
 *     K[New Change Button] -->|Navigate| L[/change-management/new]
 *     L -->|Form Submit| M[Create Change Request]
 *     M -->|Insert| F
 *     M -->|AI Analysis| N[change-impact-analyzer Edge Function]
 *     N -->|ML Prediction| O[change_impact_analysis Table]
 *     
 *     O -->|Risk Score| P[Update change_requests]
 *     P -->|Approval Flow| Q[change_approvals Table]
 *     
 *     G -->|Render List| R[Change Cards UI]
 *     R -->|Click Change| S[Navigate to /change-management/:id]
 *     S -->|Detail View| T[ChangeManagementDetail Component]
 *     
 *     T -->|NinjaOne Integration| U[Create Ticket]
 *     U -->|API Call| V[ninjaone-ticket Edge Function]
 *     
 *     style A fill:#e1f5ff
 *     style N fill:#fff4e6
 *     style V fill:#ffe6e6
 *     style F fill:#e6f7ff
 *     style O fill:#e6f7ff
 *     style Q fill:#e6f7ff
 * ```
 */

interface ChangeRequest {
  id: string;
  change_number: string;
  title: string;
  change_type: string;
  change_status: string;
  priority: string;
  risk_level?: string;
  requested_by: string;
  scheduled_start_time?: string;
  created_at: string;
}

const ChangeManagement = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [changes, setChanges] = useState<ChangeRequest[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    approved: 0,
    scheduled: 0,
    completed: 0,
    failed: 0,
  });

  useEffect(() => {
    checkAccess();
  }, []);

  const checkAccess = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      navigate("/auth");
      return;
    }
    await loadChangeData();
  };

  const loadChangeData = async () => {
    try {
      setLoading(true);

      const { data: changesData, error: changesError } = await supabase
        .from("change_requests")
        .select("*")
        .order("created_at", { ascending: false });

      if (changesError) throw changesError;

      setChanges(changesData || []);

      // Calculate stats
      const total = changesData?.length || 0;
      const pending = changesData?.filter(c => c.change_status === "pending_approval").length || 0;
      const approved = changesData?.filter(c => c.change_status === "approved").length || 0;
      const scheduled = changesData?.filter(c => c.change_status === "scheduled").length || 0;
      const completed = changesData?.filter(c => c.change_status === "completed").length || 0;
      const failed = changesData?.filter(c => c.change_status === "failed" || c.change_status === "rolled_back").length || 0;

      setStats({ total, pending, approved, scheduled, completed, failed });
    } catch (error) {
      console.error("Error loading change data:", error);
      toast.error("Failed to load change requests");
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "default";
      case "approved": return "secondary";
      case "scheduled": return "outline";
      case "pending_approval": return "default";
      case "failed": return "destructive";
      case "rolled_back": return "destructive";
      default: return "secondary";
    }
  };

  const getRiskColor = (risk?: string) => {
    switch (risk) {
      case "critical": return "destructive";
      case "high": return "default";
      case "medium": return "secondary";
      default: return "outline";
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "critical": return "destructive";
      case "high": return "default";
      case "medium": return "secondary";
      default: return "outline";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="container mx-auto px-4 pt-56 pb-16">
        <DashboardNavigation
          title="Change Management"
          dashboards={[
            { name: "Admin Dashboard", path: "/admin" },
            { name: "Employee Portal", path: "/portal" },
            { name: "Analytics Portal", path: "/analytics" },
            { name: "Compliance Portal", path: "/compliance" },
            { name: "Change Management", path: "/change-management" },
            { name: "CMDB Dashboard", path: "/cmdb" },
            { name: "Onboarding Dashboard", path: "/onboarding" },
            { name: "Executive Dashboard", path: "/dashboard/executive" },
            { name: "Finance Dashboard", path: "/dashboard/finance" },
            { name: "HR Dashboard", path: "/dashboard/hr" },
            { name: "IT Dashboard", path: "/dashboard/it" },
            { name: "Operations Dashboard", path: "/dashboard/operations" },
            { name: "Sales Dashboard", path: "/dashboard/sales" },
            { name: "SOC Dashboard", path: "/dashboard/soc" },
          ]}
        />

        {/* Main Content */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle className="text-2xl">Change Requests</CardTitle>
                <CardDescription>IT Infrastructure change tracking with ML-powered risk analysis</CardDescription>
              </div>
              <Button onClick={() => navigate("/change-management/new")}>
                <Plus className="h-4 w-4 mr-2" />
                New Change Request
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="all" className="space-y-6">
              <TabsList>
                <TabsTrigger value="all">All Changes</TabsTrigger>
                <TabsTrigger value="pending">Pending Approval</TabsTrigger>
                <TabsTrigger value="scheduled">Scheduled</TabsTrigger>
                <TabsTrigger value="completed">Completed</TabsTrigger>
              </TabsList>

              <TabsContent value="all" className="space-y-4">
                {changes.length === 0 ? (
                  <div className="text-center py-12">
                    <FileEdit className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-lg font-semibold mb-2">No Change Requests</h3>
                    <p className="text-muted-foreground mb-4">
                      Create your first change request to start tracking IT infrastructure changes
                    </p>
                    <Button onClick={() => navigate("/change-management/new")}>
                      <Plus className="h-4 w-4 mr-2" />
                      Create Change Request
                    </Button>
                  </div>
                ) : (
                  changes.map((change) => (
                    <Card key={change.id} className="hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => navigate(`/change-management/${change.id}`)}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <Badge variant="outline">{change.change_number}</Badge>
                              <h4 className="font-semibold">{change.title}</h4>
                            </div>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <span className="capitalize">{change.change_type.replace("_", " ")}</span>
                              <span>Created: {new Date(change.created_at).toLocaleDateString()}</span>
                              {change.scheduled_start_time && (
                                <span>Scheduled: {new Date(change.scheduled_start_time).toLocaleString()}</span>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant={getPriorityColor(change.priority)}>
                              {change.priority}
                            </Badge>
                            {change.risk_level && (
                              <Badge variant={getRiskColor(change.risk_level)}>
                                Risk: {change.risk_level}
                              </Badge>
                            )}
                            <Badge variant={getStatusColor(change.change_status)}>
                              {change.change_status.replace("_", " ")}
                            </Badge>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))
                )}
              </TabsContent>

              <TabsContent value="pending">
                {/* Similar structure for filtered views */}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-6 mt-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Changes</CardTitle>
              <FileEdit className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{stats.pending}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Approved</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.approved}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Scheduled</CardTitle>
              <Calendar className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.scheduled}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.completed}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Failed</CardTitle>
              <XCircle className="h-4 w-4 text-destructive" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">{stats.failed}</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default ChangeManagement;
