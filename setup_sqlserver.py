#!/usr/bin/env python3
"""
setup_sqlserver.py
==================
One-command setup for the BI Feature Adoption SQL Server database.

Steps performed:
  1. Regenerate synthetic CSVs if columns are missing (runs generate_synthetic_raw.py)
  2. Create the BI_Feature_Adoption database (idempotent)
  3. Create staging tables + intermediate views  (00_create_base_tables.sql)
  4. Create mart views in dependency order       (06 first, then 01-05)
  5. Bulk-load the three CSV files into staging tables

Requirements:
    pip install pyodbc pandas

Usage:
    python setup_sqlserver.py
"""

import re
import sys
import subprocess
from pathlib import Path

import pandas as pd
import pyodbc

# ── Connection config ─────────────────────────────────────────────────────────
SERVER   = "localhost,1434"        # comma notation for non-default port
DATABASE = "BI_Feature_Adoption"
USERNAME = "Ozzy"
PASSWORD = "Allah241012!"
DRIVER   = "ODBC Driver 18 for SQL Server"

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
SQL_DIR      = PROJECT_ROOT / "powerbi" / "sql"
DATA_DIR     = PROJECT_ROOT / "data" / "raw"
PYTHON_DIR   = PROJECT_ROOT / "python"

# Mart files are run in dependency order (06 before 02-05 which reference it)
SQL_EXECUTION_ORDER = [
    "00_create_base_tables.sql",
    "06_mart_account_monthly_state.sql",
    "01_mart_funnel_monthly.sql",
    "02_mart_cohort_retention.sql",
    "03_mart_feature_adoption.sql",
    "04_mart_revenue_bridge_quarterly.sql",
    "05_mart_feature_impact.sql",
]

# CSV → staging table mapping (load order matters for FK-free schema)
CSV_TABLE_MAP = [
    ("sim_accounts.csv",        "stg_sim_accounts"),
    ("sim_events.csv",          "stg_sim_events"),
    ("sim_revenue_monthly.csv", "stg_sim_revenue_monthly"),
]

# Columns that must exist in sim_revenue_monthly; added in a later version of
# bridge_logic.py but missing from older cached CSVs.
REQUIRED_REVENUE_COLS = {
    "feature_multi_currency_flag",
    "feature_recurring_invoices_flag",
    "features_adopted_count",
    "is_churn",
    "is_contraction",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _conn_str(database: str = "master") -> str:
    return (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={database};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=yes;"
    )


def get_connection(database: str = "master") -> pyodbc.Connection:
    try:
        return pyodbc.connect(_conn_str(database))
    except pyodbc.Error as e:
        print(f"\nERROR: Could not connect to SQL Server ({SERVER}).")
        print(f"  → {e}")
        print("  Check that SQL Server is running and ODBC Driver 18 is installed.")
        sys.exit(1)


def execute_sql_file(conn: pyodbc.Connection, path: Path) -> None:
    """Split a T-SQL file on GO batch separators and execute each batch."""
    sql = path.read_text(encoding="utf-8")
    # Split on lines that contain only 'GO' (case-insensitive)
    batches = re.split(r"^\s*GO\s*$", sql, flags=re.MULTILINE | re.IGNORECASE)
    cursor = conn.cursor()
    for batch in batches:
        batch = batch.strip()
        if not batch:
            continue
        # Skip comment-only batches
        non_comment = re.sub(r"--[^\n]*", "", batch).strip()
        if not non_comment:
            continue
        try:
            cursor.execute(batch)
            conn.commit()
        except pyodbc.Error as e:
            print(f"\n  ERROR in {path.name}:")
            print(f"  {e}")
            print(f"  Failing batch (first 200 chars): {batch[:200]}")
            conn.rollback()
            raise
    print(f"  ✓  {path.name}")


def load_csv(conn: pyodbc.Connection, csv_path: Path, table: str) -> None:
    """Bulk-insert a CSV into a SQL Server staging table."""
    df = pd.read_csv(csv_path)
    # Replace NaN with None so pyodbc sends NULL
    df = df.where(pd.notnull(df), None)

    cols         = ", ".join(f"[{c}]" for c in df.columns)
    placeholders = ", ".join("?" * len(df.columns))
    sql          = f"INSERT INTO [{table}] ({cols}) VALUES ({placeholders})"

    rows   = [tuple(r) for r in df.itertuples(index=False, name=None)]
    cursor = conn.cursor()
    cursor.fast_executemany = True
    cursor.executemany(sql, rows)
    conn.commit()
    print(f"  ✓  {table}  —  {len(df):,} rows")


def regenerate_csvs() -> None:
    """Re-run the synthetic data generator if required columns are absent."""
    revenue_csv = DATA_DIR / "sim_revenue_monthly.csv"

    if revenue_csv.exists():
        existing_cols = set(pd.read_csv(revenue_csv, nrows=0).columns)
        missing       = REQUIRED_REVENUE_COLS - existing_cols
    else:
        missing = REQUIRED_REVENUE_COLS

    if not missing:
        print("  ✓  CSV files up-to-date (all required columns present)")
        return

    print(f"  ! sim_revenue_monthly.csv is missing: {missing}")
    print("  → Running generate_synthetic_raw.py …")
    result = subprocess.run(
        [sys.executable, str(PYTHON_DIR / "generate_synthetic_raw.py")],
        cwd=str(PYTHON_DIR),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print("\nERROR: Data generation failed:")
        print(result.stderr)
        sys.exit(1)
    print("  ✓  Synthetic data regenerated")


def create_database(conn_master: pyodbc.Connection) -> None:
    conn_master.autocommit = True
    cursor = conn_master.cursor()
    cursor.execute(
        f"IF NOT EXISTS (SELECT 1 FROM sys.databases WHERE name = N'{DATABASE}') "
        f"CREATE DATABASE [{DATABASE}];"
    )
    conn_master.autocommit = False
    print(f"  ✓  Database '{DATABASE}' ready")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("  BI Feature Adoption — SQL Server Setup")
    print("=" * 60)

    # 1. Ensure CSVs have all required columns
    print("\n[1/4]  Checking synthetic data …")
    regenerate_csvs()

    # 2. Create the target database
    print(f"\n[2/4]  Creating database '{DATABASE}' …")
    with get_connection("master") as conn_master:
        create_database(conn_master)

    # 3. Create staging tables, intermediate views, and mart views
    print("\n[3/4]  Creating tables and views …")
    with get_connection(DATABASE) as conn_db:
        for fname in SQL_EXECUTION_ORDER:
            execute_sql_file(conn_db, SQL_DIR / fname)

        # 4. Load CSV data into staging tables
        print("\n[4/4]  Loading CSV data …")
        for csv_name, table in CSV_TABLE_MAP:
            load_csv(conn_db, DATA_DIR / csv_name, table)

    # Done
    print("\n" + "=" * 60)
    print("  Setup complete!")
    print()
    print(f"  Server  : {SERVER}")
    print(f"  Database: {DATABASE}")
    print()
    print("  Mart views ready for Power BI:")
    print("    • mart_funnel_monthly")
    print("    • mart_cohort_retention")
    print("    • mart_feature_adoption")
    print("    • mart_revenue_bridge_quarterly")
    print("    • mart_feature_impact")
    print("    • mart_account_monthly_state")
    print("=" * 60)


if __name__ == "__main__":
    main()
