# CLI usage examples for PowerShell

# Example: direct rates object
$in = @"
{
  "monthly_ad_spend": 60000,
  "cpc": 8,
  "rates": {"message_per_click":0.4, "reply_per_message":0.7, "followup_per_reply":0.35, "sale_per_followup":0.25},
  "avg_ticket": 50000,
  "gross_margin": 0.45
}
"@
$in | Out-File -FilePath input.json -Encoding utf8
python -m src.cli --file input.json

# Example: CSV-like row mapping
$in = @"
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
"@
$in | Out-File -FilePath input2.json -Encoding utf8
python -m src.cli --file input2.json
