from __future__ import annotations

import csv
import datetime as dt
import json
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


FUNNEL_STEPS: Sequence[str] = (
    "signup",
    "first_invoice_created",
    "first_payment_received",
    "app_integration_connected",
    "plan_upgrade",
)

FEATURES: Sequence[str] = ("bank_feed_sync", "multi_currency", "recurring_invoices")

PLAN_MRR = {
    "free": 0.0,
    "starter": 49.0,
    "growth": 99.0,
}

CHANNELS = ("organic", "paid_search", "partner", "direct")
REGIONS = ("NA", "EU", "APAC", "LATAM")


@dataclass(frozen=True)
class Account:
    account_id: str
    signup_ts_utc: dt.datetime
    signup_month: dt.date
    initial_plan_tier: str
    region: str
    acquisition_channel: str


def month_start(value: dt.date | dt.datetime) -> dt.date:
    if isinstance(value, dt.datetime):
        value = value.date()
    return dt.date(value.year, value.month, 1)


def add_months(base: dt.date, offset: int) -> dt.date:
    year = base.year + ((base.month - 1 + offset) // 12)
    month = ((base.month - 1 + offset) % 12) + 1
    return dt.date(year, month, 1)


def daterange_months(start: dt.date, months: int) -> List[dt.date]:
    return [add_months(start, i) for i in range(months)]


def classify_bridge_component(
    *,
    is_new_customer: bool,
    is_plan_upgrade: bool,
    feature_adoption_lift_eligible: bool,
    mrr_delta: float,
    is_churn: bool = False,
    is_contraction: bool = False,
) -> str:
    if mrr_delta == 0:
        return "Other/Residual"
    if mrr_delta < 0:
        if is_churn:
            return "Churn"
        if is_contraction:
            return "Contraction"
        return "Other/Residual"
    if is_new_customer:
        return "New Customers"
    if is_plan_upgrade:
        return "Plan Upgrade"
    if feature_adoption_lift_eligible:
        return "Feature Adoption Lift"
    return "Other/Residual"


def simulate_accounts(
    *,
    n_accounts: int,
    start_month: dt.date,
    months: int,
    seed: int,
) -> List[Account]:
    rng = random.Random(seed)
    accounts: List[Account] = []

    for idx in range(1, n_accounts + 1):
        signup_month = add_months(start_month, rng.randrange(max(months // 2, 1)))
        signup_day = rng.randint(1, 25)
        signup_ts = dt.datetime(
            signup_month.year,
            signup_month.month,
            signup_day,
            rng.randint(8, 20),
            rng.randint(0, 59),
            0,
            tzinfo=dt.timezone.utc,
        )
        accounts.append(
            Account(
                account_id=f"acct_{idx:06d}",
                signup_ts_utc=signup_ts,
                signup_month=month_start(signup_ts),
                initial_plan_tier="free",
                region=rng.choice(REGIONS),
                acquisition_channel=rng.choice(CHANNELS),
            )
        )

    return accounts


def _event(
    *,
    account_id: str,
    event_name: str,
    event_ts_utc: dt.datetime,
    feature_name: str = "",
    source: str = "simulation",
) -> Dict[str, str]:
    return {
        "account_id": account_id,
        "user_id": f"{account_id}_owner",
        "event_name": event_name,
        "event_ts_utc": event_ts_utc.isoformat(),
        "event_month": month_start(event_ts_utc).isoformat(),
        "feature_name": feature_name,
        "metadata_json": json.dumps({"source": source}),
    }


def simulate_events(
    *,
    accounts: Sequence[Account],
    seed: int,
) -> List[Dict[str, str]]:
    rng = random.Random(seed + 7)
    events: List[Dict[str, str]] = []

    for account in accounts:
        signup_ts = account.signup_ts_utc
        events.append(
            _event(
                account_id=account.account_id,
                event_name="signup",
                event_ts_utc=signup_ts,
            )
        )

        invoice_ts = None
        if rng.random() < 0.78:
            invoice_ts = signup_ts + dt.timedelta(days=rng.randint(1, 10))
            events.append(
                _event(
                    account_id=account.account_id,
                    event_name="first_invoice_created",
                    event_ts_utc=invoice_ts,
                )
            )

        payment_ts = None
        if invoice_ts and rng.random() < 0.83:
            payment_ts = invoice_ts + dt.timedelta(days=rng.randint(0, 8))
            events.append(
                _event(
                    account_id=account.account_id,
                    event_name="first_payment_received",
                    event_ts_utc=payment_ts,
                )
            )

        integration_ts = None
        if payment_ts and rng.random() < 0.62:
            integration_ts = payment_ts + dt.timedelta(days=rng.randint(1, 20))
            events.append(
                _event(
                    account_id=account.account_id,
                    event_name="app_integration_connected",
                    event_ts_utc=integration_ts,
                )
            )

        if integration_ts:
            feature_probs = {"bank_feed_sync": 0.58, "multi_currency": 0.35, "recurring_invoices": 0.42}
            for feat, prob in feature_probs.items():
                if rng.random() < prob:
                    feature_ts = integration_ts + dt.timedelta(days=rng.randint(1, 30))
                    events.append(
                        _event(
                            account_id=account.account_id,
                            event_name="feature_activated",
                            event_ts_utc=feature_ts,
                            feature_name=feat,
                        )
                    )

        if integration_ts and rng.random() < 0.28:
            upgrade_ts = integration_ts + dt.timedelta(days=rng.randint(15, 90))
            events.append(
                _event(
                    account_id=account.account_id,
                    event_name="plan_upgrade",
                    event_ts_utc=upgrade_ts,
                )
            )

    return sorted(events, key=lambda r: (r["account_id"], r["event_ts_utc"], r["event_name"]))


def _parse_iso(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def build_monthly_revenue(
    *,
    accounts: Sequence[Account],
    events: Sequence[Dict[str, str]],
    start_month: dt.date,
    months: int,
    seed: int,
) -> List[Dict[str, str | int | float]]:
    rng = random.Random(seed + 17)
    months_list = daterange_months(start_month, months)

    events_by_account: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for event in events:
        events_by_account[event["account_id"]].append(event)

    rows: List[Dict[str, str | int | float]] = []

    for account in accounts:
        per_account_events = events_by_account[account.account_id]
        event_dates = {
            event_name: [
                _parse_iso(e["event_ts_utc"]) for e in per_account_events if e["event_name"] == event_name
            ]
            for event_name in [
                "first_payment_received",
                "plan_upgrade",
            ]
        }

        feature_dates: Dict[str, dt.datetime | None] = {}
        for feat in FEATURES:
            feat_events = [
                _parse_iso(e["event_ts_utc"])
                for e in per_account_events
                if e["event_name"] == "feature_activated" and e.get("feature_name") == feat
            ]
            feature_dates[feat] = min(feat_events) if feat_events else None

        first_payment = min(event_dates["first_payment_received"]) if event_dates["first_payment_received"] else None
        first_upgrade = min(event_dates["plan_upgrade"]) if event_dates["plan_upgrade"] else None
        primary_feature_adopted = feature_dates.get("bank_feed_sync")

        churn_month: dt.date | None = None
        if first_payment and rng.random() < 0.18:
            churn_after = rng.randint(4, 10)
            churn_month = add_months(month_start(first_payment), churn_after)

        previous_mrr = 0.0
        previous_plan_tier = "free"
        for month in months_list:
            month_dt = dt.datetime(month.year, month.month, 1, tzinfo=dt.timezone.utc)
            plan_tier = "free"
            status = "prospect"

            if first_payment and month_dt >= dt.datetime(
                first_payment.year,
                first_payment.month,
                1,
                tzinfo=dt.timezone.utc,
            ):
                plan_tier = "starter"
                status = "active"

            if first_upgrade and month_dt >= dt.datetime(
                first_upgrade.year,
                first_upgrade.month,
                1,
                tzinfo=dt.timezone.utc,
            ):
                plan_tier = "growth"
                status = "active"

            if churn_month and month >= churn_month:
                plan_tier = "free"
                status = "churned"

            mrr_base = PLAN_MRR[plan_tier]

            adopted_features: Dict[str, int] = {}
            for feat, feat_ts in feature_dates.items():
                adopted_features[feat] = int(bool(
                    feat_ts and month_dt >= dt.datetime(feat_ts.year, feat_ts.month, 1, tzinfo=dt.timezone.utc)
                ))

            feature_adopted_flag = adopted_features.get("bank_feed_sync", 0)

            within_lift_window = bool(
                primary_feature_adopted
                and month_dt
                >= dt.datetime(primary_feature_adopted.year, primary_feature_adopted.month, 1, tzinfo=dt.timezone.utc)
                and month_dt
                <= dt.datetime(primary_feature_adopted.year, primary_feature_adopted.month, 1, tzinfo=dt.timezone.utc)
                + dt.timedelta(days=60)
            )

            feature_lift = 0.0
            if (
                primary_feature_adopted
                and within_lift_window
                and (not first_upgrade or month_dt < dt.datetime(first_upgrade.year, first_upgrade.month, 1, tzinfo=dt.timezone.utc))
                and status == "active"
            ):
                feature_lift = 15.0

            mrr_end = 0.0 if status == "churned" else mrr_base + feature_lift
            mrr_delta = mrr_end - previous_mrr

            is_churn = int(bool(
                mrr_delta < 0
                and status == "churned"
                and previous_mrr > 0
            ))
            is_contraction = int(bool(
                mrr_delta < 0
                and not is_churn
                and previous_mrr > 0
            ))

            is_new_customer = int(
                bool(
                    first_payment
                    and month_start(first_payment)
                    == month
                    and mrr_delta > 0
                )
            )
            is_plan_upgrade = int(
                bool(
                    first_upgrade
                    and month_start(first_upgrade)
                    == month
                    and mrr_delta > 0
                )
            )
            feature_adoption_lift_eligible = int(bool(within_lift_window and mrr_delta > 0 and not is_plan_upgrade))

            bridge_component = classify_bridge_component(
                is_new_customer=bool(is_new_customer),
                is_plan_upgrade=bool(is_plan_upgrade),
                feature_adoption_lift_eligible=bool(feature_adoption_lift_eligible),
                mrr_delta=mrr_delta,
                is_churn=bool(is_churn),
                is_contraction=bool(is_contraction),
            )

            features_adopted_count = sum(adopted_features.values())

            rows.append(
                {
                    "account_id": account.account_id,
                    "month": month.isoformat(),
                    "mrr_start": round(previous_mrr, 2),
                    "mrr_end": round(mrr_end, 2),
                    "plan_tier": plan_tier,
                    "status": status,
                    "feature_x_adopted_flag": feature_adopted_flag,
                    "feature_multi_currency_flag": adopted_features.get("multi_currency", 0),
                    "feature_recurring_invoices_flag": adopted_features.get("recurring_invoices", 0),
                    "features_adopted_count": features_adopted_count,
                    "is_new_customer": is_new_customer,
                    "is_plan_upgrade": is_plan_upgrade,
                    "is_churn": is_churn,
                    "is_contraction": is_contraction,
                    "feature_adoption_lift_eligible": feature_adoption_lift_eligible,
                    "mrr_delta": round(mrr_delta, 2),
                    "bridge_component": bridge_component,
                }
            )
            previous_mrr = mrr_end
            previous_plan_tier = plan_tier

    return rows


def write_csv(path: Path, rows: Iterable[dict]) -> None:
    rows = list(rows)
    if not rows:
        raise ValueError(f"No rows to write for {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
