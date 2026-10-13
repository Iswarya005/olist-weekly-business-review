# Weekly Business Review — VP Memo

**Subject:** E-commerce Marketplace Performance Review  
**Period:** Analysis period covered by the Olist dataset

## Executive Summary

This review evaluates marketplace revenue, customer repeat purchasing, delivery performance, and customer satisfaction. Monthly delivered-order revenue is used as the North Star metric. Repeat-purchase rate, average delivery delay, review score, and late-delivery rate provide supporting indicators of customer retention and operational performance.

## Key Findings

**1. Revenue:** Monthly delivered-order revenue is visualized in `charts/chart1_monthly_revenue.png`. Review the trend to identify months with growth or decline and investigate the business factors behind significant changes.

**2. Customer retention:** The repeat-purchase chart is available in `charts/chart2_repeat_purchases.png`. The previously calculated repeat-purchase rate was 3.04% under the selected customer and order-status definition. This suggests an opportunity to investigate customer retention and encourage repeat purchases.

**3. Delivery and satisfaction:** `charts/chart3_delay_by_review.png` compares average delivery delay with review scores. Use this evidence to assess whether longer delays are associated with lower customer ratings; the chart alone does not establish causation.

**4. Delivery reliability:** `charts/chart4_delivery_timeliness.png` compares late deliveries with on-time or early deliveries. Use the actual chart values to assess the scale of the delivery-performance problem.

## Recommendations

- Investigate months with significant revenue declines and identify the contributing categories, customer segments, or order trends.
- Explore customer-retention initiatives, such as post-purchase engagement and relevant product recommendations.
- Review late-delivery patterns and investigate sellers, regions, or logistics stages associated with delays.
- Monitor review scores alongside delivery performance to prioritize operational improvements.

## Data Quality Consideration

The pipeline identified 303 orders where aggregated item-plus-freight totals differed from recorded payment totals by more than 0.01. These discrepancies remain flagged for investigation. Business decisions based on financial totals should account for this unresolved data-quality issue.

## Next Review

Track monthly delivered-order revenue, repeat-purchase rate, delivery delay, review score, and late-delivery rate in the next review cycle. Validate the payment discrepancies before treating financial comparisons as fully reconciled.