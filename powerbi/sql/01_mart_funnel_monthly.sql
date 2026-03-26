-- ============================================================
-- 01_mart_funnel_monthly.sql
-- Onboarding funnel conversion by signup cohort month.
-- ============================================================
CREATE OR ALTER VIEW mart_funnel_monthly AS
WITH per_account AS (
    SELECT
        account_id,
        CAST(MIN(CASE WHEN event_name = 'signup'                   THEN event_ts_utc END) AS DATE) AS signup_date,
        CAST(MIN(CASE WHEN event_name = 'first_invoice_created'    THEN event_ts_utc END) AS DATE) AS first_invoice_date,
        CAST(MIN(CASE WHEN event_name = 'first_payment_received'   THEN event_ts_utc END) AS DATE) AS first_payment_date,
        CAST(MIN(CASE WHEN event_name = 'app_integration_connected'THEN event_ts_utc END) AS DATE) AS app_integration_date,
        CAST(MIN(CASE WHEN event_name = 'plan_upgrade'             THEN event_ts_utc END) AS DATE) AS plan_upgrade_date
    FROM int_saas_simulated_events
    GROUP BY account_id
),

cohort AS (
    SELECT
        account_id,
        DATEFROMPARTS(YEAR(signup_date), MONTH(signup_date), 1) AS month,
        signup_date,
        first_invoice_date,
        first_payment_date,
        app_integration_date,
        plan_upgrade_date
    FROM per_account
    WHERE signup_date IS NOT NULL
),

step_counts AS (
    SELECT month, 'Signup'                    AS step_name, 1 AS step_order, COUNT(DISTINCT account_id) AS users_at_step FROM cohort                                          GROUP BY month
    UNION ALL
    SELECT month, 'First Invoice Created',    2,            COUNT(DISTINCT account_id) FROM cohort WHERE first_invoice_date    IS NOT NULL GROUP BY month
    UNION ALL
    SELECT month, 'First Payment Received',   3,            COUNT(DISTINCT account_id) FROM cohort WHERE first_payment_date    IS NOT NULL GROUP BY month
    UNION ALL
    SELECT month, 'App Integration Connected',4,            COUNT(DISTINCT account_id) FROM cohort WHERE app_integration_date  IS NOT NULL GROUP BY month
    UNION ALL
    SELECT month, 'Plan Upgrade',             5,            COUNT(DISTINCT account_id) FROM cohort WHERE plan_upgrade_date     IS NOT NULL GROUP BY month
),

calc AS (
    SELECT
        month,
        step_name,
        step_order,
        users_at_step,
        LAG(users_at_step) OVER (PARTITION BY month ORDER BY step_order) AS prev_users
    FROM step_counts
)

SELECT
    month,
    step_name,
    step_order,
    users_at_step,
    CASE
        WHEN prev_users IS NULL OR prev_users = 0 THEN 1.0
        ELSE CAST(users_at_step AS FLOAT) / prev_users
    END AS conversion_from_prev,
    CASE
        WHEN prev_users IS NULL OR prev_users = 0 THEN 0.0
        ELSE 1.0 - CAST(users_at_step AS FLOAT) / prev_users
    END AS dropoff_from_prev
FROM calc;
GO
