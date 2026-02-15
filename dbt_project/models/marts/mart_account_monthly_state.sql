{{
  config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key=['account_id', 'month'],
    cluster_by=["account_id", "plan_tier"]
  )
}}

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
  bridge_component,
  signup_ts,
  first_payment_ts,
  first_upgrade_ts,
  feature_adopted_ts,
  feature_multi_currency_ts,
  feature_recurring_invoices_ts,
  quarter,
  is_paid_active
FROM {{ ref('int_account_revenue_monthly') }}
{% if is_incremental() %}
WHERE month >= (SELECT DATE_SUB(MAX(month), INTERVAL 1 MONTH) FROM {{ this }})
{% endif %}
