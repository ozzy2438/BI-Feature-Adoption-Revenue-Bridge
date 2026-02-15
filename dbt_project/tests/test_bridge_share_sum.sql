WITH q AS (
  SELECT
    quarter,
    SUM(CASE WHEN amount > 0 THEN share_pct ELSE 0 END) AS share_sum,
    SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_positive_delta
  FROM {{ ref('mart_revenue_bridge_quarterly') }}
  GROUP BY quarter
)
SELECT *
FROM q
WHERE total_positive_delta > 0
  AND ABS(share_sum - 1.0) > 0.1
