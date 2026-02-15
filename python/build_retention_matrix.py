from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

from config import get_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export cohort retention matrix from mart table.")
    parser.add_argument("--output", type=str, default="data/outputs/retention_matrix.csv")
    parser.add_argument("--max-age", type=int, default=12)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    settings = get_settings()
    client = bigquery.Client(project=settings.gcp_project_id)

    query = f"""
    SELECT
      cohort_month,
      age_month,
      retention_rate
    FROM `{settings.gcp_project_id}.{settings.bq_analytics_dataset}.mart_cohort_retention`
    WHERE age_month <= @max_age
    ORDER BY cohort_month, age_month
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("max_age", "INT64", args.max_age),
        ]
    )

    df = client.query(query, job_config=job_config).to_dataframe()
    matrix = df.pivot(index="cohort_month", columns="age_month", values="retention_rate").sort_index()
    matrix.to_csv(output)

    print(f"Wrote retention matrix with {len(matrix)} cohorts to {output}")


if __name__ == "__main__":
    main()
