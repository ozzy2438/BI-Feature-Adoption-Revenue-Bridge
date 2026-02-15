{{ config(materialized='view') }}

SELECT
  CAST(user_id AS STRING) AS user_id,
  TIMESTAMP(event_ts_utc) AS event_ts_utc,
  DATE(TIMESTAMP(event_ts_utc)) AS event_date,
  LOWER(CAST(event_name AS STRING)) AS event_name,
  LOWER(CAST(source AS STRING)) AS source,
  CAST(country AS STRING) AS country
FROM {{ source('raw', 'ga4_events') }}
WHERE user_id IS NOT NULL
