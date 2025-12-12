import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Edit,
  Trash2,
  RefreshCw,
  GitBranch,
  AlertCircle,
  Calendar,
  User,
  Network,
} from "lucide-react";
import { toast } from "sonner";
import CIAuditLog from "@/components/CIAuditLog";
import CIHealthScore from "@/components/CIHealthScore";
import CIRelationshipMap from "@/components/CIRelationshipMap";

interface ConfigurationItem {
  id: string;
  customer_id: string;
  ci_name: string;
  ci_type: string;
  ci_status: string;
  criticality: string;
  description?: string;
  ip_address?: unknown;
  mac_address?: unknown;
  hostname?: string;
  operating_system?: string;
  version?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  location?: string;
  department?: string;
  cost_center?: string;
  purchase_date?: string;
  warranty_expiry?: string;
  attributes?: any;
  created_at: string;
  updated_at: string;
  ninjaone_device_id?: string;
  azure_resource_id?: string;
}

interface Relationship {
  id: string;
  relationship_type: string;
  target_ci_id: string;
  target_ci_name?: string;
  target_ci_type?: string;
  is_critical: boolean;
  description?: string;
}

const CMDBItemDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [ci, setCi] = useState<ConfigurationItem | null>(null);
  const [relationships, setRelationships] = useState<Relationship[]>([]);
  const [changeRequests, setChangeRequests] = useState<any[]>([]);

  useEffect(() => {
    loadCIData();
  }, [id]);

  const loadCIData = async () => {
    try {
      setLoading(true);

      // Fetch CI details
      const { data: ciData, error: ciError } = await supabase
        .from("configuration_items")
        .select("*")
        .eq("id", id)
        .single();

      if (ciError) throw ciError;
      setCi(ciData);

      // Fetch relationships
      const { data: relData, error: relError } = await supabase
        .from("ci_relationships")
        .select(`
          id,
          relationship_type,
          target_ci_id,
          is_critical,
          description,
          target:configuration_items!ci_relationships_target_ci_id_fkey(ci_name, ci_type)
        `)
        .eq("source_ci_id", id);

      if (relError) throw relError;
      
      const formattedRels = (relData || []).map(rel => ({
        ...rel,
        target_ci_name: (rel as any).target?.ci_name,
        target_ci_type: (rel as any).target?.ci_type,
      }));
      setRelationships(formattedRels);

      // Fetch related change requests
      const { data: changeData } = await supabase
        .from("change_requests")
        .select("*")
        .contains("affected_ci_ids", [id])
        .order("created_at", { ascending: false })
        .limit(10);

      setChangeRequests(changeData || []);
    } catch (error) {
      console.error("Error loading CI data:", error);
      toast.error("Failed to load CI details");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this configuration item?")) return;

    try {
      const { error } = await supabase
        .from("configuration_items")
        .delete()
        .eq("id", id);

      if (error) throw error;

      toast.success("CI deleted successfully");
      navigate("/cmdb");
    } catch (error) {
      console.error("Error deleting CI:", error);
      toast.error("Failed to delete CI");
    }
  };

  if (loading || !ci) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      
      <div className="container mx-auto px-4 pb-8 pt-8" style={{ marginTop: 'var(--lanes-height, 0px)' }}>
        <DashboardNavigation
          title="Configuration Item Details"
          dashboards={[
            { name: "CMDB Dashboard", path: "/cmdb" },
            { name: "Change Management", path: "/change-management" },
          ]}
        />

        {/* Header */}
        <div className="flex items-center justify-end gap-2 mb-6">
          <Button variant="outline" onClick={() => navigate(`/cmdb/${id}/edit`)}>
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="destructive" onClick={handleDelete}>
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </Button>
        </div>

        {/* CI Overview Card */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl">{ci.ci_name}</CardTitle>
                <CardDescription className="mt-2">{ci.description || "No description provided"}</CardDescription>
              </div>
              <div className="flex gap-2">
                <Badge variant={ci.ci_status === "active" ? "default" : "secondary"}>
                  {ci.ci_status}
                </Badge>
                <Badge variant={
                  ci.criticality === "critical" ? "destructive" :
                  ci.criticality === "high" ? "default" : "secondary"
                }>
                  {ci.criticality}
                </Badge>
                {ci.ninjaone_device_id && (
                  <Badge variant="outline" className="bg-green-500/10">NinjaOne</Badge>
                )}
                {ci.azure_resource_id && (
                  <Badge variant="outline" className="bg-blue-500/10">Azure</Badge>
                )}
              </div>
            </div>
          </CardHeader>
        </Card>

        <Tabs defaultValue="details" className="space-y-6">
          <TabsList>
            <TabsTrigger value="details">Details</TabsTrigger>
            <TabsTrigger value="health">Health & Metrics</TabsTrigger>
            <TabsTrigger value="relationships">
              Relationships ({relationships.length})
            </TabsTrigger>
            <TabsTrigger value="relationship-map">Relationship Map</TabsTrigger>
            <TabsTrigger value="audit">Audit Log</TabsTrigger>
            <TabsTrigger value="changes">
              Change History ({changeRequests.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="details">
            <div className="grid gap-6 md:grid-cols-2">
              {/* Technical Details */}
              <Card>
                <CardHeader>
                  <CardTitle>Technical Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <span className="text-muted-foreground">Type:</span>
                    <span className="font-medium capitalize">{ci.ci_type.replace("_", " ")}</span>
                    
                    {ci.hostname && (
                      <>
                        <span className="text-muted-foreground">Hostname:</span>
                        <span className="font-medium">{ci.hostname}</span>
                      </>
                    )}
                    
                    {ci.ip_address && (
                      <>
                        <span className="text-muted-foreground">IP Address:</span>
                        <span className="font-medium">{String(ci.ip_address)}</span>
                      </>
                    )}
                    
                    {ci.mac_address && (
                      <>
                        <span className="text-muted-foreground">MAC Address:</span>
                        <span className="font-medium">{String(ci.mac_address)}</span>
                      </>
                    )}
                    
                    {ci.operating_system && (
                      <>
                        <span className="text-muted-foreground">OS:</span>
                        <span className="font-medium">{ci.operating_system}</span>
                      </>
                    )}
                    
                    {ci.version && (
                      <>
                        <span className="text-muted-foreground">Version:</span>
                        <span className="font-medium">{ci.version}</span>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Hardware Details */}
              <Card>
                <CardHeader>
                  <CardTitle>Hardware Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    {ci.manufacturer && (
                      <>
                        <span className="text-muted-foreground">Manufacturer:</span>
                        <span className="font-medium">{ci.manufacturer}</span>
                      </>
                    )}
                    
                    {ci.model && (
                      <>
                        <span className="text-muted-foreground">Model:</span>
                        <span className="font-medium">{ci.model}</span>
                      </>
                    )}
                    
                    {ci.serial_number && (
                      <>
                        <span className="text-muted-foreground">Serial Number:</span>
                        <span className="font-medium">{ci.serial_number}</span>
                      </>
                    )}
                    
                    {ci.location && (
                      <>
                        <span className="text-muted-foreground">Location:</span>
                        <span className="font-medium">{ci.location}</span>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Business Details */}
              <Card>
                <CardHeader>
                  <CardTitle>Business Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    {ci.department && (
                      <>
                        <span className="text-muted-foreground">Department:</span>
                        <span className="font-medium">{ci.department}</span>
                      </>
                    )}
                    
                    {ci.cost_center && (
                      <>
                        <span className="text-muted-foreground">Cost Center:</span>
                        <span className="font-medium">{ci.cost_center}</span>
                      </>
                    )}
                    
                    {ci.purchase_date && (
                      <>
                        <span className="text-muted-foreground">Purchase Date:</span>
                        <span className="font-medium">{new Date(ci.purchase_date).toLocaleDateString()}</span>
                      </>
                    )}
                    
                    {ci.warranty_expiry && (
                      <>
                        <span className="text-muted-foreground">Warranty Expiry:</span>
                        <span className="font-medium">{new Date(ci.warranty_expiry).toLocaleDateString()}</span>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Metadata */}
              <Card>
                <CardHeader>
                  <CardTitle>Metadata</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="grid grid-cols-2 gap-2">
                    <span className="text-muted-foreground">Created:</span>
                    <span className="font-medium">{new Date(ci.created_at).toLocaleString()}</span>
                    
                    <span className="text-muted-foreground">Last Updated:</span>
                    <span className="font-medium">{new Date(ci.updated_at).toLocaleString()}</span>
                    
                    {ci.ninjaone_device_id && (
                      <>
                        <span className="text-muted-foreground">NinjaOne ID:</span>
                        <span className="font-medium">{ci.ninjaone_device_id}</span>
                      </>
                    )}
                    
                    {ci.azure_resource_id && (
                      <>
                        <span className="text-muted-foreground">Azure ID:</span>
                        <span className="font-medium text-xs">{ci.azure_resource_id}</span>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="health">
            <CIHealthScore ciId={id!} customerId={ci.customer_id} />
          </TabsContent>

          <TabsContent value="relationships">
            <Card>
              <CardHeader>
                <CardTitle>Dependencies & Relationships</CardTitle>
                <CardDescription>
                  Configuration items that this CI depends on or is related to
                </CardDescription>
              </CardHeader>
              <CardContent>
                {relationships.length === 0 ? (
                  <div className="text-center py-8">
                    <Network className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No relationships defined</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {relationships.map((rel) => (
                      <Card key={rel.id} className="cursor-pointer hover:shadow-md transition-shadow"
                        onClick={() => navigate(`/cmdb/${rel.target_ci_id}`)}>
                        <CardContent className="pt-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <GitBranch className="h-4 w-4 text-muted-foreground" />
                              <div>
                                <p className="font-medium">{rel.target_ci_name}</p>
                                <p className="text-sm text-muted-foreground capitalize">
                                  {rel.relationship_type.replace("_", " ")} • {rel.target_ci_type}
                                </p>
                              </div>
                            </div>
                            {rel.is_critical && (
                              <Badge variant="destructive">Critical</Badge>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="relationship-map">
            <CIRelationshipMap ciId={id!} ciName={ci.ci_name} />
          </TabsContent>

          <TabsContent value="audit">
            <CIAuditLog ciId={id!} />
          </TabsContent>

          <TabsContent value="changes">
            <Card>
              <CardHeader>
                <CardTitle>Change History</CardTitle>
                <CardDescription>
                  Recent change requests affecting this configuration item
                </CardDescription>
              </CardHeader>
              <CardContent>
                {changeRequests.length === 0 ? (
                  <div className="text-center py-8">
                    <Calendar className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No change requests found</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {changeRequests.map((change) => (
                      <Card key={change.id} className="cursor-pointer hover:shadow-md transition-shadow"
                        onClick={() => navigate(`/change-management/${change.id}`)}>
                        <CardContent className="pt-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <p className="font-medium">{change.title}</p>
                              <p className="text-sm text-muted-foreground">
                                {change.change_number} • {new Date(change.created_at).toLocaleDateString()}
                              </p>
                            </div>
                            <div className="flex gap-2">
                              <Badge variant={
                                change.change_status === "completed" ? "default" :
                                change.change_status === "in_progress" ? "secondary" : "outline"
                              }>
                                {change.change_status}
                              </Badge>
                              <Badge variant={
                                change.risk_level === "high" ? "destructive" : "outline"
                              }>
                                {change.risk_level} risk
                              </Badge>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default CMDBItemDetail;
