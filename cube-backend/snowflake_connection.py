import snowflake.connector

conn = snowflake.connector.connect(
    user="LIKHITHA",
    password="Likhitha@25222",
    account="BNMASPU-JN64226",
    warehouse="COMPUTE_WH",
    database="CUBES_DB",
    schema="CUBES_SCHEMA"
)

print("Connected to Snowflake successfully")

