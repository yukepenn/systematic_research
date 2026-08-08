# SMV2T_NOFAST_R2 — no-FAST DUAL R2 confirmation (seq 389)

Run dir: `runs/SMV2T_NOFAST_R2` | Spec: `runs/SMV2T_NOFAST_R2/spec.yaml` (committed 547d2d4
before any read/execution). Parent: SMV2R sub_383 (FAST=vm{6,8,10,12} REMOVABLE-CANDIDATE on
the raw core, dev, p=0.821 not statistically resolved at daily-mean level).

Object under test: not the raw core (already characterized in SMV2R) — the **DECISION
object**, SOLAR_DUAL_HTF built on the no-FAST ensemble, run through the same MNQ E10
executor, and the same DAYONLY_DUAL6040 portfolio construction, tested against the frozen
house replacement bar (5 gates, all required). No data ≥ 2026-08-01 read anywhere; dev =
sessions ≤ 2026-05-31 (519,714 3m bars, 1,139 sessions); old-regime data (gate C) is
2006-01-05 → 2021-12-31, entirely pre-2022. Every number below is from an artifact in `out/`.

**BOTTOM LINE (FACT): 3 of 5 required gates FAIL (A, C, E). Per the frozen decision rule
("pass ALL → promote; fail ANY → incumbent retained, lead closed"), the no-FAST DUAL
candidate does NOT become CHAMPION-CANDIDATE. The incumbent 13-member core is retained.
The FAST-cohort removability lead from SMV2R sub_383 is CLOSED — no third bite without a
new mechanism.**

---

## Step 0 — reuse and reconstruction integrity (out/step0_verify.json)

Per CODE MAP instruction, SMV2R's verified simulator/cache was REUSED, not rewritten.

- FACT: `runs/SMV2R_SOLAR_CORE_1/out/cache_incumbent.npz` (pend matrix, 519,714 dev bars ×
  13 members, itself verified 100.0000% against the committed substrate in SMV2R step0) was
  loaded directly. `e10_target(pend)` reproduces the cached `tgt` exactly.
- FACT: the no-FAST core (9 members, vm14..vm30) built from this cache reproduces SMV2R
  sub_383's saved `daily_cohort_no_FAST.csv` daily curve to **max|dev| = 1.8e-12 $** over
  all 1,139 dev sessions; the ALL/incumbent core similarly reproduces
  `e10_daily_dev_incumbent.csv` to the same precision.
- **Spec-label discrepancy (disclosed, not improvised):** spec.yaml's `object_under_test`
  prose reads "10-member (no vm6-12) ensemble", but the parenthetical member-selection rule
  `(no vm6-12)` unambiguously removes vm{6,8,10,12} (4 members) from the 13-member ALL
  cohort, leaving **9 members** (vm14..vm30) — identical to SMV2R sub_383's own no-FAST
  arm. The prose count "10" is a labeling error (off by one from the correct 9). The member
  LIST is the only mechanically well-defined part of the instruction and was followed
  exactly; nothing about the gates, grid, or member selection was invented to resolve this.
  This is recorded, not silently corrected — see spec_label_discrepancy in
  `out/step0_verify.json`.

## DUAL_HTF transform construction (out/curves.csv, out/tpp_all_dev.npy, out/tpp_nofast_dev.npy)

Applied exactly as `runs/SMV2H_ONECONTRACT/smv2h.py` / `rerank.py` /
`runs/SMV2H2_ONELOT_CONFIRM/confirm_gate_a.py` build DUAL_HTF: `agree = sign(T)≠0 &
st_bar==sign(T)`; tilt ×1.25 on agreement; c1_50 (short half-weight iff HTF-up);
×0.9026; clip(rha(·), ±13); HTF = prior-session close vs SMA50 of session closes
(causal, `.shift(1)`). Applied to BOTH the ALL core (T, clip ±10, 13 members) and the
no-FAST core (T, clip ±10, 9 members). Both DUAL legs run through the SAME MNQ E10
executor (`common_exec.e10_exec`, the verified engine, reused verbatim).

Two independent integrity checks, both PASS exactly:
- FACT: the reconstructed **DUAL_ALL** target series matches SMV2H2 gate A's saved
  `out/tdd_dev_from_tgt.npy` **bit-for-bit on every one of 519,714 dev bars**
  (`tpp_all_matches_smv2h2_tdd = True`).
- FACT: the executed **DUAL_ALL** daily curve matches `rerank.py`'s saved
  `solar_dual_htf_daily.csv` (the incumbent DUAL leg) to **max|dev| = 1.8e-12 $** over
  all 1,139 dev sessions.

These two checks confirm the DUAL transform pipeline and executor are identical to the
prior wave's — the no-FAST leg comparison below is apples-to-apples.

---

## Gate A — dev paired bootstrap on the DUAL-transformed legs (out/gate_A.csv) — **FAIL**

House bootstrap: paired moving-block, block=5, B=10,000, seed=20260808, circular index
construction (identical to `confirm_gate_a.py`'s `path_stats`), on daily diffs of
DUAL_NOFAST − DUAL_ALL over all 1,139 dev sessions (k=56 worst days for CDaR_0.95).

| | DUAL_ALL (incumbent) | DUAL_NOFAST (challenger) | point delta |
|---|---|---|---|
| net $ | 138,280.0 | 179,466.0 | +41,186.0 |
| Sharpe | 0.899 | 1.034 | +0.134 |
| CDaR_0.95 $ | 20,447.5 | 18,336.8 | +2,110.6 (improvement) |

- FACT: point estimates favor the no-FAST DUAL leg on both statistics.
- FACT: bootstrap significance — **P(dSharpe>0) = 0.8033** (< 0.85 bar) and
  **P(dCDaR>0) = 0.3895** (well under 0.85). **Gate A FAILS both prongs.**
- INFERENCE: dSharpe is close to the bar (0.80 vs 0.85) but dCDaR is not — the tail-risk
  improvement seen in the point estimate is not robust across resampled paths (5% quantile
  of the CDaR delta is −$13,138, i.e. materially WORSE in a nontrivial share of paths).
  This mirrors SMV2R sub_383's own caveat that the daily-mean edge was "NOT statistically
  resolved" (p=0.179 there); the DUAL/HTF overlay does not resolve it either.

## Gate B — chronology (out/gate_B.csv, gate_B_loyo.csv, gate_B_fit_eval.csv) — **PASS**

LOYO (5 calendar years present in dev) dSharpe = Sharpe(NOFAST) − Sharpe(ALL):

| year | d_net $ | d_sharpe | sign |
|---|---|---|---|
| 2022 | +16,960.7 | +0.309 | + |
| 2023 | −4,562.2 | −0.253 | − |
| 2024 | +5,007.3 | +0.014 | + |
| 2025 | +9,504.4 | +0.033 | + |
| 2026 (partial, Jan–May) | +14,275.8 | +0.649 | + |

- FACT: 4/5 years same (positive) sign → passes the "≥4/5" LOYO bar.
- FACT: fit window (2022–2024) dSharpe +0.085, dNet +$17,406; eval window (2025–2026)
  dSharpe **+0.212** (point-positive), dNet **+$23,780** (point-positive).
- **Gate B PASSES** — the only gate of the five that does.

## Gate C — old-regime non-inferiority, 2006–2021 (out/gate_C.csv, gate_C_yearly.csv,
gate_C_hist_curves.csv) — **FAIL**

Both **raw cores** (no DUAL/HTF overlay — spec text says "cores", the pre-overlay
structural object from sub_383, distinct from the DUAL "decision object" in gates A/D/E)
rebuilt on the SM06 hist substrate. Per-member pending votes are NOT stored in the
committed `vote_state_3m_hist.parquet` (aggregate-only, verified by inspection); they were
regenerated by RE-RUNNING the verified simulator (`sm01_solarsim.member_states` /
`member_trades`) on the same underlying 1-min hist data SM06's `run_hist.py` used
(`research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet`, filtered
`< 2022-01-01`, resampled to 3m — entirely pre-2022, no VIRGIN-rule exposure).

Two integrity checks, both PASS:
- FACT: reconstructed `vote_pend` (sum of the 13-member pend) matches the committed
  `vote_state_3m_hist.parquet` aggregate on **100.00%** of 1,764,049 hist bars.
- FACT: the ALL-core target, run through the standard OHLC MNQ `e10_sim`, reproduces the
  committed `e10_daily_hist.csv` to **max|dev| = 9.1e-13 $** on all 4,130 hist sessions.

Executor for the gate-C comparison itself: **same conventions as SMV2H2 gate B**
(`confirm_gate_b.py`'s `run_policy_hist`) — close-only substrate, fills at next 3m bar
CLOSE ±1 tick (no OHLC on the hist file), session-close flatten, ops windows (flatten
decided 16:39, freeze 16:30–18:03) kept verbatim, NQ costs ($2.18/side, $20/point). This
produces materially different dollar magnitudes than SM06's own original MNQ/OHLC report
(net −$8,970 there) — expected and per spec's explicit convention choice, not an error.

| | ALL core (incumbent) | no-FAST core (challenger) | |
|---|---|---|---|
| net $ (2006–2021) | 318,534.3 | 301,857.9 | gap **−$16,676.4** |
| Sharpe | 0.185 | 0.158 | |
| maxDD $ | 370,365.7 | 355,749.1 | ratio 0.961 |
| CDaR_0.95 $ | 348,303.5 | 323,918.7 | |
| fills / entries | 76,864 / 66,541 | 44,245 / 37,546 | |

- FACT: **c1 (net ≥ incumbent − $10k) FAILS** — gap is −$16,676.4, i.e. $6,676 worse than
  the $10k tolerance floor.
- FACT: **c2 (maxDD ≤ 1.25× incumbent) PASSES** — ratio 0.961 (no-FAST core is actually
  *less* drawdown-prone pre-2022).
- **Gate C FAILS** (both required; c1 alone is dispositive).
- INFERENCE: worst year for both cores is 2009 (ALL −$114,023 vs no-FAST −$89,400 — the
  no-FAST core is *better* in the single worst year), and no-FAST wins 10 of 16 years on
  d_net (`out/gate_C_yearly.csv`) — the net shortfall is concentrated in a few large years
  (2008 −$25,942, 2011 −$26,517, 2020 −$225,289 where ALL's outsized COVID year dominates).
  The old-regime structural evidence is genuinely mixed, not uniformly unfavorable to
  no-FAST, but the mechanical net-floor test as specified fails.

## Gate D — right-tail retention on the DUAL-transformed dev legs (out/gate_D.csv,
gate_D_top10_detail.csv) — **PASS**

- FACT: DUAL_NOFAST's PnL on DUAL_ALL's own top-10 days = $121,024.9 vs DUAL_ALL's top-10
  sum $113,139.5 → **retention = 106.97%** (≥ 100% required). 7 of the 10 top ALL-days are
  also among no-FAST's own top-10 days.
- **Gate D PASSES** — the DUAL/HTF-transformed object does not lose the right-tail edge
  SMV2R showed on the raw core (105.9% there vs 106.97% here — preserved, slightly improved).

## Gate E — portfolio rebuild, DAYONLY_DUAL6040 (out/gate_E.csv, gate_E_curves.csv) — **FAIL**

Replicates `rerank.py`'s 60/40 cell construction exactly (same BM = BMOM E2 next-open ×5.0
ticks, same 0.6/0.4 weights, same equal-vol `vm()` rescale mechanism) with the no-FAST DUAL
leg substituted for the incumbent DUAL leg. The `vm()` scalar SIG is re-derived from the
new leg's own daily std, as `rerank.py`'s `vm()` always does (documented, not invented):
**SIG_old = 2,143.28** (incumbent DUAL_ALL daily std) → **SIG_new = 2,420.08** (DUAL_NOFAST
daily std); BM rescale factor moves from 0.604 to 0.682 correspondingly.

Two integrity checks, both PASS exactly:
- FACT: the no-FAST DUAL leg re-executed via `rerank.py`'s own `sim()` function matches
  `common_exec.e10_exec`'s output (used throughout gates A/B/D) to **max|dev| = 1.8e-12 $**.
- FACT: the reconstructed incumbent champion curve (60/40) matches
  `rerank_portfolios.csv`'s `DAYONLY_DUAL_BMOM_60_40` row exactly (net dev $0.0000, Sharpe
  dev 0.000000) — confirming the champion reference is reproduced correctly before any
  comparison is made.

| | incumbent 60/40 (champion) | no-FAST rebuild 60/40 | point delta |
|---|---|---|---|
| net $ | 194,416.0 | 234,625.5 | +40,209.5 |
| Sharpe | 1.264 | 1.351 | **+0.087 (positive)** |
| CDaR_0.95 $ | 14,322.2 | 15,975.4 | **−1,653.2 (worse)** |
| maxDD $ | 18,131.7 | 21,474.3 | −3,342.6 (worse) |

- FACT: dSharpe is point-positive → passes.
- FACT: **dCDaR is point-NEGATIVE (−$1,653.2)** → fails. Portfolio-level tail risk gets
  worse under the no-FAST rebuild despite the better Sharpe (which the sizing to equal
  DUAL-leg vol partly explains: SIG_new is 13% larger than SIG_old, so the no-FAST-based
  portfolio carries proportionally more BM/DUAL exposure at the same nominal vol target).
- **Gate E FAILS** (both AND-required; dCDaR alone is dispositive).

---

## Decision (spec: "pass ALL → CHAMPION-CANDIDATE; fail ANY → incumbent retained, lead closed")

| Gate | Requirement | Result | Verdict |
|---|---|---|---|
| A (dev bootstrap) | P(dSharpe>0)≥0.85 AND P(dCDaR>0)≥0.85 | 0.8033 / 0.3895 | **FAIL** |
| B (chronology) | LOYO ≥4/5 same sign AND eval 2025-26 point-positive | 4/5, +0.212/+$23,780 | PASS |
| C (old regime) | net ≥ incumbent−$10k AND maxDD ≤1.25× | gap −$16,676 (fail) / ratio 0.96 (pass) | **FAIL** |
| D (right tail) | top10 retention ≥1.00 | 1.0697 | PASS |
| E (portfolio) | dSharpe AND dCDaR point-positive | +0.087 (pass) / −$1,653 (fail) | **FAIL** |

**3 of 5 gates fail (A, C, E). Decision: FAIL ANY → incumbent 13-member core retained.**

The no-FAST DUAL candidate does not become CHAMPION-CANDIDATE core. No master rebuild or
parity stage is triggered. The FAST-cohort (vm6-12) removability lead opened by SMV2R
sub_383 is recorded **CLOSED**: the raw-core point improvements are real and reproduce
cleanly (net, Sharpe, CDaR, right-tail retention all improve on point estimates across
every gate that measured them), but none of the three places this wave tested for
robustness — dev bootstrap significance, pre-2022 net non-inferiority, portfolio-level
CDaR — survive. Per spec, no third bite is authorized without a new mechanism (e.g. a
reason FAST would be expected to hurt tail risk structurally, not just an empirical
retest of the same construction).

## Conventions and caveats

- Dev calendar: 1,139 sessions, 2022-01-03 → 2026-05-29 (sessions ≤ 2026-05-31); no data
  ≥ 2026-08-01 read anywhere. Gate C hist window: 2006-01-05 → 2021-12-31 (16 years),
  entirely pre-2022, no VIRGIN-rule exposure.
- All gates share one calendar within their own domain (dev gates A/B/D/E: same 1,139
  sessions, paired; gate C: same 4,130 hist sessions, paired). House bootstrap:
  block=5, B=10,000, seed=20260808 throughout (out/gate_A.csv).
- Gate C uses NQ-scaled costs and close-only ±1-tick fills (SMV2H2 gate B convention) —
  NOT the OHLC/MNQ convention SM06's own original report used; the two are not
  numerically comparable in raw dollar terms, only within gate C's own ALL-vs-no-FAST
  pairing.
- Every executor and transform step in this run cross-checked bit-for-bit or to
  sub-cent precision against a previously-committed, independently-produced artifact
  from an earlier wave (SMV2R cache, SMV2H2 saved T-dd, rerank.py's saved DUAL/champion
  curves, SM06's committed hist substrate/e10_daily_hist.csv) before being used in any
  gate computation — see the integrity-check FACTs under each gate above.
- Spec-label discrepancy (10-member vs actual 9-member no-FAST cohort) disclosed under
  Step 0 above; resolved via the only mechanically well-defined reading of the spec text,
  not by improvisation.
