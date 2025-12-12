-- Fix workflows and workflow_executions RLS policies

-- Add policies for regular users to access workflows
CREATE POLICY "Users can view workflows in their organization"
ON public.workflows
FOR SELECT
USING (customer_id = get_user_customer_id(auth.uid()));

CREATE POLICY "Users can create workflows"
ON public.workflows
FOR INSERT
WITH CHECK (customer_id = get_user_customer_id(auth.uid()));

CREATE POLICY "Users can update workflows in their organization"
ON public.workflows
FOR UPDATE
USING (customer_id = get_user_customer_id(auth.uid()));

CREATE POLICY "Users can delete workflows in their organization"
ON public.workflows
FOR DELETE
USING (customer_id = get_user_customer_id(auth.uid()));

-- Fix workflow_executions policy to use security definer function
DROP POLICY IF EXISTS "Users can view workflow executions in their organization" ON public.workflow_executions;

CREATE POLICY "Users can view workflow executions in their organization"
ON public.workflow_executions
FOR SELECT
USING (customer_id = get_user_customer_id(auth.uid()));