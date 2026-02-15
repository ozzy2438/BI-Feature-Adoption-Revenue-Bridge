{{ config(materialized='view') }}

SELECT
  CAST(fiscal_quarter AS STRING) AS fiscal_quarter,
  CAST(company_name AS STRING) AS company_name,
  CAST(cik AS STRING) AS cik,
  SAFE_CAST(revenue_usd AS NUMERIC) AS revenue_usd,
  DATE(filed_date) AS filed_date
FROM {{ source('raw', 'sec_financials') }}
WHERE fiscal_quarter IS NOT NULL
