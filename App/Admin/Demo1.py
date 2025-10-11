"""User Management - Admin Panel"""
import streamlit as st
import pandas as pd

st.title("👥 User Management")
st.write("Manage system users, recruiters, and administrators")

st.divider()

# User Statistics
st.subheader("📊 User Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Users", "0", delta="0")

with col2:
    st.metric("Active Recruiters", "0", delta="0")

with col3:
    st.metric("Admins", "0", delta="0")

with col4:
    st.metric("Pending Approvals", "0", delta="0")

st.divider()

# Add New User
st.subheader("➕ Add New User")

with st.form("add_user_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name *")
        email = st.text_input("Email *")
    
    with col2:
        role = st.selectbox("Role *", ["User", "Recruiter", "Admin"])
        password = st.text_input("Password *", type="password")
    
    submitted = st.form_submit_button("Add User", type="primary", use_container_width=True)
    
    if submitted:
        if all([name, email, role, password]):
            st.success(f"✅ User {name} added successfully!")
        else:
            st.error("❌ Please fill in all required fields")

st.divider()

# User List
st.subheader("📋 User List")

# Sample data
sample_users = pd.DataFrame({
    "Name": ["John Doe", "Jane Smith", "Bob Wilson"],
    "Email": ["john@example.com", "jane@example.com", "bob@example.com"],
    "Role": ["User", "Recruiter", "Admin"],
    "Status": ["Active", "Active", "Active"],
    "Created": ["2024-01-10", "2024-01-12", "2024-01-14"]
})

st.dataframe(sample_users, use_container_width=True, hide_index=True)

st.info("💡 User management features are in development. Connect to MongoDB to see real data.")

