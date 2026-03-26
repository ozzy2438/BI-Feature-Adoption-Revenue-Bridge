-- ═══════════════════════════════════════════════════════════════
-- STEP 0: Create Base Tables on Azure SQL / SQL Server
-- Run this FIRST to create the raw tables and load CSV data
-- ═══════════════════════════════════════════════════════════════

-- Table 1: sim_accounts
CREATE TABLE sim_accounts (
    account_id          NVARCHAR(20) NOT NULL,
    signup_ts_utc       DATETIME2,
    signup_month        DATE,
    initial_plan_tier   NVARCHAR(20),
    region              NVARCHAR(10),
    acquisition_channel NVARCHAR(30),
    CONSTRAINT PK_sim_accounts PRIMARY KEY (account_id)
);

-- Table 2: sim_events
CREATE TABLE sim_events (
    account_id    NVARCHAR(20) NOT NULL,
    user_id       NVARCHAR(40),
    event_name    NVARCHAR(50) NOT NULL,
    event_ts_utc  DATETIME2,
    event_month   DATE,
    feature_name  NVARCHAR(30),
    metadata_json NVARCHAR(MAX)
);

CREATE INDEX IX_sim_events_account ON sim_events (account_id);
CREATE INDEX IX_sim_events_event   ON sim_events (event_name);

-- Table 3: sim_revenue_monthly
CREATE TABLE sim_revenue_monthly (
    account_id                    NVARCHAR(20) NOT NULL,
    [month]                       DATE NOT NULL,
    mrr_start                     DECIMAL(10,2),
    mrr_end                       DECIMAL(10,2),
    plan_tier                     NVARCHAR(20),
    [status]                      NVARCHAR(20),
    feature_x_adopted_flag        INT DEFAULT 0,
    feature_multi_currency_flag   INT DEFAULT 0,
    feature_recurring_invoices_flag INT DEFAULT 0,
    features_adopted_count        INT DEFAULT 0,
    is_new_customer               INT DEFAULT 0,
    is_plan_upgrade               INT DEFAULT 0,
    is_churn                      INT DEFAULT 0,
    is_contraction                INT DEFAULT 0,
    feature_adoption_lift_eligible INT DEFAULT 0,
    mrr_delta                     DECIMAL(10,2),
    bridge_component              NVARCHAR(30),
    CONSTRAINT PK_sim_revenue PRIMARY KEY (account_id, [month])
);

/*
LOADING DATA: Use one of these methods

METHOD 1: Azure Data Studio → Right-click table → Import Wizard

METHOD 2: BULK INSERT
   BULK INSERT sim_accounts FROM '/path/to/sim_accounts.csv'
   WITH (FIRSTROW = 2, FIELDTERMINATOR = ',', ROWTERMINATOR = '\n');

METHOD 3: setup_sqlserver.py script (automated)
   export SQL_PASSWORD='YourPassword'
   python setup_sqlserver.py
*/
