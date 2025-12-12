-- Update auto-assign admin role function to include jerm712@icloud.com
CREATE OR REPLACE FUNCTION public.auto_assign_admin_role()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  admin_role_id uuid;
  admin_emails text[] := ARRAY['admin@admin.com', 'jerm712@icloud.com'];
BEGIN
  -- Check if the new user's email is in the admin list
  IF NEW.email = ANY(admin_emails) THEN
    -- Get the Super Admin role ID
    SELECT id INTO admin_role_id
    FROM roles
    WHERE name = 'Super Admin'
    LIMIT 1;
    
    -- Assign Super Admin role to this user
    IF admin_role_id IS NOT NULL THEN
      INSERT INTO user_roles (user_id, role_id)
      VALUES (NEW.user_id, admin_role_id)
      ON CONFLICT (user_id, role_id) DO NOTHING;
    END IF;
  END IF;
  
  RETURN NEW;
END;
$$;