-- ============================================================
-- 04_mart_revenue_bridge_quarterly.sql
-- Quarterly revenue waterfall decomposed by bridge component.
-- ============================================================
CREATE OR ALTER VIEW mart_revenue_bridge_quarterly AS
WITH classified AS (
    SELECT
        CAST(DATEADD(QUARTER, DATEDIFF(QUARTER, 0, month), 0) AS DATE) AS quarter,
        bridge_component,
        mrr_delta AS amount
    FROM mart_account_monthly_state
),

agg AS (
    SELECT
        quarter,
        bridge_component,
        SUM(amount) AS amount
    FROM classified
    GROUP BY quarter, bridge_component
),

total_positive AS (
    SELECT
        quarter,
        SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_positive_delta
    FROM agg
    GROUP BY quarter
)

SELECT
    a.quarter,
    a.bridge_component,
    a.amount,
    CASE
        WHEN t.total_positive_delta = 0 OR t.total_positive_delta IS NULL THEN 0.0
        ELSE CAST(CASE WHEN a.amount > 0 THEN a.amount ELSE 0.0 END AS FLOAT)
             / t.total_positive_delta
    END AS share_pct
FROM agg a
JOIN total_positive t ON t.quarter = a.quarter;
GO
