import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface TicketCreateRequest {
  change_request_id: string;
  action: 'create' | 'sync';
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      throw new Error('Missing authorization header');
    }

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      { global: { headers: { Authorization: authHeader } } }
    );

    const { data: { user }, error: userError } = await supabase.auth.getUser();
    if (userError || !user) {
      throw new Error('Unauthorized');
    }

    const { change_request_id, action } = await req.json() as TicketCreateRequest;

    // Get change request details
    const { data: changeRequest, error: crError } = await supabase
      .from('change_requests')
      .select('*')
      .eq('id', change_request_id)
      .single();

    if (crError) throw crError;

    // Check for NinjaOne credentials
    const clientId = Deno.env.get('NINJAONE_CLIENT_ID');
    const clientSecret = Deno.env.get('NINJAONE_CLIENT_SECRET');
    const instance = Deno.env.get('NINJAONE_INSTANCE') || 'app';

    if (!clientId || !clientSecret) {
      console.log('NinjaOne credentials not configured');
      return new Response(
        JSON.stringify({
          success: false,
          error: 'NinjaOne credentials not configured. Please add NINJAONE_CLIENT_ID and NINJAONE_CLIENT_SECRET.',
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    if (action === 'create') {
      // Get OAuth token
      const tokenResponse = await fetch(`https://${instance}.ninjarmm.com/oauth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          grant_type: 'client_credentials',
          client_id: clientId,
          client_secret: clientSecret,
          scope: 'monitoring'
        })
      });

      if (!tokenResponse.ok) {
        throw new Error(`NinjaOne authentication failed: ${tokenResponse.statusText}`);
      }

      const { access_token } = await tokenResponse.json();

      // Get affected CIs for context
      const affectedCIs = [];
      if (changeRequest.affected_ci_ids && changeRequest.affected_ci_ids.length > 0) {
        const { data: cis } = await supabase
          .from('configuration_items')
          .select('ci_name, ci_type, hostname')
          .in('id', changeRequest.affected_ci_ids);
        
        if (cis) {
          affectedCIs.push(...cis);
        }
      }

      // Create ticket description
      const description = `
CHANGE REQUEST: ${changeRequest.change_number}
Type: ${changeRequest.change_type}
Priority: ${changeRequest.priority}
Risk Level: ${changeRequest.risk_level || 'Not assessed'}

DESCRIPTION:
${changeRequest.description}

JUSTIFICATION:
${changeRequest.justification}

AFFECTED SYSTEMS:
${affectedCIs.map(ci => `- ${ci.ci_name} (${ci.ci_type}${ci.hostname ? ', ' + ci.hostname : ''})`).join('\n') || 'None specified'}

IMPLEMENTATION PLAN:
${changeRequest.implementation_plan}

ROLLBACK PLAN:
${changeRequest.rollback_plan}

${changeRequest.testing_plan ? `TESTING PLAN:\n${changeRequest.testing_plan}\n` : ''}
${changeRequest.business_impact ? `BUSINESS IMPACT:\n${changeRequest.business_impact}\n` : ''}
${changeRequest.technical_impact ? `TECHNICAL IMPACT:\n${changeRequest.technical_impact}` : ''}
      `.trim();

      // Determine NinjaOne priority
      const ninjaonePriority = changeRequest.priority === 'critical' ? 'CRITICAL' :
                               changeRequest.priority === 'high' ? 'HIGH' :
                               changeRequest.priority === 'medium' ? 'MEDIUM' : 'LOW';

      // Create ticket in NinjaOne
      const ticketPayload = {
        subject: `[CHANGE] ${changeRequest.title}`,
        description: description,
        priority: ninjaonePriority,
        status: 'OPEN',
        type: 'PROBLEM',
        tags: ['change-management', changeRequest.change_type, `risk-${changeRequest.risk_level || 'unknown'}`],
      };

      console.log('Creating NinjaOne ticket:', ticketPayload);

      const ticketResponse = await fetch(`https://${instance}.ninjarmm.com/api/v2/ticketing/ticket`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(ticketPayload),
      });

      if (!ticketResponse.ok) {
        const errorText = await ticketResponse.text();
        console.error('NinjaOne ticket creation failed:', errorText);
        throw new Error(`Failed to create NinjaOne ticket: ${ticketResponse.statusText}`);
      }

      const ticket = await ticketResponse.json();
      console.log('NinjaOne ticket created:', ticket);

      // Update change request with ticket info
      const ticketUrl = `https://${instance}.ninjarmm.com/v2/ticketing/ticket/${ticket.id}`;
      
      const { error: updateError } = await supabase
        .from('change_requests')
        .update({
          ninjaone_ticket_id: ticket.id?.toString(),
          ninjaone_ticket_number: ticket.number?.toString(),
          ninjaone_ticket_status: ticket.status,
          ninjaone_ticket_url: ticketUrl,
          ninjaone_ticket_synced_at: new Date().toISOString(),
        })
        .eq('id', change_request_id);

      if (updateError) throw updateError;

      // Log the action
      await supabase
        .from('audit_logs')
        .insert({
          customer_id: changeRequest.customer_id,
          user_id: user.id,
          system_name: 'change_management',
          action_type: 'ninjaone_ticket_created',
          action_details: {
            change_request_id,
            change_number: changeRequest.change_number,
            ticket_id: ticket.id,
            ticket_number: ticket.number,
          },
          compliance_tags: ['change_management', 'ninjaone_integration'],
        });

      return new Response(
        JSON.stringify({
          success: true,
          ticket: {
            id: ticket.id,
            number: ticket.number,
            status: ticket.status,
            url: ticketUrl,
          },
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );

    } else if (action === 'sync') {
      // Sync ticket status from NinjaOne
      if (!changeRequest.ninjaone_ticket_id) {
        throw new Error('No NinjaOne ticket linked to this change request');
      }

      const tokenResponse = await fetch(`https://${instance}.ninjarmm.com/oauth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          grant_type: 'client_credentials',
          client_id: clientId,
          client_secret: clientSecret,
          scope: 'monitoring'
        })
      });

      if (!tokenResponse.ok) {
        throw new Error(`NinjaOne authentication failed: ${tokenResponse.statusText}`);
      }

      const { access_token } = await tokenResponse.json();

      // Get ticket status
      const ticketResponse = await fetch(
        `https://${instance}.ninjarmm.com/api/v2/ticketing/ticket/${changeRequest.ninjaone_ticket_id}`,
        {
          headers: {
            'Authorization': `Bearer ${access_token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!ticketResponse.ok) {
        throw new Error(`Failed to fetch ticket: ${ticketResponse.statusText}`);
      }

      const ticket = await ticketResponse.json();

      // Update change request with latest ticket status
      const { error: updateError } = await supabase
        .from('change_requests')
        .update({
          ninjaone_ticket_status: ticket.status,
          ninjaone_ticket_synced_at: new Date().toISOString(),
        })
        .eq('id', change_request_id);

      if (updateError) throw updateError;

      return new Response(
        JSON.stringify({
          success: true,
          ticket: {
            id: ticket.id,
            number: ticket.number,
            status: ticket.status,
          },
        }),
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    throw new Error('Invalid action');

  } catch (error) {
    console.error('NinjaOne ticket error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    return new Response(
      JSON.stringify({
        success: false,
        error: errorMessage,
      }),
      { 
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    );
  }
});
