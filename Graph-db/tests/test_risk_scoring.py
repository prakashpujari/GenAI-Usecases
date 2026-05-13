from app.domain.risk import compute_scores


def test_compute_scores_balances_credit_and_network() -> None:
    risk_score, network_score = compute_scores(
        ltv=78.0,
        dti=40.0,
        risk_centrality=0.8,
        shared_contacts=2,
        similarity_flags=1,
    )
    assert 0 <= risk_score <= 100
    assert 0 <= network_score <= 100
    assert network_score > 0


def test_compute_scores_clamps_to_hundred() -> None:
    risk_score, network_score = compute_scores(
        ltv=200.0,
        dti=200.0,
        risk_centrality=5.0,
        shared_contacts=20,
        similarity_flags=10,
    )
    assert risk_score == 100
    assert network_score == 100
