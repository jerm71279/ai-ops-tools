// Revio data type definitions

export interface RevioCustomer {
  id: string;
  name: string;
  email: string;
  company?: string;
  subscription_tier?: string;
  monthly_revenue?: number;
  sla_tier?: string;
  status: 'active' | 'trial' | 'churned';
}

export interface CustomersByTicket {
  status: string;
  count: number;
  customers: RevioCustomer[];
}

export interface CustomersBySLA {
  sla_tier: string;
  count: number;
  customers: RevioCustomer[];
}

export interface CustomersByRevenue {
  revenue_tier: string;
  count: number;
  total_revenue: number;
  customers: RevioCustomer[];
}

export interface SubscriptionStats {
  active: number;
  trial: number;
  churned: number;
}

export interface CustomerInteraction {
  customer_name: string;
  interaction_type: 'payment_received' | 'ticket_created' | 'subscription_upgraded' | 'subscription_downgraded';
  amount?: number;
  timestamp: string;
  details?: string;
}

export interface RevioInvoice {
  id: string;
  invoice_number: string;
  customer_name: string;
  customer_id: string;
  amount: number;
  status: 'paid' | 'pending' | 'overdue' | 'draft';
  issue_date: string;
  due_date: string;
  paid_date?: string;
  description: string;
  line_items?: Array<{
    description: string;
    quantity: number;
    unit_price: number;
    total: number;
  }>;
}

export interface RevioDataResponse {
  customers_by_ticket: CustomersByTicket[];
  customers_by_sla: CustomersBySLA[];
  customers_by_revenue: CustomersByRevenue[];
  subscriptions: SubscriptionStats;
  recent_interactions: CustomerInteraction[];
  invoices: RevioInvoice[];
}
