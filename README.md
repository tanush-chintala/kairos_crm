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

## Text bot (SendBlue + Gemini)

Team members can text the CRM in natural language (what's due today, lead details, log calls, update stages). Inbound texts hit a Supabase Edge Function (`supabase/functions/sendblue-bot`), which matches the sender's number against `users.phone`, runs Gemini with CRM tools against the same database, and replies over iMessage/SMS. Everything runs on free tiers: SendBlue sandbox, Supabase Edge Functions, Gemini free tier.

Setup (one time):

1. If the database predates the bot, run in the SQL editor:

```sql
alter table users add column phone text;
create table bot_messages (
    id bigint generated always as identity primary key,
    user_id bigint not null references users(id) on delete cascade,
    role text not null check (role in ('user', 'model')),
    content text not null,
    created_at timestamptz not null default now()
);
create index bot_messages_user_idx on bot_messages (user_id, created_at desc);
```

2. Set each team member's E.164 phone on their `users` row.
3. Create a SendBlue account (free sandbox) and a Gemini API key (aistudio.google.com). Then:

```
supabase login
supabase link --project-ref <ref>
supabase secrets set GEMINI_API_KEY=... SENDBLUE_API_KEY_ID=... SENDBLUE_API_SECRET_KEY=... BOT_WEBHOOK_TOKEN=<random string>
supabase functions deploy sendblue-bot
```

4. Register the webhook with SendBlue (POST `/api/account/webhooks`) pointing at `https://<ref>.functions.supabase.co/sendblue-bot?token=<BOT_WEBHOOK_TOKEN>` for the `receive` event.
5. Each member adds the SendBlue number as a verified contact (free tier requires texting it once).

Test without SendBlue by POSTing a fake payload to the function URL with `&debug=1` — the reply comes back in the HTTP response.

## Notes

- No login: pick your name on the landing screen. It pre-fills owner fields and is always overridable.
- All due/overdue/stale logic runs on Central Time (America/Chicago).
- Users and channel types are managed on the Settings page; all other dropdowns are fixed for v1.
- Duplicate detection warns on matching phone/email/website or similar names within a city — it never blocks or merges automatically. Threshold lives in `utils/dedup.py`.
