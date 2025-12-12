-- Add NinjaOne ticket integration fields to change_requests
ALTER TABLE change_requests
ADD COLUMN ninjaone_ticket_id TEXT,
ADD COLUMN ninjaone_ticket_number TEXT,
ADD COLUMN ninjaone_ticket_status TEXT,
ADD COLUMN ninjaone_ticket_url TEXT,
ADD COLUMN ninjaone_ticket_synced_at TIMESTAMP WITH TIME ZONE;

-- Add index for faster lookups
CREATE INDEX idx_change_requests_ninjaone_ticket_id ON change_requests(ninjaone_ticket_id);

COMMENT ON COLUMN change_requests.ninjaone_ticket_id IS 'NinjaOne ticket ID linked to this change request';
COMMENT ON COLUMN change_requests.ninjaone_ticket_number IS 'Human-readable NinjaOne ticket number';
COMMENT ON COLUMN change_requests.ninjaone_ticket_status IS 'Current status of the linked NinjaOne ticket';
COMMENT ON COLUMN change_requests.ninjaone_ticket_url IS 'Direct URL to the NinjaOne ticket';
COMMENT ON COLUMN change_requests.ninjaone_ticket_synced_at IS 'Last time the ticket status was synced from NinjaOne';