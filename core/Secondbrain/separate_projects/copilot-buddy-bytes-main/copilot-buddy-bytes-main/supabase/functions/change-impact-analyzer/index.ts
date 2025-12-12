import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.58.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

interface ImpactAnalysisRequest {
  changeRequestId: string;
  affectedCiIds: string[];
  changeDescription: string;
  changeType: string;
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const lovableApiKey = Deno.env.get("LOVABLE_API_KEY");

    const supabase = createClient(supabaseUrl, supabaseKey);

    const { changeRequestId, affectedCiIds, changeDescription, changeType }: ImpactAnalysisRequest = await req.json();

    console.log("Analyzing change impact:", { changeRequestId, affectedCiIds: affectedCiIds.length });

    // 1. Fetch affected CIs and their relationships
    const { data: affectedCis, error: ciError } = await supabase
      .from("configuration_items")
      .select("*, ci_relationships!source_ci_id(*)")
      .in("id", affectedCiIds);

    if (ciError) throw ciError;

    // 2. Calculate dependency depth (how many CIs depend on these)
    const { data: dependentCis, error: depError } = await supabase
      .from("ci_relationships")
      .select("source_ci_id")
      .in("target_ci_id", affectedCiIds);

    if (depError) throw depError;

    const dependentCount = dependentCis?.length || 0;
    const criticalCount = affectedCis?.filter((ci: any) => ci.criticality === "critical").length || 0;

    // 3. Check historical change success rate
    const { data: historicalChanges, error: histError } = await supabase
      .from("change_requests")
      .select("change_status, change_type")
      .eq("change_type", changeType)
      .in("change_status", ["completed", "failed", "rolled_back"]);

    if (histError) throw histError;

    const completedChanges = historicalChanges?.filter((c: any) => c.change_status === "completed").length || 0;
    const totalHistorical = historicalChanges?.length || 0;
    const successRate = totalHistorical > 0 ? (completedChanges / totalHistorical) * 100 : 75;

    // 4. Calculate complexity score
    const complexityScore = Math.min(100, 
      (affectedCiIds.length * 10) + 
      (dependentCount * 5) + 
      (criticalCount * 15)
    );

    // 5. Use AI to analyze risk factors
    let aiRecommendation = "Manual review recommended";
    let riskFactors: Record<string, boolean> = {};
    let successProbability = successRate;

    if (lovableApiKey) {
      try {
        const aiPrompt = `Analyze this IT change request and provide risk assessment:

Change Type: ${changeType}
Description: ${changeDescription}
Affected Systems: ${affectedCiIds.length}
Critical Systems: ${criticalCount}
Dependent Systems: ${dependentCount}
Historical Success Rate: ${successRate.toFixed(1)}%

Provide:
1. Risk factors (technical, business, security)
2. Mitigation strategies
3. Success probability (0-100)
4. Recommended timing
5. Key concerns`;

        const aiResponse = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${lovableApiKey}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            model: "google/gemini-2.5-flash",
            messages: [
              {
                role: "system",
                content: "You are an IT change management risk analyst. Provide concise, actionable risk assessments for change requests."
              },
              {
                role: "user",
                content: aiPrompt
              }
            ],
          }),
        });

        if (aiResponse.ok) {
          const aiData = await aiResponse.json();
          aiRecommendation = aiData.choices?.[0]?.message?.content || aiRecommendation;
          
          // Extract success probability from AI response if mentioned
          const probMatch = aiRecommendation.match(/success probability[:\s]+(\d+)/i);
          if (probMatch) {
            successProbability = Math.min(100, Math.max(0, parseInt(probMatch[1])));
          }
        }
      } catch (aiError) {
        console.error("AI analysis failed:", aiError);
      }
    }

    // 6. Calculate impact scores
    const businessImpactScore = Math.min(100, (criticalCount * 25) + (dependentCount * 5));
    const technicalImpactScore = complexityScore;
    const securityImpactScore = Math.min(100, criticalCount * 20);
    const complianceImpactScore = affectedCis?.some((ci: any) => 
      ci.compliance_tags?.length > 0
    ) ? 70 : 30;

    // 7. Determine risk factors
    riskFactors = {
      high_complexity: complexityScore > 70,
      critical_systems_affected: criticalCount > 0,
      many_dependencies: dependentCount > 10,
      low_historical_success: successRate < 80,
      compliance_impact: complianceImpactScore > 60,
    };

    // 8. Insert impact analysis
    const { data: analysis, error: insertError } = await supabase
      .from("change_impact_analysis")
      .insert({
        change_request_id: changeRequestId,
        customer_id: affectedCis?.[0]?.customer_id,
        business_impact_score: businessImpactScore,
        technical_impact_score: technicalImpactScore,
        security_impact_score: securityImpactScore,
        compliance_impact_score: complianceImpactScore,
        dependent_ci_count: dependentCount,
        affected_ci_ids: affectedCiIds,
        complexity_score: complexityScore,
        risk_factors: riskFactors,
        similar_changes_analyzed: totalHistorical,
        similar_changes_success_rate: successRate,
        success_probability: successProbability,
        recommended_approach: aiRecommendation,
        ai_confidence_score: lovableApiKey ? 85 : 50,
      })
      .select()
      .single();

    if (insertError) throw insertError;

    // 9. Update change request with risk level
    let riskLevel = "low";
    if (businessImpactScore > 70 || technicalImpactScore > 70) riskLevel = "critical";
    else if (businessImpactScore > 50 || technicalImpactScore > 50) riskLevel = "high";
    else if (businessImpactScore > 30 || technicalImpactScore > 30) riskLevel = "medium";

    await supabase
      .from("change_requests")
      .update({
        risk_level: riskLevel,
        risk_score: (businessImpactScore + technicalImpactScore) / 2,
        ml_recommendation: aiRecommendation.substring(0, 500),
      })
      .eq("id", changeRequestId);

    return new Response(
      JSON.stringify({
        success: true,
        analysis: {
          ...analysis,
          risk_summary: {
            overall_risk: riskLevel,
            success_probability: successProbability,
            key_concerns: Object.keys(riskFactors).filter(k => riskFactors[k]),
          },
        },
      }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (error) {
    console.error("Change impact analysis error:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
