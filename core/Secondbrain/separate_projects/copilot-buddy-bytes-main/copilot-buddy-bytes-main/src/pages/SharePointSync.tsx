import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import {
  LogOut,
  Cloud,
  RefreshCw,
  Plus,
  Trash2,
  CheckCircle2,
  XCircle,
  Clock,
  FileText,
} from "lucide-react";
import DashboardNavigation from "@/components/DashboardNavigation";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
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

interface SyncConfig {
  id: string;
  site_name: string;
  site_url: string;
  library_name: string | null;
  sync_enabled: boolean;
  last_sync_at: string | null;
  sync_frequency_minutes: number;
  filter_extensions: string[] | null;
}

interface SyncLog {
  id: string;
  sync_started_at: string;
  sync_completed_at: string | null;
  status: string;
  files_synced: number;
  files_failed: number;
  error_message: string | null;
}

const SharePointSync = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [syncing, setSyncing] = useState<string | null>(null);
  const [configs, setConfigs] = useState<SyncConfig[]>([]);
  const [logs, setLogs] = useState<SyncLog[]>([]);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [sharePointSites, setSharePointSites] = useState<any[]>([]);
  const [selectedSite, setSelectedSite] = useState<string>("");
  const [customerId, setCustomerId] = useState<string | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const {
      data: { session },
    } = await supabase.auth.getSession();

    if (!session) {
      navigate("/auth");
      return;
    }

    // Get customer ID
    const { data: profile } = await supabase
      .from("user_profiles")
      .select("customer_id")
      .eq("user_id", session.user.id)
      .maybeSingle();

    if (profile?.customer_id) {
      setCustomerId(profile.customer_id);
    }

    await fetchConfigs();
    await fetchLogs();
    setIsLoading(false);
  };

  const fetchConfigs = async () => {
    const { data, error } = await supabase
      .from("sharepoint_sync_config")
      .select("*")
      .order("created_at", { ascending: false });

    if (error) {
      toast.error("Failed to load sync configurations");
      return;
    }

    setConfigs(data || []);
  };

  const fetchLogs = async () => {
    const { data, error } = await supabase
      .from("sharepoint_sync_logs")
      .select("*")
      .order("sync_started_at", { ascending: false })
      .limit(10);

    if (error) {
      toast.error("Failed to load sync logs");
      return;
    }

    setLogs(data || []);
  };

  const fetchSharePointSites = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      // Get Microsoft 365 linked identity
      const { data: identities } = await supabase.auth.getUserIdentities();
      const msIdentity = identities?.identities?.find(
        (i) => i.provider === "azure"
      );

      if (!msIdentity) {
        toast.error("Please link your Microsoft 365 account first");
        return;
      }

      // Call Graph API to get SharePoint sites
      const { data, error } = await supabase.functions.invoke("graph-api", {
        body: {
          endpoint: "/sites?search=*",
          method: "GET",
        },
      });

      if (error) throw error;

      setSharePointSites(data.value || []);
    } catch (error) {
      console.error("Error fetching SharePoint sites:", error);
      toast.error("Failed to fetch SharePoint sites");
    }
  };

  const handleAddConfig = async () => {
    if (!selectedSite || !customerId) return;

    const site = sharePointSites.find((s) => s.id === selectedSite);
    if (!site) return;

    const { error } = await supabase.from("sharepoint_sync_config").insert({
      customer_id: customerId,
      site_id: site.id,
      site_name: site.displayName,
      site_url: site.webUrl,
      sync_enabled: true,
      sync_frequency_minutes: 60,
    });

    if (error) {
      toast.error("Failed to add sync configuration");
      return;
    }

    toast.success("Sync configuration added successfully");
    setIsAddDialogOpen(false);
    setSelectedSite("");
    await fetchConfigs();
  };

  const handleToggleSync = async (configId: string, enabled: boolean) => {
    const { error } = await supabase
      .from("sharepoint_sync_config")
      .update({ sync_enabled: enabled })
      .eq("id", configId);

    if (error) {
      toast.error("Failed to update sync configuration");
      return;
    }

    toast.success(enabled ? "Sync enabled" : "Sync disabled");
    await fetchConfigs();
  };

  const handleSyncNow = async (config: SyncConfig) => {
    setSyncing(config.id);

    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) throw new Error("Not authenticated");

      // Get Microsoft 365 access token
      const { data: identities } = await supabase.auth.getUserIdentities();
      const msIdentity = identities?.identities?.find(
        (i) => i.provider === "azure"
      );

      if (!msIdentity) {
        throw new Error("Microsoft 365 account not linked");
      }

      // Trigger sync
      const { data, error } = await supabase.functions.invoke("sharepoint-sync", {
        body: {
          syncConfigId: config.id,
          accessToken: msIdentity.identity_data?.access_token,
        },
      });

      if (error) throw error;

      toast.success(`Synced ${data.files_synced} files successfully`);
      await fetchLogs();
      await fetchConfigs();
    } catch (error) {
      console.error("Sync error:", error);
      toast.error("Failed to sync SharePoint documents");
    } finally {
      setSyncing(null);
    }
  };

  const handleDeleteConfig = async (configId: string) => {
    const { error } = await supabase
      .from("sharepoint_sync_config")
      .delete()
      .eq("id", configId);

    if (error) {
      toast.error("Failed to delete sync configuration");
      return;
    }

    toast.success("Sync configuration deleted");
    await fetchConfigs();
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    navigate("/auth");
  };

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b bg-card">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Cloud className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-bold">SharePoint Sync</h1>
          </div>
          <Button onClick={handleSignOut} variant="outline" size="sm">
            <LogOut className="h-4 w-4 mr-2" />
            Sign Out
          </Button>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-8 space-y-6">
        <DashboardNavigation 
          title="SharePoint Sync"
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

        {/* Header with Add Button */}
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">Sync Configurations</h2>
            <p className="text-muted-foreground">
              Automatically sync documents from SharePoint to your knowledge base
            </p>
          </div>
          <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={fetchSharePointSites}>
                <Plus className="h-4 w-4 mr-2" />
                Add SharePoint Site
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add SharePoint Site</DialogTitle>
                <DialogDescription>
                  Select a SharePoint site to sync documents from
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label>SharePoint Site</Label>
                  <Select value={selectedSite} onValueChange={setSelectedSite}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a site" />
                    </SelectTrigger>
                    <SelectContent>
                      {sharePointSites.map((site) => (
                        <SelectItem key={site.id} value={site.id}>
                          {site.displayName}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <DialogFooter>
                <Button
                  variant="outline"
                  onClick={() => setIsAddDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button onClick={handleAddConfig} disabled={!selectedSite}>
                  Add Site
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        {/* Sync Configurations */}
        <div className="grid gap-4">
          {configs.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <Cloud className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  No SharePoint sites configured yet
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  Click "Add SharePoint Site" to get started
                </p>
              </CardContent>
            </Card>
          ) : (
            configs.map((config) => (
              <Card key={config.id}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {config.site_name}
                        <Badge variant={config.sync_enabled ? "default" : "secondary"}>
                          {config.sync_enabled ? "Enabled" : "Disabled"}
                        </Badge>
                      </CardTitle>
                      <CardDescription className="mt-1">
                        {config.site_url}
                        {config.library_name && ` • ${config.library_name}`}
                      </CardDescription>
                    </div>
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={config.sync_enabled}
                        onCheckedChange={(enabled) =>
                          handleToggleSync(config.id, enabled)
                        }
                      />
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleSyncNow(config)}
                        disabled={syncing === config.id}
                      >
                        <RefreshCw
                          className={`h-4 w-4 mr-2 ${
                            syncing === config.id ? "animate-spin" : ""
                          }`}
                        />
                        Sync Now
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleDeleteConfig(config.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center gap-4 text-sm text-muted-foreground">
                    <div className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      Sync every {config.sync_frequency_minutes} minutes
                    </div>
                    {config.last_sync_at && (
                      <div>
                        Last synced:{" "}
                        {new Date(config.last_sync_at).toLocaleString()}
                      </div>
                    )}
                    {config.filter_extensions && (
                      <div>
                        Filter: {config.filter_extensions.join(", ")}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Sync Logs */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Sync Activity</CardTitle>
            <CardDescription>History of SharePoint sync operations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {logs.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <FileText className="h-12 w-12 mx-auto mb-2 opacity-50" />
                  <p>No sync activity yet</p>
                </div>
              ) : (
                logs.map((log) => (
                  <div
                    key={log.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      {log.status === "completed" ? (
                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                      ) : log.status === "failed" ? (
                        <XCircle className="h-5 w-5 text-red-600" />
                      ) : (
                        <RefreshCw className="h-5 w-5 animate-spin text-blue-600" />
                      )}
                      <div>
                        <p className="font-medium">
                          {log.files_synced} files synced
                          {log.files_failed > 0 && ` • ${log.files_failed} failed`}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {new Date(log.sync_started_at).toLocaleString()}
                        </p>
                        {log.error_message && (
                          <p className="text-sm text-red-600 mt-1">
                            {log.error_message}
                          </p>
                        )}
                      </div>
                    </div>
                    <Badge
                      variant={
                        log.status === "completed"
                          ? "default"
                          : log.status === "failed"
                          ? "destructive"
                          : "secondary"
                      }
                    >
                      {log.status}
                    </Badge>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default SharePointSync;
