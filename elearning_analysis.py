# =======================================================
# Fraunhofer eLearning Management Dashboard
# Author: Linh Vu
# =======================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -------------------------------------------------------
# 1. CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="Fraunhofer Management Dashboard",
    layout="wide",
)

# Fraunhofer color palette
FRAU_GREEN = "#179C7D"
FRAU_LIGHT = "#CCEDE5"

# -------------------------------------------------------
# 2. STYLE – CSS
# -------------------------------------------------------
st.markdown(
    f"""
    <style>
        .kpi-card {{
            background-color: {FRAU_LIGHT};
            padding: 18px;
            border-radius: 12px;
            text-align: center;
            border-left: 6px solid {FRAU_GREEN};
            margin-bottom: 15px;
        }}
        .kpi-value {{
            font-size: 28px;
            font-weight: 700;
            color: {FRAU_GREEN};
        }}
        .kpi-label {{
            font-size: 14px;
            font-weight: 500;
            color: #222222;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# 3. LOAD DATA + PES
# -------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(
        "C:/Users/vuli/Documents/Elearning-Analysis/elearning-analysis/fraunhofer_dashboard_data.csv"
    )

    # Revenue per participant
    df["revenue_per_participant"] = np.where(
        df["participants"] > 0,
        df["revenue"] / df["participants"],
        0.0,
        )

    # Normalized satisfaction (0–1)
    df["satisfaction_score"] = df["satisfaction"] / 5

    # Rank-based quantile scores for adoption & engagement
    df["adoption_score"] = df["participants"].rank(pct=True)
    df["engagement_score"] = df["num_reviews"].rank(pct=True)

    # Product Engagement Score (PES)
    df["PES"] = (
                        df["adoption_score"]
                        + df["engagement_score"]
                        + df["satisfaction_score"]
                ) / 3

    return df


df = load_data()

# -------------------------------------------------------
# 4. SIDEBAR FILTER PANEL
# -------------------------------------------------------
st.sidebar.title("🔍 Filter Panel")

price_min = float(df["price"].min())
price_max = float(df["price"].max())
sat_min = 0.0
sat_max = 5.0

price_range = st.sidebar.slider(
    "Price Range (€)",
    min_value=price_min,
    max_value=price_max,
    value=(price_min, price_max),
)

satisfaction_range = st.sidebar.slider(
    "Satisfaction Range",
    min_value=sat_min,
    max_value=sat_max,
    value=(sat_min, sat_max),
)

# Apply filters
df_filtered = df[
    (df["price"].between(*price_range))
    & (df["satisfaction"].between(*satisfaction_range))
    ]

st.sidebar.success(f"{len(df_filtered):,} courses selected")

# -------------------------------------------------------
# 5. KPI CALCULATION (BASED ON FILTERED DATA)
# -------------------------------------------------------
total_revenue = df_filtered["revenue"].sum()
total_participants = df_filtered["participants"].sum()
avg_satisfaction = df_filtered["satisfaction"].mean()
avg_roi = df_filtered["revenue_per_participant"].mean()
avg_PES = df_filtered["PES"].mean()

# -------------------------------------------------------
# 6. HEADER
# -------------------------------------------------------
st.title("🎓 Fraunhofer Academy – Management Dashboard")
st.markdown("**Learning Performance • Portfolio Insights • ROI Overview**")
st.markdown("---")

# -------------------------------------------------------
# 7. KPI CARDS – SINGLE ROW
# -------------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)

def render_kpi(col, label, value):
    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

render_kpi(k1, "Total Revenue (€)", f"{total_revenue:,.0f}")
render_kpi(k2, "Participants", f"{total_participants:,.0f}")
render_kpi(k3, "Avg. Satisfaction", f"{avg_satisfaction:.2f}/5")
render_kpi(k4, "Revenue per Participant (€)", f"{avg_roi:,.2f}")
render_kpi(k5, "Product Engagement Score (PES)", f"{avg_PES:.2f}")

st.markdown("---")

# -------------------------------------------------------
# 8. MAIN VISUALIZATIONS – SINGLE ROW (3 CHARTS)
# -------------------------------------------------------

# 8.1 Revenue by Price Segment
# Define simple price segments for management view
segments = pd.cut(
    df_filtered["price"],
    bins=[0, 10, 20, df_filtered["price"].max()],
    labels=["Low (<10€)", "Mid (10–20€)", "Premium (>20€)"],
    include_lowest=True,
)

seg_df = (
    df_filtered.assign(price_segment=segments)
    .groupby("price_segment", observed=True)["revenue"]
    .sum()
    .reset_index()
    .sort_values("revenue", ascending=False)
)

fig_price_seg = px.bar(
    seg_df,
    x="price_segment",
    y="revenue",
    color_discrete_sequence=[FRAU_GREEN],
    labels={"price_segment": "Price Segment", "revenue": "Total Revenue (€)"},
    title="Revenue by Price Segment",
)
fig_price_seg.update_layout(margin=dict(l=10, r=10, t=40, b=10))

# 8.2 Risk Matrix – Revenue vs Satisfaction
fig_risk = px.scatter(
    df_filtered,
    x="satisfaction",
    y="revenue",
    size="participants",
    color="price",
    color_continuous_scale="Tealgrn",
    hover_data=["course_name"],
    labels={"satisfaction": "Satisfaction (0–5)", "revenue": "Revenue (€)"},
    title="Revenue vs Satisfaction (Risk Matrix)",
)
fig_risk.update_layout(margin=dict(l=10, r=10, t=40, b=10))

# 8.3 Top 10 Revenue Courses
top10 = df_filtered.nlargest(10, "revenue")
fig_top10 = px.bar(
    top10,
    x="revenue",
    y="course_name",
    orientation="h",
    color="satisfaction",
    color_continuous_scale="Tealgrn",
    labels={"revenue": "Revenue (€)", "course_name": "Course"},
    title="Top 10 Revenue Courses",
)
fig_top10.update_layout(
    margin=dict(l=10, r=60, t=40, b=10),
    yaxis=dict(automargin=True),
)

# Column layout: give Top10 a bit more width
c1, c2, c3 = st.columns([1.1, 1.2, 1.5])
c1.plotly_chart(fig_price_seg, use_container_width=True)
c2.plotly_chart(fig_risk, use_container_width=True)
c3.plotly_chart(fig_top10, use_container_width=True)

# -------------------------------------------------------
# 9. MANAGEMENT INSIGHTS & ACTIONS
# -------------------------------------------------------
st.markdown("### Management Insights & Recommended Actions")

st.write(
    """
**1. Very high reach, but low revenue per participant.**  
→ Consider **upselling paths**, premium certificates, or advanced tracks to increase revenue per learner.

**2. Average satisfaction (3.92/5) is good, but not excellent.**  
→ Targeted improvements in content and didactics could directly increase revenue, as high-revenue courses are mainly in the **4–5 satisfaction range**.

**3. Product Engagement Score (≈0.59) is moderate.**  
→ Optimise **course structure, interactivity, learning paths, reminders and follow-ups** to lift engagement.

**4. Price structure is clearly low-cost dominated.**  
→ Current strategy is strongly volume-driven – there is room to design **clear premium offerings**.

**5. High satisfaction aligns with high revenue.**  
→ Quality is the main revenue driver. Courses with satisfaction **< 3.5** contribute little and should be **reviewed or retired**.

**6. Clear premium candidates.**  
Courses like *Deep Learning Prerequisites*, *SQL Bootcamp*, *Financial Analyst Course* combine **high price, high satisfaction and high revenue**.  
→ These are strong anchors for **premium learning paths and certificate programmes**.

**7. Tech & management topics dominate the top-line.**  
Python, SQL, Finance, MBA and Agile/Scrum make up most of the top-revenue list.  
→ Prioritise these themes in future programme development. Underperforming themes can be reduced or repositioned.
"""
)

st.markdown("#### Executive Action Points")
st.write(
    """
- **Boost marketing for high-rated but low-revenue courses**  

- **Portfolio clean-up for low-satisfaction courses (<3.5)**  
  Improve, re-design or phase out weak offerings.

- **Expand premium programmes**  
  Build structured tracks around Deep Learning, SQL, Finance and Agile with **higher price points** and certificates.

- **Increase product engagement**  
  Introduce **gamification, badges, certificates, modular learning paths, and progress tracking** to strengthen retention.

- **Refine pricing strategy**  
  Experiment with **tiered pricing, bundles and certificate fees** instead of pure low-cost mass pricing.
"""
)

st.caption("© 2025 Fraunhofer Academy – Dashboard Design by Linh Vu")
