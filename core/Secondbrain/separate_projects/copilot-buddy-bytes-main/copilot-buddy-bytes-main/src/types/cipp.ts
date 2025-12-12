export interface CIPPTenant {
  id: string;
  customer_id: string;
  tenant_id: string;
  tenant_name: string;
  default_domain_name: string;
  display_name?: string;
  tenant_type: string;
  status: string;
  last_sync_at?: string;
  sync_status: string;
  sync_error?: string;
  cipp_relationship_id?: string;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface CIPPSecurityBaseline {
  id: string;
  customer_id: string;
  baseline_name: string;
  baseline_type: string;
  description?: string;
  settings: Record<string, any>;
  is_active: boolean;
  applied_to_tenants: string[];
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface CIPPPolicy {
  id: string;
  customer_id: string;
  tenant_id?: string;
  policy_type: string;
  policy_name: string;
  policy_id?: string;
  configuration: Record<string, any>;
  status: string;
  last_applied_at?: string;
  compliance_tags?: string[];
  created_by?: string;
  created_at: string;
  updated_at: string;
}

export interface CIPPTenantHealth {
  id: string;
  tenant_id: string;
  health_score?: number;
  security_score?: number;
  compliance_score?: number;
  alerts: any[];
  recommendations: any[];
  last_checked_at: string;
  created_at: string;
}

export interface CIPPAuditLog {
  id: string;
  customer_id: string;
  tenant_id?: string;
  action_type: string;
  action_description: string;
  performed_by?: string;
  target_resource?: string;
  result?: string;
  details?: Record<string, any>;
  created_at: string;
}
