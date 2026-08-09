# U8 — path organization / entropy (Track L, diagnostic only): CLOSED

Persisted here by the orchestrating session from the subagent's returned text — its Write tool
blocked direct creation of this file.

**Verdict: CLOSE.** No cell (of 12 required + 6 robustness) clears the campaign's bar for a
future construction candidate. Not redundant with existing state (Step 0 passed cleanly), but
every effect is small, and the single strongest cell fails the right-tail check badly (tail-blind,
would exclude half of the top-20 all-time winners under a naive filter). A clean, informative
null/near-null across the board — this restates neither Solar nor U0's existing efficiency
columns, it's just genuinely weak.

## Correctness gate

Reads `u0_state_table.parquet` only (already byte-exact-gated against all 3 certified nets); the
`fwd20_pnl_per_contract` construction for outcome (d), copied verbatim from U6, reproduced
exactly $14.43/contract on canonical SCALE_IN bars, matching U6/PA0's own published headline.

**Disclosed reconciliation (investigated, not a bug):** outcome (a)'s Product-B block table
(net_pnl = last row's `run_pnl_B_dollars`) sums to $375,109.92 over 2,064 blocks (canonical+
extension), vs. the certified $360,590.96 true bar-level total — a $14,155.20/4.7% gap. Traced
exactly: exit-fill cost (commission + fill-bar price residual) is booked on the FLAT bar
immediately after a block closes, not attributed to the closing block's own running P&L column —
the same block-boundary convention R4/U4 already used (U4's own short-only cross-check,
$35,112.38, reproduces exactly under this convention). A small, roughly-constant per-block
omission with no plausible causal channel to an entry-bar path-organization feature — does not
bias the correlations reported. Outcomes (b)/(c)/(d) are unaffected (they sum raw forward
`bar_pnl` over fixed windows regardless of position state).

## Step 0 — redundancy check (mandatory, ran first)

Raw Spearman, canonical window (519,714 bars), all 6 features vs. `trend_efficiency_20`/
`range_efficiency_20`: max |ρ| = 0.325 (perm_entropy_20 vs trend_efficiency_20), every other pair
≤0.14. **No feature flagged redundant (threshold 0.7)** — a genuinely different information
class. `reversal_rate_W` and `run_persistence_W` are exact rank-inverses of each other by
construction (ρ=−1.000 at each window) — expected, not a redundancy flag against existing state.

## Master 12-cell table (3 features × 4 outcomes, 20-bar primary window)

| Outcome | Feature | n | raw ρ | resid ρ | ΔR² | sign-stability | health-ext resid |
|---|---|---:|---:|---:|---:|---|---:|
| (a) entry value | perm_entropy_20 | 1,978 | −0.0691 | **−0.0698** | +0.00547 | 4/5 | −0.0612 (same) |
| (d) Product-A scale | perm_entropy_20 | 8,137 | −0.0514 | −0.0510 | +0.00301 | 4/5 | +0.0122 (flips) |
| (d) Product-A scale | reversal_rate_20 | 8,137 | −0.0485 | −0.0455 | +0.00208 | **5/5** | −0.1042 (same, stronger) |
| (d) Product-A scale | run_persistence_20 | 8,137 | +0.0485 | +0.0455 | +0.00262 | **5/5** | +0.1042 (same, stronger) |
| (c) reversal hazard | reversal_rate_20 | 192,723 | −0.0112 | −0.0380 | +0.00029 | 4/5 | −0.0201 (same) |
| (c) reversal hazard | run_persistence_20 | 192,723 | +0.0112 | +0.0380 | +0.00034 | 4/5 | +0.0201 (same) |
| (a) entry value | reversal_rate_20 | 1,978 | −0.0319 | −0.0277 | +0.00330 | 3/5 | −0.0861 (same) |
| (a) entry value | run_persistence_20 | 1,978 | +0.0319 | +0.0277 | +0.00388 | 3/5 | +0.0861 (same) |
| (c) reversal hazard | perm_entropy_20 | 192,723 | −0.0056 | −0.0235 | +0.00015 | 4/5 | −0.0126 (same) |
| (b) hold continuation | perm_entropy_20 | 192,723 | −0.0010 | −0.0007 | +0.00002 | 3/5 | −0.0351 (near-0 base) |
| (b) hold continuation | reversal_rate_20 | 192,723 | −0.0002 | −0.0001 | +0.00001 | 4/5 | −0.0346 |
| (b) hold continuation | run_persistence_20 | 192,723 | +0.0002 | +0.0001 | +0.00002 | 4/5 | +0.0346 |

All 12 required cells reported, no cell skipped, including (b), which is a clean null across all
three features. 10-bar robustness versions are directionally consistent throughout, generally
10-20% larger in magnitude for (a)/(c)/(d) — no window-dependent sign flips anywhere.

**By outcome:** (a) perm_entropy_20 is the single strongest cell in the whole family (resid
ρ=−0.070, largest ΔR²) — lower path entropy at entry predicts higher block net_pnl, 4/5 years,
extension consistent. (b) genuinely null everywhere (baseline fwd_5 mean $8.35/bar over 192,723
HOLD bars; feature contribution is noise-level). (c) small but the most internally-consistent
group (4-5/5 years) — a currently-persistent/low-reversal path predicts a slightly higher chance
of an imminent reversal event (an "exhaustion" story), but magnitude is tiny (ΔR²≤0.0003 vs a
0.031 baseline R² already explained by |M|×vol alone). (d) the most chronologically stable group
(5/5 years for reversal_rate/run_persistence_20, strengthening into the extension), but
smaller/comparable in magnitude to U6's own already-deprioritized scale-rate lead.

## Right-tail check (mandatory, on the single strongest cell: outcome (a) perm_entropy_20)

Canonical Product-B blocks (n=1,978), population base rate of "bad" (high-entropy) tercile =
32.7%. Top-20 all-time winning blocks: 7/20 (35%) in the "bad" tercile — statistically
indistinguishable from base rate. Bottom-20 losing blocks: 7/20 (35%) — identical rate.
**perm_entropy_20 has zero tail-discriminating power** — the exact same tail-blind pattern that
disqualified R5's `direction_x_volume`. A naive hard filter requiring "good" (low-entropy)
tercile to enter would have excluded 10 of the top-20 winners — half of them (worse than R4's
CLV, which excluded 3/20, and far worse than U5's vwap_aligned, which excluded 0/20). The single
largest winner ($41,337.82) sits in the "good" tercile, but the #4 ($15,207.82, entropy=0.971)
and #6 ($13,257.82, entropy=0.918) winners are both deep in "bad" territory.

## Verdict

No feature × outcome cell satisfies the family's own bar (real + chronologically-stable +
non-redundant + right-tail-safe). The strongest cell by magnitude fails right-tail cleanly; the
most chronologically stable cluster (outcome-d) has smaller effect size than an already-
deprioritized prior lead and was not right-tail-tested this run. Step 0 confirms this is not
simply Solar/efficiency restated, so this is a genuine negative result on a genuinely new
feature class, not a disguised redundancy. **CLOSED — no candidate constructed. Product A and
Product B remain unchanged.**

## Addendum note (organization TRANSITION, not tested this run)

This family tested organization *level* only. The owner's same-day addendum sharpens the
hypothesis to organization *transition* (short-vs-long efficiency/entropy deltas) × incumbent
momentum × session — a materially different question (change, not level) queued as a follow-on
family, U8B, informed by but not blocked on this closure.
