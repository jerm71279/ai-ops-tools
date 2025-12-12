import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

import DashboardNavigation from "@/components/DashboardNavigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Download, FileText, Calendar, Shield } from "lucide-react";
import { format, subHours, subDays, subMonths } from "date-fns";

interface AuditData {
  source_table: string;
  count: number;
  records: any[];
}

interface Framework {
  value: string;
  label: string;
}

const TIME_RANGES = [
  { value: "24h", label: "Last 24 Hours", hours: 24 },
  { value: "7d", label: "Last 7 Days", hours: 168 },
  { value: "30d", label: "Last 30 Days", hours: 720 },
  { value: "90d", label: "Last 90 Days", hours: 2160 }
];

export default function ComplianceAuditReports() {
  const navigate = useNavigate();
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [selectedFramework, setSelectedFramework] = useState<string>("");
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>("24h");
  const [isGenerating, setIsGenerating] = useState(false);
  const [auditData, setAuditData] = useState<AuditData[]>([]);
  const [reportGenerated, setReportGenerated] = useState(false);

  useEffect(() => {
    loadFrameworks();
  }, []);

  const loadFrameworks = async () => {
    try {
      const { data, error } = await supabase
        .from('compliance_frameworks')
        .select('framework_code, framework_name')
        .eq('is_active', true)
        .order('framework_name');

      if (error) throw error;

      const frameworkOptions = data?.map(f => ({
        value: f.framework_code,
        label: f.framework_name
      })) || [];

      setFrameworks(frameworkOptions);
      if (frameworkOptions.length > 0 && !selectedFramework) {
        setSelectedFramework(frameworkOptions[0].value);
      }
    } catch (error) {
      console.error('Error loading frameworks:', error);
      toast.error('Failed to load compliance frameworks');
    }
  };

  const generateReport = async () => {
    setIsGenerating(true);
    setReportGenerated(false);
    
    try {
      const timeRange = TIME_RANGES.find(t => t.value === selectedTimeRange);
      const startDate = subHours(new Date(), timeRange?.hours || 24).toISOString();
      
      // Query all tables with compliance_tags
      const queries = [
        // Audit logs
        supabase
          .from('audit_logs')
          .select('*')
          .contains('compliance_tags', [selectedFramework])
          .gte('timestamp', startDate)
          .order('timestamp', { ascending: false }),
        
        // Workflows
        supabase
          .from('workflows')
          .select('*')
          .contains('compliance_tags', [selectedFramework]),
        
        // Behavioral events
        supabase
          .from('behavioral_events')
          .select('*')
          .contains('compliance_tags', [selectedFramework])
          .gte('timestamp', startDate)
          .order('timestamp', { ascending: false }),
        
        // AI interactions
        supabase
          .from('ai_interactions')
          .select('*')
          .contains('compliance_tags', [selectedFramework])
          .gte('created_at', startDate)
          .order('created_at', { ascending: false }),
        
        // MCP execution logs
        supabase
          .from('mcp_execution_logs')
          .select('*')
          .contains('compliance_tags', [selectedFramework])
          .gte('timestamp', startDate)
          .order('timestamp', { ascending: false }),
        
        // Knowledge access logs
        supabase
          .from('knowledge_access_logs')
          .select('*')
          .contains('compliance_tags', [selectedFramework])
          .gte('timestamp', startDate)
          .order('timestamp', { ascending: false }),
        
        // System access logs
        supabase
          .from('system_access_logs')
          .select('*')
          .contains('compliance_tags', [selectedFramework])
          .gte('timestamp', startDate)
          .order('timestamp', { ascending: false }),
        
        // Anomaly detections
        supabase
          .from('anomaly_detections')
          .select('*')
          .contains('compliance_tags', [selectedFramework])
          .gte('created_at', startDate)
          .order('created_at', { ascending: false }),
        
        // Integration credentials (access tracking)
        supabase
          .from('integration_credentials')
          .select('id, integration_id, customer_id, credential_type, created_at, updated_at, compliance_tags')
          .contains('compliance_tags', [selectedFramework])
          .gte('updated_at', startDate)
          .order('updated_at', { ascending: false }),
        
        // Evidence files
        supabase
          .from('evidence_files')
          .select('*')
          .contains('compliance_tags', [selectedFramework])
          .gte('uploaded_at', startDate)
          .order('uploaded_at', { ascending: false }),
        
        // Workflow executions
        supabase
          .from('workflow_executions')
          .select('*')
          .contains('compliance_tags', [selectedFramework])
          .gte('started_at', startDate)
          .order('started_at', { ascending: false })
      ];

      const results = await Promise.all(queries);
      
      const compiledData: AuditData[] = [
        { source_table: 'Audit Logs', count: results[0].data?.length || 0, records: results[0].data || [] },
        { source_table: 'Workflows', count: results[1].data?.length || 0, records: results[1].data || [] },
        { source_table: 'Behavioral Events', count: results[2].data?.length || 0, records: results[2].data || [] },
        { source_table: 'AI Interactions', count: results[3].data?.length || 0, records: results[3].data || [] },
        { source_table: 'MCP Executions', count: results[4].data?.length || 0, records: results[4].data || [] },
        { source_table: 'Knowledge Access', count: results[5].data?.length || 0, records: results[5].data || [] },
        { source_table: 'System Access', count: results[6].data?.length || 0, records: results[6].data || [] },
        { source_table: 'Anomaly Detections', count: results[7].data?.length || 0, records: results[7].data || [] },
        { source_table: 'Credential Access', count: results[8].data?.length || 0, records: results[8].data || [] },
        { source_table: 'Evidence Files', count: results[9].data?.length || 0, records: results[9].data || [] },
        { source_table: 'Workflow Executions', count: results[10].data?.length || 0, records: results[10].data || [] }
      ];

      setAuditData(compiledData);
      setReportGenerated(true);
      
      toast.success(`Report generated: ${compiledData.reduce((sum, d) => sum + d.count, 0)} total records found`);
    } catch (error) {
      console.error('Error generating report:', error);
      toast.error('Failed to generate compliance audit report');
    } finally {
      setIsGenerating(false);
    }
  };

  const exportToCSV = () => {
    if (auditData.length === 0) {
      toast.error('No data to export');
      return;
    }

    const timeRange = TIME_RANGES.find(t => t.value === selectedTimeRange);
    const framework = frameworks.find(f => f.value === selectedFramework);
    
    let csvContent = `Compliance Audit Report\n`;
    csvContent += `Framework: ${framework?.label}\n`;
    csvContent += `Time Range: ${timeRange?.label}\n`;
    csvContent += `Generated: ${format(new Date(), 'yyyy-MM-dd HH:mm:ss')}\n\n`;

    auditData.forEach(data => {
      if (data.count > 0) {
        csvContent += `\n${data.source_table} (${data.count} records)\n`;
        csvContent += '-'.repeat(80) + '\n';
        
        data.records.forEach((record, index) => {
          csvContent += `Record ${index + 1}:\n`;
          csvContent += JSON.stringify(record, null, 2) + '\n\n';
        });
      }
    });

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `compliance-audit-${selectedFramework}-${selectedTimeRange}-${format(new Date(), 'yyyyMMdd-HHmmss')}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
    
    toast.success('Report exported successfully');
  };

  const totalRecords = auditData.reduce((sum, data) => sum + data.count, 0);

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 pb-8 pt-8" style={{ marginTop: 'var(--lanes-height, 0px)' }}>

        <DashboardNavigation 
          title="Compliance Audit Reports"
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
            <h1 className="text-4xl font-bold mb-2">Compliance Audit Reports</h1>
            <p className="text-muted-foreground">Generate framework-specific audit trails from all platform logs</p>
          </div>
          <Button variant="outline" onClick={() => navigate('/dashboard/compliance')}>
            <Shield className="mr-2 h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>

        {/* Report Configuration */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Report Configuration
            </CardTitle>
            <CardDescription>Select the compliance framework and time range for your audit report</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Compliance Framework</label>
                <Select value={selectedFramework} onValueChange={setSelectedFramework}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select framework to generate report..." />
                  </SelectTrigger>
                  <SelectContent>
                    {frameworks.map(framework => (
                      <SelectItem key={framework.value} value={framework.value}>
                        {framework.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">Time Range</label>
                <Select value={selectedTimeRange} onValueChange={setSelectedTimeRange}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TIME_RANGES.map(range => (
                      <SelectItem key={range.value} value={range.value}>
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          {range.label}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="flex gap-2">
              <Button 
                onClick={generateReport} 
                disabled={isGenerating}
                className="flex-1"
              >
                {isGenerating ? 'Generating...' : 'Generate Report'}
              </Button>
              
              {reportGenerated && (
                <Button 
                  onClick={exportToCSV}
                  variant="outline"
                >
                  <Download className="mr-2 h-4 w-4" />
                  Export CSV
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Report Results */}
        {reportGenerated && (
          <>
            {/* Data Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
              {auditData.map((data) => (
                <Card 
                  key={data.source_table}
                  className={data.count > 0 ? "cursor-pointer hover:border-primary transition-colors" : ""}
                  onClick={() => {
                    if (data.count > 0) {
                      navigate(`/compliance/framework/${selectedFramework}/records?source=${encodeURIComponent(data.source_table)}&timeRange=${selectedTimeRange}`);
                    }
                  }}
                >
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg flex items-center justify-between">
                      {data.source_table}
                      <Badge variant={data.count > 0 ? "default" : "secondary"}>
                        {data.count}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {data.count > 0 ? (
                      <div className="text-sm text-primary font-medium">
                        Click to view {data.count} {data.count === 1 ? 'record' : 'records'} →
                      </div>
                    ) : (
                      <div className="text-sm text-muted-foreground">
                        No records in this time period
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            <Card className="mb-6">
              <CardHeader>
                <CardTitle>Report Summary</CardTitle>
                <CardDescription>
                  {frameworks.find(f => f.value === selectedFramework)?.label} compliance audit for{' '}
                  {TIME_RANGES.find(t => t.value === selectedTimeRange)?.label.toLowerCase()}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-4 overflow-x-auto pb-2">
                  <div className="text-center p-4 bg-muted rounded-lg min-w-[180px] flex-shrink-0">
                    <div className="text-3xl font-bold text-primary">{totalRecords}</div>
                    <div className="text-sm text-muted-foreground mt-1">Total Records</div>
                  </div>
                  <div className="text-center p-4 bg-muted rounded-lg min-w-[180px] flex-shrink-0">
                    <div className="text-3xl font-bold text-primary">
                      {auditData.filter(d => d.count > 0).length}
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">Data Sources</div>
                  </div>
                  <div className="text-center p-4 bg-muted rounded-lg min-w-[180px] flex-shrink-0">
                    <div className="text-3xl font-bold text-primary">
                      {selectedFramework}
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">Framework</div>
                  </div>
                  <div className="text-center p-4 bg-muted rounded-lg min-w-[180px] flex-shrink-0">
                    <div className="text-3xl font-bold text-primary">
                      {TIME_RANGES.find(t => t.value === selectedTimeRange)?.label}
                    </div>
                    <div className="text-sm text-muted-foreground mt-1">Time Period</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        )}

        {!reportGenerated && (
          <Card>
            <CardContent className="py-12 text-center">
              <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Report Generated</h3>
              <p className="text-muted-foreground">
                Select a framework and time range, then click "Generate Report" to begin
              </p>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
