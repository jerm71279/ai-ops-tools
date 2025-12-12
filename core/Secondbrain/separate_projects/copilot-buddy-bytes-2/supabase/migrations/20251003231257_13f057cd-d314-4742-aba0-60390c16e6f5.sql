-- Add workflow execution history table
CREATE TABLE IF NOT EXISTS public.workflow_executions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  workflow_id UUID NOT NULL REFERENCES public.workflows(id) ON DELETE CASCADE,
  customer_id UUID NOT NULL,
  triggered_by TEXT NOT NULL, -- 'manual', 'webhook', 'schedule', 'event'
  trigger_data JSONB,
  status TEXT NOT NULL DEFAULT 'running',
  started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  completed_at TIMESTAMP WITH TIME ZONE,
  error_message TEXT,
  execution_log JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Add workflow triggers table for webhooks and events
CREATE TABLE IF NOT EXISTS public.workflow_triggers (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  workflow_id UUID NOT NULL REFERENCES public.workflows(id) ON DELETE CASCADE,
  customer_id UUID NOT NULL,
  trigger_type TEXT NOT NULL, -- 'webhook', 'schedule', 'event', 'manual'
  trigger_config JSONB NOT NULL DEFAULT '{}'::jsonb,
  webhook_url TEXT,
  webhook_secret TEXT,
  is_enabled BOOLEAN NOT NULL DEFAULT true,
  last_triggered_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Add workflow conditions table for branching logic
CREATE TABLE IF NOT EXISTS public.workflow_conditions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  workflow_id UUID NOT NULL REFERENCES public.workflows(id) ON DELETE CASCADE,
  step_id TEXT NOT NULL,
  condition_type TEXT NOT NULL, -- 'if', 'switch', 'loop'
  condition_expression JSONB NOT NULL,
  true_path JSONB,
  false_path JSONB,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enhance workflows table with new fields
ALTER TABLE public.workflows
ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT true,
ADD COLUMN IF NOT EXISTS workflow_type TEXT DEFAULT 'manual',
ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1,
ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT ARRAY[]::TEXT[];

-- Enable RLS on new tables
ALTER TABLE public.workflow_executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_triggers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workflow_conditions ENABLE ROW LEVEL SECURITY;

-- RLS policies for workflow_executions
CREATE POLICY "Admins can view all workflow executions"
ON public.workflow_executions FOR SELECT
TO authenticated
USING (has_role(auth.uid(), 'admin'::app_role));

CREATE POLICY "System can insert workflow executions"
ON public.workflow_executions FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "System can update workflow executions"
ON public.workflow_executions FOR UPDATE
TO authenticated
USING (true);

-- RLS policies for workflow_triggers
CREATE POLICY "Admins can manage workflow triggers"
ON public.workflow_triggers FOR ALL
TO authenticated
USING (has_role(auth.uid(), 'admin'::app_role));

CREATE POLICY "Admins can view workflow triggers"
ON public.workflow_triggers FOR SELECT
TO authenticated
USING (has_role(auth.uid(), 'admin'::app_role));

-- RLS policies for workflow_conditions
CREATE POLICY "Admins can manage workflow conditions"
ON public.workflow_conditions FOR ALL
TO authenticated
USING (has_role(auth.uid(), 'admin'::app_role));

CREATE POLICY "Admins can view workflow conditions"
ON public.workflow_conditions FOR SELECT
TO authenticated
USING (has_role(auth.uid(), 'admin'::app_role));

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON public.workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_customer_id ON public.workflow_executions(customer_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON public.workflow_executions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_triggers_workflow_id ON public.workflow_triggers(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_conditions_workflow_id ON public.workflow_conditions(workflow_id);

-- Add trigger for updated_at on workflow_triggers
CREATE TRIGGER update_workflow_triggers_updated_at
BEFORE UPDATE ON public.workflow_triggers
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();