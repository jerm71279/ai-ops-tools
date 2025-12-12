import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";

import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Save } from "lucide-react";
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

const CMDBAddItem = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setLoading(true);

      // Validate form data
      const validatedData = ciSchema.parse(formData);

      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        toast.error("You must be logged in");
        return;
      }

      // Get customer_id
      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) {
        toast.error("User profile not found");
        return;
      }

      // Insert the CI
      const insertData: any = {
        ...validatedData,
        customer_id: profile.customer_id,
        created_by: user.id,
        updated_by: user.id,
      };

      const { data, error } = await supabase
        .from("configuration_items")
        .insert(insertData)
        .select()
        .single();

      if (error) throw error;

      toast.success("Configuration item created successfully");
      navigate(`/cmdb/${data.id}`);
    } catch (error) {
      console.error("Error creating CI:", error);
      if (error instanceof z.ZodError) {
        toast.error(error.errors[0].message);
      } else {
        toast.error("Failed to create configuration item");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="min-h-screen bg-background">
      
      <div className="container mx-auto px-4 pb-8 pt-8" style={{ marginTop: 'var(--lanes-height, 0px)' }}>
        <DashboardNavigation
          title="Add Configuration Item"
          dashboards={[
            { name: "CMDB Dashboard", path: "/cmdb" },
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
              <Button type="button" variant="outline" onClick={() => navigate("/cmdb")}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                <Save className="h-4 w-4 mr-2" />
                {loading ? "Creating..." : "Create CI"}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CMDBAddItem;
