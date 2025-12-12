-- Phase 6: Self-Healing, Customer Portal, Mobile & Custom Reports

-- ============================================
-- 1. SELF-HEALING & AUTO-REMEDIATION TABLES
-- ============================================

-- Incidents table for tracking issues
CREATE TABLE public.incidents (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  incident_number TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low')),
  status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'investigating', 'remediation_in_progress', 'resolved', 'closed')),
  incident_type TEXT NOT NULL,
  affected_ci_ids UUID[] DEFAULT '{}',
  affected_services TEXT[] DEFAULT '{}',
  detection_method TEXT NOT NULL,
  detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  resolved_at TIMESTAMP WITH TIME ZONE,
  resolution_time_minutes INTEGER,
  auto_remediated BOOLEAN DEFAULT false,
  remediation_applied TEXT,
  root_cause TEXT,
  assigned_to UUID,
  created_by UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Auto-remediation rules
CREATE TABLE public.remediation_rules (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  rule_name TEXT NOT NULL,
  description TEXT,
  incident_pattern JSONB NOT NULL,
  conditions JSONB NOT NULL,
  remediation_actions JSONB NOT NULL,
  auto_execute BOOLEAN DEFAULT false,
  requires_approval BOOLEAN DEFAULT true,
  approval_threshold TEXT DEFAULT 'medium',
  success_rate NUMERIC,
  execution_count INTEGER DEFAULT 0,
  last_executed_at TIMESTAMP WITH TIME ZONE,
  is_active BOOLEAN DEFAULT true,
  created_by UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Remediation execution log
CREATE TABLE public.remediation_executions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  incident_id UUID NOT NULL REFERENCES public.incidents(id),
  rule_id UUID REFERENCES public.remediation_rules(id),
  execution_type TEXT NOT NULL CHECK (execution_type IN ('automatic', 'manual', 'semi_automatic')),
  actions_taken JSONB NOT NULL,
  success BOOLEAN NOT NULL,
  error_message TEXT,
  execution_duration_ms INTEGER,
  executed_by UUID,
  executed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- ============================================
-- 2. CUSTOMER SELF-SERVICE PORTAL TABLES
-- ============================================

-- Client portal users (different from internal users)
CREATE TABLE public.client_portal_users (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  email TEXT NOT NULL,
  full_name TEXT NOT NULL,
  company_name TEXT NOT NULL,
  phone TEXT,
  portal_role TEXT NOT NULL DEFAULT 'user' CHECK (portal_role IN ('admin', 'user', 'viewer')),
  is_active BOOLEAN DEFAULT true,
  last_login_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(customer_id, email)
);

-- Service catalog
CREATE TABLE public.service_catalog (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  service_name TEXT NOT NULL,
  description TEXT NOT NULL,
  category TEXT NOT NULL,
  icon TEXT DEFAULT 'Package',
  estimated_delivery_days INTEGER,
  requires_approval BOOLEAN DEFAULT false,
  approval_workflow_id UUID,
  request_form_schema JSONB NOT NULL DEFAULT '[]',
  sla_hours INTEGER,
  is_active BOOLEAN DEFAULT true,
  display_order INTEGER DEFAULT 0,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Service requests from clients
CREATE TABLE public.service_requests (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  request_number TEXT NOT NULL UNIQUE,
  service_id UUID NOT NULL REFERENCES public.service_catalog(id),
  requested_by UUID NOT NULL REFERENCES public.client_portal_users(id),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  status TEXT NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted', 'pending_approval', 'approved', 'in_progress', 'completed', 'rejected', 'cancelled')),
  form_data JSONB DEFAULT '{}',
  assigned_to UUID,
  approved_by UUID,
  approved_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE,
  due_date TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Client tickets (different from internal support tickets)
CREATE TABLE public.client_tickets (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  ticket_number TEXT NOT NULL UNIQUE,
  submitted_by UUID NOT NULL REFERENCES public.client_portal_users(id),
  subject TEXT NOT NULL,
  description TEXT NOT NULL,
  priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
  status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'assigned', 'in_progress', 'waiting_on_customer', 'resolved', 'closed')),
  category TEXT NOT NULL,
  assigned_to UUID,
  resolution TEXT,
  resolved_at TIMESTAMP WITH TIME ZONE,
  first_response_at TIMESTAMP WITH TIME ZONE,
  sla_breach BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Ticket comments
CREATE TABLE public.ticket_comments (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  ticket_id UUID NOT NULL REFERENCES public.client_tickets(id) ON DELETE CASCADE,
  author_id UUID NOT NULL,
  author_type TEXT NOT NULL CHECK (author_type IN ('client', 'staff')),
  comment TEXT NOT NULL,
  is_internal BOOLEAN DEFAULT false,
  attachments JSONB DEFAULT '[]',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- ============================================
-- 3. CUSTOM REPORT BUILDER TABLES
-- ============================================

-- Custom report definitions
CREATE TABLE public.custom_reports (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  report_name TEXT NOT NULL,
  description TEXT,
  report_type TEXT NOT NULL CHECK (report_type IN ('table', 'chart', 'dashboard', 'export')),
  data_sources JSONB NOT NULL,
  filters JSONB DEFAULT '{}',
  columns JSONB DEFAULT '[]',
  chart_config JSONB,
  layout JSONB,
  is_scheduled BOOLEAN DEFAULT false,
  schedule_cron TEXT,
  recipients TEXT[] DEFAULT '{}',
  is_public BOOLEAN DEFAULT false,
  is_favorite BOOLEAN DEFAULT false,
  created_by UUID NOT NULL,
  last_run_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Report execution history
CREATE TABLE public.report_executions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  report_id UUID NOT NULL REFERENCES public.custom_reports(id) ON DELETE CASCADE,
  customer_id UUID NOT NULL,
  executed_by UUID,
  execution_type TEXT NOT NULL CHECK (execution_type IN ('manual', 'scheduled', 'api')),
  status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
  result_count INTEGER,
  execution_time_ms INTEGER,
  error_message TEXT,
  output_file_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- ============================================
-- ENABLE RLS
-- ============================================

ALTER TABLE public.incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.remediation_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.remediation_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.client_portal_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.service_catalog ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.service_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.client_tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ticket_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.custom_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.report_executions ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS POLICIES
-- ============================================

-- Incidents policies
CREATE POLICY "Users can view incidents in their organization"
  ON public.incidents FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can create incidents"
  ON public.incidents FOR INSERT
  WITH CHECK (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()) 
    AND created_by = auth.uid());

CREATE POLICY "Users can update incidents in their organization"
  ON public.incidents FOR UPDATE
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Remediation rules policies
CREATE POLICY "Users can view remediation rules"
  ON public.remediation_rules FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Admins can manage remediation rules"
  ON public.remediation_rules FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- Remediation executions policies
CREATE POLICY "Users can view remediation executions"
  ON public.remediation_executions FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "System can insert remediation executions"
  ON public.remediation_executions FOR INSERT
  WITH CHECK (true);

-- Client portal users policies
CREATE POLICY "Portal users can view their own profile"
  ON public.client_portal_users FOR SELECT
  USING (id = auth.uid() OR customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Admins can manage portal users"
  ON public.client_portal_users FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- Service catalog policies
CREATE POLICY "Everyone can view active services"
  ON public.service_catalog FOR SELECT
  USING (is_active = true);

CREATE POLICY "Admins can manage service catalog"
  ON public.service_catalog FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- Service requests policies
CREATE POLICY "Users can view their service requests"
  ON public.service_requests FOR SELECT
  USING (requested_by = auth.uid() OR customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Portal users can create service requests"
  ON public.service_requests FOR INSERT
  WITH CHECK (requested_by = auth.uid());

CREATE POLICY "Staff can update service requests"
  ON public.service_requests FOR UPDATE
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Client tickets policies
CREATE POLICY "Users can view their tickets"
  ON public.client_tickets FOR SELECT
  USING (submitted_by = auth.uid() OR customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Portal users can create tickets"
  ON public.client_tickets FOR INSERT
  WITH CHECK (submitted_by = auth.uid());

CREATE POLICY "Staff can update tickets"
  ON public.client_tickets FOR UPDATE
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Ticket comments policies
CREATE POLICY "Users can view comments on their tickets"
  ON public.ticket_comments FOR SELECT
  USING (
    ticket_id IN (
      SELECT id FROM client_tickets 
      WHERE submitted_by = auth.uid() 
      OR customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
    )
  );

CREATE POLICY "Users can add comments"
  ON public.ticket_comments FOR INSERT
  WITH CHECK (author_id = auth.uid());

-- Custom reports policies
CREATE POLICY "Users can view reports in their organization"
  ON public.custom_reports FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()) 
    OR is_public = true);

CREATE POLICY "Users can create reports"
  ON public.custom_reports FOR INSERT
  WITH CHECK (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()) 
    AND created_by = auth.uid());

CREATE POLICY "Users can update their own reports"
  ON public.custom_reports FOR UPDATE
  USING (created_by = auth.uid() OR has_role(auth.uid(), 'admin'));

CREATE POLICY "Users can delete their own reports"
  ON public.custom_reports FOR DELETE
  USING (created_by = auth.uid() OR has_role(auth.uid(), 'admin'));

-- Report executions policies
CREATE POLICY "Users can view report executions"
  ON public.report_executions FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "System can insert report executions"
  ON public.report_executions FOR INSERT
  WITH CHECK (true);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_incidents_customer_id ON public.incidents(customer_id);
CREATE INDEX idx_incidents_status ON public.incidents(status);
CREATE INDEX idx_incidents_detected_at ON public.incidents(detected_at DESC);
CREATE INDEX idx_remediation_rules_customer_id ON public.remediation_rules(customer_id);
CREATE INDEX idx_remediation_rules_active ON public.remediation_rules(is_active);
CREATE INDEX idx_service_requests_customer_id ON public.service_requests(customer_id);
CREATE INDEX idx_service_requests_status ON public.service_requests(status);
CREATE INDEX idx_client_tickets_customer_id ON public.client_tickets(customer_id);
CREATE INDEX idx_client_tickets_status ON public.client_tickets(status);
CREATE INDEX idx_custom_reports_customer_id ON public.custom_reports(customer_id);

-- ============================================
-- TRIGGERS
-- ============================================

CREATE TRIGGER update_incidents_updated_at
  BEFORE UPDATE ON public.incidents
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_remediation_rules_updated_at
  BEFORE UPDATE ON public.remediation_rules
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_client_portal_users_updated_at
  BEFORE UPDATE ON public.client_portal_users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_requests_updated_at
  BEFORE UPDATE ON public.service_requests
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_client_tickets_updated_at
  BEFORE UPDATE ON public.client_tickets
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_custom_reports_updated_at
  BEFORE UPDATE ON public.custom_reports
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Auto-generate incident numbers
CREATE OR REPLACE FUNCTION generate_incident_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'INC' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0');
END;
$$;

CREATE OR REPLACE FUNCTION set_incident_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.incident_number IS NULL THEN
    NEW.incident_number := generate_incident_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_incident_number_trigger
  BEFORE INSERT ON public.incidents
  FOR EACH ROW EXECUTE FUNCTION set_incident_number();

-- Auto-generate service request numbers
CREATE OR REPLACE FUNCTION generate_service_request_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'SR' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0');
END;
$$;

CREATE OR REPLACE FUNCTION set_service_request_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.request_number IS NULL THEN
    NEW.request_number := generate_service_request_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_service_request_number_trigger
  BEFORE INSERT ON public.service_requests
  FOR EACH ROW EXECUTE FUNCTION set_service_request_number();

-- Auto-generate client ticket numbers
CREATE OR REPLACE FUNCTION generate_client_ticket_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'CT' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(FLOOR(RANDOM() * 10000)::TEXT, 4, '0');
END;
$$;

CREATE OR REPLACE FUNCTION set_client_ticket_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.ticket_number IS NULL THEN
    NEW.ticket_number := generate_client_ticket_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_client_ticket_number_trigger
  BEFORE INSERT ON public.client_tickets
  FOR EACH ROW EXECUTE FUNCTION set_client_ticket_number();