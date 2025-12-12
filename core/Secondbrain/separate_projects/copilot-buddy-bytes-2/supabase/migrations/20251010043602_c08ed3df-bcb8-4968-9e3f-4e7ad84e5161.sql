-- Create customer_accounts table (detailed customer records)
CREATE TABLE public.customer_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  account_number TEXT NOT NULL UNIQUE,
  company_name TEXT NOT NULL,
  account_type TEXT NOT NULL DEFAULT 'standard',
  industry TEXT,
  company_size TEXT,
  website TEXT,
  primary_contact_id UUID,
  billing_address JSONB,
  shipping_address JSONB,
  tax_id TEXT,
  payment_terms TEXT DEFAULT 'net_30',
  credit_limit NUMERIC,
  account_status TEXT NOT NULL DEFAULT 'active',
  parent_account_id UUID,
  account_manager_id UUID,
  support_tier TEXT,
  custom_fields JSONB DEFAULT '{}'::jsonb,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create customer_contacts table
CREATE TABLE public.customer_contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  account_id UUID NOT NULL REFERENCES public.customer_accounts(id) ON DELETE CASCADE,
  contact_type TEXT NOT NULL DEFAULT 'primary',
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT,
  phone TEXT,
  mobile TEXT,
  job_title TEXT,
  department TEXT,
  is_primary BOOLEAN DEFAULT false,
  is_billing_contact BOOLEAN DEFAULT false,
  is_technical_contact BOOLEAN DEFAULT false,
  preferred_contact_method TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create customer_sites table
CREATE TABLE public.customer_sites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  account_id UUID NOT NULL REFERENCES public.customer_accounts(id) ON DELETE CASCADE,
  site_name TEXT NOT NULL,
  site_code TEXT,
  site_type TEXT,
  address_line1 TEXT NOT NULL,
  address_line2 TEXT,
  city TEXT NOT NULL,
  state_province TEXT,
  postal_code TEXT,
  country TEXT NOT NULL DEFAULT 'USA',
  phone TEXT,
  is_primary_site BOOLEAN DEFAULT false,
  site_contact_id UUID,
  operating_hours JSONB,
  special_instructions TEXT,
  coordinates JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create customer_assets table (links customers to CMDB)
CREATE TABLE public.customer_assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  account_id UUID NOT NULL REFERENCES public.customer_accounts(id) ON DELETE CASCADE,
  ci_id UUID REFERENCES public.configuration_items(id) ON DELETE CASCADE,
  site_id UUID REFERENCES public.customer_sites(id),
  asset_status TEXT NOT NULL DEFAULT 'active',
  service_level TEXT,
  warranty_provider TEXT,
  support_contract_id UUID,
  installation_date DATE,
  last_service_date DATE,
  next_service_date DATE,
  monthly_cost NUMERIC,
  annual_cost NUMERIC,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create customer_service_history table
CREATE TABLE public.customer_service_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  account_id UUID NOT NULL REFERENCES public.customer_accounts(id) ON DELETE CASCADE,
  service_type TEXT NOT NULL,
  service_date DATE NOT NULL,
  performed_by UUID,
  site_id UUID REFERENCES public.customer_sites(id),
  related_ticket_id UUID,
  related_change_id UUID,
  description TEXT NOT NULL,
  resolution TEXT,
  time_spent_hours NUMERIC,
  billable BOOLEAN DEFAULT true,
  amount_charged NUMERIC,
  customer_satisfaction INTEGER,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create account number sequence and function
CREATE SEQUENCE account_number_seq;
CREATE OR REPLACE FUNCTION generate_account_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'ACC' || LPAD(nextval('account_number_seq')::TEXT, 6, '0');
END;
$$;

CREATE OR REPLACE FUNCTION set_account_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.account_number IS NULL OR NEW.account_number = '' THEN
    NEW.account_number := generate_account_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_account_number_trigger
BEFORE INSERT ON public.customer_accounts
FOR EACH ROW EXECUTE FUNCTION set_account_number();

-- Add update triggers
CREATE TRIGGER update_customer_accounts_updated_at BEFORE UPDATE ON public.customer_accounts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customer_contacts_updated_at BEFORE UPDATE ON public.customer_contacts
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customer_sites_updated_at BEFORE UPDATE ON public.customer_sites
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customer_assets_updated_at BEFORE UPDATE ON public.customer_assets
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_customer_service_history_updated_at BEFORE UPDATE ON public.customer_service_history
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE public.customer_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_sites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_assets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_service_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies for customer_accounts
CREATE POLICY "Users can view accounts in their organization"
ON public.customer_accounts FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create accounts"
ON public.customer_accounts FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can update accounts in their organization"
ON public.customer_accounts FOR UPDATE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can delete accounts in their organization"
ON public.customer_accounts FOR DELETE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- RLS Policies for customer_contacts
CREATE POLICY "Users can view contacts in their organization"
ON public.customer_contacts FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create contacts"
ON public.customer_contacts FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can update contacts in their organization"
ON public.customer_contacts FOR UPDATE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can delete contacts in their organization"
ON public.customer_contacts FOR DELETE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- RLS Policies for customer_sites
CREATE POLICY "Users can view sites in their organization"
ON public.customer_sites FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create sites"
ON public.customer_sites FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can update sites in their organization"
ON public.customer_sites FOR UPDATE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can delete sites in their organization"
ON public.customer_sites FOR DELETE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- RLS Policies for customer_assets
CREATE POLICY "Users can view customer assets in their organization"
ON public.customer_assets FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create customer assets"
ON public.customer_assets FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can update customer assets in their organization"
ON public.customer_assets FOR UPDATE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can delete customer assets in their organization"
ON public.customer_assets FOR DELETE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- RLS Policies for customer_service_history
CREATE POLICY "Users can view service history in their organization"
ON public.customer_service_history FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create service history"
ON public.customer_service_history FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can update service history in their organization"
ON public.customer_service_history FOR UPDATE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- Create indexes for performance
CREATE INDEX idx_customer_accounts_customer_id ON public.customer_accounts(customer_id);
CREATE INDEX idx_customer_accounts_account_manager ON public.customer_accounts(account_manager_id);
CREATE INDEX idx_customer_contacts_account_id ON public.customer_contacts(account_id);
CREATE INDEX idx_customer_sites_account_id ON public.customer_sites(account_id);
CREATE INDEX idx_customer_assets_account_id ON public.customer_assets(account_id);
CREATE INDEX idx_customer_assets_ci_id ON public.customer_assets(ci_id);
CREATE INDEX idx_customer_service_history_account_id ON public.customer_service_history(account_id);