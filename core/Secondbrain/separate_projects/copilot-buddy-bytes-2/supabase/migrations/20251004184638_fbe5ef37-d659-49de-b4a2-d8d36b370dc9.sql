-- Create customer onboarding system

-- Onboarding templates (reusable checklists for different client types)
CREATE TABLE public.onboarding_templates (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL REFERENCES public.customers(id) ON DELETE CASCADE,
  template_name TEXT NOT NULL,
  description TEXT,
  client_type TEXT NOT NULL DEFAULT 'standard', -- standard, enterprise, smb, etc.
  estimated_days INTEGER DEFAULT 30,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Onboarding template tasks (steps in each template)
CREATE TABLE public.onboarding_template_tasks (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  template_id UUID NOT NULL REFERENCES public.onboarding_templates(id) ON DELETE CASCADE,
  task_name TEXT NOT NULL,
  description TEXT,
  task_category TEXT NOT NULL, -- discovery, documentation, configuration, testing, training, handoff
  assigned_role TEXT, -- engineer, project_manager, sales, client
  sequence_order INTEGER NOT NULL DEFAULT 0,
  estimated_hours NUMERIC(5,2),
  requires_client_input BOOLEAN DEFAULT false,
  required_documents JSONB DEFAULT '[]'::jsonb, -- array of doc types needed
  compliance_tags TEXT[] DEFAULT '{}',
  dependencies JSONB DEFAULT '[]'::jsonb, -- array of task IDs that must complete first
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Client onboarding instances (actual client onboardings in progress)
CREATE TABLE public.client_onboardings (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID NOT NULL REFERENCES public.customers(id) ON DELETE CASCADE,
  template_id UUID NOT NULL REFERENCES public.onboarding_templates(id),
  client_name TEXT NOT NULL,
  client_contact_email TEXT NOT NULL,
  client_contact_name TEXT,
  status TEXT NOT NULL DEFAULT 'not_started', -- not_started, in_progress, on_hold, completed, cancelled
  start_date DATE,
  target_completion_date DATE,
  actual_completion_date DATE,
  completion_percentage INTEGER DEFAULT 0,
  notes TEXT,
  metadata JSONB DEFAULT '{}'::jsonb, -- custom fields for client info
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Client onboarding tasks (actual task instances for each client)
CREATE TABLE public.client_onboarding_tasks (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  onboarding_id UUID NOT NULL REFERENCES public.client_onboardings(id) ON DELETE CASCADE,
  template_task_id UUID REFERENCES public.onboarding_template_tasks(id),
  task_name TEXT NOT NULL,
  description TEXT,
  task_category TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending', -- pending, in_progress, blocked, completed, skipped
  assigned_to UUID REFERENCES auth.users(id),
  assigned_role TEXT,
  sequence_order INTEGER NOT NULL DEFAULT 0,
  due_date DATE,
  completed_at TIMESTAMP WITH TIME ZONE,
  completed_by UUID REFERENCES auth.users(id),
  estimated_hours NUMERIC(5,2),
  actual_hours NUMERIC(5,2),
  blockers TEXT, -- reason if blocked
  notes TEXT,
  required_documents JSONB DEFAULT '[]'::jsonb,
  uploaded_documents JSONB DEFAULT '[]'::jsonb, -- array of file references
  compliance_tags TEXT[] DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Onboarding task comments (collaboration on tasks)
CREATE TABLE public.onboarding_task_comments (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  task_id UUID NOT NULL REFERENCES public.client_onboarding_tasks(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id),
  comment_text TEXT NOT NULL,
  is_internal BOOLEAN DEFAULT true, -- false if visible to client
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Onboarding milestones (key checkpoints)
CREATE TABLE public.onboarding_milestones (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  onboarding_id UUID NOT NULL REFERENCES public.client_onboardings(id) ON DELETE CASCADE,
  milestone_name TEXT NOT NULL,
  description TEXT,
  target_date DATE,
  completed_date DATE,
  status TEXT NOT NULL DEFAULT 'pending', -- pending, completed, missed
  required_task_ids JSONB DEFAULT '[]'::jsonb, -- tasks that must complete for milestone
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.onboarding_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.onboarding_template_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.client_onboardings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.client_onboarding_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.onboarding_task_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.onboarding_milestones ENABLE ROW LEVEL SECURITY;

-- RLS Policies for onboarding_templates
CREATE POLICY "Users can view templates from their customer"
  ON public.onboarding_templates FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can create templates for their customer"
  ON public.onboarding_templates FOR INSERT
  WITH CHECK (
    customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
    AND created_by = auth.uid()
  );

CREATE POLICY "Users can update templates from their customer"
  ON public.onboarding_templates FOR UPDATE
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete templates from their customer"
  ON public.onboarding_templates FOR DELETE
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- RLS Policies for onboarding_template_tasks
CREATE POLICY "Users can view template tasks"
  ON public.onboarding_template_tasks FOR SELECT
  USING (template_id IN (
    SELECT id FROM onboarding_templates
    WHERE customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
  ));

CREATE POLICY "Users can manage template tasks"
  ON public.onboarding_template_tasks FOR ALL
  USING (template_id IN (
    SELECT id FROM onboarding_templates
    WHERE customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
  ));

-- RLS Policies for client_onboardings
CREATE POLICY "Users can view onboardings from their customer"
  ON public.client_onboardings FOR SELECT
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can create onboardings for their customer"
  ON public.client_onboardings FOR INSERT
  WITH CHECK (
    customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
    AND created_by = auth.uid()
  );

CREATE POLICY "Users can update onboardings from their customer"
  ON public.client_onboardings FOR UPDATE
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

CREATE POLICY "Users can delete onboardings from their customer"
  ON public.client_onboardings FOR DELETE
  USING (customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()));

-- RLS Policies for client_onboarding_tasks
CREATE POLICY "Users can view onboarding tasks"
  ON public.client_onboarding_tasks FOR SELECT
  USING (onboarding_id IN (
    SELECT id FROM client_onboardings
    WHERE customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
  ));

CREATE POLICY "Users can manage onboarding tasks"
  ON public.client_onboarding_tasks FOR ALL
  USING (onboarding_id IN (
    SELECT id FROM client_onboardings
    WHERE customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
  ));

-- RLS Policies for onboarding_task_comments
CREATE POLICY "Users can view task comments"
  ON public.onboarding_task_comments FOR SELECT
  USING (task_id IN (
    SELECT t.id FROM client_onboarding_tasks t
    JOIN client_onboardings o ON t.onboarding_id = o.id
    WHERE o.customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
  ));

CREATE POLICY "Users can create task comments"
  ON public.onboarding_task_comments FOR INSERT
  WITH CHECK (
    user_id = auth.uid()
    AND task_id IN (
      SELECT t.id FROM client_onboarding_tasks t
      JOIN client_onboardings o ON t.onboarding_id = o.id
      WHERE o.customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
    )
  );

-- RLS Policies for onboarding_milestones
CREATE POLICY "Users can view milestones"
  ON public.onboarding_milestones FOR SELECT
  USING (onboarding_id IN (
    SELECT id FROM client_onboardings
    WHERE customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
  ));

CREATE POLICY "Users can manage milestones"
  ON public.onboarding_milestones FOR ALL
  USING (onboarding_id IN (
    SELECT id FROM client_onboardings
    WHERE customer_id IN (SELECT customer_id FROM user_profiles WHERE user_id = auth.uid())
  ));

-- Create triggers for updated_at
CREATE TRIGGER update_onboarding_templates_updated_at
  BEFORE UPDATE ON public.onboarding_templates
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_client_onboardings_updated_at
  BEFORE UPDATE ON public.client_onboardings
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_client_onboarding_tasks_updated_at
  BEFORE UPDATE ON public.client_onboarding_tasks
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Create indexes for performance
CREATE INDEX idx_onboarding_templates_customer ON public.onboarding_templates(customer_id);
CREATE INDEX idx_onboarding_template_tasks_template ON public.onboarding_template_tasks(template_id);
CREATE INDEX idx_client_onboardings_customer ON public.client_onboardings(customer_id);
CREATE INDEX idx_client_onboardings_status ON public.client_onboardings(status);
CREATE INDEX idx_client_onboarding_tasks_onboarding ON public.client_onboarding_tasks(onboarding_id);
CREATE INDEX idx_client_onboarding_tasks_status ON public.client_onboarding_tasks(status);
CREATE INDEX idx_client_onboarding_tasks_assigned ON public.client_onboarding_tasks(assigned_to);
CREATE INDEX idx_onboarding_task_comments_task ON public.onboarding_task_comments(task_id);
CREATE INDEX idx_onboarding_milestones_onboarding ON public.onboarding_milestones(onboarding_id);