# U6 — Product-A path-dependent exposure science

**Disposition: diagnostic complete, no candidate constructed.** Directly answers directive
sec37: real, multi-year-stable, modest predictive information exists before scale-up — genuinely
distinguishable above chance, not safely actionable given standing right-tail discipline.
(Persisted here by the orchestrating session from the subagent's returned text — its Write tool
blocked direct creation of this file.)

## Correctness gate: PASS

This run's own forward-20-bar-per-contract substrate reproduces PA0's published canonical-window
headline numbers essentially exactly — FRESH entries +$2.03/contract (PA0: +$2.03, n=3,483) and
SCALE_IN +$14.43/contract (PA0: +$14.43, n=8,137). All primary results are the canonical window
(2022-01-03..2026-05-29); the June-July-2026 health-only extension is reported separately,
observationally, never blended.

## Part 1 — WHY are scale-in contracts more valuable than fresh entries?

**Answer: overwhelmingly because SCALE_IN bars occur, almost by construction, at a much larger
|M_A_raw| conviction magnitude** — this single feature mediates >100% of the raw premium on its
own (OLS: adding `m_abs` to `fwd20_pnl_per_contract ~ is_scale_in` drops the is_scale_in
coefficient from +$12.41 to -$40.31, ΔR²=+0.00256, the largest of any feature tested). Secondary,
genuinely separable channels — Solar13 ensemble consensus (ΔR²=0.0011-0.0012, mediates
175-179%), rising-conviction slope (ΔR²=0.0010, mediates 39%), B-MOM engagement magnitude
(ΔR²=0.0005, mediates 110%) — each add a real but order-of-magnitude-smaller slice. All ΔR² are
small in absolute terms (max 0.0026, smaller than R4/R5's own already-modest 0.009-0.012
findings) — real but modest, per this campaign's standing bar.

Entry-vs-scale-in distributional gaps (rank-biserial effect, all p<0.001 except htf_agree_code
p=0.0001): m_abs 0.918, vote_dispersion(abs) 0.606, vote_dispersion(aligned) 0.581, b_abs 0.483,
b_aligned 0.442, slope_aligned 0.129, sigma460 0.085, htf_agree_code 0.040.

**Within-SCALE_IN residual heterogeneity is a genuine null**: after bucket-residualizing by
|M_A_raw| tercile × vol tercile (R4/R5's own pattern), no feature exceeds |ρ|=0.037 — once a bar
is already a scale-in event in a given conviction/vol bucket, none of these features further
discriminate how valuable that specific unit will be.

**B-MOM's two framings diverge and both matter**: `b_aligned` (signed) shows a big
ENTRY→SCALE_IN separation (a *timing* effect — B-MOM is slow/lagging and simply has more bars,
median age 57, to swing into alignment) — distinct from Part 2's finding that B's alignment *at
inception* is non-monotonic.

**Extended window (n=121 ENTRY / 344 SCALE_IN, observational)**: dramatically richer — ENTRY
+$90.64/contract, SCALE_IN +$74.94/contract — consistent with U0's own disclosure that Product A
earned +$34,970 in just these 45 sessions.

## Part 2 — Path-dependence of low-exposure trajectories

**Population**: 4,516 of 4,809 canonical nonzero blocks (93.9%) start with |target_exposure_A|≤3.
Of those: 495 (11.0%) later reach ≥7 contracts ("low-to-high"), 3,180 (70.4%) never exceed 3
("stayed-low"), 841 (18.6%) plateau at 4-6 ("mid", excluded from the binary test per spec).

Mann-Whitney U on first-bar features, low-to-high (n=495) vs stayed-low (n=3,180) — 6 of 8
features significant (p<0.001, bootstrap CI excludes 0):

| feature | rank-biserial effect | p |
|---|---:|---:|
| sigma460_atr_proxy_pts | **0.167** | 2.1e-9 |
| htf_agree_code | **0.153** | 5.0e-10 |
| vote_dispersion (aligned) | **0.140** | 1.6e-7 |
| b_aligned | -0.103 | 5.0e-7 |
| m_abs | 0.082 | 2.0e-8 |
| b_abs | 0.071 | 0.00043 |
| vote_dispersion (abs) | 0.042 | 0.115 (n.s.) |
| slope_aligned | -0.002 | 0.941 (n.s.) |

`b_aligned`'s inverted sign is a checked, genuine anomaly, not noise: it's **U-shaped** — B-MOM
*neutral* at entry predicts the *smallest* eventual trip (mean max|exposure|=2.42), while B-MOM
strongly *aligned* (3.21) OR strongly *opposed* (3.33) both predict larger trips. Direction-
agnostic `b_abs` recovers a clean monotonic relationship.

**Continuous robustness check** (Spearman, first-bar feature vs. eventual max|exposure|, n=4,516
incl. "mid"): m_abs **0.341**, b_abs **0.238**, b_aligned 0.134, sigma460 0.094, slope_aligned
0.089, htf_agree_code 0.068 — corroborates the same features from a different angle.

**Chronology (top-3 features, year-by-year canonical)** — all three same-signed in all 5
canonical year-slices:

| feature | 2022 | 2023 | 2024 | 2025 | 2026 (Jan-May) |
|---|---:|---:|---:|---:|---:|
| sigma460 | 0.069 (p=.19) | 0.188 (p=.001) | 0.218 (p=.001) | **0.313** (p<.001) | **0.324** (p=.001) |
| htf_agree_code | 0.112 (p=.023) | 0.177 (p<.001) | 0.186 (p=.001) | 0.152 (p=.003) | 0.163 (p=.049) |
| vote_dispersion_aligned | 0.155 (p=.002) | 0.170 (p=.003) | 0.162 (p=.011) | 0.086 (p=.13, n.s.) | 0.264 (p=.004) |

`sigma460` shows a striking monotonic strengthening over calendar time. Extended window (n=30/104,
observational): sigma460 effect=0.229 (p=0.057, marginal, small n) — same sign, not blended into
the chronology.

## Part 3 — right-tail check (mandatory before Part 2's finding means anything)

| | net_pnl range | started in 1-3-contract state |
|---|---:|---:|
| Top-20 all-time winners (canonical) | $6,563.90 to $18,352.15 | **14/20 (70%)** |
| Bottom-20 all-time losers (canonical) | -$4,934.45 to -$2,509.65 | **15/20 (75%)** |
| All 4,809 canonical nonzero blocks | — | 93.9% (reference) |

Confirms PA0's own prior: most of both the best and worst blocks in history started in the exact
state PA0 found net-negative in isolation. **No elimination of low-exposure entries is
proposed.** Secondary observation: both tails sit *below* the 93.9% population base rate — blocks
starting already >3 contracts (via FLIP or an unusually strong first bar) are mildly
over-represented among BOTH winners and losers, the same tail-symmetric, non-actionable
signature R4/R5/PA0 already established.

## Verdict

**Yes — low-exposure trajectories CAN be distinguished, above chance, before the scale-up
decision.** Three first-bar features (`sigma460`, `htf_agree_code`, `vote_dispersion_aligned`)
show real, statistically significant (pooled p<1e-6), chronologically stable (same-signed 4-5/5
canonical years) separation, corroborated on the continuous side by `m_abs` (ρ=0.34) and `b_abs`
(ρ=0.24). Effect sizes are **moderate, not strong** (rank-biserial ≤0.17 — substantial group
overlap remains); no composite classifier was built (out of scope / against the no-black-box
discipline).

**This does not license construction.** Part 3 is the load-bearing constraint: extreme-outcome
blocks (both directions) are not concentrated in the low-exposure starting state any such rule
would act on — the same tail-symmetric pattern that killed R1/R3/R4/R5/PA0's own leads.

## NOT YET TESTED / NOT AUTHORIZED FOR CONSTRUCTION

Rather than filtering/shrinking any low-exposure entry, a future study could ask whether the
*rate* an already-open small position is allowed to scale could be made mildly more responsive to
`sigma460`/`htf_agree_code`/`vote_dispersion_aligned` at inception — never declining the entry
itself. Would need its own preregistered spec, its own right-tail gate on these specific
top/bottom-20 blocks, and justification that effect sizes this small (ΔR²<0.003, rank-biserial
≤0.17) survive discretization/transaction costs.
