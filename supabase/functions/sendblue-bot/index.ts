// SendBlue text bot for the Kairos CRM. Receives inbound iMessage/SMS webhooks,
// matches the sender to a CRM user by phone, runs a Gemini tool-use loop against
// Supabase (same rules as the app: activities drive next_action via the DB
// trigger; account_overview is the read model), and replies via SendBlue.
//
// Secrets (supabase secrets set ...): GEMINI_API_KEY, SENDBLUE_API_KEY_ID,
// SENDBLUE_API_SECRET_KEY, BOT_WEBHOOK_TOKEN. Optional: GEMINI_MODEL,
// GEMINI_FALLBACK_MODEL, SENDBLUE_FROM_NUMBER.
//
// The webhook URL registered with SendBlue must include ?token=<BOT_WEBHOOK_TOKEN>.
// Append &debug=1 to get the reply in the HTTP response instead of a text
// (for curl testing before SendBlue is wired up).

import { createClient } from "npm:@supabase/supabase-js@2";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
);

const GEMINI_API_KEY = Deno.env.get("GEMINI_API_KEY") ?? "";
const GEMINI_MODEL = Deno.env.get("GEMINI_MODEL") ?? "gemini-2.5-flash";
const GEMINI_FALLBACK_MODEL = Deno.env.get("GEMINI_FALLBACK_MODEL") ?? "gemini-2.5-flash-lite";
const SENDBLUE_API_KEY_ID = Deno.env.get("SENDBLUE_API_KEY_ID") ?? "";
const SENDBLUE_API_SECRET_KEY = Deno.env.get("SENDBLUE_API_SECRET_KEY") ?? "";
const SENDBLUE_FROM_NUMBER = Deno.env.get("SENDBLUE_FROM_NUMBER") ?? "";
const BOT_WEBHOOK_TOKEN = Deno.env.get("BOT_WEBHOOK_TOKEN") ?? "";

// Mirrors utils/constants.py — keep in sync.
const PIPELINE_STAGES = [
  "New Lead",
  "Contacted",
  "Interested",
  "Demo Scheduled",
  "Waiting on Decision",
  "Onboarding",
  "Closed Won",
  "Closed Lost",
  "Nurture Later",
];
const CLOSED_STAGES = ["Closed Won", "Closed Lost", "Nurture Later"];
const ACTIVITY_TYPES = [
  "In-person visit",
  "Phone call",
  "Email sent",
  "Demo scheduled",
  "Demo completed",
  "Follow-up completed",
  "Pricing/onboarding info sent",
  "No response",
  "Other",
];

const ACCOUNT_SUMMARY_COLS =
  "id, practice_name, city, pipeline_stage, kairos_owner_id, next_action, next_action_due_date, last_action_date";

function chicagoToday(): string {
  return new Date().toLocaleDateString("en-CA", { timeZone: "America/Chicago" });
}

function chicagoWeekday(): string {
  return new Date().toLocaleDateString("en-US", { timeZone: "America/Chicago", weekday: "long" });
}

function phoneDigits(raw: string): string {
  return raw.replace(/\D/g, "").slice(-10);
}

function isDate(s: unknown): s is string {
  return typeof s === "string" && /^\d{4}-\d{2}-\d{2}$/.test(s);
}

const TOOL_DECLARATIONS = [
  {
    name: "get_due_today",
    description:
      "Accounts owned by the current user whose next action is due today or overdue (America/Chicago). Use for 'what's due', 'what do I have today'.",
    parameters: { type: "OBJECT", properties: {} },
  },
  {
    name: "list_my_accounts",
    description:
      "Open accounts owned by the current user with stage, next action, and due date. Use for 'what am I working on'. Optionally filter by pipeline stage.",
    parameters: {
      type: "OBJECT",
      properties: {
        stage: { type: "STRING", description: `One of: ${PIPELINE_STAGES.join(", ")}` },
        include_closed: { type: "BOOLEAN", description: "Include Closed Won/Closed Lost/Nurture Later accounts" },
      },
    },
  },
  {
    name: "find_account",
    description:
      "Search all accounts (any owner) by practice name fragment. Returns candidate matches with ids. Always use this to resolve a name before get_account_details, log_activity, or update_account.",
    parameters: {
      type: "OBJECT",
      properties: { query: { type: "STRING", description: "Practice name or part of it" } },
      required: ["query"],
    },
  },
  {
    name: "get_account_details",
    description:
      "Full detail for one account: every field plus contacts, recent activities, and demos.",
    parameters: {
      type: "OBJECT",
      properties: { account_id: { type: "INTEGER" } },
      required: ["account_id"],
    },
  },
  {
    name: "log_activity",
    description:
      "Log an activity on an account, attributed to the current user, dated today unless another date is given. If next_action/next_action_due_date are provided the account's current next action is updated automatically.",
    parameters: {
      type: "OBJECT",
      properties: {
        account_id: { type: "INTEGER" },
        activity_type: { type: "STRING", description: `One of: ${ACTIVITY_TYPES.join(", ")}` },
        summary: { type: "STRING" },
        date: { type: "STRING", description: "YYYY-MM-DD, defaults to today in Chicago" },
        next_action: { type: "STRING" },
        next_action_due_date: { type: "STRING", description: "YYYY-MM-DD" },
      },
      required: ["account_id", "activity_type", "summary"],
    },
  },
  {
    name: "update_account",
    description:
      "Update fields on an account directly (stage change, contact info, decision maker, etc). Do NOT use this for next_action changes that stem from an activity — log_activity handles those.",
    parameters: {
      type: "OBJECT",
      properties: {
        account_id: { type: "INTEGER" },
        pipeline_stage: { type: "STRING", description: `One of: ${PIPELINE_STAGES.join(", ")}` },
        next_action: { type: "STRING" },
        next_action_due_date: { type: "STRING", description: "YYYY-MM-DD" },
        best_contact: { type: "STRING" },
        decision_maker: { type: "STRING" },
        decision_maker_reached: { type: "STRING", description: "Unknown, Yes, or No" },
        lost_reason: { type: "STRING" },
        practice_phone: { type: "STRING" },
        practice_email: { type: "STRING" },
        city: { type: "STRING" },
        pms: { type: "STRING" },
        competitor_tool: { type: "STRING" },
      },
      required: ["account_id"],
    },
  },
];

// deno-lint-ignore no-explicit-any
type ToolArgs = Record<string, any>;

type StagedCall = { name: string; args: ToolArgs };

const WRITE_TOOLS = new Set(["log_activity", "update_account"]);

// Writes are gated in code, not by the model: without commit the tool only
// validates and stages, and the actual insert/update happens in
// executePending after the user texts an affirmative.
async function execTool(name: string, args: ToolArgs, userId: number, commit = false): Promise<unknown> {
  try {
    switch (name) {
      case "get_due_today": {
        const { data, error } = await supabase
          .from("account_overview")
          .select(ACCOUNT_SUMMARY_COLS)
          .eq("kairos_owner_id", userId)
          .lte("next_action_due_date", chicagoToday())
          .not("pipeline_stage", "in", `(${CLOSED_STAGES.map((s) => `"${s}"`).join(",")})`)
          .order("next_action_due_date");
        if (error) return { error: error.message };
        return { today: chicagoToday(), accounts: data };
      }
      case "list_my_accounts": {
        let q = supabase
          .from("account_overview")
          .select(ACCOUNT_SUMMARY_COLS)
          .eq("kairos_owner_id", userId);
        if (args.stage) q = q.eq("pipeline_stage", args.stage);
        else if (!args.include_closed) {
          q = q.not("pipeline_stage", "in", `(${CLOSED_STAGES.map((s) => `"${s}"`).join(",")})`);
        }
        const { data, error } = await q.order("next_action_due_date", { ascending: true, nullsFirst: false });
        return error ? { error: error.message } : { accounts: data };
      }
      case "find_account": {
        const query = String(args.query ?? "").trim();
        if (!query) return { error: "query is required" };
        let { data } = await supabase
          .from("account_overview")
          .select(ACCOUNT_SUMMARY_COLS)
          .ilike("practice_name", `%${query}%`)
          .limit(8);
        if (!data?.length) {
          const words = query.split(/\s+/).filter((w: string) => w.length > 2);
          if (words.length) {
            const ors = words.map((w: string) => `practice_name.ilike.%${w}%`).join(",");
            data = (
              await supabase.from("account_overview").select(ACCOUNT_SUMMARY_COLS).or(ors).limit(8)
            ).data;
          }
        }
        if (!data?.length) return { matches: [], note: "No accounts matched. Ask the user to rephrase the name." };
        return { matches: data };
      }
      case "get_account_details": {
        const id = Number(args.account_id);
        const [account, contacts, activities, demos] = await Promise.all([
          supabase.from("account_overview").select("*").eq("id", id).maybeSingle(),
          supabase.from("contacts").select("name, role, email, phone").eq("account_id", id),
          supabase
            .from("activities")
            .select("date, activity_type, summary, next_action, next_action_due_date")
            .eq("account_id", id)
            .order("date", { ascending: false })
            .order("id", { ascending: false })
            .limit(6),
          supabase
            .from("demos")
            .select("demo_date, status, attendees, pain_points, objections, follow_up_required")
            .eq("account_id", id)
            .order("demo_date", { ascending: false }),
        ]);
        if (!account.data) return { error: `No account with id ${id}` };
        return {
          account: account.data,
          contacts: contacts.data ?? [],
          recent_activities: activities.data ?? [],
          demos: demos.data ?? [],
        };
      }
      case "log_activity": {
        if (!ACTIVITY_TYPES.includes(args.activity_type)) {
          return { error: `activity_type must be one of: ${ACTIVITY_TYPES.join(", ")}` };
        }
        if (args.next_action_due_date && !isDate(args.next_action_due_date)) {
          return { error: "next_action_due_date must be YYYY-MM-DD" };
        }
        if (!commit) {
          return {
            status: "needs_confirmation",
            note: "Staged, not saved. Relay the exact proposed change to the user and ask them to reply yes to save.",
          };
        }
        const row: ToolArgs = {
          account_id: Number(args.account_id),
          date: isDate(args.date) ? args.date : chicagoToday(),
          kairos_owner_id: userId,
          activity_type: args.activity_type,
          summary: args.summary ?? null,
          next_action: args.next_action ?? null,
          next_action_due_date: args.next_action_due_date ?? null,
        };
        // The activities_sync_next_action trigger updates the parent account's
        // next_action fields atomically with this insert — never update here too.
        const { error } = await supabase.from("activities").insert(row);
        return error ? { error: error.message } : { ok: true, logged: row };
      }
      case "update_account": {
        const allowed = [
          "pipeline_stage",
          "next_action",
          "next_action_due_date",
          "best_contact",
          "decision_maker",
          "decision_maker_reached",
          "lost_reason",
          "practice_phone",
          "practice_email",
          "city",
          "pms",
          "competitor_tool",
        ];
        const fields: ToolArgs = {};
        for (const k of allowed) if (args[k] !== undefined) fields[k] = args[k];
        if (fields.pipeline_stage && !PIPELINE_STAGES.includes(fields.pipeline_stage)) {
          return { error: `pipeline_stage must be one of: ${PIPELINE_STAGES.join(", ")}` };
        }
        if (fields.next_action_due_date && !isDate(fields.next_action_due_date)) {
          return { error: "next_action_due_date must be YYYY-MM-DD" };
        }
        if (!Object.keys(fields).length) return { error: "No editable fields provided" };
        if (!commit) {
          return {
            status: "needs_confirmation",
            note: "Staged, not saved. Relay the exact proposed change to the user and ask them to reply yes to save.",
          };
        }
        const { error } = await supabase.from("accounts").update(fields).eq("id", Number(args.account_id));
        return error ? { error: error.message } : { ok: true, updated: fields };
      }
      default:
        return { error: `Unknown tool ${name}` };
    }
  } catch (e) {
    return { error: String(e) };
  }
}

const AFFIRMATIVE_RE =
  /^\s*(y|ya|yes+|yep|yeah|yup|ok|okay|k|sure|confirm|confirmed|go ahead|sounds good|do it|save( it)?|yes please)[\s!.?]*$/i;

const PENDING_TTL_MS = 60 * 60 * 1000;

async function loadPending(userId: number): Promise<StagedCall[]> {
  const { data } = await supabase
    .from("bot_pending_writes")
    .select("calls, created_at")
    .eq("user_id", userId)
    .maybeSingle();
  if (!data || Date.now() - new Date(data.created_at).getTime() > PENDING_TTL_MS) return [];
  return data.calls as StagedCall[];
}

async function savePending(userId: number, calls: StagedCall[]) {
  await supabase
    .from("bot_pending_writes")
    .upsert({ user_id: userId, calls, created_at: new Date().toISOString() });
}

async function clearPending(userId: number) {
  await supabase.from("bot_pending_writes").delete().eq("user_id", userId);
}

async function accountName(id: number): Promise<string> {
  const { data } = await supabase.from("accounts").select("practice_name").eq("id", id).maybeSingle();
  return data?.practice_name ?? `account ${id}`;
}

async function executePending(userId: number, calls: StagedCall[]): Promise<string> {
  const lines: string[] = [];
  for (const call of calls) {
    const result = (await execTool(call.name, call.args, userId, true)) as ToolArgs;
    const name = await accountName(Number(call.args.account_id));
    if (result?.error) {
      lines.push(`Could not save the change on ${name}: ${result.error}`);
    } else if (call.name === "log_activity") {
      let line = `Saved. ${call.args.activity_type} logged on ${name}`;
      if (call.args.next_action) {
        line += `; next action "${call.args.next_action}"`;
        if (call.args.next_action_due_date) line += ` due ${call.args.next_action_due_date}`;
      }
      lines.push(line + ".");
    } else {
      const fields = Object.entries(call.args)
        .filter(([k]) => k !== "account_id")
        .map(([k, v]) => `${k.replaceAll("_", " ")}: ${v}`)
        .join(", ");
      lines.push(`Saved. Updated ${name} - ${fields}.`);
    }
  }
  return lines.join("\n");
}

function systemPrompt(userName: string): string {
  return [
    `You are the Kairos CRM assistant, texting with ${userName}, a member of the Kairos dental-AI sales team.`,
    `Today is ${chicagoWeekday()}, ${chicagoToday()} (America/Chicago). All dates use YYYY-MM-DD. Resolve relative days like 'Friday' or 'tomorrow' from this exact date and double-check the weekday arithmetic.`,
    "You answer questions about their sales pipeline and make edits, using the provided tools. Never invent accounts or data; if a tool returns nothing, say so.",
    "Always resolve an account name with find_account before reading details or editing. If multiple accounts plausibly match, list them briefly and ask which one instead of guessing.",
    "When the user reports something that happened (a call, a visit, an email, a demo), log it with log_activity and include any new next action there. Use update_account only for direct field edits like stage or contact info.",
    "Writes are two-step and the system enforces it. When the user requests a change, call log_activity or update_account right away with professionalized field values - the system stages the change instead of saving it and returns needs_confirmation. Then reply with one short proposal naming the account and quoting exactly what will be saved, ending with 'Reply yes to save.' Example: 'On Feel Good Dentistry I'll log a phone call under your name with summary \"Spoke with the office manager; interested in a demo\" and set the next action to \"Tanush to review pricing options\" due 2026-07-10. Reply yes to save.'",
    "You cannot save anything yourself. The system saves the staged change only when the user replies with an affirmative, and it sends its own saved-confirmation text. Never claim that something was logged, saved, or updated. If the user replies with corrections instead of yes, call the tool again with corrected values and propose again.",
    "Professionalize everything you save. The team texts in quick casual language, all caps, slang, shorthand - never store their words verbatim. Rewrite summaries and next actions into concise, dashboard-ready CRM language: proper capitalization, full words, neutral professional tone, third person, facts preserved exactly. Example: a text of 'CALLED FEEL GOOD THEY WANT TANUSH TO LOOK IT OVER' becomes summary 'Phone call with the practice' and next action 'Tanush to review the account'. Show the professionalized wording in your confirmation proposal so the user approves the final text.",
    `Pipeline stages: ${PIPELINE_STAGES.join(", ")}.`,
    `Activity types: ${ACTIVITY_TYPES.join(", ")}.`,
    "You are texting: reply in plain conversational text. No markdown, no asterisks, no emojis, no headers. Keep replies compact - short lines, one item per line for lists. Round nothing; quote fields as stored.",
  ].join("\n");
}

// deno-lint-ignore no-explicit-any
type Content = { role: string; parts: any[] };

async function geminiRequest(model: string, sys: string, contents: Content[]) {
  const resp = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-goog-api-key": GEMINI_API_KEY },
      body: JSON.stringify({
        system_instruction: { parts: [{ text: sys }] },
        contents,
        tools: [{ function_declarations: TOOL_DECLARATIONS }],
        generationConfig: { temperature: 0.2, thinkingConfig: { thinkingBudget: 0 } },
      }),
    },
  );
  return resp;
}

async function runAgent(
  userId: number,
  userName: string,
  contents: Content[],
): Promise<{ text: string; staged: StagedCall[] }> {
  const sys = systemPrompt(userName);
  let model = GEMINI_MODEL;
  let emptyRetries = 0;
  const staged: StagedCall[] = [];
  for (let step = 0; step < 8; step++) {
    const resp = await geminiRequest(model, sys, contents);
    if (!resp.ok) {
      if (model !== GEMINI_FALLBACK_MODEL && (resp.status === 429 || resp.status >= 500)) {
        model = GEMINI_FALLBACK_MODEL;
        continue;
      }
      const detail = await resp.text();
      console.error(`Gemini error ${resp.status}: ${detail.slice(0, 500)}`);
      return {
        text: "Sorry, the assistant is unavailable right now (model error). Try again in a minute.",
        staged: [],
      };
    }
    const data = await resp.json();
    const parts = data.candidates?.[0]?.content?.parts ?? [];
    // deno-lint-ignore no-explicit-any
    const calls = parts.filter((p: any) => p.functionCall);
    if (!calls.length) {
      // deno-lint-ignore no-explicit-any
      const text = parts.map((p: any) => (p.thought ? "" : p.text ?? "")).join("").trim();
      if (text) return { text, staged };
      // Gemini intermittently returns a candidate with no text and no tool
      // call; retry, then switch models before giving up.
      console.error(`Empty Gemini response (finishReason=${data.candidates?.[0]?.finishReason ?? "none"})`);
      emptyRetries += 1;
      if (emptyRetries === 2 && model !== GEMINI_FALLBACK_MODEL) model = GEMINI_FALLBACK_MODEL;
      if (emptyRetries <= 3) continue;
      return { text: "Sorry, I did not get a response. Try rephrasing.", staged };
    }
    contents.push({ role: "model", parts });
    const responses = await Promise.all(
      // deno-lint-ignore no-explicit-any
      calls.map(async (c: any) => {
        const name = c.functionCall.name;
        const args = c.functionCall.args ?? {};
        const result = (await execTool(name, args, userId)) as ToolArgs;
        if (WRITE_TOOLS.has(name) && result?.status === "needs_confirmation") {
          const entry = { name, args };
          if (!staged.some((s) => JSON.stringify(s) === JSON.stringify(entry))) staged.push(entry);
        }
        return { functionResponse: { name, response: { result } } };
      }),
    );
    contents.push({ role: "user", parts: responses });
  }
  return { text: "Sorry, that request took too many steps. Try something more specific.", staged };
}

function sendblueHeaders(): HeadersInit {
  return {
    "Content-Type": "application/json",
    "sb-api-key-id": SENDBLUE_API_KEY_ID,
    "sb-api-secret-key": SENDBLUE_API_SECRET_KEY,
  };
}

async function sendText(number: string, content: string, fromNumber: string) {
  const body: Record<string, unknown> = { number, content };
  // SendBlue rejects sends without from_number on this account. The inbound
  // payload's to_number is the line the user texted, so replying from it is
  // always correct; the env var is only a fallback.
  const from = fromNumber || SENDBLUE_FROM_NUMBER;
  if (from) body.from_number = from;
  const resp = await fetch("https://api.sendblue.com/api/send-message", {
    method: "POST",
    headers: sendblueHeaders(),
    body: JSON.stringify(body),
  });
  if (!resp.ok) console.error(`SendBlue send failed ${resp.status}: ${(await resp.text()).slice(0, 300)}`);
}

function sendTypingIndicator(number: string, fromNumber: string) {
  if (!SENDBLUE_API_KEY_ID) return;
  fetch("https://api.sendblue.com/api/send-typing-indicator", {
    method: "POST",
    headers: sendblueHeaders(),
    body: JSON.stringify({ number, from_number: fromNumber || SENDBLUE_FROM_NUMBER }),
  }).catch(() => {});
}

async function loadHistory(userId: number): Promise<Content[]> {
  const since = new Date(Date.now() - 24 * 3600 * 1000).toISOString();
  // Order by id, not created_at: the user/model pair is inserted in one
  // statement and can share a timestamp, which scrambles the turn order.
  const { data } = await supabase
    .from("bot_messages")
    .select("role, content")
    .eq("user_id", userId)
    .gte("created_at", since)
    .order("id", { ascending: false })
    .limit(12);
  return (data ?? []).reverse().map((m) => ({ role: m.role, parts: [{ text: m.content }] }));
}

async function saveExchange(userId: number, userText: string, reply: string) {
  await supabase.from("bot_messages").insert([
    { user_id: userId, role: "user", content: userText },
    { user_id: userId, role: "model", content: reply },
  ]);
}

Deno.serve(async (req) => {
  const url = new URL(req.url);
  if (!BOT_WEBHOOK_TOKEN || url.searchParams.get("token") !== BOT_WEBHOOK_TOKEN) {
    return new Response("forbidden", { status: 403 });
  }
  if (req.method !== "POST") return new Response("ok");

  let payload: Record<string, unknown>;
  try {
    payload = await req.json();
  } catch {
    return new Response("bad request", { status: 400 });
  }

  if (payload.is_outbound === true) return new Response("ignored outbound");
  const fromNumber = String(payload.from_number ?? "");
  const content = String(payload.content ?? "").trim().slice(0, 2000);
  if (!fromNumber || !content) return new Response("ignored empty");

  const { data: users } = await supabase.from("users").select("id, name, phone").eq("active", true);
  const user = (users ?? []).find((u) => u.phone && phoneDigits(u.phone) === phoneDigits(fromNumber));
  if (!user) {
    console.log(`Ignored message from unknown number ${fromNumber}`);
    return new Response("ignored unknown sender");
  }

  const debug = url.searchParams.get("debug") === "1";
  const lineNumber = String(payload.to_number ?? "");
  sendTypingIndicator(fromNumber, lineNumber);
  const sender = user;

  async function respond(reply: string): Promise<Response> {
    if (debug) {
      await saveExchange(sender.id, content, reply);
      return new Response(JSON.stringify({ user: sender.name, reply }), {
        headers: { "Content-Type": "application/json" },
      });
    }
    await Promise.all([sendText(fromNumber, reply, lineNumber), saveExchange(sender.id, content, reply)]);
    return new Response("ok");
  }

  // The confirmation gate lives here, not in the model: an affirmative reply
  // executes the staged writes deterministically; anything else discards them
  // and falls through to the model, which can re-propose with corrections.
  const pending = await loadPending(sender.id);
  if (pending.length && AFFIRMATIVE_RE.test(content)) {
    const reply = await executePending(sender.id, pending);
    await clearPending(sender.id);
    return await respond(reply);
  }
  if (pending.length) await clearPending(sender.id);

  const contents = await loadHistory(sender.id);
  contents.push({ role: "user", parts: [{ text: content }] });
  let { text: reply, staged } = await runAgent(sender.id, sender.name, contents);

  // The model sometimes writes proposal text without making the tool call, so
  // there is nothing staged and the user's yes dead-ends. Detect that and force
  // one retry turn that must produce the staged call.
  if (!staged.length && /reply yes to save/i.test(reply)) {
    contents.push({ role: "model", parts: [{ text: reply }] });
    contents.push({
      role: "user",
      parts: [{
        text: "SYSTEM: Your proposal was not staged because you did not call the tool. Call log_activity or update_account now with exactly the values you proposed, then repeat the proposal.",
      }],
    });
    const retry = await runAgent(sender.id, sender.name, contents);
    if (retry.staged.length) {
      reply = retry.text;
      staged = retry.staged;
    } else {
      reply = "Something went wrong staging that change - please resend the request.";
    }
  }

  if (staged.length) await savePending(sender.id, staged);
  return await respond(reply);
});
