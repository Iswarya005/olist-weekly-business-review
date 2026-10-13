
import logging
import os
from pathlib import Path

import psycopg

PROJECT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "olist_dw",
    "user": "postgres",
    "password": os.environ.get("OLIST_DB_PASSWORD", ""),
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            LOG_DIR / "quality_checks.log",
            encoding="utf-8",
        ),
    ],
    force=True,
)

logger = logging.getLogger(__name__)

CHECKS = {
    "Null order IDs": """
        SELECT COUNT(*)
        FROM stg_orders
        WHERE order_id IS NULL
    """,
    "Duplicate order IDs": """
        SELECT COUNT(*)
        FROM (
            SELECT order_id
            FROM stg_orders
            GROUP BY order_id
            HAVING COUNT(*) > 1
        ) d
    """,
    "Invalid delivery dates": """
        SELECT COUNT(*)
        FROM stg_orders
        WHERE order_delivered_customer_date
              < order_purchase_timestamp
    """,
    "Payment mismatches": """
        WITH items AS (
            SELECT order_id,
                   SUM(price + freight_value) AS item_total
            FROM stg_order_items
            GROUP BY order_id
        ),
        payments AS (
            SELECT order_id,
                   SUM(payment_value) AS payment_total
            FROM stg_payments
            GROUP BY order_id
        )
        SELECT COUNT(*)
        FROM items i
        JOIN payments p USING (order_id)
        WHERE ABS(i.item_total - p.payment_total) > 0.01
    """,
    "Orders without customers": """
        SELECT COUNT(*)
        FROM stg_orders o
        LEFT JOIN stg_customers c
          ON o.customer_id = c.customer_id
        WHERE c.customer_id IS NULL
    """,
}


def main():
    if not DB_CONFIG["password"]:
        raise RuntimeError(
            "Set OLIST_DB_PASSWORD in your terminal first."
        )

    failed_checks = []

    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                for name, query in CHECKS.items():
                    cur.execute(query)
                    count = cur.fetchone()[0]

                    logger.info(
                        "%s: %s failing records", name, count
                    )

                    if count > 0:
                        failed_checks.append((name, count))

                # Capture examples to help investigate mismatches.
                if any(
                    name == "Payment mismatches"
                    for name, _ in failed_checks
                ):
                    cur.execute("""
                        WITH items AS (
                            SELECT order_id,
                                   SUM(price + freight_value)
                                       AS item_total
                            FROM stg_order_items
                            GROUP BY order_id
                        ),
                        payments AS (
                            SELECT order_id,
                                   SUM(payment_value)
                                       AS payment_total
                            FROM stg_payments
                            GROUP BY order_id
                        )
                        SELECT
                            i.order_id,
                            ROUND(i.item_total::numeric, 2),
                            ROUND(p.payment_total::numeric, 2),
                            ROUND(
                                (i.item_total - p.payment_total)::numeric,
                                2
                            ) AS difference
                        FROM items i
                        JOIN payments p USING (order_id)
                        WHERE ABS(i.item_total - p.payment_total) > 0.01
                        ORDER BY ABS(
                            i.item_total - p.payment_total
                        ) DESC
                        LIMIT 10
                    """)

                    examples = cur.fetchall()
                    logger.warning(
                        "Sample payment mismatches "
                        "(order_id, item_total, payment_total, difference):"
                    )
                    for example in examples:
                        logger.warning("%s", example)

    except Exception:
        logger.exception("Could not complete data-quality checks")
        raise

    if failed_checks:
        details = "; ".join(
            f"{name}: {count}" for name, count in failed_checks
        )
        logger.error("DATA QUALITY ALARM: %s", details)
        raise RuntimeError(
            f"DATA QUALITY ALARM - Pipeline stopped: {details}"
        )

    logger.info("All data-quality checks passed.")


if __name__ == "__main__":
    main()
