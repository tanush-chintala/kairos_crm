"""Query helpers per table. Supabase is the single source of truth — every
view reads fresh through these; nothing is cached across reruns."""

from __future__ import annotations

from db.client import get_client


def list_users(active_only: bool = True) -> list[dict]:
    q = get_client().table("users").select("*").order("name")
    if active_only:
        q = q.eq("active", True)
    return q.execute().data


def add_user(name: str) -> int:
    res = get_client().table("users").insert({"name": name}).execute()
    return res.data[0]["id"]


def set_user_active(user_id: int, active: bool) -> None:
    get_client().table("users").update({"active": active}).eq("id", user_id).execute()


def list_channel_types(active_only: bool = True) -> list[dict]:
    q = get_client().table("channel_types").select("*").order("label")
    if active_only:
        q = q.eq("active", True)
    return q.execute().data


def add_channel_type(label: str) -> int:
    res = get_client().table("channel_types").insert({"label": label}).execute()
    return res.data[0]["id"]


def set_channel_type_active(channel_id: int, active: bool) -> None:
    get_client().table("channel_types").update({"active": active}).eq("id", channel_id).execute()


def list_accounts(
    owner_id: int | None = None,
    stage: str | None = None,
    channel_id: int | None = None,
    city: str | None = None,
    search: str | None = None,
) -> list[dict]:
    q = get_client().table("account_overview").select("*")
    if owner_id is not None:
        q = q.eq("kairos_owner_id", owner_id)
    if stage:
        q = q.eq("pipeline_stage", stage)
    if channel_id:
        q = q.eq("channel_type_id", channel_id)
    if city:
        q = q.ilike("city", f"%{city}%")
    if search:
        q = q.ilike("practice_name", f"%{search}%")
    return q.order("practice_name").execute().data


def get_account(account_id: int) -> dict | None:
    rows = (
        get_client().table("account_overview").select("*").eq("id", account_id).execute().data
    )
    return rows[0] if rows else None


def create_account(fields: dict) -> dict:
    return get_client().table("accounts").insert(fields).execute().data[0]


def update_account(account_id: int, fields: dict) -> None:
    get_client().table("accounts").update(fields).eq("id", account_id).execute()


def delete_account(account_id: int) -> None:
    get_client().table("accounts").delete().eq("id", account_id).execute()


def list_contacts(account_id: int) -> list[dict]:
    return (
        get_client().table("contacts").select("*").eq("account_id", account_id)
        .order("name").execute().data
    )


def create_contact(fields: dict) -> None:
    get_client().table("contacts").insert(fields).execute()


def update_contact(contact_id: int, fields: dict) -> None:
    get_client().table("contacts").update(fields).eq("id", contact_id).execute()


def delete_contact(contact_id: int) -> None:
    get_client().table("contacts").delete().eq("id", contact_id).execute()


def list_activities(account_id: int) -> list[dict]:
    return (
        get_client().table("activities").select("*").eq("account_id", account_id)
        .order("date", desc=True).order("id", desc=True).execute().data
    )


def list_recent_activities(limit: int = 20) -> list[dict]:
    return (
        get_client().table("activities").select("*, accounts(practice_name)")
        .eq("is_system", False)
        .order("date", desc=True).order("id", desc=True).limit(limit).execute().data
    )


def log_activity(fields: dict) -> None:
    # The activities_sync_next_action trigger updates the parent account's
    # next_action fields atomically with this insert — do not update here too.
    get_client().table("activities").insert(fields).execute()


def list_demos(account_id: int) -> list[dict]:
    return (
        get_client().table("demos").select("*").eq("account_id", account_id)
        .order("demo_date", desc=True).execute().data
    )


def list_all_demos() -> list[dict]:
    return get_client().table("demos").select("*").execute().data


def create_demo(fields: dict) -> None:
    get_client().table("demos").insert(fields).execute()


def update_demo(demo_id: int, fields: dict) -> None:
    get_client().table("demos").update(fields).eq("id", demo_id).execute()


def delete_demo(demo_id: int) -> None:
    get_client().table("demos").delete().eq("id", demo_id).execute()


def list_cadences(active_only: bool = True) -> list[dict]:
    q = get_client().table("cadences").select("*").order("name")
    if active_only:
        q = q.eq("active", True)
    return q.execute().data


def create_cadence(fields: dict) -> None:
    get_client().table("cadences").insert(fields).execute()


def update_cadence(cadence_id: int, fields: dict) -> None:
    get_client().table("cadences").update(fields).eq("id", cadence_id).execute()


def list_cadence_steps(cadence_id: int) -> list[dict]:
    return (
        get_client().table("cadence_steps").select("*").eq("cadence_id", cadence_id)
        .order("step_order").order("id").execute().data
    )


def create_cadence_step(fields: dict) -> None:
    get_client().table("cadence_steps").insert(fields).execute()


def update_cadence_step(step_id: int, fields: dict) -> None:
    get_client().table("cadence_steps").update(fields).eq("id", step_id).execute()


def delete_cadence_step(step_id: int) -> None:
    get_client().table("cadence_steps").delete().eq("id", step_id).execute()


def get_template(template_id: int) -> dict | None:
    rows = (
        get_client().table("email_templates").select("*").eq("id", template_id).execute().data
    )
    return rows[0] if rows else None


def list_templates(category: str | None = None) -> list[dict]:
    q = get_client().table("email_templates").select("*").order("name")
    if category:
        q = q.eq("category", category)
    return q.execute().data


def create_template(fields: dict) -> None:
    get_client().table("email_templates").insert(fields).execute()


def update_template(template_id: int, fields: dict) -> None:
    get_client().table("email_templates").update(fields).eq("id", template_id).execute()


def delete_template(template_id: int) -> None:
    get_client().table("email_templates").delete().eq("id", template_id).execute()


def get_distinct_column_values(table: str, column: str) -> list[str]:
    res = get_client().table(table).select(column).execute()
    vals = {r[column] for r in res.data if r.get(column)}
    return sorted(list(vals))


def list_bot_messages(session_id: int, limit: int = 50) -> list[dict]:
    data = (
        get_client().table("bot_messages").select("*")
        .eq("session_id", session_id)
        .order("id", desc=True).limit(limit).execute().data
    )
    return list(reversed(data))


def list_chat_sessions(user_id: int) -> list[dict]:
    return (
        get_client().table("chat_sessions").select("*")
        .eq("user_id", user_id)
        .order("last_message_at", desc=True).execute().data
    )


def get_or_create_default_session(user_id: int) -> dict:
    existing = (
        get_client().table("chat_sessions").select("*")
        .eq("user_id", user_id).eq("is_default", True).limit(1).execute().data
    )
    if existing:
        return existing[0]
    return (
        get_client().table("chat_sessions")
        .insert({"user_id": user_id, "title": "Texts", "is_default": True})
        .execute().data[0]
    )


def create_chat_session(user_id: int, title: str | None = None) -> dict:
    return (
        get_client().table("chat_sessions")
        .insert({"user_id": user_id, "title": title})
        .execute().data[0]
    )


def rename_chat_session(session_id: int, title: str | None) -> None:
    get_client().table("chat_sessions").update({"title": title}).eq("id", session_id).execute()


def delete_chat_session(session_id: int) -> None:
    get_client().table("chat_sessions").delete().eq("id", session_id).execute()
