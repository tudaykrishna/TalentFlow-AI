import streamlit as st

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None, "User", "Admin"]


def login():

    st.header("Log in")
    role = st.selectbox("Choose your role", ROLES)

    if st.button("Log in"):
        st.session_state.role = role
        st.rerun()


def logout():
    st.session_state.role = None
    st.rerun()


role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")

user_page_1 = st.Page(
    "User/user.py",
    title="User",
    icon=":material/healing:",
    default=(role == "User"),
)
user_page_2 = st.Page(
    "User/Demo4.py", title="Demo4", icon=":material/bug_report:")

admin_page_1 = st.Page(
    "Admin/admin.py",
    title="Admin",
    icon=":material/person_add:",
    default=(role == "Admin"),
)
admin_page_2 = st.Page(
    "Admin/Demo1.py", title="Demo1", icon=":material/extension:")
admin_page_3 = st.Page(
    "Admin/Demo2.py", title="Demo2", icon=":material/extension:")
admin_page_4 = st.Page(
    "Admin/Demo3.py", title="Demo3", icon=":material/extension:")

account_pages = [logout_page, settings]
user_pages = [user_page_1,user_page_2]
admin_pages = [admin_page_1,
               admin_page_2,
               admin_page_3,
               admin_page_4             
               ]

st.title("Request manager")
st.logo("images/horizontal_blue.png", icon_image="images/icon_blue.png")

page_dict = {}


if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages

if st.session_state.role in ["User", "Admin"]:
    page_dict["User"] = user_pages

if len(page_dict) > 0:
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()