"""Job Description Generator"""
import streamlit as st
import requests
import json

st.title("📝 Job Description Generator")
st.write("Generate professional job descriptions using AI")

# API Base URL
API_BASE_URL = st.session_state.get('api_base_url', 'http://localhost:8000/api')

# Get recruiter ID from session
recruiter_id = st.session_state.get('user_id', 'default_recruiter')

# Form for JD generation
with st.form("jd_generation_form"):
    st.subheader("Job Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        job_title = st.text_input(
            "Job Title *",
            placeholder="e.g., Senior Backend Engineer",
            help="Enter the position title"
        )
        
        experience = st.text_input(
            "Years of Experience *",
            placeholder="e.g., 5-7",
            help="Required years of experience"
        )
    
    with col2:
        company_tone = st.selectbox(
            "Company Tone *",
            options=[
                "Professional yet approachable",
                "Formal and corporate",
                "Casual and friendly",
                "Innovative and dynamic",
                "Traditional and established"
            ],
            help="Select the tone for your job description"
        )
    
    st.divider()
    
    responsibilities = st.text_area(
        "Key Responsibilities *",
        placeholder="Design and build scalable APIs, database management, mentor junior engineers, lead code reviews, collaborate with frontend teams",
        height=100,
        help="List the main responsibilities of the role"
    )
    
    skills = st.text_area(
        "Required Skills *",
        placeholder="Python, FastAPI, SQL (PostgreSQL), Docker, Kubernetes, AWS, CI/CD",
        height=100,
        help="List the technical and soft skills required"
    )
    
    st.divider()
    
    submitted = st.form_submit_button("🚀 Generate Job Description", type="primary", use_container_width=True)
    
    if submitted:
        # Validate inputs
        if not all([job_title, experience, responsibilities, skills]):
            st.error("❌ Please fill in all required fields marked with *")
        else:
            with st.spinner("🤖 Generating job description... This may take a moment."):
                try:
                    # Prepare request
                    payload = {
                        "job_title": job_title,
                        "company_tone": company_tone,
                        "responsibilities": responsibilities,
                        "skills": skills,
                        "experience": experience,
                        "recruiter_id": recruiter_id
                    }
                    
                    # Make API call
                    response = requests.post(
                        f"{API_BASE_URL}/jd/generate",
                        json=payload,
                        timeout=60
                    )
                    
                    if response.status_code == 201:
                        result = response.json()
                        st.session_state['generated_jd'] = result
                        st.success("✅ Job Description generated successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                        
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out. The AI model might be busy. Please try again.")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Error connecting to backend: {str(e)}")
                    st.info("Make sure the FastAPI backend is running on http://localhost:8000")

# Display generated JD
if 'generated_jd' in st.session_state:
    st.divider()
    st.subheader("📄 Generated Job Description")
    
    jd_data = st.session_state['generated_jd']
    
    # Display content
    st.markdown(jd_data['generated_content'])
    
    st.divider()
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Download PDF", type="primary", use_container_width=True):
            if jd_data.get('pdf_path'):
                st.info(f"PDF saved at: {jd_data['pdf_path']}")
                # In production, implement actual file download
            else:
                st.warning("PDF path not available")
    
    with col2:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            st.code(jd_data['generated_content'], language="markdown")
            st.info("Content displayed above. Copy manually or use your browser's copy function.")
    
    with col3:
        if st.button("🆕 Generate New JD", use_container_width=True):
            del st.session_state['generated_jd']
            st.rerun()

st.divider()

# View previous JDs
with st.expander("📚 View Previous Job Descriptions"):
    try:
        response = requests.get(f"{API_BASE_URL}/jd/recruiter/{recruiter_id}", timeout=5)
        
        if response.status_code == 200:
            jds = response.json()
            
            if jds:
                for jd in jds:
                    st.write(f"**{jd['job_title']}** - Created: {jd['created_at'][:10]}")
                    st.write(f"ID: `{jd['id']}`")
                    if jd.get('pdf_path'):
                        st.write(f"[View PDF]({jd['pdf_path']})")
                    st.divider()
            else:
                st.info("No previous job descriptions found.")
        else:
            st.error("Unable to fetch previous JDs.")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading previous JDs: {str(e)}")

