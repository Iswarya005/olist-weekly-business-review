
import os
from pathlib import Path

import pandas as pd
import psycopg

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "olist_dw",
    "user": "postgres",
    "password": os.environ.get("OLIST_DB_PASSWORD", ""),
}

QUERIES = {
    "north_star_monthly_revenue": """
        SELECT
            DATE_TRUNC('month', purchase_date)::date AS month,
            ROUND(SUM(total_order_value)::numeric, 2)
                AS delivered_revenue
        FROM mart_order_summary
        WHERE order_status = 'delivered'
        GROUP BY 1
        ORDER BY 1
    """,

    "repeat_purchase_rate": """
        WITH customer_orders AS (
            SELECT
                customer_unique_id,
                COUNT(DISTINCT order_id) AS order_count
            FROM mart_order_summary
            WHERE customer_unique_id IS NOT NULL
              AND order_status NOT IN ('canceled', 'unavailable')
            GROUP BY customer_unique_id
        )
        SELECT
            COUNT(*) AS total_customers,
            COUNT(*) FILTER (
                WHERE order_count > 1
            ) AS repeat_customers,
            ROUND(
                100.0 * COUNT(*) FILTER (
                    WHERE order_count > 1
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS repeat_purchase_rate_pct
        FROM customer_orders
    """,

    "average_delivery_delay": """
        SELECT
            ROUND(AVG(delivery_delay_days)::numeric, 2)
                AS average_delay_days
        FROM mart_order_summary
        WHERE order_status = 'delivered'
          AND delivered_date IS NOT NULL
          AND estimated_delivery_date IS NOT NULL
    """,

    "average_review_score": """
        SELECT
            ROUND(AVG(review_score)::numeric, 2)
                AS average_review_score
        FROM mart_order_summary
        WHERE review_score IS NOT NULL
    """,

    "late_delivery_rate": """
        SELECT
            COUNT(*) FILTER (
                WHERE delivery_delay_days > 0
            ) AS late_orders,
            COUNT(*) AS delivered_orders,
            ROUND(
                100.0 * COUNT(*) FILTER (
                    WHERE delivery_delay_days > 0
                ) / NULLIF(COUNT(*), 0),
                2
            ) AS late_delivery_rate_pct
        FROM mart_order_summary
        WHERE order_status = 'delivered'
          AND delivered_date IS NOT NULL
          AND estimated_delivery_date IS NOT NULL
    """,
}


def main():
    if not DB_CONFIG["password"]:
        raise RuntimeError(
            "Set OLIST_DB_PASSWORD in the terminal first."
        )

    with psycopg.connect(**DB_CONFIG) as conn:
        for name, query in QUERIES.items():
            df = pd.read_sql_query(query, conn)

            print(f"\n--- {name} ---")
            print(df.to_string(index=False))

            output_path = REPORTS_DIR / f"{name}.csv"
            df.to_csv(output_path, index=False)
            print(f"Saved results to: {output_path}")


if __name__ == "__main__":
    main()
