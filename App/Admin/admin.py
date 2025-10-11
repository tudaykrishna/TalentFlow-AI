"""Admin Dashboard - Main Page"""
import streamlit as st
import requests

st.title("⚙️ Admin Dashboard")
st.write(f"Welcome, Administrator {st.session_state.get('user_name', 'Admin')}!")

# API Base URL
API_BASE_URL = st.session_state.get('api_base_url', 'http://localhost:8000/api')

st.divider()

# System Overview
st.subheader("📊 System Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Users",
        value="0",
        delta="0 new"
    )

with col2:
    st.metric(
        label="Active Recruiters",
        value="0",
        delta="0 active"
    )

with col3:
    st.metric(
        label="Job Descriptions",
        value="0",
        delta="0 this week"
    )

with col4:
    st.metric(
        label="Total Interviews",
        value="0",
        delta="0 ongoing"
    )

st.divider()

# System Health
st.subheader("🏥 System Health")

try:
    response = requests.get("http://localhost:8000/health", timeout=5)
    
    if response.status_code == 200:
        health_data = response.json()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success("✅ Backend API: Running")
        
        with col2:
            db_status = health_data.get('database', 'unknown')
            if db_status == 'connected':
                st.success("✅ MongoDB: Connected")
            else:
                st.error("❌ MongoDB: Disconnected")
    else:
        st.error("❌ Backend API: Not responding")
        
except requests.exceptions.RequestException:
    st.error("❌ Backend API: Offline")


# Quick Actions
st.subheader("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("👥 Manage Users", use_container_width=True, type="primary"):
        st.info("User management feature - Coming soon!")

with col2:
    if st.button("📊 View Analytics", use_container_width=True, type="primary"):
        st.info("Analytics dashboard - Coming soon!")

with col3:
    if st.button("⚙️ System Settings", use_container_width=True, type="primary"):
        st.switch_page("settings.py")

st.divider()

# Recent Activity
st.subheader("🕐 Recent System Activity")

# Show recent JDs
try:
    response = requests.get(f"{API_BASE_URL}/jd/all", timeout=5)
    
    if response.status_code == 200:
        jds = response.json()
        
        if jds:
            st.write("**Recent Job Descriptions:**")
            for jd in jds[:5]:
                col1, col2, col3 = st.columns([2, 4, 3])
                
                with col1:
                    st.write(jd['created_at'][:10])
                
                with col2:
                    st.write(f"JD: {jd['job_title']}")
                
                with col3:
                    st.write(f"ID: {jd['id'][:8]}...")
        else:
            st.info("No recent activity")
    else:
        st.warning("Unable to fetch recent activity")
        
except requests.exceptions.RequestException as e:
    st.error(f"Error: {str(e)}")

st.divider()

# System Configuration
with st.expander("⚙️ System Configuration"):
    st.markdown("""
    ### Configuration Settings
    
    - **MongoDB URI**: Check .env file
    - **Azure OpenAI**: Configured for JD generation and interviews
    - **Ollama Model**: Used for resume screening
    - **Max File Upload**: 10MB per resume
    - **Session Timeout**: 30 minutes
    
    ### Maintenance
    
    - Database backup: Automated daily
    - Log retention: 30 days
    - API rate limiting: Configured
    """)

# Database Management
with st.expander("💾 Database Management"):
    st.write("**Collections:**")
    st.write("- users")
    st.write("- recruiters")
    st.write("- jds (Job Descriptions)")
    st.write("- resumes")
    st.write("- interviews")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 View Collection Stats", use_container_width=True):
            st.info("Collection statistics - Coming soon!")
    
    with col2:
        if st.button("🔄 Refresh Database", use_container_width=True):
            st.info("Database refresh - Coming soon!")
