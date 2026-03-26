-- ═══════════════════════════════════════════════════════════════
-- VIEW 6: mart_account_monthly_state  (Azure SQL / T-SQL)
-- Master Fact Table used by all dashboard pages
-- Purpose: Account-level monthly truth table with all flags
-- ═══════════════════════════════════════════════════════════════

CREATE OR ALTER VIEW mart_account_monthly_state AS

WITH first_events AS (
    SELECT
        account_id,
        MIN(CASE WHEN event_name = 'signup' THEN event_ts_utc END) AS signup_ts,
        MIN(CASE WHEN event_name = 'first_payment_received' THEN event_ts_utc END) AS first_payment_ts,
        MIN(CASE WHEN event_name = 'plan_upgrade' THEN event_ts_utc END) AS first_upgrade_ts,
        MIN(CASE WHEN event_name = 'feature_activated' AND feature_name = 'bank_feed_sync'
            THEN event_ts_utc END) AS feature_adopted_ts,
        MIN(CASE WHEN event_name = 'feature_activated' AND feature_name = 'multi_currency'
            THEN event_ts_utc END) AS feature_multi_currency_ts,
        MIN(CASE WHEN event_name = 'feature_activated' AND feature_name = 'recurring_invoices'
            THEN event_ts_utc END) AS feature_recurring_invoices_ts
    FROM sim_events
    GROUP BY account_id
)

SELECT
    r.account_id,
    r.[month],
    r.mrr_start,
    r.mrr_end,
    r.plan_tier,
    r.[status],
    r.feature_x_adopted_flag,
    r.feature_multi_currency_flag,
    r.feature_recurring_invoices_flag,
    r.features_adopted_count,
    r.is_new_customer,
    r.is_plan_upgrade,
    r.is_churn,
    r.is_contraction,
    r.feature_adoption_lift_eligible,
    r.mrr_delta,
    r.bridge_component,
    f.signup_ts,
    f.first_payment_ts,
    f.first_upgrade_ts,
    f.feature_adopted_ts,
    f.feature_multi_currency_ts,
    f.feature_recurring_invoices_ts,
    CONCAT(YEAR(r.[month]), 'Q', DATEPART(QUARTER, r.[month])) AS [quarter],
    CASE WHEN r.mrr_end > 0 THEN 1 ELSE 0 END AS is_paid_active
FROM sim_revenue_monthly r
LEFT JOIN first_events f ON r.account_id = f.account_id;
GO
