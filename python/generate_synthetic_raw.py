from __future__ import annotations

import argparse
import datetime as dt
import random
from collections import defaultdict
from pathlib import Path

from bridge_logic import (
    build_monthly_revenue,
    month_start,
    simulate_accounts,
    simulate_events,
    write_csv,
)


def build_ga4_rows(sim_events: list[dict], account_channel: dict[str, str], account_region: dict[str, str]) -> list[dict]:
    rows: list[dict] = []
    for event in sim_events:
        rows.append(
            {
                "user_id": event["user_id"],
                "event_ts_utc": event["event_ts_utc"],
                "event_name": event["event_name"],
                "source": account_channel[event["account_id"]],
                "country": account_region[event["account_id"]],
            }
        )
    return rows


def build_uci_rows(revenue_rows: list[dict], account_region: dict[str, str]) -> list[dict]:
    rows: list[dict] = []
    invoice_num = 100000

    for record in revenue_rows:
        if record["mrr_delta"] <= 0:
            continue
        invoice_num += 1
        quantity = 1
        unit_price = round(float(record["mrr_delta"]), 2)
        rows.append(
            {
                "invoice_no": str(invoice_num),
                "customer_id": record["account_id"],
                "invoice_ts_utc": f"{record['month']}T10:00:00+00:00",
                "quantity": quantity,
                "unit_price": unit_price,
                "is_cancelled": 0,
                "total_amount": round(quantity * unit_price, 2),
                "country": account_region[record["account_id"]],
            }
        )

    return rows


def build_sec_rows(start_month: dt.date, months: int, seed: int) -> list[dict]:
    rng = random.Random(seed + 101)
    companies = [
        ("Sample SaaS A", "1000001", 12_500_000),
        ("Sample SaaS B", "1000002", 8_200_000),
        ("Sample SaaS C", "1000003", 6_700_000),
    ]

    rows: list[dict] = []
    quarter_map: defaultdict[tuple[str, str], float] = defaultdict(float)

    for i in range(months):
        month = dt.date(start_month.year + (start_month.month - 1 + i) // 12, ((start_month.month - 1 + i) % 12) + 1, 1)
        quarter = (month.month - 1) // 3 + 1
        quarter_key = f"{month.year}-Q{quarter}"
        for name, cik, baseline in companies:
            growth_factor = 1.0 + (i * 0.012) + rng.uniform(-0.01, 0.02)
            quarter_map[(quarter_key, cik)] += baseline * growth_factor / 3
            rows.append(
                {
                    "fiscal_quarter": quarter_key,
                    "company_name": name,
                    "cik": cik,
                    "revenue_usd": round(quarter_map[(quarter_key, cik)], 2),
                    "filed_date": f"{month.year}-{month.month:02d}-28",
                }
            )

    deduped: dict[tuple[str, str], dict] = {}
    for row in rows:
        deduped[(row["fiscal_quarter"], row["cik"])] = row
    return list(deduped.values())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic raw datasets for Feature Adoption -> Revenue Bridge.")
    parser.add_argument("--accounts", type=int, default=2500)
    parser.add_argument("--months", type=int, default=18)
    parser.add_argument("--start-month", type=str, default="2024-01-01")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=str, default="data/raw")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    start_month = month_start(dt.date.fromisoformat(args.start_month))

    accounts = simulate_accounts(
        n_accounts=args.accounts,
        start_month=start_month,
        months=args.months,
        seed=args.seed,
    )
    sim_events = simulate_events(accounts=accounts, seed=args.seed)
    revenue_rows = build_monthly_revenue(
        accounts=accounts,
        events=sim_events,
        start_month=start_month,
        months=args.months,
        seed=args.seed,
    )

    sim_accounts_rows = [
        {
            "account_id": a.account_id,
            "signup_ts_utc": a.signup_ts_utc.isoformat(),
            "signup_month": a.signup_month.isoformat(),
            "initial_plan_tier": a.initial_plan_tier,
            "region": a.region,
            "acquisition_channel": a.acquisition_channel,
        }
        for a in accounts
    ]

    account_channel = {a.account_id: a.acquisition_channel for a in accounts}
    account_region = {a.account_id: a.region for a in accounts}

    ga4_rows = build_ga4_rows(sim_events, account_channel, account_region)
    uci_rows = build_uci_rows(revenue_rows, account_region)
    sec_rows = build_sec_rows(start_month=start_month, months=args.months, seed=args.seed)

    write_csv(output_dir / "sim_accounts.csv", sim_accounts_rows)
    write_csv(output_dir / "sim_events.csv", sim_events)
    write_csv(output_dir / "sim_revenue_monthly.csv", revenue_rows)
    write_csv(output_dir / "ga4_events.csv", ga4_rows)
    write_csv(output_dir / "uci_transactions.csv", uci_rows)
    write_csv(output_dir / "sec_financials.csv", sec_rows)

    print(f"Generated raw files in {output_dir.resolve()}")
    print(f"Accounts: {len(sim_accounts_rows)} | Events: {len(sim_events)} | Revenue rows: {len(revenue_rows)}")


if __name__ == "__main__":
    main()
