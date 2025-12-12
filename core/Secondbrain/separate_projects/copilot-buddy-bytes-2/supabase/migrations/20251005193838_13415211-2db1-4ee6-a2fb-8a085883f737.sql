-- Remove duplicate ISO 27001 framework entry
-- Delete customer frameworks linked to the duplicate
DELETE FROM customer_frameworks WHERE framework_id = '7b8e0484-fcce-42aa-ac0c-153f9d45926a';

-- Delete controls linked to the duplicate
DELETE FROM compliance_controls WHERE framework_id = '7b8e0484-fcce-42aa-ac0c-153f9d45926a';

-- Delete the duplicate framework
DELETE FROM compliance_frameworks WHERE id = '7b8e0484-fcce-42aa-ac0c-153f9d45926a';