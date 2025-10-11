"""Analytics Dashboard - Admin Panel"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.title("📊 Analytics Dashboard")
st.write("System-wide analytics and insights")

st.divider()

# Date range selector
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))

with col2:
    end_date = st.date_input("End Date", value=datetime.now())

st.divider()

# Key Metrics
st.subheader("📈 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Job Descriptions Created", "0", delta="+0%")

with col2:
    st.metric("Resumes Screened", "0", delta="+0%")

with col3:
    st.metric("Interviews Conducted", "0", delta="+0%")

with col4:
    st.metric("Avg Match Score", "0%", delta="+0%")

st.divider()

# Charts
st.subheader("📉 Trends")

# Sample chart data
dates = pd.date_range(start=start_date, end=end_date, freq='D')
chart_data = pd.DataFrame({
    'Date': dates,
    'JDs Created': np.random.randint(0, 10, len(dates)),
    'Resumes Screened': np.random.randint(0, 50, len(dates)),
    'Interviews': np.random.randint(0, 20, len(dates))
})

st.line_chart(chart_data.set_index('Date'))

st.divider()

# Top Recruiters
st.subheader("🏆 Top Performing Recruiters")

top_recruiters = pd.DataFrame({
    "Recruiter": ["Recruiter A", "Recruiter B", "Recruiter C"],
    "JDs Created": [15, 12, 10],
    "Resumes Screened": [150, 120, 100],
    "Interviews Assigned": [30, 25, 20],
    "Avg Match Score": ["85%", "82%", "80%"]
})

st.dataframe(top_recruiters, use_container_width=True, hide_index=True)

st.divider()

# Match Score Distribution
st.subheader("📊 Resume Match Score Distribution")

# Sample histogram data
scores = np.random.normal(70, 15, 100)
st.bar_chart(pd.DataFrame({'Match Score': scores}).groupby('Match Score').size())

st.info("💡 Analytics features are in development. Connect to MongoDB to see real-time data.")

