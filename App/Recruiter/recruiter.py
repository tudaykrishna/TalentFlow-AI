"""Recruiter Dashboard - Main Page"""
import streamlit as st
import requests
from datetime import datetime


st.title("📊 Recruiter Dashboard")
st.write(f"Welcome, {st.session_state.get('user_name', 'Recruiter')}!")

# API Base URL
API_BASE_URL = st.session_state.get('api_base_url', 'http://localhost:8000/api')

# Dashboard metrics
st.subheader("📈 Quick Stats")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Job Descriptions",
        value="0",
        delta="0 this month"
    )

with col2:
    st.metric(
        label="Resumes Screened",
        value="0",
        delta="0 this week"
    )

with col3:
    st.metric(
        label="Active Interviews",
        value="0",
        delta="0 pending"
    )

st.divider()

# Recent Activity
st.subheader("🕐 Recent Activity")

# Get recruiter ID from session
recruiter_id = st.session_state.get('user_id', 'default_recruiter')

try:
    # Fetch recent JDs - try recruiter-specific first, then all
    response = requests.get(f"{API_BASE_URL}/jd/recruiter/{recruiter_id}", timeout=5)
    
    if response.status_code == 200:
        jds = response.json()
        
        # If no JDs for this recruiter, fetch all JDs
        if not jds:
            response_all = requests.get(f"{API_BASE_URL}/jd/all", timeout=5)
            if response_all.status_code == 200:
                jds = response_all.json()
                if jds:
                    st.info("ℹ️ Showing all job descriptions (including ones from other recruiters)")
        
        if jds:
            st.write("**Recent Job Descriptions:**")
            for jd in jds[:5]:
                with st.expander(f"📄 {jd['job_title']} - {jd['created_at'][:10]}"):
                    st.write(f"**ID:** {jd['id']}")
                    st.write(f"**Created:** {jd['created_at']}")
                    if jd.get('pdf_path'):
                        st.write(f"**PDF:** [Download]({jd['pdf_path']})")
        else:
            st.info("No job descriptions created yet. Start by creating your first JD!")
    else:
        st.warning("Unable to fetch recent activity. Please check your connection.")
        
except requests.exceptions.RequestException as e:
    st.error(f"❌ Error connecting to backend: {str(e)}")
    st.info("Make sure the FastAPI backend is running on http://localhost:8000")

st.divider()


# Quick Actions
st.subheader("⚡ Quick Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("📝 Create New JD", use_container_width=True, type="primary"):
        st.switch_page("Recruiter/jd_generator.py")

with col2:
    if st.button("🔍 Screen Resumes", use_container_width=True, type="primary"):
        st.switch_page("Recruiter/resume_screener.py")

col3, col4 = st.columns(2)

with col3:
    if st.button("🎤 Assign Interview", use_container_width=True, type="primary"):
        st.switch_page("Recruiter/interview_assignment.py")

with col4:
    if st.button("📊 View Interview Results", use_container_width=True, type="primary"):
        st.switch_page("Recruiter/interview_results.py")

st.divider()

# Tips and Help
with st.expander("💡 Tips for Recruiters"):
    st.markdown("""
    ### Getting Started
    
    1. **Create a Job Description**: Use the JD Generator to create professional job descriptions based on keywords.
    2. **Screen Candidates**: Upload multiple resumes and get AI-powered matching scores against your JD.
    3. **Assign Interviews**: Select top candidates and assign them AI-powered screening interviews.
    
    ### Best Practices
    
    - Be specific when creating job descriptions
    - Upload resumes in PDF format for best results
    - Review AI screening results before making final decisions
    - Monitor interview progress regularly
    """)

