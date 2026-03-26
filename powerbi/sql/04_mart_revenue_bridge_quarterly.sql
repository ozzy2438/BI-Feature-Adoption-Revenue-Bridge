-- ═══════════════════════════════════════════════════════════════
-- VIEW 4: mart_revenue_bridge_quarterly  (Azure SQL / T-SQL)
-- Dashboard Page: Revenue Bridge (Waterfall)
-- Purpose: Quarterly revenue waterfall decomposition
-- ═══════════════════════════════════════════════════════════════

CREATE OR ALTER VIEW mart_revenue_bridge_quarterly AS

WITH quarterly AS (
    SELECT
        CONCAT(YEAR([month]), 'Q', DATEPART(QUARTER, [month])) AS [quarter],
        bridge_component,
        mrr_delta
    FROM sim_revenue_monthly
),

agg AS (
    SELECT
        [quarter],
        bridge_component,
        ROUND(SUM(mrr_delta), 2) AS amount
    FROM quarterly
    GROUP BY [quarter], bridge_component
),

total_positive AS (
    SELECT
        [quarter],
        SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_positive_delta
    FROM agg
    GROUP BY [quarter]
)

SELECT
    a.[quarter],
    a.bridge_component,
    a.amount,
    CASE
        WHEN t.total_positive_delta = 0 THEN 0.0
        ELSE ROUND(
            CASE WHEN a.amount > 0 THEN a.amount ELSE 0 END
            / t.total_positive_delta * 100, 2)
    END AS share_pct,
    CASE a.bridge_component
        WHEN 'New Customers' THEN 1
        WHEN 'Plan Upgrade' THEN 2
        WHEN 'Feature Adoption Lift' THEN 3
        WHEN 'Other/Residual' THEN 4
        WHEN 'Contraction' THEN 5
        WHEN 'Churn' THEN 6
        ELSE 99
    END AS bridge_sort_order
FROM agg a
INNER JOIN total_positive t ON a.[quarter] = t.[quarter];
GO
