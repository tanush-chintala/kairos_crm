import streamlit as st
from dotenv import load_dotenv
import requests
import os
from streamlit_cookies_controller import CookieController

load_dotenv()

controller = CookieController()

st.set_page_config(
    page_title="Kairos CRM",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.ui import GLOBAL_PREMIUM_CSS
st.markdown(GLOBAL_PREMIUM_CSS, unsafe_allow_html=True)

from db import queries

if st.session_state.get("current_user"):
    with st.sidebar:
        st.markdown("""
            <style>
            /* Target the button immediately following this anchor and style it like a nav item */
            div.element-container:has(.user-btn-anchor) + div.element-container {
                position: absolute !important;
                top: 1rem !important;
                left: 1rem !important;
                width: auto !important;
                max-width: calc(100% - 4rem) !important;
                z-index: 9999 !important;
            }
            div.element-container:has(.user-btn-anchor) + div.element-container div.stButton button {
                background-color: transparent !important;
                color: rgba(26, 26, 26, 0.8) !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0.125rem 0.5rem !important; /* nav link: paddingLeft/Right spacing.sm, marginTop/Bottom threeXS */
                border-radius: 0.5rem !important; /* nav link: radii.default */
                font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
                font-size: 0.875rem !important; /* nav label: fontSizes.sm */
                font-weight: 600 !important;
                line-height: 2 !important; /* nav link: lineHeights.menuItem */
                display: flex !important;
                align-items: center !important;
                justify-content: flex-start !important;
                gap: 0.5rem !important; /* nav link: spacing.sm */
                width: 100% !important;
                transition: background-color 0.2s ease, color 0.2s ease !important;
            }
            div.element-container:has(.user-btn-anchor) + div.element-container div.stButton button [data-testid="stMarkdownContainer"] {
                flex: 0 1 auto !important;
            }
            div.element-container:has(.user-btn-anchor) + div.element-container div.stButton button p {
                font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
                font-size: 0.875rem !important; /* nav label: fontSizes.sm */
                font-weight: 600 !important;
                line-height: 2 !important;
                text-align: left !important;
                margin: 0 !important;
                padding: 0 !important;
            }
            div.element-container:has(.user-btn-anchor) + div.element-container div.stButton button span[data-testid="stIconMaterial"] {
                font-size: 1rem !important; /* nav icon: DynamicIcon size "base" = iconSizes.base = 1rem */
                width: 1rem !important;
                font-weight: 600 !important;
                color: inherit !important;
            }
            [data-testid="stSidebar"] [data-testid="stChatMessageContent"],
            [data-testid="stSidebar"] [data-testid="stChatMessageContent"] p {
                font-size: 0.75rem !important;
            }
            [data-testid="stSidebar"] [data-testid="stChatMessage"] {
                padding: 0.25rem 0.25rem !important;
                gap: 0.5rem !important;
            }
            [data-testid="stSidebar"] [data-testid^="stChatMessageAvatar"] {
                width: 1.25rem !important;
                height: 1.25rem !important;
                flex-shrink: 0 !important;
            }
            [data-testid="stSidebar"] [data-testid^="stChatMessageAvatar"] svg {
                width: 0.75rem !important;
                height: 0.75rem !important;
            }
            [data-testid="stSidebar"] [data-testid="stChatInput"] textarea,
            [data-testid="stSidebar"] [data-testid="stChatInput"] textarea::placeholder {
                font-size: 0.75rem !important; /* match chat message text */
            }
            [data-testid="stSidebar"] [data-testid="stChatInput"] {
                align-items: center !important;
            }
            [data-testid="stSidebar"] [data-testid="stChatInput"] textarea {
                min-height: 1.75rem !important;
                padding-top: 5px !important;
                padding-bottom: 0 !important;
                line-height: 1.75rem !important;
            }
            [data-testid="stSidebar"] [data-testid="stChatInputSubmitButton"] {
                align-self: center !important;
                margin-bottom: 0 !important;
            }
            [data-testid="stSidebar"] [data-testid="stChatInputSubmitButton"] svg {
                width: 1.1rem !important;
                height: 1.1rem !important;
            }
            [data-testid="stSidebar"] div[data-testid="stChatMessage"] + div[data-testid="stChatMessage"] {
                margin-top: 0 !important;
            }
            [data-testid="stSidebar"] [data-testid="stVerticalBlock"]:has(> [data-testid="stChatMessage"]) {
                gap: 0.25rem !important;
            }
            [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stChatMessage"]) > div,
            [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stChatMessage"]) [data-testid="stElementContainer"] {
                padding-left: 0.25rem !important;
                padding-right: 0.25rem !important;
            }
            div.element-container:has(.user-btn-anchor) + div.element-container div.stButton button:hover {
                background-color: rgba(182, 182, 164, 0.15) !important;
                color: rgb(26, 26, 26) !important;
                border: none !important;
                box-shadow: none !important;
            }
            div.element-container:has(.user-btn-anchor) + div.element-container div.stButton button:hover p {
                color: rgb(26, 26, 26) !important;
            }
            div.element-container:has(.user-btn-anchor) + div.element-container div.stButton button:active {
                background-color: rgba(182, 182, 164, 0.25) !important;
                font-weight: 600 !important;
            }
            div.element-container:has(.user-btn-anchor) + div.element-container div.stButton button:active p {
                font-weight: 600 !important;
            }
            div.element-container:has(.user-btn-anchor) + div.element-container div.stButton button span {
                color: inherit !important;
            }
            /* Tighten up spacing around the navigation menu */
            [data-testid="stSidebarNav"] {
                margin-top: 0.25rem !important;
                margin-bottom: 0 !important;
                padding-bottom: 0 !important;
            }
            [data-testid="stSidebarUserContent"] {
                padding-top: 0 !important;
                margin-top: -1rem !important;
            }
            [data-testid="stSidebarNavSeparator"], [data-testid="stSidebar"] hr {
                transform: translateY(-20px) !important;
                margin-bottom: 0.5rem !important;
                border: none !important;
                background: transparent !important;
            }
            </style>
            <div class="user-btn-anchor"></div>
        """, unsafe_allow_html=True)
        if st.button(f"Logged in as {st.session_state['current_user']['name']}", icon=":material/person:", use_container_width=True, help="Click to switch user"):
            st.session_state["current_user"] = None
            st.session_state.pop("filters_persist", None)
            controller.remove("kairos_user_id")
            st.rerun()

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

if st.session_state.get("current_user") is None:
    try:
        users = queries.list_users()
    except Exception as e:
        st.error(str(e))
        st.stop()
        
    saved_user_id = controller.get("kairos_user_id")
    if saved_user_id:
        for u in users:
            if str(u["id"]) == str(saved_user_id):
                st.session_state["current_user"] = u
                st.rerun()

    st.title("Kairos CRM")
    st.subheader("Who are you?")
    st.caption(
        "Your selection pre-fills the Kairos Owner field on new records. "
        "It is always editable per-entry."
    )
    if not users:
        st.warning("No active users found. Run schema.sql to seed the users table.")
        st.stop()
    cols = st.columns(min(len(users), 4))
    for i, user in enumerate(users):
        if cols[i % len(cols)].button(
            user["name"], key=f"pick_user_{user['id']}", use_container_width=True
        ):
            st.session_state["current_user"] = user
            controller.set("kairos_user_id", str(user["id"]))
            st.rerun()
    st.stop()

with st.sidebar:
    chat_container = st.container(height=400)
    
    current_user_id = st.session_state['current_user']['id']
    messages = queries.list_bot_messages(current_user_id)
    
    with chat_container:
        if not messages:
            st.caption("No messages yet. Try asking 'what's due today?'")
        for msg in messages:
            role = "user" if msg["role"] == "user" else "assistant"
            st.chat_message(role).write(msg["content"])
            
    if prompt := st.chat_input("Message Kairos Bot..."):
        url = os.environ.get("SUPABASE_URL", "") + "/functions/v1/sendblue-bot?debug=1&token=" + os.environ.get("BOT_WEBHOOK_TOKEN", "")
        payload = {
            "user_id": current_user_id,
            "content": prompt
        }
        with chat_container:
            st.chat_message("user").write(prompt)
            with st.spinner("Thinking..."):
                try:
                    resp = requests.post(url, json=payload, timeout=30)
                    resp.raise_for_status()
                except Exception as e:
                    body = getattr(getattr(e, "response", None), "text", "")
                    st.error(f"Bot error: {e}" + (f" - {body}" if body else ""))
        st.rerun()

pages.run()
