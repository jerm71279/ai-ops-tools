import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Shield, Search, Filter, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface AuditLog {
  id: string;
  created_at: string;
  user_id: string;
  action_type: string;
  system_name: string;
  action_details: any;
  compliance_tags: string[];
}

export default function PrivilegedAccessAudit() {
  const navigate = useNavigate();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [filteredLogs, setFilteredLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [systemFilter, setSystemFilter] = useState<string>("all");
  const [userProfiles, setUserProfiles] = useState<Record<string, string>>({});

  useEffect(() => {
    checkAuthAndLoad();
  }, []);

  useEffect(() => {
    filterLogs();
  }, [logs, searchTerm, systemFilter]);

  const checkAuthAndLoad = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      navigate('/auth');
      return;
    }
    await loadAuditLogs();
  };

  const loadAuditLogs = async () => {
    try {
      // Fetch privileged access logs
      const { data: logsData, error } = await supabase
        .from('audit_logs')
        .select('*')
        .contains('compliance_tags', ['privileged_access'])
        .order('created_at', { ascending: false })
        .limit(100);

      if (error) throw error;

      setLogs(logsData || []);

      // Fetch user profiles for display names
      if (logsData && logsData.length > 0) {
        const userIds = [...new Set(logsData.map(log => log.user_id))];
        const { data: profiles } = await supabase
          .from('user_profiles')
          .select('user_id, full_name')
          .in('user_id', userIds);

        const profileMap: Record<string, string> = {};
        profiles?.forEach(profile => {
          profileMap[profile.user_id] = profile.full_name || 'Unknown User';
        });
        setUserProfiles(profileMap);
      }
    } catch (error) {
      console.error('Error loading audit logs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterLogs = () => {
    let filtered = logs;

    if (searchTerm) {
      filtered = filtered.filter(log => 
        log.action_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
        log.system_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        JSON.stringify(log.action_details).toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (systemFilter !== "all") {
      filtered = filtered.filter(log => log.system_name === systemFilter);
    }

    setFilteredLogs(filtered);
  };

  const exportLogs = () => {
    const csv = [
      ['Timestamp', 'User', 'System', 'Action', 'Details'].join(','),
      ...filteredLogs.map(log => [
        new Date(log.created_at).toISOString(),
        userProfiles[log.user_id] || log.user_id,
        log.system_name,
        log.action_type,
        JSON.stringify(log.action_details).replace(/,/g, ';')
      ].join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `privileged-access-audit-${new Date().toISOString()}.csv`;
    a.click();
  };

  const getActionBadge = (actionType: string) => {
    if (actionType.includes('connect') || actionType.includes('access')) {
      return <Badge variant="default">Access</Badge>;
    }
    if (actionType.includes('view')) {
      return <Badge variant="secondary">View</Badge>;
    }
    if (actionType.includes('execute') || actionType.includes('action')) {
      return <Badge variant="destructive">Execute</Badge>;
    }
    return <Badge variant="outline">Other</Badge>;
  };

  const uniqueSystems = ['all', ...new Set(logs.map(log => log.system_name))];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 pt-56 pb-8">
          <Card>
            <CardContent className="py-8 text-center">
              Loading audit logs...
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 pt-56 pb-8">
        <DashboardNavigation 
          title="Privileged Access Audit"
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
            <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
              <Shield className="h-10 w-10" />
              Privileged Access Audit Log
            </h1>
            <p className="text-muted-foreground">
              Complete audit trail of all privileged RMM and system access
            </p>
          </div>
          <Button onClick={exportLogs} variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Total Logs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{filteredLogs.length}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Unique Users</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {new Set(filteredLogs.map(l => l.user_id)).size}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Systems Accessed</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {new Set(filteredLogs.map(l => l.system_name)).size}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Last 24h</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {filteredLogs.filter(l => 
                  new Date(l.created_at) > new Date(Date.now() - 24*60*60*1000)
                ).length}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Filters</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search logs..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>
              <Select value={systemFilter} onValueChange={setSystemFilter}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Filter by system" />
                </SelectTrigger>
                <SelectContent>
                  {uniqueSystems.map(system => (
                    <SelectItem key={system} value={system}>
                      {system === 'all' ? 'All Systems' : system}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Audit Log Table */}
        <Card>
          <CardHeader>
            <CardTitle>Audit Trail</CardTitle>
            <CardDescription>
              Showing {filteredLogs.length} privileged access entries
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>System</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Details</TableHead>
                  <TableHead>Type</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredLogs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                      No privileged access logs found
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredLogs.map((log) => (
                    <TableRow key={log.id}>
                      <TableCell className="font-mono text-sm">
                        {new Date(log.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        {userProfiles[log.user_id] || log.user_id.slice(0, 8)}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{log.system_name}</Badge>
                      </TableCell>
                      <TableCell className="font-medium">
                        {log.action_type}
                      </TableCell>
                      <TableCell className="max-w-md truncate text-sm text-muted-foreground">
                        {JSON.stringify(log.action_details)}
                      </TableCell>
                      <TableCell>
                        {getActionBadge(log.action_type)}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
