-- Create departments table
CREATE TABLE public.departments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  department_name TEXT NOT NULL,
  department_code TEXT NOT NULL,
  parent_department_id UUID REFERENCES public.departments(id),
  manager_id UUID,
  budget_allocation NUMERIC,
  cost_center TEXT,
  location TEXT,
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(customer_id, department_code)
);

-- Create employees table
CREATE TABLE public.employees (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  user_id UUID REFERENCES auth.users(id),
  employee_number TEXT NOT NULL UNIQUE,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT,
  department_id UUID REFERENCES public.departments(id),
  job_title TEXT NOT NULL,
  employment_type TEXT NOT NULL DEFAULT 'full_time',
  employment_status TEXT NOT NULL DEFAULT 'active',
  hire_date DATE NOT NULL,
  termination_date DATE,
  manager_id UUID REFERENCES public.employees(id),
  work_location TEXT,
  salary NUMERIC,
  hourly_rate NUMERIC,
  emergency_contact_name TEXT,
  emergency_contact_phone TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create performance_reviews table
CREATE TABLE public.performance_reviews (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  employee_id UUID NOT NULL REFERENCES public.employees(id) ON DELETE CASCADE,
  reviewer_id UUID NOT NULL REFERENCES public.employees(id),
  review_period_start DATE NOT NULL,
  review_period_end DATE NOT NULL,
  review_date DATE NOT NULL,
  review_type TEXT NOT NULL DEFAULT 'annual',
  overall_rating INTEGER,
  performance_score NUMERIC,
  strengths TEXT,
  areas_for_improvement TEXT,
  goals_achieved TEXT,
  goals_next_period TEXT,
  reviewer_comments TEXT,
  employee_comments TEXT,
  review_status TEXT NOT NULL DEFAULT 'draft',
  signed_by_employee_at TIMESTAMPTZ,
  signed_by_manager_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create employee_certifications table
CREATE TABLE public.employee_certifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  employee_id UUID NOT NULL REFERENCES public.employees(id) ON DELETE CASCADE,
  certification_name TEXT NOT NULL,
  certification_body TEXT,
  certification_number TEXT,
  issue_date DATE NOT NULL,
  expiry_date DATE,
  renewal_required BOOLEAN DEFAULT false,
  cost NUMERIC,
  verification_url TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create training_courses table
CREATE TABLE public.training_courses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  course_name TEXT NOT NULL,
  course_code TEXT,
  course_provider TEXT,
  course_type TEXT NOT NULL DEFAULT 'online',
  duration_hours NUMERIC,
  cost_per_person NUMERIC,
  description TEXT,
  prerequisites TEXT,
  course_url TEXT,
  is_mandatory BOOLEAN DEFAULT false,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create employee_training table
CREATE TABLE public.employee_training (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  employee_id UUID NOT NULL REFERENCES public.employees(id) ON DELETE CASCADE,
  course_id UUID NOT NULL REFERENCES public.training_courses(id) ON DELETE CASCADE,
  enrollment_date DATE NOT NULL DEFAULT CURRENT_DATE,
  scheduled_date DATE,
  completion_date DATE,
  training_status TEXT NOT NULL DEFAULT 'enrolled',
  score NUMERIC,
  passed BOOLEAN,
  certificate_url TEXT,
  instructor TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create leave_types table
CREATE TABLE public.leave_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  leave_type_name TEXT NOT NULL,
  leave_code TEXT NOT NULL,
  annual_allowance_days NUMERIC DEFAULT 0,
  is_paid BOOLEAN DEFAULT true,
  requires_approval BOOLEAN DEFAULT true,
  max_consecutive_days INTEGER,
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(customer_id, leave_code)
);

-- Create employee_leave table
CREATE TABLE public.employee_leave (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  employee_id UUID NOT NULL REFERENCES public.employees(id) ON DELETE CASCADE,
  leave_type_id UUID NOT NULL REFERENCES public.leave_types(id),
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  total_days NUMERIC NOT NULL,
  leave_reason TEXT,
  leave_status TEXT NOT NULL DEFAULT 'pending',
  requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  approved_by UUID REFERENCES public.employees(id),
  approved_at TIMESTAMPTZ,
  rejection_reason TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create employee number sequence and function
CREATE SEQUENCE employee_number_seq;
CREATE OR REPLACE FUNCTION generate_employee_number()
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  RETURN 'EMP' || LPAD(nextval('employee_number_seq')::TEXT, 5, '0');
END;
$$;

CREATE OR REPLACE FUNCTION set_employee_number()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  IF NEW.employee_number IS NULL OR NEW.employee_number = '' THEN
    NEW.employee_number := generate_employee_number();
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER set_employee_number_trigger
BEFORE INSERT ON public.employees
FOR EACH ROW EXECUTE FUNCTION set_employee_number();

-- Add update triggers
CREATE TRIGGER update_departments_updated_at BEFORE UPDATE ON public.departments
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employees_updated_at BEFORE UPDATE ON public.employees
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_performance_reviews_updated_at BEFORE UPDATE ON public.performance_reviews
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employee_certifications_updated_at BEFORE UPDATE ON public.employee_certifications
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_training_courses_updated_at BEFORE UPDATE ON public.training_courses
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employee_training_updated_at BEFORE UPDATE ON public.employee_training
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_leave_types_updated_at BEFORE UPDATE ON public.leave_types
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employee_leave_updated_at BEFORE UPDATE ON public.employee_leave
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS
ALTER TABLE public.departments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.performance_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employee_certifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.training_courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employee_training ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.leave_types ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employee_leave ENABLE ROW LEVEL SECURITY;

-- RLS Policies for departments
CREATE POLICY "Users can view departments in their organization"
ON public.departments FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Admins can manage departments"
ON public.departments FOR ALL
USING (
  customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ) AND has_role(auth.uid(), 'admin'::app_role)
);

-- RLS Policies for employees
CREATE POLICY "Users can view employees in their organization"
ON public.employees FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Admins can manage employees"
ON public.employees FOR ALL
USING (
  customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ) AND has_role(auth.uid(), 'admin'::app_role)
);

-- RLS Policies for performance_reviews
CREATE POLICY "Users can view their own reviews and reviews they manage"
ON public.performance_reviews FOR SELECT
USING (
  customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ) AND (
    employee_id IN (SELECT id FROM employees WHERE user_id = auth.uid()) OR
    reviewer_id IN (SELECT id FROM employees WHERE user_id = auth.uid()) OR
    has_role(auth.uid(), 'admin'::app_role)
  )
);

CREATE POLICY "Managers can create reviews"
ON public.performance_reviews FOR INSERT
WITH CHECK (
  customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Reviewers can update reviews"
ON public.performance_reviews FOR UPDATE
USING (
  customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ) AND (
    reviewer_id IN (SELECT id FROM employees WHERE user_id = auth.uid()) OR
    has_role(auth.uid(), 'admin'::app_role)
  )
);

-- RLS Policies for certifications
CREATE POLICY "Users can view certifications in their organization"
ON public.employee_certifications FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can manage certifications"
ON public.employee_certifications FOR ALL
USING (
  customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  )
);

-- RLS Policies for training courses
CREATE POLICY "Users can view training courses in their organization"
ON public.training_courses FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Admins can manage training courses"
ON public.training_courses FOR ALL
USING (
  customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ) AND has_role(auth.uid(), 'admin'::app_role)
);

-- RLS Policies for employee training
CREATE POLICY "Users can view training records in their organization"
ON public.employee_training FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Users can manage training records"
ON public.employee_training FOR ALL
USING (
  customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  )
);

-- RLS Policies for leave types
CREATE POLICY "Users can view leave types in their organization"
ON public.leave_types FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Admins can manage leave types"
ON public.leave_types FOR ALL
USING (
  customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ) AND has_role(auth.uid(), 'admin'::app_role)
);

-- RLS Policies for employee leave
CREATE POLICY "Users can view leave requests in their organization"
ON public.employee_leave FOR SELECT
USING (customer_id IN (
  SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
));

CREATE POLICY "Employees can create leave requests"
ON public.employee_leave FOR INSERT
WITH CHECK (
  customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Employees and managers can update leave requests"
ON public.employee_leave FOR UPDATE
USING (
  customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  )
);

-- Create indexes for performance
CREATE INDEX idx_departments_customer_id ON public.departments(customer_id);
CREATE INDEX idx_departments_manager ON public.departments(manager_id);
CREATE INDEX idx_employees_customer_id ON public.employees(customer_id);
CREATE INDEX idx_employees_department ON public.employees(department_id);
CREATE INDEX idx_employees_manager ON public.employees(manager_id);
CREATE INDEX idx_performance_reviews_employee ON public.performance_reviews(employee_id);
CREATE INDEX idx_employee_certifications_employee ON public.employee_certifications(employee_id);
CREATE INDEX idx_employee_training_employee ON public.employee_training(employee_id);
CREATE INDEX idx_employee_leave_employee ON public.employee_leave(employee_id);