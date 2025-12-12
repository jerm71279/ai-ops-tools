-- Create SharePoint sync configuration table
CREATE TABLE public.sharepoint_sync_config (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
  site_id TEXT NOT NULL,
  site_name TEXT NOT NULL,
  site_url TEXT NOT NULL,
  library_id TEXT,
  library_name TEXT,
  sync_enabled BOOLEAN NOT NULL DEFAULT true,
  last_sync_at TIMESTAMPTZ,
  sync_frequency_minutes INTEGER NOT NULL DEFAULT 60,
  filter_extensions TEXT[], -- e.g., ['pdf', 'docx', 'xlsx']
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(customer_id, site_id, library_id)
);

-- Enable RLS
ALTER TABLE public.sharepoint_sync_config ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view their own sync configs"
  ON public.sharepoint_sync_config
  FOR SELECT
  USING (auth.uid() IN (
    SELECT user_id FROM user_profiles WHERE customer_id = sharepoint_sync_config.customer_id
  ));

CREATE POLICY "Users can create sync configs"
  ON public.sharepoint_sync_config
  FOR INSERT
  WITH CHECK (auth.uid() IN (
    SELECT user_id FROM user_profiles WHERE customer_id = sharepoint_sync_config.customer_id
  ));

CREATE POLICY "Users can update their own sync configs"
  ON public.sharepoint_sync_config
  FOR UPDATE
  USING (auth.uid() IN (
    SELECT user_id FROM user_profiles WHERE customer_id = sharepoint_sync_config.customer_id
  ));

CREATE POLICY "Users can delete their own sync configs"
  ON public.sharepoint_sync_config
  FOR DELETE
  USING (auth.uid() IN (
    SELECT user_id FROM user_profiles WHERE customer_id = sharepoint_sync_config.customer_id
  ));

-- Create trigger for updated_at
CREATE TRIGGER update_sharepoint_sync_config_updated_at
  BEFORE UPDATE ON public.sharepoint_sync_config
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();

-- Create SharePoint sync logs table
CREATE TABLE public.sharepoint_sync_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sync_config_id UUID NOT NULL REFERENCES sharepoint_sync_config(id) ON DELETE CASCADE,
  sync_started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  sync_completed_at TIMESTAMPTZ,
  status TEXT NOT NULL DEFAULT 'running', -- running, completed, failed
  files_synced INTEGER DEFAULT 0,
  files_failed INTEGER DEFAULT 0,
  error_message TEXT,
  sync_details JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE public.sharepoint_sync_logs ENABLE ROW LEVEL SECURITY;

-- RLS Policy
CREATE POLICY "Users can view their own sync logs"
  ON public.sharepoint_sync_logs
  FOR SELECT
  USING (sync_config_id IN (
    SELECT id FROM sharepoint_sync_config WHERE customer_id IN (
      SELECT customer_id FROM user_profiles WHERE user_id = auth.uid()
    )
  ));

-- Create index for performance
CREATE INDEX idx_sharepoint_sync_logs_config ON sharepoint_sync_logs(sync_config_id);
CREATE INDEX idx_sharepoint_sync_logs_status ON sharepoint_sync_logs(status);
CREATE INDEX idx_sharepoint_sync_config_customer ON sharepoint_sync_config(customer_id);
CREATE INDEX idx_sharepoint_sync_config_enabled ON sharepoint_sync_config(sync_enabled) WHERE sync_enabled = true;