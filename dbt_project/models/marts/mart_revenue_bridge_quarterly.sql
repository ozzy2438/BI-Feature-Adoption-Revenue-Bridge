{{ config(materialized='table') }}

WITH classified AS (
  SELECT
    DATE_TRUNC(month, QUARTER) AS quarter,
    bridge_component,
    mrr_delta AS amount
  FROM {{ ref('mart_account_monthly_state') }}
),

agg AS (
  SELECT
    quarter,
    bridge_component,
    SUM(amount) AS amount
  FROM classified
  GROUP BY quarter, bridge_component
),

total_positive AS (
  SELECT
    quarter,
    SUM(IF(amount > 0, amount, 0)) AS total_positive_delta
  FROM agg
  GROUP BY quarter
)

SELECT
  a.quarter,
  a.bridge_component,
  a.amount,
  CASE
    WHEN t.total_positive_delta = 0 THEN 0
    ELSE SAFE_DIVIDE(IF(a.amount > 0, a.amount, 0), t.total_positive_delta)
  END AS share_pct
FROM agg a
JOIN total_positive t USING (quarter)
