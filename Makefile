PYTHON ?= python3
VENV ?= .venv
ACTIVATE = . $(VENV)/bin/activate
DBT_DIR = dbt_project

ifneq (,$(wildcard .env))
include .env
export
endif

.PHONY: setup generate-raw fetch-ga4 fetch-uci fetch-sec load-raw dbt-deps dbt-run dbt-test retention-matrix quality-checks revenue-bridge-chart powerbi-export all clean

setup:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install -r requirements.txt

generate-raw:
	$(ACTIVATE) && $(PYTHON) python/generate_synthetic_raw.py --output-dir data/raw

fetch-ga4:
	$(ACTIVATE) && $(PYTHON) python/fetch_ga4_public.py --output data/raw/ga4_events_real.csv

fetch-uci:
	$(ACTIVATE) && $(PYTHON) python/fetch_uci_online_retail.py --output data/raw/uci_transactions_real.csv

fetch-sec:
	$(ACTIVATE) && $(PYTHON) python/fetch_sec_financials.py --output data/raw/sec_financials_real.csv

load-raw:
	$(ACTIVATE) && $(PYTHON) python/load_to_bigquery.py --input-dir data/raw

dbt-deps:
	$(ACTIVATE) && cd $(DBT_DIR) && dbt deps

dbt-run: dbt-deps
	$(ACTIVATE) && cd $(DBT_DIR) && dbt run --target $${DBT_TARGET:-dev}

dbt-test:
	$(ACTIVATE) && cd $(DBT_DIR) && dbt test --target $${DBT_TARGET:-dev}

retention-matrix:
	$(ACTIVATE) && $(PYTHON) python/build_retention_matrix.py --output data/outputs/retention_matrix.csv

quality-checks:
	$(ACTIVATE) && $(PYTHON) python/quality_checks.py --output data/outputs/quality_report.json

revenue-bridge-chart:
	$(ACTIVATE) && $(PYTHON) python/plot_revenue_bridge.py --output-dir data/outputs

powerbi-export:
	$(ACTIVATE) && $(PYTHON) python/export_powerbi_extracts.py --output-dir data/outputs/powerbi_extracts

all: generate-raw load-raw dbt-run dbt-test retention-matrix quality-checks

clean:
	rm -rf data/outputs/*
