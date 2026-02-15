from __future__ import annotations

import argparse
import json
from pathlib import Path

from google.cloud import bigquery

from config import get_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run data quality checks on mart tables.")
    parser.add_argument("--output", type=str, default="data/outputs/quality_report.json")
    return parser.parse_args()


def check_adoption_bounds(client: bigquery.Client, project_id: str, dataset: str) -> dict:
    query = f"""
    SELECT COUNT(*) AS bad_rows
    FROM `{project_id}.{dataset}.mart_feature_adoption`
    WHERE adoption_rate < 0 OR adoption_rate > 1
    """
    bad_rows = list(client.query(query).result())[0].bad_rows
    return {
        "check": "adoption_rate_bounds",
        "status": "pass" if bad_rows == 0 else "fail",
        "bad_rows": int(bad_rows),
    }


def check_bridge_share(client: bigquery.Client, project_id: str, dataset: str) -> dict:
    query = f"""
    WITH share AS (
      SELECT
        quarter,
        SUM(CASE WHEN amount > 0 THEN share_pct ELSE 0 END) AS share_sum,
        SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) AS total_positive_delta
      FROM `{project_id}.{dataset}.mart_revenue_bridge_quarterly`
      GROUP BY quarter
    )
    SELECT COUNT(*) AS bad_rows
    FROM share
    WHERE total_positive_delta > 0
      AND ABS(share_sum - 1.0) > 0.1
    """
    bad_rows = list(client.query(query).result())[0].bad_rows
    return {
        "check": "bridge_share_sum",
        "status": "pass" if bad_rows == 0 else "fail",
        "bad_rows": int(bad_rows),
    }


def check_funnel_monotonic(client: bigquery.Client, project_id: str, dataset: str) -> dict:
    query = f"""
    WITH ordered AS (
      SELECT
        month,
        CASE step_name
          WHEN 'Signup' THEN 1
          WHEN 'First Invoice Created' THEN 2
          WHEN 'First Payment Received' THEN 3
          WHEN 'App Integration Connected' THEN 4
          WHEN 'Plan Upgrade' THEN 5
        END AS step_order,
        users_at_step
      FROM `{project_id}.{dataset}.mart_funnel_monthly`
    ),
    chk AS (
      SELECT
        month,
        step_order,
        users_at_step,
        LAG(users_at_step) OVER (PARTITION BY month ORDER BY step_order) AS prev_users
      FROM ordered
    )
    SELECT COUNT(*) AS bad_rows
    FROM chk
    WHERE prev_users IS NOT NULL AND users_at_step > prev_users
    """
    bad_rows = list(client.query(query).result())[0].bad_rows
    return {
        "check": "funnel_monotonic",
        "status": "pass" if bad_rows == 0 else "fail",
        "bad_rows": int(bad_rows),
    }


def check_retention_jump_warning(client: bigquery.Client, project_id: str, dataset: str) -> dict:
    query = f"""
    WITH x AS (
      SELECT
        cohort_month,
        age_month,
        retention_rate,
        LAG(retention_rate) OVER (PARTITION BY cohort_month ORDER BY age_month) AS prev_retention
      FROM `{project_id}.{dataset}.mart_cohort_retention`
    )
    SELECT COUNT(*) AS warning_rows
    FROM x
    WHERE prev_retention IS NOT NULL AND retention_rate - prev_retention > 0.25
    """
    warning_rows = list(client.query(query).result())[0].warning_rows
    return {
        "check": "retention_jump_warning",
        "status": "warn" if warning_rows > 0 else "pass",
        "warning_rows": int(warning_rows),
    }


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    settings = get_settings()
    client = bigquery.Client(project=settings.gcp_project_id)

    checks = [
        check_adoption_bounds(client, settings.gcp_project_id, settings.bq_analytics_dataset),
        check_bridge_share(client, settings.gcp_project_id, settings.bq_analytics_dataset),
        check_funnel_monotonic(client, settings.gcp_project_id, settings.bq_analytics_dataset),
        check_retention_jump_warning(client, settings.gcp_project_id, settings.bq_analytics_dataset),
    ]

    failed = [c for c in checks if c["status"] == "fail"]
    report = {
        "status": "pass" if not failed else "fail",
        "checks": checks,
        "failed_count": len(failed),
    }

    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote quality report to {output}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
