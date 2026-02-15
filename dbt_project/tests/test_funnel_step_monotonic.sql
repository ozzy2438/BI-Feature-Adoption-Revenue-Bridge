WITH ordered AS (
  SELECT
    month,
    CASE step_name
      WHEN 'Signup' THEN 1
      WHEN 'First Invoice Created' THEN 2
      WHEN 'First Payment Received' THEN 3
      WHEN 'App Integration Connected' THEN 4
      WHEN 'Plan Upgrade' THEN 5
    END AS step_order,
    users_at_step
  FROM {{ ref('mart_funnel_monthly') }}
),
chk AS (
  SELECT
    month,
    step_order,
    users_at_step,
    LAG(users_at_step) OVER (PARTITION BY month ORDER BY step_order) AS prev_users
  FROM ordered
)
SELECT *
FROM chk
WHERE prev_users IS NOT NULL
  AND users_at_step > prev_users
