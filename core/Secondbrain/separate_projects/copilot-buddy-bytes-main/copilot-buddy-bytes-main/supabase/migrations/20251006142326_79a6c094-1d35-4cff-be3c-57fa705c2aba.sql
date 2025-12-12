-- CIPP Integration Tables

-- CIPP Tenants table to store Microsoft 365 tenant connections
CREATE TABLE IF NOT EXISTS public.cipp_tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES public.customers(id) ON DELETE CASCADE,
  tenant_id TEXT NOT NULL,
  tenant_name TEXT NOT NULL,
  default_domain_name TEXT NOT NULL,
  display_name TEXT,
  tenant_type TEXT DEFAULT 'managed',
  status TEXT NOT NULL DEFAULT 'active',
  last_sync_at TIMESTAMP WITH TIME ZONE,
  sync_status TEXT DEFAULT 'pending',
  sync_error TEXT,
  cipp_relationship_id TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(customer_id, tenant_id)
);

-- CIPP Security Baselines
CREATE TABLE IF NOT EXISTS public.cipp_security_baselines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES public.customers(id) ON DELETE CASCADE,
  baseline_name TEXT NOT NULL,
  baseline_type TEXT NOT NULL,
  description TEXT,
  settings JSONB NOT NULL DEFAULT '{}'::jsonb,
  is_active BOOLEAN DEFAULT true,
  applied_to_tenants UUID[] DEFAULT ARRAY[]::UUID[],
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- CIPP Policies (Conditional Access, Intune, etc.)
CREATE TABLE IF NOT EXISTS public.cipp_policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES public.customers(id) ON DELETE CASCADE,
  tenant_id UUID REFERENCES public.cipp_tenants(id) ON DELETE CASCADE,
  policy_type TEXT NOT NULL,
  policy_name TEXT NOT NULL,
  policy_id TEXT,
  configuration JSONB NOT NULL DEFAULT '{}'::jsonb,
  status TEXT DEFAULT 'active',
  last_applied_at TIMESTAMP WITH TIME ZONE,
  compliance_tags TEXT[] DEFAULT ARRAY[]::TEXT[],
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- CIPP Tenant Health Monitoring
CREATE TABLE IF NOT EXISTS public.cipp_tenant_health (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES public.cipp_tenants(id) ON DELETE CASCADE,
  health_score INTEGER,
  security_score INTEGER,
  compliance_score INTEGER,
  alerts JSONB DEFAULT '[]'::jsonb,
  recommendations JSONB DEFAULT '[]'::jsonb,
  last_checked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- CIPP Audit Logs
CREATE TABLE IF NOT EXISTS public.cipp_audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES public.customers(id) ON DELETE CASCADE,
  tenant_id UUID REFERENCES public.cipp_tenants(id) ON DELETE CASCADE,
  action_type TEXT NOT NULL,
  action_description TEXT NOT NULL,
  performed_by UUID REFERENCES auth.users(id),
  target_resource TEXT,
  result TEXT,
  details JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.cipp_tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cipp_security_baselines ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cipp_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cipp_tenant_health ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cipp_audit_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for CIPP Tenants
CREATE POLICY "Users can view tenants in their organization"
  ON public.cipp_tenants FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "Admins can manage tenants"
  ON public.cipp_tenants FOR ALL
  USING (has_role(auth.uid(), 'admin'::app_role));

-- RLS Policies for Security Baselines
CREATE POLICY "Users can view baselines in their organization"
  ON public.cipp_security_baselines FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "Admins can manage baselines"
  ON public.cipp_security_baselines FOR ALL
  USING (has_role(auth.uid(), 'admin'::app_role));

-- RLS Policies for Policies
CREATE POLICY "Users can view policies in their organization"
  ON public.cipp_policies FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "Admins can manage policies"
  ON public.cipp_policies FOR ALL
  USING (has_role(auth.uid(), 'admin'::app_role));

-- RLS Policies for Tenant Health
CREATE POLICY "Users can view tenant health"
  ON public.cipp_tenant_health FOR SELECT
  USING (tenant_id IN (
    SELECT id FROM cipp_tenants WHERE customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    )
  ));

CREATE POLICY "System can insert health data"
  ON public.cipp_tenant_health FOR INSERT
  WITH CHECK (true);

-- RLS Policies for Audit Logs
CREATE POLICY "Users can view audit logs in their organization"
  ON public.cipp_audit_logs FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "System can insert audit logs"
  ON public.cipp_audit_logs FOR INSERT
  WITH CHECK (true);

-- Create indexes for performance
CREATE INDEX idx_cipp_tenants_customer_id ON public.cipp_tenants(customer_id);
CREATE INDEX idx_cipp_tenants_tenant_id ON public.cipp_tenants(tenant_id);
CREATE INDEX idx_cipp_policies_tenant_id ON public.cipp_policies(tenant_id);
CREATE INDEX idx_cipp_tenant_health_tenant_id ON public.cipp_tenant_health(tenant_id);
CREATE INDEX idx_cipp_audit_logs_customer_id ON public.cipp_audit_logs(customer_id);
CREATE INDEX idx_cipp_audit_logs_created_at ON public.cipp_audit_logs(created_at DESC);