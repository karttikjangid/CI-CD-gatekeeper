### WARNING: CRITICAL DOWNSTREAM IMPACT DETECTED 

This Pull Request modifies schema structures that directly affect **1 critical downstream assets**.

| Source Table Altered | Downstream Asset FQN | Asset Type | Risk Classification |
|---|---|---|---|
| raw_customer | sample_data.ecommerce_db.shopify.dim_customer | **Table** | Tier-1 |


### Remediation Patch
```sql
CREATE VIEW raw_customer AS SELECT customer_id, shop_id, average_order_size, total_order_count, total_order_value, first_order_date, last_order_date, rank, new, returning, loyal, at_risk, dormant, promising, predicted_average_number_of_days_between_orders, expected_purchase_value_in_next_30_days, first_name, last_name, city, region, country, email, phone, verified_email, created_at, accepts_marketing, CAST(NULL AS STRUCT) AS customer, CAST(NULL AS ARRAY<STRUCT>) AS shipping_address, CAST(NULL AS ARRAY<STRUCT>) AS orders
```
