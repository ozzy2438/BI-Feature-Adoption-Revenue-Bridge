from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import pandas as pd
import requests

SEC_BASE = "https://www.sec.gov/files/dera/data/financial-statement-data-sets"
REVENUE_TAGS = {
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueNet",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download SEC financial statement data and extract revenue benchmark rows.")
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--quarter", type=int, default=4)
    parser.add_argument("--output", type=str, default="data/raw/sec_financials_real.csv")
    parser.add_argument("--top-n", type=int, default=200)
    return parser.parse_args()


def _download_zip(year: int, quarter: int) -> bytes:
    url = f"{SEC_BASE}/{year}q{quarter}.zip"
    headers = {"User-Agent": "FeatureAdoptionRevenueBridge/1.0 contact@example.com"}
    resp = requests.get(url, headers=headers, timeout=180)
    resp.raise_for_status()
    return resp.content


def _read_txt_from_zip(zbytes: bytes, name: str) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(zbytes), "r") as zf:
        with zf.open(name) as f:
            return pd.read_csv(f, sep="\t", dtype=str, low_memory=False)


def main() -> None:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    zbytes = _download_zip(args.year, args.quarter)
    sub = _read_txt_from_zip(zbytes, "sub.txt")
    num = _read_txt_from_zip(zbytes, "num.txt")

    num = num[num["tag"].isin(REVENUE_TAGS)].copy()
    num = num[num["uom"] == "USD"].copy()
    num["value"] = pd.to_numeric(num["value"], errors="coerce")
    num = num.dropna(subset=["value"])

    sub_cols = ["adsh", "cik", "name", "period", "filed"]
    num_cols = ["adsh", "tag", "version", "ddate", "qtrs", "value"]
    merged = num[num_cols].merge(sub[sub_cols], on="adsh", how="left")

    merged["ddate"] = pd.to_datetime(merged["ddate"], format="%Y%m%d", errors="coerce")
    merged["filed"] = pd.to_datetime(merged["filed"], format="%Y%m%d", errors="coerce")
    merged = merged.dropna(subset=["ddate", "cik", "name"])

    merged["fiscal_quarter"] = merged["ddate"].dt.to_period("Q").astype(str).str.replace("Q", "-Q", regex=False)

    out = (
        merged.sort_values(["cik", "ddate", "value"], ascending=[True, False, False])
        .groupby(["fiscal_quarter", "cik", "name"], as_index=False)
        .head(1)
        .sort_values("value", ascending=False)
        .head(args.top_n)
        .rename(columns={"name": "company_name", "value": "revenue_usd", "filed": "filed_date"})
    )

    out = out[["fiscal_quarter", "company_name", "cik", "revenue_usd", "filed_date"]]
    out["filed_date"] = out["filed_date"].dt.date.astype(str)
    out.to_csv(output, index=False)

    print(f"Wrote {len(out)} rows to {output}")


if __name__ == "__main__":
    main()
