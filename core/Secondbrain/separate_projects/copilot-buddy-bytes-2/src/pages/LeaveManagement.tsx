import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Plus, Calendar, Check, X, Clock } from "lucide-react";

interface LeaveRequest {
  id: string;
  start_date: string;
  end_date: string;
  total_days: number;
  leave_reason: string;
  leave_status: string;
  requested_at: string;
}

const LeaveManagement = () => {
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [leaveTypes, setLeaveTypes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const { toast } = useToast();

  const [newLeaveRequest, setNewLeaveRequest] = useState({
    leave_type_id: "",
    start_date: "",
    end_date: "",
    leave_reason: "",
  });

  useEffect(() => {
    fetchLeaveData();
  }, []);

  const fetchLeaveData = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) return;

      const [leavesData, typesData] = await Promise.all([
        supabase
          .from("employee_leave")
          .select("*")
          .eq("customer_id", profile.customer_id)
          .order("requested_at", { ascending: false }),
        supabase
          .from("leave_types")
          .select("*")
          .eq("customer_id", profile.customer_id)
          .eq("is_active", true),
      ]);

      if (leavesData.error) throw leavesData.error;
      if (typesData.error) throw typesData.error;

      setLeaveRequests(leavesData.data || []);
      setLeaveTypes(typesData.data || []);
    } catch (error) {
      console.error("Error fetching leave data:", error);
      toast({
        title: "Error",
        description: "Failed to load leave requests",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateLeaveRequest = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) return;

      // Calculate total days
      const start = new Date(newLeaveRequest.start_date);
      const end = new Date(newLeaveRequest.end_date);
      const diffTime = Math.abs(end.getTime() - start.getTime());
      const totalDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

      const { error } = await supabase.from("employee_leave").insert([
        {
          customer_id: profile.customer_id,
          employee_id: null, // Would need to link to actual employee
          ...newLeaveRequest,
          total_days: totalDays,
        },
      ]);

      if (error) throw error;

      toast({
        title: "Success",
        description: "Leave request submitted successfully",
      });

      setIsCreateDialogOpen(false);
      setNewLeaveRequest({
        leave_type_id: "",
        start_date: "",
        end_date: "",
        leave_reason: "",
      });
      fetchLeaveData();
    } catch (error) {
      console.error("Error creating leave request:", error);
      toast({
        title: "Error",
        description: "Failed to submit leave request",
        variant: "destructive",
      });
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: { [key: string]: "default" | "secondary" | "destructive" | "outline" } = {
      pending: "secondary",
      approved: "default",
      rejected: "destructive",
      cancelled: "outline",
    };
    return <Badge variant={variants[status] || "default"}>{status}</Badge>;
  };

  const filteredLeaveRequests = leaveRequests.filter((request) => {
    return statusFilter === "all" || request.leave_status === statusFilter;
  });

  const stats = {
    total: leaveRequests.length,
    pending: leaveRequests.filter((r) => r.leave_status === "pending").length,
    approved: leaveRequests.filter((r) => r.leave_status === "approved").length,
    rejected: leaveRequests.filter((r) => r.leave_status === "rejected").length,
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation />
      
      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Leave Management</h1>
            <p className="text-muted-foreground">Manage employee leave requests</p>
          </div>
          
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Request Leave
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>New Leave Request</DialogTitle>
              </DialogHeader>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <Label htmlFor="leave_type_id">Leave Type*</Label>
                  <Select
                    value={newLeaveRequest.leave_type_id}
                    onValueChange={(value) =>
                      setNewLeaveRequest({ ...newLeaveRequest, leave_type_id: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select leave type" />
                    </SelectTrigger>
                    <SelectContent>
                      {leaveTypes.map((type) => (
                        <SelectItem key={type.id} value={type.id}>
                          {type.leave_type_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="start_date">Start Date*</Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={newLeaveRequest.start_date}
                    onChange={(e) =>
                      setNewLeaveRequest({ ...newLeaveRequest, start_date: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="end_date">End Date*</Label>
                  <Input
                    id="end_date"
                    type="date"
                    value={newLeaveRequest.end_date}
                    onChange={(e) =>
                      setNewLeaveRequest({ ...newLeaveRequest, end_date: e.target.value })
                    }
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="leave_reason">Reason</Label>
                  <Textarea
                    id="leave_reason"
                    value={newLeaveRequest.leave_reason}
                    onChange={(e) =>
                      setNewLeaveRequest({ ...newLeaveRequest, leave_reason: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateLeaveRequest}>Submit Request</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.pending}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Approved</CardTitle>
              <Check className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.approved}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Rejected</CardTitle>
              <X className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.rejected}</div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>Leave Requests</CardTitle>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p>Loading...</p>
            ) : filteredLeaveRequests.length === 0 ? (
              <p className="text-muted-foreground">No leave requests found</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Start Date</TableHead>
                    <TableHead>End Date</TableHead>
                    <TableHead>Days</TableHead>
                    <TableHead>Reason</TableHead>
                    <TableHead>Requested</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredLeaveRequests.map((request) => (
                    <TableRow key={request.id}>
                      <TableCell>
                        {new Date(request.start_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        {new Date(request.end_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>{request.total_days}</TableCell>
                      <TableCell>{request.leave_reason || "-"}</TableCell>
                      <TableCell>
                        {new Date(request.requested_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>{getStatusBadge(request.leave_status)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default LeaveManagement;