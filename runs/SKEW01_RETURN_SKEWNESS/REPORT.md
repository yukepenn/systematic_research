# SKEW01 — causal return-skewness diagnostic: CLOSE (weak, tail-unsafe, not redundant, not confounded)

Persisted here by the orchestrating session from the subagent's returned text — its Write tool
blocked direct creation of this file.

## Construction (verified)

Causal `skewness_W(t) = mean((r-mean(r))^3)/std(r)^3` over trailing W bars of `ret_1`,
std-guarded (NaN if std<1e-8). Self-tests: symmetric alternating series → 0.000000 exactly;
synthetic right-skew block → +4.129483 (exact match to `scipy.stats.skew`); left-skew mirror →
−4.129483 (exact mirror); near-constant window → NaN via guard. On the real table:
540,212/540,232 bars valid for skewness_20 (population mean −0.020, std 0.760).

## Step 0 — redundancy check: PASSED, not redundant

Raw Spearman, canonical window (n=519,714): max |ρ| = 0.182 (skewness_20 vs `M_slope_20`); vs
U8's own perm_entropy_20/reversal_rate_20/run_persistence_20 all |ρ|≤0.017; vs
trend_efficiency_20/range_efficiency_20/sigma460 all |ρ|≤0.035. No pair exceeds 0.7 — genuinely
distinct information class, not a restatement of U8's organization features or U0's existing
efficiency/vol columns.

## Outcome tests — 8 primary (20-bar) cells, all computed, none skipped

| Outcome | Feature | n | raw ρ | resid ρ | ΔR² | sign-stab | health-ext resid |
|---|---|---:|---:|---:|---:|---|---:|
| (c) reversal hazard | aligned_skewness_20 | 192,723 | −0.0189 | **+0.0467** | +0.000027 | **5/5** | +0.0230 (same) |
| (d) Product-A scale | aligned_skewness_20 | 8,137 | +0.0288 | +0.0266 | +0.00068 | 4/5 | −0.0142 (flips) |
| (d) Product-A scale | skewness_20 (raw) | 8,137 | −0.0277 | −0.0253 | +0.00088 | 4/5 | −0.0260 (same) |
| (a) entry value | entry_skewness_20 (raw) | 1,978 | +0.0169 | +0.0224 | +0.00012 | 3/5 | +0.1233 (n=86, unstable) |
| (a) entry value | entry_aligned_skewness_20 | 1,978 | −0.0055 | −0.0126 | +0.00031 | 3/5 | +0.0504 (flips) |
| (b) hold continuation | aligned_skewness_20 | 192,723 | −0.0056 | −0.0059 | +0.0000007 | 3/5 | −0.0238 |
| (b) hold continuation | skewness_20 (raw) | 192,723 | +0.0028 | +0.0032 | +0.0000138 | 4/5 | −0.0040 |
| (c) reversal hazard | skewness_20 (raw) | 192,723 | −0.0081 | +0.0024 | +0.000061 | 4/5 | −0.0381 |

10-bar robustness (8 more cells) is directionally consistent with the 20-bar versions, no sign
flips. Baseline cross-checks confirm substrate integrity: outcome (a) n=1,978 matches U8 exactly;
outcome (d) canonical mean fwd20_pnl_per_contract = $14.43, matching U6/PA0/U8's own published
headline exactly.

## Too-good-to-be-true gate: no trigger

Max |ΔR²| across all 8 primary cells = 0.00088 (outcome d, raw skewness_20) — an order of
magnitude below U8's own already-closed max (0.00547) and roughly 23x below the spec's 0.02
example threshold. No cell required look-ahead re-derivation; bar-alignment documented for all
4 constructions regardless (matching the already-cleared conventions U6/U8/U8B established).

## Right-tail check: FAILS badly

Strongest cell overall by |residualized Spearman| is (c) `aligned_skewness_20` vs reversal
hazard (ρ=+0.0467, 5/5-year stable — the most chronologically consistent cell, but also the
smallest ΔR² of all 8). Checked at block level (n=1,974 blocks): population "bad" (high
aligned-skew/exhaustion-risk) tercile rate = 33.3%. Top-20 all-time winning blocks: 7/20 (35%) —
statistically indistinguishable from base rate. But a naive hard filter requiring the "good"
tercile to hold through would have **excluded 18 of the top-20 winning blocks**, including the
single largest winner ($41,337.82) — far worse than every prior right-tail check this campaign
has run (U8's perm_entropy_20 excluded 10/20; R4's CLV excluded 3/20).

## Verdict: CLOSE — weak and tail-unsafe (not redundant, not confounded)

Return-skewness_20 is a genuinely new, non-redundant feature class (Step 0 clean, max |ρ|=0.182).
Not confounded (TGTT gate clean, all effects tiny by construction — no look-ahead needed). But
every one of the 8 required cells is uniformly small: max ΔR²=0.00088 (vs U8's own
already-closed max of 0.00547 — roughly 6x smaller). Three of four outcomes show unstable sign
(3-4/5 years, including sign flips into the 2026 extension). The one cell with perfect
chronological stability (outcome c, reversal hazard, 5/5) has the smallest ΔR² of the entire
table (0.000027, essentially zero explanatory power beyond |M|×vol) and fails the right-tail
check more decisively than any other closed family this campaign has tested (18/20 top winners
excluded under a naive filter). Consistent with the self-test sanity check showing mean
|skewness_20| ≈ 0.37 on pure random N(0,1) noise at W=20 — small-sample estimation noise
plausibly dominates any genuine signal at this window length on 3-minute bars.

External trend-reversal/skewness literature (`research/system_master/LITERATURE_SCOUT_
20260809.md` sec2) is not corroborated by this system's own causal state layer at the
preregistered 10/20-bar windows. **CLOSED — no candidate constructed. Product A and Product B
remain unchanged.**
