import streamlit as st

from db import queries

st.title("Settings")
st.caption(
    "Users and channel types are editable here without a code deploy. "
    "Deactivate rather than delete — historical records keep their references."
)

st.subheader("Users", divider=True)
with st.form("add_user", clear_on_submit=True):
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    name = c1.text_input("New user name")
    if c2.form_submit_button("Add user", icon=":material/person_add:"):
        if name.strip():
            queries.add_user(name.strip())
            st.rerun()

for user in queries.list_users(active_only=False):
    c1, c2, c3 = st.columns([3, 1, 1], vertical_alignment="center")
    c1.write(user["name"])
    c2.write("Active" if user["active"] else "Inactive")
    toggle_label = "Deactivate" if user["active"] else "Reactivate"
    if c3.button(toggle_label, key=f"user_toggle_{user['id']}"):
        queries.set_user_active(user["id"], not user["active"])
        st.rerun()

st.subheader("Channel types", divider=True)
with st.form("add_channel", clear_on_submit=True):
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    label = c1.text_input("New channel type")
    if c2.form_submit_button("Add channel", icon=":material/add:"):
        if label.strip():
            queries.add_channel_type(label.strip())
            st.rerun()

for channel in queries.list_channel_types(active_only=False):
    c1, c2, c3 = st.columns([3, 1, 1], vertical_alignment="center")
    c1.write(channel["label"])
    c2.write("Active" if channel["active"] else "Inactive")
    toggle_label = "Deactivate" if channel["active"] else "Reactivate"
    if c3.button(toggle_label, key=f"channel_toggle_{channel['id']}"):
        queries.set_channel_type_active(channel["id"], not channel["active"])
        st.rerun()
