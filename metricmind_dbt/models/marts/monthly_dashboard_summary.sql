{{ config(materialized='table') }}

SELECT
    YEAR(order_date) AS year,
    MONTH(order_date) AS month_number,
    MONTHNAME(order_date) AS month_name,
    category,
    SUM(sales) AS total_sales,
    SUM(sales) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_customers,
    SUM(profit) AS total_profit,
    SUM(shipping_cost) AS total_shipping_cost
FROM {{ ref('stg_superstore') }}
GROUP BY
    YEAR(order_date),
    MONTH(order_date),
    MONTHNAME(order_date),
    category
ORDER BY
    year,
    month_number
