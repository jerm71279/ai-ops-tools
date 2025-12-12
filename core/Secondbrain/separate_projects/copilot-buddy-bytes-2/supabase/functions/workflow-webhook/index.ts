/**
 * Workflow Webhook Edge Function
 * 
 * Receives HTTP POST requests to trigger workflow executions.
 * Each webhook trigger has a unique URL that external systems can call.
 * Validates trigger status, verifies signatures (if configured), and initiates workflow execution.
 * 
 * Features:
 * - Unique webhook URLs per trigger
 * - HMAC SHA-256 signature verification (optional)
 * - Trigger enable/disable without changing URL
 * - Last triggered timestamp tracking
 * - Payload forwarding to workflow executor
 * 
 * Webhook URL Format:
 * {SUPABASE_URL}/functions/v1/workflow-webhook?id={trigger_id}
 * 
 * Request Format:
 * POST {webhook_url}
 * Headers:
 *   Content-Type: application/json
 *   x-webhook-signature: {hmac_signature} (optional, if webhook_secret configured)
 * Body:
 *   Any JSON payload (passed to workflow as trigger_data)
 * 
 * Security:
 * - Validates trigger exists and is enabled
 * - Verifies HMAC signature if webhook_secret is configured
 * - Uses service role key for database access
 * 
 * Integration Points:
 * - WorkflowTriggerManager: Webhook URLs created here
 * - workflow-executor: Called to execute the workflow
 * - workflow_triggers: Trigger configuration and status
 * 
 * @module workflow-webhook
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { z } from "https://deno.land/x/zod@v3.22.4/mod.ts";

/**
 * CORS headers for webhook requests
 * Includes x-webhook-signature for signature verification
 */
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type, x-webhook-signature',
};

// Input validation schema
const webhookPayloadSchema = z.record(z.any());

// Maximum payload size (1MB)
const MAX_PAYLOAD_SIZE = 1024 * 1024;

serve(async (req) => {
  // Handle preflight OPTIONS request
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    // Check payload size
    const contentLength = req.headers.get('content-length');
    if (contentLength && parseInt(contentLength) > MAX_PAYLOAD_SIZE) {
      return new Response(
        JSON.stringify({ error: 'Payload too large. Maximum size is 1MB' }),
        { status: 413, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Initialize Supabase client with service role (full access)
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Extract webhook ID from query parameter
    const url = new URL(req.url);
    const webhookId = url.searchParams.get('id');

    // Validation: webhook ID is required
    if (!webhookId) {
      return new Response(
        JSON.stringify({ error: 'Webhook ID is required' }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    console.log(`Webhook triggered: ${webhookId}`);

    // Step 1: Parse and validate webhook payload
    const rawPayload = await req.json();
    const payload = webhookPayloadSchema.parse(rawPayload);
    console.log('Webhook payload:', payload);

    // Step 2: Find and validate the trigger
    // Joins with workflows table to get workflow details
    const { data: trigger, error: triggerError } = await supabase
      .from('workflow_triggers')
      .select('*, workflows(*)')
      .eq('id', webhookId)
      .eq('trigger_type', 'webhook')     // Must be webhook type
      .eq('is_enabled', true)            // Must be enabled
      .single();

    // Validation: trigger must exist and be enabled
    if (triggerError || !trigger) {
      console.error('Trigger not found or disabled:', triggerError);
      return new Response(
        JSON.stringify({ error: 'Webhook not found or disabled' }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    // Step 3: Verify webhook signature (if configured)
    // This ensures the request is from a trusted source
    const signature = req.headers.get('x-webhook-signature');
    if (trigger.webhook_secret && signature) {
      const isValid = await verifyWebhookSignature(
        JSON.stringify(payload),
        signature,
        trigger.webhook_secret
      );

      if (!isValid) {
        console.error('Invalid webhook signature');
        return new Response(
          JSON.stringify({ error: 'Invalid signature' }),
          { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        );
      }
    }

    // Step 4: Update last triggered timestamp
    // Tracks webhook usage for analytics and debugging
    await supabase
      .from('workflow_triggers')
      .update({ last_triggered_at: new Date().toISOString() })
      .eq('id', webhookId);

    // Step 5: Execute the workflow
    // Calls workflow-executor edge function with payload
    const executionResult = await supabase.functions.invoke('workflow-executor', {
      body: {
        workflow_id: trigger.workflow_id,
        trigger_data: payload,           // Original webhook payload
        triggered_by: 'webhook'          // Identifies trigger source
      }
    });

    // Check if workflow execution started successfully
    if (executionResult.error) {
      console.error('Workflow execution error:', executionResult.error);
      return new Response(
        JSON.stringify({
          success: false,
          error: 'Failed to execute workflow',
          details: executionResult.error
        }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      );
    }

    console.log('Workflow execution started successfully');

    // Return success response with execution ID
    return new Response(
      JSON.stringify({
        success: true,
        message: 'Workflow execution started',
        execution_id: executionResult.data?.execution_id
      }),
      { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );

  } catch (error: any) {
    // Top-level error (parsing, database, etc.)
    console.error('Webhook error:', error);
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    );
  }
});

/**
 * Verifies webhook signature using HMAC SHA-256
 * Ensures the webhook request is from a trusted source
 * 
 * Process:
 * 1. Import webhook secret as HMAC key
 * 2. Convert hex signature to buffer
 * 3. Verify signature against payload
 * 
 * Signature Generation (sender side):
 * const signature = crypto.createHmac('sha256', secret)
 *   .update(JSON.stringify(payload))
 *   .digest('hex');
 * 
 * @param payload - The webhook payload as JSON string
 * @param signature - The HMAC signature from x-webhook-signature header (hex format)
 * @param secret - The webhook secret from trigger configuration
 * @returns true if signature is valid, false otherwise
 */
async function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): Promise<boolean> {
  try {
    const encoder = new TextEncoder();
    
    // Import secret as HMAC key
    const key = await crypto.subtle.importKey(
      'raw',
      encoder.encode(secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['verify']
    );

    // Convert hex signature to buffer
    const signatureBuffer = hexToBuffer(signature);
    const dataBuffer = encoder.encode(payload);

    // Verify signature
    return await crypto.subtle.verify(
      'HMAC',
      key,
      signatureBuffer,
      dataBuffer
    );
  } catch (error) {
    console.error('Signature verification error:', error);
    return false;
  }
}

/**
 * Converts a hex string to ArrayBuffer
 * Used for signature verification
 * 
 * Example:
 * hex = "48656c6c6f"
 * returns: ArrayBuffer containing [72, 101, 108, 108, 111]
 * 
 * @param hex - Hex string (e.g., "48656c6c6f")
 * @returns ArrayBuffer containing the binary data
 */
function hexToBuffer(hex: string): ArrayBuffer {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substr(i, 2), 16);
  }
  return bytes.buffer;
}
