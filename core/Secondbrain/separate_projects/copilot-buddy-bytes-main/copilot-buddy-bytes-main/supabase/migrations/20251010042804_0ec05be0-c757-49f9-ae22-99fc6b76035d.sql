-- Vendors
CREATE TABLE public.vendors (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  vendor_code TEXT NOT NULL UNIQUE,
  vendor_name TEXT NOT NULL,
  vendor_type TEXT NOT NULL CHECK (vendor_type IN ('supplier', 'manufacturer', 'distributor', 'contractor', 'consultant', 'other')),
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'pending', 'suspended', 'blocked')),
  contact_name TEXT,
  contact_email TEXT,
  contact_phone TEXT,
  website TEXT,
  address TEXT,
  city TEXT,
  state TEXT,
  postal_code TEXT,
  country TEXT DEFAULT 'USA',
  tax_id TEXT,
  payment_terms TEXT,
  preferred_payment_method TEXT,
  credit_limit NUMERIC(12,2),
  current_balance NUMERIC(12,2) DEFAULT 0,
  performance_score INTEGER DEFAULT 0,
  on_time_delivery_rate NUMERIC(5,2),
  quality_rating NUMERIC(3,2),
  certifications JSONB DEFAULT '[]'::jsonb,
  insurance_info JSONB DEFAULT '{}'::jsonb,
  contract_start_date DATE,
  contract_end_date DATE,
  notes TEXT,
  tags TEXT[],
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  created_by UUID NOT NULL
);

ALTER TABLE public.vendors ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view vendors in their organization"
  ON public.vendors FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage vendors"
  ON public.vendors FOR ALL
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Vendor Performance History
CREATE TABLE public.vendor_performance (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  vendor_id UUID NOT NULL REFERENCES public.vendors(id) ON DELETE CASCADE,
  evaluation_date DATE NOT NULL,
  evaluator_id UUID NOT NULL,
  delivery_score INTEGER CHECK (delivery_score BETWEEN 1 AND 100),
  quality_score INTEGER CHECK (quality_score BETWEEN 1 AND 100),
  communication_score INTEGER CHECK (communication_score BETWEEN 1 AND 100),
  pricing_score INTEGER CHECK (pricing_score BETWEEN 1 AND 100),
  overall_score INTEGER CHECK (overall_score BETWEEN 1 AND 100),
  comments TEXT,
  issues_reported TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

ALTER TABLE public.vendor_performance ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view vendor performance"
  ON public.vendor_performance FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage vendor performance"
  ON public.vendor_performance FOR ALL
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Inventory Items
CREATE TABLE public.inventory_items (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  sku TEXT NOT NULL,
  item_name TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL,
  subcategory TEXT,
  unit_of_measure TEXT NOT NULL DEFAULT 'each',
  current_quantity INTEGER NOT NULL DEFAULT 0,
  minimum_quantity INTEGER DEFAULT 0,
  reorder_point INTEGER DEFAULT 0,
  reorder_quantity INTEGER DEFAULT 0,
  maximum_quantity INTEGER,
  unit_cost NUMERIC(10,2),
  unit_price NUMERIC(10,2),
  location TEXT,
  warehouse_id UUID,
  bin_location TEXT,
  vendor_id UUID REFERENCES public.vendors(id),
  lead_time_days INTEGER DEFAULT 0,
  last_restock_date DATE,
  last_count_date DATE,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'discontinued', 'out_of_stock', 'backordered')),
  barcode TEXT,
  serial_numbers TEXT[],
  batch_numbers TEXT[],
  expiry_date DATE,
  attributes JSONB DEFAULT '{}'::jsonb,
  images TEXT[],
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(customer_id, sku)
);

ALTER TABLE public.inventory_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view inventory in their organization"
  ON public.inventory_items FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage inventory"
  ON public.inventory_items FOR ALL
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Inventory Transactions
CREATE TABLE public.inventory_transactions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  inventory_item_id UUID NOT NULL REFERENCES public.inventory_items(id) ON DELETE CASCADE,
  transaction_type TEXT NOT NULL CHECK (transaction_type IN ('purchase', 'sale', 'adjustment', 'transfer', 'return', 'waste', 'count')),
  quantity INTEGER NOT NULL,
  unit_cost NUMERIC(10,2),
  total_cost NUMERIC(12,2),
  reference_type TEXT,
  reference_id UUID,
  from_location TEXT,
  to_location TEXT,
  reason TEXT,
  notes TEXT,
  performed_by UUID NOT NULL,
  transaction_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

ALTER TABLE public.inventory_transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view inventory transactions"
  ON public.inventory_transactions FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can create inventory transactions"
  ON public.inventory_transactions FOR INSERT
  WITH CHECK (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()) AND performed_by = auth.uid());

-- Warehouses
CREATE TABLE public.warehouses (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL,
  warehouse_code TEXT NOT NULL,
  warehouse_name TEXT NOT NULL,
  warehouse_type TEXT CHECK (warehouse_type IN ('main', 'distribution', 'retail', 'virtual')),
  address TEXT NOT NULL,
  city TEXT,
  state TEXT,
  postal_code TEXT,
  country TEXT DEFAULT 'USA',
  manager_id UUID,
  capacity_sqft INTEGER,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance')),
  operating_hours TEXT,
  contact_phone TEXT,
  contact_email TEXT,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(customer_id, warehouse_code)
);

ALTER TABLE public.warehouses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view warehouses"
  ON public.warehouses FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can manage warehouses"
  ON public.warehouses FOR ALL
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- Purchase Orders link to Vendors (already exists, add foreign key)
ALTER TABLE public.purchase_orders ADD COLUMN IF NOT EXISTS vendor_id_fk UUID REFERENCES public.vendors(id);

-- Reorder Alerts View
CREATE OR REPLACE VIEW public.inventory_reorder_alerts AS
SELECT 
  ii.id,
  ii.customer_id,
  ii.sku,
  ii.item_name,
  ii.current_quantity,
  ii.reorder_point,
  ii.reorder_quantity,
  ii.vendor_id,
  v.vendor_name,
  v.contact_email as vendor_email,
  ii.lead_time_days,
  ii.location,
  (ii.reorder_point - ii.current_quantity) as shortage_quantity,
  CASE 
    WHEN ii.current_quantity <= 0 THEN 'critical'
    WHEN ii.current_quantity <= (ii.reorder_point * 0.5) THEN 'urgent'
    WHEN ii.current_quantity <= ii.reorder_point THEN 'low'
    ELSE 'normal'
  END as alert_level
FROM public.inventory_items ii
LEFT JOIN public.vendors v ON v.id = ii.vendor_id
WHERE ii.current_quantity <= ii.reorder_point
  AND ii.status = 'active';

-- Auto-generate vendor codes
CREATE SEQUENCE IF NOT EXISTS vendor_code_seq;

CREATE OR REPLACE FUNCTION public.generate_vendor_code()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'VEN' || LPAD(nextval('vendor_code_seq')::TEXT, 6, '0');
END;
$$;

CREATE OR REPLACE FUNCTION public.set_vendor_code()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.vendor_code IS NULL OR NEW.vendor_code = '' THEN
    NEW.vendor_code := generate_vendor_code();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_vendor_code_trigger
  BEFORE INSERT ON public.vendors
  FOR EACH ROW
  EXECUTE FUNCTION public.set_vendor_code();

-- Updated_at triggers
CREATE TRIGGER update_vendors_updated_at
  BEFORE UPDATE ON public.vendors
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_inventory_items_updated_at
  BEFORE UPDATE ON public.inventory_items
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_warehouses_updated_at
  BEFORE UPDATE ON public.warehouses
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();