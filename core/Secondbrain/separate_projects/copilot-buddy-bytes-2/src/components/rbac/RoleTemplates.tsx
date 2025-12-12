import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Plus, Layout, Copy } from "lucide-react";
import { toast } from "sonner";

export default function RoleTemplates() {
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isApplyOpen, setIsApplyOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);
  const [selectedRoleId, setSelectedRoleId] = useState("");
  const queryClient = useQueryClient();

  // Fetch templates
  const { data: templates, isLoading } = useQuery({
    queryKey: ["role-templates"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("role_templates" as any)
        .select("*")
        .order("template_name");
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

  // Apply template mutation
  const applyTemplateMutation = useMutation({
    mutationFn: async (data: { roleId: string; permissions: any[] }) => {
      // Delete existing permissions for the role
      const { error: deleteError } = await supabase
        .from("role_permissions")
        .delete()
        .eq("role_id", data.roleId);
      
      if (deleteError) throw deleteError;

      // Insert new permissions from template
      const permissionsToInsert = data.permissions.map((perm: any) => ({
        role_id: data.roleId,
        resource_type: perm.resource_type,
        resource_name: perm.resource_name,
        permission_level: perm.permission_level,
      }));

      const { error: insertError } = await supabase
        .from("role_permissions")
        .insert(permissionsToInsert);
      
      if (insertError) throw insertError;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["role-permissions"] });
      toast.success("Template applied successfully");
      setIsApplyOpen(false);
      setSelectedTemplate(null);
      setSelectedRoleId("");
    },
    onError: (error: any) => {
      toast.error(`Failed to apply template: ${error.message}`);
    },
  });

  const handleApplyTemplate = () => {
    if (!selectedRoleId) {
      toast.error("Please select a role");
      return;
    }
    if (!selectedTemplate) {
      toast.error("No template selected");
      return;
    }
    applyTemplateMutation.mutate({
      roleId: selectedRoleId,
      permissions: selectedTemplate.permissions,
    });
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Role Templates</CardTitle>
            <CardDescription>
              Pre-configured permission sets for common roles
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p>Loading templates...</p>
        ) : templates && templates.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template: any) => (
              <Card key={template.id} className="relative">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <Layout className="h-5 w-5 text-primary" />
                    {template.is_system_template && (
                      <Badge variant="secondary">System</Badge>
                    )}
                  </div>
                  <CardTitle className="text-lg">{template.template_name}</CardTitle>
                  <CardDescription className="line-clamp-2">
                    {template.description || "No description"}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="text-sm text-muted-foreground">
                      {Array.isArray(template.permissions) ? template.permissions.length : 0} permissions
                    </div>
                    <Dialog
                      open={isApplyOpen && selectedTemplate?.id === template.id}
                      onOpenChange={(open) => {
                        setIsApplyOpen(open);
                        if (!open) {
                          setSelectedTemplate(null);
                          setSelectedRoleId("");
                        }
                      }}
                    >
                      <DialogTrigger asChild>
                        <Button
                          variant="outline"
                          size="sm"
                          className="w-full"
                          onClick={() => setSelectedTemplate(template)}
                        >
                          <Copy className="mr-2 h-4 w-4" />
                          Apply to Role
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader>
                          <DialogTitle>Apply Template</DialogTitle>
                          <DialogDescription>
                            Apply "{template.template_name}" to a role
                          </DialogDescription>
                        </DialogHeader>
                        <div className="space-y-4">
                          <div>
                            <Label>Select Role</Label>
                            <Select value={selectedRoleId} onValueChange={setSelectedRoleId}>
                              <SelectTrigger>
                                <SelectValue placeholder="Choose a role" />
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
                          <div className="text-sm text-muted-foreground">
                            This will replace all existing permissions for the selected role.
                          </div>
                        </div>
                        <DialogFooter>
                          <Button
                            variant="outline"
                            onClick={() => {
                              setIsApplyOpen(false);
                              setSelectedTemplate(null);
                              setSelectedRoleId("");
                            }}
                          >
                            Cancel
                          </Button>
                          <Button
                            onClick={handleApplyTemplate}
                            disabled={applyTemplateMutation.isPending}
                          >
                            {applyTemplateMutation.isPending ? "Applying..." : "Apply Template"}
                          </Button>
                        </DialogFooter>
                      </DialogContent>
                    </Dialog>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No role templates available
          </div>
        )}
      </CardContent>
    </Card>
  );
}
