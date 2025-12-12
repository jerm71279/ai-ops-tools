import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

import DashboardNavigation from "@/components/DashboardNavigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { Shield, FileCheck, AlertTriangle, TrendingUp, Plus } from "lucide-react";

interface Framework {
  id: string;
  framework_name: string;
  framework_code: string;
  description: string | null;
  industry: string;
}

interface EvidenceFile {
  id: string;
  file_name: string;
  framework_id: string | null;
  control_id: string | null;
  uploaded_at: string;
}

interface ComplianceReport {
  id: string;
  report_name: string;
  framework: string;
  status: string;
  generated_at: string;
  evidence_count: number;
}

export default function CompliancePortal() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [evidenceFiles, setEvidenceFiles] = useState<EvidenceFile[]>([]);
  const [reports, setReports] = useState<ComplianceReport[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({
    frameworks: 0,
    evidenceFiles: 0,
    reports: 0,
    complianceScore: 0
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
    await loadComplianceData();
  };

  const loadComplianceData = async () => {
    try {
      const [frameworksRes, evidenceRes, reportsRes] = await Promise.all([
        supabase.from('compliance_frameworks').select('*').eq('is_active', true),
        supabase.from('evidence_files').select('*'),
        supabase.from('compliance_reports').select('*').order('generated_at', { ascending: false }).limit(10)
      ]);

      if (frameworksRes.error) throw frameworksRes.error;
      if (evidenceRes.error) throw evidenceRes.error;
      if (reportsRes.error) throw reportsRes.error;

      setFrameworks(frameworksRes.data || []);
      setEvidenceFiles(evidenceRes.data || []);
      setReports(reportsRes.data || []);

      setStats({
        frameworks: frameworksRes.data?.length || 0,
        evidenceFiles: evidenceRes.data?.length || 0,
        reports: reportsRes.data?.length || 0,
        complianceScore: 85 // Calculate based on controls/evidence
      });
    } catch (error) {
      console.error('Error loading compliance data:', error);
      toast({
        title: "Error",
        description: "Failed to load compliance data",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      draft: "secondary",
      in_review: "default",
      approved: "default",
      published: "default"
    };
    return colors[status] || "secondary";
  };

  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      <main className="container mx-auto px-4 pb-8 pt-8" style={{ marginTop: 'var(--lanes-height, 0px)' }}>
        
        <div className="mb-6">
          <h1 className="text-4xl font-bold mb-2">Compliance Management</h1>
          <p className="text-muted-foreground">Track compliance frameworks and evidence collection</p>
        </div>

        <div className="flex flex-wrap items-center gap-3 mb-6 overflow-x-auto">
          <Button size="sm" onClick={() => navigate('/compliance/audit-reports')}>
            <FileCheck className="mr-2 h-4 w-4" />
            Generate Audit Report
          </Button>
          <Button size="sm" onClick={() => navigate('/compliance/evidence/upload')} variant="outline">
            <Plus className="mr-2 h-4 w-4" />
            Upload Evidence
          </Button>
        </div>

        <Tabs defaultValue="frameworks" className="space-y-4">
          <TabsList>
            <TabsTrigger value="frameworks">Frameworks</TabsTrigger>
            <TabsTrigger value="evidence">Evidence</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
          </TabsList>

          <TabsContent value="frameworks" className="space-y-4">
            {isLoading ? (
              <Card>
                <CardContent className="py-8 text-center">
                  Loading frameworks...
                </CardContent>
              </Card>
            ) : frameworks.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <Shield className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No frameworks configured</h3>
                  <p className="text-muted-foreground">Contact support to enable compliance frameworks</p>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Select Compliance Framework</CardTitle>
                  <CardDescription>Choose a framework to view details and manage compliance</CardDescription>
                </CardHeader>
                <CardContent>
                  <Select onValueChange={(value) => navigate(`/compliance/frameworks/${value}`)}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select a compliance framework..." />
                    </SelectTrigger>
                    <SelectContent>
                      {frameworks.map((framework) => (
                        <SelectItem key={framework.id} value={framework.id}>
                          {framework.framework_name} ({framework.framework_code})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="evidence" className="space-y-4">
            {evidenceFiles.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <FileCheck className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No evidence files uploaded</h3>
                  <p className="text-muted-foreground mb-4">Upload compliance evidence to get started</p>
                  <Button onClick={() => navigate('/compliance/evidence/upload')}>
                    <Plus className="mr-2 h-4 w-4" />
                    Upload Evidence
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-2">
                {evidenceFiles.slice(0, 10).map((file) => (
                  <Card key={file.id}>
                    <CardContent className="py-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium">{file.file_name}</p>
                          <p className="text-sm text-muted-foreground">
                            Uploaded {new Date(file.uploaded_at).toLocaleDateString()}
                          </p>
                        </div>
                        <Button variant="ghost" size="sm">View</Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="reports" className="space-y-4">
            {reports.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <AlertTriangle className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No compliance reports</h3>
                  <p className="text-muted-foreground">Generate your first compliance report</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-2">
                {reports.map((report) => (
                  <Card 
                    key={report.id}
                    className="cursor-pointer hover:shadow-md transition-shadow"
                    onClick={() => navigate(`/compliance/reports/${report.id}`)}
                  >
                    <CardContent className="py-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="font-medium">{report.report_name}</p>
                          <p className="text-sm text-muted-foreground">
                            {report.framework} • {new Date(report.generated_at).toLocaleDateString()} • {report.evidence_count} evidence files
                          </p>
                        </div>
                        <Badge variant={getStatusColor(report.status) as any}>
                          {report.status}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Active Frameworks
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.frameworks}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <FileCheck className="h-4 w-4" />
                Evidence Files
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.evidenceFiles}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Compliance Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.complianceScore}%</div>
              <Progress value={stats.complianceScore} className="mt-2" />
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <AlertTriangle className="h-4 w-4" />
                Reports
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.reports}</div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
