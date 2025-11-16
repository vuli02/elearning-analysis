# =======================================================
# Fraunhofer Mini-KI Demo – Forecast + Anomaly + Insights
# Author: Linh Vu
# =======================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests

st.set_page_config(page_title="KI Automation Demo", layout="wide")

# -------------------------------------------------------
# 1. LOAD DATA
# -------------------------------------------------------
@st.cache_data
def load_timeseries():
    df = pd.read_csv("courses_timeseries.csv")
    df["month"] = pd.to_datetime(df["month"])
    df = df.sort_values("month")
    return df

df = load_timeseries()

# -------------------------------------------------------
# 2. COURSE SELECTOR
# -------------------------------------------------------
st.sidebar.header("Filter Panel")

course_list = sorted(df["course_name"].unique())
selected_course = st.sidebar.selectbox("Select Course", course_list)

ts = df[df["course_name"] == selected_course].copy()
ts = ts.sort_values("month")

course_name = selected_course
st.title("Demo – Forecasting, Anomaly Detection & Insights")
st.subheader(f"Course: **{course_name}**")

ts["revenue"] = ts["revenue_monthly"]

# -------------------------------------------------------
# 3. FORECAST MODEL
# -------------------------------------------------------
ts["ma"] = ts["revenue"].rolling(window=3, min_periods=1).mean()

x = np.arange(len(ts))
y = ts["revenue"].values

if len(ts) > 1:
    slope, intercept = np.polyfit(x, y, 1)
else:
    slope, intercept = 0, ts["revenue"].iloc[0]

ts["trend"] = intercept + slope * x

next_x = len(ts)
forecast = max(intercept + slope * next_x, 0)

# -------------------------------------------------------
# 4. ANOMALY DETECTION – Z-SCORE
# -------------------------------------------------------
mean_rev = ts["revenue"].mean()
std_rev = ts["revenue"].std() if ts["revenue"].std() != 0 else 1

ts["z_score"] = (ts["revenue"] - mean_rev) / std_rev
ts["anomaly"] = ts["z_score"].abs() > 2

last_is_anomaly = ts["anomaly"].iloc[-1]
last_month = ts["month"].iloc[-1]

# -------------------------------------------------------
# 5. KPI CARDS
# -------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("Last Revenue", f"{ts['revenue'].iloc[-1]:,.0f} €")
col2.metric("Trend Slope", f"{slope:,.2f}")
col3.metric("Forecast Next Month", f"{forecast:,.0f} €")
col4.metric("Anomaly Detected?", "⚠️ YES" if last_is_anomaly else "✅ No")

st.markdown("---")

# -------------------------------------------------------
# 6. PLOT FORECAST
# -------------------------------------------------------
fig = px.line(ts, x="month", y="revenue", title="📈 Revenue Forecasting", markers=True)

# Moving avg
fig.add_scatter(x=ts["month"], y=ts["ma"], mode="lines", name="Moving Avg")

# Trend
fig.add_scatter(x=ts["month"], y=ts["trend"], mode="lines", name="Trend Line")

# Forecast point
fig.add_scatter(
    x=[last_month + pd.DateOffset(months=1)],
    y=[forecast],
    mode="markers",
    name="Forecast",
    marker=dict(size=16, symbol="star", color="red"),
)

# Highlight LAST MONTH
fig.add_scatter(
    x=[last_month],
    y=[ts["revenue"].iloc[-1]],
    mode="markers",
    name="Last Month",
    marker=dict(size=22, color="orange"),
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------
# 7. PLOT ANOMALIES
# -------------------------------------------------------
fig2 = px.scatter(
    ts,
    x="month",
    y="revenue",
    color="anomaly",
    title="🔍 Anomaly Detection (Z-Score > 2)",
    color_discrete_map={False: "green", True: "red"},
    size=np.where(ts["anomaly"], 20, 10),
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# -------------------------------------------------------
# 8. INSIGHTS – Root Cause + Explanation
# -------------------------------------------------------

st.subheader("Why is this anomaly happening?")

if last_is_anomaly:
    last_rev = ts["revenue"].iloc[-1]
    avg_rev = ts["revenue"].mean()

    diff_pct = (last_rev - avg_rev) / avg_rev * 100

    if diff_pct < 0:
        direction = "Revenue dropped significantly"
    else:
        direction = "Revenue spiked unexpectedly"

    st.write(f"""
### ⚠️ Insight for {last_month.strftime('%B %Y')}
- **{direction}**: {diff_pct:.1f}%
- Z-Score: **{ts['z_score'].iloc[-1]:.2f}**
- Compared to normal demand, this value is **outside typical variation**.

""")

    # ROOT CAUSE TABLE
    st.write("### Possible Root Causes")

    # ACTIONS
    st.write("### Recommended Actions")

else:
    st.info("No anomaly detected → No insights needed.")

st.markdown("---")

# -------------------------------------------------------
# 9. SLACK ALERT
# -------------------------------------------------------

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

def send_slack_alert(msg_text):
    payload = {"text": msg_text}
    requests.post(SLACK_WEBHOOK_URL, json=payload)

st.subheader("Alerting")

if last_is_anomaly:
    if st.button("Send Slack Alert"):
        alert_text = f"""
*⚠️ Revenue Anomaly Detected!*
Course: *{course_name}*
Month: *{last_month.strftime('%B %Y')}*

• Revenue: *{ts['revenue'].iloc[-1]:,.0f} €*
• Z-Score: *{ts['z_score'].iloc[-1]:.2f}*
• Deviation: *{diff_pct:.1f}%* from normal

Please review immediately.
"""
        send_slack_alert(alert_text)
        st.success("Slack alert sent successfully!")
else:
    st.info("No anomaly → Slack alert disabled.")
