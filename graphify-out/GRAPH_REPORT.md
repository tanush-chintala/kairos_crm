# Graph Report - .  (2026-07-31)

## Corpus Check
- 12 files · ~48,647 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 348 nodes · 602 edges · 26 communities (18 shown, 8 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.5)
- Token cost: 11,248 input · 1,408 output

## Community Hubs (Navigation)
- SendBlue Bot Tool Layer
- Dashboard Chatbot UI
- Donut Search Geometry
- Clinic Dedup Pipeline
- Donut Scraper Page & Queries
- Clinic Classification & Enrichment
- CRM Query Helpers
- Contact/Demo CRUD
- Donut Promotion & City Parsing
- Account Dedup Utils
- Accounts View Forms
- Google Places Client
- External Services Overview
- Supabase Client Setup
- User Management
- Account Creation Logging
- Project Docs
- Streamlit Fragment
- Chat Transcript Doc
- Gemini Model Reference
- Google Places API Node
- Requirements File
- Supabase Service Node

## God Nodes (most connected - your core abstractions)
1. `_render_detail()` - 24 edges
2. `execTool()` - 16 edges
3. `_render_run_detail()` - 12 edges
4. `_entry()` - 11 edges
5. `promote_donut_result()` - 11 edges
6. `_account_form()` - 11 edges
7. `_fold_persons_in_building()` - 10 edges
8. `_tab_new_scrape()` - 10 edges
9. `find_duplicates()` - 9 edges
10. `findDuplicates()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `_dashboard_body()` --calls--> `list_accounts()`  [EXTRACTED]
  views/dashboard.py → db/queries.py
- `_dashboard_body()` --calls--> `list_all_demos()`  [EXTRACTED]
  views/dashboard.py → db/queries.py
- `_account_form()` --calls--> `add_user()`  [EXTRACTED]
  views/accounts.py → db/queries.py
- `_render_detail()` --calls--> `add_user()`  [EXTRACTED]
  views/accounts.py → db/queries.py
- `_account_form()` --calls--> `add_channel_type()`  [EXTRACTED]
  views/accounts.py → db/queries.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CRM Text Bot Integration** — supabase_functions_sendblue_bot, gemini_api, sendblue_api, supabase_project [EXTRACTED 1.00]

## Communities (26 total, 8 thin omitted)

### Community 0 - "SendBlue Bot Tool Layer"
Cohesion: 0.07
Nodes (47): ACCOUNT_SCOPED_TOOLS, accountName(), ACTIVITY_TYPES, CADENCE_CHANNELS, chicagoToday(), chicagoWeekday(), cityFromAddress(), CLOSED_STAGES (+39 more)

### Community 1 - "Dashboard Chatbot UI"
Cohesion: 0.08
Nodes (28): _chat_timestamp(), _render_messages(), _sidebar_chat(), datetime, list_all_demos(), list_bot_messages(), fragment, Fixed application-level enums. users and channel_types are admin-editable… (+20 more)

### Community 2 - "Donut Search Geometry"
Cohesion: 0.09
Nodes (35): adaptive_buffer_miles(), _buffered_polygon(), compute_bounding_box(), compute_buffered_outline(), compute_polygon_area_sqmi(), compute_polygon_centroid(), compute_polygon_iou(), estimate_circle_count() (+27 more)

### Community 3 - "Clinic Dedup Pipeline"
Cohesion: 0.11
Nodes (32): _add_doctors_to_clinic(), _best_business_match(), _building_key(), _data_richness(), deduplicate_clinics(), _digits(), _domain(), _entry() (+24 more)

### Community 4 - "Donut Scraper Page & Queries"
Cohesion: 0.10
Nodes (28): cache_data, bulk_create_donut_run_results(), create_donut_run(), list_donut_runs(), list_users(), update_donut_run(), MacroElement, _clear_polygon_state() (+20 more)

### Community 5 - "Clinic Classification & Enrichment"
Cohesion: 0.12
Nodes (24): classify_clinic(), _is_dso(), Returns 'DSO' | 'chain' | 'independent' | 'unknown'. Best-effort heuristic —…, _call_gemini_structured(), _confidence_rank(), enrich_clinic(), _enrich_with_gemini(), _extract_dentist_regex() (+16 more)

### Community 6 - "CRM Query Helpers"
Cohesion: 0.09
Nodes (5): add_channel_type(), _get_donut_channel_id(), Query helpers per table. Supabase is the single source of truth — every view…, Get or create the 'Donut Visit' channel type., set_channel_type_active()

### Community 7 - "Contact/Demo CRUD"
Cohesion: 0.12
Nodes (21): create_contact(), create_demo(), delete_account(), delete_contact(), delete_demo(), get_template(), list_activities(), list_cadence_steps() (+13 more)

### Community 8 - "Donut Promotion & City Parsing"
Cohesion: 0.14
Nodes (19): bulk_promote_donut_results(), _city_from_address(), find_donut_result_duplicates(), get_account(), list_accounts(), list_donut_run_results(), promote_donut_result(), Create a CRM account from a donut run result and link them. (+11 more)

### Community 9 - "Account Dedup Utils"
Cohesion: 0.23
Nodes (11): find_batch_duplicates(), find_duplicates(), _name_core(), _norm_city(), _norm_name(), normalize_domain(), normalize_email(), normalize_phone() (+3 more)

### Community 10 - "Accounts View Forms"
Cohesion: 0.26
Nodes (12): create_account(), get_distinct_column_values(), _account_form(), _changed_fields(), _channel_select(), _custom_select(), _id_options(), _nullable_select() (+4 more)

### Community 12 - "External Services Overview"
Cohesion: 0.40
Nodes (5): Bot Transfer Guide, Google Gemini API, SendBlue API, SendBlue Text Bot, Supabase Project

### Community 13 - "Supabase Client Setup"
Cohesion: 0.50
Nodes (4): cache_resource, Client, get_client(), _secret()

### Community 14 - "User Management"
Cohesion: 0.67
Nodes (3): add_user(), Idempotent by name: inline creation from a dropdown can fire twice for the same…, set_user_active()

### Community 15 - "Account Creation Logging"
Cohesion: 0.67
Nodes (3): get_donut_run(), log_account_creation(), Log how an account came to exist as the first entry in its activity log,…

## Knowledge Gaps
- **18 isolated node(s):** `Kairos CRM Feature Spec`, `Developer Notes for Claude`, `Supabase Project`, `Bot Transfer Guide`, `Google Gemini API` (+13 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `enrich_clinic()` connect `Clinic Classification & Enrichment` to `Donut Scraper Page & Queries`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `_render_run_detail()` connect `Donut Promotion & City Parsing` to `Donut Scraper Page & Queries`, `Account Creation Logging`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **What connects `Kairos CRM Feature Spec`, `Developer Notes for Claude`, `Supabase Project` to the rest of the system?**
  _18 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `SendBlue Bot Tool Layer` be split into smaller, more focused modules?**
  _Cohesion score 0.06568832983927324 - nodes in this community are weakly interconnected._
- **Should `Dashboard Chatbot UI` be split into smaller, more focused modules?**
  _Cohesion score 0.08170731707317073 - nodes in this community are weakly interconnected._
- **Should `Donut Search Geometry` be split into smaller, more focused modules?**
  _Cohesion score 0.08888888888888889 - nodes in this community are weakly interconnected._
- **Should `Clinic Dedup Pipeline` be split into smaller, more focused modules?**
  _Cohesion score 0.11363636363636363 - nodes in this community are weakly interconnected._