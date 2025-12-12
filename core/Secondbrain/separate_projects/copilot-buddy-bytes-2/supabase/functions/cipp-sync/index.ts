import "https://deno.land/x/xhr@0.1.0/mod.ts";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      {
        auth: {
          persistSession: false,
        },
      }
    );

    const authHeader = req.headers.get('Authorization')!;
    const token = authHeader.replace('Bearer ', '');
    const { data: { user } } = await supabaseClient.auth.getUser(token);

    if (!user) {
      throw new Error('Unauthorized');
    }

    const { action, tenantId, customerId } = await req.json();

    // Get CIPP credentials from secrets
    const cippUrl = Deno.env.get('CIPP_URL');
    const cippApiKey = Deno.env.get('CIPP_API_KEY');

    if (!cippUrl || !cippApiKey) {
      throw new Error('CIPP credentials not configured');
    }

    let result;

    switch (action) {
      case 'sync_tenants': {
        console.log('Syncing CIPP tenants...');
        
        // Call CIPP API to get all tenants
        const tenantsResponse = await fetch(`${cippUrl}/api/ListTenants`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'X-API-KEY': cippApiKey,
          },
        });

        if (!tenantsResponse.ok) {
          throw new Error(`CIPP API error: ${tenantsResponse.statusText}`);
        }

        const tenants = await tenantsResponse.json();
        console.log(`Found ${tenants.length} tenants from CIPP`);

        // Get customer_id from user profile
        const { data: profile } = await supabaseClient
          .from('user_profiles')
          .select('customer_id')
          .eq('user_id', user.id)
          .single();

        if (!profile?.customer_id) {
          throw new Error('Customer ID not found for user');
        }

        // Sync tenants to database
        const syncResults = [];
        for (const tenant of tenants) {
          const { data, error } = await supabaseClient
            .from('cipp_tenants')
            .upsert({
              customer_id: profile.customer_id,
              tenant_id: tenant.customerId || tenant.tenantId,
              tenant_name: tenant.displayName || tenant.defaultDomainName,
              default_domain_name: tenant.defaultDomainName,
              display_name: tenant.displayName,
              status: 'active',
              last_sync_at: new Date().toISOString(),
              sync_status: 'success',
              metadata: tenant,
            }, {
              onConflict: 'customer_id,tenant_id',
            });

          if (error) {
            console.error('Error syncing tenant:', error);
            syncResults.push({ tenant: tenant.displayName, status: 'error', error: error.message });
          } else {
            syncResults.push({ tenant: tenant.displayName, status: 'success' });
          }
        }

        result = {
          success: true,
          message: `Synced ${syncResults.filter(r => r.status === 'success').length} tenants`,
          results: syncResults,
        };
        break;
      }

      case 'get_tenant_health': {
        console.log(`Getting health for tenant: ${tenantId}`);
        
        const healthResponse = await fetch(`${cippUrl}/api/ListGraphRequest`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-KEY': cippApiKey,
          },
          body: JSON.stringify({
            TenantFilter: tenantId,
            Endpoint: 'reports/getSecureScore',
          }),
        });

        if (!healthResponse.ok) {
          throw new Error(`CIPP API error: ${healthResponse.statusText}`);
        }

        const healthData = await healthResponse.json();

        // Store health data
        const { data: tenant } = await supabaseClient
          .from('cipp_tenants')
          .select('id')
          .eq('tenant_id', tenantId)
          .eq('customer_id', customerId)
          .single();

        if (tenant) {
          await supabaseClient
            .from('cipp_tenant_health')
            .insert({
              tenant_id: tenant.id,
              security_score: healthData.currentScore,
              health_score: Math.round((healthData.currentScore / healthData.maxScore) * 100),
              recommendations: healthData.controlScores || [],
              last_checked_at: new Date().toISOString(),
            });
        }

        result = {
          success: true,
          data: healthData,
        };
        break;
      }

      case 'apply_baseline': {
        const { baselineId, targetTenantIds } = await req.json();
        
        console.log(`Applying baseline ${baselineId} to ${targetTenantIds.length} tenants`);

        // Get baseline settings
        const { data: baseline } = await supabaseClient
          .from('cipp_security_baselines')
          .select('*')
          .eq('id', baselineId)
          .single();

        if (!baseline) {
          throw new Error('Baseline not found');
        }

        const applyResults = [];
        for (const targetTenantId of targetTenantIds) {
          const applyResponse = await fetch(`${cippUrl}/api/AddStandardsDeploy`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-API-KEY': cippApiKey,
            },
            body: JSON.stringify({
              TenantFilter: targetTenantId,
              Standards: baseline.settings,
            }),
          });

          if (applyResponse.ok) {
            applyResults.push({ tenant: targetTenantId, status: 'success' });
          } else {
            applyResults.push({ tenant: targetTenantId, status: 'error' });
          }
        }

        result = {
          success: true,
          message: `Applied baseline to ${applyResults.filter(r => r.status === 'success').length} tenants`,
          results: applyResults,
        };
        break;
      }

      default:
        throw new Error(`Unknown action: ${action}`);
    }

    // Log audit trail
    await supabaseClient
      .from('cipp_audit_logs')
      .insert({
        customer_id: customerId,
        action_type: action,
        action_description: `CIPP ${action} executed`,
        performed_by: user.id,
        result: 'success',
        details: result,
      });

    return new Response(JSON.stringify(result), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  } catch (error) {
    console.error('Error in cipp-sync function:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    return new Response(JSON.stringify({ 
      success: false, 
      error: errorMessage 
    }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
    });
  }
});
