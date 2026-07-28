import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(
    page_title="MetricMind Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 MetricMind Analytics Dashboard")
st.markdown("Live data from Cube API")


CUBE_API_URL = "http://localhost:4000/cubejs-api/v1/load"


def get_cube_data(query):
    response = requests.get(
        CUBE_API_URL,
        params={"query": json.dumps(query)}
    )

    result = response.json()

    if "data" in result:
        return pd.DataFrame(result["data"])
    else:
        return pd.DataFrame()


# Sidebar

st.sidebar.title("🔍 Filters")

category = st.sidebar.selectbox(
    "Select Category",
    ["All", "Electronics", "Clothing", "Food"]
)
year = st.sidebar.selectbox(
    "Select Year",
    ["All", 2023, 2024, 2025]
)


# Cube Query

query = {
    "measures": [
        "monthly_dashboard_summary.total_sales",
        "monthly_dashboard_summary.total_revenue",
        "monthly_dashboard_summary.total_orders",
        "monthly_dashboard_summary.total_customers",
        "monthly_dashboard_summary.total_profit"
    ],
   "dimensions": [
    "monthly_dashboard_summary.month_name",
    "monthly_dashboard_summary.category",
    "monthly_dashboard_summary.year"
]
    
}


if category != "All":
    if year != "All":
     query["filters"] = query.get("filters", []) + [
        {
            "member": "monthly_dashboard_summary.year",
            "operator": "equals",
            "values": [str(year)]
        }
    ]
    query["filters"] = [
        {
            "member": "monthly_dashboard_summary.category",
            "operator": "equals",
            "values": [category]
        }
    ]
df = get_cube_data(query)
month_order = [
    "Jan","Feb","Mar","Apr",
    "May","Jun","Jul","Aug",
    "Sep","Oct","Nov","Dec"
]

df["monthly_dashboard_summary.month_name"] = pd.Categorical(
    df["monthly_dashboard_summary.month_name"],
    categories=month_order,
    ordered=True
)

df = df.sort_values(
    "monthly_dashboard_summary.month_name"
)

df["monthly_dashboard_summary.month_name"] = pd.Categorical(
    df["monthly_dashboard_summary.month_name"],
    categories=month_order,
    ordered=True
)

df = df.sort_values(
    "monthly_dashboard_summary.month_name"
)
# Convert Cube values from string to numbers
numeric_columns = [
    "monthly_dashboard_summary.total_sales",
    "monthly_dashboard_summary.total_revenue",
    "monthly_dashboard_summary.total_orders",
    "monthly_dashboard_summary.total_customers",
    "monthly_dashboard_summary.total_profit"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col])
st.write(df)

# KPI Cards

st.subheader("📌 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "💰 Total Sales",
        f"₹{df['monthly_dashboard_summary.total_sales'].sum():,.0f}"
    )

with col2:
    st.metric(
        "💵 Revenue",
        f"₹{df['monthly_dashboard_summary.total_revenue'].sum():,.0f}"
    )


with col3:
    st.metric(
        "📦 Orders",
        f"{df['monthly_dashboard_summary.total_orders'].sum():,.0f}"
    )


with col4:
    st.metric(
        "👥 Customers",
        f"{df['monthly_dashboard_summary.total_customers'].sum():,.0f}"
    )


# Sales Chart

st.subheader("📈 Monthly Sales")

sales_chart = df[
    [
        "monthly_dashboard_summary.month_name",
        "monthly_dashboard_summary.total_sales"
    ]
]

sales_chart = sales_chart.rename(
    columns={
        "monthly_dashboard_summary.month_name": "Month",
        "monthly_dashboard_summary.total_sales": "Sales"
    }
)

sales_chart = sales_chart.set_index("Month")

st.line_chart(sales_chart)
st.subheader("🛍️ Category-wise Sales")

category_sales = (
    df.groupby("monthly_dashboard_summary.category")
    ["monthly_dashboard_summary.total_sales"]
    .sum()
)

category_sales = category_sales.reset_index()

category_sales = category_sales.rename(
    columns={
        "monthly_dashboard_summary.category": "Category",
        "monthly_dashboard_summary.total_sales": "Sales"
    }
)

st.bar_chart(
    category_sales.set_index("Category")
)
# Revenue Chart

st.subheader("💵 Revenue Trend")

revenue_chart = df[
    [
        "monthly_dashboard_summary.month_name",
        "monthly_dashboard_summary.total_revenue"
    ]
]

revenue_chart = revenue_chart.rename(
    columns={
        "monthly_dashboard_summary.month_name": "Month",
        "monthly_dashboard_summary.total_revenue": "Revenue"
    }
)

revenue_chart = revenue_chart.set_index("Month")

st.area_chart(revenue_chart)
st.subheader("🤖 MetricMind Insights")

total_sales = df["monthly_dashboard_summary.total_sales"].sum()
total_profit = df["monthly_dashboard_summary.total_profit"].sum()

if total_sales > 0:
    profit_margin = (total_profit / total_sales) * 100

    st.info(
        f"""
        📊 Business Insight:

        • Total Sales: ₹{total_sales:,.0f}

        • Total Profit: ₹{total_profit:,.0f}

        • Profit Margin: {profit_margin:.2f}%

        """
    )
# Orders Chart

st.subheader("📦 Orders Trend")

orders_chart = df[
    [
        "monthly_dashboard_summary.month_name",
        "monthly_dashboard_summary.total_orders"
    ]
]

orders_chart = orders_chart.rename(
    columns={
        "monthly_dashboard_summary.month_name": "Month",
        "monthly_dashboard_summary.total_orders": "Orders"
    }
)

orders_chart = orders_chart.set_index("Month")

st.bar_chart(orders_chart)



# Profit Chart

st.subheader("📈 Profit Analysis")

profit_chart = df[
    [
        "monthly_dashboard_summary.month_name",
        "monthly_dashboard_summary.total_profit"
    ]
]

profit_chart = profit_chart.rename(
    columns={
        "monthly_dashboard_summary.month_name": "Month",
        "monthly_dashboard_summary.total_profit": "Profit"
    }
)

profit_chart = profit_chart.set_index("Month")

st.line_chart(profit_chart)
st.line_chart(profit_chart)


# AI Business Insights
st.subheader("🤖 AI Business Insights")

top_category = (
    df.groupby("monthly_dashboard_summary.category")
    ["monthly_dashboard_summary.total_sales"]
    .sum()
    .idxmax()
)

top_month = (
    df.groupby("monthly_dashboard_summary.month_name")
    ["monthly_dashboard_summary.total_sales"]
    .sum()
    .idxmax()
)

total_sales = df["monthly_dashboard_summary.total_sales"].sum()
total_profit = df["monthly_dashboard_summary.total_profit"].sum()

profit_margin = (total_profit / total_sales) * 100


st.success(
    f"""
    🏆 Top Category: {top_category}

    📅 Best Sales Month: {top_month}

    💰 Total Sales: ₹{total_sales:,.0f}

    📈 Profit Margin: {profit_margin:.2f}%

    """
)
# Download Report

st.subheader("📥 Download Report")

csv = df.to_csv(index=False)

st.download_button(
    label="Download CSV Report",
    data=csv,
    file_name="MetricMind_Report.csv",
    mime="text/csv"
)
# Data Table

st.subheader("📋 Cube Data")

st.dataframe(
    df,
    use_container_width=True
)