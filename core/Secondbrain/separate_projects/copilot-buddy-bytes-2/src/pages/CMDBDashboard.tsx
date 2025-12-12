import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Database,
  Server,
  HardDrive,
  Network,
  Cloud,
  Shield,
  Plus,
  Search,
  GitBranch,
  AlertCircle,
  TrendingUp,
  RefreshCw,
} from "lucide-react";
import { toast } from "sonner";

/**
 * CMDB Dashboard Data Flow
 * 
 * ```mermaid
 * graph TD
 *     A[User] -->|Visits /cmdb| B[CMDBDashboard Component]
 *     B -->|useEffect| C[checkAccess & loadCMDBData]
 *     C -->|Auth Check| D[supabase.auth.getUser]
 *     
 *     D -->|Authenticated| E[Query CIs]
 *     E -->|Filter by Type| F[configuration_items Table]
 *     E -->|Filter by Status| F
 *     F -->|Return CIs| G[setCis State]
 *     
 *     G -->|Calculate| H[Stats: total, critical, active, synced]
 *     H -->|Update| I[Stats Cards UI]
 *     
 *     J[NinjaOne Sync Button] -->|Invoke| K[ninjaone-sync Edge Function]
 *     K -->|API Call| L[NinjaOne API]
 *     L -->|Device Data| M[Transform to CI Format]
 *     M -->|Upsert| F
 *     M -->|Reload| E
 *     
 *     N[Add CI Button] -->|Navigate| O[/cmdb/add]
 *     
 *     G -->|Search Filter| P[filteredCis]
 *     P -->|Render| Q[CI Cards UI]
 *     Q -->|Click CI| R[Navigate to /cmdb/:id]
 *     
 *     S[Azure Sync] -.->|Future| F
 *     
 *     style A fill:#e1f5ff
 *     style K fill:#fff4e6
 *     style L fill:#e6ffe6
 *     style F fill:#e6f7ff
 *     style Q fill:#f0f0f0
 * ```
 */

interface ConfigurationItem {
  id: string;
  ci_name: string;
  ci_type: string;
  ci_status: string;
  criticality: string;
  ip_address?: unknown;
  operating_system?: string;
  department?: string;
  ninjaone_device_id?: string;
  azure_resource_id?: string;
  created_at: string;
}

const CMDBDashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [cis, setCis] = useState<ConfigurationItem[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    critical: 0,
    active: 0,
    ninjaone_synced: 0,
    azure_synced: 0,
  });
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");

  useEffect(() => {
    checkAccess();
  }, []);

  const checkAccess = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      navigate("/auth");
      return;
    }
    await loadCMDBData();
  };

  const loadCMDBData = async () => {
    try {
      setLoading(true);

      // Fetch configuration items
      let query = supabase
        .from("configuration_items")
        .select("*")
        .order("created_at", { ascending: false });

      if (filterType !== "all") {
        query = query.eq("ci_type", filterType as any);
      }
      if (filterStatus !== "all") {
        query = query.eq("ci_status", filterStatus as any);
      }

      const { data: cisData, error: cisError } = await query;
      if (cisError) throw cisError;

      setCis((cisData || []) as any);

      // Calculate stats
      const total = cisData?.length || 0;
      const critical = cisData?.filter(ci => ci.criticality === "critical").length || 0;
      const active = cisData?.filter(ci => ci.ci_status === "active").length || 0;
      const ninjaone_synced = cisData?.filter(ci => ci.ninjaone_device_id).length || 0;
      const azure_synced = cisData?.filter(ci => ci.azure_resource_id).length || 0;

      setStats({ total, critical, active, ninjaone_synced, azure_synced });
    } catch (error) {
      console.error("Error loading CMDB data:", error);
      toast.error("Failed to load CMDB data");
    } finally {
      setLoading(false);
    }
  };

  const syncNinjaOneDevices = async () => {
    try {
      setLoading(true);
      toast.info('Starting NinjaOne sync...');
      
      const { data, error } = await supabase.functions.invoke('ninjaone-sync');
      
      if (error) throw error;
      
      if (data.success) {
        toast.success(data.message);
        console.log('Sync stats:', data.stats);
        
        // Reload the CMDB data after sync
        await loadCMDBData();
      } else {
        toast.error(data.error || 'Sync failed');
      }
    } catch (error) {
      console.error('NinjaOne sync error:', error);
      toast.error('Failed to sync with NinjaOne');
    } finally {
      setLoading(false);
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "server": return <Server className="h-4 w-4" />;
      case "workstation": return <HardDrive className="h-4 w-4" />;
      case "network_device": return <Network className="h-4 w-4" />;
      case "cloud_resource": return <Cloud className="h-4 w-4" />;
      case "security_device": return <Shield className="h-4 w-4" />;
      default: return <Database className="h-4 w-4" />;
    }
  };

  const getCriticalityColor = (criticality: string) => {
    switch (criticality) {
      case "critical": return "destructive";
      case "high": return "default";
      case "medium": return "secondary";
      default: return "outline";
    }
  };

  const filteredCis = cis.filter(ci =>
    ci.ci_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (typeof ci.ip_address === 'string' && ci.ip_address.includes(searchTerm)) ||
    ci.operating_system?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      <div className="container mx-auto px-4 pb-8 pt-8" style={{ marginTop: 'var(--lanes-height, 0px)' }}>

        {/* Floating Add CI Button - Partially Hidden */}
        <Button
          onClick={() => navigate("/cmdb/add")}
          className="fixed -right-8 hover:right-0 transition-all duration-300 rounded-l-lg rounded-r-none shadow-lg z-50 px-4 py-6 bg-primary hover:bg-primary/90"
          style={{ top: 'calc(var(--lanes-bottom, var(--lanes-height, 0px)) + 0.75rem)' }}
          title="Add Configuration Item"
        >
          <Plus className="h-5 w-5" />
        </Button>

        {/* Main Content */}
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle className="text-2xl">Configuration Items</CardTitle>
                <CardDescription>Manage your IT assets and infrastructure components</CardDescription>
              </div>
              <div className="flex flex-wrap gap-2 overflow-x-auto">
                <Button onClick={() => navigate("/cmdb/reconciliation")} variant="outline">
                  <GitBranch className="h-4 w-4 mr-2" />
                  Reconciliation
                </Button>
                <Button onClick={syncNinjaOneDevices} variant="outline">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Sync NinjaOne
                </Button>
                <Button onClick={() => navigate("/cmdb/add")}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add CI
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {/* Filters */}
            <div className="flex gap-4 mb-6">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by name, IP, or OS..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={filterType} onValueChange={setFilterType}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Filter by type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="server">Server</SelectItem>
                  <SelectItem value="workstation">Workstation</SelectItem>
                  <SelectItem value="network_device">Network Device</SelectItem>
                  <SelectItem value="cloud_resource">Cloud Resource</SelectItem>
                  <SelectItem value="security_device">Security Device</SelectItem>
                </SelectContent>
              </Select>
              <Select value={filterStatus} onValueChange={setFilterStatus}>
                <SelectTrigger className="w-[180px]">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="inactive">Inactive</SelectItem>
                  <SelectItem value="maintenance">Maintenance</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* CI List */}
            <div className="space-y-4">
              {filteredCis.length === 0 ? (
                <div className="text-center py-12">
                  <Database className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Configuration Items Found</h3>
                  <p className="text-muted-foreground mb-4">
                    {searchTerm || filterType !== "all" || filterStatus !== "all"
                      ? "Try adjusting your filters"
                      : "Start by adding your first CI or syncing from NinjaOne"}
                  </p>
                  <Button onClick={() => navigate("/cmdb/add")}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Configuration Item
                  </Button>
                </div>
              ) : (
                filteredCis.map((ci) => (
                  <Card key={ci.id} className="hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => navigate(`/cmdb/${ci.id}`)}>
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 flex-1">
                          <div className="p-3 bg-accent/10 rounded-lg">
                            {getTypeIcon(ci.ci_type)}
                          </div>
                          <div className="flex-1">
                            <h4 className="font-semibold">{ci.ci_name}</h4>
                            <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                              <span className="capitalize">{ci.ci_type.replace("_", " ")}</span>
                              {ci.ip_address && <span>IP: {String(ci.ip_address)}</span>}
                              {ci.operating_system && <span>{ci.operating_system}</span>}
                              {ci.department && <span>{ci.department}</span>}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant={getCriticalityColor(ci.criticality)}>
                            {ci.criticality}
                          </Badge>
                          <Badge variant={ci.ci_status === "active" ? "default" : "secondary"}>
                            {ci.ci_status}
                          </Badge>
                          {ci.ninjaone_device_id && (
                            <Badge variant="outline" className="bg-green-500/10">
                              NinjaOne
                            </Badge>
                          )}
                          {ci.azure_resource_id && (
                            <Badge variant="outline" className="bg-blue-500/10">
                              Azure
                            </Badge>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mt-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total CIs</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Critical Assets</CardTitle>
              <AlertCircle className="h-4 w-4 text-destructive" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-destructive">{stats.critical}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.active}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">NinjaOne Synced</CardTitle>
              <GitBranch className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.ninjaone_synced}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Azure Synced</CardTitle>
              <Cloud className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.azure_synced}</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default CMDBDashboard;
