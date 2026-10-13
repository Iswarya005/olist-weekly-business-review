
-- Query 3: Seven-day rolling average of daily order count

WITH daily_orders AS (
    SELECT
        purchase_date::date AS order_date,
        COUNT(DISTINCT order_id) AS daily_order_count
    FROM mart_order_summary
    WHERE purchase_date IS NOT NULL
    GROUP BY purchase_date::date
)
SELECT
    order_date,
    daily_order_count,
    ROUND(
        AVG(daily_order_count) OVER (
            ORDER BY order_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ),
        2
    ) AS rolling_7_day_average
FROM daily_orders
ORDER BY order_date;
