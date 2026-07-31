# Graph Report - .  (2026-07-31)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 325 nodes · 658 edges · 14 communities (13 shown, 1 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.5)
- Token cost: 838 input · 33 output

## Graph Freshness
- Built from commit: `90b1a0ae`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Database Client Operations
- Frontend Constants and Tools
- donut_scraper.py
- tz.py
- pipeline/dedup.py
- donut_search.py
- donut_enrichment.py
- utils/dedup.py
- accounts.py
- SendBlue Text Bot
- Developer Notes for Claude

## God Nodes (most connected - your core abstractions)
1. `get_client()` - 57 edges
2. `_render_detail()` - 29 edges
3. `_tab_new_scrape()` - 14 edges
4. `execTool()` - 12 edges
5. `central_today()` - 12 edges
6. `promote_donut_result()` - 11 edges
7. `_entry()` - 11 edges
8. `find_duplicates()` - 11 edges
9. `_account_form()` - 11 edges
10. `_render_cadence_panel()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `_sidebar_chat()` --calls--> `list_bot_messages()`  [EXTRACTED]
  app.py → db/queries.py
- `render_creation_context()` --calls--> `list_users()`  [EXTRACTED]
  views/donut_scraper.py → db/queries.py
- `_account_form()` --calls--> `add_user()`  [EXTRACTED]
  views/accounts.py → db/queries.py
- `_account_form()` --calls--> `add_channel_type()`  [EXTRACTED]
  views/accounts.py → db/queries.py
- `_render_list()` --calls--> `list_accounts()`  [EXTRACTED]
  views/accounts.py → db/queries.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **CRM Text Bot Integration** — supabase_functions_sendblue_bot, gemini_api, sendblue_api, supabase_project [EXTRACTED 1.00]

## Communities (14 total, 1 thin omitted)

### Community 0 - "Database Client Operations"
Cohesion: 0.06
Nodes (71): cache_resource, Client, get_client(), _secret(), add_channel_type(), add_user(), bulk_create_donut_run_results(), bulk_promote_donut_results() (+63 more)

### Community 1 - "Frontend Constants and Tools"
Cohesion: 0.07
Nodes (43): ACCOUNT_SCOPED_TOOLS, accountName(), ACTIVITY_TYPES, CADENCE_CHANNELS, chicagoToday(), chicagoWeekday(), CLOSED_STAGES, COMPETITOR_TOOLS (+35 more)

### Community 2 - "donut_scraper.py"
Cohesion: 0.09
Nodes (33): cache_data, MacroElement, adaptive_buffer_miles(), compute_buffered_outline(), compute_polygon_area_sqmi(), compute_polygon_centroid(), filter_by_polygon(), Approximate the area of the polygon in square miles. (+25 more)

### Community 3 - "tz.py"
Cohesion: 0.12
Nodes (25): _chat_timestamp(), fragment, _render_messages(), _sidebar_chat(), datetime, categorize(), date, Dashboard bucketing: Due Today / Overdue / Stale / Upcoming (spec section 6).… (+17 more)

### Community 4 - "pipeline/dedup.py"
Cohesion: 0.11
Nodes (32): _add_doctors_to_clinic(), _best_business_match(), _building_key(), _data_richness(), deduplicate_clinics(), _digits(), _domain(), _entry() (+24 more)

### Community 5 - "donut_search.py"
Cohesion: 0.14
Nodes (25): _buffered_polygon(), compute_bounding_box(), compute_polygon_iou(), estimate_circle_count(), _expand_bbox(), get_place_details_for_donut(), _meters_to_lat_deg(), _meters_to_lng_deg() (+17 more)

### Community 6 - "donut_enrichment.py"
Cohesion: 0.15
Nodes (19): classify_clinic(), _is_dso(), Returns 'DSO' | 'chain' | 'independent' | 'unknown'. Best-effort heuristic —…, _call_gemini_structured(), _confidence_rank(), enrich_clinic(), _extract_dentist_regex(), _extract_dso() (+11 more)

### Community 7 - "utils/dedup.py"
Cohesion: 0.15
Nodes (12): Fixed application-level enums. users and channel_types are admin-editable…, find_batch_duplicates(), find_duplicates(), _name_core(), _norm_city(), _norm_name(), normalize_domain(), normalize_email() (+4 more)

### Community 8 - "accounts.py"
Cohesion: 0.18
Nodes (17): get_distinct_column_values(), _account_form(), _cadence_gap_label(), _changed_fields(), _channel_select(), _custom_select(), _id_options(), _log_system() (+9 more)

### Community 9 - "SendBlue Text Bot"
Cohesion: 0.40
Nodes (5): Bot Transfer Guide, Google Gemini API, SendBlue API, SendBlue Text Bot, Supabase Project

## Knowledge Gaps
- **16 isolated node(s):** `supabase`, `CLOSED_STAGES`, `LOST_REASONS`, `COMPETITOR_TOOLS`, `TOOL_DECLARATIONS` (+11 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `deduplicate_clinics()` connect `pipeline/dedup.py` to `donut_scraper.py`?**
  _High betweenness centrality (0.143) - this node is a cross-community bridge._
- **Why does `get_client()` connect `Database Client Operations` to `accounts.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **What connects `supabase`, `CLOSED_STAGES`, `LOST_REASONS` to the rest of the system?**
  _16 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Database Client Operations` be split into smaller, more focused modules?**
  _Cohesion score 0.06164383561643835 - nodes in this community are weakly interconnected._
- **Should `Frontend Constants and Tools` be split into smaller, more focused modules?**
  _Cohesion score 0.06938775510204082 - nodes in this community are weakly interconnected._
- **Should `donut_scraper.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08502024291497975 - nodes in this community are weakly interconnected._
- **Should `tz.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12121212121212122 - nodes in this community are weakly interconnected._