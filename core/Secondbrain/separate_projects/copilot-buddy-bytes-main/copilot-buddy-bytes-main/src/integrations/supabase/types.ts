export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "13.0.5"
  }
  public: {
    Tables: {
      ai_interactions: {
        Row: {
          ai_response: string
          compliance_tags: string[] | null
          confidence_score: number | null
          conversation_id: string
          created_at: string
          customer_id: string
          feedback_rating: number | null
          id: string
          insight_generated: boolean | null
          interaction_type: string
          knowledge_sources: Json | null
          metadata: Json | null
          user_id: string
          user_query: string
          was_helpful: boolean | null
        }
        Insert: {
          ai_response: string
          compliance_tags?: string[] | null
          confidence_score?: number | null
          conversation_id: string
          created_at?: string
          customer_id: string
          feedback_rating?: number | null
          id?: string
          insight_generated?: boolean | null
          interaction_type: string
          knowledge_sources?: Json | null
          metadata?: Json | null
          user_id: string
          user_query: string
          was_helpful?: boolean | null
        }
        Update: {
          ai_response?: string
          compliance_tags?: string[] | null
          confidence_score?: number | null
          conversation_id?: string
          created_at?: string
          customer_id?: string
          feedback_rating?: number | null
          id?: string
          insight_generated?: boolean | null
          interaction_type?: string
          knowledge_sources?: Json | null
          metadata?: Json | null
          user_id?: string
          user_query?: string
          was_helpful?: boolean | null
        }
        Relationships: [
          {
            foreignKeyName: "ai_interactions_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      ai_learning_metrics: {
        Row: {
          articles_created: number | null
          avg_confidence_score: number | null
          avg_user_rating: number | null
          created_at: string
          customer_id: string
          id: string
          improvement_rate: number | null
          insights_generated: number | null
          knowledge_base_size: number | null
          metric_date: string
          total_interactions: number | null
          updated_at: string
        }
        Insert: {
          articles_created?: number | null
          avg_confidence_score?: number | null
          avg_user_rating?: number | null
          created_at?: string
          customer_id: string
          id?: string
          improvement_rate?: number | null
          insights_generated?: number | null
          knowledge_base_size?: number | null
          metric_date?: string
          total_interactions?: number | null
          updated_at?: string
        }
        Update: {
          articles_created?: number | null
          avg_confidence_score?: number | null
          avg_user_rating?: number | null
          created_at?: string
          customer_id?: string
          id?: string
          improvement_rate?: number | null
          insights_generated?: number | null
          knowledge_base_size?: number | null
          metric_date?: string
          total_interactions?: number | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "ai_learning_metrics_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      anomaly_detections: {
        Row: {
          affected_user_id: string | null
          anomaly_type: string
          compliance_tags: string[] | null
          confidence_score: number | null
          created_at: string
          customer_id: string
          description: string
          detection_method: string
          id: string
          raw_data: Json | null
          resolved_at: string | null
          severity: string
          status: string
          system_name: string
        }
        Insert: {
          affected_user_id?: string | null
          anomaly_type: string
          compliance_tags?: string[] | null
          confidence_score?: number | null
          created_at?: string
          customer_id: string
          description: string
          detection_method: string
          id?: string
          raw_data?: Json | null
          resolved_at?: string | null
          severity: string
          status?: string
          system_name: string
        }
        Update: {
          affected_user_id?: string | null
          anomaly_type?: string
          compliance_tags?: string[] | null
          confidence_score?: number | null
          created_at?: string
          customer_id?: string
          description?: string
          detection_method?: string
          id?: string
          raw_data?: Json | null
          resolved_at?: string | null
          severity?: string
          status?: string
          system_name?: string
        }
        Relationships: [
          {
            foreignKeyName: "anomaly_detections_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      application_access: {
        Row: {
          application_id: string
          created_at: string
          department: string | null
          id: string
          role_id: string | null
        }
        Insert: {
          application_id: string
          created_at?: string
          department?: string | null
          id?: string
          role_id?: string | null
        }
        Update: {
          application_id?: string
          created_at?: string
          department?: string | null
          id?: string
          role_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "application_access_application_id_fkey"
            columns: ["application_id"]
            isOneToOne: false
            referencedRelation: "applications"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "application_access_role_id_fkey"
            columns: ["role_id"]
            isOneToOne: false
            referencedRelation: "roles"
            referencedColumns: ["id"]
          },
        ]
      }
      applications: {
        Row: {
          app_url: string | null
          auth_type: string
          category: string
          config: Json | null
          created_at: string
          description: string | null
          display_order: number | null
          icon_name: string
          id: string
          is_active: boolean
          name: string
          updated_at: string
        }
        Insert: {
          app_url?: string | null
          auth_type?: string
          category?: string
          config?: Json | null
          created_at?: string
          description?: string | null
          display_order?: number | null
          icon_name?: string
          id?: string
          is_active?: boolean
          name: string
          updated_at?: string
        }
        Update: {
          app_url?: string | null
          auth_type?: string
          category?: string
          config?: Json | null
          created_at?: string
          description?: string | null
          display_order?: number | null
          icon_name?: string
          id?: string
          is_active?: boolean
          name?: string
          updated_at?: string
        }
        Relationships: []
      }
      asset_financials: {
        Row: {
          acquisition_date: string | null
          ci_id: string
          created_at: string
          current_value: number | null
          customer_id: string
          depreciation_method: string | null
          depreciation_rate: number | null
          disposal_date: string | null
          id: string
          insurance_cost: number | null
          lease_end_date: string | null
          lease_monthly_cost: number | null
          lease_start_date: string | null
          maintenance_cost_ytd: number | null
          purchase_price: number | null
          salvage_value: number | null
          total_cost_ownership: number | null
          updated_at: string
          useful_life_years: number | null
        }
        Insert: {
          acquisition_date?: string | null
          ci_id: string
          created_at?: string
          current_value?: number | null
          customer_id: string
          depreciation_method?: string | null
          depreciation_rate?: number | null
          disposal_date?: string | null
          id?: string
          insurance_cost?: number | null
          lease_end_date?: string | null
          lease_monthly_cost?: number | null
          lease_start_date?: string | null
          maintenance_cost_ytd?: number | null
          purchase_price?: number | null
          salvage_value?: number | null
          total_cost_ownership?: number | null
          updated_at?: string
          useful_life_years?: number | null
        }
        Update: {
          acquisition_date?: string | null
          ci_id?: string
          created_at?: string
          current_value?: number | null
          customer_id?: string
          depreciation_method?: string | null
          depreciation_rate?: number | null
          disposal_date?: string | null
          id?: string
          insurance_cost?: number | null
          lease_end_date?: string | null
          lease_monthly_cost?: number | null
          lease_start_date?: string | null
          maintenance_cost_ytd?: number | null
          purchase_price?: number | null
          salvage_value?: number | null
          total_cost_ownership?: number | null
          updated_at?: string
          useful_life_years?: number | null
        }
        Relationships: []
      }
      audit_logs: {
        Row: {
          action_details: Json | null
          action_type: string
          compliance_tags: string[] | null
          created_at: string
          customer_id: string
          id: string
          system_name: string
          timestamp: string
          user_id: string
        }
        Insert: {
          action_details?: Json | null
          action_type: string
          compliance_tags?: string[] | null
          created_at?: string
          customer_id: string
          id?: string
          system_name: string
          timestamp?: string
          user_id: string
        }
        Update: {
          action_details?: Json | null
          action_type?: string
          compliance_tags?: string[] | null
          created_at?: string
          customer_id?: string
          id?: string
          system_name?: string
          timestamp?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "audit_logs_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      behavioral_events: {
        Row: {
          action: string
          compliance_tags: string[] | null
          context: Json | null
          created_at: string
          customer_id: string
          duration_ms: number | null
          event_type: string
          id: string
          success: boolean
          system_name: string
          timestamp: string
          user_id: string
        }
        Insert: {
          action: string
          compliance_tags?: string[] | null
          context?: Json | null
          created_at?: string
          customer_id: string
          duration_ms?: number | null
          event_type: string
          id?: string
          success?: boolean
          system_name: string
          timestamp?: string
          user_id: string
        }
        Update: {
          action?: string
          compliance_tags?: string[] | null
          context?: Json | null
          created_at?: string
          customer_id?: string
          duration_ms?: number | null
          event_type?: string
          id?: string
          success?: boolean
          system_name?: string
          timestamp?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "behavioral_events_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      budget_transactions: {
        Row: {
          amount: number
          budget_id: string
          created_at: string
          customer_id: string
          description: string | null
          id: string
          reference_id: string | null
          reference_type: string | null
          transaction_date: string
          transaction_type: string
        }
        Insert: {
          amount: number
          budget_id: string
          created_at?: string
          customer_id: string
          description?: string | null
          id?: string
          reference_id?: string | null
          reference_type?: string | null
          transaction_date?: string
          transaction_type: string
        }
        Update: {
          amount?: number
          budget_id?: string
          created_at?: string
          customer_id?: string
          description?: string | null
          id?: string
          reference_id?: string | null
          reference_type?: string | null
          transaction_date?: string
          transaction_type?: string
        }
        Relationships: [
          {
            foreignKeyName: "budget_transactions_budget_id_fkey"
            columns: ["budget_id"]
            isOneToOne: false
            referencedRelation: "budgets"
            referencedColumns: ["id"]
          },
        ]
      }
      budgets: {
        Row: {
          alert_threshold: number | null
          allocated_amount: number
          budget_name: string
          budget_type: string
          category: string | null
          committed_amount: number | null
          created_at: string
          customer_id: string
          department: string | null
          fiscal_year: number
          id: string
          notes: string | null
          owner_id: string | null
          period_end: string
          period_start: string
          remaining_amount: number | null
          spent_amount: number | null
          status: string
          updated_at: string
          utilization_percentage: number | null
        }
        Insert: {
          alert_threshold?: number | null
          allocated_amount: number
          budget_name: string
          budget_type: string
          category?: string | null
          committed_amount?: number | null
          created_at?: string
          customer_id: string
          department?: string | null
          fiscal_year: number
          id?: string
          notes?: string | null
          owner_id?: string | null
          period_end: string
          period_start: string
          remaining_amount?: number | null
          spent_amount?: number | null
          status?: string
          updated_at?: string
          utilization_percentage?: number | null
        }
        Update: {
          alert_threshold?: number | null
          allocated_amount?: number
          budget_name?: string
          budget_type?: string
          category?: string | null
          committed_amount?: number | null
          created_at?: string
          customer_id?: string
          department?: string | null
          fiscal_year?: number
          id?: string
          notes?: string | null
          owner_id?: string | null
          period_end?: string
          period_start?: string
          remaining_amount?: number | null
          spent_amount?: number | null
          status?: string
          updated_at?: string
          utilization_percentage?: number | null
        }
        Relationships: []
      }
      case_studies: {
        Row: {
          challenge: string
          company_name: string
          created_at: string
          id: string
          industry: string
          is_featured: boolean
          is_published: boolean
          metrics: Json
          published_date: string | null
          results: Json
          slug: string
          solution: string
          summary: string
          testimonial_author: string | null
          testimonial_quote: string | null
          testimonial_role: string | null
          title: string
          updated_at: string
        }
        Insert: {
          challenge: string
          company_name: string
          created_at?: string
          id?: string
          industry: string
          is_featured?: boolean
          is_published?: boolean
          metrics: Json
          published_date?: string | null
          results: Json
          slug: string
          solution: string
          summary: string
          testimonial_author?: string | null
          testimonial_quote?: string | null
          testimonial_role?: string | null
          title: string
          updated_at?: string
        }
        Update: {
          challenge?: string
          company_name?: string
          created_at?: string
          id?: string
          industry?: string
          is_featured?: boolean
          is_published?: boolean
          metrics?: Json
          published_date?: string | null
          results?: Json
          slug?: string
          solution?: string
          summary?: string
          testimonial_author?: string | null
          testimonial_quote?: string | null
          testimonial_role?: string | null
          title?: string
          updated_at?: string
        }
        Relationships: []
      }
      change_approvals: {
        Row: {
          approval_level: number
          approval_status: Database["public"]["Enums"]["approval_status"]
          approver_id: string
          approver_role: string | null
          change_request_id: string
          comments: string | null
          conditions: string | null
          created_at: string
          decision_date: string | null
          due_date: string | null
          id: string
          requested_at: string
        }
        Insert: {
          approval_level: number
          approval_status?: Database["public"]["Enums"]["approval_status"]
          approver_id: string
          approver_role?: string | null
          change_request_id: string
          comments?: string | null
          conditions?: string | null
          created_at?: string
          decision_date?: string | null
          due_date?: string | null
          id?: string
          requested_at?: string
        }
        Update: {
          approval_level?: number
          approval_status?: Database["public"]["Enums"]["approval_status"]
          approver_id?: string
          approver_role?: string | null
          change_request_id?: string
          comments?: string | null
          conditions?: string | null
          created_at?: string
          decision_date?: string | null
          due_date?: string | null
          id?: string
          requested_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "change_approvals_change_request_id_fkey"
            columns: ["change_request_id"]
            isOneToOne: false
            referencedRelation: "change_request_dashboard"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "change_approvals_change_request_id_fkey"
            columns: ["change_request_id"]
            isOneToOne: false
            referencedRelation: "change_requests"
            referencedColumns: ["id"]
          },
        ]
      }
      change_impact_analysis: {
        Row: {
          affected_ci_ids: string[] | null
          affected_services: string[] | null
          affected_workflows: string[] | null
          ai_confidence_score: number | null
          analysis_version: number | null
          analyzed_at: string
          business_impact_score: number | null
          change_request_id: string
          complexity_score: number | null
          compliance_impact_score: number | null
          critical_dependencies: string[] | null
          customer_id: string
          dependent_ci_count: number | null
          estimated_downtime_minutes: number | null
          estimated_user_impact: number | null
          historical_incidents: number | null
          id: string
          mitigation_strategies: string[] | null
          recommended_approach: string | null
          recommended_timing: string | null
          risk_factors: Json | null
          security_impact_score: number | null
          similar_changes_analyzed: number | null
          similar_changes_success_rate: number | null
          success_probability: number | null
          technical_impact_score: number | null
        }
        Insert: {
          affected_ci_ids?: string[] | null
          affected_services?: string[] | null
          affected_workflows?: string[] | null
          ai_confidence_score?: number | null
          analysis_version?: number | null
          analyzed_at?: string
          business_impact_score?: number | null
          change_request_id: string
          complexity_score?: number | null
          compliance_impact_score?: number | null
          critical_dependencies?: string[] | null
          customer_id: string
          dependent_ci_count?: number | null
          estimated_downtime_minutes?: number | null
          estimated_user_impact?: number | null
          historical_incidents?: number | null
          id?: string
          mitigation_strategies?: string[] | null
          recommended_approach?: string | null
          recommended_timing?: string | null
          risk_factors?: Json | null
          security_impact_score?: number | null
          similar_changes_analyzed?: number | null
          similar_changes_success_rate?: number | null
          success_probability?: number | null
          technical_impact_score?: number | null
        }
        Update: {
          affected_ci_ids?: string[] | null
          affected_services?: string[] | null
          affected_workflows?: string[] | null
          ai_confidence_score?: number | null
          analysis_version?: number | null
          analyzed_at?: string
          business_impact_score?: number | null
          change_request_id?: string
          complexity_score?: number | null
          compliance_impact_score?: number | null
          critical_dependencies?: string[] | null
          customer_id?: string
          dependent_ci_count?: number | null
          estimated_downtime_minutes?: number | null
          estimated_user_impact?: number | null
          historical_incidents?: number | null
          id?: string
          mitigation_strategies?: string[] | null
          recommended_approach?: string | null
          recommended_timing?: string | null
          risk_factors?: Json | null
          security_impact_score?: number | null
          similar_changes_analyzed?: number | null
          similar_changes_success_rate?: number | null
          success_probability?: number | null
          technical_impact_score?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "change_impact_analysis_change_request_id_fkey"
            columns: ["change_request_id"]
            isOneToOne: false
            referencedRelation: "change_request_dashboard"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "change_impact_analysis_change_request_id_fkey"
            columns: ["change_request_id"]
            isOneToOne: false
            referencedRelation: "change_requests"
            referencedColumns: ["id"]
          },
        ]
      }
      change_requests: {
        Row: {
          actual_end_time: string | null
          actual_start_time: string | null
          affected_ci_ids: string[] | null
          affected_services: string[] | null
          affected_users: number | null
          approved_at: string | null
          approved_by: string[] | null
          assigned_to: string | null
          audit_trail: Json | null
          automation_enabled: boolean | null
          business_impact: string | null
          change_number: string
          change_status: Database["public"]["Enums"]["change_status"]
          change_type: Database["public"]["Enums"]["change_type"]
          completed_at: string | null
          completion_notes: string | null
          compliance_tags: string[] | null
          created_at: string
          customer_id: string
          description: string
          emergency_justification: string | null
          estimated_downtime_minutes: number | null
          id: string
          implementation_notes: string | null
          implementation_plan: string
          implemented_by: string | null
          justification: string
          ml_recommendation: string | null
          ninjaone_ticket_id: string | null
          ninjaone_ticket_number: string | null
          ninjaone_ticket_status: string | null
          ninjaone_ticket_synced_at: string | null
          ninjaone_ticket_url: string | null
          primary_ci_id: string | null
          priority: Database["public"]["Enums"]["change_priority"]
          requested_by: string
          requested_end_time: string | null
          requested_start_time: string | null
          requires_emergency_approval: boolean | null
          risk_factors: Json | null
          risk_level: Database["public"]["Enums"]["change_risk"]
          risk_score: number | null
          rollback_plan: string
          scheduled_end_time: string | null
          scheduled_start_time: string | null
          similar_changes_success_rate: number | null
          submitted_at: string | null
          success_criteria: string | null
          technical_impact: string | null
          testing_plan: string | null
          title: string
          updated_at: string
          workflow_id: string | null
        }
        Insert: {
          actual_end_time?: string | null
          actual_start_time?: string | null
          affected_ci_ids?: string[] | null
          affected_services?: string[] | null
          affected_users?: number | null
          approved_at?: string | null
          approved_by?: string[] | null
          assigned_to?: string | null
          audit_trail?: Json | null
          automation_enabled?: boolean | null
          business_impact?: string | null
          change_number: string
          change_status?: Database["public"]["Enums"]["change_status"]
          change_type?: Database["public"]["Enums"]["change_type"]
          completed_at?: string | null
          completion_notes?: string | null
          compliance_tags?: string[] | null
          created_at?: string
          customer_id: string
          description: string
          emergency_justification?: string | null
          estimated_downtime_minutes?: number | null
          id?: string
          implementation_notes?: string | null
          implementation_plan: string
          implemented_by?: string | null
          justification: string
          ml_recommendation?: string | null
          ninjaone_ticket_id?: string | null
          ninjaone_ticket_number?: string | null
          ninjaone_ticket_status?: string | null
          ninjaone_ticket_synced_at?: string | null
          ninjaone_ticket_url?: string | null
          primary_ci_id?: string | null
          priority?: Database["public"]["Enums"]["change_priority"]
          requested_by: string
          requested_end_time?: string | null
          requested_start_time?: string | null
          requires_emergency_approval?: boolean | null
          risk_factors?: Json | null
          risk_level?: Database["public"]["Enums"]["change_risk"]
          risk_score?: number | null
          rollback_plan: string
          scheduled_end_time?: string | null
          scheduled_start_time?: string | null
          similar_changes_success_rate?: number | null
          submitted_at?: string | null
          success_criteria?: string | null
          technical_impact?: string | null
          testing_plan?: string | null
          title: string
          updated_at?: string
          workflow_id?: string | null
        }
        Update: {
          actual_end_time?: string | null
          actual_start_time?: string | null
          affected_ci_ids?: string[] | null
          affected_services?: string[] | null
          affected_users?: number | null
          approved_at?: string | null
          approved_by?: string[] | null
          assigned_to?: string | null
          audit_trail?: Json | null
          automation_enabled?: boolean | null
          business_impact?: string | null
          change_number?: string
          change_status?: Database["public"]["Enums"]["change_status"]
          change_type?: Database["public"]["Enums"]["change_type"]
          completed_at?: string | null
          completion_notes?: string | null
          compliance_tags?: string[] | null
          created_at?: string
          customer_id?: string
          description?: string
          emergency_justification?: string | null
          estimated_downtime_minutes?: number | null
          id?: string
          implementation_notes?: string | null
          implementation_plan?: string
          implemented_by?: string | null
          justification?: string
          ml_recommendation?: string | null
          ninjaone_ticket_id?: string | null
          ninjaone_ticket_number?: string | null
          ninjaone_ticket_status?: string | null
          ninjaone_ticket_synced_at?: string | null
          ninjaone_ticket_url?: string | null
          primary_ci_id?: string | null
          priority?: Database["public"]["Enums"]["change_priority"]
          requested_by?: string
          requested_end_time?: string | null
          requested_start_time?: string | null
          requires_emergency_approval?: boolean | null
          risk_factors?: Json | null
          risk_level?: Database["public"]["Enums"]["change_risk"]
          risk_score?: number | null
          rollback_plan?: string
          scheduled_end_time?: string | null
          scheduled_start_time?: string | null
          similar_changes_success_rate?: number | null
          submitted_at?: string | null
          success_criteria?: string | null
          technical_impact?: string | null
          testing_plan?: string | null
          title?: string
          updated_at?: string
          workflow_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "change_requests_primary_ci_id_fkey"
            columns: ["primary_ci_id"]
            isOneToOne: false
            referencedRelation: "ci_overview"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "change_requests_primary_ci_id_fkey"
            columns: ["primary_ci_id"]
            isOneToOne: false
            referencedRelation: "configuration_items"
            referencedColumns: ["id"]
          },
        ]
      }
      change_schedules: {
        Row: {
          blackout_reason: string | null
          change_request_id: string
          confirmed_at: string | null
          confirmed_by: string | null
          created_at: string
          customer_id: string
          id: string
          is_blackout_period: boolean | null
          is_confirmed: boolean | null
          maintenance_window_id: string | null
          notification_recipients: string[] | null
          notification_sent: boolean | null
          reminder_sent: boolean | null
          scheduled_date: string
          scheduled_end_time: string
          scheduled_start_time: string
          time_zone: string
        }
        Insert: {
          blackout_reason?: string | null
          change_request_id: string
          confirmed_at?: string | null
          confirmed_by?: string | null
          created_at?: string
          customer_id: string
          id?: string
          is_blackout_period?: boolean | null
          is_confirmed?: boolean | null
          maintenance_window_id?: string | null
          notification_recipients?: string[] | null
          notification_sent?: boolean | null
          reminder_sent?: boolean | null
          scheduled_date: string
          scheduled_end_time: string
          scheduled_start_time: string
          time_zone?: string
        }
        Update: {
          blackout_reason?: string | null
          change_request_id?: string
          confirmed_at?: string | null
          confirmed_by?: string | null
          created_at?: string
          customer_id?: string
          id?: string
          is_blackout_period?: boolean | null
          is_confirmed?: boolean | null
          maintenance_window_id?: string | null
          notification_recipients?: string[] | null
          notification_sent?: boolean | null
          reminder_sent?: boolean | null
          scheduled_date?: string
          scheduled_end_time?: string
          scheduled_start_time?: string
          time_zone?: string
        }
        Relationships: [
          {
            foreignKeyName: "change_schedules_change_request_id_fkey"
            columns: ["change_request_id"]
            isOneToOne: false
            referencedRelation: "change_request_dashboard"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "change_schedules_change_request_id_fkey"
            columns: ["change_request_id"]
            isOneToOne: false
            referencedRelation: "change_requests"
            referencedColumns: ["id"]
          },
        ]
      }
      ci_audit_log: {
        Row: {
          change_reason: string | null
          change_type: string
          changed_by: string
          ci_id: string
          created_at: string
          customer_id: string
          field_name: string | null
          id: string
          new_value: Json | null
          old_value: Json | null
          source: string | null
        }
        Insert: {
          change_reason?: string | null
          change_type: string
          changed_by: string
          ci_id: string
          created_at?: string
          customer_id: string
          field_name?: string | null
          id?: string
          new_value?: Json | null
          old_value?: Json | null
          source?: string | null
        }
        Update: {
          change_reason?: string | null
          change_type?: string
          changed_by?: string
          ci_id?: string
          created_at?: string
          customer_id?: string
          field_name?: string | null
          id?: string
          new_value?: Json | null
          old_value?: Json | null
          source?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "ci_audit_log_ci_id_fkey"
            columns: ["ci_id"]
            isOneToOne: false
            referencedRelation: "ci_overview"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ci_audit_log_ci_id_fkey"
            columns: ["ci_id"]
            isOneToOne: false
            referencedRelation: "configuration_items"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ci_audit_log_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      ci_health_metrics: {
        Row: {
          alert_count: number | null
          calculated_at: string
          ci_id: string
          compliance_score: number | null
          critical_alerts: number | null
          customer_id: string
          failed_scans_count: number | null
          health_score: number | null
          id: string
          last_scan_date: string | null
          metrics_data: Json | null
          relationship_health: number | null
          uptime_percentage: number | null
        }
        Insert: {
          alert_count?: number | null
          calculated_at?: string
          ci_id: string
          compliance_score?: number | null
          critical_alerts?: number | null
          customer_id: string
          failed_scans_count?: number | null
          health_score?: number | null
          id?: string
          last_scan_date?: string | null
          metrics_data?: Json | null
          relationship_health?: number | null
          uptime_percentage?: number | null
        }
        Update: {
          alert_count?: number | null
          calculated_at?: string
          ci_id?: string
          compliance_score?: number | null
          critical_alerts?: number | null
          customer_id?: string
          failed_scans_count?: number | null
          health_score?: number | null
          id?: string
          last_scan_date?: string | null
          metrics_data?: Json | null
          relationship_health?: number | null
          uptime_percentage?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "ci_health_metrics_ci_id_fkey"
            columns: ["ci_id"]
            isOneToOne: false
            referencedRelation: "ci_overview"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ci_health_metrics_ci_id_fkey"
            columns: ["ci_id"]
            isOneToOne: false
            referencedRelation: "configuration_items"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ci_health_metrics_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      ci_relationships: {
        Row: {
          created_at: string
          created_by: string
          customer_id: string
          description: string | null
          discovered_by: string | null
          id: string
          is_critical: boolean | null
          relationship_type: Database["public"]["Enums"]["relationship_type"]
          source_ci_id: string
          strength: string | null
          target_ci_id: string
        }
        Insert: {
          created_at?: string
          created_by: string
          customer_id: string
          description?: string | null
          discovered_by?: string | null
          id?: string
          is_critical?: boolean | null
          relationship_type: Database["public"]["Enums"]["relationship_type"]
          source_ci_id: string
          strength?: string | null
          target_ci_id: string
        }
        Update: {
          created_at?: string
          created_by?: string
          customer_id?: string
          description?: string | null
          discovered_by?: string | null
          id?: string
          is_critical?: boolean | null
          relationship_type?: Database["public"]["Enums"]["relationship_type"]
          source_ci_id?: string
          strength?: string | null
          target_ci_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "ci_relationships_source_ci_id_fkey"
            columns: ["source_ci_id"]
            isOneToOne: false
            referencedRelation: "ci_overview"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ci_relationships_source_ci_id_fkey"
            columns: ["source_ci_id"]
            isOneToOne: false
            referencedRelation: "configuration_items"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ci_relationships_target_ci_id_fkey"
            columns: ["target_ci_id"]
            isOneToOne: false
            referencedRelation: "ci_overview"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "ci_relationships_target_ci_id_fkey"
            columns: ["target_ci_id"]
            isOneToOne: false
            referencedRelation: "configuration_items"
            referencedColumns: ["id"]
          },
        ]
      }
      cipp_audit_logs: {
        Row: {
          action_description: string
          action_type: string
          created_at: string
          customer_id: string
          details: Json | null
          id: string
          performed_by: string | null
          result: string | null
          target_resource: string | null
          tenant_id: string | null
        }
        Insert: {
          action_description: string
          action_type: string
          created_at?: string
          customer_id: string
          details?: Json | null
          id?: string
          performed_by?: string | null
          result?: string | null
          target_resource?: string | null
          tenant_id?: string | null
        }
        Update: {
          action_description?: string
          action_type?: string
          created_at?: string
          customer_id?: string
          details?: Json | null
          id?: string
          performed_by?: string | null
          result?: string | null
          target_resource?: string | null
          tenant_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "cipp_audit_logs_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "cipp_audit_logs_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "cipp_tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      cipp_policies: {
        Row: {
          compliance_tags: string[] | null
          configuration: Json
          created_at: string
          created_by: string | null
          customer_id: string
          id: string
          last_applied_at: string | null
          policy_id: string | null
          policy_name: string
          policy_type: string
          status: string | null
          tenant_id: string | null
          updated_at: string
        }
        Insert: {
          compliance_tags?: string[] | null
          configuration?: Json
          created_at?: string
          created_by?: string | null
          customer_id: string
          id?: string
          last_applied_at?: string | null
          policy_id?: string | null
          policy_name: string
          policy_type: string
          status?: string | null
          tenant_id?: string | null
          updated_at?: string
        }
        Update: {
          compliance_tags?: string[] | null
          configuration?: Json
          created_at?: string
          created_by?: string | null
          customer_id?: string
          id?: string
          last_applied_at?: string | null
          policy_id?: string | null
          policy_name?: string
          policy_type?: string
          status?: string | null
          tenant_id?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "cipp_policies_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "cipp_policies_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "cipp_tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      cipp_security_baselines: {
        Row: {
          applied_to_tenants: string[] | null
          baseline_name: string
          baseline_type: string
          created_at: string
          created_by: string | null
          customer_id: string
          description: string | null
          id: string
          is_active: boolean | null
          settings: Json
          updated_at: string
        }
        Insert: {
          applied_to_tenants?: string[] | null
          baseline_name: string
          baseline_type: string
          created_at?: string
          created_by?: string | null
          customer_id: string
          description?: string | null
          id?: string
          is_active?: boolean | null
          settings?: Json
          updated_at?: string
        }
        Update: {
          applied_to_tenants?: string[] | null
          baseline_name?: string
          baseline_type?: string
          created_at?: string
          created_by?: string | null
          customer_id?: string
          description?: string | null
          id?: string
          is_active?: boolean | null
          settings?: Json
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "cipp_security_baselines_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      cipp_tenant_health: {
        Row: {
          alerts: Json | null
          compliance_score: number | null
          created_at: string
          health_score: number | null
          id: string
          last_checked_at: string
          recommendations: Json | null
          security_score: number | null
          tenant_id: string
        }
        Insert: {
          alerts?: Json | null
          compliance_score?: number | null
          created_at?: string
          health_score?: number | null
          id?: string
          last_checked_at?: string
          recommendations?: Json | null
          security_score?: number | null
          tenant_id: string
        }
        Update: {
          alerts?: Json | null
          compliance_score?: number | null
          created_at?: string
          health_score?: number | null
          id?: string
          last_checked_at?: string
          recommendations?: Json | null
          security_score?: number | null
          tenant_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "cipp_tenant_health_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "cipp_tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      cipp_tenants: {
        Row: {
          cipp_relationship_id: string | null
          created_at: string
          customer_id: string
          default_domain_name: string
          display_name: string | null
          id: string
          last_sync_at: string | null
          metadata: Json | null
          status: string
          sync_error: string | null
          sync_status: string | null
          tenant_id: string
          tenant_name: string
          tenant_type: string | null
          updated_at: string
        }
        Insert: {
          cipp_relationship_id?: string | null
          created_at?: string
          customer_id: string
          default_domain_name: string
          display_name?: string | null
          id?: string
          last_sync_at?: string | null
          metadata?: Json | null
          status?: string
          sync_error?: string | null
          sync_status?: string | null
          tenant_id: string
          tenant_name: string
          tenant_type?: string | null
          updated_at?: string
        }
        Update: {
          cipp_relationship_id?: string | null
          created_at?: string
          customer_id?: string
          default_domain_name?: string
          display_name?: string | null
          id?: string
          last_sync_at?: string | null
          metadata?: Json | null
          status?: string
          sync_error?: string | null
          sync_status?: string | null
          tenant_id?: string
          tenant_name?: string
          tenant_type?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "cipp_tenants_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      client_onboarding_tasks: {
        Row: {
          actual_hours: number | null
          assigned_role: string | null
          assigned_to: string | null
          blockers: string | null
          completed_at: string | null
          completed_by: string | null
          compliance_tags: string[] | null
          created_at: string
          description: string | null
          due_date: string | null
          estimated_hours: number | null
          id: string
          notes: string | null
          onboarding_id: string
          required_documents: Json | null
          sequence_order: number
          status: string
          task_category: string
          task_name: string
          template_task_id: string | null
          updated_at: string
          uploaded_documents: Json | null
        }
        Insert: {
          actual_hours?: number | null
          assigned_role?: string | null
          assigned_to?: string | null
          blockers?: string | null
          completed_at?: string | null
          completed_by?: string | null
          compliance_tags?: string[] | null
          created_at?: string
          description?: string | null
          due_date?: string | null
          estimated_hours?: number | null
          id?: string
          notes?: string | null
          onboarding_id: string
          required_documents?: Json | null
          sequence_order?: number
          status?: string
          task_category: string
          task_name: string
          template_task_id?: string | null
          updated_at?: string
          uploaded_documents?: Json | null
        }
        Update: {
          actual_hours?: number | null
          assigned_role?: string | null
          assigned_to?: string | null
          blockers?: string | null
          completed_at?: string | null
          completed_by?: string | null
          compliance_tags?: string[] | null
          created_at?: string
          description?: string | null
          due_date?: string | null
          estimated_hours?: number | null
          id?: string
          notes?: string | null
          onboarding_id?: string
          required_documents?: Json | null
          sequence_order?: number
          status?: string
          task_category?: string
          task_name?: string
          template_task_id?: string | null
          updated_at?: string
          uploaded_documents?: Json | null
        }
        Relationships: [
          {
            foreignKeyName: "client_onboarding_tasks_onboarding_id_fkey"
            columns: ["onboarding_id"]
            isOneToOne: false
            referencedRelation: "client_onboardings"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "client_onboarding_tasks_template_task_id_fkey"
            columns: ["template_task_id"]
            isOneToOne: false
            referencedRelation: "onboarding_template_tasks"
            referencedColumns: ["id"]
          },
        ]
      }
      client_onboardings: {
        Row: {
          actual_completion_date: string | null
          client_contact_email: string
          client_contact_name: string | null
          client_name: string
          completion_percentage: number | null
          created_at: string
          created_by: string
          customer_id: string
          id: string
          metadata: Json | null
          notes: string | null
          start_date: string | null
          status: string
          target_completion_date: string | null
          template_id: string
          updated_at: string
        }
        Insert: {
          actual_completion_date?: string | null
          client_contact_email: string
          client_contact_name?: string | null
          client_name: string
          completion_percentage?: number | null
          created_at?: string
          created_by: string
          customer_id: string
          id?: string
          metadata?: Json | null
          notes?: string | null
          start_date?: string | null
          status?: string
          target_completion_date?: string | null
          template_id: string
          updated_at?: string
        }
        Update: {
          actual_completion_date?: string | null
          client_contact_email?: string
          client_contact_name?: string | null
          client_name?: string
          completion_percentage?: number | null
          created_at?: string
          created_by?: string
          customer_id?: string
          id?: string
          metadata?: Json | null
          notes?: string | null
          start_date?: string | null
          status?: string
          target_completion_date?: string | null
          template_id?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "client_onboardings_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "client_onboardings_template_id_fkey"
            columns: ["template_id"]
            isOneToOne: false
            referencedRelation: "onboarding_templates"
            referencedColumns: ["id"]
          },
        ]
      }
      client_portal_users: {
        Row: {
          company_name: string
          created_at: string
          customer_id: string
          email: string
          full_name: string
          id: string
          is_active: boolean | null
          last_login_at: string | null
          phone: string | null
          portal_role: string
          updated_at: string
        }
        Insert: {
          company_name: string
          created_at?: string
          customer_id: string
          email: string
          full_name: string
          id?: string
          is_active?: boolean | null
          last_login_at?: string | null
          phone?: string | null
          portal_role?: string
          updated_at?: string
        }
        Update: {
          company_name?: string
          created_at?: string
          customer_id?: string
          email?: string
          full_name?: string
          id?: string
          is_active?: boolean | null
          last_login_at?: string | null
          phone?: string | null
          portal_role?: string
          updated_at?: string
        }
        Relationships: []
      }
      client_tickets: {
        Row: {
          assigned_to: string | null
          category: string
          created_at: string
          customer_id: string
          description: string
          first_response_at: string | null
          id: string
          priority: string
          resolution: string | null
          resolved_at: string | null
          sla_breach: boolean | null
          status: string
          subject: string
          submitted_by: string
          ticket_number: string
          updated_at: string
        }
        Insert: {
          assigned_to?: string | null
          category: string
          created_at?: string
          customer_id: string
          description: string
          first_response_at?: string | null
          id?: string
          priority?: string
          resolution?: string | null
          resolved_at?: string | null
          sla_breach?: boolean | null
          status?: string
          subject: string
          submitted_by: string
          ticket_number: string
          updated_at?: string
        }
        Update: {
          assigned_to?: string | null
          category?: string
          created_at?: string
          customer_id?: string
          description?: string
          first_response_at?: string | null
          id?: string
          priority?: string
          resolution?: string | null
          resolved_at?: string | null
          sla_breach?: boolean | null
          status?: string
          subject?: string
          submitted_by?: string
          ticket_number?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "client_tickets_submitted_by_fkey"
            columns: ["submitted_by"]
            isOneToOne: false
            referencedRelation: "client_portal_users"
            referencedColumns: ["id"]
          },
        ]
      }
      compliance_controls: {
        Row: {
          automation_level: string
          category: string
          control_id: string
          control_name: string
          created_at: string
          description: string | null
          framework_id: string
          id: string
          required_evidence: string[] | null
        }
        Insert: {
          automation_level?: string
          category: string
          control_id: string
          control_name: string
          created_at?: string
          description?: string | null
          framework_id: string
          id?: string
          required_evidence?: string[] | null
        }
        Update: {
          automation_level?: string
          category?: string
          control_id?: string
          control_name?: string
          created_at?: string
          description?: string | null
          framework_id?: string
          id?: string
          required_evidence?: string[] | null
        }
        Relationships: [
          {
            foreignKeyName: "compliance_controls_framework_id_fkey"
            columns: ["framework_id"]
            isOneToOne: false
            referencedRelation: "compliance_frameworks"
            referencedColumns: ["id"]
          },
        ]
      }
      compliance_frameworks: {
        Row: {
          created_at: string
          description: string | null
          framework_code: string
          framework_name: string
          id: string
          industry: string
          is_active: boolean
          updated_at: string
          version: string | null
        }
        Insert: {
          created_at?: string
          description?: string | null
          framework_code: string
          framework_name: string
          id?: string
          industry: string
          is_active?: boolean
          updated_at?: string
          version?: string | null
        }
        Update: {
          created_at?: string
          description?: string | null
          framework_code?: string
          framework_name?: string
          id?: string
          industry?: string
          is_active?: boolean
          updated_at?: string
          version?: string | null
        }
        Relationships: []
      }
      compliance_reports: {
        Row: {
          created_at: string
          customer_id: string
          evidence_count: number | null
          findings: Json | null
          framework: string
          generated_at: string
          generated_by: string
          id: string
          report_name: string
          report_period_end: string
          report_period_start: string
          status: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          customer_id: string
          evidence_count?: number | null
          findings?: Json | null
          framework: string
          generated_at?: string
          generated_by: string
          id?: string
          report_name: string
          report_period_end: string
          report_period_start: string
          status?: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          customer_id?: string
          evidence_count?: number | null
          findings?: Json | null
          framework?: string
          generated_at?: string
          generated_by?: string
          id?: string
          report_name?: string
          report_period_end?: string
          report_period_start?: string
          status?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "compliance_reports_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      compliance_tags: {
        Row: {
          applicable_frameworks: string[] | null
          created_at: string
          description: string | null
          id: string
          tag_name: string
          tag_type: string
        }
        Insert: {
          applicable_frameworks?: string[] | null
          created_at?: string
          description?: string | null
          id?: string
          tag_name: string
          tag_type: string
        }
        Update: {
          applicable_frameworks?: string[] | null
          created_at?: string
          description?: string | null
          id?: string
          tag_name?: string
          tag_type?: string
        }
        Relationships: []
      }
      configuration_items: {
        Row: {
          asset_tag: string | null
          assigned_to: string | null
          attributes: Json | null
          azure_resource_id: string | null
          ci_name: string
          ci_status: Database["public"]["Enums"]["ci_status"]
          ci_subtype: string | null
          ci_type: Database["public"]["Enums"]["ci_type"]
          compliance_tags: string[] | null
          cost_center: string | null
          created_at: string
          created_by: string
          criticality: Database["public"]["Enums"]["ci_criticality"]
          customer_id: string
          department: string | null
          description: string | null
          eol_date: string | null
          external_id: string | null
          hostname: string | null
          id: string
          integration_source: string | null
          ip_address: unknown | null
          last_audit_date: string | null
          location: string | null
          mac_address: unknown | null
          manufacturer: string | null
          model: string | null
          ninjaone_device_id: string | null
          notes: string | null
          operating_system: string | null
          owner_user_id: string | null
          purchase_date: string | null
          requires_mfa: boolean | null
          security_classification: string | null
          serial_number: string | null
          updated_at: string
          updated_by: string | null
          version: string | null
          warranty_expiry: string | null
        }
        Insert: {
          asset_tag?: string | null
          assigned_to?: string | null
          attributes?: Json | null
          azure_resource_id?: string | null
          ci_name: string
          ci_status?: Database["public"]["Enums"]["ci_status"]
          ci_subtype?: string | null
          ci_type: Database["public"]["Enums"]["ci_type"]
          compliance_tags?: string[] | null
          cost_center?: string | null
          created_at?: string
          created_by: string
          criticality?: Database["public"]["Enums"]["ci_criticality"]
          customer_id: string
          department?: string | null
          description?: string | null
          eol_date?: string | null
          external_id?: string | null
          hostname?: string | null
          id?: string
          integration_source?: string | null
          ip_address?: unknown | null
          last_audit_date?: string | null
          location?: string | null
          mac_address?: unknown | null
          manufacturer?: string | null
          model?: string | null
          ninjaone_device_id?: string | null
          notes?: string | null
          operating_system?: string | null
          owner_user_id?: string | null
          purchase_date?: string | null
          requires_mfa?: boolean | null
          security_classification?: string | null
          serial_number?: string | null
          updated_at?: string
          updated_by?: string | null
          version?: string | null
          warranty_expiry?: string | null
        }
        Update: {
          asset_tag?: string | null
          assigned_to?: string | null
          attributes?: Json | null
          azure_resource_id?: string | null
          ci_name?: string
          ci_status?: Database["public"]["Enums"]["ci_status"]
          ci_subtype?: string | null
          ci_type?: Database["public"]["Enums"]["ci_type"]
          compliance_tags?: string[] | null
          cost_center?: string | null
          created_at?: string
          created_by?: string
          criticality?: Database["public"]["Enums"]["ci_criticality"]
          customer_id?: string
          department?: string | null
          description?: string | null
          eol_date?: string | null
          external_id?: string | null
          hostname?: string | null
          id?: string
          integration_source?: string | null
          ip_address?: unknown | null
          last_audit_date?: string | null
          location?: string | null
          mac_address?: unknown | null
          manufacturer?: string | null
          model?: string | null
          ninjaone_device_id?: string | null
          notes?: string | null
          operating_system?: string | null
          owner_user_id?: string | null
          purchase_date?: string | null
          requires_mfa?: boolean | null
          security_classification?: string | null
          serial_number?: string | null
          updated_at?: string
          updated_by?: string | null
          version?: string | null
          warranty_expiry?: string | null
        }
        Relationships: []
      }
      custom_reports: {
        Row: {
          chart_config: Json | null
          columns: Json | null
          created_at: string
          created_by: string
          customer_id: string
          data_sources: Json
          description: string | null
          filters: Json | null
          id: string
          is_favorite: boolean | null
          is_public: boolean | null
          is_scheduled: boolean | null
          last_run_at: string | null
          layout: Json | null
          recipients: string[] | null
          report_name: string
          report_type: string
          schedule_cron: string | null
          updated_at: string
        }
        Insert: {
          chart_config?: Json | null
          columns?: Json | null
          created_at?: string
          created_by: string
          customer_id: string
          data_sources: Json
          description?: string | null
          filters?: Json | null
          id?: string
          is_favorite?: boolean | null
          is_public?: boolean | null
          is_scheduled?: boolean | null
          last_run_at?: string | null
          layout?: Json | null
          recipients?: string[] | null
          report_name: string
          report_type: string
          schedule_cron?: string | null
          updated_at?: string
        }
        Update: {
          chart_config?: Json | null
          columns?: Json | null
          created_at?: string
          created_by?: string
          customer_id?: string
          data_sources?: Json
          description?: string | null
          filters?: Json | null
          id?: string
          is_favorite?: boolean | null
          is_public?: boolean | null
          is_scheduled?: boolean | null
          last_run_at?: string | null
          layout?: Json | null
          recipients?: string[] | null
          report_name?: string
          report_type?: string
          schedule_cron?: string | null
          updated_at?: string
        }
        Relationships: []
      }
      customer_accounts: {
        Row: {
          account_manager_id: string | null
          account_number: string
          account_status: string
          account_type: string
          billing_address: Json | null
          company_name: string
          company_size: string | null
          created_at: string
          credit_limit: number | null
          custom_fields: Json | null
          customer_id: string
          id: string
          industry: string | null
          notes: string | null
          parent_account_id: string | null
          payment_terms: string | null
          primary_contact_id: string | null
          shipping_address: Json | null
          support_tier: string | null
          tax_id: string | null
          updated_at: string
          website: string | null
        }
        Insert: {
          account_manager_id?: string | null
          account_number: string
          account_status?: string
          account_type?: string
          billing_address?: Json | null
          company_name: string
          company_size?: string | null
          created_at?: string
          credit_limit?: number | null
          custom_fields?: Json | null
          customer_id: string
          id?: string
          industry?: string | null
          notes?: string | null
          parent_account_id?: string | null
          payment_terms?: string | null
          primary_contact_id?: string | null
          shipping_address?: Json | null
          support_tier?: string | null
          tax_id?: string | null
          updated_at?: string
          website?: string | null
        }
        Update: {
          account_manager_id?: string | null
          account_number?: string
          account_status?: string
          account_type?: string
          billing_address?: Json | null
          company_name?: string
          company_size?: string | null
          created_at?: string
          credit_limit?: number | null
          custom_fields?: Json | null
          customer_id?: string
          id?: string
          industry?: string | null
          notes?: string | null
          parent_account_id?: string | null
          payment_terms?: string | null
          primary_contact_id?: string | null
          shipping_address?: Json | null
          support_tier?: string | null
          tax_id?: string | null
          updated_at?: string
          website?: string | null
        }
        Relationships: []
      }
      customer_activity_log: {
        Row: {
          activity_description: string
          activity_type: string
          created_at: string
          customer_id: string
          id: string
          ip_address: unknown | null
          metadata: Json | null
          user_agent: string | null
          user_id: string | null
        }
        Insert: {
          activity_description: string
          activity_type: string
          created_at?: string
          customer_id: string
          id?: string
          ip_address?: unknown | null
          metadata?: Json | null
          user_agent?: string | null
          user_id?: string | null
        }
        Update: {
          activity_description?: string
          activity_type?: string
          created_at?: string
          customer_id?: string
          id?: string
          ip_address?: unknown | null
          metadata?: Json | null
          user_agent?: string | null
          user_id?: string | null
        }
        Relationships: []
      }
      customer_assets: {
        Row: {
          account_id: string
          annual_cost: number | null
          asset_status: string
          ci_id: string | null
          created_at: string
          customer_id: string
          id: string
          installation_date: string | null
          last_service_date: string | null
          monthly_cost: number | null
          next_service_date: string | null
          notes: string | null
          service_level: string | null
          site_id: string | null
          support_contract_id: string | null
          updated_at: string
          warranty_provider: string | null
        }
        Insert: {
          account_id: string
          annual_cost?: number | null
          asset_status?: string
          ci_id?: string | null
          created_at?: string
          customer_id: string
          id?: string
          installation_date?: string | null
          last_service_date?: string | null
          monthly_cost?: number | null
          next_service_date?: string | null
          notes?: string | null
          service_level?: string | null
          site_id?: string | null
          support_contract_id?: string | null
          updated_at?: string
          warranty_provider?: string | null
        }
        Update: {
          account_id?: string
          annual_cost?: number | null
          asset_status?: string
          ci_id?: string | null
          created_at?: string
          customer_id?: string
          id?: string
          installation_date?: string | null
          last_service_date?: string | null
          monthly_cost?: number | null
          next_service_date?: string | null
          notes?: string | null
          service_level?: string | null
          site_id?: string | null
          support_contract_id?: string | null
          updated_at?: string
          warranty_provider?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "customer_assets_account_id_fkey"
            columns: ["account_id"]
            isOneToOne: false
            referencedRelation: "customer_accounts"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "customer_assets_ci_id_fkey"
            columns: ["ci_id"]
            isOneToOne: false
            referencedRelation: "ci_overview"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "customer_assets_ci_id_fkey"
            columns: ["ci_id"]
            isOneToOne: false
            referencedRelation: "configuration_items"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "customer_assets_site_id_fkey"
            columns: ["site_id"]
            isOneToOne: false
            referencedRelation: "customer_sites"
            referencedColumns: ["id"]
          },
        ]
      }
      customer_billing: {
        Row: {
          billing_period_end: string
          billing_period_start: string
          created_at: string
          currency: string
          customer_id: string
          due_date: string | null
          id: string
          invoice_number: string | null
          invoice_url: string | null
          line_items: Json | null
          notes: string | null
          paid_at: string | null
          payment_method: string | null
          status: string
          total_amount: number
          updated_at: string
        }
        Insert: {
          billing_period_end: string
          billing_period_start: string
          created_at?: string
          currency?: string
          customer_id: string
          due_date?: string | null
          id?: string
          invoice_number?: string | null
          invoice_url?: string | null
          line_items?: Json | null
          notes?: string | null
          paid_at?: string | null
          payment_method?: string | null
          status?: string
          total_amount?: number
          updated_at?: string
        }
        Update: {
          billing_period_end?: string
          billing_period_start?: string
          created_at?: string
          currency?: string
          customer_id?: string
          due_date?: string | null
          id?: string
          invoice_number?: string | null
          invoice_url?: string | null
          line_items?: Json | null
          notes?: string | null
          paid_at?: string | null
          payment_method?: string | null
          status?: string
          total_amount?: number
          updated_at?: string
        }
        Relationships: []
      }
      customer_contacts: {
        Row: {
          account_id: string
          contact_type: string
          created_at: string
          customer_id: string
          department: string | null
          email: string | null
          first_name: string
          id: string
          is_billing_contact: boolean | null
          is_primary: boolean | null
          is_technical_contact: boolean | null
          job_title: string | null
          last_name: string
          mobile: string | null
          notes: string | null
          phone: string | null
          preferred_contact_method: string | null
          updated_at: string
        }
        Insert: {
          account_id: string
          contact_type?: string
          created_at?: string
          customer_id: string
          department?: string | null
          email?: string | null
          first_name: string
          id?: string
          is_billing_contact?: boolean | null
          is_primary?: boolean | null
          is_technical_contact?: boolean | null
          job_title?: string | null
          last_name: string
          mobile?: string | null
          notes?: string | null
          phone?: string | null
          preferred_contact_method?: string | null
          updated_at?: string
        }
        Update: {
          account_id?: string
          contact_type?: string
          created_at?: string
          customer_id?: string
          department?: string | null
          email?: string | null
          first_name?: string
          id?: string
          is_billing_contact?: boolean | null
          is_primary?: boolean | null
          is_technical_contact?: boolean | null
          job_title?: string | null
          last_name?: string
          mobile?: string | null
          notes?: string | null
          phone?: string | null
          preferred_contact_method?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "customer_contacts_account_id_fkey"
            columns: ["account_id"]
            isOneToOne: false
            referencedRelation: "customer_accounts"
            referencedColumns: ["id"]
          },
        ]
      }
      customer_customizations: {
        Row: {
          accent_color: string | null
          company_logo_url: string | null
          created_at: string
          custom_settings: Json | null
          customer_id: string
          dashboard_layout: Json | null
          default_dashboard: string | null
          enabled_features: Json | null
          enabled_integrations: Json | null
          enabled_modules: Json | null
          enabled_portals: Json | null
          id: string
          primary_color: string | null
          secondary_color: string | null
          updated_at: string
        }
        Insert: {
          accent_color?: string | null
          company_logo_url?: string | null
          created_at?: string
          custom_settings?: Json | null
          customer_id: string
          dashboard_layout?: Json | null
          default_dashboard?: string | null
          enabled_features?: Json | null
          enabled_integrations?: Json | null
          enabled_modules?: Json | null
          enabled_portals?: Json | null
          id?: string
          primary_color?: string | null
          secondary_color?: string | null
          updated_at?: string
        }
        Update: {
          accent_color?: string | null
          company_logo_url?: string | null
          created_at?: string
          custom_settings?: Json | null
          customer_id?: string
          dashboard_layout?: Json | null
          default_dashboard?: string | null
          enabled_features?: Json | null
          enabled_integrations?: Json | null
          enabled_modules?: Json | null
          enabled_portals?: Json | null
          id?: string
          primary_color?: string | null
          secondary_color?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "customer_customizations_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: true
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      customer_details: {
        Row: {
          address_line1: string | null
          address_line2: string | null
          billing_email: string | null
          city: string | null
          company_name: string
          company_size: string | null
          country: string | null
          created_at: string
          customer_id: string
          id: string
          industry: string | null
          is_trial: boolean | null
          logo_url: string | null
          metadata: Json | null
          postal_code: string | null
          primary_contact_email: string | null
          primary_contact_name: string | null
          primary_contact_phone: string | null
          settings: Json | null
          state: string | null
          status: string
          subscription_end_date: string | null
          subscription_start_date: string | null
          subscription_tier: string | null
          timezone: string | null
          trial_end_date: string | null
          updated_at: string
          website: string | null
        }
        Insert: {
          address_line1?: string | null
          address_line2?: string | null
          billing_email?: string | null
          city?: string | null
          company_name: string
          company_size?: string | null
          country?: string | null
          created_at?: string
          customer_id: string
          id?: string
          industry?: string | null
          is_trial?: boolean | null
          logo_url?: string | null
          metadata?: Json | null
          postal_code?: string | null
          primary_contact_email?: string | null
          primary_contact_name?: string | null
          primary_contact_phone?: string | null
          settings?: Json | null
          state?: string | null
          status?: string
          subscription_end_date?: string | null
          subscription_start_date?: string | null
          subscription_tier?: string | null
          timezone?: string | null
          trial_end_date?: string | null
          updated_at?: string
          website?: string | null
        }
        Update: {
          address_line1?: string | null
          address_line2?: string | null
          billing_email?: string | null
          city?: string | null
          company_name?: string
          company_size?: string | null
          country?: string | null
          created_at?: string
          customer_id?: string
          id?: string
          industry?: string | null
          is_trial?: boolean | null
          logo_url?: string | null
          metadata?: Json | null
          postal_code?: string | null
          primary_contact_email?: string | null
          primary_contact_name?: string | null
          primary_contact_phone?: string | null
          settings?: Json | null
          state?: string | null
          status?: string
          subscription_end_date?: string | null
          subscription_start_date?: string | null
          subscription_tier?: string | null
          timezone?: string | null
          trial_end_date?: string | null
          updated_at?: string
          website?: string | null
        }
        Relationships: []
      }
      customer_features: {
        Row: {
          created_at: string
          created_by: string | null
          customer_id: string
          disabled_at: string | null
          enabled_at: string | null
          feature_name: string
          id: string
          is_enabled: boolean
          settings: Json | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          created_by?: string | null
          customer_id: string
          disabled_at?: string | null
          enabled_at?: string | null
          feature_name: string
          id?: string
          is_enabled?: boolean
          settings?: Json | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          created_by?: string | null
          customer_id?: string
          disabled_at?: string | null
          enabled_at?: string | null
          feature_name?: string
          id?: string
          is_enabled?: boolean
          settings?: Json | null
          updated_at?: string
        }
        Relationships: []
      }
      customer_frameworks: {
        Row: {
          created_at: string
          custom_controls: Json | null
          customer_id: string
          enabled_at: string
          framework_id: string
          id: string
        }
        Insert: {
          created_at?: string
          custom_controls?: Json | null
          customer_id: string
          enabled_at?: string
          framework_id: string
          id?: string
        }
        Update: {
          created_at?: string
          custom_controls?: Json | null
          customer_id?: string
          enabled_at?: string
          framework_id?: string
          id?: string
        }
        Relationships: [
          {
            foreignKeyName: "customer_frameworks_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "customer_frameworks_framework_id_fkey"
            columns: ["framework_id"]
            isOneToOne: false
            referencedRelation: "compliance_frameworks"
            referencedColumns: ["id"]
          },
        ]
      }
      customer_health: {
        Row: {
          adoption_score: number | null
          calculated_at: string
          created_at: string
          customer_id: string
          engagement_score: number | null
          health_factors: Json | null
          health_score: number
          id: string
          last_activity_at: string | null
          recommendations: Json | null
          risk_level: string
          satisfaction_score: number | null
        }
        Insert: {
          adoption_score?: number | null
          calculated_at?: string
          created_at?: string
          customer_id: string
          engagement_score?: number | null
          health_factors?: Json | null
          health_score: number
          id?: string
          last_activity_at?: string | null
          recommendations?: Json | null
          risk_level?: string
          satisfaction_score?: number | null
        }
        Update: {
          adoption_score?: number | null
          calculated_at?: string
          created_at?: string
          customer_id?: string
          engagement_score?: number | null
          health_factors?: Json | null
          health_score?: number
          id?: string
          last_activity_at?: string | null
          recommendations?: Json | null
          risk_level?: string
          satisfaction_score?: number | null
        }
        Relationships: []
      }
      customer_notes: {
        Row: {
          content: string
          created_at: string
          created_by: string
          customer_id: string
          id: string
          is_important: boolean | null
          note_type: string
          subject: string | null
          tags: string[] | null
          updated_at: string
        }
        Insert: {
          content: string
          created_at?: string
          created_by: string
          customer_id: string
          id?: string
          is_important?: boolean | null
          note_type?: string
          subject?: string | null
          tags?: string[] | null
          updated_at?: string
        }
        Update: {
          content?: string
          created_at?: string
          created_by?: string
          customer_id?: string
          id?: string
          is_important?: boolean | null
          note_type?: string
          subject?: string | null
          tags?: string[] | null
          updated_at?: string
        }
        Relationships: []
      }
      customer_service_history: {
        Row: {
          account_id: string
          amount_charged: number | null
          billable: boolean | null
          created_at: string
          customer_id: string
          customer_satisfaction: number | null
          description: string
          id: string
          notes: string | null
          performed_by: string | null
          related_change_id: string | null
          related_ticket_id: string | null
          resolution: string | null
          service_date: string
          service_type: string
          site_id: string | null
          time_spent_hours: number | null
          updated_at: string
        }
        Insert: {
          account_id: string
          amount_charged?: number | null
          billable?: boolean | null
          created_at?: string
          customer_id: string
          customer_satisfaction?: number | null
          description: string
          id?: string
          notes?: string | null
          performed_by?: string | null
          related_change_id?: string | null
          related_ticket_id?: string | null
          resolution?: string | null
          service_date: string
          service_type: string
          site_id?: string | null
          time_spent_hours?: number | null
          updated_at?: string
        }
        Update: {
          account_id?: string
          amount_charged?: number | null
          billable?: boolean | null
          created_at?: string
          customer_id?: string
          customer_satisfaction?: number | null
          description?: string
          id?: string
          notes?: string | null
          performed_by?: string | null
          related_change_id?: string | null
          related_ticket_id?: string | null
          resolution?: string | null
          service_date?: string
          service_type?: string
          site_id?: string | null
          time_spent_hours?: number | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "customer_service_history_account_id_fkey"
            columns: ["account_id"]
            isOneToOne: false
            referencedRelation: "customer_accounts"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "customer_service_history_site_id_fkey"
            columns: ["site_id"]
            isOneToOne: false
            referencedRelation: "customer_sites"
            referencedColumns: ["id"]
          },
        ]
      }
      customer_sites: {
        Row: {
          account_id: string
          address_line1: string
          address_line2: string | null
          city: string
          coordinates: Json | null
          country: string
          created_at: string
          customer_id: string
          id: string
          is_primary_site: boolean | null
          operating_hours: Json | null
          phone: string | null
          postal_code: string | null
          site_code: string | null
          site_contact_id: string | null
          site_name: string
          site_type: string | null
          special_instructions: string | null
          state_province: string | null
          updated_at: string
        }
        Insert: {
          account_id: string
          address_line1: string
          address_line2?: string | null
          city: string
          coordinates?: Json | null
          country?: string
          created_at?: string
          customer_id: string
          id?: string
          is_primary_site?: boolean | null
          operating_hours?: Json | null
          phone?: string | null
          postal_code?: string | null
          site_code?: string | null
          site_contact_id?: string | null
          site_name: string
          site_type?: string | null
          special_instructions?: string | null
          state_province?: string | null
          updated_at?: string
        }
        Update: {
          account_id?: string
          address_line1?: string
          address_line2?: string | null
          city?: string
          coordinates?: Json | null
          country?: string
          created_at?: string
          customer_id?: string
          id?: string
          is_primary_site?: boolean | null
          operating_hours?: Json | null
          phone?: string | null
          postal_code?: string | null
          site_code?: string | null
          site_contact_id?: string | null
          site_name?: string
          site_type?: string | null
          special_instructions?: string | null
          state_province?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "customer_sites_account_id_fkey"
            columns: ["account_id"]
            isOneToOne: false
            referencedRelation: "customer_accounts"
            referencedColumns: ["id"]
          },
        ]
      }
      customer_subscriptions: {
        Row: {
          created_at: string
          currency: string | null
          current_price: number | null
          customer_id: string
          end_date: string | null
          id: string
          metadata: Json | null
          notes: string | null
          product_id: string
          renewal_date: string | null
          revio_customer_id: string | null
          revio_subscription_id: string | null
          start_date: string
          status: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          currency?: string | null
          current_price?: number | null
          customer_id: string
          end_date?: string | null
          id?: string
          metadata?: Json | null
          notes?: string | null
          product_id: string
          renewal_date?: string | null
          revio_customer_id?: string | null
          revio_subscription_id?: string | null
          start_date?: string
          status?: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          currency?: string | null
          current_price?: number | null
          customer_id?: string
          end_date?: string | null
          id?: string
          metadata?: Json | null
          notes?: string | null
          product_id?: string
          renewal_date?: string | null
          revio_customer_id?: string | null
          revio_subscription_id?: string | null
          start_date?: string
          status?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "customer_subscriptions_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "customer_subscriptions_product_id_fkey"
            columns: ["product_id"]
            isOneToOne: false
            referencedRelation: "products"
            referencedColumns: ["id"]
          },
        ]
      }
      customer_usage: {
        Row: {
          created_at: string
          customer_id: string
          id: string
          metric_type: string
          metric_value: number
          quota_limit: number | null
          usage_date: string
          usage_details: Json | null
        }
        Insert: {
          created_at?: string
          customer_id: string
          id?: string
          metric_type: string
          metric_value?: number
          quota_limit?: number | null
          usage_date: string
          usage_details?: Json | null
        }
        Update: {
          created_at?: string
          customer_id?: string
          id?: string
          metric_type?: string
          metric_value?: number
          quota_limit?: number | null
          usage_date?: string
          usage_details?: Json | null
        }
        Relationships: []
      }
      customers: {
        Row: {
          company_name: string
          contact_name: string
          created_at: string
          email: string
          id: string
          phone: string | null
          plan_type: string
          status: string
          subscription_end_date: string | null
          subscription_plan_id: string | null
          subscription_start_date: string | null
          subscription_status: string | null
          updated_at: string
          user_id: string | null
        }
        Insert: {
          company_name: string
          contact_name: string
          created_at?: string
          email: string
          id?: string
          phone?: string | null
          plan_type?: string
          status?: string
          subscription_end_date?: string | null
          subscription_plan_id?: string | null
          subscription_start_date?: string | null
          subscription_status?: string | null
          updated_at?: string
          user_id?: string | null
        }
        Update: {
          company_name?: string
          contact_name?: string
          created_at?: string
          email?: string
          id?: string
          phone?: string | null
          plan_type?: string
          status?: string
          subscription_end_date?: string | null
          subscription_plan_id?: string | null
          subscription_start_date?: string | null
          subscription_status?: string | null
          updated_at?: string
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "customers_subscription_plan_id_fkey"
            columns: ["subscription_plan_id"]
            isOneToOne: false
            referencedRelation: "subscription_plans"
            referencedColumns: ["id"]
          },
        ]
      }
      dashboard_widgets: {
        Row: {
          created_at: string
          customer_id: string
          height: number
          id: string
          is_visible: boolean
          position_x: number
          position_y: number
          updated_at: string
          user_id: string
          widget_config: Json
          widget_type: string
          width: number
        }
        Insert: {
          created_at?: string
          customer_id: string
          height: number
          id?: string
          is_visible?: boolean
          position_x: number
          position_y: number
          updated_at?: string
          user_id: string
          widget_config: Json
          widget_type: string
          width: number
        }
        Update: {
          created_at?: string
          customer_id?: string
          height?: number
          id?: string
          is_visible?: boolean
          position_x?: number
          position_y?: number
          updated_at?: string
          user_id?: string
          widget_config?: Json
          widget_type?: string
          width?: number
        }
        Relationships: [
          {
            foreignKeyName: "dashboard_widgets_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      department_permissions: {
        Row: {
          accessible_features: Json
          accessible_tables: Json
          created_at: string
          dashboard_widgets: Json
          department: string
          display_name: string
          id: string
          updated_at: string
        }
        Insert: {
          accessible_features?: Json
          accessible_tables?: Json
          created_at?: string
          dashboard_widgets?: Json
          department: string
          display_name: string
          id?: string
          updated_at?: string
        }
        Update: {
          accessible_features?: Json
          accessible_tables?: Json
          created_at?: string
          dashboard_widgets?: Json
          department?: string
          display_name?: string
          id?: string
          updated_at?: string
        }
        Relationships: []
      }
      departments: {
        Row: {
          budget_allocation: number | null
          cost_center: string | null
          created_at: string
          customer_id: string
          department_code: string
          department_name: string
          description: string | null
          id: string
          is_active: boolean | null
          location: string | null
          manager_id: string | null
          parent_department_id: string | null
          updated_at: string
        }
        Insert: {
          budget_allocation?: number | null
          cost_center?: string | null
          created_at?: string
          customer_id: string
          department_code: string
          department_name: string
          description?: string | null
          id?: string
          is_active?: boolean | null
          location?: string | null
          manager_id?: string | null
          parent_department_id?: string | null
          updated_at?: string
        }
        Update: {
          budget_allocation?: number | null
          cost_center?: string | null
          created_at?: string
          customer_id?: string
          department_code?: string
          department_name?: string
          description?: string | null
          id?: string
          is_active?: boolean | null
          location?: string | null
          manager_id?: string | null
          parent_department_id?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "departments_parent_department_id_fkey"
            columns: ["parent_department_id"]
            isOneToOne: false
            referencedRelation: "departments"
            referencedColumns: ["id"]
          },
        ]
      }
      device_metrics: {
        Row: {
          additional_data: Json | null
          created_at: string
          customer_id: string
          device_id: string
          id: string
          interface_name: string | null
          metric_name: string
          metric_type: string
          metric_unit: string | null
          metric_value: number | null
          oid: string | null
          polled_at: string
        }
        Insert: {
          additional_data?: Json | null
          created_at?: string
          customer_id: string
          device_id: string
          id?: string
          interface_name?: string | null
          metric_name: string
          metric_type: string
          metric_unit?: string | null
          metric_value?: number | null
          oid?: string | null
          polled_at?: string
        }
        Update: {
          additional_data?: Json | null
          created_at?: string
          customer_id?: string
          device_id?: string
          id?: string
          interface_name?: string | null
          metric_name?: string
          metric_type?: string
          metric_unit?: string | null
          metric_value?: number | null
          oid?: string | null
          polled_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "device_metrics_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "network_devices"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "device_metrics_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "soc_engineer_network_devices"
            referencedColumns: ["id"]
          },
        ]
      }
      employee_certifications: {
        Row: {
          certification_body: string | null
          certification_name: string
          certification_number: string | null
          cost: number | null
          created_at: string
          customer_id: string
          employee_id: string
          expiry_date: string | null
          id: string
          issue_date: string
          notes: string | null
          renewal_required: boolean | null
          updated_at: string
          verification_url: string | null
        }
        Insert: {
          certification_body?: string | null
          certification_name: string
          certification_number?: string | null
          cost?: number | null
          created_at?: string
          customer_id: string
          employee_id: string
          expiry_date?: string | null
          id?: string
          issue_date: string
          notes?: string | null
          renewal_required?: boolean | null
          updated_at?: string
          verification_url?: string | null
        }
        Update: {
          certification_body?: string | null
          certification_name?: string
          certification_number?: string | null
          cost?: number | null
          created_at?: string
          customer_id?: string
          employee_id?: string
          expiry_date?: string | null
          id?: string
          issue_date?: string
          notes?: string | null
          renewal_required?: boolean | null
          updated_at?: string
          verification_url?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "employee_certifications_employee_id_fkey"
            columns: ["employee_id"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
        ]
      }
      employee_leave: {
        Row: {
          approved_at: string | null
          approved_by: string | null
          created_at: string
          customer_id: string
          employee_id: string
          end_date: string
          id: string
          leave_reason: string | null
          leave_status: string
          leave_type_id: string
          notes: string | null
          rejection_reason: string | null
          requested_at: string
          start_date: string
          total_days: number
          updated_at: string
        }
        Insert: {
          approved_at?: string | null
          approved_by?: string | null
          created_at?: string
          customer_id: string
          employee_id: string
          end_date: string
          id?: string
          leave_reason?: string | null
          leave_status?: string
          leave_type_id: string
          notes?: string | null
          rejection_reason?: string | null
          requested_at?: string
          start_date: string
          total_days: number
          updated_at?: string
        }
        Update: {
          approved_at?: string | null
          approved_by?: string | null
          created_at?: string
          customer_id?: string
          employee_id?: string
          end_date?: string
          id?: string
          leave_reason?: string | null
          leave_status?: string
          leave_type_id?: string
          notes?: string | null
          rejection_reason?: string | null
          requested_at?: string
          start_date?: string
          total_days?: number
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "employee_leave_approved_by_fkey"
            columns: ["approved_by"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "employee_leave_employee_id_fkey"
            columns: ["employee_id"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "employee_leave_leave_type_id_fkey"
            columns: ["leave_type_id"]
            isOneToOne: false
            referencedRelation: "leave_types"
            referencedColumns: ["id"]
          },
        ]
      }
      employee_onboarding_tasks: {
        Row: {
          actual_hours: number | null
          assigned_role: string | null
          assigned_to: string | null
          blockers: string | null
          completed_at: string | null
          completed_by: string | null
          compliance_tags: string[] | null
          created_at: string | null
          description: string | null
          due_date: string | null
          estimated_hours: number | null
          id: string
          notes: string | null
          onboarding_id: string
          required_documents: Json | null
          sequence_order: number | null
          status: string
          task_category: string
          task_name: string
          template_task_id: string | null
          updated_at: string | null
          uploaded_documents: Json | null
        }
        Insert: {
          actual_hours?: number | null
          assigned_role?: string | null
          assigned_to?: string | null
          blockers?: string | null
          completed_at?: string | null
          completed_by?: string | null
          compliance_tags?: string[] | null
          created_at?: string | null
          description?: string | null
          due_date?: string | null
          estimated_hours?: number | null
          id?: string
          notes?: string | null
          onboarding_id: string
          required_documents?: Json | null
          sequence_order?: number | null
          status?: string
          task_category: string
          task_name: string
          template_task_id?: string | null
          updated_at?: string | null
          uploaded_documents?: Json | null
        }
        Update: {
          actual_hours?: number | null
          assigned_role?: string | null
          assigned_to?: string | null
          blockers?: string | null
          completed_at?: string | null
          completed_by?: string | null
          compliance_tags?: string[] | null
          created_at?: string | null
          description?: string | null
          due_date?: string | null
          estimated_hours?: number | null
          id?: string
          notes?: string | null
          onboarding_id?: string
          required_documents?: Json | null
          sequence_order?: number | null
          status?: string
          task_category?: string
          task_name?: string
          template_task_id?: string | null
          updated_at?: string | null
          uploaded_documents?: Json | null
        }
        Relationships: [
          {
            foreignKeyName: "employee_onboarding_tasks_onboarding_id_fkey"
            columns: ["onboarding_id"]
            isOneToOne: false
            referencedRelation: "employee_onboardings"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "employee_onboarding_tasks_template_task_id_fkey"
            columns: ["template_task_id"]
            isOneToOne: false
            referencedRelation: "employee_onboarding_template_tasks"
            referencedColumns: ["id"]
          },
        ]
      }
      employee_onboarding_template_tasks: {
        Row: {
          assigned_role: string | null
          compliance_tags: string[] | null
          created_at: string | null
          dependencies: Json | null
          description: string | null
          estimated_hours: number | null
          id: string
          required_documents: Json | null
          requires_employee_input: boolean | null
          sequence_order: number | null
          task_category: string
          task_name: string
          template_id: string
        }
        Insert: {
          assigned_role?: string | null
          compliance_tags?: string[] | null
          created_at?: string | null
          dependencies?: Json | null
          description?: string | null
          estimated_hours?: number | null
          id?: string
          required_documents?: Json | null
          requires_employee_input?: boolean | null
          sequence_order?: number | null
          task_category: string
          task_name: string
          template_id: string
        }
        Update: {
          assigned_role?: string | null
          compliance_tags?: string[] | null
          created_at?: string | null
          dependencies?: Json | null
          description?: string | null
          estimated_hours?: number | null
          id?: string
          required_documents?: Json | null
          requires_employee_input?: boolean | null
          sequence_order?: number | null
          task_category?: string
          task_name?: string
          template_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "employee_onboarding_template_tasks_template_id_fkey"
            columns: ["template_id"]
            isOneToOne: false
            referencedRelation: "employee_onboarding_templates"
            referencedColumns: ["id"]
          },
        ]
      }
      employee_onboarding_templates: {
        Row: {
          created_at: string | null
          created_by: string
          customer_id: string
          department_type: string | null
          description: string | null
          estimated_days: number | null
          id: string
          is_active: boolean | null
          template_name: string
          updated_at: string | null
        }
        Insert: {
          created_at?: string | null
          created_by: string
          customer_id: string
          department_type?: string | null
          description?: string | null
          estimated_days?: number | null
          id?: string
          is_active?: boolean | null
          template_name: string
          updated_at?: string | null
        }
        Update: {
          created_at?: string | null
          created_by?: string
          customer_id?: string
          department_type?: string | null
          description?: string | null
          estimated_days?: number | null
          id?: string
          is_active?: boolean | null
          template_name?: string
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "employee_onboarding_templates_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      employee_onboardings: {
        Row: {
          actual_completion_date: string | null
          address_line1: string | null
          address_line2: string | null
          assigned_role_id: string | null
          city: string | null
          completion_percentage: number | null
          country: string | null
          created_at: string | null
          created_by: string
          customer_id: string
          date_of_birth: string | null
          department: string | null
          emergency_contact_name: string | null
          emergency_contact_phone: string | null
          emergency_contact_relationship: string | null
          employee_email: string
          employee_name: string
          employee_phone: string | null
          employment_type: string | null
          id: string
          job_title: string | null
          manager_id: string | null
          metadata: Json | null
          notes: string | null
          postal_code: string | null
          start_date: string | null
          state: string | null
          status: string
          target_completion_date: string | null
          template_id: string | null
          updated_at: string | null
          work_location: string | null
        }
        Insert: {
          actual_completion_date?: string | null
          address_line1?: string | null
          address_line2?: string | null
          assigned_role_id?: string | null
          city?: string | null
          completion_percentage?: number | null
          country?: string | null
          created_at?: string | null
          created_by: string
          customer_id: string
          date_of_birth?: string | null
          department?: string | null
          emergency_contact_name?: string | null
          emergency_contact_phone?: string | null
          emergency_contact_relationship?: string | null
          employee_email: string
          employee_name: string
          employee_phone?: string | null
          employment_type?: string | null
          id?: string
          job_title?: string | null
          manager_id?: string | null
          metadata?: Json | null
          notes?: string | null
          postal_code?: string | null
          start_date?: string | null
          state?: string | null
          status?: string
          target_completion_date?: string | null
          template_id?: string | null
          updated_at?: string | null
          work_location?: string | null
        }
        Update: {
          actual_completion_date?: string | null
          address_line1?: string | null
          address_line2?: string | null
          assigned_role_id?: string | null
          city?: string | null
          completion_percentage?: number | null
          country?: string | null
          created_at?: string | null
          created_by?: string
          customer_id?: string
          date_of_birth?: string | null
          department?: string | null
          emergency_contact_name?: string | null
          emergency_contact_phone?: string | null
          emergency_contact_relationship?: string | null
          employee_email?: string
          employee_name?: string
          employee_phone?: string | null
          employment_type?: string | null
          id?: string
          job_title?: string | null
          manager_id?: string | null
          metadata?: Json | null
          notes?: string | null
          postal_code?: string | null
          start_date?: string | null
          state?: string | null
          status?: string
          target_completion_date?: string | null
          template_id?: string | null
          updated_at?: string | null
          work_location?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "employee_onboardings_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "employee_onboardings_template_id_fkey"
            columns: ["template_id"]
            isOneToOne: false
            referencedRelation: "employee_onboarding_templates"
            referencedColumns: ["id"]
          },
        ]
      }
      employee_training: {
        Row: {
          certificate_url: string | null
          completion_date: string | null
          course_id: string
          created_at: string
          customer_id: string
          employee_id: string
          enrollment_date: string
          id: string
          instructor: string | null
          notes: string | null
          passed: boolean | null
          scheduled_date: string | null
          score: number | null
          training_status: string
          updated_at: string
        }
        Insert: {
          certificate_url?: string | null
          completion_date?: string | null
          course_id: string
          created_at?: string
          customer_id: string
          employee_id: string
          enrollment_date?: string
          id?: string
          instructor?: string | null
          notes?: string | null
          passed?: boolean | null
          scheduled_date?: string | null
          score?: number | null
          training_status?: string
          updated_at?: string
        }
        Update: {
          certificate_url?: string | null
          completion_date?: string | null
          course_id?: string
          created_at?: string
          customer_id?: string
          employee_id?: string
          enrollment_date?: string
          id?: string
          instructor?: string | null
          notes?: string | null
          passed?: boolean | null
          scheduled_date?: string | null
          score?: number | null
          training_status?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "employee_training_course_id_fkey"
            columns: ["course_id"]
            isOneToOne: false
            referencedRelation: "training_courses"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "employee_training_employee_id_fkey"
            columns: ["employee_id"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
        ]
      }
      employees: {
        Row: {
          created_at: string
          customer_id: string
          department_id: string | null
          email: string
          emergency_contact_name: string | null
          emergency_contact_phone: string | null
          employee_number: string
          employment_status: string
          employment_type: string
          first_name: string
          hire_date: string
          hourly_rate: number | null
          id: string
          job_title: string
          last_name: string
          manager_id: string | null
          notes: string | null
          phone: string | null
          salary: number | null
          termination_date: string | null
          updated_at: string
          user_id: string | null
          work_location: string | null
        }
        Insert: {
          created_at?: string
          customer_id: string
          department_id?: string | null
          email: string
          emergency_contact_name?: string | null
          emergency_contact_phone?: string | null
          employee_number: string
          employment_status?: string
          employment_type?: string
          first_name: string
          hire_date: string
          hourly_rate?: number | null
          id?: string
          job_title: string
          last_name: string
          manager_id?: string | null
          notes?: string | null
          phone?: string | null
          salary?: number | null
          termination_date?: string | null
          updated_at?: string
          user_id?: string | null
          work_location?: string | null
        }
        Update: {
          created_at?: string
          customer_id?: string
          department_id?: string | null
          email?: string
          emergency_contact_name?: string | null
          emergency_contact_phone?: string | null
          employee_number?: string
          employment_status?: string
          employment_type?: string
          first_name?: string
          hire_date?: string
          hourly_rate?: number | null
          id?: string
          job_title?: string
          last_name?: string
          manager_id?: string | null
          notes?: string | null
          phone?: string | null
          salary?: number | null
          termination_date?: string | null
          updated_at?: string
          user_id?: string | null
          work_location?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "employees_department_id_fkey"
            columns: ["department_id"]
            isOneToOne: false
            referencedRelation: "departments"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "employees_manager_id_fkey"
            columns: ["manager_id"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
        ]
      }
      evidence_files: {
        Row: {
          compliance_tags: string[] | null
          control_id: string | null
          created_at: string
          customer_id: string
          description: string | null
          file_name: string
          file_size: number
          file_type: string
          framework_id: string | null
          id: string
          incident_id: string | null
          storage_path: string
          uploaded_at: string
          uploaded_by: string
        }
        Insert: {
          compliance_tags?: string[] | null
          control_id?: string | null
          created_at?: string
          customer_id: string
          description?: string | null
          file_name: string
          file_size: number
          file_type: string
          framework_id?: string | null
          id?: string
          incident_id?: string | null
          storage_path: string
          uploaded_at?: string
          uploaded_by: string
        }
        Update: {
          compliance_tags?: string[] | null
          control_id?: string | null
          created_at?: string
          customer_id?: string
          description?: string | null
          file_name?: string
          file_size?: number
          file_type?: string
          framework_id?: string | null
          id?: string
          incident_id?: string | null
          storage_path?: string
          uploaded_at?: string
          uploaded_by?: string
        }
        Relationships: [
          {
            foreignKeyName: "evidence_files_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "evidence_files_framework_id_fkey"
            columns: ["framework_id"]
            isOneToOne: false
            referencedRelation: "compliance_frameworks"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "evidence_files_incident_id_fkey"
            columns: ["incident_id"]
            isOneToOne: false
            referencedRelation: "incidents"
            referencedColumns: ["id"]
          },
        ]
      }
      expenses: {
        Row: {
          amount: number
          approval_status: string
          approved_at: string | null
          approved_by: string | null
          billable: boolean | null
          category: string
          created_at: string
          currency: string
          customer_id: string
          description: string | null
          expense_date: string
          expense_number: string
          id: string
          merchant: string
          notes: string | null
          paid_at: string | null
          payment_method: string | null
          project_id: string | null
          receipt_url: string | null
          reimbursement_status: string
          submitted_at: string | null
          submitted_by: string
          tags: string[] | null
          updated_at: string
        }
        Insert: {
          amount: number
          approval_status?: string
          approved_at?: string | null
          approved_by?: string | null
          billable?: boolean | null
          category: string
          created_at?: string
          currency?: string
          customer_id: string
          description?: string | null
          expense_date: string
          expense_number: string
          id?: string
          merchant: string
          notes?: string | null
          paid_at?: string | null
          payment_method?: string | null
          project_id?: string | null
          receipt_url?: string | null
          reimbursement_status?: string
          submitted_at?: string | null
          submitted_by: string
          tags?: string[] | null
          updated_at?: string
        }
        Update: {
          amount?: number
          approval_status?: string
          approved_at?: string | null
          approved_by?: string | null
          billable?: boolean | null
          category?: string
          created_at?: string
          currency?: string
          customer_id?: string
          description?: string | null
          expense_date?: string
          expense_number?: string
          id?: string
          merchant?: string
          notes?: string | null
          paid_at?: string | null
          payment_method?: string | null
          project_id?: string | null
          receipt_url?: string | null
          reimbursement_status?: string
          submitted_at?: string | null
          submitted_by?: string
          tags?: string[] | null
          updated_at?: string
        }
        Relationships: []
      }
      feature_access_log: {
        Row: {
          access_granted: boolean
          accessed_at: string
          customer_id: string
          denial_reason: string | null
          feature_name: string
          id: string
          integration_name: string | null
          user_id: string
        }
        Insert: {
          access_granted: boolean
          accessed_at?: string
          customer_id: string
          denial_reason?: string | null
          feature_name: string
          id?: string
          integration_name?: string | null
          user_id: string
        }
        Update: {
          access_granted?: boolean
          accessed_at?: string
          customer_id?: string
          denial_reason?: string | null
          feature_name?: string
          id?: string
          integration_name?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "feature_access_log_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      incidents: {
        Row: {
          affected_ci_ids: string[] | null
          affected_services: string[] | null
          assigned_to: string | null
          auto_remediated: boolean | null
          created_at: string
          created_by: string
          customer_id: string
          description: string
          detected_at: string
          detection_method: string
          id: string
          incident_number: string
          incident_type: string
          remediation_applied: string | null
          resolution_time_minutes: number | null
          resolved_at: string | null
          root_cause: string | null
          severity: string
          status: string
          title: string
          updated_at: string
        }
        Insert: {
          affected_ci_ids?: string[] | null
          affected_services?: string[] | null
          assigned_to?: string | null
          auto_remediated?: boolean | null
          created_at?: string
          created_by: string
          customer_id: string
          description: string
          detected_at?: string
          detection_method: string
          id?: string
          incident_number: string
          incident_type: string
          remediation_applied?: string | null
          resolution_time_minutes?: number | null
          resolved_at?: string | null
          root_cause?: string | null
          severity: string
          status?: string
          title: string
          updated_at?: string
        }
        Update: {
          affected_ci_ids?: string[] | null
          affected_services?: string[] | null
          assigned_to?: string | null
          auto_remediated?: boolean | null
          created_at?: string
          created_by?: string
          customer_id?: string
          description?: string
          detected_at?: string
          detection_method?: string
          id?: string
          incident_number?: string
          incident_type?: string
          remediation_applied?: string | null
          resolution_time_minutes?: number | null
          resolved_at?: string | null
          root_cause?: string | null
          severity?: string
          status?: string
          title?: string
          updated_at?: string
        }
        Relationships: []
      }
      integration_credentials: {
        Row: {
          compliance_tags: string[] | null
          created_at: string
          credential_type: string
          customer_id: string
          encrypted_data: string
          expires_at: string | null
          id: string
          integration_id: string
          updated_at: string
        }
        Insert: {
          compliance_tags?: string[] | null
          created_at?: string
          credential_type: string
          customer_id: string
          encrypted_data: string
          expires_at?: string | null
          id?: string
          integration_id: string
          updated_at?: string
        }
        Update: {
          compliance_tags?: string[] | null
          created_at?: string
          credential_type?: string
          customer_id?: string
          encrypted_data?: string
          expires_at?: string | null
          id?: string
          integration_id?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "integration_credentials_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "integration_credentials_integration_id_fkey"
            columns: ["integration_id"]
            isOneToOne: false
            referencedRelation: "integrations"
            referencedColumns: ["id"]
          },
        ]
      }
      integrations: {
        Row: {
          auth_method: string
          connected_at: string | null
          created_at: string
          customer_id: string
          id: string
          last_sync: string | null
          status: string
          system_name: string
          system_type: string
          updated_at: string
        }
        Insert: {
          auth_method: string
          connected_at?: string | null
          created_at?: string
          customer_id: string
          id?: string
          last_sync?: string | null
          status?: string
          system_name: string
          system_type: string
          updated_at?: string
        }
        Update: {
          auth_method?: string
          connected_at?: string | null
          created_at?: string
          customer_id?: string
          id?: string
          last_sync?: string | null
          status?: string
          system_name?: string
          system_type?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "integrations_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      inventory_items: {
        Row: {
          attributes: Json | null
          barcode: string | null
          batch_numbers: string[] | null
          bin_location: string | null
          category: string
          created_at: string
          current_quantity: number
          customer_id: string
          description: string | null
          expiry_date: string | null
          id: string
          images: string[] | null
          item_name: string
          last_count_date: string | null
          last_restock_date: string | null
          lead_time_days: number | null
          location: string | null
          maximum_quantity: number | null
          minimum_quantity: number | null
          reorder_point: number | null
          reorder_quantity: number | null
          serial_numbers: string[] | null
          sku: string
          status: string
          subcategory: string | null
          unit_cost: number | null
          unit_of_measure: string
          unit_price: number | null
          updated_at: string
          vendor_id: string | null
          warehouse_id: string | null
        }
        Insert: {
          attributes?: Json | null
          barcode?: string | null
          batch_numbers?: string[] | null
          bin_location?: string | null
          category: string
          created_at?: string
          current_quantity?: number
          customer_id: string
          description?: string | null
          expiry_date?: string | null
          id?: string
          images?: string[] | null
          item_name: string
          last_count_date?: string | null
          last_restock_date?: string | null
          lead_time_days?: number | null
          location?: string | null
          maximum_quantity?: number | null
          minimum_quantity?: number | null
          reorder_point?: number | null
          reorder_quantity?: number | null
          serial_numbers?: string[] | null
          sku: string
          status?: string
          subcategory?: string | null
          unit_cost?: number | null
          unit_of_measure?: string
          unit_price?: number | null
          updated_at?: string
          vendor_id?: string | null
          warehouse_id?: string | null
        }
        Update: {
          attributes?: Json | null
          barcode?: string | null
          batch_numbers?: string[] | null
          bin_location?: string | null
          category?: string
          created_at?: string
          current_quantity?: number
          customer_id?: string
          description?: string | null
          expiry_date?: string | null
          id?: string
          images?: string[] | null
          item_name?: string
          last_count_date?: string | null
          last_restock_date?: string | null
          lead_time_days?: number | null
          location?: string | null
          maximum_quantity?: number | null
          minimum_quantity?: number | null
          reorder_point?: number | null
          reorder_quantity?: number | null
          serial_numbers?: string[] | null
          sku?: string
          status?: string
          subcategory?: string | null
          unit_cost?: number | null
          unit_of_measure?: string
          unit_price?: number | null
          updated_at?: string
          vendor_id?: string | null
          warehouse_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "inventory_items_vendor_id_fkey"
            columns: ["vendor_id"]
            isOneToOne: false
            referencedRelation: "vendors"
            referencedColumns: ["id"]
          },
        ]
      }
      inventory_transactions: {
        Row: {
          created_at: string
          customer_id: string
          from_location: string | null
          id: string
          inventory_item_id: string
          notes: string | null
          performed_by: string
          quantity: number
          reason: string | null
          reference_id: string | null
          reference_type: string | null
          to_location: string | null
          total_cost: number | null
          transaction_date: string
          transaction_type: string
          unit_cost: number | null
        }
        Insert: {
          created_at?: string
          customer_id: string
          from_location?: string | null
          id?: string
          inventory_item_id: string
          notes?: string | null
          performed_by: string
          quantity: number
          reason?: string | null
          reference_id?: string | null
          reference_type?: string | null
          to_location?: string | null
          total_cost?: number | null
          transaction_date?: string
          transaction_type: string
          unit_cost?: number | null
        }
        Update: {
          created_at?: string
          customer_id?: string
          from_location?: string | null
          id?: string
          inventory_item_id?: string
          notes?: string | null
          performed_by?: string
          quantity?: number
          reason?: string | null
          reference_id?: string | null
          reference_type?: string | null
          to_location?: string | null
          total_cost?: number | null
          transaction_date?: string
          transaction_type?: string
          unit_cost?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "inventory_transactions_inventory_item_id_fkey"
            columns: ["inventory_item_id"]
            isOneToOne: false
            referencedRelation: "inventory_items"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "inventory_transactions_inventory_item_id_fkey"
            columns: ["inventory_item_id"]
            isOneToOne: false
            referencedRelation: "inventory_reorder_alerts"
            referencedColumns: ["id"]
          },
        ]
      }
      invoices: {
        Row: {
          client_id: string | null
          client_name: string
          created_at: string
          created_by: string
          currency: string
          customer_id: string
          discount_amount: number | null
          due_date: string
          id: string
          invoice_number: string
          issue_date: string
          line_items: Json | null
          notes: string | null
          paid_date: string | null
          payment_method: string | null
          payment_terms: string | null
          project_id: string | null
          purchase_order_id: string | null
          sent_at: string | null
          status: string
          subtotal: number
          tax_amount: number | null
          total_amount: number
          updated_at: string
        }
        Insert: {
          client_id?: string | null
          client_name: string
          created_at?: string
          created_by: string
          currency?: string
          customer_id: string
          discount_amount?: number | null
          due_date: string
          id?: string
          invoice_number: string
          issue_date: string
          line_items?: Json | null
          notes?: string | null
          paid_date?: string | null
          payment_method?: string | null
          payment_terms?: string | null
          project_id?: string | null
          purchase_order_id?: string | null
          sent_at?: string | null
          status?: string
          subtotal?: number
          tax_amount?: number | null
          total_amount: number
          updated_at?: string
        }
        Update: {
          client_id?: string | null
          client_name?: string
          created_at?: string
          created_by?: string
          currency?: string
          customer_id?: string
          discount_amount?: number | null
          due_date?: string
          id?: string
          invoice_number?: string
          issue_date?: string
          line_items?: Json | null
          notes?: string | null
          paid_date?: string | null
          payment_method?: string | null
          payment_terms?: string | null
          project_id?: string | null
          purchase_order_id?: string | null
          sent_at?: string | null
          status?: string
          subtotal?: number
          tax_amount?: number | null
          total_amount?: number
          updated_at?: string
        }
        Relationships: []
      }
      knowledge_access_logs: {
        Row: {
          access_type: string
          article_id: string | null
          compliance_tags: string[] | null
          customer_id: string
          id: string
          search_query: string | null
          timestamp: string
          user_id: string
        }
        Insert: {
          access_type: string
          article_id?: string | null
          compliance_tags?: string[] | null
          customer_id: string
          id?: string
          search_query?: string | null
          timestamp?: string
          user_id: string
        }
        Update: {
          access_type?: string
          article_id?: string | null
          compliance_tags?: string[] | null
          customer_id?: string
          id?: string
          search_query?: string | null
          timestamp?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "knowledge_access_logs_article_id_fkey"
            columns: ["article_id"]
            isOneToOne: false
            referencedRelation: "knowledge_articles"
            referencedColumns: ["id"]
          },
        ]
      }
      knowledge_articles: {
        Row: {
          article_type: string
          category_id: string | null
          content: string
          created_at: string
          created_by: string
          customer_id: string
          id: string
          source_metadata: Json | null
          source_type: string | null
          status: string
          tags: string[] | null
          title: string
          updated_at: string
          updated_by: string | null
          version: number
        }
        Insert: {
          article_type: string
          category_id?: string | null
          content: string
          created_at?: string
          created_by: string
          customer_id: string
          id?: string
          source_metadata?: Json | null
          source_type?: string | null
          status?: string
          tags?: string[] | null
          title: string
          updated_at?: string
          updated_by?: string | null
          version?: number
        }
        Update: {
          article_type?: string
          category_id?: string | null
          content?: string
          created_at?: string
          created_by?: string
          customer_id?: string
          id?: string
          source_metadata?: Json | null
          source_type?: string | null
          status?: string
          tags?: string[] | null
          title?: string
          updated_at?: string
          updated_by?: string | null
          version?: number
        }
        Relationships: [
          {
            foreignKeyName: "knowledge_articles_category_id_fkey"
            columns: ["category_id"]
            isOneToOne: false
            referencedRelation: "knowledge_categories"
            referencedColumns: ["id"]
          },
        ]
      }
      knowledge_categories: {
        Row: {
          created_at: string
          description: string | null
          icon_name: string | null
          id: string
          name: string
          parent_category_id: string | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          description?: string | null
          icon_name?: string | null
          id?: string
          name: string
          parent_category_id?: string | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          description?: string | null
          icon_name?: string | null
          id?: string
          name?: string
          parent_category_id?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "knowledge_categories_parent_category_id_fkey"
            columns: ["parent_category_id"]
            isOneToOne: false
            referencedRelation: "knowledge_categories"
            referencedColumns: ["id"]
          },
        ]
      }
      knowledge_files: {
        Row: {
          ai_summary: string | null
          article_id: string | null
          customer_id: string
          extracted_content: string | null
          file_name: string
          file_size: number
          file_type: string
          id: string
          metadata: Json | null
          processed_status: string
          storage_path: string
          uploaded_at: string
          uploaded_by: string
        }
        Insert: {
          ai_summary?: string | null
          article_id?: string | null
          customer_id: string
          extracted_content?: string | null
          file_name: string
          file_size: number
          file_type: string
          id?: string
          metadata?: Json | null
          processed_status?: string
          storage_path: string
          uploaded_at?: string
          uploaded_by: string
        }
        Update: {
          ai_summary?: string | null
          article_id?: string | null
          customer_id?: string
          extracted_content?: string | null
          file_name?: string
          file_size?: number
          file_type?: string
          id?: string
          metadata?: Json | null
          processed_status?: string
          storage_path?: string
          uploaded_at?: string
          uploaded_by?: string
        }
        Relationships: [
          {
            foreignKeyName: "knowledge_files_article_id_fkey"
            columns: ["article_id"]
            isOneToOne: false
            referencedRelation: "knowledge_articles"
            referencedColumns: ["id"]
          },
        ]
      }
      knowledge_insights: {
        Row: {
          confidence_score: number | null
          created_at: string
          customer_id: string
          data_sources: Json | null
          description: string
          id: string
          insight_type: string
          related_articles: string[] | null
          related_workflows: string[] | null
          reviewed_at: string | null
          reviewed_by: string | null
          status: string
          title: string
        }
        Insert: {
          confidence_score?: number | null
          created_at?: string
          customer_id: string
          data_sources?: Json | null
          description: string
          id?: string
          insight_type: string
          related_articles?: string[] | null
          related_workflows?: string[] | null
          reviewed_at?: string | null
          reviewed_by?: string | null
          status?: string
          title: string
        }
        Update: {
          confidence_score?: number | null
          created_at?: string
          customer_id?: string
          data_sources?: Json | null
          description?: string
          id?: string
          insight_type?: string
          related_articles?: string[] | null
          related_workflows?: string[] | null
          reviewed_at?: string | null
          reviewed_by?: string | null
          status?: string
          title?: string
        }
        Relationships: []
      }
      knowledge_versions: {
        Row: {
          article_id: string
          change_summary: string | null
          changed_by: string
          content: string
          created_at: string
          id: string
          title: string
          version: number
        }
        Insert: {
          article_id: string
          change_summary?: string | null
          changed_by: string
          content: string
          created_at?: string
          id?: string
          title: string
          version: number
        }
        Update: {
          article_id?: string
          change_summary?: string | null
          changed_by?: string
          content?: string
          created_at?: string
          id?: string
          title?: string
          version?: number
        }
        Relationships: [
          {
            foreignKeyName: "knowledge_versions_article_id_fkey"
            columns: ["article_id"]
            isOneToOne: false
            referencedRelation: "knowledge_articles"
            referencedColumns: ["id"]
          },
        ]
      }
      leave_types: {
        Row: {
          annual_allowance_days: number | null
          created_at: string
          customer_id: string
          description: string | null
          id: string
          is_active: boolean | null
          is_paid: boolean | null
          leave_code: string
          leave_type_name: string
          max_consecutive_days: number | null
          requires_approval: boolean | null
          updated_at: string
        }
        Insert: {
          annual_allowance_days?: number | null
          created_at?: string
          customer_id: string
          description?: string | null
          id?: string
          is_active?: boolean | null
          is_paid?: boolean | null
          leave_code: string
          leave_type_name: string
          max_consecutive_days?: number | null
          requires_approval?: boolean | null
          updated_at?: string
        }
        Update: {
          annual_allowance_days?: number | null
          created_at?: string
          customer_id?: string
          description?: string | null
          id?: string
          is_active?: boolean | null
          is_paid?: boolean | null
          leave_code?: string
          leave_type_name?: string
          max_consecutive_days?: number | null
          requires_approval?: boolean | null
          updated_at?: string
        }
        Relationships: []
      }
      mcp_execution_logs: {
        Row: {
          compliance_tags: string[] | null
          customer_id: string
          error_message: string | null
          execution_time_ms: number | null
          id: string
          input_data: Json
          output_data: Json | null
          server_id: string
          status: string
          timestamp: string
          tool_id: string | null
          tool_name: string
          user_id: string | null
        }
        Insert: {
          compliance_tags?: string[] | null
          customer_id: string
          error_message?: string | null
          execution_time_ms?: number | null
          id?: string
          input_data: Json
          output_data?: Json | null
          server_id: string
          status: string
          timestamp?: string
          tool_id?: string | null
          tool_name: string
          user_id?: string | null
        }
        Update: {
          compliance_tags?: string[] | null
          customer_id?: string
          error_message?: string | null
          execution_time_ms?: number | null
          id?: string
          input_data?: Json
          output_data?: Json | null
          server_id?: string
          status?: string
          timestamp?: string
          tool_id?: string | null
          tool_name?: string
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "mcp_execution_logs_server_id_fkey"
            columns: ["server_id"]
            isOneToOne: false
            referencedRelation: "mcp_servers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "mcp_execution_logs_tool_id_fkey"
            columns: ["tool_id"]
            isOneToOne: false
            referencedRelation: "mcp_tools"
            referencedColumns: ["id"]
          },
        ]
      }
      mcp_resources: {
        Row: {
          access_count: number
          created_at: string
          description: string | null
          id: string
          last_accessed: string | null
          metadata: Json | null
          resource_type: string
          resource_uri: string
          server_id: string
        }
        Insert: {
          access_count?: number
          created_at?: string
          description?: string | null
          id?: string
          last_accessed?: string | null
          metadata?: Json | null
          resource_type: string
          resource_uri: string
          server_id: string
        }
        Update: {
          access_count?: number
          created_at?: string
          description?: string | null
          id?: string
          last_accessed?: string | null
          metadata?: Json | null
          resource_type?: string
          resource_uri?: string
          server_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "mcp_resources_server_id_fkey"
            columns: ["server_id"]
            isOneToOne: false
            referencedRelation: "mcp_servers"
            referencedColumns: ["id"]
          },
        ]
      }
      mcp_servers: {
        Row: {
          capabilities: Json
          config: Json | null
          created_at: string
          customer_id: string
          description: string | null
          endpoint_url: string | null
          error_message: string | null
          id: string
          last_health_check: string | null
          server_name: string
          server_type: string
          status: string
          updated_at: string
        }
        Insert: {
          capabilities?: Json
          config?: Json | null
          created_at?: string
          customer_id: string
          description?: string | null
          endpoint_url?: string | null
          error_message?: string | null
          id?: string
          last_health_check?: string | null
          server_name: string
          server_type: string
          status?: string
          updated_at?: string
        }
        Update: {
          capabilities?: Json
          config?: Json | null
          created_at?: string
          customer_id?: string
          description?: string | null
          endpoint_url?: string | null
          error_message?: string | null
          id?: string
          last_health_check?: string | null
          server_name?: string
          server_type?: string
          status?: string
          updated_at?: string
        }
        Relationships: []
      }
      mcp_tools: {
        Row: {
          avg_execution_time_ms: number | null
          created_at: string
          description: string
          execution_count: number
          id: string
          input_schema: Json
          is_enabled: boolean
          output_schema: Json | null
          server_id: string
          tool_name: string
        }
        Insert: {
          avg_execution_time_ms?: number | null
          created_at?: string
          description: string
          execution_count?: number
          id?: string
          input_schema: Json
          is_enabled?: boolean
          output_schema?: Json | null
          server_id: string
          tool_name: string
        }
        Update: {
          avg_execution_time_ms?: number | null
          created_at?: string
          description?: string
          execution_count?: number
          id?: string
          input_schema?: Json
          is_enabled?: boolean
          output_schema?: Json | null
          server_id?: string
          tool_name?: string
        }
        Relationships: [
          {
            foreignKeyName: "mcp_tools_server_id_fkey"
            columns: ["server_id"]
            isOneToOne: false
            referencedRelation: "mcp_servers"
            referencedColumns: ["id"]
          },
        ]
      }
      ml_insights: {
        Row: {
          affected_users: string[] | null
          category: string
          confidence_score: number | null
          created_at: string
          customer_id: string
          data_source: Json | null
          description: string
          expires_at: string | null
          id: string
          insight_type: string
          status: string
        }
        Insert: {
          affected_users?: string[] | null
          category: string
          confidence_score?: number | null
          created_at?: string
          customer_id: string
          data_source?: Json | null
          description: string
          expires_at?: string | null
          id?: string
          insight_type: string
          status?: string
        }
        Update: {
          affected_users?: string[] | null
          category?: string
          confidence_score?: number | null
          created_at?: string
          customer_id?: string
          data_source?: Json | null
          description?: string
          expires_at?: string | null
          id?: string
          insight_type?: string
          status?: string
        }
        Relationships: [
          {
            foreignKeyName: "ml_insights_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      ml_models: {
        Row: {
          accuracy_score: number | null
          created_at: string
          customer_id: string
          deployed_at: string | null
          features_used: string[] | null
          hyperparameters: Json | null
          id: string
          model_name: string
          model_type: string
          status: string
          trained_at: string | null
          training_data_count: number | null
          updated_at: string
          version: string
        }
        Insert: {
          accuracy_score?: number | null
          created_at?: string
          customer_id: string
          deployed_at?: string | null
          features_used?: string[] | null
          hyperparameters?: Json | null
          id?: string
          model_name: string
          model_type: string
          status?: string
          trained_at?: string | null
          training_data_count?: number | null
          updated_at?: string
          version: string
        }
        Update: {
          accuracy_score?: number | null
          created_at?: string
          customer_id?: string
          deployed_at?: string | null
          features_used?: string[] | null
          hyperparameters?: Json | null
          id?: string
          model_name?: string
          model_type?: string
          status?: string
          trained_at?: string | null
          training_data_count?: number | null
          updated_at?: string
          version?: string
        }
        Relationships: [
          {
            foreignKeyName: "ml_models_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      network_alert_rules: {
        Row: {
          auto_remediation_workflow_id: string | null
          conditions: Json
          created_at: string
          created_by: string
          customer_id: string
          description: string | null
          id: string
          is_enabled: boolean | null
          notification_channels: string[] | null
          rule_name: string
          rule_type: string
          severity: string
          updated_at: string
        }
        Insert: {
          auto_remediation_workflow_id?: string | null
          conditions: Json
          created_at?: string
          created_by: string
          customer_id: string
          description?: string | null
          id?: string
          is_enabled?: boolean | null
          notification_channels?: string[] | null
          rule_name: string
          rule_type: string
          severity: string
          updated_at?: string
        }
        Update: {
          auto_remediation_workflow_id?: string | null
          conditions?: Json
          created_at?: string
          created_by?: string
          customer_id?: string
          description?: string | null
          id?: string
          is_enabled?: boolean | null
          notification_channels?: string[] | null
          rule_name?: string
          rule_type?: string
          severity?: string
          updated_at?: string
        }
        Relationships: []
      }
      network_alerts: {
        Row: {
          alert_type: string
          assigned_to: string | null
          auto_remediation_triggered: boolean | null
          correlation_id: string | null
          created_at: string
          customer_id: string
          description: string
          device_id: string | null
          id: string
          incident_id: string | null
          notes: string | null
          remediation_action: string | null
          resolved_at: string | null
          resolved_by: string | null
          severity: string
          source_data: Json | null
          status: string | null
          title: string
          updated_at: string
        }
        Insert: {
          alert_type: string
          assigned_to?: string | null
          auto_remediation_triggered?: boolean | null
          correlation_id?: string | null
          created_at?: string
          customer_id: string
          description: string
          device_id?: string | null
          id?: string
          incident_id?: string | null
          notes?: string | null
          remediation_action?: string | null
          resolved_at?: string | null
          resolved_by?: string | null
          severity: string
          source_data?: Json | null
          status?: string | null
          title: string
          updated_at?: string
        }
        Update: {
          alert_type?: string
          assigned_to?: string | null
          auto_remediation_triggered?: boolean | null
          correlation_id?: string | null
          created_at?: string
          customer_id?: string
          description?: string
          device_id?: string | null
          id?: string
          incident_id?: string | null
          notes?: string | null
          remediation_action?: string | null
          resolved_at?: string | null
          resolved_by?: string | null
          severity?: string
          source_data?: Json | null
          status?: string | null
          title?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "network_alerts_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "network_devices"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "network_alerts_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "soc_engineer_network_devices"
            referencedColumns: ["id"]
          },
        ]
      }
      network_devices: {
        Row: {
          ci_id: string | null
          created_at: string
          created_by: string
          customer_id: string
          description: string | null
          device_name: string
          device_type: string
          id: string
          ip_address: unknown
          last_poll_at: string | null
          last_syslog_at: string | null
          location: string | null
          metadata: Json | null
          model: string | null
          polling_enabled: boolean | null
          polling_interval_seconds: number | null
          snmp_community: string | null
          snmp_port: number | null
          snmp_version: string | null
          status: string | null
          syslog_enabled: boolean | null
          updated_at: string
          vendor: string | null
        }
        Insert: {
          ci_id?: string | null
          created_at?: string
          created_by: string
          customer_id: string
          description?: string | null
          device_name: string
          device_type: string
          id?: string
          ip_address: unknown
          last_poll_at?: string | null
          last_syslog_at?: string | null
          location?: string | null
          metadata?: Json | null
          model?: string | null
          polling_enabled?: boolean | null
          polling_interval_seconds?: number | null
          snmp_community?: string | null
          snmp_port?: number | null
          snmp_version?: string | null
          status?: string | null
          syslog_enabled?: boolean | null
          updated_at?: string
          vendor?: string | null
        }
        Update: {
          ci_id?: string | null
          created_at?: string
          created_by?: string
          customer_id?: string
          description?: string | null
          device_name?: string
          device_type?: string
          id?: string
          ip_address?: unknown
          last_poll_at?: string | null
          last_syslog_at?: string | null
          location?: string | null
          metadata?: Json | null
          model?: string | null
          polling_enabled?: boolean | null
          polling_interval_seconds?: number | null
          snmp_community?: string | null
          snmp_port?: number | null
          snmp_version?: string | null
          status?: string | null
          syslog_enabled?: boolean | null
          updated_at?: string
          vendor?: string | null
        }
        Relationships: []
      }
      notifications: {
        Row: {
          created_at: string
          customer_id: string
          id: string
          is_read: boolean
          link_url: string | null
          message: string
          notification_type: string
          severity: string
          title: string
          user_id: string
        }
        Insert: {
          created_at?: string
          customer_id: string
          id?: string
          is_read?: boolean
          link_url?: string | null
          message: string
          notification_type: string
          severity?: string
          title: string
          user_id: string
        }
        Update: {
          created_at?: string
          customer_id?: string
          id?: string
          is_read?: boolean
          link_url?: string | null
          message?: string
          notification_type?: string
          severity?: string
          title?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "notifications_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      onboarding_milestones: {
        Row: {
          completed_date: string | null
          created_at: string
          description: string | null
          id: string
          milestone_name: string
          onboarding_id: string
          required_task_ids: Json | null
          status: string
          target_date: string | null
        }
        Insert: {
          completed_date?: string | null
          created_at?: string
          description?: string | null
          id?: string
          milestone_name: string
          onboarding_id: string
          required_task_ids?: Json | null
          status?: string
          target_date?: string | null
        }
        Update: {
          completed_date?: string | null
          created_at?: string
          description?: string | null
          id?: string
          milestone_name?: string
          onboarding_id?: string
          required_task_ids?: Json | null
          status?: string
          target_date?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "onboarding_milestones_onboarding_id_fkey"
            columns: ["onboarding_id"]
            isOneToOne: false
            referencedRelation: "client_onboardings"
            referencedColumns: ["id"]
          },
        ]
      }
      onboarding_task_comments: {
        Row: {
          comment_text: string
          created_at: string
          id: string
          is_internal: boolean | null
          task_id: string
          user_id: string
        }
        Insert: {
          comment_text: string
          created_at?: string
          id?: string
          is_internal?: boolean | null
          task_id: string
          user_id: string
        }
        Update: {
          comment_text?: string
          created_at?: string
          id?: string
          is_internal?: boolean | null
          task_id?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "onboarding_task_comments_task_id_fkey"
            columns: ["task_id"]
            isOneToOne: false
            referencedRelation: "client_onboarding_tasks"
            referencedColumns: ["id"]
          },
        ]
      }
      onboarding_template_tasks: {
        Row: {
          assigned_role: string | null
          compliance_tags: string[] | null
          created_at: string
          dependencies: Json | null
          description: string | null
          estimated_hours: number | null
          id: string
          required_documents: Json | null
          requires_client_input: boolean | null
          sequence_order: number
          task_category: string
          task_name: string
          template_id: string
        }
        Insert: {
          assigned_role?: string | null
          compliance_tags?: string[] | null
          created_at?: string
          dependencies?: Json | null
          description?: string | null
          estimated_hours?: number | null
          id?: string
          required_documents?: Json | null
          requires_client_input?: boolean | null
          sequence_order?: number
          task_category: string
          task_name: string
          template_id: string
        }
        Update: {
          assigned_role?: string | null
          compliance_tags?: string[] | null
          created_at?: string
          dependencies?: Json | null
          description?: string | null
          estimated_hours?: number | null
          id?: string
          required_documents?: Json | null
          requires_client_input?: boolean | null
          sequence_order?: number
          task_category?: string
          task_name?: string
          template_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "onboarding_template_tasks_template_id_fkey"
            columns: ["template_id"]
            isOneToOne: false
            referencedRelation: "onboarding_templates"
            referencedColumns: ["id"]
          },
        ]
      }
      onboarding_templates: {
        Row: {
          client_type: string
          created_at: string
          created_by: string
          customer_id: string
          description: string | null
          estimated_days: number | null
          id: string
          is_active: boolean
          template_name: string
          updated_at: string
        }
        Insert: {
          client_type?: string
          created_at?: string
          created_by: string
          customer_id: string
          description?: string | null
          estimated_days?: number | null
          id?: string
          is_active?: boolean
          template_name: string
          updated_at?: string
        }
        Update: {
          client_type?: string
          created_at?: string
          created_by?: string
          customer_id?: string
          description?: string | null
          estimated_days?: number | null
          id?: string
          is_active?: boolean
          template_name?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "onboarding_templates_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      performance_reviews: {
        Row: {
          areas_for_improvement: string | null
          created_at: string
          customer_id: string
          employee_comments: string | null
          employee_id: string
          goals_achieved: string | null
          goals_next_period: string | null
          id: string
          overall_rating: number | null
          performance_score: number | null
          review_date: string
          review_period_end: string
          review_period_start: string
          review_status: string
          review_type: string
          reviewer_comments: string | null
          reviewer_id: string
          signed_by_employee_at: string | null
          signed_by_manager_at: string | null
          strengths: string | null
          updated_at: string
        }
        Insert: {
          areas_for_improvement?: string | null
          created_at?: string
          customer_id: string
          employee_comments?: string | null
          employee_id: string
          goals_achieved?: string | null
          goals_next_period?: string | null
          id?: string
          overall_rating?: number | null
          performance_score?: number | null
          review_date: string
          review_period_end: string
          review_period_start: string
          review_status?: string
          review_type?: string
          reviewer_comments?: string | null
          reviewer_id: string
          signed_by_employee_at?: string | null
          signed_by_manager_at?: string | null
          strengths?: string | null
          updated_at?: string
        }
        Update: {
          areas_for_improvement?: string | null
          created_at?: string
          customer_id?: string
          employee_comments?: string | null
          employee_id?: string
          goals_achieved?: string | null
          goals_next_period?: string | null
          id?: string
          overall_rating?: number | null
          performance_score?: number | null
          review_date?: string
          review_period_end?: string
          review_period_start?: string
          review_status?: string
          review_type?: string
          reviewer_comments?: string | null
          reviewer_id?: string
          signed_by_employee_at?: string | null
          signed_by_manager_at?: string | null
          strengths?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "performance_reviews_employee_id_fkey"
            columns: ["employee_id"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "performance_reviews_reviewer_id_fkey"
            columns: ["reviewer_id"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
        ]
      }
      prediction_history: {
        Row: {
          actual_value: Json | null
          confidence_score: number | null
          created_at: string
          customer_id: string
          id: string
          input_features: Json
          model_id: string
          predicted_value: Json
          prediction_type: string
          was_accurate: boolean | null
        }
        Insert: {
          actual_value?: Json | null
          confidence_score?: number | null
          created_at?: string
          customer_id: string
          id?: string
          input_features: Json
          model_id: string
          predicted_value: Json
          prediction_type: string
          was_accurate?: boolean | null
        }
        Update: {
          actual_value?: Json | null
          confidence_score?: number | null
          created_at?: string
          customer_id?: string
          id?: string
          input_features?: Json
          model_id?: string
          predicted_value?: Json
          prediction_type?: string
          was_accurate?: boolean | null
        }
        Relationships: [
          {
            foreignKeyName: "prediction_history_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "prediction_history_model_id_fkey"
            columns: ["model_id"]
            isOneToOne: false
            referencedRelation: "ml_models"
            referencedColumns: ["id"]
          },
        ]
      }
      products: {
        Row: {
          base_price: number | null
          billing_frequency: string | null
          category: string
          created_at: string
          description: string | null
          enabled_features: string[] | null
          enabled_integrations: string[] | null
          feature_limits: Json | null
          id: string
          is_active: boolean | null
          product_code: string
          product_name: string
          service_tier: string | null
          updated_at: string
        }
        Insert: {
          base_price?: number | null
          billing_frequency?: string | null
          category?: string
          created_at?: string
          description?: string | null
          enabled_features?: string[] | null
          enabled_integrations?: string[] | null
          feature_limits?: Json | null
          id?: string
          is_active?: boolean | null
          product_code: string
          product_name: string
          service_tier?: string | null
          updated_at?: string
        }
        Update: {
          base_price?: number | null
          billing_frequency?: string | null
          category?: string
          created_at?: string
          description?: string | null
          enabled_features?: string[] | null
          enabled_integrations?: string[] | null
          feature_limits?: Json | null
          id?: string
          is_active?: boolean | null
          product_code?: string
          product_name?: string
          service_tier?: string | null
          updated_at?: string
        }
        Relationships: []
      }
      project_documents: {
        Row: {
          created_at: string
          customer_id: string
          description: string | null
          document_name: string
          document_type: string | null
          file_size: number | null
          file_url: string
          id: string
          is_active: boolean | null
          project_id: string
          updated_at: string
          uploaded_by: string | null
          version: string | null
        }
        Insert: {
          created_at?: string
          customer_id: string
          description?: string | null
          document_name: string
          document_type?: string | null
          file_size?: number | null
          file_url: string
          id?: string
          is_active?: boolean | null
          project_id: string
          updated_at?: string
          uploaded_by?: string | null
          version?: string | null
        }
        Update: {
          created_at?: string
          customer_id?: string
          description?: string | null
          document_name?: string
          document_type?: string | null
          file_size?: number | null
          file_url?: string
          id?: string
          is_active?: boolean | null
          project_id?: string
          updated_at?: string
          uploaded_by?: string | null
          version?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "project_documents_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "project_documents_uploaded_by_fkey"
            columns: ["uploaded_by"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
        ]
      }
      project_expenses: {
        Row: {
          amount: number
          approved_at: string | null
          approved_by: string | null
          created_at: string
          customer_id: string
          expense_date: string
          expense_description: string
          expense_status: string
          expense_type: string
          id: string
          is_billable: boolean | null
          is_reimbursable: boolean | null
          notes: string | null
          project_id: string
          receipt_url: string | null
          submitted_by: string | null
          updated_at: string
          vendor_id: string | null
        }
        Insert: {
          amount: number
          approved_at?: string | null
          approved_by?: string | null
          created_at?: string
          customer_id: string
          expense_date?: string
          expense_description: string
          expense_status?: string
          expense_type: string
          id?: string
          is_billable?: boolean | null
          is_reimbursable?: boolean | null
          notes?: string | null
          project_id: string
          receipt_url?: string | null
          submitted_by?: string | null
          updated_at?: string
          vendor_id?: string | null
        }
        Update: {
          amount?: number
          approved_at?: string | null
          approved_by?: string | null
          created_at?: string
          customer_id?: string
          expense_date?: string
          expense_description?: string
          expense_status?: string
          expense_type?: string
          id?: string
          is_billable?: boolean | null
          is_reimbursable?: boolean | null
          notes?: string | null
          project_id?: string
          receipt_url?: string | null
          submitted_by?: string | null
          updated_at?: string
          vendor_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "project_expenses_approved_by_fkey"
            columns: ["approved_by"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "project_expenses_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "project_expenses_submitted_by_fkey"
            columns: ["submitted_by"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "project_expenses_vendor_id_fkey"
            columns: ["vendor_id"]
            isOneToOne: false
            referencedRelation: "vendors"
            referencedColumns: ["id"]
          },
        ]
      }
      project_milestones: {
        Row: {
          completion_date: string | null
          created_at: string
          customer_id: string
          deliverables: string | null
          due_date: string
          id: string
          is_critical: boolean | null
          milestone_description: string | null
          milestone_name: string
          milestone_status: string
          project_id: string
          updated_at: string
        }
        Insert: {
          completion_date?: string | null
          created_at?: string
          customer_id: string
          deliverables?: string | null
          due_date: string
          id?: string
          is_critical?: boolean | null
          milestone_description?: string | null
          milestone_name: string
          milestone_status?: string
          project_id: string
          updated_at?: string
        }
        Update: {
          completion_date?: string | null
          created_at?: string
          customer_id?: string
          deliverables?: string | null
          due_date?: string
          id?: string
          is_critical?: boolean | null
          milestone_description?: string | null
          milestone_name?: string
          milestone_status?: string
          project_id?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "project_milestones_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      project_tasks: {
        Row: {
          actual_hours: number | null
          assigned_to: string | null
          billing_rate: number | null
          completed_date: string | null
          completion_percentage: number | null
          created_at: string
          customer_id: string
          due_date: string | null
          estimated_hours: number | null
          id: string
          is_billable: boolean | null
          notes: string | null
          parent_task_id: string | null
          priority: string
          project_id: string
          start_date: string | null
          task_description: string | null
          task_name: string
          task_number: string
          task_status: string
          updated_at: string
        }
        Insert: {
          actual_hours?: number | null
          assigned_to?: string | null
          billing_rate?: number | null
          completed_date?: string | null
          completion_percentage?: number | null
          created_at?: string
          customer_id: string
          due_date?: string | null
          estimated_hours?: number | null
          id?: string
          is_billable?: boolean | null
          notes?: string | null
          parent_task_id?: string | null
          priority?: string
          project_id: string
          start_date?: string | null
          task_description?: string | null
          task_name: string
          task_number: string
          task_status?: string
          updated_at?: string
        }
        Update: {
          actual_hours?: number | null
          assigned_to?: string | null
          billing_rate?: number | null
          completed_date?: string | null
          completion_percentage?: number | null
          created_at?: string
          customer_id?: string
          due_date?: string | null
          estimated_hours?: number | null
          id?: string
          is_billable?: boolean | null
          notes?: string | null
          parent_task_id?: string | null
          priority?: string
          project_id?: string
          start_date?: string | null
          task_description?: string | null
          task_name?: string
          task_number?: string
          task_status?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "project_tasks_assigned_to_fkey"
            columns: ["assigned_to"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "project_tasks_parent_task_id_fkey"
            columns: ["parent_task_id"]
            isOneToOne: false
            referencedRelation: "project_tasks"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "project_tasks_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      project_team: {
        Row: {
          allocation_percentage: number | null
          created_at: string
          customer_id: string
          employee_id: string
          end_date: string | null
          hourly_rate: number | null
          id: string
          is_active: boolean | null
          project_id: string
          role: string
          start_date: string | null
          updated_at: string
        }
        Insert: {
          allocation_percentage?: number | null
          created_at?: string
          customer_id: string
          employee_id: string
          end_date?: string | null
          hourly_rate?: number | null
          id?: string
          is_active?: boolean | null
          project_id: string
          role: string
          start_date?: string | null
          updated_at?: string
        }
        Update: {
          allocation_percentage?: number | null
          created_at?: string
          customer_id?: string
          employee_id?: string
          end_date?: string | null
          hourly_rate?: number | null
          id?: string
          is_active?: boolean | null
          project_id?: string
          role?: string
          start_date?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "project_team_employee_id_fkey"
            columns: ["employee_id"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "project_team_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
        ]
      }
      project_time_entries: {
        Row: {
          approved_at: string | null
          approved_by: string | null
          billed_amount: number | null
          billing_rate: number | null
          created_at: string
          customer_id: string
          description: string | null
          employee_id: string
          end_time: string | null
          entry_date: string
          hours: number
          id: string
          invoice_id: string | null
          is_approved: boolean | null
          is_billable: boolean | null
          project_id: string
          start_time: string | null
          task_id: string | null
          updated_at: string
        }
        Insert: {
          approved_at?: string | null
          approved_by?: string | null
          billed_amount?: number | null
          billing_rate?: number | null
          created_at?: string
          customer_id: string
          description?: string | null
          employee_id: string
          end_time?: string | null
          entry_date: string
          hours: number
          id?: string
          invoice_id?: string | null
          is_approved?: boolean | null
          is_billable?: boolean | null
          project_id: string
          start_time?: string | null
          task_id?: string | null
          updated_at?: string
        }
        Update: {
          approved_at?: string | null
          approved_by?: string | null
          billed_amount?: number | null
          billing_rate?: number | null
          created_at?: string
          customer_id?: string
          description?: string | null
          employee_id?: string
          end_time?: string | null
          entry_date?: string
          hours?: number
          id?: string
          invoice_id?: string | null
          is_approved?: boolean | null
          is_billable?: boolean | null
          project_id?: string
          start_time?: string | null
          task_id?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "project_time_entries_approved_by_fkey"
            columns: ["approved_by"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "project_time_entries_employee_id_fkey"
            columns: ["employee_id"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "project_time_entries_project_id_fkey"
            columns: ["project_id"]
            isOneToOne: false
            referencedRelation: "projects"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "project_time_entries_task_id_fkey"
            columns: ["task_id"]
            isOneToOne: false
            referencedRelation: "project_tasks"
            referencedColumns: ["id"]
          },
        ]
      }
      projects: {
        Row: {
          actual_cost: number | null
          actual_hours: number | null
          billing_type: string | null
          budget_amount: number | null
          completion_percentage: number | null
          created_at: string
          customer_account_id: string | null
          customer_id: string
          deliverables: string | null
          description: string | null
          end_date: string | null
          estimated_hours: number | null
          hourly_rate: number | null
          id: string
          is_billable: boolean | null
          objectives: string | null
          priority: string
          project_code: string | null
          project_manager_id: string | null
          project_name: string
          project_number: string
          project_status: string
          project_type: string
          risks: string | null
          start_date: string | null
          updated_at: string
        }
        Insert: {
          actual_cost?: number | null
          actual_hours?: number | null
          billing_type?: string | null
          budget_amount?: number | null
          completion_percentage?: number | null
          created_at?: string
          customer_account_id?: string | null
          customer_id: string
          deliverables?: string | null
          description?: string | null
          end_date?: string | null
          estimated_hours?: number | null
          hourly_rate?: number | null
          id?: string
          is_billable?: boolean | null
          objectives?: string | null
          priority?: string
          project_code?: string | null
          project_manager_id?: string | null
          project_name: string
          project_number: string
          project_status?: string
          project_type?: string
          risks?: string | null
          start_date?: string | null
          updated_at?: string
        }
        Update: {
          actual_cost?: number | null
          actual_hours?: number | null
          billing_type?: string | null
          budget_amount?: number | null
          completion_percentage?: number | null
          created_at?: string
          customer_account_id?: string | null
          customer_id?: string
          deliverables?: string | null
          description?: string | null
          end_date?: string | null
          estimated_hours?: number | null
          hourly_rate?: number | null
          id?: string
          is_billable?: boolean | null
          objectives?: string | null
          priority?: string
          project_code?: string | null
          project_manager_id?: string | null
          project_name?: string
          project_number?: string
          project_status?: string
          project_type?: string
          risks?: string | null
          start_date?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "projects_customer_account_id_fkey"
            columns: ["customer_account_id"]
            isOneToOne: false
            referencedRelation: "customer_accounts"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "projects_project_manager_id_fkey"
            columns: ["project_manager_id"]
            isOneToOne: false
            referencedRelation: "employees"
            referencedColumns: ["id"]
          },
        ]
      }
      purchase_orders: {
        Row: {
          approval_workflow: Json | null
          approved_at: string | null
          approved_by: string | null
          attachments: Json | null
          billing_address: string | null
          created_at: string
          currency: string
          customer_id: string
          delivery_date: string | null
          id: string
          items: Json | null
          notes: string | null
          payment_terms: string | null
          po_number: string
          priority: string
          received_at: string | null
          requested_by: string
          shipping_address: string | null
          status: string
          submitted_at: string | null
          total_amount: number
          updated_at: string
          vendor_id: string | null
          vendor_id_fk: string | null
          vendor_name: string
        }
        Insert: {
          approval_workflow?: Json | null
          approved_at?: string | null
          approved_by?: string | null
          attachments?: Json | null
          billing_address?: string | null
          created_at?: string
          currency?: string
          customer_id: string
          delivery_date?: string | null
          id?: string
          items?: Json | null
          notes?: string | null
          payment_terms?: string | null
          po_number: string
          priority?: string
          received_at?: string | null
          requested_by: string
          shipping_address?: string | null
          status?: string
          submitted_at?: string | null
          total_amount?: number
          updated_at?: string
          vendor_id?: string | null
          vendor_id_fk?: string | null
          vendor_name: string
        }
        Update: {
          approval_workflow?: Json | null
          approved_at?: string | null
          approved_by?: string | null
          attachments?: Json | null
          billing_address?: string | null
          created_at?: string
          currency?: string
          customer_id?: string
          delivery_date?: string | null
          id?: string
          items?: Json | null
          notes?: string | null
          payment_terms?: string | null
          po_number?: string
          priority?: string
          received_at?: string | null
          requested_by?: string
          shipping_address?: string | null
          status?: string
          submitted_at?: string | null
          total_amount?: number
          updated_at?: string
          vendor_id?: string | null
          vendor_id_fk?: string | null
          vendor_name?: string
        }
        Relationships: [
          {
            foreignKeyName: "purchase_orders_vendor_id_fk_fkey"
            columns: ["vendor_id_fk"]
            isOneToOne: false
            referencedRelation: "vendors"
            referencedColumns: ["id"]
          },
        ]
      }
      remediation_executions: {
        Row: {
          actions_taken: Json
          customer_id: string
          error_message: string | null
          executed_at: string
          executed_by: string | null
          execution_duration_ms: number | null
          execution_type: string
          id: string
          incident_id: string
          rule_id: string | null
          success: boolean
        }
        Insert: {
          actions_taken: Json
          customer_id: string
          error_message?: string | null
          executed_at?: string
          executed_by?: string | null
          execution_duration_ms?: number | null
          execution_type: string
          id?: string
          incident_id: string
          rule_id?: string | null
          success: boolean
        }
        Update: {
          actions_taken?: Json
          customer_id?: string
          error_message?: string | null
          executed_at?: string
          executed_by?: string | null
          execution_duration_ms?: number | null
          execution_type?: string
          id?: string
          incident_id?: string
          rule_id?: string | null
          success?: boolean
        }
        Relationships: [
          {
            foreignKeyName: "remediation_executions_incident_id_fkey"
            columns: ["incident_id"]
            isOneToOne: false
            referencedRelation: "incidents"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "remediation_executions_rule_id_fkey"
            columns: ["rule_id"]
            isOneToOne: false
            referencedRelation: "remediation_rules"
            referencedColumns: ["id"]
          },
        ]
      }
      remediation_rules: {
        Row: {
          approval_threshold: string | null
          auto_execute: boolean | null
          conditions: Json
          created_at: string
          created_by: string
          customer_id: string
          description: string | null
          execution_count: number | null
          id: string
          incident_pattern: Json
          is_active: boolean | null
          last_executed_at: string | null
          remediation_actions: Json
          requires_approval: boolean | null
          rule_name: string
          success_rate: number | null
          updated_at: string
        }
        Insert: {
          approval_threshold?: string | null
          auto_execute?: boolean | null
          conditions: Json
          created_at?: string
          created_by: string
          customer_id: string
          description?: string | null
          execution_count?: number | null
          id?: string
          incident_pattern: Json
          is_active?: boolean | null
          last_executed_at?: string | null
          remediation_actions: Json
          requires_approval?: boolean | null
          rule_name: string
          success_rate?: number | null
          updated_at?: string
        }
        Update: {
          approval_threshold?: string | null
          auto_execute?: boolean | null
          conditions?: Json
          created_at?: string
          created_by?: string
          customer_id?: string
          description?: string | null
          execution_count?: number | null
          id?: string
          incident_pattern?: Json
          is_active?: boolean | null
          last_executed_at?: string | null
          remediation_actions?: Json
          requires_approval?: boolean | null
          rule_name?: string
          success_rate?: number | null
          updated_at?: string
        }
        Relationships: []
      }
      report_executions: {
        Row: {
          created_at: string
          customer_id: string
          error_message: string | null
          executed_by: string | null
          execution_time_ms: number | null
          execution_type: string
          id: string
          output_file_url: string | null
          report_id: string
          result_count: number | null
          status: string
        }
        Insert: {
          created_at?: string
          customer_id: string
          error_message?: string | null
          executed_by?: string | null
          execution_time_ms?: number | null
          execution_type: string
          id?: string
          output_file_url?: string | null
          report_id: string
          result_count?: number | null
          status: string
        }
        Update: {
          created_at?: string
          customer_id?: string
          error_message?: string | null
          executed_by?: string | null
          execution_time_ms?: number | null
          execution_type?: string
          id?: string
          output_file_url?: string | null
          report_id?: string
          result_count?: number | null
          status?: string
        }
        Relationships: [
          {
            foreignKeyName: "report_executions_report_id_fkey"
            columns: ["report_id"]
            isOneToOne: false
            referencedRelation: "custom_reports"
            referencedColumns: ["id"]
          },
        ]
      }
      role_permissions: {
        Row: {
          created_at: string
          id: string
          permission_level: string
          resource_name: string
          resource_type: string
          role_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          permission_level?: string
          resource_name: string
          resource_type: string
          role_id: string
        }
        Update: {
          created_at?: string
          id?: string
          permission_level?: string
          resource_name?: string
          resource_type?: string
          role_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "role_permissions_role_id_fkey"
            columns: ["role_id"]
            isOneToOne: false
            referencedRelation: "roles"
            referencedColumns: ["id"]
          },
        ]
      }
      roles: {
        Row: {
          created_at: string
          description: string | null
          id: string
          name: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          description?: string | null
          id?: string
          name: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          description?: string | null
          id?: string
          name?: string
          updated_at?: string
        }
        Relationships: []
      }
      sales_activities: {
        Row: {
          activity_status: string
          activity_type: string
          assigned_to: string
          completed_at: string | null
          created_at: string
          customer_id: string
          description: string | null
          due_date: string | null
          id: string
          priority: string | null
          related_to_id: string | null
          related_to_type: string | null
          subject: string
          updated_at: string
        }
        Insert: {
          activity_status?: string
          activity_type: string
          assigned_to: string
          completed_at?: string | null
          created_at?: string
          customer_id: string
          description?: string | null
          due_date?: string | null
          id?: string
          priority?: string | null
          related_to_id?: string | null
          related_to_type?: string | null
          subject: string
          updated_at?: string
        }
        Update: {
          activity_status?: string
          activity_type?: string
          assigned_to?: string
          completed_at?: string | null
          created_at?: string
          customer_id?: string
          description?: string | null
          due_date?: string | null
          id?: string
          priority?: string | null
          related_to_id?: string | null
          related_to_type?: string | null
          subject?: string
          updated_at?: string
        }
        Relationships: []
      }
      sales_leads: {
        Row: {
          assigned_to: string | null
          company_name: string
          company_size: string | null
          contact_email: string | null
          contact_name: string
          contact_phone: string | null
          converted_at: string | null
          converted_to_opportunity_id: string | null
          created_at: string
          customer_id: string
          estimated_value: number | null
          id: string
          industry: string | null
          lead_number: string
          lead_score: number | null
          lead_source: string | null
          lead_status: string
          next_follow_up: string | null
          notes: string | null
          updated_at: string
        }
        Insert: {
          assigned_to?: string | null
          company_name: string
          company_size?: string | null
          contact_email?: string | null
          contact_name: string
          contact_phone?: string | null
          converted_at?: string | null
          converted_to_opportunity_id?: string | null
          created_at?: string
          customer_id: string
          estimated_value?: number | null
          id?: string
          industry?: string | null
          lead_number: string
          lead_score?: number | null
          lead_source?: string | null
          lead_status?: string
          next_follow_up?: string | null
          notes?: string | null
          updated_at?: string
        }
        Update: {
          assigned_to?: string | null
          company_name?: string
          company_size?: string | null
          contact_email?: string | null
          contact_name?: string
          contact_phone?: string | null
          converted_at?: string | null
          converted_to_opportunity_id?: string | null
          created_at?: string
          customer_id?: string
          estimated_value?: number | null
          id?: string
          industry?: string | null
          lead_number?: string
          lead_score?: number | null
          lead_source?: string | null
          lead_status?: string
          next_follow_up?: string | null
          notes?: string | null
          updated_at?: string
        }
        Relationships: []
      }
      sales_opportunities: {
        Row: {
          account_name: string
          actual_close_date: string | null
          amount: number
          assigned_to: string | null
          competitors: string[] | null
          contact_email: string | null
          contact_name: string
          created_at: string
          customer_id: string
          expected_close_date: string | null
          id: string
          key_decision_makers: Json | null
          lead_id: string | null
          loss_reason: string | null
          notes: string | null
          opportunity_name: string
          opportunity_number: string
          opportunity_type: string | null
          probability: number | null
          stage: string
          updated_at: string
        }
        Insert: {
          account_name: string
          actual_close_date?: string | null
          amount: number
          assigned_to?: string | null
          competitors?: string[] | null
          contact_email?: string | null
          contact_name: string
          created_at?: string
          customer_id: string
          expected_close_date?: string | null
          id?: string
          key_decision_makers?: Json | null
          lead_id?: string | null
          loss_reason?: string | null
          notes?: string | null
          opportunity_name: string
          opportunity_number: string
          opportunity_type?: string | null
          probability?: number | null
          stage?: string
          updated_at?: string
        }
        Update: {
          account_name?: string
          actual_close_date?: string | null
          amount?: number
          assigned_to?: string | null
          competitors?: string[] | null
          contact_email?: string | null
          contact_name?: string
          created_at?: string
          customer_id?: string
          expected_close_date?: string | null
          id?: string
          key_decision_makers?: Json | null
          lead_id?: string | null
          loss_reason?: string | null
          notes?: string | null
          opportunity_name?: string
          opportunity_number?: string
          opportunity_type?: string | null
          probability?: number | null
          stage?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "sales_opportunities_lead_id_fkey"
            columns: ["lead_id"]
            isOneToOne: false
            referencedRelation: "sales_leads"
            referencedColumns: ["id"]
          },
        ]
      }
      sales_quotes: {
        Row: {
          accepted_at: string | null
          account_name: string
          contact_email: string | null
          contact_name: string
          created_at: string
          created_by: string
          customer_id: string
          discount_amount: number | null
          expiry_date: string | null
          id: string
          line_items: Json
          notes: string | null
          opportunity_id: string | null
          quote_date: string
          quote_name: string
          quote_number: string
          quote_status: string
          subtotal: number
          tax_amount: number | null
          terms_conditions: string | null
          total_amount: number
          updated_at: string
        }
        Insert: {
          accepted_at?: string | null
          account_name: string
          contact_email?: string | null
          contact_name: string
          created_at?: string
          created_by: string
          customer_id: string
          discount_amount?: number | null
          expiry_date?: string | null
          id?: string
          line_items?: Json
          notes?: string | null
          opportunity_id?: string | null
          quote_date?: string
          quote_name: string
          quote_number: string
          quote_status?: string
          subtotal?: number
          tax_amount?: number | null
          terms_conditions?: string | null
          total_amount?: number
          updated_at?: string
        }
        Update: {
          accepted_at?: string | null
          account_name?: string
          contact_email?: string | null
          contact_name?: string
          created_at?: string
          created_by?: string
          customer_id?: string
          discount_amount?: number | null
          expiry_date?: string | null
          id?: string
          line_items?: Json
          notes?: string | null
          opportunity_id?: string | null
          quote_date?: string
          quote_name?: string
          quote_number?: string
          quote_status?: string
          subtotal?: number
          tax_amount?: number | null
          terms_conditions?: string | null
          total_amount?: number
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "sales_quotes_opportunity_id_fkey"
            columns: ["opportunity_id"]
            isOneToOne: false
            referencedRelation: "sales_opportunities"
            referencedColumns: ["id"]
          },
        ]
      }
      service_catalog: {
        Row: {
          approval_workflow_id: string | null
          category: string
          created_at: string
          customer_id: string
          description: string
          display_order: number | null
          estimated_delivery_days: number | null
          icon: string | null
          id: string
          is_active: boolean | null
          request_form_schema: Json
          requires_approval: boolean | null
          service_name: string
          sla_hours: number | null
          updated_at: string
        }
        Insert: {
          approval_workflow_id?: string | null
          category: string
          created_at?: string
          customer_id: string
          description: string
          display_order?: number | null
          estimated_delivery_days?: number | null
          icon?: string | null
          id?: string
          is_active?: boolean | null
          request_form_schema?: Json
          requires_approval?: boolean | null
          service_name: string
          sla_hours?: number | null
          updated_at?: string
        }
        Update: {
          approval_workflow_id?: string | null
          category?: string
          created_at?: string
          customer_id?: string
          description?: string
          display_order?: number | null
          estimated_delivery_days?: number | null
          icon?: string | null
          id?: string
          is_active?: boolean | null
          request_form_schema?: Json
          requires_approval?: boolean | null
          service_name?: string
          sla_hours?: number | null
          updated_at?: string
        }
        Relationships: []
      }
      service_requests: {
        Row: {
          approved_at: string | null
          approved_by: string | null
          assigned_to: string | null
          completed_at: string | null
          created_at: string
          customer_id: string
          description: string
          due_date: string | null
          form_data: Json | null
          id: string
          priority: string
          request_number: string
          requested_by: string
          service_id: string
          status: string
          title: string
          updated_at: string
        }
        Insert: {
          approved_at?: string | null
          approved_by?: string | null
          assigned_to?: string | null
          completed_at?: string | null
          created_at?: string
          customer_id: string
          description: string
          due_date?: string | null
          form_data?: Json | null
          id?: string
          priority?: string
          request_number: string
          requested_by: string
          service_id: string
          status?: string
          title: string
          updated_at?: string
        }
        Update: {
          approved_at?: string | null
          approved_by?: string | null
          assigned_to?: string | null
          completed_at?: string | null
          created_at?: string
          customer_id?: string
          description?: string
          due_date?: string | null
          form_data?: Json | null
          id?: string
          priority?: string
          request_number?: string
          requested_by?: string
          service_id?: string
          status?: string
          title?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "service_requests_requested_by_fkey"
            columns: ["requested_by"]
            isOneToOne: false
            referencedRelation: "client_portal_users"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "service_requests_service_id_fkey"
            columns: ["service_id"]
            isOneToOne: false
            referencedRelation: "service_catalog"
            referencedColumns: ["id"]
          },
        ]
      }
      service_tier_packages: {
        Row: {
          created_at: string
          description: string | null
          id: string
          included_integrations: string[] | null
          included_products: string[] | null
          is_active: boolean | null
          max_storage_gb: number | null
          max_users: number | null
          support_level: string | null
          tier_level: number
          tier_name: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          description?: string | null
          id?: string
          included_integrations?: string[] | null
          included_products?: string[] | null
          is_active?: boolean | null
          max_storage_gb?: number | null
          max_users?: number | null
          support_level?: string | null
          tier_level: number
          tier_name: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          description?: string | null
          id?: string
          included_integrations?: string[] | null
          included_products?: string[] | null
          is_active?: boolean | null
          max_storage_gb?: number | null
          max_users?: number | null
          support_level?: string | null
          tier_level?: number
          tier_name?: string
          updated_at?: string
        }
        Relationships: []
      }
      sharepoint_sync_config: {
        Row: {
          created_at: string
          customer_id: string
          filter_extensions: string[] | null
          id: string
          last_sync_at: string | null
          library_id: string | null
          library_name: string | null
          site_id: string
          site_name: string
          site_url: string
          sync_enabled: boolean
          sync_frequency_minutes: number
          updated_at: string
        }
        Insert: {
          created_at?: string
          customer_id: string
          filter_extensions?: string[] | null
          id?: string
          last_sync_at?: string | null
          library_id?: string | null
          library_name?: string | null
          site_id: string
          site_name: string
          site_url: string
          sync_enabled?: boolean
          sync_frequency_minutes?: number
          updated_at?: string
        }
        Update: {
          created_at?: string
          customer_id?: string
          filter_extensions?: string[] | null
          id?: string
          last_sync_at?: string | null
          library_id?: string | null
          library_name?: string | null
          site_id?: string
          site_name?: string
          site_url?: string
          sync_enabled?: boolean
          sync_frequency_minutes?: number
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "sharepoint_sync_config_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      sharepoint_sync_logs: {
        Row: {
          created_at: string
          error_message: string | null
          files_failed: number | null
          files_synced: number | null
          id: string
          status: string
          sync_completed_at: string | null
          sync_config_id: string
          sync_details: Json | null
          sync_started_at: string
        }
        Insert: {
          created_at?: string
          error_message?: string | null
          files_failed?: number | null
          files_synced?: number | null
          id?: string
          status?: string
          sync_completed_at?: string | null
          sync_config_id: string
          sync_details?: Json | null
          sync_started_at?: string
        }
        Update: {
          created_at?: string
          error_message?: string | null
          files_failed?: number | null
          files_synced?: number | null
          id?: string
          status?: string
          sync_completed_at?: string | null
          sync_config_id?: string
          sync_details?: Json | null
          sync_started_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "sharepoint_sync_logs_sync_config_id_fkey"
            columns: ["sync_config_id"]
            isOneToOne: false
            referencedRelation: "sharepoint_sync_config"
            referencedColumns: ["id"]
          },
        ]
      }
      snmp_traps: {
        Row: {
          acknowledged_at: string | null
          acknowledged_by: string | null
          created_at: string
          created_incident_id: string | null
          customer_id: string
          device_id: string | null
          id: string
          is_acknowledged: boolean | null
          processed: boolean | null
          raw_data: Json | null
          received_at: string
          severity: string | null
          source_ip: unknown
          trap_oid: string
          trap_type: string | null
          varbinds: Json | null
        }
        Insert: {
          acknowledged_at?: string | null
          acknowledged_by?: string | null
          created_at?: string
          created_incident_id?: string | null
          customer_id: string
          device_id?: string | null
          id?: string
          is_acknowledged?: boolean | null
          processed?: boolean | null
          raw_data?: Json | null
          received_at?: string
          severity?: string | null
          source_ip: unknown
          trap_oid: string
          trap_type?: string | null
          varbinds?: Json | null
        }
        Update: {
          acknowledged_at?: string | null
          acknowledged_by?: string | null
          created_at?: string
          created_incident_id?: string | null
          customer_id?: string
          device_id?: string | null
          id?: string
          is_acknowledged?: boolean | null
          processed?: boolean | null
          raw_data?: Json | null
          received_at?: string
          severity?: string | null
          source_ip?: unknown
          trap_oid?: string
          trap_type?: string | null
          varbinds?: Json | null
        }
        Relationships: [
          {
            foreignKeyName: "snmp_traps_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "network_devices"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "snmp_traps_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "soc_engineer_network_devices"
            referencedColumns: ["id"]
          },
        ]
      }
      subscription_plans: {
        Row: {
          created_at: string
          features: Json
          id: string
          is_active: boolean
          max_controls: number | null
          max_frameworks: number | null
          max_team_members: number | null
          plan_name: string
          plan_tier: string
          price_monthly: number | null
          price_yearly: number | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          features: Json
          id?: string
          is_active?: boolean
          max_controls?: number | null
          max_frameworks?: number | null
          max_team_members?: number | null
          plan_name: string
          plan_tier: string
          price_monthly?: number | null
          price_yearly?: number | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          features?: Json
          id?: string
          is_active?: boolean
          max_controls?: number | null
          max_frameworks?: number | null
          max_team_members?: number | null
          plan_name?: string
          plan_tier?: string
          price_monthly?: number | null
          price_yearly?: number | null
          updated_at?: string
        }
        Relationships: []
      }
      support_tickets: {
        Row: {
          assigned_to: string | null
          category: string | null
          created_at: string
          created_by: string
          customer_id: string
          description: string
          id: string
          metadata: Json | null
          priority: string
          resolution_notes: string | null
          resolved_at: string | null
          resolved_by: string | null
          status: string
          subject: string
          tags: string[] | null
          ticket_number: string
          updated_at: string
        }
        Insert: {
          assigned_to?: string | null
          category?: string | null
          created_at?: string
          created_by: string
          customer_id: string
          description: string
          id?: string
          metadata?: Json | null
          priority?: string
          resolution_notes?: string | null
          resolved_at?: string | null
          resolved_by?: string | null
          status?: string
          subject: string
          tags?: string[] | null
          ticket_number: string
          updated_at?: string
        }
        Update: {
          assigned_to?: string | null
          category?: string | null
          created_at?: string
          created_by?: string
          customer_id?: string
          description?: string
          id?: string
          metadata?: Json | null
          priority?: string
          resolution_notes?: string | null
          resolved_at?: string | null
          resolved_by?: string | null
          status?: string
          subject?: string
          tags?: string[] | null
          ticket_number?: string
          updated_at?: string
        }
        Relationships: []
      }
      syslog_messages: {
        Row: {
          acknowledged_at: string | null
          acknowledged_by: string | null
          app_name: string | null
          created_at: string
          created_incident_id: string | null
          customer_id: string
          device_id: string | null
          facility: number | null
          hostname: string | null
          id: string
          is_acknowledged: boolean | null
          is_security_event: boolean | null
          message: string
          msg_id: string | null
          priority: number | null
          proc_id: string | null
          received_at: string
          severity: number | null
          source_ip: unknown
          structured_data: Json | null
          tags: string[] | null
          timestamp: string | null
        }
        Insert: {
          acknowledged_at?: string | null
          acknowledged_by?: string | null
          app_name?: string | null
          created_at?: string
          created_incident_id?: string | null
          customer_id: string
          device_id?: string | null
          facility?: number | null
          hostname?: string | null
          id?: string
          is_acknowledged?: boolean | null
          is_security_event?: boolean | null
          message: string
          msg_id?: string | null
          priority?: number | null
          proc_id?: string | null
          received_at?: string
          severity?: number | null
          source_ip: unknown
          structured_data?: Json | null
          tags?: string[] | null
          timestamp?: string | null
        }
        Update: {
          acknowledged_at?: string | null
          acknowledged_by?: string | null
          app_name?: string | null
          created_at?: string
          created_incident_id?: string | null
          customer_id?: string
          device_id?: string | null
          facility?: number | null
          hostname?: string | null
          id?: string
          is_acknowledged?: boolean | null
          is_security_event?: boolean | null
          message?: string
          msg_id?: string | null
          priority?: number | null
          proc_id?: string | null
          received_at?: string
          severity?: number | null
          source_ip?: unknown
          structured_data?: Json | null
          tags?: string[] | null
          timestamp?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "syslog_messages_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "network_devices"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "syslog_messages_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "soc_engineer_network_devices"
            referencedColumns: ["id"]
          },
        ]
      }
      system_access_logs: {
        Row: {
          access_type: string
          compliance_tags: string[] | null
          created_at: string
          customer_id: string
          id: string
          resource_accessed: string | null
          success: boolean
          system_name: string
          timestamp: string
          user_id: string
        }
        Insert: {
          access_type: string
          compliance_tags?: string[] | null
          created_at?: string
          customer_id: string
          id?: string
          resource_accessed?: string | null
          success?: boolean
          system_name: string
          timestamp?: string
          user_id: string
        }
        Update: {
          access_type?: string
          compliance_tags?: string[] | null
          created_at?: string
          customer_id?: string
          id?: string
          resource_accessed?: string | null
          success?: boolean
          system_name?: string
          timestamp?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "system_access_logs_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      task_repetition_analysis: {
        Row: {
          action_type: string
          created_at: string
          customer_id: string
          first_occurrence: string
          id: string
          last_occurrence: string
          repetition_count: number
          status: string
          suggested_workflow: Json | null
          suggestion_confidence: number | null
          system_name: string
          task_context: Json | null
          task_signature: string
          updated_at: string
          user_id: string
        }
        Insert: {
          action_type: string
          created_at?: string
          customer_id: string
          first_occurrence?: string
          id?: string
          last_occurrence?: string
          repetition_count?: number
          status?: string
          suggested_workflow?: Json | null
          suggestion_confidence?: number | null
          system_name: string
          task_context?: Json | null
          task_signature: string
          updated_at?: string
          user_id: string
        }
        Update: {
          action_type?: string
          created_at?: string
          customer_id?: string
          first_occurrence?: string
          id?: string
          last_occurrence?: string
          repetition_count?: number
          status?: string
          suggested_workflow?: Json | null
          suggestion_confidence?: number | null
          system_name?: string
          task_context?: Json | null
          task_signature?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: []
      }
      testimonials: {
        Row: {
          author_name: string
          author_role: string
          company_name: string
          created_at: string
          display_order: number | null
          id: string
          is_featured: boolean
          is_published: boolean
          quote: string
          rating: number
          updated_at: string
        }
        Insert: {
          author_name: string
          author_role: string
          company_name: string
          created_at?: string
          display_order?: number | null
          id?: string
          is_featured?: boolean
          is_published?: boolean
          quote: string
          rating: number
          updated_at?: string
        }
        Update: {
          author_name?: string
          author_role?: string
          company_name?: string
          created_at?: string
          display_order?: number | null
          id?: string
          is_featured?: boolean
          is_published?: boolean
          quote?: string
          rating?: number
          updated_at?: string
        }
        Relationships: []
      }
      ticket_comments: {
        Row: {
          attachments: Json | null
          author_id: string
          author_type: string
          comment: string
          created_at: string
          id: string
          is_internal: boolean | null
          ticket_id: string
        }
        Insert: {
          attachments?: Json | null
          author_id: string
          author_type: string
          comment: string
          created_at?: string
          id?: string
          is_internal?: boolean | null
          ticket_id: string
        }
        Update: {
          attachments?: Json | null
          author_id?: string
          author_type?: string
          comment?: string
          created_at?: string
          id?: string
          is_internal?: boolean | null
          ticket_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "ticket_comments_ticket_id_fkey"
            columns: ["ticket_id"]
            isOneToOne: false
            referencedRelation: "client_tickets"
            referencedColumns: ["id"]
          },
        ]
      }
      training_courses: {
        Row: {
          cost_per_person: number | null
          course_code: string | null
          course_name: string
          course_provider: string | null
          course_type: string
          course_url: string | null
          created_at: string
          customer_id: string
          description: string | null
          duration_hours: number | null
          id: string
          is_active: boolean | null
          is_mandatory: boolean | null
          prerequisites: string | null
          updated_at: string
        }
        Insert: {
          cost_per_person?: number | null
          course_code?: string | null
          course_name: string
          course_provider?: string | null
          course_type?: string
          course_url?: string | null
          created_at?: string
          customer_id: string
          description?: string | null
          duration_hours?: number | null
          id?: string
          is_active?: boolean | null
          is_mandatory?: boolean | null
          prerequisites?: string | null
          updated_at?: string
        }
        Update: {
          cost_per_person?: number | null
          course_code?: string | null
          course_name?: string
          course_provider?: string | null
          course_type?: string
          course_url?: string | null
          created_at?: string
          customer_id?: string
          description?: string | null
          duration_hours?: number | null
          id?: string
          is_active?: boolean | null
          is_mandatory?: boolean | null
          prerequisites?: string | null
          updated_at?: string
        }
        Relationships: []
      }
      use_cases: {
        Row: {
          created_at: string
          description: string
          display_order: number | null
          frameworks: string[] | null
          icon_name: string | null
          id: string
          industry: string
          is_featured: boolean
          is_published: boolean
          key_features: string[] | null
          metrics: Json | null
          problem_statement: string
          solution_approach: string
          title: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          description: string
          display_order?: number | null
          frameworks?: string[] | null
          icon_name?: string | null
          id?: string
          industry: string
          is_featured?: boolean
          is_published?: boolean
          key_features?: string[] | null
          metrics?: Json | null
          problem_statement: string
          solution_approach: string
          title: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          description?: string
          display_order?: number | null
          frameworks?: string[] | null
          icon_name?: string | null
          id?: string
          industry?: string
          is_featured?: boolean
          is_published?: boolean
          key_features?: string[] | null
          metrics?: Json | null
          problem_statement?: string
          solution_approach?: string
          title?: string
          updated_at?: string
        }
        Relationships: []
      }
      user_profiles: {
        Row: {
          avatar_url: string | null
          created_at: string
          customer_id: string | null
          department: string | null
          full_name: string | null
          id: string
          job_title: string | null
          preferences: Json | null
          updated_at: string
          user_id: string
        }
        Insert: {
          avatar_url?: string | null
          created_at?: string
          customer_id?: string | null
          department?: string | null
          full_name?: string | null
          id?: string
          job_title?: string | null
          preferences?: Json | null
          updated_at?: string
          user_id: string
        }
        Update: {
          avatar_url?: string | null
          created_at?: string
          customer_id?: string | null
          department?: string | null
          full_name?: string | null
          id?: string
          job_title?: string | null
          preferences?: Json | null
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_profiles_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      user_roles: {
        Row: {
          assigned_at: string
          assigned_by: string | null
          id: string
          role_id: string
          user_id: string
        }
        Insert: {
          assigned_at?: string
          assigned_by?: string | null
          id?: string
          role_id: string
          user_id: string
        }
        Update: {
          assigned_at?: string
          assigned_by?: string | null
          id?: string
          role_id?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_roles_role_id_fkey"
            columns: ["role_id"]
            isOneToOne: false
            referencedRelation: "roles"
            referencedColumns: ["id"]
          },
        ]
      }
      user_sessions: {
        Row: {
          created_at: string
          customer_id: string
          id: string
          ip_address: string | null
          session_end: string | null
          session_start: string
          status: string
          user_agent: string | null
          user_id: string
        }
        Insert: {
          created_at?: string
          customer_id: string
          id?: string
          ip_address?: string | null
          session_end?: string | null
          session_start?: string
          status?: string
          user_agent?: string | null
          user_id: string
        }
        Update: {
          created_at?: string
          customer_id?: string
          id?: string
          ip_address?: string | null
          session_end?: string | null
          session_start?: string
          status?: string
          user_agent?: string | null
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_sessions_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
      vendor_contracts: {
        Row: {
          auto_renew: boolean | null
          contract_name: string
          contract_number: string
          contract_type: string
          contract_value: number | null
          created_at: string
          created_by: string
          customer_id: string
          document_url: string | null
          end_date: string | null
          id: string
          notes: string | null
          payment_schedule: string | null
          renewal_notice_days: number | null
          signed_by: string | null
          signed_date: string | null
          start_date: string
          status: string
          terms: string | null
          updated_at: string
          vendor_id: string
        }
        Insert: {
          auto_renew?: boolean | null
          contract_name: string
          contract_number: string
          contract_type: string
          contract_value?: number | null
          created_at?: string
          created_by: string
          customer_id: string
          document_url?: string | null
          end_date?: string | null
          id?: string
          notes?: string | null
          payment_schedule?: string | null
          renewal_notice_days?: number | null
          signed_by?: string | null
          signed_date?: string | null
          start_date: string
          status?: string
          terms?: string | null
          updated_at?: string
          vendor_id: string
        }
        Update: {
          auto_renew?: boolean | null
          contract_name?: string
          contract_number?: string
          contract_type?: string
          contract_value?: number | null
          created_at?: string
          created_by?: string
          customer_id?: string
          document_url?: string | null
          end_date?: string | null
          id?: string
          notes?: string | null
          payment_schedule?: string | null
          renewal_notice_days?: number | null
          signed_by?: string | null
          signed_date?: string | null
          start_date?: string
          status?: string
          terms?: string | null
          updated_at?: string
          vendor_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "vendor_contracts_vendor_id_fkey"
            columns: ["vendor_id"]
            isOneToOne: false
            referencedRelation: "vendors"
            referencedColumns: ["id"]
          },
        ]
      }
      vendor_performance: {
        Row: {
          comments: string | null
          communication_score: number | null
          created_at: string
          customer_id: string
          delivery_score: number | null
          evaluation_date: string
          evaluator_id: string
          id: string
          issues_reported: string | null
          overall_score: number | null
          pricing_score: number | null
          quality_score: number | null
          vendor_id: string
        }
        Insert: {
          comments?: string | null
          communication_score?: number | null
          created_at?: string
          customer_id: string
          delivery_score?: number | null
          evaluation_date: string
          evaluator_id: string
          id?: string
          issues_reported?: string | null
          overall_score?: number | null
          pricing_score?: number | null
          quality_score?: number | null
          vendor_id: string
        }
        Update: {
          comments?: string | null
          communication_score?: number | null
          created_at?: string
          customer_id?: string
          delivery_score?: number | null
          evaluation_date?: string
          evaluator_id?: string
          id?: string
          issues_reported?: string | null
          overall_score?: number | null
          pricing_score?: number | null
          quality_score?: number | null
          vendor_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "vendor_performance_vendor_id_fkey"
            columns: ["vendor_id"]
            isOneToOne: false
            referencedRelation: "vendors"
            referencedColumns: ["id"]
          },
        ]
      }
      vendors: {
        Row: {
          address: string | null
          certifications: Json | null
          city: string | null
          contact_email: string | null
          contact_name: string | null
          contact_phone: string | null
          contract_end_date: string | null
          contract_start_date: string | null
          country: string | null
          created_at: string
          created_by: string
          credit_limit: number | null
          current_balance: number | null
          customer_id: string
          id: string
          insurance_info: Json | null
          notes: string | null
          on_time_delivery_rate: number | null
          payment_terms: string | null
          performance_score: number | null
          postal_code: string | null
          preferred_payment_method: string | null
          quality_rating: number | null
          state: string | null
          status: string
          tags: string[] | null
          tax_id: string | null
          updated_at: string
          vendor_code: string
          vendor_name: string
          vendor_type: string
          website: string | null
        }
        Insert: {
          address?: string | null
          certifications?: Json | null
          city?: string | null
          contact_email?: string | null
          contact_name?: string | null
          contact_phone?: string | null
          contract_end_date?: string | null
          contract_start_date?: string | null
          country?: string | null
          created_at?: string
          created_by: string
          credit_limit?: number | null
          current_balance?: number | null
          customer_id: string
          id?: string
          insurance_info?: Json | null
          notes?: string | null
          on_time_delivery_rate?: number | null
          payment_terms?: string | null
          performance_score?: number | null
          postal_code?: string | null
          preferred_payment_method?: string | null
          quality_rating?: number | null
          state?: string | null
          status?: string
          tags?: string[] | null
          tax_id?: string | null
          updated_at?: string
          vendor_code: string
          vendor_name: string
          vendor_type: string
          website?: string | null
        }
        Update: {
          address?: string | null
          certifications?: Json | null
          city?: string | null
          contact_email?: string | null
          contact_name?: string | null
          contact_phone?: string | null
          contract_end_date?: string | null
          contract_start_date?: string | null
          country?: string | null
          created_at?: string
          created_by?: string
          credit_limit?: number | null
          current_balance?: number | null
          customer_id?: string
          id?: string
          insurance_info?: Json | null
          notes?: string | null
          on_time_delivery_rate?: number | null
          payment_terms?: string | null
          performance_score?: number | null
          postal_code?: string | null
          preferred_payment_method?: string | null
          quality_rating?: number | null
          state?: string | null
          status?: string
          tags?: string[] | null
          tax_id?: string | null
          updated_at?: string
          vendor_code?: string
          vendor_name?: string
          vendor_type?: string
          website?: string | null
        }
        Relationships: []
      }
      warehouses: {
        Row: {
          address: string
          capacity_sqft: number | null
          city: string | null
          contact_email: string | null
          contact_phone: string | null
          country: string | null
          created_at: string
          customer_id: string
          id: string
          manager_id: string | null
          notes: string | null
          operating_hours: string | null
          postal_code: string | null
          state: string | null
          status: string
          updated_at: string
          warehouse_code: string
          warehouse_name: string
          warehouse_type: string | null
        }
        Insert: {
          address: string
          capacity_sqft?: number | null
          city?: string | null
          contact_email?: string | null
          contact_phone?: string | null
          country?: string | null
          created_at?: string
          customer_id: string
          id?: string
          manager_id?: string | null
          notes?: string | null
          operating_hours?: string | null
          postal_code?: string | null
          state?: string | null
          status?: string
          updated_at?: string
          warehouse_code: string
          warehouse_name: string
          warehouse_type?: string | null
        }
        Update: {
          address?: string
          capacity_sqft?: number | null
          city?: string | null
          contact_email?: string | null
          contact_phone?: string | null
          country?: string | null
          created_at?: string
          customer_id?: string
          id?: string
          manager_id?: string | null
          notes?: string | null
          operating_hours?: string | null
          postal_code?: string | null
          state?: string | null
          status?: string
          updated_at?: string
          warehouse_code?: string
          warehouse_name?: string
          warehouse_type?: string | null
        }
        Relationships: []
      }
      workflow_conditions: {
        Row: {
          condition_expression: Json
          condition_type: string
          created_at: string
          false_path: Json | null
          id: string
          step_id: string
          true_path: Json | null
          workflow_id: string
        }
        Insert: {
          condition_expression: Json
          condition_type: string
          created_at?: string
          false_path?: Json | null
          id?: string
          step_id: string
          true_path?: Json | null
          workflow_id: string
        }
        Update: {
          condition_expression?: Json
          condition_type?: string
          created_at?: string
          false_path?: Json | null
          id?: string
          step_id?: string
          true_path?: Json | null
          workflow_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "workflow_conditions_workflow_id_fkey"
            columns: ["workflow_id"]
            isOneToOne: false
            referencedRelation: "workflows"
            referencedColumns: ["id"]
          },
        ]
      }
      workflow_executions: {
        Row: {
          completed_at: string | null
          compliance_tags: string[] | null
          created_at: string
          customer_id: string
          error_message: string | null
          execution_log: Json | null
          id: string
          started_at: string
          status: string
          trigger_data: Json | null
          triggered_by: string
          workflow_id: string
        }
        Insert: {
          completed_at?: string | null
          compliance_tags?: string[] | null
          created_at?: string
          customer_id: string
          error_message?: string | null
          execution_log?: Json | null
          id?: string
          started_at?: string
          status?: string
          trigger_data?: Json | null
          triggered_by: string
          workflow_id: string
        }
        Update: {
          completed_at?: string | null
          compliance_tags?: string[] | null
          created_at?: string
          customer_id?: string
          error_message?: string | null
          execution_log?: Json | null
          id?: string
          started_at?: string
          status?: string
          trigger_data?: Json | null
          triggered_by?: string
          workflow_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "workflow_executions_workflow_id_fkey"
            columns: ["workflow_id"]
            isOneToOne: false
            referencedRelation: "workflows"
            referencedColumns: ["id"]
          },
        ]
      }
      workflow_triggers: {
        Row: {
          created_at: string
          customer_id: string
          id: string
          is_enabled: boolean
          last_triggered_at: string | null
          trigger_config: Json
          trigger_type: string
          updated_at: string
          webhook_secret: string | null
          webhook_url: string | null
          workflow_id: string
        }
        Insert: {
          created_at?: string
          customer_id: string
          id?: string
          is_enabled?: boolean
          last_triggered_at?: string | null
          trigger_config?: Json
          trigger_type: string
          updated_at?: string
          webhook_secret?: string | null
          webhook_url?: string | null
          workflow_id: string
        }
        Update: {
          created_at?: string
          customer_id?: string
          id?: string
          is_enabled?: boolean
          last_triggered_at?: string | null
          trigger_config?: Json
          trigger_type?: string
          updated_at?: string
          webhook_secret?: string | null
          webhook_url?: string | null
          workflow_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "workflow_triggers_workflow_id_fkey"
            columns: ["workflow_id"]
            isOneToOne: false
            referencedRelation: "workflows"
            referencedColumns: ["id"]
          },
        ]
      }
      workflows: {
        Row: {
          avg_completion_time: number | null
          compliance_tags: string[] | null
          created_at: string
          customer_id: string
          description: string | null
          id: string
          is_active: boolean
          steps: Json | null
          successful_executions: number | null
          systems_involved: string[] | null
          tags: string[] | null
          total_executions: number | null
          updated_at: string
          version: number | null
          workflow_name: string
          workflow_type: string | null
        }
        Insert: {
          avg_completion_time?: number | null
          compliance_tags?: string[] | null
          created_at?: string
          customer_id: string
          description?: string | null
          id?: string
          is_active?: boolean
          steps?: Json | null
          successful_executions?: number | null
          systems_involved?: string[] | null
          tags?: string[] | null
          total_executions?: number | null
          updated_at?: string
          version?: number | null
          workflow_name: string
          workflow_type?: string | null
        }
        Update: {
          avg_completion_time?: number | null
          compliance_tags?: string[] | null
          created_at?: string
          customer_id?: string
          description?: string | null
          id?: string
          is_active?: boolean
          steps?: Json | null
          successful_executions?: number | null
          systems_involved?: string[] | null
          tags?: string[] | null
          total_executions?: number | null
          updated_at?: string
          version?: number | null
          workflow_name?: string
          workflow_type?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "workflows_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      change_request_dashboard: {
        Row: {
          actual_end_time: string | null
          actual_start_time: string | null
          affected_ci_ids: string[] | null
          affected_services: string[] | null
          affected_users: number | null
          approved_at: string | null
          approved_by: string[] | null
          approved_count: number | null
          assigned_to: string | null
          audit_trail: Json | null
          automation_enabled: boolean | null
          business_impact: string | null
          business_impact_score: number | null
          change_number: string | null
          change_status: Database["public"]["Enums"]["change_status"] | null
          change_type: Database["public"]["Enums"]["change_type"] | null
          completed_at: string | null
          completion_notes: string | null
          compliance_tags: string[] | null
          created_at: string | null
          customer_id: string | null
          description: string | null
          emergency_justification: string | null
          estimated_downtime_minutes: number | null
          id: string | null
          implementation_notes: string | null
          implementation_plan: string | null
          implemented_by: string | null
          justification: string | null
          ml_recommendation: string | null
          pending_approvals: number | null
          primary_ci_id: string | null
          priority: Database["public"]["Enums"]["change_priority"] | null
          requested_by: string | null
          requested_by_name: string | null
          requested_end_time: string | null
          requested_start_time: string | null
          requires_emergency_approval: boolean | null
          risk_factors: Json | null
          risk_level: Database["public"]["Enums"]["change_risk"] | null
          risk_score: number | null
          rollback_plan: string | null
          scheduled_end_time: string | null
          scheduled_start_time: string | null
          similar_changes_success_rate: number | null
          submitted_at: string | null
          success_criteria: string | null
          success_probability: number | null
          technical_impact: string | null
          testing_plan: string | null
          title: string | null
          total_approvals: number | null
          updated_at: string | null
          workflow_id: string | null
        }
        Relationships: [
          {
            foreignKeyName: "change_requests_primary_ci_id_fkey"
            columns: ["primary_ci_id"]
            isOneToOne: false
            referencedRelation: "ci_overview"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "change_requests_primary_ci_id_fkey"
            columns: ["primary_ci_id"]
            isOneToOne: false
            referencedRelation: "configuration_items"
            referencedColumns: ["id"]
          },
        ]
      }
      ci_overview: {
        Row: {
          asset_tag: string | null
          assigned_to: string | null
          attributes: Json | null
          azure_resource_id: string | null
          ci_name: string | null
          ci_status: Database["public"]["Enums"]["ci_status"] | null
          ci_subtype: string | null
          ci_type: Database["public"]["Enums"]["ci_type"] | null
          compliance_tags: string[] | null
          cost_center: string | null
          created_at: string | null
          created_by: string | null
          criticality: Database["public"]["Enums"]["ci_criticality"] | null
          customer_id: string | null
          department: string | null
          description: string | null
          eol_date: string | null
          external_id: string | null
          hostname: string | null
          id: string | null
          inbound_relationships: number | null
          integration_source: string | null
          ip_address: unknown | null
          last_audit_date: string | null
          location: string | null
          mac_address: unknown | null
          manufacturer: string | null
          model: string | null
          ninjaone_device_id: string | null
          notes: string | null
          operating_system: string | null
          outbound_relationships: number | null
          owner_user_id: string | null
          pending_changes: number | null
          purchase_date: string | null
          requires_mfa: boolean | null
          security_classification: string | null
          serial_number: string | null
          updated_at: string | null
          updated_by: string | null
          version: string | null
          warranty_expiry: string | null
        }
        Relationships: []
      }
      inventory_reorder_alerts: {
        Row: {
          alert_level: string | null
          current_quantity: number | null
          customer_id: string | null
          id: string | null
          item_name: string | null
          lead_time_days: number | null
          location: string | null
          reorder_point: number | null
          reorder_quantity: number | null
          shortage_quantity: number | null
          sku: string | null
          vendor_email: string | null
          vendor_id: string | null
          vendor_name: string | null
        }
        Relationships: [
          {
            foreignKeyName: "inventory_items_vendor_id_fkey"
            columns: ["vendor_id"]
            isOneToOne: false
            referencedRelation: "vendors"
            referencedColumns: ["id"]
          },
        ]
      }
      soc_engineer_alert_rules: {
        Row: {
          auto_remediation_workflow_id: string | null
          conditions: Json | null
          created_at: string | null
          created_by: string | null
          created_by_name: string | null
          customer_id: string | null
          description: string | null
          id: string | null
          is_enabled: boolean | null
          notification_channels: string[] | null
          rule_name: string | null
          rule_type: string | null
          severity: string | null
          updated_at: string | null
        }
        Relationships: []
      }
      soc_engineer_device_metrics: {
        Row: {
          additional_data: Json | null
          created_at: string | null
          customer_id: string | null
          device_id: string | null
          device_location: string | null
          device_name: string | null
          device_type: string | null
          id: string | null
          interface_name: string | null
          metric_name: string | null
          metric_type: string | null
          metric_unit: string | null
          metric_value: number | null
          model: string | null
          oid: string | null
          polled_at: string | null
          vendor: string | null
        }
        Relationships: [
          {
            foreignKeyName: "device_metrics_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "network_devices"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "device_metrics_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "soc_engineer_network_devices"
            referencedColumns: ["id"]
          },
        ]
      }
      soc_engineer_network_alerts: {
        Row: {
          alert_type: string | null
          assigned_to: string | null
          assigned_to_name: string | null
          auto_remediation_triggered: boolean | null
          correlation_id: string | null
          created_at: string | null
          customer_id: string | null
          description: string | null
          device_id: string | null
          device_location: string | null
          device_name: string | null
          device_type: string | null
          id: string | null
          incident_id: string | null
          notes: string | null
          remediation_action: string | null
          resolved_at: string | null
          resolved_by: string | null
          resolved_by_name: string | null
          severity: string | null
          source_data: Json | null
          status: string | null
          title: string | null
          updated_at: string | null
        }
        Relationships: [
          {
            foreignKeyName: "network_alerts_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "network_devices"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "network_alerts_device_id_fkey"
            columns: ["device_id"]
            isOneToOne: false
            referencedRelation: "soc_engineer_network_devices"
            referencedColumns: ["id"]
          },
        ]
      }
      soc_engineer_network_devices: {
        Row: {
          assigned_department: string | null
          assigned_to: string | null
          assigned_to_name: string | null
          ci_id: string | null
          ci_name: string | null
          created_at: string | null
          created_by: string | null
          customer_id: string | null
          description: string | null
          device_name: string | null
          device_type: string | null
          id: string | null
          ip_address: unknown | null
          last_poll_at: string | null
          last_syslog_at: string | null
          location: string | null
          metadata: Json | null
          model: string | null
          polling_enabled: boolean | null
          polling_interval_seconds: number | null
          snmp_community: string | null
          snmp_port: number | null
          snmp_version: string | null
          status: string | null
          syslog_enabled: boolean | null
          updated_at: string | null
          vendor: string | null
        }
        Relationships: []
      }
      soc_engineer_network_monitoring: {
        Row: {
          acknowledged_at: string | null
          acknowledged_by: string | null
          created_at: string | null
          customer_id: string | null
          device_name: string | null
          device_type: string | null
          event_identifier: string | null
          event_type: string | null
          hostname: string | null
          id: string | null
          is_acknowledged: boolean | null
          message: string | null
          monitor_type: string | null
          severity: string | null
          source_ip: unknown | null
        }
        Relationships: []
      }
    }
    Functions: {
      calculate_ci_health: {
        Args: { ci_id_param: string }
        Returns: number
      }
      can_manage_roles: {
        Args: { _user_id: string }
        Returns: boolean
      }
      create_employee_onboarding_template: {
        Args: { _created_by: string; _customer_id: string }
        Returns: string
      }
      customer_has_feature: {
        Args: { _customer_id: string; _feature_name: string }
        Returns: boolean
      }
      generate_account_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_change_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_client_ticket_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_contract_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_employee_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_expense_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_incident_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_invoice_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_lead_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_opportunity_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_po_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_project_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_quote_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_service_request_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_ticket_number: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      generate_vendor_code: {
        Args: Record<PropertyKey, never>
        Returns: string
      }
      get_integration_credential: {
        Args: { _customer_id: string; _integration_id: string }
        Returns: {
          credential_type: string
          customer_id: string
          encrypted_data: string
          expires_at: string
          id: string
          integration_id: string
        }[]
      }
      get_user_customer_id: {
        Args: { _user_id: string }
        Returns: string
      }
      has_permission: {
        Args: {
          _min_permission?: string
          _resource_name: string
          _resource_type: string
          _user_id: string
        }
        Returns: boolean
      }
      has_resource_permission: {
        Args: {
          _min_permission?: string
          _resource_name: string
          _resource_type: string
          _user_id: string
        }
        Returns: boolean
      }
      has_role: {
        Args: {
          _role: Database["public"]["Enums"]["app_role"]
          _user_id: string
        }
        Returns: boolean
      }
      validate_uuid_not_undefined: {
        Args: { uuid_value: string }
        Returns: boolean
      }
    }
    Enums: {
      app_role: "admin" | "customer"
      approval_status: "pending" | "approved" | "rejected" | "deferred"
      change_priority: "critical" | "high" | "medium" | "low"
      change_risk: "critical" | "high" | "medium" | "low"
      change_status:
        | "draft"
        | "submitted"
        | "pending_approval"
        | "approved"
        | "rejected"
        | "scheduled"
        | "in_progress"
        | "implemented"
        | "completed"
        | "failed"
        | "rolled_back"
        | "cancelled"
      change_type: "standard" | "normal" | "emergency" | "routine"
      ci_criticality: "critical" | "high" | "medium" | "low"
      ci_status:
        | "active"
        | "inactive"
        | "maintenance"
        | "retired"
        | "planned"
        | "under_review"
      ci_type:
        | "hardware"
        | "software"
        | "network_device"
        | "server"
        | "workstation"
        | "mobile_device"
        | "application"
        | "database"
        | "service"
        | "virtual_machine"
        | "cloud_resource"
        | "security_device"
      relationship_type:
        | "depends_on"
        | "uses"
        | "hosts"
        | "runs_on"
        | "connects_to"
        | "managed_by"
        | "backs_up"
        | "monitors"
        | "protects"
        | "integrates_with"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      app_role: ["admin", "customer"],
      approval_status: ["pending", "approved", "rejected", "deferred"],
      change_priority: ["critical", "high", "medium", "low"],
      change_risk: ["critical", "high", "medium", "low"],
      change_status: [
        "draft",
        "submitted",
        "pending_approval",
        "approved",
        "rejected",
        "scheduled",
        "in_progress",
        "implemented",
        "completed",
        "failed",
        "rolled_back",
        "cancelled",
      ],
      change_type: ["standard", "normal", "emergency", "routine"],
      ci_criticality: ["critical", "high", "medium", "low"],
      ci_status: [
        "active",
        "inactive",
        "maintenance",
        "retired",
        "planned",
        "under_review",
      ],
      ci_type: [
        "hardware",
        "software",
        "network_device",
        "server",
        "workstation",
        "mobile_device",
        "application",
        "database",
        "service",
        "virtual_machine",
        "cloud_resource",
        "security_device",
      ],
      relationship_type: [
        "depends_on",
        "uses",
        "hosts",
        "runs_on",
        "connects_to",
        "managed_by",
        "backs_up",
        "monitors",
        "protects",
        "integrates_with",
      ],
    },
  },
} as const
