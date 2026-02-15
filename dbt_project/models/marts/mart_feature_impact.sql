{{ config(materialized='table') }}

WITH monthly AS (
  SELECT
    account_id,
    month,
    mrr_end,
    is_churn,
    is_contraction,
    features_adopted_count,
    feature_x_adopted_flag,
    feature_multi_currency_flag,
    feature_recurring_invoices_flag
  FROM {{ ref('mart_account_monthly_state') }}
),

feature_segments AS (
  SELECT month, account_id, mrr_end, is_churn, is_contraction,
    'bank_feed_sync' AS feature_name,
    feature_x_adopted_flag AS is_adopted
  FROM monthly

  UNION ALL

  SELECT month, account_id, mrr_end, is_churn, is_contraction,
    'multi_currency' AS feature_name,
    feature_multi_currency_flag AS is_adopted
  FROM monthly

  UNION ALL

  SELECT month, account_id, mrr_end, is_churn, is_contraction,
    'recurring_invoices' AS feature_name,
    feature_recurring_invoices_flag AS is_adopted
  FROM monthly
),

per_feature AS (
  SELECT
    month,
    feature_name,
    CASE WHEN is_adopted = 1 THEN 'adopted' ELSE 'not_adopted' END AS segment,
    COUNT(DISTINCT account_id) AS total_accounts,
    COUNTIF(is_churn = 1) AS churned_accounts,
    SAFE_DIVIDE(COUNTIF(is_churn = 1), COUNT(DISTINCT account_id)) AS churn_rate,
    COUNTIF(is_contraction = 1) AS contracted_accounts,
    SAFE_DIVIDE(COUNTIF(is_contraction = 1), COUNT(DISTINCT account_id)) AS contraction_rate,
    AVG(mrr_end) AS avg_mrr,
    SUM(mrr_end) AS total_mrr
  FROM feature_segments
  GROUP BY month, feature_name, segment
),

by_count AS (
  SELECT
    month,
    'feature_count' AS feature_name,
    CAST(features_adopted_count AS STRING) AS segment,
    COUNT(DISTINCT account_id) AS total_accounts,
    COUNTIF(is_churn = 1) AS churned_accounts,
    SAFE_DIVIDE(COUNTIF(is_churn = 1), COUNT(DISTINCT account_id)) AS churn_rate,
    COUNTIF(is_contraction = 1) AS contracted_accounts,
    SAFE_DIVIDE(COUNTIF(is_contraction = 1), COUNT(DISTINCT account_id)) AS contraction_rate,
    AVG(mrr_end) AS avg_mrr,
    SUM(mrr_end) AS total_mrr
  FROM monthly
  GROUP BY month, feature_name, segment
)

SELECT * FROM per_feature
UNION ALL
SELECT * FROM by_count
