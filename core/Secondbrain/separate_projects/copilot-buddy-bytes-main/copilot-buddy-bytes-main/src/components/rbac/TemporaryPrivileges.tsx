import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Plus, Clock, XCircle } from "lucide-react";
import { toast } from "sonner";

export default function TemporaryPrivileges() {
  const [isGrantOpen, setIsGrantOpen] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState("");
  const [selectedRoleId, setSelectedRoleId] = useState("");
  const [reason, setReason] = useState("");
  const [validHours, setValidHours] = useState("24");
  const queryClient = useQueryClient();

  // Fetch users
  const { data: users } = useQuery({
    queryKey: ["users-for-temp-privileges"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("user_profiles")
        .select("user_id, full_name")
        .order("full_name");
      if (error) throw error;
      return data;
    },
  });

  // Fetch roles
  const { data: roles } = useQuery({
    queryKey: ["roles"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("roles")
        .select("*")
        .order("name");
      if (error) throw error;
      return data;
    },
  });

  // Fetch temporary privileges
  const { data: privileges, isLoading } = useQuery({
    queryKey: ["temporary-privileges"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("temporary_privileges" as any)
        .select(`
          *,
          role:roles(name),
          user:user_profiles!temporary_privileges_user_id_fkey(full_name),
          granted_by_user:user_profiles!temporary_privileges_granted_by_fkey(full_name)
        `)
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data;
    },
  });

  // Grant privilege mutation
  const grantPrivilegeMutation = useMutation({
    mutationFn: async (data: any) => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const validUntil = new Date();
      validUntil.setHours(validUntil.getHours() + parseInt(data.validHours));

      const { error } = await supabase
        .from("temporary_privileges" as any)
        .insert({
          user_id: data.userId,
          role_id: data.roleId,
          granted_by: user.id,
          reason: data.reason,
          valid_until: validUntil.toISOString(),
        });
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["temporary-privileges"] });
      toast.success("Temporary privilege granted successfully");
      setIsGrantOpen(false);
      setSelectedUserId("");
      setSelectedRoleId("");
      setReason("");
      setValidHours("24");
    },
    onError: (error: any) => {
      toast.error(`Failed to grant privilege: ${error.message}`);
    },
  });

  // Revoke privilege mutation
  const revokePrivilegeMutation = useMutation({
    mutationFn: async (privilegeId: string) => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { error } = await supabase
        .from("temporary_privileges" as any)
        .update({
          is_active: false,
          revoked_at: new Date().toISOString(),
          revoked_by: user.id,
        })
        .eq("id", privilegeId);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["temporary-privileges"] });
      toast.success("Temporary privilege revoked successfully");
    },
    onError: (error: any) => {
      toast.error(`Failed to revoke privilege: ${error.message}`);
    },
  });

  const handleGrantPrivilege = () => {
    if (!selectedUserId || !selectedRoleId || !reason.trim()) {
      toast.error("Please fill in all fields");
      return;
    }
    grantPrivilegeMutation.mutate({
      userId: selectedUserId,
      roleId: selectedRoleId,
      reason,
      validHours,
    });
  };

  const isExpired = (validUntil: string) => {
    return new Date(validUntil) < new Date();
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Temporary Privileges</CardTitle>
            <CardDescription>
              Grant time-limited elevated privileges with approval tracking
            </CardDescription>
          </div>
          <Dialog open={isGrantOpen} onOpenChange={setIsGrantOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Grant Privilege
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Grant Temporary Privilege</DialogTitle>
                <DialogDescription>
                  Provide temporary elevated access to a user
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>User</Label>
                  <Select value={selectedUserId} onValueChange={setSelectedUserId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select user" />
                    </SelectTrigger>
                    <SelectContent>
                      {users?.map((user: any) => (
                        <SelectItem key={user.user_id} value={user.user_id}>
                          {user.full_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Role</Label>
                  <Select value={selectedRoleId} onValueChange={setSelectedRoleId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select role" />
                    </SelectTrigger>
                    <SelectContent>
                      {roles?.map((role: any) => (
                        <SelectItem key={role.id} value={role.id}>
                          {role.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Duration (hours)</Label>
                  <Input
                    type="number"
                    value={validHours}
                    onChange={(e) => setValidHours(e.target.value)}
                    min="1"
                    max="168"
                  />
                </div>
                <div>
                  <Label>Reason</Label>
                  <Textarea
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    placeholder="Why is this privilege needed?"
                    rows={3}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsGrantOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleGrantPrivilege} disabled={grantPrivilegeMutation.isPending}>
                  {grantPrivilegeMutation.isPending ? "Granting..." : "Grant Privilege"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p>Loading privileges...</p>
        ) : privileges && privileges.length > 0 ? (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Granted By</TableHead>
                <TableHead>Valid Until</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {privileges.map((priv: any) => {
                const expired = isExpired(priv.valid_until);
                const status = !priv.is_active
                  ? "revoked"
                  : expired
                  ? "expired"
                  : "active";

                return (
                  <TableRow key={priv.id}>
                    <TableCell className="font-medium">
                      {priv.user?.full_name || "Unknown"}
                    </TableCell>
                    <TableCell>{priv.role?.name || "Unknown"}</TableCell>
                    <TableCell className="max-w-xs truncate">{priv.reason}</TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {priv.granted_by_user?.full_name || "Unknown"}
                    </TableCell>
                    <TableCell className="text-sm">
                      {new Date(priv.valid_until).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          status === "active"
                            ? "default"
                            : status === "expired"
                            ? "secondary"
                            : "outline"
                        }
                      >
                        <Clock className="mr-1 h-3 w-3" />
                        {status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {status === "active" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => revokePrivilegeMutation.mutate(priv.id)}
                          disabled={revokePrivilegeMutation.isPending}
                        >
                          <XCircle className="h-4 w-4" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No temporary privileges granted
          </div>
        )}
      </CardContent>
    </Card>
  );
}
