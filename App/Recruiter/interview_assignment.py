"""Interview Assignment - Assign AI Interviews to Candidates"""
import streamlit as st
import requests
from datetime import datetime

st.title("🎤 AI Interview Assignment")
st.write("Assign AI-powered screening interviews to candidates")

# API Base URL
API_BASE_URL = st.session_state.get('api_base_url', 'http://localhost:8000/api')

# Get recruiter ID from session
recruiter_id = st.session_state.get('user_id', 'default_recruiter')

# Form for interview assignment
with st.form("interview_assignment_form"):
    st.subheader("Assign Interview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Select JD
        st.write("**Select Job Description**")
        try:
            response = requests.get(f"{API_BASE_URL}/jd/recruiter/{recruiter_id}", timeout=5)
            
            if response.status_code == 200:
                jds = response.json()
                
                # If no JDs for this recruiter, fetch all JDs
                if not jds:
                    response_all = requests.get(f"{API_BASE_URL}/jd/all", timeout=5)
                    if response_all.status_code == 200:
                        jds = response_all.json()
                
                if jds:
                    jd_options = {f"{jd['job_title']} ({jd['created_at'][:10]})": jd['id'] for jd in jds}
                    selected_jd = st.selectbox("Job Description", options=list(jd_options.keys()))
                    jd_id = jd_options[selected_jd]
                else:
                    st.warning("No JDs found. Please create a JD first.")
                    jd_id = None
            else:
                st.error("Unable to fetch JDs.")
                jd_id = None
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error loading JDs: {str(e)}")
            jd_id = None
    
    with col2:
        # Candidate Details
        st.write("**Candidate Details**")
        candidate_name = st.text_input(
            "Full Name",
            placeholder="e.g., John Doe",
            help="Enter the candidate's full name"
        )
        candidate_username = st.text_input(
            "Username/Email",
            placeholder="e.g., john.doe or john@example.com",
            help="Enter a username or email for the candidate to login"
        )
    
    max_questions = st.slider(
        "Number of Interview Questions",
        min_value=3,
        max_value=10,
        value=5,
        help="Select how many questions the AI should ask"
    )
    
    st.divider()
    
    submitted = st.form_submit_button("📤 Assign Interview", type="primary", use_container_width=True)
    
    if submitted:
        if not jd_id:
            st.error("❌ Please select a Job Description")
        elif not candidate_name or not candidate_name.strip():
            st.error("❌ Please enter candidate's full name")
        elif not candidate_username or not candidate_username.strip():
            st.error("❌ Please enter candidate's username/email")
        else:
            with st.spinner("Assigning interview and creating candidate account..."):
                try:
                    payload = {
                        "candidate_name": candidate_name.strip(),
                        "candidate_username": candidate_username.strip(),
                        "jd_id": jd_id,
                        "recruiter_id": recruiter_id,
                        "max_questions": max_questions
                    }
                    
                    response = requests.post(
                        f"{API_BASE_URL}/interview/assign",
                        json=payload,
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        result = response.json()
                        credentials = result.get("candidate_credentials", {})
                        
                        st.success(f"✅ Interview assigned successfully to {credentials.get('name', 'candidate')}!")
                        
                        # Display credentials prominently
                        st.divider()
                        st.subheader("🔑 Candidate Login Credentials")
                        st.info(credentials.get("message", "Share these credentials with the candidate"))
                        
                        col_email, col_pass = st.columns(2)
                        with col_email:
                            st.text_input("Email/Username", value=credentials.get("email", ""), disabled=True, key="cred_email")
                        with col_pass:
                            st.text_input("Password", value=credentials.get("password", ""), type="default", disabled=True, key="cred_pass")
                        
                        st.warning(f"⚠️ Valid for: {credentials.get('valid_for', '24 hours')} | One-time use only")
                        
                        # Copy button alternatives
                        st.code(f"Name: {credentials.get('name', '')}\nEmail: {credentials.get('email', '')}\nPassword: {credentials.get('password', '')}", language=None)
                        
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                        
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Error connecting to backend: {str(e)}")

st.divider()

# View assigned interviews
st.subheader("📋 Recently Assigned Interviews")

# Mock data for now - in production, fetch from backend
try:
    # You can implement an endpoint to get interviews by recruiter_id
    st.info("Viewing assigned interviews - Feature coming soon!")
    
    # Example display
    example_data = [
        {"Candidate ID": "user_001", "Job Title": "Senior Backend Engineer", "Status": "Assigned", "Date": "2024-01-15"},
        {"Candidate ID": "user_002", "Job Title": "Python Developer", "Status": "In Progress", "Date": "2024-01-14"},
        {"Candidate ID": "user_003", "Job Title": "Senior Backend Engineer", "Status": "Completed", "Date": "2024-01-13"},
    ]
    
    import pandas as pd
    df = pd.DataFrame(example_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
except Exception as e:
    st.error(f"Error loading interviews: {str(e)}")

st.divider()

# Instructions
with st.expander("📖 How It Works"):
    st.markdown("""
    ### AI Interview Assignment Process
    
    1. **Select a Job Description**: Choose the position for which you want to conduct interviews
    2. **Enter Candidate ID**: Provide the user ID of the candidate
    3. **Set Number of Questions**: Choose how comprehensive the interview should be
    4. **Assign**: The candidate will be notified and can start the interview from their dashboard
    
    ### Interview Features
    
    - **Adaptive Questioning**: AI adjusts follow-up questions based on candidate responses
    - **Automatic Evaluation**: Each answer is evaluated and rated
    - **Final Summary**: Complete summary with hiring recommendation after interview completion
    - **Conversation History**: Full transcript available for review
    
    ### Best Practices
    
    - Assign 5-7 questions for initial screening
    - Review AI recommendations but make final decisions yourself
    - Provide candidates with clear instructions before the interview
    """)

