-- Create sales_leads table
CREATE TABLE public.sales_leads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  lead_number TEXT NOT NULL UNIQUE,
  company_name TEXT NOT NULL,
  contact_name TEXT NOT NULL,
  contact_email TEXT,
  contact_phone TEXT,
  lead_source TEXT,
  industry TEXT,
  company_size TEXT,
  estimated_value NUMERIC,
  lead_status TEXT NOT NULL DEFAULT 'new',
  lead_score INTEGER DEFAULT 0,
  assigned_to UUID,
  notes TEXT,
  next_follow_up DATE,
  converted_to_opportunity_id UUID,
  converted_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create sales_opportunities table
CREATE TABLE public.sales_opportunities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  opportunity_number TEXT NOT NULL UNIQUE,
  lead_id UUID REFERENCES public.sales_leads(id),
  opportunity_name TEXT NOT NULL,
  account_name TEXT NOT NULL,
  contact_name TEXT NOT NULL,
  contact_email TEXT,
  opportunity_type TEXT,
  stage TEXT NOT NULL DEFAULT 'qualification',
  probability INTEGER DEFAULT 0,
  amount NUMERIC NOT NULL,
  expected_close_date DATE,
  actual_close_date DATE,
  assigned_to UUID,
  competitors TEXT[],
  key_decision_makers JSONB DEFAULT '[]'::jsonb,
  notes TEXT,
  loss_reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create sales_quotes table
CREATE TABLE public.sales_quotes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  quote_number TEXT NOT NULL UNIQUE,
  opportunity_id UUID REFERENCES public.sales_opportunities(id),
  quote_name TEXT NOT NULL,
  account_name TEXT NOT NULL,
  contact_name TEXT NOT NULL,
  contact_email TEXT,
  quote_date DATE NOT NULL DEFAULT CURRENT_DATE,
  expiry_date DATE,
  line_items JSONB NOT NULL DEFAULT '[]'::jsonb,
  subtotal NUMERIC NOT NULL DEFAULT 0,
  tax_amount NUMERIC DEFAULT 0,
  discount_amount NUMERIC DEFAULT 0,
  total_amount NUMERIC NOT NULL DEFAULT 0,
  quote_status TEXT NOT NULL DEFAULT 'draft',
  terms_conditions TEXT,
  notes TEXT,
  accepted_at TIMESTAMPTZ,
  created_by UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create sales_activities table
CREATE TABLE public.sales_activities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  activity_type TEXT NOT NULL,
  subject TEXT NOT NULL,
  description TEXT,
  related_to_type TEXT,
  related_to_id UUID,
  assigned_to UUID NOT NULL,
  due_date DATE,
  completed_at TIMESTAMPTZ,
  activity_status TEXT NOT NULL DEFAULT 'pending',
  priority TEXT DEFAULT 'medium',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create lead number sequence and function
CREATE SEQUENCE lead_number_seq;
CREATE OR REPLACE FUNCTION generate_lead_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'LEAD' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('lead_number_seq')::TEXT, 4, '0');
END;
$$;

CREATE OR REPLACE FUNCTION set_lead_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.lead_number IS NULL OR NEW.lead_number = '' THEN
    NEW.lead_number := generate_lead_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_lead_number_trigger
BEFORE INSERT ON public.sales_leads
FOR EACH ROW EXECUTE FUNCTION set_lead_number();

-- Create opportunity number sequence and function
CREATE SEQUENCE opportunity_number_seq;
CREATE OR REPLACE FUNCTION generate_opportunity_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'OPP' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('opportunity_number_seq')::TEXT, 4, '0');
END;
$$;

CREATE OR REPLACE FUNCTION set_opportunity_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.opportunity_number IS NULL OR NEW.opportunity_number = '' THEN
    NEW.opportunity_number := generate_opportunity_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_opportunity_number_trigger
BEFORE INSERT ON public.sales_opportunities
FOR EACH ROW EXECUTE FUNCTION set_opportunity_number();

-- Create quote number sequence and function
CREATE SEQUENCE quote_number_seq;
CREATE OR REPLACE FUNCTION generate_quote_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'QTE' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('quote_number_seq')::TEXT, 4, '0');
END;
$$;

CREATE OR REPLACE FUNCTION set_quote_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.quote_number IS NULL OR NEW.quote_number = '' THEN
    NEW.quote_number := generate_quote_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_quote_number_trigger
BEFORE INSERT ON public.sales_quotes
FOR EACH ROW EXECUTE FUNCTION set_quote_number();

-- Add update triggers
CREATE TRIGGER update_sales_leads_updated_at BEFORE UPDATE ON public.sales_leads
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sales_opportunities_updated_at BEFORE UPDATE ON public.sales_opportunities
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sales_quotes_updated_at BEFORE UPDATE ON public.sales_quotes
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sales_activities_updated_at BEFORE UPDATE ON public.sales_activities
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE public.sales_leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sales_opportunities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sales_quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sales_activities ENABLE ROW LEVEL SECURITY;

-- RLS Policies for sales_leads
CREATE POLICY "Users can view leads in their organization"
ON public.sales_leads FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create leads"
ON public.sales_leads FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can update leads in their organization"
ON public.sales_leads FOR UPDATE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- RLS Policies for sales_opportunities
CREATE POLICY "Users can view opportunities in their organization"
ON public.sales_opportunities FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create opportunities"
ON public.sales_opportunities FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can update opportunities in their organization"
ON public.sales_opportunities FOR UPDATE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- RLS Policies for sales_quotes
CREATE POLICY "Users can view quotes in their organization"
ON public.sales_quotes FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create quotes"
ON public.sales_quotes FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
) AND created_by = auth.uid());

CREATE POLICY "Users can update quotes in their organization"
ON public.sales_quotes FOR UPDATE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- RLS Policies for sales_activities
CREATE POLICY "Users can view activities in their organization"
ON public.sales_activities FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create activities"
ON public.sales_activities FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can update activities in their organization"
ON public.sales_activities FOR UPDATE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));