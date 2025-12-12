-- Vendor Contracts
CREATE TABLE public.vendor_contracts (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  vendor_id UUID NOT NULL REFERENCES public.vendors(id) ON DELETE CASCADE,
  contract_number TEXT NOT NULL,
  contract_name TEXT NOT NULL,
  contract_type TEXT NOT NULL CHECK (contract_type IN ('service', 'purchase', 'maintenance', 'subscription', 'lease', 'other')),
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'expired', 'terminated', 'renewal_pending')),
  start_date DATE NOT NULL,
  end_date DATE,
  contract_value NUMERIC,
  payment_schedule TEXT CHECK (payment_schedule IN ('one_time', 'monthly', 'quarterly', 'annually', 'milestone')),
  auto_renew BOOLEAN DEFAULT false,
  renewal_notice_days INTEGER DEFAULT 30,
  terms TEXT,
  notes TEXT,
  document_url TEXT,
  signed_by UUID,
  signed_date DATE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID NOT NULL,
  UNIQUE(customer_id, contract_number)
);

ALTER TABLE public.vendor_contracts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view contracts in their organization"
  ON public.vendor_contracts FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage contracts"
  ON public.vendor_contracts FOR ALL
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Contract number sequence and trigger
CREATE SEQUENCE IF NOT EXISTS vendor_contract_seq;

CREATE OR REPLACE FUNCTION public.generate_contract_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'VC' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(nextval('vendor_contract_seq')::TEXT, 4, '0');
END;
$$;

CREATE OR REPLACE FUNCTION public.set_contract_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.contract_number IS NULL OR NEW.contract_number = '' THEN
    NEW.contract_number := generate_contract_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_contract_number_trigger
  BEFORE INSERT ON public.vendor_contracts
  FOR EACH ROW
  EXECUTE FUNCTION public.set_contract_number();

CREATE TRIGGER update_vendor_contracts_updated_at
  BEFORE UPDATE ON public.vendor_contracts
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();