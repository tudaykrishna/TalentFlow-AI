"""Interview Results - View Completed Interview Results"""
import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.title("📊 Interview Results")
st.write("View completed interview results and candidate performance")

# API Base URL
API_BASE_URL = st.session_state.get('api_base_url', 'http://localhost:8000/api')

# Get recruiter ID from session
recruiter_id = st.session_state.get('user_id', 'default_recruiter')

# Fetch interview results
try:
    response = requests.get(f"{API_BASE_URL}/interview/recruiter/{recruiter_id}/results", timeout=10)
    
    if response.status_code == 200:
        results = response.json()
        
        if results:
            st.subheader(f"📋 Completed Interviews ({len(results)})")
            
            # Create DataFrame for overview
            df_data = []
            for result in results:
                df_data.append({
                    "Candidate": result.get("candidate_name", "Unknown"),
                    "Username": result.get("candidate_username", "N/A"),
                    "Job Title": result.get("job_title", "Unknown"),
                    "Avg Score": f"{result.get('average_score', 0):.1f}/5",
                    "Questions": result.get("total_questions", 0),
                    "Recommendation": result.get("recommendation", "N/A"),
                    "Completed": result.get("completed_at", "N/A")[:10] if result.get("completed_at") else "N/A"
                })
            
            df = pd.DataFrame(df_data)
            
            # Display summary table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Candidate": st.column_config.TextColumn("Candidate Name", width="medium"),
                    "Username": st.column_config.TextColumn("Username", width="medium"),
                    "Job Title": st.column_config.TextColumn("Position", width="medium"),
                    "Avg Score": st.column_config.TextColumn("Avg Score", width="small"),
                    "Questions": st.column_config.NumberColumn("Questions", width="small"),
                    "Recommendation": st.column_config.TextColumn("Recommendation", width="small"),
                    "Completed": st.column_config.TextColumn("Date", width="small")
                }
            )
            
            st.divider()
            
            # Detailed view for each candidate
            st.subheader("📝 Detailed Interview Results")
            
            for result in results:
                with st.expander(f"👤 {result.get('candidate_name', 'Unknown')} - {result.get('job_title', 'Unknown')}"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Average Score", f"{result.get('average_score', 0):.1f}/5")
                    
                    with col2:
                        recommendation = result.get("recommendation", "N/A")
                        if recommendation == "Proceed":
                            st.success(f"✅ {recommendation}")
                        elif recommendation == "Hold":
                            st.warning(f"⏸️ {recommendation}")
                        else:
                            st.error(f"❌ {recommendation}")
                    
                    with col3:
                        st.write(f"**Completed:** {result.get('completed_at', 'N/A')[:10] if result.get('completed_at') else 'N/A'}")
                    
                    st.divider()
                    
                    # Get full interview details
                    interview_id = result.get("interview_id")
                    if interview_id:
                        try:
                            detail_response = requests.get(f"{API_BASE_URL}/interview/{interview_id}/summary", timeout=5)
                            
                            if detail_response.status_code == 200:
                                details = detail_response.json()
                                
                                # Display final summary
                                final_summary = details.get("final_summary", {})
                                st.subheader("📄 Summary")
                                st.write(final_summary.get("summary_text", "No summary available"))
                                
                                st.divider()
                                
                                # Display Q&A and evaluations
                                st.subheader("💬 Questions & Answers")
                                conversation = details.get("conversation_history", [])
                                evaluations = details.get("evaluations", [])
                                
                                for i, qa in enumerate(conversation):
                                    st.write(f"**Q{i+1}:** {qa.get('question', 'N/A')}")
                                    st.write(f"**A:** {qa.get('answer', 'N/A')}")
                                    
                                    if i < len(evaluations):
                                        eval_data = evaluations[i]
                                        rating = eval_data.get('rating', 0)
                                        
                                        # Display rating with color
                                        if rating >= 4:
                                            st.success(f"⭐ Rating: {rating}/5 - {eval_data.get('feedback', 'N/A')}")
                                        elif rating >= 3:
                                            st.info(f"⭐ Rating: {rating}/5 - {eval_data.get('feedback', 'N/A')}")
                                        else:
                                            st.warning(f"⭐ Rating: {rating}/5 - {eval_data.get('feedback', 'N/A')}")
                                    
                                    st.divider()
                            else:
                                st.error("Unable to load interview details")
                                
                        except requests.exceptions.RequestException as e:
                            st.error(f"Error loading details: {str(e)}")
        else:
            st.info("📭 No completed interviews yet. Assign interviews to candidates to get started!")
            
            if st.button("➕ Assign New Interview", type="primary"):
                st.switch_page("Recruiter/interview_assignment.py")
    else:
        st.error("❌ Unable to fetch interview results")
        st.write(f"Status Code: {response.status_code}")
        
except requests.exceptions.RequestException as e:
    st.error(f"❌ Error connecting to backend: {str(e)}")
    st.info("Make sure the FastAPI backend is running on http://localhost:8000")

st.divider()

# Filter and export options
with st.expander("⚙️ Advanced Options"):
    st.write("**Filter by:**")
    col1, col2 = st.columns(2)
    
    with col1:
        filter_recommendation = st.multiselect(
            "Recommendation",
            options=["Proceed", "Hold", "Reject"],
            default=["Proceed", "Hold", "Reject"]
        )
    
    with col2:
        min_score = st.slider("Minimum Score", 0.0, 5.0, 0.0, 0.5)
    
    st.info("Note: Filtering functionality will be implemented in the next update")

st.divider()

# Navigation
col1, col2 = st.columns(2)

with col1:
    if st.button("← Back to Dashboard", use_container_width=True):
        st.switch_page("Recruiter/recruiter.py")

with col2:
    if st.button("➕ Assign New Interview", use_container_width=True, type="primary"):
        st.switch_page("Recruiter/interview_assignment.py")

