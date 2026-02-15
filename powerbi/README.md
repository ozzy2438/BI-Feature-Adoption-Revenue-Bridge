# Power BI Assets

This folder contains Power BI implementation guidance for the Feature Adoption -> Revenue Bridge project.

## Files
- `dashboard_blueprint.md`: page-by-page visual build and DAX starter measures.

## Data Preparation for Power BI
Export ready-to-import CSVs from BigQuery marts:

```bash
make VENV=.venv311 powerbi-export
```

Outputs:
- `data/outputs/powerbi_extracts/mart_funnel_monthly.csv`
- `data/outputs/powerbi_extracts/mart_cohort_retention.csv`
- `data/outputs/powerbi_extracts/mart_feature_adoption.csv`
- `data/outputs/powerbi_extracts/mart_revenue_bridge_quarterly.csv`
- `data/outputs/powerbi_extracts/mart_account_monthly_state.csv`

Then in Power BI Desktop:
1. `Get data` -> `Text/CSV` (or BigQuery connector).
2. Load the five tables.
3. Apply visuals from `dashboard_blueprint.md`.
