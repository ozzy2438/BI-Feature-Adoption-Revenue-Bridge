# Power BI + Azure SQL — Complete Setup Guide

## 📋 Execution Order

```
00_create_base_tables.sql    →  Creates 3 raw tables (sim_accounts, sim_events, sim_revenue_monthly)
   ↓  (Load CSV data)
01_mart_funnel_monthly.sql   →  VIEW for Page 1: Funnel Leakage
02_mart_cohort_retention.sql →  VIEW for Page 2: Cohort Retention
03_mart_feature_adoption.sql →  VIEW for Page 3: Feature Adoption
04_mart_revenue_bridge.sql   →  VIEW for Page 4: Revenue Bridge Waterfall
05_mart_feature_impact.sql   →  VIEW for Page 5: Feature Impact Matrix
06_mart_account_monthly.sql  →  VIEW (Master fact table used by all pages)
```

---

## STEP 1: Create Azure SQL Database

### Option A: Azure Portal
1. Go to [portal.azure.com](https://portal.azure.com)
2. Click **Create a resource** → **SQL Database**
3. Settings:
   - **Resource Group**: Create new or use existing
   - **Database name**: `feature_adoption_bridge`
   - **Server**: Click 'Create new'
   - **Compute**: **Basic** or **S0** tier ($5-15/month)
4. Click **Review + Create** → **Create**

### Option B: Local SQL Server
If using a local SQL Server instance, use `setup_sqlserver.py`:
```bash
export SQL_SERVER='localhost,1434'
export SQL_USERNAME='YourUser'
export SQL_PASSWORD='YourPassword'
python setup_sqlserver.py
```

---

## STEP 2: Connect Power BI to SQL Server

1. Open **Power BI Desktop**
2. Click **Home → Get Data → SQL Server** (or Azure SQL Database)
3. Enter:
   - **Server**: `localhost,1434` or `your-server.database.windows.net`
   - **Database**: `FeatureAdoptionBridge`
   - **Data Connectivity mode**: **Import** (recommended)
4. Click **OK** → Enter SQL credentials
5. In the Navigator, select these 6 views:
   - ☑️ `mart_funnel_monthly`
   - ☑️ `mart_cohort_retention`
   - ☑️ `mart_feature_adoption`
   - ☑️ `mart_revenue_bridge_quarterly`
   - ☑️ `mart_feature_impact`
   - ☑️ `mart_account_monthly_state`
6. Click **Load**

---

## STEP 3: Create DAX Measures

### Funnel Measures
```dax
Overall Conversion = 
DIVIDE(
    CALCULATE(SUM(mart_funnel_monthly[users_at_step]),
              mart_funnel_monthly[step_name] = "First Payment Received"),
    CALCULATE(SUM(mart_funnel_monthly[users_at_step]),
              mart_funnel_monthly[step_name] = "Signup")
)
```

### Retention Measures
```dax
M6 Retention Avg = 
AVERAGEX(
    FILTER(mart_cohort_retention, mart_cohort_retention[age_month] = 6),
    mart_cohort_retention[retention_rate]
)
```

### Revenue Bridge Measures
```dax
Net MRR Delta = SUM(mart_revenue_bridge_quarterly[amount])

Feature Lift Share = 
DIVIDE(
    CALCULATE(SUM(mart_revenue_bridge_quarterly[amount]),
              mart_revenue_bridge_quarterly[bridge_component] = "Feature Adoption Lift",
              mart_revenue_bridge_quarterly[amount] > 0),
    CALCULATE(SUM(mart_revenue_bridge_quarterly[amount]),
              mart_revenue_bridge_quarterly[amount] > 0)
)
```

### Feature Impact Measures
```dax
MRR Uplift = 
CALCULATE(AVERAGE(mart_feature_impact[avg_mrr]),
          mart_feature_impact[segment] = "adopted",
          mart_feature_impact[feature_name] = "bank_feed_sync")
-
CALCULATE(AVERAGE(mart_feature_impact[avg_mrr]),
          mart_feature_impact[segment] = "not_adopted",
          mart_feature_impact[feature_name] = "bank_feed_sync")
```

---

## STEP 4: Build 5 Dashboard Pages

### Page 1: Funnel Leakage
| Visual | Config |
|--------|--------|
| **Funnel chart** | Category: `step_name`, Values: `users_at_step` |
| **Table** | Cols: step_name, users_at_step, conversion_from_prev, dropoff_from_prev |
| **KPI cards** | Signups, Paid, Overall Conversion % |
| **Slicer** | `month` (single select) |

### Page 2: Cohort Retention
| Visual | Config |
|--------|--------|
| **Matrix** (heatmap) | Rows: cohort_month, Cols: age_month, Values: retention_rate |
| **Conditional formatting** | Background color scale: green (high) → red (low) |
| **Line chart** | X: age_month, Y: retention_rate, Legend: cohort_month |

### Page 3: Feature Adoption
| Visual | Config |
|--------|--------|
| **Line chart** | X: month, Y: adoption_rate, Legend: feature_name |
| **Clustered bar** | X: feature_name, Y: adopted_accounts |

### Page 4: Revenue Bridge
| Visual | Config |
|--------|--------|
| **Waterfall chart** | Category: bridge_component (sorted by bridge_sort_order), Y: amount |
| **Slicer** | quarter (single select) |

### Page 5: Feature Impact
| Visual | Config |
|--------|--------|
| **Clustered bar** | X: feature_name, Y: churn_rate, Legend: segment |
| **Clustered bar** | X: feature_name, Y: avg_mrr, Legend: segment |

---

## 📁 Files in This Repo

```
powerbi/
├── sql/
│   ├── 00_create_base_tables.sql
│   ├── 01_mart_funnel_monthly.sql
│   ├── 02_mart_cohort_retention.sql
│   ├── 03_mart_feature_adoption.sql
│   ├── 04_mart_revenue_bridge_quarterly.sql
│   ├── 05_mart_feature_impact.sql
│   └── 06_mart_account_monthly_state.sql
└── POWERBI_SETUP_GUIDE.md

setup_sqlserver.py          ← Automated setup script
dashboard/                  ← Interactive web dashboard
data/outputs/               ← Generated mart CSVs
```
