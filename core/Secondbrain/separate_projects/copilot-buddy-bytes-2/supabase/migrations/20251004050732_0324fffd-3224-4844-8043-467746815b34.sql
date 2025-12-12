-- Create a default admin account setup
-- This will grant Super Admin role to admin@admin.com when they sign up

-- First, let's create a function that auto-assigns admin role to specific emails
CREATE OR REPLACE FUNCTION public.auto_assign_admin_role()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  admin_role_id uuid;
  admin_emails text[] := ARRAY['admin@admin.com'];
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

-- Create trigger to auto-assign admin role after profile creation
DROP TRIGGER IF EXISTS auto_assign_admin_trigger ON user_profiles;
CREATE TRIGGER auto_assign_admin_trigger
  AFTER INSERT ON user_profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.auto_assign_admin_role();