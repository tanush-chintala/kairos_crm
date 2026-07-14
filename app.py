import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Kairos CRM",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.ui import GLOBAL_PREMIUM_CSS
st.markdown(GLOBAL_PREMIUM_CSS, unsafe_allow_html=True)


from db import queries

# No auth by design (spec section 3): a user-select landing screen sets a
# convenience default for owner fields, not an identity enforcement.
if st.session_state.get("current_user") is None:
    st.title("Kairos CRM")
    st.subheader("Who are you?")
    st.caption(
        "Your selection pre-fills the Kairos Owner field on new records. "
        "It is always editable per-entry."
    )
    try:
        users = queries.list_users()
    except Exception as e:
        st.error(str(e))
        st.stop()
    if not users:
        st.warning("No active users found. Run schema.sql to seed the users table.")
        st.stop()
    cols = st.columns(min(len(users), 4))
    for i, user in enumerate(users):
        if cols[i % len(cols)].button(
            user["name"], key=f"pick_user_{user['id']}", use_container_width=True
        ):
            st.session_state["current_user"] = user
            st.rerun()
    st.stop()

pages = st.navigation(
    [
        st.Page("views/dashboard.py", title="Dashboard", icon=":material/dashboard:", default=True),
        st.Page("views/overview.py", title="Team Overview", icon=":material/groups:"),
        st.Page("views/accounts.py", title="Accounts", icon=":material/business:"),
        st.Page("views/email_templates.py", title="Email Templates", icon=":material/mail:"),
        st.Page("views/csv_import.py", title="CSV Import", icon=":material/upload_file:"),
        st.Page("views/admin.py", title="Settings", icon=":material/settings:"),
    ]
)

with st.sidebar:
    st.markdown(f"Acting as: **{st.session_state['current_user']['name']}**")
    if st.button("Switch user", icon=":material/swap_horiz:", use_container_width=True):
        st.session_state["current_user"] = None
        # Filter defaults derive from the acting user, so they must reinitialize
        st.session_state.pop("filters_persist", None)
        st.rerun()
    st.divider()

pages.run()
