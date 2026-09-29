import pytest
from app.engine.alert_engine import LookAheadAlertEngine

def test_alert_tiers():
    engine = LookAheadAlertEngine()
    assert engine.get_tier(10.0) == "L3"
    assert engine.get_tier(30.0) == "L2"
    assert engine.get_tier(75.0) == "L1"
    assert engine.get_tier(150.0) is None

def test_heuristic_risk_score():
    engine = LookAheadAlertEngine()
    score_close = engine.calculate_heuristic_risk_score(distance_m=5.0, severity="L3")
    score_far = engine.calculate_heuristic_risk_score(distance_m=90.0, severity="L1")
    assert score_close > score_far
    assert 0.0 <= score_close <= 100.0
