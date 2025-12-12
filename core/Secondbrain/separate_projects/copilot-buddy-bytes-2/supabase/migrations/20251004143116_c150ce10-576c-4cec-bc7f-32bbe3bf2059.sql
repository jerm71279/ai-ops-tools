-- Create knowledge management tables

-- Knowledge categories for organization
CREATE TABLE public.knowledge_categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  icon_name TEXT,
  parent_category_id UUID REFERENCES public.knowledge_categories(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Main knowledge articles and SOPs
CREATE TABLE public.knowledge_articles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  category_id UUID REFERENCES public.knowledge_categories(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  article_type TEXT NOT NULL CHECK (article_type IN ('sop', 'guide', 'faq', 'documentation', 'insight')),
  status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published', 'archived')),
  version INTEGER NOT NULL DEFAULT 1,
  tags TEXT[] DEFAULT '{}',
  source_type TEXT CHECK (source_type IN ('manual', 'ai_generated', 'file_import', 'workflow_insight')),
  source_metadata JSONB DEFAULT '{}',
  created_by UUID NOT NULL,
  updated_by UUID,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Version history for SOPs and articles
CREATE TABLE public.knowledge_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id UUID NOT NULL REFERENCES public.knowledge_articles(id) ON DELETE CASCADE,
  version INTEGER NOT NULL,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  changed_by UUID NOT NULL,
  change_summary TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- File attachments and uploads
CREATE TABLE public.knowledge_files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  article_id UUID REFERENCES public.knowledge_articles(id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  file_type TEXT NOT NULL,
  file_size INTEGER NOT NULL,
  storage_path TEXT NOT NULL,
  processed_status TEXT NOT NULL DEFAULT 'pending' CHECK (processed_status IN ('pending', 'processing', 'completed', 'failed')),
  extracted_content TEXT,
  ai_summary TEXT,
  metadata JSONB DEFAULT '{}',
  uploaded_by UUID NOT NULL,
  uploaded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- AI-generated insights from knowledge base
CREATE TABLE public.knowledge_insights (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL,
  insight_type TEXT NOT NULL CHECK (insight_type IN ('pattern', 'recommendation', 'gap_analysis', 'trend', 'optimization')),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  confidence_score NUMERIC CHECK (confidence_score >= 0 AND confidence_score <= 1),
  related_articles UUID[] DEFAULT '{}',
  related_workflows UUID[] DEFAULT '{}',
  data_sources JSONB DEFAULT '{}',
  status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'reviewed', 'implemented', 'dismissed')),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  reviewed_by UUID,
  reviewed_at TIMESTAMP WITH TIME ZONE
);

-- Knowledge search and access logs
CREATE TABLE public.knowledge_access_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  customer_id UUID NOT NULL,
  article_id UUID REFERENCES public.knowledge_articles(id) ON DELETE CASCADE,
  access_type TEXT NOT NULL CHECK (access_type IN ('view', 'search', 'edit', 'download')),
  search_query TEXT,
  timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS on all tables
ALTER TABLE public.knowledge_categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.knowledge_access_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policies for knowledge_categories
CREATE POLICY "Authenticated users can view categories"
  ON public.knowledge_categories FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Admins can manage categories"
  ON public.knowledge_categories FOR ALL
  TO authenticated
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for knowledge_articles
CREATE POLICY "Users can view published articles"
  ON public.knowledge_articles FOR SELECT
  TO authenticated
  USING (status = 'published' OR created_by = auth.uid());

CREATE POLICY "Users can create articles"
  ON public.knowledge_articles FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users can update own articles"
  ON public.knowledge_articles FOR UPDATE
  TO authenticated
  USING (created_by = auth.uid() OR has_role(auth.uid(), 'admin'));

CREATE POLICY "Admins can delete articles"
  ON public.knowledge_articles FOR DELETE
  TO authenticated
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for knowledge_versions
CREATE POLICY "Users can view article versions"
  ON public.knowledge_versions FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "System can insert versions"
  ON public.knowledge_versions FOR INSERT
  TO authenticated
  WITH CHECK (true);

-- RLS Policies for knowledge_files
CREATE POLICY "Users can view files"
  ON public.knowledge_files FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "Users can upload files"
  ON public.knowledge_files FOR INSERT
  TO authenticated
  WITH CHECK (uploaded_by = auth.uid());

CREATE POLICY "Admins can manage files"
  ON public.knowledge_files FOR ALL
  TO authenticated
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for knowledge_insights
CREATE POLICY "Users can view insights"
  ON public.knowledge_insights FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "System can create insights"
  ON public.knowledge_insights FOR INSERT
  TO authenticated
  WITH CHECK (true);

CREATE POLICY "Admins can manage insights"
  ON public.knowledge_insights FOR ALL
  TO authenticated
  USING (has_role(auth.uid(), 'admin'));

-- RLS Policies for knowledge_access_logs
CREATE POLICY "Users can view own access logs"
  ON public.knowledge_access_logs FOR SELECT
  TO authenticated
  USING (user_id = auth.uid() OR has_role(auth.uid(), 'admin'));

CREATE POLICY "System can insert access logs"
  ON public.knowledge_access_logs FOR INSERT
  TO authenticated
  WITH CHECK (user_id = auth.uid());

-- Create triggers for updated_at
CREATE TRIGGER update_knowledge_categories_updated_at
  BEFORE UPDATE ON public.knowledge_categories
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_knowledge_articles_updated_at
  BEFORE UPDATE ON public.knowledge_articles
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Create indexes for performance
CREATE INDEX idx_knowledge_articles_customer ON public.knowledge_articles(customer_id);
CREATE INDEX idx_knowledge_articles_category ON public.knowledge_articles(category_id);
CREATE INDEX idx_knowledge_articles_type ON public.knowledge_articles(article_type);
CREATE INDEX idx_knowledge_articles_status ON public.knowledge_articles(status);
CREATE INDEX idx_knowledge_files_customer ON public.knowledge_files(customer_id);
CREATE INDEX idx_knowledge_files_article ON public.knowledge_files(article_id);
CREATE INDEX idx_knowledge_insights_customer ON public.knowledge_insights(customer_id);
CREATE INDEX idx_knowledge_access_logs_user ON public.knowledge_access_logs(user_id, timestamp);