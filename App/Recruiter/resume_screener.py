"""Resume Screener - ATS System"""
import streamlit as st
import requests
import pandas as pd
from io import BytesIO

st.title("🔍 Resume Screener & Candidate Matcher")
st.write("Upload resumes and match them against job descriptions")

# API Base URL
API_BASE_URL = st.session_state.get('api_base_url', 'http://localhost:8000/api')

# Get recruiter ID from session
recruiter_id = st.session_state.get('user_id', 'default_recruiter')

# Tab selection
tab1, tab2 = st.tabs(["📤 Screen New Resumes", "📊 View Results"])

with tab1:
    st.subheader("Upload and Screen Resumes")
    
    # Step 1: Select JD
    st.write("**Step 1: Select or Enter Job Description**")
    
    jd_option = st.radio(
        "Choose how to provide the Job Description:",
        options=["Use existing JD", "Enter JD manually"],
        horizontal=True
    )
    
    jd_id = None
    jd_text = None
    
    if jd_option == "Use existing JD":
        try:
            response = requests.get(f"{API_BASE_URL}/jd/recruiter/{recruiter_id}", timeout=5)
            
            if response.status_code == 200:
                jds = response.json()
                
                if jds:
                    jd_options = {jd['job_title']: jd['id'] for jd in jds}
                    selected_jd = st.selectbox("Select Job Description", options=list(jd_options.keys()))
                    jd_id = jd_options[selected_jd]
                    st.success(f"✅ Selected JD ID: {jd_id}")
                else:
                    st.warning("No existing JDs found. Please enter JD manually or create one first.")
            else:
                st.error("Unable to fetch JDs. Please enter JD manually.")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error loading JDs: {str(e)}")
    else:
        jd_text = st.text_area(
            "Enter Job Description",
            height=200,
            placeholder="Paste the complete job description here..."
        )
    
    st.divider()
    
    # Step 2: Upload Resumes
    st.write("**Step 2: Upload Resume Files (PDF only)**")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Upload one or more resume files in PDF format"
    )
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} file(s) uploaded")
        for file in uploaded_files:
            st.write(f"- {file.name}")
    
    st.divider()
    
    # Step 3: Screen Resumes
    if st.button("🚀 Screen Resumes", type="primary", use_container_width=True):
        if not jd_id and not jd_text:
            st.error("❌ Please provide a Job Description")
        elif not uploaded_files:
            st.error("❌ Please upload at least one resume")
        else:
            with st.spinner("🤖 Screening resumes... This may take a while for multiple resumes."):
                try:
                    # Prepare files and data
                    files = [('resumes', (file.name, file, 'application/pdf')) for file in uploaded_files]
                    
                    data = {
                        'recruiter_id': recruiter_id
                    }
                    
                    if jd_id:
                        data['jd_id'] = jd_id
                    if jd_text:
                        data['jd_text'] = jd_text
                    
                    # Make API call
                    response = requests.post(
                        f"{API_BASE_URL}/resume/screen",
                        files=files,
                        data=data,
                        timeout=180
                    )
                    
                    if response.status_code == 200:
                        results = response.json()
                        st.session_state['screening_results'] = results
                        st.success(f"✅ Successfully screened {results['total_processed']} resumes!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                        
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out. Try uploading fewer resumes at once.")
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Error connecting to backend: {str(e)}")
                    st.info("Make sure the FastAPI backend is running and Ollama is accessible")

    # Display results
    if 'screening_results' in st.session_state:
        st.divider()
        st.subheader("📊 Screening Results")
        
        results = st.session_state['screening_results']
        
        if results.get('job_title'):
            st.write(f"**Position:** {results['job_title']}")
        
        st.write(f"**Total Candidates Screened:** {results['total_processed']}")
        
        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'Candidate Name': r['candidate_name'],
                'Match Score': r['match_score'],
                'Status': r['status'],
                'Summary': r['summary'][:100] + '...' if len(r['summary']) > 100 else r['summary']
            }
            for r in results['results']
        ])
        
        # Color code by status
        def color_status(val):
            if val == 'Strong Match':
                return 'background-color: #d4edda'
            elif val == 'Potential Fit':
                return 'background-color: #fff3cd'
            else:
                return 'background-color: #f8d7da'
        
        st.dataframe(
            df.style.applymap(color_status, subset=['Status']),
            use_container_width=True,
            hide_index=True
        )
        
        # Download as CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"screening_results_{results.get('job_title', 'job')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        # Detailed view
        with st.expander("👁️ View Detailed Results"):
            for r in results['results']:
                st.write(f"### {r['candidate_name']}")
                st.write(f"**Match Score:** {r['match_score']}%")
                st.write(f"**Status:** {r['status']}")
                st.write(f"**Summary:** {r['summary']}")
                st.divider()

with tab2:
    st.subheader("Previous Screening Results")
    
    try:
        response = requests.get(f"{API_BASE_URL}/resume/results/{recruiter_id}", timeout=5)
        
        if response.status_code == 200:
            all_results = response.json()
            
            if all_results:
                # Convert to DataFrame
                df_all = pd.DataFrame(all_results)
                
                st.dataframe(
                    df_all[['candidate_name', 'match_score', 'status', 'created_at']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No previous screening results found.")
        else:
            st.error("Unable to fetch previous results.")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error loading results: {str(e)}")

