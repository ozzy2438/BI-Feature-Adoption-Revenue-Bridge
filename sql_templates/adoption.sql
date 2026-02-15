-- Parameterized Feature Adoption Template
-- Parameters:
--   @feature_name STRING
--   @start_date DATE
--   @end_date DATE
--   @activation_window_days INT64 (reserved for custom variants)

SELECT
  month,
  feature_name,
  eligible_accounts,
  adopted_accounts,
  adoption_rate
FROM `{{ project_id }}.{{ analytics_dataset }}.mart_feature_adoption`
WHERE feature_name = @feature_name
  AND month BETWEEN @start_date AND @end_date
ORDER BY month;
