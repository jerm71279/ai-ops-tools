-- CI Change Audit Log
CREATE TABLE IF NOT EXISTS public.ci_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  ci_id UUID NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,
  changed_by UUID NOT NULL,
  change_type TEXT NOT NULL CHECK (change_type IN ('created', 'updated', 'deleted', 'status_changed', 'relationship_added', 'relationship_removed')),
  field_name TEXT,
  old_value JSONB,
  new_value JSONB,
  change_reason TEXT,
  source TEXT DEFAULT 'manual',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.ci_audit_log ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view audit logs in their organization"
  ON public.ci_audit_log
  FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "System can insert audit logs"
  ON public.ci_audit_log
  FOR INSERT
  WITH CHECK (true);

-- Create index for performance
CREATE INDEX idx_ci_audit_log_ci_id ON public.ci_audit_log(ci_id);
CREATE INDEX idx_ci_audit_log_created_at ON public.ci_audit_log(created_at DESC);

-- CI Health Metrics
CREATE TABLE IF NOT EXISTS public.ci_health_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ci_id UUID NOT NULL REFERENCES configuration_items(id) ON DELETE CASCADE,
  customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
  uptime_percentage NUMERIC(5,2),
  last_scan_date TIMESTAMPTZ,
  failed_scans_count INTEGER DEFAULT 0,
  alert_count INTEGER DEFAULT 0,
  critical_alerts INTEGER DEFAULT 0,
  relationship_health INTEGER,
  compliance_score INTEGER,
  metrics_data JSONB,
  calculated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(ci_id, calculated_at)
);

-- Enable RLS
ALTER TABLE public.ci_health_metrics ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view health metrics in their organization"
  ON public.ci_health_metrics
  FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "System can manage health metrics"
  ON public.ci_health_metrics
  FOR ALL
  USING (true)
  WITH CHECK (true);

-- Create index
CREATE INDEX idx_ci_health_metrics_ci_id ON public.ci_health_metrics(ci_id);
CREATE INDEX idx_ci_health_metrics_calculated_at ON public.ci_health_metrics(calculated_at DESC);

-- Function to log CI changes
CREATE OR REPLACE FUNCTION public.log_ci_change()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  change_type_val TEXT;
  field TEXT;
  old_val JSONB;
  new_val JSONB;
BEGIN
  IF TG_OP = 'INSERT' THEN
    change_type_val := 'created';
    INSERT INTO ci_audit_log (
      customer_id,
      ci_id,
      changed_by,
      change_type,
      new_value,
      source
    ) VALUES (
      NEW.customer_id,
      NEW.id,
      COALESCE(auth.uid(), '00000000-0000-0000-0000-000000000000'::uuid),
      change_type_val,
      to_jsonb(NEW),
      COALESCE(NEW.integration_source, 'manual')
    );
  ELSIF TG_OP = 'UPDATE' THEN
    -- Log status changes specifically
    IF OLD.ci_status IS DISTINCT FROM NEW.ci_status THEN
      INSERT INTO ci_audit_log (
        customer_id,
        ci_id,
        changed_by,
        change_type,
        field_name,
        old_value,
        new_value,
        source
      ) VALUES (
        NEW.customer_id,
        NEW.id,
        COALESCE(auth.uid(), '00000000-0000-0000-0000-000000000000'::uuid),
        'status_changed',
        'ci_status',
        to_jsonb(OLD.ci_status),
        to_jsonb(NEW.ci_status),
        COALESCE(NEW.integration_source, 'manual')
      );
    END IF;
    
    -- Log general update with changed fields
    INSERT INTO ci_audit_log (
      customer_id,
      ci_id,
      changed_by,
      change_type,
      old_value,
      new_value,
      source
    ) VALUES (
      NEW.customer_id,
      NEW.id,
      COALESCE(auth.uid(), '00000000-0000-0000-0000-000000000000'::uuid),
      'updated',
      to_jsonb(OLD),
      to_jsonb(NEW),
      COALESCE(NEW.integration_source, 'manual')
    );
  ELSIF TG_OP = 'DELETE' THEN
    INSERT INTO ci_audit_log (
      customer_id,
      ci_id,
      changed_by,
      change_type,
      old_value,
      source
    ) VALUES (
      OLD.customer_id,
      OLD.id,
      COALESCE(auth.uid(), '00000000-0000-0000-0000-000000000000'::uuid),
      'deleted',
      to_jsonb(OLD),
      COALESCE(OLD.integration_source, 'manual')
    );
  END IF;
  
  RETURN NEW;
END;
$$;

-- Create trigger for CI audit logging
DROP TRIGGER IF EXISTS trigger_log_ci_changes ON configuration_items;
CREATE TRIGGER trigger_log_ci_changes
  AFTER INSERT OR UPDATE OR DELETE ON configuration_items
  FOR EACH ROW
  EXECUTE FUNCTION log_ci_change();

-- Function to log relationship changes
CREATE OR REPLACE FUNCTION public.log_relationship_change()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO ci_audit_log (
      customer_id,
      ci_id,
      changed_by,
      change_type,
      new_value
    ) VALUES (
      NEW.customer_id,
      NEW.source_ci_id,
      COALESCE(auth.uid(), '00000000-0000-0000-0000-000000000000'::uuid),
      'relationship_added',
      jsonb_build_object(
        'target_ci_id', NEW.target_ci_id,
        'relationship_type', NEW.relationship_type,
        'is_critical', NEW.is_critical
      )
    );
  ELSIF TG_OP = 'DELETE' THEN
    INSERT INTO ci_audit_log (
      customer_id,
      ci_id,
      changed_by,
      change_type,
      old_value
    ) VALUES (
      OLD.customer_id,
      OLD.source_ci_id,
      COALESCE(auth.uid(), '00000000-0000-0000-0000-000000000000'::uuid),
      'relationship_removed',
      jsonb_build_object(
        'target_ci_id', OLD.target_ci_id,
        'relationship_type', OLD.relationship_type
      )
    );
  END IF;
  
  RETURN NEW;
END;
$$;

-- Create trigger for relationship audit logging
DROP TRIGGER IF EXISTS trigger_log_relationship_changes ON ci_relationships;
CREATE TRIGGER trigger_log_relationship_changes
  AFTER INSERT OR DELETE ON ci_relationships
  FOR EACH ROW
  EXECUTE FUNCTION log_relationship_change();

-- Function to calculate CI health score
CREATE OR REPLACE FUNCTION public.calculate_ci_health(ci_id_param UUID)
RETURNS INTEGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  base_score INTEGER := 100;
  ci_record RECORD;
  days_since_update INTEGER;
  pending_changes_count INTEGER;
  critical_relationships_count INTEGER;
  health_score INTEGER;
BEGIN
  -- Get CI details
  SELECT * INTO ci_record FROM configuration_items WHERE id = ci_id_param;
  
  IF NOT FOUND THEN
    RETURN NULL;
  END IF;
  
  -- Deduct for inactive status
  IF ci_record.ci_status = 'inactive' THEN
    base_score := base_score - 30;
  ELSIF ci_record.ci_status = 'maintenance' THEN
    base_score := base_score - 10;
  END IF;
  
  -- Deduct for missing warranty
  IF ci_record.warranty_expiry IS NOT NULL AND ci_record.warranty_expiry < CURRENT_DATE THEN
    base_score := base_score - 15;
  END IF;
  
  -- Deduct for EOL
  IF ci_record.eol_date IS NOT NULL AND ci_record.eol_date < CURRENT_DATE THEN
    base_score := base_score - 25;
  END IF;
  
  -- Deduct for stale data (not updated in 90 days)
  days_since_update := EXTRACT(DAY FROM (now() - ci_record.updated_at));
  IF days_since_update > 90 THEN
    base_score := base_score - 20;
  END IF;
  
  -- Deduct for pending changes
  SELECT COUNT(*) INTO pending_changes_count
  FROM change_requests
  WHERE ci_id_param = ANY(affected_ci_ids)
    AND change_status IN ('pending_approval', 'scheduled');
  base_score := base_score - (pending_changes_count * 5);
  
  -- Add for critical relationships (good interconnectedness)
  SELECT COUNT(*) INTO critical_relationships_count
  FROM ci_relationships
  WHERE source_ci_id = ci_id_param AND is_critical = true;
  IF critical_relationships_count > 0 THEN
    base_score := base_score + 10;
  END IF;
  
  -- Ensure score is between 0-100
  health_score := GREATEST(0, LEAST(100, base_score));
  
  RETURN health_score;
END;
$$;