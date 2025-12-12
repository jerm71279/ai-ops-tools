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
import { Plus, Search, FileText } from "lucide-react";

interface Quote {
  id: string;
  quote_number: string;
  quote_name: string;
  account_name: string;
  contact_name: string;
  quote_date: string;
  expiry_date: string;
  total_amount: number;
  quote_status: string;
}

const SalesQuotes = () => {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const { toast } = useToast();

  const [newQuote, setNewQuote] = useState({
    quote_name: "",
    account_name: "",
    contact_name: "",
    contact_email: "",
    expiry_date: "",
    total_amount: "",
  });

  useEffect(() => {
    fetchQuotes();
  }, []);

  const fetchQuotes = async () => {
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
        .from("sales_quotes")
        .select("*")
        .eq("customer_id", profile.customer_id)
        .order("created_at", { ascending: false });

      if (error) throw error;
      setQuotes(data || []);
    } catch (error) {
      console.error("Error fetching quotes:", error);
      toast({
        title: "Error",
        description: "Failed to load quotes",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateQuote = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: profile } = await supabase
        .from("user_profiles")
        .select("customer_id")
        .eq("user_id", user.id)
        .single();

      if (!profile?.customer_id) return;

      const { error } = await supabase.from("sales_quotes").insert([
        {
          customer_id: profile.customer_id,
          quote_number: "",
          created_by: user.id,
          ...newQuote,
          total_amount: parseFloat(newQuote.total_amount),
        },
      ]);

      if (error) throw error;

      toast({
        title: "Success",
        description: "Quote created successfully",
      });

      setIsCreateDialogOpen(false);
      setNewQuote({
        quote_name: "",
        account_name: "",
        contact_name: "",
        contact_email: "",
        expiry_date: "",
        total_amount: "",
      });
      fetchQuotes();
    } catch (error) {
      console.error("Error creating quote:", error);
      toast({
        title: "Error",
        description: "Failed to create quote",
        variant: "destructive",
      });
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: { [key: string]: "default" | "secondary" | "destructive" | "outline" } = {
      draft: "secondary",
      sent: "default",
      accepted: "default",
      declined: "destructive",
      expired: "destructive",
    };
    return <Badge variant={variants[status] || "default"}>{status}</Badge>;
  };

  const filteredQuotes = quotes.filter((quote) => {
    const matchesSearch =
      quote.quote_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      quote.account_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      quote.quote_number?.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === "all" || quote.quote_status === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

  const totalQuoteValue = quotes.reduce((sum, quote) => sum + (quote.total_amount || 0), 0);
  const acceptedQuotes = quotes.filter((q) => q.quote_status === "accepted");

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation />
      
      <main className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Sales Quotes</h1>
            <p className="text-muted-foreground">Create and manage sales quotes</p>
          </div>
          
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Quote
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Quote</DialogTitle>
              </DialogHeader>
              <div className="grid grid-cols-2 gap-4">
                <div className="col-span-2">
                  <Label htmlFor="quote_name">Quote Name*</Label>
                  <Input
                    id="quote_name"
                    value={newQuote.quote_name}
                    onChange={(e) => setNewQuote({ ...newQuote, quote_name: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="account_name">Account Name*</Label>
                  <Input
                    id="account_name"
                    value={newQuote.account_name}
                    onChange={(e) => setNewQuote({ ...newQuote, account_name: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="contact_name">Contact Name*</Label>
                  <Input
                    id="contact_name"
                    value={newQuote.contact_name}
                    onChange={(e) => setNewQuote({ ...newQuote, contact_name: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="contact_email">Contact Email</Label>
                  <Input
                    id="contact_email"
                    type="email"
                    value={newQuote.contact_email}
                    onChange={(e) => setNewQuote({ ...newQuote, contact_email: e.target.value })}
                  />
                </div>
                <div>
                  <Label htmlFor="total_amount">Total Amount*</Label>
                  <Input
                    id="total_amount"
                    type="number"
                    value={newQuote.total_amount}
                    onChange={(e) => setNewQuote({ ...newQuote, total_amount: e.target.value })}
                  />
                </div>
                <div className="col-span-2">
                  <Label htmlFor="expiry_date">Expiry Date</Label>
                  <Input
                    id="expiry_date"
                    type="date"
                    value={newQuote.expiry_date}
                    onChange={(e) => setNewQuote({ ...newQuote, expiry_date: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateQuote}>Create Quote</Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Quote Value</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${totalQuoteValue.toLocaleString()}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Accepted Quotes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{acceptedQuotes.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Quotes</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{quotes.length}</div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <CardTitle>All Quotes</CardTitle>
              <div className="flex gap-2">
                <div className="relative">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search quotes..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-8"
                  />
                </div>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="sent">Sent</SelectItem>
                    <SelectItem value="accepted">Accepted</SelectItem>
                    <SelectItem value="declined">Declined</SelectItem>
                    <SelectItem value="expired">Expired</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p>Loading...</p>
            ) : filteredQuotes.length === 0 ? (
              <p className="text-muted-foreground">No quotes found</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Quote #</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Account</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredQuotes.map((quote) => (
                    <TableRow key={quote.id}>
                      <TableCell className="font-medium">{quote.quote_number}</TableCell>
                      <TableCell>{quote.quote_name}</TableCell>
                      <TableCell>{quote.account_name}</TableCell>
                      <TableCell>{quote.contact_name}</TableCell>
                      <TableCell>${quote.total_amount?.toLocaleString()}</TableCell>
                      <TableCell>
                        {new Date(quote.quote_date).toLocaleDateString()}
                      </TableCell>
                      <TableCell>{getStatusBadge(quote.quote_status)}</TableCell>
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

export default SalesQuotes;