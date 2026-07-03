# Kairos CRM — Developer Notes for Claude

## Hard rules (inherited from the kairosintern repo — keep both in sync)

- **No emojis anywhere.** Never use emoji characters in any Python file, HTML string, button label, markdown string, or comment. Use Streamlit Material icons (`:material/refresh:`, `:material/dashboard:`, etc.) or plain text instead.
- **No comments explaining what code does.** Only add a comment when the WHY is non-obvious.
- **No new files unless required.** Prefer editing existing files.

## What this is

Internal CRM for the Kairos sales team (Tanush, Aditya, Sanjana, Adhira) tracking dental-practice leads: accounts, contacts, activity log, demos, email templates. Spec lives in `CRM_SPEC.md`. Deliberately a separate repo/deploy from `kairosintern` (the lead-gen/Donut Scraper tool) — this is the system of record, higher reliability bar.

## Stack

- Streamlit multi-page app (`app.py` + `views/`, mirrors kairosintern's structure)
- Supabase (Postgres) via `supabase-py` — single source of truth for every read/write; nothing meaningful lives in `st.session_state` beyond the selected user, in-progress form values, and filter selections
- `rapidfuzz` for duplicate detection name matching

## Blocking dependency status

The dedicated Supabase project for this CRM **did not exist as of 2026-07-03**. Tanush is creating it on the company account. Until credentials land in `.env` (see `.env.example`), the app cannot run and nothing here is verified end-to-end. Run `schema.sql` in the new project's SQL editor before first launch. Do NOT point this at the kairosintern Supabase project or a local Postgres.

## Non-negotiable design decisions (from the spec, confirmed by Yajat)

- **No auth.** User-select landing screen only; selection pre-fills owner fields but never locks them.
- **All due/overdue/stale date logic in America/Chicago**, unconditionally. Timestamps stored UTC.
- `last_action_date` and "current state" are **derived** from `activities` (see the `account_overview` view in `schema.sql`), never stored on `accounts`.
- Activity inserts sync the parent account's `next_action`/`next_action_due_date` via a Postgres trigger (`sync_account_next_action`) so it is atomic — do not replicate that update in Python.
- `users` and `channel_types` are admin-editable tables; every other enum is a fixed constant in `utils/constants.py` (deliberate v1 scope decision — do not convert them to tables unless asked).
- Duplicate detection **warns and lets the user decide** — never silently block, skip, or merge.
- No auto-refresh on any page with an edit form (a rerun blows away unsaved input). Dashboard read-only fragment only.

## Duplicate detection tuning

`NAME_SIMILARITY_THRESHOLD` in `utils/dedup.py` (default 85) is a starting default, not tuned. If it produces obviously wrong results in real usage, flag to Yajat — do not silently adjust.
