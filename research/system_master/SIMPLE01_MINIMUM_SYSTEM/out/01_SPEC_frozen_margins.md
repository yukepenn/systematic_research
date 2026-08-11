# SIMPLE01 — SPEC — Frozen Non-Inferiority Margins and Methodology (Task 2)

**Frozen before any candidate result exists.** Written by the SPEC agent (sec71-72), blind to
performance. Every adjustment below is justified against already-committed campaign evidence
(`CAPITAL_FRONTIER.md`, `FORWARD_READINESS.md`, `CONVENTIONS.md`, `primary_objective_v2.py`) read in
full before this document was drafted — not against any new computation. Once frozen here, **no
margin may be loosened after this task**; only a dated, justified, append-only correction (matching
this program's own C7 discipline, see `HOLDOUT_DETERMINATION_20260809.md` for precedent) may touch
this file, and never to make a gate easier to pass.

---

## 1. Reporting windows — frozen, and adjusted from the raw proposal (reasoning disclosed)

**The provisional proposal was "canonical 2023-01-01..2025-02-02 plus the fuller available history
through the LOCKED_FORWARD boundary."** Two problems were found reviewing this against
already-frozen SYSTEM_MASTER conventions, so it is adjusted as follows.

### 1.1 Primary gating window: `CONVENTIONS.md`'s own CURRENT (dev) window, 2022-01-01 → 2026-05-31

`research/system_master/CONVENTIONS.md` (frozen 2026-08-08, i.e. already binding on this whole
program before this task started) defines **CURRENT (dev) = 2022-01-01 → 2026-05-31** as "primary
economic lens; all development, all selection" — this is the SYSTEM_MASTER program's own frozen
primary window, not something this task needs to invent. The narrower legacy canonical window
(2023-01-01T06:00Z→2025-02-02T22:59:59Z, `CLAUDE.md`'s "frozen truth") was built for a *different*
purpose — UI/MCP parity certification of the original `SolarWaveRKReplicaV0` baseline against
NinjaTrader's own Strategy Analyzer — and was never adopted as SYSTEM_MASTER's own selection window;
`CONVENTIONS.md` supersedes it for anything decided inside `research/system_master/`.

**Internal evidence this adjustment is correct, not just preferred:** margin #7 as proposed
("same-sign annual net in ≥4/5 current-regime annual partitions **(2022,2023,2024,2025,2026-
partial)**") already presupposes five calendar-year partitions spanning 2022 through 2026. The
legacy 2023-01-01..2025-02-02 window physically cannot supply five such partitions — it does not
reach 2022 or 2026 at all, and only touches five weeks of 2025. The provisional margin list is
therefore already, internally, written for the dev window; treating "canonical 2023-2025" as the
primary window would make margin #7 uncomputable as stated. **Primary window = dev, 2022-01-01 →
2026-05-31 (≈1,139 sessions, per `FORWARD_READINESS.md`'s own committed count).**

### 1.2 Secondary (comparability-only, non-gating) window: legacy canonical 2023-01-01..2025-02-02

Reported alongside every candidate for continuity with the one number every other document in this
repo already cites (`CLAUDE.md`'s frozen $146,440.60 / 2,915-trade baseline figure is on this exact
window) — but **it gates nothing**. ~505-527 sessions (≈2.1 years), roughly half the dev window's
sample, which independently makes it the WORSE choice for the statistical-power-sensitive Sharpe
margin (§2.3) — another reason it is secondary, not primary.

### 1.3 The 2026-06-01→2026-07-31 window: excluded from every gate, disclosure-only if used at all

**This is not a fresh proposal — it corrects a stale premise in the provisional instruction.**
`research/system_master/HOLDOUT_DETERMINATION_20260809.md` (written one day before this freeze, and
read in full before this document) establishes with direct evidence that this window is
**CONSUMED**, not clean: `runs/SM11_HOLDOUT_READ/` scored six finalists on it and published the
numbers into permanent campaign documents on 2026-08-08, before SIMPLE01 existed. `CONVENTIONS.md`
§8 is explicit that "No iteration afterward: post-read changes create a new candidate class that
cannot claim the holdout." SIMPLE01's candidates are new (never-before-scored) objects relative to
that consumed window's six finalists, so scoring them on 2026-06-01..2026-07-31 now would not be
"claiming a clean holdout" — it would be a **second, unauthorized use** of an already-spent one-time
asset, exactly what §8 forbids. **This window is therefore excluded from every non-inferiority GATE
in this document.** Following the one narrow precedent this campaign has already set for this exact
situation (`SM14_ONELOT_DAYMARGIN`, `SMV2Q_DIAGNOSTICS` both used it for **characterization only,
explicitly "no tuning, no gate, no selection follows"**), a future execution task MAY report
June-July figures for SIMPLE01 candidates as a disclosed, clearly-labeled, non-gating characterization
panel — but must not let any pass/fail decision depend on it, and must say so in the same words this
document does.

### 1.4 VIRGIN (≥2026-08-01): untouched, no exception

Per `research/operational/LOCKED_FORWARD.md`, consumable only by quarterly MONITOR-01 readings or a
pre-registered annual frozen-champion evaluation. SIMPLE01 is neither. Not read, not reported, not
referenced beyond this sentence.

---

## 2. Statistical methodology — frozen

### 2.1 Bootstrap design: reused, not reinvented, from `CONVENTIONS.md` §5

**Circular session-block bootstrap, block = 5 sessions, B = 10,000 replicates, seed = 20260808.**
This is not a new choice for this task — it is `CONVENTIONS.md`'s own already-frozen "Statistical
protocol" for exactly this program, and `seed=20260808` is the house default reused throughout
(`primary_objective.py: SEED = 20260808`, `CAPITAL_FRONTIER.md`'s own bootstraps). Reusing it here
rather than deriving a fresh block/B/seed is itself the answer to "consistency with owner utility
conventions used elsewhere in this campaign" the task asks for — a new, SIMPLE01-specific choice
would be an unforced inconsistency with a program that has already frozen this exact parameter.

**Block-size reasoning (why 5 sessions is appropriate for A/B's holding-period scale, not just
inherited):** both products are trend-following, flat-at-session-close engines whose 13 virtual
Solar members use anchor/stop distances derived from `VolMult ∈ {6,...,30} × causal σ`, giving
multi-day-to-multi-week effective holding periods when a trend persists (members do not reset
intra-trend). A block of 5 sessions (≈1 trading week) is long enough to capture short-range serial
dependence from that multi-day persistence without shrinking the number of independent blocks too
far: at n≈1,139 dev sessions, block=5 gives ≈228 blocks to resample from (≈101 at the ≈505-session
legacy window) — adequate for a circular block bootstrap, and identical to what the rest of this
program already uses for its own headline Sharpe/CI work.

### 2.2 CDaR and top-day metrics: reused definitions, not new ones

`src/analytics/primary_objective.py` already ships house definitions for both quantities used in the
margins below — reused verbatim rather than redefined:
- `cdar_dollar(x, alpha=0.95)` — CDaR₀.₉₅ = mean of the worst 5% of the end-of-day dollar drawdown
  series (`DEFAULT_CDAR_ALPHA=0.95`, the house convention already used by `primary_objective_v2` and
  `CAPITAL_FRONTIER.md`'s own figures). **Frozen: CDaR margin (§3.2) uses α=0.95, computed on each of
  the B=10,000 resampled daily-P&L paths from §2.1, not a single-path point estimate.**
- `top10_day_retention(x, baseline)` — the evaluated series' P&L summed over the baseline's own
  top-10-day positions, divided by the baseline's own top-10 sum. **Frozen: baseline = A_FULL /
  B_FULL for that product, exactly as `primary_objective.py` already implements it.**

### 2.3 Power review for the Sharpe margin — the task's explicit request, answered with a number

**Question asked: is a 10,000-rep block bootstrap sufficient power to resolve a 0.10 annualized-
Sharpe margin at this sample size?** Two separable questions hide in that one, and conflating them
would misdiagnose the risk:

- **Monte Carlo error from B=10,000 itself: negligible, not the binding constraint.** The MC standard
  error of an estimated bootstrap tail probability is ≈√(p(1−p)/B) ≈ √(0.09/10,000) ≈ 0.003 (0.3
  percentage points) at p≈0.90 — B=10,000 resolves the *simulated* probability to well inside 1
  percentage point. **B=10,000 is not the limiting factor.**
- **Sampling uncertainty from ≈1,139 correlated trading days of actual history: the real constraint,
  and it is margin-relevant.** `FORWARD_READINESS.md`'s own committed figure for Product A's
  full-history Sharpe is 1.1819 with a **95% CI of [0.320, 2.036]** on n=1,139 — a half-width of
  0.858, implying SE(Sharpe) ≈ 0.44 for a SINGLE object's Sharpe estimate (cross-checked against Lo's
  (2002) asymptotic formula, SE ≈ √252·√((1+SR_daily²/2)/n) ≈ 0.47 at this SR/n — consistent).

  A SIMPLE01 rung is not an independent draw from a single marginal SE, though — it is a
  highly-overlapping variant of the same underlying signal on the same calendar days, so the relevant
  quantity is the SE of the PAIRED difference (Sharpe_simple − Sharpe_full), which shrinks with the
  candidate/full correlation ρ: approximately SE_diff ≈ SE_each·√(2(1−ρ)) if both series have similar
  variance. Using SE_each≈0.44:

  | assumed ρ (candidate vs. full daily P&L) | SE_diff | one-sided z at margin=0.10 | implied P(diff≥−0.10) if TRUE diff = 0 |
  |---:|---:|---:|---:|
  | 0.99 | 0.067 | 1.50 | 93.3% — clears the 90% bar |
  | 0.95 | 0.149 | 0.67 | 74.9% — **fails** the 90% bar even for a truly-tied candidate |
  | 0.90 | 0.211 | 0.47 | 68.2% — **fails** |
  | 0.80 | 0.298 | 0.34 | 63.2% — **fails** |

  **This is a genuine, disclosed power risk, not a reason to abandon the margin.** Near-neighbor
  rungs — B1 vs B_FULL (only `mm`'s discrete rounding effect ablated), A1 vs A_FULL, A2 vs A_FULL
  (only one of two mutually-exclusive, individually-rare branches ablated, per
  `00_SPEC_candidate_manifest.md` §2.2) — plausibly sit at the high-ρ end of this table, where power
  is adequate. Far rungs — B0 vs B_FULL, A0 vs A_FULL (B-MOM itself removed, a materially larger
  behavioral change that can flip Product B's hysteresis regime outright) — plausibly sit lower, where
  this specific gate may be underpowered to *confirm* non-inferiority even for a candidate that is, in
  truth, fine. The true ρ for each specific pair is only known once the paired bootstrap is actually
  run; napkin figures above are for calibrating expectations, not for pre-judging any rung.

**Frozen response to this finding (methodology, not a loosened margin):**
1. The 0.10 Sharpe margin itself is **kept unchanged** — it is economically well-calibrated (≈8.5%
   relative to Product A's full-history 1.18 Sharpe; a materially different degradation than 0.02-0.03
   would be) and the power concern is about the TEST's resolving power, not about whether 0.10 is the
   right number to ask for.
2. **A third labeled outcome, INCONCLUSIVE, is added alongside PASS/FAIL for this margin only,
   frozen here so it cannot be invented post-hoc to rescue a result:** a rung is INCONCLUSIVE on the
   Sharpe margin if the realized bootstrap P(diff≥−0.10) falls in [0.80, 0.90) — i.e. directionally
   supportive but short of the pre-registered bar by less than the width the ρ=0.90-0.95 band above
   suggests could be pure underpower rather than genuine inferiority. INCONCLUSIVE is not a pass; it
   is a disclosed "this specific test could not resolve the question at this sample size," to be
   reported as such rather than silently rounded to FAIL.
3. **The realized bootstrap SE, the realized candidate/full correlation, and the full CI — not just
   the pass/fail flag — must be reported for every rung**, matching this program's own
   `FORWARD_READINESS.md` standard ("no bare point estimate").
4. This is a further argument (beyond §1.1's) for the dev window over the legacy canonical window as
   primary: n≈1,139 beats n≈505-527, and SE scales ≈√(1139/527)≈1.47× worse on the shorter window,
   directly hurting this already power-constrained test.

---

## 3. Margins — reviewed individually, frozen

For each: the provisional proposal, the review, and the frozen final (identical to the proposal
unless a change is explicitly justified).

### 3.1 Sharpe non-inferiority: `P[Sharpe_simple ≥ Sharpe_full − 0.10] ≥ 0.90` (dev window, primary)

**Review.** Economically meaningful (§ above). Statistically coherent with the caveats and the added
INCONCLUSIVE band in §2.3. Consistent with `FORWARD_READINESS.md`'s own discipline of never quoting a
bare point estimate. **Frozen unchanged**, computed via the §2.1 block bootstrap on **paired daily
P&L differences** (not two independent marginal bootstraps compared after the fact — the correlation
between candidate and full is exactly what makes this test informative, and independent marginal
bootstraps would throw that structure away).

### 3.2 CDaR: no worse than +10% (i.e. `CDaR_simple ≤ 1.10 × CDaR_full`)

**Review.** Directly consistent with this campaign's own repeated framing of drawdown as "the #1
system problem" (owner directive) and with `CAPITAL_FRONTIER.md`'s finding that Product A's
$150,000 operating point already carries a non-trivial (~4%) bootstrapped intraday P_ruin even though
its realized bar-level DD (21.7-21.9%) stays under the 25% ruin threshold — this system is not far
from its own risk budget, so a CDaR-preservation margin is not a formality. **Frozen unchanged**, at
α=0.95 (§2.2), computed on the same B=10,000 dev-window resampled paths as §3.1, for methodological
consistency (one bootstrap run per candidate produces both the Sharpe and the CDaR read, not two
separate resampling exercises that could disagree on which paths were drawn).

### 3.3 MTM intraday DD: no worse than +15%

**Review.** Looser than CDaR's 10% by design (bar-level intraday DD is a noisier, higher-variance
statistic than session-level CDaR, so a tighter bar would mostly measure resampling noise rather than
real degradation) — but reviewed specifically against `CAPITAL_FRONTIER.md`'s disclosed fragility
finding: at Product A's **$100,000** headline capital, the single REALIZED (non-bootstrapped)
worst bar-level intraday drawdown already consumes **32.6-32.9% of capital — past the 25% ruin
threshold with zero resampling**, and even at the better-supported $150,000 minimum operating capital
it sits at 21.7-21.9%, uncomfortably close to that same boundary. A simpler candidate that is 15%
worse on this specific metric is not a hypothetical risk — it could plausibly push an already-marginal
operating capital level over the ruin boundary. **Frozen unchanged at +15%, explicitly BECAUSE of
this fragility, not despite it** — this is the one margin in this document where the review argues
FOR keeping the number exactly as proposed rather than loosening it, on the strength of already-
committed capital-frontier evidence.

### 3.4 Top-10-day PnL retention ≥90% vs. full — kept, AND the sibling top-1%-trade-retention leg restored

**Review.** The provisional list states only the day-level leg. `CONVENTIONS.md` §6 gate 6 (this
program's own, already-frozen, general promotion gate) requires BOTH legs jointly: **"top-1% trade
P&L retention ≥ 90% AND top-10 day retention ≥ 90%"**, describing this as the "HARD RIGHT-TAIL GATE."
Dropping the trade-level leg here would silently weaken an already-frozen campaign-wide standard for
this one program's own simplification test — the opposite of what a non-inferiority review should do.
**Frozen: BOTH legs required, matching `CONVENTIONS.md` gate 6 exactly** — top-10-day retention ≥90%
(reused `top10_day_retention()`, §2.2) AND top-1% trade P&L retention ≥90% (same definition, applied
to individual trade P&L rather than daily P&L; per gate 6's own extra clause, any state a simpler
candidate down-weights below the full system must additionally hold top-1% P&L share ≤ its own trade
share — reused verbatim).

### 3.5 After-cost positive (dev window, base cost model)

**Review.** Trivial sanity floor, matches `CONVENTIONS.md` gate 1 exactly ("positive after base costs
on CURRENT dev"). **Frozen unchanged**, base cost model = this program's own committed cost model
(`CONVENTIONS.md` §3 — Solar-member costs, Lifetime commission + 1 tick/execution, as already used
throughout this repo; not a SIMPLE01-specific invention).

### 3.6 Positive under +1 tick/side cost stress

**Review.** This is not a new stress level for this program — `CONVENTIONS.md` §3 already defines
**C1 = 2.872 t/RT primary, C2 = 4.872 t/RT stress** for new minute-bar NQ engines: the C1→C2 step is
exactly +2.0 ticks/round-trip, i.e. **+1 tick per side**, identical to the provisional margin.
**Frozen unchanged**, explicitly identified as a reuse of the already-frozen C2 stress convention, not
a new number.

### 3.7 Same-sign annual net in ≥4/5 current-regime annual partitions (2022, 2023, 2024, 2025,
2026-partial)

**Review — clarified, not loosened.** As worded, "same sign" is ambiguous without a stated referent.
Read literally as "candidate is net-positive in ≥4/5 years" it would duplicate `CONVENTIONS.md` gate
2 (**"≥3 of 5 dev years positive"**) at a stricter bar (4/5 vs. 3/5) for no stated reason. The more
defensible reading, and the one **frozen here**, is a *comparative* test: **in ≥4 of the 5 annual
partitions, `sign(net_simple[year]) == sign(net_full[year])`** — i.e. the simpler candidate must not
diverge from the full incumbent's own win/lose pattern in more than one of the five years. This is
deliberately a different, stricter question than gate 2's absolute profitability bar: gate 2 asks "is
this object good enough to promote at all," this margin asks "does removing a component change which
years the system wins or loses in" — a genuine behavioral-fidelity check appropriate to a
non-inferiority (not a promotion) claim, and its numeric bar (4/5, not 3/5) is intentional and
justified on those grounds, not an oversight. **Frozen: 4/5 years, same-sign-as-FULL reading.**

### 3.8 Concentration gate on INCREMENTAL advantage: no one day > 25% of any advantage a simpler
candidate shows over the full system

**Review.** Well-designed and asymmetric by construction — it fires only when a simpler candidate
BEATS the full system, guarding specifically against a false "simpler is better" claim driven by one
lucky day, which is exactly the failure mode this campaign's own stated objective (prefer simplest
among candidates that are NOT WORSE, never chase a Sharpe win) is most vulnerable to. It is the natural
day-level, incremental-delta-scoped tightening of `CONVENTIONS.md` gate 4 ("no single month > 40% of
the candidate's net," which is on absolute net at month granularity) — a stricter unit (day vs.
month) and a stricter scope (an incremental, more fragile quantity) is appropriate specifically
because "simplification improved things" claims deserve more scrutiny than "this object is
profitable" claims in this program. **Frozen unchanged.**

### 3.9 Meaningful implementation-complexity reduction

**Review.** Quantified fully in `02_SPEC_complexity_metric.md` §4, not restated as prose here to avoid
two documents disagreeing later. **Frozen: a rung must drop ≥1 full signal module, or ≥2 incremental
behavioral parameters without dropping a module, relative to its product's FULL incumbent** (the exact
rule from the complexity spec). Applying it (construction-only, no performance involved) already
shows A1/A2 do not qualify on complexity grounds alone regardless of how they perform — see that
document §4 for the full table and consequence.

---

## 4. What a rung must clear, altogether, to be a genuine SIMPLE01 promotion candidate

All of §3.1-3.9 (with §3.1 admitting the INCONCLUSIVE outcome as a non-pass, non-silent-fail label),
on the **primary (dev) window**, with the **legacy canonical window and the disclosed June-July
characterization panel reported alongside but gating nothing** (§1.2-1.3). Per the governance
constraint restated in `00_SPEC_candidate_manifest.md` §0: if more than one rung clears every gate,
the SIMPLEST clearing rung (by the complexity spec's own counts) is preferred — a rung is never
promoted for having the highest Sharpe among those that pass.

## 5. What this document does not do

It does not evaluate any candidate. No block bootstrap has been run under this specification; no
Sharpe, CDaR, drawdown, retention, or cost-stress figure for A0/A1/A2/A_FULL/B0/B1/B_FULL has been
computed or viewed while writing it. Execution against this frozen spec is a separate, future task.
