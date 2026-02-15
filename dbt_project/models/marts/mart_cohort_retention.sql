{{
  config(
    materialized='table',
    cluster_by=["age_month"]
  )
}}

WITH paid_cohorts AS (
  SELECT
    account_id,
    DATE_TRUNC(DATE(first_payment_ts), MONTH) AS cohort_month
  FROM {{ ref('int_account_revenue_monthly') }}
  WHERE first_payment_ts IS NOT NULL
  GROUP BY account_id, cohort_month
),

activity AS (
  SELECT
    c.account_id,
    c.cohort_month,
    s.month,
    DATE_DIFF(s.month, c.cohort_month, MONTH) AS age_month,
    s.status,
    s.is_paid_active
  FROM {{ ref('mart_account_monthly_state') }} s
  JOIN paid_cohorts c USING (account_id)
  WHERE s.month >= c.cohort_month
),

cohort_size AS (
  SELECT
    cohort_month,
    COUNT(DISTINCT account_id) AS cohort_accounts
  FROM paid_cohorts
  GROUP BY cohort_month
),

retention AS (
  SELECT
    a.cohort_month,
    a.age_month,
    COUNT(DISTINCT IF(a.status = 'active', a.account_id, NULL)) AS active_accounts
  FROM activity a
  GROUP BY a.cohort_month, a.age_month
)

SELECT
  r.cohort_month,
  r.age_month,
  r.active_accounts,
  SAFE_DIVIDE(r.active_accounts, c.cohort_accounts) AS retention_rate
FROM retention r
JOIN cohort_size c USING (cohort_month)
WHERE r.age_month >= 0
