import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import { Plus, Power, PowerOff } from "lucide-react";

export default function RemediationRules() {
  const queryClient = useQueryClient();
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newRule, setNewRule] = useState({
    rule_name: "",
    description: "",
    conditions: {} as any,
    incident_pattern: {} as any,
    remediation_actions: {} as any,
    auto_execute: true,
    requires_approval: false,
    is_active: true
  });

  const { data: rules, isLoading } = useQuery({
    queryKey: ["remediation_rules"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("remediation_rules")
        .select("*")
        .order("priority", { ascending: false });
      if (error) throw error;
      return data;
    },
  });

  const createRule = useMutation({
    mutationFn: async (rule: typeof newRule) => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      const { data, error } = await supabase
        .from("remediation_rules")
        .insert({
          rule_name: rule.rule_name,
          description: rule.description,
          conditions: rule.conditions,
          incident_pattern: rule.incident_pattern,
          remediation_actions: rule.remediation_actions,
          auto_execute: rule.auto_execute,
          requires_approval: rule.requires_approval,
          is_active: rule.is_active,
          customer_id: profile?.customer_id!,
          created_by: user.id
        })
        .select()
        .single();
      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["remediation_rules"] });
      toast.success("Remediation rule created successfully");
      setIsCreateOpen(false);
      setNewRule({
        rule_name: "",
        description: "",
        conditions: {},
        incident_pattern: {},
        remediation_actions: {},
        auto_execute: true,
        requires_approval: false,
        is_active: true
      });
    },
  });

  const toggleRule = useMutation({
    mutationFn: async ({ id, is_active }: { id: string; is_active: boolean }) => {
      const { error } = await supabase
        .from("remediation_rules")
        .update({ is_active })
        .eq("id", id);
      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["remediation_rules"] });
      toast.success("Rule status updated");
    },
  });

  if (isLoading) {
    return <div className="p-8">Loading remediation rules...</div>;
  }

  return (
    <div className="container mx-auto p-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Remediation Rules</h1>
          <p className="text-muted-foreground">Configure auto-remediation for incidents</p>
        </div>
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Rule
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create Remediation Rule</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label>Rule Name</Label>
                <Input
                  value={newRule.rule_name}
                  onChange={(e) => setNewRule({ ...newRule, rule_name: e.target.value })}
                />
              </div>
              <div>
                <Label>Description</Label>
                <Textarea
                  value={newRule.description}
                  onChange={(e) => setNewRule({ ...newRule, description: e.target.value })}
                />
              </div>
              <div>
                <Label>Remediation Actions (JSON)</Label>
                <Textarea
                  value={JSON.stringify(newRule.remediation_actions, null, 2)}
                  onChange={(e) => {
                    try {
                      setNewRule({ ...newRule, remediation_actions: JSON.parse(e.target.value) });
                    } catch {
                      // Invalid JSON, keep editing
                    }
                  }}
                  placeholder='{"action": "restart_service", "service": "nginx"}'
                  rows={6}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={newRule.auto_execute}
                    onCheckedChange={(checked) => setNewRule({ ...newRule, auto_execute: checked })}
                  />
                  <Label>Auto Execute</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={newRule.requires_approval}
                    onCheckedChange={(checked) => setNewRule({ ...newRule, requires_approval: checked })}
                  />
                  <Label>Requires Approval</Label>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <Switch
                  checked={newRule.is_active}
                  onCheckedChange={(checked) => setNewRule({ ...newRule, is_active: checked })}
                />
                <Label>Active</Label>
              </div>
              <Button onClick={() => createRule.mutate(newRule)} className="w-full">
                Create Rule
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Total Rules</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{rules?.length || 0}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Active Rules</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-success">
              {rules?.filter(r => r.is_active).length || 0}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Automatic Rules</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">
              {rules?.filter(r => r.auto_execute).length || 0}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Remediation Rules</CardTitle>
          <CardDescription>Manage automated incident response rules</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rule Name</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Execution Mode</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {rules?.map((rule) => (
                <TableRow key={rule.id}>
                  <TableCell className="font-medium">{rule.rule_name}</TableCell>
                  <TableCell className="max-w-md truncate">{rule.description}</TableCell>
                  <TableCell>
                    <Badge variant={rule.auto_execute ? "default" : "secondary"}>
                      {rule.auto_execute ? "Automatic" : "Manual Approval"}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {rule.is_active ? (
                        <Power className="h-4 w-4 text-success" />
                      ) : (
                        <PowerOff className="h-4 w-4 text-muted-foreground" />
                      )}
                      <span>{rule.is_active ? "Active" : "Inactive"}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => toggleRule.mutate({ id: rule.id, is_active: !rule.is_active })}
                    >
                      {rule.is_active ? "Disable" : "Enable"}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
