# Revio Integration Guide

## Current Status
✅ Infrastructure code is ready  
⏳ Pending actual Revio API connection (currently using OneBill)

## Overview
The Revio integration infrastructure is set up to display customer data segmented by:
- **Tickets** - Customer support ticket status
- **SLA** - Service Level Agreement tiers
- **Revenue** - Monthly revenue brackets

## Files Created

### 1. Edge Function: `supabase/functions/revio-data/index.ts`
- Handles all Revio API communication
- Currently returns placeholder data
- Ready to accept real API calls

### 2. Type Definitions: `src/types/revio.ts`
- TypeScript interfaces for Revio data structures
- Defines customer, subscription, and interaction types

### 3. React Hook: `src/hooks/useRevioData.tsx`
- Simplifies data fetching in components
- Handles loading and error states
- Provides refetch functionality

## When Going Live with Revio

### Step 1: Add Revio API Credentials
```bash
# Add these secrets via Lovable Cloud backend
REVIO_API_KEY=your_api_key_here
REVIO_API_URL=https://api.revio.com/v1
```

### Step 2: Implement API Calls
Update `supabase/functions/revio-data/index.ts`:

1. Uncomment the API key retrieval:
```typescript
const revioApiKey = Deno.env.get('REVIO_API_KEY');
const revioApiUrl = Deno.env.get('REVIO_API_URL');
```

2. Replace placeholder data with real API calls:
```typescript
// Example: Fetch customers by ticket status
const ticketResponse = await fetch(`${revioApiUrl}/customers/tickets`, {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${revioApiKey}`,
    'Content-Type': 'application/json',
  }
});

const ticketData = await ticketResponse.json();
```

### Step 3: Update Sales Dashboard
The `SalesDashboard.tsx` component is ready to consume real data.  
Simply import and use the `useRevioData` hook when ready:

```typescript
import { useRevioData } from '@/hooks/useRevioData';

// In component
const { data, loading, error } = useRevioData();
```

## API Endpoints to Implement

Based on requirements, implement these Revio API endpoints:

1. **GET `/customers`** - List all customers with filters
   - Query params: `status`, `sla_tier`, `revenue_bracket`

2. **GET `/customers/{id}/tickets`** - Get customer tickets
   - Returns: ticket status, priority, timestamps

3. **GET `/customers/{id}/subscriptions`** - Get customer subscriptions
   - Returns: plan details, billing cycle, status

4. **GET `/analytics/revenue`** - Revenue analytics
   - Query params: `start_date`, `end_date`, `group_by`

5. **GET `/interactions/recent`** - Recent customer interactions
   - Returns: payment events, support tickets, upgrades

## Data Structure Expected

The edge function expects this response format:

```typescript
{
  customers_by_ticket: [
    { status: string, count: number, customers: RevioCustomer[] }
  ],
  customers_by_sla: [
    { sla_tier: string, count: number, customers: RevioCustomer[] }
  ],
  customers_by_revenue: [
    { 
      revenue_tier: string, 
      count: number, 
      total_revenue: number,
      customers: RevioCustomer[] 
    }
  ],
  subscriptions: {
    active: number,
    trial: number,
    churned: number
  },
  recent_interactions: CustomerInteraction[]
}
```

## Testing

1. **With Placeholder Data** (Current):
   - Dashboard displays mock data
   - No API calls made

2. **With Real Revio API**:
   - Test with Revio sandbox/staging environment first
   - Verify data structure matches expected format
   - Check error handling for failed API calls

## Migration from OneBill

When transitioning from OneBill to Revio:

1. Keep both systems running in parallel initially
2. Map OneBill data fields to Revio equivalents
3. Update any OneBill-specific logic in the codebase
4. Test data accuracy between systems
5. Switch over to Revio once validated

## Security Notes

- ✅ API keys stored securely in Lovable Cloud secrets
- ✅ Never expose API keys in frontend code
- ✅ All API calls go through edge function
- ✅ CORS properly configured for web app

## Support

For questions about:
- **Revio API**: Check Revio API documentation
- **Integration Code**: See inline comments in `supabase/functions/revio-data/index.ts`
- **TypeScript Types**: Review `src/types/revio.ts`
