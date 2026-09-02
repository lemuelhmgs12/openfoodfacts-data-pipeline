# Design Document: OpenFoodFacts Ingestion Pipeline

## 1. Problem Statement
Retailers and product-catalog teams need visibility into how their product data changes over time — new items added, pricing/ingredient updates, category shifts — without re-processing an entire catalog on every run. This project builds a small-scale, production-style incremental data pipeline that ingests snack product data from the Open Food Facts API, lands it in a raw data lake (S3), and tracks changes over time using a watermark-based incremental extraction pattern. The goal is to demonstrate core data engineering competencies — API integration, incremental ETL design, cloud storage, orchestration, and data quality — on a real dataset.

## 2. Data Source
- API: Open Food Facts (world.openfoodfacts.org)
- Scope: "snacks" category
- Access: No auth required; requires custom User-Agent header
- Known constraints: intermittent 503s observed during development (needs retry logic)

## 3. Alternatives Considered
- Best Buy API — rejected: blocked free/edu email signups
- eBay API — rejected: developer application denied
- Open Food Facts — selected: no signup friction, real incremental field (last_modified_t)

## 4. Architecture
\`\`\`mermaid
flowchart LR
    A[Open Food Facts API] -->|fetch new/changed products| B[Ingestion Script]
    B -->|raw JSON| C[S3: raw zone<br/>partitioned by ingest_date]
    B -->|read/update| D[S3: watermark.json<br/>last_modified_t]
    C --> E[Future: Glue/Spark<br/>transform layer]
    E --> F[Future: Redshift/Athena<br/>warehouse]
    F --> G[Future: dbt models]
    G --> H[Future: Dashboard]
\`\`\`

## 5. Incremental Strategy
- Watermark on `last_modified_t`, stored as JSON in S3 (s3://bucket/state/watermark.json)
- Each run: fetch records where last_modified_t > watermark
- Watermark updated only after successful write (avoid data loss on partial failure)

## 6. Storage Layout
s3://bucket/raw/openfoodfacts/ingest_date=YYYY-MM-DD/batch_NNN.json

## 7. Error Handling
- Retry with exponential backoff on 503 (tenacity, max 3 attempts)
- **503 failure rate measured empirically at ~60%** (see Findings Log) —
  high enough that retry is load-bearing, not a nice-to-have
- **Retry-exhaustion behavior**: fail the run loudly (non-zero exit,
  watermark NOT advanced — safe to simply re-run) AND trigger an alert.
  Silent skip was rejected: at a 60% base failure rate, silently
  skipping would lose data almost every run.
- **Not yet implemented**: the alerting mechanism itself (candidates:
  SNS topic + email/Slack, or a simple webhook). Tracked in section 8.

## 8. Open Questions / Future Work
- Pagination limit per run (287K total products — need a sane cap)
- Terraform for infra-as-code?
- Monitoring/alerting approach
- Alerting mechanism for failed runs (SNS? Slack webhook?) — decision
  made in section 7, implementation still pending

## 9. Findings Log
- **Endpoint choice**: switched from `/cgi/search.pl` to `/api/v2/search`.
  OFF's own docs mark the legacy `search.pl` endpoint as "not recommended
  for new integrations" in favor of the v2 structured search API, which
  supports `categories_tags`, `sort_by`, `fields`, and documented pagination.
- **Sort order verified empirically**: `sort_by=last_modified_t` on
  `/api/v2/search` returns results **newest-first (descending)**. This
  was not documented explicitly, so it was confirmed by requesting page 1
  and checking that timestamps were in descending order (see
  `verify_sort_order.py`). This is what makes early-stop pagination for
  the incremental strategy (section 5) valid — without it, we'd have to
  page through the entire catalog on every run.