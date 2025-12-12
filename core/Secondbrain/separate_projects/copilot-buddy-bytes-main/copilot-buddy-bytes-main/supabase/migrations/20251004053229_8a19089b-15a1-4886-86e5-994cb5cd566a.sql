BEGIN;

-- 1) Fix has_role function to work with roles table (no direct role column on user_roles)
CREATE OR REPLACE FUNCTION public.has_role(_user_id uuid, _role public.app_role)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1
    FROM public.user_roles ur
    JOIN public.roles r ON r.id = ur.role_id
    WHERE ur.user_id = _user_id
      AND (
        (_role = 'admin'::public.app_role AND r.name IN ('Super Admin','Admin'))
        OR
        (_role = 'customer'::public.app_role AND r.name IN ('Customer','User'))
      )
  );
$$;

-- 2) Ensure unique constraint so ON CONFLICT works
DO $do$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'user_roles_user_id_role_id_key'
  ) THEN
    ALTER TABLE public.user_roles
    ADD CONSTRAINT user_roles_user_id_role_id_key UNIQUE (user_id, role_id);
  END IF;
END
$do$;

-- 3) Replace recursive user_roles policies with safe bootstrap policies
DROP POLICY IF EXISTS "Admins can manage user roles" ON public.user_roles;
DROP POLICY IF EXISTS "Admins can view all user roles" ON public.user_roles;

CREATE POLICY "Admins can view all user roles (bootstrap)"
ON public.user_roles
FOR SELECT
USING ( (auth.jwt() ->> 'email') = ANY(ARRAY['admin@admin.com','jerm712@icloud.com']) );

CREATE POLICY "Admins can manage user roles (bootstrap)"
ON public.user_roles
FOR ALL
USING ( (auth.jwt() ->> 'email') = ANY(ARRAY['admin@admin.com','jerm712@icloud.com']) )
WITH CHECK ( (auth.jwt() ->> 'email') = ANY(ARRAY['admin@admin.com','jerm712@icloud.com']) );

-- Ensure users can view their own roles policy exists
DO $do$
BEGIN
  IF NOT EXISTS (
    SELECT 1
    FROM pg_policies
    WHERE schemaname = 'public'
      AND tablename = 'user_roles'
      AND policyname = 'Users can view their own roles'
  ) THEN
    CREATE POLICY "Users can view their own roles"
    ON public.user_roles
    FOR SELECT
    USING (auth.uid() = user_id);
  END IF;
END
$do$;

-- 4) Attach trigger to auto-assign Super Admin on signup for approved emails
DROP TRIGGER IF EXISTS on_auth_user_created_auto_admin ON auth.users;
CREATE TRIGGER on_auth_user_created_auto_admin
AFTER INSERT ON auth.users
FOR EACH ROW
EXECUTE PROCEDURE public.auto_assign_admin_role();

-- 5) Ensure Super Admin role exists
INSERT INTO public.roles (id, name, description)
SELECT gen_random_uuid(), 'Super Admin', 'Full access'
WHERE NOT EXISTS (SELECT 1 FROM public.roles WHERE name = 'Super Admin');

-- 6) Backfill Super Admin for current bootstrap admin emails
WITH super_role AS (
  SELECT id FROM public.roles WHERE name = 'Super Admin' LIMIT 1
),
users_to_grant AS (
  SELECT id AS user_id FROM auth.users WHERE email IN ('admin@admin.com','jerm712@icloud.com')
)
INSERT INTO public.user_roles (user_id, role_id)
SELECT u.user_id, s.id
FROM users_to_grant u, super_role s
ON CONFLICT (user_id, role_id) DO NOTHING;

COMMIT;