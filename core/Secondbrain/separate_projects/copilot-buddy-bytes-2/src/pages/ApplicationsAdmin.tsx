import { useEffect, useState } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Checkbox } from '@/components/ui/checkbox';
import { useToast } from '@/hooks/use-toast';
import { Plus, Trash2, Save, Loader2 } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import Navigation from '@/components/Navigation';
import DashboardNavigation from '@/components/DashboardNavigation';

interface Application {
  id: string;
  name: string;
  description: string | null;
  icon_name: string;
  app_url: string | null;
  category: string;
  auth_type: string;
  is_active: boolean;
  display_order: number;
}

interface ApplicationAccess {
  application_id: string;
  department: string | null;
}

const DEPARTMENTS = ['IT', 'HR', 'Finance', 'Sales', 'Operations', 'Executive'];
const CATEGORIES = ['communication', 'productivity', 'security', 'analytics', 'finance', 'other'];
const AUTH_TYPES = ['microsoft365', 'oauth', 'saml', 'api_key'];

export default function ApplicationsAdmin() {
  const [apps, setApps] = useState<Application[]>([]);
  const [access, setAccess] = useState<Record<string, string[]>>({});
  const [loading, setLoading] = useState(true);
  const [editingApp, setEditingApp] = useState<Partial<Application> | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);

      const { data: appsData, error: appsError } = await supabase
        .from('applications')
        .select('*')
        .order('display_order');

      if (appsError) throw appsError;

      const { data: accessData, error: accessError } = await supabase
        .from('application_access')
        .select('application_id, department');

      if (accessError) throw accessError;

      setApps(appsData || []);

      // Group access by application_id
      const accessMap: Record<string, string[]> = {};
      accessData?.forEach((item) => {
        if (item.department) {
          if (!accessMap[item.application_id]) {
            accessMap[item.application_id] = [];
          }
          accessMap[item.application_id].push(item.department);
        }
      });
      setAccess(accessMap);
    } catch (error) {
      console.error('Error loading data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load applications',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSaveApp = async () => {
    if (!editingApp?.name) {
      toast({
        title: 'Error',
        description: 'Application name is required',
        variant: 'destructive',
      });
      return;
    }

    try {
      if (editingApp.id) {
        const { error } = await supabase
          .from('applications')
          .update(editingApp)
          .eq('id', editingApp.id);

        if (error) throw error;
      } else {
        const { error } = await supabase
          .from('applications')
          .insert([editingApp as any]);

        if (error) throw error;
      }

      toast({
        title: 'Success',
        description: `Application ${editingApp.id ? 'updated' : 'created'} successfully`,
      });

      setIsDialogOpen(false);
      setEditingApp(null);
      loadData();
    } catch (error) {
      console.error('Error saving application:', error);
      toast({
        title: 'Error',
        description: 'Failed to save application',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteApp = async (id: string) => {
    if (!confirm('Are you sure you want to delete this application?')) return;

    try {
      const { error } = await supabase
        .from('applications')
        .delete()
        .eq('id', id);

      if (error) throw error;

      toast({
        title: 'Success',
        description: 'Application deleted successfully',
      });

      loadData();
    } catch (error) {
      console.error('Error deleting application:', error);
      toast({
        title: 'Error',
        description: 'Failed to delete application',
        variant: 'destructive',
      });
    }
  };

  const handleAccessChange = async (appId: string, department: string, checked: boolean) => {
    try {
      if (checked) {
        const { error } = await supabase
          .from('application_access')
          .insert({ application_id: appId, department });

        if (error) throw error;
      } else {
        const { error } = await supabase
          .from('application_access')
          .delete()
          .eq('application_id', appId)
          .eq('department', department);

        if (error) throw error;
      }

      loadData();
    } catch (error) {
      console.error('Error updating access:', error);
      toast({
        title: 'Error',
        description: 'Failed to update access',
        variant: 'destructive',
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 pt-56 pb-8">
        <DashboardNavigation 
          title="Applications Manager"
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
        
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold">Applications Manager</h1>
            <p className="text-muted-foreground mt-2">
              Manage employee applications and department access
            </p>
          </div>

          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => setEditingApp({ is_active: true, display_order: 0 })}>
                <Plus className="mr-2 h-4 w-4" />
                Add Application
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>
                  {editingApp?.id ? 'Edit Application' : 'New Application'}
                </DialogTitle>
              </DialogHeader>

              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Application Name</Label>
                  <Input
                    id="name"
                    value={editingApp?.name || ''}
                    onChange={(e) => setEditingApp({ ...editingApp, name: e.target.value })}
                  />
                </div>

                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={editingApp?.description || ''}
                    onChange={(e) => setEditingApp({ ...editingApp, description: e.target.value })}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="icon">Icon Name (Lucide)</Label>
                    <Input
                      id="icon"
                      value={editingApp?.icon_name || 'Package'}
                      onChange={(e) => setEditingApp({ ...editingApp, icon_name: e.target.value })}
                    />
                  </div>

                  <div>
                    <Label htmlFor="url">Application URL</Label>
                    <Input
                      id="url"
                      value={editingApp?.app_url || ''}
                      onChange={(e) => setEditingApp({ ...editingApp, app_url: e.target.value })}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="category">Category</Label>
                    <Select
                      value={editingApp?.category || 'productivity'}
                      onValueChange={(value) => setEditingApp({ ...editingApp, category: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {CATEGORIES.map((cat) => (
                          <SelectItem key={cat} value={cat}>
                            {cat}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div>
                    <Label htmlFor="auth">Auth Type</Label>
                    <Select
                      value={editingApp?.auth_type || 'microsoft365'}
                      onValueChange={(value) => setEditingApp({ ...editingApp, auth_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {AUTH_TYPES.map((type) => (
                          <SelectItem key={type} value={type}>
                            {type}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="active"
                    checked={editingApp?.is_active ?? true}
                    onCheckedChange={(checked) =>
                      setEditingApp({ ...editingApp, is_active: checked })
                    }
                  />
                  <Label htmlFor="active">Active</Label>
                </div>

                <div className="flex justify-end gap-2 pt-4">
                  <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleSaveApp}>
                    <Save className="mr-2 h-4 w-4" />
                    Save
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid gap-6">
          {apps.map((app) => (
            <Card key={app.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle>{app.name}</CardTitle>
                    <CardDescription>{app.description}</CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setEditingApp(app);
                        setIsDialogOpen(true);
                      }}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDeleteApp(app.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Label>Department Access</Label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {DEPARTMENTS.map((dept) => (
                      <div key={dept} className="flex items-center space-x-2">
                        <Checkbox
                          id={`${app.id}-${dept}`}
                          checked={access[app.id]?.includes(dept) || false}
                          onCheckedChange={(checked) =>
                            handleAccessChange(app.id, dept, checked as boolean)
                          }
                        />
                        <Label htmlFor={`${app.id}-${dept}`} className="font-normal">
                          {dept}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
    </div>
  );
}
