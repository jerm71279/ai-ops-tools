-- Fix user profiles for Microsoft 365 OAuth users
-- Step 1: Drop ALL existing triggers and functions to start fresh

-- Drop all triggers on auth.users
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users CASCADE;
DROP TRIGGER IF EXISTS on_auth_user_created_assign_admin ON auth.users CASCADE;

-- Drop all related functions
DROP FUNCTION IF EXISTS public.auto_assign_admin_role() CASCADE;
DROP FUNCTION IF EXISTS public.auto_assign_admin_role_after_profile() CASCADE;
DROP FUNCTION IF EXISTS public.handle_new_user() CASCADE;
DROP FUNCTION IF EXISTS public.handle_new_user_profile() CASCADE;

-- Step 2: Create NEW function to handle user profile creation for ALL auth methods
CREATE OR REPLACE FUNCTION public.handle_new_user_profile()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  user_full_name text;
  admin_role_id uuid;
  admin_emails text[] := ARRAY['admin@admin.com', 'jerm712@icloud.com'];
BEGIN
  -- Extract user information from metadata (works for both email and OAuth)
  user_full_name := COALESCE(
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'name',
    NEW.email
  );

  -- Insert user profile
  INSERT INTO public.user_profiles (
    user_id,
    full_name,
    department,
    customer_id,
    created_at,
    updated_at
  )
  VALUES (
    NEW.id,
    user_full_name,
    NULL,
    NULL,
    now(),
    now()
  )
  ON CONFLICT (user_id) DO NOTHING;

  -- Handle admin role assignment
  IF NEW.email = ANY(admin_emails) THEN
    SELECT id INTO admin_role_id
    FROM roles
    WHERE name = 'Super Admin'
    LIMIT 1;
    
    IF admin_role_id IS NOT NULL THEN
      INSERT INTO user_roles (user_id, role_id)
      VALUES (NEW.id, admin_role_id)
      ON CONFLICT (user_id, role_id) DO NOTHING;
    END IF;
  END IF;

  RETURN NEW;
END;
$$;

-- Step 3: Create single trigger that handles everything
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW 
  EXECUTE FUNCTION public.handle_new_user_profile();

-- Step 4: Backfill existing users who don't have profiles
INSERT INTO public.user_profiles (
  user_id,
  full_name,
  department,
  customer_id,
  created_at,
  updated_at
)
SELECT 
  u.id,
  COALESCE(
    u.raw_user_meta_data->>'full_name',
    u.raw_user_meta_data->>'name',
    u.email
  ) as full_name,
  NULL as department,
  NULL as customer_id,
  u.created_at,
  now() as updated_at
FROM auth.users u
LEFT JOIN public.user_profiles up ON up.user_id = u.id
WHERE up.user_id IS NULL;

-- Add helpful comment
COMMENT ON FUNCTION public.handle_new_user_profile() IS 
  'Automatically creates user profile for all authentication methods (email, OAuth, etc.) and assigns admin roles to whitelisted emails';