import streamlit as st

from db import queries
from utils.stale import categorize
from utils.tz import central_today, parse_date

left, right = st.columns([5, 1], vertical_alignment="center")
left.title("Dashboard")
if right.button("Refresh", icon=":material/refresh:", use_container_width=True):
    st.rerun()


def _open_account(account_id: int) -> None:
    st.session_state["selected_account_id"] = account_id
    st.switch_page("views/accounts.py")


def _rows(items: list[dict], users: dict, key_prefix: str, show_days_overdue: bool = False) -> None:
    if not items:
        st.caption("Nothing here.")
        return
    for item in items:
        acct = item["account"]
        cols = st.columns([3, 2, 2, 3, 2, 1], vertical_alignment="center")
        cols[0].markdown(f"**{acct['practice_name']}**")
        cols[1].write(users.get(acct.get("kairos_owner_id"), "—"))
        cols[2].write(acct.get("pipeline_stage") or "—")
        cols[3].write(acct.get("next_action") or "—")
        due = parse_date(acct.get("next_action_due_date"))
        if show_days_overdue and item.get("days_overdue") is not None:
            cols[4].write(f"{due} ({item['days_overdue']}d overdue)")
        else:
            cols[4].write(str(due) if due else "—")
        if cols[5].button("Open", key=f"{key_prefix}_{acct['id']}"):
            _open_account(acct["id"])
        if item.get("reasons"):
            st.caption("; ".join(item["reasons"]))


# Read-only fragment, so a 60s auto-refresh can't blow away form input
# (spec section 2 — never auto-refresh pages with edit forms).
@st.fragment(run_every=60)
def _dashboard_body() -> None:
    accounts = queries.list_accounts()
    users = {u["id"]: u["name"] for u in queries.list_users(active_only=False)}
    demos_by_account: dict[int, list[dict]] = {}
    for demo in queries.list_all_demos():
        demos_by_account.setdefault(demo["account_id"], []).append(demo)

    today = central_today()
    buckets = categorize(accounts, demos_by_account, today)

    st.info(
        f"{len(buckets['overdue'])} overdue follow-ups, "
        f"{len(buckets['due_today'])} actions due today, "
        f"{len(buckets['stale'])} stale leads, "
        f"{len(buckets['upcoming'])} upcoming this week."
    )

    st.subheader("Due Today", divider=True)
    _rows(buckets["due_today"], users, "due")

    st.subheader("Overdue", divider=True)
    _rows(buckets["overdue"], users, "over", show_days_overdue=True)

    st.subheader("Stale Leads", divider=True)
    _rows(buckets["stale"], users, "stale")

    st.subheader("Upcoming This Week", divider=True)
    _rows(buckets["upcoming"], users, "up")

    st.caption(f"As of {today} (Central). Auto-refreshes every 60 seconds.")


_dashboard_body()
