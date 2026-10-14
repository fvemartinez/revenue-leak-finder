"""
Post-Click Leakage Calculator — core funnel decomposition model.

Single question: given the leads you already paid for, which funnel stage
destroys the most money?

This module is descriptive, not causal. It ranks stages by marginal economic
impact (revenue unlocked per point of improvement, given current volume),
NOT by lowest conversion rate. See LIMITS_OF_USE.md.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List


STAGE_LABELS = [
    "message_per_click",      # % of clicks that reach WhatsApp
    "reply_per_message",      # % of messages that get a real reply
    "followup_per_reply",     # % of replies that get real follow-up
    "sale_per_followup",      # % of followed-up leads that close
]

STAGE_HUMAN = {
    "message_per_click": "% message / click",
    "reply_per_message": "% reply / message",
    "followup_per_reply": "% follow-up / reply",
    "sale_per_followup": "% sale / follow-up",
}


@dataclass
class FunnelInputs:
    monthly_ad_spend: float          # currency
    cpc: float                       # cost per click
    rates: Dict[str, float]          # the four stage rates, 0..1
    avg_ticket: float                # revenue per sale
    gross_margin: float = 0.0        # optional, 0..1

    def __post_init__(self) -> None:
        if self.cpc <= 0:
            raise ValueError("cpc must be > 0")
        for k in STAGE_LABELS:
            r = self.rates.get(k)
            if r is None or not (0.0 <= r <= 1.0):
                raise ValueError(f"rate '{k}' must be in [0, 1], got {r}")
        if self.avg_ticket < 0:
            raise ValueError("avg_ticket must be >= 0")


@dataclass
class FunnelResult:
    clicks: float
    stage_volumes: Dict[str, float]
    sales: float
    revenue: float
    gross_profit: float
    cac: float
    roas: float
    marginal_gain: Dict[str, float] = field(default_factory=dict)
    ranking: List[str] = field(default_factory=list)
    priority_stage: str = ""


def _revenue_from_rates(inp: FunnelInputs, rates: Dict[str, float]) -> float:
    """Compute revenue given an explicit rates mapping without computing marginals.

    This helper avoids recursion and provides a numerically stable way to
    compute the effect of changing a single rate by simulation rather than
    relying on analytical division which is undefined for p=0.
    """
    clicks = inp.monthly_ad_spend / inp.cpc if inp.cpc > 0 else 0.0
    running = clicks
    for k in STAGE_LABELS:
        running = running * rates.get(k, 0.0)
    sales = running
    return sales * inp.avg_ticket


def compute(inp: FunnelInputs) -> FunnelResult:
    clicks = inp.monthly_ad_spend / inp.cpc

    vol: Dict[str, float] = {}
    running = clicks
    for k in STAGE_LABELS:
        running = running * inp.rates[k]
        vol[k] = running

    sales = vol[STAGE_LABELS[-1]]
    revenue = sales * inp.avg_ticket
    gross_profit = revenue * inp.gross_margin
    cac = (inp.monthly_ad_spend / sales) if sales > 0 else 0.0
    roas = (revenue / inp.monthly_ad_spend) if inp.monthly_ad_spend > 0 else 0.0

    # Marginal economic impact: explicit simulation of +1 percentage point
    # (absolute) on each stage, all else equal. We simulate because the
    # analytic derivative Revenue/p is undefined when p == 0 and may be
    # numerically unstable for very small p.
    marginal: Dict[str, float] = {}
    for k in STAGE_LABELS:
        p = inp.rates[k]
        bumped = dict(inp.rates)
        bumped[k] = min(1.0, p + 0.01)
        new_revenue = _revenue_from_rates(inp, bumped)
        marginal[k] = new_revenue - revenue

    # Deterministic ranking (stable across runs). In case of ties, Python's
    # sorted is stable and will preserve the STAGE_LABELS relative order.
    ranking = sorted(STAGE_LABELS, key=lambda k: marginal[k], reverse=True)
    priority = ranking[0]

    return FunnelResult(
        clicks=clicks,
        stage_volumes=vol,
        sales=sales,
        revenue=revenue,
        gross_profit=gross_profit,
        cac=cac,
        roas=roas,
        marginal_gain=marginal,
        ranking=ranking,
        priority_stage=priority,
    )


def scenario(inp: FunnelInputs, relative_uplift: float) -> Dict[str, float]:
    """
    Hypothesis scenario: concentrate a relative uplift on the priority stage.

    Returns the incremental revenue. This is a hypothesis to be validated with
    a real before/after test — never a guaranteed outcome. See LIMITS_OF_USE.md.
    """
    base = compute(inp)
    k = base.priority_stage
    new_rates = dict(inp.rates)
    new_rates[k] = min(1.0, inp.rates[k] * (1.0 + relative_uplift))
    bumped = FunnelInputs(
        monthly_ad_spend=inp.monthly_ad_spend,
        cpc=inp.cpc,
        rates=new_rates,
        avg_ticket=inp.avg_ticket,
        gross_margin=inp.gross_margin,
    )
    after = compute(bumped)
    incremental_revenue = after.revenue - base.revenue
    incremental_gross_profit = after.gross_profit - base.gross_profit
    return {
        "uplift": relative_uplift,
        "stage": k,
        "revenue_before": base.revenue,
        "revenue_after": after.revenue,
        "incremental_revenue": incremental_revenue,
        "incremental_gross_profit": incremental_gross_profit,
        "roas_before": base.roas,
        "roas_after": after.roas,
    }
