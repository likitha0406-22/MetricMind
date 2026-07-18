/* Superstore Snowflake Data Preparation and Analysis */

USE DATABASE METRICMIND_DB;
USE SCHEMA METRICMIND_DB.RETAIL;

/* Create Raw Superstore Table */

CREATE TABLE IF NOT EXISTS METRICMIND_DB.RETAIL.SUPERSTORE (
    "Order ID" VARCHAR,
    "Customer Name" VARCHAR,
    "Customer ID" VARCHAR,
    "Segment" VARCHAR,
    "City" VARCHAR,
    "State" VARCHAR,
    "Country" VARCHAR,
    "Region" VARCHAR,
    "Product ID" VARCHAR,
    "Product Name" VARCHAR,
    "Category" VARCHAR,
    "Sub Category" VARCHAR,
    "Quantity" VARCHAR,
    "Sales" VARCHAR,
    "Discount" VARCHAR,
    "Profit" VARCHAR,
    "Market" VARCHAR,
    "Order Date" VARCHAR,
    "Year" VARCHAR,
    "Order Priority" VARCHAR,
    "Ship Date" VARCHAR,
    "Ship Mode" VARCHAR,
    "Shipping Cost" VARCHAR
);

/* Create Cleaned Superstore Table */

CREATE OR REPLACE TABLE METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED AS
SELECT
    "Order ID",
    "Customer Name",
    "Customer ID",
    "Segment",
    "City",
    "State",
    "Country",
    "Region",
    "Product ID",
    "Product Name",
    "Category",
    "Sub Category",

    TRY_TO_NUMBER("Quantity") AS "Quantity",

    TRY_TO_DECIMAL(
        REPLACE(REPLACE("Sales", '₹', ''), ',', ''),
        18, 2
    ) AS "Sales",

    TRY_TO_DECIMAL(
        REPLACE("Discount", '%', ''),
        5, 2
    ) / 100 AS "Discount",

    TRY_TO_DECIMAL(
        REPLACE(REPLACE("Profit", '₹', ''), ',', ''),
        18, 2
    ) AS "Profit",

    "Market",

    TRY_TO_DATE(
        "Order Date",
        'DD/MM/YY'
    ) AS "Order Date",

    TRY_TO_NUMBER("Year") AS "Year",

    "Order Priority",

    TRY_TO_DATE(
        "Ship Date",
        'DD/MM/YY'
    ) AS "Ship Date",

    "Ship Mode",

    TRY_TO_DECIMAL(
        REPLACE(REPLACE("Shipping Cost", '₹', ''), ',', ''),
        18, 2
    ) AS "Shipping Cost"

FROM METRICMIND_DB.RETAIL.SUPERSTORE;

/* Raw vs Cleaned Row Count Validation */

SELECT
    (SELECT COUNT(*)
     FROM METRICMIND_DB.RETAIL.SUPERSTORE) AS raw_rows,

    (SELECT COUNT(*)
     FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED) AS cleaned_rows;

/* Null Validation After Datatype Conversion */

SELECT
    COUNT_IF("Order Date" IS NULL) AS order_date_nulls,
    COUNT_IF("Ship Date" IS NULL) AS ship_date_nulls,
    COUNT_IF("Quantity" IS NULL) AS quantity_nulls,
    COUNT_IF("Sales" IS NULL) AS sales_nulls,
    COUNT_IF("Discount" IS NULL) AS discount_nulls,
    COUNT_IF("Profit" IS NULL) AS profit_nulls,
    COUNT_IF("Shipping Cost" IS NULL) AS shipping_cost_nulls
FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED;

/* Dataset Overview */

SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT "Order ID") AS total_orders,
    COUNT(DISTINCT "Customer ID") AS total_customers,
    COUNT(DISTINCT "Product ID") AS total_products,
    MIN("Order Date") AS first_order_date,
    MAX("Order Date") AS last_order_date
FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED;

/* Core Business KPIs */

SELECT
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,
    SUM("Quantity") AS total_quantity,
    ROUND(AVG("Sales"), 2) AS avg_sales_per_line,
    ROUND(AVG("Profit"), 2) AS avg_profit_per_line,

    ROUND(
        SUM("Profit") /
        NULLIF(SUM("Sales"), 0) * 100,
        2
    ) AS profit_margin_percentage

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED;

/* Yearly Performance */

SELECT
    "Year",
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,
    SUM("Quantity") AS total_quantity,

    ROUND(
        SUM("Profit") /
        NULLIF(SUM("Sales"), 0) * 100,
        2
    ) AS profit_margin_percentage

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
GROUP BY "Year"
ORDER BY "Year";

/* Category Performance */

SELECT
    "Category",
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,
    SUM("Quantity") AS total_quantity,

    ROUND(
        SUM("Profit") /
        NULLIF(SUM("Sales"), 0) * 100,
        2
    ) AS profit_margin_percentage

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
GROUP BY "Category"
ORDER BY total_sales DESC;

/* Overall Sub-Category Performance */

SELECT
    "Sub Category",
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,

    ROUND(
        SUM("Profit") /
        NULLIF(SUM("Sales"), 0) * 100,
        2
    ) AS profit_margin_percentage

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
GROUP BY "Sub Category"
ORDER BY total_profit DESC;

/* Furniture Sub-Category Analysis */

SELECT
    "Sub Category",
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,

    ROUND(
        SUM("Profit") /
        NULLIF(SUM("Sales"), 0) * 100,
        2
    ) AS profit_margin_percentage

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
WHERE "Category" = 'Furniture'
GROUP BY "Sub Category"
ORDER BY total_profit ASC;

/* Tables Discount Impact Analysis */

SELECT
    "Discount",
    COUNT(*) AS transactions,
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,

    ROUND(
        SUM("Profit") /
        NULLIF(SUM("Sales"), 0) * 100,
        2
    ) AS profit_margin_percentage

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
WHERE "Sub Category" = 'Tables'
GROUP BY "Discount"
ORDER BY "Discount";

/* Tables Regional Analysis */

SELECT
    "Region",
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,
    ROUND(AVG("Discount") * 100, 2) AS avg_discount_pct,

    ROUND(
        SUM("Profit") /
        NULLIF(SUM("Sales"), 0) * 100,
        2
    ) AS profit_margin_pct

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
WHERE "Sub Category" = 'Tables'
GROUP BY "Region"
ORDER BY total_profit ASC;

/* Overall Regional Performance */

SELECT
    "Region",
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,

    ROUND(
        SUM("Profit") /
        NULLIF(SUM("Sales"), 0) * 100,
        2
    ) AS profit_margin_pct

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
GROUP BY "Region"
ORDER BY total_sales DESC;

/* Customer Segment Performance */

SELECT
    "Segment",
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,
    COUNT(DISTINCT "Order ID") AS total_orders,

    ROUND(
        SUM("Profit") /
        NULLIF(SUM("Sales"), 0) * 100,
        2
    ) AS profit_margin_pct

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
GROUP BY "Segment"
ORDER BY total_sales DESC;

/* Top 10 Profitable Products */

SELECT
    "Product Name",
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
GROUP BY "Product Name"
ORDER BY total_profit DESC NULLS LAST
LIMIT 10;

/* Top 10 Loss-Making Products */

SELECT
    "Product Name",
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
GROUP BY "Product Name"
ORDER BY total_profit ASC NULLS LAST
LIMIT 10;

/* Overall Discount Impact */

SELECT
    "Discount",
    COUNT(*) AS total_rows,
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,

    ROUND(
        SUM("Profit") /
        NULLIF(SUM("Sales"), 0) * 100,
        2
    ) AS profit_margin_pct

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
GROUP BY "Discount"
ORDER BY "Discount";

/* Shipping Mode Analysis */

SELECT
    "Ship Mode",
    COUNT(DISTINCT "Order ID") AS total_orders,
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,
    ROUND(AVG("Shipping Cost"), 2) AS avg_shipping_cost,

    ROUND(
        SUM("Profit") /
        NULLIF(SUM("Sales"), 0) * 100,
        2
    ) AS profit_margin_pct

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
GROUP BY "Ship Mode"
ORDER BY total_sales DESC;

/* Monthly and Seasonal Performance */

SELECT
    MONTH("Order Date") AS month_number,
    MONTHNAME("Order Date") AS month_name,
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,
    COUNT(DISTINCT "Order ID") AS total_orders

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED

GROUP BY
    MONTH("Order Date"),
    MONTHNAME("Order Date")

ORDER BY month_number;

/* Top 10 Customers by Sales */

SELECT
    "Customer Name",
    ROUND(SUM("Sales"), 2) AS total_sales,
    ROUND(SUM("Profit"), 2) AS total_profit,
    COUNT(DISTINCT "Order ID") AS total_orders

FROM METRICMIND_DB.RETAIL.SUPERSTORE_CLEANED
GROUP BY "Customer Name"
ORDER BY total_sales DESC
LIMIT 10;