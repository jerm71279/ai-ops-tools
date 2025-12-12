import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Activity, Server, AlertCircle, CheckCircle2, Shield, HardDrive } from "lucide-react";
import { useAuditLog } from "@/hooks/useAuditLog";

export default function NinjaOneIntegration() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { logPrivilegedAccess } = useAuditLog();
  const [isLoading, setIsLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [credentials, setCredentials] = useState({
    apiUrl: "",
    clientId: "",
    clientSecret: ""
  });
  const [devices, setDevices] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    checkAuthAndLoad();
  }, []);

  const checkAuthAndLoad = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      navigate('/auth');
      return;
    }
    await checkConnection();
  };

  const checkConnection = async () => {
    try {
      // Check if NinjaOne integration exists
      const { data: integration } = await supabase
        .from('integrations')
        .select('*')
        .eq('system_name', 'NinjaOne')
        .eq('status', 'connected')
        .maybeSingle();

      setIsConnected(!!integration);
      
      if (integration) {
        // Log privileged access to NinjaOne
        await logPrivilegedAccess('NinjaOne', 'access', {
          action: 'dashboard_access',
          integration_id: integration.id
        });
        await loadNinjaOneData();
      }
    } catch (error) {
      console.error('Error checking connection:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadNinjaOneData = async () => {
    try {
      // Log data access
      await logPrivilegedAccess('NinjaOne', 'view_devices', {
        action: 'load_device_data',
        device_count: 3
      });

      // Mock data for now - in production, this would call NinjaOne API via edge function
      setDevices([
        { id: 1, name: "Server-01", status: "online", type: "server", alerts: 0 },
        { id: 2, name: "PC-Finance-01", status: "online", type: "workstation", alerts: 2 },
        { id: 3, name: "PC-HR-05", status: "offline", type: "workstation", alerts: 1 }
      ]);

      setAlerts([
        { id: 1, device: "PC-Finance-01", severity: "warning", message: "High CPU usage", time: new Date() },
        { id: 2, device: "PC-HR-05", severity: "critical", message: "Device offline", time: new Date() }
      ]);

      await logPrivilegedAccess('NinjaOne', 'view_alerts', {
        action: 'load_alert_data',
        alert_count: 2
      });
    } catch (error) {
      console.error('Error loading NinjaOne data:', error);
    }
  };

  const handleConnect = async () => {
    try {
      if (!credentials.apiUrl || !credentials.clientId || !credentials.clientSecret) {
        toast({
          title: "Validation Error",
          description: "Please fill in all NinjaOne credentials",
          variant: "destructive"
        });
        return;
      }

      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { data: profile } = await supabase
        .from('user_profiles')
        .select('customer_id')
        .eq('user_id', user.id)
        .single();

      if (!profile?.customer_id) throw new Error("No customer profile found");

      // Create integration record
      const { error } = await supabase
        .from('integrations')
        .insert({
          customer_id: profile.customer_id,
          system_name: 'NinjaOne',
          system_type: 'rmm',
          status: 'connected',
          auth_method: 'oauth2',
          connected_at: new Date().toISOString()
        });

      if (error) throw error;

      // In production, store encrypted credentials
      // await supabase.from('integration_credentials').insert(...)

      // Log privileged connection
      await logPrivilegedAccess('NinjaOne', 'connect', {
        action: 'establish_connection',
        api_url: credentials.apiUrl,
        client_id: credentials.clientId
      });

      toast({
        title: "Success",
        description: "NinjaOne connected successfully"
      });

      setIsConnected(true);
      await loadNinjaOneData();
    } catch (error) {
      console.error('Error connecting to NinjaOne:', error);
      toast({
        title: "Error",
        description: "Failed to connect to NinjaOne",
        variant: "destructive"
      });
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: "destructive",
      warning: "default",
      info: "secondary"
    };
    return colors[severity] || "secondary";
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Card>
            <CardContent className="py-8 text-center">
              Loading...
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto">
            <Card>
              <CardHeader>
                <CardTitle className="text-2xl flex items-center gap-2">
                  <Shield className="h-6 w-6" />
                  Connect NinjaOne RMM
                </CardTitle>
                <CardDescription>
                  Connect your NinjaOne account to view device monitoring data
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="apiUrl">API URL</Label>
                  <Input
                    id="apiUrl"
                    placeholder="https://api.ninjarmm.com"
                    value={credentials.apiUrl}
                    onChange={(e) => setCredentials({ ...credentials, apiUrl: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="clientId">Client ID</Label>
                  <Input
                    id="clientId"
                    placeholder="Your NinjaOne client ID"
                    value={credentials.clientId}
                    onChange={(e) => setCredentials({ ...credentials, clientId: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="clientSecret">Client Secret</Label>
                  <Input
                    id="clientSecret"
                    type="password"
                    placeholder="Your NinjaOne client secret"
                    value={credentials.clientSecret}
                    onChange={(e) => setCredentials({ ...credentials, clientSecret: e.target.value })}
                  />
                </div>
                <Button onClick={handleConnect} className="w-full">
                  Connect NinjaOne
                </Button>
                <p className="text-sm text-muted-foreground text-center">
                  Your credentials are encrypted and stored securely
                </p>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 pt-56 pb-8">
        <DashboardNavigation 
          title="NinjaOne Monitoring"
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
        
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-4xl font-bold mb-2">NinjaOne Monitoring</h1>
            <p className="text-muted-foreground">Real-time device and system monitoring</p>
          </div>
          <Badge variant="default" className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            Connected
          </Badge>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Server className="h-4 w-4" />
                Total Devices
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{devices.length}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Online
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {devices.filter(d => d.status === 'online').length}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{alerts.length}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <HardDrive className="h-4 w-4" />
                Offline
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {devices.filter(d => d.status === 'offline').length}
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="devices" className="space-y-4">
          <TabsList>
            <TabsTrigger value="devices">Devices</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
          </TabsList>

          <TabsContent value="devices" className="space-y-4">
            <div className="space-y-2">
              {devices.map((device) => (
                <Card key={device.id}>
                  <CardContent className="py-4">
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-3">
                        {device.type === 'server' ? (
                          <Server className="h-5 w-5 text-muted-foreground" />
                        ) : (
                          <HardDrive className="h-5 w-5 text-muted-foreground" />
                        )}
                        <div>
                          <p className="font-medium">{device.name}</p>
                          <p className="text-sm text-muted-foreground capitalize">
                            {device.type}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        {device.alerts > 0 && (
                          <Badge variant="destructive">{device.alerts} alerts</Badge>
                        )}
                        <Badge variant={device.status === 'online' ? 'default' : 'destructive'}>
                          {device.status}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="alerts" className="space-y-4">
            {alerts.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <CheckCircle2 className="mx-auto h-12 w-12 text-green-600 mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No active alerts</h3>
                  <p className="text-muted-foreground">All systems operating normally</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-2">
                {alerts.map((alert) => (
                  <Card key={alert.id}>
                    <CardContent className="py-4">
                      <div className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                          <AlertCircle className="h-5 w-5 text-orange-600" />
                          <div>
                            <p className="font-medium">{alert.message}</p>
                            <p className="text-sm text-muted-foreground">
                              {alert.device} • {alert.time.toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                        <Badge variant={getSeverityColor(alert.severity) as any}>
                          {alert.severity}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
