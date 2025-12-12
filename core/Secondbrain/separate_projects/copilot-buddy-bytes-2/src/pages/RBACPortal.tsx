import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Shield, Users, GitBranch, Clock, FileText, Layout } from "lucide-react";
import { toast } from "sonner";
import RoleManagement from "@/components/rbac/RoleManagement";
import PermissionManagement from "@/components/rbac/PermissionManagement";
import RoleHierarchy from "@/components/rbac/RoleHierarchy";
import TemporaryPrivileges from "@/components/rbac/TemporaryPrivileges";
import PermissionAuditLog from "@/components/rbac/PermissionAuditLog";
import RoleTemplates from "@/components/rbac/RoleTemplates";

export default function RBACPortal() {
  const [activeTab, setActiveTab] = useState("roles");
  const queryClient = useQueryClient();

  // Check if user has admin permissions
  const { data: isAdmin, isLoading } = useQuery({
    queryKey: ["rbac-admin-check"],
    queryFn: async () => {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return false;

      const { data, error } = await supabase
        .rpc("has_role", { _user_id: user.id, _role: "admin" });
      
      if (error) throw error;
      return data;
    },
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 pb-8" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAdmin) {
    return (
      <div className="min-h-screen bg-background">
        <main className="container mx-auto px-4 pb-8" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>
          <Card>
            <CardHeader>
              <CardTitle>Access Denied</CardTitle>
              <CardDescription>
                You need administrator privileges to access this page.
              </CardDescription>
            </CardHeader>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      
      <main className="container mx-auto px-4 pb-8" style={{ paddingTop: 'calc(var(--lanes-height, 200px) + 1rem)' }}>
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <Shield className="h-8 w-8 text-primary" />
            <h1 className="text-4xl font-bold">Enhanced RBAC Portal</h1>
          </div>
          <p className="text-muted-foreground">
            Comprehensive role-based access control management with advanced features
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <div className="overflow-x-auto">
            <TabsList className="inline-flex w-auto min-w-full">
              <TabsTrigger value="roles" className="gap-2">
                <Users className="h-4 w-4" />
                Roles
              </TabsTrigger>
              <TabsTrigger value="permissions" className="gap-2">
                <Shield className="h-4 w-4" />
                Permissions
              </TabsTrigger>
              <TabsTrigger value="hierarchy" className="gap-2">
                <GitBranch className="h-4 w-4" />
                Hierarchy
              </TabsTrigger>
              <TabsTrigger value="temporary" className="gap-2">
                <Clock className="h-4 w-4" />
                Temporary
              </TabsTrigger>
              <TabsTrigger value="audit" className="gap-2">
                <FileText className="h-4 w-4" />
                Audit Log
              </TabsTrigger>
              <TabsTrigger value="templates" className="gap-2">
                <Layout className="h-4 w-4" />
                Templates
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="roles">
            <RoleManagement />
          </TabsContent>

          <TabsContent value="permissions">
            <PermissionManagement />
          </TabsContent>

          <TabsContent value="hierarchy">
            <RoleHierarchy />
          </TabsContent>

          <TabsContent value="temporary">
            <TemporaryPrivileges />
          </TabsContent>

          <TabsContent value="audit">
            <PermissionAuditLog />
          </TabsContent>

          <TabsContent value="templates">
            <RoleTemplates />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
