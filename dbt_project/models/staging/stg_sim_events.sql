{{ config(materialized='view') }}

SELECT
  CAST(account_id AS STRING) AS account_id,
  CAST(user_id AS STRING) AS user_id,
  LOWER(CAST(event_name AS STRING)) AS event_name,
  TIMESTAMP(event_ts_utc) AS event_ts_utc,
  DATE(event_month) AS event_month,
  CAST(feature_name AS STRING) AS feature_name,
  CAST(metadata_json AS STRING) AS metadata_json
FROM {{ source('raw', 'sim_events') }}
WHERE account_id IS NOT NULL
