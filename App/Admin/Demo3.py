"""System Logs - Admin Panel"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.title("📝 System Logs")
st.write("View and monitor system activity logs")

st.divider()

# Log filters
col1, col2, col3 = st.columns(3)

with col1:
    log_level = st.selectbox("Log Level", ["All", "INFO", "WARNING", "ERROR", "DEBUG"])

with col2:
    log_source = st.selectbox("Source", ["All", "Backend", "Frontend", "Database", "AI Services"])

with col3:
    time_range = st.selectbox("Time Range", ["Last Hour", "Last 24 Hours", "Last 7 Days", "Last 30 Days"])

st.divider()

# Refresh button
col1, col2 = st.columns([1, 4])

with col1:
    if st.button("🔄 Refresh Logs", use_container_width=True):
        st.rerun()

st.divider()

# Sample logs
st.subheader("📋 Recent Logs")

# Generate sample log data
sample_logs = []
for i in range(20):
    timestamp = datetime.now() - timedelta(minutes=i*5)
    levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
    sources = ["Backend API", "MongoDB", "Azure OpenAI", "Streamlit"]
    messages = [
        "User login successful",
        "JD generation completed",
        "Resume screening started",
        "Interview assigned",
        "Database connection established",
        "API endpoint called",
        "File uploaded successfully",
        "Cache cleared"
    ]
    
    sample_logs.append({
        "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "Level": levels[i % 4],
        "Source": sources[i % 4],
        "Message": messages[i % 8]
    })

logs_df = pd.DataFrame(sample_logs)

# Color code log levels
def color_level(val):
    if val == 'ERROR':
        return 'background-color: #f8d7da'
    elif val == 'WARNING':
        return 'background-color: #fff3cd'
    elif val == 'INFO':
        return 'background-color: #d4edda'
    else:
        return ''

st.dataframe(
    logs_df.style.applymap(color_level, subset=['Level']),
    use_container_width=True,
    hide_index=True,
    height=600
)

st.divider()

# Log statistics
st.subheader("📊 Log Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Logs", "1,234", delta="+45 today")

with col2:
    st.metric("Errors", "5", delta="-2 vs yesterday")

with col3:
    st.metric("Warnings", "23", delta="+3 vs yesterday")

with col4:
    st.metric("Info", "1,206", delta="+44 today")

st.divider()

# Export logs
col1, col2 = st.columns([1, 4])

with col1:
    if st.button("📥 Export Logs", type="primary", use_container_width=True):
        csv = logs_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

st.info("💡 System logs are sample data. Connect to actual logging system for real-time logs.")

