-- Parameterized Cohort Retention Template
-- Parameters:
--   @cohort_start DATE
--   @cohort_end DATE
--   @retention_horizon_month INT64

SELECT
  cohort_month,
  age_month,
  active_accounts,
  retention_rate
FROM `{{ project_id }}.{{ analytics_dataset }}.mart_cohort_retention`
WHERE cohort_month BETWEEN @cohort_start AND @cohort_end
  AND age_month BETWEEN 0 AND @retention_horizon_month
ORDER BY cohort_month, age_month;
