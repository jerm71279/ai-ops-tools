-- Assign the Acme Corporation customer to the user profile for jerm712@icloud.com
UPDATE public.user_profiles
SET 
  customer_id = '710092dc-c33c-4f8e-8c65-11fc62982c96',
  updated_at = now()
WHERE user_id = '7aea5ddd-61b6-4aa5-b271-cbe2751feb83';