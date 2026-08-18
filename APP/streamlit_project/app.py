import streamlit as st
import pandas as pd
import requests
import json

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="MetricMind Dashboard",
    page_icon="📊",
    layout="wide"
)
# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

st.title("📊 MetricMind")

st.subheader(
    "Retail Business Intelligence & Analytics Dashboard"
)

st.caption(
    "⚡ Analytics powered by Cube API & Snowflake"
)

st.success(
    "🟢 Live Dashboard"
)
# --------------------------------------------------
# CUSTOM DASHBOARD STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>

    /* Main page */
    .main {
        padding-top: 1rem;
    }

    /* KPI metric cards */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(128, 128, 128, 0.25);
    }

    /* KPI labels */
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
    }

    /* KPI values */
    div[data-testid="stMetricValue"] {
        font-size: 1.6rem;
        font-weight: 700;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.2);
    }

    /* Success / insight box */
    div[data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* Dataframe */
    div[data-testid="stDataFrame"] {
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)
# --------------------------------------------------
# CUBE API
# --------------------------------------------------

CUBE_API_URL = "http://localhost:4000/cubejs-api/v1/load"


def get_cube_data(query):
    try:
        response = requests.get(
            CUBE_API_URL,
            params={"query": json.dumps(query)},
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        if "data" in result:
            return pd.DataFrame(result["data"])

        st.error("Cube API returned no data.")
        return pd.DataFrame()

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to Cube API: {e}")
        return pd.DataFrame()

    except Exception as e:
        st.error(f"Something went wrong: {e}")
        return pd.DataFrame()

# --------------------------------------------------
# GET FILTER OPTIONS FROM CUBE
# --------------------------------------------------

filter_query = {
    "dimensions": [
        "monthly_dashboard_summary.category",
        "monthly_dashboard_summary.year"
    ]
}

filter_df = get_cube_data(filter_query)

if not filter_df.empty:

    category_column = "monthly_dashboard_summary.category"
    year_column = "monthly_dashboard_summary.year"

    categories = sorted(
        filter_df[category_column]
        .dropna()
        .unique()
        .tolist()
    )

    years = sorted(
        filter_df[year_column]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

else:
    categories = []
    years = []

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.markdown(
    """
    <div style="padding-bottom: 10px;">
        <h1 style="margin-bottom: 0;">🔍 MetricMind</h1>
        <p style="margin-top: 4px; opacity: 0.7;">
            Dashboard Filters
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.divider()

# Category filter
category_options = ["All"] + categories

category = st.sidebar.selectbox(
    "🛍️ Select Category",
    category_options
)

# Year filter
year_options = ["All"] + years

year = st.sidebar.selectbox(
    "📅 Select Year",
    year_options
)

st.sidebar.divider()

# Current selection
st.sidebar.markdown("### 📌 Current Selection")

selection_col1, selection_col2 = st.sidebar.columns(2)

with selection_col1:
    st.sidebar.caption("Category")
    st.sidebar.write(f"**{category}**")

with selection_col2:
    st.sidebar.caption("Year")
    st.sidebar.write(f"**{year}**")

st.sidebar.divider()

# Dashboard status
st.sidebar.markdown(
    """
    ### 🟢 Dashboard Status
    **Cube API:** Connected  
    **Data Source:** Snowflake
    """
)

# --------------------------------------------------
# CUBE QUERY
# --------------------------------------------------

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

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filters = []

if category != "All":
    filters.append({
        "member": "monthly_dashboard_summary.category",
        "operator": "equals",
        "values": [category]
    })

if year != "All":
    filters.append({
        "member": "monthly_dashboard_summary.year",
        "operator": "equals",
        "values": [year]
    })

if filters:
    query["filters"] = filters

# --------------------------------------------------
# GET DATA
# --------------------------------------------------

df = get_cube_data(query)

# --------------------------------------------------
# CHECK DATA
# --------------------------------------------------

if df.empty:
    st.warning("⚠️ No data available for the selected filters.")
    st.write("Cube returned:", df)
    st.stop()

# --------------------------------------------------
# CONVERT NUMERIC COLUMNS
# --------------------------------------------------

numeric_columns = [
    "monthly_dashboard_summary.total_sales",
    "monthly_dashboard_summary.total_revenue",
    "monthly_dashboard_summary.total_orders",
    "monthly_dashboard_summary.total_customers",
    "monthly_dashboard_summary.total_profit"
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        ).fillna(0)

# --------------------------------------------------
# MONTH SORTING
# --------------------------------------------------

month_order = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

month_column = "monthly_dashboard_summary.month_name"

if month_column in df.columns:

    df[month_column] = pd.Categorical(
        df[month_column],
        categories=month_order,
        ordered=True
    )

    df = df.sort_values(month_column)

# --------------------------------------------------
# FILTER SUMMARY
# --------------------------------------------------

st.caption(
    f"📌 Category: **{category}**  |  "
    f"Year: **{year}**"
)

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_sales = df[
    "monthly_dashboard_summary.total_sales"
].sum()

total_revenue = df[
    "monthly_dashboard_summary.total_revenue"
].sum()

total_orders = df[
    "monthly_dashboard_summary.total_orders"
].sum()

total_customers = df[
    "monthly_dashboard_summary.total_customers"
].sum()

total_profit = df[
    "monthly_dashboard_summary.total_profit"
].sum()

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

st.subheader("📌 Key Performance Indicators")

# Calculate profit margin
if total_sales > 0:
    profit_margin = (total_profit / total_sales) * 100
else:
    profit_margin = 0

# KPI row
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="💰 Total Sales",
        value=f"₹{total_sales:,.0f}"
    )

with col2:
    st.metric(
        label="💵 Revenue",
        value=f"₹{total_revenue:,.0f}"
    )

with col3:
    st.metric(
        label="📈 Total Profit",
        value=f"₹{total_profit:,.0f}"
    )

with col4:
    st.metric(
        label="📦 Total Orders",
        value=f"{total_orders:,.0f}"
    )

with col5:
    st.metric(
        label="👥 Customers",
        value=f"{total_customers:,.0f}"
    )

# Profit margin
st.caption(
    f"📊 Profit Margin: **{profit_margin:.2f}%**"
)

# --------------------------------------------------
# CHARTS
# --------------------------------------------------

st.subheader("📊 Sales & Revenue Analytics")

# --------------------------------------------------
# ROW 1 — SALES + CATEGORY
# --------------------------------------------------

chart_col1, chart_col2 = st.columns(2)

with chart_col1:

    st.markdown("### 📈 Monthly Sales")

    sales_chart = df[
        [
            month_column,
            "monthly_dashboard_summary.total_sales"
        ]
    ].copy()

    sales_chart = sales_chart.rename(
        columns={
            month_column: "Month",
            "monthly_dashboard_summary.total_sales": "Sales"
        }
    )

    sales_chart = sales_chart.set_index("Month")

    st.line_chart(sales_chart)


with chart_col2:

    st.markdown("### 🛍️ Category-wise Sales")

    category_sales = (
        df.groupby(
            "monthly_dashboard_summary.category",
            observed=True
        )["monthly_dashboard_summary.total_sales"]
        .sum()
        .reset_index()
    )

    category_sales = category_sales.rename(
        columns={
            "monthly_dashboard_summary.category": "Category",
            "monthly_dashboard_summary.total_sales": "Sales"
        }
    )

    if not category_sales.empty:
        st.bar_chart(
            category_sales.set_index("Category")
        )


# --------------------------------------------------
# ROW 2 — REVENUE + ORDERS
# --------------------------------------------------

chart_col3, chart_col4 = st.columns(2)

with chart_col3:

    st.markdown("### 💵 Revenue Trend")

    revenue_chart = df[
        [
            month_column,
            "monthly_dashboard_summary.total_revenue"
        ]
    ].copy()

    revenue_chart = revenue_chart.rename(
        columns={
            month_column: "Month",
            "monthly_dashboard_summary.total_revenue": "Revenue"
        }
    )

    revenue_chart = revenue_chart.set_index("Month")

    st.area_chart(revenue_chart)


with chart_col4:

    st.markdown("### 📦 Orders Trend")

    orders_chart = df[
        [
            month_column,
            "monthly_dashboard_summary.total_orders"
        ]
    ].copy()

    orders_chart = orders_chart.rename(
        columns={
            month_column: "Month",
            "monthly_dashboard_summary.total_orders": "Orders"
        }
    )

    orders_chart = orders_chart.set_index("Month")

    st.bar_chart(orders_chart)


# --------------------------------------------------
# ROW 3 — REVENUE VS PROFIT
# --------------------------------------------------

st.markdown("### 💰 Revenue vs Profit")

revenue_profit_chart = df[
    [
        month_column,
        "monthly_dashboard_summary.total_revenue",
        "monthly_dashboard_summary.total_profit"
    ]
].copy()

revenue_profit_chart = revenue_profit_chart.rename(
    columns={
        month_column: "Month",
        "monthly_dashboard_summary.total_revenue": "Revenue",
        "monthly_dashboard_summary.total_profit": "Profit"
    }
)

revenue_profit_chart = (
    revenue_profit_chart
    .groupby("Month", observed=True)[
        ["Revenue", "Profit"]
    ]
    .sum()
)

st.line_chart(revenue_profit_chart)
# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

st.subheader("🤖 MetricMind Business Insights")

# Top performing category
if not category_sales.empty:

    top_category = category_sales.loc[
        category_sales["Sales"].idxmax(),
        "Category"
    ]

    top_category_sales = category_sales.loc[
        category_sales["Sales"].idxmax(),
        "Sales"
    ]

else:
    top_category = "N/A"
    top_category_sales = 0

# Best sales month
monthly_sales = (
    df.groupby(
        month_column,
        observed=True
    )["monthly_dashboard_summary.total_sales"]
    .sum()
)

if not monthly_sales.empty:
    top_month = monthly_sales.idxmax()
    top_month_sales = monthly_sales.max()
else:
    top_month = "N/A"
    top_month_sales = 0
# --------------------------------------------------
# SALES PERFORMANCE SUMMARY
# --------------------------------------------------

st.subheader("📊 Sales Performance Summary")

# Highest and lowest sales month
if not monthly_sales.empty:

    highest_sales_month = monthly_sales.idxmax()
    highest_month_sales = monthly_sales.max()

    lowest_sales_month = monthly_sales.idxmin()
    lowest_month_sales = monthly_sales.min()

    average_monthly_sales = monthly_sales.mean()

else:

    highest_sales_month = "N/A"
    highest_month_sales = 0

    lowest_sales_month = "N/A"
    lowest_month_sales = 0

    average_monthly_sales = 0

summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)

with summary_col1:
    st.metric(
        "📈 Highest Sales Month",
        highest_sales_month
    )

with summary_col2:
    st.metric(
        "💰 Highest Monthly Sales",
        f"₹{highest_month_sales:,.0f}"
    )

with summary_col3:
    st.metric(
        "📉 Lowest Sales Month",
        lowest_sales_month
    )

with summary_col4:
    st.metric(
        "📊 Avg. Monthly Sales",
        f"₹{average_monthly_sales:,.0f}"
    )
# --------------------------------------------------
# SALES TREND
# --------------------------------------------------

st.markdown("### 📈 Sales Trend")

if len(monthly_sales) >= 2:

    sorted_sales = monthly_sales.sort_index()

    latest_month = sorted_sales.index[-1]
    previous_month = sorted_sales.index[-2]

    latest_sales = sorted_sales.iloc[-1]
    previous_sales = sorted_sales.iloc[-2]

    if previous_sales != 0:
        sales_change = (
            (latest_sales - previous_sales)
            / previous_sales
        ) * 100
    else:
        sales_change = 0

    trend_col1, trend_col2, trend_col3 = st.columns(3)

    with trend_col1:
        st.metric(
            "📅 Latest Month",
            latest_month
        )

    with trend_col2:
        st.metric(
            "💰 Latest Sales",
            f"₹{latest_sales:,.0f}"
        )

    with trend_col3:
        st.metric(
            "📊 Month-over-Month Change",
            f"{sales_change:+.2f}%"
        )

else:
    st.info(
        "Not enough monthly data available to calculate sales trend."
    )
# Average Order Value
if total_orders > 0:
    average_order_value = total_sales / total_orders
else:
    average_order_value = 0

# Display insights
insight_col1, insight_col2, insight_col3 = st.columns(3)

with insight_col1:
    st.info(
        f"""
        🏆 **Top Category**

        ### {top_category}

        Sales: **₹{top_category_sales:,.0f}**
        """
    )

with insight_col2:
    st.info(
        f"""
        📅 **Best Sales Month**

        ### {top_month}

        Sales: **₹{top_month_sales:,.0f}**
        """
    )

with insight_col3:
    st.info(
        f"""
        🛒 **Average Order Value**

        ### ₹{average_order_value:,.0f}

        Based on total sales and orders
        """
    )

st.success(
    f"""
    💰 **Total Sales:** ₹{total_sales:,.0f}  
    💵 **Total Revenue:** ₹{total_revenue:,.0f}  
    📈 **Total Profit:** ₹{total_profit:,.0f}  
    📊 **Profit Margin:** {profit_margin:.2f}%
    """
)
# --------------------------------------------------
# DOWNLOAD REPORT
# --------------------------------------------------

st.subheader("📥 Download Filtered Report")

csv = df.to_csv(index=False)

# Create a clean filename based on filters
category_name = str(category).replace(" ", "_")
year_name = str(year).replace(" ", "_")

report_filename = (
    f"MetricMind_{category_name}_{year_name}.csv"
)

st.download_button(
    label="⬇️ Download CSV Report",
    data=csv,
    file_name=report_filename,
    mime="text/csv"
)

st.caption(
    f"Report contains the data currently filtered by "
    f"Category: **{category}** and Year: **{year}**."
)
# --------------------------------------------------
# DATA TABLE
# --------------------------------------------------

st.subheader("📋 Cube Data")

st.dataframe(
    df,
    use_container_width=True
)