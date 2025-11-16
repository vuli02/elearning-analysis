# =======================================================
# Fraunhofer – AI Forecasting Demo (Streamlit)
# Author: Linh Vu
# =======================================================

import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------------
# 1. PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="AI Forecasting – Fraunhofer Academy",
    layout="wide",
)

st.title("🤖 AI Forecasting – Fraunhofer Learning Analytics")
st.markdown("**Revenue & Participant Forecast using Synthetic Data**")
st.markdown("---")

# -------------------------------------------------------
# 2. LOAD SYNTHETIC TIME-SERIES DATA
# -------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("courses_timeseries.csv")
    df["month"] = pd.to_datetime(df["month"])
    return df

df = load_data()


# -------------------------------------------------------
# 3. SIDEBAR: COURSE SELECTION
# -------------------------------------------------------
st.sidebar.header("📌 Select Course")

course_list = df["course_name"].unique().tolist()
selected_course = st.sidebar.selectbox("Course:", course_list)

df_course = df[df["course_name"] == selected_course].copy()

st.sidebar.success(f"{len(df_course)} months of data loaded.")


# -------------------------------------------------------
# 4. PREPARE DATA FOR PROPHET
# -------------------------------------------------------
def prepare_prophet(col_name):
    temp = df_course[["month", col_name]].rename(columns={
        "month": "ds",
        col_name: "y"
    })
    return temp

revenue_ts = prepare_prophet("revenue_monthly")
participants_ts = prepare_prophet("participants_monthly")


# -------------------------------------------------------
# 5. RUN FORECASTING
# -------------------------------------------------------
def prophet_forecast(df_ts, periods=3):
    model = Prophet(seasonality_mode="multiplicative")
    model.fit(df_ts)

    future = model.make_future_dataframe(periods=periods, freq="M")
    forecast = model.predict(future)
    return model, forecast

model_rev, fc_rev = prophet_forecast(revenue_ts)
model_part, fc_part = prophet_forecast(participants_ts)


# -------------------------------------------------------
# 6. PLOT – REVENUE FORECAST
# -------------------------------------------------------
st.subheader("📈 Revenue Forecast (Next 3 Months)")

fig_rev = go.Figure()

# Past
fig_rev.add_trace(go.Scatter(
    x=fc_rev["ds"], y=fc_rev["yhat"],
    mode="lines",
    name="Forecast",
    line=dict(color="#179C7D", width=3)
))

# Confidence interval
fig_rev.add_traces([
    go.Scatter(
        x=fc_rev["ds"], y=fc_rev["yhat_upper"],
        line=dict(color="#CCEDE5"), showlegend=False
    ),
    go.Scatter(
        x=fc_rev["ds"], y=fc_rev["yhat_lower"],
        fill="tonexty",
        line=dict(color="#CCEDE5"),
        name="Confidence Interval",
        opacity=0.3
    )
])

fig_rev.update_layout(
    height=380,
    xaxis_title="Month",
    yaxis_title="Revenue (€)",
    template="plotly_white"
)

st.plotly_chart(fig_rev, use_container_width=True)


# -------------------------------------------------------
# 7. PLOT – PARTICIPANT FORECAST
# -------------------------------------------------------
st.subheader("👥 Participants Forecast (Next 3 Months)")

fig_part = go.Figure()

fig_part.add_trace(go.Scatter(
    x=fc_part["ds"], y=fc_part["yhat"],
    mode="lines",
    name="Forecast",
    line=dict(color="#179C7D", width=3)
))

fig_part.add_traces([
    go.Scatter(
        x=fc_part["ds"], y=fc_part["yhat_upper"],
        line=dict(color="#CCEDE5"), showlegend=False
    ),
    go.Scatter(
        x=fc_part["ds"], y=fc_part["yhat_lower"],
        fill="tonexty",
        line=dict(color="#CCEDE5"),
        name="Confidence Interval",
        opacity=0.3
    )
])

fig_part.update_layout(
    height=380,
    xaxis_title="Month",
    yaxis_title="Participants",
    template="plotly_white"
)

st.plotly_chart(fig_part, use_container_width=True)


# -------------------------------------------------------
# 8. AUTO INSIGHTS
# -------------------------------------------------------
st.markdown("### 🧠 AI-Generated Forecast Insights")

def create_insights(forecast, label):
    last = forecast.iloc[-1]
    prev = forecast.iloc[-4]  # 3 months before

    growth_rate = (last["yhat"] - prev["yhat"]) / prev["yhat"] * 100

    if growth_rate > 15:
        trend = "strong upward trend 📈"
    elif growth_rate > 5:
        trend = "moderate growth 📈"
    elif growth_rate > 0:
        trend = "slight upward trend ↗"
    else:
        trend = "downward trend 📉"

    return f"""
### **{label}**
- Expected value in 3 months: **{last['yhat']:.0f}**
- Growth vs. today: **{growth_rate:.1f}%**
- Trend Classification: **{trend}**
"""

insight_revenue = create_insights(fc_rev, "Revenue")
insight_part = create_insights(fc_part, "Participants")

st.info(insight_revenue)
st.info(insight_part)


# -------------------------------------------------------
# 9. END
# -------------------------------------------------------
st.caption("© 2025 Fraunhofer Academy – AI Forecasting Demo by Linh Vu")
