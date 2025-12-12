-- ============================================================================
-- CMDB & CHANGE MANAGEMENT SYSTEM FOR OBERACONNECT
-- ============================================================================
-- Configuration Management Database (CMDB) with integrated Change Management
-- Leverages NinjaOne data as foundation, adds relationships, change tracking
-- ============================================================================

-- ============================================================================
-- 1. CONFIGURATION ITEMS (CI) - Core CMDB Table
-- ============================================================================

CREATE TYPE public.ci_type AS ENUM (
  'hardware',
  'software',
  'network_device',
  'server',
  'workstation',
  'mobile_device',
  'application',
  'database',
  'service',
  'virtual_machine',
  'cloud_resource',
  'security_device'
);

CREATE TYPE public.ci_status AS ENUM (
  'active',
  'inactive',
  'maintenance',
  'retired',
  'planned',
  'under_review'
);

CREATE TYPE public.ci_criticality AS ENUM (
  'critical',
  'high',
  'medium',
  'low'
);

CREATE TABLE public.configuration_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  
  -- CI Identification
  ci_name TEXT NOT NULL,
  ci_type public.ci_type NOT NULL,
  ci_subtype TEXT,
  ci_status public.ci_status NOT NULL DEFAULT 'active',
  criticality public.ci_criticality NOT NULL DEFAULT 'medium',
  
  -- Asset Information
  asset_tag TEXT,
  serial_number TEXT,
  manufacturer TEXT,
  model TEXT,
  location TEXT,
  
  -- Ownership & Assignment
  owner_user_id UUID,
  assigned_to UUID,
  department TEXT,
  cost_center TEXT,
  
  -- Technical Details
  ip_address INET,
  mac_address MACADDR,
  hostname TEXT,
  operating_system TEXT,
  version TEXT,
  
  -- External System References
  ninjaone_device_id TEXT,
  azure_resource_id TEXT,
  integration_source TEXT,
  external_id TEXT,
  
  -- Lifecycle Management
  purchase_date DATE,
  warranty_expiry DATE,
  eol_date DATE,
  last_audit_date DATE,
  
  -- Compliance & Security
  compliance_tags TEXT[] DEFAULT '{}',
  security_classification TEXT,
  requires_mfa BOOLEAN DEFAULT false,
  
  -- Metadata
  description TEXT,
  notes TEXT,
  attributes JSONB DEFAULT '{}',
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  created_by UUID NOT NULL,
  updated_by UUID
);

-- Indexes for performance
CREATE INDEX idx_ci_customer ON configuration_items(customer_id);
CREATE INDEX idx_ci_type ON configuration_items(ci_type);
CREATE INDEX idx_ci_status ON configuration_items(ci_status);
CREATE INDEX idx_ci_criticality ON configuration_items(criticality);
CREATE INDEX idx_ci_ninjaone ON configuration_items(ninjaone_device_id) WHERE ninjaone_device_id IS NOT NULL;
CREATE INDEX idx_ci_azure ON configuration_items(azure_resource_id) WHERE azure_resource_id IS NOT NULL;
CREATE INDEX idx_ci_ip ON configuration_items(ip_address) WHERE ip_address IS NOT NULL;

-- Enable RLS
ALTER TABLE public.configuration_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view CIs in their organization"
  ON public.configuration_items FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "Users can create CIs for their organization"
  ON public.configuration_items FOR INSERT
  WITH CHECK (
    customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
    AND created_by = auth.uid()
  );

CREATE POLICY "Users can update CIs in their organization"
  ON public.configuration_items FOR UPDATE
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "Admins can delete CIs"
  ON public.configuration_items FOR DELETE
  USING (has_role(auth.uid(), 'admin'));

-- ============================================================================
-- 2. CI RELATIONSHIPS - Dependency Mapping
-- ============================================================================

CREATE TYPE public.relationship_type AS ENUM (
  'depends_on',
  'uses',
  'hosts',
  'runs_on',
  'connects_to',
  'managed_by',
  'backs_up',
  'monitors',
  'protects',
  'integrates_with'
);

CREATE TABLE public.ci_relationships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  
  -- Relationship Definition
  source_ci_id UUID NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,
  target_ci_id UUID NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,
  relationship_type public.relationship_type NOT NULL,
  
  -- Relationship Details
  description TEXT,
  strength TEXT CHECK (strength IN ('strong', 'medium', 'weak')),
  is_critical BOOLEAN DEFAULT false,
  
  -- Metadata
  discovered_by TEXT, -- 'manual', 'automated', 'ninjaone', 'azure'
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  created_by UUID NOT NULL,
  
  -- Prevent duplicate relationships
  UNIQUE(source_ci_id, target_ci_id, relationship_type)
);

CREATE INDEX idx_rel_source ON ci_relationships(source_ci_id);
CREATE INDEX idx_rel_target ON ci_relationships(target_ci_id);
CREATE INDEX idx_rel_customer ON ci_relationships(customer_id);

ALTER TABLE public.ci_relationships ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view relationships in their organization"
  ON public.ci_relationships FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "Users can manage relationships in their organization"
  ON public.ci_relationships FOR ALL
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

-- ============================================================================
-- 3. CHANGE REQUESTS - Change Management
-- ============================================================================

CREATE TYPE public.change_type AS ENUM (
  'standard',
  'normal',
  'emergency',
  'routine'
);

CREATE TYPE public.change_status AS ENUM (
  'draft',
  'submitted',
  'pending_approval',
  'approved',
  'rejected',
  'scheduled',
  'in_progress',
  'implemented',
  'completed',
  'failed',
  'rolled_back',
  'cancelled'
);

CREATE TYPE public.change_priority AS ENUM (
  'critical',
  'high',
  'medium',
  'low'
);

CREATE TYPE public.change_risk AS ENUM (
  'critical',
  'high',
  'medium',
  'low'
);

CREATE TABLE public.change_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  
  -- Change Identification
  change_number TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  
  -- Change Classification
  change_type public.change_type NOT NULL DEFAULT 'normal',
  change_status public.change_status NOT NULL DEFAULT 'draft',
  priority public.change_priority NOT NULL DEFAULT 'medium',
  risk_level public.change_risk NOT NULL DEFAULT 'medium',
  
  -- Affected CIs
  affected_ci_ids UUID[] DEFAULT '{}',
  primary_ci_id UUID REFERENCES configuration_items(id),
  
  -- Change Details
  justification TEXT NOT NULL,
  implementation_plan TEXT NOT NULL,
  rollback_plan TEXT NOT NULL,
  testing_plan TEXT,
  
  -- Impact Analysis
  estimated_downtime_minutes INTEGER,
  affected_users INTEGER,
  affected_services TEXT[],
  business_impact TEXT,
  technical_impact TEXT,
  
  -- Risk Assessment (ML-powered)
  risk_score NUMERIC(5,2),
  risk_factors JSONB,
  similar_changes_success_rate NUMERIC(5,2),
  ml_recommendation TEXT,
  
  -- Scheduling
  requested_start_time TIMESTAMP WITH TIME ZONE,
  requested_end_time TIMESTAMP WITH TIME ZONE,
  scheduled_start_time TIMESTAMP WITH TIME ZONE,
  scheduled_end_time TIMESTAMP WITH TIME ZONE,
  actual_start_time TIMESTAMP WITH TIME ZONE,
  actual_end_time TIMESTAMP WITH TIME ZONE,
  
  -- Implementation
  implementation_notes TEXT,
  completion_notes TEXT,
  success_criteria TEXT,
  
  -- Compliance & Audit
  compliance_tags TEXT[] DEFAULT '{}',
  requires_emergency_approval BOOLEAN DEFAULT false,
  emergency_justification TEXT,
  audit_trail JSONB DEFAULT '[]',
  
  -- Workflow Integration
  workflow_id UUID,
  automation_enabled BOOLEAN DEFAULT false,
  
  -- Ownership
  requested_by UUID NOT NULL,
  assigned_to UUID,
  implemented_by UUID,
  approved_by UUID[],
  
  -- Timestamps
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  submitted_at TIMESTAMP WITH TIME ZONE,
  approved_at TIMESTAMP WITH TIME ZONE,
  completed_at TIMESTAMP WITH TIME ZONE
);

-- Auto-generate change number
CREATE SEQUENCE change_number_seq START 1000;

CREATE OR REPLACE FUNCTION generate_change_number()
RETURNS TEXT AS $$
BEGIN
  RETURN 'CHG' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('change_number_seq')::TEXT, 4, '0');
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-generate change number
CREATE OR REPLACE FUNCTION set_change_number()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.change_number IS NULL THEN
    NEW.change_number := generate_change_number();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_change_number
  BEFORE INSERT ON change_requests
  FOR EACH ROW
  EXECUTE FUNCTION set_change_number();

-- Indexes
CREATE INDEX idx_cr_customer ON change_requests(customer_id);
CREATE INDEX idx_cr_status ON change_requests(change_status);
CREATE INDEX idx_cr_type ON change_requests(change_type);
CREATE INDEX idx_cr_priority ON change_requests(priority);
CREATE INDEX idx_cr_scheduled ON change_requests(scheduled_start_time) WHERE scheduled_start_time IS NOT NULL;
CREATE INDEX idx_cr_change_number ON change_requests(change_number);

-- RLS Policies
ALTER TABLE public.change_requests ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view change requests in their organization"
  ON public.change_requests FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "Users can create change requests"
  ON public.change_requests FOR INSERT
  WITH CHECK (
    customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
    AND requested_by = auth.uid()
  );

CREATE POLICY "Users can update their change requests"
  ON public.change_requests FOR UPDATE
  USING (
    customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
    AND (requested_by = auth.uid() OR assigned_to = auth.uid() OR has_role(auth.uid(), 'admin'))
  );

-- ============================================================================
-- 4. CHANGE APPROVALS - Approval Workflow
-- ============================================================================

CREATE TYPE public.approval_status AS ENUM (
  'pending',
  'approved',
  'rejected',
  'deferred'
);

CREATE TABLE public.change_approvals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  change_request_id UUID NOT NULL REFERENCES change_requests(id) ON DELETE CASCADE,
  
  -- Approver Info
  approver_id UUID NOT NULL,
  approver_role TEXT,
  approval_level INTEGER NOT NULL, -- 1=technical, 2=management, 3=executive
  
  -- Approval Decision
  approval_status public.approval_status NOT NULL DEFAULT 'pending',
  decision_date TIMESTAMP WITH TIME ZONE,
  comments TEXT,
  conditions TEXT,
  
  -- Request Info
  requested_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  due_date TIMESTAMP WITH TIME ZONE,
  
  -- Metadata
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE INDEX idx_ca_change ON change_approvals(change_request_id);
CREATE INDEX idx_ca_approver ON change_approvals(approver_id);
CREATE INDEX idx_ca_status ON change_approvals(approval_status);

ALTER TABLE public.change_approvals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view approvals for their organization's changes"
  ON public.change_approvals FOR SELECT
  USING (change_request_id IN (
    SELECT id FROM change_requests 
    WHERE customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
  ));

CREATE POLICY "Approvers can update their approvals"
  ON public.change_approvals FOR UPDATE
  USING (approver_id = auth.uid());

-- ============================================================================
-- 5. CHANGE IMPACT ANALYSIS - ML-Powered Impact Assessment
-- ============================================================================

CREATE TABLE public.change_impact_analysis (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  change_request_id UUID NOT NULL REFERENCES change_requests(id) ON DELETE CASCADE,
  customer_id UUID NOT NULL,
  
  -- Impact Scores (0-100)
  business_impact_score INTEGER CHECK (business_impact_score BETWEEN 0 AND 100),
  technical_impact_score INTEGER CHECK (technical_impact_score BETWEEN 0 AND 100),
  security_impact_score INTEGER CHECK (security_impact_score BETWEEN 0 AND 100),
  compliance_impact_score INTEGER CHECK (compliance_impact_score BETWEEN 0 AND 100),
  
  -- Affected Components
  dependent_ci_count INTEGER DEFAULT 0,
  affected_ci_ids UUID[],
  critical_dependencies UUID[],
  
  -- Service Impact
  affected_services TEXT[],
  affected_workflows UUID[],
  estimated_user_impact INTEGER,
  estimated_downtime_minutes INTEGER,
  
  -- Risk Factors
  complexity_score INTEGER CHECK (complexity_score BETWEEN 0 AND 100),
  risk_factors JSONB,
  mitigation_strategies TEXT[],
  
  -- Historical Analysis
  similar_changes_analyzed INTEGER,
  similar_changes_success_rate NUMERIC(5,2),
  historical_incidents INTEGER,
  
  -- ML Predictions
  success_probability NUMERIC(5,2),
  recommended_timing TEXT,
  recommended_approach TEXT,
  ai_confidence_score NUMERIC(5,2),
  
  -- Timestamps
  analyzed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  analysis_version INTEGER DEFAULT 1
);

CREATE INDEX idx_cia_change ON change_impact_analysis(change_request_id);
CREATE INDEX idx_cia_customer ON change_impact_analysis(customer_id);

ALTER TABLE public.change_impact_analysis ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view impact analysis for their organization"
  ON public.change_impact_analysis FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

-- ============================================================================
-- 6. CHANGE SCHEDULES - Change Calendar
-- ============================================================================

CREATE TABLE public.change_schedules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  change_request_id UUID NOT NULL REFERENCES change_requests(id) ON DELETE CASCADE,
  
  -- Schedule Info
  scheduled_date DATE NOT NULL,
  scheduled_start_time TIME NOT NULL,
  scheduled_end_time TIME NOT NULL,
  time_zone TEXT NOT NULL DEFAULT 'UTC',
  
  -- Blackout/Maintenance Windows
  is_blackout_period BOOLEAN DEFAULT false,
  blackout_reason TEXT,
  maintenance_window_id UUID,
  
  -- Notifications
  notification_sent BOOLEAN DEFAULT false,
  notification_recipients UUID[],
  reminder_sent BOOLEAN DEFAULT false,
  
  -- Status
  is_confirmed BOOLEAN DEFAULT false,
  confirmed_by UUID,
  confirmed_at TIMESTAMP WITH TIME ZONE,
  
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

CREATE INDEX idx_cs_customer ON change_schedules(customer_id);
CREATE INDEX idx_cs_date ON change_schedules(scheduled_date);
CREATE INDEX idx_cs_change ON change_schedules(change_request_id);

ALTER TABLE public.change_schedules ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view schedules for their organization"
  ON public.change_schedules FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "Users can manage schedules for their organization"
  ON public.change_schedules FOR ALL
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

-- ============================================================================
-- 7. TRIGGERS FOR TIMESTAMPS
-- ============================================================================

CREATE TRIGGER update_ci_updated_at
  BEFORE UPDATE ON configuration_items
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_cr_updated_at
  BEFORE UPDATE ON change_requests
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active CIs with relationship counts
CREATE VIEW ci_overview AS
SELECT 
  ci.*,
  COUNT(DISTINCT r1.id) as outbound_relationships,
  COUNT(DISTINCT r2.id) as inbound_relationships,
  COUNT(DISTINCT cr.id) as pending_changes
FROM configuration_items ci
LEFT JOIN ci_relationships r1 ON ci.id = r1.source_ci_id
LEFT JOIN ci_relationships r2 ON ci.id = r2.target_ci_id
LEFT JOIN change_requests cr ON ci.id = ANY(cr.affected_ci_ids) 
  AND cr.change_status IN ('pending_approval', 'approved', 'scheduled')
WHERE ci.ci_status = 'active'
GROUP BY ci.id;

-- Change request dashboard view
CREATE VIEW change_request_dashboard AS
SELECT 
  cr.*,
  up.full_name as requested_by_name,
  COUNT(DISTINCT ca.id) as total_approvals,
  COUNT(DISTINCT ca.id) FILTER (WHERE ca.approval_status = 'approved') as approved_count,
  COUNT(DISTINCT ca.id) FILTER (WHERE ca.approval_status = 'pending') as pending_approvals,
  cia.business_impact_score,
  cia.success_probability
FROM change_requests cr
LEFT JOIN user_profiles up ON cr.requested_by = up.user_id
LEFT JOIN change_approvals ca ON cr.id = ca.change_request_id
LEFT JOIN change_impact_analysis cia ON cr.id = cia.change_request_id
GROUP BY cr.id, up.full_name, cia.business_impact_score, cia.success_probability;