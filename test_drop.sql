-- Simulating a developer removing PII (email) without realizing 
-- that the downstream Tier-1 customer features dashboard relies on it.

ALTER TABLE sample_data.ecommerce_db.shopify.raw_customer 
DROP COLUMN email;