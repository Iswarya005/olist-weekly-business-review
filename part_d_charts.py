
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import psycopg

PROJECT_DIR = Path(__file__).resolve().parent.parent
CHART_DIR = PROJECT_DIR / "reports" / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "olist_dw",
    "user": "postgres",
    "password": os.environ.get("OLIST_DB_PASSWORD", ""),
}


def fetch_data(conn, query):
    return pd.read_sql_query(query, conn)


def main():
    if not DB_CONFIG["password"]:
        raise RuntimeError(
            "Set OLIST_DB_PASSWORD in the terminal first."
        )

    with psycopg.connect(**DB_CONFIG) as conn:

        # Chart 1: Monthly delivered-order revenue
        revenue = fetch_data(conn, """
            SELECT
                DATE_TRUNC('month', purchase_date)::date AS month,
                SUM(total_order_value) AS revenue
            FROM mart_order_summary
            WHERE order_status = 'delivered'
            GROUP BY 1
            ORDER BY 1
        """)

        if revenue.empty:
            raise ValueError("No monthly revenue data found.")

        revenue["month"] = pd.to_datetime(revenue["month"])

        plt.figure(figsize=(10, 5))
        plt.plot(revenue["month"], revenue["revenue"], marker="o")
        plt.title("Monthly Delivered-Order Revenue")
        plt.xlabel("Month")
        plt.ylabel("Revenue (dataset currency units)")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(
            CHART_DIR / "chart1_monthly_revenue.png",
            dpi=300
        )
        plt.close()

        # Chart 2: Repeat-purchase rate
        repeat = fetch_data(conn, """
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
                COUNT(*) FILTER (WHERE order_count > 1) AS repeat,
                COUNT(*) AS total
            FROM customer_orders
        """)

        repeat_rate = (
            100 * repeat.loc[0, "repeat"] / repeat.loc[0, "total"]
            if repeat.loc[0, "total"] else 0
        )

        plt.figure(figsize=(6, 5))
        plt.bar(
            ["Repeat customers", "One-order customers"],
            [
                repeat.loc[0, "repeat"],
                repeat.loc[0, "total"] - repeat.loc[0, "repeat"],
            ],
        )
        plt.title(f"Customer Repeat Purchasing ({repeat_rate:.2f}%)")
        plt.ylabel("Number of customers")
        plt.tight_layout()
        plt.savefig(
            CHART_DIR / "chart2_repeat_purchases.png",
            dpi=300
        )
        plt.close()

        # Chart 3: Average delivery delay by review score
        delay = fetch_data(conn, """
            SELECT
                review_score,
                AVG(delivery_delay_days) AS average_delay
            FROM mart_order_summary
            WHERE order_status = 'delivered'
              AND review_score IS NOT NULL
              AND delivery_delay_days IS NOT NULL
            GROUP BY review_score
            ORDER BY review_score
        """)

        if delay.empty:
            raise ValueError("No delivery-delay/review data found.")

        plt.figure(figsize=(8, 5))
        plt.bar(delay["review_score"], delay["average_delay"])
        plt.axhline(0, linestyle="--")
        plt.title("Average Delivery Delay by Review Score")
        plt.xlabel("Review score (1–5)")
        plt.ylabel("Average delay (days; negative = early)")
        plt.tight_layout()
        plt.savefig(
            CHART_DIR / "chart3_delay_by_review.png",
            dpi=300
        )
        plt.close()

        # Chart 4: Late versus on-time/early deliveries
        delivery = fetch_data(conn, """
            SELECT
                COUNT(*) FILTER (
                    WHERE delivery_delay_days > 0
                ) AS late_orders,
                COUNT(*) FILTER (
                    WHERE delivery_delay_days <= 0
                ) AS on_time_or_early_orders
            FROM mart_order_summary
            WHERE order_status = 'delivered'
              AND delivered_date IS NOT NULL
              AND estimated_delivery_date IS NOT NULL
        """)

        counts = [
            delivery.loc[0, "late_orders"],
            delivery.loc[0, "on_time_or_early_orders"],
        ]

        plt.figure(figsize=(7, 5))
        plt.bar(["Late", "On time or early"], counts)
        plt.title("Delivery Timeliness")
        plt.ylabel("Number of delivered orders")
        plt.tight_layout()
        plt.savefig(
            CHART_DIR / "chart4_delivery_timeliness.png",
            dpi=300
        )
        plt.close()

    print("All four charts created successfully:")
    for path in sorted(CHART_DIR.glob("chart*.png")):
        print(path)


if __name__ == "__main__":
    main()
