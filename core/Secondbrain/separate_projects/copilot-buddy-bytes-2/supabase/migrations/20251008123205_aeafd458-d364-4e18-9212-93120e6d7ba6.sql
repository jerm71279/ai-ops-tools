-- Phase 5: Multi-Customer Administration & Tenant Management

-- Create customer details table
CREATE TABLE IF NOT EXISTS public.customer_details (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL UNIQUE,
  company_name TEXT NOT NULL,
  industry TEXT,
  company_size TEXT,
  primary_contact_name TEXT,
  primary_contact_email TEXT,
  primary_contact_phone TEXT,
  billing_email TEXT,
  address_line1 TEXT,
  address_line2 TEXT,
  city TEXT,
  state TEXT,
  postal_code TEXT,
  country TEXT,
  timezone TEXT DEFAULT 'UTC',
  website TEXT,
  logo_url TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  subscription_tier TEXT DEFAULT 'free',
  subscription_start_date DATE,
  subscription_end_date DATE,
  trial_end_date DATE,
  is_trial BOOLEAN DEFAULT false,
  settings JSONB DEFAULT '{}'::jsonb,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create customer usage tracking table
CREATE TABLE IF NOT EXISTS public.customer_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  usage_date DATE NOT NULL,
  metric_type TEXT NOT NULL,
  metric_value NUMERIC NOT NULL DEFAULT 0,
  quota_limit NUMERIC,
  usage_details JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(customer_id, usage_date, metric_type)
);

-- Create customer health scores table
CREATE TABLE IF NOT EXISTS public.customer_health (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  health_score INTEGER NOT NULL,
  engagement_score INTEGER,
  adoption_score INTEGER,
  satisfaction_score INTEGER,
  risk_level TEXT NOT NULL DEFAULT 'low',
  health_factors JSONB DEFAULT '{}'::jsonb,
  recommendations JSONB DEFAULT '[]'::jsonb,
  last_activity_at TIMESTAMPTZ,
  calculated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create customer billing table
CREATE TABLE IF NOT EXISTS public.customer_billing (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  billing_period_start DATE NOT NULL,
  billing_period_end DATE NOT NULL,
  total_amount NUMERIC NOT NULL DEFAULT 0,
  currency TEXT NOT NULL DEFAULT 'USD',
  status TEXT NOT NULL DEFAULT 'pending',
  invoice_number TEXT,
  invoice_url TEXT,
  payment_method TEXT,
  paid_at TIMESTAMPTZ,
  due_date DATE,
  line_items JSONB DEFAULT '[]'::jsonb,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create customer feature flags table
CREATE TABLE IF NOT EXISTS public.customer_features (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  feature_name TEXT NOT NULL,
  is_enabled BOOLEAN NOT NULL DEFAULT false,
  enabled_at TIMESTAMPTZ,
  disabled_at TIMESTAMPTZ,
  settings JSONB DEFAULT '{}'::jsonb,
  created_by UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(customer_id, feature_name)
);

-- Create customer support tickets table
CREATE TABLE IF NOT EXISTS public.support_tickets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  ticket_number TEXT NOT NULL UNIQUE,
  subject TEXT NOT NULL,
  description TEXT NOT NULL,
  priority TEXT NOT NULL DEFAULT 'medium',
  status TEXT NOT NULL DEFAULT 'open',
  category TEXT,
  assigned_to UUID,
  created_by UUID NOT NULL,
  resolved_at TIMESTAMPTZ,
  resolved_by UUID,
  resolution_notes TEXT,
  tags TEXT[],
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create customer notes table
CREATE TABLE IF NOT EXISTS public.customer_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  note_type TEXT NOT NULL DEFAULT 'general',
  subject TEXT,
  content TEXT NOT NULL,
  is_important BOOLEAN DEFAULT false,
  tags TEXT[],
  created_by UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create customer activity log table
CREATE TABLE IF NOT EXISTS public.customer_activity_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  activity_type TEXT NOT NULL,
  activity_description TEXT NOT NULL,
  user_id UUID,
  metadata JSONB DEFAULT '{}'::jsonb,
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create indexes
CREATE INDEX idx_customer_details_customer ON public.customer_details(customer_id);
CREATE INDEX idx_customer_details_status ON public.customer_details(status);
CREATE INDEX idx_customer_usage_customer_date ON public.customer_usage(customer_id, usage_date DESC);
CREATE INDEX idx_customer_health_customer ON public.customer_health(customer_id, calculated_at DESC);
CREATE INDEX idx_customer_billing_customer ON public.customer_billing(customer_id, billing_period_start DESC);
CREATE INDEX idx_customer_features_customer ON public.customer_features(customer_id, feature_name);
CREATE INDEX idx_support_tickets_customer ON public.support_tickets(customer_id, created_at DESC);
CREATE INDEX idx_support_tickets_status ON public.support_tickets(status, priority);
CREATE INDEX idx_customer_notes_customer ON public.customer_notes(customer_id, created_at DESC);
CREATE INDEX idx_customer_activity_customer ON public.customer_activity_log(customer_id, created_at DESC);

-- Enable RLS
ALTER TABLE public.customer_details ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_health ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_billing ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_features ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_activity_log ENABLE ROW LEVEL SECURITY;

-- RLS Policies for customer_details
CREATE POLICY "Users can view their customer details"
  ON public.customer_details FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "Admins can manage all customer details"
  ON public.customer_details FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for customer_usage
CREATE POLICY "Users can view their usage"
  ON public.customer_usage FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "System can insert usage"
  ON public.customer_usage FOR INSERT
  WITH CHECK (true);

-- RLS Policies for customer_health
CREATE POLICY "Users can view their health scores"
  ON public.customer_health FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "System can insert health scores"
  ON public.customer_health FOR INSERT
  WITH CHECK (true);

-- RLS Policies for customer_billing
CREATE POLICY "Admins can view billing"
  ON public.customer_billing FOR SELECT
  USING (
    has_role(auth.uid(), 'admin') OR
    customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    )
  );

CREATE POLICY "Admins can manage billing"
  ON public.customer_billing FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for customer_features
CREATE POLICY "Users can view their features"
  ON public.customer_features FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "Admins can manage features"
  ON public.customer_features FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for support_tickets
CREATE POLICY "Users can view their tickets"
  ON public.support_tickets FOR SELECT
  USING (
    customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    ) OR
    created_by = auth.uid() OR
    has_role(auth.uid(), 'admin')
  );

CREATE POLICY "Users can create tickets"
  ON public.support_tickets FOR INSERT
  WITH CHECK (
    customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    ) AND
    created_by = auth.uid()
  );

CREATE POLICY "Admins can manage all tickets"
  ON public.support_tickets FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for customer_notes
CREATE POLICY "Admins can manage customer notes"
  ON public.customer_notes FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for customer_activity_log
CREATE POLICY "Users can view their activity"
  ON public.customer_activity_log FOR SELECT
  USING (
    customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    ) OR
    has_role(auth.uid(), 'admin')
  );

CREATE POLICY "System can insert activity"
  ON public.customer_activity_log FOR INSERT
  WITH CHECK (true);

-- Create triggers for updated_at
CREATE TRIGGER update_customer_details_updated_at
  BEFORE UPDATE ON public.customer_details
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_customer_billing_updated_at
  BEFORE UPDATE ON public.customer_billing
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_customer_features_updated_at
  BEFORE UPDATE ON public.customer_features
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_support_tickets_updated_at
  BEFORE UPDATE ON public.support_tickets
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_customer_notes_updated_at
  BEFORE UPDATE ON public.customer_notes
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Function to generate ticket numbers
CREATE OR REPLACE FUNCTION generate_ticket_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'TKT' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0');
END;
$$;

-- Trigger to auto-generate ticket numbers
CREATE OR REPLACE FUNCTION set_ticket_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.ticket_number IS NULL THEN
    NEW.ticket_number := generate_ticket_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_support_ticket_number
  BEFORE INSERT ON public.support_tickets
  FOR EACH ROW
  EXECUTE FUNCTION set_ticket_number();