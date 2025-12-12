import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { ArrowLeft, Save, Server } from "lucide-react";
import { toast } from "sonner";
import { networkDeviceSchema, sanitizeText } from "@/lib/validation";
import { z } from "zod";

const NetworkDeviceNew = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    device_name: "",
    device_type: "router",
    ip_address: "",
    location: "",
    snmp_community: "",
    snmp_version: "v2c",
    snmp_port: "161",
    polling_enabled: true,
    polling_interval: "300",
    description: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setLoading(true);

      // Validate form data
      const validatedData = networkDeviceSchema.parse({
        device_name: formData.device_name,
        device_type: formData.device_type as any,
        ip_address: formData.ip_address,
        location: formData.location || undefined,
        snmp_community: formData.snmp_community || undefined,
        snmp_version: formData.snmp_version as any,
        polling_interval: parseInt(formData.polling_interval) || undefined,
      });

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
        .maybeSingle();

      if (!profile?.customer_id) {
        toast.error("User profile not found");
        return;
      }

      // Insert the network device
      const { error } = await supabase
        .from("network_devices")
        .insert({
          customer_id: profile.customer_id,
          device_name: validatedData.device_name,
          device_type: validatedData.device_type,
          ip_address: validatedData.ip_address,
          location: validatedData.location,
          snmp_community: validatedData.snmp_community,
          snmp_version: validatedData.snmp_version,
          snmp_port: parseInt(formData.snmp_port) || 161,
          polling_enabled: formData.polling_enabled,
          polling_interval_seconds: validatedData.polling_interval,
          description: formData.description ? sanitizeText(formData.description) : null,
          status: "active",
          created_by: user.id,
        });

      if (error) throw error;

      toast.success("Network device added successfully");
      navigate("/network-monitoring");
    } catch (error: any) {
      console.error("Error creating network device:", error);
      if (error instanceof z.ZodError) {
        const firstError = error.errors[0];
        toast.error(`${firstError.path.join(".")}: ${firstError.message}`);
      } else {
        toast.error(error.message || "Failed to add network device");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation
        dashboards={[
          { name: "Dashboard", path: "/portal" },
          { name: "Network Monitoring", path: "/network-monitoring" },
        ]}
      />
      
      <main className="container mx-auto px-4 pt-56 pb-8">
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/network-monitoring")}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Network Monitoring
          </Button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="grid gap-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <Server className="h-5 w-5 text-primary" />
                  <CardTitle>Basic Device Information</CardTitle>
                </div>
                <CardDescription>Core device identification and network settings</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="device_name">Device Name *</Label>
                    <Input
                      id="device_name"
                      value={formData.device_name}
                      onChange={(e) => setFormData({ ...formData, device_name: e.target.value })}
                      placeholder="e.g., Router-Core-01"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="device_type">Device Type *</Label>
                    <Select
                      value={formData.device_type}
                      onValueChange={(value) => setFormData({ ...formData, device_type: value })}
                    >
                      <SelectTrigger id="device_type">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="router">Router</SelectItem>
                        <SelectItem value="switch">Switch</SelectItem>
                        <SelectItem value="firewall">Firewall</SelectItem>
                        <SelectItem value="access_point">Access Point</SelectItem>
                        <SelectItem value="load_balancer">Load Balancer</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="ip_address">IP Address *</Label>
                    <Input
                      id="ip_address"
                      value={formData.ip_address}
                      onChange={(e) => setFormData({ ...formData, ip_address: e.target.value })}
                      placeholder="192.168.1.1"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      value={formData.location}
                      onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                      placeholder="Data Center, Rack 3, U12"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Additional device information..."
                    rows={3}
                  />
                </div>
              </CardContent>
            </Card>

            {/* SNMP Configuration */}
            <Card>
              <CardHeader>
                <CardTitle>SNMP Configuration</CardTitle>
                <CardDescription>Simple Network Management Protocol settings for monitoring</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="snmp_version">SNMP Version</Label>
                    <Select
                      value={formData.snmp_version}
                      onValueChange={(value) => setFormData({ ...formData, snmp_version: value })}
                    >
                      <SelectTrigger id="snmp_version">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="v1">v1</SelectItem>
                        <SelectItem value="v2c">v2c</SelectItem>
                        <SelectItem value="v3">v3</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="snmp_community">SNMP Community String</Label>
                    <Input
                      id="snmp_community"
                      type="password"
                      value={formData.snmp_community}
                      onChange={(e) => setFormData({ ...formData, snmp_community: e.target.value })}
                      placeholder="public"
                    />
                  </div>
                  <div>
                    <Label htmlFor="snmp_port">SNMP Port</Label>
                    <Input
                      id="snmp_port"
                      type="number"
                      value={formData.snmp_port}
                      onChange={(e) => setFormData({ ...formData, snmp_port: e.target.value })}
                      placeholder="161"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label htmlFor="polling_enabled">Enable Polling</Label>
                      <p className="text-sm text-muted-foreground">
                        Automatically collect device metrics
                      </p>
                    </div>
                    <Switch
                      id="polling_enabled"
                      checked={formData.polling_enabled}
                      onCheckedChange={(checked) => setFormData({ ...formData, polling_enabled: checked })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="polling_interval">Polling Interval (seconds)</Label>
                    <Input
                      id="polling_interval"
                      type="number"
                      value={formData.polling_interval}
                      onChange={(e) => setFormData({ ...formData, polling_interval: e.target.value })}
                      placeholder="300"
                      min="30"
                      max="3600"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Range: 30-3600 seconds
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Submit Button */}
            <div className="flex justify-end gap-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate("/network-monitoring")}
                disabled={loading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                <Save className="h-4 w-4 mr-2" />
                {loading ? "Adding Device..." : "Add Device"}
              </Button>
            </div>
          </div>
        </form>
      </main>
    </div>
  );
};

export default NetworkDeviceNew;
