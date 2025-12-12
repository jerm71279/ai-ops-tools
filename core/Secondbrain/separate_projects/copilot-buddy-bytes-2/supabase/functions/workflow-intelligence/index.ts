import "https://deno.land/x/xhr@0.1.0/mod.ts";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.3';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { query, type = 'analyze', timeframe = '7d' } = await req.json();
    
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const lovableApiKey = Deno.env.get('LOVABLE_API_KEY');

    if (!lovableApiKey) {
      throw new Error('LOVABLE_API_KEY not configured');
    }

    const supabase = createClient(supabaseUrl, supabaseKey);

    // Get authorization header
    const authHeader = req.headers.get('authorization');
    if (!authHeader) {
      throw new Error('No authorization header');
    }

    // Get user from token
    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error: userError } = await supabase.auth.getUser(token);
    
    if (userError || !user) {
      throw new Error('Unauthorized');
    }

    // Get user's customer_id
    const { data: profile } = await supabase
      .from('user_profiles')
      .select('customer_id')
      .eq('user_id', user.id)
      .single();

    if (!profile?.customer_id) {
      throw new Error('No customer associated with user');
    }

    console.log(`Processing ${type} query for customer ${profile.customer_id}`);

    // Calculate timeframe
    const daysAgo = parseInt(timeframe.replace('d', ''));
    const sinceDate = new Date();
    sinceDate.setDate(sinceDate.getDate() - daysAgo);

    // Gather context data based on query type
    let contextData: any = {};

    if (type === 'analyze' || type === 'workflows') {
      // Get recent workflow executions
      const { data: workflows } = await supabase
        .from('workflow_executions')
        .select(`
          id,
          workflow_id,
          status,
          started_at,
          completed_at,
          error_message,
          input_data,
          output_data,
          workflows (
            name,
            description,
            compliance_tags
          )
        `)
        .eq('customer_id', profile.customer_id)
        .gte('started_at', sinceDate.toISOString())
        .order('started_at', { ascending: false })
        .limit(50);

      contextData.workflows = workflows || [];
    }

    if (type === 'analyze' || type === 'compliance') {
      // Get compliance-related audit logs
      const { data: auditLogs } = await supabase
        .from('audit_logs')
        .select('*')
        .eq('customer_id', profile.customer_id)
        .gte('timestamp', sinceDate.toISOString())
        .not('compliance_tags', 'is', null)
        .order('timestamp', { ascending: false })
        .limit(100);

      contextData.auditLogs = auditLogs || [];
    }

    if (type === 'analyze' || type === 'changes') {
      // Get change requests
      const { data: changes } = await supabase
        .from('change_requests')
        .select('*')
        .eq('customer_id', profile.customer_id)
        .gte('created_at', sinceDate.toISOString())
        .order('created_at', { ascending: false })
        .limit(30);

      contextData.changes = changes || [];
    }

    if (type === 'analyze' || type === 'anomalies') {
      // Get anomaly detections
      const { data: anomalies } = await supabase
        .from('anomaly_detections')
        .select('*')
        .eq('customer_id', profile.customer_id)
        .gte('created_at', sinceDate.toISOString())
        .order('created_at', { ascending: false })
        .limit(20);

      contextData.anomalies = anomalies || [];
    }

    // Build system prompt with context
    const systemPrompt = `You are an intelligent workflow analysis assistant for OberaConnect, a compliance-aware business automation platform.

Your role is to analyze operational data and provide insights about:
- Business process execution and outcomes
- Compliance alignment with frameworks (ISO, SOC2, HIPAA, etc.)
- Workflow anomalies and optimization opportunities
- Change management impact
- Executive-level summaries

Context data for the last ${daysAgo} days:
${JSON.stringify(contextData, null, 2)}

When analyzing:
1. Link findings to specific compliance clauses when relevant
2. Identify patterns, anomalies, and trends
3. Provide actionable recommendations
4. Use clear, concise language appropriate for the audience
5. Cite specific workflow IDs, audit log entries, or change request numbers

Format your response in markdown with clear sections.`;

    // Prepare AI request
    const aiPayload: any = {
      model: 'google/gemini-2.5-flash',
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: query }
      ],
      stream: true
    };

    // Add tool calling for structured outputs
    if (type === 'suggest' || type === 'classify') {
      aiPayload.tools = [
        {
          type: 'function',
          function: {
            name: 'structured_analysis',
            description: 'Return structured analysis results',
            parameters: {
              type: 'object',
              properties: {
                summary: { type: 'string', description: 'Executive summary' },
                findings: {
                  type: 'array',
                  items: {
                    type: 'object',
                    properties: {
                      title: { type: 'string' },
                      severity: { type: 'string', enum: ['low', 'medium', 'high', 'critical'] },
                      clause_reference: { type: 'string' },
                      recommendation: { type: 'string' }
                    },
                    required: ['title', 'severity']
                  }
                },
                metrics: {
                  type: 'object',
                  properties: {
                    success_rate: { type: 'number' },
                    total_workflows: { type: 'number' },
                    anomalies_detected: { type: 'number' }
                  }
                }
              },
              required: ['summary', 'findings']
            }
          }
        }
      ];
      aiPayload.tool_choice = { type: 'function', function: { name: 'structured_analysis' } };
    }

    console.log('Calling Lovable AI Gateway...');

    // Call Lovable AI
    const aiResponse = await fetch('https://ai.gateway.lovable.dev/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${lovableApiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(aiPayload),
    });

    if (!aiResponse.ok) {
      const errorText = await aiResponse.text();
      console.error('AI Gateway error:', aiResponse.status, errorText);
      
      if (aiResponse.status === 429) {
        return new Response(
          JSON.stringify({ error: 'Rate limit exceeded. Please try again later.' }),
          { status: 429, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
      
      throw new Error(`AI Gateway error: ${aiResponse.status}`);
    }

    // Log the query for learning
    await supabase
      .from('ai_interactions')
      .insert({
        customer_id: profile.customer_id,
        user_id: user.id,
        conversation_id: crypto.randomUUID(),
        interaction_type: `workflow_intelligence_${type}`,
        user_query: query,
        ai_response: '', // Will be updated after streaming
        compliance_tags: ['workflow_intelligence'],
        metadata: { timeframe, context_size: JSON.stringify(contextData).length }
      });

    // Return streaming response
    return new Response(aiResponse.body, {
      headers: {
        ...corsHeaders,
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });

  } catch (error) {
    console.error('Error in workflow-intelligence:', error);
    return new Response(
      JSON.stringify({ 
        error: error instanceof Error ? error.message : 'Unknown error',
        details: error instanceof Error ? error.stack : undefined
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
});
