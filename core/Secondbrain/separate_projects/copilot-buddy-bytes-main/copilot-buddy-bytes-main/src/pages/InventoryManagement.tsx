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
import { Plus, Search, Package, AlertTriangle, TrendingUp } from "lucide-react";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";

interface InventoryItem {
  id: string;
  sku: string;
  item_name: string;
  category: string;
  current_quantity: number;
  reorder_point: number;
  unit_cost: number | null;
  unit_price: number | null;
  location: string | null;
  status: string;
  created_at: string;
}

export default function InventoryManagement() {
  const navigate = useNavigate();
  const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [customerId, setCustomerId] = useState<string | null>(null);

  const [newItem, setNewItem] = useState({
    sku: "",
    item_name: "",
    category: "",
    description: "",
    current_quantity: "",
    reorder_point: "",
    reorder_quantity: "",
    unit_cost: "",
    unit_price: "",
    location: "",
  });

  useEffect(() => {
    fetchUserProfile();
  }, []);

  useEffect(() => {
    if (customerId) {
      fetchInventory();
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

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from("inventory_items")
        .select("*")
        .eq("customer_id", customerId!)
        .order("created_at", { ascending: false });

      if (error) throw error;
      setInventoryItems(data || []);
    } catch (error) {
      console.error("Error fetching inventory:", error);
      toast.error("Failed to load inventory");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateItem = async () => {
    try {
      if (!customerId) return;

      const { error } = await supabase.from("inventory_items").insert([{
        customer_id: customerId,
        sku: newItem.sku,
        item_name: newItem.item_name,
        category: newItem.category,
        description: newItem.description,
        current_quantity: parseInt(newItem.current_quantity) || 0,
        reorder_point: parseInt(newItem.reorder_point) || 0,
        reorder_quantity: parseInt(newItem.reorder_quantity) || 0,
        unit_cost: newItem.unit_cost ? parseFloat(newItem.unit_cost) : null,
        unit_price: newItem.unit_price ? parseFloat(newItem.unit_price) : null,
        location: newItem.location,
      }]);

      if (error) throw error;

      toast.success("Inventory item created successfully");
      setIsCreateDialogOpen(false);
      setNewItem({
        sku: "",
        item_name: "",
        category: "",
        description: "",
        current_quantity: "",
        reorder_point: "",
        reorder_quantity: "",
        unit_cost: "",
        unit_price: "",
        location: "",
      });
      fetchInventory();
    } catch (error) {
      console.error("Error creating inventory item:", error);
      toast.error("Failed to create inventory item");
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      active: "default",
      discontinued: "secondary",
      out_of_stock: "destructive",
      backordered: "outline",
    };
    return <Badge variant={variants[status] || "default"}>{status.replace("_", " ")}</Badge>;
  };

  const getStockLevel = (item: InventoryItem) => {
    if (item.current_quantity <= 0) return { color: "text-red-600", label: "Out of Stock" };
    if (item.current_quantity <= item.reorder_point) return { color: "text-yellow-600", label: "Low Stock" };
    return { color: "text-green-600", label: "In Stock" };
  };

  const filteredItems = inventoryItems.filter((item) => {
    const matchesSearch =
      item.item_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.sku.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === "all" || item.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const stats = {
    total: inventoryItems.length,
    lowStock: inventoryItems.filter(i => i.current_quantity <= i.reorder_point).length,
    outOfStock: inventoryItems.filter(i => i.current_quantity <= 0).length,
    totalValue: inventoryItems.reduce((sum, i) => sum + (i.current_quantity * (parseFloat(i.unit_cost?.toString() || "0"))), 0),
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation />
      
      <main className="container mx-auto p-6 space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Inventory Management</h1>
            <p className="text-muted-foreground">Track and manage inventory stock levels</p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Item
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Add Inventory Item</DialogTitle>
                <DialogDescription>Create a new inventory item</DialogDescription>
              </DialogHeader>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label>SKU</Label>
                  <Input
                    value={newItem.sku}
                    onChange={(e) => setNewItem({ ...newItem, sku: e.target.value })}
                    placeholder="SKU-12345"
                  />
                </div>
                <div>
                  <Label>Item Name</Label>
                  <Input
                    value={newItem.item_name}
                    onChange={(e) => setNewItem({ ...newItem, item_name: e.target.value })}
                    placeholder="Product name"
                  />
                </div>
                <div>
                  <Label>Category</Label>
                  <Input
                    value={newItem.category}
                    onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
                    placeholder="Electronics"
                  />
                </div>
                <div>
                  <Label>Location</Label>
                  <Input
                    value={newItem.location}
                    onChange={(e) => setNewItem({ ...newItem, location: e.target.value })}
                    placeholder="Warehouse A"
                  />
                </div>
                <div>
                  <Label>Current Quantity</Label>
                  <Input
                    type="number"
                    value={newItem.current_quantity}
                    onChange={(e) => setNewItem({ ...newItem, current_quantity: e.target.value })}
                    placeholder="0"
                  />
                </div>
                <div>
                  <Label>Reorder Point</Label>
                  <Input
                    type="number"
                    value={newItem.reorder_point}
                    onChange={(e) => setNewItem({ ...newItem, reorder_point: e.target.value })}
                    placeholder="10"
                  />
                </div>
                <div>
                  <Label>Reorder Quantity</Label>
                  <Input
                    type="number"
                    value={newItem.reorder_quantity}
                    onChange={(e) => setNewItem({ ...newItem, reorder_quantity: e.target.value })}
                    placeholder="50"
                  />
                </div>
                <div>
                  <Label>Unit Cost</Label>
                  <Input
                    type="number"
                    value={newItem.unit_cost}
                    onChange={(e) => setNewItem({ ...newItem, unit_cost: e.target.value })}
                    placeholder="0.00"
                  />
                </div>
                <div>
                  <Label>Unit Price</Label>
                  <Input
                    type="number"
                    value={newItem.unit_price}
                    onChange={(e) => setNewItem({ ...newItem, unit_price: e.target.value })}
                    placeholder="0.00"
                  />
                </div>
                <div className="col-span-2">
                  <Label>Description</Label>
                  <Textarea
                    value={newItem.description}
                    onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
                    placeholder="Item description..."
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>Cancel</Button>
                <Button onClick={handleCreateItem}>Create</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Items</CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Low Stock</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{stats.lowStock}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Out of Stock</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.outOfStock}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Value</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.totalValue.toLocaleString()}</div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Inventory Items</CardTitle>
            <CardDescription>View and manage all inventory items</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search items..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Filter by status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="discontinued">Discontinued</SelectItem>
                  <SelectItem value="out_of_stock">Out of Stock</SelectItem>
                  <SelectItem value="backordered">Backordered</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>SKU</TableHead>
                  <TableHead>Item Name</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Quantity</TableHead>
                  <TableHead>Reorder Point</TableHead>
                  <TableHead>Stock Level</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Location</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center">Loading...</TableCell>
                  </TableRow>
                ) : filteredItems.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center">No inventory items found</TableCell>
                  </TableRow>
                ) : (
                  filteredItems.map((item) => {
                    const stockLevel = getStockLevel(item);
                    return (
                      <TableRow key={item.id}>
                        <TableCell className="font-medium">{item.sku}</TableCell>
                        <TableCell>{item.item_name}</TableCell>
                        <TableCell>{item.category}</TableCell>
                        <TableCell>{item.current_quantity}</TableCell>
                        <TableCell>{item.reorder_point}</TableCell>
                        <TableCell>
                          <span className={stockLevel.color}>{stockLevel.label}</span>
                        </TableCell>
                        <TableCell>{getStatusBadge(item.status)}</TableCell>
                        <TableCell>{item.location || "—"}</TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
