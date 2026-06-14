# Limits of Use

This document defines the boundary within which this tool is valid and honest. Read it before using the model with anyone's money.

## 1. This is a descriptive model, not a causal one

The calculator decomposes a funnel and ranks stages by **marginal economic impact at current volume**. It tells you *where money concentrates*. It says nothing about *what will happen if you intervene*.

- A high marginal-impact ranking means: improving this stage would unlock the most revenue **if** you could improve it, holding all else equal.
- It does **not** mean: your specific intervention will improve it, or that the other stages will stay constant when you do.

Causal claims require an actual experiment or quasi-experiment on real traffic. This model is the **prioritization step before** that experiment, not a substitute for it.

## 2. Scenarios are hypotheses, never guarantees

The `+10% / +20% / +30%` scenarios assume:

- the uplift lands entirely on the priority stage,
- no other stage changes,
- the rate stays within `[0, 1]`.

Real funnels violate all three regularly (improving follow-up can change close rate; fixing response time can shift message volume). Treat every scenario number as a **hypothesis to be tested with a measured before/after**, typically over one to three weeks. Never present a scenario figure as a promised result.

## 3. Small-sample caution

With a few weeks of a single client's data, conversion rates are noisy. A measured "improvement" can be regression to the mean rather than signal. Before declaring victory, confirm the lift is distinguishable from noise (a Bayesian Beta-Binomial update or a simple proportion test is enough for early reads). This repository deliberately ships only the descriptive layer; the inferential layer belongs in a real engagement with real data.

## 4. Data boundary — what must never enter this repository

This is a public portfolio artifact. The following are prohibited, permanently:

- Real client names, identifiers, or any personally identifiable information (PII).
- Any protected health information (PHI).
- Real funnel numbers from any actual business.
- API keys, tokens, credentials, or secrets of any kind.
- Symlinks, submodules, or hidden dependencies pointing to any private repository.
- Internal governance vocabulary or canon from private systems.

All data here is synthetic and fictional. Any resemblance to a real business is coincidental.

## 5. Appropriate use

**Appropriate:** teaching the funnel-decomposition method; demonstrating prioritization logic; a discovery conversation where a prospect supplies their own numbers into a private copy of the model.

**Inappropriate:** presenting model output as a guaranteed outcome; using it to justify a fixed performance promise; treating a ranking as proof of causation.

## 6. Honesty clause

If a stage shows the highest marginal impact, the correct statement is:

> "With your current numbers, this stage appears to have the highest economic leverage. That is a hypothesis. We validate it by measuring before and after a real change."

Not:

> "If you fix this, I guarantee your CAC drops."

The first is defensible. The second is not.
