# Kairos CRM

Internal CRM for the Kairos sales team: dental-practice accounts, contacts, activity log, demos, email templates, dashboard with due/overdue/stale follow-ups, CSV import with duplicate detection. Spec in `CRM_SPEC.md`; developer conventions in `CLAUDE.md`.

## Setup

1. Get the dedicated CRM Supabase project credentials (Tanush is creating it on the company account — this must be its own project, separate from the lead-gen one).
2. In that project's SQL editor, run `schema.sql` once. It creates all tables, the `account_overview` view, the next-action sync trigger, and seeds the four users and initial channel types.
3. Copy `.env.example` to `.env` and fill in `SUPABASE_URL` and `SUPABASE_KEY` (or set them in Streamlit Cloud secrets when deploying).
4. Install and run:

```
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- No login: pick your name on the landing screen. It pre-fills owner fields and is always overridable.
- All due/overdue/stale logic runs on Central Time (America/Chicago).
- Users and channel types are managed on the Settings page; all other dropdowns are fixed for v1.
- Duplicate detection warns on matching phone/email/website or similar names within a city — it never blocks or merges automatically. Threshold lives in `utils/dedup.py`.
