-- ============================================================
-- 02_mart_cohort_retention.sql
-- Monthly retention curve per paid-customer cohort.
-- ============================================================
CREATE OR ALTER VIEW mart_cohort_retention AS
WITH paid_cohorts AS (
    SELECT
        account_id,
        DATEFROMPARTS(
            YEAR(CAST(first_payment_ts AS DATE)),
            MONTH(CAST(first_payment_ts AS DATE)),
            1
        ) AS cohort_month
    FROM int_account_revenue_monthly
    WHERE first_payment_ts IS NOT NULL
    GROUP BY
        account_id,
        DATEFROMPARTS(
            YEAR(CAST(first_payment_ts AS DATE)),
            MONTH(CAST(first_payment_ts AS DATE)),
            1
        )
),

activity AS (
    SELECT
        c.account_id,
        c.cohort_month,
        s.month,
        DATEDIFF(MONTH, c.cohort_month, s.month) AS age_month,
        s.status,
        s.is_paid_active
    FROM mart_account_monthly_state s
    JOIN paid_cohorts c ON c.account_id = s.account_id
    WHERE s.month >= c.cohort_month
),

cohort_size AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT account_id) AS cohort_accounts
    FROM paid_cohorts
    GROUP BY cohort_month
),

retention AS (
    SELECT
        a.cohort_month,
        a.age_month,
        COUNT(DISTINCT CASE WHEN a.status = 'active' THEN a.account_id END) AS active_accounts
    FROM activity a
    GROUP BY a.cohort_month, a.age_month
)

SELECT
    r.cohort_month,
    r.age_month,
    r.active_accounts,
    CASE
        WHEN c.cohort_accounts = 0 OR c.cohort_accounts IS NULL THEN 0.0
        ELSE CAST(r.active_accounts AS FLOAT) / c.cohort_accounts
    END AS retention_rate
FROM retention r
JOIN cohort_size c ON c.cohort_month = r.cohort_month
WHERE r.age_month >= 0;
GO
