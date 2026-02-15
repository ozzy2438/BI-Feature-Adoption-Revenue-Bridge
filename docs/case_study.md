# Case Study: Feature Adoption -> Revenue Bridge

## Problem
Product teams often track usage metrics (events, activation, retention), while finance teams track revenue outcomes. Without a shared layer, it is difficult to explain which usage behavior drives growth — and equally important, what drives contraction and churn.

## Goal
Build a reproducible analytics system to answer:
1. Where users drop in onboarding funnel.
2. Which paid cohorts remain active after 6 months.
3. How multi-feature adoption changes account economics.
4. How quarterly revenue delta decomposes into expansion (new customers, upgrades, feature adoption lift) and contraction (churn, downgrades).

## Data Strategy
- Behavior signal: GA4 public sample.
- Transaction benchmark: UCI Online Retail II.
- Public revenue benchmark: SEC financial statement datasets.
- Main analytical entity: simulated Xero-like SaaS lifecycle events and monthly account revenue snapshots.

## Modeling Layers
1. Staging: schema normalization and timezone standardization.
2. Intermediate: event and revenue enrichment, first-event timestamps (per feature), benchmark features.
3. Marts:
   - Funnel monthly
   - Cohort retention (based on first payment, not signup)
   - Feature adoption (bank_feed_sync, multi_currency, recurring_invoices)
   - Revenue bridge quarterly (full growth decomposition)

## Revenue Bridge Logic

### Positive delta (mrr_delta > 0)
Classified in order:
1. New customer
2. Plan upgrade
3. Feature adoption lift (within 60 days, no upgrade)
4. Residual

### Negative delta (mrr_delta < 0)
Classified in order:
1. Churn (mrr_end = 0)
2. Contraction (mrr_end > 0 but decreased)
3. Residual

## Key Outputs
- `mart_funnel_monthly`
- `mart_cohort_retention`
- `mart_feature_adoption`
- `mart_revenue_bridge_quarterly`
- `mart_account_monthly_state`

## BI Story (Power BI — 4-page report)
1. **Funnel Leakage**: step conversion and drop-off by month.
2. **Cohort Retention**: paid-cohort heatmap with month-6 snapshot card.
3. **Feature Adoption Comparison**: adoption rate trends for 3 features, clustered bar for latest month.
4. **Revenue Bridge (Waterfall)**: quarterly waterfall with expansion (New, Upgrade, Feature Lift) and contraction (Churn, Contraction) components with share labels.

## Validation
- dbt schema and singular tests.
- Python quality checks for monotonic funnel, adoption bounds, bridge share consistency.
- Retention jump warning to detect suspicious simulated patterns.
- 13 unit tests covering bridge classification (positive + negative), simulation output, and multi-feature generation.

## Business Interpretation Template
- "Quarterly growth of X is mainly explained by component A (Y%), followed by B (Z%)."
- "Churn accounted for X% of negative delta, while contraction contributed Y%."
- "Cohorts after month M show improved month-6 retention after feature activation improvements."
- "Largest funnel leak is between step S1 and S2, with N% drop-off."
- "Multi-feature adopters show higher retention than single-feature users."
