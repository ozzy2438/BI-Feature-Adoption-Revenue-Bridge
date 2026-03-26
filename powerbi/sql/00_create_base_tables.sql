-- ============================================================
-- 00_create_base_tables.sql
-- Creates staging tables and intermediate views.
-- Run BEFORE loading CSV data.
-- ============================================================

-- ── Staging: sim_accounts ─────────────────────────────────
DROP TABLE IF EXISTS stg_sim_accounts;
CREATE TABLE stg_sim_accounts (
    account_id          NVARCHAR(50)  NOT NULL,
    signup_ts_utc       DATETIME2,
    signup_month        DATE,
    initial_plan_tier   NVARCHAR(50),
    region              NVARCHAR(50),
    acquisition_channel NVARCHAR(100)
);
GO

-- ── Staging: sim_events ───────────────────────────────────
DROP TABLE IF EXISTS stg_sim_events;
CREATE TABLE stg_sim_events (
    account_id    NVARCHAR(50),
    user_id       NVARCHAR(100),
    event_name    NVARCHAR(100),
    event_ts_utc  DATETIME2,
    event_month   DATE,
    feature_name  NVARCHAR(100),
    metadata_json NVARCHAR(MAX)
);
GO

-- ── Staging: sim_revenue_monthly ─────────────────────────
DROP TABLE IF EXISTS stg_sim_revenue_monthly;
CREATE TABLE stg_sim_revenue_monthly (
    account_id                      NVARCHAR(50),
    month                           DATE,
    mrr_start                       DECIMAL(18,4),
    mrr_end                         DECIMAL(18,4),
    plan_tier                       NVARCHAR(50),
    status                          NVARCHAR(50),
    feature_x_adopted_flag          INT,
    feature_multi_currency_flag     INT,
    feature_recurring_invoices_flag INT,
    features_adopted_count          INT,
    is_new_customer                 INT,
    is_plan_upgrade                 INT,
    is_churn                        INT,
    is_contraction                  INT,
    feature_adoption_lift_eligible  INT,
    mrr_delta                       DECIMAL(18,4),
    bridge_component                NVARCHAR(100)
);
GO

-- ============================================================
-- Intermediate view: int_saas_simulated_accounts
-- ============================================================
CREATE OR ALTER VIEW int_saas_simulated_accounts AS
SELECT
    account_id,
    signup_ts_utc,
    signup_month        AS cohort_month,
    initial_plan_tier,
    region,
    acquisition_channel
FROM stg_sim_accounts;
GO

-- ============================================================
-- Intermediate view: int_saas_simulated_events
-- (Simplified: GA4/UCI enrichment omitted for SQL Server)
-- ============================================================
CREATE OR ALTER VIEW int_saas_simulated_events AS
WITH adoption_points AS (
    SELECT
        account_id,
        MIN(event_ts_utc) AS feature_first_adopted_ts
    FROM stg_sim_events
    WHERE event_name = 'feature_activated'
    GROUP BY account_id
)
SELECT
    e.account_id,
    e.user_id,
    e.event_name,
    e.event_ts_utc,
    e.event_month,
    e.feature_name,
    e.metadata_json,
    a.feature_first_adopted_ts
FROM stg_sim_events e
LEFT JOIN adoption_points a ON a.account_id = e.account_id;
GO

-- ============================================================
-- Intermediate view: int_account_revenue_monthly
-- ============================================================
CREATE OR ALTER VIEW int_account_revenue_monthly AS
WITH first_events AS (
    SELECT
        account_id,
        MIN(CASE WHEN event_name = 'signup'                                              THEN event_ts_utc END) AS signup_ts,
        MIN(CASE WHEN event_name = 'first_payment_received'                              THEN event_ts_utc END) AS first_payment_ts,
        MIN(CASE WHEN event_name = 'plan_upgrade'                                        THEN event_ts_utc END) AS first_upgrade_ts,
        MIN(CASE WHEN event_name = 'feature_activated' AND feature_name = 'bank_feed_sync'      THEN event_ts_utc END) AS feature_adopted_ts,
        MIN(CASE WHEN event_name = 'feature_activated' AND feature_name = 'multi_currency'      THEN event_ts_utc END) AS feature_multi_currency_ts,
        MIN(CASE WHEN event_name = 'feature_activated' AND feature_name = 'recurring_invoices'  THEN event_ts_utc END) AS feature_recurring_invoices_ts
    FROM stg_sim_events
    GROUP BY account_id
)
SELECT
    r.account_id,
    r.month,
    r.mrr_start,
    r.mrr_end,
    r.plan_tier,
    r.status,
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
    CAST(DATEADD(QUARTER, DATEDIFF(QUARTER, 0, r.month), 0) AS DATE) AS quarter,
    IIF(r.mrr_end > 0, 1, 0)                                         AS is_paid_active
FROM stg_sim_revenue_monthly r
LEFT JOIN first_events f ON f.account_id = r.account_id
WHERE r.account_id IS NOT NULL;
GO
