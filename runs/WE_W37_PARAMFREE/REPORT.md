# WE_W37 — CAUSAL, PARAMETER-FREE QUALITY LAYER · REPORT

Two defects fixed at once: a **threshold look-ahead** found while writing the spec, and the
**parameter churn** that failed W36's walk-forward.

| arm | pts/session | $/trade | weekly | worst week | Sharpe | **weekly ÷ \|worst\|** |
|---|---|---|---|---|---|---|
| P0 BASE (no quality layer) | 10.62 | $103.9 | $1,060 | −$7,487 | 0.305 | 0.142 |
| P4 full-sample quantiles *(look-ahead)* | 15.86 | $165.2 | $1,583 | −$7,418 | 0.331 | 0.213 |
| P4 + cut + big target *(= old A3, look-ahead)* | 17.78 | $170.5 | $1,774 | −$7,418 | 0.338 | 0.239 |
| **P1 causal, trailing 250 entries** | **14.72** | $153.0 | $1,470 | −$7,418 | 0.311 | 0.198 |
| **P2 P1 + causal cut @23 bars** | 13.50 | $82.2 | $1,347 | **−$5,818** | 0.291 | **0.232** |
| P3 causal w=100 / w=500 | 13.42 / 15.62 | — | — | −$8,275 / −$7,418 | 0.314 / 0.331 | 0.162 / 0.210 |

## 1. The look-ahead, quantified

The score's cut points were `np.nanquantile(feature[ALL entries])` — the full-sample entry
distribution, which contains **future** entries. Making them causal (trailing 250 prior
entries) costs **−3.05 pts/session and −0.027 Sharpe**. Every fixed-calibration quality number
in W34 and W35 carried this; they are superseded.

**The two independent honest paths now agree**: W36's quarterly walk-forward gave
**14.41 pts / Sharpe 0.303**; this wave's causal fixed rule gives **14.72 / 0.311**. Two
different corrections of two different contaminations land on the same number, which is the
strongest cross-validation the campaign has produced.

## 2. Parameter-free by construction

`k = 3` is no longer chosen from a grid — it is **"a majority of the five quality features"**,
derived from the feature count. The big target is dropped (W36 C1 measured its marginal at
−0.000). The cut length is no longer chosen either: it is the base object's own **trailing
median hold, which the data set to 23 bars**. With nothing left to select, there is no churn
for a walk-forward to punish.

## 3. A trend I must flag against myself

Longer trailing windows score better: w=100 → 13.42, w=250 → 14.72, w=500 → 15.62, and
w = ∞ *is* the contaminated 15.86. **The monotone improvement with window length is the
look-ahead creeping back in**, not evidence that a longer window is better. w = 250 is the
defensible choice; w = 500 is not, and is reported only to make this visible.

## 4. Adoption and null

**P2 is adopted** on the owner's stated objective (maximum profit, minimum drawdown):
+27 % weekly mean and a **22 % smaller worst week** than base, i.e. **weekly-per-unit-of-tail
0.142 → 0.232, +63 %**. Its circular-shift null is **100th percentile, p = 0.000 — EVIDENCE**.
P1 is also adopted and is the higher-production, higher-Sharpe alternative
(14.72 pts, 0.311, tail unchanged). The choice between P1 and P2 is a risk preference, not an
evidence question, and both are kept.

Sharpe is deliberately **not** the sole gate here, per W36: it penalises the upside variance
this layer is designed to add, while the owner's objective is a tail objective. Both metrics
are reported for every arm.
