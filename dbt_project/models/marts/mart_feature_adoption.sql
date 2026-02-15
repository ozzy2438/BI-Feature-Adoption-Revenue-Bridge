{{
  config(
    materialized='table'
  )
}}

WITH per_feature AS (
  SELECT
    month,
    'bank_feed_sync' AS feature_name,
    COUNT(DISTINCT IF(status = 'active', account_id, NULL)) AS eligible_accounts,
    COUNT(DISTINCT IF(status = 'active' AND feature_x_adopted_flag = 1, account_id, NULL)) AS adopted_accounts
  FROM {{ ref('mart_account_monthly_state') }}
  GROUP BY month

  UNION ALL

  SELECT
    month,
    'multi_currency' AS feature_name,
    COUNT(DISTINCT IF(status = 'active', account_id, NULL)) AS eligible_accounts,
    COUNT(DISTINCT IF(status = 'active' AND feature_multi_currency_flag = 1, account_id, NULL)) AS adopted_accounts
  FROM {{ ref('mart_account_monthly_state') }}
  GROUP BY month

  UNION ALL

  SELECT
    month,
    'recurring_invoices' AS feature_name,
    COUNT(DISTINCT IF(status = 'active', account_id, NULL)) AS eligible_accounts,
    COUNT(DISTINCT IF(status = 'active' AND feature_recurring_invoices_flag = 1, account_id, NULL)) AS adopted_accounts
  FROM {{ ref('mart_account_monthly_state') }}
  GROUP BY month
)

SELECT
  month,
  feature_name,
  eligible_accounts,
  adopted_accounts,
  SAFE_DIVIDE(adopted_accounts, eligible_accounts) AS adoption_rate
FROM per_feature
