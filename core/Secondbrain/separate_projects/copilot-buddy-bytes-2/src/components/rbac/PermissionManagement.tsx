import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Plus, Shield, Trash2 } from "lucide-react";
import { toast } from "sonner";

const RESOURCE_TYPES = [
  "compliance", "workflows", "cmdb", "change_management",
  "knowledge_base", "analytics", "integrations", "audit_logs",
  "reports", "settings", "users", "customers"
];

const PERMISSION_LEVELS = ["none", "view", "edit", "admin", "owner"];

export default function PermissionManagement() {
  const [selectedRole, setSelectedRole] = useState<string>("");
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [newPermission, setNewPermission] = useState({
    resource_type: "",
    resource_name: "*",
    permission_level: "view",
  });
  const queryClient = useQueryClient();

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

  // Fetch permissions for selected role
  const { data: permissions, isLoading } = useQuery({
    queryKey: ["role-permissions", selectedRole],
    queryFn: async () => {
      if (!selectedRole) return [];
      const { data, error } = await supabase
        .from("role_permissions")
        .select("*")
        .eq("role_id", selectedRole)
        .order("resource_type");
      if (error) throw error;
      return data;
    },
    enabled: !!selectedRole,
  });

  // Add permission mutation
  const addPermissionMutation = useMutation({
    mutationFn: async (permission: any) => {
      const { data, error } = await supabase
        .from("role_permissions")
        .insert({
          role_id: selectedRole,
          ...permission,
        })
        .select()
        .single();
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["role-permissions", selectedRole] });
      toast.success("Permission added successfully");
      setIsAddOpen(false);
      setNewPermission({
        resource_type: "",
        resource_name: "*",
        permission_level: "view",
      });
    },
    onError: (error: any) => {
      toast.error(`Failed to add permission: ${error.message}`);
    },
  });

  // Delete permission mutation
  const deletePermissionMutation = useMutation({
    mutationFn: async (permissionId: string) => {
      const { error } = await supabase
        .from("role_permissions")
        .delete()
        .eq("id", permissionId);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["role-permissions", selectedRole] });
      toast.success("Permission removed successfully");
    },
    onError: (error: any) => {
      toast.error(`Failed to remove permission: ${error.message}`);
    },
  });

  const handleAddPermission = () => {
    if (!newPermission.resource_type) {
      toast.error("Please select a resource type");
      return;
    }
    addPermissionMutation.mutate(newPermission);
  };

  const getPermissionBadgeVariant = (level: string) => {
    switch (level) {
      case "owner": return "default";
      case "admin": return "destructive";
      case "edit": return "secondary";
      case "view": return "outline";
      default: return "outline";
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Permission Management</CardTitle>
            <CardDescription>
              Configure resource-level permissions for roles
            </CardDescription>
          </div>
          <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
            <DialogTrigger asChild>
              <Button disabled={!selectedRole}>
                <Plus className="mr-2 h-4 w-4" />
                Add Permission
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Permission</DialogTitle>
                <DialogDescription>
                  Grant permission to a resource for this role
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Resource Type</Label>
                  <Select
                    value={newPermission.resource_type}
                    onValueChange={(value) =>
                      setNewPermission({ ...newPermission, resource_type: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select resource type" />
                    </SelectTrigger>
                    <SelectContent>
                      {RESOURCE_TYPES.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type.replace("_", " ")}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Permission Level</Label>
                  <Select
                    value={newPermission.permission_level}
                    onValueChange={(value) =>
                      setNewPermission({ ...newPermission, permission_level: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PERMISSION_LEVELS.map((level) => (
                        <SelectItem key={level} value={level}>
                          {level}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsAddOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAddPermission} disabled={addPermissionMutation.isPending}>
                  {addPermissionMutation.isPending ? "Adding..." : "Add Permission"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <Label>Select Role</Label>
          <Select value={selectedRole} onValueChange={setSelectedRole}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a role to manage permissions" />
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

        {selectedRole && (
          <div>
            {isLoading ? (
              <p>Loading permissions...</p>
            ) : permissions && permissions.length > 0 ? (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Resource Type</TableHead>
                    <TableHead>Resource Name</TableHead>
                    <TableHead>Permission Level</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {permissions.map((perm: any) => (
                    <TableRow key={perm.id}>
                      <TableCell className="font-medium">
                        <div className="flex items-center gap-2">
                          <Shield className="h-4 w-4 text-muted-foreground" />
                          {perm.resource_type.replace("_", " ")}
                        </div>
                      </TableCell>
                      <TableCell>{perm.resource_name}</TableCell>
                      <TableCell>
                        <Badge variant={getPermissionBadgeVariant(perm.permission_level)}>
                          {perm.permission_level}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deletePermissionMutation.mutate(perm.id)}
                          disabled={deletePermissionMutation.isPending}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No permissions configured for this role
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
