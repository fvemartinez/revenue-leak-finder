import math
import pytest

from src.leakage import FunnelInputs, compute


def base_rates():
    return {
        "message_per_click": 0.4,
        "reply_per_message": 0.7,
        "followup_per_reply": 0.35,
        "sale_per_followup": 0.25,
    }


def test_p_zero_stage_has_finite_marginal_and_matches_recompute():
    rates = base_rates().copy()
    rates["reply_per_message"] = 0.0
    inp = FunnelInputs(monthly_ad_spend=60000, cpc=8, rates=rates, avg_ticket=50000, gross_margin=0.45)
    res = compute(inp)
    # marginal for reply_per_message should be finite number
    m = res.marginal_gain["reply_per_message"]
    assert isinstance(m, float)
    assert math.isfinite(m)

    # recompute by creating bumped inputs and comparing revenue delta
    bumped = rates.copy()
    bumped["reply_per_message"] = min(1.0, 0.0 + 0.01)
    inp_bumped = FunnelInputs(monthly_ad_spend=60000, cpc=8, rates=bumped, avg_ticket=50000, gross_margin=0.45)
    res_bumped = compute(inp_bumped)
    assert abs(res_bumped.revenue - res.revenue - m) < 1e-6


def test_rate_one_has_zero_marginal():
    rates = base_rates().copy()
    rates["sale_per_followup"] = 1.0
    inp = FunnelInputs(monthly_ad_spend=10000, cpc=2, rates=rates, avg_ticket=1000, gross_margin=0.5)
    res = compute(inp)
    assert abs(res.marginal_gain["sale_per_followup"]) < 1e-12


def test_zero_ad_spend_all_marginals_zero():
    inp = FunnelInputs(monthly_ad_spend=0.0, cpc=5, rates=base_rates(), avg_ticket=1000, gross_margin=0.4)
    res = compute(inp)
    for v in res.marginal_gain.values():
        assert abs(v) < 1e-12


def test_invalid_cpc_raises():
    with pytest.raises(ValueError):
        FunnelInputs(monthly_ad_spend=1000, cpc=0, rates=base_rates(), avg_ticket=1000)


def test_avg_ticket_zero_produces_zero_revenue_and_zero_marginals():
    inp = FunnelInputs(monthly_ad_spend=1000, cpc=1, rates=base_rates(), avg_ticket=0.0)
    res = compute(inp)
    assert res.revenue == 0.0
    for v in res.marginal_gain.values():
        assert abs(v) < 1e-12


def test_determinism_of_ranking():
    inp = FunnelInputs(monthly_ad_spend=60000, cpc=8, rates=base_rates(), avg_ticket=50000)
    r1 = compute(inp)
    r2 = compute(inp)
    assert r1.priority_stage == r2.priority_stage
    assert r1.ranking == r2.ranking
