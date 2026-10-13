
import logging
import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
from sqlalchemy import create_engine, text

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"

DB_USER = "postgres"
DB_PASSWORD = os.environ.get("OLIST_DB_PASSWORD", "")
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "olist_dw"

if not DB_PASSWORD:
    raise RuntimeError(
        "OLIST_DB_PASSWORD is not set in the terminal."
    )

DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:"
    f"{quote_plus(DB_PASSWORD)}@{DB_HOST}:"
    f"{DB_PORT}/{DB_NAME}"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)

FILES = {
    "olist_orders_dataset.csv": (
        "raw_orders",
        ["order_id", "customer_id", "order_status",
         "order_purchase_timestamp"]
    ),
    "olist_order_items_dataset.csv": (
        "raw_order_items",
        ["order_id", "order_item_id", "product_id",
         "seller_id", "price", "freight_value"]
    ),
    "olist_order_payments_dataset.csv": (
        "raw_payments",
        ["order_id", "payment_value", "payment_type"]
    ),
    "olist_order_reviews_dataset.csv": (
        "raw_reviews",
        ["review_id", "order_id", "review_score"]
    ),
    "olist_customers_dataset.csv": (
        "raw_customers",
        ["customer_id", "customer_unique_id", "customer_state"]
    ),
    "olist_sellers_dataset.csv": (
        "raw_sellers",
        ["seller_id", "seller_state"]
    ),
    "olist_products_dataset.csv": (
        "raw_products",
        ["product_id", "product_category_name"]
    ),
    "olist_geolocation_dataset.csv": (
        "raw_geolocation",
        ["geolocation_zip_code_prefix", "geolocation_lat",
         "geolocation_lng"]
    ),
    "product_category_name_translation.csv": (
        "raw_category_translation",
        ["product_category_name",
         "product_category_name_english"]
    ),
}


def main():
    logging.info("Starting raw CSV ingestion")

    # Validate all files and columns before loading any table.
    for filename, (table_name, required_columns) in FILES.items():
        filepath = DATA_DIR / filename

        if not filepath.is_file():
            raise FileNotFoundError(
                f"Required CSV file not found: {filepath}"
            )

        columns = pd.read_csv(filepath, nrows=0).columns.tolist()
        missing = sorted(set(required_columns) - set(columns))

        if missing:
            raise ValueError(
                f"{filename} is missing required columns: {missing}"
            )

    engine = create_engine(DATABASE_URL)

    try:
        for filename, (table_name, required_columns) in FILES.items():
            filepath = DATA_DIR / filename
            logging.info("Loading %s into %s", filename, table_name)

            df = pd.read_csv(filepath)

            with engine.begin() as connection:
                df.to_sql(
                    table_name,
                    con=connection,
                    if_exists="replace",
                    index=False,
                    chunksize=5000
                )

                count = connection.execute(
                    text(f'SELECT COUNT(*) FROM "{table_name}"')
                ).scalar_one()

            logging.info(
                "Loaded %s rows into %s", count, table_name
            )

        logging.info("All raw CSV files loaded successfully")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()

