# STAT01 — Selection-Robustness Audit: DSR-by-N, V-sensitivity, PBO/SPA defensibility

**Scope.** This is a bookkeeping/statistical audit, not a promotion or rejection decision on its
own (per campaign directive sec61-66). It recomputes the campaign's own deflated/haircut Sharpe
under every defensible trial-count (`N`) assumption currently on the record, checks how much of
that answer is actually coming from `N` versus from the cross-sectional variance input `V`, and
separately assesses whether PBO (CSCV) or Hansen SPA have a defensible computation to run at all
given what candidate families and adjudications currently exist. Nothing here reruns a backtest,
touches a strategy file, or changes any prior verdict. The campaign is formally **CLOSED**
(`CAMPAIGN_STATE.md` §9b, 2026-08-07); this is post-closure audit work, same footing as
`REGISTRY_GAP_NOTE.md` and `HASH01_BEHAVIORAL_POLICY_REGISTRY`.

**Governance constraint honored throughout (sec61-66):** no trial-count assumption is selected or
presented as preferred — every defensible `N` is reported side by side. No PBO number is
manufactured on a family too coarse/collinear to support one. No SPA is run against a manufactured
"apparently superior" candidate. Nothing here claims to restore the campaign's lost
preregistration guarantee (sec66) — the DSR-by-N sweep is a sensitivity disclosure layered on top
of an already-disclosed gap, not a repair of it.

**Reuse discipline.** All DSR/Harvey-Liu numbers are produced by direct import of
`src/analytics/trials.py` (`harvey_liu_haircut()`, `deflated_sharpe()`) and
`src/analytics/validation.py` (`psr()`, `sharpe()`) — the only executable DSR/Harvey-Liu
implementation anywhere in the repo (confirmed by grep for `Harvey|haircut|deflated|DSR` across
the full tree: 66 files matched, only these two modules contain code rather than prose report
tables). Nothing was reimplemented. The PBO/SPA assessment reuses HASH01's own already-computed
deduplication and eigenvalue-participation-ratio results verbatim — no P&L was rebuilt, no
correlation matrix recomputed, no dedup redone.

Outputs:
- `src/01_dsr_multi_n.py`, `src/02_pbo_spa.py`
- `out/dsr_results.csv`, `out/dsr_results.json`
- `out/dsr_v_sensitivity.csv`
- `out/pbo_spa_results.csv`, `out/pbo_spa_results.json`

---

## 1. DSR / R6 Harvey-Liu haircut across every defensible `N`

**Candidates.** The campaign's two live incumbents — `SolarWaveSMMaster_v4.cs` (Product A,
`A_FULL`) and `SolarWaveOneContractNQ_v5.cs` (Product B, `B_FULL`) — since Wave 3/SIMPLE01
produced no new promotable candidate to test instead (SIMPLE01's own headline: "zero rungs pass,
for either product," §5 below). Daily P&L: full available history 2022-01-03 → 2026-07-31
(n=1,184 sessions), from `research/system_master/SIMPLE01_MINIMUM_SYSTEM/out/
daily_pnl_{A,B}_FULL_base_cost_full_history_through_20260731.csv`.

| Candidate | n_days | Window | Sharpe (ann) | Skew | Excess kurtosis |
|---|--:|---|--:|--:|--:|
| A_FULL (`SolarWaveSMMaster_v4.cs`) | 1,184 | 2022-01-03 → 2026-07-31 | 1.3073 | 1.821 | 9.021 |
| B_FULL (`SolarWaveOneContractNQ_v5.cs`) | 1,184 | 2022-01-03 → 2026-07-31 | 1.2129 | 1.097 | 7.863 |

Skew/excess-kurtosis are computed with the same estimators `psr()` uses internally
(`scipy.stats.skew(bias=False)`, `scipy.stats.kurtosis(fisher=True, bias=False)`); both are
properties of the candidate series alone, not `N`-dependent, and are the same at every row below.

### 1.1 Five `N` assumptions, all defensible, none preferred

| `N` | Label | Basis |
|--:|---|---|
| 90 | Contemporaneously registered (lower bound) | `tested_configs.csv` seq 1-90 (Wave 1/1b), before the registry-convention lapse. The **only** `N` with an unbroken, committed-before-results paper trail for every row. |
| 229 | Gap-note R1 basis | `REGISTRY_GAP_NOTE.md`: 90 + 139 (Waves 1c-3 backfill, distinct parameter sets, `reconstructed=yes`). Same basis WAVE3_report.md's own N_raw=255/316 figures were drawn from at earlier ledger snapshots. |
| 383 | Gap-note upper bound | 90 + 293 (every backfilled ledger row incl. cost-stress/slip re-runs of the same config counted separately). |
| 499 | HASH01 updated lower bound (2026-08-10) | 90 + 139 + 270 (post-gap-note `tested_configs.csv` seq 230-498, distinct seq/letter-id slots). Supersedes the 229-383 bracket — 270 more trial-slots were logged in the interim. |
| 653 | HASH01 updated upper bound (2026-08-10) | 90 + 293 + 270. |

### 1.2 R6 Harvey-Liu Bonferroni haircut Sharpe (function of `N` and the series only — no `V` needed)

This is the exact function that produced every prior "haircut Sharpe = 0.000" figure in
`REGISTRY_GAP_NOTE.md`, `CAMPAIGN_STATE.md`, and `WAVE3_report.md` (there run at N_raw=316). Only
`N` is swept here; nothing else about the calculation changes.

| N | A_FULL haircut Sharpe | A_FULL passes BHY | B_FULL haircut Sharpe | B_FULL passes BHY |
|--:|--:|:--:|--:|:--:|
| 90 | **0.3768** | false | **0.1345** | false |
| 229 | 0.0000 | false | 0.0000 | false |
| 383 | 0.0000 | false | 0.0000 | false |
| 499 | 0.0000 | false | 0.0000 | false |
| 653 | 0.0000 | false | 0.0000 | false |

**Finding.** At every `N` in the wider bracket the task asked about (229, 383, 499, 653), the
haircut Sharpe stays at **0.000 and fails BHY for both candidates** — the campaign's prior
conclusion holds unchanged, qualitatively, from 229-383 out to 499-653. The one place the answer
is *not* uniform is `N=90`: there, some signal survives the Bonferroni correction (A_FULL 0.377,
B_FULL 0.135). `N=90` is also the only assumption with an unbroken contemporaneous paper trail.
This N=90-vs-N>=229 threshold was not visible in the campaign's own prior reporting, which jumped
straight from an assumed N~255-316 to the 229-383 bracket without ever tabulating N=90 as its own
row. It is reported here as a genuine, previously-undisclosed sensitivity — not as grounds to
prefer N=90 (sec61-66 forbids picking the assumption that gives the best number, and N=90 is also
the assumption that most understates how many configurations were actually looked at before these
two were treated as incumbents).

### 1.3 Bailey-Lopez de Prado Deflated Sharpe Ratio proper (needs a second input, `V`)

`deflated_sharpe()` needs `V` (cross-sectional variance of trial Sharpes), which is **not** a
function of `N` alone — it was computed once, campaign-wide, under the preregistered R2-R4
clustering pipeline in `WAVE3_report.md` §4: N_eff=5, V=0.645 (std 0.803), on a 213-trial pool.
No comparable `V` exists for any of the wider `N` assumptions (no full daily-P&L pool for
N=499-653 has ever been assembled — HASH01's own report explicitly found no full-registry pool
exists). Per "change nothing else about the calculation as `N` varies," `V` is **held fixed at
0.645** while `N` is substituted directly for `n_eff` — flagged explicitly as a diagnostic, not an
endorsed estimator, since `V` and `N_eff` were originally computed together and are not
independently portable.

| N | A_FULL DSR (V=0.645 fixed) | B_FULL DSR (V=0.645 fixed) |
|--:|--:|--:|
| 90 | 0.0531 | 0.0381 |
| 229 | 0.0137 | 0.0095 |
| 383 | 0.0061 | 0.0042 |
| 499 | 0.0039 | 0.0027 |
| 653 | 0.0025 | 0.0017 |

Under the campaign's own last preregistered `V`, DSR never approaches the R7 promotion bar
(>=0.90) at any `N` in the bracket, for either candidate — and it *decreases* monotonically as `N`
grows, mechanically, because a larger assumed trial count raises the benchmark Sharpe `SR0` that
the realized Sharpe is tested against.

### 1.4 `V`-sensitivity grid — the number is dominated by `V`, not by `N`

A companion sweep (`out/dsr_v_sensitivity.csv`/`.json`) holds `N` fixed at each of the five values
above and varies `V` over every value disclosed anywhere in the campaign's own record
(`TRIAL_ACCOUNTING_RULE.md`'s "honest pool" bounds 0.40/0.50, WAVE3's primary 0.645, and WAVE3's
own disclosed-but-explicitly-not-for-promotion "mechanically-broken-arms-removed" sensitivity
0.027):

| V | Label | A_FULL DSR range (N=90 to 653) | B_FULL DSR range (N=90 to 653) |
|--:|---|---|---|
| 0.645 | Campaign's last preregistered value — **primary** | 0.053 to 0.002 | 0.038 to 0.002 |
| 0.500 | `TRIAL_ACCOUNTING_RULE.md` honest-pool upper bound | 0.145 to 0.017 | 0.108 to 0.012 |
| 0.400 | `TRIAL_ACCOUNTING_RULE.md` honest-pool lower bound | 0.265 to 0.059 | 0.207 to 0.042 |
| 0.027 | WAVE3's own disclosed sensitivity — **explicitly not used for promotion** | 0.982 to 0.967 | 0.964 to 0.942 |

Holding `N` fixed and dropping `V` from 0.645 to WAVE3's own disclosed-but-not-used 0.027
sensitivity pushes DSR from ~0.05 up to ~0.94-0.98 for both candidates **at every `N` tested** —
i.e. it crosses the R7 promotion bar on the strength of the `V` assumption alone, independent of
which `N` is used. This reproduces, at the wider bracket, exactly the "the answer is dominated by
a judgement call, not the data" finding `WAVE3_report.md` already made at its narrower, single-`N`
snapshot. `V=0.027` is carried here only because it is already on the record as a disclosed
sensitivity, not because it is endorsed — WAVE3 itself declined to use it for promotion, and
nothing in this task changes that.

### 1.5 `N_eff` via participation ratio — deliberately not computed campaign-wide

Per the known facts and the task's explicit instruction not to force one: no defensible
campaign-wide daily-P&L correlation matrix exists. HASH01's own eigenvalue participation ratio
(PR=1.015 ProductA / 1.070 ProductB, out of a maximum possible 7) covers only the 7-config
VolMult-grid family (GRID01 G7/G13/G25/G49 + GRID02's 3 endpoints) — roughly 1.1-1.4% of the
lower-bound 499-trial-slot registry. HASH01's own report explicitly warns that figure must never
be quoted as representative of the full registry; this task does not override that warning. It is
carried through the outputs (`out/dsr_results.json`
-> `context_N_eff_participation_ratio`) as **labeled context only**, with no DSR number attached to
it, and it is a different candidate family from `A_FULL`/`B_FULL` — it says nothing directly about
either incumbent's own effective trial count.

### 1.6 Bottom line, §1

At the wider `N=499-653` bracket the campaign's selection-adjusted evidence for A_FULL/B_FULL
remains weak by every measure computed here — Bonferroni haircut 0.000 (fails BHY); Bailey DSR
0.002-0.004 under the campaign's own `V` — unchanged in kind from the 229-383 conclusion already
on record. The one new, honestly-surfaced wrinkle is the N=90 threshold effect in §1.2, and the
confirmation in §1.4 that the Bailey-DSR number is far more sensitive to which `V` a reader
chooses to believe than to which `N` they choose to believe. Neither observation resolves sec66's
underlying preregistration gap; both extend the campaign's own existing disclosed sensitivities
one bracket further and find no qualitative change.

---

## 2. PBO (CSCV) — assessed as NOT DEFENSIBLE on the only available candidate family

**Candidate family available.** The only pre-existing family with full daily P&L *and* candidate
identities that existed before scoring (per sec63's PBO requirement) is the VolMult-grid family:
GRID01's G7/G13/G25/G49 plus GRID02's three endpoint perturbations — 7 raw configs, reused from
HASH01's own dedup/participation-ratio work verbatim (no P&L rebuilt, no correlation recomputed).

**Two independently-sufficient blocking reasons** (either alone would block a defensible CSCV run
here):

1. **Rank-statistic resolution.** HASH01's own dedup finds exactly one exact-duplicate pair
   (GRID02 `endpoint_6_30` = GRID01 `G13`), leaving **N=6 behaviorally-distinct configs**. CSCV's
   rank statistic has at most `N` possible support values per split — with N=6 that is far coarser
   than the resolution the method needs, and well below the dozens-to-thousands of candidates
   typical published CSCV applications use.
2. **Near-collinearity.** By HASH01's own eigenvalue participation ratio, those 6 configs behave
   as roughly **one** effective independent dimension (PR=1.015 ProductA / 1.070 ProductB out of a
   max of 7). Confirmed here by pairwise full-history daily-P&L correlation among the 6 unique
   configs: ProductA median r=0.9907 (min 0.9857), ProductB median r=0.9535 (min 0.9296); 9/15
   ProductA pairs already clear r>=0.99. This was a density/robustness probe around one incumbent,
   not a search over meaningfully different strategies — CSCV on it would measure rank-statistic
   noise on ~1 effective dimension, not a real selection-induced overfitting risk.

A third, **supporting-only** reason: GRID01/GRID02's own `REPORT.md` files self-adjudicate as
diagnostic-only ("No winner is selected. No candidate is promoted or frozen."), including GRID02
explicitly declining to treat its one numerically-outperforming config as a selection signal
("a three-point comparison is far too coarse to support such a decision even if it were in
scope").

**Explicitly not the blocking constraint: sub-period data length.** Both the canonical window (539
sessions, ~33.7 obs/sub-period at S=16) and the full history (1,184 sessions, ~74.0
obs/sub-period) comfortably support S=16 sub-periods (C(16,8)=12,870 combinations). This is a
candidate-diversity problem, not a data-length problem, and is reported as such rather than
blurred into a generic "not enough data" excuse.

**Result.** Per campaign directive sec64's explicit instruction, no CSCV was run and **no PBO
percentage is reported anywhere** in this output.

---

## 3. SPA (Hansen) — no natural target in this pass

Hansen's SPA test requires an adjudicated *apparently superior* alternative against a stated
benchmark as its input. Reviewing the final adjudications of the four candidate-generating
exercises available:

| Source | Final adjudication (quoted) |
|---|---|
| `SIMPLE01_MINIMUM_SYSTEM/REPORT.md` (headline + §8.3) | "zero rungs pass, for either product" — a non-inferiority test; nothing cleared even that weaker bar. |
| `GRID01_SOLAR_RESOLUTION_CONVERGENCE/REPORT.md` | "Diagnostic-only sweep ... No winner is selected. No candidate is promoted or frozen." |
| `GRID02_ENDPOINT_PERTURBATION/REPORT.md` | The one place a raw number nominally "outperforms" the incumbent (2 of 3 endpoints beat [6,30] on one product each) — and the report itself refuses to read that as a selection signal, calling a three-point comparison "far too coarse to support such a decision even if it were in scope." |
| `PERT01_STRUCTURAL_INVARIANCE/REPORT.md` | "Diagnostic-only ... No winner is selected. No candidate is promoted or frozen." |

None of the four ever adjudicated a candidate as apparently superior to a benchmark. Per campaign
directive sec65's explicit instruction, no artificial "superior candidate" was manufactured to
produce an SPA p-value, and **no SPA was run**. If a future task does produce a genuinely
adjudicated apparently-superior candidate, SPA is the right tool to reach for then — not
retrofitted onto this wave's diagnostic-only results.

---

## 4. Cross-reference — the campaign's independent falsification evidence (not re-derived here)

Per sec62: weak selection-adjusted evidence (§1) must not be silently converted into "no real
mechanism" without weighing it alongside the campaign's other, independent evidence. That evidence
already exists and is not re-derived by this task — it is cross-referenced:

- **PLACEBO01 (component causality, 4 tests).** MIXED for B-MOM (favorable on Sharpe/Net/maxDD
  percentiles, but turnover percentile at 100.0/15.9 — the real path is far more active than
  almost every placebo draw, an artifact-consistent signature); CONCERNING for HTF/`tiltState`
  (both products, both headline metrics, sit *below* the null median under within-year block
  reordering); directionally favorable but not tail-significant for Product-B hysteresis(3,1);
  and Product-A's continuous sizing is judged substantially a turnover/denominator artifact, with
  one real residual caveat. This is evidence about *mechanism*, orthogonal to the trial-count
  question §1 addresses — a component can be causally real or artifactual independent of how many
  total configurations the campaign tried.
- **SIMPLE01 (minimum-system non-inferiority).** Zero rungs (of 5 tested: A0/A1/A2, B0/B1) pass
  the full preregistered non-inferiority ladder against A_FULL/B_FULL, even after a completion
  pass closed every previously-open gap. Read together with §1: not only is the *statistical*
  evidence for A_FULL/B_FULL weak against a trial-count-adjusted null, the campaign also could not
  show a *simpler* architecture is non-inferior to either — i.e. whatever the incumbents are
  doing, ablating pieces of them measurably hurts, on this evidence, even though the whole is not
  shown to survive a haircut Sharpe.
- **EQV01-EQV03 (finite-state equivalence, full-history array equality, PnL equality).** All
  EXACT_EQUIVALENCE, 0 mismatches, both products, every window/basis tested. This class of
  evidence establishes that the incumbents' *own reported numbers are computed correctly and
  reproducibly* — it says nothing about whether those numbers reflect a real edge versus
  selection artifact (the question §1-3 address), but it does rule out "the weak DSR is because
  the underlying P&L series itself is wrong or unreproducible."
- **GRID01/GRID02/PERT01 (resolution convergence, endpoint perturbation, structural
  invariance).** All three are preregistered, diagnostic-only, and self-adjudicate "no winner
  selected, no candidate promoted" — consistent with §2/§3's finding that none of them produced an
  input PBO/SPA could act on, and independently establishing that the incumbents are not
  hair-trigger sensitive to small parameter perturbations around their current settings (a
  different robustness question from the trial-count question this task addresses).

**None of the above is re-derived, re-scored, or re-adjudicated by this task.** They are listed so
this report's weak-DSR finding is read in the context sec62 requires, not in isolation.

---

## 5. What this task is, and is not

This is a bookkeeping/statistical audit: it recomputes an already-implemented statistic under a
wider, honestly-disclosed range of inputs, and separately documents why two other standard
selection-robustness tools (PBO, SPA) have no defensible application to the material currently on
hand. It does not:

- restore the campaign's lost preregistration guarantee (sec66) — no amount of post-hoc
  sensitivity analysis can prove what pass/fail criteria were fixed in advance for Waves 1c-3 or
  the 2026-08-09/10 wave's same-commit spec+result pattern (`REGISTRY_GAP_NOTE.md` addendum);
- select or endorse a preferred `N` or `V` — every defensible value is reported side by side,
  per sec61-66;
- promote or reject A_FULL or B_FULL — that decision, if ever revisited, belongs to a governance
  process outside this task's scope, and the campaign is formally closed (`CAMPAIGN_STATE.md`
  §9b);
- convert "selection-adjusted evidence is weak" into "there is no real mechanism" — §4 lists the
  independent, non-redundant evidence a reader would also need to weigh, per sec62, before drawing
  that stronger conclusion.

**Bottom line.** At the wider N=499-653 bracket the campaign's selection-adjusted evidence for
A_FULL/B_FULL remains weak by every measure computed here (Bonferroni haircut 0.000/fails BHY;
Bailey DSR 0.002-0.004 under the campaign's own V), unchanged in kind from the previously-published
229-383 conclusion. The Bailey-DSR number is shown to be far more sensitive to the `V` assumption
than to `N` (§1.4), reproducing WAVE3's own "dominated by a judgement call, not the data" finding
at the wider bracket too. PBO is not reported anywhere (family too small/collinear, §2); SPA is
not reported anywhere (no adjudicated superior candidate exists in this wave, §3). This extends the
campaign's existing disclosed sensitivities one bracket further; it does not resolve them.
