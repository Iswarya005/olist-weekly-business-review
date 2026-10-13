
import logging
import os
from pathlib import Path

import psycopg
from load_raw import main as load_raw
from quality_checks import main as run_quality_checks

PROJECT_DIR = Path(__file__).resolve().parent.parent
SQL_DIR = PROJECT_DIR / "sql"
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
            LOG_DIR / "pipeline.log",
            encoding="utf-8",
        ),
    ],
    force=True,
)

logger = logging.getLogger(__name__)


def run_sql_file(conn, filename):
    sql_path = SQL_DIR / filename

    if not sql_path.is_file():
        raise FileNotFoundError(
            f"Required SQL file not found: {sql_path}"
        )

    sql = sql_path.read_text(encoding="utf-8")

    if not sql.strip():
        raise ValueError(
            f"Required SQL file is empty: {sql_path}"
        )

    logger.info("Running %s", filename)
    conn.execute(sql)
    logger.info("Completed %s", filename)


def main():
    if not DB_CONFIG["password"]:
        raise RuntimeError(
            "OLIST_DB_PASSWORD is not set in the terminal."
        )

    logger.info("Starting Olist ELT pipeline")

    try:
        # Stage 1: Load and validate raw CSV files.
        logger.info("Stage 1: Loading raw CSV files")
        load_raw()
        logger.info("Raw CSV loading completed")

        # Stage 2: Build staging tables and the mart.
        logger.info("Stage 2: Building staging tables and mart")

        with psycopg.connect(**DB_CONFIG) as conn:
            run_sql_file(conn, "create_staging.sql")
            run_sql_file(conn, "create_mart.sql")

            with conn.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) FROM mart_order_summary"
                )
                mart_rows = cur.fetchone()[0]

            if mart_rows == 0:
                raise RuntimeError(
                    "mart_order_summary contains zero rows"
                )

            logger.info(
                "mart_order_summary row count: %s",
                mart_rows,
            )

        # Stage 3: Run all data quality checks.
        # Any failing check raises an error and stops the pipeline.
        logger.info("Stage 3: Running data quality checks")
        run_quality_checks()
        logger.info("All data quality checks passed")

        logger.info("ELT pipeline completed successfully")

    except Exception:
        logger.exception("ELT PIPELINE FAILED")
        raise


if __name__ == "__main__":
    main()

