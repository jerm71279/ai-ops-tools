import "https://deno.land/x/xhr@0.1.0/mod.ts";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.3';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

interface MCPGenerationRequest {
  customerId: string;
  department: string;
  businessContext: {
    currentProcesses: string[];
    painPoints: string[];
    goals: string[];
    existingTools?: string[];
  };
  userPerformanceData?: {
    avgTaskCompletionTime?: number;
    commonBottlenecks?: string[];
    frequentActions?: string[];
  };
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const LOVABLE_API_KEY = Deno.env.get('LOVABLE_API_KEY');
    const SUPABASE_URL = Deno.env.get('SUPABASE_URL');
    const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');

    if (!LOVABLE_API_KEY || !SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
      throw new Error('Missing required environment variables');
    }

    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);
    const requestData: MCPGenerationRequest = await req.json();

    console.log('AI MCP Generator invoked for customer:', requestData.customerId);
    console.log('Department:', requestData.department);
    console.log('Business context:', requestData.businessContext);

    // Step 1: Use AI to analyze business needs and recommend MCP servers
    const analysisPrompt = `You are an expert business process automation architect. Analyze the following business context and recommend specific MCP (Model Context Protocol) servers that would streamline operations, automate workflows, and improve performance.

Department: ${requestData.department}

Current Processes:
${requestData.businessContext.currentProcesses.map(p => `- ${p}`).join('\n')}

Pain Points:
${requestData.businessContext.painPoints.map(p => `- ${p}`).join('\n')}

Goals:
${requestData.businessContext.goals.map(g => `- ${g}`).join('\n')}

${requestData.businessContext.existingTools ? `Existing Tools: ${requestData.businessContext.existingTools.join(', ')}` : ''}

${requestData.userPerformanceData ? `
User Performance Data:
- Average task completion time: ${requestData.userPerformanceData.avgTaskCompletionTime}ms
- Common bottlenecks: ${requestData.userPerformanceData.commonBottlenecks?.join(', ')}
- Frequent actions: ${requestData.userPerformanceData.frequentActions?.join(', ')}
` : ''}

Based on this context, recommend 1-3 specific MCP servers that would provide the most value. For each server, provide:
1. Server name (short, descriptive)
2. Description (what it does)
3. Server type (integration, automation, analytics, or custom)
4. Capabilities (array of key capabilities)
5. 2-3 specific tools with their names, descriptions, and input schemas

Return your response as a JSON array of server configurations.`;

    console.log('Calling Lovable AI for MCP recommendations...');

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
            content: 'You are an expert business process automation architect. Respond only with valid JSON arrays containing MCP server configurations.'
          },
          {
            role: 'user',
            content: analysisPrompt
          }
        ],
        temperature: 0.7,
      }),
    });

    if (!aiResponse.ok) {
      const errorText = await aiResponse.text();
      console.error('AI API error:', aiResponse.status, errorText);
      throw new Error(`AI API error: ${aiResponse.status}`);
    }

    const aiData = await aiResponse.json();
    const aiRecommendation = aiData.choices[0].message.content;
    console.log('AI recommendation received:', aiRecommendation);

    // Parse AI response
    let mcpConfigs;
    try {
      // Extract JSON from markdown code blocks if present
      const jsonMatch = aiRecommendation.match(/```json\n([\s\S]*?)\n```/) || 
                       aiRecommendation.match(/```\n([\s\S]*?)\n```/);
      const jsonStr = jsonMatch ? jsonMatch[1] : aiRecommendation;
      mcpConfigs = JSON.parse(jsonStr);
    } catch (parseError) {
      console.error('Failed to parse AI response:', parseError);
      throw new Error('AI returned invalid JSON format');
    }

    // Step 2: Create MCP servers in database
    const createdServers = [];

    for (const config of mcpConfigs) {
      console.log(`Creating MCP server: ${config.server_name}`);

      // Insert MCP server
      const { data: server, error: serverError } = await supabase
        .from('mcp_servers')
        .insert({
          customer_id: requestData.customerId,
          server_name: config.server_name,
          description: config.description,
          server_type: config.server_type || 'custom',
          status: 'active',
          capabilities: config.capabilities || [],
          config: {
            auto_generated: true,
            department: requestData.department,
            generated_at: new Date().toISOString(),
            business_context: requestData.businessContext
          }
        })
        .select()
        .single();

      if (serverError) {
        console.error('Error creating server:', serverError);
        throw serverError;
      }

      console.log(`Server created with ID: ${server.id}`);

      // Create tools for this server
      const createdTools = [];
      if (config.tools && Array.isArray(config.tools)) {
        for (const tool of config.tools) {
          const { data: toolData, error: toolError } = await supabase
            .from('mcp_tools')
            .insert({
              server_id: server.id,
              tool_name: tool.name,
              description: tool.description,
              input_schema: tool.input_schema || {
                type: 'object',
                properties: {},
                required: []
              },
              output_schema: tool.output_schema || {
                type: 'object',
                properties: {
                  success: { type: 'boolean' },
                  result: { type: 'string' }
                }
              },
              is_enabled: true
            })
            .select()
            .single();

          if (toolError) {
            console.error('Error creating tool:', toolError);
          } else {
            console.log(`Tool created: ${tool.name}`);
            createdTools.push(toolData);
          }
        }
      }

      // Create resources if specified
      if (config.resources && Array.isArray(config.resources)) {
        for (const resource of config.resources) {
          const { error: resourceError } = await supabase
            .from('mcp_resources')
            .insert({
              server_id: server.id,
              resource_type: resource.type,
              resource_uri: resource.uri,
              description: resource.description,
              metadata: resource.metadata || {}
            });

          if (resourceError) {
            console.error('Error creating resource:', resourceError);
          } else {
            console.log(`Resource created: ${resource.uri}`);
          }
        }
      }

      createdServers.push({
        server: server,
        tools: createdTools,
        ai_reasoning: config.reasoning || 'Auto-generated to optimize business processes'
      });
    }

    // Log the creation activity
    const authHeader = req.headers.get('authorization');
    let userId = null;
    if (authHeader) {
      const token = authHeader.replace('Bearer ', '');
      const { data: { user } } = await supabase.auth.getUser(token);
      userId = user?.id;
    }

    await supabase.from('audit_logs').insert({
      customer_id: requestData.customerId,
      user_id: userId || '00000000-0000-0000-0000-000000000000',
      system_name: 'ai_mcp_generator',
      action_type: 'mcp_servers_created',
      action_details: {
        department: requestData.department,
        servers_created: createdServers.length,
        business_goals: requestData.businessContext.goals
      },
      compliance_tags: ['automation', 'ai', 'mcp']
    });

    // Insert ML insight about the optimization
    await supabase.from('ml_insights').insert({
      customer_id: requestData.customerId,
      insight_type: 'optimization',
      category: 'automation',
      description: `AI automatically created ${createdServers.length} MCP server(s) for ${requestData.department} department to address: ${requestData.businessContext.painPoints.slice(0, 2).join(', ')}`,
      confidence_score: 0.85,
      status: 'new',
      data_source: {
        model: 'gemini-2.5-flash',
        department: requestData.department,
        automation_type: 'mcp_generation'
      }
    });

    console.log(`Successfully created ${createdServers.length} MCP servers`);

    return new Response(
      JSON.stringify({
        success: true,
        serversCreated: createdServers.length,
        servers: createdServers,
        message: `Successfully created ${createdServers.length} MCP server(s) to optimize ${requestData.department} workflows`
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200
      }
    );

  } catch (error) {
    console.error('Error in ai-mcp-generator:', error);
    return new Response(
      JSON.stringify({
        error: error instanceof Error ? error.message : 'Unknown error occurred',
        details: error instanceof Error ? error.stack : undefined
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500
      }
    );
  }
});
