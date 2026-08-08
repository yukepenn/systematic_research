# SMV2W_5MCLOCK_R2 — 5m time-matched clock R2 confirmation (seq 395)

Run dir: `runs/SMV2W_5MCLOCK_R2` | Spec: `runs/SMV2W_5MCLOCK_R2/spec.yaml` (committed
7abeb79 before any read/execution). Parent: SMV2U seq 391 arm "5m_time_matched"
(VolPeriod=276 5m bars) — the only one of four clock-challenger arms to beat the 3m
incumbent standalone AND at the raw-arm portfolio level in SMV2U's R1 screen (Sharpe
0.793 vs 0.709; CDaR $22,521 vs $27,162; portfolio Sharpe 1.156 vs 1.120, CDaR $17,922
vs $19,299; LOYO 5/5; friction_share 0.211 < incumbent's 0.326). DISCLOSED PRIOR — the
house replacement bar is applied here exactly as SMV2T/SMV2S applied it, no lowering.

Object under test: the 5m-clock 13-member ensemble (VolPeriod=276, SMinTicks=40,
SMaxTicks=1200, E10 executor `tgt=clip(rha(10*mean pending),±10)`, MNQ costs, session
flatten) **AND** its DUAL_HTF-transformed + portfolio-composed decision object (tilt
×1.25/c1_50/×0.9026/clip13, then 60/40 vs frozen BMOM E2, same vm/rerank construction as
the incumbent champion). No data ≥ 2026-08-01 read anywhere; dev = sessions ≤
2026-05-31 (1,139 sessions, 2022-01-03 → 2026-05-29). Every number below is from an
artifact in `out/`.

**BOTTOM LINE (FACT): 2 of 4 AVAILABLE gates FAIL (A, B); Gate C is BLOCKED-BY-DATA
(unanimous A/B/D/E required, not met). Per the frozen decision rule ("pass all
AVAILABLE gates → CHAMPION-CANDIDATE; fail any available gate → incumbent retained,
lead closed"), the 5m time-matched clock does NOT become CHAMPION-CANDIDATE. The 3m
incumbent clock is retained. This R2 lead is CLOSED (one attempt per lead, per spec).**

---

## Step 0 — reproduction gate (out/step0_repro_gate.csv, step0_verify.json) — **PASS**

Per CODE MAP instruction, SMV2U's step0 5m-bar substrate (`bars_5m_dev.parquet`,
already session-calendar-matched to the 3m incumbent's NT8-authoritative calendar) was
REUSED, not rebuilt. The 13-member V3 ensemble (`sm01_solarsim.member_states` /
`member_trades`, verbatim) was rebuilt on those bars at VolPeriod=276, exactly
reproducing SMV2U step1's CONFIGS entry `("5m", bars5, "time_matched", 276)`.

- FACT: **10/10 checked fields match SMV2U's committed `out/clock_arms.csv` row
  `5m_time_matched` EXACTLY** (net $136,527.20, Sharpe 0.792645, max_dd −$28,603.70,
  CDaR5 $22,521.04, 1,139 sessions, 311,849 bars, 22,345 target changes, 31,682
  contracts traded, friction_share 0.210650, VolPeriod 276) — all `abs_dev = 0`
  except friction_share at 5.6e-17 (float rounding noise).
- FACT: the rebuilt daily curve matches SMV2U's saved `daily_curves.csv` column
  `5m_time_matched` to **max|dev| = 1.8e-12 $** over all 1,139 dev sessions.
- FACT: the 5m core's session calendar is identical, session-for-session, to the 3m
  incumbent's 1,139-session dev calendar (verified by list equality, not just count).
- **Repro gate: PASS.** Proceeding to build on this object is licensed.

## DUAL_HTF transform construction (out/curves.csv, step1_dual_htf_verify.json)

Applied exactly as `runs/SMV2H_ONECONTRACT/smv2h.py` builds DUAL_HTF: `agree =
sign(T)≠0 & st_bar==sign(T)`; tilt ×1.25 on agreement; c1_50 (short half-weight iff
HTF-up); ×0.9026; `clip(rha(·), ±13)`; HTF = prior-session close vs SMA50 of session
closes (causal, `.shift(1)`), computed from the 3m bars' session-close series. Applied
to the 5m core's T (13 members, clip ±10, VolPeriod=276) to build the **NEW DUAL_5M
challenger leg** — this is a genuinely fresh construction this wave, not a reused
number. The incumbent DUAL_ALL (3m) leg was REUSED from the already-committed,
already-verified object, not recomputed from scratch as a "new" number.

Three independent integrity checks, all PASS exactly:
- FACT: session close prices agree between the 3m bar file and the 5m bar file on all
  1,139 dev sessions, **max|dev| = 0.0** — the HTF state (a session-level quantity) is
  clock-invariant by construction, confirmed rather than assumed.
- FACT: the reconstructed **DUAL_ALL** target series (rebuilt here independently via
  `dual_htf()`) matches SMV2H2 gate A's saved `tdd_dev_from_tgt.npy`
  **bit-for-bit on all 519,714 dev bars**.
- FACT: the executed **DUAL_ALL** daily curve matches `rerank.py`'s saved
  `solar_dual_htf_daily.csv` to **max|dev| = 1.8e-12 $** over all 1,139 sessions.

These three checks confirm the DUAL transform pipeline and executor used for the new
DUAL_5M leg are identical to the prior wave's on the reference side — the comparison
below is apples-to-apples. `net(DUAL_ALL) = $138,280.0`, `net(DUAL_5M) = $152,668.6`.

---

## Gate A — dev paired bootstrap on the DUAL-transformed legs (out/gate_A.csv) — **FAIL**

House bootstrap: paired moving-block, block=5, B=10,000, seed=20260808, circular index
construction, on daily diffs of DUAL_5M − DUAL_ALL over all 1,139 dev sessions (k=56
worst days for CDaR_0.95).

| | DUAL_ALL (incumbent) | DUAL_5M (challenger) | point delta |
|---|---|---|---|
| net $ | 138,280.0 | 152,668.6 | +14,388.6 |
| Sharpe | 0.899 | 0.969 | +0.070 |
| CDaR_0.95 $ | 20,447.5 | 14,893.1 | +5,554.4 (improvement) |

- FACT: point estimates favor the 5m DUAL leg on every statistic (net, Sharpe, CDaR).
- FACT: bootstrap significance — **P(dSharpe>0) = 0.642** (well under the 0.85 bar) and
  **P(dCDaR>0) = 0.549** (well under 0.85). **Gate A FAILS both prongs.**
- INFERENCE: unlike SMV2U's R1 screen (which used point comparisons only), the house
  bootstrap bar is materially harder to clear — the 5m clock's edge over the 3m
  incumbent, though positive on every point estimate at both the standalone and
  DUAL-transformed level, is not statistically resolved under paired resampling. The 5%
  quantile of the Sharpe delta is −0.248 and of the CDaR delta is −$15,218, i.e. a
  nontrivial share of resampled paths show the challenger materially worse on both axes.

## Gate B — chronology (out/gate_B.csv, gate_B_loyo.csv, gate_B_fit_eval.csv) — **FAIL**

Per-year dSharpe = Sharpe(DUAL_5M) − Sharpe(DUAL_ALL), 5 calendar years present in dev:

| year | d_net $ | d_sharpe | sign |
|---|---|---|---|
| 2022 | −1,887.0 | −0.032 | − |
| 2023 | −2,502.9 | −0.069 | − |
| 2024 | +5,354.7 | +0.212 | + |
| 2025 | +5,786.1 | +0.015 | + |
| 2026 (partial, Jan–May) | +7,637.7 | +0.375 | + |

- FACT: only **3/5 years share the same (positive) sign** — below the "≥4/5" LOYO bar.
  (Note this differs from SMV2U's R1 read, which reported "LOYO 5/5 sign-stable" on a
  leave-one-year-out sign-stability construction on the RAW arm; this gate's per-year
  breakdown on the DUAL-transformed object is a different, harder test, per spec, and
  is genuinely unseen — not pre-committed by the R1 number.)
- FACT: fit window (2022–2024) dSharpe +0.037, dNet +$964.8; eval window (2025–2026)
  dSharpe **+0.123** (point-positive), dNet **+$13,423.8** (point-positive) — this half
  of gate B passes.
- **Gate B FAILS overall** (both prongs AND-required; LOYO 3/5 is dispositive).

## Gate C — old-regime (2006–2021) — **BLOCKED-BY-DATA**

Per spec's own contingency, first determined honestly whether a 5m-equivalent hist
series is causally derivable from the **committed** SM06 hist substrate
(`out/gate_C_determination.json`, reading `runs/SM06_SOLAR_HISTORY/run_hist.py` and the
committed `vote_state_3m_hist.parquet` directly, not just asserting the spec text):

- FACT: the committed hist substrate's own bar spacing mode is **180.0 seconds (3
  minutes)**, built via `sm.resample_3m(h)` directly from the raw 1-minute hist file,
  and stores **aggregate-only** `vote_pos`/`vote_pend` columns — no per-member columns
  (`has_per_member_cols = False`, confirmed by column inspection, corroborating
  SMV2T gate_C.py's own independent finding on the same file).
- **Reason 1 (structural):** a 3-minute OHLC bar is a lossy aggregate of the 1-minute
  path inside it; 5-minute bar boundaries do not align with 3-minute bar boundaries (3
  and 5 share no common sub-multiple), so 5-minute OHLC cannot be reconstructed from
  3-minute OHLC by any bar-merging operation on the committed file. A 5m-equivalent
  series is **not** causally derivable from the committed 3m hist substrate.
- **Reason 2 (scope, independent of reason 1):** this run's OWN `spec.yaml` "data"
  field authorizes exactly one substrate — `runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.
  parquet` (2022–2026, dev ≤ 2026-05-31) aggregated to 5m. It does not authorize the
  separate pre-2022 raw file
  (`research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet`) that SM06's
  own build (and SMV2T's gate C, under SMV2T's own different, explicitly-scoped spec)
  used. Reaching past this spec's declared data to build a brand-new hist-period 5m
  ensemble from that raw file would be improvising data/scope beyond the frozen spec —
  not performed, per the hard rule "never improvise gates/grids/data."
- **Gate C verdict: BLOCKED-BY-DATA**, exactly as spec's contingency describes. Per
  spec: "require unanimous pass on A/B/D/E to proceed" — this condition is **not met**
  (A and B both fail; see below), independent of Gate C's block. The old-regime data
  gap is logged as an open risk: the 5m clock's stress-test behavior in the 2006–2021
  regime is genuinely unknown, neither supporting nor contradicting the challenger.

## Gate D — right-tail retention on the DUAL-transformed dev legs (out/gate_D.csv,
gate_D_top10_detail.csv) — **PASS**

- FACT: DUAL_5M's PnL on DUAL_ALL's own top-10 days = $104,587.3 vs DUAL_ALL's top-10
  sum $113,139.5 → **retention = 92.44%** (≥ 90% required, this spec's bar — note this
  is LOWER than SMV2T's 100% bar; SMV2W's own spec sets 0.90). 7 of the 10 top ALL-days
  are also among DUAL_5M's own top-10 days.
- **Gate D PASSES.**

## Gate E — portfolio rebuild, DAYONLY_DUAL6040 (out/gate_E.csv, gate_E_curves.csv,
gate_E_reconciliation.csv) — **PASS**

**Part 1 — reconciliation (required before trusting the new bootstrap-based gates,
per spec):** rebuilt the RAW (non-DUAL) 5m_time_matched arm's own 60/40 portfolio blend
using SMV2U step1's exact `portfolio_blend()` construction and confirmed it against
SMV2U's committed `out/portfolio_contrib.csv` row `5m_time_matched_portfolio`:

| | mine | SMV2U ref | abs dev |
|---|---|---|---|
| net $ | 199,173.31 | 199,173.31 | 5.8e-11 |
| Sharpe | 1.156354 | 1.156354 | 2.2e-16 |
| CDaR5 $ | 17,921.74 | 17,921.74 | 3.6e-12 |
| maxDD $ | 25,008.99 | 25,008.99 | 2.9e-11 |

- FACT: **RECONCILIATION PASS (4/4 fields exact)** — the raw-leg portfolio
  construction pipeline reproduces SMV2U's committed numbers to floating-point noise.
  The new DUAL-transformed gate E result below is trustworthy.

**Part 2 — the actual gate:** DUAL_5M leg, portfolio-composed via `rerank.py`'s exact
60/40 `vm()` construction (SIG re-derived from DUAL_5M's own std = $2,195.65 vs
incumbent's $2,143.28), compared against the incumbent champion curve
(`rerank_curves.csv` "60_40", cross-checked exactly against `rerank_portfolios.csv`
— net/Sharpe dev both 0.0):

| | incumbent 60/40 (champion) | 5m rebuild 60/40 | point delta |
|---|---|---|---|
| net $ | 194,416.0 | 203,338.0 | +8,922.0 |
| Sharpe | 1.264 | 1.291 | **+0.026 (positive)** |
| CDaR_0.95 $ | 14,322.2 | 13,142.7 | **+1,179.5 (improvement)** |
| maxDD $ | 18,131.7 | 16,831.9 | +1,299.7 (improvement) |

- FACT: dSharpe point-positive, dCDaR point-positive (improvement) — **both prongs
  PASS. Gate E PASSES.**

---

## Decision (spec: "pass all AVAILABLE gates (A/B/D/E; C per its own contingency) →
CHAMPION-CANDIDATE; fail any available gate → incumbent retained, lead closed")

| Gate | Requirement | Result | Verdict |
|---|---|---|---|
| A (dev bootstrap) | P(dSharpe>0)≥0.85 AND P(dCDaR>0)≥0.85 | 0.642 / 0.549 | **FAIL** |
| B (chronology) | LOYO ≥4/5 same sign AND eval 2025-26 point-positive | 3/5 (fail) / +0.123 (pass) | **FAIL** |
| C (old regime) | derivable from committed substrate → rebuild; else BLOCKED | not derivable | **BLOCKED-BY-DATA** |
| D (right tail) | top10 retention ≥0.90 | 0.9244 | PASS |
| E (portfolio) | dSharpe AND dCDaR point-positive | +0.026 / +$1,179.5 (both pass) | PASS |

**2 of 4 available gates fail (A, B). Decision: fail any available gate → 3m incumbent
clock retained.**

The 5m time-matched clock does not become CHAMPION-CANDIDATE. No master rebuild or
parity stage (Stage 4) is triggered; the live master's clock is untouched, as required.
This R2 confirmation lead, opened by SMV2U seq 391's R1 screen, is recorded **CLOSED**:
the point-estimate improvements are real and reproduce cleanly at every level tested
(standalone raw arm, DUAL-transformed standalone, and DUAL-transformed portfolio all
show positive Sharpe and CDaR deltas — Gate E even PASSES outright), but the two places
this wave specifically tested for statistical/chronological robustness — the dev
bootstrap (Gate A) and per-year LOYO sign-stability on the DUAL-transformed object
(Gate B) — do not survive. This is consistent with SMV2T_NOFAST_R2's finding on a
different lead: point-estimate superiority at the R1 screening stage does not
automatically survive the house's harder R2 statistical bar. Per spec, no third bite is
authorized on this same 5m-clock lead without a new mechanism.

## Conventions and caveats

- Dev calendar: 1,139 sessions, 2022-01-03 → 2026-05-29 (sessions ≤ 2026-05-31); no
  data ≥ 2026-08-01 read anywhere (VIRGIN rule respected). Gate C's would-be hist window
  (2006–2021) was never touched — blocked before any hist-period computation.
- All dev gates (A/B/D/E) share one calendar: the same 1,139 sessions, paired,
  identical to the 3m incumbent's own dev calendar (verified by list equality in step0,
  not just count). House bootstrap: block=5, B=10,000, seed=20260808 throughout
  (out/gate_A.csv), matching the run header's house bootstrap convention exactly.
- Every executor and transform step cross-checked bit-for-bit or to sub-cent precision
  against a previously-committed, independently-produced artifact before being used in
  any gate computation: SMV2U's `clock_arms.csv`/`daily_curves.csv` (step0 repro gate,
  10/10 exact), SMV2H2's saved `tdd_dev_from_tgt.npy` (bit-for-bit on 519,714 bars),
  `rerank.py`'s saved `solar_dual_htf_daily.csv` and `rerank_curves.csv`/
  `rerank_portfolios.csv` (Gate E champion reconstruction, net/Sharpe dev = 0.0), and
  SMV2U's `portfolio_contrib.csv` (Gate E Part 1 raw-leg reconciliation, 4/4 exact) —
  see the integrity-check FACTs under each section above.
- Gate D's pass bar in THIS spec is retention ≥ 0.90 — deliberately different from (and
  looser than) SMV2T_NOFAST_R2's ≥ 1.00 bar; both are taken verbatim from each run's own
  frozen spec.yaml, not harmonized after the fact.
- Gate C's BLOCKED-BY-DATA determination rests on two independent grounds (structural
  non-derivability from 3-minute bars, and this spec's own data-field scope); either one
  alone is sufficient. No raw pre-2022 1-minute data was read in producing this report.
