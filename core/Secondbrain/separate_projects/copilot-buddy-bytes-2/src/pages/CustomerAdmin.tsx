import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { 
  Building2, 
  Users, 
  TrendingUp, 
  AlertTriangle,
  Activity,
  DollarSign,
  Settings,
  Plus
} from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function CustomerAdmin() {
  const [searchTerm, setSearchTerm] = useState("");
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [newCustomer, setNewCustomer] = useState({
    company_name: "",
    industry: "",
    primary_contact_email: "",
  });
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: customers, isLoading } = useQuery({
    queryKey: ['customer-details'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('customer_details' as any)
        .select('*')
        .order('created_at', { ascending: false });
      if (error) throw error;
      return data;
    },
  });

  const { data: healthScores } = useQuery({
    queryKey: ['customer-health-all'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('customer_health' as any)
        .select('customer_id, health_score, risk_level, calculated_at')
        .order('calculated_at', { ascending: false });
      if (error) throw error;
      
      // Get latest health score for each customer
      const latest = new Map();
      data?.forEach((score: any) => {
        if (!latest.has(score.customer_id) || 
            new Date(score.calculated_at) > new Date(latest.get(score.customer_id).calculated_at)) {
          latest.set(score.customer_id, score);
        }
      });
      return Array.from(latest.values());
    },
  });

  const { data: usage } = useQuery({
    queryKey: ['customer-usage-summary'],
    queryFn: async () => {
      const today = new Date().toISOString().split('T')[0];
      const { data, error } = await supabase
        .from('customer_usage' as any)
        .select('customer_id, metric_type, metric_value')
        .eq('usage_date', today);
      if (error) throw error;
      return data;
    },
  });

  const addCustomerMutation = useMutation({
    mutationFn: async () => {
      const customerId = crypto.randomUUID();
      const { error } = await supabase
        .from('customer_details' as any)
        .insert({
          customer_id: customerId,
          ...newCustomer,
          status: 'active',
          is_trial: true,
          trial_end_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
        });
      if (error) throw error;
      return customerId;
    },
    onSuccess: () => {
      toast.success('Customer added successfully');
      setIsAddOpen(false);
      setNewCustomer({ company_name: "", industry: "", primary_contact_email: "" });
      queryClient.invalidateQueries({ queryKey: ['customer-details'] });
    },
    onError: (error) => {
      toast.error(`Failed to add customer: ${error.message}`);
    },
  });

  const filteredCustomers = customers?.filter((c: any) => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      c.company_name?.toLowerCase().includes(search) ||
      c.industry?.toLowerCase().includes(search) ||
      c.primary_contact_email?.toLowerCase().includes(search)
    );
  });

  const getHealthScore = (customerId: string) => {
    return healthScores?.find((h: any) => h.customer_id === customerId);
  };

  const getUsageMetric = (customerId: string, metricType: string): number => {
    if (!usage || !Array.isArray(usage)) return 0;
    const metric = usage.find((u: any) => 
      u?.customer_id === customerId && u?.metric_type === metricType
    );
    if (!metric || !('metric_value' in metric)) return 0;
    return Number(metric.metric_value);
  };

  const totalCustomers = customers?.length || 0;
  const activeCustomers = customers?.filter((c: any) => c.status === 'active').length || 0;
  const trialCustomers = customers?.filter((c: any) => c.is_trial).length || 0;
  const atRiskCustomers = healthScores?.filter((h: any) => 
    h.risk_level === 'high' || h.risk_level === 'critical'
  ).length || 0;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 pt-56 pb-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold">Customer Administration</h1>
            <p className="text-muted-foreground mt-2">
              Manage tenants, monitor health, and track usage
            </p>
          </div>
          <Dialog open={isAddOpen} onOpenChange={setIsAddOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Customer
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Customer</DialogTitle>
                <DialogDescription>
                  Create a new customer account
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Company Name</Label>
                  <Input
                    value={newCustomer.company_name}
                    onChange={(e) => setNewCustomer({ ...newCustomer, company_name: e.target.value })}
                    placeholder="Acme Corp"
                  />
                </div>
                <div>
                  <Label>Industry</Label>
                  <Input
                    value={newCustomer.industry}
                    onChange={(e) => setNewCustomer({ ...newCustomer, industry: e.target.value })}
                    placeholder="Technology"
                  />
                </div>
                <div>
                  <Label>Primary Contact Email</Label>
                  <Input
                    type="email"
                    value={newCustomer.primary_contact_email}
                    onChange={(e) => setNewCustomer({ ...newCustomer, primary_contact_email: e.target.value })}
                    placeholder="contact@acme.com"
                  />
                </div>
                <Button
                  onClick={() => addCustomerMutation.mutate()}
                  disabled={!newCustomer.company_name || !newCustomer.primary_contact_email || addCustomerMutation.isPending}
                  className="w-full"
                >
                  Create Customer
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total Customers</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalCustomers}</div>
              <p className="text-xs text-muted-foreground">
                {activeCustomers} active
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Trial Accounts</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{trialCustomers}</div>
              <p className="text-xs text-muted-foreground">
                Active trials
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">At Risk</CardTitle>
              <AlertTriangle className="h-4 w-4 text-destructive" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{atRiskCustomers}</div>
              <p className="text-xs text-muted-foreground">
                Require attention
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Avg Health Score</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {healthScores && healthScores.length > 0
                  ? Math.round(
                      healthScores.reduce((sum: number, h: any) => sum + h.health_score, 0) /
                      healthScores.length
                    )
                  : 0}
              </div>
              <p className="text-xs text-muted-foreground">Overall health</p>
            </CardContent>
          </Card>
        </div>

        {/* Search */}
        <div className="mb-6">
          <Input
            placeholder="Search customers by name, industry, or email..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="max-w-md"
          />
        </div>

        {/* Customer List */}
        <Card>
          <CardHeader>
            <CardTitle>All Customers</CardTitle>
            <CardDescription>Manage and monitor customer accounts</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <p className="text-center py-8 text-muted-foreground">Loading customers...</p>
            ) : filteredCustomers && filteredCustomers.length > 0 ? (
              <div className="space-y-4">
                {filteredCustomers.map((customer: any) => {
                  const health = getHealthScore(customer.customer_id);
                  const users = getUsageMetric(customer.customer_id, 'users');
                  
                  return (
                    <Card 
                      key={customer.id}
                      className="cursor-pointer hover:bg-muted/50 transition-colors"
                      onClick={() => navigate(`/customers/${customer.customer_id}`)}
                    >
                      <CardContent className="pt-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-lg font-semibold">{customer.company_name}</h3>
                              <Badge variant={customer.status === 'active' ? 'default' : 'secondary'}>
                                {customer.status}
                              </Badge>
                              {customer.is_trial && (
                                <Badge variant="outline">Trial</Badge>
                              )}
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                              <div>
                                <p className="text-muted-foreground">Industry</p>
                                <p className="font-medium">{customer.industry || 'Not specified'}</p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Contact</p>
                                <p className="font-medium">{customer.primary_contact_email}</p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Users</p>
                                <p className="font-medium">{users}</p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Subscription</p>
                                <p className="font-medium capitalize">{customer.subscription_tier}</p>
                              </div>
                            </div>
                          </div>
                          <div className="flex flex-col items-end gap-2">
                            {health && (
                              <>
                                <div className="text-right">
                                  <p className="text-2xl font-bold">{health.health_score}</p>
                                  <p className="text-xs text-muted-foreground">Health Score</p>
                                </div>
                                <Badge variant={
                                  health.risk_level === 'critical' ? 'destructive' :
                                  health.risk_level === 'high' ? 'destructive' :
                                  health.risk_level === 'medium' ? 'secondary' :
                                  'default'
                                }>
                                  {health.risk_level} risk
                                </Badge>
                              </>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            ) : (
              <p className="text-center py-8 text-muted-foreground">
                {searchTerm ? 'No matching customers found' : 'No customers yet'}
              </p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}