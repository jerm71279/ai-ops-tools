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
        global: {
          headers: { Authorization: req.headers.get('Authorization')! },
        },
      }
    );

    const { action, fileId, workflowData, articleContent } = await req.json();
    const LOVABLE_API_KEY = Deno.env.get('LOVABLE_API_KEY');

    console.log("📚 Processing knowledge request:", action);

    switch (action) {
      case 'process_file': {
        // Get file metadata
        const { data: file, error: fileError } = await supabaseClient
          .from('knowledge_files')
          .select('*')
          .eq('id', fileId)
          .single();

        if (fileError) throw fileError;

        // Update status to processing
        await supabaseClient
          .from('knowledge_files')
          .update({ processed_status: 'processing' })
          .eq('id', fileId);

        // Generate AI summary and extract key insights
        const aiResponse = await fetch('https://ai.gateway.lovable.dev/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${LOVABLE_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'google/gemini-2.5-flash',
            messages: [
              {
                role: 'system',
                content: 'You are a knowledge management AI. Extract key information, create summaries, and identify actionable insights from documents. Format your response as JSON with: summary, key_points (array), recommended_tags (array), and suggested_sop_updates (array).'
              },
              {
                role: 'user',
                content: `Analyze this file content and extract knowledge:\n\nFile: ${file.file_name}\nType: ${file.file_type}\nContent: ${file.extracted_content || 'No content extracted'}`
              }
            ],
            tools: [
              {
                type: "function",
                function: {
                  name: "extract_knowledge",
                  description: "Extract structured knowledge from file content",
                  parameters: {
                    type: "object",
                    properties: {
                      summary: { type: "string" },
                      key_points: { type: "array", items: { type: "string" } },
                      recommended_tags: { type: "array", items: { type: "string" } },
                      suggested_sop_updates: { type: "array", items: { type: "string" } }
                    },
                    required: ["summary", "key_points", "recommended_tags"],
                    additionalProperties: false
                  }
                }
              }
            ],
            tool_choice: { type: "function", function: { name: "extract_knowledge" } }
          }),
        });

        const aiData = await aiResponse.json();
        const toolCall = aiData.choices[0].message.tool_calls[0];
        const knowledge = JSON.parse(toolCall.function.arguments);

        // Update file with AI summary
        await supabaseClient
          .from('knowledge_files')
          .update({
            ai_summary: knowledge.summary,
            metadata: knowledge,
            processed_status: 'completed'
          })
          .eq('id', fileId);

        return new Response(JSON.stringify({ success: true, knowledge }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      case 'generate_from_workflows': {
        // Analyze workflow data and generate knowledge articles
        const aiResponse = await fetch('https://ai.gateway.lovable.dev/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${LOVABLE_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'google/gemini-2.5-flash',
            messages: [
              {
                role: 'system',
                content: 'You are an expert at creating SOPs and documentation from workflow data. Generate clear, actionable standard operating procedures based on successful workflow patterns.'
              },
              {
                role: 'user',
                content: `Generate SOPs and knowledge articles from these workflow patterns:\n\n${JSON.stringify(workflowData, null, 2)}`
              }
            ],
          }),
        });

        const aiData = await aiResponse.json();
        const generatedContent = aiData.choices[0].message.content;

        return new Response(JSON.stringify({ content: generatedContent }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      case 'enhance_article': {
        // Enhance existing article with AI suggestions
        const aiResponse = await fetch('https://ai.gateway.lovable.dev/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${LOVABLE_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'google/gemini-2.5-flash',
            messages: [
              {
                role: 'system',
                content: 'You are an expert technical writer. Enhance documentation by improving clarity, adding missing details, and suggesting better structure.'
              },
              {
                role: 'user',
                content: `Enhance this knowledge article:\n\n${articleContent}`
              }
            ],
          }),
        });

        const aiData = await aiResponse.json();
        const enhanced = aiData.choices[0].message.content;

        return new Response(JSON.stringify({ enhanced }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        });
      }

      default:
        throw new Error('Invalid action');
    }
  } catch (error) {
    console.error('Error in knowledge-processor:', error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : 'Unknown error' }),
      {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      }
    );
  }
});