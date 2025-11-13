# ============================================
# Fraunhofer eLearning / Udemy Dataset Analysis
# Author: Linh Vu
# ============================================

# fraunhofer_management_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------
# 1. LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("C:/Users/vuli/Documents/Elearning-Analysis/elearning-analysis/fraunhofer_dashboard_data.csv")
    df['revenue_per_participant'] = np.where(df['participants'] > 0,
                                             df['revenue'] / df['participants'], 0)
    # Chuẩn hóa satisfaction (0–5)
    df['satisfaction_norm'] = df['satisfaction'] / 5
    return df

df = load_data()

# -----------------------------
# 2. KPI CALCULATION
# -----------------------------
total_revenue = df['revenue'].sum()
total_participants = df['participants'].sum()
avg_satisfaction = df['satisfaction'].mean()
revenue_per_participant = df['revenue_per_participant'].mean()

# Product Engagement Score (PES)
# = trung bình normalized của adoption, growth, satisfaction
df['adoption'] = df['participants'] / df['participants'].max()
df['growth'] = df['num_reviews'] / df['num_reviews'].max()
df['PES'] = ((df['adoption'] + df['growth'] + df['satisfaction_norm']) / 3)
avg_PES = df['PES'].mean()

# -----------------------------
# 3. STREAMLIT DASHBOARD
# -----------------------------
st.set_page_config(page_title="Fraunhofer Management Dashboard", layout="wide")
st.title("📊 Fraunhofer Academy – Management Dashboard")
st.markdown("**Learning Performance & ROI Overview**")

# KPI cards
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💶 Total Revenue (€)", f"{total_revenue:,.0f}")
col2.metric("👥 Participants", f"{total_participants:,.0f}")
col3.metric("⭐ Avg. Satisfaction", f"{avg_satisfaction:.2f}/5")
col4.metric("📈 Revenue per Participant (€)", f"{revenue_per_participant:,.0f}")
col5.metric("🔥 Product Engagement Score (PES)", f"{avg_PES:.2f}")

st.markdown("---")

# -----------------------------
# 4. VISUALIZATIONS
# -----------------------------
st.subheader("Top 10 Courses by ROI (Revenue per Participant)")
top10_roi = df.nlargest(10, 'revenue_per_participant')
fig1 = px.bar(top10_roi, x='revenue_per_participant', y='course_name', orientation='h',
              color='satisfaction', color_continuous_scale='Tealgrn',
              labels={'revenue_per_participant': 'Revenue per Participant (€)', 'course_name': 'Course Name'},
              title='Top 10 ROI Courses')
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Revenue vs Satisfaction (Bubble = Participants, Color = Price)")
fig2 = px.scatter(df, x='satisfaction', y='revenue',
                  size='participants', color='price',
                  color_continuous_scale='RdBu',
                  hover_data=['course_name'],
                  title='Revenue vs Satisfaction (Bubble = Participants, Color = Price)')
st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 5. Quadrant Analysis
# -----------------------------
st.subheader("Revenue vs Satisfaction Quadrant")
median_revenue = df['revenue'].median()
median_satisfaction = df['satisfaction'].median()

df['revenue_level'] = np.where(df['revenue'] >= median_revenue, 'High', 'Low')
df['satisfaction_level'] = np.where(df['satisfaction'] >= median_satisfaction, 'High', 'Low')
quadrant = df.groupby(['revenue_level', 'satisfaction_level']).size().unstack(fill_value=0)

fig3 = px.imshow(quadrant, text_auto=True, color_continuous_scale='Blues',
                 labels=dict(x="Satisfaction Level", y="Revenue Level", color="Course Count"),
                 title="Revenue vs Satisfaction Quadrant")
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# 6. Key Insights
# -----------------------------
st.markdown("## 🧠 Key Insights & Recommendations")
st.write("""
- **High revenue – low satisfaction courses** indicate potential risk zones; consider reviewing content quality and learner feedback.
- **Low revenue – high satisfaction courses** have strong potential for marketing & scaling.
- The overall **Product Engagement Score (PES)** shows solid learner engagement across most offerings.
- **Price does not strongly correlate** with satisfaction — focus on quality and relevance rather than pricing strategy.
- Regularly monitor **Revenue per Participant** to evaluate ROI of new learning programs.
""")

st.markdown("---")
st.caption("© 2025 Fraunhofer Academy | Dashboard design by Linh Vu")
