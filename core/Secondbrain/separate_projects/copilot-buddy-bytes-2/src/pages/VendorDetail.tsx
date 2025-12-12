import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { toast } from "sonner";
import { ArrowLeft, Plus, Building2, FileText, TrendingUp, Star, Calendar } from "lucide-react";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";

interface Vendor {
  id: string;
  vendor_code: string;
  vendor_name: string;
  vendor_type: string;
  status: string;
  contact_name: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  address: string | null;
  payment_terms: string | null;
  credit_limit: number | null;
  current_balance: number | null;
  performance_score: number | null;
  notes: string | null;
  created_at: string;
}

interface Contract {
  id: string;
  contract_number: string;
  contract_name: string;
  contract_type: string;
  status: string;
  start_date: string;
  end_date: string | null;
  contract_value: number | null;
  auto_renew: boolean;
}

interface Performance {
  id: string;
  evaluation_date: string;
  delivery_score: number | null;
  quality_score: number | null;
  communication_score: number | null;
  pricing_score: number | null;
  overall_score: number | null;
  comments: string | null;
}

export default function VendorDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [vendor, setVendor] = useState<Vendor | null>(null);
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [performance, setPerformance] = useState<Performance[]>([]);
  const [loading, setLoading] = useState(true);
  const [isContractDialogOpen, setIsContractDialogOpen] = useState(false);
  const [customerId, setCustomerId] = useState<string | null>(null);

  const [newContract, setNewContract] = useState({
    contract_name: "",
    contract_type: "service",
    start_date: "",
    end_date: "",
    contract_value: "",
    payment_schedule: "monthly",
    auto_renew: false,
    terms: "",
    notes: "",
  });

  useEffect(() => {
    fetchUserProfile();
  }, []);

  useEffect(() => {
    if (customerId && id) {
      fetchVendorDetails();
    }
  }, [customerId, id]);

  const fetchUserProfile = async () => {
    const { data: { user } } = await supabase.auth.getUser();
    if (!user) {
      navigate("/auth");
      return;
    }

    const { data: profile } = await supabase
      .from("user_profiles")
      .select("customer_id")
      .eq("user_id", user.id)
      .single();

    if (profile?.customer_id) {
      setCustomerId(profile.customer_id);
    }
  };

  const fetchVendorDetails = async () => {
    try {
      setLoading(true);

      // Fetch vendor
      const { data: vendorData, error: vendorError } = await supabase
        .from("vendors")
        .select("*")
        .eq("id", id!)
        .eq("customer_id", customerId!)
        .single();

      if (vendorError) throw vendorError;
      setVendor(vendorData);

      // Fetch contracts
      const { data: contractsData, error: contractsError } = await supabase
        .from("vendor_contracts")
        .select("*")
        .eq("vendor_id", id!)
        .eq("customer_id", customerId!)
        .order("created_at", { ascending: false });

      if (contractsError) throw contractsError;
      setContracts(contractsData || []);

      // Fetch performance
      const { data: performanceData, error: performanceError } = await supabase
        .from("vendor_performance")
        .select("*")
        .eq("vendor_id", id!)
        .eq("customer_id", customerId!)
        .order("evaluation_date", { ascending: false });

      if (performanceError) throw performanceError;
      setPerformance(performanceData || []);
    } catch (error) {
      console.error("Error fetching vendor details:", error);
      toast.error("Failed to load vendor details");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateContract = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user || !customerId) return;

      const { error } = await supabase.from("vendor_contracts").insert([{
        customer_id: customerId,
        vendor_id: id!,
        contract_number: '',
        contract_name: newContract.contract_name,
        contract_type: newContract.contract_type,
        start_date: newContract.start_date,
        end_date: newContract.end_date || null,
        contract_value: newContract.contract_value ? parseFloat(newContract.contract_value) : null,
        payment_schedule: newContract.payment_schedule,
        auto_renew: newContract.auto_renew,
        terms: newContract.terms,
        notes: newContract.notes,
        created_by: user.id,
      }]);

      if (error) throw error;

      toast.success("Contract created successfully");
      setIsContractDialogOpen(false);
      setNewContract({
        contract_name: "",
        contract_type: "service",
        start_date: "",
        end_date: "",
        contract_value: "",
        payment_schedule: "monthly",
        auto_renew: false,
        terms: "",
        notes: "",
      });
      fetchVendorDetails();
    } catch (error) {
      console.error("Error creating contract:", error);
      toast.error("Failed to create contract");
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      active: "default",
      inactive: "secondary",
      draft: "outline",
      expired: "destructive",
      terminated: "destructive",
      renewal_pending: "outline",
    };
    return <Badge variant={variants[status] || "default"}>{status}</Badge>;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <DashboardNavigation />
        <main className="container mx-auto p-6">
          <div className="text-center">Loading...</div>
        </main>
      </div>
    );
  }

  if (!vendor) {
    return (
      <div className="min-h-screen bg-background">
        <Navigation />
        <DashboardNavigation />
        <main className="container mx-auto p-6">
          <div className="text-center">Vendor not found</div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation />
      
      <main className="container mx-auto p-6 space-y-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" onClick={() => navigate("/vendors")}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back
          </Button>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h1 className="text-3xl font-bold">{vendor.vendor_name}</h1>
              {getStatusBadge(vendor.status)}
            </div>
            <p className="text-muted-foreground">
              {vendor.vendor_code} • {vendor.vendor_type}
            </p>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Performance Score</CardTitle>
              <Star className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{vendor.performance_score || "—"}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Contracts</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{contracts.filter(c => c.status === 'active').length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Current Balance</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${vendor.current_balance?.toLocaleString() || "0"}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Credit Limit</CardTitle>
              <Building2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${vendor.credit_limit?.toLocaleString() || "—"}</div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="contracts">Contracts</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Vendor Information</CardTitle>
              </CardHeader>
              <CardContent className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label className="text-muted-foreground">Contact Name</Label>
                  <p className="text-lg">{vendor.contact_name || "—"}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Contact Email</Label>
                  <p className="text-lg">{vendor.contact_email || "—"}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Contact Phone</Label>
                  <p className="text-lg">{vendor.contact_phone || "—"}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Payment Terms</Label>
                  <p className="text-lg">{vendor.payment_terms || "—"}</p>
                </div>
                <div className="md:col-span-2">
                  <Label className="text-muted-foreground">Address</Label>
                  <p className="text-lg">{vendor.address || "—"}</p>
                </div>
                {vendor.notes && (
                  <div className="md:col-span-2">
                    <Label className="text-muted-foreground">Notes</Label>
                    <p className="text-lg">{vendor.notes}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="contracts" className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Contracts</CardTitle>
                    <CardDescription>Manage vendor contracts and agreements</CardDescription>
                  </div>
                  <Dialog open={isContractDialogOpen} onOpenChange={setIsContractDialogOpen}>
                    <DialogTrigger asChild>
                      <Button>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Contract
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Add New Contract</DialogTitle>
                        <DialogDescription>Create a new contract for this vendor</DialogDescription>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <Label>Contract Name</Label>
                          <Input
                            value={newContract.contract_name}
                            onChange={(e) => setNewContract({ ...newContract, contract_name: e.target.value })}
                            placeholder="Enter contract name"
                          />
                        </div>
                        <div>
                          <Label>Contract Type</Label>
                          <Select value={newContract.contract_type} onValueChange={(value) => setNewContract({ ...newContract, contract_type: value })}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="service">Service</SelectItem>
                              <SelectItem value="purchase">Purchase</SelectItem>
                              <SelectItem value="maintenance">Maintenance</SelectItem>
                              <SelectItem value="subscription">Subscription</SelectItem>
                              <SelectItem value="lease">Lease</SelectItem>
                              <SelectItem value="other">Other</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label>Start Date</Label>
                            <Input
                              type="date"
                              value={newContract.start_date}
                              onChange={(e) => setNewContract({ ...newContract, start_date: e.target.value })}
                            />
                          </div>
                          <div>
                            <Label>End Date</Label>
                            <Input
                              type="date"
                              value={newContract.end_date}
                              onChange={(e) => setNewContract({ ...newContract, end_date: e.target.value })}
                            />
                          </div>
                        </div>
                        <div>
                          <Label>Contract Value</Label>
                          <Input
                            type="number"
                            value={newContract.contract_value}
                            onChange={(e) => setNewContract({ ...newContract, contract_value: e.target.value })}
                            placeholder="0.00"
                          />
                        </div>
                        <div>
                          <Label>Payment Schedule</Label>
                          <Select value={newContract.payment_schedule} onValueChange={(value) => setNewContract({ ...newContract, payment_schedule: value })}>
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="one_time">One Time</SelectItem>
                              <SelectItem value="monthly">Monthly</SelectItem>
                              <SelectItem value="quarterly">Quarterly</SelectItem>
                              <SelectItem value="annually">Annually</SelectItem>
                              <SelectItem value="milestone">Milestone</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div>
                          <Label>Terms</Label>
                          <Textarea
                            value={newContract.terms}
                            onChange={(e) => setNewContract({ ...newContract, terms: e.target.value })}
                            placeholder="Contract terms and conditions..."
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setIsContractDialogOpen(false)}>Cancel</Button>
                        <Button onClick={handleCreateContract}>Create</Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Contract #</TableHead>
                      <TableHead>Name</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Start Date</TableHead>
                      <TableHead>End Date</TableHead>
                      <TableHead>Value</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {contracts.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} className="text-center">No contracts found</TableCell>
                      </TableRow>
                    ) : (
                      contracts.map((contract) => (
                        <TableRow key={contract.id}>
                          <TableCell className="font-medium">{contract.contract_number}</TableCell>
                          <TableCell>{contract.contract_name}</TableCell>
                          <TableCell className="capitalize">{contract.contract_type}</TableCell>
                          <TableCell>{getStatusBadge(contract.status)}</TableCell>
                          <TableCell>{new Date(contract.start_date).toLocaleDateString()}</TableCell>
                          <TableCell>{contract.end_date ? new Date(contract.end_date).toLocaleDateString() : "—"}</TableCell>
                          <TableCell>${contract.contract_value?.toLocaleString() || "—"}</TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="performance" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Performance History</CardTitle>
                <CardDescription>Track vendor performance over time</CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Date</TableHead>
                      <TableHead>Delivery</TableHead>
                      <TableHead>Quality</TableHead>
                      <TableHead>Communication</TableHead>
                      <TableHead>Pricing</TableHead>
                      <TableHead>Overall</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {performance.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={6} className="text-center">No performance data available</TableCell>
                      </TableRow>
                    ) : (
                      performance.map((perf) => (
                        <TableRow key={perf.id}>
                          <TableCell>{new Date(perf.evaluation_date).toLocaleDateString()}</TableCell>
                          <TableCell>{perf.delivery_score || "—"}</TableCell>
                          <TableCell>{perf.quality_score || "—"}</TableCell>
                          <TableCell>{perf.communication_score || "—"}</TableCell>
                          <TableCell>{perf.pricing_score || "—"}</TableCell>
                          <TableCell className="font-medium">{perf.overall_score || "—"}</TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
