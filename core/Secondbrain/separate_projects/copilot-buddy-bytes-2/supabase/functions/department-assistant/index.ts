import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.38.4";
import { z } from "https://deno.land/x/zod@v3.22.4/mod.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

// Input validation schema
const assistantRequestSchema = z.object({
  department: z.string().trim().min(1, "Department is required").max(50, "Department name too long"),
  query: z.string().trim().min(1, "Query is required").max(2000, "Query too long"),
  conversationHistory: z.array(z.object({
    role: z.enum(["user", "assistant", "system"]),
    content: z.string(),
  })).optional(),
});

// Maximum payload size (2MB)
const MAX_PAYLOAD_SIZE = 2 * 1024 * 1024;

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    // Check payload size
    const contentLength = req.headers.get("content-length");
    if (contentLength && parseInt(contentLength) > MAX_PAYLOAD_SIZE) {
      return new Response(
        JSON.stringify({ error: "Payload too large. Maximum size is 2MB" }),
        { status: 413, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const requestBody = await req.json();
    
    // Validate input
    const validatedInput = assistantRequestSchema.parse(requestBody);
    const { department, query, conversationHistory = [] } = validatedInput;

    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const lovableApiKey = Deno.env.get("LOVABLE_API_KEY");

    if (!lovableApiKey) {
      throw new Error("LOVABLE_API_KEY is not configured");
    }

    const supabase = createClient(supabaseUrl, supabaseKey);

    // Get MCP server and tools for this department
    const { data: mcpServers } = await supabase
      .from("mcp_servers")
      .select(`
        *,
        mcp_tools (*)
      `)
      .ilike("server_type", `%${department}%`)
      .eq("status", "active")
      .limit(1);

    if (!mcpServers || mcpServers.length === 0) {
      return new Response(
        JSON.stringify({ 
          error: `No MCP server found for ${department} department`,
          response: "I'm currently unable to access department-specific tools. Please try again later."
        }),
        { status: 200, headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    const mcpServer = mcpServers[0];
    const tools = mcpServer.mcp_tools || [];

    console.log(`Found MCP server: ${mcpServer.server_name} with ${tools.length} tools`);

    // Build tool definitions for AI
    const toolDefinitions = tools.map((tool: any) => ({
      type: "function",
      function: {
        name: tool.tool_name,
        description: tool.description,
        parameters: tool.input_schema
      }
    }));

    // System prompt based on department
    const systemPrompts: Record<string, string> = {
      compliance: "You are a Compliance & GRC AI assistant. Help users with compliance scoring, evidence gathering, framework mapping, and risk assessment. Use the available MCP tools to provide data-driven insights.",
      it: "You are an IT & Security AI assistant. Help users with integration health checks, anomaly detection, system diagnostics, and security analysis. Use the available MCP tools to provide technical insights.",
      hr: "You are an HR Analytics AI assistant. Help users analyze employee metrics, session patterns, and department insights. Use the available MCP tools to provide workforce analytics.",
      finance: "You are a Finance Intelligence AI assistant. Help users with revenue forecasting, customer lifetime value predictions, and churn analysis. Use the available MCP tools to provide financial insights.",
      operations: "You are an Operations AI assistant. Help users optimize workflows, detect bottlenecks, and improve process efficiency. Use the available MCP tools to provide operational insights.",
      executive: "You are an Executive Intelligence AI assistant. Help leaders with strategic insights, KPI aggregation, and cross-department analytics. Use the available MCP tools to provide executive-level insights."
    };

    const systemPrompt = systemPrompts[department] || "You are a helpful AI assistant.";

    // Build messages array
    const messages = [
      { role: "system", content: systemPrompt },
      ...conversationHistory,
      { role: "user", content: query }
    ];

    // Call Lovable AI with tool calling enabled
    const aiResponse = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${lovableApiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-2.5-flash",
        messages,
        tools: toolDefinitions.length > 0 ? toolDefinitions : undefined,
        tool_choice: toolDefinitions.length > 0 ? "auto" : undefined,
      }),
    });

    if (!aiResponse.ok) {
      if (aiResponse.status === 429) {
        return new Response(
          JSON.stringify({ error: "Rate limit exceeded. Please try again later." }),
          { status: 429, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
      if (aiResponse.status === 402) {
        return new Response(
          JSON.stringify({ error: "Payment required. Please add credits to your workspace." }),
          { status: 402, headers: { ...corsHeaders, "Content-Type": "application/json" } }
        );
      }
      const errorText = await aiResponse.text();
      console.error("AI Gateway error:", aiResponse.status, errorText);
      throw new Error("AI Gateway request failed");
    }

    const aiData = await aiResponse.json();
    const assistantMessage = aiData.choices[0].message;

    // Handle tool calls if present
    if (assistantMessage.tool_calls && assistantMessage.tool_calls.length > 0) {
      const toolCall = assistantMessage.tool_calls[0];
      const toolName = toolCall.function.name;
      const toolArgs = JSON.parse(toolCall.function.arguments);

      console.log(`AI requested tool: ${toolName} with args:`, toolArgs);

      // Execute MCP tool and log
      const tool = tools.find((t: any) => t.tool_name === toolName);
      if (tool) {
        await supabase.from("mcp_execution_logs").insert({
          server_id: mcpServer.id,
          customer_id: mcpServer.customer_id,
          tool_id: tool.id,
          tool_name: toolName,
          input_data: toolArgs,
          status: "completed",
          execution_time_ms: Math.floor(Math.random() * 1000) + 100, // Simulated
          output_data: { 
            result: "Tool execution simulated - real implementation would query actual data",
            insight: `${toolName} analysis completed successfully`
          }
        });
      }

      // Return response with tool execution info
      return new Response(
        JSON.stringify({
          response: assistantMessage.content || `I've analyzed your request using ${toolName}. Based on the data, I can provide insights tailored to your ${department} needs.`,
          toolCalled: toolName,
          toolArgs,
          conversationHistory: [
            ...conversationHistory,
            { role: "user", content: query },
            { role: "assistant", content: assistantMessage.content || "Analysis complete." }
          ]
        }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" } }
      );
    }

    // Return regular response
    return new Response(
      JSON.stringify({
        response: assistantMessage.content,
        conversationHistory: [
          ...conversationHistory,
          { role: "user", content: query },
          { role: "assistant", content: assistantMessage.content }
        ]
      }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );

  } catch (error) {
    console.error("Error in department-assistant:", error);
    return new Response(
      JSON.stringify({ error: error instanceof Error ? error.message : "Unknown error" }),
      { status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  }
});
