-- Create roles table to define available roles
CREATE TABLE public.roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Create role permissions table to map roles to dashboard access
CREATE TABLE public.role_permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  role_id UUID NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
  resource_type TEXT NOT NULL, -- 'dashboard', 'feature', etc.
  resource_name TEXT NOT NULL, -- 'executive', 'finance', 'hr', 'it', 'sales', 'operations', 'compliance'
  permission_level TEXT NOT NULL DEFAULT 'view', -- 'view', 'edit', 'admin'
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  UNIQUE(role_id, resource_type, resource_name)
);

-- Update user_roles table to reference new roles table
-- First, we need to migrate existing data
-- Drop the old user_roles table and recreate it
DROP TABLE IF EXISTS public.user_roles CASCADE;

CREATE TABLE public.user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  role_id UUID NOT NULL REFERENCES public.roles(id) ON DELETE CASCADE,
  assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  assigned_by UUID,
  UNIQUE(user_id, role_id)
);

-- Enable RLS on new tables
ALTER TABLE public.roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.role_permissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

-- RLS Policies for roles table
CREATE POLICY "Everyone can view roles"
  ON public.roles FOR SELECT
  USING (true);

CREATE POLICY "Only admins can manage roles"
  ON public.roles FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.user_roles ur
      JOIN public.roles r ON r.id = ur.role_id
      WHERE ur.user_id = auth.uid() AND r.name = 'Super Admin'
    )
  );

-- RLS Policies for role_permissions table
CREATE POLICY "Everyone can view role permissions"
  ON public.role_permissions FOR SELECT
  USING (true);

CREATE POLICY "Only admins can manage role permissions"
  ON public.role_permissions FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.user_roles ur
      JOIN public.roles r ON r.id = ur.role_id
      WHERE ur.user_id = auth.uid() AND r.name = 'Super Admin'
    )
  );

-- RLS Policies for user_roles table
CREATE POLICY "Users can view their own roles"
  ON public.user_roles FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Admins can view all user roles"
  ON public.user_roles FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM public.user_roles ur
      JOIN public.roles r ON r.id = ur.role_id
      WHERE ur.user_id = auth.uid() AND r.name = 'Super Admin'
    )
  );

CREATE POLICY "Admins can manage user roles"
  ON public.user_roles FOR ALL
  USING (
    EXISTS (
      SELECT 1 FROM public.user_roles ur
      JOIN public.roles r ON r.id = ur.role_id
      WHERE ur.user_id = auth.uid() AND r.name = 'Super Admin'
    )
  );

-- Create function to check if user has permission
CREATE OR REPLACE FUNCTION public.has_permission(
  _user_id UUID,
  _resource_type TEXT,
  _resource_name TEXT,
  _min_permission TEXT DEFAULT 'view'
)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.user_roles ur
    JOIN public.role_permissions rp ON rp.role_id = ur.role_id
    WHERE ur.user_id = _user_id
      AND rp.resource_type = _resource_type
      AND rp.resource_name = _resource_name
      AND (
        _min_permission = 'view' OR
        (_min_permission = 'edit' AND rp.permission_level IN ('edit', 'admin')) OR
        (_min_permission = 'admin' AND rp.permission_level = 'admin')
      )
  )
$$;

-- Insert default roles
INSERT INTO public.roles (name, description) VALUES
  ('Super Admin', 'Full system access to all dashboards and features'),
  ('Executive', 'Access to executive dashboard'),
  ('Finance Manager', 'Access to finance dashboard'),
  ('HR Manager', 'Access to HR dashboard'),
  ('IT Manager', 'Access to IT dashboard'),
  ('Sales Manager', 'Access to sales dashboard'),
  ('Operations Manager', 'Access to operations dashboard'),
  ('Compliance Manager', 'Access to compliance dashboard'),
  ('Department Viewer', 'Read-only access to assigned departments');

-- Insert default role permissions for Super Admin (access to everything)
INSERT INTO public.role_permissions (role_id, resource_type, resource_name, permission_level)
SELECT r.id, 'dashboard', dashboard, 'admin'
FROM public.roles r
CROSS JOIN (
  VALUES ('executive'), ('finance'), ('hr'), ('it'), ('sales'), ('operations'), ('compliance'), ('admin')
) AS dashboards(dashboard)
WHERE r.name = 'Super Admin';

-- Insert role permissions for each department manager
INSERT INTO public.role_permissions (role_id, resource_type, resource_name, permission_level)
VALUES
  ((SELECT id FROM roles WHERE name = 'Executive'), 'dashboard', 'executive', 'admin'),
  ((SELECT id FROM roles WHERE name = 'Finance Manager'), 'dashboard', 'finance', 'admin'),
  ((SELECT id FROM roles WHERE name = 'HR Manager'), 'dashboard', 'hr', 'admin'),
  ((SELECT id FROM roles WHERE name = 'IT Manager'), 'dashboard', 'it', 'admin'),
  ((SELECT id FROM roles WHERE name = 'Sales Manager'), 'dashboard', 'sales', 'admin'),
  ((SELECT id FROM roles WHERE name = 'Operations Manager'), 'dashboard', 'operations', 'admin'),
  ((SELECT id FROM roles WHERE name = 'Compliance Manager'), 'dashboard', 'compliance', 'admin');

-- Migrate existing admin users to Super Admin role
INSERT INTO public.user_roles (user_id, role_id, assigned_by)
SELECT 
  'c7dffdb3-10a6-4747-8071-0d281cdeb927'::uuid,
  (SELECT id FROM public.roles WHERE name = 'Super Admin'),
  'c7dffdb3-10a6-4747-8071-0d281cdeb927'::uuid
WHERE EXISTS (SELECT 1 FROM auth.users WHERE id = 'c7dffdb3-10a6-4747-8071-0d281cdeb927'::uuid);

INSERT INTO public.user_roles (user_id, role_id, assigned_by)
SELECT 
  'c696dcc9-6edd-436b-aa9f-7d64b0dd632a'::uuid,
  (SELECT id FROM public.roles WHERE name = 'Super Admin'),
  'c696dcc9-6edd-436b-aa9f-7d64b0dd632a'::uuid
WHERE EXISTS (SELECT 1 FROM auth.users WHERE id = 'c696dcc9-6edd-436b-aa9f-7d64b0dd632a'::uuid);

-- Create trigger to update updated_at
CREATE TRIGGER update_roles_updated_at
  BEFORE UPDATE ON public.roles
  FOR EACH ROW
  EXECUTE FUNCTION public.update_updated_at_column();