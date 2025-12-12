import { useState, useEffect } from 'react';
import { supabase } from '@/integrations/supabase/client';
import { RevioDataResponse } from '@/types/revio';
import { toast } from 'sonner';

export const useRevioData = () => {
  const [data, setData] = useState<RevioDataResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRevioData = async () => {
    try {
      setLoading(true);
      setError(null);

      const { data: responseData, error: functionError } = await supabase.functions.invoke('revio-data', {
        body: { dataType: 'all' }
      });

      if (functionError) {
        throw functionError;
      }

      if (responseData?.success) {
        setData(responseData.data);
        
        // Show info toast if using placeholder data
        if (responseData.message?.includes('placeholder')) {
          console.log('Using Revio placeholder data - actual integration pending');
        }
      } else {
        throw new Error(responseData?.error || 'Failed to fetch Revio data');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch Revio data';
      setError(errorMessage);
      console.error('Revio data fetch error:', err);
      toast.error('Failed to load customer data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRevioData();
  }, []);

  return {
    data,
    loading,
    error,
    refetch: fetchRevioData
  };
};
