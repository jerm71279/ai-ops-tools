import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Shield, Activity, Clock, FileText, BookOpen, Workflow, BarChart3, Settings, ExternalLink, Brain, Zap, Calendar, MessagesSquare, ArrowLeft, AlertTriangle, Users, Database, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useNavigate, Link, useLocation } from "react-router-dom";
import EmployeeToolbar from "@/components/EmployeeToolbar";
import ExternalSystemsBar from "@/components/ExternalSystemsBar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Microsoft365Integration } from "@/components/Microsoft365Integration";
import { AppLauncher } from "@/components/AppLauncher";
import DashboardNavigation from "@/components/DashboardNavigation";
import AutomationSuggestions from "@/components/AutomationSuggestions";
import { RepetitiveTaskTester } from "@/components/RepetitiveTaskTester";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSub, DropdownMenuSubTrigger, DropdownMenuSubContent } from "@/components/ui/dropdown-menu";
import { ChevronDown } from "lucide-react";
import { GlobalSearch } from "@/components/GlobalSearch";

const Portal = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(true);
  const [customerData, setCustomerData] = useState<any>(null);
  const [userDepartment, setUserDepartment] = useState<string | null>(null);
  const [recentArticles, setRecentArticles] = useState<any[]>([]);
  const [recentWorkflows, setRecentWorkflows] = useState<any[]>([]);
  const [searchOpen, setSearchOpen] = useState(false);

  useEffect(() => {
    loadCustomerData();
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        setSearchOpen(true);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    // Handle scroll to dashboards section
    if (location.state?.scrollToDashboards) {
      setTimeout(() => {
        const dashboardsSection = document.getElementById('dashboards-section');
        dashboardsSection?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }, [location]);

  const loadCustomerData = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      // Get user profile (may not have customer_id yet)
      const { data: profile } = await supabase
        .from("user_profiles")
        .select("*")
        .eq("user_id", session.user.id)
        .maybeSingle();

      // If profile has customer_id, fetch customer data
      let customerInfo = null;
      if (profile?.customer_id) {
        const { data: customer } = await supabase
          .from("customers")
          .select("*")
          .eq("id", profile.customer_id)
          .maybeSingle();
        customerInfo = customer;
      }

      // Set combined data
      setCustomerData({
        ...profile,
        customers: customerInfo
      });
      
      // Set user department for app launcher
      setUserDepartment(profile?.department || null);

      // Load recent knowledge articles
      const { data: articles } = await supabase
        .from("knowledge_articles")
        .select("*")
        .eq("status", "published")
        .order("updated_at", { ascending: false })
        .limit(5);

      setRecentArticles(articles || []);

      // Load recent workflow executions (only if customer_id exists)
      if (profile?.customer_id) {
        const { data: workflows } = await supabase
          .from("workflow_executions")
          .select("*")
          .eq("customer_id", profile.customer_id)
          .order("started_at", { ascending: false })
          .limit(5);

        setRecentWorkflows(workflows || []);
      }
    } catch (error) {
      console.error("Error loading customer data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    navigate("/");
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Clock className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
          <p>Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  // Quick access tools
  const quickAccessTools = [
    { name: "Knowledge Base", icon: BookOpen, path: "/knowledge", description: "SOPs, guides, and documentation" },
    { name: "Workflows", icon: Workflow, path: "/workflow/automation", description: "Process automation and execution" },
    { name: "AI Assistant", icon: Brain, path: "/portal", description: "Get AI-powered help and insights" },
    { name: "Integrations", icon: Zap, path: "/integrations", description: "Connected systems and tools" },
    { name: "CMDB", icon: Database, path: "/cmdb", description: "Configuration items and assets" },
    { name: "Incidents & Auto-Remediation", icon: AlertTriangle, path: "/incidents", description: "Monitor and resolve incidents" },
    { name: "Client Portal", icon: Users, path: "/client-portal", description: "Support tickets and services" },
    { name: "Custom Reports", icon: FileText, path: "/reports/builder", description: "Build and schedule reports" },
  ];

  // Analytics/Dashboards - Secondary access
  const analyticsDashboards = [
    { name: "Operations", icon: BarChart3, path: "/dashboard/operations", description: "Workflow metrics and insights" },
    { name: "Compliance", icon: Shield, path: "/dashboard/compliance", description: "Compliance status and reports" },
    { name: "IT Systems", icon: Activity, path: "/dashboard/it", description: "System health and performance" },
    { name: "Executive", icon: BarChart3, path: "/dashboard/executive", description: "High-level business metrics" },
  ];

  return (
    <div className="min-h-screen bg-background" style={{ paddingTop: 'var(--lanes-height, 0px)' }}>
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="h-8 w-8 text-primary" />
              <div>
                <h1 className="text-2xl font-bold">
                  My Workspace
                </h1>
                <p className="text-sm text-muted-foreground">
                  {customerData?.customers?.company_name || 'OberaConnect'}
                </p>
              </div>
            </div>
              <div className="flex items-center gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => setSearchOpen(true)}
                  className="gap-2"
                >
                  <Search className="h-4 w-4" />
                  Search
                  <kbd className="ml-2 pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">
                    <span className="text-xs">⌘</span>K
                  </kbd>
                </Button>
                <Button variant="outline" onClick={handleSignOut}>
                  Sign Out
                </Button>
              </div>
          </div>
        </div>
      </header>

      {/* Employee System Toolbar */}
      <EmployeeToolbar />

      {/* External Systems Bar */}
      <ExternalSystemsBar />

      <div className="container mx-auto px-4 pb-8 pt-8">
        {/* Tools and Activities Dropdown */}
        <div className="flex items-center gap-3 mb-8">
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                Tools and Activities <ChevronDown className="ml-2 h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="start" className="w-80">
              <DropdownMenuSub>
                <DropdownMenuSubTrigger>
                  <Zap className="mr-2 h-4 w-4" />
                  Quick Access
                </DropdownMenuSubTrigger>
                <DropdownMenuSubContent>
                  {quickAccessTools.map((tool) => (
                    <DropdownMenuItem key={tool.name} asChild>
                      <Link to={tool.path} className="flex items-center gap-3 cursor-pointer">
                        <tool.icon className="h-4 w-4" />
                        <div className="flex-1">
                          <p className="font-medium">{tool.name}</p>
                          <p className="text-xs text-muted-foreground">{tool.description}</p>
                        </div>
                      </Link>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuSubContent>
              </DropdownMenuSub>
              
              <DropdownMenuSub>
                <DropdownMenuSubTrigger>
                  <Activity className="mr-2 h-4 w-4" />
                  Recent Activity
                </DropdownMenuSubTrigger>
                <DropdownMenuSubContent>
                  <DropdownMenuItem asChild>
                    <Link to="/knowledge" className="flex items-center gap-2 cursor-pointer">
                      <BookOpen className="h-4 w-4" />
                      <div className="flex-1">
                        <p className="font-medium">Recent Documentation</p>
                        <p className="text-xs text-muted-foreground">View all knowledge articles</p>
                      </div>
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/workflow/automation" className="flex items-center gap-2 cursor-pointer">
                      <Workflow className="h-4 w-4" />
                      <div className="flex-1">
                        <p className="font-medium">Recent Workflows</p>
                        <p className="text-xs text-muted-foreground">View workflow executions</p>
                      </div>
                    </Link>
                  </DropdownMenuItem>
                </DropdownMenuSubContent>
              </DropdownMenuSub>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="mb-8">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="apps">Applications</TabsTrigger>
            <TabsTrigger value="microsoft365">Microsoft 365</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            {/* Welcome Section */}
            <div className="mb-8">
              <h2 className="text-3xl font-bold mb-2">
                Welcome back, {customerData?.full_name || "User"}
              </h2>
              <p className="text-muted-foreground">
                Access your tools, knowledge, and insights all in one place
              </p>
            </div>

            {/* Task Detection Tester - For Validation */}
            <RepetitiveTaskTester />

            {/* Automation Suggestions */}
            <AutomationSuggestions />

            {/* Analytics & Insights - Dropdown */}
            <section id="dashboards-section">
              <div className="flex items-center gap-4 mb-6">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm">
                      View Dashboards <ChevronDown className="ml-2 h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="start" className="w-80">
                    {analyticsDashboards.map((dashboard) => (
                      <DropdownMenuItem key={dashboard.name} asChild>
                        <Link to={dashboard.path} className="flex items-center gap-3 cursor-pointer">
                          <dashboard.icon className="h-4 w-4" />
                          <div className="flex-1">
                            <p className="font-medium">{dashboard.name}</p>
                            <p className="text-xs text-muted-foreground">{dashboard.description}</p>
                          </div>
                        </Link>
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </section>
            </TabsContent>

            <TabsContent value="apps">
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold">My Applications</h2>
                  <p className="text-muted-foreground mt-1">
                    Access your work applications and services
                  </p>
                </div>
                <AppLauncher userDepartment={userDepartment} />
              </div>
            </TabsContent>

            <TabsContent value="microsoft365">
              <Microsoft365Integration />
            </TabsContent>
        </Tabs>
      </div>

      <GlobalSearch open={searchOpen} onOpenChange={setSearchOpen} />
    </div>
  );
};

export default Portal;
