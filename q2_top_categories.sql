
-- Query 2: Top 3 product categories by revenue
-- for each customer state

WITH category_revenue AS (
    SELECT
        c.customer_state,
        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'Unknown'
        ) AS product_category,
        SUM(oi.price) AS revenue
    FROM stg_orders o
    JOIN stg_customers c
        ON o.customer_id = c.customer_id
    JOIN stg_order_items oi
        ON o.order_id = oi.order_id
    LEFT JOIN stg_products p
        ON oi.product_id = p.product_id
    LEFT JOIN stg_category_translation t
        ON p.product_category_name = t.product_category_name
    WHERE o.order_status NOT IN ('canceled', 'unavailable')
    GROUP BY
        c.customer_state,
        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'Unknown'
        )
),
ranked_categories AS (
    SELECT
        customer_state,
        product_category,
        revenue,
        DENSE_RANK() OVER (
            PARTITION BY customer_state
            ORDER BY revenue DESC
        ) AS category_rank
    FROM category_revenue
)
SELECT
    customer_state,
    product_category,
    ROUND(revenue, 2) AS revenue,
    category_rank
FROM ranked_categories
WHERE category_rank <= 3
ORDER BY customer_state, category_rank, product_category;
