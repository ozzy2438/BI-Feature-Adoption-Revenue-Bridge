import datetime as dt

from bridge_logic import FEATURES, FUNNEL_STEPS, add_months, build_monthly_revenue, simulate_accounts, simulate_events


def test_simulation_generates_signup_for_every_account() -> None:
    accounts = simulate_accounts(n_accounts=100, start_month=dt.date(2024, 1, 1), months=12, seed=1)
    events = simulate_events(accounts=accounts, seed=1)

    signup_accounts = {e["account_id"] for e in events if e["event_name"] == "signup"}
    assert len(signup_accounts) == len(accounts)


def test_funnel_event_order_is_consistent() -> None:
    accounts = simulate_accounts(n_accounts=150, start_month=dt.date(2024, 1, 1), months=12, seed=2)
    events = simulate_events(accounts=accounts, seed=2)

    steps = list(FUNNEL_STEPS)
    step_rank = {step: i for i, step in enumerate(steps)}

    per_account = {}
    for event in events:
        if event["event_name"] in step_rank:
            per_account.setdefault(event["account_id"], []).append((step_rank[event["event_name"]], event["event_ts_utc"]))

    for row in per_account.values():
        ranks = [r for r, _ in row]
        assert ranks == sorted(ranks)


def test_monthly_revenue_shape() -> None:
    start = dt.date(2024, 1, 1)
    months = 6
    accounts = simulate_accounts(n_accounts=10, start_month=start, months=months, seed=3)
    events = simulate_events(accounts=accounts, seed=3)
    revenue = build_monthly_revenue(accounts=accounts, events=events, start_month=start, months=months, seed=3)

    assert len(revenue) == len(accounts) * months
    assert all("bridge_component" in row for row in revenue)
    assert all(dt.date.fromisoformat(row["month"]) < add_months(start, months) for row in revenue)


def test_multiple_features_generated() -> None:
    accounts = simulate_accounts(n_accounts=500, start_month=dt.date(2024, 1, 1), months=12, seed=10)
    events = simulate_events(accounts=accounts, seed=10)

    feature_events = [e for e in events if e["event_name"] == "feature_activated"]
    feature_names_seen = {e["feature_name"] for e in feature_events}

    for feat in FEATURES:
        assert feat in feature_names_seen, f"Feature {feat} was never generated"


def test_churn_and_contraction_buckets_present() -> None:
    start = dt.date(2024, 1, 1)
    months = 18
    accounts = simulate_accounts(n_accounts=500, start_month=start, months=months, seed=20)
    events = simulate_events(accounts=accounts, seed=20)
    revenue = build_monthly_revenue(accounts=accounts, events=events, start_month=start, months=months, seed=20)

    components = {r["bridge_component"] for r in revenue}
    assert "Churn" in components, "Expected Churn bucket in bridge components"


def test_revenue_has_multi_feature_flags() -> None:
    start = dt.date(2024, 1, 1)
    months = 6
    accounts = simulate_accounts(n_accounts=10, start_month=start, months=months, seed=5)
    events = simulate_events(accounts=accounts, seed=5)
    revenue = build_monthly_revenue(accounts=accounts, events=events, start_month=start, months=months, seed=5)

    assert all("feature_multi_currency_flag" in row for row in revenue)
    assert all("feature_recurring_invoices_flag" in row for row in revenue)
    assert all("features_adopted_count" in row for row in revenue)
    assert all("is_churn" in row for row in revenue)
    assert all("is_contraction" in row for row in revenue)
