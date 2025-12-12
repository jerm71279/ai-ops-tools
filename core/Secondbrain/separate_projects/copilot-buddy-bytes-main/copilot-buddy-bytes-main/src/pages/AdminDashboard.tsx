import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { LogOut, Users, ChevronDown, Server, TestTube } from "lucide-react";
import MCPServerStatus from "@/components/MCPServerStatus";
import { MCPServerConfig } from "@/components/MCPServerConfig";
import { AIMCPGenerator } from "@/components/AIMCPGenerator";
import MCPExecutionLogs from "@/components/MCPExecutionLogs";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useDemoMode } from "@/hooks/useDemoMode";


import { DashboardSettingsMenu } from "@/components/DashboardSettingsMenu";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

/**
 * Admin Dashboard Data Flow
 * 
 * ```mermaid
 * graph TD
 *     A[User] -->|Visits /admin| B[AdminDashboard Component]
 *     B -->|useEffect| C[checkAdminAccess]
 *     C -->|Auth Check| D[supabase.auth.getSession]
 *     
 *     D -->|Check Admin Role| E[user_roles Table]
 *     E -->|Query roles| F[roles Table JOIN]
 *     F -->|Verify Admin/Super Admin| G{Has Admin?}
 *     
 *     G -->|No| H[Redirect to /]
 *     G -->|Yes| I[Get customer_id]
 *     
 *     I -->|Query| J[user_profiles Table]
 *     J -->|Set State| K[userCustomerId]
 *     
 *     C -->|Load Customers| L[fetchCustomers]
 *     L -->|Query| M[customers Table]
 *     M -->|Return Data| N[setCustomers State]
 *     
 *     N -->|Render| O[Customer Table UI]
 *     O -->|Edit Action| P[Navigate to Customer Detail]
 *     
 *     Q[MCP Server Tab] -->|Display| R[MCPServerStatus Component]
 *     R -->|Query| S[mcp_servers Table]
 *     
 *     T[AI MCP Generator] -->|Invoke| U[ai-mcp-generator Edge Function]
 *     U -->|Generate Config| V[AI Model Processing]
 *     V -->|Store| S
 *     
 *     W[Test Dashboard Tab] -->|Navigate| X[/test-dashboard]
 *     
 *     style A fill:#e1f5ff
 *     style U fill:#fff4e6
 *     style M fill:#e6f7ff
 *     style S fill:#e6f7ff
 *     style G fill:#ffe6e6
 * ```
 */

type Customer = {
  id: string;
  company_name: string;
  contact_name: string;
  email: string;
  phone: string | null;
  status: string;
  plan_type: string;
  created_at: string;
};

const AdminDashboard = () => {
  const navigate = useNavigate();
  const isPreviewMode = useDemoMode();
  const [isLoading, setIsLoading] = useState(true);
  const [isAdmin, setIsAdmin] = useState(false);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [userCustomerId, setUserCustomerId] = useState<string>("00000000-0000-0000-0000-000000000000");
  const [activeView, setActiveView] = useState<string | null>(null);

  useEffect(() => {
    checkAdminAccess();
  }, []);

  const checkAdminAccess = async () => {
    if (isPreviewMode) {
      setIsAdmin(true);
      // In preview mode, try to get a real customer ID from the database
      const { data: customers } = await supabase
        .from("customers")
        .select("id")
        .limit(1)
        .maybeSingle();
      
      if (customers?.id) {
        setUserCustomerId(customers.id);
      } else {
        // Generate a valid UUID for preview mode if no customers exist
        setUserCustomerId("00000000-0000-0000-0000-000000000000");
      }
      fetchCustomers();
      return;
    }

    const { data: { session } } = await supabase.auth.getSession();
    
    if (!session) {
      navigate("/auth");
      return;
    }

    // Check if user has admin role
    const { data: roles } = await supabase
      .from("user_roles")
      .select("role_id, roles(name)")
      .eq("user_id", session.user.id);

    let hasAdmin = roles?.some((ur: any) => ur.roles?.name === 'Super Admin' || ur.roles?.name === 'Admin');

    if (!hasAdmin) {
      const { data: rpcHasAdmin } = await supabase.rpc('has_role', {
        _user_id: session.user.id,
        _role: 'admin'
      });
      hasAdmin = !!rpcHasAdmin;
    }

    if (!hasAdmin) {
      toast.error("Access denied: Admin privileges required");
      navigate("/");
      return;
    }

    // Get user's customer_id
    const { data: profile } = await supabase
      .from("user_profiles")
      .select("customer_id")
      .eq("user_id", session.user.id)
      .maybeSingle();

    if (profile?.customer_id) {
      setUserCustomerId(profile.customer_id);
    }

    setIsAdmin(true);
    fetchCustomers();
  };

  const fetchCustomers = async () => {
    setIsLoading(true);
    const { data, error } = await supabase
      .from("customers")
      .select("*")
      .order("created_at", { ascending: false });

    if (error) {
      toast.error("Failed to load customers");
      console.error(error);
    } else {
      setCustomers(data || []);
    }
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

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive"> = {
      active: "default",
      trial: "secondary",
      inactive: "destructive",
    };
    return <Badge variant={variants[status] || "default"}>{status}</Badge>;
  };

  const getPlanBadge = (plan: string) => {
    return <Badge variant="outline">{plan}</Badge>;
  };

  if (!isAdmin) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 pb-8 space-y-8" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>
        
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <Users className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold">Admin Dashboard</h1>
            {isPreviewMode && <Badge variant="outline">Preview Mode</Badge>}
          </div>
          <DashboardSettingsMenu dashboardName="Admin" />
        </div>

        {/* Active View Content */}
        {activeView && (
          <Card className="mb-6">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>
                  {activeView === 'mcp-status' && 'MCP Server Status'}
                  {activeView === 'mcp-logs' && 'Execution Logs'}
                  {activeView === 'mcp-configure' && 'Configure New Server'}
                  {activeView === 'mcp-ai' && 'AI MCP Generator'}
                </CardTitle>
                <Button variant="ghost" size="sm" onClick={() => setActiveView(null)}>
                  Close
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {activeView === 'mcp-status' && <MCPServerStatus customerId={userCustomerId} />}
              {activeView === 'mcp-logs' && <MCPExecutionLogs customerId={userCustomerId} />}
              {activeView === 'mcp-configure' && <MCPServerConfig customerId={userCustomerId} />}
              {activeView === 'mcp-ai' && (
                <AIMCPGenerator 
                  customerId={userCustomerId}
                  department="admin"
                  onServersCreated={() => {
                    toast.success("MCP servers created successfully!");
                    setActiveView('mcp-status');
                  }}
                />
              )}
            </CardContent>
          </Card>
        )}
        
        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/admin/applications')}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="h-5 w-5" />
                Applications
              </CardTitle>
              <CardDescription>Manage system applications</CardDescription>
            </CardHeader>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/admin/products')}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="h-5 w-5" />
                Products
              </CardTitle>
              <CardDescription>Manage product offerings</CardDescription>
            </CardHeader>
          </Card>

          <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/admin/modules')}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="h-5 w-5" />
                Module Management
              </CardTitle>
              <CardDescription>Enable/disable portals and modules</CardDescription>
            </CardHeader>
          </Card>
        </div>
        
        <Card>
          <CardHeader>
            <CardTitle>Customer Management</CardTitle>
            <CardDescription>
              View and manage all customer accounts
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">Loading customers...</div>
            ) : customers.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No customers yet. They will appear here once they sign up.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Company</TableHead>
                      <TableHead>Contact</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Phone</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Plan</TableHead>
                      <TableHead>Joined</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {customers.map((customer) => (
                      <TableRow key={customer.id}>
                        <TableCell className="font-medium">
                          {customer.company_name}
                        </TableCell>
                        <TableCell>{customer.contact_name}</TableCell>
                        <TableCell>{customer.email}</TableCell>
                        <TableCell>{customer.phone || "—"}</TableCell>
                        <TableCell>{getStatusBadge(customer.status)}</TableCell>
                        <TableCell>{getPlanBadge(customer.plan_type)}</TableCell>
                        <TableCell>
                          {new Date(customer.created_at).toLocaleDateString()}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AdminDashboard;