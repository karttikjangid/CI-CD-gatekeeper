-- Simulating a developer removing a column that breaks the downstream ML pipeline
ALTER TABLE sample_data.ecommerce_db.shopify.raw_customer 
DROP COLUMN email;