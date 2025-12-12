import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { toast } from "sonner";
import { DollarSign, TrendingDown, Calendar, Search } from "lucide-react";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";

interface AssetFinancial {
  id: string;
  ci_id: string;
  purchase_price: number | null;
  current_value: number | null;
  depreciation_method: string | null;
  total_cost_ownership: number | null;
  acquisition_date: string | null;
  lease_monthly_cost: number | null;
  ci_name?: string;
}

export default function AssetFinancials() {
  const navigate = useNavigate();
  const [assetFinancials, setAssetFinancials] = useState<AssetFinancial[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [customerId, setCustomerId] = useState<string | null>(null);

  useEffect(() => {
    fetchUserProfile();
  }, []);

  useEffect(() => {
    if (customerId) {
      fetchAssetFinancials();
    }
  }, [customerId]);

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

  const fetchAssetFinancials = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from("asset_financials")
        .select(`
          *,
          configuration_items!inner(ci_name)
        `)
        .eq("customer_id", customerId!)
        .order("created_at", { ascending: false });

      if (error) throw error;

      const formatted = data?.map((item: any) => ({
        ...item,
        ci_name: item.configuration_items?.ci_name,
      })) || [];

      setAssetFinancials(formatted);
    } catch (error) {
      console.error("Error fetching asset financials:", error);
      toast.error("Failed to load asset financials");
    } finally {
      setLoading(false);
    }
  };

  const filteredAssets = assetFinancials.filter((asset) => {
    return asset.ci_name?.toLowerCase().includes(searchTerm.toLowerCase());
  });

  const stats = {
    total: assetFinancials.length,
    totalPurchaseValue: assetFinancials.reduce((sum, a) => sum + (parseFloat(a.purchase_price?.toString() || "0")), 0),
    totalCurrentValue: assetFinancials.reduce((sum, a) => sum + (parseFloat(a.current_value?.toString() || "0")), 0),
    totalTCO: assetFinancials.reduce((sum, a) => sum + (parseFloat(a.total_cost_ownership?.toString() || "0")), 0),
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation />
      
      <main className="container mx-auto p-6 space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Asset Financials</h1>
            <p className="text-muted-foreground">Track asset lifecycle costs and depreciation</p>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Assets</CardTitle>
              <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Purchase Value</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.totalPurchaseValue.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Current Value</CardTitle>
              <TrendingDown className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.totalCurrentValue.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total TCO</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.totalTCO.toLocaleString()}</div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Asset Financial Details</CardTitle>
            <CardDescription>View financial information for all tracked assets</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search assets..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Asset Name</TableHead>
                  <TableHead>Purchase Price</TableHead>
                  <TableHead>Current Value</TableHead>
                  <TableHead>Depreciation</TableHead>
                  <TableHead>TCO</TableHead>
                  <TableHead>Lease Cost/mo</TableHead>
                  <TableHead>Acquisition Date</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center">Loading...</TableCell>
                  </TableRow>
                ) : filteredAssets.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center">No asset financials found</TableCell>
                  </TableRow>
                ) : (
                  filteredAssets.map((asset) => (
                    <TableRow key={asset.id}>
                      <TableCell className="font-medium">{asset.ci_name || "—"}</TableCell>
                      <TableCell>${asset.purchase_price ? parseFloat(asset.purchase_price.toString()).toLocaleString() : "—"}</TableCell>
                      <TableCell>${asset.current_value ? parseFloat(asset.current_value.toString()).toLocaleString() : "—"}</TableCell>
                      <TableCell>{asset.depreciation_method || "—"}</TableCell>
                      <TableCell>${asset.total_cost_ownership ? parseFloat(asset.total_cost_ownership.toString()).toLocaleString() : "—"}</TableCell>
                      <TableCell>${asset.lease_monthly_cost ? parseFloat(asset.lease_monthly_cost.toString()).toLocaleString() : "—"}</TableCell>
                      <TableCell>{asset.acquisition_date ? new Date(asset.acquisition_date).toLocaleDateString() : "—"}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
