import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Shield } from "lucide-react";
import { useState } from "react";

export default function PermissionAuditLog() {
  const [searchTerm, setSearchTerm] = useState("");

  const { data: auditLogs, isLoading } = useQuery({
    queryKey: ["permission-audit-log"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("permission_audit_log" as any)
        .select(`
          *,
          user:user_profiles!permission_audit_log_user_id_fkey(full_name),
          target_user:user_profiles!permission_audit_log_target_user_id_fkey(full_name)
        `)
        .order("created_at", { ascending: false })
        .limit(100);
      if (error) throw error;
      return data;
    },
  });

  const filteredLogs = auditLogs?.filter((log: any) => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      log.action_type?.toLowerCase().includes(search) ||
      log.user?.full_name?.toLowerCase().includes(search) ||
      log.target_user?.full_name?.toLowerCase().includes(search) ||
      log.resource_type?.toLowerCase().includes(search)
    );
  });

  const getActionBadgeVariant = (action: string) => {
    if (action.includes("granted") || action.includes("created")) return "default";
    if (action.includes("revoked") || action.includes("deleted")) return "destructive";
    if (action.includes("modified")) return "secondary";
    return "outline";
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Permission Audit Log</CardTitle>
            <CardDescription>
              Track all permission changes and access modifications
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <Input
            placeholder="Search audit logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        {isLoading ? (
          <p>Loading audit logs...</p>
        ) : filteredLogs && filteredLogs.length > 0 ? (
          <div className="space-y-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Performed By</TableHead>
                  <TableHead>Target User</TableHead>
                  <TableHead>Resource</TableHead>
                  <TableHead>Permission Level</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLogs.map((log: any) => (
                  <TableRow key={log.id}>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(log.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge variant={getActionBadgeVariant(log.action_type)}>
                        {log.action_type.replace(/_/g, " ")}
                      </Badge>
                    </TableCell>
                    <TableCell className="font-medium">
                      {log.user?.full_name || "System"}
                    </TableCell>
                    <TableCell>
                      {log.target_user?.full_name || "-"}
                    </TableCell>
                    <TableCell>
                      {log.resource_type ? (
                        <div className="flex items-center gap-2">
                          <Shield className="h-4 w-4 text-muted-foreground" />
                          {log.resource_type.replace(/_/g, " ")}
                        </div>
                      ) : (
                        "-"
                      )}
                    </TableCell>
                    <TableCell>
                      {log.permission_level ? (
                        <Badge variant="outline">{log.permission_level}</Badge>
                      ) : (
                        "-"
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            {searchTerm ? "No matching audit logs found" : "No audit logs available"}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
