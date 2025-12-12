# Revio Integration API Reference

## Overview

The Revio integration provides customer billing and revenue data to the OberaConnect platform. The integration is designed to work with the Revio API once the platform migrates from OneBill.

**Current Status**: Infrastructure complete with placeholder data. Live API integration pending OneBill → Revio migration.

---

## Edge Function: revio-data

**Endpoint**: `revio-data`

**Purpose**: Fetch customer billing and revenue data from Revio API

**Current Behavior**: Returns structured placeholder data until live Revio API is connected

### Request

```typescript
const { data, error } = await supabase.functions.invoke('revio-data', {
  body: {
    dataType: 'all' | 'customers_by_ticket' | 'customers_by_sla' | 'customers_by_revenue' | 'subscriptions' | 'recent_interactions'
  }
});
```

### Response Structure

```typescript
{
  success: boolean;
  message?: string;
  data: {
    customers_by_ticket: CustomersByTicket[];
    customers_by_sla: CustomersBySLA[];
    customers_by_revenue: CustomersByRevenue[];
    subscriptions: SubscriptionStats;
    recent_interactions: CustomerInteraction[];
  }
}
```

### Data Types

#### CustomersByTicket
```typescript
interface CustomersByTicket {
  status: string;  // 'open', 'in_progress', 'resolved'
  count: number;
  customers: RevioCustomer[];
}
```

#### CustomersBySLA
```typescript
interface CustomersBySLA {
  sla_tier: string;  // 'platinum', 'gold', 'silver', 'bronze'
  count: number;
  customers: RevioCustomer[];
}
```

#### CustomersByRevenue
```typescript
interface CustomersByRevenue {
  revenue_tier: string;  // 'enterprise', 'mid_market', 'smb'
  count: number;
  total_revenue: number;
  customers: RevioCustomer[];
}
```

#### SubscriptionStats
```typescript
interface SubscriptionStats {
  active: number;
  trial: number;
  churned: number;
}
```

#### CustomerInteraction
```typescript
interface CustomerInteraction {
  customer_name: string;
  interaction_type: 'payment_received' | 'ticket_created' | 'subscription_upgraded' | 'subscription_downgraded';
  amount?: number;
  timestamp: string;
  details?: string;
}
```

#### RevioCustomer
```typescript
interface RevioCustomer {
  id: string;
  name: string;
  email: string;
  company?: string;
  subscription_tier?: string;
  monthly_revenue?: number;
  sla_tier?: string;
  status: 'active' | 'trial' | 'churned';
}
```

---

## React Hook: useRevioData

**Location**: `src/hooks/useRevioData.tsx`

**Purpose**: Convenience hook for fetching Revio data in components

### Usage

```typescript
import { useRevioData } from '@/hooks/useRevioData';

const MyComponent = () => {
  const { data, loading, error, refetch } = useRevioData();

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Active Subscriptions: {data?.subscriptions.active}</h2>
      <h2>Total Revenue: ${data?.customers_by_revenue.reduce((sum, tier) => sum + tier.total_revenue, 0)}</h2>
    </div>
  );
};
```

### Return Values

```typescript
{
  data: RevioDataResponse | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}
```

---

## Sales Dashboard Integration

The Revio data is displayed in the Sales Dashboard with the following breakdowns:

### Customers by Ticket Status
- Visual card showing open, in progress, and resolved ticket counts
- Customer list grouped by ticket status

### Customers by SLA Tier
- Distribution across platinum, gold, silver, bronze tiers
- Revenue implications by tier

### Customers by Revenue
- Enterprise, mid-market, and SMB segmentation
- Total revenue by segment
- Customer count by revenue tier

### Recent Interactions
- Timeline of customer activities
- Payment receipts
- Ticket creation events
- Subscription changes (upgrades/downgrades)

---

## Migration to Live Revio API

When ready to connect to the live Revio API:

1. **Add Revio API Credentials**
   ```bash
   # Using Lovable Cloud secrets management
   REVIO_API_KEY=your_api_key_here
   REVIO_API_URL=https://api.revio.com/v1
   ```

2. **Update Edge Function**
   - Replace placeholder data in `supabase/functions/revio-data/index.ts`
   - Implement actual Revio API calls
   - Add error handling and retry logic
   - Implement caching for performance

3. **API Endpoints to Implement**
   - `GET /customers` - Fetch all customers
   - `GET /customers/:id/tickets` - Customer ticket data
   - `GET /customers/:id/subscription` - Subscription details
   - `GET /customers/:id/sla` - SLA tier information
   - `GET /transactions` - Recent payment transactions
   - `GET /analytics/revenue` - Revenue aggregation

4. **Data Mapping**
   - Map Revio customer fields to `RevioCustomer` type
   - Transform SLA data to match expected tiers
   - Calculate revenue segmentation based on actual values

5. **Testing**
   - Validate data structure matches type definitions
   - Test error scenarios (API down, rate limiting)
   - Verify dashboard displays correctly with live data
   - Load testing for performance

---

## Security Considerations

- **API Key Storage**: Use Lovable Cloud secrets, never hardcode
- **Data Caching**: Implement caching to reduce API calls and costs
- **Rate Limiting**: Respect Revio API rate limits
- **Error Handling**: Graceful degradation when API is unavailable
- **Audit Logging**: Log all Revio data access for compliance

---

## Performance Optimization

- **Caching Strategy**: Cache frequently accessed data (5-15 minutes)
- **Incremental Updates**: Only fetch changed data when possible
- **Lazy Loading**: Load detailed customer data on-demand
- **Pagination**: Implement pagination for large customer lists

---

## Documentation

For detailed implementation guide, see: `REVIO_INTEGRATION_GUIDE.md`

For troubleshooting and common issues, see: `URGENT_NEXT_STEPS.md` (Revio section)
