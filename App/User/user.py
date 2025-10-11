"""User Dashboard - Main Page"""
import streamlit as st
import requests
from datetime import datetime

st.title("👤 User Dashboard")
st.write(f"Welcome, {st.session_state.get('user_name', 'User')}!")

# API Base URL
API_BASE_URL = st.session_state.get('api_base_url', 'http://localhost:8000/api')

# Get user ID from session
user_id = st.session_state.get('user_id', 'default_user')

st.divider()

# Assigned Interviews Section
st.subheader("🎤 Your Assigned Interviews")

try:
    response = requests.get(f"{API_BASE_URL}/interview/user/{user_id}", timeout=5)
    
    if response.status_code == 200:
        interviews = response.json()
        
        if interviews:
            # Separate interviews by status
            assigned = [i for i in interviews if i['status'] == 'Assigned']
            in_progress = [i for i in interviews if i['status'] == 'In Progress']
            completed = [i for i in interviews if i['status'] == 'Completed']
            
            # Show assigned interviews
            if assigned:
                st.write("**📋 New Interviews:**")
                for interview in assigned:
                    col1, col2, col3 = st.columns([3, 2, 2])
                    
                    with col1:
                        st.write(f"Interview ID: `{interview['id']}`")
                        st.write(f"Assigned: {interview['created_at'][:10]}")
                    
                    with col2:
                        st.write(f"Status: {interview['status']}")
                    
                    with col3:
                        if st.button("▶️ Start Interview", key=f"start_{interview['id']}", use_container_width=True):
                            st.session_state['current_interview_id'] = interview['id']
                            st.switch_page("User/ai_interview.py")
                    
                    st.divider()
            
            # Show in-progress interviews
            if in_progress:
                st.write("**⏳ In Progress:**")
                for interview in in_progress:
                    col1, col2, col3 = st.columns([3, 2, 2])
                    
                    with col1:
                        st.write(f"Interview ID: `{interview['id']}`")
                        st.write(f"Started: {interview.get('started_at', 'N/A')[:10]}")
                    
                    with col2:
                        st.write(f"Status: {interview['status']}")
                    
                    with col3:
                        if st.button("▶️ Continue", key=f"continue_{interview['id']}", use_container_width=True):
                            st.session_state['current_interview_id'] = interview['id']
                            st.switch_page("User/ai_interview.py")
                    
                    st.divider()
            
            # Show completed interviews
            if completed:
                st.write("**✅ Completed Interviews:**")
                for interview in completed:
                    col1, col2, col3 = st.columns([3, 2, 2])
                    
                    with col1:
                        st.write(f"Interview ID: `{interview['id']}`")
                        st.write(f"Completed: {interview.get('completed_at', 'N/A')[:10]}")
                    
                    with col2:
                        st.write(f"Status: {interview['status']}")
                    
                    with col3:
                        if st.button("📊 View Summary", key=f"summary_{interview['id']}", use_container_width=True):
                            st.session_state['view_interview_id'] = interview['id']
                            # Show summary in expander below
                    
                    st.divider()
        else:
            st.info("No interviews assigned yet. Your recruiter will assign interviews when available.")
    else:
        st.error("Unable to fetch interviews. Please try again later.")
        
except requests.exceptions.RequestException as e:
    st.error(f"❌ Error connecting to backend: {str(e)}")
    st.info("Make sure the FastAPI backend is running on http://localhost:8000")

st.divider()

# Quick Stats
st.subheader("📊 Your Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Interviews",
        value=len(interviews) if 'interviews' in locals() else 0
    )

with col2:
    st.metric(
        label="Completed",
        value=len(completed) if 'completed' in locals() else 0
    )

with col3:
    st.metric(
        label="Pending",
        value=len(assigned) if 'assigned' in locals() else 0
    )

st.divider()

# Tips for candidates
with st.expander("💡 Tips for Your Interview"):
    st.markdown("""
    ### Preparing for Your AI Interview
    
    1. **Find a Quiet Space**: Ensure you're in a quiet environment if voice is enabled
    2. **Be Specific**: Provide detailed answers with examples from your experience
    3. **Take Your Time**: Think through your responses before answering
    4. **Be Honest**: The AI is designed to assess your actual skills and experience
    
    ### During the Interview
    
    - Answer each question thoroughly
    - Use the STAR method (Situation, Task, Action, Result) for behavioral questions
    - Don't hesitate to ask for clarification if needed
    - Be professional and concise
    
    ### After the Interview
    
    - Your responses are evaluated immediately
    - A summary will be generated at the end
    - The recruiter will review your performance
    - You may be contacted for next steps
    """)

