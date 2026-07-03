# Kairos CRM — Handover & Setup Guide

Goal: stand this CRM up entirely on **Kairos-owned** accounts, with none of Yajat's
personal credentials involved. Unlike the lead-gen tool, this app touches exactly **one**
external service: a Supabase database. There are no Google, Outscraper, Gemini, or Adzuna
keys here. So the whole setup is: create a GitHub repo, create a Supabase project, run one
SQL file, deploy to Streamlit Cloud, and paste two secrets.

Everything you create below produces exactly **two** values (`SUPABASE_URL`, `SUPABASE_KEY`).
Both get pasted into one place: the Streamlit Cloud secrets manager (Section 4). Nothing in
the code needs editing.

---

## 0. What the app is (30-second overview)

- **What it does:** internal CRM for the sales team (Tanush, Aditya, Sanjana, Adhira) to track
  dental-practice leads — accounts, contacts, an activity log, demos, email templates, and a
  dashboard of due/overdue/stale follow-ups. Full feature spec is in `CRM_SPEC.md`.
- **Frontend/host:** Streamlit multi-page app, intended for **Streamlit Community Cloud**. It
  auto-builds from the GitHub repo's `main` branch — every push to `main` redeploys in ~1 minute.
- **Database:** Supabase (Postgres), accessed via the `supabase-py` client. This is the single
  source of truth — the app holds nothing meaningful in memory between requests.
- **Auth:** none by design. Anyone with the URL picks their name on a landing screen (spec
  Section 3). Do not add a login; that was an explicit product decision. Keep the deployed URL
  within the team.

The complete list of credentials the app expects:

| Secret name | Service | Currently on |
|---|---|---|
| `SUPABASE_URL` | Supabase | **Nothing yet — must be created (see below)** |
| `SUPABASE_KEY` | Supabase | **Nothing yet — must be created (see below)** |

> **Important:** this CRM was built against a **dedicated, brand-new Supabase project that did
> not exist yet** at handover time. It must be its **own** project — do **not** point it at the
> lead-gen tool's Supabase project (they share nothing and must stay isolated so an experiment on
> one can't corrupt the other; that separation is the whole reason this is a separate repo). It
> was never run against a real database by Yajat, so treat Section 5's verification as the true
> "does it work" test.

---

## 1. GitHub repository

1. Create a repo under a **Kairos-owned GitHub org/account**, e.g. `kairos-crm`, and push this
   project to it (`git init` is already done locally; add the remote and push `main`).
2. If Yajat created it under his account first, transfer it: Settings → Transfer ownership, or add
   the team as admins under Settings → Collaborators.
3. You'll connect this repo to Streamlit Cloud in Section 4.

Nothing in the code is personal to Yajat — only the secrets are. The code can stay as-is.

Do **not** commit a `.env` file — it's gitignored on purpose. Secrets live only in Streamlit
Cloud (Section 4), or in a local untracked `.env` for local dev (Section 6).

---

## 2. Supabase (database) — create the project

1. Go to <https://supabase.com> → sign in with the **company** account → **New project**.
2. Name it e.g. `kairos-crm`, pick a region close to the team (DFW → US East or US Central is
   fine), set a database password and save it somewhere safe.
3. Wait for it to finish provisioning (~2 minutes).
4. Open **Project Settings → API** and copy two things:
   - **Project URL** → this is `SUPABASE_URL` (looks like `https://abcdefgh.supabase.co`).
   - **service_role key**, under "Project API keys" → this is `SUPABASE_KEY`. The app both reads
     and writes, so it needs the **service_role** key, **not** the anon/public key.

> Why service_role: there is no per-user auth or row-level security in this app (by design), so the
> app connects with a single privileged key and is only ever exposed to the trusted team. Keep this
> key in Streamlit secrets only — never commit it, never put it in the frontend.

---

## 3. Supabase — create the schema

The repo ships a complete `schema.sql` at the project root. It creates all seven tables
(`users`, `channel_types`, `accounts`, `contacts`, `activities`, `demos`, `email_templates`),
the indexes, a trigger that keeps each account's "next action" in sync with its activity log, a
view the app reads from (`account_overview`), and it seeds the four team members and the initial
channel types.

1. In your new Supabase project, open **SQL Editor → New query**.
2. Open `schema.sql` from this repo, copy its **entire** contents, paste into the editor.
3. Click **Run**. You should see it succeed with no errors.
4. Sanity check: open **Table Editor** and confirm the `users` table has four rows (Tanush,
   Aditya, Sanjana, Adhira) and `channel_types` has six (Donut Visit, Cold Visit, Apollo Cold
   Outreach, Conference, Referral, Other).

Run `schema.sql` **once** on a fresh project. It is not written to be re-run on top of itself
(the `create table` statements will error if the tables already exist) — that's fine, it's a
one-time setup step. If you need to start over, delete the tables (or the whole project) first.

> Leave Row Level Security **disabled** on every table (Supabase may prompt you to enable it).
> This app has no auth and connects with the service_role key; enabling RLS without policies would
> just block all access. This is deliberate — see `CRM_SPEC.md` Section 3.

---

## 4. Streamlit Community Cloud (host) + entering the secrets

1. Go to <https://share.streamlit.io> → sign in with the **company** account (the one that
   owns/collaborates on the GitHub repo from Section 1).
2. **Create app** → pick the repo, branch `main`, main file `app.py` → **Deploy**.
3. Open the app → **Settings (⋮ / Manage app) → Secrets**.
4. Paste the block below, filling in the two values from Section 2. Format is TOML:

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_KEY = "your-supabase-service-role-key"
```

5. Save. Streamlit reboots the app automatically with the new secrets.

That's the entire secret set — just those two lines.

---

## 5. Final verification checklist

After the app reboots with the secrets, confirm it actually works end-to-end. This matters more
than usual because the app was never run against a live database before handover.

- [ ] App loads and shows the **"Who are you?"** landing screen with four name buttons (this alone
      verifies `SUPABASE_URL`/`SUPABASE_KEY` are correct and the `users` table seeded — if the
      credentials are missing or wrong, you'll see a red error explaining exactly that instead).
- [ ] Click a name → you land on the **Dashboard** with an "Acting as: [name]" line in the sidebar.
- [ ] **Accounts → Add account:** create a test practice. It saves and appears in the list.
- [ ] Add a second account with the **same phone number or a similar name in the same city** →
      the duplicate warning fires and lets you save anyway or discard (it should never hard-block).
- [ ] Open the account → **Activity Log:** log an activity with a "next action" and due date. Confirm
      the account's next-action fields update to match (this verifies the Supabase trigger).
- [ ] Add a **contact** and a **demo** under that account — both save.
- [ ] Set a next-action due date of today on an account → it appears under **Due Today** on the
      Dashboard. Set one in the past → it appears under **Overdue**.
- [ ] **Email Templates:** create, edit, and delete a template.
- [ ] **Settings:** add a channel type and deactivate a user → the deactivated user disappears from
      the owner dropdowns but historical records still show their name.
- [ ] **CSV Import:** upload a small CSV, map columns, preview, and commit a couple of rows.
- [ ] Delete your test data when done (or leave it — it's a fresh DB, your call).

If the landing screen shows a credentials error, re-check Section 2 (right URL, **service_role**
key not anon) and that Section 3's `schema.sql` ran successfully.

---

## 6. Local development (optional)

To run it on your own machine instead of / before deploying to the cloud:

1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in the same `SUPABASE_URL` / `SUPABASE_KEY` from
   Section 2. (`.env` is gitignored — it will not be committed.)
3. `streamlit run app.py` and open the `localhost` URL it prints.

Local and cloud can safely point at the **same** Supabase project. If you'd rather sandbox, spin
up a second Supabase project and run `schema.sql` in it too.

---

## 7. Things to know for later (not required to launch)

- **Duplicate-detection threshold** — the name-similarity cutoff lives in `utils/dedup.py`
  (`NAME_SIMILARITY_THRESHOLD`, currently 85). It's a starting default, not tuned against real
  data. If it flags too much or misses obvious duplicates once the team is using it, tell Yajat
  rather than guessing at a new number.
- **Admin-editable lists** — only `users` and `channel_types` are editable from the in-app
  Settings page. Everything else (pipeline stages, activity types, lost reasons, competitor tools)
  is a fixed list in `utils/constants.py` and needs a code change to alter. That was the agreed v1
  scope; making the others editable is a small follow-up if the team asks.
- **All date logic is Central Time** (America/Chicago), hardcoded on purpose — the whole team is
  DFW-based. Don't add timezone settings.
- **No auto-pipe from the lead-gen tool** — CSV import is the only way data comes in for v1, by
  design. If a direct integration is wanted later, it's new work, not something half-built here.
- **Developer conventions** for anyone editing the code are in `CLAUDE.md`.
