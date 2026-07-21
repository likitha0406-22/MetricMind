{{ config(materialized='view') }}

select
    "Order ID" as order_id,
    "Customer ID" as customer_id,
    "Customer Name" as customer_name,
    "Segment" as segment,
    "City" as city,
    "State" as state,
    "Country" as country,
    "Region" as region,
    "Product ID" as product_id,
    "Product Name" as product_name,
    "Category" as category,
    "Sub Category" as sub_category,
    "Quantity" as quantity,
    "Sales" as sales,
    "Discount" as discount,
    "Profit" as profit,
    "Market" as market,
    "Order Date" as order_date,
    "Year" as year,
    "Order Priority" as order_priority,
    "Ship Date" as ship_date,
    "Ship Mode" as ship_mode,
    "Shipping Cost" as shipping_cost
from {{ source('retail', 'SUPERSTORE_CLEANED') }}