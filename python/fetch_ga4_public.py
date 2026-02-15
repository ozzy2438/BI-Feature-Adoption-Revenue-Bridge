from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

import pandas as pd
from google.cloud import bigquery


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch GA4 public sample events into a local CSV.")
    parser.add_argument("--start-date", type=str, default="2020-11-01")
    parser.add_argument("--end-date", type=str, default="2021-01-31")
    parser.add_argument("--row-limit", type=int, default=500000)
    parser.add_argument("--output", type=str, default="data/raw/ga4_events_real.csv")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start_date = dt.date.fromisoformat(args.start_date)
    end_date = dt.date.fromisoformat(args.end_date)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    client = bigquery.Client()

    query = """
    SELECT
      user_pseudo_id AS user_id,
      TIMESTAMP_MICROS(event_timestamp) AS event_ts_utc,
      LOWER(event_name) AS event_name,
      IFNULL(traffic_source.source, 'unknown') AS source,
      IFNULL(geo.country, 'unknown') AS country
    FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
    WHERE _TABLE_SUFFIX BETWEEN FORMAT_DATE('%Y%m%d', @start_date) AND FORMAT_DATE('%Y%m%d', @end_date)
      AND user_pseudo_id IS NOT NULL
    LIMIT @row_limit
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("start_date", "DATE", start_date),
            bigquery.ScalarQueryParameter("end_date", "DATE", end_date),
            bigquery.ScalarQueryParameter("row_limit", "INT64", args.row_limit),
        ]
    )

    df: pd.DataFrame = client.query(query, job_config=job_config).to_dataframe()
    df.to_csv(output, index=False)

    print(f"Wrote {len(df)} rows to {output}")


if __name__ == "__main__":
    main()
