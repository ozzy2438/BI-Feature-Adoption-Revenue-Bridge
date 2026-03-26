-- ═══════════════════════════════════════════════════════════════
-- VIEW 2: mart_cohort_retention  (Azure SQL / T-SQL)
-- Dashboard Page: Cohort Retention
-- Purpose: Paid-cohort retention heatmap (first payment month)
-- ═══════════════════════════════════════════════════════════════

CREATE OR ALTER VIEW mart_cohort_retention AS

WITH first_payment AS (
    SELECT
        account_id,
        DATEFROMPARTS(YEAR(MIN(CAST(event_ts_utc AS DATE))),
                      MONTH(MIN(CAST(event_ts_utc AS DATE))), 1) AS cohort_month
    FROM sim_events
    WHERE event_name = 'first_payment_received'
    GROUP BY account_id
),

active_months AS (
    SELECT
        r.account_id,
        CAST(r.[month] AS DATE) AS [month],
        fp.cohort_month
    FROM sim_revenue_monthly r
    INNER JOIN first_payment fp ON r.account_id = fp.account_id
    WHERE r.mrr_end > 0
),

aged AS (
    SELECT
        account_id,
        cohort_month,
        [month],
        DATEDIFF(MONTH, cohort_month, [month]) AS age_month
    FROM active_months
),

cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT account_id) AS cohort_size
    FROM aged
    WHERE age_month = 0
    GROUP BY cohort_month
)

SELECT
    a.cohort_month,
    a.age_month,
    COUNT(DISTINCT a.account_id) AS active_accounts,
    cs.cohort_size,
    ROUND(CAST(COUNT(DISTINCT a.account_id) AS FLOAT) / cs.cohort_size, 4) AS retention_rate
FROM aged a
INNER JOIN cohort_sizes cs ON a.cohort_month = cs.cohort_month
WHERE a.age_month >= 0
GROUP BY a.cohort_month, a.age_month, cs.cohort_size;
GO
