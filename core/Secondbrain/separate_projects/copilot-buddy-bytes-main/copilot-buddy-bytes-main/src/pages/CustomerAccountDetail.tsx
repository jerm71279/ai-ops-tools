import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, Building2, Users, MapPin, Package, History } from "lucide-react";

interface CustomerAccount {
  id: string;
  account_number: string;
  company_name: string;
  account_type: string;
  industry: string;
  account_status: string;
  support_tier: string;
  payment_terms: string;
  website: string;
  notes: string;
}

interface Contact {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  job_title: string;
  is_primary: boolean;
}

interface Site {
  id: string;
  site_name: string;
  address_line1: string;
  city: string;
  state_province: string;
  postal_code: string;
  phone: string;
  is_primary_site: boolean;
}

interface Asset {
  id: string;
  ci_id: string;
  asset_status: string;
  service_level: string;
  installation_date: string;
}

interface ServiceHistory {
  id: string;
  service_type: string;
  service_date: string;
  description: string;
  time_spent_hours: number;
  amount_charged: number;
}

const CustomerAccountDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [account, setAccount] = useState<CustomerAccount | null>(null);
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [sites, setSites] = useState<Site[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [serviceHistory, setServiceHistory] = useState<ServiceHistory[]>([]);
  const { toast } = useToast();

  useEffect(() => {
    if (id) {
      fetchAccountDetails();
    }
  }, [id]);

  const fetchAccountDetails = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) return;

      // Fetch account details
      const { data: accountData, error: accountError } = await supabase
        .from("customer_accounts")
        .select("*")
        .eq("id", id)
        .eq("customer_id", profile.customer_id)
        .single();

      if (accountError) throw accountError;
      setAccount(accountData);

      // Fetch contacts
      const { data: contactsData } = await supabase
        .from("customer_contacts")
        .select("*")
        .eq("account_id", id)
        .eq("customer_id", profile.customer_id);

      setContacts(contactsData || []);

      // Fetch sites
      const { data: sitesData } = await supabase
        .from("customer_sites")
        .select("*")
        .eq("account_id", id)
        .eq("customer_id", profile.customer_id);

      setSites(sitesData || []);

      // Fetch assets
      const { data: assetsData } = await supabase
        .from("customer_assets")
        .select("*")
        .eq("account_id", id)
        .eq("customer_id", profile.customer_id);

      setAssets(assetsData || []);

      // Fetch service history
      const { data: historyData } = await supabase
        .from("customer_service_history")
        .select("*")
        .eq("account_id", id)
        .eq("customer_id", profile.customer_id)
        .order("service_date", { ascending: false });

      setServiceHistory(historyData || []);
    } catch (error) {
      console.error("Error fetching account details:", error);
      toast({
        title: "Error",
        description: "Failed to load customer account details",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!account) {
    return <div className="min-h-screen flex items-center justify-center">Account not found</div>;
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation />
      
      <main className="container mx-auto px-4 py-8">
        <Button
          variant="ghost"
          onClick={() => navigate("/customers")}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Accounts
        </Button>

        <div className="mb-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-4xl font-bold mb-2">{account.company_name}</h1>
              <p className="text-muted-foreground">Account #{account.account_number}</p>
            </div>
            <Badge>{account.account_status}</Badge>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Contacts</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{contacts.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Sites</CardTitle>
              <MapPin className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{sites.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Assets</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{assets.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Service Records</CardTitle>
              <History className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{serviceHistory.length}</div>
            </CardContent>
          </Card>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Account Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Account Type</p>
                <p className="font-medium">{account.account_type}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Industry</p>
                <p className="font-medium">{account.industry || "-"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Support Tier</p>
                <p className="font-medium">{account.support_tier || "-"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Payment Terms</p>
                <p className="font-medium">{account.payment_terms || "-"}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Website</p>
                <p className="font-medium">{account.website || "-"}</p>
              </div>
            </div>
            {account.notes && (
              <div className="mt-4">
                <p className="text-sm text-muted-foreground">Notes</p>
                <p className="font-medium">{account.notes}</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Tabs defaultValue="contacts" className="space-y-4">
          <TabsList>
            <TabsTrigger value="contacts">Contacts</TabsTrigger>
            <TabsTrigger value="sites">Sites</TabsTrigger>
            <TabsTrigger value="assets">Assets</TabsTrigger>
            <TabsTrigger value="history">Service History</TabsTrigger>
          </TabsList>

          <TabsContent value="contacts">
            <Card>
              <CardHeader>
                <CardTitle>Contacts</CardTitle>
              </CardHeader>
              <CardContent>
                {contacts.length === 0 ? (
                  <p className="text-muted-foreground">No contacts found</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Email</TableHead>
                        <TableHead>Phone</TableHead>
                        <TableHead>Title</TableHead>
                        <TableHead>Primary</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {contacts.map((contact) => (
                        <TableRow key={contact.id}>
                          <TableCell className="font-medium">
                            {contact.first_name} {contact.last_name}
                          </TableCell>
                          <TableCell>{contact.email || "-"}</TableCell>
                          <TableCell>{contact.phone || "-"}</TableCell>
                          <TableCell>{contact.job_title || "-"}</TableCell>
                          <TableCell>
                            {contact.is_primary && <Badge>Primary</Badge>}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sites">
            <Card>
              <CardHeader>
                <CardTitle>Sites & Locations</CardTitle>
              </CardHeader>
              <CardContent>
                {sites.length === 0 ? (
                  <p className="text-muted-foreground">No sites found</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Site Name</TableHead>
                        <TableHead>Address</TableHead>
                        <TableHead>City</TableHead>
                        <TableHead>State</TableHead>
                        <TableHead>Phone</TableHead>
                        <TableHead>Primary</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {sites.map((site) => (
                        <TableRow key={site.id}>
                          <TableCell className="font-medium">{site.site_name}</TableCell>
                          <TableCell>{site.address_line1}</TableCell>
                          <TableCell>{site.city}</TableCell>
                          <TableCell>{site.state_province || "-"}</TableCell>
                          <TableCell>{site.phone || "-"}</TableCell>
                          <TableCell>
                            {site.is_primary_site && <Badge>Primary</Badge>}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="assets">
            <Card>
              <CardHeader>
                <CardTitle>Customer Assets</CardTitle>
              </CardHeader>
              <CardContent>
                {assets.length === 0 ? (
                  <p className="text-muted-foreground">No assets found</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Status</TableHead>
                        <TableHead>Service Level</TableHead>
                        <TableHead>Installation Date</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {assets.map((asset) => (
                        <TableRow key={asset.id}>
                          <TableCell>
                            <Badge>{asset.asset_status}</Badge>
                          </TableCell>
                          <TableCell>{asset.service_level || "-"}</TableCell>
                          <TableCell>
                            {asset.installation_date
                              ? new Date(asset.installation_date).toLocaleDateString()
                              : "-"}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history">
            <Card>
              <CardHeader>
                <CardTitle>Service History</CardTitle>
              </CardHeader>
              <CardContent>
                {serviceHistory.length === 0 ? (
                  <p className="text-muted-foreground">No service history found</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Date</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead>Hours</TableHead>
                        <TableHead>Amount</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {serviceHistory.map((service) => (
                        <TableRow key={service.id}>
                          <TableCell>
                            {new Date(service.service_date).toLocaleDateString()}
                          </TableCell>
                          <TableCell>{service.service_type}</TableCell>
                          <TableCell>{service.description}</TableCell>
                          <TableCell>{service.time_spent_hours || "-"}</TableCell>
                          <TableCell>
                            {service.amount_charged
                              ? `$${service.amount_charged.toLocaleString()}`
                              : "-"}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default CustomerAccountDetail;