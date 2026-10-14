"""Adapter helpers to convert CSV rows / dicts into FunnelInputs.

The adapter enforces explicit mapping and validation. It intentionally avoids
silent conversions: invalid or missing fields raise ValueError with a clear
message so calling code can surface or log the exact row failure.
"""
from __future__ import annotations
from typing import Dict, Any

from .leakage import FunnelInputs, STAGE_LABELS


CSV_TO_RATE_KEYS = {
    "rate_message_per_click": "message_per_click",
    "rate_reply_per_message": "reply_per_message",
    "rate_followup_per_reply": "followup_per_reply",
    "rate_sale_per_followup": "sale_per_followup",
}


def csv_row_to_funnelinputs(row: Dict[str, Any]) -> FunnelInputs:
    """Map a CSV/dict row with legacy keys into a validated FunnelInputs.

    Expected keys in `row` (either as numeric types or parsable strings):
      - monthly_ad_spend
      - cpc
      - rate_message_per_click
      - rate_reply_per_message
      - rate_followup_per_reply
      - rate_sale_per_followup
      - avg_ticket
      - gross_margin (optional, defaults to 0.0)

    The function will raise ValueError on missing fields, out-of-range values,
    or inability to parse numeric values.
    """
    missing = []
    for k in ["monthly_ad_spend", "cpc", "avg_ticket"] + list(CSV_TO_RATE_KEYS.keys()):
        if k not in row or row[k] is None:
            missing.append(k)
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")

    def _as_float(key: str) -> float:
        v = row.get(key)
        try:
            return float(v)
        except Exception:
            raise ValueError(f"field '{key}' must be a number, got: {v!r}")

    monthly_ad_spend = _as_float("monthly_ad_spend")
    cpc = _as_float("cpc")
    avg_ticket = _as_float("avg_ticket")
    gross_margin = float(row.get("gross_margin", 0.0)) if row.get("gross_margin") is not None else 0.0

    rates: Dict[str, float] = {}
    for csv_k, rate_k in CSV_TO_RATE_KEYS.items():
        r = _as_float(csv_k)
        if not (0.0 <= r <= 1.0):
            raise ValueError(f"rate '{csv_k}' must be in [0,1], got {r}")
        rates[rate_k] = r

    # Ensure all expected stage labels are present
    for label in STAGE_LABELS:
        if label not in rates:
            raise ValueError(f"missing mapped rate for '{label}'")

    return FunnelInputs(
        monthly_ad_spend=monthly_ad_spend,
        cpc=cpc,
        rates=rates,
        avg_ticket=avg_ticket,
        gross_margin=gross_margin,
    )
