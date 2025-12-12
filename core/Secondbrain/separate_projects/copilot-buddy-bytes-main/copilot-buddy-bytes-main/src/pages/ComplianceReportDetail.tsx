import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

import DashboardNavigation from "@/components/DashboardNavigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, FileText, Download, Calendar, Shield, CheckCircle, AlertCircle, XCircle } from "lucide-react";
import { Separator } from "@/components/ui/separator";

interface Finding {
  title?: string;
  description?: string;
  severity?: string;
  status?: string;
  category?: string;
  recommendations?: string[];
  impact?: string;
  controlId?: string;
}

function FindingsDisplay({ findings }: { findings: any }) {
  // Handle different finding formats
  const renderFindings = () => {
    // If findings is an array
    if (Array.isArray(findings)) {
      return findings.map((finding: Finding, index: number) => (
        <div key={index} className="mb-6 last:mb-0">
          {renderFindingCard(finding, index)}
          {index < findings.length - 1 && <Separator className="mt-6" />}
        </div>
      ));
    }
    
    // If findings is an object with categories
    if (typeof findings === 'object' && findings !== null) {
      const categories = Object.keys(findings);
      if (categories.length === 0) {
        return <p className="text-muted-foreground">No findings to display.</p>;
      }
      
      return categories.map((category, catIndex) => (
        <div key={category} className="mb-6 last:mb-0">
          <h3 className="text-lg font-semibold mb-4 capitalize">{category.replace(/_/g, ' ')}</h3>
          {Array.isArray(findings[category]) ? (
            findings[category].map((finding: Finding, findingIndex: number) => (
              <div key={`${category}-${findingIndex}`} className="ml-4 mb-4">
                {renderFindingCard(finding, findingIndex)}
              </div>
            ))
          ) : (
            <div className="ml-4">
              {renderFindingContent(findings[category])}
            </div>
          )}
          {catIndex < categories.length - 1 && <Separator className="mt-6" />}
        </div>
      ));
    }
    
    return <p className="text-muted-foreground">No findings available.</p>;
  };

  const getSeverityIcon = (severity?: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
      case 'high':
        return <XCircle className="h-5 w-5 text-destructive" />;
      case 'medium':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      case 'low':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      default:
        return <FileText className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const getSeverityBadge = (severity?: string) => {
    const variant: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      critical: "destructive",
      high: "destructive",
      medium: "outline",
      low: "secondary"
    };
    return variant[severity?.toLowerCase() || ''] || "default";
  };

  const renderFindingCard = (finding: Finding, index: number) => {
    return (
      <div className="space-y-3">
        <div className="flex items-start gap-3">
          {finding.severity && getSeverityIcon(finding.severity)}
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              {finding.title && (
                <h4 className="font-semibold text-base">{finding.title}</h4>
              )}
              {finding.severity && (
                <Badge variant={getSeverityBadge(finding.severity)}>
                  {finding.severity}
                </Badge>
              )}
              {finding.status && (
                <Badge variant="outline">{finding.status}</Badge>
              )}
            </div>
            
            {finding.controlId && (
              <p className="text-sm text-muted-foreground mb-2">
                Control: {finding.controlId}
              </p>
            )}
            
            {finding.category && (
              <p className="text-sm text-muted-foreground mb-2">
                Category: {finding.category}
              </p>
            )}
            
            {finding.description && (
              <p className="text-sm mb-3">{finding.description}</p>
            )}
            
            {finding.impact && (
              <div className="mb-3">
                <p className="text-sm font-medium mb-1">Impact:</p>
                <p className="text-sm text-muted-foreground">{finding.impact}</p>
              </div>
            )}
            
            {finding.recommendations && finding.recommendations.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-1">Recommendations:</p>
                <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                  {finding.recommendations.map((rec, i) => (
                    <li key={i}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderFindingContent = (content: any) => {
    if (typeof content === 'string') {
      return <p className="text-sm">{content}</p>;
    }
    if (typeof content === 'object') {
      return (
        <div className="space-y-2">
          {Object.entries(content).map(([key, value]) => (
            <div key={key}>
              <span className="text-sm font-medium capitalize">{key.replace(/_/g, ' ')}: </span>
              <span className="text-sm text-muted-foreground">
                {typeof value === 'object' ? JSON.stringify(value) : String(value)}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return <div>{renderFindings()}</div>;
}

export default function ComplianceReportDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [report, setReport] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadReport();
  }, [id]);

  const loadReport = async () => {
    try {
      const { data, error } = await supabase
        .from('compliance_reports')
        .select('*')
        .eq('id', id)
        .single();

      if (error) throw error;
      setReport(data);
    } catch (error) {
      console.error('Error loading report:', error);
      toast({
        title: "Error",
        description: "Failed to load report details",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      draft: "secondary",
      in_review: "outline",
      approved: "default",
      published: "default"
    };
    return colors[status] || "secondary";
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 pb-8 pt-8" style={{ marginTop: 'var(--lanes-height, 0px)' }}>
          <p>Loading report...</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 pb-8 pt-8" style={{ marginTop: 'var(--lanes-height, 0px)' }}>
          <p>Report not found</p>
          <Button onClick={() => navigate('/compliance')} className="mt-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Compliance Portal
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 pb-8 pt-8" style={{ marginTop: 'var(--lanes-height, 0px)' }}>

        <DashboardNavigation 
          title="Report Detail"
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
        
        <Button
          onClick={() => navigate('/compliance')} 
          variant="ghost" 
          className="mb-6"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Compliance Portal
        </Button>

        <div className="space-y-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">{report.report_name}</h1>
              <div className="flex items-center gap-4 text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Shield className="h-4 w-4" />
                  <span>{report.framework}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  <span>{new Date(report.generated_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={getStatusColor(report.status)}>
                {report.status}
              </Badge>
              <Button variant="outline">
                <Download className="mr-2 h-4 w-4" />
                Export Report
              </Button>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Report Overview</CardTitle>
              <CardDescription>
                Report period: {new Date(report.report_period_start).toLocaleDateString()} - {new Date(report.report_period_end).toLocaleDateString()}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Evidence Files</p>
                  <p className="text-2xl font-bold">{report.evidence_count}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Framework</p>
                  <p className="text-lg font-semibold">{report.framework}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Generated</p>
                  <p className="text-lg font-semibold">{new Date(report.generated_at).toLocaleDateString()}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {report.findings && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Findings & Observations
                </CardTitle>
              </CardHeader>
              <CardContent>
                <FindingsDisplay findings={report.findings} />
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
}
