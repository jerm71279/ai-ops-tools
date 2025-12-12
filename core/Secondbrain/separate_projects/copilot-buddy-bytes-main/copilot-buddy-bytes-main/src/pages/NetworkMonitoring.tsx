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
import { 
  Server, Activity, AlertCircle, Network, 
  Radio, HardDrive, Eye, Search, Plus,
  FileText, TrendingUp, CheckCircle2
} from "lucide-react";
import { toast } from "sonner";

export default function NetworkMonitoring() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [devices, setDevices] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [recentLogs, setRecentLogs] = useState<any[]>([]);
  const [stats, setStats] = useState({
    totalDevices: 0,
    activeDevices: 0,
    openAlerts: 0,
    criticalAlerts: 0,
  });
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    checkAuthAndLoad();
  }, []);

  const checkAuthAndLoad = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) {
      navigate('/auth');
      return;
    }
    await loadData();
  };

  const loadData = async () => {
    try {
      // Load devices
      const { data: devicesData, error: devicesError } = await supabase
        .from('network_devices')
        .select('*')
        .order('device_name');

      if (devicesError) throw devicesError;
      setDevices(devicesData || []);

      // Load alerts
      const { data: alertsData, error: alertsError } = await supabase
        .from('network_alerts')
        .select('*, network_devices(device_name)')
        .eq('status', 'open')
        .order('created_at', { ascending: false })
        .limit(20);

      if (alertsError) throw alertsError;
      setAlerts(alertsData || []);

      // Load recent syslog messages
      const { data: logsData, error: logsError } = await supabase
        .from('syslog_messages')
        .select('*, network_devices(device_name)')
        .order('received_at', { ascending: false })
        .limit(50);

      if (logsError) throw logsError;
      setRecentLogs(logsData || []);

      // Calculate stats
      const activeDevices = devicesData?.filter(d => d.status === 'active').length || 0;
      const criticalAlerts = alertsData?.filter(a => a.severity === 'critical').length || 0;

      setStats({
        totalDevices: devicesData?.length || 0,
        activeDevices,
        openAlerts: alertsData?.length || 0,
        criticalAlerts,
      });

    } catch (error) {
      console.error('Error loading data:', error);
      toast.error('Failed to load monitoring data');
    } finally {
      setIsLoading(false);
    }
  };

  const pollDevice = async (deviceId: string) => {
    try {
      toast.info('Polling device...');
      const { data, error } = await supabase.functions.invoke('device-poller', {
        body: { device_id: deviceId }
      });

      if (error) throw error;
      
      toast.success(`Collected ${data.metrics_collected} metrics from ${data.device}`);
      await loadData();
    } catch (error) {
      console.error('Error polling device:', error);
      toast.error('Failed to poll device');
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, any> = {
      critical: "destructive",
      high: "destructive",
      medium: "default",
      low: "secondary",
      info: "outline"
    };
    return colors[severity] || "secondary";
  };

  const getSeverityLevel = (syslogSeverity: number) => {
    if (syslogSeverity <= 2) return 'critical';
    if (syslogSeverity <= 4) return 'high';
    if (syslogSeverity <= 5) return 'medium';
    return 'info';
  };

  const filteredLogs = recentLogs.filter(log =>
    log.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
    log.hostname?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Card>
            <CardContent className="py-8 text-center">
              Loading network monitoring data...
            </CardContent>
          </Card>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="container mx-auto px-4 pt-56 pb-8">
        <DashboardNavigation 
          title="Network Monitoring"
          dashboards={[
            { name: "IT Dashboard", path: "/dashboard/it" },
            { name: "SOC Dashboard", path: "/dashboard/soc" },
            { name: "CMDB", path: "/cmdb" },
          ]}
        />
        
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-4xl font-bold mb-2">SNMP & Syslog Monitoring</h1>
            <p className="text-muted-foreground">Centralized network device monitoring and log management</p>
          </div>
          <Button onClick={() => navigate('/network-monitoring/devices/new')}>
            <Plus className="h-4 w-4 mr-2" />
            Add Device
          </Button>
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
              <div className="text-2xl font-bold">{stats.totalDevices}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Active Devices
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.activeDevices}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                Open Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">{stats.openAlerts}</div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Eye className="h-4 w-4" />
                Critical Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.criticalAlerts}</div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="devices" className="space-y-4">
          <TabsList>
            <TabsTrigger value="devices">Devices</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
            <TabsTrigger value="logs">Syslog Messages</TabsTrigger>
          </TabsList>

          <TabsContent value="devices" className="space-y-4">
            {devices.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <Server className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No devices configured</h3>
                  <p className="text-muted-foreground mb-4">Add your first network device to start monitoring</p>
                  <Button onClick={() => navigate('/network-monitoring/devices/new')}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Device
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                {devices.map((device) => (
                  <Card key={device.id}>
                    <CardContent className="py-4">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex items-center gap-3">
                          <Network className="h-5 w-5 text-muted-foreground" />
                          <div>
                            <p className="font-medium">{device.device_name}</p>
                            <p className="text-sm text-muted-foreground">{device.ip_address}</p>
                          </div>
                        </div>
                        <Badge variant={device.status === 'active' ? 'default' : 'destructive'}>
                          {device.status}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 gap-2 text-sm mb-3">
                        <div>
                          <span className="text-muted-foreground">Type:</span> {device.device_type}
                        </div>
                        <div>
                          <span className="text-muted-foreground">SNMP:</span> {device.snmp_version}
                        </div>
                        {device.last_poll_at && (
                          <div className="col-span-2">
                            <span className="text-muted-foreground">Last polled:</span>{' '}
                            {new Date(device.last_poll_at).toLocaleString()}
                          </div>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" variant="outline" onClick={() => pollDevice(device.id)}>
                          <TrendingUp className="h-3 w-3 mr-1" />
                          Poll Now
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => navigate(`/network-monitoring/devices/${device.id}`)}>
                          <Eye className="h-3 w-3 mr-1" />
                          View Details
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
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
                      <div className="flex justify-between items-start">
                        <div className="flex items-start gap-3 flex-1">
                          <AlertCircle className="h-5 w-5 text-orange-600 mt-0.5" />
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <p className="font-medium">{alert.title}</p>
                              <Badge variant={getSeverityColor(alert.severity)}>
                                {alert.severity}
                              </Badge>
                            </div>
                            <p className="text-sm text-muted-foreground mb-1">{alert.description}</p>
                            {alert.network_devices && (
                              <p className="text-xs text-muted-foreground">
                                Device: {alert.network_devices.device_name}
                              </p>
                            )}
                            <p className="text-xs text-muted-foreground">
                              {new Date(alert.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        <Button size="sm" variant="outline">
                          Acknowledge
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          <TabsContent value="logs" className="space-y-4">
            <div className="flex gap-2 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search logs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            <Card>
              <CardContent className="p-0">
                <div className="max-h-[600px] overflow-y-auto">
                  {filteredLogs.length === 0 ? (
                    <div className="py-12 text-center">
                      <FileText className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                      <h3 className="text-lg font-semibold mb-2">No log messages</h3>
                      <p className="text-muted-foreground">Waiting for syslog messages...</p>
                    </div>
                  ) : (
                    <div className="divide-y">
                      {filteredLogs.map((log) => (
                        <div key={log.id} className="p-4 hover:bg-accent/50 transition-colors">
                          <div className="flex items-start gap-3">
                            <Badge variant={getSeverityColor(getSeverityLevel(log.severity))}>
                              SEV-{log.severity}
                            </Badge>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-1">
                                <p className="text-sm font-medium truncate">
                                  {log.hostname || log.source_ip}
                                </p>
                                {log.is_security_event && (
                                  <Badge variant="destructive" className="text-xs">Security</Badge>
                                )}
                              </div>
                              <p className="text-sm text-muted-foreground mb-1 break-words">{log.message}</p>
                              <p className="text-xs text-muted-foreground">
                                {new Date(log.received_at).toLocaleString()}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}