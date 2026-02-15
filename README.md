# Feature Adoption -> Revenue Bridge

Interview-ready analytics project that maps SaaS feature adoption to revenue outcomes.

## What This Project Delivers
- Hybrid data strategy: GA4 public behavior signals + UCI transaction benchmark + SEC revenue benchmark + Xero-like synthetic SaaS lifecycle.
- BigQuery + dbt semantic layer for reproducible metrics.
- SQL templates for funnel, retention, adoption, and revenue bridge analysis.
- Python utilities for data ingestion, synthetic generation, retention matrix export, and quality checks.
- Tableau + Power BI dashboard blueprints (waterfall + cohort + funnel).

## Core Business Questions
1. Which onboarding step causes the biggest revenue-impacting drop-off?
2. Which signup cohorts are still active after 6 months?
3. What is the core feature adoption rate by month?
4. How much quarter-over-quarter growth came from:
- Feature Adoption Lift
- Plan Upgrade
- New Customers

## Repository Layout
- `dbt_project/`: dbt models (`staging`, `intermediate`, `marts`) and tests.
- `python/`: ingestion, simulation, retention matrix, and quality checks.
- `sql_templates/`: reusable parameterized query templates.
- `docs/`: case study, data dictionary, interview Q&A.
- `tableau/`: dashboard implementation blueprint and data mapping.
- `powerbi/`: Power BI dashboard blueprint and DAX starter measures.
- `data/raw/`: generated or downloaded raw CSVs before BigQuery load.
- `data/outputs/`: exported matrices and QA reports.

## Prerequisites
- Python 3.11+
- `bq` CLI authenticated to your GCP project
- BigQuery datasets for raw and analytics layers
- `dbt-bigquery`

## Environment Setup
1. Create a virtual environment and install dependencies:
```bash
make setup
```
2. Copy env template and fill values:
```bash
cp .env.example .env
```
3. Configure dbt profile:
```bash
mkdir -p ~/.dbt
cp dbt_project/profiles.example.yml ~/.dbt/profiles.yml
```

Required env variables:
- `GCP_PROJECT_ID`
- `BQ_LOCATION` (default: `US`)
- `BQ_RAW_DATASET` (default: `raw_bridge`)
- `BQ_ANALYTICS_DATASET` (default: `analytics_bridge`)
- `DBT_TARGET` (default: `dev`)
- `SYNTHETIC_SEED` (default: `42`)

## Recommended Run Sequence
1. Generate synthetic raw inputs:
```bash
make generate-raw
```
2. (Optional) Pull real benchmark data into CSV:
```bash
make fetch-ga4
make fetch-uci
make fetch-sec
```
3. Load CSVs to BigQuery raw dataset:
```bash
make load-raw
```
4. Build dbt models and run tests:
```bash
make dbt-run
make dbt-test
```
5. Export retention matrix and run quality checks:
```bash
make retention-matrix
make quality-checks
```

Single command orchestration:
```bash
make all
```

## Public Mart Interfaces
- `mart_funnel_monthly`
- `mart_cohort_retention`
- `mart_feature_adoption`
- `mart_revenue_bridge_quarterly`
- `mart_account_monthly_state`

Detailed metric contracts are in `docs/data_dictionary.md`.

## Cost Control (Free-Tier First)
- All template queries require explicit date filters.
- In paid BigQuery projects, marts can be partitioned for scan cost control.
- In BigQuery Sandbox mode, this repo keeps marts unpartitioned to avoid 60-day partition TTL data loss.
- Raw ingestion scripts support small sampling windows.

## Tableau Build
Use `tableau/dashboard_blueprint.md` for worksheet and dashboard assembly order.

## Power BI Build
Use `powerbi/dashboard_blueprint.md` for page-by-page visual setup and starter DAX.

Export Power BI import files:
```bash
make powerbi-export
```

## Notes
- `stg_sec_financials` is benchmark-only. Core attribution logic is independent from SEC feed.
- Synthetic layer is explicitly tagged as simulation to avoid overclaiming causality.
