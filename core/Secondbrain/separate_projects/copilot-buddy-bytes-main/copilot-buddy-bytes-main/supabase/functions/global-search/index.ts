import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.38.4";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { query, customerId } = await req.json();

    if (!query || query.trim().length === 0) {
      return new Response(JSON.stringify({ results: [] }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_ANON_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Search across multiple tables
    const [
      workflows, 
      compliance, 
      cmdb, 
      knowledge, 
      changeRecords, 
      anomalies,
      auditLogs,
      users,
      applications,
      tenants,
      onboardings,
      complianceFrameworks,
      aiInteractions
    ] = await Promise.all([
      supabase.from("workflow_executions").select("*").ilike("workflow_name", `%${query}%`).limit(5),
      supabase.from("compliance_audit_reports").select("*").ilike("report_title", `%${query}%`).limit(5),
      supabase.from("cmdb_items").select("*").or(`name.ilike.%${query}%,description.ilike.%${query}%`).limit(5),
      supabase.from("knowledge_articles").select("*").or(`title.ilike.%${query}%,content.ilike.%${query}%`).limit(5),
      supabase.from("change_requests").select("*").or(`title.ilike.%${query}%,description.ilike.%${query}%`).limit(5),
      supabase.from("anomaly_detections").select("*").or(`description.ilike.%${query}%,system_name.ilike.%${query}%,anomaly_type.ilike.%${query}%`).limit(5),
      supabase.from("audit_logs").select("*").or(`system_name.ilike.%${query}%,action_type.ilike.%${query}%`).limit(5),
      supabase.from("user_profiles").select("*").or(`full_name.ilike.%${query}%,department.ilike.%${query}%`).limit(5),
      supabase.from("applications").select("*").or(`name.ilike.%${query}%,description.ilike.%${query}%`).limit(5),
      supabase.from("cipp_tenants").select("*").or(`tenant_name.ilike.%${query}%,display_name.ilike.%${query}%`).limit(5),
      supabase.from("client_onboardings").select("*").or(`client_name.ilike.%${query}%,client_contact_name.ilike.%${query}%`).limit(5),
      supabase.from("compliance_frameworks").select("*").or(`framework_name.ilike.%${query}%,description.ilike.%${query}%`).limit(5),
      supabase.from("ai_interactions").select("*").or(`user_query.ilike.%${query}%,ai_response.ilike.%${query}%`).limit(5),
    ]);

    // Use AI to rank and contextualize results
    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    
    const allResults = [
      ...(workflows.data || []).map(w => ({ type: "workflow", data: w, title: w.workflow_name, url: `/workflow-execution/${w.id}` })),
      ...(compliance.data || []).map(c => ({ type: "compliance", data: c, title: c.report_title, url: `/compliance/reports/${c.id}` })),
      ...(cmdb.data || []).map(i => ({ type: "cmdb", data: i, title: i.name, url: `/cmdb/items/${i.id}` })),
      ...(knowledge.data || []).map(k => ({ type: "knowledge", data: k, title: k.title, url: `/knowledge/${k.id}` })),
      ...(changeRecords.data || []).map(cr => ({ type: "change", data: cr, title: cr.title, url: `/change-management/${cr.id}` })),
      ...(anomalies.data || []).map(a => ({ type: "anomaly", data: a, title: `${a.anomaly_type} - ${a.system_name}`, url: `/dashboard/soc` })),
      ...(auditLogs.data || []).map(al => ({ type: "audit", data: al, title: `${al.action_type} - ${al.system_name}`, url: `/compliance/audit-reports` })),
      ...(users.data || []).map(u => ({ type: "user", data: u, title: u.full_name, url: `/admin` })),
      ...(applications.data || []).map(app => ({ type: "application", data: app, title: app.name, url: `/admin/applications` })),
      ...(tenants.data || []).map(t => ({ type: "tenant", data: t, title: t.tenant_name, url: `/cipp` })),
      ...(onboardings.data || []).map(o => ({ type: "onboarding", data: o, title: `${o.client_name} Onboarding`, url: `/onboarding` })),
      ...(complianceFrameworks.data || []).map(cf => ({ type: "framework", data: cf, title: cf.framework_name, url: `/compliance/frameworks/${cf.id}` })),
      ...(aiInteractions.data || []).map(ai => ({ type: "ai-chat", data: ai, title: ai.user_query.substring(0, 50) + "...", url: `/intelligent-assistant` })),
    ];

    if (LOVABLE_API_KEY && allResults.length > 0) {
      try {
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
                content: "You analyze search results and provide a brief relevance summary. Return only JSON with 'summary' and 'topMatch' fields."
              },
              {
                role: "user",
                content: `Query: "${query}"\nResults: ${JSON.stringify(allResults.slice(0, 10).map(r => ({ type: r.type, title: r.title })))}\n\nProvide a one-sentence summary and indicate the most relevant result type.`
              }
            ],
            tools: [{
              type: "function",
              function: {
                name: "analyze_search",
                description: "Analyze search results",
                parameters: {
                  type: "object",
                  properties: {
                    summary: { type: "string" },
                    topMatch: { type: "string" }
                  },
                  required: ["summary", "topMatch"],
                  additionalProperties: false
                }
              }
            }],
            tool_choice: { type: "function", function: { name: "analyze_search" } }
          }),
        });

        if (aiResponse.ok) {
          const aiData = await aiResponse.json();
          const toolCall = aiData.choices?.[0]?.message?.tool_calls?.[0];
          if (toolCall) {
            const analysis = JSON.parse(toolCall.function.arguments);
            return new Response(JSON.stringify({ results: allResults, aiSummary: analysis.summary, topMatch: analysis.topMatch }), {
              headers: { ...corsHeaders, "Content-Type": "application/json" },
            });
          }
        }
      } catch (aiError) {
        console.error("AI analysis error:", aiError);
      }
    }

    return new Response(JSON.stringify({ results: allResults }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("Search error:", error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    return new Response(JSON.stringify({ error: errorMessage }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
