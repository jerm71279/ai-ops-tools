import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Shield, Server, Users, Briefcase, DollarSign, TrendingUp, Settings, Info } from "lucide-react";

const DemoSelector = () => {
  const navigate = useNavigate();

  const departments = [
    {
      id: "admin",
      name: "Admin Dashboard",
      description: "Manage customers, MCP servers, and system configuration",
      icon: Settings,
      route: "/admin",
      color: "text-purple-600"
    },
    {
      id: "compliance",
      name: "Compliance & GRC",
      description: "Framework coverage, controls monitoring, evidence management",
      icon: Shield,
      route: "/dashboard/compliance",
      color: "text-blue-600"
    },
    {
      id: "it",
      name: "IT & Security",
      description: "System integrations, MCP servers, anomaly detection",
      icon: Server,
      route: "/dashboard/it",
      color: "text-green-600"
    },
    {
      id: "hr",
      name: "Human Resources",
      description: "Employee management, onboarding workflows, policy compliance",
      icon: Users,
      route: "/dashboard/hr",
      color: "text-orange-600"
    },
    {
      id: "operations",
      name: "Operations",
      description: "Process automation, workflow efficiency, bottleneck detection",
      icon: Briefcase,
      route: "/dashboard/operations",
      color: "text-indigo-600"
    },
    {
      id: "finance",
      name: "Finance",
      description: "Financial controls, audit trails, expense tracking",
      icon: DollarSign,
      route: "/dashboard/finance",
      color: "text-emerald-600"
    },
    {
      id: "sales",
      name: "Sales",
      description: "Customer pipeline, revenue tracking, opportunity management",
      icon: TrendingUp,
      route: "/dashboard/sales",
      color: "text-pink-600"
    },
    {
      id: "executive",
      name: "Executive Leadership",
      description: "High-level metrics, strategic insights, cross-department analytics",
      icon: TrendingUp,
      route: "/dashboard/executive",
      color: "text-red-600"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto space-y-8">
          <Alert className="bg-primary/5 border-primary/20">
            <Info className="h-4 w-4" />
            <AlertDescription>
              <strong>Testing Environment:</strong> All dashboards are in preview mode. You can explore each department's interface, features, and AI assistants without authentication. Click "View Demos" in the navigation to return here anytime.
            </AlertDescription>
          </Alert>

          <div className="text-center space-y-4">
            <h1 className="text-4xl font-bold">Department Dashboard Demo</h1>
            <p className="text-xl text-muted-foreground">
              Test each department's customized interface and AI assistant
            </p>
            <div className="flex gap-4 justify-center">
              <Button onClick={() => navigate("/")} variant="outline">
                Back to Marketing Site
              </Button>
              <Button onClick={() => navigate("/auth")} variant="default">
                Sign Up / Login
              </Button>
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {departments.map((dept) => {
              const Icon = dept.icon;
              return (
                <Card key={dept.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div className={`p-3 rounded-lg bg-primary/10`}>
                        <Icon className={`h-6 w-6 ${dept.color}`} />
                      </div>
                      <div>
                        <CardTitle className="text-lg">{dept.name}</CardTitle>
                      </div>
                    </div>
                    <CardDescription className="mt-2">
                      {dept.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                  <Button 
                    onClick={(e) => {
                      e.preventDefault();
                      navigate(`${dept.route}?preview=true`);
                    }} 
                    className="w-full"
                    variant="outline"
                  >
                    View Dashboard
                  </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <Card className="bg-primary/5 border-primary/20">
            <CardHeader>
              <CardTitle>Testing Instructions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <h3 className="font-semibold">To Test Department Dashboards:</h3>
                <ol className="list-decimal list-inside space-y-1 text-sm text-muted-foreground">
                  <li>Sign up with a test account and select your department</li>
                  <li>You'll be automatically redirected to your department's dashboard</li>
                  <li>Explore the AI assistant, metrics, and department-specific features</li>
                  <li>Sign out and create another account to test different departments</li>
                </ol>
              </div>
              <div className="space-y-2">
                <h3 className="font-semibold">Admin Dashboard Access:</h3>
                <p className="text-sm text-muted-foreground">
                  Admin access requires a database entry in the user_roles table. After signing up, 
                  you'll need to manually add an admin role for your user in the backend.
                </p>
              </div>
              <div className="space-y-2">
                <h3 className="font-semibold">Key Features to Test:</h3>
                <ul className="list-disc list-inside space-y-1 text-sm text-muted-foreground">
                  <li>Department-specific metrics and KPIs</li>
                  <li>AI assistant with department context</li>
                  <li>Real-time data from database tables</li>
                  <li>MCP server integration status</li>
                  <li>Role-based access control</li>
                </ul>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DemoSelector;
