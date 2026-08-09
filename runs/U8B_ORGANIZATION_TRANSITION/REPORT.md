# U8B — path organization TRANSITION: CLOSE

Persisted here by the orchestrating session from the subagent's returned text — its Write tool
blocked direct creation of this file.

**Verdict: CLOSE.** Right-tail-unsafe, matching U8's own precedent, but genuinely different in
character — the addendum's central mechanism (transition effect amplifies with incumbent
conviction) gets qualitative support, but the mandatory right-tail-safety condition still fails,
more decisively than U8's own already-closed level-feature finding.

## Reuse verification (not a formal correctness gate — no new pricing/position path built)

Every population count reproduces U8/U0 exactly: Product-B block table sums to $375,109.92 over
2,064 blocks (matches U8's own disclosed reconciliation figure exactly); HOLD-bar population
203,252 (192,723 canonical) matches U0/U8 exactly; Product-A SCALE_IN population 8,481 (8,137
canonical) and canonical `fwd20_pnl_per_contract` mean $14.43 reproduce U6/U8's own headline
exactly.

## Step 0 — redundancy check (mandatory, run first)

Transition features are genuinely orthogonal to both adjacencies: max |ρ| = 0.128
(run_persistence_transition vs U8's reversal_rate_20) against U8's own LEVEL features, and
near-zero (≤0.011) against U0's M_change/M_slope_20. **No feature flagged redundant** (threshold
0.7). Mirror check: reversal_rate_transition vs run_persistence_transition ρ = −0.950 — strongly
negative as expected but empirically *not* the exact −1.000 identity U8 found at single windows.

## Stage-1 master table (18 cells, 3 features × 6 outcomes) — strongest to weakest

| Outcome | Feature | n | resid ρ | ΔR² | sign-stab | extension |
|---|---|---:|---:|---:|---|---|
| (a) MFE | reversal_rate_transition | 1,978 | **−0.0756** | +0.00305 | 5/5 | same sign, weaker |
| (a) MFE | run_persistence_transition | 1,978 | +0.0656 | +0.00146 | 5/5 | flips |
| (a) MFE | perm_entropy_transition | 1,978 | −0.0631 | +0.00157 | 5/5 | flips |
| (b) MAE | reversal_rate_transition | 1,978 | +0.0598 | +0.00217 | 4/5 | flips |
| (b) MAE | run_persistence_transition | 1,978 | −0.0578 | +0.00146 | 4/5 | flips |
| (d) bars-to-MFE | perm_entropy_transition | 1,978 | −0.0518 | +0.00259 | 4/5 | same sign, weak |
| (d) bars-to-MFE | reversal_rate_transition | 1,978 | −0.0513 | +0.00266 | 4/5 | flips |
| (f) Product-A scale | reversal_rate_transition | 8,137 | −0.0320 | +0.00076 | **5/5** | **same sign** |
| (f) Product-A scale | perm_entropy_transition | 8,137 | −0.0301 | +0.00062 | **5/5** | **same sign** |
| (e) top-decile P | reversal_rate_transition | 1,978 | −0.0207 | +0.00204 | 4/5 | same sign |
| (c) reversal hazard | reversal_rate_transition | 192,723 | −0.0073 | +0.00004 | 4/5 | ~null |
| (c) reversal hazard | perm_entropy_transition | 192,723 | −0.0023 | +0.00006 | 3/5 | ~null |

Outcome (c) is a clean null everywhere (matches U8's own outcome-c finding). Outcome (f)
Product-A scale is again — like in U8 — the most chronologically robust group (5/5 canonical
years, extension holds sign for all 3 features), though smallest in magnitude.

## Stage-2 interaction test (organization_transition × |M|, U1's own OLS-interaction pattern)

The strongest cells are (a) MFE × reversal_rate_transition (ΔR²_interaction=+0.00254,
coef=−923.9, t=−2.31) and (f) Product-A × reversal_rate_transition (ΔR²=+0.00099, coef=−80.6,
t=−2.84, largest t-stat in the family). Both interactions are **directionally consistent with
the addendum's central hypothesis**: the transition→outcome relationship gets stronger (more
negative slope) as |M|/|M_A_raw| rises — the effect is genuinely conditional on incumbent
conviction, not just additive. Magnitudes remain small (ΔR²≤0.0025).

## Too-good-to-be-true gate

Max ΔR² = 0.00305 (Stage 1), 0.00254 (Stage 2) — both an order of magnitude below the 0.02
trigger. Not flagged, no sunk-P&L investigation needed.

## Session interaction (addendum's own emphasis), winning cell (a) MFE × reversal_rate_transition

Blended ΔR²=+0.00305 (n=1,978); RTH ΔR²=+0.00480 (n=1,151, resid ρ=−0.0730); ETH ΔR²=+0.00083
(n=827, resid ρ=−0.0475). Same sign both sessions, but the effect is roughly 6x stronger in RTH
than ETH.

## Right-tail check (mandatory, on the single strongest cell)

Population base rate of the "bad" (becoming-disorganized) tercile = 29.8%. Top-20 all-time
winners: 4/20 (20%) in that tercile (mildly below base rate — the correct direction), bottom-20
losers: 7/20 (35%). But **a naive hard filter requiring the "good" tercile to enter would have
excluded 13/20 (65%) of the top-20 winners — including the single largest winner ever
($41,337.82, sits in the "mid" tercile).** This is worse than U8's own already-disqualified
perm_entropy_20 finding (which excluded 10/20).

## Verdict

**CLOSE.** Step 0 confirms this is genuinely new information (not redundant with level or
momentum's own rate-of-change), the strongest cell is chronologically stable (5/5 years,
extension holds sign though weaker), and the Stage-2 interaction test gives qualitative support
to the addendum's specific mechanism (transition effect amplifies with |M|, t≈−2.3 to −2.8). But
the mandatory right-tail-safety bar is a hard AND condition, and the strongest cell fails it more
decisively than U8's own closed level-feature finding — a naive filter would have cost the
single largest winning trade in the whole dataset. Per this family's own verdict condition, all
four conditions (real, stable, non-redundant, right-tail-safe) must hold before a policy
translation is authorized; only three do. No candidate is constructed, no policy translation
prose is offered. **Product A and Product B remain unchanged.**
