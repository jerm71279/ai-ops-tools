import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, Shield, FileText, CheckCircle2 } from "lucide-react";
import { toast } from "sonner";

interface Control {
  id: string;
  framework_id: string;
  control_id: string;
  control_name: string;
  description: string;
  category: string;
  automation_level: string;
  required_evidence: string[];
}

interface Framework {
  id: string;
  framework_name: string;
  framework_code: string;
}

interface EvidenceFile {
  id: string;
  file_name: string;
  control_id: string;
  uploaded_at: string;
  uploaded_by: string;
}

export default function ComplianceControlDetail() {
  const { frameworkId, controlId } = useParams();
  const navigate = useNavigate();
  const [control, setControl] = useState<Control | null>(null);
  const [framework, setFramework] = useState<Framework | null>(null);
  const [evidenceFiles, setEvidenceFiles] = useState<EvidenceFile[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadControlDetails();
  }, [frameworkId, controlId]);

  const loadControlDetails = async () => {
    setIsLoading(true);
    try {
      // Load control details
      const { data: controlData, error: controlError } = await supabase
        .from('compliance_controls')
        .select('*')
        .eq('id', controlId)
        .eq('framework_id', frameworkId)
        .single();

      if (controlError) throw controlError;
      setControl(controlData);

      // Load framework details
      const { data: frameworkData, error: frameworkError } = await supabase
        .from('compliance_frameworks')
        .select('id, framework_name, framework_code')
        .eq('id', frameworkId)
        .single();

      if (frameworkError) throw frameworkError;
      setFramework(frameworkData);

      // Load evidence files for this control
      const { data: evidenceData, error: evidenceError } = await supabase
        .from('evidence_files')
        .select('*')
        .eq('framework_id', frameworkId)
        .eq('control_id', controlData.control_id)
        .order('uploaded_at', { ascending: false });

      if (evidenceError) throw evidenceError;
      setEvidenceFiles(evidenceData || []);
    } catch (error) {
      console.error('Error loading control details:', error);
      toast.error('Failed to load control details');
    } finally {
      setIsLoading(false);
    }
  };

  const getAutomationColor = (level: string) => {
    switch (level) {
      case 'automated': return 'default';
      case 'semi-automated': return 'secondary';
      case 'manual': return 'outline';
      default: return 'outline';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 pt-56 pb-8">
          <p className="text-center text-muted-foreground">Loading control details...</p>
        </main>
      </div>
    );
  }

  if (!control || !framework) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Card>
            <CardContent className="py-12 text-center">
              <Shield className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">Control Not Found</h3>
              <p className="text-muted-foreground mb-4">
                The requested control could not be found.
              </p>
              <Button onClick={() => navigate(-1)}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Go Back
              </Button>
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 py-8">
        <DashboardNavigation 
          title="Control Detail"
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
        
        <div className="flex justify-between items-center mb-6">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline">{framework.framework_code}</Badge>
              <Badge variant={getAutomationColor(control.automation_level)}>
                {control.automation_level}
              </Badge>
            </div>
            <h1 className="text-4xl font-bold mb-2">
              {control.control_id}: {control.control_name}
            </h1>
            <p className="text-muted-foreground">{framework.framework_name}</p>
          </div>
          <Button variant="outline" onClick={() => navigate(`/compliance/frameworks/${frameworkId}`)}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Framework
          </Button>
        </div>

        <div className="grid gap-6">
          {/* Control Details */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Control Details
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Description</h3>
                <p className="text-muted-foreground">{control.description || 'No description available'}</p>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Category</h3>
                <Badge>{control.category}</Badge>
              </div>

              <div>
                <h3 className="font-semibold mb-2">Automation Level</h3>
                <Badge variant={getAutomationColor(control.automation_level)}>
                  {control.automation_level}
                </Badge>
              </div>

              {control.required_evidence && control.required_evidence.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Required Evidence</h3>
                  <ul className="list-disc list-inside space-y-1">
                    {control.required_evidence.map((evidence, idx) => (
                      <li key={idx} className="text-muted-foreground">{evidence}</li>
                    ))}
                  </ul>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Evidence Files */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Evidence Files ({evidenceFiles.length})
                </div>
                <Button 
                  size="sm"
                  onClick={() => navigate('/compliance/evidence/upload')}
                >
                  Upload Evidence
                </Button>
              </CardTitle>
              <CardDescription>
                Supporting documentation and evidence for this control
              </CardDescription>
            </CardHeader>
            <CardContent>
              {evidenceFiles.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No evidence files uploaded yet</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {evidenceFiles.map((file) => (
                    <div 
                      key={file.id}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <CheckCircle2 className="h-5 w-5 text-primary" />
                        <div>
                          <p className="font-medium">{file.file_name}</p>
                          <p className="text-sm text-muted-foreground">
                            Uploaded {new Date(file.uploaded_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                      <Badge variant="outline">Control: {file.control_id}</Badge>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Implementation Status */}
          <Card>
            <CardHeader>
              <CardTitle>Implementation Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-3xl font-bold text-primary">{evidenceFiles.length}</div>
                  <div className="text-sm text-muted-foreground mt-1">Evidence Files</div>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-3xl font-bold text-primary">
                    {control.required_evidence?.length || 0}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">Required Evidence</div>
                </div>
                <div className="text-center p-4 bg-muted rounded-lg">
                  <div className="text-3xl font-bold text-primary">
                    {evidenceFiles.length >= (control.required_evidence?.length || 0) ? '100%' : 
                     Math.round((evidenceFiles.length / (control.required_evidence?.length || 1)) * 100) + '%'}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">Compliance</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
