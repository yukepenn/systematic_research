# SIMPLE01 — SPEC — Complexity Metric (Task 3)

**Frozen before any candidate is scored on performance.** Every number in this document is a count
of the CONSTRUCTION of each rung defined in `00_SPEC_candidate_manifest.md` — module presence,
parameter presence, branch presence — never a function of returns, PnL, or Sharpe. This is
deliberate: campaign directive sec77-79 requires the complexity metric to exist and be frozen
*before* results can bias it, and it is written here, in the same no-look pass as the manifest.

## 1. Axes and counting rules

Five axes, each counted directly from the pseudocode in `00_SPEC_candidate_manifest.md`, not from
any weighted composite (a single blended scalar invites arbitrary axis-weighting; the disaggregated
table is the score, and margin #9 in `01_SPEC_frozen_margins.md` is defined directly on these
counts, not on a manufactured index).

1. **Signal modules (M)** — count of distinct upstream information sources actively *used* by the
   rung. Max 3: `{Solar13 ensemble, B-MOM (bmomPos), HTF (tiltState)}`. "Used" means the module's
   output actually reaches the final target/`M` computation on some reachable state — a module whose
   only consumer is force-set to a constant (e.g. `tiltState` when both `mm` and `ss` are forced) is
   **not** counted, because its computation becomes dead code for that rung's decision (it may still
   run in an unmodified `.cs` file for engineering-inertia reasons, but a from-scratch reimplementation
   of that rung would not need to compute it at all).
2. **Distinct horizons (H)** — the time-scale each active module draws on: Solar13 is bar-level
   (~460×3-min causal σ window, session-scoped); B-MOM is intraday-plus-recent-history (RTH price
   action compared against a 14-session band); HTF is regime-scale (50-session SMA). In this specific
   architecture each active module introduces exactly one new horizon, so **H = M** for every rung
   below — reported as its own column for transparency (the task asks for it explicitly) but not
   summed separately into anything, since doing so would double-count M.
3. **Behavioral parameters (P)**, post-EQV01 canonicalization — count of free/fixed numeric constants
   actually exercised by the rung's active branches. **EQV01 canonicalization rule applied**: a
   constant and its representationally-equivalent restatement are the SAME parameter, counted once —
   e.g. `TiltRescale=0.9026` is one parameter regardless of whether a document states it as `0.9026`
   or its proven-interchangeable `0.91`; `KSolar` and `KBmom` are two parameters, never three (the
   induced ratio `KBmom/KSolar≈4.0268` is not an independent third number). Dead constants (feeding
   only a forced-neutral branch) are not counted, matching the module rule above.
4. **State branches (B)** — count of distinct conditional decision points in the rung's active
   construction (a ternary is 1 branch; an n-way state-machine transition is counted per transition
   rule). A branch whose condition is real but whose consequent is a no-op forcing (e.g. `mm`'s
   ternary literally replaced by the constant `1.0`) does **not** count — the branch has been
   eliminated from the construction, not merely made unreachable.
5. **Special-case asymmetries (X)** — disclosed, deliberate deviations from a "clean" symmetric rule
   that a reader must separately remember (not just any branch — a branch already counted in axis 4;
   an asymmetry is counted only where the SHAPE of the rule itself is uneven, e.g. a long/short-only
   effect with no mirror-image counterpart). A dormant asymmetry that is real in the code but proven
   (EQV01) never to change behavior over the reachable domain is counted at half weight and footnoted,
   not silently dropped and not counted at full weight either.

## 2. Baseline (architecturally invariant) complexity — reported once, not re-litigated per rung

Both ladders share a Solar13-ensemble core plus decode-to-target/decode-to-`M` skeleton that is
IDENTICAL across every rung of a given product (it is never ablated by this ladder). Counting it once
here, separately from the per-rung incremental table in §3, avoids a large constant offset drowning
out the actual differences between rungs.

| Baseline item | Product A | Product B |
|---|---|---|
| Member ensemble design (`NMEM=13`, `VolMults` grid) | 1 module, counted as 2 design choices (member count + grid) | same |
| Sigma/stop tuning (`VolPeriod, SMinTicks, SMaxTicks, StopMultiplier`) | 4 parameters | same |
| `TiltRescale` (base Solar rescale — applied in **every** rung of both ladders regardless of `mm`/`ss`/`mm`-equivalent, so it is baseline, not HTF-specific) | 1 parameter | 1 parameter |
| Solar weight (`KSolar` / `WSolar`) | 1 parameter | 1 parameter |
| Decode shape | memoryless round+clip, 0 extra state branches | **stateful hysteresis**: `EntryLevel=3.0, ExitLevel=1.0` (2 parameters) + 3-state machine (flat/long/short) with 6 conditional transition rules (6 branches) |
| **Baseline subtotal** | **P=8, B=0** (beyond the per-member up/down machine, itself invariant and not itemized further since it never differs across rungs) | **P=10, B=6** |

**Disclosed, real finding from this exercise (structural, not a performance claim):** Product B's
architecture is intrinsically more complex than Product A's *before any of B-MOM/HTF/short-halving
is even considered* — 2 more baseline parameters and 6 more baseline state branches — because Product
B commits to a discrete, path-dependent hysteresis position while Product A emits a memoryless graded
target every bar. This matches `CANONICAL_MATHEMATICAL_SPEC.md`'s own observation that Product A's
`M` is always rounded/clamped while Product B's is not, and it means a "Product A rung" and a
"Product B rung" at the same nominal complexity LEVEL (e.g. both "Solar+B-MOM only") are not
apples-to-apples in absolute complexity — only within-product comparisons on this ladder are.

## 3. Per-rung incremental complexity (beyond baseline)

### Product B

| Rung | Modules used (M) | Horizons (H) | Incremental params (P) | Incremental branches (B) | Asymmetries (X) |
|---|---:|---:|---:|---:|---:|
| B0 | 1 (Solar) | 1 | 0 | 0 | 0 |
| B1 | 2 (Solar, B-MOM) | 2 | 2 (`WBmom`, `BmomBandDays`) | 1 (B-MOM's 3-way sign branch) | 0 |
| B_FULL | 3 (Solar, B-MOM, HTF) | 3 | 2 (B1's) + 2 (`TiltMult`, `TiltSma`) = **4** | 1 (B1's) + 1 (`mm` ternary) = **2** | 0.5 (dormant: `mm` gates on `sign(sumNext)` not `sign(T)`, proven by EQV01 never to diverge over the reachable domain — real in code, behaviorally inert) |

### Product A

| Rung | Modules used (M) | Horizons (H) | Incremental params (P) | Incremental branches (B) | Asymmetries (X) |
|---|---:|---:|---:|---:|---:|
| A0 | 2 (Solar, B-MOM) | 2 | 2 (`KBmom`, `BmomBandDays`) | 1 (B-MOM's 3-way sign branch) | 0 |
| A1 | 3 (Solar, B-MOM, HTF via `ss`) | 3 | A0's 2 + `ShortHalf`(1) + `TiltSma`(1) = **4** | A0's 1 + `ss` ternary(1) = **2** | 1 (`ss`: long/short-asymmetric, no mirror term for longs) |
| A2 | 3 (Solar, B-MOM, HTF via `mm`) | 3 | A0's 2 + `TiltMult`(1) + `TiltSma`(1) = **4** | A0's 1 + `mm` ternary(1) = **2** | 0 |
| A_FULL | 3 (Solar, B-MOM, HTF via both `ss` and `mm`) | 3 | A0's 2 + `ShortHalf`(1) + `TiltMult`(1) + `TiltSma`(1, shared, counted once) = **5** | A0's 1 + `ss`(1) + `mm`(1) = **3** | 1 (`ss`, same as A1) |

Note the shared-dependency rule applied at A_FULL: `TiltSma` (the 50-session SMA that produces
`tiltState`) is counted **once**, not twice, even though both `ss` and `mm` consume it — it is one
computation, not two.

## 4. Frozen quantitative bar for "meaningful complexity reduction" (feeds margin #9)

A candidate rung is **MEANINGFULLY SIMPLER** than its product's FULL incumbent iff, relative to
FULL, it satisfies at least one of:

- **(a) drops ≥1 full signal module** (a nonzero entry in the Modules-used column disappears), OR
- **(b) drops ≥2 incremental behavioral parameters (post-canonicalization) without dropping a full
  module.**

Applying this bar to every rung in §3, using no performance information:

| Rung | Vs. FULL | Qualifies? | Why |
|---|---|---|---|
| B0 | −2 modules (B-MOM, HTF), −6 params, −3 branches | **YES**, via (a) | drops two modules |
| B1 | −1 module (HTF), −4 params, −2 branches | **YES**, via (a) | drops one module |
| A0 | −1 module (HTF), −3 params, −2 branches | **YES**, via (a) | drops one module |
| A1 | 0 modules dropped (HTF's module — `tiltState`/`TiltSma` — still live via `ss`), −1 param (`TiltMult` only) | **NO** | neither (a) nor (b): the HTF module is not dropped, and only 1 parameter (not ≥2) is dropped |
| A2 | 0 modules dropped (HTF still live via `mm`), −1 param (`ShortHalf` only) | **NO** | same reasoning as A1 |

**Consequence, stated plainly and frozen:** under the campaign's own stated objective ("simplest
architecture that cannot be shown materially worse," not "highest Sharpe" — governance constraints,
this task), **A1 and A2 are not eligible to be promoted as "the simpler system" even if their
non-inferiority margins pass.** They exist in the frozen ladder for causal attribution only (isolating
short-halving's vs HTF-up-weight's marginal contribution to A_FULL−A0's gap, extending PLACEBO01's
program). The only rungs that can result in an actual promoted simplification are **A0** (Product A)
and **B0 or B1** (Product B, whichever is simplER among the two that pass, i.e. B0 preferred over B1
if both clear the margins, per the "prefer simplest, not highest-Sharpe" mandate). This conclusion
follows from construction alone and was reached before any candidate's performance was inspected.

## 5. What this document does not do

It does not rank candidates by complexity against each other's PERFORMANCE (that comparison happens
only after Task 2's margins are evaluated, in a future execution task). It does not compute, run, or
infer anything about net/Sharpe/drawdown for any rung. The counts above are exhaustive readings of
the pseudocode in `00_SPEC_candidate_manifest.md`, re-derivable by anyone from the cited `.cs` line
ranges without running anything.
