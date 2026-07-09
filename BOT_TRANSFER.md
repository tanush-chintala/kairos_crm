# Transferring the text bot to Tanush's accounts

The CRM text bot is live and tested. It currently runs on Yajat's SendBlue
sandbox and the shared Gemini key. This guide moves both to accounts Tanush
owns. Nothing in the code or the Supabase project changes - only credentials.

## 1. Create the SendBlue account

1. Go to sendblue.com and sign up (free sandbox plan, no credit card).
2. In the dashboard, open the API settings page. Copy BOTH values:
   - API Key ID
   - API Secret Key
   The API rejects requests unless both are sent, so grab the pair.
3. Note the phone number SendBlue assigns to the account - that becomes the
   new number everyone texts.

Sandbox limits to know about: max 10 verified contacts, shared relay line
(inbound texts can occasionally lag by up to a minute), and each team member
must text the number once before it can reply to them. The $100/mo AI Agent
plan gets a dedicated line and faster relay if the lag ever becomes a problem.

## 2. Create the Gemini API key

1. Go to aistudio.google.com/apikey while logged into the company Google
   account.
2. Click "Create API key" and copy it. Free tier is plenty: the bot uses
   gemini-3.1-flash-lite (same model as the lead-gen project). A separate key
   keeps the CRM bot's quota isolated from the Donut Scraper's usage.

## 3. Swap the credentials into the bot

Requires the Supabase CLI logged into the project (`supabase login`, then
`supabase link --project-ref hxtskdwnhjrjljftccst`). From the repo root:

```
supabase secrets set \
  SENDBLUE_API_KEY_ID=<new key id> \
  SENDBLUE_API_SECRET_KEY=<new secret> \
  SENDBLUE_FROM_NUMBER=<new sendblue number, +1XXXXXXXXXX> \
  GEMINI_API_KEY=<new gemini key>
```

The function picks up new secrets automatically - no redeploy needed. Also
update `.env` locally so debug testing keeps working.

## 4. Register the webhook on the new SendBlue account

The new account starts with no webhooks. Register the bot's endpoint (the
BOT_WEBHOOK_TOKEN value is in `.env`; keep it or generate a new one and set it
as a secret too):

```
curl -X POST "https://api.sendblue.com/api/account/webhooks" \
  -H "sb-api-key-id: <new key id>" \
  -H "sb-api-secret-key: <new secret>" \
  -H "Content-Type: application/json" \
  -d '{"webhooks": ["https://hxtskdwnhjrjljftccst.supabase.co/functions/v1/sendblue-bot?token=<BOT_WEBHOOK_TOKEN>"], "type": "receive"}'
```

## 5. Re-add the team as contacts

For each team member (numbers live in the `users` table):

```
curl -X POST "https://api.sendblue.com/api/v2/contacts" \
  -H "sb-api-key-id: <new key id>" \
  -H "sb-api-secret-key: <new secret>" \
  -H "Content-Type: application/json" \
  -d '{"number": "+1XXXXXXXXXX", "first_name": "<Name>"}'
```

Then everyone saves the new number and texts it once (any message) to complete
sandbox verification.

## 6. Verify

Text the new number "whats due today". Expect a typing indicator within a few
seconds and an answer citing real CRM data. For an edit, text something like
"log a call on <account>, they want a demo friday" - the bot proposes the
exact change and only saves after a yes (any casing counts). The saved
confirmation always reflects the real database write.

If nothing comes back, check in order: the webhook is registered on the new
account (step 4), the sender's phone matches their `users.phone` row, and the
function logs in the Supabase dashboard under Edge Functions > sendblue-bot.
