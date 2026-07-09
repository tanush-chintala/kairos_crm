import streamlit as st

from db import queries
from utils.stale import categorize
from utils.tz import central_today, parse_date

left, right = st.columns([5, 1], vertical_alignment="center")
left.title("Dashboard")
if right.button("Refresh", icon=":material/refresh:", use_container_width=True):
    st.rerun()

# Same keyed-container trick as the accounts list: Streamlit has no native
# striping or header row for st.columns lists.
_LIST_CSS = """
<style>
[class*="st-key-dash_header"],
[class*="st-key-dash_row_"] {
    padding: 0.15rem 0.6rem;
    border-radius: 0.5rem;
}
[class*="st-key-dash_header"] {
    background-color: rgba(151, 166, 195, 0.35);
    padding-top: 0.4rem;
    padding-bottom: 0.4rem;
}
[class*="st-key-dash_row_even"] {
    background-color: rgba(151, 166, 195, 0.12);
}
[class*="st-key-dash_row_"] button,
[class*="st-key-dash_row_"] button p {
    white-space: nowrap;
}
</style>
"""

_LIST_WIDTHS = [3, 2, 3, 2, 1.4]
_LIST_HEADERS = ["Practice", "Stage", "Next action", "Due date", ""]


def _open_account(account_id: int) -> None:
    st.session_state["selected_account_id"] = account_id
    st.switch_page("views/accounts.py")


def _rows(items: list[dict], key_prefix: str, show_days_overdue: bool = False) -> None:
    if not items:
        st.caption("Nothing here.")
        return
    with st.container(key=f"dash_header_{key_prefix}"):
        cols = st.columns(_LIST_WIDTHS, vertical_alignment="center")
        for col, label in zip(cols, _LIST_HEADERS):
            if label:
                col.markdown(f"**{label}**")
    for i, item in enumerate(items):
        acct = item["account"]
        parity = "even" if i % 2 == 0 else "odd"
        with st.container(key=f"dash_row_{parity}_{key_prefix}_{acct['id']}"):
            cols = st.columns(_LIST_WIDTHS, vertical_alignment="center")
            cols[0].markdown(f"**{acct['practice_name']}**")
            cols[1].write(acct.get("pipeline_stage") or "—")
            cols[2].write(acct.get("next_action") or "—")
            due = parse_date(acct.get("next_action_due_date"))
            if show_days_overdue and item.get("days_overdue") is not None:
                cols[3].write(f"{due} ({item['days_overdue']}d overdue)")
            else:
                cols[3].write(str(due) if due else "—")
            if cols[4].button("Open", key=f"{key_prefix}_{acct['id']}", use_container_width=True):
                _open_account(acct["id"])
            if item.get("reasons"):
                st.caption("; ".join(item["reasons"]))


# Read-only fragment, so a 60s auto-refresh can't blow away form input
# (spec section 2 — never auto-refresh pages with edit forms).
@st.fragment(run_every=60)
def _dashboard_body() -> None:
    current_user = st.session_state["current_user"]
    accounts = queries.list_accounts(owner_id=current_user["id"])
    demos_by_account: dict[int, list[dict]] = {}
    for demo in queries.list_all_demos():
        demos_by_account.setdefault(demo["account_id"], []).append(demo)

    today = central_today()
    buckets = categorize(accounts, demos_by_account, today)

    st.info(
        f"Showing accounts owned by {current_user['name']}: "
        f"{len(buckets['overdue'])} overdue follow-ups, "
        f"{len(buckets['due_today'])} actions due today, "
        f"{len(buckets['stale'])} stale leads, "
        f"{len(buckets['upcoming'])} upcoming this week."
    )

    st.markdown(_LIST_CSS, unsafe_allow_html=True)

    st.subheader("Due Today", divider=True)
    _rows(buckets["due_today"], "due")

    st.subheader("Overdue", divider=True)
    _rows(buckets["overdue"], "over", show_days_overdue=True)

    st.subheader("Stale Leads", divider=True)
    _rows(buckets["stale"], "stale")

    st.subheader("Upcoming This Week", divider=True)
    _rows(buckets["upcoming"], "up")

    st.caption(f"As of {today} (Central). Auto-refreshes every 60 seconds.")


_dashboard_body()
