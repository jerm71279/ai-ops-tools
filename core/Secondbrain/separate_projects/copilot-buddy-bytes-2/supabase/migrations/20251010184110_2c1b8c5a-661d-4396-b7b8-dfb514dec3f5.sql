-- =====================================================
-- EMPLOYEE ONBOARDING SYSTEM - SEPARATE FROM CLIENT ONBOARDING
-- =====================================================

-- Employee Onboarding Templates Table
CREATE TABLE IF NOT EXISTS public.employee_onboarding_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES public.customers(id) ON DELETE CASCADE,
  template_name TEXT NOT NULL,
  description TEXT,
  department_type TEXT, -- 'general', 'it', 'sales', 'hr', 'finance', etc.
  estimated_days INTEGER DEFAULT 7,
  is_active BOOLEAN DEFAULT true,
  created_by UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Employee Onboarding Template Tasks Table
CREATE TABLE IF NOT EXISTS public.employee_onboarding_template_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id UUID NOT NULL REFERENCES public.employee_onboarding_templates(id) ON DELETE CASCADE,
  task_name TEXT NOT NULL,
  description TEXT,
  task_category TEXT NOT NULL, -- 'Demographics', 'IT Setup', 'HR', 'Orientation', etc.
  sequence_order INTEGER DEFAULT 0,
  estimated_hours NUMERIC(5,2),
  assigned_role TEXT, -- 'HR Manager', 'IT Admin', 'Manager', etc.
  requires_employee_input BOOLEAN DEFAULT false,
  required_documents JSONB DEFAULT '[]'::jsonb,
  compliance_tags TEXT[] DEFAULT '{}',
  dependencies JSONB, -- Other tasks that must be completed first
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Employee Onboardings Table (Active onboarding records)
CREATE TABLE IF NOT EXISTS public.employee_onboardings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES public.customers(id) ON DELETE CASCADE,
  template_id UUID REFERENCES public.employee_onboarding_templates(id) ON DELETE SET NULL,
  
  -- Employee Information
  employee_name TEXT NOT NULL,
  employee_email TEXT NOT NULL,
  employee_phone TEXT,
  date_of_birth DATE,
  
  -- Employment Details
  start_date DATE,
  employment_type TEXT, -- 'full-time', 'part-time', 'contract', 'intern'
  department TEXT,
  job_title TEXT,
  manager_id UUID, -- References user who will be their manager
  work_location TEXT,
  
  -- RBAC & Access
  assigned_role_id UUID, -- RBAC role to be assigned
  
  -- Status & Progress
  status TEXT NOT NULL DEFAULT 'not_started', -- 'not_started', 'in_progress', 'on_hold', 'completed', 'cancelled'
  completion_percentage INTEGER DEFAULT 0,
  target_completion_date DATE,
  actual_completion_date DATE,
  
  -- Demographics & Additional Info
  emergency_contact_name TEXT,
  emergency_contact_phone TEXT,
  emergency_contact_relationship TEXT,
  address_line1 TEXT,
  address_line2 TEXT,
  city TEXT,
  state TEXT,
  postal_code TEXT,
  country TEXT,
  
  -- Metadata
  notes TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_by UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Employee Onboarding Tasks Table
CREATE TABLE IF NOT EXISTS public.employee_onboarding_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  onboarding_id UUID NOT NULL REFERENCES public.employee_onboardings(id) ON DELETE CASCADE,
  template_task_id UUID REFERENCES public.employee_onboarding_template_tasks(id) ON DELETE SET NULL,
  
  task_name TEXT NOT NULL,
  description TEXT,
  task_category TEXT NOT NULL,
  sequence_order INTEGER DEFAULT 0,
  
  status TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'in_progress', 'blocked', 'completed', 'skipped'
  assigned_to UUID, -- User responsible for completing this task
  assigned_role TEXT,
  
  due_date DATE,
  completed_at TIMESTAMP WITH TIME ZONE,
  completed_by UUID,
  
  estimated_hours NUMERIC(5,2),
  actual_hours NUMERIC(5,2),
  
  required_documents JSONB DEFAULT '[]'::jsonb,
  uploaded_documents JSONB DEFAULT '[]'::jsonb,
  compliance_tags TEXT[] DEFAULT '{}',
  
  notes TEXT,
  blockers TEXT,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Enable RLS on all tables
ALTER TABLE public.employee_onboarding_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employee_onboarding_template_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employee_onboardings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.employee_onboarding_tasks ENABLE ROW LEVEL SECURITY;

-- RLS Policies for employee_onboarding_templates
CREATE POLICY "Users can view templates in their organization"
  ON public.employee_onboarding_templates FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "HR can manage templates"
  ON public.employee_onboarding_templates FOR ALL
  USING (
    customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    )
    AND has_role(auth.uid(), 'admin'::app_role)
  );

-- RLS Policies for employee_onboarding_template_tasks
CREATE POLICY "Users can view template tasks in their organization"
  ON public.employee_onboarding_template_tasks FOR SELECT
  USING (template_id IN (
    SELECT id FROM employee_onboarding_templates 
    WHERE customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    )
  ));

CREATE POLICY "HR can manage template tasks"
  ON public.employee_onboarding_template_tasks FOR ALL
  USING (
    template_id IN (
      SELECT id FROM employee_onboarding_templates 
      WHERE customer_id IN (
        SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
      )
    )
    AND has_role(auth.uid(), 'admin'::app_role)
  );

-- RLS Policies for employee_onboardings
CREATE POLICY "Users can view onboardings in their organization"
  ON public.employee_onboardings FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "HR can manage onboardings"
  ON public.employee_onboardings FOR ALL
  USING (
    customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    )
    AND has_role(auth.uid(), 'admin'::app_role)
  );

-- RLS Policies for employee_onboarding_tasks
CREATE POLICY "Users can view tasks in their organization"
  ON public.employee_onboarding_tasks FOR SELECT
  USING (onboarding_id IN (
    SELECT id FROM employee_onboardings 
    WHERE customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    )
  ));

CREATE POLICY "Users can manage assigned tasks"
  ON public.employee_onboarding_tasks FOR UPDATE
  USING (
    onboarding_id IN (
      SELECT id FROM employee_onboardings 
      WHERE customer_id IN (
        SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
      )
    )
    AND (assigned_to = auth.uid() OR has_role(auth.uid(), 'admin'::app_role))
  );

CREATE POLICY "HR can manage all tasks"
  ON public.employee_onboarding_tasks FOR ALL
  USING (
    onboarding_id IN (
      SELECT id FROM employee_onboardings 
      WHERE customer_id IN (
        SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
      )
    )
    AND has_role(auth.uid(), 'admin'::app_role)
  );

-- Create indexes for better performance
CREATE INDEX idx_employee_templates_customer ON employee_onboarding_templates(customer_id);
CREATE INDEX idx_employee_template_tasks_template ON employee_onboarding_template_tasks(template_id);
CREATE INDEX idx_employee_onboardings_customer ON employee_onboardings(customer_id);
CREATE INDEX idx_employee_onboardings_status ON employee_onboardings(status);
CREATE INDEX idx_employee_onboarding_tasks_onboarding ON employee_onboarding_tasks(onboarding_id);
CREATE INDEX idx_employee_onboarding_tasks_assigned ON employee_onboarding_tasks(assigned_to);

-- Create updated_at triggers
CREATE TRIGGER update_employee_templates_updated_at
  BEFORE UPDATE ON employee_onboarding_templates
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employee_onboardings_updated_at
  BEFORE UPDATE ON employee_onboardings
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_employee_tasks_updated_at
  BEFORE UPDATE ON employee_onboarding_tasks
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- Update the create_employee_onboarding_template function to use new tables
DROP FUNCTION IF EXISTS public.create_employee_onboarding_template(UUID, UUID);

CREATE OR REPLACE FUNCTION public.create_employee_onboarding_template(
  _customer_id UUID,
  _created_by UUID
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  template_id UUID;
BEGIN
  -- Check if template already exists for this customer
  SELECT id INTO template_id
  FROM employee_onboarding_templates
  WHERE customer_id = _customer_id
    AND template_name = 'Standard Employee Onboarding';
  
  IF template_id IS NOT NULL THEN
    RETURN template_id;
  END IF;
  
  -- Create the employee onboarding template
  INSERT INTO employee_onboarding_templates (
    customer_id,
    created_by,
    template_name,
    description,
    department_type,
    estimated_days,
    is_active
  ) VALUES (
    _customer_id,
    _created_by,
    'Standard Employee Onboarding',
    'Comprehensive employee onboarding template including demographics, IT setup, HR enrollment, RBAC configuration, and orientation',
    'general',
    7,
    true
  )
  RETURNING id INTO template_id;
  
  -- Task 1: Personal Information
  INSERT INTO employee_onboarding_template_tasks (
    template_id, task_name, description, task_category, sequence_order,
    estimated_hours, assigned_role, requires_employee_input, compliance_tags
  ) VALUES (
    template_id,
    'Collect Personal Information',
    'Gather employee legal name, date of birth, Social Security Number/Tax ID, home address, phone number, and emergency contact information',
    'Demographics', 1, 0.5, 'HR Manager', true, ARRAY['PII', 'HR']
  );
  
  -- Task 2: Contact Information
  INSERT INTO employee_onboarding_template_tasks (
    template_id, task_name, description, task_category, sequence_order,
    estimated_hours, assigned_role, requires_employee_input, compliance_tags
  ) VALUES (
    template_id,
    'Setup Contact Details',
    'Configure work email address, work phone number, mobile number, and preferred contact methods',
    'Demographics', 2, 0.25, 'IT Admin', true, ARRAY['HR']
  );
  
  -- Task 3: Employment Information
  INSERT INTO employee_onboarding_template_tasks (
    template_id, task_name, description, task_category, sequence_order,
    estimated_hours, assigned_role, requires_employee_input, compliance_tags, required_documents
  ) VALUES (
    template_id,
    'Document Employment Details',
    'Record employment start date, employment type (full-time/part-time/contract), work location, employee ID, and salary information',
    'Employment', 3, 0.5, 'HR Manager', false, ARRAY['HR', 'Finance'],
    '["Signed Offer Letter", "Employment Contract"]'::jsonb
  );
  
  -- Task 4: Department Assignment
  INSERT INTO employee_onboarding_template_tasks (
    template_id, task_name, description, task_category, sequence_order,
    estimated_hours, assigned_role, requires_employee_input, compliance_tags
  ) VALUES (
    template_id,
    'Assign Department',
    'Assign employee to appropriate department, team, and reporting manager. Update organizational chart',
    'Organization', 4, 0.25, 'HR Manager', false, ARRAY['HR']
  );
  
  -- Task 5: Job Title and Description
  INSERT INTO employee_onboarding_template_tasks (
    template_id, task_name, description, task_category, sequence_order,
    estimated_hours, assigned_role, requires_employee_input, compliance_tags
  ) VALUES (
    template_id,
    'Configure Job Title and Responsibilities',
    'Set official job title, job level/grade, and provide detailed job description including key responsibilities and success metrics',
    'Organization', 5, 0.5, 'HR Manager', false, ARRAY['HR']
  );
  
  -- Task 6: RBAC Role Assignment
  INSERT INTO employee_onboarding_template_tasks (
    template_id, task_name, description, task_category, sequence_order,
    estimated_hours, assigned_role, requires_employee_input, compliance_tags
  ) VALUES (
    template_id,
    'Assign RBAC Profile and Permissions',
    'Configure role-based access control profile, assign appropriate system permissions, application access, and security groups based on job function',
    'IT Setup', 6, 1.0, 'IT Admin', false, ARRAY['Security', 'IT', 'Compliance']
  );
  
  -- Task 7: System Accounts
  INSERT INTO employee_onboarding_template_tasks (
    template_id, task_name, description, task_category, sequence_order,
    estimated_hours, assigned_role, requires_employee_input, compliance_tags
  ) VALUES (
    template_id,
    'Create System Accounts',
    'Create user accounts for email, Active Directory/Azure AD, VPN, time tracking, HR system, and other required applications',
    'IT Setup', 7, 1.5, 'IT Admin', false, ARRAY['IT', 'Security']
  );
  
  -- Task 8: Workspace Setup
  INSERT INTO employee_onboarding_template_tasks (
    template_id, task_name, description, task_category, sequence_order,
    estimated_hours, assigned_role, requires_employee_input, compliance_tags, required_documents
  ) VALUES (
    template_id,
    'Prepare Workspace and Equipment',
    'Assign desk/workspace, provide computer hardware, monitor, keyboard, mouse, headset, phone, and any specialized equipment needed for role',
    'Logistics', 8, 2.0, 'IT Admin', false, ARRAY['IT'],
    '["Equipment Acknowledgment Form"]'::jsonb
  );
  
  -- Task 9: Benefits Enrollment
  INSERT INTO employee_onboarding_template_tasks (
    template_id, task_name, description, task_category, sequence_order,
    estimated_hours, assigned_role, requires_employee_input, compliance_tags, required_documents
  ) VALUES (
    template_id,
    'Complete Benefits Enrollment',
    'Enroll in health insurance, dental, vision, 401(k), life insurance, and other company benefits. Provide benefit cards and documentation',
    'Benefits', 9, 1.0, 'HR Manager', true, ARRAY['HR', 'Finance'],
    '["W-4 Form", "I-9 Form", "Direct Deposit Form", "Benefits Election Form"]'::jsonb
  );
  
  -- Task 10: Compliance Training
  INSERT INTO employee_onboarding_template_tasks (
    template_id, task_name, description, task_category, sequence_order,
    estimated_hours, assigned_role, requires_employee_input, compliance_tags, required_documents
  ) VALUES (
    template_id,
    'Complete Mandatory Training',
    'Complete required compliance training including security awareness, harassment prevention, code of conduct, data privacy (GDPR/CCPA), and industry-specific certifications',
    'Compliance', 10, 4.0, 'HR Manager', true, ARRAY['Compliance', 'Security', 'HR'],
    '["Training Completion Certificates"]'::jsonb
  );
  
  -- Task 11: Team Introduction
  INSERT INTO employee_onboarding_template_tasks (
    template_id, task_name, description, task_category, sequence_order,
    estimated_hours, assigned_role, requires_employee_input, compliance_tags
  ) VALUES (
    template_id,
    'Team Introductions and Orientation',
    'Schedule meetings with team members, manager, and key stakeholders. Provide team directory and organizational overview',
    'Orientation', 11, 2.0, 'HR Manager', false, ARRAY['HR']
  );
  
  -- Task 12: First Week Goals
  INSERT INTO employee_onboarding_template_tasks (
    template_id, task_name, description, task_category, sequence_order,
    estimated_hours, assigned_role, requires_employee_input, compliance_tags
  ) VALUES (
    template_id,
    'Set 30-60-90 Day Goals',
    'Establish clear performance objectives and success metrics for first 30, 60, and 90 days. Schedule regular check-ins with manager',
    'Orientation', 12, 1.0, 'Manager', false, ARRAY['HR']
  );
  
  RETURN template_id;
END;
$$;