import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.58.0';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface TestResult {
  component: string;
  success: boolean;
  records_created: number;
  errors: string[];
  duration_ms: number;
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    console.log('Starting comprehensive test data generation...');
    
    const results: TestResult[] = [];
    const startTime = Date.now();

    // Get test customer
    const { data: customers } = await supabase
      .from('customers')
      .select('id')
      .limit(1);
    
    const customerId = customers?.[0]?.id || '710092dc-c33c-4f8e-8c65-11fc62982c96';
    const testUserId = '00000000-0000-0000-0000-000000000001';

    // 1. Knowledge Base Component
    const kbStart = Date.now();
    const kbErrors: string[] = [];
    let kbCount = 0;

    try {
      // Create categories
      const { data: categories, error: catError } = await supabase
        .from('knowledge_categories')
        .insert([
          { name: 'Security Policies', description: 'Security and compliance policies', icon_name: 'Shield' },
          { name: 'IT Operations', description: 'IT operational procedures', icon_name: 'Server' },
          { name: 'HR Procedures', description: 'Human resources guidelines', icon_name: 'Users' },
          { name: 'Troubleshooting', description: 'Technical troubleshooting guides', icon_name: 'Tool' }
        ])
        .select();

      if (catError) throw catError;
      kbCount += categories?.length || 0;

      // Create articles
      const { data: articles, error: artError } = await supabase
        .from('knowledge_articles')
        .insert([
          {
            customer_id: customerId,
            category_id: categories?.[0]?.id,
            title: 'Password Policy Requirements',
            content: 'All passwords must be at least 12 characters and include uppercase, lowercase, numbers, and special characters.',
            article_type: 'sop',
            status: 'published',
            created_by: testUserId,
            tags: ['security', 'authentication', 'policy']
          },
          {
            customer_id: customerId,
            category_id: categories?.[1]?.id,
            title: 'Server Backup Procedures',
            content: 'Daily automated backups run at 2 AM. Manual backups can be triggered from the admin panel.',
            article_type: 'sop',
            status: 'published',
            created_by: testUserId,
            tags: ['backup', 'operations', 'maintenance']
          },
          {
            customer_id: customerId,
            category_id: categories?.[2]?.id,
            title: 'Employee Onboarding Checklist',
            content: 'Complete background check, setup email, assign equipment, schedule training sessions.',
            article_type: 'guide',
            status: 'published',
            created_by: testUserId,
            tags: ['onboarding', 'hr', 'checklist']
          }
        ])
        .select();

      if (artError) throw artError;
      kbCount += articles?.length || 0;

    } catch (err) {
      kbErrors.push(err instanceof Error ? err.message : String(err));
    }

    results.push({
      component: 'Knowledge Base',
      success: kbErrors.length === 0,
      records_created: kbCount,
      errors: kbErrors,
      duration_ms: Date.now() - kbStart
    });

    // 2. AI Interactions Component
    const aiStart = Date.now();
    const aiErrors: string[] = [];
    let aiCount = 0;

    try {
      const conversationId = crypto.randomUUID();
      
      const { data: interactions, error: aiError } = await supabase
        .from('ai_interactions')
        .insert([
          {
            customer_id: customerId,
            user_id: testUserId,
            conversation_id: conversationId,
            interaction_type: 'query',
            user_query: 'What is our password policy?',
            ai_response: 'All passwords must be at least 12 characters long and include a mix of uppercase, lowercase, numbers, and special characters.',
            confidence_score: 0.95,
            insight_generated: true,
            was_helpful: true,
            feedback_rating: 5,
            compliance_tags: ['security', 'policy']
          },
          {
            customer_id: customerId,
            user_id: testUserId,
            conversation_id: conversationId,
            interaction_type: 'query',
            user_query: 'How do I request time off?',
            ai_response: 'Submit a time-off request through the HR portal at least 2 weeks in advance.',
            confidence_score: 0.88,
            insight_generated: false,
            was_helpful: true,
            feedback_rating: 4,
            compliance_tags: ['hr', 'policy']
          }
        ])
        .select();

      if (aiError) throw aiError;
      aiCount = interactions?.length || 0;

    } catch (err) {
      aiErrors.push(err instanceof Error ? err.message : String(err));
    }

    results.push({
      component: 'AI Interactions',
      success: aiErrors.length === 0,
      records_created: aiCount,
      errors: aiErrors,
      duration_ms: Date.now() - aiStart
    });

    // 3. Audit Logs Component
    const auditStart = Date.now();
    const auditErrors: string[] = [];
    let auditCount = 0;

    try {
      const { data: logs, error: auditError } = await supabase
        .from('audit_logs')
        .insert([
          {
            customer_id: customerId,
            user_id: testUserId,
            system_name: 'user_management',
            action_type: 'user_created',
            action_details: { username: 'john.doe', department: 'IT' },
            compliance_tags: ['access_control', 'user_management']
          },
          {
            customer_id: customerId,
            user_id: testUserId,
            system_name: 'evidence_management',
            action_type: 'file_uploaded',
            action_details: { file_name: 'security_policy.pdf', size: 524288 },
            compliance_tags: ['compliance', 'evidence']
          },
          {
            customer_id: customerId,
            user_id: testUserId,
            system_name: 'workflow_automation',
            action_type: 'workflow_executed',
            action_details: { workflow_name: 'User Access Provisioning', status: 'completed' },
            compliance_tags: ['automation', 'access_control']
          }
        ])
        .select();

      if (auditError) throw auditError;
      auditCount = logs?.length || 0;

    } catch (err) {
      auditErrors.push(err instanceof Error ? err.message : String(err));
    }

    results.push({
      component: 'Audit Logs',
      success: auditErrors.length === 0,
      records_created: auditCount,
      errors: auditErrors,
      duration_ms: Date.now() - auditStart
    });

    // 4. Behavioral Events Component
    const behaviorStart = Date.now();
    const behaviorErrors: string[] = [];
    let behaviorCount = 0;

    try {
      const { data: events, error: behaviorError } = await supabase
        .from('behavioral_events')
        .insert([
          {
            customer_id: customerId,
            user_id: testUserId,
            system_name: 'portal',
            event_type: 'page_view',
            action: 'viewed_compliance_dashboard',
            duration_ms: 45000,
            context: { page: '/compliance', browser: 'Chrome' },
            compliance_tags: ['usage', 'compliance']
          },
          {
            customer_id: customerId,
            user_id: testUserId,
            system_name: 'knowledge_base',
            event_type: 'search',
            action: 'searched_articles',
            duration_ms: 2500,
            context: { query: 'password policy', results: 5 },
            compliance_tags: ['knowledge', 'search']
          }
        ])
        .select();

      if (behaviorError) throw behaviorError;
      behaviorCount = events?.length || 0;

    } catch (err) {
      behaviorErrors.push(err instanceof Error ? err.message : String(err));
    }

    results.push({
      component: 'Behavioral Events',
      success: behaviorErrors.length === 0,
      records_created: behaviorCount,
      errors: behaviorErrors,
      duration_ms: Date.now() - behaviorStart
    });

    // 5. Anomaly Detection Component
    const anomalyStart = Date.now();
    const anomalyErrors: string[] = [];
    let anomalyCount = 0;

    try {
      const { data: anomalies, error: anomalyError } = await supabase
        .from('anomaly_detections')
        .insert([
          {
            customer_id: customerId,
            affected_user_id: testUserId,
            anomaly_type: 'unusual_access_pattern',
            severity: 'medium',
            system_name: 'access_control',
            description: 'User accessed system outside normal business hours',
            detection_method: 'ml_algorithm',
            confidence_score: 0.82,
            status: 'investigating',
            compliance_tags: ['security', 'access_control']
          },
          {
            customer_id: customerId,
            anomaly_type: 'failed_login_attempts',
            severity: 'high',
            system_name: 'authentication',
            description: 'Multiple failed login attempts detected from IP 192.168.1.100',
            detection_method: 'threshold_exceeded',
            confidence_score: 0.95,
            status: 'new',
            compliance_tags: ['security', 'authentication']
          }
        ])
        .select();

      if (anomalyError) throw anomalyError;
      anomalyCount = anomalies?.length || 0;

    } catch (err) {
      anomalyErrors.push(err instanceof Error ? err.message : String(err));
    }

    results.push({
      component: 'Anomaly Detection',
      success: anomalyErrors.length === 0,
      records_created: anomalyCount,
      errors: anomalyErrors,
      duration_ms: Date.now() - anomalyStart
    });

    // 6. MCP Servers Component
    const mcpStart = Date.now();
    const mcpErrors: string[] = [];
    let mcpCount = 0;

    try {
      const { data: servers, error: serverError } = await supabase
        .from('mcp_servers')
        .insert([
          {
            customer_id: customerId,
            server_name: 'Compliance Automation Server',
            server_type: 'compliance',
            description: 'MCP server for automated compliance checks',
            status: 'active',
            capabilities: ['evidence_validation', 'report_generation', 'gap_analysis'],
            last_health_check: new Date().toISOString()
          },
          {
            customer_id: customerId,
            server_name: 'IT Operations Server',
            server_type: 'operations',
            description: 'MCP server for IT operations automation',
            status: 'active',
            capabilities: ['backup_management', 'monitoring', 'incident_response'],
            last_health_check: new Date().toISOString()
          }
        ])
        .select();

      if (serverError) throw serverError;
      mcpCount = servers?.length || 0;

      // Create tools for servers
      if (servers && servers.length > 0) {
        const { data: tools, error: toolError } = await supabase
          .from('mcp_tools')
          .insert([
            {
              server_id: servers[0].id,
              tool_name: 'validate_evidence',
              description: 'Validates compliance evidence files',
              input_schema: { type: 'object', properties: { file_id: { type: 'string' } } },
              execution_count: 15
            },
            {
              server_id: servers[1].id,
              tool_name: 'check_backup_status',
              description: 'Checks the status of system backups',
              input_schema: { type: 'object', properties: { system_id: { type: 'string' } } },
              execution_count: 42
            }
          ])
          .select();

        if (!toolError) mcpCount += tools?.length || 0;
      }

    } catch (err) {
      mcpErrors.push(err instanceof Error ? err.message : String(err));
    }

    results.push({
      component: 'MCP Servers',
      success: mcpErrors.length === 0,
      records_created: mcpCount,
      errors: mcpErrors,
      duration_ms: Date.now() - mcpStart
    });

    // 7. ML Insights Component
    const mlStart = Date.now();
    const mlErrors: string[] = [];
    let mlCount = 0;

    try {
      const { data: insights, error: mlError } = await supabase
        .from('ml_insights')
        .insert([
          {
            customer_id: customerId,
            insight_type: 'compliance_risk',
            title: 'Increasing Gap in Access Control Documentation',
            description: 'ML model detected 15% increase in undocumented access control changes',
            confidence_score: 0.87,
            priority: 'high',
            status: 'pending_review',
            recommended_actions: ['Schedule access control audit', 'Update documentation procedures']
          },
          {
            customer_id: customerId,
            insight_type: 'workflow_optimization',
            title: 'Backup Workflow Efficiency Improvement',
            description: 'ML analysis suggests backup workflow could be 30% faster with parallel processing',
            confidence_score: 0.92,
            priority: 'medium',
            status: 'pending_review',
            recommended_actions: ['Enable parallel backup processing', 'Increase resource allocation']
          }
        ])
        .select();

      if (mlError) throw mlError;
      mlCount = insights?.length || 0;

    } catch (err) {
      mlErrors.push(err instanceof Error ? err.message : String(err));
    }

    results.push({
      component: 'ML Insights',
      success: mlErrors.length === 0,
      records_created: mlCount,
      errors: mlErrors,
      duration_ms: Date.now() - mlStart
    });

    // 8. Client Onboarding Component
    const onboardingStart = Date.now();
    const onboardingErrors: string[] = [];
    let onboardingCount = 0;

    try {
      // Get a template
      const { data: templates } = await supabase
        .from('onboarding_templates')
        .select('id')
        .limit(1);

      if (templates && templates.length > 0) {
        const { data: onboardings, error: onboardingError } = await supabase
          .from('client_onboardings')
          .insert([
            {
              customer_id: customerId,
              template_id: templates[0].id,
              client_name: 'Acme Corporation',
              client_contact_email: 'contact@acme.com',
              client_contact_name: 'Jane Smith',
              status: 'in_progress',
              start_date: new Date().toISOString().split('T')[0],
              created_by: testUserId,
              completion_percentage: 35
            },
            {
              customer_id: customerId,
              template_id: templates[0].id,
              client_name: 'TechStart Inc',
              client_contact_email: 'admin@techstart.io',
              client_contact_name: 'Bob Johnson',
              status: 'not_started',
              created_by: testUserId,
              completion_percentage: 0
            }
          ])
          .select();

        if (onboardingError) throw onboardingError;
        onboardingCount = onboardings?.length || 0;
      }

    } catch (err) {
      onboardingErrors.push(err instanceof Error ? err.message : String(err));
    }

    results.push({
      component: 'Client Onboarding',
      success: onboardingErrors.length === 0,
      records_created: onboardingCount,
      errors: onboardingErrors,
      duration_ms: Date.now() - onboardingStart
    });

    const totalDuration = Date.now() - startTime;
    const totalRecords = results.reduce((sum, r) => sum + r.records_created, 0);
    const totalErrors = results.reduce((sum, r) => sum + r.errors.length, 0);

    console.log(`Test data generation complete: ${totalRecords} records in ${totalDuration}ms`);

    return new Response(
      JSON.stringify({
        success: totalErrors === 0,
        summary: {
          total_components: results.length,
          total_records_created: totalRecords,
          total_errors: totalErrors,
          total_duration_ms: totalDuration
        },
        results
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error) {
    console.error('Error in comprehensive-test-data-generator:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    return new Response(
      JSON.stringify({ error: errorMessage }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    );
  }
});
