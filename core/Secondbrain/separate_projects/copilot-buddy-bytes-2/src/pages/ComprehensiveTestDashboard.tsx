import { useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { 
  Play, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Database, 
  Shield,
  Zap,
  Activity,
  GitBranch,
  ArrowRight
} from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function ComprehensiveTestDashboard() {
  const { toast } = useToast();
  const [isGenerating, setIsGenerating] = useState(false);
  const [isFuzzing, setIsFuzzing] = useState(false);
  const [isTracing, setIsTracing] = useState(false);
  const [testDataResult, setTestDataResult] = useState<any>(null);
  const [fuzzResult, setFuzzResult] = useState<any>(null);
  const [flowTrace, setFlowTrace] = useState<any>(null);

  const generateTestData = async () => {
    setIsGenerating(true);
    setTestDataResult(null);

    try {
      const { data, error } = await supabase.functions.invoke('comprehensive-test-data-generator', {});
      if (error) throw error;

      setTestDataResult(data);
      toast({
        title: "Success",
        description: `Generated ${data.summary.total_records_created} test records`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate test data",
        variant: "destructive"
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const runFuzzTests = async () => {
    setIsFuzzing(true);
    setFuzzResult(null);

    try {
      const { data, error } = await supabase.functions.invoke('input-fuzzer', {});
      if (error) throw error;

      setFuzzResult(data);
      toast({
        title: data.summary.vulnerabilities_found === 0 ? "All Tests Passed" : "Vulnerabilities Found",
        description: `${data.summary.passed}/${data.summary.total_tests} tests passed`,
        variant: data.summary.vulnerabilities_found > 0 ? "destructive" : "default"
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to run fuzz tests",
        variant: "destructive"
      });
    } finally {
      setIsFuzzing(false);
    }
  };

  const traceFlow = async (flowType: string) => {
    setIsTracing(true);
    setFlowTrace(null);

    try {
      const { data, error } = await supabase.functions.invoke('database-flow-logger', {
        body: { action: `trace_${flowType}` }
      });
      if (error) throw error;

      setFlowTrace(data);
      toast({
        title: "Flow Traced",
        description: `Traced ${data.summary.total_operations} operations`,
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to trace flow",
        variant: "destructive"
      });
    } finally {
      setIsTracing(false);
    }
  };

  const runAllTests = async () => {
    await generateTestData();
    await runFuzzTests();
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 pt-56 pb-8">
        <DashboardNavigation 
          title="Comprehensive Testing Dashboard"
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
        
        <div className="mb-8">
          <p className="text-muted-foreground">
            Generate test data, run fuzz tests, and validate system security
          </p>
        </div>

        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="results">Test Results</TabsTrigger>
            <TabsTrigger value="flows">Flow Tracing</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Play className="h-5 w-5" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="flex gap-4">
                <Button onClick={runAllTests} disabled={isGenerating || isFuzzing} size="lg" className="flex-1">
                  <Zap className="mr-2 h-4 w-4" />
                  {(isGenerating || isFuzzing) ? "Running..." : "Run All Tests"}
                </Button>
                <Button onClick={generateTestData} disabled={isGenerating} variant="outline" size="lg" className="flex-1">
                  <Database className="mr-2 h-4 w-4" />
                  {isGenerating ? "Generating..." : "Generate Data"}
                </Button>
                <Button onClick={runFuzzTests} disabled={isFuzzing} variant="outline" size="lg" className="flex-1">
                  <Shield className="mr-2 h-4 w-4" />
                  {isFuzzing ? "Fuzzing..." : "Fuzz Tests"}
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Testing Coverage
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Badge variant="outline">✓ Knowledge Base</Badge>
                    <Badge variant="outline">✓ AI Systems</Badge>
                    <Badge variant="outline">✓ Security & Compliance</Badge>
                  </div>
                  <div className="space-y-2">
                    <Badge variant="outline">✓ Workflow Automation</Badge>
                    <Badge variant="outline">✓ MCP Servers</Badge>
                    <Badge variant="outline">✓ Client Onboarding</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="results" className="space-y-6">
            {testDataResult && (
              <Card>
                <CardHeader>
                  <CardTitle>Test Data Results</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-4 gap-4">
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground">Components</p>
                      <p className="text-2xl font-bold">{testDataResult.summary.total_components}</p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground">Records</p>
                      <p className="text-2xl font-bold text-green-600">{testDataResult.summary.total_records_created}</p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground">Errors</p>
                      <p className="text-2xl font-bold text-red-600">{testDataResult.summary.total_errors}</p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground">Duration</p>
                      <p className="text-2xl font-bold">{testDataResult.summary.total_duration_ms}ms</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {fuzzResult && (
              <Card>
                <CardHeader>
                  <CardTitle>Security Fuzz Results</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-4 gap-4">
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground">Total Tests</p>
                      <p className="text-2xl font-bold">{fuzzResult.summary.total_tests}</p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground">Passed</p>
                      <p className="text-2xl font-bold text-green-600">{fuzzResult.summary.passed}</p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground">Failed</p>
                      <p className="text-2xl font-bold text-yellow-600">{fuzzResult.summary.failed}</p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg">
                      <p className="text-sm text-muted-foreground">Vulnerabilities</p>
                      <p className="text-2xl font-bold text-red-600">{fuzzResult.summary.vulnerabilities_found}</p>
                    </div>
                  </div>
                  <Progress value={(fuzzResult.summary.passed / fuzzResult.summary.total_tests) * 100} />
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="flows" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GitBranch className="h-5 w-5" />
                  Database Flow Tracing
                </CardTitle>
                <CardDescription>Trace data flows through the database</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-4">
                  <Button onClick={() => traceFlow('workflow')} disabled={isTracing} variant="outline">
                    Trace Workflow Flow
                  </Button>
                  <Button onClick={() => traceFlow('compliance')} disabled={isTracing} variant="outline">
                    Trace Compliance Flow
                  </Button>
                  <Button onClick={() => traceFlow('knowledge')} disabled={isTracing} variant="outline">
                    Trace Knowledge Flow
                  </Button>
                </div>

                {flowTrace && (
                  <div className="space-y-4 mt-6">
                    <div className="flex items-center gap-4">
                      <Badge>{flowTrace.flow}</Badge>
                      <span className="text-sm text-muted-foreground">
                        {flowTrace.summary.total_operations} operations across {flowTrace.summary.tables_affected.length} tables
                      </span>
                    </div>

                    <div className="space-y-2">
                      {flowTrace.steps.map((step: any, index: number) => (
                        <div key={index} className="flex items-center gap-3 p-3 bg-muted rounded">
                          <ArrowRight className="h-4 w-4 text-muted-foreground" />
                          <Badge variant="outline">{step.operation}</Badge>
                          <span className="font-medium">{step.table}</span>
                          <span className="text-sm text-muted-foreground">
                            {step.record_count} record(s)
                          </span>
                          {step.related_tables && (
                            <span className="text-xs text-muted-foreground">
                              → {step.related_tables.join(', ')}
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
