# ===========================================================
# FRAUNHOFER MANAGEMENT DASHBOARD — Compact PowerBI Layout
# ===========================================================

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

FRAU_GREEN = "#179C7D"
FRAU_LIGHT = "#CCEDE5"
FRAU_BG = "#F4FAF8"

# -------------------------------------------------------
# 2. CSS STYLE — Compact Like PowerBI
# -------------------------------------------------------
st.markdown(
    f"""
    <style>
        .main {{
            background-color: {FRAU_BG};
        }}
        .block-container {{
            padding: 1rem 2rem 1rem 2rem;
            max-width: 95%;
        }}
        /* KPI CARD */
        .kpi-card {{
            background-color: {FRAU_LIGHT};
            padding: 10px 14px;
            border-radius: 12px;
            border-left: 6px solid {FRAU_GREEN};
            margin-bottom: 5px;
            height: 80px;
        }}
        .kpi-inner {{
            display: flex;
            align-items: center;
        }}
        .kpi-icon {{
            font-size: 22px;
            margin-right: 10px;
        }}
        .kpi-label {{
            font-size: 11px;
            font-weight: 600;
            color: #234;
        }}
        .kpi-value {{
            font-size: 20px;
            font-weight: 700;
            color: {FRAU_GREEN};
            margin-top: -2px;
        }}
        .section-title {{
            font-size: 18px;
            font-weight: 700;
            margin-top: 12px;
            margin-bottom: 2px;
        }}
        .section-sub {{
            font-size: 11px;
            color: #555;
            margin-bottom: 5px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# 3. LOAD DATA
# -------------------------------------------------------
def load_data():
    df = pd.read_csv("fraunhofer_enriched.csv")

    if "ROI" not in df.columns:
        rng = np.random.default_rng(42)
        df["program_cost"] = df["revenue"] * rng.uniform(0.4, 0.7, len(df))
        df["ROI"] = (df["revenue"] - df["program_cost"]) / df["program_cost"]

    df = df[df["subject"] != "Other"].copy()
    return df

df = load_data()

# -------------------------------------------------------
# 4. Minimal Sidebar — chỉ có Subject
# -------------------------------------------------------
st.sidebar.header("🔍 Filter")

subjects = ["All"] + sorted(df["subject"].unique())
selected_subject = st.sidebar.selectbox("Themenfeld", subjects)

df_filtered = df.copy()
if selected_subject != "All":
    df_filtered = df_filtered[df_filtered["subject"] == selected_subject]

# -------------------------------------------------------
# 5. KPI CALC
# -------------------------------------------------------
total_revenue = df_filtered["revenue"].sum()
total_participants = df_filtered["participants"].sum()
avg_satisfaction = df_filtered["satisfaction"].mean()
avg_roi = df_filtered["ROI"].mean()

# -------------------------------------------------------
# 6. HEADER
# -------------------------------------------------------
st.title("🎓 Fraunhofer Academy – Management Dashboard")
st.markdown("**Themenfeld Overview • ROI • Satisfaction**")
st.markdown("---")

# -------------------------------------------------------
# 7. KPI ROW — COMPACT
# -------------------------------------------------------
k1, k2, k3, k4 = st.columns(4)

def kpi(col, icon, label, value):
    col.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-inner">
             <div class="kpi-icon">{icon}</div>
             <div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
             </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

kpi(k1, "💶", "Total Revenue (€)", f"{total_revenue:,.0f}")
kpi(k2, "👥", "Total Participants", f"{total_participants:,.0f}")
kpi(k3, "⭐", "Avg. Satisfaction", f"{avg_satisfaction:.2f}/5")
kpi(k4, "📈", "Avg. ROI", f"{avg_roi:.2f}")

st.markdown("---")

# -------------------------------------------------------
# 8. PORTFOLIO OVERVIEW — 3 Horizontal Charts in One Row
# -------------------------------------------------------
st.markdown('<div class="section-title">📊 Portfolio Overview</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Umsatz • Zufriedenheit • ROI nach Themenfeld</div>', unsafe_allow_html=True)

# Revenue
rev = df_filtered.groupby("subject")["revenue"].sum().reset_index()
rev = rev.sort_values("revenue", ascending=True)

fig_rev = px.bar(
    rev, x="revenue", y="subject",
    orientation="h",
    color_discrete_sequence=[FRAU_GREEN],
    title="Revenue",
)
fig_rev.update_layout(height=300, margin=dict(l=5,r=5,t=30,b=5))

# Satisfaction
sat = df_filtered.groupby("subject")["satisfaction"].mean().reset_index()
sat = sat.sort_values("satisfaction", ascending=True)

fig_sat = px.bar(
    sat, x="satisfaction", y="subject",
    orientation="h",
    color_discrete_sequence=[FRAU_GREEN],
    title="Satisfaction",
)
fig_sat.update_layout(height=300, margin=dict(l=5,r=5,t=30,b=5), xaxis_range=[0,5])

# ROI
roi = df_filtered.groupby("subject")["ROI"].mean().reset_index()
roi = roi.sort_values("ROI", ascending=True)

fig_roi = px.bar(
    roi, x="ROI", y="subject",
    orientation="h",
    color_discrete_sequence=[FRAU_GREEN],
    title="ROI",
)
fig_roi.update_layout(height=300, margin=dict(l=5,r=5,t=30,b=5))

c1, c2, c3 = st.columns(3)
c1.plotly_chart(fig_rev, use_container_width=True)
c2.plotly_chart(fig_sat, use_container_width=True)
c3.plotly_chart(fig_roi, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------
# 9. COURSE PERFORMANCE — 2 Horizontal Charts
# -------------------------------------------------------
st.markdown('<div class="section-title">📚 Course Performance</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Top 10 Revenue & ROI</div>', unsafe_allow_html=True)

top_rev = (
    df_filtered.sort_values("revenue", ascending=False)
    .head(10)
    .sort_values("revenue")
)

fig_top_rev = px.bar(
    top_rev,
    x="revenue",
    y="course_name",
    orientation="h",
    color="satisfaction",
    color_continuous_scale="Tealgrn",
    title="Top Revenue",
)
fig_top_rev.update_layout(height=350, margin=dict(l=5,r=5,t=30,b=5))

top_roi = (
    df_filtered.sort_values("ROI", ascending=False)
    .head(10)
    .sort_values("ROI")
)

fig_top_roi = px.bar(
    top_roi,
    x="ROI",
    y="course_name",
    orientation="h",
    color="ROI",
    color_continuous_scale="Viridis",
    title="Top ROI",
)
fig_top_roi.update_layout(height=350, margin=dict(l=5,r=5,t=30,b=5))

c4, c5 = st.columns(2)
c4.plotly_chart(fig_top_rev, use_container_width=True)
c5.plotly_chart(fig_top_roi, use_container_width=True)

st.caption("© 2025 Fraunhofer Academy — Dashboard by Linh Vu")
