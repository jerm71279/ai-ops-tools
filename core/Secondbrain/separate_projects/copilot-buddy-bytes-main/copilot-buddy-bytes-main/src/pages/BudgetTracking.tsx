import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { Plus, Search, DollarSign, TrendingUp, AlertTriangle } from "lucide-react";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";

interface Budget {
  id: string;
  budget_name: string;
  budget_type: string;
  fiscal_year: number;
  allocated_amount: number;
  spent_amount: number;
  committed_amount: number;
  remaining_amount: number;
  utilization_percentage: number;
  status: string;
  period_start: string;
  period_end: string;
}

export default function BudgetTracking() {
  const navigate = useNavigate();
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [customerId, setCustomerId] = useState<string | null>(null);

  const [newBudget, setNewBudget] = useState({
    budget_name: "",
    budget_type: "department",
    fiscal_year: new Date().getFullYear(),
    allocated_amount: "",
    period_start: "",
    period_end: "",
    department: "",
    notes: "",
  });

  useEffect(() => {
    fetchUserProfile();
  }, []);

  useEffect(() => {
    if (customerId) {
      fetchBudgets();
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

  const fetchBudgets = async () => {
    try {
      setLoading(true);
      const { data, error } = await supabase
        .from("budgets")
        .select("*")
        .eq("customer_id", customerId!)
        .order("fiscal_year", { ascending: false });

      if (error) throw error;
      setBudgets(data || []);
    } catch (error) {
      console.error("Error fetching budgets:", error);
      toast.error("Failed to load budgets");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBudget = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user || !customerId) return;

      const { error } = await supabase.from("budgets").insert([{
        customer_id: customerId,
        budget_name: newBudget.budget_name,
        budget_type: newBudget.budget_type,
        fiscal_year: newBudget.fiscal_year,
        allocated_amount: parseFloat(newBudget.allocated_amount),
        period_start: newBudget.period_start,
        period_end: newBudget.period_end,
        department: newBudget.department || null,
        notes: newBudget.notes,
        owner_id: user.id,
      }]);

      if (error) throw error;

      toast.success("Budget created successfully");
      setIsCreateDialogOpen(false);
      setNewBudget({
        budget_name: "",
        budget_type: "department",
        fiscal_year: new Date().getFullYear(),
        allocated_amount: "",
        period_start: "",
        period_end: "",
        department: "",
        notes: "",
      });
      fetchBudgets();
    } catch (error) {
      console.error("Error creating budget:", error);
      toast.error("Failed to create budget");
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, "default" | "secondary" | "destructive" | "outline"> = {
      draft: "outline",
      active: "default",
      locked: "secondary",
      closed: "destructive",
    };
    return <Badge variant={variants[status] || "default"}>{status}</Badge>;
  };

  const getUtilizationColor = (percentage: number) => {
    if (percentage >= 90) return "text-destructive";
    if (percentage >= 75) return "text-yellow-600";
    return "text-green-600";
  };

  const filteredBudgets = budgets.filter((budget) => {
    const matchesSearch = budget.budget_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = typeFilter === "all" || budget.budget_type === typeFilter;
    return matchesSearch && matchesType;
  });

  const stats = {
    total: budgets.filter(b => b.status === "active").length,
    totalAllocated: budgets.reduce((sum, b) => sum + parseFloat(b.allocated_amount.toString()), 0),
    totalSpent: budgets.reduce((sum, b) => sum + parseFloat(b.spent_amount.toString()), 0),
    overBudget: budgets.filter(b => parseFloat(b.utilization_percentage.toString()) > 100).length,
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation />
      
      <main className="container mx-auto p-6 space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Budget Tracking</h1>
            <p className="text-muted-foreground">Monitor and manage organizational budgets</p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Budget
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Budget</DialogTitle>
                <DialogDescription>Create a new budget allocation</DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label>Budget Name</Label>
                  <Input
                    value={newBudget.budget_name}
                    onChange={(e) => setNewBudget({ ...newBudget, budget_name: e.target.value })}
                    placeholder="e.g., IT Department Q4 2025"
                  />
                </div>
                <div>
                  <Label>Budget Type</Label>
                  <Select value={newBudget.budget_type} onValueChange={(value) => setNewBudget({ ...newBudget, budget_type: value })}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="department">Department</SelectItem>
                      <SelectItem value="project">Project</SelectItem>
                      <SelectItem value="category">Category</SelectItem>
                      <SelectItem value="vendor">Vendor</SelectItem>
                      <SelectItem value="annual">Annual</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Fiscal Year</Label>
                  <Input
                    type="number"
                    value={newBudget.fiscal_year}
                    onChange={(e) => setNewBudget({ ...newBudget, fiscal_year: parseInt(e.target.value) })}
                  />
                </div>
                <div>
                  <Label>Allocated Amount</Label>
                  <Input
                    type="number"
                    value={newBudget.allocated_amount}
                    onChange={(e) => setNewBudget({ ...newBudget, allocated_amount: e.target.value })}
                    placeholder="0.00"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Period Start</Label>
                    <Input
                      type="date"
                      value={newBudget.period_start}
                      onChange={(e) => setNewBudget({ ...newBudget, period_start: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label>Period End</Label>
                    <Input
                      type="date"
                      value={newBudget.period_end}
                      onChange={(e) => setNewBudget({ ...newBudget, period_end: e.target.value })}
                    />
                  </div>
                </div>
                {newBudget.budget_type === "department" && (
                  <div>
                    <Label>Department</Label>
                    <Input
                      value={newBudget.department}
                      onChange={(e) => setNewBudget({ ...newBudget, department: e.target.value })}
                      placeholder="Department name"
                    />
                  </div>
                )}
                <div>
                  <Label>Notes</Label>
                  <Textarea
                    value={newBudget.notes}
                    onChange={(e) => setNewBudget({ ...newBudget, notes: e.target.value })}
                    placeholder="Budget notes..."
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>Cancel</Button>
                <Button onClick={handleCreateBudget}>Create</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Budgets</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Allocated</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.totalAllocated.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Spent</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${stats.totalSpent.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Over Budget</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.overBudget}</div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Budgets</CardTitle>
            <CardDescription>View and manage all budget allocations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4 mb-4">
              <div className="relative flex-1">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search budgets..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Filter by type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="department">Department</SelectItem>
                  <SelectItem value="project">Project</SelectItem>
                  <SelectItem value="category">Category</SelectItem>
                  <SelectItem value="vendor">Vendor</SelectItem>
                  <SelectItem value="annual">Annual</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Budget Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>FY</TableHead>
                  <TableHead>Allocated</TableHead>
                  <TableHead>Spent</TableHead>
                  <TableHead>Remaining</TableHead>
                  <TableHead>Utilization</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center">Loading...</TableCell>
                  </TableRow>
                ) : filteredBudgets.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center">No budgets found</TableCell>
                  </TableRow>
                ) : (
                  filteredBudgets.map((budget) => (
                    <TableRow key={budget.id}>
                      <TableCell className="font-medium">{budget.budget_name}</TableCell>
                      <TableCell>{budget.budget_type}</TableCell>
                      <TableCell>{budget.fiscal_year}</TableCell>
                      <TableCell>${parseFloat(budget.allocated_amount.toString()).toLocaleString()}</TableCell>
                      <TableCell>${parseFloat(budget.spent_amount.toString()).toLocaleString()}</TableCell>
                      <TableCell>${parseFloat(budget.remaining_amount.toString()).toLocaleString()}</TableCell>
                      <TableCell>
                        <div className="space-y-1">
                          <div className={`text-sm font-medium ${getUtilizationColor(parseFloat(budget.utilization_percentage.toString()))}`}>
                            {parseFloat(budget.utilization_percentage.toString()).toFixed(1)}%
                          </div>
                          <Progress value={Math.min(parseFloat(budget.utilization_percentage.toString()), 100)} />
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(budget.status)}</TableCell>
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
