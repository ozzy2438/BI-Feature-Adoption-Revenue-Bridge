-- Cohort retention at month 6 by onboarding feature usage.
-- Parameters:
--   @cohort_start DATE
--   @cohort_end DATE
--   @onboarding_window_days INT64

WITH base AS (
  SELECT
    account_id,
    DATE_TRUNC(DATE(signup_ts), MONTH) AS cohort_month,
    DATE(signup_ts) AS signup_date,
    DATE(feature_adopted_ts) AS feature_adopted_date
  FROM `{{ project_id }}.{{ analytics_dataset }}.mart_account_monthly_state`
  GROUP BY account_id, cohort_month, signup_date, feature_adopted_date
),

onboarding_feature AS (
  SELECT
    account_id,
    cohort_month,
    CASE
      WHEN feature_adopted_date IS NOT NULL
           AND DATE_DIFF(feature_adopted_date, signup_date, DAY) BETWEEN 0 AND @onboarding_window_days
      THEN 1
      ELSE 0
    END AS used_feature_in_onboarding
  FROM base
),

month6 AS (
  SELECT
    account_id,
    month,
    status
  FROM `{{ project_id }}.{{ analytics_dataset }}.mart_account_monthly_state`
),

joined AS (
  SELECT
    o.cohort_month,
    o.used_feature_in_onboarding,
    m.account_id,
    m.status
  FROM onboarding_feature o
  JOIN month6 m USING (account_id)
  WHERE m.month = DATE_ADD(o.cohort_month, INTERVAL 6 MONTH)
)

SELECT
  cohort_month,
  used_feature_in_onboarding,
  COUNT(DISTINCT account_id) AS cohort_accounts_at_m6,
  COUNT(DISTINCT IF(status = 'active', account_id, NULL)) AS active_accounts_m6,
  SAFE_DIVIDE(
    COUNT(DISTINCT IF(status = 'active', account_id, NULL)),
    COUNT(DISTINCT account_id)
  ) AS retention_rate_m6
FROM joined
WHERE cohort_month BETWEEN @cohort_start AND @cohort_end
GROUP BY cohort_month, used_feature_in_onboarding
ORDER BY cohort_month, used_feature_in_onboarding DESC;
