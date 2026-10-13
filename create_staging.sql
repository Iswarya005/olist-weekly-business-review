
-- Create cleaned staging tables from the raw tables.
-- Original raw tables remain unchanged.

DROP TABLE IF EXISTS stg_orders CASCADE;
CREATE TABLE stg_orders AS
SELECT
    order_id,
    customer_id,
    order_status,
    NULLIF(order_purchase_timestamp::text, '')::timestamp
        AS order_purchase_timestamp,
    NULLIF(order_approved_at::text, '')::timestamp
        AS order_approved_at,
    NULLIF(order_delivered_carrier_date::text, '')::timestamp
        AS order_delivered_carrier_date,
    NULLIF(order_delivered_customer_date::text, '')::timestamp
        AS order_delivered_customer_date,
    NULLIF(order_estimated_delivery_date::text, '')::timestamp
        AS order_estimated_delivery_date
FROM raw_orders;

DROP TABLE IF EXISTS stg_customers CASCADE;
CREATE TABLE stg_customers AS
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    UPPER(TRIM(customer_city)) AS customer_city,
    UPPER(TRIM(customer_state)) AS customer_state
FROM raw_customers;

DROP TABLE IF EXISTS stg_order_items CASCADE;
CREATE TABLE stg_order_items AS
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date::timestamp AS shipping_limit_date,
    price::numeric AS price,
    freight_value::numeric AS freight_value
FROM raw_order_items;

DROP TABLE IF EXISTS stg_payments CASCADE;
CREATE TABLE stg_payments AS
SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value::numeric AS payment_value
FROM raw_payments;

DROP TABLE IF EXISTS stg_reviews CASCADE;
CREATE TABLE stg_reviews AS
SELECT
    review_id,
    order_id,
    review_score::integer AS review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date::timestamp AS review_creation_date,
    review_answer_timestamp::timestamp AS review_answer_timestamp
FROM raw_reviews;

DROP TABLE IF EXISTS stg_products CASCADE;
CREATE TABLE stg_products AS
SELECT
    product_id,
    product_category_name,
    product_name_lenght,
    product_description_lenght,
    product_photos_qty,
    product_weight_g,
    product_length_cm,
    product_height_cm,
    product_width_cm
FROM raw_products;

DROP TABLE IF EXISTS stg_sellers CASCADE;
CREATE TABLE stg_sellers AS
SELECT
    seller_id,
    seller_zip_code_prefix,
    UPPER(TRIM(seller_city)) AS seller_city,
    UPPER(TRIM(seller_state)) AS seller_state
FROM raw_sellers;

DROP TABLE IF EXISTS stg_category_translation CASCADE;
CREATE TABLE stg_category_translation AS
SELECT
    product_category_name,
    product_category_name_english
FROM raw_category_translation;

-- Geolocation contains repeated postal-code prefixes.
-- Keep the raw data intact for now.
DROP TABLE IF EXISTS stg_geolocation CASCADE;
CREATE TABLE stg_geolocation AS
SELECT
    geolocation_zip_code_prefix,
    geolocation_lat,
    geolocation_lng,
    UPPER(TRIM(geolocation_city)) AS geolocation_city,
    UPPER(TRIM(geolocation_state)) AS geolocation_state
FROM raw_geolocation;

-- Basic indexes for common joins
CREATE INDEX idx_stg_orders_order_id
    ON stg_orders(order_id);
CREATE INDEX idx_stg_customers_customer_id
    ON stg_customers(customer_id);
CREATE INDEX idx_stg_items_order_id
    ON stg_order_items(order_id);
CREATE INDEX idx_stg_payments_order_id
    ON stg_payments(order_id);
CREATE INDEX idx_stg_reviews_order_id
    ON stg_reviews(order_id);
