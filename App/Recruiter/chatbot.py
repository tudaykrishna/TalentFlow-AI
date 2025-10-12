"""AI Chatbot for Recruiters"""
import streamlit as st
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path to import utils
app_dir = Path(__file__).resolve().parent.parent
if str(app_dir) not in sys.path:
    sys.path.insert(0, str(app_dir))

# Load environment variables from project root
from utils.env_loader import load_env_from_root
load_env_from_root()

from langchain.prompts import PromptTemplate
from langchain_openai import AzureChatOpenAI

logger = logging.getLogger(__name__)

# Initialize LLM once (module level)
_llm_instance = None
_init_error = None

def _initialize_llm():
    """Initialize Azure OpenAI LLM"""
    global _llm_instance, _init_error
    
    if _llm_instance is not None:
        return _llm_instance
    
    if _init_error is not None:
        raise _init_error
    
    try:
        # Get environment variables
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment_name = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        
        # Validate
        if not all([api_key, api_version, azure_endpoint, deployment_name]):
            missing = []
            if not api_key: missing.append("AZURE_OPENAI_API_KEY")
            if not api_version: missing.append("AZURE_OPENAI_API_VERSION")
            if not azure_endpoint: missing.append("AZURE_OPENAI_ENDPOINT")
            if not deployment_name: missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")
        
        # Initialize LLM
        _llm_instance = AzureChatOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
            deployment_name=deployment_name,
            temperature=0.7
        )
        
        logger.info("✅ Chatbot LLM initialized successfully")
        return _llm_instance
        
    except Exception as e:
        _init_error = e
        logger.error(f"❌ Failed to initialize chatbot LLM: {e}")
        raise

def get_llm_response(user_message):
    """Get AI response using Azure OpenAI"""
    try:
        # Get or initialize LLM
        llm = _initialize_llm()
        
        # Create prompt template
        template = """You are a helpful AI assistant for recruiters using the TalentFlow AI platform.

You can help with:
- Creating job descriptions
- Screening resumes
- Managing interviews
- Understanding platform features
- General recruiting advice

Keep responses concise, helpful, and focused on recruiting tasks.
If asked about platform features, provide step-by-step guidance.

User Question: {user_input}

Your Response:"""
        
        prompt = PromptTemplate(
            input_variables=["user_input"],
            template=template
        )
        
        # Create chain
        chain = prompt | llm
        
        # Get response
        response = chain.invoke({"user_input": user_message})
        return response.content
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Chatbot error: {error_msg}")
        
        # User-friendly error messages
        if "Missing environment variables" in error_msg:
            return "⚠️ Configuration Error: Azure OpenAI credentials are not set up properly. Please contact your administrator."
        elif "API key" in error_msg or "authentication" in error_msg.lower():
            return "⚠️ Authentication Error: Invalid API key. Please check your Azure OpenAI configuration."
        elif "timeout" in error_msg.lower():
            return "⏱️ The AI service is taking too long to respond. Please try again."
        else:
            return f"⚠️ I'm having trouble connecting to the AI service right now. Please try again in a moment."

def render_chatbot():
    """Render the chatbot interface"""
    st.subheader("🤖 Recruiter Assistant")
    
    # Initialize chat history in session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
    
    # Chat input
    if user_input := st.chat_input("Ask me anything about recruiting..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get and display bot response
        with st.spinner("AI is thinking..."):
            bot_response = get_llm_response(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": bot_response})
        
        with st.chat_message("assistant"):
            st.write(bot_response)
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", type="secondary"):
        st.session_state.chat_history = []
        st.rerun()
