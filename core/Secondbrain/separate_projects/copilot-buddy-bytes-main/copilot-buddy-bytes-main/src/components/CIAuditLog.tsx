import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { FileEdit, Plus, Trash2, GitBranch, AlertCircle, User, Clock } from "lucide-react";
import { toast } from "sonner";

interface AuditLogEntry {
  id: string;
  change_type: string;
  field_name?: string;
  old_value?: any;
  new_value?: any;
  change_reason?: string;
  source: string;
  created_at: string;
  changed_by: string;
}

interface CIAuditLogProps {
  ciId: string;
}

const CIAuditLog = ({ ciId }: CIAuditLogProps) => {
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAuditLogs();
  }, [ciId]);

  const loadAuditLogs = async () => {
    try {
      const { data, error } = await supabase
        .from("ci_audit_log")
        .select("*")
        .eq("ci_id", ciId)
        .order("created_at", { ascending: false })
        .limit(50);

      if (error) throw error;
      setLogs(data || []);
    } catch (error) {
      console.error("Error loading audit logs:", error);
      toast.error("Failed to load audit history");
    } finally {
      setLoading(false);
    }
  };

  const getChangeIcon = (changeType: string) => {
    switch (changeType) {
      case "created": return <Plus className="h-4 w-4" />;
      case "updated": return <FileEdit className="h-4 w-4" />;
      case "deleted": return <Trash2 className="h-4 w-4" />;
      case "status_changed": return <AlertCircle className="h-4 w-4" />;
      case "relationship_added":
      case "relationship_removed": return <GitBranch className="h-4 w-4" />;
      default: return <FileEdit className="h-4 w-4" />;
    }
  };

  const getChangeColor = (changeType: string) => {
    switch (changeType) {
      case "created": return "default";
      case "updated": return "secondary";
      case "deleted": return "destructive";
      case "status_changed": return "outline";
      default: return "secondary";
    }
  };

  const formatValue = (value: any) => {
    if (!value) return "—";
    if (typeof value === "object") {
      return JSON.stringify(value, null, 2);
    }
    return String(value);
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Audit History</CardTitle>
          <CardDescription>Loading change history...</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Audit History</CardTitle>
        <CardDescription>
          Complete history of all changes made to this configuration item
        </CardDescription>
      </CardHeader>
      <CardContent>
        {logs.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Clock className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No audit history available</p>
          </div>
        ) : (
          <ScrollArea className="h-[400px] pr-4">
            <div className="space-y-4">
              {logs.map((log) => (
                <div key={log.id} className="flex gap-4 pb-4 border-b last:border-0">
                  <div className="flex-shrink-0 mt-1">
                    <div className="p-2 bg-accent/10 rounded-lg">
                      {getChangeIcon(log.change_type)}
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant={getChangeColor(log.change_type)}>
                        {log.change_type.replace(/_/g, " ")}
                      </Badge>
                      {log.field_name && (
                        <span className="text-sm font-medium">{log.field_name}</span>
                      )}
                      <Badge variant="outline" className="ml-auto">
                        {log.source}
                      </Badge>
                    </div>
                    
                    {(log.old_value || log.new_value) && (
                      <div className="grid grid-cols-2 gap-2 mt-2 text-sm">
                        {log.old_value && (
                          <div className="bg-red-50 dark:bg-red-950/20 p-2 rounded">
                            <p className="text-xs text-muted-foreground mb-1">Old Value</p>
                            <pre className="text-xs overflow-x-auto">
                              {formatValue(log.old_value)}
                            </pre>
                          </div>
                        )}
                        {log.new_value && (
                          <div className="bg-green-50 dark:bg-green-950/20 p-2 rounded">
                            <p className="text-xs text-muted-foreground mb-1">New Value</p>
                            <pre className="text-xs overflow-x-auto">
                              {formatValue(log.new_value)}
                            </pre>
                          </div>
                        )}
                      </div>
                    )}
                    
                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {new Date(log.created_at).toLocaleString()}
                      </span>
                      {log.change_reason && (
                        <span className="truncate">Reason: {log.change_reason}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
};

export default CIAuditLog;
