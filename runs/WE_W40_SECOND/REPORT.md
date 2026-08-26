# WE_W40 — THE SECOND MODEL · REPORT

Spec `034e4ea` + amendments 1–5, each appended before its own arm was read.
**B1 PASS on every read**: the long object reproduced at exactly 14.72 pts/session.
Net $4.36/RT; stress $14.36/RT. No data ≥ 2026-08-01.

**Verdict: no second model adopted.** Four structurally different mechanisms; three fail
outright; the fourth (volatility-expansion) is the closest the campaign has come and is
recorded as a **parked candidate with its exact revival condition**, not as a model.

---

## 1. The four mechanisms (2023-07 → 2026-08, each with the session box)

| axis | pts/session | stress-net | Sharpe | corr vs long | **corr in the long object's worst-decile weeks** | bar overlap |
|---|---|---|---|---|---|---|
| A fade **event** k2.0 / k1.5 | −11.39 / −12.38 | negative | −0.22 / −0.25 | −0.14 / −0.12 | 0.35 / 0.30 | 88 % / 90 % |
| **B vol-expansion event** | **+5.90** | **+$390** | 0.138 | **0.07** | **−0.18** | **10.2 %** |
| C sweep-and-reclaim | −3.08 | negative | −0.082 | 0.02 | 0.26 | 27.7 % |
| D complement-set ridge | +2.14 gross | **−$55** | 0.048 | 0.06 | 0.29 | **2.7 %** |

- **A** was a legitimate reopening: W11/W18 falsified fade as a *state* rule, before W31
  established that this instrument pays *events*. Tested as an event it is far worse
  (`FALSIFIED`).
- **C**: the stop-run story does not survive frictions at this cadence (`FALSIFIED`).
- **D** is a substantive negative, not an empty one: structural orthogonality was achieved by
  construction (2.7 % overlap), and a ridge on 42 causal features over the 83 % of bars where
  Solar holds nothing is **negative after the stress line**. Those bars are poor, not merely
  unexploited (`FALSIFIED`).

## 2. B looked adoptable, then did not — the sequence, in order

**Amendment 1** (weight scan at constant total exposure — the measurement read 1 lacked, since
read 1 had silently handed B 34 % of the book) cleared **all five** preregistered conditions on
2023-07 → 2026-08: at w = 0.05 eff 0.229→0.241, CVaR-eff 0.289→0.310, Sharpe 0.331→0.340 **and**
the worst week −$7,418→−$6,935 — a four-way improvement matched previously only by the session
halt. Both nulls at the **100th percentile, p = 0.000**. Parameter surface not knife-edge
(81 % of 36 settings stress-positive; the preregistered 1.6/1.0/15 is a *below-median* setting).
Its parameter walk-forward failed (64 % churn, 46 % retention), so it would have been quoted at
fixed preregistered parameters.

**Amendment 2** — full-window and per-year re-measurement, made a precondition before writing
anything into the state documents — **withdrew that adoption**: B alone is negative in 2023 and
2024, the pair beats exposure-matched long-alone only in the years B itself works, and on the
full window the 6:1 pair is eff 0.197 vs 0.198 (tied) for 5.6 % less money. The adoption window
had been chosen in W39 for Q1 comparability, not for B — and it flattered B.

**Amendments 3–4** — regime vs recency. The regime split looked decisive: B loses in the
bottom half of the volatility regime (−$3.0 and −$4.0 per trade) and earns in the top half
(+$45.8 and +$39.5, where 109 % of its money is), and the high-vol band was stress-net positive
in **both** modern halves (+$12,015 and +$75,665) while the low band was negative in both — the
preregistered promotion condition, met. Deep history framed it as an **epoch**: 2006-2011,
2011-2016 and 2016-2019 are stress-negative in both bands; 2019-2022 is stress-positive in both.
H1 was settled both ways and neither was quietly chosen: **8/16 positive deep-history years on
net (the literal threshold, met) but 2/16 on stress-net** (the campaign's standing requirement,
and the binding number).

**Amendment 5 — and this is the wave's most valuable catch.** The regime band of amendment 4
was cut at the **full-sample median** of the regime variable. Re-expressed causally, as the
**trailing-250-session median** of the same variable — no fitted constant, in the spirit of
W37's derived k — the separation largely disappears:

| full window 2022-07 → 2026-08 | weekly | wk + % | worst | Sharpe | eff | stress |
|---|---|---|---|---|---|---|
| B ungated | $323 | 53.7 % | −$11,175 | 0.076 | 0.029 | +$114 |
| **B causally regime-gated** | **$200** | **32.0 %** | −$9,142 | 0.060 | 0.022 | +$84 |

The gate makes B **worse**, not better. **The regime effect was a full-sample-quantile
artifact** — the third time in this campaign that a full-sample threshold manufactured a
result (W03's gate, W37's score thresholds, now this).

## 3. Where B ends up

| measure | value | verdict |
|---|---|---|
| standalone stress-net, full window | +$114 (ungated) / +$84 (gated) | barely positive |
| correlation with the long object | +0.01 | genuinely independent |
| **correlation inside the long object's worst-decile weeks** | **−0.25** | genuinely decoupled |
| bar overlap | 5.7 % | structurally separate |
| weight scan, full window | w = 0.05–0.10 improves **CVaR-efficiency** 0.272 → 0.295 (+8 %) but **not** eff | partial |
| 8 long : 1 B-gated vs exposure-matched long alone | eff 0.201 vs 0.198, CVaR-eff 0.291 vs 0.272, worst −$59,497 vs −$61,723, weekly $11,957 vs $12,228 | marginal |
| N1 circular shift | 97th percentile, p = 0.030 | EVIDENCE |
| **N2 count-matched random entries** | **92nd percentile, p = 0.080** | **weak — adoption requires ≥ 95th** |
| per year, gated | 2023 ≈ 0 · 2024 −$470/wk · 2025 +$1,946/wk · 2026 +$846/wk | 2 poor of 4 |

**PARKED, with the revival condition stated**: B returns to candidacy if its binding
count-matched null reaches the 95th percentile on a longer sample, or if a mechanism is found
that explains why volatility-expansion entries became viable around 2019 and *stays* causal
when its threshold is derived from trailing data. What it already proves is narrower and real:
**a non-Solar engine that is positive after frictions and decoupled inside our drawdowns
exists** — W25/W27's orthogonal engines were all loss-making, and this one is not.

## 4. Standing rules this wave adds
1. **Full-window and per-year re-measurement is a precondition for any adoption.** A window
   chosen for one purpose will flatter something else.
2. **Any threshold or quantile cut on the measurement sample must be re-derived causally
   before it can support a conclusion** — three separate results in this campaign have died
   at this step, and the third one had already produced a promotion.
3. An arbitrary portfolio allocation is not a diversification verdict: scan weight at
   **constant total exposure**, time-weighted in contract-minutes.

## 5. What this means for the objective
The route to the owner's target is diversification that lowers the tail, and after four
mechanism families plus W25/W27's five signal families, **none has been found on NQ 1-minute
bars.** The honest bound is exactly that — not that none exists. The next escalation is a
different data representation (W41, the multi-clock axis on the true engine) or a different
instrument, not more rules on this one.
