
SELECT
    review_score,
    COUNT(*) AS reviewed_delivered_orders,
    ROUND(AVG(delivery_delay_days)::numeric, 2)
        AS average_delay_days,
    COUNT(*) FILTER (
        WHERE delivery_delay_days > 0
    ) AS late_orders,
    COUNT(*) FILTER (
        WHERE delivery_delay_days <= 0
    ) AS on_time_or_early_orders
FROM mart_order_summary
WHERE delivered_date IS NOT NULL
  AND estimated_delivery_date IS NOT NULL
  AND review_score IS NOT NULL
GROUP BY review_score
ORDER BY review_score;
