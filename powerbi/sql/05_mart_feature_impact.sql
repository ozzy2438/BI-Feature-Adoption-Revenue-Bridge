-- ============================================================
-- 05_mart_feature_impact.sql
-- Adopted vs not-adopted comparison: churn, MRR, contraction.
-- ============================================================
CREATE OR ALTER VIEW mart_feature_impact AS
WITH monthly AS (
    SELECT
        account_id,
        month,
        mrr_end,
        is_churn,
        is_contraction,
        features_adopted_count,
        feature_x_adopted_flag,
        feature_multi_currency_flag,
        feature_recurring_invoices_flag
    FROM mart_account_monthly_state
),

feature_segments AS (
    SELECT month, account_id, mrr_end, is_churn, is_contraction, 'bank_feed_sync'     AS feature_name, feature_x_adopted_flag          AS is_adopted FROM monthly
    UNION ALL
    SELECT month, account_id, mrr_end, is_churn, is_contraction, 'multi_currency',      feature_multi_currency_flag      FROM monthly
    UNION ALL
    SELECT month, account_id, mrr_end, is_churn, is_contraction, 'recurring_invoices',  feature_recurring_invoices_flag  FROM monthly
),

per_feature AS (
    SELECT
        month,
        feature_name,
        CASE WHEN is_adopted = 1 THEN 'adopted' ELSE 'not_adopted' END AS segment,
        COUNT(DISTINCT account_id)                                      AS total_accounts,
        SUM(CASE WHEN is_churn       = 1 THEN 1 ELSE 0 END)            AS churned_accounts,
        CASE
            WHEN COUNT(DISTINCT account_id) = 0 THEN 0.0
            ELSE CAST(SUM(CASE WHEN is_churn = 1 THEN 1 ELSE 0 END) AS FLOAT)
                 / COUNT(DISTINCT account_id)
        END                                                             AS churn_rate,
        SUM(CASE WHEN is_contraction = 1 THEN 1 ELSE 0 END)            AS contracted_accounts,
        CASE
            WHEN COUNT(DISTINCT account_id) = 0 THEN 0.0
            ELSE CAST(SUM(CASE WHEN is_contraction = 1 THEN 1 ELSE 0 END) AS FLOAT)
                 / COUNT(DISTINCT account_id)
        END                                                             AS contraction_rate,
        AVG(CAST(mrr_end AS FLOAT))                                     AS avg_mrr,
        SUM(mrr_end)                                                    AS total_mrr
    FROM feature_segments
    GROUP BY month, feature_name, CASE WHEN is_adopted = 1 THEN 'adopted' ELSE 'not_adopted' END
),

by_count AS (
    SELECT
        month,
        'feature_count'                              AS feature_name,
        CAST(features_adopted_count AS NVARCHAR(10)) AS segment,
        COUNT(DISTINCT account_id)                   AS total_accounts,
        SUM(CASE WHEN is_churn       = 1 THEN 1 ELSE 0 END) AS churned_accounts,
        CASE
            WHEN COUNT(DISTINCT account_id) = 0 THEN 0.0
            ELSE CAST(SUM(CASE WHEN is_churn = 1 THEN 1 ELSE 0 END) AS FLOAT)
                 / COUNT(DISTINCT account_id)
        END                                          AS churn_rate,
        SUM(CASE WHEN is_contraction = 1 THEN 1 ELSE 0 END) AS contracted_accounts,
        CASE
            WHEN COUNT(DISTINCT account_id) = 0 THEN 0.0
            ELSE CAST(SUM(CASE WHEN is_contraction = 1 THEN 1 ELSE 0 END) AS FLOAT)
                 / COUNT(DISTINCT account_id)
        END                                          AS contraction_rate,
        AVG(CAST(mrr_end AS FLOAT))                  AS avg_mrr,
        SUM(mrr_end)                                 AS total_mrr
    FROM monthly
    GROUP BY month, CAST(features_adopted_count AS NVARCHAR(10))
)

SELECT * FROM per_feature
UNION ALL
SELECT * FROM by_count;
GO
