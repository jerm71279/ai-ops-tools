import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Plus, Search, Warehouse, MapPin } from "lucide-react";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";

interface WarehouseType {
  id: string;
  warehouse_code: string;
  warehouse_name: string;
  warehouse_type: string | null;
  address: string;
  city: string | null;
  state: string | null;
  status: string;
  capacity_sqft: number | null;
  contact_phone: string | null;
  created_at: string;
}

export default function WarehouseManagement() {
  const navigate = useNavigate();
  const [warehouses, setWarehouses] = useState<WarehouseType[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [customerId, setCustomerId] = useState<string | null>(null);

  const [newWarehouse, setNewWarehouse] = useState({
    warehouse_code: "",
    warehouse_name: "",
    warehouse_type: "main",
    address: "",
    city: "",
    state: "",
    postal_code: "",
    capacity_sqft: "",
    contact_phone: "",
    notes: "",
  });

  useEffect(() => {
    fetchUserProfile();
  }, []);

  useEffect(() => {
    if (customerId) {
      fetchWarehouses();
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

  const fetchWarehouses = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from("warehouses")
        .select("*")
        .eq("customer_id", customerId!)
        .order("created_at", { ascending: false });

      if (error) throw error;
      setWarehouses(data || []);
    } catch (error) {
      console.error("Error fetching warehouses:", error);
      toast.error("Failed to load warehouses");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWarehouse = async () => {
    try {
      if (!customerId) return;

      const { error } = await supabase.from("warehouses").insert([{
        customer_id: customerId,
        warehouse_code: newWarehouse.warehouse_code,
        warehouse_name: newWarehouse.warehouse_name,
        warehouse_type: newWarehouse.warehouse_type,
        address: newWarehouse.address,
        city: newWarehouse.city,
        state: newWarehouse.state,
        postal_code: newWarehouse.postal_code,
        capacity_sqft: newWarehouse.capacity_sqft ? parseInt(newWarehouse.capacity_sqft) : null,
        contact_phone: newWarehouse.contact_phone,
        notes: newWarehouse.notes,
      }]);

      if (error) throw error;

      toast.success("Warehouse created successfully");
      setIsCreateDialogOpen(false);
      setNewWarehouse({
        warehouse_code: "",
        warehouse_name: "",
        warehouse_type: "main",
        address: "",
        city: "",
        state: "",
        postal_code: "",
        capacity_sqft: "",
        contact_phone: "",
        notes: "",
      });
      fetchWarehouses();
    } catch (error) {
      console.error("Error creating warehouse:", error);
      toast.error("Failed to create warehouse");
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive"> = {
      active: "default",
      inactive: "secondary",
      maintenance: "destructive",
    };
    return <Badge variant={variants[status] || "default"}>{status}</Badge>;
  };

  const filteredWarehouses = warehouses.filter((warehouse) => {
    return (
      warehouse.warehouse_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      warehouse.warehouse_code.toLowerCase().includes(searchTerm.toLowerCase())
    );
  });

  const stats = {
    total: warehouses.length,
    active: warehouses.filter(w => w.status === "active").length,
    totalCapacity: warehouses.reduce((sum, w) => sum + (w.capacity_sqft || 0), 0),
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation />
      
      <main className="container mx-auto p-6 space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Warehouse Management</h1>
            <p className="text-muted-foreground">Manage warehouse locations and capacity</p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Warehouse
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Add Warehouse</DialogTitle>
                <DialogDescription>Create a new warehouse location</DialogDescription>
              </DialogHeader>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>Warehouse Code</Label>
                  <Input
                    value={newWarehouse.warehouse_code}
                    onChange={(e) => setNewWarehouse({ ...newWarehouse, warehouse_code: e.target.value })}
                    placeholder="WH-001"
                  />
                </div>
                <div>
                  <Label>Warehouse Name</Label>
                  <Input
                    value={newWarehouse.warehouse_name}
                    onChange={(e) => setNewWarehouse({ ...newWarehouse, warehouse_name: e.target.value })}
                    placeholder="Main Warehouse"
                  />
                </div>
                <div>
                  <Label>Type</Label>
                  <Select value={newWarehouse.warehouse_type} onValueChange={(value) => setNewWarehouse({ ...newWarehouse, warehouse_type: value })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="main">Main</SelectItem>
                      <SelectItem value="distribution">Distribution</SelectItem>
                      <SelectItem value="retail">Retail</SelectItem>
                      <SelectItem value="virtual">Virtual</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Capacity (sq ft)</Label>
                  <Input
                    type="number"
                    value={newWarehouse.capacity_sqft}
                    onChange={(e) => setNewWarehouse({ ...newWarehouse, capacity_sqft: e.target.value })}
                    placeholder="10000"
                  />
                </div>
                <div className="col-span-2">
                  <Label>Address</Label>
                  <Input
                    value={newWarehouse.address}
                    onChange={(e) => setNewWarehouse({ ...newWarehouse, address: e.target.value })}
                    placeholder="123 Storage St"
                  />
                </div>
                <div>
                  <Label>City</Label>
                  <Input
                    value={newWarehouse.city}
                    onChange={(e) => setNewWarehouse({ ...newWarehouse, city: e.target.value })}
                    placeholder="City"
                  />
                </div>
                <div>
                  <Label>State</Label>
                  <Input
                    value={newWarehouse.state}
                    onChange={(e) => setNewWarehouse({ ...newWarehouse, state: e.target.value })}
                    placeholder="CA"
                  />
                </div>
                <div>
                  <Label>Postal Code</Label>
                  <Input
                    value={newWarehouse.postal_code}
                    onChange={(e) => setNewWarehouse({ ...newWarehouse, postal_code: e.target.value })}
                    placeholder="12345"
                  />
                </div>
                <div>
                  <Label>Contact Phone</Label>
                  <Input
                    value={newWarehouse.contact_phone}
                    onChange={(e) => setNewWarehouse({ ...newWarehouse, contact_phone: e.target.value })}
                    placeholder="(555) 123-4567"
                  />
                </div>
                <div className="col-span-2">
                  <Label>Notes</Label>
                  <Textarea
                    value={newWarehouse.notes}
                    onChange={(e) => setNewWarehouse({ ...newWarehouse, notes: e.target.value })}
                    placeholder="Additional notes..."
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>Cancel</Button>
                <Button onClick={handleCreateWarehouse}>Create</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Warehouses</CardTitle>
              <Warehouse className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active</CardTitle>
              <MapPin className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.active}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Capacity</CardTitle>
              <Warehouse className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalCapacity.toLocaleString()} sq ft</div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Warehouses</CardTitle>
            <CardDescription>View and manage all warehouse locations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search warehouses..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Code</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Capacity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Contact</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center">Loading...</TableCell>
                  </TableRow>
                ) : filteredWarehouses.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center">No warehouses found</TableCell>
                  </TableRow>
                ) : (
                  filteredWarehouses.map((warehouse) => (
                    <TableRow key={warehouse.id}>
                      <TableCell className="font-medium">{warehouse.warehouse_code}</TableCell>
                      <TableCell>{warehouse.warehouse_name}</TableCell>
                      <TableCell className="capitalize">{warehouse.warehouse_type || "—"}</TableCell>
                      <TableCell>{`${warehouse.city || ""}, ${warehouse.state || ""}`.trim() || warehouse.address}</TableCell>
                      <TableCell>{warehouse.capacity_sqft ? `${warehouse.capacity_sqft.toLocaleString()} sq ft` : "—"}</TableCell>
                      <TableCell>{getStatusBadge(warehouse.status)}</TableCell>
                      <TableCell>{warehouse.contact_phone || "—"}</TableCell>
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
