"""Command-line JSON interface for the revenue-leak-finder model.

Usage examples:

# Read from stdin (JSON object) and print result to stdout
cat input.json | python -m src.cli

# Read from a file
python -m src.cli --file input.json

Where input.json can be either:
- A direct FunnelInputs JSON:
  {
    "monthly_ad_spend": 60000,
    "cpc": 8,
    "rates": {"message_per_click":0.4, "reply_per_message":0.7, "followup_per_reply":0.35, "sale_per_followup":0.25},
    "avg_ticket": 50000,
    "gross_margin": 0.45
  }

- Or a CSV-like single row mapping (keys used in data/synthetic_funnels.csv):
  {
    "monthly_ad_spend": 60000,
    "cpc": 8,
    "rate_message_per_click":0.4,
    "rate_reply_per_message":0.7,
    "rate_followup_per_reply":0.35,
    "rate_sale_per_followup":0.25,
    "avg_ticket":50000,
    "gross_margin":0.45
  }

Outputs a single JSON object to stdout with stable keys. On error it prints
only a short message to stderr and exits with code 2.
"""
from __future__ import annotations
import sys
import json
import argparse
from typing import Any, Dict

from .leakage import FunnelInputs, compute
from .adapter import csv_row_to_funnelinputs


EXIT_OK = 0
EXIT_INPUT_ERROR = 2


def _parse_input(obj: Dict[str, Any]) -> FunnelInputs:
    # If `rates` present and looks correct, use it directly
    if "rates" in obj:
        rates = obj["rates"]
        # Basic validation will happen in FunnelInputs
        return FunnelInputs(
            monthly_ad_spend=float(obj["monthly_ad_spend"]),
            cpc=float(obj["cpc"]),
            rates={k: float(v) for k, v in rates.items()},
            avg_ticket=float(obj["avg_ticket"]),
            gross_margin=float(obj.get("gross_margin", 0.0)),
        )
    # Otherwise treat as CSV-like row
    return csv_row_to_funnelinputs(obj)


def _result_to_json(res) -> Dict[str, Any]:
    return {
        "clicks": res.clicks,
        "stage_volumes": res.stage_volumes,
        "sales": res.sales,
        "revenue": res.revenue,
        "gross_profit": res.gross_profit,
        "cac": res.cac,
        "roas": res.roas,
        "marginal_gain": res.marginal_gain,
        "ranking": res.ranking,
        "priority_stage": res.priority_stage,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="rlf-cli")
    parser.add_argument("--file", "-f", help="JSON input file (defaults to stdin)")
    args = parser.parse_args(argv)

    try:
        if args.file:
            with open(args.file, "r", encoding="utf-8") as fh:
                obj = json.load(fh)
        else:
            obj = json.load(sys.stdin)
    except Exception as e:
        print(f"invalid JSON input: {e}", file=sys.stderr)
        return EXIT_INPUT_ERROR

    try:
        inp = _parse_input(obj)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return EXIT_INPUT_ERROR

    try:
        res = compute(inp)
    except Exception as e:
        print(f"model error: {e}", file=sys.stderr)
        return EXIT_INPUT_ERROR

    out = _result_to_json(res)
    # Stable JSON: sort keys and ensure floats are regular Python floats
    json.dump(out, sys.stdout, ensure_ascii=False, sort_keys=True, indent=2)
    sys.stdout.write("\n")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
