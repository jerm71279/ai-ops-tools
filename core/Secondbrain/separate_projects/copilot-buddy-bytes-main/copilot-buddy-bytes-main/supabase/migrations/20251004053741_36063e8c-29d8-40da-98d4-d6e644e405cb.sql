DO $$
DECLARE
  super_admin_id uuid;
  target_user_id uuid;
BEGIN
  -- Ensure Super Admin role exists
  INSERT INTO public.roles (id, name, description)
  SELECT gen_random_uuid(), 'Super Admin', 'Full access'
  WHERE NOT EXISTS (SELECT 1 FROM public.roles WHERE name = 'Super Admin');

  SELECT id INTO super_admin_id FROM public.roles WHERE name = 'Super Admin' LIMIT 1;
  SELECT id INTO target_user_id FROM auth.users WHERE email = 'jerm712@icloud.com' LIMIT 1;

  IF super_admin_id IS NOT NULL AND target_user_id IS NOT NULL THEN
    INSERT INTO public.user_roles (user_id, role_id)
    VALUES (target_user_id, super_admin_id)
    ON CONFLICT (user_id, role_id) DO NOTHING;
  END IF;
END $$;