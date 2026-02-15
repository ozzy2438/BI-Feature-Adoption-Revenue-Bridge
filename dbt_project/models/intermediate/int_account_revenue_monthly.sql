{{ config(materialized='table') }}

WITH revenue AS (
  SELECT
    account_id,
    month,
    mrr_start,
    mrr_end,
    plan_tier,
    status,
    feature_x_adopted_flag,
    feature_multi_currency_flag,
    feature_recurring_invoices_flag,
    features_adopted_count,
    is_new_customer,
    is_plan_upgrade,
    is_churn,
    is_contraction,
    feature_adoption_lift_eligible,
    mrr_delta,
    bridge_component
  FROM {{ ref('stg_sim_revenue_monthly') }}
),

first_events AS (
  SELECT
    account_id,
    MIN(IF(event_name = 'signup', event_ts_utc, NULL)) AS signup_ts,
    MIN(IF(event_name = 'first_payment_received', event_ts_utc, NULL)) AS first_payment_ts,
    MIN(IF(event_name = 'plan_upgrade', event_ts_utc, NULL)) AS first_upgrade_ts,
    MIN(IF(event_name = 'feature_activated' AND feature_name = 'bank_feed_sync', event_ts_utc, NULL)) AS feature_adopted_ts,
    MIN(IF(event_name = 'feature_activated' AND feature_name = 'multi_currency', event_ts_utc, NULL)) AS feature_multi_currency_ts,
    MIN(IF(event_name = 'feature_activated' AND feature_name = 'recurring_invoices', event_ts_utc, NULL)) AS feature_recurring_invoices_ts
  FROM {{ ref('int_saas_simulated_events') }}
  GROUP BY account_id
),

final AS (
  SELECT
    r.account_id,
    r.month,
    r.mrr_start,
    r.mrr_end,
    r.plan_tier,
    r.status,
    r.feature_x_adopted_flag,
    r.feature_multi_currency_flag,
    r.feature_recurring_invoices_flag,
    r.features_adopted_count,
    r.is_new_customer,
    r.is_plan_upgrade,
    r.is_churn,
    r.is_contraction,
    r.feature_adoption_lift_eligible,
    r.mrr_delta,
    r.bridge_component,
    f.signup_ts,
    f.first_payment_ts,
    f.first_upgrade_ts,
    f.feature_adopted_ts,
    f.feature_multi_currency_ts,
    f.feature_recurring_invoices_ts,
    DATE_TRUNC(r.month, QUARTER) AS quarter,
    IF(r.mrr_end > 0, 1, 0) AS is_paid_active
  FROM revenue r
  LEFT JOIN first_events f USING (account_id)
)

SELECT *
FROM final
