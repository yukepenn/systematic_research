# PLACEBO01 — Component Causality: Four Causal Placebo Tests

**Scope:** falsification science, not an alpha trial (campaign directive sec44-50). Each of the
incumbent's four non-Solar-core components — B-MOM, HTF (`tiltState`), Product-B hysteresis(3,1),
and Product-A's continuous |size| mapping — is tested against a preregistered null distribution
built to isolate what that *specific* component contributes beyond a same-shaped but
uninformed/randomized version of itself. No incumbent code was modified. All four tests wrote their
preregistration (N, seed family, null construction) **before** generating or inspecting any placebo
draw, and all four pass their own internal correctness gate (exact or near-exact reproduction of the
campaign's certified nets) before any placebo replicate is trusted. This report synthesizes the four
already-completed result files; it does not re-run or extend any of them.

**Inputs (all read in full before writing this synthesis):**
`out/bmom_placebo_results.json` (+ `.csv`, `bmom_placebo_preregistration.md`),
`out/htf_placebo_results.json` (+ `.csv`, `htf_placebo_preregistration.json`),
`out/hysteresis_placebo_results.json` (+ `.csv`), `out/sizing_placebo_results.json` (+ `.csv`), plus
a direct re-execution of `src/04_sizing_placebo.py`'s own functions (below) to resolve an internal
tension in the sizing result that its raw JSON left unexplained.

## Headline verdicts

| Component | Null construction (one line) | N / seed family | Real's percentile in null | Verdict |
|---|---|---|---|---|
| B-MOM | circular per-session block shift of the real `bmomPos` path | 500 / `20260810+i` | Net: A=94.2, B=88.8 · Sharpe: A=90.4, B=89.2 · maxDD: A=1.6, B=0.0 (favorable-tail) · turnover: A=100.0, B=15.9 | **MIXED** |
| HTF (`tiltState`) | within-year natural-block reordering of the real `tiltState` chronology | 1000 / `20260810+i` | Net: A=27.8, B=28.8 · Sharpe: A=32.1, B=31.2 | **CONCERNING** |
| Hysteresis(3,1) | turnover/occupancy-matched naive-threshold null with random suppression/extension | 300 / `20260810+i` (calibration pilot: disjoint `9000000+i`) | Sharpe=69.3, Net=78.3, maxDD(favorable dir.)=86.7 | **DIRECTIONALLY FAVORABLE, NOT TAIL-SIGNIFICANT** |
| Product-A sizing | within-stratum permutation of realized \|target_exposure_A\| (direction × session-phase × vol tercile × conviction tercile held fixed) | 500 / `20260810+i` | PnL/contract=100.0 · PnL/exposure-hr=15.2 · marginal gradient=0.0 | **SUBSTANTIALLY A TURNOVER/DENOMINATOR ARTIFACT, one real residual caveat** |

---

## 1. B-MOM — MIXED

**Null construction.** The real, complete per-session `bmomPos` path (`{-1,0,+1}`) is circularly
shifted across the `M=539` canonical-window sessions by a single random offset `K ~
Uniform{1,...,M-1}` per replicate: session at chronological rank `r` receives the intact
within-day path of donor session `(r+K) mod M`, reattached by time-of-day slot (defaulting to flat
where the donor session had already closed early). Because `K≠0`, no session ever receives its own
real path back. This is a bijection on the same multiset of real per-session B-MOM paths already in
the window, so activation frequency, state-duration distribution, and time-of-day/volatility
composition are preserved exactly, not approximately — only which calendar day each session's path
lands on is randomized. The comparison baseline is Solar+HTF-only (`bmomPos≡0`), so the reported
delta isolates B-MOM's own marginal contribution.

**Preregistered N / seed:** 500 replicates, `seed_i = 20260810+i`.

**Result.** Net and Sharpe marginal contributions are **not tail-significant** for either product:
Product A lands at the 94.2nd (net) / 90.4th (Sharpe) percentile, Product B at the 88.8th / 89.2nd —
directionally favorable (above the null median) but below the ~95th-percentile bar this campaign
treats as tail-significant. Turnover for Product A sits at the **100.0th percentile** (real turnover
is above every one of the 500 placebo draws) — a real, structural cost-side caveat: B-MOM's real
activation timing for Product A trades measurably more than a randomly-shuffled-but-same-shaped
B-MOM path would. Drawdown is the strongest result: real B-MOM's marginal effect on `maxDD_eod`
lands in the favorable tail for both products (1.6th percentile for A, 0.0th — i.e. below every
placebo draw — for B, where the marginal maxDD delta is *negative*, meaning B-MOM materially
**reduces** Product B's worst drawdown versus Solar-only, an effect no placebo draw matched).

**Verdict.** MIXED, stated plainly, not oversold: B-MOM shows an extreme, tail-significant
drawdown-timing benefit for Product B specifically, but net-PnL/Sharpe for both products is only
comparable-to-placebo (not tail-significant), and Product A carries a genuine, tail-significant
turnover/cost penalty versus a same-shaped random path. This is "real drawdown-timing value,
unconfirmed profit-timing value, real cost caveat for A" — not "confirmed" and not "falsified."

---

## 2. HTF (`tiltState`) — CONCERNING

**Null construction.** `tiltState` is a session-level quantity (constant across all bars of a
session). Within each calendar year separately (2023, 2024, 2025-stub), the real chronological
`tiltState` sequence is partitioned into its natural blocks (maximal contiguous runs of one value,
boundaries taken from the real data, never a fixed length), the block *order* is randomly permuted
within that year, and the reordered blocks are relaid onto that year's own session-date slots (block
sizes never split/merged/resampled; blocks never cross a year boundary). This preserves the exact
marginal distribution of `tiltState` values, the exact block/run-length distribution at the block
level, and exact year composition — it only breaks the correspondence between a given block and the
calendar dates (and hence real market conditions) it originally occurred on. The same shuffled
realization is applied to both products in a given replicate (one shared HTF-input shuffle, not two
independent draws). Baseline is Solar+BMOM-only (`tiltState≡0`, forcing Product A's `mm=ss=1.0` and
Product B's `mm=1.0`), isolating HTF's own marginal contribution.

**Preregistered N / seed:** 1000 replicates, `seed_i = 20260810+i` — double the other three
components' N, and the preregistration explicitly states the decision rule in advance: "if the real
HTF-overlay's marginal contribution performs no better than the randomized-chronology null (percentile
≤ ~50%), HTF's economic interpretation weakens substantially. This will be reported plainly
regardless of which way it comes out."

**Result.** Real HTF's marginal net contribution sits at the **27.8th percentile** (Product A,
$5,967 real vs. null mean $9,827) and the **28.8th percentile** (Product B, $9,148 real vs. null mean
$14,904); Sharpe marginal contribution sits at the 32.1st (A) and 31.2nd (B) percentiles. **Both
products, on both headline metrics, sit below the null median** — a randomly-time-shuffled HTF state
(same marginal distribution, same within-year block-run structure, wrong calendar alignment) would,
on average, have added *more* net PnL and Sharpe than the real, correctly-time-aligned HTF state
actually did.

**Verdict.** CONCERNING, stated plainly — this is exactly the scenario the preregistration explicitly
anticipated and flagged in advance as the falsification-relevant outcome, not a post-hoc
reinterpretation. HTF's marginal net/Sharpe contribution performs **no better than** a randomized
version of its own chronology for either product; its economic interpretation as a genuine
directional-timing signal weakens substantially on this evidence.

---

## 3. Product-B hysteresis(3.0,1.0) — directionally favorable, not tail-significant

**Null construction.** Not a naive shuffle: a "naive zero-hysteresis" baseline (`sign(M)`, no dead
zone, same forceFlat/entryBlocked gates as real) is given two free parameters — `p_exit` (random
chance of suppressing what would otherwise be a discretionary exit) and `p_accept` (random chance of
accepting a would-be entry), plus dwell lengths bootstrap-sampled from the real system's own observed
non-forced flat-dwell-run-length distribution. `(p_exit, p_accept) = (0.45, 0.5)` was selected by a
110-point grid search calibrated **only** to match the real system's own discretionary-event count
(1511) and occupancy (0.355) — the calibration objective never touches PnL, Sharpe, or drawdown,
disclosed explicitly to avoid circularity. This produces a null that churns/occupies the market at
matched turnover to the real hysteresis(3,1) rule but with no informed threshold logic — the
comparison this test is built to make is "does the *specific* 3.0/1.0 threshold choice add value
over a generic, turnover-matched churn-reducer," not "does hysteresis beat zero-hysteresis" (the
latter is reported only as uncalibrated context: naive zero-hysteresis alone nets $111,374 vs. real's
$83,363, but at 2.3x the turnover and no calibration — not the tested null).

**Preregistered N / seed:** 300 scored replicates, `seed_i = 20260810+i`; calibration used a disjoint
15-seed pilot family (`9000000+i`), never overlapping the scored seeds.

**Result.** Real hysteresis(3,1)'s Sharpe sits at the **69.3rd percentile**, net at the **78.3rd
percentile**, and maxDD at the **86.7th percentile** (favorable direction) of the 300 turnover-matched
nulls. Real beats the null median on all three; none clears the preregistered ≥95th-percentile
tail-significance bar, and none falls below the 5th-percentile underperformance bar either.

**Verdict.** Reassuring but not decisive — not a clean pass. The specific 3.0/1.0 entry/exit
construction beats the median of a generic, matched-turnover churn-reducer on Sharpe/net/DD alike,
suggesting the particular threshold choice (not merely "reducing churn somehow") contributes real
value, but the margin does not reach statistical tail-significance at this N.

---

## 4. Product-A sizing — resolved: substantially a turnover/denominator artifact, with one real residual caveat

**Null construction.** Within each of 126 populated (direction × session-phase × volatility-tercile ×
Solar-conviction-tercile) strata, the real |target_exposure_A| values observed at bars in that
stratum are independently permuted (uniform random permutation) across those same bars — direction
and bar timing untouched, only the size *label* reshuffled among bars that already share direction,
session-phase, vol regime, and conviction regime. This exactly preserves the global (and per-stratum)
histogram of |target_exposure_A| by construction (a bijection), while breaking the pairing of "this
bar's chosen size" to "this bar's realized outcome" beyond what the coarse stratum already controls
for.

**Preregistered N / seed:** 500 replicates, `seed_i = 20260810+i`.

**Raw result (as it appeared in the JSON, unresolved):** real PnL/contract sits at the **100.0th
percentile** ($4.836 vs. null mean $0.487 — real beats all 500 draws), real PnL/exposure-hour sits at
the **15.2nd percentile** (real below most draws), and real's marginal-exposure-value gradient sits
at the **0.0th percentile** (0.074 vs. null mean 0.334 — real below *every* draw). Taken at face
value this reads as an internal contradiction (dramatically better on one metric, dramatically worse
on two others) and the prior draft mislabeled it `INDISTINGUISHABLE_FROM_PLACEBO`, which understates
what the data actually shows.

**Investigation and resolution (this session, verified with direct computation against the real
data and re-execution of the placebo script's own functions, not speculation):**

- **`exposure_hours` (total position-hours deployed) is mathematically identical between the real
  system and all 500 null replicates** — 53,636.9 in every single case (std = 1.5e-11, floating-point
  noise only). This is a structural necessity of the within-stratum bijective permutation: it
  preserves the *sum* of |size| exactly, so total exposure deployed cannot differ between real and
  any null draw. This means `pnl_per_exposure_hour`'s percentile (15.2) is, mechanically, nothing
  more than a percentile of **net PnL for a fixed, identical exposure budget** — a clean,
  apples-to-apples comparison, not confounded by turnover.
- **`contracts_traded` (turnover) explodes 11.4x under the null**: real = 36,794; null mean =
  420,218 (range 418,432–422,454 — real sits far *below the entire null range*, not just below the
  mean). This confirms hypothesis (a): real Product A's smooth, autocorrelated scale-in/scale-out
  produces vastly fewer round-trip contracts per unit of exposure than a within-stratum random
  reassignment, which destroys that autocorrelation and re-trades on nearly every bar. Since null net
  PnL averages only **15% higher** than real ($204,548 vs. $177,924) while contracts_traded is
  **11.4x** higher, `pnl_per_contract`'s 100th-percentile result is overwhelmingly a turnover-
  efficiency artifact of real Product A's smoothness, not evidence that its specific size choices are
  more profitable in raw-dollar terms — if anything the null's raw net PnL is *higher* on average for
  the same exposure.
- **Instrumented re-execution** (splitting bars by whether the bar was a fresh trade vs. a held
  position) shows only **3–13%** of real Product-A's size-`k` bars (k≥2) are freshly-traded bars vs.
  **61–96%** of size-`k` bars in a representative null replicate — a 7–9x composition shift. The
  metric's own disclosed caveat ("bar_pnl on a bar where the position changed mixes the markout of
  pre-existing and newly-added contracts... APPROXIMATE") is empirically confirmed to bite hard here:
  trade-bar and hold-bar unit-PnL-by-k patterns are materially different quantities. Recomputing the
  WLS gradient on **real Product A's own trade-bars only** (the same bar-composition regime that
  dominates the null) gives **0.375** — at or above the null's mean (0.334) and near its p90–p95 —
  while real's hold-bars-only gradient is 0.062 (close to the full-sample 0.074, since real is
  hold-dominated). This directly confirms hypothesis (b): the 0th-percentile aggregate gradient
  result is driven by a composition mismatch (real's aggregate is ~95% steady-state holding bars,
  mechanically flatter; the null's aggregate is ~75% fresh-entry bars, mechanically steeper), not by
  real's actual within-stratum size choices being anti-aligned with profitability. On a like-for-like
  (trade-bar) basis, real is competitive with the null on this metric too.

**Conclusion (high confidence for the artifact finding, moderate confidence on the residual
caveat):** the 100th-percentile PnL/contract and 0th-percentile marginal-gradient results are
**substantially artifacts of a turnover/bar-composition confound in the null construction**, not
apples-to-apples evidence that real sizing is worse than random at matching size to circumstance.
However, one real, non-artifactual, mildly unflattering signal survives and should not be swept
away by the artifact explanation: **`pnl_per_exposure_hour` at the 15.2nd percentile is a clean,
denominator-matched comparison** (exposure_hours is literally identical across all draws) showing
that, holding total exposure fixed, 84.8% of stratum-matched random size reassignments produced more
net profit than Product A's actual smooth allocation. This is directionally unfavorable and worth
disclosing, though it does not reach the 5th-percentile tail-significance threshold that would make
it a strong claim on its own.

---

## Cross-cutting governance notes (per campaign directive sec44/sec50)

- **This diagnostic does not by itself justify removing any component.** Per sec50/sec43, a
  component may earn its place through tail-risk or regime-defense value even where its average
  placebo-beating margin is modest or absent — B-MOM's tail-significant Product-B drawdown reduction
  despite comparable-to-placebo net/Sharpe is a live example of exactly this pattern within this same
  report. Final removal decisions for any of these four components belong to a future SIMPLE01
  minimum-system-ladder task, not to this report.
- **This is falsification-first evidence, not the final word (sec44).** These are causal *nulls* —
  each test asks whether a component beats a specific, disclosed randomization of itself — not proof
  of the absence of value. A component that lands near or below its null median here (HTF; the
  sizing gradient before artifact-correction) has failed to *demonstrate* the specific causal
  mechanism this test targeted; it has not been proven valueless, and no incumbent code has been
  changed as a result of this report.
- All four incumbent NinjaScript components (`SolarWaveSMMaster_v4`, `SolarWaveOneContractNQ_v5`)
  remain unmodified. No orders, deployments, connections, or licensed vendor assemblies were touched
  in the course of this task.

## Artifacts

- B-MOM: `src/01_bmom_placebo.py` → `out/bmom_placebo_results.json` (+`.csv`),
  `out/bmom_placebo_preregistration.md`
- HTF: `src/02_htf_placebo.py` → `out/htf_placebo_results.json` (+`.csv`),
  `out/htf_placebo_preregistration.json`
- Hysteresis: `src/03_hysteresis_placebo.py` → `out/hysteresis_placebo_results.json` (+`.csv`)
- Sizing: `src/04_sizing_placebo.py` → `out/sizing_placebo_results.json` (+`.csv`),
  `out/preregistration.json` / `out/PREREGISTRATION.md`
