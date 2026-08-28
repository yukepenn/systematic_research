# SPEC — `VOLUME_LIQUIDITY_V1` · ONE frozen within-sector liquidity-risk-premium specification

**COMMITTED BEFORE ANY VOLUME ALPHA P&L EXISTS.** Commit C of the campaign.
**ONE primary formulation. ZERO challengers. NO machine learning.**

| | |
|---|---|
| **family** | multi-market **VOLUME / PARTICIPATION / LIQUIDITY** — genuinely new information in this substrate |
| **what it is NOT** | not TSMOM, not carry, not BBO, not ESNQ, not INT02, not event response. **A failure in any of those is not evidence about this, in either direction** |
| **data contract** | `VOLUME00` (`f4ba199`) → **`DATA-CAPABLE`**, representation **`ROOT_TOTAL`**, roll embargo **`E = 0`** |
| **universe** | **21 roots · 6 sectors**, admitted by `VOLUME00` on **coverage alone**. Nothing excluded |
| **attempt budget** | **ONE specification. Zero challengers.** Every cell tried against outcome data is selection debt |
| **LIVE ENABLED** | **NO** |

> ## ⚠️ **`MAXIMUM HISTORICAL EVIDENCE CLASS = DISCOVERY-GRADE`. PERMANENT FOR THIS FAMILY.**
> Every usable historical date in this substrate is already outcome-consumed — 2009–2018 by TSMOM
> development and CARRY development, 2019–2022 by TSMOM V2 validation, 2023–2026 by TSMOM TAIL-H1.
> **No historical window can produce `VALIDATED`, `LIVE-ELIGIBLE` or `PRODUCTION-READY`.**
> The chronological held-back windows are still useful — they control *family-specific* selection —
> and they are named exactly what they are:
> ### **`FAMILY-SPECIFIC HELD-BACK / MARKET-OUTCOME-CONSUMED`**
> ⛔ Never `pristine OOS` · `clean historical validation` · `forward` · `prospective` ·
> `independent validation`. **The best a historical pass can create is
> `DISCOVERY-GRADE / HISTORICALLY REPLICATED`. Only genuinely future evidence raises the class.**

---

## 1. Mechanism — ONE, and the sign is fixed by economics before any result

> ### **LIQUIDITY-RISK PREMIUM.** Within a sector, a market whose **participation is abnormally LOW
> ### relative to its own recent norm** commands a return premium for bearing illiquidity — thin
> ### participation means wider effective spreads, higher inventory risk and greater price impact,
> ### so those willing to hold demand compensation.

| | |
|---|---|
| **LOW** relative participation | → **LONG** / positive expected-return exposure |
| **HIGH** relative participation | → **SHORT** / negative expected-return exposure |

**⛔ THE SIGN MAY NOT BE FLIPPED AFTER SEEING A RESULT.** See §9 — a mirror that wins does not
create `VOLUME_LIQUIDITY_V1_INVERTED`; it closes V1.

**Why not trend:** it reads **volume**, never past returns, and is deliberately agnostic to price
direction. **Why not carry:** it reads **participation**, not the near/deferred **price**
relationship. **Why within-sector:** a raw cross-sector volume level encodes **contract size and
tick convention**, not liquidity.

## 2. Signal — the EXACT feature, frozen here

For root `i` and completed session `d`, using **`ROOT_TOTAL` volume** (the sum over all live
contracts of root `i` on `d`, per `VOLUME00`):

```
LV(i,d)     = log(1 + Volume(i,d))

MED63(i,d)  = median of the prior 63 eligible LV observations, STRICTLY before the decision
MAD63(i,d)  = median absolute deviation of those same prior 63 observations

ZVOL(i,d)   = (LV(i,d) - MED63(i,d)) / max(1.4826 * MAD63(i,d), 1e-6)

RELZ(i,d)   = ZVOL(i,d) - mean over eligible j in the SAME SECTOR of ZVOL(j,d)

S(i,d)      = clip(-RELZ(i,d), -3, +3)                      <-- the frozen signal
```

| decision | commitment |
|---|---|
| **63** | **ONE frozen quarterly-ish horizon.** ⛔ No 20 / 42 / 126-day sweep. ⛔ No EWMA-vs-median shootout |
| **median / MAD** | robust to the roll-adjacent spikes `VOLUME00` measured. **Not compared to mean/sd by performance** |
| **`1e-6` floor** | **a division-by-zero guard, not a parameter.** It is not tuned and never will be |
| **`log`** | volume is right-skewed by orders of magnitude; a level difference would be dominated by the largest contract |
| **clip ±3** | bounds a single degenerate observation. Fixed now |
| **demean, NOT centred rank** | ⚠️ **`CARRY_V1`'s recorded structural finding**: with `n_sector = 2`, a centred rank degenerates to **±1** and becomes a full-strength binary pair trade. Demeaning gives `RELZ₁ = −RELZ₂ = (Z₁−Z₂)/2`, which **preserves magnitude** — a small difference produces a small position. **That mistake is not repeated** |

**A sector with fewer than 2 eligible roots yields `RELZ = 0` and therefore no position** — a
consequence of the formula, not a special case.

## 3. Sizing — signal strength must matter

> ### ⛔ **NO CONSTANT-GROSS NORMALIZATION.** Normalizing every date to a target gross exposure
> ### would turn microscopic signal differences into full-risk trades. **A small signal produces a
> ### small position; a zero signal produces zero position.**

```
RISK_SCORE(i,d) = S(i,d) / 3                        approximately in [-1, +1]

SIGMA(i,d)      = sd of the prior 63 basis-safe daily economic returns in USD,
                  STRICTLY LAGGED, from the certified TSMOM substrate

n(i,w)          = RISK_SCORE(i, cutoff_w) * RISK_BUDGET / SIGMA(i, cutoff_w)      contracts
RISK_BUDGET     = $1,000 of daily-P&L sd per root at |RISK_SCORE| = 1
```

`RISK_BUDGET` is a **scale constant**. Sharpe, cost/gross, every share and every ratio gate are
**scale-invariant**; only absolute dollars move with it. Fractional contracts are **research
sizing** and are labelled as such. ⛔ **No Markowitz. No covariance optimizer. No ex-post Sharpe or
correlation weights. No full-sample inverse-vol weight.**

### Sector concentration control — CAP DOWN ONLY

Ex-ante sector gross risk `G_s = Σ_{i∈s} |RISK_SCORE(i)| · RISK_BUDGET`; total `G = Σ_s G_s`.
**Single deterministic pass, no iteration:** any sector with `G_s / G > 0.40` is scaled by
`0.40·G / G_s`. ⛔ **The removed risk is NOT reallocated. Other sectors are never scaled up.**
Economic exposure stays tied to signal strength.

## 4. Trading object

| element | commitment |
|---|---|
| **rebalance** | **WEEKLY**, one frequency, frozen. Positions for ISO week `W` are determined **entirely** from sessions completed **strictly before `W` begins** — cutoff = the last eligible session with `date < Monday(W)`. ⛔ No same-week volume. ⛔ No best-weekday search |
| **why weekly** | participation is not a millisecond signal; lower turnover, lower cost sensitivity, aligns with the incumbent's weekly evaluation axis, and does not convert daily activity noise into churn |
| **position / roll** | root-level economic exposure mapped into the **causally active full contract**. If the active contract changes mid-week: **close old, open new, charge real roll turnover, preserve the root-level direction.** ⛔ Roll costs are never erased. P&L uses the certified basis-safe self-financing return, which never differences two contracts |
| **model** | **NO MACHINE LEARNING.** One deterministic rule. The signal is already the hypothesis; a Ridge or GBM would only add a second search layer |

### Costs — stated per SIDE so nothing is double-counted

```
COST_PER_SIDE(i) = (COMMISSION_RT + SLIP_TICKS_RT * tick_size(i) * point_value(i)) / 2
COMMISSION_RT    = $4.36 per contract round turn        (NinjaTrader Lifetime template)

sides at a weekly rebalance = |n(i,w) - n(i,w-1)|
sides at a roll             = 2 * |n(i,w)|              close old + open new = one full RT
```

| | `SLIP_TICKS_RT` |
|---|---|
| **PRIMARY** | **1.0** — the canonical multi-market assumption |
| **PURE COST STRESS** | **2.0** — one additional tick of friction on **the SAME trades** |

> ### ⚠️ **THE `ESNQ_V1` STRESS AMBIGUITY MUST NOT RECUR, SO IT IS DEFINED OUT OF EXISTENCE.**
> The stress recomputes costs on an **IDENTICAL, FROZEN position path**. It may not change the
> signal, any threshold, or the action set. **This strategy has no threshold at all** — weights are
> continuous — so there is structurally nothing for a stress to move.
> **`net_stress ≤ net_primary` is asserted mechanically on the identical path.**

**Reported every time:** gross · costs · net · **cost / |gross|** · turnover.

## 5. Chronology — and the honest name for each window

| window | role | reachability |
|---|---|---|
| **2009-01-01 → 2018-12-31** | **DEVELOPMENT** (substrate effectively begins 2010-03-23 after the certified 252-day warmup; a further 63 sessions are consumed by `MED63`) | now |
| **2019-01-01 → 2022-12-31** | **HELD-BACK CONFIRMATION** | unreachable until the development verdict is committed |
| **2023-01-01 → 2026-07-31** | **MODERN CONFIRMATION** — the substrate's actual pre-seal endpoint | unreachable until held-back confirmation is committed |

**Protection is structural, not advisory:** the development runner asserts
`max(evaluated date) < 2019-01-01`; every runner asserts `max(date) < 2026-08-01`.
⛔ The **≥ 2026-08-01 global seal is never crossed.** ⛔ No post-seal data is fetched.

## 6. PRE-RESULT ENGINE CERTIFICATION — blocking, before any development economics

No alpha result is admissible in this repo without direct engine falsification. **All five must
pass before the economics are read**, and the completion order is recorded.

| # | certification | requirement |
|---|---|---|
| **6A-NEG** | corrupt volume **and** prices strictly **after** the information cutoff | weights for the current decision are **EXACTLY unchanged** |
| **6A-POS** | corrupt a **causally admissible prior** volume observation that `MED63`/`MAD63` actually use | **at least some affected future weights MUST change.** ⚠️ A probe that returns "nothing moved" is not certification — it must be shown to have teeth |
| **6B** | corrupt **future returns** | current weights unmoved; **only subsequent P&L** changes |
| **6C** | key safety via `research_sdk/keysafe.py` | expected keys resolve · no silent empty merge · unmatched counts reported · non-empty inputs may not produce silently empty outputs |
| **6D** | **P&L identity**, proved independently | `daily root P&L = prior position × basis-safe price change − actual turnover cost`; reconcile root → sector → portfolio. No hidden exposure multiplication, no merged/back-adjusted basis |
| **6E** | **INDEPENDENT IMPLEMENTATION** | a structurally different second calculation of the frozen signal, weights and P&L |

**6E contract.** PRIMARY = vectorized dataframe path. INDEPENDENT = explicit chronological
root/date loop. The independent implementation may share **certified raw data, generic safe
utilities and frozen constants**; it **may NOT import the primary signal-construction function**
(verified by AST, not by grep — a docstring once matched a grep). Required before P&L is
interpreted: identical eligible dates · identical active contracts · identical signal availability ·
signal and weight differences within tight deterministic tolerance · **position direction exact** ·
**turnover exact** · root P&L reconciled · portfolio P&L reconciled to cents or a justified floating
tolerance.

> **If parity fails, STOP BEFORE ECONOMIC INTERPRETATION.** Fix only contract/implementation
> defects. ⛔ **Never choose the implementation whose P&L is nicer.**

## 7. Development — ONE shot

Run **exactly once** after this SPEC and both implementations are committed. ⛔ Do not inspect
held-back or modern confirmation.

**DEPENDENCE UNIT = WEEK.** Not root-day, not root-trade, not individual market. **The portfolio
weekly net P&L series is the inferential object.**

### 7A. Required economic report

gross · costs · net · cost/|gross| · weekly mean · weekly median · weekly sd · annualized weekly
Sharpe (`mean/sd × √52`) · max drawdown · drawdown duration · ES 5 % · positive-week rate ·
turnover · average gross risk · average net directional exposure · long vs short contribution ·
root contribution · sector contribution · calendar-year results · four equal chronological blocks ·
top 1 / 5 / 10 weeks · top root · top sector · leave-one-root-out · leave-one-sector-out ·
market-beta / equal-risk-long-basket diagnostic · **LOW-participation sleeve vs HIGH-participation
sleeve contribution** · **contribution by distance-to-roll** (`VOLUME00`'s declared residual risk:
the ±1 embargo ratio was **1.481** against a 1.5 gate).

### 7B. Dependence-aware uncertainty — frozen before running

Circular block bootstrap on **weekly portfolio net**: `L = round(n_weeks^(1/3))`, `B = 20,000`,
seed **`20260828`**. **Primary inference: one-sided lower 95 % bound of mean weekly net > 0.**
An IID bootstrap may be reported as a diagnostic. ⛔ **The block result is never replaced by a
friendlier IID result.**

### 7C. NULL #1 — TEMPORAL ASSOCIATION

**ONE shared circular shift per replicate, in WHOLE WEEKS, applied identically to every root's
volume series.** A shared shift preserves the cross-sectional dependence of participation and the
sector-demean structure completely, and destroys **only** the alignment between volume and future
return. ⛔ No tiny one-day shifts. ⛔ No shift chosen from observed performance.
**Every replicate re-runs the complete portfolio construction.** Shifts are the **exhaustive** set
of distinct non-zero whole-week shifts, capped at 500; the exact count is reported.
**Assert ≥ 2 distinct outcomes.** Real must exceed the **95th percentile**.

### 7D. NULL #2 — WITHIN-SECTOR SIGNAL-IDENTITY PLACEBO

At each rebalance, permute the frozen `S(i,d)` values **across eligible roots within sector**.
**Preserved:** signal distribution, number of active roots, risk scaling (each root keeps its own
`SIGMA`), sector structure, turnover architecture. **Destroyed:** the mapping between a root's own
liquidity state and its own future return. 500 replicates, seed `20260828`.
Real must exceed the **95th percentile**.

### 7E. STATIC-LONG CONTAMINATION DIAGNOSTIC

Average signed exposure · beta to an **equal-risk long-only multi-market basket**
(`RISK_SCORE ≡ +1`) · regression intercept · R² · P&L of a static exposure-matched benchmark.
⛔ **The strategy is NOT residualized after seeing the result.** This adjudicates *interpretation*;
it is not a post-hoc repair.

## 8. Development gates — ALL FROZEN NOW, ALL MUST PASS

| # | gate |
|---|---|
| **D1** | PRIMARY after-cost net **> 0** |
| **D2** | annualized weekly Sharpe **≥ 0.50** |
| **D3** | circular-block-bootstrap one-sided **lower 95 % bound** of mean weekly net **> 0** |
| **D4** | **PURE COST STRESS** net **> 0** on the **SAME** position path |
| **D5** | cost drag `cost / |gross P&L|` **≤ 25 %** |
| **D6** | net **> 0** in **≥ 3 of 4** equal chronological development blocks |
| **D7** | top root **≤ 35 %** of the **SUM OF POSITIVE root contributions** **AND** top sector **≤ 50 %** of the **SUM OF POSITIVE sector contributions** |
| **D8** | **leave-one-root-out**: removing **ANY** single root leaves development net **> 0** |
| **D9** | temporal null — real **> 95th percentile** |
| **D10** | within-sector identity placebo — real **> 95th percentile** |
| **D11** | top **10** positive weeks **≤ 50 %** of total positive weekly contribution |

**Positive-contribution denominators are used in D7 and D11 so the metric stays defined**
(RR_W001's G2 read 39.28 % on |value| and **104.9 %** on the sum — only the sum is what a book
earns). **If a threshold creates a mathematically undefined object, it is marked `NOT ADJUDICATED`
and explained.** ⛔ **No friendly replacement is invented after the result.**

### 8A. ⛔ NO MIRROR RESCUE

The sign mirror may be reported as a diagnostic. **If the mirror is better, that does NOT create
`VOLUME_LIQUIDITY_V1_INVERTED`.** The economic sign was selected before outcomes; a reversal after
observing P&L is a **new hypothesis whose discovery population has now been consumed**.
**V1 fails. STOP.**

## 9. If development fails — pre-committed, so no result can be rescued

**STATUS: `VOLUME_LIQUIDITY_V1 — NO CANDIDATE / CLOSED AT EXACT SCOPE`.**
⛔ Do not read held-back volume P&L. ⛔ Explicitly forbidden afterwards:
20d · 42d · 126d · daily rebalance · monthly rebalance · no sector demean · sector-only ·
energy-only · metals-only · equity-only · long-only · nonlinear volume transform · volume
acceleration · volume momentum · volume × trend · volume × carry · volume-confirms-price ·
open interest · volume-price divergence · ML.

Write the closure, re-rank the frontier, **return to owner**. ⛔ Do not spend the remaining unread
ES BBO, NQ BBO 19, `ESNQ_BLIND_EFFECTIVE_14`, the 141-session Last-only pool, or the global seal.

## 10. If development passes

Freeze **everything** — universe, exclusions, formula, lookback, clipping, rebalance, risk scaling,
sector cap, roll handling, costs, stress, implementation hashes, development population, null
definitions. **STATUS: `DEVELOPMENT-SUPPORTED / DISCOVERY-GRADE`. NOT validated.** Only then open
2019–2022, with gates **H1–H7** as preregistered by the owner directive; then, only on a pass,
2023 → 2026-07-31 with **M1–M6**; then portfolio additivity with **P1–P6**; and only after all four
stages, `VOLUME_LIQUIDITY_CANDIDATE_1` at
**`DISCOVERY-GRADE / HISTORICALLY REPLICATED / PORTFOLIO-ADDITIVE`** — **never `VALIDATED`**.

**LIVE ENABLED remains NO at every stage.**
