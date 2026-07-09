-- Kairos CRM schema. Run once in the dedicated CRM Supabase project's SQL editor.
-- No auth by design (internal trusted team) — leave RLS disabled on all tables.

create table users (
    id bigint generated always as identity primary key,
    name text not null,
    active boolean not null default true,
    -- E.164, e.g. +13125550100. Identity for the SendBlue text bot: inbound
    -- texts are matched against this and unknown numbers are ignored.
    phone text
);

create table channel_types (
    id bigint generated always as identity primary key,
    label text not null,
    active boolean not null default true
);

create table accounts (
    id bigint generated always as identity primary key,
    practice_name text not null,
    practice_email text,
    practice_phone text,
    website text,
    city text,
    kairos_owner_id bigint references users(id),
    channel_type_id bigint references channel_types(id),
    source_detail text,
    initial_encounter_summary text,
    pipeline_stage text not null default 'New Lead',
    next_action text,
    next_action_due_date date,
    created_at timestamptz not null default now(),
    lost_reason text,
    competitor_tool text,
    pms text,
    best_contact text,
    decision_maker text,
    decision_maker_reached text not null default 'Unknown'
);

create table contacts (
    id bigint generated always as identity primary key,
    account_id bigint not null references accounts(id) on delete cascade,
    name text not null,
    role text,
    email text,
    phone text
);

create table activities (
    id bigint generated always as identity primary key,
    account_id bigint not null references accounts(id) on delete cascade,
    date date not null,
    kairos_owner_id bigint references users(id),
    activity_type text not null,
    summary text,
    next_action text,
    next_action_due_date date,
    created_at timestamptz not null default now()
);

create table demos (
    id bigint generated always as identity primary key,
    account_id bigint not null references accounts(id) on delete cascade,
    demo_date date,
    attendees text,
    status text not null default 'Scheduled',
    pain_points text,
    objections text,
    follow_up_required text,
    created_at timestamptz not null default now()
);

create table email_templates (
    id bigint generated always as identity primary key,
    name text not null,
    category text not null,
    situation text,
    subject text,
    body text,
    notes text
);

-- Rolling conversation history for the SendBlue text bot (supabase/functions/
-- sendblue-bot). Only user text and final bot replies are stored, not tool calls.
create table bot_messages (
    id bigint generated always as identity primary key,
    user_id bigint not null references users(id) on delete cascade,
    role text not null check (role in ('user', 'model')),
    content text not null,
    created_at timestamptz not null default now()
);

create index bot_messages_user_idx on bot_messages (user_id, created_at desc);

-- Staged bot edits awaiting the user's yes-by-text. The edge function, not the
-- model, decides when these execute (code-enforced confirmation gate).
create table bot_pending_writes (
    user_id bigint primary key references users(id) on delete cascade,
    calls jsonb not null,
    created_at timestamptz not null default now()
);

create index accounts_stage_idx on accounts (pipeline_stage);
create index accounts_due_idx on accounts (next_action_due_date);
create index activities_account_idx on activities (account_id, date desc);
create index contacts_account_idx on contacts (account_id);
create index demos_account_idx on demos (account_id);

-- The account-level next_action fields hold "the current single next action";
-- the activity log is the history of how it evolved. Syncing in a trigger makes
-- the update atomic with the activity insert.
create function sync_account_next_action() returns trigger
language plpgsql as $$
begin
    if new.next_action is not null or new.next_action_due_date is not null then
        update accounts
        set next_action = new.next_action,
            next_action_due_date = new.next_action_due_date
        where id = new.account_id;
    end if;
    return new;
end;
$$;

create trigger activities_sync_next_action
after insert on activities
for each row execute function sync_account_next_action();

-- last_action_date and "current state" are derived, never stored (spec 5.1).
create view account_overview as
select
    a.*,
    coalesce(la.last_date, a.created_at::date) as last_action_date,
    la.last_summary as latest_activity_summary
from accounts a
left join lateral (
    select date as last_date, summary as last_summary
    from activities
    where account_id = a.id
    order by date desc, id desc
    limit 1
) la on true;

insert into users (name) values ('Tanush'), ('Aditya'), ('Sanjana'), ('Adhira'), ('Yajat');

insert into channel_types (label) values
    ('Donut Visit'),
    ('Cold Visit'),
    ('Apollo Cold Outreach'),
    ('Conference'),
    ('Referral'),
    ('Other');
