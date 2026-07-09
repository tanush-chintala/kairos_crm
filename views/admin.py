import streamlit as st

from db import queries

# Same keyed-container trick as the accounts list: Streamlit has no native
# striping or header row for st.columns lists.
_LIST_CSS = """
<style>
[class*="st-key-admin_header"],
[class*="st-key-admin_row_"] {
    padding: 0.15rem 0.6rem;
    border-radius: 0.5rem;
}
[class*="st-key-admin_header"] {
    background-color: rgba(151, 166, 195, 0.35);
    padding-top: 0.4rem;
    padding-bottom: 0.4rem;
}
[class*="st-key-admin_row_even"] {
    background-color: rgba(151, 166, 195, 0.12);
}
[class*="st-key-admin_row_"] button,
[class*="st-key-admin_row_"] button p {
    white-space: nowrap;
}
</style>
"""

_LIST_WIDTHS = [3, 1, 1]

st.title("Settings")
st.caption(
    "Users and channel types are editable here without a code deploy. "
    "Deactivate rather than delete — historical records keep their references."
)
st.markdown(_LIST_CSS, unsafe_allow_html=True)


def _list_header(key: str, name_label: str) -> None:
    with st.container(key=f"admin_header_{key}"):
        cols = st.columns(_LIST_WIDTHS, vertical_alignment="center")
        cols[0].markdown(f"**{name_label}**")
        cols[1].markdown("**Status**")


st.subheader("Users", divider=True)
with st.form("add_user", clear_on_submit=True):
    c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
    name = c1.text_input("New user name")
    if c2.form_submit_button("Add user", icon=":material/person_add:"):
        if name.strip():
            queries.add_user(name.strip())
            st.rerun()

_list_header("users", "Name")
for i, user in enumerate(queries.list_users(active_only=False)):
    parity = "even" if i % 2 == 0 else "odd"
    with st.container(key=f"admin_row_{parity}_user_{user['id']}"):
        c1, c2, c3 = st.columns(_LIST_WIDTHS, vertical_alignment="center")
        c1.write(user["name"])
        c2.write("Active" if user["active"] else "Inactive")
        toggle_label = "Deactivate" if user["active"] else "Reactivate"
        if c3.button(toggle_label, key=f"user_toggle_{user['id']}", use_container_width=True):
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

_list_header("channels", "Channel")
for i, channel in enumerate(queries.list_channel_types(active_only=False)):
    parity = "even" if i % 2 == 0 else "odd"
    with st.container(key=f"admin_row_{parity}_channel_{channel['id']}"):
        c1, c2, c3 = st.columns(_LIST_WIDTHS, vertical_alignment="center")
        c1.write(channel["label"])
        c2.write("Active" if channel["active"] else "Inactive")
        toggle_label = "Deactivate" if channel["active"] else "Reactivate"
        if c3.button(toggle_label, key=f"channel_toggle_{channel['id']}", use_container_width=True):
            queries.set_channel_type_active(channel["id"], not channel["active"])
            st.rerun()
