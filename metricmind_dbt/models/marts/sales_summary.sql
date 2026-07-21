{{ config(materialized='table') }}

select
    region,
    category,
    sum(sales) as total_sales,
    sum(profit) as total_profit,
    sum(quantity) as total_quantity,
    sum(shipping_cost) as total_shipping_cost,
    count(order_id) as total_orders
from {{ ref('stg_superstore') }}
group by
    region,
    category