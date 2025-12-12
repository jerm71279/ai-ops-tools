import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { taskId } = await req.json();
    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
    const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

    if (!LOVABLE_API_KEY || !SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
      throw new Error("Required environment variables are not configured");
    }

    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

    // Fetch the task repetition details
    const { data: task, error: taskError } = await supabase
      .from('task_repetition_analysis')
      .select('*')
      .eq('id', taskId)
      .single();

    if (taskError || !task) {
      throw new Error("Task not found");
    }

    console.log(`Generating automation suggestion for task: ${task.action_type} on ${task.system_name}`);

    const systemPrompt = `You are an AI workflow automation specialist. Analyze repetitive tasks and suggest specific, actionable automation workflows.
Your suggestions should be practical, specific to the user's context, and include:
1. Clear workflow steps
2. Required integrations/systems
3. Triggers and conditions
4. Expected time savings
5. Implementation difficulty (easy/medium/hard)`;

    const userPrompt = `A user has performed this task ${task.repetition_count} times:

TASK DETAILS:
- Action Type: ${task.action_type}
- System: ${task.system_name}
- Context: ${JSON.stringify(task.task_context, null, 2)}
- First Occurrence: ${task.first_occurrence}
- Last Occurrence: ${task.last_occurrence}
- Time Period: ${Math.round((new Date(task.last_occurrence).getTime() - new Date(task.first_occurrence).getTime()) / (1000 * 60 * 60 * 24))} days

Based on this repetitive behavior, suggest a specific automation workflow. Include:
1. Workflow name
2. Description of what it automates
3. Step-by-step workflow actions
4. Trigger type (schedule/manual/webhook)
5. Estimated time savings per execution
6. Implementation difficulty

Format as JSON:
{
  "workflowName": "string",
  "description": "string",
  "steps": [
    { "order": 1, "action": "string", "details": "string" }
  ],
  "triggerType": "schedule|manual|webhook",
  "triggerConfig": {},
  "estimatedTimeSavingsMinutes": number,
  "implementationDifficulty": "easy|medium|hard",
  "requiredIntegrations": ["system1", "system2"],
  "confidence": number (0-100)
}`;

    const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-flash",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: userPrompt }
        ],
      }),
    });

    if (!response.ok) {
      if (response.status === 429) {
        return new Response(
          JSON.stringify({ error: "Rate limit exceeded. Please try again later." }),
          { status: 429, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
      if (response.status === 402) {
        return new Response(
          JSON.stringify({ error: "AI credits exhausted. Please add credits to continue." }),
          { status: 402, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
      throw new Error(`AI gateway error: ${response.status}`);
    }

    const data = await response.json();
    const content = data.choices[0].message.content;
    
    let suggestion;
    try {
      const jsonMatch = content.match(/```json\n([\s\S]*?)\n```/) || content.match(/```\n([\s\S]*?)\n```/);
      const jsonString = jsonMatch ? jsonMatch[1] : content;
      suggestion = JSON.parse(jsonString);
    } catch (e) {
      console.error("Failed to parse AI response:", content);
      suggestion = {
        workflowName: "Automate Repetitive Task",
        description: "Based on your repetitive actions, this workflow can save time",
        steps: [
          { order: 1, action: "Detect trigger", details: "Monitor for task initiation" },
          { order: 2, action: "Execute automation", details: "Perform the repetitive actions automatically" }
        ],
        triggerType: "manual",
        triggerConfig: {},
        estimatedTimeSavingsMinutes: 5,
        implementationDifficulty: "medium",
        requiredIntegrations: [task.system_name],
        confidence: 60
      };
    }

    // Update the task with the suggestion
    const { error: updateError } = await supabase
      .from('task_repetition_analysis')
      .update({
        suggested_workflow: suggestion,
        suggestion_confidence: suggestion.confidence / 100,
        status: 'suggested'
      })
      .eq('id', taskId);

    if (updateError) {
      console.error("Error updating task with suggestion:", updateError);
      throw updateError;
    }

    console.log(`✅ Generated automation suggestion for task ${taskId}`);

    // Create a knowledge insight
    if (suggestion.confidence > 70) {
      await supabase
        .from("knowledge_insights")
        .insert({
          customer_id: task.customer_id,
          insight_type: "recommendation",
          title: `Automation Opportunity: ${suggestion.workflowName}`,
          description: `${suggestion.description}\n\nEstimated time savings: ${suggestion.estimatedTimeSavingsMinutes} minutes per execution\nTask repeated ${task.repetition_count} times`,
          confidence_score: suggestion.confidence / 100,
          status: "new",
          data_sources: {
            task_id: taskId,
            action_type: task.action_type,
            system_name: task.system_name,
            repetition_count: task.repetition_count
          }
        });
    }

    return new Response(
      JSON.stringify({ 
        success: true,
        suggestion,
        taskId
      }),
      { 
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      }
    );

  } catch (error) {
    console.error("Error in automation-suggester function:", error);
    return new Response(
      JSON.stringify({ 
        error: error instanceof Error ? error.message : "Unknown error occurred" 
      }),
      { 
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      }
    );
  }
});
