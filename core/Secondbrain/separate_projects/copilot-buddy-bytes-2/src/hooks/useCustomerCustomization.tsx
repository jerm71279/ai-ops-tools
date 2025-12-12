import { useEffect, useState } from 'react';
import { supabase } from '@/integrations/supabase/client';

export interface CustomerCustomization {
  id: string;
  customer_id: string;
  company_logo_url: string | null;
  primary_color: string;
  secondary_color: string;
  accent_color: string;
  enabled_integrations: string[];
  enabled_features: string[];
  default_dashboard: string;
  dashboard_layout: Record<string, any>;
  custom_settings: Record<string, any>;
  enabled_portals?: string[];
  enabled_modules?: Record<string, boolean>;
}

export const useCustomerCustomization = (customerId?: string) => {
  const [customization, setCustomization] = useState<CustomerCustomization | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchCustomization = async () => {
      if (!customerId) {
        setIsLoading(false);
        return;
      }

      try {
        const { data, error } = await supabase
          .from('customer_customizations')
          .select('*')
          .eq('customer_id', customerId)
          .single();

        if (error) throw error;
        setCustomization(data as CustomerCustomization);
      } catch (error) {
        console.error('Error fetching customization:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCustomization();
  }, [customerId]);

  const applyCustomization = (customization: CustomerCustomization) => {
    // Apply theme colors to CSS variables
    const root = document.documentElement;
    root.style.setProperty('--primary', customization.primary_color);
    root.style.setProperty('--secondary', customization.secondary_color);
    root.style.setProperty('--accent', customization.accent_color);
  };

  useEffect(() => {
    if (customization) {
      applyCustomization(customization);
    }
  }, [customization]);

  return { customization, isLoading };
};
