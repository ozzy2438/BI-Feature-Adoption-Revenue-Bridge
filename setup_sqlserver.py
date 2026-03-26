"""
Setup script: Creates database, loads CSV data, and creates mart views
on local SQL Server using pyodbc.

Usage: python setup_sqlserver.py
"""
import pyodbc
import pandas as pd
import os
import sys

# ═══════════════════════════════════════════════════════════
# CONNECTION CONFIG
# ═══════════════════════════════════════════════════════════
SERVER = os.environ.get('SQL_SERVER', 'localhost,1434')
USERNAME = os.environ.get('SQL_USERNAME', 'sa')
PASSWORD = os.environ.get('SQL_PASSWORD', '')
DB_NAME = os.environ.get('SQL_DATABASE', 'FeatureAdoptionBridge')
DRIVER = os.environ.get('SQL_DRIVER', '{ODBC Driver 18 for SQL Server}')

if not PASSWORD:
    print("⚠️  Set SQL_PASSWORD environment variable or edit this file.")
    print("   Example: export SQL_PASSWORD='YourPassword'")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
SQL_DIR = os.path.join(BASE_DIR, 'powerbi', 'sql')

def get_connection(database=None, autocommit=False):
    conn_str = (
        f"DRIVER={DRIVER};"
        f"SERVER={SERVER};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        f"TrustServerCertificate=yes;"
        f"Encrypt=yes;"
    )
    if database:
        conn_str += f"DATABASE={database};"
    return pyodbc.connect(conn_str, autocommit=autocommit)

def step1_create_database():
    print("=" * 60)
    print("STEP 1: Creating database...")
    print("=" * 60)
    conn = get_connection(autocommit=True)
    cursor = conn.cursor()
    cursor.execute(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{DB_NAME}') BEGIN CREATE DATABASE [{DB_NAME}] END")
    print(f"  ✅ Database '{DB_NAME}' ready")
    cursor.close()
    conn.close()

def step2_create_tables():
    print("\n" + "=" * 60)
    print("STEP 2: Creating base tables...")
    print("=" * 60)
    conn = get_connection(database=DB_NAME)
    cursor = conn.cursor()
    for view_name in ['mart_funnel_monthly', 'mart_cohort_retention', 'mart_feature_adoption',
                      'mart_revenue_bridge_quarterly', 'mart_feature_impact', 'mart_account_monthly_state']:
        cursor.execute(f"IF OBJECT_ID('{view_name}', 'V') IS NOT NULL DROP VIEW [{view_name}]")
    conn.commit()
    for table_name in ['sim_events', 'sim_revenue_monthly', 'sim_accounts']:
        cursor.execute(f"IF OBJECT_ID('{table_name}', 'U') IS NOT NULL DROP TABLE [{table_name}]")
    conn.commit()
    cursor.execute("CREATE TABLE sim_accounts (account_id NVARCHAR(20) NOT NULL PRIMARY KEY, signup_ts_utc DATETIME2, signup_month DATE, initial_plan_tier NVARCHAR(20), region NVARCHAR(10), acquisition_channel NVARCHAR(30))")
    print("  ✅ sim_accounts created")
    cursor.execute("CREATE TABLE sim_events (account_id NVARCHAR(20) NOT NULL, user_id NVARCHAR(40), event_name NVARCHAR(50) NOT NULL, event_ts_utc DATETIME2, event_month DATE, feature_name NVARCHAR(30))")
    cursor.execute("CREATE INDEX IX_sim_events_account ON sim_events (account_id)")
    cursor.execute("CREATE INDEX IX_sim_events_event ON sim_events (event_name)")
    print("  ✅ sim_events created")
    cursor.execute("CREATE TABLE sim_revenue_monthly (account_id NVARCHAR(20) NOT NULL, [month] DATE NOT NULL, mrr_start DECIMAL(10,2), mrr_end DECIMAL(10,2), plan_tier NVARCHAR(20), [status] NVARCHAR(20), feature_x_adopted_flag INT DEFAULT 0, feature_multi_currency_flag INT DEFAULT 0, feature_recurring_invoices_flag INT DEFAULT 0, features_adopted_count INT DEFAULT 0, is_new_customer INT DEFAULT 0, is_plan_upgrade INT DEFAULT 0, is_churn INT DEFAULT 0, is_contraction INT DEFAULT 0, feature_adoption_lift_eligible INT DEFAULT 0, mrr_delta DECIMAL(10,2), bridge_component NVARCHAR(30), CONSTRAINT PK_sim_revenue PRIMARY KEY (account_id, [month]))")
    print("  ✅ sim_revenue_monthly created")
    conn.commit()
    cursor.close()
    conn.close()

def step3_load_csvs():
    print("\n" + "=" * 60)
    print("STEP 3: Loading CSV data...")
    print("=" * 60)
    conn = get_connection(database=DB_NAME)
    cursor = conn.cursor()
    # sim_accounts
    csv_path = os.path.join(RAW_DIR, 'sim_accounts.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"  📄 sim_accounts.csv: {len(df)} rows")
        for _, row in df.iterrows():
            cursor.execute("INSERT INTO sim_accounts (account_id, signup_ts_utc, signup_month, initial_plan_tier, region, acquisition_channel) VALUES (?, ?, ?, ?, ?, ?)",
                str(row.get('account_id', '')),
                pd.to_datetime(row.get('signup_ts_utc'), errors='coerce'),
                pd.to_datetime(row.get('signup_month'), errors='coerce'),
                str(row.get('initial_plan_tier', '')) if pd.notna(row.get('initial_plan_tier')) else None,
                str(row.get('region', '')) if pd.notna(row.get('region')) else None,
                str(row.get('acquisition_channel', '')) if pd.notna(row.get('acquisition_channel')) else None)
        conn.commit()
        print(f"  ✅ sim_accounts loaded: {len(df)} rows")
    # sim_events
    csv_path = os.path.join(RAW_DIR, 'sim_events.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"  📄 sim_events.csv: {len(df)} rows")
        batch = []
        for _, row in df.iterrows():
            batch.append((str(row.get('account_id', '')), str(row.get('user_id', '')) if pd.notna(row.get('user_id')) else None, str(row.get('event_name', '')), pd.to_datetime(row.get('event_ts_utc'), errors='coerce'), pd.to_datetime(row.get('event_month'), errors='coerce'), str(row.get('feature_name', '')) if pd.notna(row.get('feature_name')) else None))
            if len(batch) >= 1000:
                cursor.executemany("INSERT INTO sim_events (account_id, user_id, event_name, event_ts_utc, event_month, feature_name) VALUES (?, ?, ?, ?, ?, ?)", batch)
                conn.commit()
                batch = []
        if batch:
            cursor.executemany("INSERT INTO sim_events (account_id, user_id, event_name, event_ts_utc, event_month, feature_name) VALUES (?, ?, ?, ?, ?, ?)", batch)
            conn.commit()
        print(f"  ✅ sim_events loaded: {len(df)} rows")
    # sim_revenue_monthly
    csv_path = os.path.join(RAW_DIR, 'sim_revenue_monthly.csv')
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"  📄 sim_revenue_monthly.csv: {len(df)} rows")
        batch = []
        for _, row in df.iterrows():
            batch.append((str(row.get('account_id', '')), pd.to_datetime(row.get('month'), errors='coerce'), float(row.get('mrr_start', 0) or 0), float(row.get('mrr_end', 0) or 0), str(row.get('plan_tier', '')) if pd.notna(row.get('plan_tier')) else None, str(row.get('status', '')) if pd.notna(row.get('status')) else None, int(row.get('feature_x_adopted_flag', 0) or 0), int(row.get('feature_multi_currency_flag', 0) or 0), int(row.get('feature_recurring_invoices_flag', 0) or 0), int(row.get('features_adopted_count', 0) or 0), int(row.get('is_new_customer', 0) or 0), int(row.get('is_plan_upgrade', 0) or 0), int(row.get('is_churn', 0) or 0), int(row.get('is_contraction', 0) or 0), int(row.get('feature_adoption_lift_eligible', 0) or 0), float(row.get('mrr_delta', 0) or 0), str(row.get('bridge_component', '')) if pd.notna(row.get('bridge_component')) else None))
            if len(batch) >= 500:
                cursor.executemany("INSERT INTO sim_revenue_monthly (account_id, [month], mrr_start, mrr_end, plan_tier, [status], feature_x_adopted_flag, feature_multi_currency_flag, feature_recurring_invoices_flag, features_adopted_count, is_new_customer, is_plan_upgrade, is_churn, is_contraction, feature_adoption_lift_eligible, mrr_delta, bridge_component) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", batch)
                conn.commit()
                batch = []
        if batch:
            cursor.executemany("INSERT INTO sim_revenue_monthly (account_id, [month], mrr_start, mrr_end, plan_tier, [status], feature_x_adopted_flag, feature_multi_currency_flag, feature_recurring_invoices_flag, features_adopted_count, is_new_customer, is_plan_upgrade, is_churn, is_contraction, feature_adoption_lift_eligible, mrr_delta, bridge_component) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", batch)
            conn.commit()
        print(f"  ✅ sim_revenue_monthly loaded: {len(df)} rows")
    cursor.close()
    conn.close()

def step4_create_views():
    print("\n" + "=" * 60)
    print("STEP 4: Creating mart views...")
    print("=" * 60)
    conn = get_connection(database=DB_NAME)
    cursor = conn.cursor()
    view_files = ['06_mart_account_monthly_state.sql', '01_mart_funnel_monthly.sql', '02_mart_cohort_retention.sql', '03_mart_feature_adoption.sql', '04_mart_revenue_bridge_quarterly.sql', '05_mart_feature_impact.sql']
    for sql_file in view_files:
        filepath = os.path.join(SQL_DIR, sql_file)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                sql = f.read()
            batches = sql.split('\nGO')
            for batch in batches:
                batch = batch.strip()
                if batch and 'CREATE OR ALTER VIEW' in batch:
                    try:
                        cursor.execute(batch)
                        conn.commit()
                        print(f"  ✅ {sql_file.replace('.sql', '')} created")
                    except Exception as e:
                        print(f"  ❌ Error in {sql_file}: {e}")
    cursor.close()
    conn.close()

def step5_verify():
    print("\n" + "=" * 60)
    print("STEP 5: Verifying...")
    print("=" * 60)
    conn = get_connection(database=DB_NAME)
    cursor = conn.cursor()
    checks = [('sim_accounts', 'TABLE'), ('sim_events', 'TABLE'), ('sim_revenue_monthly', 'TABLE'), ('mart_account_monthly_state', 'VIEW'), ('mart_funnel_monthly', 'VIEW'), ('mart_cohort_retention', 'VIEW'), ('mart_feature_adoption', 'VIEW'), ('mart_revenue_bridge_quarterly', 'VIEW'), ('mart_feature_impact', 'VIEW')]
    for name, obj_type in checks:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM [{name}]")
            count = cursor.fetchone()[0]
            print(f"  ✅ {obj_type}: {name} → {count:,} rows")
        except Exception as e:
            print(f"  ❌ {obj_type}: {name} → ERROR: {e}")
    cursor.close()
    conn.close()
    print("\n" + "=" * 60)
    print("🎉 DONE! Database is ready for Power BI connection.")
    print(f"   Server: {SERVER}")
    print(f"   Database: {DB_NAME}")
    print("=" * 60)

if __name__ == '__main__':
    try:
        step1_create_database()
        step2_create_tables()
        step3_load_csvs()
        step4_create_views()
        step5_verify()
    except pyodbc.Error as e:
        print(f"\n❌ SQL Server connection error: {e}")
        print("\nTroubleshooting:")
        print("  1. Is SQL Server running? Check: brew services list")
        print("  2. Is ODBC Driver 18 installed? Run: odbcinst -q -d")
        print("  3. Try port: localhost,1433 instead of 1434")
        print("  4. Check firewall allows TCP on port 1434")
        sys.exit(1)
    except ImportError as e:
        print(f"\n❌ Missing package: {e}")
        print("  Run: pip install pyodbc pandas")
        sys.exit(1)
