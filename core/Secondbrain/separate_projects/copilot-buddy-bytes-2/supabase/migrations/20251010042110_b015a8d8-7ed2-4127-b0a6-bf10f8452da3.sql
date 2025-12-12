-- Purchase Orders
CREATE TABLE public.purchase_orders (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  po_number TEXT NOT NULL UNIQUE,
  vendor_name TEXT NOT NULL,
  vendor_id UUID,
  requested_by UUID NOT NULL,
  approved_by UUID,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending_approval', 'approved', 'ordered', 'received', 'cancelled')),
  priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  total_amount NUMERIC(12,2) NOT NULL DEFAULT 0,
  currency TEXT NOT NULL DEFAULT 'USD',
  shipping_address TEXT,
  billing_address TEXT,
  payment_terms TEXT,
  delivery_date DATE,
  notes TEXT,
  items JSONB DEFAULT '[]'::jsonb,
  attachments JSONB DEFAULT '[]'::jsonb,
  approval_workflow JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  submitted_at TIMESTAMP WITH TIME ZONE,
  approved_at TIMESTAMP WITH TIME ZONE,
  received_at TIMESTAMP WITH TIME ZONE
);

ALTER TABLE public.purchase_orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view POs in their organization"
  ON public.purchase_orders FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can create POs"
  ON public.purchase_orders FOR INSERT
  WITH CHECK (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()) AND requested_by = auth.uid());

CREATE POLICY "Users can update POs in their organization"
  ON public.purchase_orders FOR UPDATE
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Expenses
CREATE TABLE public.expenses (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  expense_number TEXT NOT NULL UNIQUE,
  submitted_by UUID NOT NULL,
  approved_by UUID,
  category TEXT NOT NULL,
  merchant TEXT NOT NULL,
  amount NUMERIC(10,2) NOT NULL,
  currency TEXT NOT NULL DEFAULT 'USD',
  expense_date DATE NOT NULL,
  description TEXT,
  payment_method TEXT,
  receipt_url TEXT,
  project_id UUID,
  billable BOOLEAN DEFAULT false,
  reimbursement_status TEXT NOT NULL DEFAULT 'pending' CHECK (reimbursement_status IN ('pending', 'approved', 'rejected', 'paid')),
  approval_status TEXT NOT NULL DEFAULT 'pending' CHECK (approval_status IN ('pending', 'approved', 'rejected')),
  notes TEXT,
  tags TEXT[],
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  submitted_at TIMESTAMP WITH TIME ZONE,
  approved_at TIMESTAMP WITH TIME ZONE,
  paid_at TIMESTAMP WITH TIME ZONE
);

ALTER TABLE public.expenses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their expenses"
  ON public.expenses FOR SELECT
  USING (submitted_by = auth.uid() OR customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can create expenses"
  ON public.expenses FOR INSERT
  WITH CHECK (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()) AND submitted_by = auth.uid());

CREATE POLICY "Users can update their expenses"
  ON public.expenses FOR UPDATE
  USING (submitted_by = auth.uid() OR has_role(auth.uid(), 'admin'));

-- Budgets
CREATE TABLE public.budgets (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  budget_name TEXT NOT NULL,
  budget_type TEXT NOT NULL CHECK (budget_type IN ('department', 'project', 'category', 'vendor', 'annual')),
  department TEXT,
  category TEXT,
  fiscal_year INTEGER NOT NULL,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  allocated_amount NUMERIC(12,2) NOT NULL,
  spent_amount NUMERIC(12,2) DEFAULT 0,
  committed_amount NUMERIC(12,2) DEFAULT 0,
  remaining_amount NUMERIC(12,2) GENERATED ALWAYS AS (allocated_amount - spent_amount - committed_amount) STORED,
  utilization_percentage NUMERIC(5,2) GENERATED ALWAYS AS (CASE WHEN allocated_amount > 0 THEN ((spent_amount + committed_amount) / allocated_amount * 100) ELSE 0 END) STORED,
  owner_id UUID,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('draft', 'active', 'locked', 'closed')),
  alert_threshold NUMERIC(5,2) DEFAULT 80,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

ALTER TABLE public.budgets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view budgets in their organization"
  ON public.budgets FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Admins can manage budgets"
  ON public.budgets FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- Invoices (separate from Revio integration)
CREATE TABLE public.invoices (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  invoice_number TEXT NOT NULL UNIQUE,
  client_id UUID,
  client_name TEXT NOT NULL,
  issue_date DATE NOT NULL,
  due_date DATE NOT NULL,
  paid_date DATE,
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'sent', 'paid', 'overdue', 'cancelled', 'refunded')),
  subtotal NUMERIC(12,2) NOT NULL DEFAULT 0,
  tax_amount NUMERIC(12,2) DEFAULT 0,
  discount_amount NUMERIC(12,2) DEFAULT 0,
  total_amount NUMERIC(12,2) NOT NULL,
  currency TEXT NOT NULL DEFAULT 'USD',
  payment_terms TEXT,
  payment_method TEXT,
  line_items JSONB DEFAULT '[]'::jsonb,
  notes TEXT,
  project_id UUID,
  purchase_order_id UUID,
  created_by UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  sent_at TIMESTAMP WITH TIME ZONE
);

ALTER TABLE public.invoices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view invoices in their organization"
  ON public.invoices FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage invoices"
  ON public.invoices FOR ALL
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Asset Financials (extends CMDB)
CREATE TABLE public.asset_financials (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  ci_id UUID NOT NULL,
  purchase_price NUMERIC(12,2),
  current_value NUMERIC(12,2),
  depreciation_method TEXT CHECK (depreciation_method IN ('straight_line', 'declining_balance', 'units_of_production', 'none')),
  depreciation_rate NUMERIC(5,2),
  salvage_value NUMERIC(12,2),
  useful_life_years INTEGER,
  acquisition_date DATE,
  disposal_date DATE,
  total_cost_ownership NUMERIC(12,2),
  maintenance_cost_ytd NUMERIC(12,2) DEFAULT 0,
  lease_monthly_cost NUMERIC(10,2),
  lease_start_date DATE,
  lease_end_date DATE,
  insurance_cost NUMERIC(10,2),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(ci_id)
);

ALTER TABLE public.asset_financials ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view asset financials in their organization"
  ON public.asset_financials FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage asset financials"
  ON public.asset_financials FOR ALL
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Budget Transactions (for tracking actual spend against budgets)
CREATE TABLE public.budget_transactions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  budget_id UUID NOT NULL REFERENCES public.budgets(id) ON DELETE CASCADE,
  transaction_type TEXT NOT NULL CHECK (transaction_type IN ('expense', 'purchase_order', 'invoice', 'adjustment')),
  reference_id UUID,
  reference_type TEXT,
  amount NUMERIC(12,2) NOT NULL,
  description TEXT,
  transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

ALTER TABLE public.budget_transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view budget transactions"
  ON public.budget_transactions FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "System can insert budget transactions"
  ON public.budget_transactions FOR INSERT
  WITH CHECK (true);

-- Auto-generate PO numbers
CREATE SEQUENCE IF NOT EXISTS po_number_seq;

CREATE OR REPLACE FUNCTION public.generate_po_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'PO' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('po_number_seq')::TEXT, 4, '0');
END;
$$;

CREATE OR REPLACE FUNCTION public.set_po_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.po_number IS NULL THEN
    NEW.po_number := generate_po_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_po_number_trigger
  BEFORE INSERT ON public.purchase_orders
  FOR EACH ROW
  EXECUTE FUNCTION public.set_po_number();

-- Auto-generate expense numbers
CREATE SEQUENCE IF NOT EXISTS expense_number_seq;

CREATE OR REPLACE FUNCTION public.generate_expense_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'EXP' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('expense_number_seq')::TEXT, 4, '0');
END;
$$;

CREATE OR REPLACE FUNCTION public.set_expense_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.expense_number IS NULL THEN
    NEW.expense_number := generate_expense_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_expense_number_trigger
  BEFORE INSERT ON public.expenses
  FOR EACH ROW
  EXECUTE FUNCTION public.set_expense_number();

-- Auto-generate invoice numbers
CREATE SEQUENCE IF NOT EXISTS invoice_number_seq;

CREATE OR REPLACE FUNCTION public.generate_invoice_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'INV' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('invoice_number_seq')::TEXT, 4, '0');
END;
$$;

CREATE OR REPLACE FUNCTION public.set_invoice_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.invoice_number IS NULL THEN
    NEW.invoice_number := generate_invoice_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_invoice_number_trigger
  BEFORE INSERT ON public.invoices
  FOR EACH ROW
  EXECUTE FUNCTION public.set_invoice_number();

-- Updated_at triggers
CREATE TRIGGER update_purchase_orders_updated_at
  BEFORE UPDATE ON public.purchase_orders
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_expenses_updated_at
  BEFORE UPDATE ON public.expenses
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_budgets_updated_at
  BEFORE UPDATE ON public.budgets
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_invoices_updated_at
  BEFORE UPDATE ON public.invoices
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_asset_financials_updated_at
  BEFORE UPDATE ON public.asset_financials
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();