-- Parameterized Revenue Bridge Template
-- Parameters:
--   @quarter_start DATE
--   @quarter_end DATE
--   @attribution_window_days INT64 (default 60 in model)

SELECT
  quarter,
  bridge_component,
  amount,
  share_pct
FROM `{{ project_id }}.{{ analytics_dataset }}.mart_revenue_bridge_quarterly`
WHERE quarter BETWEEN @quarter_start AND @quarter_end
ORDER BY quarter, amount DESC;
