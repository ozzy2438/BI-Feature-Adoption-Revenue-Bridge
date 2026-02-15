{{ config(materialized='table') }}

SELECT
  account_id,
  signup_ts_utc,
  signup_month AS cohort_month,
  initial_plan_tier,
  region,
  acquisition_channel
FROM {{ ref('stg_sim_accounts') }}
