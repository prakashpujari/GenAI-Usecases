from __future__ import annotations


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def compute_scores(
    *,
    ltv: float,
    dti: float,
    risk_centrality: float | None,
    shared_contacts: int,
    similarity_flags: int,
) -> tuple[float, float]:
    """Compute explainable composite and network risk scores on a 0-100 scale."""
    centrality_component = clamp((risk_centrality or 0.0) * 100.0, 0.0, 100.0)
    credit_component = clamp((ltv * 0.45) + (dti * 0.55), 0.0, 100.0)
    network_component = clamp((shared_contacts * 8.0) + (similarity_flags * 15.0) + (centrality_component * 0.4), 0.0, 100.0)

    risk_score = clamp((credit_component * 0.7) + (network_component * 0.3), 0.0, 100.0)
    network_risk_score = clamp(network_component, 0.0, 100.0)
    return risk_score, network_risk_score
