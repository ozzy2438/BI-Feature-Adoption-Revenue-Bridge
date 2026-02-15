{{
  config(
    materialized='table'
  )
}}

WITH per_account AS (
  SELECT
    account_id,
    DATE(MIN(IF(event_name = 'signup', event_ts_utc, NULL))) AS signup_date,
    DATE(MIN(IF(event_name = 'first_invoice_created', event_ts_utc, NULL))) AS first_invoice_date,
    DATE(MIN(IF(event_name = 'first_payment_received', event_ts_utc, NULL))) AS first_payment_date,
    DATE(MIN(IF(event_name = 'app_integration_connected', event_ts_utc, NULL))) AS app_integration_date,
    DATE(MIN(IF(event_name = 'plan_upgrade', event_ts_utc, NULL))) AS plan_upgrade_date
  FROM {{ ref('int_saas_simulated_events') }}
  GROUP BY account_id
),

cohort AS (
  SELECT
    account_id,
    DATE_TRUNC(signup_date, MONTH) AS month,
    signup_date,
    first_invoice_date,
    first_payment_date,
    app_integration_date,
    plan_upgrade_date
  FROM per_account
  WHERE signup_date IS NOT NULL
),

step_counts AS (
  SELECT
    month,
    'Signup' AS step_name,
    1 AS step_order,
    COUNT(DISTINCT account_id) AS users_at_step
  FROM cohort
  GROUP BY month

  UNION ALL

  SELECT
    month,
    'First Invoice Created' AS step_name,
    2 AS step_order,
    COUNT(DISTINCT account_id) AS users_at_step
  FROM cohort
  WHERE first_invoice_date IS NOT NULL
  GROUP BY month

  UNION ALL

  SELECT
    month,
    'First Payment Received' AS step_name,
    3 AS step_order,
    COUNT(DISTINCT account_id) AS users_at_step
  FROM cohort
  WHERE first_payment_date IS NOT NULL
  GROUP BY month

  UNION ALL

  SELECT
    month,
    'App Integration Connected' AS step_name,
    4 AS step_order,
    COUNT(DISTINCT account_id) AS users_at_step
  FROM cohort
  WHERE app_integration_date IS NOT NULL
  GROUP BY month

  UNION ALL

  SELECT
    month,
    'Plan Upgrade' AS step_name,
    5 AS step_order,
    COUNT(DISTINCT account_id) AS users_at_step
  FROM cohort
  WHERE plan_upgrade_date IS NOT NULL
  GROUP BY month
),

calc AS (
  SELECT
    month,
    step_name,
    step_order,
    users_at_step,
    LAG(users_at_step) OVER (PARTITION BY month ORDER BY step_order) AS prev_users
  FROM step_counts
)

SELECT
  month,
  step_name,
  users_at_step,
  CASE
    WHEN prev_users IS NULL OR prev_users = 0 THEN 1
    ELSE SAFE_DIVIDE(users_at_step, prev_users)
  END AS conversion_from_prev,
  CASE
    WHEN prev_users IS NULL OR prev_users = 0 THEN 0
    ELSE 1 - SAFE_DIVIDE(users_at_step, prev_users)
  END AS dropoff_from_prev
FROM calc
