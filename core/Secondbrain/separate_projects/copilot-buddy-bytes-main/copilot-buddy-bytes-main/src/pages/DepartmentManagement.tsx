import { useState, useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Plus, Building, Folder } from "lucide-react";

interface Department {
  id: string;
  department_name: string;
  department_code: string;
  location: string;
  budget_allocation: number;
  is_active: boolean;
}

const DepartmentManagement = () => {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const { toast } = useToast();

  const [newDepartment, setNewDepartment] = useState({
    department_name: "",
    department_code: "",
    location: "",
    budget_allocation: "",
    description: "",
  });

  useEffect(() => {
    fetchDepartments();
  }, []);

  const fetchDepartments = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) return;

      const { data, error } = await supabase
        .from("departments")
        .select("*")
        .eq("customer_id", profile.customer_id)
        .order("department_name");

      if (error) throw error;
      setDepartments(data || []);
    } catch (error) {
      console.error("Error fetching departments:", error);
      toast({
        title: "Error",
        description: "Failed to load departments",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDepartment = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) return;

      const { error } = await supabase.from("departments").insert([
        {
          customer_id: profile.customer_id,
          ...newDepartment,
          budget_allocation: parseFloat(newDepartment.budget_allocation) || null,
        },
      ]);

      if (error) throw error;

      toast({
        title: "Success",
        description: "Department created successfully",
      });

      setIsCreateDialogOpen(false);
      setNewDepartment({
        department_name: "",
        department_code: "",
        location: "",
        budget_allocation: "",
        description: "",
      });
      fetchDepartments();
    } catch (error) {
      console.error("Error creating department:", error);
      toast({
        title: "Error",
        description: "Failed to create department",
        variant: "destructive",
      });
    }
  };

  const totalBudget = departments.reduce(
    (sum, dept) => sum + (dept.budget_allocation || 0),
    0
  );

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation />
      
      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Department Management</h1>
            <p className="text-muted-foreground">Manage organizational departments</p>
          </div>
          
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Department
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Department</DialogTitle>
              </DialogHeader>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="department_name">Department Name*</Label>
                  <Input
                    id="department_name"
                    value={newDepartment.department_name}
                    onChange={(e) =>
                      setNewDepartment({ ...newDepartment, department_name: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="department_code">Department Code*</Label>
                  <Input
                    id="department_code"
                    value={newDepartment.department_code}
                    onChange={(e) =>
                      setNewDepartment({ ...newDepartment, department_code: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    value={newDepartment.location}
                    onChange={(e) =>
                      setNewDepartment({ ...newDepartment, location: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="budget_allocation">Budget Allocation</Label>
                  <Input
                    id="budget_allocation"
                    type="number"
                    value={newDepartment.budget_allocation}
                    onChange={(e) =>
                      setNewDepartment({ ...newDepartment, budget_allocation: e.target.value })
                    }
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={newDepartment.description}
                    onChange={(e) =>
                      setNewDepartment({ ...newDepartment, description: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateDepartment}>Create Department</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Departments</CardTitle>
              <Building className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{departments.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Departments</CardTitle>
              <Folder className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {departments.filter((d) => d.is_active).length}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Budget</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalBudget.toLocaleString()}</div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>All Departments</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p>Loading...</p>
            ) : departments.length === 0 ? (
              <p className="text-muted-foreground">No departments found</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Department Name</TableHead>
                    <TableHead>Code</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Budget</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {departments.map((dept) => (
                    <TableRow key={dept.id}>
                      <TableCell className="font-medium">{dept.department_name}</TableCell>
                      <TableCell>{dept.department_code}</TableCell>
                      <TableCell>{dept.location || "-"}</TableCell>
                      <TableCell>
                        {dept.budget_allocation
                          ? `$${dept.budget_allocation.toLocaleString()}`
                          : "-"}
                      </TableCell>
                      <TableCell>
                        {dept.is_active ? (
                          <Badge>Active</Badge>
                        ) : (
                          <Badge variant="secondary">Inactive</Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default DepartmentManagement;