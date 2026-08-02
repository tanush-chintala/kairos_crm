-- Migration: Donut Scraper Integration + Account Creation Context
-- Run this in the Kairos CRM Supabase project SQL editor.

-- ─── 1. Account creation context columns ────────────────────────────────────
alter table accounts
    add column if not exists creation_source text not null default 'manual',
    add column if not exists creation_reason text,
    add column if not exists creation_user_id bigint references users(id);

-- Back-fill existing accounts as manual creations
update accounts set creation_source = 'manual' where creation_source is null;

-- ─── 2. Donut runs table ────────────────────────────────────────────────────
create table if not exists donut_runs (
    id bigint generated always as identity primary key,
    run_name text not null,
    area_name text,
    polygon_geojson jsonb,
    buffer_miles numeric(4,2),
    total_clinics int not null default 0,
    new_clinics int not null default 0,
    reused_clinics int not null default 0,
    status text not null default 'pending',  -- pending | confirmed | archived
    created_by bigint references users(id),
    created_at timestamptz not null default now()
);

-- ─── 3. Donut run results (staging table for scraped clinics) ───────────────
create table if not exists donut_run_results (
    id bigint generated always as identity primary key,
    donut_run_id bigint not null references donut_runs(id) on delete cascade,
    place_id text,
    clinic_name text not null,
    classification text,
    address text,
    lat numeric(10,7),
    lng numeric(10,7),
    inclusion_zone text,          -- 'core' | 'buffer'
    phone text,
    website text,
    email text,
    email_source text,
    head_dentist text,
    staff_source text,
    hours_json jsonb,
    notes text,
    call_status text not null default 'Not Called',
    call_notes text,
    promoted_account_id bigint references accounts(id),
    promoted_by bigint references users(id),
    promoted_at timestamptz,
    updated_by bigint references users(id),
    updated_at timestamptz,
    created_at timestamptz not null default now()
);

create index if not exists donut_run_results_run_idx
    on donut_run_results (donut_run_id);

-- ─── 6. Add user attribution columns to donut_run_results ─────────────────
alter table donut_run_results
    add column if not exists promoted_by bigint references users(id),
    add column if not exists promoted_at timestamptz,
    add column if not exists updated_by bigint references users(id),
    add column if not exists updated_at timestamptz;

-- ─── 4. Add donut_run_id FK on accounts ─────────────────────────────────────
alter table accounts
    add column if not exists donut_run_id bigint references donut_runs(id);

-- ─── 5. Update account_overview view to include new columns ─────────────────
drop view if exists account_overview cascade;

create view account_overview as
select
    a.*,
    coalesce(la.last_date, a.created_at::date) as last_action_date,
    la.last_summary as latest_activity_summary,
    la.last_type as latest_activity_type
from accounts a
left join lateral (
    select date as last_date, summary as last_summary, activity_type as last_type
    from activities
    where account_id = a.id and not is_system
    order by date desc, id desc
    limit 1
) la on true;
