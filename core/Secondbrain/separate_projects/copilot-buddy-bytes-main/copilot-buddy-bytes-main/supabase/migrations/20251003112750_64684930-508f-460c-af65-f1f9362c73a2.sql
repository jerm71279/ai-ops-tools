-- Create behavioral_events table for ML training data
CREATE TABLE public.behavioral_events (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID NOT NULL,
  customer_id UUID REFERENCES public.customers(id) ON DELETE CASCADE NOT NULL,
  event_type TEXT NOT NULL,
  system_name TEXT NOT NULL,
  action TEXT NOT NULL,
  context JSONB,
  duration_ms INTEGER,
  success BOOLEAN NOT NULL DEFAULT true,
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create ml_models table for model management
CREATE TABLE public.ml_models (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID REFERENCES public.customers(id) ON DELETE CASCADE NOT NULL,
  model_name TEXT NOT NULL,
  model_type TEXT NOT NULL,
  version TEXT NOT NULL,
  accuracy_score NUMERIC(5,4),
  training_data_count INTEGER,
  features_used TEXT[],
  hyperparameters JSONB,
  status TEXT NOT NULL DEFAULT 'training',
  trained_at TIMESTAMP WITH TIME ZONE,
  deployed_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create prediction_history table for tracking predictions
CREATE TABLE public.prediction_history (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  model_id UUID REFERENCES public.ml_models(id) ON DELETE CASCADE NOT NULL,
  customer_id UUID REFERENCES public.customers(id) ON DELETE CASCADE NOT NULL,
  prediction_type TEXT NOT NULL,
  input_features JSONB NOT NULL,
  predicted_value JSONB NOT NULL,
  actual_value JSONB,
  confidence_score NUMERIC(3,2),
  was_accurate BOOLEAN,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create anomaly_detections table
CREATE TABLE public.anomaly_detections (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID REFERENCES public.customers(id) ON DELETE CASCADE NOT NULL,
  anomaly_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  affected_user_id UUID,
  system_name TEXT NOT NULL,
  description TEXT NOT NULL,
  detection_method TEXT NOT NULL,
  confidence_score NUMERIC(3,2),
  raw_data JSONB,
  status TEXT NOT NULL DEFAULT 'new',
  resolved_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create compliance_frameworks table for modular framework support
CREATE TABLE public.compliance_frameworks (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  framework_code TEXT NOT NULL UNIQUE,
  framework_name TEXT NOT NULL,
  industry TEXT NOT NULL,
  description TEXT,
  version TEXT,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create compliance_controls table for framework controls
CREATE TABLE public.compliance_controls (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  framework_id UUID REFERENCES public.compliance_frameworks(id) ON DELETE CASCADE NOT NULL,
  control_id TEXT NOT NULL,
  control_name TEXT NOT NULL,
  description TEXT,
  category TEXT NOT NULL,
  required_evidence TEXT[],
  automation_level TEXT NOT NULL DEFAULT 'manual',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(framework_id, control_id)
);

-- Create compliance_tags table for reusable tags
CREATE TABLE public.compliance_tags (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  tag_name TEXT NOT NULL UNIQUE,
  description TEXT,
  tag_type TEXT NOT NULL,
  applicable_frameworks UUID[],
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create customer_frameworks table to link customers with their frameworks
CREATE TABLE public.customer_frameworks (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  customer_id UUID REFERENCES public.customers(id) ON DELETE CASCADE NOT NULL,
  framework_id UUID REFERENCES public.compliance_frameworks(id) ON DELETE CASCADE NOT NULL,
  enabled_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  custom_controls JSONB,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(customer_id, framework_id)
);

-- Enable RLS on all new tables
ALTER TABLE public.behavioral_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ml_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.prediction_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.anomaly_detections ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.compliance_frameworks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.compliance_controls ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.compliance_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.customer_frameworks ENABLE ROW LEVEL SECURITY;

-- RLS Policies for behavioral_events
CREATE POLICY "Users can view their own events"
  ON public.behavioral_events FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all events"
  ON public.behavioral_events FOR SELECT
  USING (has_role(auth.uid(), 'admin'));

CREATE POLICY "System can insert events"
  ON public.behavioral_events FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- RLS Policies for ml_models
CREATE POLICY "Admins can view all ML models"
  ON public.ml_models FOR SELECT
  USING (has_role(auth.uid(), 'admin'));

CREATE POLICY "Admins can manage ML models"
  ON public.ml_models FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for prediction_history
CREATE POLICY "Admins can view prediction history"
  ON public.prediction_history FOR SELECT
  USING (has_role(auth.uid(), 'admin'));

CREATE POLICY "Admins can manage prediction history"
  ON public.prediction_history FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for anomaly_detections
CREATE POLICY "Admins can view anomalies"
  ON public.anomaly_detections FOR SELECT
  USING (has_role(auth.uid(), 'admin'));

CREATE POLICY "Admins can manage anomalies"
  ON public.anomaly_detections FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for compliance_frameworks
CREATE POLICY "Everyone can view active frameworks"
  ON public.compliance_frameworks FOR SELECT
  USING (is_active = true);

CREATE POLICY "Admins can manage frameworks"
  ON public.compliance_frameworks FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for compliance_controls
CREATE POLICY "Everyone can view controls"
  ON public.compliance_controls FOR SELECT
  USING (true);

CREATE POLICY "Admins can manage controls"
  ON public.compliance_controls FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for compliance_tags
CREATE POLICY "Everyone can view tags"
  ON public.compliance_tags FOR SELECT
  USING (true);

CREATE POLICY "Admins can manage tags"
  ON public.compliance_tags FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for customer_frameworks
CREATE POLICY "Admins can view customer frameworks"
  ON public.customer_frameworks FOR SELECT
  USING (has_role(auth.uid(), 'admin'));

CREATE POLICY "Admins can manage customer frameworks"
  ON public.customer_frameworks FOR ALL
  USING (has_role(auth.uid(), 'admin'));

-- Create triggers for updated_at columns
CREATE TRIGGER update_ml_models_updated_at
  BEFORE UPDATE ON public.ml_models
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_compliance_frameworks_updated_at
  BEFORE UPDATE ON public.compliance_frameworks
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Create indexes for performance
CREATE INDEX idx_behavioral_events_user_timestamp 
  ON public.behavioral_events(user_id, timestamp DESC);

CREATE INDEX idx_behavioral_events_customer_timestamp 
  ON public.behavioral_events(customer_id, timestamp DESC);

CREATE INDEX idx_prediction_history_model 
  ON public.prediction_history(model_id, created_at DESC);

CREATE INDEX idx_anomaly_detections_customer_status 
  ON public.anomaly_detections(customer_id, status, created_at DESC);