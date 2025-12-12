import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

import DashboardNavigation from "@/components/DashboardNavigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { useToast } from "@/hooks/use-toast";
import { Plus, Users, Clock, CheckCircle, AlertCircle } from "lucide-react";

/**
 * Onboarding Dashboard Data Flow
 * 
 * ```mermaid
 * graph TD
 *     A[User] -->|Visits /onboarding-dashboard| B[OnboardingDashboard Component]
 *     B -->|useEffect| C[checkAuthAndLoad]
 *     C -->|Auth Check| D[supabase.auth.getSession]
 *     
 *     D -->|Authenticated| E[loadOnboardings]
 *     E -->|Query| F[client_onboardings Table]
 *     F -->|Order by created_at| G[setOnboardings State]
 *     
 *     G -->|Calculate Stats| H[Total, In Progress, Completed, Overdue]
 *     H -->|Update| I[Stats Cards UI]
 *     
 *     J[Create Onboarding Button] -->|Navigate| K[Onboarding Creation Modal]
 *     K -->|Select Template| L[onboarding_templates Table]
 *     L -->|Load Template| M[Template Tasks]
 *     
 *     M -->|Submit| N[Insert Onboarding]
 *     N -->|Store| F
 *     N -->|Copy Tasks| O[client_onboarding_tasks Table]
 *     
 *     P[View Onboarding] -->|Click| Q[Onboarding Detail Page]
 *     Q -->|Load Tasks| O
 *     O -->|Display| R[Task List with Status]
 *     
 *     R -->|Update Task| S[Change Status/Complete]
 *     S -->|Update| O
 *     S -->|Recalculate| T[completion_percentage]
 *     T -->|Update| F
 *     
 *     U[Upload Document] -->|Task Action| V[File Upload]
 *     V -->|Store Reference| W[uploaded_documents in Task]
 *     
 *     X[Assign Task] -->|Select User| Y[Update assigned_to]
 *     Y -->|Notify| Z[User Notification]
 *     
 *     AA[Overdue Check] -->|Compare Dates| AB[target_completion_date]
 *     AB -->|Flag Overdue| AC[stats.overdue]
 *     
 *     AD[Progress Tracking] -->|Real-time| AE[Progress Bars]
 *     AE -->|Visual Feedback| AF[Color-coded Status]
 *     
 *     style A fill:#e1f5ff
 *     style F fill:#e6f7ff
 *     style L fill:#e6f7ff
 *     style O fill:#e6f7ff
 * ```
 */

interface ClientOnboarding {
  id: string;
  client_name: string;
  status: string;
  completion_percentage: number;
  start_date: string | null;
  target_completion_date: string | null;
  created_at: string;
}

export default function OnboardingDashboard() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [onboardings, setOnboardings] = useState<ClientOnboarding[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    inProgress: 0,
    completed: 0,
    overdue: 0
  });

  useEffect(() => {
    checkAuthAndLoad();
  }, []);

  const checkAuthAndLoad = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      navigate('/auth');
      return;
    }
    await loadOnboardings();
  };

  const loadOnboardings = async () => {
    try {
      const { data, error } = await supabase
        .from('client_onboardings')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;

      setOnboardings(data || []);
      
      // Calculate stats
      const total = data?.length || 0;
      const inProgress = data?.filter(o => o.status === 'in_progress').length || 0;
      const completed = data?.filter(o => o.status === 'completed').length || 0;
      const overdue = data?.filter(o => {
        if (!o.target_completion_date || o.status === 'completed') return false;
        return new Date(o.target_completion_date) < new Date();
      }).length || 0;

      setStats({ total, inProgress, completed, overdue });
    } catch (error) {
      console.error('Error loading onboardings:', error);
      toast({
        title: "Error",
        description: "Failed to load client onboardings",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      not_started: "secondary",
      in_progress: "default",
      on_hold: "destructive",
      completed: "default",
      cancelled: "secondary"
    };
    return colors[status] || "secondary";
  };

  const getStatusIcon = (status: string) => {
    if (status === 'completed') return <CheckCircle className="h-4 w-4" />;
    if (status === 'on_hold') return <AlertCircle className="h-4 w-4" />;
    return <Clock className="h-4 w-4" />;
  };

  return (
    <div className="min-h-screen bg-background">
      
      <main className="container mx-auto px-4 pb-8" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>
        <DashboardNavigation 
          title="Client Onboarding"
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
          ]}
        />
        
        <div className="flex justify-end gap-2 mb-6">
          <Button onClick={() => navigate('/onboarding/templates')}>
            <Users className="mr-2 h-4 w-4" />
            Templates
          </Button>
          <Button onClick={() => navigate('/onboarding/new')}>
            <Plus className="mr-2 h-4 w-4" />
            New Onboarding
          </Button>
        </div>

        <div className="mb-6">
          <h1 className="text-4xl font-bold mb-2">Client Onboarding</h1>
          <p className="text-muted-foreground">Manage and track MSP customer onboarding processes</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Clients</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.inProgress}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Completed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Overdue</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.overdue}</div>
            </CardContent>
          </Card>
        </div>

        {/* Onboardings List */}
        {isLoading ? (
          <Card>
            <CardContent className="py-8 text-center">
              Loading onboardings...
            </CardContent>
          </Card>
        ) : onboardings.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Users className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No client onboardings yet</h3>
              <p className="text-muted-foreground">Use the "New Onboarding" button above to start onboarding your first client</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {onboardings.map((onboarding) => (
              <Card 
                key={onboarding.id}
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => navigate(`/onboarding/${onboarding.id}`)}
              >
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {onboarding.client_name}
                        {getStatusIcon(onboarding.status)}
                      </CardTitle>
                      <CardDescription className="mt-1">
                        Started {new Date(onboarding.created_at).toLocaleDateString()}
                        {onboarding.target_completion_date && (
                          <> • Target: {new Date(onboarding.target_completion_date).toLocaleDateString()}</>
                        )}
                      </CardDescription>
                    </div>
                    <Badge variant={getStatusColor(onboarding.status) as any}>
                      {onboarding.status.replace('_', ' ')}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Progress</span>
                      <span className="font-medium">{onboarding.completion_percentage}%</span>
                    </div>
                    <Progress value={onboarding.completion_percentage} />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
