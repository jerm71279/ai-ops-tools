import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.39.3";

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
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    );

    const { analysisType, resourceId, customerId } = await req.json();
    console.log('Generating insights for:', { analysisType, resourceId, customerId });

    let analysisData: any = {};
    let prompt = "";

    // Gather data based on analysis type
    switch (analysisType) {
      case 'change_risk':
        const { data: changes } = await supabaseClient
          .from('change_requests')
          .select('*')
          .eq('customer_id', customerId)
          .order('created_at', { ascending: false })
          .limit(50);
        
        analysisData = { recentChanges: changes };
        prompt = `Analyze these change requests and identify patterns, risks, and optimization opportunities. 
        Consider: success rates, common failure points, timing patterns, affected systems.
        Recent changes: ${JSON.stringify(changes?.slice(0, 5))}`;
        break;

      case 'cmdb_health':
        const { data: cis } = await supabaseClient
          .from('configuration_items')
          .select('*')
          .eq('customer_id', customerId)
          .limit(100);
        
        analysisData = { configItems: cis };
        prompt = `Analyze this CMDB data for health issues, compliance risks, and optimization opportunities.
        Look for: outdated items, missing relationships, security risks, warranty expirations.
        Configuration items sample: ${JSON.stringify(cis?.slice(0, 10))}`;
        break;

      case 'anomaly_detection':
        const { data: events } = await supabaseClient
          .from('behavioral_events')
          .select('*')
          .eq('customer_id', customerId)
          .order('created_at', { ascending: false })
          .limit(200);
        
        analysisData = { behavioralEvents: events };
        prompt = `Analyze these behavioral events for anomalies and security concerns.
        Identify: unusual patterns, potential security threats, access anomalies, performance issues.
        Recent events: ${JSON.stringify(events?.slice(0, 10))}`;
        break;

      case 'compliance_risk':
        const { data: auditLogs } = await supabaseClient
          .from('audit_logs')
          .select('*')
          .eq('customer_id', customerId)
          .order('created_at', { ascending: false })
          .limit(100);
        
        analysisData = { auditLogs };
        prompt = `Analyze audit logs for compliance risks and security concerns.
        Look for: unauthorized access attempts, policy violations, suspicious patterns, compliance gaps.
        Recent audit logs: ${JSON.stringify(auditLogs?.slice(0, 10))}`;
        break;
    }

    // Call Lovable AI for analysis
    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    if (!LOVABLE_API_KEY) {
      throw new Error("LOVABLE_API_KEY not configured");
    }

    const aiResponse = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-flash",
        messages: [
          {
            role: "system",
            content: "You are an AI analyst specialized in IT operations, security, and compliance. Provide structured insights with specific, actionable recommendations. Format your response as JSON with: insights (array of {type, severity, title, description, confidence, recommendations})."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        tools: [{
          type: "function",
          function: {
            name: "create_insights",
            description: "Create structured insights from analysis",
            parameters: {
              type: "object",
              properties: {
                insights: {
                  type: "array",
                  items: {
                    type: "object",
                    properties: {
                      type: { type: "string", enum: ["risk_prediction", "anomaly_detection", "optimization_suggestion", "trend_analysis", "compliance_risk", "security_alert"] },
                      severity: { type: "string", enum: ["info", "low", "medium", "high", "critical"] },
                      title: { type: "string" },
                      description: { type: "string" },
                      confidence: { type: "number", minimum: 0, maximum: 100 },
                      recommendations: { type: "array", items: { type: "string" } }
                    },
                    required: ["type", "severity", "title", "description", "confidence", "recommendations"]
                  }
                }
              },
              required: ["insights"]
            }
          }
        }],
        tool_choice: { type: "function", function: { name: "create_insights" } }
      }),
    });

    if (!aiResponse.ok) {
      const errorText = await aiResponse.text();
      console.error('AI API error:', aiResponse.status, errorText);
      throw new Error(`AI analysis failed: ${errorText}`);
    }

    const aiData = await aiResponse.json();
    console.log('AI response:', JSON.stringify(aiData));

    const toolCall = aiData.choices[0]?.message?.tool_calls?.[0];
    const insightsData = toolCall ? JSON.parse(toolCall.function.arguments) : { insights: [] };

    // Store insights in database
    const insightsToInsert = insightsData.insights.map((insight: any) => ({
      customer_id: customerId,
      insight_type: insight.type,
      severity: insight.severity,
      title: insight.title,
      description: insight.description,
      confidence_score: insight.confidence,
      recommendations: insight.recommendations,
      supporting_data: analysisData,
      model_version: 'gemini-2.5-flash-v1',
      status: 'active',
      expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString() // 7 days
    }));

    const { data: savedInsights, error: insertError } = await supabaseClient
      .from('ai_insights')
      .insert(insightsToInsert)
      .select();

    if (insertError) {
      console.error('Error saving insights:', insertError);
      throw insertError;
    }

    console.log('Saved insights:', savedInsights?.length);

    return new Response(
      JSON.stringify({ 
        success: true, 
        insights: savedInsights,
        analysisType 
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error: any) {
    console.error('Error in predictive-insights:', error);
    return new Response(
      JSON.stringify({ error: error?.message || 'Unknown error' }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    );
  }
});