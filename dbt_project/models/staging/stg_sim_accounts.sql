{{ config(materialized='view') }}

SELECT
  CAST(account_id AS STRING) AS account_id,
  TIMESTAMP(signup_ts_utc) AS signup_ts_utc,
  DATE(signup_month) AS signup_month,
  CAST(initial_plan_tier AS STRING) AS initial_plan_tier,
  CAST(region AS STRING) AS region,
  CAST(acquisition_channel AS STRING) AS acquisition_channel
FROM {{ source('raw', 'sim_accounts') }}
WHERE account_id IS NOT NULL
