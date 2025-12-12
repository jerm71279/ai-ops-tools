import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  GitMerge, 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw,
  Server,
  Network
} from "lucide-react";
import { toast } from "sonner";

interface DuplicateGroup {
  matchType: string;
  confidence: number;
  cis: Array<{
    id: string;
    ci_name: string;
    ci_type: string;
    ip_address?: string;
    hostname?: string;
    serial_number?: string;
    mac_address?: string;
    integration_source?: string;
    created_at: string;
  }>;
}

const CMDBReconciliation = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [duplicates, setDuplicates] = useState<DuplicateGroup[]>([]);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    checkAccess();
  }, []);

  const checkAccess = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      navigate("/auth");
      return;
    }
    await analyzeDuplicates();
  };

  const analyzeDuplicates = async () => {
    try {
      setAnalyzing(true);
      
      // Fetch all CIs
      const { data: cis, error } = await supabase
        .from("configuration_items")
        .select(`
          id,
          ci_name,
          ci_type,
          ip_address,
          hostname,
          serial_number,
          mac_address,
          integration_source,
          created_at
        `)
        .order("created_at", { ascending: false });

      if (error) throw error;

      // Detect duplicates using various matching strategies
      const duplicateGroups: DuplicateGroup[] = [];

      // 1. Match by serial number
      const serialGroups = new Map<string, any[]>();
      cis?.forEach(ci => {
        if (ci.serial_number) {
          const key = ci.serial_number.toLowerCase().trim();
          if (!serialGroups.has(key)) {
            serialGroups.set(key, []);
          }
          serialGroups.get(key)!.push(ci);
        }
      });
      serialGroups.forEach((group, serial) => {
        if (group.length > 1) {
          duplicateGroups.push({
            matchType: `Serial Number: ${serial}`,
            confidence: 95,
            cis: group,
          });
        }
      });

      // 2. Match by MAC address
      const macGroups = new Map<string, any[]>();
      cis?.forEach(ci => {
        if (ci.mac_address) {
          const key = String(ci.mac_address).toLowerCase().replace(/[:-]/g, "");
          if (!macGroups.has(key)) {
            macGroups.set(key, []);
          }
          macGroups.get(key)!.push(ci);
        }
      });
      macGroups.forEach((group, mac) => {
        if (group.length > 1) {
          duplicateGroups.push({
            matchType: `MAC Address: ${mac}`,
            confidence: 90,
            cis: group,
          });
        }
      });

      // 3. Match by hostname + IP
      const hostIpGroups = new Map<string, any[]>();
      cis?.forEach(ci => {
        if (ci.hostname && ci.ip_address) {
          const key = `${ci.hostname.toLowerCase()}_${ci.ip_address}`;
          if (!hostIpGroups.has(key)) {
            hostIpGroups.set(key, []);
          }
          hostIpGroups.get(key)!.push(ci);
        }
      });
      hostIpGroups.forEach((group, key) => {
        if (group.length > 1) {
          duplicateGroups.push({
            matchType: `Hostname + IP: ${key}`,
            confidence: 85,
            cis: group,
          });
        }
      });

      // 4. Fuzzy match by name (similar names)
      const nameGroups = new Map<string, any[]>();
      cis?.forEach(ci => {
        // Normalize name for fuzzy matching
        const normalized = ci.ci_name
          .toLowerCase()
          .replace(/[^a-z0-9]/g, "")
          .substring(0, 20);
        
        if (!nameGroups.has(normalized)) {
          nameGroups.set(normalized, []);
        }
        nameGroups.get(normalized)!.push(ci);
      });
      nameGroups.forEach((group, name) => {
        if (group.length > 1) {
          duplicateGroups.push({
            matchType: `Similar Name: ${name}`,
            confidence: 60,
            cis: group,
          });
        }
      });

      setDuplicates(duplicateGroups);
      
      if (duplicateGroups.length === 0) {
        toast.success("No duplicates found - CMDB is clean!");
      } else {
        toast.info(`Found ${duplicateGroups.length} potential duplicate groups`);
      }
    } catch (error) {
      console.error("Error analyzing duplicates:", error);
      toast.error("Failed to analyze duplicates");
    } finally {
      setLoading(false);
      setAnalyzing(false);
    }
  };

  const mergeCIs = async (groupIndex: number, keepId: string) => {
    try {
      const group = duplicates[groupIndex];
      const idsToDelete = group.cis
        .filter(ci => ci.id !== keepId)
        .map(ci => ci.id);

      // Update relationships to point to the kept CI
      for (const oldId of idsToDelete) {
        await supabase
          .from("ci_relationships")
          .update({ source_ci_id: keepId })
          .eq("source_ci_id", oldId);

        await supabase
          .from("ci_relationships")
          .update({ target_ci_id: keepId })
          .eq("target_ci_id", oldId);

        // Update change requests
        const { data: changes } = await supabase
          .from("change_requests")
          .select("id, affected_ci_ids")
          .contains("affected_ci_ids", [oldId]);

        if (changes) {
          for (const change of changes) {
            const newIds = change.affected_ci_ids.map((id: string) => 
              id === oldId ? keepId : id
            );
            await supabase
              .from("change_requests")
              .update({ affected_ci_ids: newIds })
              .eq("id", change.id);
          }
        }

        // Delete the duplicate CI
        await supabase
          .from("configuration_items")
          .delete()
          .eq("id", oldId);
      }

      toast.success(`Merged ${idsToDelete.length} duplicate CI(s)`);
      
      // Refresh the list
      await analyzeDuplicates();
    } catch (error) {
      console.error("Error merging CIs:", error);
      toast.error("Failed to merge CIs");
    }
  };

  const dismissGroup = (groupIndex: number) => {
    setDuplicates(prev => prev.filter((_, i) => i !== groupIndex));
    toast.info("Duplicate group dismissed");
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return "destructive";
    if (confidence >= 75) return "default";
    return "secondary";
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      <main className="container mx-auto px-4 pb-8 pt-8" style={{ marginTop: 'var(--lanes-height, 0px)' }}>
        <div className="flex justify-end mb-6">
          <Button onClick={analyzeDuplicates} disabled={analyzing}>
            <RefreshCw className={`h-4 w-4 mr-2 ${analyzing ? "animate-spin" : ""}`} />
            Re-analyze
          </Button>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>CI Reconciliation & Duplicate Detection</CardTitle>
            <CardDescription>
              Identify and merge duplicate configuration items from multiple sources
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="flex items-center gap-3 p-4 bg-accent/10 rounded-lg">
                <AlertTriangle className="h-8 w-8 text-yellow-600" />
                <div>
                  <p className="text-2xl font-bold">{duplicates.length}</p>
                  <p className="text-sm text-muted-foreground">Duplicate Groups</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-4 bg-accent/10 rounded-lg">
                <GitMerge className="h-8 w-8 text-blue-600" />
                <div>
                  <p className="text-2xl font-bold">
                    {duplicates.reduce((sum, g) => sum + g.cis.length, 0)}
                  </p>
                  <p className="text-sm text-muted-foreground">Total CIs Affected</p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-4 bg-accent/10 rounded-lg">
                <CheckCircle className="h-8 w-8 text-green-600" />
                <div>
                  <p className="text-2xl font-bold">
                    {duplicates.filter(g => g.confidence >= 90).length}
                  </p>
                  <p className="text-sm text-muted-foreground">High Confidence</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {duplicates.length === 0 ? (
          <Card>
            <CardContent className="py-12">
              <div className="text-center">
                <CheckCircle className="h-16 w-16 mx-auto text-green-600 mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Duplicates Found</h3>
                <p className="text-muted-foreground">
                  Your CMDB is clean and well-maintained!
                </p>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {duplicates.map((group, groupIndex) => (
              <Card key={groupIndex}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <AlertTriangle className="h-5 w-5 text-yellow-600" />
                      <div>
                        <CardTitle className="text-lg">{group.matchType}</CardTitle>
                        <CardDescription>{group.cis.length} potential duplicates</CardDescription>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant={getConfidenceColor(group.confidence)}>
                        {group.confidence}% confidence
                      </Badge>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => dismissGroup(groupIndex)}
                      >
                        Dismiss
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {group.cis.map((ci) => (
                      <div key={ci.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center gap-3 flex-1">
                          <div className="p-2 bg-accent/10 rounded">
                            {ci.ci_type === "network_device" ? (
                              <Network className="h-4 w-4" />
                            ) : (
                              <Server className="h-4 w-4" />
                            )}
                          </div>
                          <div className="flex-1">
                            <p className="font-medium">{ci.ci_name}</p>
                            <div className="flex items-center gap-3 text-sm text-muted-foreground">
                              <span className="capitalize">{ci.ci_type}</span>
                              {ci.ip_address && <span>IP: {ci.ip_address}</span>}
                              {ci.hostname && <span>Host: {ci.hostname}</span>}
                              {ci.serial_number && <span>S/N: {ci.serial_number}</span>}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {ci.integration_source && (
                            <Badge variant="outline">{ci.integration_source}</Badge>
                          )}
                          <Badge variant="secondary">
                            {new Date(ci.created_at).toLocaleDateString()}
                          </Badge>
                          <Button
                            size="sm"
                            variant="default"
                            onClick={() => mergeCIs(groupIndex, ci.id)}
                          >
                            <GitMerge className="h-4 w-4 mr-1" />
                            Keep This
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default CMDBReconciliation;
