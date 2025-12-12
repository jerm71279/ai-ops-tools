import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Plus, Play, FileText, Clock } from "lucide-react";

export default function CustomReportBuilder() {
  const queryClient = useQueryClient();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newReport, setNewReport] = useState({
    report_name: "",
    description: "",
    data_sources: [] as any[],
  });

  const { data: reports } = useQuery({
    queryKey: ["custom_reports"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("custom_reports")
        .select("*")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data;
    },
  });

  const { data: executions } = useQuery({
    queryKey: ["report_executions"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("report_executions")
        .select("*, custom_reports(report_name)")
        .order("executed_at", { ascending: false })
        .limit(10);
      if (error) throw error;
      return data;
    },
  });

  const createReport = useMutation({
    mutationFn: async (report: typeof newReport) => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      const { data, error } = await supabase
        .from("custom_reports")
        .insert({
          report_name: report.report_name,
          description: report.description,
          customer_id: profile?.customer_id!,
          created_by: user.id,
          report_type: "custom",
          data_sources: report.data_sources.length > 0 ? report.data_sources : [
            {
              table: "audit_logs",
              columns: ["id", "action_type", "system_name", "timestamp"],
              filters: {}
            }
          ]
        })
        .select()
        .single();
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["custom_reports"] });
      toast.success("Report created successfully");
      setIsCreateOpen(false);
      setNewReport({ report_name: "", description: "", data_sources: [] });
    },
  });

  const executeReport = useMutation({
    mutationFn: async (reportId: string) => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      const { data, error } = await supabase.functions.invoke("custom-report-engine", {
        body: {
          action: "execute_report",
          reportId,
          customerId: profile?.customer_id
        },
      });
      if (error) throw error;
      return data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["report_executions"] });
      toast.success(`Report executed: ${data.count} records in ${data.executionTime}ms`);
    },
  });

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <div className="container mx-auto px-4 pt-56 pb-8 space-y-6">
        <DashboardNavigation 
          title="Custom Report Builder"
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
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Custom Report Builder</h1>
            <p className="text-muted-foreground">Create and execute custom reports from your data</p>
          </div>
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Report
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create Custom Report</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Report Name</Label>
                <Input
                  value={newReport.report_name}
                  onChange={(e) => setNewReport({ ...newReport, report_name: e.target.value })}
                  placeholder="Monthly Audit Report"
                />
              </div>
              <div>
                <Label>Description</Label>
                <Textarea
                  value={newReport.description}
                  onChange={(e) => setNewReport({ ...newReport, description: e.target.value })}
                  placeholder="Describe what this report will show..."
                />
              </div>
              <div className="text-sm text-muted-foreground">
                <p>This will create a basic audit log report. You can customize data sources after creation.</p>
              </div>
              <Button onClick={() => createReport.mutate(newReport)} className="w-full">
                Create Report
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Reports</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{reports?.length || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scheduled</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {reports?.filter(r => r.is_scheduled).length || 0}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Executions Today</CardTitle>
            <Play className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {executions?.filter(e => {
                const today = new Date().toDateString();
                return new Date(e.created_at).toDateString() === today;
              }).length || 0}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Execution</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {executions && executions.length > 0
                ? Math.round(executions.reduce((sum, e) => sum + (e.execution_time_ms || 0), 0) / executions.length)
                : 0}ms
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>My Reports</CardTitle>
          <CardDescription>Manage and execute your custom reports</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Report Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Run</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {reports?.map((report) => (
                <TableRow key={report.id}>
                  <TableCell className="font-medium">{report.report_name}</TableCell>
                  <TableCell className="max-w-md truncate">{report.description}</TableCell>
                  <TableCell>
                    {report.is_scheduled ? (
                      <Badge>Scheduled</Badge>
                    ) : (
                      <Badge variant="secondary">Manual</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    {report.last_run_at
                      ? new Date(report.last_run_at).toLocaleString()
                      : "Never"}
                  </TableCell>
                  <TableCell>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => executeReport.mutate(report.id)}
                    >
                      <Play className="h-4 w-4 mr-1" />
                      Run
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Recent Executions</CardTitle>
          <CardDescription>Latest report execution history</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Report</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Records</TableHead>
                <TableHead>Execution Time</TableHead>
                <TableHead>Executed At</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {executions?.map((execution) => (
                <TableRow key={execution.id}>
                  <TableCell>{execution.custom_reports?.report_name}</TableCell>
                  <TableCell>
                    <Badge variant={execution.status === "completed" ? "default" : "destructive"}>
                      {execution.status}
                    </Badge>
                  </TableCell>
                  <TableCell>{execution.result_count || 0}</TableCell>
                  <TableCell>{execution.execution_time_ms}ms</TableCell>
                  <TableCell>{new Date(execution.created_at).toLocaleString()}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      </div>
    </div>
  );
}
