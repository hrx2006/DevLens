import pytest
from app.services.priority_engine import priority_engine, SEVERITY_WEIGHTS, CATEGORY_WEIGHT_MULTIPLIERS

def test_priority_engine_severity_mapping():
    """Verify severity levels map correctly to expected priority bounds."""
    for severity, base_weight in SEVERITY_WEIGHTS.items():
        priority = priority_engine.calculate_priority(severity)
        assert 0 <= priority <= 100
        assert priority == base_weight

def test_priority_engine_category_weight_modifiers():
    """Verify security issues receive higher priority and SEO receives slight dampening."""
    sec_crit = priority_engine.calculate_priority("Critical", "Security")
    seo_crit = priority_engine.calculate_priority("Critical", "SEO")
    
    assert sec_crit >= 95
    assert sec_crit <= 100
    assert seo_crit < sec_crit
    assert seo_crit == round(95 * 0.95)

def test_priority_engine_bounds_clamping():
    """Verify priority never drops below 0 or exceeds 100."""
    assert priority_engine.calculate_priority("Unknown", "Security") >= 0
    assert priority_engine.calculate_priority("Critical", "Security") <= 100
    assert priority_engine.calculate_priority("Info", "SEO") >= 0

def test_overall_health_calculation_all_passing():
    """All 5 categories score 100 -> overall health is 100.0."""
    score = priority_engine.calculate_overall_health(100.0, 100.0, 100.0, 100.0, 100.0)
    assert score == 100.0

def test_overall_health_calculation_all_failing():
    """All 5 categories score 0 -> overall health is 0.0."""
    score = priority_engine.calculate_overall_health(0.0, 0.0, 0.0, 0.0, 0.0)
    assert score == 0.0

def test_overall_health_calculation_mixed():
    """Verify equal weighting of active categories."""
    # (80 + 70 + 90 + 60 + 100) / 5 = 400 / 5 = 80.0
    score = priority_engine.calculate_overall_health(80.0, 70.0, 90.0, 60.0, 100.0)
    assert score == 80.0

def test_overall_health_calculation_empty():
    """Missing or empty inputs return 0.0 safely without division by zero."""
    score = priority_engine.calculate_overall_health(None, None, None, None, None)
    assert score == 0.0
