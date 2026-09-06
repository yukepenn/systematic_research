# CARRY_SIGC_CONFIRM_20260906 — REPORT

**Ledger G00070 · family GENESIS3_RV · executed 2026-09-06 · one-shot, windows SPENT.**
Design: `DESIGN_FROZEN.md` sha256 `62d5a342c1e22daf52aebb0e415ca0b63607112380d5124be06f4bb02ca088a2` (verified at execution). Spec committed before results (`d430b98`).

## Verdict

**INVALID-RUN → ledger DEFECT.** The preregistered G4a/G4b agreement clause tripped: circular-shift null percentile **63.3** vs 13-week block-permutation percentile **73.7**, |d| = **10.4 pts > 5**. Per §6/§8 this is adjudicated, not pass/fail; the evidence windows count as **spent** (CONSUMED marker written at panel load). The CARRY_V1 dev verdict (FAILED/CLOSED) is unchanged.

**What the spent windows actually said (stated plainly, so the DEFECT label cannot hide it):** both null computations agree the headline result is *not* in the tail — 63.3 and 73.7 are both far below the 95 bar. Had the agreement clause not tripped, **G4a fails under both computations** and the mechanical outcome would have been **ACCIDENTAL WINNER — PERMANENT CLOSURE**. The confirmation era did not reproduce the dev *switching* relation: the switch was long-SI **97.5%** of live weeks (dev 66.3%) with **4** sign flips (dev 75), and its long-SI-state P&L ($155,877) is statistically indistinguishable from the static long-SI control ($156,012). The $157,547 headline net is the 2019–2026 silver rally worn as a carry signal; any composition-preserving shuffle of the weight stream earns Sharpe ~0.65–0.68, which is why the null centers there. G8 passed by 0.723 vs 0.708 — a 0.015 margin that corroborates the same reading. H1 (a live conditional inventory/dislocation relation) is not supported by these windows; H0/selection (accidental winner riding a silver decade, take two) fits everything observed.

## Phase A — dev reproduction (all before any post-2018 row; 6/6 PASS)

| gate | spec | observed | verdict |
|---|---|---|---|
| A-DIFF | exactly 2 sanctioned changes | contract range 2017–2027 + window constants 2018-01-02/2026-08-01, nothing else | PASS |
| A-UT s6/s7 | all pass | telescoping 0.0, basis-invariance 8e-13, roll causality both clauses | PASS |
| A-ROOTS | 10 roots | 10 roots | PASS |
| R0a construction identity | 3,421 rows match 100% | 3421/3421, max\|dw\| 7.98e-17 | PASS |
| R0b pair identity + economics | 696/696, absent {2012-W49, 2013-W49}, $286,211±500, 0.932±0.005 | 696/696, 0 sign contradictions, absent exactly as expected, **$286,211 / 0.932** | PASS |
| R2 dev family rank | GC/SI 1 of 9 | 1 of 9 | PASS |

MDE (committed §7) printed: only a P1-class persistent effect passes; a halved edge most likely fails.

**Defect caught by the Phase-A smoke, before any confirmation data:** my null machinery zeroed CASH weeks, but the frozen `simulate()` ffills through them (a stale-pair week *persists* the prior position) — dev discrepancy $40,612. Fixed to replicate frozen semantics; k=0 pivot reconstruction asserted equal to direct simulate ($0.000000); Phase A fully re-run; marker hash discipline held (Phase B refuses on any code drift).

## Phase B — one-shot confirmation

Panel: 10 roots, warmup 2018-01-02, seal assert max session **2026-07-31 < 2026-08-01** PASS. CONSUMED written at load. R1 two-sided causality on the confirmation pair panel: future 0.0e+00 / past 1.0e+00, PASS.

### Gate table (program-printed; full table in `out/confirm.txt`)

| gate | spec | observed | verdict |
|---|---|---|---|
| R1 causality | future<1e-12, past>1e-9 | 0.0 / 1.0 | PASS |
| SEAL | < 2026-08-01 | 2026-07-31 | PASS |
| G1 HL PRIMARY net > 0 | > $0 | $157,547 | PASS |
| G2 HL Sharpe | ≥ 0.45 | 0.723 | PASS |
| G3 W1 and W2 net > 0 | each > 0 | $42,204 / $115,344 | PASS |
| **G4a null percentile** | ≥ 95.0 | **63.3** | **FAIL** |
| **G4b agreement** | \|d\| ≤ 5 | **73.7 vs 63.3, \|d\|=10.4** | **FAIL → INVALID-RUN** |
| G5 family rank | ≤ 2 of 9 | 2 of 9 (ZC/ZW 0.754 ranks 1) | PASS |
| G6a STRESS-A net | > $0 | $156,496 | PASS |
| G6b STRESS-B net | > $0 | $155,463 | PASS |
| G8 beats both static arms | Sharpe > both | 0.723 vs +0.708 / −0.717 | PASS (margin 0.015) |
| COV coverage clause | ≥ 50% CARRY00 frac | GC 0.527/0.594, SI 0.558/0.602 | PASS |
| G7 yearly | REPORT-ONLY | 5/7 positive years | — |

All figures: **PRE-FROZEN (spent this execution) · MODELED costs (COMMISSION+SPREAD, never "all-in") · research sizing.**

### Nulls (the probability wording rule)

G4a event in words: *the probability, under timing-destroyed signals that preserve each series' serial structure and the family's cross-pair dependence, of a HEADLINE net Sharpe at least as large as observed.* Circular shift, all 199 offsets k∈[26, N−26] on the N=250-week headline grid, P&L and costs recomputed per shift, same offset construction across all 9 pairs: null mean Sharpe **+0.679** sd 0.112 → percentile **63.3**. G4b second computation, 13-week block permutation (999 draws, seed 20260906): null mean **+0.646** sd 0.138 → percentile **73.7**. The null *means* are the finding: a shuffled stream keeps ~94% of the observed Sharpe because it keeps the 97.5% long-SI composition.

### Family (headline PRIMARY Sharpe / net)

ZC/ZW 0.754/$1,229 · **GC/SI 0.723/$157,547** · ZW/ZL 0.619/$14,633 · ZM/ZL 0.562/$13,277 · ZC/ZL 0.393/$9,189 · ZW/ZM 0.169/$661 · ZC/ZM 0.037/$136 · ES/YM −0.538/−$939 · ZN/ZB −0.949/−$16,845. Full per-window/per-arm table with G4a percentiles: `out/family_table.csv`.

### G7 diagnostics (report-only)

Years: 2019 −$6,247 · 2020 +$40,346 · 2021 −$17,505 · 2022 +$25,610 · 2023 +$5,791 · 2024 +$34,605 · 2025 +$61,103 · 2026 Jan–May +$13,846 (5/7 positive). Turnover 0.0351; drag 0.8/1.4/2.1% across arms — cost immaterial, as designed. Realized gaps: median 2mo all windows (dev 2mo). State split: long-SI 1,078 days switch $155,877 vs static-SI $156,012 / static-GC −$157,497; long-GC 24 days switch $1,650. Orthogonality vs P1/PCT: **NOT-COMPUTED** (no in-run P1 weekly P&L artifact; outside the frozen code surface). ANNEX (BURNED, non-gating, `out/annex.txt`): −$16,847 over 40 days.

## Anomalies and honesty items

1. **The INVALID-RUN is an agreement-clause artifact, not a machinery defect found:** the two null classes have genuinely different dispersions (0.112 vs 0.138) and the observed statistic sits mid-distribution, where percentiles are maximally sensitive; the 5-pt clause was implicitly calibrated for the tail. Recorded as tripped; not reinterpreted.
2. **GC pairing ends 2026-03-27** (no GC deferred leg in the store after that); the final ~2 months of W2 persist the last position via the frozen ffill semantics (benchmarked identically in dev). Coverage clause passes anyway.
3. Headline weekly grid is 250 of ~387 calendar weeks (pairing holes; dev analogue 350/421).
4. Implementation choices not pinned by the design, fixed in code before Phase B: G4b n=999/seed 20260906; mid-rank percentile convention.
5. G5 passed exactly at the bound; the pair that outranks (ZC/ZW) nets only $1,229.

## Consequences (per §8, for coordinator/owner adjudication)

The rule book maps this run to **INVALID-RUN / ledger DEFECT** with the windows spent. No promotion; no closure is auto-executed by this label — but the record must carry that both null computations, the flip collapse (4 vs 75), and the state-split all point the same way: **the dev SI/GC conditional relation did not persist; what the windows contain is a static long-silver drift already priced by the null family.** Any V2 requires new information, its own prereg, explicit multiplicity debt, and an EVI win. LIVE ENABLED = NO; nothing here touches the live book.

Artifacts: `out/confirm.txt`, `out/confirm_verdict.json`, `out/family_table.csv`, `out/sigc_daily_headline.csv`, `out/annex.txt`, `out/phase_a.txt`, `out/phase_a_result.json`, `out/PHASE_A_PASS`, `out/CONSUMED`; code `src/carry_confirm.py` (2-line diff), `src/run_confirm.py`.