-- Create AI interactions log to track all LLM conversations
CREATE TABLE public.ai_interactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  user_id UUID NOT NULL,
  conversation_id UUID NOT NULL,
  interaction_type TEXT NOT NULL, -- 'query', 'insight', 'recommendation'
  user_query TEXT NOT NULL,
  ai_response TEXT NOT NULL,
  knowledge_sources JSONB, -- References to knowledge articles used
  confidence_score NUMERIC,
  feedback_rating INTEGER, -- 1-5 stars
  was_helpful BOOLEAN,
  insight_generated BOOLEAN DEFAULT false,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.ai_interactions ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own interactions"
  ON public.ai_interactions
  FOR SELECT
  USING (user_id = auth.uid() OR customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

CREATE POLICY "System can insert interactions"
  ON public.ai_interactions
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own interactions"
  ON public.ai_interactions
  FOR UPDATE
  USING (user_id = auth.uid());

-- Create learning metrics table
CREATE TABLE public.ai_learning_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  metric_date DATE NOT NULL DEFAULT CURRENT_DATE,
  total_interactions INTEGER DEFAULT 0,
  insights_generated INTEGER DEFAULT 0,
  articles_created INTEGER DEFAULT 0,
  avg_confidence_score NUMERIC,
  avg_user_rating NUMERIC,
  knowledge_base_size INTEGER DEFAULT 0,
  improvement_rate NUMERIC,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(customer_id, metric_date)
);

-- Enable RLS
ALTER TABLE public.ai_learning_metrics ENABLE ROW LEVEL SECURITY;

-- RLS Policy
CREATE POLICY "Users can view their metrics"
  ON public.ai_learning_metrics
  FOR SELECT
  USING (customer_id IN (
    SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
  ));

-- Create trigger for updated_at
CREATE TRIGGER update_ai_learning_metrics_updated_at
  BEFORE UPDATE ON public.ai_learning_metrics
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Create indexes for performance
CREATE INDEX idx_ai_interactions_customer ON ai_interactions(customer_id);
CREATE INDEX idx_ai_interactions_user ON ai_interactions(user_id);
CREATE INDEX idx_ai_interactions_conversation ON ai_interactions(conversation_id);
CREATE INDEX idx_ai_interactions_created ON ai_interactions(created_at);
CREATE INDEX idx_ai_learning_metrics_customer ON ai_learning_metrics(customer_id);
CREATE INDEX idx_ai_learning_metrics_date ON ai_learning_metrics(metric_date);