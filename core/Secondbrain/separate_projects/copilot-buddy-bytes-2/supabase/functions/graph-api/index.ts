import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.38.4";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!;
    const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Get the user's session
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      console.error('Missing authorization header');
      return new Response(
        JSON.stringify({ 
          error: 'Authentication required',
          code: 'NO_AUTH_HEADER'
        }), 
        { 
          status: 401, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    const token = authHeader.replace('Bearer ', '');
    const { data: { user }, error: userError } = await supabase.auth.getUser(token);
    
    if (userError || !user) {
      console.error('Invalid user token:', userError);
      return new Response(
        JSON.stringify({ 
          error: 'Invalid authentication token',
          code: 'INVALID_TOKEN'
        }), 
        { 
          status: 401, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    const { endpoint, method = 'GET', body } = await req.json();
    console.log(`User ${user.id} requesting: ${method} ${endpoint}`);

    // Check if user signed in with Azure (Microsoft 365)
    const provider = user.app_metadata?.provider;
    if (provider !== 'azure') {
      console.warn(`User signed in with ${provider}, not Microsoft 365`);
      return new Response(
        JSON.stringify({ 
          error: 'Please sign in with Microsoft 365 to access this feature',
          code: 'WRONG_PROVIDER',
          current_provider: provider
        }), 
        { 
          status: 403, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    // Get the provider access token
    const providerToken = user.user_metadata?.provider_token;
    const providerRefreshToken = user.user_metadata?.provider_refresh_token;

    if (!providerToken) {
      console.error('No provider token found for user:', user.id);
      return new Response(
        JSON.stringify({ 
          error: 'Microsoft access token not found. Please sign out and sign in again with Microsoft 365.',
          code: 'NO_PROVIDER_TOKEN',
          hint: 'Try signing out and signing back in with Microsoft 365'
        }), 
        { 
          status: 401, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    console.log(`Making Graph API request to: https://graph.microsoft.com/v1.0${endpoint}`);

    // Make the Graph API request with retry logic
    let graphResponse = await fetch(`https://graph.microsoft.com/v1.0${endpoint}`, {
      method,
      headers: {
        'Authorization': `Bearer ${providerToken}`,
        'Content-Type': 'application/json',
      },
      body: body ? JSON.stringify(body) : undefined,
    });

    // Handle token expiration with detailed error
    if (!graphResponse.ok) {
      const errorText = await graphResponse.text();
      console.error(`Graph API error: ${graphResponse.status} - ${errorText}`);
      
      if (graphResponse.status === 401) {
        // Token expired or invalid
        return new Response(
          JSON.stringify({ 
            error: 'Your Microsoft 365 session has expired. Please sign out and sign in again.',
            code: 'TOKEN_EXPIRED',
            status: graphResponse.status,
            details: errorText,
            action_required: 'Sign out and sign back in with Microsoft 365'
          }), 
          { 
            status: 401, 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
          }
        );
      }

      if (graphResponse.status === 403) {
        // Permission issue
        return new Response(
          JSON.stringify({ 
            error: 'Permission denied. Administrator needs to grant consent for this permission in Azure AD.',
            code: 'PERMISSION_DENIED',
            status: graphResponse.status,
            details: errorText,
            action_required: 'Contact your Azure AD administrator to grant consent'
          }), 
          { 
            status: 403, 
            headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
          }
        );
      }

      if (graphResponse.status === 429) {
        // Rate limit
        const retryAfter = graphResponse.headers.get('Retry-After') || '60';
        return new Response(
          JSON.stringify({ 
            error: 'Microsoft API rate limit exceeded. Please try again later.',
            code: 'RATE_LIMIT',
            retry_after: retryAfter,
            status: graphResponse.status
          }), 
          { 
            status: 429, 
            headers: { 
              ...corsHeaders, 
              'Content-Type': 'application/json',
              'Retry-After': retryAfter
            } 
          }
        );
      }
      
      // Other errors
      return new Response(
        JSON.stringify({ 
          error: `Microsoft Graph API error: ${graphResponse.status}`,
          code: 'GRAPH_API_ERROR',
          status: graphResponse.status,
          details: errorText
        }),
        { 
          status: graphResponse.status, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      );
    }

    const data = await graphResponse.json();
    console.log(`Successfully retrieved data from: ${endpoint}`);

    return new Response(
      JSON.stringify(data),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  } catch (error) {
    console.error('Unexpected error in graph-api function:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    const errorStack = error instanceof Error ? error.stack : undefined;
    
    return new Response(
      JSON.stringify({ 
        error: errorMessage,
        code: 'INTERNAL_ERROR',
        stack: Deno.env.get('ENVIRONMENT') === 'development' ? errorStack : undefined
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    );
  }
});
