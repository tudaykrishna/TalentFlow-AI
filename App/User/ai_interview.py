"""AI Interview Interface"""
import streamlit as st
import requests
import json
import io
from audio_recorder_streamlit import audio_recorder

st.title("🎤 AI Interview")

# API Base URL
API_BASE_URL = st.session_state.get('api_base_url', 'http://localhost:8000/api')

# Get interview ID from session
interview_id = st.session_state.get('current_interview_id')

if not interview_id:
    st.error("❌ No interview selected. Please go back to your dashboard.")
    if st.button("← Back to Dashboard"):
        st.switch_page("User/user.py")
    st.stop()

# Get interview status
try:
    response = requests.get(f"{API_BASE_URL}/interview/{interview_id}/status", timeout=5)
    
    if response.status_code == 200:
        status_data = response.json()
        
        st.write(f"**Interview ID:** `{interview_id}`")
        st.write(f"**Status:** {status_data['status']}")
        
        # Progress bar
        if status_data['total_questions'] > 0:
            progress = status_data['questions_completed'] / status_data['total_questions']
            st.progress(progress)
            
            # Show current question number only if interview is in progress
            if status_data['status'] == 'In Progress':
                current_question_num = status_data['questions_completed'] + 1
                st.write(f"Question {current_question_num} of {status_data['total_questions']}")
            else:
                st.write(f"Questions Completed: {status_data['questions_completed']} of {status_data['total_questions']}")
        
        st.divider()
        
        # If interview is completed
        if status_data['status'] == 'Completed':
            st.success("✅ Interview Completed!")
            
            # Fetch summary
            try:
                summary_response = requests.get(f"{API_BASE_URL}/interview/{interview_id}/summary", timeout=5)
                
                if summary_response.status_code == 200:
                    summary_data = summary_response.json()
                    
                    st.subheader("📊 Interview Summary")
                    
                    final_summary = summary_data.get('final_summary', {})
                    
                    # Display recommendation
                    recommendation = final_summary.get('recommendation', 'Unknown')
                    
                    if recommendation == 'Proceed':
                        st.success(f"**Recommendation:** {recommendation} ✅")
                    elif recommendation == 'Hold':
                        st.warning(f"**Recommendation:** {recommendation} ⏸️")
                    else:
                        st.error(f"**Recommendation:** {recommendation} ❌")
                    
                    st.write("**Summary:**")
                    st.write(final_summary.get('summary_text', 'No summary available'))
                    
                    st.divider()
                    
                    # Show conversation history
                    with st.expander("📝 View Full Interview Transcript"):
                        conversation = summary_data.get('conversation_history', [])
                        evaluations = summary_data.get('evaluations', [])
                        
                        for i, qa in enumerate(conversation):
                            st.write(f"**Q{i+1}:** {qa['question']}")
                            st.write(f"**A:** {qa['answer']}")
                            
                            if i < len(evaluations):
                                eval_data = evaluations[i]
                                st.write(f"*Rating: {eval_data.get('rating', 'N/A')}/5*")
                                st.write(f"*Feedback: {eval_data.get('feedback', 'N/A')}*")
                            
                            st.divider()
                else:
                    st.error("Unable to fetch interview summary.")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Error fetching summary: {str(e)}")
            
            if st.button("← Back to Dashboard", type="primary"):
                if 'current_interview_id' in st.session_state:
                    del st.session_state['current_interview_id']
                st.switch_page("User/user.py")
            
        # If interview is assigned but not started
        elif status_data['status'] == 'Assigned':
            st.info("📋 Please configure your interview preferences and upload your resume before starting.")
            
            st.divider()
            
            # Interview Configuration Section
            st.subheader("⚙️ Interview Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Interviewer Communication")
                interviewer_mode = st.radio(
                    "How would you like to receive questions?",
                    options=["Text", "Audio"],
                    index=0,
                    help="Choose how the interviewer will present questions to you",
                    key="interviewer_mode"
                )
            
            with col2:
                st.markdown("##### Your Response Method")
                user_mode = st.radio(
                    "How would you like to respond?",
                    options=["Text", "Audio"],
                    index=0,
                    help="Choose how you want to provide your answers",
                    key="user_mode"
                )
            
            st.divider()
            
            # Resume Upload Section
            st.subheader("📄 Upload Your Resume")
            st.markdown("Upload your resume so we can ask personalized questions based on your experience.")
            
            uploaded_resume = st.file_uploader(
                "Choose your resume (PDF)",
                type=["pdf"],
                help="Upload your resume in PDF format",
                key="resume_upload"
            )
            
            if uploaded_resume:
                st.success(f"✅ Resume uploaded: {uploaded_resume.name}")
            
            st.divider()
            
            # Start button
            if st.button("🚀 Start Interview", type="primary", use_container_width=True, disabled=not uploaded_resume):
                if not uploaded_resume:
                    st.error("❌ Please upload your resume before starting the interview.")
                else:
                    with st.spinner("Uploading resume and starting interview..."):
                        try:
                            # First upload the resume
                            files = {"resume_file": (uploaded_resume.name, uploaded_resume.getvalue(), "application/pdf")}
                            data = {
                                "interviewer_mode": interviewer_mode,
                                "user_mode": user_mode
                            }
                            
                            upload_response = requests.post(
                                f"{API_BASE_URL}/interview/{interview_id}/upload-resume",
                                files=files,
                                data=data,
                                timeout=30
                            )
                            
                            if upload_response.status_code == 200:
                                st.success("✅ Resume uploaded successfully!")
                                
                                # Now start the interview
                                start_response = requests.post(
                                    f"{API_BASE_URL}/interview/{interview_id}/start",
                                    timeout=10
                                )
                                
                                if start_response.status_code == 200:
                                    st.success("✅ Interview started!")
                                    st.rerun()
                                else:
                                    st.error(f"Error starting interview: {start_response.json().get('detail', 'Unknown error')}")
                            else:
                                st.error(f"Error uploading resume: {upload_response.json().get('detail', 'Unknown error')}")
                                
                        except requests.exceptions.RequestException as e:
                            st.error(f"Error: {str(e)}")
            
            if not uploaded_resume:
                st.warning("⚠️ Please upload your resume to enable the Start Interview button.")
        
        # If interview is in progress
        elif status_data['status'] == 'In Progress':
            current_question = status_data.get('current_question')
            
            if current_question:
                st.subheader("Current Question")
                
                # Get interview details to check mode
                interview_details_response = requests.get(
                    f"{API_BASE_URL}/interview/{interview_id}/details",
                    timeout=5
                )
                
                interviewer_mode = "Text"
                user_mode = "Text"
                
                if interview_details_response.status_code == 200:
                    interview_details = interview_details_response.json()
                    interviewer_mode = interview_details.get('interviewer_mode', 'Text')
                    user_mode = interview_details.get('user_mode', 'Text')
                
                # Display question text
                st.info(current_question)
                
                # Always show "Play Audio" button (works regardless of mode)
                st.markdown("---")
                col_audio, col_space = st.columns([1, 3])
                with col_audio:
                    if st.button("🔊 Play Question as Audio", type="secondary", use_container_width=True):
                        with st.spinner("Generating audio..."):
                            try:
                                tts_response = requests.post(
                                    f"{API_BASE_URL}/interview/tts/generate",
                                    params={"text": current_question},
                                    timeout=30
                                )
                                
                                if tts_response.status_code == 200:
                                    tts_data = tts_response.json()
                                    audio_path = tts_data.get('audio_path')
                                    
                                    # Display audio player
                                    audio_url = f"http://localhost:8000/{audio_path}"
                                    st.audio(audio_url, format='audio/mp3', autoplay=True)
                                    st.success("✅ Audio playing!")
                                else:
                                    error_detail = tts_response.json().get('detail', 'Unknown error')
                                    st.error(f"❌ Could not generate audio: {error_detail}")
                                    
                            except Exception as e:
                                st.error(f"❌ Audio generation error: {str(e)}")
                
                st.markdown("---")
                
                # Show mode indicators
                col1, col2 = st.columns(2)
                with col1:
                    st.caption(f"📢 Interviewer: {interviewer_mode}")
                with col2:
                    st.caption(f"🎤 Your Response: {user_mode}")
            
            # Answer form - Voice or Text based on user preference
            st.subheader("📝 Provide Your Answer")
            
            # Get interview details to check user mode
            interview_details_response = requests.get(
                f"{API_BASE_URL}/interview/{interview_id}/details",
                timeout=5
            )
            
            user_mode = "Text"
            if interview_details_response.status_code == 200:
                interview_details = interview_details_response.json()
                user_mode = interview_details.get('user_mode', 'Text')
            
            # Tab selection for input method - default based on user_mode
            if user_mode == "Audio":
                input_tab2, input_tab1 = st.tabs(["🎙️ Voice Answer (Preferred)", "✍️ Type Answer"])
            else:
                input_tab1, input_tab2 = st.tabs(["✍️ Type Answer (Preferred)", "🎙️ Voice Answer"])
            
            answer_text = ""
            
            with input_tab1:
                with st.form("answer_form_text", clear_on_submit=True):
                    answer_text = st.text_area(
                        "Your Answer:",
                        height=150,
                        placeholder="Type your answer here...",
                        help="Provide a detailed answer. Use examples from your experience.",
                        key="text_answer"
                    )
                    
                    submitted_text = st.form_submit_button("Submit Text Answer", type="primary", use_container_width=True)
                    
                    if submitted_text:
                        if not answer_text.strip():
                            st.error("❌ Please provide an answer before submitting.")
                        else:
                            with st.spinner("Evaluating your answer..."):
                                try:
                                    answer_response = requests.post(
                                        f"{API_BASE_URL}/interview/{interview_id}/answer",
                                        params={"answer": answer_text},
                                        timeout=30
                                    )
                                    
                                    if answer_response.status_code == 200:
                                        result = answer_response.json()
                                        
                                        if result['status'] == 'Completed':
                                            st.success("✅ Interview completed! Generating summary...")
                                        else:
                                            st.success("✅ Answer submitted!")
                                            
                                            # Show evaluation if available
                                            if 'evaluation' in result:
                                                eval_data = result['evaluation']
                                                st.write(f"**Rating:** {eval_data.get('rating', 'N/A')}/5")
                                                st.write(f"**Feedback:** {eval_data.get('feedback', 'N/A')}")
                                        
                                        st.rerun()
                                    else:
                                        st.error(f"Error: {answer_response.json().get('detail', 'Unknown error')}")
                                        
                                except requests.exceptions.RequestException as e:
                                    st.error(f"Error submitting answer: {str(e)}")
            
            with input_tab2:
                st.info("🎤 Click the microphone button below to record your answer")
                
                # Audio recorder
                audio_bytes = audio_recorder(
                    text="Click to record",
                    recording_color="#e74c3c",
                    neutral_color="#3498db",
                    icon_name="microphone",
                    icon_size="2x",
                )
                
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/wav")
                    
                    if st.button("🚀 Submit Voice Answer", type="primary", use_container_width=True):
                        with st.spinner("Transcribing your answer using Whisper AI..."):
                            try:
                                # Prepare audio file for upload
                                files = {
                                    "audio_file": ("recording.wav", io.BytesIO(audio_bytes), "audio/wav")
                                }
                                
                                # Send to transcription endpoint
                                transcribe_response = requests.post(
                                    f"{API_BASE_URL}/interview/transcribe",
                                    files=files,
                                    timeout=30
                                )
                                
                                if transcribe_response.status_code == 200:
                                    transcription_data = transcribe_response.json()
                                    transcribed_text = transcription_data.get("text", "")
                                    
                                    st.success(f"✅ Transcribed: {transcribed_text}")
                                    
                                    # Submit the transcribed answer
                                    with st.spinner("Evaluating your answer..."):
                                        answer_response = requests.post(
                                            f"{API_BASE_URL}/interview/{interview_id}/answer",
                                            params={"answer": transcribed_text},
                                            timeout=30
                                        )
                                        
                                        if answer_response.status_code == 200:
                                            result = answer_response.json()
                                            
                                            if result['status'] == 'Completed':
                                                st.success("✅ Interview completed! Generating summary...")
                                            else:
                                                st.success("✅ Answer submitted!")
                                                
                                                # Show evaluation if available
                                                if 'evaluation' in result:
                                                    eval_data = result['evaluation']
                                                    st.write(f"**Rating:** {eval_data.get('rating', 'N/A')}/5")
                                                    st.write(f"**Feedback:** {eval_data.get('feedback', 'N/A')}")
                                            
                                            st.rerun()
                                        else:
                                            st.error(f"Error: {answer_response.json().get('detail', 'Unknown error')}")
                                else:
                                    st.error(f"Transcription failed: {transcribe_response.json().get('detail', 'Unknown error')}")
                                    
                            except requests.exceptions.RequestException as e:
                                st.error(f"Error: {str(e)}")
            
            st.divider()
            
            # Show previous Q&A
            with st.expander("📝 View Previous Questions & Answers"):
                try:
                    interview_response = requests.get(f"{API_BASE_URL}/interview/{interview_id}/status", timeout=5)
                    # This is a simplified version - you'd need a proper endpoint to get full conversation
                    st.info("Previous conversation history will be shown here")
                except:
                    st.error("Unable to load conversation history")
        
    else:
        st.error("❌ Interview not found or unable to fetch status.")
        
except requests.exceptions.RequestException as e:
    st.error(f"❌ Error connecting to backend: {str(e)}")
    st.info("Make sure the FastAPI backend is running")

st.divider()

# Navigation buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("← Back to Dashboard", use_container_width=True):
        if 'current_interview_id' in st.session_state:
            del st.session_state['current_interview_id']
        st.switch_page("User/user.py")

