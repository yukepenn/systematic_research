# G3_RATESCARRY_20260906 — REPORT

**Verdict: INVALID-RUN (split null verdict) — ledger G00081: DEFECT.** The preregistered
G2b clause (`agreement judged TAIL-SIDE (both above or both below the bar); split
verdicts = INVALID-RUN`) fired: the circular-shift null put the observed pool mean at the
**97.3** percentile (BELOW the 97.5 debt-tightened bar) while the 13-week
block-permutation null put it at **98.5** (ABOVE the bar). The two null computations
disagree about which side of the bar the object sits on, so the run **cannot deliver a
verdict in either direction** and is recorded exactly as the spec pre-declared.

Evidence status: **DISCOVERY_CONSUMED** on every table — the per-root arms were observed
as positive controls in G00074 *before* this registration; the selection debt was priced
by (a) the null bar tightened to 97.5 and (b) mandatory victory over both
exposure-matched static arms. The 2026-06/07 segment lies in the globally BURNED window;
no forward claim. Costs MODELED ($4.36 RT + 1-tick primary / 2-tick stress per leg,
BASIS: modeled, not measured). Seal asserted by the program: max session 2026-07-31.

## What was tested (frozen object, zero free parameters)

Per root i ∈ {ZN, ZB}, weekly ISO, decision = last observation strictly before the
week's first trading day: `position_t = sign(carry_i,t)`,
`carry = (P_near − P_deferred)/month_gap / sigma_63d` — CARRY_V1/G00074 construction
**verbatim**. Always in, long or short, sized 1/sigma_i. Both roots separately and as the
equal-vol pool (headline). Machinery reuse was **byte-verified**: `carry_znzb.py`,
`run_znzb.py`, `ncd_day.py`, `roll.py` sha256 == G00074's recorded hashes; the per-root
arms reproduce G00074's `outright_control.csv` to $4.6e-13 (RECON-B); pool = armZN +
armZB to $9.1e-13 (RECON-A); pivot reconstruction exact (RECON-C); s6/s7 unit tests and
the two-sided causality probe pass.

## Headline numbers [DISCOVERY_CONSUMED, MODELED costs]

| quantity | value |
|---|---|
| N (ISO weeks with P&L) | 596 (matches spec expectation) |
| MDE, printed before observed | **$199/week** (≈ ann Sharpe 0.83 at 80% power) |
| pool after-cost weekly mean (PRIMARY) | **+$178.56** — BELOW the powered MDE |
| pool total gross / cost / net | $117,203 / $10,778 / **$106,425** |
| pool ann Sharpe (weekly basis) | **0.743** |
| STRESS (2-tick) total net / weekly mean | $97,523 / $163.63 |
| 95% block-bootstrap CI of weekly mean | **[$29.20, $327.97]** (13-wk blocks, seed 20260916) |
| circular-shift null percentile | **97.3** (595 offsets; bar 97.5) — FAIL by ~2 offsets |
| block-permutation null percentile | **98.5** (2000 draws, 46 blocks, seed 20260918) — above bar |
| G2b tail-side agreement | **SPLIT → INVALID-RUN** |
| arm ZN / arm ZB | +$47,713 (S 0.611) / +$58,711 (S 0.701) — = G00074 controls exactly |
| static always-LONG / always-SHORT | +$55,960 (S 0.360) / −$75,535 (S −0.487) |
| alpha vs static-LONG | **+$127.59/wk**, CI [$20.29, $243.49], beta 0.543, R² 0.346 (seed 20260917) |
| era cells (pool) 2009-15 / 2016-21 / 2022-26 | **+$74,114 / +$9,016 / +$23,295** — all positive |
| 2022-26: pool vs static-LONG | **+$23,295 vs −$22,248** — timing delivered through the bear |
| long share of decided weeks | ZN 80.6%, ZB 77.4% (the mostly-long threat, quantified) |
| weekly turnover / cost | 0.7223 dUnits / $18.08 (1tk), $33.02 (2tk) |
| weekly maxDD / CDaR95 (dollar descriptors only) | $25,886 / $21,192 |
| rho to P1 (daily / weekly) | −0.0069 / +0.0362 (spec expectation ~−0.05 class: same near-zero class) |

Program-printed gate table: `out/gate_table.txt`. Console: `out/ratescarry_console.txt`.
Weekly P&L (pool + arms + stress): `out/weekly_pnl.csv`. Static arms:
`out/static_arms.csv`. Eras: `out/era_table.csv`. Machine verdict:
`out/ratescarry_verdict.json`.

## Gate outcomes (mechanical)

- G2a mean > 0: **PASS** (+$178.56). G2ci CI excludes 0: **PASS**. G2n shift-null ≥
  97.5: **FAIL at 97.3**. → G2 FAIL on one clause of three.
- G2b tail-side agreement: **SPLIT** (shift BELOW / perm ABOVE) → **INVALID-RUN** per
  the pre-declared clause. This supersedes the ordinary FAIL path.
- G3: **PASS all three clauses** — pool Sharpe 0.743 > both arms; alpha vs static-LONG
  CI entirely positive. The timing does NOT reduce to the bull.
- G4: **PASS** — the decisive 2022-26 cell is +$23,295 while always-long lost −$22,248
  there. Genuinely conditional behaviour, not the bull in disguise.

## What the split means (recorded, not argued around)

1. **Both nulls carry positive drift** (shift mean $47.39/wk, perm mean $43.67/wk): an
   always-in, mostly-long rates position stream earns bull drift under ANY timing, and
   both nulls correctly charge for it. The observed $178.56 sits ~2.1–2.3 null sd above
   — exactly at the 97.5 boundary, where the two routes' small construction differences
   decide the verdict.
2. **The shift-null verdict at this bar is decided by ~2 offsets**: resolution is
   1/595 ≈ 0.17 pctl; 16 of 595 offsets beat the observed (97.31); 14 would have passed
   (97.65). The bar sits inside the null's discreteness granularity.
3. **The debt pricing did its job.** Under G00074's un-tightened 95 bar both nulls agree
   ABOVE (97.3 and 98.5) and the run would have PASSed all gates. The 97.5 bar — the
   deliberate price of observing the controls first — is precisely what created the
   split. That is the system working, not failing: the honest statement is "at the
   debt-priced evidence standard, the data cannot adjudicate this object."
4. INVALID-RUN means **no verdict either way**: the object is neither promoted nor
   closed-as-refuted at scope. Any re-test must be a NEW registration with a
   pre-committed resolution for boundary discreteness (e.g., a bar expressed in whole
   offsets, or a single pre-named primary null), and it inherits this run's consumed
   discovery as additional debt.

## Anomalies

- **A1 — the split itself** (above): genuine conflict between the two preregistered null
  computations, straddling the bar by 0.2 / 1.0 pctl. Recorded; decision rule applied
  mechanically.
- **A2 — observed edge below its own MDE** ($178.56 vs $199/wk): the design predicted a
  marginal read even before the split; at N=596 this object cannot be powered into the
  debt bar without more data (forward evidence is the only non-debt-increasing source).
- **A3 — 5 exact-zero carries** (of 1008 root-weeks): sign(0)=0 makes that root flat for
  that week, so "always in" holds in 1003/1008 root-weeks and the exposure match to the
  static arms differs on those 5 rows. Negligible but recorded.
- **A4 — rho-to-P1 sign**: weekly +0.036 vs the spec's "~−0.05 class" expectation — same
  near-zero orthogonality class, opposite sign; daily is −0.007. Report-only.
- **A5 — panel starts 2009-06-29**, not 2009-01-01 (63d sigma warmup + pairing), same as
  G00074; N matches the spec's ~596 expectation exactly.

## Completion note for the G00074 §28 block (spec: "either way")

> The adjacent-question fork "outright rates carry-timing (ZN/ZB controls positive,
> selection caveat)" was given its own registered, debt-priced trial as
> `G3_RATESCARRY_20260906` (G00081) on 2026-09-06. Outcome: **INVALID-RUN (split null
> verdict, ledger DEFECT)** — pool +$178.56/wk (S 0.74), CI [+$29, +$328], alpha vs
> static-long CI entirely positive, all three era cells positive including 2022-26
> (+$23.3k while always-long lost −$22.2k), but the shift null read 97.3 vs the 97.5
> debt bar while the permutation null read 98.5 — a tail-side split the spec pre-declared
> INVALID. The object is neither promoted nor refuted; the fork is no longer "unpriced",
> and any successor registration inherits this run's consumed discovery.

## Ledger

G00081, family GENESIS3_RV: **DEFECT (INVALID-RUN)**, registered before outcomes,
recorded exactly as the decision rule produced it. Seeds: shift null deterministic
all-offsets; block bootstrap 13-wk, mean CI 20260916, alpha CI 20260917; permutation
null 20260918 (2000 draws).

*(Note: the harness refused writing REPORT.md into the run directory; this content is
returned here per instruction. All program-generated artifacts exist under
`runs/G3_RATESCARRY_20260906/out/` and `src/run_ratescarry.py`.)*