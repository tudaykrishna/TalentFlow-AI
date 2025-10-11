"""Debug Configuration Page"""
import streamlit as st
import requests

st.title("🔧 Debug Configuration")
st.warning("⚠️ This page shows sensitive configuration information - FOR TESTING ONLY!")

# API Base URL
API_BASE_URL = st.session_state.get('api_base_url', 'http://localhost:8000/api')

st.subheader("📋 Backend Configuration Status")

if st.button("🔍 Load Backend Configuration", type="primary"):
    try:
        response = requests.get(f"{API_BASE_URL}/auth/debug/config", timeout=5)
        
        if response.status_code == 200:
            config = response.json()
            
            # Azure OpenAI Settings
            st.subheader("🔵 Azure OpenAI Configuration")
            azure_config = config.get('azure_openai', {})
            
            col1, col2 = st.columns(2)
            with col1:
                st.code(f"API Key: {azure_config.get('api_key_masked', 'NOT SET')}")
                st.code(f"Endpoint: {azure_config.get('endpoint', 'NOT SET')}")
                st.code(f"API Version: {azure_config.get('api_version', 'NOT SET')}")
            
            with col2:
                st.code(f"Chat Deployment: {azure_config.get('chat_deployment', 'NOT SET')}")
                st.code(f"Whisper Deployment: {azure_config.get('whisper_deployment', 'NOT SET')}")
            
            # Show issues if any
            issues = config.get('issues_detected', [])
            if issues:
                st.subheader("⚠️ Issues Detected")
                for issue in issues:
                    if '✅' in issue:
                        st.success(issue)
                    else:
                        st.error(issue)
            else:
                st.success("✅ No configuration issues detected")
            
            # MongoDB Settings
            st.subheader("🗄️ MongoDB Configuration")
            mongo_config = config.get('mongodb', {})
            st.code(f"URI: {mongo_config.get('uri', 'NOT SET')}")
            st.code(f"Database: {mongo_config.get('db_name', 'NOT SET')}")
            
            # API Settings
            st.subheader("⚙️ API Settings")
            api_config = config.get('api_settings', {})
            st.code(f"Host: {api_config.get('host', 'NOT SET')}")
            st.code(f"Port: {api_config.get('port', 'NOT SET')}")
            st.code(f"Debug: {api_config.get('debug', 'NOT SET')}")
            
        else:
            st.error(f"❌ Failed to get config: {response.status_code}")
            st.error(f"Response: {response.text}")
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend!")
        st.info("💡 Make sure the FastAPI backend is running on http://localhost:8000")
    
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out!")
        st.info("💡 The backend might be slow or unresponsive")
    
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")

st.divider()

st.subheader("🧪 Quick Tests")

col1, col2 = st.columns(2)

with col1:
    if st.button("🌐 Test Backend Connection", use_container_width=True):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ Backend is running!")
                health_data = response.json()
                st.json(health_data)
            else:
                st.error(f"❌ Backend returned status {response.status_code}")
        except Exception as e:
            st.error(f"❌ Backend connection failed: {str(e)}")

with col2:
    if st.button("🔑 Test API Endpoint", use_container_width=True):
        try:
            response = requests.get(f"{API_BASE_URL}/auth/debug/config", timeout=5)
            if response.status_code == 200:
                st.success("✅ API endpoint is accessible!")
            else:
                st.error(f"❌ API endpoint returned status {response.status_code}")
        except Exception as e:
            st.error(f"❌ API endpoint test failed: {str(e)}")

st.divider()

st.subheader("📝 Instructions")
st.markdown("""
### How to use this debug page:

1. **Load Configuration**: Click the button above to fetch current backend configuration
2. **Check Issues**: Review any detected configuration issues
3. **Test Connections**: Use the quick test buttons to verify connectivity
4. **Troubleshoot**: If you see errors, check:
   - Backend is running (`start_backend.bat`)
   - `.env` file is properly configured
   - Azure OpenAI credentials are correct
   - MongoDB is accessible

### Common Issues:
- **401 Error**: Check Azure OpenAI API key and endpoint
- **404 Error**: Verify deployment names in `.env`
- **Connection Error**: Ensure backend is running on port 8000
""")

st.info("💡 This debug information helps troubleshoot configuration issues. Remove this page in production!")
