"""
Synthetic dataset generator. NO real clients, NO PII, NO PHI.

Produces fictional WhatsApp-funnel monthly snapshots for fictional storefronts,
purely to demonstrate the model's mechanics. Seed is fixed for reproducibility.

Every row is invented. Any resemblance to a real business is coincidental.
"""
from __future__ import annotations
import csv
import random
from pathlib import Path

SEED = 4744  # fixed for reproducibility
random.seed(SEED)

# Fictional vertical archetypes with plausible (invented) rate envelopes.
ARCHETYPES = [
    # name, spend range, cpc range, (p1,p2,p3,p4) center ranges, ticket range
    ("luxury_furniture", (40000, 90000), (6, 12), (0.30, 0.50), (0.60, 0.80),
     (0.25, 0.45), (0.18, 0.32), (35000, 75000)),
    ("real_estate_lead", (80000, 160000), (10, 22), (0.20, 0.38), (0.55, 0.75),
     (0.20, 0.40), (0.05, 0.15), (150000, 400000)),
    ("premium_decor", (20000, 50000), (4, 9), (0.35, 0.55), (0.65, 0.85),
     (0.30, 0.50), (0.20, 0.38), (8000, 25000)),
]

FICTIONAL_NAMES = [
    "Tienda Aurora", "Casa Lumen", "Estudio Roble", "Marca Ficticia A",
    "Comercio Demo B", "Showroom Sintetico", "Negocio Ejemplo C", "Brand Placeholder D",
    "Vertiente Ficticia", "Demo Storefront E", "Marca Prueba F", "Cliente Sintetico G",
]


def _r(lo, hi):
    return round(random.uniform(lo, hi), 4)


def generate(n_rows: int = 12) -> list[dict]:
    rows = []
    for i in range(n_rows):
        arch = ARCHETYPES[i % len(ARCHETYPES)]
        (name, spend_r, cpc_r, p1_r, p2_r, p3_r, p4_r, tk_r) = arch
        rows.append({
            "storefront": FICTIONAL_NAMES[i % len(FICTIONAL_NAMES)],
            "vertical": name,
            "monthly_ad_spend": round(_r(*spend_r), 0),
            "cpc": round(_r(*cpc_r), 2),
            "rate_message_per_click": _r(*p1_r),
            "rate_reply_per_message": _r(*p2_r),
            "rate_followup_per_reply": _r(*p3_r),
            "rate_sale_per_followup": _r(*p4_r),
            "avg_ticket": round(_r(*tk_r), 0),
            "gross_margin": _r(0.35, 0.55),
        })
    return rows


def write_csv(path: str, n_rows: int = 12) -> None:
    rows = generate(n_rows)
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} synthetic rows -> {path}")


if __name__ == "__main__":
    write_csv("data/synthetic_funnels.csv", 12)
