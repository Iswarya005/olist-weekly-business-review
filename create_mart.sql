
DROP TABLE IF EXISTS mart_order_summary;

CREATE TABLE mart_order_summary AS
WITH item_totals AS (
    SELECT
        order_id,
        SUM(price) AS total_item_value,
        SUM(freight_value) AS total_freight
    FROM stg_order_items
    GROUP BY order_id
),
payment_totals AS (
    SELECT
        order_id,
        SUM(payment_value) AS total_payment
    FROM stg_payments
    GROUP BY order_id
),
review_totals AS (
    SELECT
        order_id,
        AVG(review_score)::numeric(4,2) AS review_score
    FROM stg_reviews
    GROUP BY order_id
)
SELECT
    o.order_id,
    o.customer_id,
    c.customer_unique_id,
    c.customer_state,
    o.order_status,
    o.order_purchase_timestamp AS purchase_date,
    o.order_delivered_customer_date AS delivered_date,
    o.order_estimated_delivery_date AS estimated_delivery_date,
    COALESCE(i.total_item_value, 0) AS total_item_value,
    COALESCE(i.total_freight, 0) AS total_freight,
    COALESCE(i.total_item_value, 0)
        + COALESCE(i.total_freight, 0) AS total_order_value,
    p.total_payment,
    r.review_score,
    EXTRACT(EPOCH FROM (
        o.order_delivered_customer_date
        - o.order_purchase_timestamp
    )) / 86400.0 AS delivery_days,
    EXTRACT(EPOCH FROM (
        o.order_delivered_customer_date
        - o.order_estimated_delivery_date
    )) / 86400.0 AS delivery_delay_days
FROM stg_orders o
LEFT JOIN stg_customers c
    ON o.customer_id = c.customer_id
LEFT JOIN item_totals i
    ON o.order_id = i.order_id
LEFT JOIN payment_totals p
    ON o.order_id = p.order_id
LEFT JOIN review_totals r
    ON o.order_id = r.order_id;
