import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { FileText, AlertTriangle, CheckCircle, Calendar, DollarSign, Clock } from "lucide-react";
import { differenceInDays, parseISO } from "date-fns";

const ContractManagement = () => {
  const [selectedTab, setSelectedTab] = useState("active");

  // Fetch contracts
  const { data: contracts } = useQuery({
    queryKey: ["contracts"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("contracts" as any)
        .select("*")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return data as any[];
    },
  });

  // Fetch contract terms
  const { data: contractTerms } = useQuery({
    queryKey: ["contract-terms"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("contract_terms" as any)
        .select("*");
      if (error) throw error;
      return data as any[];
    },
  });

  // Fetch upcoming renewals
  const { data: upcomingRenewals } = useQuery({
    queryKey: ["contract-renewals"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("contract_renewals" as any)
        .select("*, contracts(contract_name)")
        .eq("renewal_status", "upcoming")
        .order("renewal_date");
      if (error) throw error;
      return data as any[];
    },
  });

  // Calculate stats
  const activeContracts = contracts?.filter(c => c.status === 'active').length || 0;
  const expiringContracts = contracts?.filter(c => {
    if (!c.end_date || c.status !== 'active') return false;
    const daysUntilExpiry = differenceInDays(parseISO(c.end_date), new Date());
    return daysUntilExpiry <= 90 && daysUntilExpiry > 0;
  }).length || 0;
  const totalValue = contracts?.filter(c => c.status === 'active').reduce((sum, c) => sum + (Number(c.contract_value) || 0), 0) || 0;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'default';
      case 'draft': return 'secondary';
      case 'expiring': return 'warning';
      case 'expired': return 'destructive';
      case 'terminated': return 'destructive';
      default: return 'default';
    }
  };

  const getDaysUntilExpiry = (endDate: string) => {
    return differenceInDays(parseISO(endDate), new Date());
  };

  const isExpiringSoon = (endDate: string) => {
    const days = getDaysUntilExpiry(endDate);
    return days <= 90 && days > 0;
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Contract Management</h1>
            <p className="text-muted-foreground">Track agreements, renewals, and SLA terms</p>
          </div>
          <Button>
            <FileText className="mr-2 h-4 w-4" />
            New Contract
          </Button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Active Contracts</CardTitle>
              <CheckCircle className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{activeContracts}</div>
              <p className="text-xs text-muted-foreground mt-1">In force</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Contract Value</CardTitle>
              <DollarSign className="h-4 w-4 text-success" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalValue.toFixed(0)}</div>
              <p className="text-xs text-muted-foreground mt-1">Active contracts</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
              <AlertTriangle className="h-4 w-4 text-warning" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-warning">{expiringContracts}</div>
              <p className="text-xs text-muted-foreground mt-1">Within 90 days</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Renewals Due</CardTitle>
              <Calendar className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{upcomingRenewals?.length || 0}</div>
              <p className="text-xs text-muted-foreground mt-1">Pending action</p>
            </CardContent>
          </Card>
        </div>

        <Tabs value={selectedTab} onValueChange={setSelectedTab}>
          <TabsList>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="expiring">Expiring</TabsTrigger>
            <TabsTrigger value="draft">Draft</TabsTrigger>
            <TabsTrigger value="all">All Contracts</TabsTrigger>
          </TabsList>

          <TabsContent value={selectedTab} className="space-y-4">
            {contracts
              ?.filter(contract => {
                if (selectedTab === 'all') return true;
                if (selectedTab === 'expiring') {
                  return contract.status === 'active' && contract.end_date && isExpiringSoon(contract.end_date);
                }
                return contract.status === selectedTab;
              })
              .map((contract) => {
                const terms = contractTerms?.filter(t => t.contract_id === contract.id) || [];
                const slaTerms = terms.filter(t => t.term_type === 'sla');
                const daysUntilExpiry = contract.end_date ? getDaysUntilExpiry(contract.end_date) : null;
                const expiring = daysUntilExpiry !== null && isExpiringSoon(contract.end_date);

                return (
                  <Card key={contract.id} className={expiring ? "border-warning" : ""}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <CardTitle className="text-xl">{contract.contract_name}</CardTitle>
                            <Badge variant={getStatusColor(contract.status) as any}>
                              {contract.status}
                            </Badge>
                            {expiring && (
                              <Badge variant="outline" className="border-warning text-warning">
                                <AlertTriangle className="h-3 w-3 mr-1" />
                                Expiring in {daysUntilExpiry} days
                              </Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-4 text-sm text-muted-foreground">
                            <span>Contract #{contract.contract_number}</span>
                            <span>•</span>
                            <span>{contract.contract_type}</span>
                          </div>
                        </div>
                        <Button variant="outline" size="sm">View Details</Button>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* Contract Details Grid */}
                      <div className="grid grid-cols-4 gap-4 pb-4 border-b">
                        <div>
                          <p className="text-xs text-muted-foreground">Value</p>
                          <p className="font-medium">${contract.contract_value?.toFixed(0) || "N/A"}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Start Date</p>
                          <p className="font-medium">{contract.start_date || "N/A"}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">End Date</p>
                          <p className="font-medium">{contract.end_date || "N/A"}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted-foreground">Renewal Type</p>
                          <Badge variant="outline" className="mt-1">{contract.renewal_type}</Badge>
                        </div>
                      </div>

                      {/* SLA Terms */}
                      {slaTerms.length > 0 && (
                        <div className="space-y-2">
                          <div className="flex items-center gap-2">
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            <p className="text-sm font-medium">SLA Terms ({slaTerms.length})</p>
                          </div>
                          <div className="grid grid-cols-2 gap-2">
                            {slaTerms.slice(0, 4).map((term) => (
                              <div key={term.id} className="p-2 border rounded text-sm">
                                <p className="font-medium">{term.term_name}</p>
                                <p className="text-xs text-muted-foreground">{term.target_metric}: {term.target_value}</p>
                              </div>
                            ))}
                          </div>
                          {slaTerms.length > 4 && (
                            <Button variant="link" size="sm" className="p-0 h-auto">
                              View all {slaTerms.length} terms
                            </Button>
                          )}
                        </div>
                      )}

                      {/* Billing Info */}
                      <div className="flex items-center gap-4 text-sm pt-2 border-t">
                        <div className="flex items-center gap-2">
                          <DollarSign className="h-4 w-4 text-muted-foreground" />
                          <span className="text-muted-foreground">Billing:</span>
                          <span className="font-medium">{contract.billing_frequency}</span>
                        </div>
                        {contract.payment_terms && (
                          <>
                            <span>•</span>
                            <span className="text-muted-foreground">Terms: {contract.payment_terms}</span>
                          </>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}

            {(!contracts || contracts.filter(c => selectedTab === 'all' || c.status === selectedTab).length === 0) && (
              <Card>
                <CardContent className="py-12">
                  <p className="text-center text-muted-foreground">No contracts found</p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>

        {/* Upcoming Renewals */}
        {upcomingRenewals && upcomingRenewals.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Upcoming Renewals</CardTitle>
              <CardDescription>Contracts requiring renewal action</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {upcomingRenewals.map((renewal: any) => (
                  <div key={renewal.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <p className="font-medium">{renewal.contracts?.contract_name}</p>
                      <p className="text-sm text-muted-foreground">
                        Renewal Date: {renewal.renewal_date}
                      </p>
                    </div>
                    <Button size="sm">Review</Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ContractManagement;
