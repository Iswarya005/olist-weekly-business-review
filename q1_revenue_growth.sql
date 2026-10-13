
-- Query 1: Monthly revenue and month-over-month growth

WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', purchase_date)::date AS revenue_month,
        SUM(total_order_value) AS revenue
    FROM mart_order_summary
    WHERE order_status NOT IN ('canceled', 'unavailable')
    GROUP BY DATE_TRUNC('month', purchase_date)
),
revenue_with_previous AS (
    SELECT
        revenue_month,
        revenue,
        LAG(revenue) OVER (
            ORDER BY revenue_month
        ) AS previous_month_revenue
    FROM monthly_revenue
)
SELECT
    revenue_month,
    ROUND(revenue, 2) AS revenue,
    ROUND(previous_month_revenue, 2) AS previous_month_revenue,
    ROUND(
        100.0 * (revenue - previous_month_revenue)
        / NULLIF(previous_month_revenue, 0),
        2
    ) AS growth_percentage
FROM revenue_with_previous
ORDER BY revenue_month;
