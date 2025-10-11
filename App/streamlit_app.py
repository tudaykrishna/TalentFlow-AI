"""
TalentFlow AI - Streamlit Frontend
Main Application Entry Point
"""
import streamlit as st

# Initialize session state
if "role" not in st.session_state:
    st.session_state.role = None

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = "http://localhost:8000/api"

if "interview_id" not in st.session_state:
    st.session_state.interview_id = None


def login():
    """Login page"""
    st.header("🔐 Log in to TalentFlow AI")
    st.write("Enter your credentials to access the platform")
    
    # Email/Username input
    email = st.text_input(
        "Email Address",
        placeholder="your.email@example.com",
        help="Enter your registered email or temporary email provided by recruiter"
    )
    
    # Password input
    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password",
        help="Enter your password or temporary password provided by recruiter"
    )
    
    if st.button("Log in", type="primary", use_container_width=True):
        if email and password:
            # Call authentication API
            import requests
            try:
                response = requests.post(
                    f"{st.session_state.api_base_url}/auth/login",
                    json={"email": email, "password": password},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Store user info in session
                    st.session_state.user_id = data["user_id"]
                    st.session_state.user_email = data["email"]
                    st.session_state.user_name = data.get("username", email.split("@")[0])
                    
                    # Map role to the format expected by the app
                    role_map = {
                        "user": "User",
                        "recruiter": "Recruiter",
                        "admin": "Admin"
                    }
                    st.session_state.role = role_map.get(data["role"], "User")
                    
                    st.success(data.get("message", "Login successful!"))
                    st.rerun()
                    
                elif response.status_code == 401:
                    st.error("❌ Invalid email or password. Please try again.")
                    
                elif response.status_code == 403:
                    error_detail = response.json().get("detail", "Access forbidden")
                    st.error(f"❌ {error_detail}")
                    
                else:
                    st.error(f"❌ Login failed: {response.json().get('detail', 'Unknown error')}")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Unable to connect to authentication server: {str(e)}")
                st.info("💡 Make sure the backend server is running")
        else:
            st.error("Please enter both email and password")
    
    # Registration info for new users
    st.divider()
    with st.expander("ℹ️ New User Information"):
        st.markdown("""
        ### For Candidates:
        - You will receive temporary login credentials from your recruiter
        - These credentials are valid for **24 hours** only
        - You can attempt the interview **only once**
        
        ### For Recruiters/Admins:
        - Contact your system administrator to create an account
        - Use your registered email and password to log in
        """)


def logout():
    """Logout and clear session"""
    st.session_state.role = None
    st.session_state.user_id = None
    st.session_state.user_name = None
    st.session_state.user_email = None
    st.session_state.interview_id = None
    st.rerun()


# Get current role
role = st.session_state.role

# Define pages
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

# User pages
user_page_1 = st.Page(
    "User/user.py",
    title="Dashboard",
    icon=":material/dashboard:",
    default=(role == "User"),
)
user_page_2 = st.Page(
    "User/ai_interview.py", 
    title="AI Interview", 
    icon=":material/mic:"
)

# Recruiter pages
recruiter_page_1 = st.Page(
    "Recruiter/recruiter.py",
    title="Dashboard",
    icon=":material/dashboard:",
    default=(role == "Recruiter"),
)
recruiter_page_2 = st.Page(
    "Recruiter/jd_generator.py", 
    title="JD Generator", 
    icon=":material/description:"
)
recruiter_page_3 = st.Page(
    "Recruiter/resume_screener.py", 
    title="Resume Screener", 
    icon=":material/fact_check:"
)
recruiter_page_4 = st.Page(
    "Recruiter/interview_assignment.py", 
    title="Interview Assignment", 
    icon=":material/assignment:"
)
recruiter_page_5 = st.Page(
    "Recruiter/interview_results.py", 
    title="Interview Results", 
    icon=":material/analytics:"
)

# Admin pages
admin_page_1 = st.Page(
    "Admin/admin.py",
    title="Dashboard",
    icon=":material/admin_panel_settings:",
    default=(role == "Admin"),
)
admin_page_2 = st.Page(
    "Admin/Demo1.py", 
    title="User Management", 
    icon=":material/group:"
)
admin_page_3 = st.Page(
    "Admin/Demo2.py", 
    title="Analytics", 
    icon=":material/analytics:"
)
admin_page_4 = st.Page(
    "Admin/Demo3.py", 
    title="System Logs", 
    icon=":material/description:"
)
admin_page_5 = st.Page(
    "debug_config.py", 
    title="Debug Config", 
    icon=":material/bug_report:"
)

# Account pages
account_pages = [logout_page, settings]
user_pages = [user_page_1, user_page_2]
recruiter_pages = [recruiter_page_1, recruiter_page_2, recruiter_page_3, recruiter_page_4, recruiter_page_5]
admin_pages = [admin_page_1, admin_page_2, admin_page_3, admin_page_4, admin_page_5]

# Set page configuration
st.set_page_config(
    page_title="TalentFlow AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and logo
st.title("TalentFlow AI")
st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")

# Build navigation based on role
page_dict = {}

if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages
    page_dict["User"] = user_pages  # Admin can access user pages

if st.session_state.role == "Recruiter":
    page_dict["Recruiter"] = recruiter_pages

if st.session_state.role == "User":
    page_dict["User"] = user_pages

# Navigation
if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

# Run the selected page
pg.run()
