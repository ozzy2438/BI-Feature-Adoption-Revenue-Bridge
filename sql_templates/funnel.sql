-- Parameterized Funnel Template
-- Parameters:
--   @start_date DATE
--   @end_date DATE
--   @cohort_grain STRING ('month' | 'week')

WITH scoped AS (
  SELECT *
  FROM `{{ project_id }}.{{ analytics_dataset }}.mart_funnel_monthly`
  WHERE month BETWEEN @start_date AND @end_date
),
ordered AS (
  SELECT
    month,
    step_name,
    users_at_step,
    conversion_from_prev,
    dropoff_from_prev,
    CASE step_name
      WHEN 'Signup' THEN 1
      WHEN 'First Invoice Created' THEN 2
      WHEN 'First Payment Received' THEN 3
      WHEN 'App Integration Connected' THEN 4
      WHEN 'Plan Upgrade' THEN 5
    END AS step_order
  FROM scoped
)
SELECT
  month,
  step_name,
  users_at_step,
  conversion_from_prev,
  dropoff_from_prev
FROM ordered
ORDER BY month, step_order;
