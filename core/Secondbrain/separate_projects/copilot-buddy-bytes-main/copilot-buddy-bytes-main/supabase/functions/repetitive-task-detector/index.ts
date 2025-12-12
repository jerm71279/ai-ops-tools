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
    const { userId, actionType, systemName, context } = await req.json();
    const SUPABASE_URL = Deno.env.get("SUPABASE_URL");
    const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");

    if (!SUPABASE_URL || !SUPABASE_SERVICE_ROLE_KEY) {
      throw new Error("Required environment variables are not configured");
    }

    const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

    // Get user's customer_id
    const { data: profile } = await supabase
      .from('user_profiles')
      .select('customer_id')
      .eq('user_id', userId)
      .single();

    if (!profile?.customer_id) {
      throw new Error("User profile not found");
    }

    // Create a normalized task signature (action + system + key context elements)
    const taskSignature = `${actionType}:${systemName}:${JSON.stringify(context || {})}`;

    console.log(`Checking task repetition for user ${userId}: ${taskSignature}`);

    // Check if this task pattern already exists
    const { data: existing, error: fetchError } = await supabase
      .from('task_repetition_analysis')
      .select('*')
      .eq('user_id', userId)
      .eq('task_signature', taskSignature)
      .maybeSingle();

    if (fetchError) {
      console.error("Error fetching existing task:", fetchError);
      throw fetchError;
    }

    let repetitionCount = 1;
    let shouldSuggest = false;

    if (existing) {
      // Update existing record
      repetitionCount = existing.repetition_count + 1;
      
      const { error: updateError } = await supabase
        .from('task_repetition_analysis')
        .update({
          repetition_count: repetitionCount,
          last_occurrence: new Date().toISOString(),
          task_context: context || {}
        })
        .eq('id', existing.id);

      if (updateError) {
        console.error("Error updating task repetition:", updateError);
        throw updateError;
      }

      // Suggest automation after 3 repetitions if not already suggested
      if (repetitionCount >= 3 && existing.status === 'detected') {
        shouldSuggest = true;
      }

      console.log(`✅ Updated task repetition count to ${repetitionCount}`);
    } else {
      // Insert new record
      const { error: insertError } = await supabase
        .from('task_repetition_analysis')
        .insert({
          user_id: userId,
          customer_id: profile.customer_id,
          task_signature: taskSignature,
          action_type: actionType,
          system_name: systemName,
          task_context: context || {},
          repetition_count: 1,
          status: 'detected'
        });

      if (insertError) {
        console.error("Error inserting task repetition:", insertError);
        throw insertError;
      }

      console.log(`✅ Created new task repetition tracking`);
    }

    return new Response(
      JSON.stringify({ 
        success: true,
        repetitionCount,
        shouldSuggest,
        message: shouldSuggest 
          ? `Task repeated ${repetitionCount} times - automation suggestion triggered` 
          : `Task tracked (${repetitionCount} repetitions)`
      }),
      { 
        status: 200,
        headers: { ...corsHeaders, "Content-Type": "application/json" }
      }
    );

  } catch (error) {
    console.error("Error in repetitive-task-detector function:", error);
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
