from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

UCI_URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download and clean UCI Online Retail II dataset.")
    parser.add_argument("--output", type=str, default="data/raw/uci_transactions_real.csv")
    parser.add_argument("--max-rows", type=int, default=500000)
    return parser.parse_args()


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    rename_map = {
        "invoice": "invoice_no",
        "invoicedate": "invoice_ts_utc",
        "invoice_date": "invoice_ts_utc",
        "price": "unit_price",
        "customer_id": "customer_id",
    }
    for old, new in rename_map.items():
        if old in df.columns:
            df = df.rename(columns={old: new})

    required = ["invoice_no", "quantity", "invoice_ts_utc", "unit_price", "country"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"UCI file missing expected columns: {missing}")

    if "customer_id" not in df.columns:
        df["customer_id"] = "unknown"

    df["invoice_no"] = df["invoice_no"].astype(str)
    df["is_cancelled"] = df["invoice_no"].str.startswith("C").astype(int)

    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0)
    df["invoice_ts_utc"] = pd.to_datetime(df["invoice_ts_utc"], errors="coerce", utc=True)
    df = df.dropna(subset=["invoice_ts_utc"])

    df["customer_id"] = df["customer_id"].fillna("unknown").astype(str)
    df["total_amount"] = (df["quantity"] * df["unit_price"]).round(2)

    return df[
        [
            "invoice_no",
            "customer_id",
            "invoice_ts_utc",
            "quantity",
            "unit_price",
            "is_cancelled",
            "total_amount",
            "country",
        ]
    ]


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(UCI_URL, timeout=120)
    response.raise_for_status()

    frames: list[pd.DataFrame] = []
    with zipfile.ZipFile(io.BytesIO(response.content), "r") as zf:
        xlsx_name = next((n for n in zf.namelist() if n.lower().endswith(".xlsx")), None)
        if xlsx_name is None:
            raise FileNotFoundError("No .xlsx file found inside UCI zip archive.")

        with zf.open(xlsx_name) as f:
            xlsx_bytes = io.BytesIO(f.read())
            sheet_names = pd.ExcelFile(xlsx_bytes).sheet_names
            for sheet in sheet_names:
                xlsx_bytes.seek(0)
                frame = pd.read_excel(xlsx_bytes, sheet_name=sheet)
                frames.append(frame)

    raw_df = pd.concat(frames, ignore_index=True)
    clean_df = normalize_columns(raw_df)

    if args.max_rows > 0 and len(clean_df) > args.max_rows:
        clean_df = clean_df.head(args.max_rows)

    clean_df.to_csv(output, index=False)
    print(f"Wrote {len(clean_df)} rows to {output}")


if __name__ == "__main__":
    main()
