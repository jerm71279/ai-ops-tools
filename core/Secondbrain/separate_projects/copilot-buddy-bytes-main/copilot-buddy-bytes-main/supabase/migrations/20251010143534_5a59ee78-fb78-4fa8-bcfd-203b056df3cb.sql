-- Add incident_id support to evidence_files table for incident evidence uploads
ALTER TABLE public.evidence_files 
ADD COLUMN incident_id UUID REFERENCES public.incidents(id) ON DELETE CASCADE;

-- Create index for better query performance
CREATE INDEX idx_evidence_files_incident_id ON public.evidence_files(incident_id);

-- Update RLS policy to allow viewing evidence for incidents
CREATE POLICY "Users can view incident evidence in their organization"
ON public.evidence_files
FOR SELECT
USING (
  incident_id IS NOT NULL 
  AND customer_id IN (
    SELECT customer_id 
    FROM user_profiles 
    WHERE user_id = auth.uid()
  )
);

-- Allow users to insert incident evidence
CREATE POLICY "Users can upload incident evidence"
ON public.evidence_files
FOR INSERT
WITH CHECK (
  incident_id IS NOT NULL
  AND customer_id IN (
    SELECT customer_id 
    FROM user_profiles 
    WHERE user_id = auth.uid()
  )
  AND uploaded_by = auth.uid()
);