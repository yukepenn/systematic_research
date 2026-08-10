# U6B_PRODUCT_A_SCALE_RATE — Capital Frontier & Intraday Drawdown/Ruin Risk Panel

**Master Directive v4, Wave 5 — final adjudication input.** Scope: Part 1 (audit prior capital
methodology), Part 2 (capital frontier, directive sec6), Part 3 (intraday DD/ruin, directive
sec7). This document does **not** render a promotion verdict — U6B's original "NOT PROMOTED"
disposition (`runs/U6B_PRODUCT_A_SCALE_RATE/REPORT.md`, 2022-2025-only wash threshold) and O2's
"high-priority frozen challenger, pending independent adversarial review"
(`runs/O2_OWNER_UTILITY_READJUDICATION/REPORT.md`) both stand untouched; this panel supplies the
capital/risk evidence the directive asked for, for whoever renders the final call.

All work is under `runs/U6B_PRODUCT_A_SCALE_RATE/risk_panel/` (`src/` = 4 scripts, `out/` = every
CSV/JSON/parquet cited below). **ABSOLUTE RULE compliance**: every script asserts on
`research/operational/LOCKED_FORWARD.md`'s 2026-08-01 boundary (verified: substrate's own
`HEALTH_END=2026-07-31` upstream guard, plus an explicit assertion in
`01_bar_level_construction.py`); nothing on/after 2026-08-01 is touched anywhere in this panel.

Convention used throughout: **FACT** = a measured statistic of the one realized historical path,
no resampling. **INFERENCE** = a statistic of the bootstrap/resampled path distribution (a model
of possible histories, not a measurement of the future). **LIMITATION** = a disclosed scope
choice or known gap. Genuine-MNQ pricing throughout (per the directive); canonical window
2022-01-03 → 2026-05-29 (1,139 sessions) unless the June–July-2026 health-only extension is
explicitly named.

---

## PART 1 — Audit of prior capital methodology (done first, before any frontier was built)

**(a) The existing house capital-map rule, and where it already touches Product A.**
`capital_needed = p95(bootstrapped max-$-drawdown) / thr` — coded once in
`runs/PRODUCTB_ONECONTRACT_FINAL/build_parity_and_metrics.py::capital_map` (three bootstrap
methods L5/L20/stat60, `nb=2000`, `seed=20260808`, `thr ∈ {0.10,...,0.30}`) and already applied
to a Product-A object with the **identical function body, grids and seed** in
`runs/W17_C4_COMPLIANCE/out/v1f_capital_map_productA.csv` (documented in
`runs/W17_C4_COMPLIANCE/V1F_EVENTDAY.md` §3, "Product A's unit is one copy of the master, peak
physical size 11 MNQ"). At `thr=0.25` (the O1 pre-registered tolerance), `stress_mult=1.0`:

| method | p95 max-$-DD | capital_needed @ thr=0.25 |
|---|---:|---:|
| L5 (moving5) | $52,946.04 | **$211,784.16** |
| L20 (moving20) | $37,056.56 | **$148,226.24** |
| stat60 (stationary60) | $28,829.12 | **$115,316.48** |

**Disclosed caveat**: this pre-existing map was built on the SolarWaveSMMaster_v2 "master"
research curve (net $194,416.04, per `O1_OBJECTIVE.md` §5), a closely related but **not
bit-identical** series to U6B's own CONTROL genuine-MNQ canonical series (net $178,687.40). It is
cited here as **context/an anchor for the grid range**, not as U6B's own recomputed capital map —
U6B's own maxDD (below) is used to set the actual grid.

**(b) Numerical re-verification of the O1 §2.6 scaling identity, on THIS run's own object**
(not merely citing the prior document's claim about a different series). `primary_objective_v2`
was called directly, twice, on U6B CONTROL's genuine-MNQ canonical series:

| quantity | L=0.5 / C=$100,000 | L=1.0 / C=$200,000 | \|diff\| |
|---|---:|---:|---:|
| objective_J (mixture) | 0.1727465215438444 | 0.1727465215438444 | **0.000e+00** |
| CE_g | 0.17981310185487095 | 0.17981310185487095 | 0.000e+00 |
| P_ruin | 0.005166666666666667 | 0.005166666666666667 | 0.000e+00 |
| J_worst (Γ-minimax) | 0.15811708858698417 | 0.15811708858698417 | 0.000e+00 |

**IDENTITY CONFIRMED, bit-exact** (both calls draw from the same seeded bootstrap generator at
the same `n`, so this is the same computation reached two ways, not an approximation). This
licenses treating `PO2.leverage_curve(capital=REF, grid=[REF/c for c in CAPITAL_GRID])` as **the**
capital-frontier engine below — it *is* `primary_objective(capital=c, leverage=1.0)` for every `c`
in the grid, exactly as the task instructed ("USE THIS rather than writing new capital-sweep
machinery"), not a separate implementation of the same idea. A grid point (C=$200,000) computed
via the leverage-curve reparametrization was cross-checked against the direct call above:
**exact match** (`0.1727465215438444` both ways).

**Grid chosen and justified**: `{$50k, $75k, $100k, $150k, $200k, $300k, $500k}`, leverage=1.0,
applied identically to CONTROL/F0.5/F0.7. Anchor: U6B's own certified canonical genuine-MNQ
maxDD_eod is **$17,069.90 / $17,390.80 / $16,977.30** (CONTROL/F0.5/F0.7, from
`out/u6b_mnq_grid_battery.csv`, re-verified independently in Part 3 below). $50k ≈ 2.9–3.0×
this maxDD (clearly thin — a 25%-of-capital ruin barrier is already ~34% consumed by the single
historical worst EOD drawdown); $500k ≈ 29–30× (clearly generous). The grid also **brackets the
pre-existing $115k–$212k capital-map band from (a) on both sides**, so it is not narrower than
the house's own prior methodology would suggest.

Files: `risk_panel/src/02_capital_frontier.py` (Parts 1a/1b + 2), `risk_panel/out/part1_audit.json`.

---

## PART 2 — Capital frontier (directive sec6)

### 2.1 Headline table — J (mixture), J_worst (Γ-minimax), CE_g, P_ruin, by candidate × capital

Daily-close leg, R1=25% absorbing barrier, `n_boot=2000`, `seed=20260808`, `λ≈1.3677/yr`
(fixed-fraction convention, module-derived, unchanged from PO2 defaults). **INFERENCE** (bootstrap).

| candidate | capital | J (mixture) | J_worst (Γ-minimax) | CE_g | P_ruin (mixture) | mc_se(J) |
|---|---:|---:|---:|---:|---:|---:|
| CONTROL | $50,000 | −1.1744 | −1.1872 | 0.1436 | 0.9637 | 0.0057 |
| CONTROL | $75,000 | −0.3377 | −0.7277 | 0.3118 | 0.4748 | 0.0116 |
| CONTROL | $100,000 | +0.0594 | −0.2146 | 0.3051 | 0.1797 | 0.0086 |
| CONTROL | **$150,000** | **+0.1970** | **+0.1312** | 0.2319 | 0.0255 | 0.0036 |
| CONTROL | $200,000 | +0.1727 | +0.1581 | 0.1798 | 0.0052 | 0.0019 |
| CONTROL | $300,000 | +0.1231 | +0.1222 | 0.1231 | 0.0000 | 0.0008 |
| CONTROL | $500,000 | +0.0753 | +0.0748 | 0.0753 | 0.0000 | 0.0005 |
| F0.5 | $50,000 | −1.1712 | −1.1822 | 0.1457 | 0.9628 | 0.0058 |
| F0.5 | $75,000 | −0.3331 | −0.7192 | 0.3139 | 0.4730 | 0.0116 |
| F0.5 | $100,000 | +0.0620 | −0.2007 | 0.3063 | 0.1787 | 0.0086 |
| F0.5 | **$150,000** | **+0.1990** | **+0.1355** | 0.2325 | 0.0245 | 0.0036 |
| F0.5 | $200,000 | +0.1741 | +0.1614 | 0.1802 | 0.0045 | 0.0018 |
| F0.5 | $300,000 | +0.1234 | +0.1225 | 0.1234 | 0.0000 | 0.0008 |
| F0.5 | $500,000 | +0.0755 | +0.0749 | 0.0755 | 0.0000 | 0.0005 |
| F0.7 | $50,000 | −1.1717 | −1.1819 | 0.1456 | 0.9632 | 0.0058 |
| F0.7 | $75,000 | −0.3316 | −0.7229 | 0.3140 | 0.4720 | 0.0116 |
| F0.7 | $100,000 | +0.0621 | −0.2079 | 0.3065 | 0.1787 | 0.0086 |
| F0.7 | **$150,000** | **+0.1982** | **+0.1331** | 0.2329 | 0.0253 | 0.0036 |
| F0.7 | $200,000 | +0.1744 | +0.1617 | 0.1806 | 0.0045 | 0.0018 |
| F0.7 | $300,000 | +0.1236 | +0.1227 | 0.1236 | 0.0000 | 0.0008 |
| F0.7 | $500,000 | +0.0756 | +0.0751 | 0.0756 | 0.0000 | 0.0005 |

File: `risk_panel/out/part2_capital_frontier.csv`.

### 2.2 Shape (described, per the task's request for a text description alongside the tables)

`J(C)` is **hump-shaped for all three candidates**, peaking at the *same* grid point, **$150,000**,
for CONTROL, F0.5, and F0.7 alike. At $50,000 the account is thin enough that P_ruin is
near-saturated (~96%) and J is deeply negative despite CE_g itself being modest (absorption
destroys most of the raw growth). J crosses zero between $75,000 and $100,000. `CE_g(C)` is
**not** monotone: it is compressed at $50,000 (clipping/absorption), rises to a local high around
$75,000–$100,000, then declines steadily through $150k→$500k as the account becomes progressively
less levered and CE_g converges toward the un-levered arithmetic return rate. `P_ruin(C)` is
monotone decreasing, from ~96% at $50k to exactly 0 in the pooled bootstrap sample (no breaches
observed in ~6,000 pooled paths at $300k/$500k — report as "<1-in-~6,000 in this sample", not as
literally impossible). This qualitative shape (interior maximum, driven by the ruin penalty
dominating at thin capital and CE_g's own decline dominating at thick capital) is the same
qualitative shape as the house's own prior leverage-grid finding in `O1_OBJECTIVE.md` §5.4 (there
peaking near L=0.5, i.e. C≈$200k in that document's own reparametrization) — consistent, not
identical, as expected given a different underlying series and a different (repaired) λ
convention between v1 and v2.

### 2.3 Does the ranking flip? — NO, on the primary shared grid; the F0.5-vs-F0.7 order does wobble slightly (immaterial)

At **every one of the 7 grid points**, under **both** aggregation conventions (mixture J and
Γ-minimax J_worst), **CONTROL scores strictly below both F0.5 and F0.7** — e.g. at $100,000:
CONTROL J=0.0594/J_worst=−0.2146 vs F0.5 J=0.0620/J_worst=−0.2007 vs F0.7 J=0.0621/J_worst=−0.2079.
**No ranking flip for candidate-vs-control across the capital grid.** This generalizes O2's own
$100k-only finding (`Δ J mixture/Γ-minimax both positive vs control`) to the entire preregistered
frontier. **Caveat, stated plainly**: the CONTROL-vs-candidate gaps (~0.002–0.003 in J at most
points) are **smaller than the single-point Monte-Carlo SE** (mc_se≈0.0086 at $100k) — no single
grid point is individually statistically distinguishable from noise. What is being reported is the
**consistency of direction across all 7 paired grid points** (same seed ⇒ same underlying
bootstrap draws compared across candidates at every capital level), which is suggestive but is
**not** a formal significance test on the delta. Between F0.5 and F0.7 the ordering is *not*
always consistent (F0.5 edges ahead at $150k; F0.7 usually ahead elsewhere) — expected and
unconcerning, since `spec.yaml` itself declares "F0.5/F0.7 have NO declared primary between them —
a frozen 2-cell plateau."

### 2.4 Alternative capital normalization — explicit disagreement, reported per directive instruction

**(a) Equal historical stressed-DD fraction** — capital such that each candidate's OWN certified
canonical maxDD_eod is exactly 25% of capital (`ruin_dd_frac`'s own convention), computed
individually per candidate:

| candidate | own maxDD_eod | capital (own maxDD/0.25) | J | J_worst | P_ruin |
|---|---:|---:|---:|---:|---:|
| CONTROL | $17,069.90 | $68,279.60 | −0.5342 | −0.8743 | 0.6068 |
| **F0.5** | $17,390.80 | $69,563.20 | **−0.4994 (best)** | −0.8387 | 0.5847 |
| F0.7 | $16,977.30 | $67,909.20 | **−0.5385 (worst)** | −0.8726 | 0.6112 |

**Disagreement, stated explicitly (per the directive's repeated instruction not to pick whichever
convention flatters a candidate):** under the **shared** $50k–$500k grid (§2.1/2.3), **F0.7
dominates CONTROL at every point**. Under this **individualized equal-DD-fraction** capital, **F0.7
is WORSE than CONTROL** (J=−0.5385 vs −0.5342). **F0.5 dominates CONTROL under both conventions** —
its ranking does not flip. Mechanically: funding each candidate at its own single-path maxDD/0.25
gives F0.7 the *thinnest* capital of the three (its historical maxDD happens to be smallest), and
a slightly worse bootstrapped tail at that thinner funding level is enough to overturn its
shared-grid advantage. All three equal-DD-fraction capitals (~$68k–$70k) land deeply negative in J
regardless of candidate — consistent with the house's own standing finding in
`research/system_master/DRAWDOWN_FRONTIER.md` ("the historical maxDD is one realized path;
resampled paths breach $25k with ≥14% probability per 2y window" — i.e. the bootstrapped tail is
routinely much worse than the single realized path, so funding exactly at the single path's own
maxDD/0.25 is thin under resampling for every candidate, not specific to U6B).

**Scope note**: only one alternative normalization was built (of the "1-2" the task allowed), given
time budget; a second (e.g. per-candidate capital-map-implied capital) was not attempted here.
**LIMITATION.**

File: `risk_panel/out/part2_alt_normalization_equalDDfrac.csv`.

### 2.5 Product B context (optional, explicitly NOT a promotion comparison — different risk scale)

Same shared grid, Product B's own certified daily series (`U0_UNIFIED_STATE`'s
`bar_pnl_B_{nq,mnq}_dollars`, canonical ≤2026-05-31 per O2's own construction pattern):

| candidate | $100k | $150k | $200k | $300k | $500k |
|---|---:|---:|---:|---:|---:|
| ProductB_NQ, J | −1.1502 | −0.6824 | −0.1923 | +0.1306 | +0.1226 |
| ProductB_NQ, P_ruin | 0.9472 | 0.6600 | 0.3143 | 0.0473 | 0.0010 |
| ProductB_MNQ, J | +0.0602 | +0.0405 | +0.0306 | +0.0205 | +0.0123 |
| ProductB_MNQ, P_ruin | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |

Reproduces O2's own finding: Product B-NQ only turns clearly positive/low-ruin around
$300k–$500k (its own risk scale is far larger than $100k, a capital-mismatch artifact, not
evidence the strategy is broken); Product B-MNQ is clean (positive J, ~0 P_ruin) throughout.
**Caveat repeated**: this is context only, not comparable to U6B's own promotion status — Product
A/B are different products with different risk scales. File:
`risk_panel/out/part2_context_productB_frontier.csv`.

---

## PART 3 — Intraday drawdown / ruin (directive sec7)

**Resolution honesty (stated once, applies everywhere below):** this campaign's execution
granularity is **3-minute bars**, not tick data. "Intraday" below means bar-level (3-min)
within-session excursion, not true tick-by-tick equity. The continuous equity path used for
bar-level FACTs is `cumsum(bar_pnl)` over all canonical bars in time order — positions are forced
flat at every session close (per this campaign's own convention), so no additional overnight
excursion risk is hidden by that construction. Built by re-instrumenting
`02_genuine_mnq_repricing.py`'s own decision loop **verbatim** (same M_a/tgt/quality/step_mag/C4
formulas byte-for-byte) to additionally retain the full per-bar array —
`risk_panel/src/01_bar_level_construction.py`, correctness-gated (reproduces the certified
canonical genuine-MNQ nets exactly for all three candidates; intraday MTM reconciles to daily net
at 0.0 max abs diff).

### 3.1 Direct (single-path, FACT) statistics

| | CONTROL | F0.5 | F0.7 |
|---|---:|---:|---:|
| maxDD_eod ($) | 17,069.90 | 17,390.80 | 16,977.30 |
| — matches `u6b_mnq_grid_battery.csv`? | ✓ exact | ✓ exact | ✓ exact |
| CDaR95_eod ($, own recomputation) | 14,254.11 | 14,217.43 | 14,187.36 |
| — matches battery CDaR95 column? | ✓ exact | ✓ exact | ✓ exact |
| worst session ($) | −7,405.60 | −7,405.60 | −7,405.60 |
| — matches directive-stated −$7,405.60? | ✓ | ✓ | ✓ |
| **maxDD, bar-level (3-min, continuous path)** | **32,853.0** | **32,645.7** | **32,578.7** |
| bar-level / EOD maxDD ratio | 1.925× | 1.877× | 1.919× |
| when (all 3 candidates, same session) | 2025-07-30 15:51 ET | same | same |
| CDaR95, bar-level naive ($) | 26,157.02 | 25,990.59 | 25,946.43 |
| CDaR95, bar-level freq.-matched ($) | 27,055.77 | 26,879.64 | 26,833.40 |
| matched CDaR / EOD CDaR ratio | 1.898× | 1.891× | 1.891× |
| worst intraday (bar-level) excursion ($) | 32,853.0 | 32,645.7 | 32,578.7 |

**FACT.** Bar-level intraday drawdown is ~1.88×–1.93× the EOD-only figure, and bar-level
frequency-matched CDaR is ~1.89×–1.90× the EOD figure — both single-path measurements, no
resampling, on this specific realized history. All three candidates' worst bar-level excursion
occurred on the *same calendar session* (2025-07-30), consistent with the rate limiter only
occasionally altering which bars are scale-ups.

**Time-under-water / recovery-time (EOD equity, sessions), FACT:**

| | CONTROL | F0.5 | F0.7 |
|---|---:|---:|---:|
| n drawdown episodes | 73 | 72 | 72 |
| still open (censored) at series end | 1 | 1 | 1 |
| time-under-water: mean / median / p90 / max | 14.1 / 5.0 / 32.6 / 133 | 14.4 / 4.5 / 34.9 / 133 | 14.4 / 4.5 / 34.2 / 133 |
| recovery time (uncensored): mean / median / p90 / max | 7.2 / 2.0 / 16.0 / **112** | 6.4 / 2.0 / 16.0 / 56 | 6.6 / 2.0 / 16.0 / 56 |

CONTROL's single longest recovery episode (112 sessions) is roughly 2× F0.5/F0.7's longest (56
sessions) — one specific episode, not a general pattern (means/medians/p90 are all close across
the three). Files: `risk_panel/out/part3_direct_stats_summary.csv`,
`risk_panel/out/part3_drawdown_episodes.json` (full per-episode detail), computed by
`risk_panel/src/03_direct_stats.py`.

### 3.2 Capital-dependent intraday-vs-daily ruin (INFERENCE, bootstrap, full $50k–$500k grid, R1=25%)

`primary_objective_v2.primary_objective(..., intraday_path=<bar-level parquet>, ...)` — reuses
PO2's own machinery exactly, no separate bootstrap; run 21× (3 candidates × 7 capitals), ~30s each
(~10.5 min total, log at `risk_panel/out/part3_sweep_log.txt`).

| capital | P_ruin daily (mixture) | P_ruin intraday (mixture) | gap (abs) | gap material? | matched CDaR ratio (mixture) |
|---:|---:|---:|---:|---|---:|
| $50,000 | 0.9637 | 0.9913 | +0.0277 | **YES** | 1.148 |
| $75,000 | 0.4748 | 0.7420 | +0.2672 | **YES** | 1.176 |
| $100,000 | 0.1797 | 0.3460 | +0.1663 | **YES** | 1.192 |
| $150,000 | 0.0255 | 0.0417 | +0.0162 | **YES** (rel. bar) | 1.211 |
| $200,000 | 0.0052 | 0.0078 | +0.0027 | **YES** (rel. bar) | 1.221 |
| $300,000 | 0.0000 | 0.0002 | +0.0002 | no | 1.231 |
| $500,000 | 0.0000 | 0.0000 | +0.0000 | no | 1.240 |

(CONTROL row shown; F0.5/F0.7 track within ±0.003 of CONTROL at every capital — same qualitative
pattern for all three, full table in `risk_panel/out/part3_sweepA_intraday_capital_grid.csv`.)
**Pre-registered materiality bars**: P_ruin gap ≥0.02 abs OR ≥20% rel → **material at $50k–$200k**,
immaterial at $300k/$500k (both effectively zero). CDaR matched ratio ≥1.20 → **material from
$150k upward**, just under the bar at $50k–$100k. **The two bars disagree on where the intraday
gap "starts mattering"**: the P_ruin-gap bar fires hardest in the mid-grid ($75k–$150k, where
P_ruin itself is neither ~0 nor ~1); the CDaR-ratio bar fires more at the thick end of the grid.
Both are reported, neither is suppressed.

`J_intraday` tracks `J_daily`'s ranking (CONTROL dominated by F0.5/F0.7) at every capital except
one immaterial, sub-noise exception: at $50,000, F0.5's J_intraday (−1.274719) is marginally
*below* CONTROL's (−1.274436) — a difference of 0.0003, both deeply negative/saturated at this
thinnest grid point; not treated as a genuine flip.

### 3.3 Empirical margin-to-ruin distance (FACT, no bootstrap, same capital grid)

`headroom = capital − realized worst drawdown`; `consumed_fraction = realized worst drawdown / capital`.

| capital | EOD maxDD consumed (CONTROL) | bar-level maxDD consumed (CONTROL) | bar-level consumed (F0.5) | bar-level consumed (F0.7) |
|---:|---:|---:|---:|---:|
| $50,000 | 34.1% | **65.7%** | 65.3% | 65.2% |
| $75,000 | 22.8% | **43.8%** | 43.5% | 43.4% |
| **$100,000** | 17.1% | **32.9%** ⚠ | 32.6% ⚠ | 32.6% ⚠ |
| $150,000 | 11.4% | **21.9%** | 21.8% | 21.7% |
| $200,000 | 8.5% | 16.4% | 16.3% | 16.3% |
| $300,000 | 5.7% | 11.0% | 10.9% | 10.9% |
| $500,000 | 3.4% | 6.6% | 6.5% | 6.5% |

**FACT, headline of this section**: at the **$100,000 headline capital, the single realized
(non-resampled) worst bar-level intraday drawdown alone already consumes 32.6%–32.9% of
capital — past the pre-registered 25% ruin threshold, with zero bootstrapping involved.** At
$150,000 the realized bar-level maxDD (21.7%–21.9%) stays *under* 25% — but §3.2's bootstrap still
reads a non-trivial ~4.1%–4.2% intraday P_ruin there, because resampling explores session orderings
worse than the one that actually happened. Full table per candidate:
`risk_panel/out/part3_margin_to_ruin_{CONTROL,F0.5,F0.7}.csv`.

### 3.4 Crossing-fraction probabilities (INFERENCE, daily-close, 2 representative capitals)

`ruin_dd_frac` override on the same `primary_objective` call (reuses the identical machinery, just
a different absorbing threshold) — $100,000 (headline) and $150,000 (near the house capital-map's
own $115k–$212k band from Part 1). All three candidates track within ~0.5pp of each other.

| capital | P(cross 10% of capital) | P(cross 20%) | P(cross 30%) |
|---:|---:|---:|---:|
| $100,000 | 99.85% | 41.1%–41.3% | 7.0%–7.2% |
| $150,000 | 85.5%–87.8% | 8.7%–8.8% | 0.83% |

File: `risk_panel/out/part3_sweepB_crossing_fractions.csv`.

---

## Integrity / correctness gates (all PASS)

- Bar-level reconstruction reproduces certified canonical genuine-MNQ nets exactly for all three
  candidates (CONTROL $178,687.40, F0.5 $178,988.70, F0.7 $179,302.30).
- Intraday cumulative-MTM reconciles to session daily net at 0.0 max abs diff (all 3 candidates);
  PO2's own internal `intraday_vs_daily_sessionend_maxabs_logdiff` check ≈1e-17 (float-precision
  zero) on every one of the 21 capital-dependent calls.
- Zero equity-nonpositive clippings at any grid point, including the thinnest ($50,000).
- Only warning raised anywhere: "truncated 45 post-dev sessions (>2026-05-29) — dev window only"
  — i.e. `primary_objective_v2`'s own `dev_window="truncate"` correctly drops the June–July-2026
  health-only extension automatically; the extension is never blended into any figure above.
- No data on/after 2026-08-01 read anywhere (asserted in code; `HEALTH_END=2026-07-31` upstream).

## Disclosed scope limitations (LIMITATION)

1. Bar-level (intraday) bootstrap was run at the R1=25% threshold across the **full** capital
   grid (21 calls). The 10%/20%/30% crossing-fraction sweep (§3.4) was run **daily-close only**,
   at 2 representative capitals, for tractability — not extended to bar-level at every
   (capital, threshold) combination (would be ~18 more ~30s calls).
2. Only one alternative capital normalization (§2.4a) was built, of the "1-2" the task allowed.
3. `n_boot=2000`, `seed=20260808` (house defaults) used throughout — no reduction, but also no
   increase; Monte-Carlo SEs are reported (§2.1) and are non-trivial relative to the
   candidate-vs-control gaps at single grid points (§2.3).
4. λ (ruin penalty) is a preference parameter, held at its module-derived value throughout
   (`≈1.3677/yr`, fixed-fraction convention) — not re-swept here; the λ-grid sensitivity already
   exists in `O1_OBJECTIVE.md` and was not re-run per capital level in this panel.
5. The v1f Product-A capital map cited in Part 1(a) was built on a related but not bit-identical
   series to U6B's own CONTROL — used as context/range justification only, not as U6B's own map.

## Reproduce

```
cd "D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
python runs/U6B_PRODUCT_A_SCALE_RATE/risk_panel/src/01_bar_level_construction.py
python runs/U6B_PRODUCT_A_SCALE_RATE/risk_panel/src/02_capital_frontier.py
python runs/U6B_PRODUCT_A_SCALE_RATE/risk_panel/src/03_direct_stats.py
python runs/U6B_PRODUCT_A_SCALE_RATE/risk_panel/src/04_capital_dependent_risk.py   # ~11 min
```

## File manifest

`runs/U6B_PRODUCT_A_SCALE_RATE/risk_panel/`:
- `src/01_bar_level_construction.py` — bar-level (3-min) equity reconstruction, genuine MNQ, all 3 candidates
- `src/02_capital_frontier.py` — Part 1 audit + Part 2 capital frontier (leverage_curve reuse)
- `src/03_direct_stats.py` — Part 3 direct/FACT statistics (EOD & bar-level DD/CDaR, TUW, recovery)
- `src/04_capital_dependent_risk.py` — Part 3 capital-dependent bootstrap sweeps (intraday P_ruin, crossing fractions)
- `out/{CONTROL,F0.5,F0.7}_barlevel_GENUINE_MNQ_{canonical,extension}.parquet` — bar-level equity series
- `out/part1_audit.json`, `out/part2_capital_frontier.csv`, `out/part2_alt_normalization_equalDDfrac.csv`, `out/part2_context_productB_frontier.csv`
- `out/part3_direct_stats_summary.csv`, `out/part3_drawdown_episodes.json`, `out/part3_margin_to_ruin_{CONTROL,F0.5,F0.7}.csv`
- `out/part3_sweepA_intraday_capital_grid.csv`, `out/part3_sweepB_crossing_fractions.csv`, `out/part3_full_result_<candidate>_C<capital>.json` (21 files, full PO2 output per grid point), `out/part3_sweep_log.txt`
- `out/barlevel_construction_summary.csv`
