# Adapter Guide: Connecting Real Data Sources

This project is designed so that **only the staging layer changes** when you connect real company data.
Everything from `intermediate` upwards — transformations, mart interfaces, DAX measures — remains identical.

---

## Architecture Principle

```
[Raw Sources]         ← swap here only
     ↓
[Staging Layer]       ← the data contract surface
     ↓
[Intermediate]        ← source-agnostic, unchanged
     ↓
[Marts]               ← source-agnostic, unchanged
     ↓
[Power BI / BI tool]  ← unchanged
```

---

## Current Synthetic Sources → Real Replacements

### 1. `sim_events` → Segment / Amplitude / Mixpanel

The staging model `stg_sim_events` expects:

| Column | Type | Notes |
|---|---|---|
| `account_id` | STRING | Workspace/org identifier |
| `event_name` | STRING | `signup`, `first_payment_received`, `app_integration_connected`, `plan_upgrade`, `feature_activated` |
| `event_ts_utc` | TIMESTAMP | UTC normalized |
| `feature_name` | STRING | `bank_feed_sync`, `multi_currency`, `recurring_invoices` (or your feature names) |

**Replacement**: Create `stg_segment_events.sql` or `stg_amplitude_events.sql` that selects from your event stream and maps to these column names. Update `sources.yml` to point to your Segment/Amplitude BigQuery export dataset.

---

### 2. `sim_revenue_monthly` → Stripe / Chargebee / Recurly MRR snapshots

The staging model `stg_sim_revenue_monthly` expects:

| Column | Type | Notes |
|---|---|---|
| `account_id` | STRING | |
| `month` | DATE | First day of month |
| `mrr_start` | NUMERIC | MRR at start of month |
| `mrr_end` | NUMERIC | MRR at end of month |
| `plan_tier` | STRING | `starter`, `professional`, `enterprise` |
| `status` | STRING | `active` or `churned` |
| `bridge_component` | STRING | Pre-classified or derived in staging |
| `is_new_customer`, `is_plan_upgrade`, `is_churn`, `is_contraction` | INT64 | 0/1 flags |

**Replacement**: Build `stg_stripe_mrr_monthly.sql` from Stripe's subscription exports (via Fivetran or custom pipeline). Chargebee and Recurly both support BigQuery data destinations.

---

### 3. `sim_accounts` → Your CRM / auth system

| Column | Type |
|---|---|
| `account_id` | STRING |
| `signup_ts_utc` | TIMESTAMP |
| `initial_plan_tier` | STRING |
| `region` | STRING |
| `acquisition_channel` | STRING |

**Replacement**: Map from HubSpot, Salesforce, or your internal accounts table.

---

### 4. `ga4_events` → Your GA4 BigQuery export (already real)

This source is already a real public BigQuery dataset. At a company, replace the project/dataset reference in `sources.yml` with your own GA4 export.

---

## Step-by-Step: Adapting to a New Company

1. **Fork the repo** and create a new branch `feature/real-data-[company-name]`.

2. **Update `sources.yml`**:
   ```yaml
   sources:
     - name: raw
       database: "your-gcp-project"
       schema: "your_raw_dataset"
       tables:
         - name: segment_events      # was: sim_events
         - name: stripe_mrr_monthly  # was: sim_revenue_monthly
         - name: accounts            # was: sim_accounts
   ```

3. **Create new staging models** that map real column names to the expected schema above. Staging models are the only files that change.

4. **Update `int_saas_simulated_events` reference** in `int_account_revenue_monthly.sql` to point to your new staging event model.

5. **Run `dbt build`** — all intermediate and mart models compile and run unchanged.

6. **Reload the Power BI report** — because the mart table names and column names are identical, no DAX changes are needed.

---

## Feature Name Mapping

If your company uses different feature names, update the feature name constants in `bridge_logic.py` and the corresponding references in `mart_feature_adoption.sql` and `mart_feature_impact.sql`:

```python
# python/bridge_logic.py
FEATURES: Sequence[str] = ("your_feature_1", "your_feature_2", "your_feature_3")
```

And in the dbt marts, replace the feature name string literals in the UNION ALL blocks.

---

## Production Checklist

- [ ] Replace synthetic staging models with real source staging models
- [ ] Update `sources.yml` with real GCP project and dataset
- [ ] Set `GCP_PROJECT_ID` and `BQ_RAW_DATASET` environment variables
- [ ] Run `dbt build --select staging+` to validate the swap
- [ ] Run `dbt test` to confirm grain and quality constraints pass
- [ ] Schedule `dbt run` via dbt Cloud, Airflow, or Cloud Composer (monthly grain → monthly trigger)
- [ ] Set Power BI dataset refresh schedule to match dbt run cadence
- [ ] Add row-level security in Power BI workspace if multi-tenant reporting
