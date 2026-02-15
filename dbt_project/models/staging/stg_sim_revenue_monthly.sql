{{ config(materialized='view') }}

SELECT
  CAST(account_id AS STRING) AS account_id,
  DATE(month) AS month,
  SAFE_CAST(mrr_start AS NUMERIC) AS mrr_start,
  SAFE_CAST(mrr_end AS NUMERIC) AS mrr_end,
  CAST(plan_tier AS STRING) AS plan_tier,
  CAST(status AS STRING) AS status,
  SAFE_CAST(feature_x_adopted_flag AS INT64) AS feature_x_adopted_flag,
  SAFE_CAST(feature_multi_currency_flag AS INT64) AS feature_multi_currency_flag,
  SAFE_CAST(feature_recurring_invoices_flag AS INT64) AS feature_recurring_invoices_flag,
  SAFE_CAST(features_adopted_count AS INT64) AS features_adopted_count,
  SAFE_CAST(is_new_customer AS INT64) AS is_new_customer,
  SAFE_CAST(is_plan_upgrade AS INT64) AS is_plan_upgrade,
  SAFE_CAST(is_churn AS INT64) AS is_churn,
  SAFE_CAST(is_contraction AS INT64) AS is_contraction,
  SAFE_CAST(feature_adoption_lift_eligible AS INT64) AS feature_adoption_lift_eligible,
  SAFE_CAST(mrr_delta AS NUMERIC) AS mrr_delta,
  CAST(bridge_component AS STRING) AS bridge_component
FROM {{ source('raw', 'sim_revenue_monthly') }}
WHERE account_id IS NOT NULL
