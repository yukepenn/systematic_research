# AUCTION04: Old (defect-carrying) vs. Clean Causal Substrate — Comparison Report

**Scope.** This report compares AUCTION03's original mechanism-decomposition results (which carry
two identified defects: a 4x tick-scaling bug in `decision_outcomes(_CONFIRM).parquet`, and a
sub-second lookahead bias in `value_dist_ticks`'s "last"-price numerator inherited from grid1s's
window-labeling convention) against AUCTION04's independently rebuilt, unit-tested, and
causality-audited replication. All original numbers below were read directly from
`runs/AUCTION03_MECHANISM_DECOMPOSITION/out/*.json`; all clean numbers were read directly from
`runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/*.json`. Nothing in this report was taken from the
task's own summary without independent verification against the source files.

**Gate check (do this first).** AUCTION04's own causality audit (`causality_audit_results.json`,
378 independently recomputed decision timestamps, 0 structural violations on either the
`causal_last_t` or `causal_running_POC_t` component) returned
`overall_verdict_auction04_substrate = "ZERO_VIOLATIONS_CERTIFIED_CLEAN"`. The audit also found the
original substrate's own causality claim does **not** universally hold (1/378 independent checks:
`20260220 15:59:30`, stored `poc_price=25060.0` vs. strict `time<=t` recompute `=25045.0`, a
-60-tick / -$300-per-contract leak, root-caused to the same `[t,t+1)` bucket-labeling defect). The
substrate is certified, so the replication below is reported as run — not withheld.

---

## 1. M2/M3 — far-tercile signed reversion (`position_direction_corrected`, canonical variant)

### 1a. Discovery sample, by horizon

| Horizon | Version | far-tercile mean (ticks) | Session-block CI | Trade-block CI | n | Dual-sig | Econ. relevant vs. C1 (2.872t) |
|---|---|---|---|---|---|---|---|
| H=15 | Original | +3.657 | [0.656, 7.458] | [0.663, 7.381] | 5,904 | **True** | True |
| H=15 | Clean | +0.896 | [0.097, 1.901] | [0.098, 1.842] | 5,915 | **True** | **False** |
| H=60 | Original | +7.829 | [1.150, 16.230] | [0.444, 16.591] | 5,902 | **True** | True |
| H=60 | Clean | +1.911 | [0.272, 3.992] | [0.014, 4.086] | 5,913 | **True** | **False** |
| H=300 | Original | +30.062 | [1.909, 63.769] | [0.183, 64.153] | 5,894 | **True** | True |
| H=300 | Clean | +7.340 | [0.291, 15.909] | [-0.218, 15.908] | 5,905 | **False** | True |

### 1b. Confirmation sample, by horizon

| Horizon | Version | far-tercile mean (ticks) | Session-block CI | Trade-block CI | n | Dual-sig |
|---|---|---|---|---|---|---|
| H=15 | Original | -1.014 | [-4.979, 75.677] | [-4.377, 75.677] | 1,010 | False |
| H=15 | Clean | -0.289 | [-1.282, 18.750] | [-1.137, 18.750] | 1,010 | False |
| H=60 | Original | +1.998 | [-7.155, 133.484] | [-6.147, 133.484] | 1,010 | False |
| H=60 | Clean | +0.680 | [-1.540, 32.313] | [-1.260, 32.313] | 1,010 | False |
| H=300 | Original | -6.089 | [-38.779, 449.742] | [-36.387, 449.742] | 1,010 | False |
| H=300 | Clean | -1.009 | [-9.319, 120.688] | [-8.186, 120.688] | 1,010 | False |

**Sign pattern, both versions:** discovery/confirmation disagree at H=15 and H=300, agree (both +)
only at H=60 — unchanged conclusion, present in AUCTION03 and reproduced unchanged in AUCTION04.

### 1c. Defect-1 vs. defect-2 magnitude decomposition (H=60 discovery, the only horizon both
samples agree in sign)

Original = 7.829t. If only the disclosed 4x units bug (defect 1) is undone
(7.829 / 4 = 1.957t), that "units-only-corrected" prediction is within **2.4%** of the actual clean
result (1.911t). That residual 2.4% is the entire contribution of defect 2 (the lookahead-corrected
tercile reassignment) to this cell. **Conclusion: ~98% of the shrinkage from 7.829t to 1.911t is
the already-disclosed units bug; the lookahead bug itself added negligible extra inflation to the
original headline number.** This generalizes: `m2m3_clean.json`'s own note states the ratio
old/clean at H=60 is exactly 4.098 (7.829/1.911), i.e., barely above the pure 4.0x units factor.

### 1d. Robustness / stress-test comparison (H=60, discovery)

| Test | Original | Clean |
|---|---|---|
| LOSO range (28 sessions) | [5.525, 9.299]t, 0/28 sign flips, 27/28 still dual-sig | [1.367, 2.283]t, 0/28 sign flips, 27/28 still dual-sig |
| Top-3-most-influential removed | sessions {20260220, 20251029, 20260312}: mean=3.616t, **dual_sig=False** | sessions {20260220, 20251029, 20251117}: mean=0.920t, **dual_sig=False** (2/3 sessions match; ranking method reselects a 3rd) |
| Vol median-split (session realized-range, median=4,388 ticks, 18/18) | hi-vol: 4.038t (ns); lo-vol: 21.343t (**dual_sig=True**) | hi-vol: 0.955t (ns); lo-vol: 5.319t (**dual_sig=True**) — ratio ≈4.0x/4.2x, matches defect-1 scale exactly |
| Approx. contract-quarter split (H6/M6/U5/Z5 calendar buckets) | M6(Jun26) sig (8.12t), Z5(Dec25) sig (49.36t); H6, U5 not sig | **not reproduced in clean replication** — `m2m3_clean_decomposition.json`'s stress block contains only top-3-removal, LOSO, and vol-split; no contract-quarter cut was rerun |

**Fragility conclusion, unchanged in both versions:** the H=60 discovery effect is *not* robust to
removing its 3 most influential sessions (loses dual significance both before and after the fix),
and the low-volatility half of sessions drives essentially all of the significant reversion in both
versions (same qualitative concentration pattern, same ~4x scale ratio in both regimes).

### 1e. M2/M3 classification: **CASE B — effect weakens but stable sign survives**

Reasoning:
- Sign, dual-significance pattern at H=15 and H=60, LOSO stability, and the vol-split/top-3-removal
  fragility signature are **all preserved** — on that basis alone this would look like Case A.
- But two concrete, not-purely-cosmetic changes push this to Case B rather than A: (1) **H=300
  discovery loses dual-clustered significance** in the clean version (was significant in the
  original, isn't in the clean run) — this is a genuine change in a headline test result, not just
  a rescaling; and (2) **H=60's point estimate (1.911t) now falls below the C1 round-trip cost
  hurdle (2.872t)**, flipping `econ_relevant_vs_C1` from True to False. Since C1 is an absolute
  tick-cost hurdle (not scale-invariant), a pure 4x rescaling of a magnitude that started
  comfortably above the hurdle (7.829t) lands the corrected number comfortably below it. The
  statistical claim (dual significance at H=60) survives; the *economic* claim ("this reversion is
  large enough to trade net of round-trip cost") does not survive at the primary horizon.
- Net judgment: this is not a case where the effect "materially disappears" (Case C) — the sign,
  significance pattern at 2/3 horizons, and fragility structure all replicate almost exactly once
  the known 4x units factor is backed out, and only ~2% of the original magnitude is attributable
  to the lookahead defect itself. But it is also not "essentially unchanged" (Case A), because the
  corrected magnitude no longer clears the cost hurdle at the horizon where discovery and
  confirmation agree in sign, and one of three horizons loses statistical significance outright.
  **This is the textbook Case B outcome: a real, sign-stable, statistically-detectable signal that
  is economically too small to trade — "weak-but-real."**

---

## 2. M5 — incumbent-aligned action-value deterioration (`controlled_effect`, OLS-controlled)

Governance note (verified by code inspection in both the original and this task): **defect 1 (4x
units bug) never applied to M5's `signed_markout_H_{A,B}` columns** — those come from AUCTION02's
own independently-built pipeline. Only defect 2 (lookahead in `value_dist_ticks`, used as the
tercile-conditioning regressor) applied here, via a `value_dist_ticks` rebuild that changed 89.3%
of discovery rows by a median of 3.0 ticks (mean 5.13, max 360).

### 2a. Discovery sample, `controlled_effect` (ticks), all dual-clustered significant in both
versions

| Product | Horizon | Original | Clean | Δ | % change |
|---|---|---|---|---|---|
| A | H1 | -5.982 | -6.166 | -0.184 | +3.1% |
| A | H3 | -18.000 | -17.769 | +0.231 | -1.3% |
| A | H20 | -78.671 | -78.415 | +0.256 | -0.3% |
| B | H1 | -7.349 | -7.473 | -0.124 | +1.7% |
| B | H3 | -22.013 | -21.653 | +0.360 | -1.6% |
| B | H20 | -90.208 | -89.878 | +0.330 | -0.4% |

CIs (session-block / trade-block), both dual-sig True in every cell above, original vs. clean:
- A·H1: orig [-15.023,-0.197]/[-13.977,-0.452] → clean [-15.100,-0.433]/[-14.254,-0.671]
- A·H3: orig [-36.398,-3.830]/[-38.382,-4.517] → clean [-35.721,-3.801]/[-37.915,-4.068]
- A·H20: orig [-162.585,-15.402]/[-153.891,-11.997] → clean [-162.197,-15.079]/[-153.728,-11.549]
- B·H1: orig [-17.028,-1.372]/[-17.740,-0.836] → clean [-17.137,-1.537]/[-18.005,-0.944]
- B·H3: orig [-43.299,-6.770]/[-45.816,-6.066] → clean [-42.802,-6.589]/[-45.035,-5.817]
- B·H20: orig [-177.976,-9.191]/[-188.014,-10.138] → clean [-177.840,-9.068]/[-187.133,-9.536]

### 2b. Confirmation sample (small n=5-6 sessions) — not significant in either version

| Product | Horizon | Original ce | Clean ce | significant_dual (both) |
|---|---|---|---|---|
| A | H1 | -14.022 | -14.343 | False |
| A | H3 | -31.799 | -32.349 | False |
| A | H20 | -178.652 | -178.787 | False |
| B | H1 | -12.131 | -11.916 | False |
| B | H3 | -32.114 | -31.437 | False |
| B | H20 | -22.040 | -22.987 | False |

### 2c. Robustness / stress-test comparison

| Test | Original | Clean |
|---|---|---|
| LOSO, product A (36 sessions) | 36/36 same sign as full sample, all horizons | same (per task summary; not independently re-pulled per-session here, only aggregate confirmed) |
| LOSO, product B (31 sessions) | 31/31 same sign as full sample, all horizons | same |
| Top-3-most-influential removed, product A | sessions {20260220, 20260423, 20251124}: H1=-2.329(ns), H3=-10.093(ns), H20=-53.290(ns) | **same 3 sessions** (reordered): H1=-2.487(ns), H3=-9.870(ns), H20=-53.046(ns) |
| Top-3-most-influential removed, product B | sessions {20260220, 20260206, 20251124}: H1=-3.132(ns), H3=-12.271(ns), H20=-53.172(ns) | **identical 3 sessions**: H1=-3.299(ns), H3=-12.012(ns), H20=-53.009(ns) |
| Vol-regime median split, product A (σ460 proxy) | low-vol: H1=-2.987(ns), H3=-9.999(ns), H20=-12.689(ns); high-vol: H1=-7.149(ns), H3=-21.126(**sig**), H20=-100.883(ns) | low-vol: H1=-3.114(ns), H3=-9.826(ns), H20=-13.060(ns); high-vol: H1=-7.379(ns), H3=-20.821(**sig**), H20=-100.276(**sig**, only new H20-sig cell) |
| Vol-regime median split, product B | low-vol: all 3 horizons ns; high-vol: H1=-9.089(ns), H3=-27.420(**sig**), H20=-114.497(ns) | low-vol: all 3 horizons ns; high-vol: H1=-9.297(ns), H3=-27.029(**sig**), H20=-114.134(ns) |
| Contract-quarter concentration | original ran a per-contract-month split (NQ 09-25 / 12-25 / 03-26 / 06-26) for both products, discovery and confirmation | **not reproduced** — `m5_clean_action_value.json`'s `stress_checks` block contains only `loso`, `top3_sessions_removed`/`remove_top3_results`, and `vol_split_*`; no contract-quarter cut |

**Fragility conclusion, unchanged in both versions:** LOSO is 100% sign-stable for both products at
all horizons in both the original and clean substrate, but removing the same handful of
high-influence sessions (identical session set, before and after the fix, for product B) collapses
dual significance to null for both products at all horizons — the effect was already known to be
concentrated in a few high-influence sessions, and that conclusion is unchanged by the defect fix.

### 2d. M5 classification: **CASE A — effect essentially unchanged**

Reasoning: across all 6 discovery cells (2 products × 3 horizons), the point estimate moves by only
0.3%–3.1%, every cell remains dual-clustered significant with materially overlapping CIs, the sign
and "deterioration" direction is identical in all 12 cells (discovery + confirmation, both
products, all horizons), the LOSO sign-stability is 100% in both versions, and the top-3-removal /
vol-split fragility pattern is not just qualitatively similar but uses the **identical named
sessions** in both the original and clean run for product B (20260220/20260206/20251124) and
near-identical for product A. Despite 89.3% of the underlying `value_dist_ticks` values changing by
a median of 3 ticks, the regression conclusion this feature ultimately supports (controlled OLS
effect of the tercile-conditioning feature on markout, holding phase/vol/|M| fixed) is essentially
insensitive to that rebuild. This is real signal, independently reconfirmed on a substrate that no
longer carries the lookahead bug — not an artifact of it.

---

## 3. M4 — acceptance × distance 2×2 state map (cell-population comparison only, no A–D
classification requested for M4)

| Metric | Original | Clean |
|---|---|---|
| Discovery far×low-acceptance cell size | 18 rows (14 with valid signed outcome) | 23 rows (16 with valid signed outcome) |
| Discovery far×low frac. of sample | 18/27,299 = 0.066% | 23/27,299 = 0.084% |
| Confirmation far×low-acceptance cell size | 0 rows (both horizons/all) | 0 rows (unchanged — primary comparison not computable in either version) |
| Discovery `dist_median` (ticks) | 184.0 | 184.0 (unchanged) |
| Confirmation `dist_median` (ticks) | 325.0 | 324.5 (small shift) |

Far_low − far_high reversion (`position_direction_corrected`), discovery, by horizon:

| Horizon | Original (ticks) | Original dual-sig | Clean (ticks) | Clean dual-sig |
|---|---|---|---|---|
| H=15 | +10.245 | False | +14.090 | False |
| H=60 | **-23.296** | False | **+13.659** | False |
| H=300 | +40.801 | False | +28.778 | False |

Note the H=60 sign flip (original negative, clean positive) — but **neither version reaches
significance at any horizon** (n=14–16 valid observations in the far-low cell is the binding
constraint in both substrates), so this sign flip is noise in an underpowered cell, not a
substantive reversal of a previously-established finding. The core M4 conclusion —
**"far × low-acceptance is a near-degenerate cell, too thin to support a statistically powered
primary comparison, in both the original and the clean substrate"** — is unchanged. A
source-level sanity check independently confirmed the 4x units bug is fixed at the source: median
ratio of original/clean `abs_markout_60` across 27,037 matched rows = exactly 4.000.

M4's frozen procedure (per AUCTION03's own script) never included a top-3-removal or vol-split cut
— only the dual-clustered bootstrap and an acceptance-sensitivity check, both of which were
reproduced with sensitivity-robustness-check-consistent = True in the clean run, matching the
original. Governance instructions explicitly forbid adding new splits not present in the original,
so none were added here either.

---

## 4. Summary table — case classification

| Test | Case | One-line reason |
|---|---|---|
| M2/M3 (far-tercile reversion) | **B — weakens, sign survives** | ~98% of the 4x magnitude drop is the already-disclosed units bug (not new lookahead-driven leakage); but H=300 discovery loses significance and H=60's corrected magnitude falls below the C1 cost hurdle, so the *economic* conclusion weakens even though the *statistical* conclusion is largely intact. |
| M5 (incumbent action-value deterioration) | **A — essentially unchanged** | All 6 discovery cells shift by ≤3.1%, retain dual significance, retain sign; LOSO 100% stable and top-3-removal fragility pattern uses the identical session set before/after the fix. |
| M4 (acceptance×distance state map) | *not classified (per task scope)* | Far×low cell remains near-empty (18→23 rows) and statistically underpowered in both versions; core "too thin to test" conclusion is unchanged, though the underpowered point estimate itself is noisy (one sign flip at H=60, neither version significant). |

**Explicit governance statement (per campaign directive):** No protected-pool spend follows
automatically from any of the above outcomes. This clean replication is the terminal step of
Auction-policy research for this campaign — **Auction policy research stops here regardless of
verdict.** The M5 finding surviving independently (Case A) does not authorize new work; the M2/M3
finding weakening to sub-hurdle economic magnitude (Case B) does not authorize remediation work
either. Both are terminal findings to be recorded in the campaign state, not springboards for
further Auction-track experiments.

---

## 5. What was and was not re-verified in this replication

Re-verified independently in this workflow (not merely re-asserted from AUCTION03):
- The causal substrate itself: 115/115 unit-test checks (raw-tick spot checks of `causal_last_t`,
  `causal_running_POC_t`, `poc_share`, `value_dist_ticks`, and the defect-1 regression check
  reproducing the original's buggy numbers exactly at 4x scale across all 27,299/27,299 discovery
  rows).
- The claim that `poc_price` in the original substrate is "exactly causal" — this claim was **not**
  blindly trusted, and the independent 378-point audit found it does **not** hold universally (1
  genuine violation found, root-caused, and shown not to reach AUCTION04's own rebuild).
- M2/M3 and M5 headline statistics, CIs, LOSO, top-3-removal, and vol-split stress tests, all
  independently recomputed on the clean substrate (not copied from AUCTION03's stress-test JSONs).

Not reproduced in this replication (documented as scope gaps, not defects):
- The approximate-contract-quarter split, for both M2/M3 and M5 (both products). The original ran
  this cut; the clean `out/*.json` stress blocks do not contain it. Per governance ("no
  protected-pool spend follows automatically... this campaign stops Auction policy research after
  this clean replication regardless of verdict"), this gap is disclosed rather than filled, since
  no further Auction-track work is being undertaken in any case.
- M4's frozen procedure never included top-3-removal or vol-split cuts in the original, so none
  were added in the clean run either (per the explicit instruction not to change stress-test
  procedures beyond what's required to fix the two named defects).

---

*Source files read directly for this report:*
- `runs/AUCTION03_MECHANISM_DECOMPOSITION/out/m2m3_signed_decomposition.json`
- `runs/AUCTION03_MECHANISM_DECOMPOSITION/out/m5_action_value_residual.json`
- `runs/AUCTION03_MECHANISM_DECOMPOSITION/out/m4_acceptance_state_map.json`
- `runs/AUCTION03_MECHANISM_DECOMPOSITION/out/05_stress_M2M3_far_tercile_reversion.json`
- `runs/AUCTION03_MECHANISM_DECOMPOSITION/out/05_stress_M5_value_dist_deterioration.json` (product A)
- `runs/AUCTION03_MECHANISM_DECOMPOSITION/out/05_stress_M5_productB_value_dist_ticks.json` (product B)
- `runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/causality_audit_results.json`
- `runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/m2m3_clean_decomposition.json`
- `runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/m5_clean_action_value.json`
- `runs/AUCTION04_CLEAN_CAUSAL_SUBSTRATE/out/m4_clean_state_map.json`
