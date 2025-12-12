import "https://deno.land/x/xhr@0.1.0/mod.ts";
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { dataType } = await req.json();
    
    console.log('Revio data request:', { dataType });

    // TODO: Implement actual Revio API calls when going live
    // const revioApiKey = Deno.env.get('REVIO_API_KEY');
    // const revioApiUrl = Deno.env.get('REVIO_API_URL');
    
    // Placeholder response structure - matches expected Revio data format
    const placeholderData = {
      customers_by_ticket: [
        { status: 'Open', count: 12, customers: [] },
        { status: 'In Progress', count: 8, customers: [] },
        { status: 'Resolved', count: 45, customers: [] }
      ],
      customers_by_sla: [
        { sla_tier: 'Premium', count: 23, customers: [] },
        { sla_tier: 'Standard', count: 34, customers: [] },
        { sla_tier: 'Basic', count: 8, customers: [] }
      ],
      customers_by_revenue: [
        { revenue_tier: 'High (>$10k/mo)', count: 15, total_revenue: 245000, customers: [] },
        { revenue_tier: 'Medium ($5k-$10k/mo)', count: 28, total_revenue: 198000, customers: [] },
        { revenue_tier: 'Low (<$5k/mo)', count: 22, total_revenue: 67000, customers: [] }
      ],
      subscriptions: {
        active: 65,
        trial: 8,
        churned: 12
      },
      recent_interactions: [
        {
          customer_name: 'Demo Customer',
          interaction_type: 'payment_received',
          amount: 1500,
          timestamp: new Date().toISOString()
        }
      ],
      invoices: [
        {
          id: 'INV-001',
          invoice_number: 'INV-2025-001',
          customer_name: 'Acme Corporation',
          customer_id: 'CUST-001',
          amount: 15000,
          status: 'paid',
          issue_date: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
          due_date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          paid_date: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
          description: 'Monthly Managed Services - Enterprise Plan',
          line_items: [
            { description: 'Enterprise Support', quantity: 1, unit_price: 10000, total: 10000 },
            { description: 'Premium SLA', quantity: 1, unit_price: 5000, total: 5000 }
          ]
        },
        {
          id: 'INV-002',
          invoice_number: 'INV-2025-002',
          customer_name: 'TechStart Inc',
          customer_id: 'CUST-002',
          amount: 7500,
          status: 'pending',
          issue_date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          due_date: new Date(Date.now() + 10 * 24 * 60 * 60 * 1000).toISOString(),
          description: 'Monthly Managed Services - Professional Plan',
          line_items: [
            { description: 'Professional Support', quantity: 1, unit_price: 5000, total: 5000 },
            { description: 'Cloud Services', quantity: 1, unit_price: 2500, total: 2500 }
          ]
        },
        {
          id: 'INV-003',
          invoice_number: 'INV-2025-003',
          customer_name: 'Global Systems LLC',
          customer_id: 'CUST-003',
          amount: 22000,
          status: 'overdue',
          issue_date: new Date(Date.now() - 45 * 24 * 60 * 60 * 1000).toISOString(),
          due_date: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
          description: 'Quarterly Enterprise Services',
          line_items: [
            { description: 'Enterprise Support (3 months)', quantity: 3, unit_price: 7000, total: 21000 },
            { description: 'Setup Fee', quantity: 1, unit_price: 1000, total: 1000 }
          ]
        },
        {
          id: 'INV-004',
          invoice_number: 'INV-2025-004',
          customer_name: 'DataFlow Partners',
          customer_id: 'CUST-004',
          amount: 4500,
          status: 'paid',
          issue_date: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000).toISOString(),
          due_date: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
          paid_date: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString(),
          description: 'Monthly Managed Services - Standard Plan',
          line_items: [
            { description: 'Standard Support', quantity: 1, unit_price: 3000, total: 3000 },
            { description: 'Monitoring Services', quantity: 1, unit_price: 1500, total: 1500 }
          ]
        },
        {
          id: 'INV-005',
          invoice_number: 'INV-2025-005',
          customer_name: 'Innovation Labs',
          customer_id: 'CUST-005',
          amount: 12500,
          status: 'pending',
          issue_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          due_date: new Date(Date.now() + 28 * 24 * 60 * 60 * 1000).toISOString(),
          description: 'Monthly Managed Services - Professional Plan',
          line_items: [
            { description: 'Professional Support', quantity: 1, unit_price: 8000, total: 8000 },
            { description: 'Security Services', quantity: 1, unit_price: 4500, total: 4500 }
          ]
        }
      ]
    };

    return new Response(
      JSON.stringify({ 
        success: true, 
        data: placeholderData,
        message: 'Using placeholder data - Revio integration pending'
      }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200 
      }
    );

  } catch (error) {
    console.error('Error in revio-data function:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
    return new Response(
      JSON.stringify({ 
        error: errorMessage,
        success: false 
      }),
      { 
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    );
  }
});

/* 
 * REVIO API INTEGRATION - TO BE IMPLEMENTED
 * 
 * When going live with Revio, implement these endpoints:
 * 
 * 1. GET /customers - List all customers with filters
 * 2. GET /customers/{id}/tickets - Get customer tickets
 * 3. GET /customers/{id}/subscriptions - Get customer subscriptions
 * 4. GET /customers/{id}/invoices - Get customer invoices
 * 5. GET /analytics/revenue - Revenue analytics
 * 
 * Required environment variables:
 * - REVIO_API_KEY: API authentication key
 * - REVIO_API_URL: Base URL for Revio API
 * 
 * Sample API call structure:
 * 
 * const response = await fetch(`${revioApiUrl}/customers`, {
 *   method: 'GET',
 *   headers: {
 *     'Authorization': `Bearer ${revioApiKey}`,
 *     'Content-Type': 'application/json',
 *   }
 * });
 * 
 * const customers = await response.json();
 */
