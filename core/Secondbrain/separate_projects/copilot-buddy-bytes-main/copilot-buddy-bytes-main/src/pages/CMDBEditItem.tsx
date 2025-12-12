import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Save, RefreshCw } from "lucide-react";
import { toast } from "sonner";
import { z } from "zod";

const ciSchema = z.object({
  ci_name: z.string().trim().min(1, "CI name is required").max(200),
  ci_type: z.string().min(1, "CI type is required"),
  ci_status: z.string().min(1, "CI status is required"),
  criticality: z.string().min(1, "Criticality is required"),
  description: z.string().max(1000).optional(),
  hostname: z.string().max(200).optional(),
  ip_address: z.string().max(45).optional(),
  mac_address: z.string().max(17).optional(),
  operating_system: z.string().max(200).optional(),
  version: z.string().max(100).optional(),
  manufacturer: z.string().max(200).optional(),
  model: z.string().max(200).optional(),
  serial_number: z.string().max(200).optional(),
  location: z.string().max(200).optional(),
  department: z.string().max(200).optional(),
  cost_center: z.string().max(100).optional(),
});

const CMDBEditItem = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    ci_name: "",
    ci_type: "hardware",
    ci_status: "active",
    criticality: "medium",
    description: "",
    hostname: "",
    ip_address: "",
    mac_address: "",
    operating_system: "",
    version: "",
    manufacturer: "",
    model: "",
    serial_number: "",
    location: "",
    department: "",
    cost_center: "",
  });

  useEffect(() => {
    loadCI();
  }, [id]);

  const loadCI = async () => {
    try {
      setLoading(true);

      const { data, error } = await supabase
        .from("configuration_items")
        .select("*")
        .eq("id", id)
        .single();

      if (error) throw error;

      setFormData({
        ci_name: data.ci_name || "",
        ci_type: data.ci_type || "hardware",
        ci_status: data.ci_status || "active",
        criticality: data.criticality || "medium",
        description: data.description || "",
        hostname: data.hostname || "",
        ip_address: data.ip_address ? String(data.ip_address) : "",
        mac_address: data.mac_address ? String(data.mac_address) : "",
        operating_system: data.operating_system || "",
        version: data.version || "",
        manufacturer: data.manufacturer || "",
        model: data.model || "",
        serial_number: data.serial_number || "",
        location: data.location || "",
        department: data.department || "",
        cost_center: data.cost_center || "",
      });
    } catch (error) {
      console.error("Error loading CI:", error);
      toast.error("Failed to load configuration item");
      navigate("/cmdb");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setSaving(true);

      // Validate form data
      const validatedData = ciSchema.parse(formData);

      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        toast.error("You must be logged in");
        return;
      }

      // Update the CI
      const updateData: any = {
        ...validatedData,
        updated_by: user.id,
      };

      const { error } = await supabase
        .from("configuration_items")
        .update(updateData)
        .eq("id", id);

      if (error) throw error;

      toast.success("Configuration item updated successfully");
      navigate(`/cmdb/${id}`);
    } catch (error) {
      console.error("Error updating CI:", error);
      if (error instanceof z.ZodError) {
        toast.error(error.errors[0].message);
      } else {
        toast.error("Failed to update configuration item");
      }
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (loading) {
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
          title="Edit Configuration Item"
          dashboards={[
            { name: "CMDB Dashboard", path: "/cmdb" },
            { name: "CI Detail", path: `/cmdb/${id}` },
          ]}
        />

        <form onSubmit={handleSubmit}>
          <div className="grid gap-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle>Basic Information</CardTitle>
                <CardDescription>Core details about the configuration item</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="ci_name">CI Name *</Label>
                    <Input
                      id="ci_name"
                      value={formData.ci_name}
                      onChange={(e) => handleChange("ci_name", e.target.value)}
                      required
                      maxLength={200}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="ci_type">CI Type *</Label>
                    <Select value={formData.ci_type} onValueChange={(v) => handleChange("ci_type", v)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="hardware">Hardware</SelectItem>
                        <SelectItem value="software">Software</SelectItem>
                        <SelectItem value="network_device">Network Device</SelectItem>
                        <SelectItem value="cloud_resource">Cloud Resource</SelectItem>
                        <SelectItem value="security_device">Security Device</SelectItem>
                        <SelectItem value="database">Database</SelectItem>
                        <SelectItem value="application">Application</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="ci_status">Status *</Label>
                    <Select value={formData.ci_status} onValueChange={(v) => handleChange("ci_status", v)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="inactive">Inactive</SelectItem>
                        <SelectItem value="maintenance">Maintenance</SelectItem>
                        <SelectItem value="retired">Retired</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="criticality">Criticality *</Label>
                    <Select value={formData.criticality} onValueChange={(v) => handleChange("criticality", v)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => handleChange("description", e.target.value)}
                    rows={3}
                    maxLength={1000}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Technical Details */}
            <Card>
              <CardHeader>
                <CardTitle>Technical Details</CardTitle>
                <CardDescription>Network and system information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="hostname">Hostname</Label>
                    <Input
                      id="hostname"
                      value={formData.hostname}
                      onChange={(e) => handleChange("hostname", e.target.value)}
                      maxLength={200}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="ip_address">IP Address</Label>
                    <Input
                      id="ip_address"
                      value={formData.ip_address}
                      onChange={(e) => handleChange("ip_address", e.target.value)}
                      maxLength={45}
                      placeholder="192.168.1.1"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="mac_address">MAC Address</Label>
                    <Input
                      id="mac_address"
                      value={formData.mac_address}
                      onChange={(e) => handleChange("mac_address", e.target.value)}
                      maxLength={17}
                      placeholder="00:00:00:00:00:00"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="operating_system">Operating System</Label>
                    <Input
                      id="operating_system"
                      value={formData.operating_system}
                      onChange={(e) => handleChange("operating_system", e.target.value)}
                      maxLength={200}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="version">Version</Label>
                    <Input
                      id="version"
                      value={formData.version}
                      onChange={(e) => handleChange("version", e.target.value)}
                      maxLength={100}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Hardware Details */}
            <Card>
              <CardHeader>
                <CardTitle>Hardware Details</CardTitle>
                <CardDescription>Physical device information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="manufacturer">Manufacturer</Label>
                    <Input
                      id="manufacturer"
                      value={formData.manufacturer}
                      onChange={(e) => handleChange("manufacturer", e.target.value)}
                      maxLength={200}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="model">Model</Label>
                    <Input
                      id="model"
                      value={formData.model}
                      onChange={(e) => handleChange("model", e.target.value)}
                      maxLength={200}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="serial_number">Serial Number</Label>
                    <Input
                      id="serial_number"
                      value={formData.serial_number}
                      onChange={(e) => handleChange("serial_number", e.target.value)}
                      maxLength={200}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      value={formData.location}
                      onChange={(e) => handleChange("location", e.target.value)}
                      maxLength={200}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Business Details */}
            <Card>
              <CardHeader>
                <CardTitle>Business Details</CardTitle>
                <CardDescription>Organizational information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-4 md:grid-cols-2">
                  <div className="space-y-2">
                    <Label htmlFor="department">Department</Label>
                    <Input
                      id="department"
                      value={formData.department}
                      onChange={(e) => handleChange("department", e.target.value)}
                      maxLength={200}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="cost_center">Cost Center</Label>
                    <Input
                      id="cost_center"
                      value={formData.cost_center}
                      onChange={(e) => handleChange("cost_center", e.target.value)}
                      maxLength={100}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex justify-end gap-4">
              <Button type="button" variant="outline" onClick={() => navigate(`/cmdb/${id}`)}>
                Cancel
              </Button>
              <Button type="submit" disabled={saving}>
                <Save className="h-4 w-4 mr-2" />
                {saving ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CMDBEditItem;
