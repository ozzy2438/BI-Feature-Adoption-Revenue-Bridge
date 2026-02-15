{{ config(severity='warn') }}

WITH x AS (
  SELECT
    cohort_month,
    age_month,
    retention_rate,
    LAG(retention_rate) OVER (PARTITION BY cohort_month ORDER BY age_month) AS prev_retention
  FROM {{ ref('mart_cohort_retention') }}
)
SELECT *
FROM x
WHERE prev_retention IS NOT NULL
  AND retention_rate - prev_retention > 0.25
