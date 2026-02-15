from bridge_logic import classify_bridge_component


def test_classify_new_customer_precedence() -> None:
    assert (
        classify_bridge_component(
            is_new_customer=True,
            is_plan_upgrade=True,
            feature_adoption_lift_eligible=True,
            mrr_delta=100,
        )
        == "New Customers"
    )


def test_classify_upgrade_over_feature_lift() -> None:
    assert (
        classify_bridge_component(
            is_new_customer=False,
            is_plan_upgrade=True,
            feature_adoption_lift_eligible=True,
            mrr_delta=30,
        )
        == "Plan Upgrade"
    )


def test_churn_classification() -> None:
    assert (
        classify_bridge_component(
            is_new_customer=False,
            is_plan_upgrade=False,
            feature_adoption_lift_eligible=False,
            mrr_delta=-49,
            is_churn=True,
            is_contraction=False,
        )
        == "Churn"
    )


def test_contraction_classification() -> None:
    assert (
        classify_bridge_component(
            is_new_customer=False,
            is_plan_upgrade=False,
            feature_adoption_lift_eligible=False,
            mrr_delta=-15,
            is_churn=False,
            is_contraction=True,
        )
        == "Contraction"
    )


def test_negative_delta_without_flags_is_residual() -> None:
    assert (
        classify_bridge_component(
            is_new_customer=False,
            is_plan_upgrade=False,
            feature_adoption_lift_eligible=False,
            mrr_delta=-10,
            is_churn=False,
            is_contraction=False,
        )
        == "Other/Residual"
    )


def test_zero_delta_is_residual() -> None:
    assert (
        classify_bridge_component(
            is_new_customer=True,
            is_plan_upgrade=True,
            feature_adoption_lift_eligible=True,
            mrr_delta=0,
        )
        == "Other/Residual"
    )


def test_feature_adoption_lift() -> None:
    assert (
        classify_bridge_component(
            is_new_customer=False,
            is_plan_upgrade=False,
            feature_adoption_lift_eligible=True,
            mrr_delta=15,
        )
        == "Feature Adoption Lift"
    )
