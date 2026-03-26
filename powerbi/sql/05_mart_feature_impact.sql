-- ═══════════════════════════════════════════════════════════════
-- VIEW 5: mart_feature_impact  (Azure SQL / T-SQL)
-- Dashboard Page: Feature Impact Matrix
-- Purpose: Adopted vs not-adopted comparison per feature
-- ═══════════════════════════════════════════════════════════════

CREATE OR ALTER VIEW mart_feature_impact AS

WITH base AS (
    SELECT
        account_id,
        CAST([month] AS DATE) AS [month],
        mrr_end,
        is_churn,
        is_contraction,
        feature_x_adopted_flag,
        feature_multi_currency_flag,
        feature_recurring_invoices_flag,
        features_adopted_count
    FROM sim_revenue_monthly
),

feature_segments AS (
    SELECT [month], account_id, mrr_end, is_churn, is_contraction,
        N'bank_feed_sync' AS feature_name,
        CASE WHEN feature_x_adopted_flag = 1 THEN N'adopted' ELSE N'not_adopted' END AS segment
    FROM base

    UNION ALL

    SELECT [month], account_id, mrr_end, is_churn, is_contraction,
        N'multi_currency',
        CASE WHEN feature_multi_currency_flag = 1 THEN N'adopted' ELSE N'not_adopted' END
    FROM base

    UNION ALL

    SELECT [month], account_id, mrr_end, is_churn, is_contraction,
        N'recurring_invoices',
        CASE WHEN feature_recurring_invoices_flag = 1 THEN N'adopted' ELSE N'not_adopted' END
    FROM base
),

per_feature AS (
    SELECT
        [month],
        feature_name,
        segment,
        COUNT(DISTINCT account_id) AS total_accounts,
        SUM(is_churn) AS churned_accounts,
        ROUND(CAST(SUM(is_churn) AS FLOAT) / NULLIF(COUNT(DISTINCT account_id), 0), 4) AS churn_rate,
        SUM(is_contraction) AS contracted_accounts,
        ROUND(CAST(SUM(is_contraction) AS FLOAT) / NULLIF(COUNT(DISTINCT account_id), 0), 4) AS contraction_rate,
        ROUND(AVG(CAST(mrr_end AS FLOAT)), 2) AS avg_mrr,
        ROUND(SUM(CAST(mrr_end AS FLOAT)), 2) AS total_mrr
    FROM feature_segments
    GROUP BY [month], feature_name, segment
),

by_count AS (
    SELECT
        [month],
        N'feature_count' AS feature_name,
        CAST(features_adopted_count AS NVARCHAR(5)) AS segment,
        COUNT(DISTINCT account_id) AS total_accounts,
        SUM(is_churn) AS churned_accounts,
        ROUND(CAST(SUM(is_churn) AS FLOAT) / NULLIF(COUNT(DISTINCT account_id), 0), 4) AS churn_rate,
        SUM(is_contraction) AS contracted_accounts,
        ROUND(CAST(SUM(is_contraction) AS FLOAT) / NULLIF(COUNT(DISTINCT account_id), 0), 4) AS contraction_rate,
        ROUND(AVG(CAST(mrr_end AS FLOAT)), 2) AS avg_mrr,
        ROUND(SUM(CAST(mrr_end AS FLOAT)), 2) AS total_mrr
    FROM base
    GROUP BY [month], features_adopted_count
)

SELECT * FROM per_feature
UNION ALL
SELECT * FROM by_count;
GO
