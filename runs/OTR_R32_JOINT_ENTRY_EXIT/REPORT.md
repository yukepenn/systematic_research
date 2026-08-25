# OTR_R32_JOINT_ENTRY_EXIT — report

Spec preregistered before readout. Owner directive R31 §7/§13/§14. Designed around R31's lesson:
23 non-sealed windows, an explicit fit/holdout split fixed in advance, no selection on any single
correlation or on net P&L. August sealed and untouched.

**Fit** = 17 windows to 2026-05-29 (continuous parquet, the incumbent's convention).
**Holdout** = 4 Strategy Analyzer windows in June/July, run per-window from the contract CSVs.
The two June **Trade Performance** records (0152/0154) are excluded from scoring — live executions
with commission included and non-uniform size are a different measurement basis from a backtest.

**B1 HARNESS CHECK: PASS.** `D_MOM|G_WITH|P_MED|C_DIR|X_OPP` reproduces the incumbent exactly —
**1,512 trades, §40 distance 0.4768**. The run is valid.

---

## 1. Part B — the fade axis is now tested, and it is DISFAVOURED

Every one of the 144 members in the R7/R8 grid is trend-conditional (`cand = +1` iff `trend > 0`),
so a counter-trend architecture was never representable. `layer_a_v2` adds the direction and
trend-gate flags. 288 configurations.

| direction | n | fit min | fit median | hold min | hold median | median trades |
|---|---|---|---|---|---|---|
| **D_MOM** | 144 | **0.4368** | 0.8415 | **0.3503** | 0.7015 | 1,691 |
| **D_FADE** | 144 | 0.5268 | 0.8468 | 0.4790 | 0.8194 | **1,194** |

**B2 confirmed in the sense registered:** fade is clearly *distinguishable* — and it is worse on
both samples, by 0.09 on fit and 0.13 on holdout.

Note the trap it walks into: **D_FADE's median trade count (1,194) is far closer to his 1,214 than
D_MOM's (1,691)** — and it still fits worse on both samples. That is the third independent
instance this campaign of *matching the trade count without matching the trades*.

> **The counter-trend / value-fading hypothesis is tested and disfavoured.** It was the last
> untested structural axis in the entry space, and it is not where he is.

---

## 2. Part B — a configuration that beats the incumbent on BOTH samples

**B4 answered: 8 configurations beat the incumbent on fit and holdout. B3 names 3 as LEADING**
(top-5 fit *and* top-10 holdout) — but two of those are the same thing, since under `D_MOM` the
`G_WITH` gate is redundant (direction is already the trend sign), which is itself a useful
internal consistency check that the harness passed.

| configuration | fit | fit rank | **holdout** | hold rank | trades (fit) |
|---|---|---|---|---|---|
| **`D_MOM \| P_IN \| C_REC \| X_TRAIL_PTS:80`** | **0.4368** | 1 | **0.3503** | 1 | 1,339 |
| `D_MOM \| P_MED \| C_DIR \| X_TARGET:60` | 0.4693 | 5 | 0.3817 | 5 | 1,643 |
| incumbent `P_MED \| C_DIR \| X_OPP` | 0.4768 | 12 | 0.4546 | 22 | 1,512 |

Three structural changes from the incumbent, all in the same direction:

1. **`P_IN` beats `P_MED`** — entries at the **outer rails** (MAX/MIN), not at fair value.
2. **`C_REC` beats `C_DIR`** — confirmation by *close beyond the rail*, not by bar direction.
3. **`X_TRAIL_PTS:80`** — a fixed 80-point trailing stop. Note this is **not** the 20–30 points
   of the identification R31 withdrew; the joint search prefers a trail nearly 4× wider.

**It performs BETTER out of sample than in sample** (0.3503 holdout vs 0.4368 fit). That is the
opposite of the overfit signature, and the holdout windows include the two largest right-tail
weeks of 2026.

**Discipline, stated plainly.** 288 configurations were scanned; the expected number passing a
top-5 × top-10 rule by chance is ≈ 0.17, and 3 (really 2 distinct) passed. That is above chance.
But **the holdout is only 4 windows**, so its rank is noisy. Per the spec, **nothing here is
promoted into any model.** Two configurations were correctly identified as **OVERFIT** by the rule
(`P_IN|C_REC|X_TARGET:60`, fit #3–4 → holdout #23–24), which is evidence the rule discriminates.

---

## 3. Part A — the one robust regularity is NOT an exit phenomenon

The only relationship that survived R31's out-of-sample extension is
`corr(ATR, his avg_loss) = −0.509 → −0.515`. His average **loss** shrinks as volatility rises.

A fixed hard stop predicts the **opposite** sign: at higher volatility the stop is reached more
often, losses pile at the cap and drag the mean up. Measured across nine exit families:

| exit family | avg_loss | /cap | stop-out share | corr(ATR, avg_loss) |
|---|---|---|---|---|
| X_OPP (incumbent) | $540 | 0.208 | 0.091 | **+0.775** |
| X_TREND | $266 | 0.102 | 0.001 | +0.837 |
| X_FV | $218 | 0.084 | 0.001 | +0.848 |
| X_BAND | $180 | 0.069 | 0.001 | +0.738 |
| X_TRAIL_PTS 80 | $443 | 0.170 | 0.001 | +0.727 |
| X_TARGET 60 | $517 | 0.199 | 0.080 | +0.762 |
| X_TIMEOUT 60 | $480 | 0.185 | 0.049 | +0.869 |
| **the trader** | **$949 (median)** | **0.365** | not observable | **−0.509** |

> **A2's registered consequence fires: 0 of 9 families reproduce his sign.** All nine are strongly
> positive (+0.66 to +0.87) against his −0.51 — a gap of 1.2–1.4 in correlation with nothing close.

### And a second gap I did not predict

**His average loss is 36.5 % of his stop. Every configuration we have sits at 7–21 %.**

That ratio is **scale-invariant** — it does not depend on quantity, so it survives the whole
130×1 vs 65×2 ambiguity. It says something simple and structural:

> **His losing trades run roughly twice as far, relative to his own risk limit, as any exit rule
> we have built.** Our exits are too tight on the losing side, and no family tested closes it —
> the widest (X_OPP at 0.208) is still 40 % short.

Combined with his larger average winners, the honest summary is that **his entire trade
distribution is wider than ours in both directions at the same stop.**

---

## 4. What this run establishes

- **Fade/counter-trend: tested and disfavoured.** The last untested entry axis is closed.
- **A better configuration exists and survives an out-of-sample check** — outer-rail entries,
  close-beyond-rail confirmation, wide 80-point trail. Not promoted.
- **No exit mechanism explains `corr(ATR, avg_loss)`**, the one regularity that survived R31.
  Per the preregistered consequence, an **exposure/sizing law is now the only remaining candidate**
  for it — and R31's A3 already established that sizing cannot explain holding time, so the
  exposure law and the hold law are separate phenomena needing separate explanations.
- **A new scale-invariant constraint**: `avg_loss / stop = 0.365` for him, 0.07–0.21 for us.

## 5. What it does not establish

- It does not identify his entry rule; `P_IN|C_REC` is better than the incumbent, not identified.
- The holdout is 4 windows. The leader is a candidate, not a finding.
- It says nothing about any vendor component (§5, §43).
- It does not explain the loss-width gap or the ATR–avg_loss sign.
