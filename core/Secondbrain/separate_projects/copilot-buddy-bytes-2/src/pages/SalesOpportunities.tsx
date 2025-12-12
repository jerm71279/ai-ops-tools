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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useToast } from "@/hooks/use-toast";
import { Plus, Search, Target } from "lucide-react";

interface Opportunity {
  id: string;
  opportunity_number: string;
  opportunity_name: string;
  account_name: string;
  contact_name: string;
  stage: string;
  probability: number;
  amount: number;
  expected_close_date: string;
}

const SalesOpportunities = () => {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [stageFilter, setStageFilter] = useState("all");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const { toast } = useToast();

  const [newOpportunity, setNewOpportunity] = useState({
    opportunity_name: "",
    account_name: "",
    contact_name: "",
    contact_email: "",
    amount: "",
    expected_close_date: "",
  });

  useEffect(() => {
    fetchOpportunities();
  }, []);

  const fetchOpportunities = async () => {
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
        .from("sales_opportunities")
        .select("*")
        .eq("customer_id", profile.customer_id)
        .order("created_at", { ascending: false });

      if (error) throw error;
      setOpportunities(data || []);
    } catch (error) {
      console.error("Error fetching opportunities:", error);
      toast({
        title: "Error",
        description: "Failed to load opportunities",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOpportunity = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) return;

      const { error } = await supabase.from("sales_opportunities").insert([
        {
          customer_id: profile.customer_id,
          opportunity_number: "",
          ...newOpportunity,
          amount: parseFloat(newOpportunity.amount),
        },
      ]);

      if (error) throw error;

      toast({
        title: "Success",
        description: "Opportunity created successfully",
      });

      setIsCreateDialogOpen(false);
      setNewOpportunity({
        opportunity_name: "",
        account_name: "",
        contact_name: "",
        contact_email: "",
        amount: "",
        expected_close_date: "",
      });
      fetchOpportunities();
    } catch (error) {
      console.error("Error creating opportunity:", error);
      toast({
        title: "Error",
        description: "Failed to create opportunity",
        variant: "destructive",
      });
    }
  };

  const getStageBadge = (stage: string) => {
    const variants: { [key: string]: "default" | "secondary" | "destructive" | "outline" } = {
      qualification: "default",
      proposal: "secondary",
      negotiation: "outline",
      closed_won: "default",
      closed_lost: "destructive",
    };
    return <Badge variant={variants[stage] || "default"}>{stage.replace("_", " ")}</Badge>;
  };

  const filteredOpportunities = opportunities.filter((opp) => {
    const matchesSearch =
      opp.opportunity_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      opp.account_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      opp.opportunity_number?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStage = stageFilter === "all" || opp.stage === stageFilter;
    
    return matchesSearch && matchesStage;
  });

  const totalValue = opportunities.reduce((sum, opp) => sum + (opp.amount || 0), 0);
  const weightedValue = opportunities.reduce(
    (sum, opp) => sum + (opp.amount || 0) * ((opp.probability || 0) / 100),
    0
  );

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation />
      
      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Sales Opportunities</h1>
            <p className="text-muted-foreground">Manage your sales pipeline</p>
          </div>
          
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Opportunity
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Opportunity</DialogTitle>
              </DialogHeader>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <Label htmlFor="opportunity_name">Opportunity Name*</Label>
                  <Input
                    id="opportunity_name"
                    value={newOpportunity.opportunity_name}
                    onChange={(e) =>
                      setNewOpportunity({ ...newOpportunity, opportunity_name: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="account_name">Account Name*</Label>
                  <Input
                    id="account_name"
                    value={newOpportunity.account_name}
                    onChange={(e) =>
                      setNewOpportunity({ ...newOpportunity, account_name: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="contact_name">Contact Name*</Label>
                  <Input
                    id="contact_name"
                    value={newOpportunity.contact_name}
                    onChange={(e) =>
                      setNewOpportunity({ ...newOpportunity, contact_name: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="contact_email">Contact Email</Label>
                  <Input
                    id="contact_email"
                    type="email"
                    value={newOpportunity.contact_email}
                    onChange={(e) =>
                      setNewOpportunity({ ...newOpportunity, contact_email: e.target.value })
                    }
                  />
                </div>
                <div>
                  <Label htmlFor="amount">Amount*</Label>
                  <Input
                    id="amount"
                    type="number"
                    value={newOpportunity.amount}
                    onChange={(e) =>
                      setNewOpportunity({ ...newOpportunity, amount: e.target.value })
                    }
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="expected_close_date">Expected Close Date</Label>
                  <Input
                    id="expected_close_date"
                    type="date"
                    value={newOpportunity.expected_close_date}
                    onChange={(e) =>
                      setNewOpportunity({ ...newOpportunity, expected_close_date: e.target.value })
                    }
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateOpportunity}>Create Opportunity</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Pipeline</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalValue.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Weighted Pipeline</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${weightedValue.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Open Opportunities</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{opportunities.length}</div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>All Opportunities</CardTitle>
              <div className="flex gap-2">
                <div className="relative">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search opportunities..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8"
                  />
                </div>
                <Select value={stageFilter} onValueChange={setStageFilter}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Stage" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Stages</SelectItem>
                    <SelectItem value="qualification">Qualification</SelectItem>
                    <SelectItem value="proposal">Proposal</SelectItem>
                    <SelectItem value="negotiation">Negotiation</SelectItem>
                    <SelectItem value="closed_won">Closed Won</SelectItem>
                    <SelectItem value="closed_lost">Closed Lost</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p>Loading...</p>
            ) : filteredOpportunities.length === 0 ? (
              <p className="text-muted-foreground">No opportunities found</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Opportunity #</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Account</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Probability</TableHead>
                    <TableHead>Stage</TableHead>
                    <TableHead>Close Date</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredOpportunities.map((opp) => (
                    <TableRow key={opp.id}>
                      <TableCell className="font-medium">{opp.opportunity_number}</TableCell>
                      <TableCell>{opp.opportunity_name}</TableCell>
                      <TableCell>{opp.account_name}</TableCell>
                      <TableCell>${opp.amount?.toLocaleString()}</TableCell>
                      <TableCell>{opp.probability || 0}%</TableCell>
                      <TableCell>{getStageBadge(opp.stage)}</TableCell>
                      <TableCell>
                        {opp.expected_close_date
                          ? new Date(opp.expected_close_date).toLocaleDateString()
                          : "-"}
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

export default SalesOpportunities;