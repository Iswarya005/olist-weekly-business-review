SELECT COUNT(*) AS null_order_ids
FROM stg_orders
WHERE order_id IS NULL;

SELECT COUNT(*) AS duplicate_order_ids
FROM (
    SELECT order_id
    FROM stg_orders
    GROUP BY order_id
    HAVING COUNT(*) > 1
) AS duplicates;

SELECT COUNT(*) AS invalid_delivery_dates
FROM stg_orders
WHERE order_delivered_customer_date
      < order_purchase_timestamp;

WITH item_totals AS (
    SELECT
        order_id,
        SUM(price + freight_value) AS item_and_freight_total
    FROM stg_order_items
    GROUP BY order_id
),
payment_totals AS (
    SELECT
        order_id,
        SUM(payment_value) AS payment_total
    FROM stg_payments
    GROUP BY order_id
)
SELECT COUNT(*) AS payment_mismatches
FROM item_totals i
JOIN payment_totals p
    ON i.order_id = p.order_id
WHERE ABS(i.item_and_freight_total - p.payment_total) > 0.01;

SELECT COUNT(*) AS orders_without_customer
FROM stg_orders o
LEFT JOIN stg_customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Data Quality Findings
-- 1. Null order IDs: 0
-- 2. Duplicate order IDs: 0
-- 3. Invalid delivery dates: 0
-- 4. Payment mismatches: 303
-- 5. Orders without matching customers: 0
--
-- Handling:
-- Payment mismatches are flagged for investigation.
-- No source records are deleted or silently modified.
-- The strict automated quality check raises an alarm
-- when payment mismatches are present.


