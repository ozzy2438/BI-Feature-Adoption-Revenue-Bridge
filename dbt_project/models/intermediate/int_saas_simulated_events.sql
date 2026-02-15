{{ config(materialized='table') }}

WITH base_events AS (
  SELECT
    account_id,
    user_id,
    event_name,
    event_ts_utc,
    event_month,
    feature_name,
    metadata_json
  FROM {{ ref('stg_sim_events') }}
),

adoption_points AS (
  SELECT
    account_id,
    MIN(event_ts_utc) AS feature_first_adopted_ts
  FROM base_events
  WHERE event_name = 'feature_activated'
  GROUP BY account_id
),

ga4_signal AS (
  SELECT
    event_name,
    COUNT(*) AS ga4_event_count
  FROM {{ ref('stg_ga4_events') }}
  GROUP BY event_name
),

uci_signal AS (
  SELECT
    AVG(total_amount) AS avg_ticket_size,
    APPROX_QUANTILES(total_amount, 10)[OFFSET(5)] AS median_ticket_size
  FROM {{ ref('stg_uci_transactions') }}
  WHERE is_cancelled = 0
)

SELECT
  e.*,
  a.feature_first_adopted_ts,
  COALESCE(g.ga4_event_count, 0) AS ga4_event_count_for_name,
  u.avg_ticket_size,
  u.median_ticket_size
FROM base_events e
LEFT JOIN adoption_points a USING (account_id)
LEFT JOIN ga4_signal g ON g.event_name = e.event_name
CROSS JOIN uci_signal u
