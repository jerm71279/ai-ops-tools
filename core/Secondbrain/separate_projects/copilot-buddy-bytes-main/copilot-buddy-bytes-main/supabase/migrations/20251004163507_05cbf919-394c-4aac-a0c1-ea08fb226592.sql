-- Create applications table for managing service portals
CREATE TABLE public.applications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  icon_name TEXT NOT NULL DEFAULT 'Package',
  app_url TEXT,
  category TEXT NOT NULL DEFAULT 'productivity',
  auth_type TEXT NOT NULL DEFAULT 'microsoft365',
  is_active BOOLEAN NOT NULL DEFAULT true,
  display_order INTEGER DEFAULT 0,
  config JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create application_access table for role/department-based access control
CREATE TABLE public.application_access (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID NOT NULL REFERENCES public.applications(id) ON DELETE CASCADE,
  department TEXT,
  role_id UUID REFERENCES public.roles(id) ON DELETE CASCADE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(application_id, department),
  UNIQUE(application_id, role_id),
  CHECK (department IS NOT NULL OR role_id IS NOT NULL)
);

-- Enable RLS
ALTER TABLE public.applications ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.application_access ENABLE ROW LEVEL SECURITY;

-- RLS Policies for applications
CREATE POLICY "Everyone can view active applications"
ON public.applications FOR SELECT
USING (is_active = true);

CREATE POLICY "Admins can manage applications"
ON public.applications FOR ALL
USING (has_role(auth.uid(), 'admin'::app_role));

-- RLS Policies for application_access
CREATE POLICY "Everyone can view application access"
ON public.application_access FOR SELECT
USING (true);

CREATE POLICY "Admins can manage application access"
ON public.application_access FOR ALL
USING (has_role(auth.uid(), 'admin'::app_role));

-- Trigger for updated_at
CREATE TRIGGER update_applications_updated_at
BEFORE UPDATE ON public.applications
FOR EACH ROW
EXECUTE FUNCTION public.update_updated_at_column();

-- Insert default Microsoft 365 applications
INSERT INTO public.applications (name, description, icon_name, app_url, category, auth_type, display_order) VALUES
('Outlook', 'Email and calendar management', 'Mail', '/portal?tab=microsoft365', 'communication', 'microsoft365', 1),
('OneDrive', 'Cloud file storage and sharing', 'Cloud', '/portal?tab=microsoft365', 'productivity', 'microsoft365', 2),
('Teams', 'Chat, meetings, and collaboration', 'Users', '/portal?tab=microsoft365', 'communication', 'microsoft365', 3),
('SharePoint', 'Document management and intranet', 'FolderOpen', '/portal?tab=microsoft365', 'productivity', 'microsoft365', 4),
('Calendar', 'Schedule and event management', 'Calendar', '/portal?tab=microsoft365', 'productivity', 'microsoft365', 5);

-- Grant access to all departments for Microsoft 365 apps by default
INSERT INTO public.application_access (application_id, department)
SELECT id, dept FROM public.applications, 
UNNEST(ARRAY['IT', 'HR', 'Finance', 'Sales', 'Operations', 'Executive']) AS dept
WHERE category = 'communication' OR category = 'productivity';