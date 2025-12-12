-- Create function to generate employee onboarding template for a customer
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
  FROM onboarding_templates
  WHERE customer_id = _customer_id
    AND template_name = 'Employee Onboarding'
    AND client_type = 'employee';
  
  IF template_id IS NOT NULL THEN
    RETURN template_id;
  END IF;
  
  -- Create the employee onboarding template
  INSERT INTO onboarding_templates (
    customer_id,
    created_by,
    template_name,
    description,
    client_type,
    estimated_days,
    is_active
  ) VALUES (
    _customer_id,
    _created_by,
    'Employee Onboarding',
    'Standard employee onboarding template including demographic information, department assignment, job details, and RBAC role configuration',
    'employee',
    7,
    true
  )
  RETURNING id INTO template_id;
  
  -- Task 1: Personal Information
  INSERT INTO onboarding_template_tasks (
    template_id,
    task_name,
    description,
    task_category,
    sequence_order,
    estimated_hours,
    assigned_role,
    requires_client_input,
    compliance_tags
  ) VALUES (
    template_id,
    'Collect Personal Information',
    'Gather employee legal name, date of birth, Social Security Number/Tax ID, home address, phone number, and emergency contact information',
    'Demographics',
    1,
    0.5,
    'HR Manager',
    true,
    ARRAY['PII', 'HR']
  );
  
  -- Task 2: Contact Information
  INSERT INTO onboarding_template_tasks (
    template_id,
    task_name,
    description,
    task_category,
    sequence_order,
    estimated_hours,
    assigned_role,
    requires_client_input,
    compliance_tags
  ) VALUES (
    template_id,
    'Setup Contact Details',
    'Configure work email address, work phone number, mobile number, and preferred contact methods',
    'Demographics',
    2,
    0.25,
    'IT Admin',
    true,
    ARRAY['HR']
  );
  
  -- Task 3: Employment Information
  INSERT INTO onboarding_template_tasks (
    template_id,
    task_name,
    description,
    task_category,
    sequence_order,
    estimated_hours,
    assigned_role,
    requires_client_input,
    compliance_tags,
    required_documents
  ) VALUES (
    template_id,
    'Document Employment Details',
    'Record employment start date, employment type (full-time/part-time/contract), work location, employee ID, and salary information',
    'Employment',
    3,
    0.5,
    'HR Manager',
    false,
    ARRAY['HR', 'Finance'],
    '["Signed Offer Letter", "Employment Contract"]'::jsonb
  );
  
  -- Task 4: Department Assignment
  INSERT INTO onboarding_template_tasks (
    template_id,
    task_name,
    description,
    task_category,
    sequence_order,
    estimated_hours,
    assigned_role,
    requires_client_input,
    compliance_tags
  ) VALUES (
    template_id,
    'Assign Department',
    'Assign employee to appropriate department, team, and reporting manager. Update organizational chart',
    'Organization',
    4,
    0.25,
    'HR Manager',
    false,
    ARRAY['HR']
  );
  
  -- Task 5: Job Title and Description
  INSERT INTO onboarding_template_tasks (
    template_id,
    task_name,
    description,
    task_category,
    sequence_order,
    estimated_hours,
    assigned_role,
    requires_client_input,
    compliance_tags
  ) VALUES (
    template_id,
    'Configure Job Title and Responsibilities',
    'Set official job title, job level/grade, and provide detailed job description including key responsibilities and success metrics',
    'Organization',
    5,
    0.5,
    'HR Manager',
    false,
    ARRAY['HR']
  );
  
  -- Task 6: RBAC Role Assignment
  INSERT INTO onboarding_template_tasks (
    template_id,
    task_name,
    description,
    task_category,
    sequence_order,
    estimated_hours,
    assigned_role,
    requires_client_input,
    compliance_tags
  ) VALUES (
    template_id,
    'Assign RBAC Profile and Permissions',
    'Configure role-based access control profile, assign appropriate system permissions, application access, and security groups based on job function',
    'IT Setup',
    6,
    1.0,
    'IT Admin',
    false,
    ARRAY['Security', 'IT', 'Compliance']
  );
  
  -- Task 7: System Accounts
  INSERT INTO onboarding_template_tasks (
    template_id,
    task_name,
    description,
    task_category,
    sequence_order,
    estimated_hours,
    assigned_role,
    requires_client_input,
    compliance_tags
  ) VALUES (
    template_id,
    'Create System Accounts',
    'Create user accounts for email, Active Directory/Azure AD, VPN, time tracking, HR system, and other required applications',
    'IT Setup',
    7,
    1.5,
    'IT Admin',
    false,
    ARRAY['IT', 'Security']
  );
  
  -- Task 8: Workspace Setup
  INSERT INTO onboarding_template_tasks (
    template_id,
    task_name,
    description,
    task_category,
    sequence_order,
    estimated_hours,
    assigned_role,
    requires_client_input,
    compliance_tags,
    required_documents
  ) VALUES (
    template_id,
    'Prepare Workspace and Equipment',
    'Assign desk/workspace, provide computer hardware, monitor, keyboard, mouse, headset, phone, and any specialized equipment needed for role',
    'Logistics',
    8,
    2.0,
    'IT Admin',
    false,
    ARRAY['IT'],
    '["Equipment Acknowledgment Form"]'::jsonb
  );
  
  -- Task 9: Benefits Enrollment
  INSERT INTO onboarding_template_tasks (
    template_id,
    task_name,
    description,
    task_category,
    sequence_order,
    estimated_hours,
    assigned_role,
    requires_client_input,
    compliance_tags,
    required_documents
  ) VALUES (
    template_id,
    'Complete Benefits Enrollment',
    'Enroll in health insurance, dental, vision, 401(k), life insurance, and other company benefits. Provide benefit cards and documentation',
    'Benefits',
    9,
    1.0,
    'HR Manager',
    true,
    ARRAY['HR', 'Finance'],
    '["W-4 Form", "I-9 Form", "Direct Deposit Form", "Benefits Election Form"]'::jsonb
  );
  
  -- Task 10: Compliance Training
  INSERT INTO onboarding_template_tasks (
    template_id,
    task_name,
    description,
    task_category,
    sequence_order,
    estimated_hours,
    assigned_role,
    requires_client_input,
    compliance_tags,
    required_documents
  ) VALUES (
    template_id,
    'Complete Mandatory Training',
    'Complete required compliance training including security awareness, harassment prevention, code of conduct, data privacy (GDPR/CCPA), and industry-specific certifications',
    'Compliance',
    10,
    4.0,
    'HR Manager',
    true,
    ARRAY['Compliance', 'Security', 'HR'],
    '["Training Completion Certificates"]'::jsonb
  );
  
  -- Task 11: Team Introduction
  INSERT INTO onboarding_template_tasks (
    template_id,
    task_name,
    description,
    task_category,
    sequence_order,
    estimated_hours,
    assigned_role,
    requires_client_input,
    compliance_tags
  ) VALUES (
    template_id,
    'Team Introductions and Orientation',
    'Schedule meetings with team members, manager, and key stakeholders. Provide team directory and organizational overview',
    'Orientation',
    11,
    2.0,
    'HR Manager',
    false,
    ARRAY['HR']
  );
  
  -- Task 12: First Week Goals
  INSERT INTO onboarding_template_tasks (
    template_id,
    task_name,
    description,
    task_category,
    sequence_order,
    estimated_hours,
    assigned_role,
    requires_client_input,
    compliance_tags
  ) VALUES (
    template_id,
    'Set 30-60-90 Day Goals',
    'Establish clear performance objectives and success metrics for first 30, 60, and 90 days. Schedule regular check-ins with manager',
    'Orientation',
    12,
    1.0,
    'Manager',
    false,
    ARRAY['HR']
  );
  
  RETURN template_id;
END;
$$;