from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    gcp_project_id: str
    bq_location: str
    bq_raw_dataset: str
    bq_analytics_dataset: str
    synthetic_seed: int


def get_settings() -> Settings:
    project_id = os.getenv("GCP_PROJECT_ID", "").strip()
    if not project_id:
        raise ValueError("Missing GCP_PROJECT_ID in environment.")

    return Settings(
        gcp_project_id=project_id,
        bq_location=os.getenv("BQ_LOCATION", "US"),
        bq_raw_dataset=os.getenv("BQ_RAW_DATASET", "raw_bridge"),
        bq_analytics_dataset=os.getenv("BQ_ANALYTICS_DATASET", "analytics_bridge"),
        synthetic_seed=int(os.getenv("SYNTHETIC_SEED", "42")),
    )
