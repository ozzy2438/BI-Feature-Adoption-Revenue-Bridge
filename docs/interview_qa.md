# Interview Q&A Prep

## 1) Why hybrid data instead of only synthetic?
Hybrid keeps the project credible. Real public datasets anchor behavior and transaction distributions, while synthetic SaaS events let us model missing lifecycle steps (invoice, integration, plan upgrade) end-to-end.

## 2) Why BigQuery + dbt?
GA4 public data is native in BigQuery, and dbt gives a transparent semantic layer with tests and reusable models.

## 3) How do you avoid overclaiming causality?
This project uses deterministic attribution rules, not causal inference. We state this explicitly and keep a residual bucket.

## 4) Why is SEC data not in core attribution?
SEC data is company-level benchmark context, not account-level causal input. It informs narrative and sanity checks.

## 5) How is feature adoption rate defined?
`adopted_active_accounts / eligible_active_accounts` on monthly grain, tracked separately for each feature (bank_feed_sync, multi_currency, recurring_invoices).

## 6) How do you validate data quality?
- Unique account-month grain in state table.
- Adoption rate bounds [0,1].
- Funnel monotonicity by step order.
- Bridge share consistency per quarter.
- 13 unit tests covering classification, simulation, and multi-feature logic.

## 7) What are known limitations?
- Synthetic assumptions influence absolute values.
- Attribution window and precedence are policy choices.
- No real-time ingestion in this version.

## 8) How would you productionize next?
- Add scheduled ingestion jobs.
- Replace synthetic layer with event instrumentation from product backend.
- Add versioned metric contracts and data observability alerts.

## 9) How do you handle churn and contraction in the bridge?
Negative MRR delta is classified separately: **Churn** when mrr_end = 0 (account fully lost), **Contraction** when mrr_end > 0 but decreased (downgrade). This gives the waterfall a complete growth decomposition — expansion components on the positive side, churn and contraction on the negative side.

## 10) Why track multiple features instead of just one?
A single feature makes the adoption analysis trivial. Tracking bank_feed_sync, multi_currency, and recurring_invoices lets us compare adoption curves, identify which features drive the most expansion revenue, and show that multi-feature adopters have different retention and economics than single-feature users.

## 11) Why base retention cohorts on first payment instead of signup?
Signup-based cohorts mix free-trial users who never convert with paying customers. Using first payment as the cohort anchor ensures month-0 retention is ~100% and subsequent months measure true paid customer retention — which is the metric finance and product teams actually care about.

## 12) What does the Feature Impact Matrix show?
It cross-tabulates each feature (adopted vs not-adopted) against churn rate, contraction rate, and avg MRR — per month. It also segments by feature count (0, 1, 2, 3). This answers: "Do bank_feed_sync adopters churn less?", "What is the MRR uplift for multi-feature accounts?", and "Is there a feature count threshold where churn drops significantly?" — the kind of questions that turn a descriptive dashboard into a product strategy tool.
