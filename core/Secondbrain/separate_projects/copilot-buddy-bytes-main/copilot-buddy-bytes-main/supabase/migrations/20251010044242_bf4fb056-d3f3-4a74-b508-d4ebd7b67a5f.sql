-- Create projects table
CREATE TABLE public.projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  project_number TEXT NOT NULL UNIQUE,
  project_name TEXT NOT NULL,
  project_code TEXT,
  customer_account_id UUID REFERENCES public.customer_accounts(id),
  project_manager_id UUID REFERENCES public.employees(id),
  project_type TEXT NOT NULL DEFAULT 'internal',
  project_status TEXT NOT NULL DEFAULT 'planning',
  priority TEXT NOT NULL DEFAULT 'medium',
  start_date DATE,
  end_date DATE,
  estimated_hours NUMERIC,
  actual_hours NUMERIC DEFAULT 0,
  budget_amount NUMERIC,
  actual_cost NUMERIC DEFAULT 0,
  billing_type TEXT DEFAULT 'fixed_price',
  hourly_rate NUMERIC,
  description TEXT,
  objectives TEXT,
  deliverables TEXT,
  risks TEXT,
  is_billable BOOLEAN DEFAULT true,
  completion_percentage INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create project_tasks table
CREATE TABLE public.project_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  task_number TEXT NOT NULL,
  task_name TEXT NOT NULL,
  task_description TEXT,
  assigned_to UUID REFERENCES public.employees(id),
  task_status TEXT NOT NULL DEFAULT 'not_started',
  priority TEXT NOT NULL DEFAULT 'medium',
  parent_task_id UUID REFERENCES public.project_tasks(id),
  start_date DATE,
  due_date DATE,
  completed_date DATE,
  estimated_hours NUMERIC,
  actual_hours NUMERIC DEFAULT 0,
  completion_percentage INTEGER DEFAULT 0,
  is_billable BOOLEAN DEFAULT true,
  billing_rate NUMERIC,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create project_milestones table
CREATE TABLE public.project_milestones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  milestone_name TEXT NOT NULL,
  milestone_description TEXT,
  due_date DATE NOT NULL,
  completion_date DATE,
  milestone_status TEXT NOT NULL DEFAULT 'pending',
  deliverables TEXT,
  is_critical BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create project_team table
CREATE TABLE public.project_team (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  employee_id UUID NOT NULL REFERENCES public.employees(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  allocation_percentage INTEGER DEFAULT 100,
  hourly_rate NUMERIC,
  start_date DATE,
  end_date DATE,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(project_id, employee_id)
);

-- Create project_expenses table
CREATE TABLE public.project_expenses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  expense_type TEXT NOT NULL,
  expense_description TEXT NOT NULL,
  amount NUMERIC NOT NULL,
  expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
  vendor_id UUID REFERENCES public.vendors(id),
  is_billable BOOLEAN DEFAULT true,
  is_reimbursable BOOLEAN DEFAULT false,
  receipt_url TEXT,
  submitted_by UUID REFERENCES public.employees(id),
  approved_by UUID REFERENCES public.employees(id),
  approved_at TIMESTAMPTZ,
  expense_status TEXT NOT NULL DEFAULT 'pending',
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create project_time_entries table
CREATE TABLE public.project_time_entries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  task_id UUID REFERENCES public.project_tasks(id) ON DELETE SET NULL,
  employee_id UUID NOT NULL REFERENCES public.employees(id),
  entry_date DATE NOT NULL,
  start_time TIME,
  end_time TIME,
  hours NUMERIC NOT NULL,
  description TEXT,
  is_billable BOOLEAN DEFAULT true,
  billing_rate NUMERIC,
  billed_amount NUMERIC,
  is_approved BOOLEAN DEFAULT false,
  approved_by UUID REFERENCES public.employees(id),
  approved_at TIMESTAMPTZ,
  invoice_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create project_documents table
CREATE TABLE public.project_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  project_id UUID NOT NULL REFERENCES public.projects(id) ON DELETE CASCADE,
  document_name TEXT NOT NULL,
  document_type TEXT,
  file_url TEXT NOT NULL,
  file_size INTEGER,
  uploaded_by UUID REFERENCES public.employees(id),
  description TEXT,
  version TEXT DEFAULT '1.0',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create project number sequence and function
CREATE SEQUENCE project_number_seq;
CREATE OR REPLACE FUNCTION generate_project_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'PRJ' || TO_CHAR(NOW(), 'YYYYMM') || '-' || LPAD(nextval('project_number_seq')::TEXT, 4, '0');
END;
$$;

CREATE OR REPLACE FUNCTION set_project_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.project_number IS NULL OR NEW.project_number = '' THEN
    NEW.project_number := generate_project_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_project_number_trigger
BEFORE INSERT ON public.projects
FOR EACH ROW EXECUTE FUNCTION set_project_number();

-- Add update triggers
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON public.projects
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_tasks_updated_at BEFORE UPDATE ON public.project_tasks
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_milestones_updated_at BEFORE UPDATE ON public.project_milestones
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_team_updated_at BEFORE UPDATE ON public.project_team
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_expenses_updated_at BEFORE UPDATE ON public.project_expenses
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_time_entries_updated_at BEFORE UPDATE ON public.project_time_entries
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_project_documents_updated_at BEFORE UPDATE ON public.project_documents
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_milestones ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_team ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_time_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_documents ENABLE ROW LEVEL SECURITY;

-- RLS Policies for projects
CREATE POLICY "Users can view projects in their organization"
ON public.projects FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create projects"
ON public.projects FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can update projects in their organization"
ON public.projects FOR UPDATE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- RLS Policies for project_tasks
CREATE POLICY "Users can view tasks in their organization"
ON public.project_tasks FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create tasks"
ON public.project_tasks FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can update tasks in their organization"
ON public.project_tasks FOR UPDATE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- RLS Policies for project_milestones
CREATE POLICY "Users can view milestones in their organization"
ON public.project_milestones FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can manage milestones"
ON public.project_milestones FOR ALL
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- RLS Policies for project_team
CREATE POLICY "Users can view team members in their organization"
ON public.project_team FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can manage team members"
ON public.project_team FOR ALL
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- RLS Policies for project_expenses
CREATE POLICY "Users can view expenses in their organization"
ON public.project_expenses FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create expenses"
ON public.project_expenses FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can update expenses in their organization"
ON public.project_expenses FOR UPDATE
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- RLS Policies for project_time_entries
CREATE POLICY "Users can view time entries in their organization"
ON public.project_time_entries FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can create time entries"
ON public.project_time_entries FOR INSERT
WITH CHECK (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can update their own time entries"
ON public.project_time_entries FOR UPDATE
USING (
  customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ) AND (
    employee_id IN (SELECT id FROM employees WHERE user_id = auth.uid()) OR
    has_role(auth.uid(), 'admin'::app_role)
  )
);

-- RLS Policies for project_documents
CREATE POLICY "Users can view documents in their organization"
ON public.project_documents FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can manage documents"
ON public.project_documents FOR ALL
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

-- Create indexes for performance
CREATE INDEX idx_projects_customer_id ON public.projects(customer_id);
CREATE INDEX idx_projects_project_manager ON public.projects(project_manager_id);
CREATE INDEX idx_projects_customer_account ON public.projects(customer_account_id);
CREATE INDEX idx_project_tasks_project ON public.project_tasks(project_id);
CREATE INDEX idx_project_tasks_assigned_to ON public.project_tasks(assigned_to);
CREATE INDEX idx_project_milestones_project ON public.project_milestones(project_id);
CREATE INDEX idx_project_team_project ON public.project_team(project_id);
CREATE INDEX idx_project_team_employee ON public.project_team(employee_id);
CREATE INDEX idx_project_expenses_project ON public.project_expenses(project_id);
CREATE INDEX idx_project_time_entries_project ON public.project_time_entries(project_id);
CREATE INDEX idx_project_time_entries_employee ON public.project_time_entries(employee_id);