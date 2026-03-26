-- ============================================================
-- 03_mart_feature_adoption.sql
-- Monthly adoption rate per feature across active accounts.
-- ============================================================
CREATE OR ALTER VIEW mart_feature_adoption AS
WITH per_feature AS (
    SELECT
        month,
        'bank_feed_sync' AS feature_name,
        COUNT(DISTINCT CASE WHEN status = 'active'                             THEN account_id END) AS eligible_accounts,
        COUNT(DISTINCT CASE WHEN status = 'active' AND feature_x_adopted_flag          = 1 THEN account_id END) AS adopted_accounts
    FROM mart_account_monthly_state
    GROUP BY month

    UNION ALL

    SELECT
        month,
        'multi_currency',
        COUNT(DISTINCT CASE WHEN status = 'active'                             THEN account_id END),
        COUNT(DISTINCT CASE WHEN status = 'active' AND feature_multi_currency_flag      = 1 THEN account_id END)
    FROM mart_account_monthly_state
    GROUP BY month

    UNION ALL

    SELECT
        month,
        'recurring_invoices',
        COUNT(DISTINCT CASE WHEN status = 'active'                             THEN account_id END),
        COUNT(DISTINCT CASE WHEN status = 'active' AND feature_recurring_invoices_flag  = 1 THEN account_id END)
    FROM mart_account_monthly_state
    GROUP BY month
)

SELECT
    month,
    feature_name,
    eligible_accounts,
    adopted_accounts,
    CASE
        WHEN eligible_accounts = 0 OR eligible_accounts IS NULL THEN 0.0
        ELSE CAST(adopted_accounts AS FLOAT) / eligible_accounts
    END AS adoption_rate
FROM per_feature;
GO
