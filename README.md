# Olist E-commerce Weekly Business Review

## Project Overview

This project analyzes the Olist Brazilian E-commerce dataset to evaluate marketplace revenue, customer retention, delivery performance, and customer satisfaction.

The project implements an ELT pipeline using Python, PostgreSQL, and SQL. It loads raw CSV files, creates staging tables, builds an analysis-ready data mart, and performs data quality checks.

## Technologies Used

- Python
- PostgreSQL
- SQL
- Pandas
- SQLAlchemy
- Psycopg
- Matplotlib

## Project Structure

```text
olist-weekly-business-review/
├── data/
│   └── raw/
├── logs/
├── reports/
│   ├── charts/
│   ├── quality_check_report.md
│   └── vp_memo.md
├── sql/
│   ├── create_staging.sql
│   ├── create_mart.sql
│   ├── quality_checks.sql
│   ├── q1_revenue_growth.sql
│   ├── q2_top_categories.sql
│   ├── q3_rolling_orders.sql
│   ├── q4_repeat_purchase.sql
│   └── q5_delivery_delay.sql
├── src/
│   ├── pipeline.py
│   ├── load_raw.py
│   ├── quality_checks.py
│   ├── part_d_metrics.py
│   └── part_d_charts.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. Install Python and PostgreSQL.
2. Create a PostgreSQL database named `olist_dw`.
3. Open a terminal in the project folder.
4. Install the required packages:

```bash
pip install -r requirements.txt
```

5. Set the `OLIST_DB_PASSWORD` environment variable to your PostgreSQL password.

For Windows Command Prompt, use:

```cmd
set OLIST_DB_PASSWORD=your_postgres_password
```

Replace `your_postgres_password` with your actual password. Do not commit your password to GitHub.

## Run the Pipeline

From the project root, run:

```bash
python src/pipeline.py
```

The pipeline loads raw data, builds staging tables and the data mart, and executes quality checks. The pipeline stops when a quality check fails.

## SQL Analysis

Five SQL queries are included:

1. Monthly revenue and month-over-month growth.
2. Top three product categories by customer state.
3. Seven-day rolling average of daily orders.
4. Repeat-purchase rate using unique customer IDs.
5. Delivery delay and review-score analysis.

## Reports and Visualizations

The `reports/` directory contains the data quality report, VP memo, metric outputs, and charts for revenue, repeat purchases, delivery delays, and delivery timeliness.

## Data Quality

Five data quality checks validate order IDs, duplicate records, delivery dates, payment reconciliation, and customer references.

The current analysis identified 303 payment mismatches. These discrepancies are documented for investigation and should not be treated as confirmed errors without further validation.

## Business Objective

The objective is to identify trends in marketplace performance and recommend improvements in revenue growth, customer retention, delivery reliability, and customer satisfaction.