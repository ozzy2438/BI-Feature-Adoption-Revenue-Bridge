{{ config(materialized='view') }}

SELECT
  CAST(invoice_no AS STRING) AS invoice_no,
  CAST(customer_id AS STRING) AS customer_id,
  TIMESTAMP(invoice_ts_utc) AS invoice_ts_utc,
  DATE(TIMESTAMP(invoice_ts_utc)) AS invoice_date,
  SAFE_CAST(quantity AS INT64) AS quantity,
  SAFE_CAST(unit_price AS NUMERIC) AS unit_price,
  SAFE_CAST(is_cancelled AS INT64) AS is_cancelled,
  SAFE_CAST(total_amount AS NUMERIC) AS total_amount,
  CAST(country AS STRING) AS country
FROM {{ source('raw', 'uci_transactions') }}
WHERE invoice_no IS NOT NULL
