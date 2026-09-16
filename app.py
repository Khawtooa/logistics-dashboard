import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Logistics & Delivery Performance Dashboard",
    page_icon="🚚",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-title {
        font-size: 26px;
        font-weight: bold;
        color: #1B365D;
        margin-bottom: 5px;
    }
    .sub-title {
        font-size: 14px;
        color: #555555;
        margin-bottom: 25px;
    }
    div[data-testid="stMetricValue"] {
        font-size: 22px;
        font-weight: bold;
        color: #1B365D;
    }
</style>
""", unsafe_allow_html=True)

# 2. Load Data
@st.cache_data
def load_data():
    file_path = "Delivery_Logistics_300rows_12cols.xlsx"
    df = pd.read_excel(file_path, df = pd.read_excel(file_path)
    return df

df = load_data()

# 3. Sidebar Filters
st.sidebar.image("https://img.icons8.com/color/96/delivery--v1.png", width=70)
st.sidebar.title("🔍 ตัวกรองข้อมูล (Filters)")

region_filter = st.sidebar.multiselect(
    "เลือกภูมิภาค (Region):",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

partner_filter = st.sidebar.multiselect(
    "เลือกผู้ให้บริการขนส่ง (Partner):",
    options=df["Delivery Partner"].unique(),
    default=df["Delivery Partner"].unique()
)

vehicle_filter = st.sidebar.multiselect(
    "เลือกประเภทยานพาหนะ (Vehicle):",
    options=df["Vehicle Type"].unique(),
    default=df["Vehicle Type"].unique()
)

status_filter = st.sidebar.multiselect(
    "เลือกสถานะการจัดส่ง (Status):",
    options=df["Delivery Status"].unique(),
    default=df["Delivery Status"].unique()
)

# Filter Dataset
df_filtered = df[
    (df["Region"].isin(region_filter)) &
    (df["Delivery Partner"].isin(partner_filter)) &
    (df["Vehicle Type"].isin(vehicle_filter)) &
    (df["Delivery Status"].isin(status_filter))
]

# 4. Main Dashboard Header
st.markdown('<div class="main-title">🚚 Web Interactive Dashboard: logistics & Delivery Performance</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">ระบบวิเคราะห์ประสิทธิภาพการจัดส่งและต้นทุนโลจิสติกส์ (Descriptive Analytics)</div>', unsafe_allow_html=True)

st.divider()

# 5. KPI Metrics (5 KPIs)
col1, col2, col3, col4, col5 = st.columns(5)

total_shipments = len(df_filtered)
otd_count = (df_filtered["Delivery Status"] == "delivered").sum()
otd_rate = (otd_count / total_shipments * 100) if total_shipments > 0 else 0
avg_time = df_filtered["Delivery Time (hrs)"].mean() if total_shipments > 0 else 0
total_cost = df_filtered["Delivery Cost (THB)"].sum() if total_shipments > 0 else 0
avg_cost_km = (df_filtered["Delivery Cost (THB)"] / df_filtered["Distance (km)"]).mean() if total_shipments > 0 else 0
fail_delay_count = (df_filtered["Delivery Status"].isin(["delayed", "failed"])).sum()
fail_delay_rate = (fail_delay_count / total_shipments * 100) if total_shipments > 0 else 0

with col1:
    st.metric("1. OTD Rate (%)", f"{otd_rate:.2f}%", help="อัตราการจัดส่งตรงเวลา")

with col2:
    st.metric("2. Avg Transit Time", f"{avg_time:.2f} ชม.", help="เวลาจัดส่งเฉลี่ย")

with col3:
    st.metric("3. Total Cost", f"฿{total_cost:,.2f}", help="ต้นทุนขนส่งรวม")

with col4:
    st.metric("4. Avg Cost / KM", f"฿{avg_cost_km:.2f}/กม.", help="ต้นทุนเฉลี่ยต่อกิโลเมตร")

with col5:
    st.metric("5. Failure & Delay Rate", f"{fail_delay_rate:.2f}%", help="อัตราส่งล่าช้าและล้มเหลว")

st.divider()

# 6. Visualizations Section
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("📊 สัดส่วนสถานะการจัดส่ง (Delivery Status)")
    if total_shipments > 0:
        fig_status = px.pie(
            df_filtered, 
            names="Delivery Status", 
            color="Delivery Status",
            color_discrete_map={"delivered": "#2E7D32", "delayed": "#ED6C02", "failed": "#D32F2F"},
            hole=0.4
        )
        fig_status.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)
    else:
        st.warning("ไม่มีข้อมูลตามตัวกรองที่เลือก")

with row1_col2:
    st.subheader("🚛 ยอดรวมค่าขนส่งแยกตาม Partner")
    if total_shipments > 0:
        cost_partner = df_filtered.groupby("Delivery Partner")["Delivery Cost (THB)"].sum().reset_index()
        fig_partner = px.bar(
            cost_partner, 
            x="Delivery Partner", 
            y="Delivery Cost (THB)",
            text_auto=".2f",
            color="Delivery Partner",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_partner.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_partner, use_container_width=True)
    else:
        st.warning("ไม่มีข้อมูลตามตัวกรองที่เลือก")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("🗺️ ต้นทุนและระยะทางเฉลี่ยแยกตามภูมิภาค")
    if total_shipments > 0:
        region_df = df_filtered.groupby("Region").agg({"Delivery Cost (THB)": "sum", "Distance (km)": "mean"}).reset_index()
        fig_region = px.bar(
            region_df,
            x="Region",
            y="Delivery Cost (THB)",
            hover_data=["Distance (km)"],
            color_discrete_sequence=["#1B365D"]
        )
        fig_region.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_region, use_container_width=True)
    else:
        st.warning("ไม่มีข้อมูลตามตัวกรองที่เลือก")

with row2_col2:
    st.subheader("☀️ ระยะเวลาส่งเฉลี่ยแยกตามสภาพอากาศ")
    if total_shipments > 0:
        weather_df = df_filtered.groupby("Weather Condition")["Delivery Time (hrs)"].mean().reset_index()
        fig_weather = px.bar(
            weather_df,
            x="Weather Condition",
            y="Delivery Time (hrs)",
            text_auto=".2f",
            color_discrete_sequence=["#0288D1"]
        )
        fig_weather.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_weather, use_container_width=True)
    else:
        st.warning("ไม่มีข้อมูลตามตัวกรองที่เลือก")

# Data Table Section
with st.expander("📋 ดูข้อมูลตารางที่ผ่านการกรอง (Cleaned Data View)"):
    st.dataframe(df_filtered)
