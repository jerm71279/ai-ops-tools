-- Create customer_customizations table to store per-customer branding and settings
CREATE TABLE public.customer_customizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES public.customers(id) ON DELETE CASCADE,
  
  -- Branding
  company_logo_url TEXT,
  primary_color TEXT DEFAULT '#10b981',
  secondary_color TEXT DEFAULT '#3b82f6',
  accent_color TEXT DEFAULT '#8b5cf6',
  
  -- Features
  enabled_integrations JSONB DEFAULT '[]'::jsonb,
  enabled_features JSONB DEFAULT '["dashboard", "integrations", "compliance", "ml_insights"]'::jsonb,
  
  -- Dashboard settings
  default_dashboard TEXT DEFAULT 'executive',
  dashboard_layout JSONB DEFAULT '{}'::jsonb,
  
  -- Custom settings
  custom_settings JSONB DEFAULT '{}'::jsonb,
  
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  
  UNIQUE(customer_id)
);

-- Enable RLS
ALTER TABLE public.customer_customizations ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view their own customer customizations"
ON public.customer_customizations
FOR SELECT
USING (
  customer_id IN (
    SELECT id FROM public.customers WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Users can update their own customer customizations"
ON public.customer_customizations
FOR UPDATE
USING (
  customer_id IN (
    SELECT id FROM public.customers WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Admins can manage all customizations"
ON public.customer_customizations
FOR ALL
USING (has_role(auth.uid(), 'admin'::app_role));

CREATE POLICY "System can insert customizations"
ON public.customer_customizations
FOR INSERT
WITH CHECK (true);

-- Add trigger for updated_at
CREATE TRIGGER update_customer_customizations_updated_at
BEFORE UPDATE ON public.customer_customizations
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();