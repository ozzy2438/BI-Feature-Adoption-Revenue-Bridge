from __future__ import annotations

import argparse
from pathlib import Path

from google.cloud import bigquery

from config import get_settings


TABLE_FILE_PRIORITY = {
    "ga4_events": ["ga4_events_real.csv", "ga4_events.csv"],
    "uci_transactions": ["uci_transactions_real.csv", "uci_transactions.csv"],
    "sec_financials": ["sec_financials_real.csv", "sec_financials.csv"],
    "sim_accounts": ["sim_accounts.csv"],
    "sim_events": ["sim_events.csv"],
    "sim_revenue_monthly": ["sim_revenue_monthly.csv"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load raw CSV files into BigQuery raw dataset.")
    parser.add_argument("--input-dir", type=str, default="data/raw")
    parser.add_argument("--write-disposition", type=str, default="WRITE_TRUNCATE")
    return parser.parse_args()


def pick_file(input_dir: Path, candidates: list[str]) -> Path | None:
    for name in candidates:
        path = input_dir / name
        if path.exists():
            return path
    return None


def ensure_dataset(client: bigquery.Client, project_id: str, dataset_id: str, location: str) -> None:
    ds_ref = bigquery.Dataset(f"{project_id}.{dataset_id}")
    ds_ref.location = location
    client.create_dataset(ds_ref, exists_ok=True)


def load_csv(
    *,
    client: bigquery.Client,
    table_id: str,
    csv_path: Path,
    write_disposition: str,
) -> None:
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=write_disposition,
    )
    with csv_path.open("rb") as f:
        job = client.load_table_from_file(f, table_id, job_config=job_config)
    job.result()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    input_dir = Path(args.input_dir)

    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    client = bigquery.Client(project=settings.gcp_project_id)
    ensure_dataset(
        client=client,
        project_id=settings.gcp_project_id,
        dataset_id=settings.bq_raw_dataset,
        location=settings.bq_location,
    )

    for table_name, candidates in TABLE_FILE_PRIORITY.items():
        file_path = pick_file(input_dir, candidates)
        if file_path is None:
            print(f"[skip] {table_name}: no candidate file found in {input_dir}")
            continue

        table_id = f"{settings.gcp_project_id}.{settings.bq_raw_dataset}.{table_name}"
        load_csv(
            client=client,
            table_id=table_id,
            csv_path=file_path,
            write_disposition=args.write_disposition,
        )
        print(f"[ok] loaded {file_path.name} -> {table_id}")


if __name__ == "__main__":
    main()
