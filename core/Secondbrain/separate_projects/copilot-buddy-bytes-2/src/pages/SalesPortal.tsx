import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  LogOut, TrendingUp, Users, DollarSign, Target, 
  BarChart, Calendar, FileText, CheckCircle, Clock, Phone
} from "lucide-react";
import { useDemoMode } from "@/hooks/useDemoMode";
import { DepartmentAIAssistant } from "@/components/DepartmentAIAssistant";

import { toast } from "sonner";

const SalesPortal = () => {
  const navigate = useNavigate();
  const isPreviewMode = useDemoMode();
  const [isLoading, setIsLoading] = useState(true);
  const [userProfile, setUserProfile] = useState<any>(null);
  const [myStats, setMyStats] = useState({
    activeDeals: 12,
    monthlyRevenue: 145000,
    quota: 200000,
    quotaProgress: 72.5,
    closedDeals: 8,
    activitiesThisWeek: 24
  });

  useEffect(() => {
    checkAccess();
  }, []);

  const checkAccess = async () => {
    if (isPreviewMode) {
      setUserProfile({ full_name: "Sales Rep", department: "sales" });
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
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <TrendingUp className="h-8 w-8 text-primary" />
              Sales Portal
            </h1>
            <p className="text-muted-foreground mt-2">
              Manage your pipeline and close more deals
            </p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">{userProfile?.full_name}</span>
            {isPreviewMode && <Badge variant="outline">Preview Mode</Badge>}
            <Button onClick={handleSignOut} variant="outline" size="sm">
              <LogOut className="h-4 w-4 mr-2" />
              {isPreviewMode ? "Back to Demos" : "Sign Out"}
            </Button>
          </div>
        </div>

        {/* My Performance Metrics */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Deals</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{myStats.activeDeals}</div>
              <p className="text-xs text-muted-foreground">In your pipeline</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${(myStats.monthlyRevenue / 1000).toFixed(0)}K</div>
              <p className="text-xs text-success">+18% from last month</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Quota Progress</CardTitle>
              <BarChart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{myStats.quotaProgress}%</div>
              <Progress value={myStats.quotaProgress} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Closed This Month</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{myStats.closedDeals}</div>
              <p className="text-xs text-muted-foreground">{myStats.activitiesThisWeek} activities this week</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="pipeline" className="space-y-6">
          <TabsList>
            <TabsTrigger value="pipeline">My Pipeline</TabsTrigger>
            <TabsTrigger value="activities">Activities</TabsTrigger>
            <TabsTrigger value="customers">Customers</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
            <TabsTrigger value="assistant">AI Assistant</TabsTrigger>
          </TabsList>

          <TabsContent value="pipeline" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>My Active Deals</CardTitle>
                <CardDescription>Opportunities in your sales pipeline</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Deal 1 */}
                  <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 cursor-pointer">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold">Enterprise Corp - Network Upgrade</h4>
                        <Badge>Negotiation</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">Contact: John Smith • Last activity: 2 days ago</p>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-lg">$120,000</div>
                      <p className="text-xs text-muted-foreground">Close date: Dec 15</p>
                    </div>
                  </div>

                  {/* Deal 2 */}
                  <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 cursor-pointer">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold">Tech Solutions Inc - Security Systems</h4>
                        <Badge variant="secondary">Proposal</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">Contact: Sarah Johnson • Last activity: Today</p>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-lg">$95,000</div>
                      <p className="text-xs text-muted-foreground">Close date: Dec 20</p>
                    </div>
                  </div>

                  {/* Deal 3 */}
                  <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 cursor-pointer">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold">Global Services Ltd - Phone System</h4>
                        <Badge variant="outline">Qualification</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">Contact: Mike Davis • Last activity: Yesterday</p>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-lg">$78,000</div>
                      <p className="text-xs text-muted-foreground">Close date: Jan 10</p>
                    </div>
                  </div>
                </div>

                <Button className="w-full mt-4" variant="outline" onClick={() => navigate('/workflow/deals?department=sales')}>
                  View All Deals
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="activities" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activities</CardTitle>
                <CardDescription>Your sales activities and follow-ups</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex gap-4">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                        <Phone className="h-5 w-5 text-primary" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">Call with Enterprise Corp</p>
                        <Badge variant="outline">Completed</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">Discussed network requirements and pricing</p>
                      <p className="text-xs text-muted-foreground mt-1">Today at 2:30 PM</p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-secondary/10 flex items-center justify-center">
                        <FileText className="h-5 w-5 text-secondary" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">Sent proposal to Tech Solutions</p>
                        <Badge variant="outline">Sent</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">Security camera system proposal with 3 tier options</p>
                      <p className="text-xs text-muted-foreground mt-1">Today at 10:00 AM</p>
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <div className="flex-shrink-0">
                      <div className="h-10 w-10 rounded-full bg-accent flex items-center justify-center">
                        <Calendar className="h-5 w-5" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">Demo scheduled with Modern Office</p>
                        <Badge variant="secondary">Upcoming</Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">Product demo for IT package</p>
                      <p className="text-xs text-muted-foreground mt-1">Tomorrow at 3:00 PM</p>
                    </div>
                  </div>
                </div>

                <Button className="w-full mt-4" variant="outline">
                  View All Activities
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="customers" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>My Customers</CardTitle>
                <CardDescription>Active customer accounts you manage</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="p-3 border rounded-lg hover:bg-accent/50 cursor-pointer" onClick={() => navigate('/workflow/customers?department=sales')}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Enterprise Corp</p>
                        <p className="text-sm text-muted-foreground">Technology • 150 employees</p>
                      </div>
                      <Badge>Active</Badge>
                    </div>
                  </div>

                  <div className="p-3 border rounded-lg hover:bg-accent/50 cursor-pointer" onClick={() => navigate('/workflow/customers?department=sales')}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Retail Partners LLC</p>
                        <p className="text-sm text-muted-foreground">Retail • 85 employees</p>
                      </div>
                      <Badge>Active</Badge>
                    </div>
                  </div>

                  <div className="p-3 border rounded-lg hover:bg-accent/50 cursor-pointer" onClick={() => navigate('/workflow/customers?department=sales')}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">Manufacturing Pro Inc</p>
                        <p className="text-sm text-muted-foreground">Manufacturing • 200 employees</p>
                      </div>
                      <Badge>Active</Badge>
                    </div>
                  </div>
                </div>

                <Button className="w-full mt-4" variant="outline" onClick={() => navigate('/workflow/customers?department=sales')}>
                  View All Customers
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="reports" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/analytics?department=sales')}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart className="h-5 w-5" />
                    Sales Analytics
                  </CardTitle>
                  <CardDescription>View detailed sales performance metrics</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full">Open Analytics</Button>
                </CardContent>
              </Card>

              <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/workflow/performance-reports?department=sales')}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Performance Reports
                  </CardTitle>
                  <CardDescription>Access your sales performance reports</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full">View Reports</Button>
                </CardContent>
              </Card>

              <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/workflow/pipeline?department=sales')}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    Pipeline Management
                  </CardTitle>
                  <CardDescription>Manage your sales pipeline</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full">Open Pipeline</Button>
                </CardContent>
              </Card>

              <Card className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => navigate('/dashboard/sales')}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Sales Dashboard
                  </CardTitle>
                  <CardDescription>View team-wide sales dashboard</CardDescription>
                </CardHeader>
                <CardContent>
                  <Button variant="outline" className="w-full">Open Dashboard</Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="assistant" className="space-y-4">
            <DepartmentAIAssistant 
              department="sales" 
              departmentLabel="Sales" 
            />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default SalesPortal;
