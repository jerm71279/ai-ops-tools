-- Create task repetition analysis table
CREATE TABLE IF NOT EXISTS public.task_repetition_analysis (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  customer_id UUID NOT NULL,
  task_signature TEXT NOT NULL,
  repetition_count INTEGER NOT NULL DEFAULT 1,
  first_occurrence TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  last_occurrence TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  action_type TEXT NOT NULL,
  system_name TEXT NOT NULL,
  task_context JSONB DEFAULT '{}'::jsonb,
  suggested_workflow JSONB,
  suggestion_confidence NUMERIC,
  status TEXT NOT NULL DEFAULT 'detected' CHECK (status IN ('detected', 'suggested', 'automated', 'dismissed', 'ignored')),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  UNIQUE(user_id, task_signature)
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_task_repetition_user_status ON public.task_repetition_analysis(user_id, status);
CREATE INDEX IF NOT EXISTS idx_task_repetition_count ON public.task_repetition_analysis(repetition_count) WHERE status = 'detected';
CREATE INDEX IF NOT EXISTS idx_task_repetition_customer ON public.task_repetition_analysis(customer_id, status);

-- Enable RLS
ALTER TABLE public.task_repetition_analysis ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own task repetitions"
  ON public.task_repetition_analysis
  FOR SELECT
  USING (user_id = auth.uid());

CREATE POLICY "System can insert task repetitions"
  ON public.task_repetition_analysis
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own task repetitions"
  ON public.task_repetition_analysis
  FOR UPDATE
  USING (user_id = auth.uid());

-- Trigger to update updated_at
CREATE TRIGGER update_task_repetition_analysis_updated_at
  BEFORE UPDATE ON public.task_repetition_analysis
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();