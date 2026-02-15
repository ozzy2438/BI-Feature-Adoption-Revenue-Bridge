from __future__ import annotations

import argparse
from pathlib import Path

from google.cloud import bigquery

from config import get_settings


MART_TABLES = [
    "mart_funnel_monthly",
    "mart_cohort_retention",
    "mart_feature_adoption",
    "mart_revenue_bridge_quarterly",
    "mart_account_monthly_state",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export mart tables to CSV for Power BI import.")
    parser.add_argument("--output-dir", type=str, default="data/outputs/powerbi_extracts")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    settings = get_settings()
    client = bigquery.Client(project=settings.gcp_project_id)

    for table_name in MART_TABLES:
        query = f"SELECT * FROM `{settings.gcp_project_id}.{settings.bq_analytics_dataset}.{table_name}`"
        df = client.query(query).to_dataframe()
        output_path = output_dir / f"{table_name}.csv"
        df.to_csv(output_path, index=False)
        print(f"[ok] {table_name}: {len(df)} rows -> {output_path}")


if __name__ == "__main__":
    main()
