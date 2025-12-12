import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";
import { BarChart, DollarSign, TrendingUp, TrendingDown, FileText, Download } from "lucide-react";
import Navigation from "@/components/Navigation";
import DashboardNavigation from "@/components/DashboardNavigation";

export default function FinancialReporting() {
  const navigate = useNavigate();
  const [customerId, setCustomerId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [reportPeriod, setReportPeriod] = useState("current_month");
  const [financialData, setFinancialData] = useState({
    totalRevenue: 0,
    totalExpenses: 0,
    totalPOs: 0,
    totalInvoices: 0,
    budgetUtilization: 0,
    profitMargin: 0,
  });

  useEffect(() => {
    fetchUserProfile();
  }, []);

  useEffect(() => {
    if (customerId) {
      fetchFinancialData();
    }
  }, [customerId, reportPeriod]);

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

  const fetchFinancialData = async () => {
    try {
      setLoading(true);

      const [invoicesData, expensesData, posData, budgetsData] = await Promise.all([
        supabase.from("invoices").select("total_amount, status").eq("customer_id", customerId!),
        supabase.from("expenses").select("amount, approval_status").eq("customer_id", customerId!),
        supabase.from("purchase_orders").select("total_amount, status").eq("customer_id", customerId!),
        supabase.from("budgets").select("allocated_amount, spent_amount, status").eq("customer_id", customerId!),
      ]);

      const totalRevenue = invoicesData.data
        ?.filter(inv => inv.status === "paid")
        .reduce((sum, inv) => sum + parseFloat(inv.total_amount.toString()), 0) || 0;

      const totalExpenses = expensesData.data
        ?.filter(exp => exp.approval_status === "approved")
        .reduce((sum, exp) => sum + parseFloat(exp.amount.toString()), 0) || 0;

      const totalPOs = posData.data
        ?.reduce((sum, po) => sum + parseFloat(po.total_amount.toString()), 0) || 0;

      const totalInvoices = invoicesData.data?.length || 0;

      const activeBudgets = budgetsData.data?.filter(b => b.status === "active") || [];
      const totalAllocated = activeBudgets.reduce((sum, b) => sum + parseFloat(b.allocated_amount.toString()), 0);
      const totalSpent = activeBudgets.reduce((sum, b) => sum + parseFloat(b.spent_amount.toString()), 0);
      const budgetUtilization = totalAllocated > 0 ? (totalSpent / totalAllocated) * 100 : 0;

      const profitMargin = totalRevenue > 0 ? ((totalRevenue - totalExpenses) / totalRevenue) * 100 : 0;

      setFinancialData({
        totalRevenue,
        totalExpenses,
        totalPOs,
        totalInvoices,
        budgetUtilization,
        profitMargin,
      });
    } catch (error) {
      console.error("Error fetching financial data:", error);
      toast.error("Failed to load financial data");
    } finally {
      setLoading(false);
    }
  };

  const handleExport = () => {
    toast.success("Report export functionality coming soon");
  };

  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      <DashboardNavigation />
      
      <main className="container mx-auto p-6 space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Financial Reporting</h1>
            <p className="text-muted-foreground">Comprehensive financial analytics and insights</p>
          </div>
          <div className="flex gap-4">
            <Select value={reportPeriod} onValueChange={setReportPeriod}>
              <SelectTrigger className="w-[200px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="current_month">Current Month</SelectItem>
                <SelectItem value="last_month">Last Month</SelectItem>
                <SelectItem value="current_quarter">Current Quarter</SelectItem>
                <SelectItem value="last_quarter">Last Quarter</SelectItem>
                <SelectItem value="current_year">Current Year</SelectItem>
                <SelectItem value="last_year">Last Year</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={handleExport}>
              <Download className="mr-2 h-4 w-4" />
              Export Report
            </Button>
          </div>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${financialData.totalRevenue.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground mt-1">From paid invoices</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Expenses</CardTitle>
              <TrendingDown className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${financialData.totalExpenses.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground mt-1">Approved expenses</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Profit Margin</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{financialData.profitMargin.toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground mt-1">Revenue minus expenses</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Purchase Orders</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">${financialData.totalPOs.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground mt-1">Total PO value</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Invoices Issued</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{financialData.totalInvoices}</div>
              <p className="text-xs text-muted-foreground mt-1">Total count</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Budget Utilization</CardTitle>
              <BarChart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{financialData.budgetUtilization.toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground mt-1">Of allocated budget</p>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Financial Overview</CardTitle>
            <CardDescription>Key financial metrics and performance indicators</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Net Income</span>
                <span className="text-2xl font-bold">
                  ${(financialData.totalRevenue - financialData.totalExpenses).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Expense Ratio</span>
                <span className="text-lg font-semibold">
                  {financialData.totalRevenue > 0 
                    ? ((financialData.totalExpenses / financialData.totalRevenue) * 100).toFixed(1) 
                    : 0}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm font-medium">Average Invoice Value</span>
                <span className="text-lg font-semibold">
                  ${financialData.totalInvoices > 0 
                    ? (financialData.totalRevenue / financialData.totalInvoices).toLocaleString() 
                    : 0}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
