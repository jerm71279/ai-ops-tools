import { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

import DashboardNavigation from "@/components/DashboardNavigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ArrowLeft, FileText, Calendar } from "lucide-react";
import { format } from "date-fns";

export default function ComplianceFrameworkRecords() {
  const navigate = useNavigate();
  const { framework } = useParams();
  const [searchParams] = useSearchParams();
  const sourceTable = searchParams.get("source");
  const timeRange = searchParams.get("timeRange");
  
  const [records, setRecords] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadRecords();
  }, [framework, sourceTable]);

  const loadRecords = async () => {
    if (!framework || !sourceTable) return;
    
    setIsLoading(true);
    try {
      // Map display names to actual table names
      const tableMap: Record<string, string> = {
        'Audit Logs': 'audit_logs',
        'Workflows': 'workflows',
        'Behavioral Events': 'behavioral_events',
        'AI Interactions': 'ai_interactions',
        'MCP Executions': 'mcp_execution_logs',
        'Knowledge Access': 'knowledge_access_logs',
        'System Access': 'system_access_logs',
        'Anomaly Detections': 'anomaly_detections',
        'Credential Access': 'integration_credentials',
        'Evidence Files': 'evidence_files',
        'Workflow Executions': 'workflow_executions'
      };

      const actualTableName = tableMap[sourceTable];
      let data, error;

      // Query each table with proper typing
      switch (actualTableName) {
        case 'audit_logs': {
          const result = await supabase
            .from('audit_logs')
            .select('*')
            .contains('compliance_tags', [framework])
            .order('timestamp', { ascending: false });
          data = result.data;
          error = result.error;
          break;
        }
        case 'workflows': {
          const result = await supabase
            .from('workflows')
            .select('*')
            .contains('compliance_tags', [framework])
            .order('created_at', { ascending: false });
          data = result.data;
          error = result.error;
          break;
        }
        case 'behavioral_events': {
          const result = await supabase
            .from('behavioral_events')
            .select('*')
            .contains('compliance_tags', [framework])
            .order('timestamp', { ascending: false });
          data = result.data;
          error = result.error;
          break;
        }
        case 'ai_interactions': {
          const result = await supabase
            .from('ai_interactions')
            .select('*')
            .contains('compliance_tags', [framework])
            .order('created_at', { ascending: false });
          data = result.data;
          error = result.error;
          break;
        }
        case 'mcp_execution_logs': {
          const result = await supabase
            .from('mcp_execution_logs')
            .select('*')
            .contains('compliance_tags', [framework])
            .order('timestamp', { ascending: false });
          data = result.data;
          error = result.error;
          break;
        }
        case 'knowledge_access_logs': {
          const result = await supabase
            .from('knowledge_access_logs')
            .select('*')
            .contains('compliance_tags', [framework])
            .order('timestamp', { ascending: false });
          data = result.data;
          error = result.error;
          break;
        }
        case 'system_access_logs': {
          const result = await supabase
            .from('system_access_logs')
            .select('*')
            .contains('compliance_tags', [framework])
            .order('timestamp', { ascending: false });
          data = result.data;
          error = result.error;
          break;
        }
        case 'anomaly_detections': {
          const result = await supabase
            .from('anomaly_detections')
            .select('*')
            .contains('compliance_tags', [framework])
            .order('created_at', { ascending: false });
          data = result.data;
          error = result.error;
          break;
        }
        case 'integration_credentials': {
          const result = await supabase
            .from('integration_credentials')
            .select('id, integration_id, customer_id, credential_type, created_at, updated_at, compliance_tags')
            .contains('compliance_tags', [framework])
            .order('updated_at', { ascending: false });
          data = result.data;
          error = result.error;
          break;
        }
        case 'evidence_files': {
          const result = await supabase
            .from('evidence_files')
            .select('*')
            .contains('compliance_tags', [framework])
            .order('uploaded_at', { ascending: false });
          data = result.data;
          error = result.error;
          break;
        }
        case 'workflow_executions': {
          const result = await supabase
            .from('workflow_executions')
            .select('*')
            .contains('compliance_tags', [framework])
            .order('started_at', { ascending: false });
          data = result.data;
          error = result.error;
          break;
        }
        default:
          data = [];
          error = null;
      }
      
      if (error) throw error;
      setRecords(data || []);
    } catch (error) {
      console.error('Error loading records:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'boolean') return value ? 'Yes' : 'No';
    if (typeof value === 'object') return JSON.stringify(value);
    if (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}T/)) {
      try {
        return format(new Date(value), 'MMM dd, yyyy HH:mm:ss');
      } catch {
        return value;
      }
    }
    return String(value);
  };

  const getDisplayColumns = () => {
    if (!records.length) return [];
    
    const record = records[0];
    const allKeys = Object.keys(record);
    
    // Prioritize important columns
    const priorityColumns = ['id', 'timestamp', 'created_at', 'action_type', 'system_name', 'status', 'user_id'];
    const otherColumns = allKeys.filter(k => !priorityColumns.includes(k) && k !== 'compliance_tags');
    
    return [...priorityColumns.filter(k => allKeys.includes(k)), ...otherColumns].slice(0, 8);
  };

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto px-4 pb-8 pt-8" style={{ marginTop: 'var(--lanes-height, 0px)' }}>

        <DashboardNavigation 
          title="Framework Records"
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
            <h1 className="text-4xl font-bold mb-2">
              {framework} - {sourceTable}
            </h1>
            <p className="text-muted-foreground">
              Detailed compliance records for this framework and data source
            </p>
          </div>
          <Button variant="outline" onClick={() => navigate(-1)}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
        </div>

        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Records ({records.length})
              </CardTitle>
              <Badge variant="default">{framework}</Badge>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-12">
                <p className="text-muted-foreground">Loading records...</p>
              </div>
            ) : records.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Records Found</h3>
                <p className="text-muted-foreground">
                  No compliance records found for this framework and data source
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      {getDisplayColumns().map((column) => (
                        <TableHead key={column} className="whitespace-nowrap">
                          {column.split('_').map(word => 
                            word.charAt(0).toUpperCase() + word.slice(1)
                          ).join(' ')}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {records.map((record, idx) => (
                      <TableRow key={idx}>
                        {getDisplayColumns().map((column) => (
                          <TableCell key={column} className="max-w-xs truncate">
                            {formatValue(record[column])}
                          </TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
