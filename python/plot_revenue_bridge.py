from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from google.cloud import bigquery

from config import get_settings


PREFERRED_ORDER = [
    "New Customers",
    "Plan Upgrade",
    "Feature Adoption Lift",
    "Other/Residual",
    "Contraction",
    "Churn",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot Revenue Bridge waterfall from mart_revenue_bridge_quarterly.")
    parser.add_argument("--quarter", type=str, default="", help="Quarter start date YYYY-MM-DD. Empty => auto select.")
    parser.add_argument("--min-positive", type=float, default=1000.0, help="Auto-select threshold for positive delta.")
    parser.add_argument("--output-dir", type=str, default="data/outputs")
    return parser.parse_args()


def choose_quarter(client: bigquery.Client, project_id: str, dataset: str, min_positive: float) -> dt.date:
    query = f"""
    WITH q AS (
      SELECT
        quarter,
        SUM(IF(amount > 0, amount, 0)) AS total_positive
      FROM `{project_id}.{dataset}.mart_revenue_bridge_quarterly`
      GROUP BY quarter
    )
    SELECT quarter
    FROM q
    WHERE total_positive >= @min_positive
    ORDER BY quarter DESC
    LIMIT 1
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("min_positive", "FLOAT64", float(min_positive))]
    )
    rows = list(client.query(query, job_config=job_config).result())
    if rows:
        return rows[0].quarter

    fallback_query = f"""
    WITH q AS (
      SELECT
        quarter,
        SUM(IF(amount > 0, amount, 0)) AS total_positive
      FROM `{project_id}.{dataset}.mart_revenue_bridge_quarterly`
      GROUP BY quarter
    )
    SELECT quarter
    FROM q
    WHERE total_positive > 0
    ORDER BY quarter DESC
    LIMIT 1
    """
    fallback = list(client.query(fallback_query).result())
    if not fallback:
        raise ValueError("No quarter with positive revenue contribution found.")
    return fallback[0].quarter


def fetch_bridge_df(client: bigquery.Client, project_id: str, dataset: str, quarter: dt.date) -> pd.DataFrame:
    query = f"""
    SELECT
      quarter,
      bridge_component,
      CAST(amount AS FLOAT64) AS amount,
      CAST(share_pct AS FLOAT64) AS share_pct
    FROM `{project_id}.{dataset}.mart_revenue_bridge_quarterly`
    WHERE quarter = @quarter
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("quarter", "DATE", quarter)]
    )
    df = client.query(query, job_config=job_config).to_dataframe()
    if df.empty:
        raise ValueError(f"No bridge rows found for quarter {quarter}")

    df["order"] = df["bridge_component"].apply(
        lambda c: PREFERRED_ORDER.index(c) if c in PREFERRED_ORDER else len(PREFERRED_ORDER)
    )
    df = df.sort_values(["order", "bridge_component"]).drop(columns=["order"]).reset_index(drop=True)
    return df


def plot_waterfall(df: pd.DataFrame, quarter: dt.date, output_png: Path) -> None:
    components = df["bridge_component"].tolist()
    amounts = df["amount"].tolist()

    starts = []
    running = 0.0
    for amount in amounts:
        starts.append(running)
        running += amount

    total_delta = running
    labels = components + ["Total Delta"]
    display_starts = starts + [0.0]
    display_amounts = amounts + [total_delta]

    colors = []
    for idx, amount in enumerate(display_amounts):
        if idx == len(display_amounts) - 1:
            colors.append("#0f172a")
        elif amount >= 0:
            colors.append("#2e7d32")
        else:
            colors.append("#c62828")

    fig, ax = plt.subplots(figsize=(11, 6))
    x = range(len(labels))

    ax.bar(x, display_amounts, bottom=display_starts, color=colors, edgecolor="black", linewidth=0.4)

    for i, (start, amount, label) in enumerate(zip(display_starts, display_amounts, labels)):
        y = start + amount
        offset = 250 if amount >= 0 else -450
        pct_text = ""
        if i < len(components) and amount > 0:
            share = float(df.iloc[i]["share_pct"]) * 100
            pct_text = f"\n({share:.1f}%)"
        ax.text(
            i,
            y + offset,
            f"{amount:,.0f}{pct_text}",
            ha="center",
            va="bottom" if amount >= 0 else "top",
            fontsize=9,
        )

    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=20, ha="right")
    ax.set_ylabel("Revenue Delta")
    ax.set_title(f"Revenue Bridge Waterfall - {quarter}")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.grid(axis="y", linestyle="--", alpha=0.25)

    fig.tight_layout()
    output_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_png, dpi=150)
    plt.close(fig)


def main() -> None:
    args = parse_args()
    settings = get_settings()
    client = bigquery.Client(project=settings.gcp_project_id)

    if args.quarter:
        quarter = dt.date.fromisoformat(args.quarter)
    else:
        quarter = choose_quarter(client, settings.gcp_project_id, settings.bq_analytics_dataset, args.min_positive)

    df = fetch_bridge_df(client, settings.gcp_project_id, settings.bq_analytics_dataset, quarter)

    output_dir = Path(args.output_dir)
    output_png = output_dir / f"revenue_bridge_waterfall_{quarter}.png"
    output_csv = output_dir / f"revenue_bridge_waterfall_{quarter}.csv"

    plot_waterfall(df, quarter, output_png)
    df.to_csv(output_csv, index=False)

    positive = df[df["amount"] > 0][["bridge_component", "amount", "share_pct"]].copy()
    positive["share_pct"] = (positive["share_pct"] * 100).round(2)

    print(f"Quarter selected: {quarter}")
    print(f"PNG: {output_png}")
    print(f"CSV: {output_csv}")
    if positive.empty:
        print("No positive components in selected quarter.")
    else:
        print("Positive contribution summary:")
        for _, row in positive.iterrows():
            print(f"- {row['bridge_component']}: amount={row['amount']:.2f}, share={row['share_pct']:.2f}%")


if __name__ == "__main__":
    main()
