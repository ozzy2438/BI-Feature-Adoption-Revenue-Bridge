-- ═══════════════════════════════════════════════════════════════
-- VIEW 3: mart_feature_adoption  (Azure SQL / T-SQL)
-- Dashboard Page: Feature Adoption Comparison
-- Purpose: Tracks adoption rate per feature over time
-- ═══════════════════════════════════════════════════════════════

CREATE OR ALTER VIEW mart_feature_adoption AS

WITH active_accounts AS (
    SELECT
        account_id,
        CAST([month] AS DATE) AS [month],
        feature_x_adopted_flag,
        feature_multi_currency_flag,
        feature_recurring_invoices_flag
    FROM sim_revenue_monthly
    WHERE [status] = 'active'
)

SELECT [month], N'bank_feed_sync' AS feature_name,
    COUNT(*) AS eligible_accounts,
    SUM(feature_x_adopted_flag) AS adopted_accounts,
    ROUND(CAST(SUM(feature_x_adopted_flag) AS FLOAT) / NULLIF(COUNT(*), 0), 4) AS adoption_rate
FROM active_accounts GROUP BY [month]

UNION ALL

SELECT [month], N'multi_currency',
    COUNT(*),
    SUM(feature_multi_currency_flag),
    ROUND(CAST(SUM(feature_multi_currency_flag) AS FLOAT) / NULLIF(COUNT(*), 0), 4)
FROM active_accounts GROUP BY [month]

UNION ALL

SELECT [month], N'recurring_invoices',
    COUNT(*),
    SUM(feature_recurring_invoices_flag),
    ROUND(CAST(SUM(feature_recurring_invoices_flag) AS FLOAT) / NULLIF(COUNT(*), 0), 4)
FROM active_accounts GROUP BY [month];
GO
