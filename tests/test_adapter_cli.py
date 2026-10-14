import json
import io

from src.adapter import csv_row_to_funnelinputs
from src.cli import _parse_input, main


def test_adapter_maps_csv_row():
    row = {
        "monthly_ad_spend": "60000",
        "cpc": "8",
        "rate_message_per_click": "0.4",
        "rate_reply_per_message": "0.7",
        "rate_followup_per_reply": "0.35",
        "rate_sale_per_followup": "0.25",
        "avg_ticket": "50000",
        "gross_margin": "0.45",
    }
    inp = csv_row_to_funnelinputs(row)
    assert inp.cpc == 8.0
    assert inp.rates["message_per_click"] == 0.4


def test_cli_parses_direct_rates_dict(monkeypatch, capsys, tmp_path):
    data = {
        "monthly_ad_spend": 60000,
        "cpc": 8,
        "rates": {"message_per_click":0.4, "reply_per_message":0.7, "followup_per_reply":0.35, "sale_per_followup":0.25},
        "avg_ticket": 50000,
        "gross_margin": 0.45
    }
    p = tmp_path / "in.json"
    p.write_text(json.dumps(data))
    # call main with file
    rc = main(["--file", str(p)])
    assert rc == 0

