import streamlit as st

# Initialize session state for login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Define login function
def login():
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()


# Define logout function
def logout():
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()

# Define pages
login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

dashboard = st.Page(
    "pages/Dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True
)
reports = st.Page("pages/Reports.py", title="Reports", icon=":material/bug_report:")
upload = st.Page("pages/Upload.py", title="Upload", icon=":material/upload:")
time_slider = st.Page("pages/Time_Slider.py", title="Time Slider", icon=":material/notification_important:")

# Navigation based on login state
if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Account": [logout_page],
            "Pages": [dashboard, reports, upload, time_slider],
        }
    )
else:
    pg = st.navigation([login_page])

# Set the page layout to wide
st.set_page_config(layout="wide")

pg.run()