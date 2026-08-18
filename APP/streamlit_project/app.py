import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="MetricMind Dashboard", page_icon="📊", layout="wide")

st.title("📊 MetricMind")
st.subheader("Retail Business Intelligence & Analytics Dashboard")
st.caption("⚡ Analytics powered by Cube API & Snowflake")
st.success("🟢 Live Dashboard")

st.markdown("""
<style>
.main {padding-top:1rem;}
div[data-testid="stMetric"] {background-color:rgba(255,255,255,.05);padding:18px;border-radius:12px;border:1px solid rgba(128,128,128,.25);}
div[data-testid="stMetricValue"] {font-size:1.6rem;font-weight:700;}
section[data-testid="stSidebar"] {border-right:1px solid rgba(128,128,128,.2);}
</style>
""", unsafe_allow_html=True)

CUBE_API_URL = "http://localhost:4000/cubejs-api/v1/load"
CUBE = "monthly_dashboard_summary"

CATEGORY=f"{CUBE}.category"
MONTH_NAME=f"{CUBE}.month_name"
MONTH_NUMBER=f"{CUBE}.month_number"
YEAR=f"{CUBE}.year"
SALES=f"{CUBE}.total_sales"
REVENUE=f"{CUBE}.total_revenue"
ORDERS=f"{CUBE}.total_orders"
CUSTOMERS=f"{CUBE}.total_customers"
PROFIT=f"{CUBE}.total_profit"

def cube(query):
    try:
        r=requests.get(CUBE_API_URL,params={"query":json.dumps(query)},timeout=30)
        r.raise_for_status()
        result=r.json()
        return pd.DataFrame(result.get("data",[]))
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to Cube. Make sure Docker Cube is running on port 4000.")
        return pd.DataFrame()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Cube API error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return pd.DataFrame()

# Filter options
options_df=cube({"dimensions":[CATEGORY,YEAR]})

if not options_df.empty:
    categories=sorted(options_df[CATEGORY].dropna().astype(str).unique().tolist())
    years=sorted(options_df[YEAR].dropna().astype(str).unique().tolist())
else:
    categories,years=[],[]

st.sidebar.markdown("## 🔍 MetricMind")
st.sidebar.caption("Dashboard Filters")
st.sidebar.divider()

category=st.sidebar.selectbox("🛍️ Select Category",["All"]+categories)
year=st.sidebar.selectbox("📅 Select Year",["All"]+years)

st.sidebar.divider()
st.sidebar.markdown("### 📌 Current Selection")
st.sidebar.write(f"**Category:** {category}")
st.sidebar.write(f"**Year:** {year}")
st.sidebar.divider()
st.sidebar.markdown("### 🟢 Dashboard Status")
st.sidebar.write("**Cube API:** Connected")
st.sidebar.write("**Data Source:** Snowflake")

filters=[]
if category!="All":
    filters.append({"member":CATEGORY,"operator":"equals","values":[category]})
if year!="All":
    filters.append({"member":YEAR,"operator":"equals","values":[year]})

def with_filters(q):
    if filters:
        q["filters"]=filters
    return q

# IMPORTANT: KPI query has NO dimensions.
# This prevents monthly/category rows from being summed twice.
kpi=cube(with_filters({
    "measures":[SALES,REVENUE,ORDERS,CUSTOMERS,PROFIT]
}))

if kpi.empty:
    st.warning("⚠️ No KPI data available for the selected filters.")
    st.stop()

def value(col):
    if col not in kpi.columns:
        return 0
    return float(pd.to_numeric(kpi[col],errors="coerce").fillna(0).iloc[0])

total_sales=value(SALES)
total_revenue=value(REVENUE)
total_orders=value(ORDERS)
total_customers=value(CUSTOMERS)
total_profit=value(PROFIT)
profit_margin=(total_profit/total_sales*100) if total_sales else 0

# Monthly query
monthly=cube(with_filters({
    "measures":[SALES,REVENUE,ORDERS,PROFIT],
    "dimensions":[MONTH_NAME,MONTH_NUMBER]
}))

if monthly.empty:
    st.warning("⚠️ No monthly data available.")
    st.stop()

for col in [SALES,REVENUE,ORDERS,PROFIT]:
    if col in monthly.columns:
        monthly[col]=pd.to_numeric(monthly[col],errors="coerce").fillna(0)

monthly[MONTH_NUMBER]=pd.to_numeric(monthly[MONTH_NUMBER],errors="coerce")
monthly=monthly.sort_values(MONTH_NUMBER)

# Category query
cat=cube(with_filters({
    "measures":[SALES],
    "dimensions":[CATEGORY]
}))

if not cat.empty:
    cat[SALES]=pd.to_numeric(cat[SALES],errors="coerce").fillna(0)

st.caption(f"📌 Category: **{category}** | Year: **{year}**")

# KPIs
st.subheader("📌 Key Performance Indicators")
c1,c2,c3,c4,c5=st.columns(5)
c1.metric("💰 Total Sales",f"₹{total_sales:,.0f}")
c2.metric("💵 Revenue",f"₹{total_revenue:,.0f}")
c3.metric("📈 Total Profit",f"₹{total_profit:,.0f}")
c4.metric("📦 Total Orders",f"{total_orders:,.0f}")
c5.metric("👥 Customers",f"{total_customers:,.0f}")
st.caption(f"📊 Profit Margin: **{profit_margin:.2f}%**")

st.subheader("📊 Sales & Revenue Analytics")

# Monthly Sales
a,b=st.columns(2)
with a:
    st.markdown("### 📈 Monthly Sales")
    x=monthly[[MONTH_NAME,SALES]].rename(columns={MONTH_NAME:"Month",SALES:"Sales"}).set_index("Month")
    st.line_chart(x)

# Category Sales
with b:
    st.markdown("### 🛍️ Category-wise Sales")
    if not cat.empty:
        x=cat[[CATEGORY,SALES]].rename(columns={CATEGORY:"Category",SALES:"Sales"})
        x=x.groupby("Category")["Sales"].sum()
        st.bar_chart(x)
    else:
        st.info("No category data available.")

# Revenue + Orders
a,b=st.columns(2)
with a:
    st.markdown("### 💵 Revenue Trend")
    x=monthly[[MONTH_NAME,REVENUE]].rename(columns={MONTH_NAME:"Month",REVENUE:"Revenue"}).set_index("Month")
    st.area_chart(x)

with b:
    st.markdown("### 📦 Orders Trend")
    x=monthly[[MONTH_NAME,ORDERS]].rename(columns={MONTH_NAME:"Month",ORDERS:"Orders"}).set_index("Month")
    st.bar_chart(x)

# Revenue vs Profit
st.markdown("### 💰 Revenue vs Profit")
x=monthly[[MONTH_NAME,REVENUE,PROFIT]].rename(
    columns={MONTH_NAME:"Month",REVENUE:"Revenue",PROFIT:"Profit"}
).set_index("Month")
st.line_chart(x)

# Sales summary
st.subheader("📊 Sales Performance Summary")
month_order=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

trend=monthly.copy()
trend[MONTH_NAME]=pd.Categorical(trend[MONTH_NAME],categories=month_order,ordered=True)
trend=trend.sort_values(MONTH_NAME)

monthly_sales=trend.groupby(MONTH_NAME,observed=True)[SALES].sum()

if not monthly_sales.empty:
    high_month=monthly_sales.idxmax()
    high_sales=monthly_sales.max()
    low_month=monthly_sales.idxmin()
    low_sales=monthly_sales.min()
    avg_sales=monthly_sales.mean()
else:
    high_month=low_month="N/A"
    high_sales=low_sales=avg_sales=0

a,b,c,d=st.columns(4)
a.metric("📈 Highest Sales Month",high_month)
b.metric("💰 Highest Monthly Sales",f"₹{high_sales:,.0f}")
c.metric("📉 Lowest Sales Month",low_month)
d.metric("📊 Avg. Monthly Sales",f"₹{avg_sales:,.0f}")

# Trend
st.markdown("### 📈 Sales Trend")
if len(monthly_sales)>=2:
    latest_month=monthly_sales.index[-1]
    previous_month=monthly_sales.index[-2]
    latest_sales=monthly_sales.iloc[-1]
    previous_sales=monthly_sales.iloc[-2]
    change=((latest_sales-previous_sales)/previous_sales*100) if previous_sales else 0

    a,b,c=st.columns(3)
    a.metric("📅 Latest Month",latest_month)
    b.metric("💰 Latest Sales",f"₹{latest_sales:,.0f}")
    c.metric("📊 Month-over-Month Change",f"{change:+.2f}%")
else:
    st.info("Not enough monthly data to calculate the sales trend.")

# Insights
st.subheader("🤖 MetricMind Business Insights")

if not cat.empty:
    top_row=cat.loc[cat[SALES].idxmax()]
    top_category=top_row[CATEGORY]
    top_category_sales=top_row[SALES]
else:
    top_category="N/A"
    top_category_sales=0

top_month=monthly_sales.idxmax() if not monthly_sales.empty else "N/A"
top_month_sales=monthly_sales.max() if not monthly_sales.empty else 0
aov=total_sales/total_orders if total_orders else 0

a,b,c=st.columns(3)
with a:
    st.info(f"🏆 **Top Category**\n\n### {top_category}\n\nSales: **₹{top_category_sales:,.0f}**")
with b:
    st.info(f"📅 **Best Sales Month**\n\n### {top_month}\n\nSales: **₹{top_month_sales:,.0f}**")
with c:
    st.info(f"🛒 **Average Order Value**\n\n### ₹{aov:,.0f}\n\nBased on total sales and orders")

st.success(
    f"💰 **Total Sales:** ₹{total_sales:,.0f}\n\n"
    f"💵 **Total Revenue:** ₹{total_revenue:,.0f}\n\n"
    f"📈 **Total Profit:** ₹{total_profit:,.0f}\n\n"
    f"📊 **Profit Margin:** {profit_margin:.2f}%"
)

# Download
st.subheader("📥 Download Filtered Report")
report=monthly.drop(columns=[MONTH_NUMBER],errors="ignore")
filename=f"MetricMind_{str(category).replace(' ','_')}_{str(year).replace(' ','_')}.csv"

st.download_button(
    "⬇️ Download CSV Report",
    data=report.to_csv(index=False),
    file_name=filename,
    mime="text/csv"
)

st.subheader("📋 Cube Data")
st.dataframe(report,use_container_width=True)