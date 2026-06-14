# revenue-leak-finder

> **Most funnels don't die at the click. They bleed out after it.**
> This finds the wound.

You paid for the click. The lead arrived, wrote in, and then — somewhere between the first message and the sale — the value quietly drained away. Not all at once. One stage at a time, invisibly, while the dashboard still showed traffic.

`revenue-leak-finder` is a small, auditable diagnostic that decomposes the post-click funnel into its five real stages and tells you the one truth most reports hide: **which stage is destroying the most money right now.**

```
Click  →  Message  →  Reply  →  Follow-up  →  Sale
```

![Sensitivity diagram](assets/sensitivity_diagram.png)

---

## The mistake everyone makes

The instinct is to attack the stage with the worst conversion rate. That instinct is wrong, and it is expensive.

A terrible rate on a stage almost no one reaches moves less money than a mediocre rate on a stage with volume. The leak that matters is not the *weakest* stage — it's the one where a small improvement unlocks the most revenue, given who actually arrives there.

So this tool ranks by the economic derivative, not by the rate:

```
∂Revenue / ∂p_i  =  Revenue / p_i
```

A one-point improvement on stage *i* unlocks `Revenue / p_i × 0.01` in incremental revenue. The priority is wherever that number is largest. That is the difference between fixing the symptom and fixing the leak.

---

## No causality without real data

This is the part most tools bury in a footnote. It belongs in the open.

This model is **descriptive, not causal.** It shows you where money concentrates in a funnel. It does not promise that improving a stage *causes* a given lift — that claim can only be earned by a measured before/after on real traffic.

- The ranking answers: *"if this stage's rate rose by a point, how much revenue would that free up, holding everything else still?"*
- It does **not** answer: *"will your intervention actually move that rate?"* — only measurement answers that.

Every `+10% / +20% / +30%` scenario here is a **hypothesis to test**, never a forecast. Anyone who hands you a model like this and promises a guaranteed CAC reduction is selling you something. The honest sentence — the one worth more than the guarantee — is: *"with your current numbers, this stage has the highest economic leverage; we validate it by measuring."* See [`LIMITS_OF_USE.md`](LIMITS_OF_USE.md).

---

## What's inside

```
revenue-leak-finder/
├── README.md
├── LIMITS_OF_USE.md            # where this tool stops being valid
├── requirements.txt
├── src/
│   ├── leakage.py              # the model — pure, no I/O
│   └── generate_synthetic.py   # synthetic dataset, fixed seed
├── data/
│   └── synthetic_funnels.csv   # 12 fictional storefronts — synthetic only
├── notebooks/
│   └── post_click_leakage.ipynb
└── assets/
    └── sensitivity_diagram.png
```

## Run it

```bash
pip install -r requirements.txt
python src/generate_synthetic.py
jupyter notebook notebooks/post_click_leakage.ipynb
```

Or call the model directly:

```python
from src.leakage import FunnelInputs, compute, scenario

inp = FunnelInputs(
    monthly_ad_spend=60000, cpc=8,
    rates={"message_per_click":0.40, "reply_per_message":0.70,
           "followup_per_reply":0.35, "sale_per_followup":0.25},
    avg_ticket=50000, gross_margin=0.45,
)
res = compute(inp)
print(res.priority_stage, res.roas)
```

## On the data

Every number here is **synthetic**, generated with a fixed seed. No real clients, no PII, no PHI, no secrets — by design and by policy. The point of this repository is not the data. It's the judgment: a transparent method, and an honest account of where that method stops. See [`LIMITS_OF_USE.md`](LIMITS_OF_USE.md).

## License

MIT. See [`LICENSE`](LICENSE).
