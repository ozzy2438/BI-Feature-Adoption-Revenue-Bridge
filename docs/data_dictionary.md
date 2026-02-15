# Data Dictionary and Metric Contract

## Raw Tables (`raw_bridge`)

### `ga4_events`
- `user_id` STRING: pseudo user identifier.
- `event_ts_utc` TIMESTAMP: event timestamp in UTC.
- `event_name` STRING: normalized event name.
- `source` STRING: acquisition/source dimension.
- `country` STRING: country dimension.

### `uci_transactions`
- `invoice_no` STRING
- `customer_id` STRING
- `invoice_ts_utc` TIMESTAMP
- `quantity` INT64
- `unit_price` NUMERIC
- `is_cancelled` INT64
- `total_amount` NUMERIC
- `country` STRING

### `sec_financials`
- `fiscal_quarter` STRING (`YYYY-QN`)
- `company_name` STRING
- `cik` STRING
- `revenue_usd` NUMERIC
- `filed_date` DATE

### `sim_accounts`
- `account_id` STRING
- `signup_ts_utc` TIMESTAMP
- `signup_month` DATE
- `initial_plan_tier` STRING
- `region` STRING
- `acquisition_channel` STRING

### `sim_events`
- `account_id` STRING
- `user_id` STRING
- `event_name` STRING
- `event_ts_utc` TIMESTAMP
- `event_month` DATE
- `feature_name` STRING — one of `bank_feed_sync`, `multi_currency`, `recurring_invoices`
- `metadata_json` STRING

### `sim_revenue_monthly`
- `account_id` STRING
- `month` DATE
- `mrr_start` NUMERIC
- `mrr_end` NUMERIC
- `plan_tier` STRING
- `status` STRING — `active` or `churned`
- `feature_x_adopted_flag` INT64 — bank_feed_sync adoption (legacy column name)
- `feature_multi_currency_flag` INT64
- `feature_recurring_invoices_flag` INT64
- `features_adopted_count` INT64 — total distinct features adopted (0-3)
- `is_new_customer` INT64
- `is_plan_upgrade` INT64
- `is_churn` INT64 — 1 if mrr_end = 0 and mrr_start > 0
- `is_contraction` INT64 — 1 if mrr_end < mrr_start and mrr_end > 0
- `feature_adoption_lift_eligible` INT64
- `mrr_delta` NUMERIC
- `bridge_component` STRING

## Public Mart Interfaces (`analytics_bridge`)

### `mart_account_monthly_state`
Shared account-month truth table.
- `account_id`, `month` (unique key)
- `mrr_start`, `mrr_end`, `mrr_delta`
- `plan_tier`, `status`
- `feature_x_adopted_flag`, `feature_multi_currency_flag`, `feature_recurring_invoices_flag`
- `features_adopted_count`
- `is_new_customer`, `is_plan_upgrade`, `is_churn`, `is_contraction`
- `feature_adoption_lift_eligible`
- `bridge_component`
- `signup_ts`, `first_payment_ts`, `first_upgrade_ts`
- `feature_adopted_ts` (bank_feed_sync), `feature_multi_currency_ts`, `feature_recurring_invoices_ts`
- `quarter`, `is_paid_active`

### `mart_funnel_monthly`
- `month`
- `step_name`
- `users_at_step`
- `conversion_from_prev`
- `dropoff_from_prev`

### `mart_cohort_retention`
Cohorts are defined by **first payment month** (not signup). This ensures month-0 retention is ~100% since the denominator is paying customers.
- `cohort_month` — first payment month
- `age_month`
- `active_accounts`
- `retention_rate`

### `mart_feature_adoption`
Tracks adoption for three features via UNION ALL: `bank_feed_sync`, `multi_currency`, `recurring_invoices`.
- `month`
- `feature_name`
- `eligible_accounts`
- `adopted_accounts`
- `adoption_rate`

### `mart_feature_impact`
Feature impact matrix: per-feature adopted vs not-adopted comparison, plus by feature count (0-3).
- `month`
- `feature_name` — `bank_feed_sync`, `multi_currency`, `recurring_invoices`, or `feature_count`
- `segment` — `adopted` / `not_adopted` (per feature) or `0` / `1` / `2` / `3` (feature count)
- `total_accounts`
- `churned_accounts`
- `churn_rate`
- `contracted_accounts`
- `contraction_rate`
- `avg_mrr`
- `total_mrr`

### `mart_revenue_bridge_quarterly`
- `quarter`
- `bridge_component`
- `amount`
- `share_pct`

## Metric Definitions

### Core Feature Adoption Rate
`adopted_accounts / eligible_accounts`

### 6-Month Retention
For a paid cohort month `C`:
`active_accounts(age_month=6) / cohort_accounts(at age 0)`

### Funnel Conversion
For each step `n`:
`users_at_step_n / users_at_step_n-1`

### Bridge Share
For each quarter and component:
`component_positive_amount / total_positive_delta`

## Attribution Precedence (Deterministic)

### Positive delta (mrr_delta > 0)
1. `New Customers`
2. `Plan Upgrade`
3. `Feature Adoption Lift`
4. `Other/Residual`

### Negative delta (mrr_delta < 0)
1. `Churn` — mrr_end = 0
2. `Contraction` — mrr_end > 0 but < mrr_start
3. `Other/Residual`

This precedence is enforced both in simulation output and mart model logic.
