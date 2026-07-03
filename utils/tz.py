"""All due/overdue/stale comparisons use Central Time (America/Chicago),
unconditionally — the whole team is DFW-based (spec section 7)."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

CENTRAL = ZoneInfo("America/Chicago")


def central_now() -> datetime:
    return datetime.now(CENTRAL)


def central_today() -> date:
    return central_now().date()


def end_of_week(today: date) -> date:
    """Sunday of the current Mon-Sun week."""
    return today + timedelta(days=6 - today.weekday())


def parse_date(value) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return date.fromisoformat(str(value)[:10])
