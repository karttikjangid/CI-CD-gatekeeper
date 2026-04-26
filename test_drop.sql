-- AUTO-MEDIC TEST CASE: Destructive Schema Change
-- Impact: High (Downstream ML Feature Store)
ALTER TABLE sample_data.ecommerce_db.shopify.raw_customer 
DROP COLUMN email;

-- Adding a harmless change to prove the AST parser differentiates between nodes
ALTER TABLE sample_data.ecommerce_db.shopify.raw_customer 
ADD COLUMN last_audit_timestamp   TIMESTAMP;