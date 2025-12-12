import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { toast } from "sonner";
import { TrendingUp, Users, DollarSign, Target, ArrowUpRight, Calendar, AlertCircle, CheckCircle, Clock, ChevronDown, FileText, BarChart, Server } from "lucide-react";
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
 * Sales Dashboard Data Flow
 * 
 * ```mermaid
 * graph TD
 *     A[Sales User] -->|Visits /dashboard/sales| B[SalesDashboard Component]
 *     B -->|useEffect| C[checkAccess]
 *     C -->|Auth Check| D[supabase.auth.getSession]
 *     D -->|Get Profile| E[user_profiles Table]
 *     
 *     B -->|Fetch MCP Servers| F[fetchMcpServers]
 *     F -->|Query| G[mcp_servers Table]
 *     F -->|Filter: server_type=sales| H[Sales MCP Servers]
 *     H -->|Display| I[MCP Server Dropdown]
 *     
 *     J[Stats Display] -->|Static Data| K[Revenue: $1.25M]
 *     J -->|Static Data| L[Active Deals: 24]
 *     J -->|Static Data| M[Customers: 187]
 *     J -->|Static Data| N[Conversion: 32%]
 *     
 *     O[View Sales Portal] -->|Navigate| P[/sales-portal]
 *     P -->|Load| Q[Sales CRM Interface]
 *     
 *     R[Revio Integration] -->|API Call| S[revio-data Edge Function]
 *     S -->|Fetch| T[Revio API]
 *     T -->|Return| U[Customer & Revenue Data]
 *     
 *     V[Click Deal Card] -->|Navigate| W[Deal Detail Page]
 *     
 *     X[Pipeline View] -->|Filter| Y[Deal Stages]
 *     Y -->|Group by| Z[Stage Categories]
 *     
 *     AA[AI Assistant] -->|Invoke| AB[department-assistant Edge Function]
 *     AB -->|Context: Sales| AC[Sales Insights & Recommendations]
 *     
 *     AD[Top Performers] -->|Query| E
 *     AD -->|Calculate| AE[Sales Metrics by User]
 *     
 *     style A fill:#e1f5ff
 *     style S fill:#fff4e6
 *     style AB fill:#fff4e6
 *     style T fill:#ffe6e6
 *     style E fill:#e6f7ff
 *     style G fill:#e6f7ff
 * ```
 */

const SalesDashboard = () => {
  const navigate = useNavigate();
  const isPreviewMode = useDemoMode();
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [stats, setStats] = useState({
    totalRevenue: 1250000,
    activeDeals: 24,
    customerCount: 187,
    conversionRate: 32,
    monthlyGrowth: 18
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
      .eq("server_type", "sales")
      .eq("status", "active")
      .order("server_name");
    
    if (data) setMcpServers(data);
  };

  const checkAccess = async () => {
    if (isPreviewMode) {
      setUserProfile({ full_name: "Demo User", department: "sales" });
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

      <main className="container mx-auto px-4 pb-8" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>

        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Sales Dashboard</h1>
          <DashboardSettingsMenu dashboardName="Sales" />
        </div>
        
        
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-2">Sales Performance</h2>
          <p className="text-muted-foreground">
            Track revenue, pipeline, and customer metrics
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/revenue?metric=Total Revenue&department=sales`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${(stats.totalRevenue / 1000000).toFixed(2)}M</div>
              <p className="text-xs text-muted-foreground flex items-center gap-1">
                <ArrowUpRight className="h-3 w-3 text-green-600" />
                <span className="text-green-600">+{stats.monthlyGrowth}% from last month</span>
              </p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/deals?metric=Active Deals&department=sales`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Deals</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeDeals}</div>
              <p className="text-xs text-muted-foreground">
                In pipeline
              </p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/customers?metric=Total Customers&department=sales`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.customerCount}</div>
              <p className="text-xs text-muted-foreground">
                Active accounts
              </p>
            </CardContent>
          </Card>

          <Card 
            className="cursor-pointer hover:shadow-lg transition-shadow"
            onClick={() => navigate(`/workflow/conversion?metric=Conversion Rate&department=sales`)}
          >
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.conversionRate}%</div>
              <Progress value={stats.conversionRate} className="mt-2" />
            </CardContent>
          </Card>
        </div>

        {/* Sales Pipeline */}
        <div className="grid gap-6 md:grid-cols-2 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Sales Pipeline</CardTitle>
              <CardDescription>Active opportunities by stage</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Qualification</span>
                  <span className="font-medium">8 deals - $320K</span>
                </div>
                <Progress value={33} />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Proposal</span>
                  <span className="font-medium">6 deals - $450K</span>
                </div>
                <Progress value={25} />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Negotiation</span>
                  <span className="font-medium">5 deals - $280K</span>
                </div>
                <Progress value={21} />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Closing</span>
                  <span className="font-medium">5 deals - $200K</span>
                </div>
                <Progress value={21} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Top Opportunities</CardTitle>
              <CardDescription>Highest value deals in pipeline</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Enterprise Corp</p>
                    <p className="text-sm text-muted-foreground">Network Infrastructure</p>
                  </div>
                  <Badge variant="default">$120K</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Tech Solutions Inc</p>
                    <p className="text-sm text-muted-foreground">Security Cameras & IT</p>
                  </div>
                  <Badge variant="default">$95K</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Global Services Ltd</p>
                    <p className="text-sm text-muted-foreground">Phone System Install</p>
                  </div>
                  <Badge variant="default">$78K</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Modern Office Co</p>
                    <p className="text-sm text-muted-foreground">Complete IT Package</p>
                  </div>
                  <Badge variant="default">$65K</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity & Forecast */}
        <div className="grid gap-6 md:grid-cols-2 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>Latest sales interactions</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex gap-3">
                  <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div className="space-y-1">
                    <p className="text-sm font-medium">Demo scheduled - Enterprise Corp</p>
                    <p className="text-sm text-muted-foreground">Network infrastructure solution - Tomorrow 2:00 PM</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div className="space-y-1">
                    <p className="text-sm font-medium">Proposal sent - Tech Solutions</p>
                    <p className="text-sm text-muted-foreground">Security camera system - 2 hours ago</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div className="space-y-1">
                    <p className="text-sm font-medium">Deal closed - Retail Partners</p>
                    <p className="text-sm text-muted-foreground">Phone system installation - Today</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                  <div className="space-y-1">
                    <p className="text-sm font-medium">Follow-up call - Modern Office</p>
                    <p className="text-sm text-muted-foreground">Complete IT package discussion - Yesterday</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Quarterly Forecast</CardTitle>
              <CardDescription>Projected vs. actual performance</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Q1 Target: $1.5M</span>
                  <span className="font-medium text-green-600">$1.6M (107%)</span>
                </div>
                <Progress value={107} className="h-2" />
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Q2 Target: $1.8M</span>
                  <span className="font-medium">$1.25M (69%)</span>
                </div>
                <Progress value={69} className="h-2" />
              </div>
              <div className="mt-4 p-4 bg-muted rounded-lg">
                <p className="text-sm font-medium mb-2">Forecast Insights</p>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>• 5 deals likely to close this week ($450K)</li>
                  <li>• Q2 on track to meet 95% of target</li>
                  <li>• Network infrastructure deals trending up 25%</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Revio Customer Insights */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Revio Customer Insights</CardTitle>
            <CardDescription>Recent billing interactions and customer updates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {/* Summary Stats */}
              <div className="grid gap-4 md:grid-cols-3">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <span className="text-sm font-medium">Active Subscriptions</span>
                  </div>
                  <div className="text-2xl font-bold">142</div>
                  <p className="text-xs text-muted-foreground">+12 this month</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <Clock className="h-5 w-5 text-yellow-600" />
                    <span className="text-sm font-medium">Open Tickets</span>
                  </div>
                  <div className="text-2xl font-bold">8</div>
                  <p className="text-xs text-muted-foreground">Avg response: 2.4hrs</p>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    <span className="text-sm font-medium">Payment Issues</span>
                  </div>
                  <div className="text-2xl font-bold">3</div>
                  <p className="text-xs text-muted-foreground">Require attention</p>
                </div>
              </div>

              {/* Recent Customer Interactions */}
              <div>
                <h4 className="text-sm font-semibold mb-3">Recent Customer Interactions</h4>
                <div className="space-y-3">
                  <div className="flex items-start gap-3 p-3 border rounded-lg">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-medium text-sm">Enterprise Corp - Payment Received</p>
                        <Badge variant="outline" className="text-xs">Billing</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">Monthly subscription payment processed - $12,000</p>
                      <p className="text-xs text-muted-foreground mt-1">2 hours ago</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-3 border rounded-lg">
                    <Clock className="h-5 w-5 text-yellow-600 mt-0.5" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-medium text-sm">Tech Solutions Inc - Support Ticket</p>
                        <Badge variant="outline" className="text-xs">Support</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">Question about invoice details for recent upgrade</p>
                      <p className="text-xs text-muted-foreground mt-1">5 hours ago</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-3 border rounded-lg">
                    <AlertCircle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-medium text-sm">Global Services Ltd - Payment Failed</p>
                        <Badge variant="destructive" className="text-xs">Urgent</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">Credit card declined - subscription at risk</p>
                      <p className="text-xs text-muted-foreground mt-1">Yesterday</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3 p-3 border rounded-lg">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <p className="font-medium text-sm">Modern Office Co - Subscription Upgrade</p>
                        <Badge variant="outline" className="text-xs">Update</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">Upgraded from Standard to Premium plan - $8,500/mo</p>
                      <p className="text-xs text-muted-foreground mt-1">2 days ago</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        
        <DepartmentAIAssistant department="sales" departmentLabel="Sales" />
      </main>
    </div>
  );
};

export default SalesDashboard;
