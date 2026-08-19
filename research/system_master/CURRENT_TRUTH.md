# CURRENT_TRUTH — single page, updated after every wave

## WAVE 2026-08-18 — OUTSIDE_VIEW review + HTFDIR01 construction (1 alpha hypothesis consumed)

**Supersedes the 2026-08-14 section below for anything it touches.**

- **OUTSIDE_VIEW_20260818.md** (new): four independent third-party perspectives (allocator /
  risk committee / alpha anatomy / research-director lever ranking), every number checked by a
  second agent. Headlines: raw Sharpe real but selection-adjusted evidence ≈ 0 (Harvey-Liu 0.000,
  DSR ~0.003 at the honest N=499-653 bracket) → the fundable evidence is the FORWARD calendar;
  concentration on every axis (one instrument, one family, 2022 = ~39% of B-NQ net, top-10 days
  52-62% of net, long Sharpe 1.540 vs short 0.179); the owner's daily-consistency wish is
  structurally incompatible with this edge (44-47% positive days; every smoothing construction
  killed) — consistency lives at week/month horizon and the only honest daily-consistency lever
  is another near-zero-ρ engine. **Correction of record surfaced by the check pass: the
  S-resampling "untouched surface" (Wave-18 §7) was in fact tested and CLOSED UNCONDITIONALLY by
  the Wave-18 red team's de-confounded constructions (ΔSharpe −0.303, P=0.116; seq 464-465) —
  do not re-queue it.**
- **HTFDIR01** (spec fb44d67 frozen pre-readout): direction-conditioned HTF tilt (LONGONLY
  up-weight, zero new constants) + SHORTONLY falsification control. **Product B: PASS-SCREEN on
  every frozen gate** (net $301,916→$323,979, Sharpe 1.113→1.198, P=0.9556, LOYO min +0.051,
  retention 99.4%, CDaR improves; control failed as predicted). **Product A: FAIL** (honest,
  and mechanistically coherent — see report). **Four-attacker red team: no kill, but BINDING
  corrections**: 86.4% of the B delta is 2025-26 (pre-2025-04 P=0.585; −$55.76 inside
  HTFMECH01's own window; post-dev Jun-Jul extension ADVERSE both products); the effect =
  conditional trim of marginal hysteresis-threshold shorts + real long-side tilt value
  (beats NOTILT placebo P≈0.94), NOT "new HTF information"; HTFMECH01's A-side −$22,020
  conflated two channels (correction appended there). **Disposition: NT8-parity promotion step
  queued READY but NOT started — recommended instead: owner-authorized candidate shadow ledger
  at MONITOR-01 readings, letting forward data separate "regime bet that peaked" from
  "structural trim" before any build spend.** A-side direction-conditioning CLOSED (one shot).
  Full report: `HTFDIR01_DIRECTIONAL_TILT/REPORT.md`. Registry: TESTING_LEDGER row 2026-08-18.

> **READER'S CORRECTIONS INDEX (2026-08-18 consolidation pass — 5 traps in the layers below):**
> (1) Two different things are named **"B1"**: the *SYSTEM_MASTER frozen challenger* (drop-HTF
> Product-B variant, implementation-certified, INCONCLUSIVE on Sharpe, revival per
> `B1_FUTURE_CONFIRMATION_SPEC.md`) vs the *scalping-lab/portfolio "B1 overnight" sleeve*
> (parked-marginal, demoted from an ablation gate). Context decides; they share nothing but the name.
> (2) Any "holdout clean/untouched" line below the top layers is superseded — SM11 consumed
> 2026-06/07 on 2026-08-08 for **everything** (`HOLDOUT_DETERMINATION_20260809.md`).
> (3) Per-object nets $303,239.64 / $177,315 / $28,705.20 / $28,900.70 in lower layers are
> superseded by `/BASELINE_MODELS.md` ($301,915.92 / $177,924.40 / $28,587.10).
> (4) The $75,449.60 figure and the "$2,575 gap" are **UNVERIFIED — DO NOT CITE** (Wave-18 §6).
> (5) `SYSTEM_FRONTIER.yaml` / `SYSTEM_SCORECARD.md` named in old layers no longer exist
> (archived). Repo-wide current map: **`/STATE_OF_RESEARCH_20260818.md`**.

## RETURN TO PRIMARY RESEARCH PROGRAM — 2026-08-14 (non-DOM frontier re-ranked, HTFMECH01 closed)

DOM branch stays `PAUSED` (see policy note directly below, unchanged). Re-read `BASELINE_MODELS.md`,
`ACTIVE_RESEARCH_QUEUE.md`, `RESEARCH_FRONTIER.md`, and
`STRUCTURAL_INVARIANCE_MINIMUM_SYSTEM_SYNTHESIS.md`; re-ranked the remaining non-DOM frontier by
EVI (full table: `ACTIVE_RESEARCH_QUEUE.md`). Excluded from consideration per standing instruction:
DOM/Replay, B1 historical tuning, ACTIONMAP01, U6B, generic OHLCV feature mining (8 independently-
built feature families already show a consistent right-tail-unsafe-or-too-small failure pattern).

**Top-ranked item actioned this wave: HTFMECH01**, a pure diagnostic decomposing PLACEBO01's
already-established finding (HTF's marginal contribution sits below its own randomized-chronology
null, the weakest-evidenced live component per two independent methods —
`STRUCTURAL_INVARIANCE_MINIMUM_SYSTEM_SYNTHESIS.md`'s own named future-work target). **Real,
corroborated result, no promotion**: HTF's underperformance is not uniform across years, but is
sharply concentrated by direction — value-additive on longs, value-destructive on shorts (Product A
short-side cost −$22,020, over 3.5× the whole-window net positive), independently corroborated by
SA0/PA0/PA1's own long/short asymmetry findings. Sharpens, does not resolve, the open HTF question.
No incumbent file touched, no `B1` file touched, no construction attempted. Full report:
`research/system_master/HTFMECH01_TILT_MECHANISM/REPORT.md`. Next-ranked item (a
separately-preregistered direction-conditioned HTF construction test) queued `READY`, not started.

## DOM RESOURCE POLICY — effective 2026-08-12 (supersedes DOM01/DATA03 status below)

**Full-depth DOM / Level-II continuous collection is PAUSED**, following a workstation
resource-instability incident on 2026-08-12 during heavy DOM/Level-II/Market Replay work (the
machine became unstable and crashed; recovered). This is a risk-control decision — the
resource-heavy workflow coincided with instability, that is the extent of the claim; DOM work is
not shown to have caused a hardware failure. Until explicitly re-authorized: no continuous DOM
capture, no automated full-depth collection, no bulk Market Replay downloading, no background
Level-II collector. DOM-dependent research is not, and must not become, a prerequisite for
current baselines — **the baseline strategies work without DOM by design**; DOM/order-flow work
is downstream research only. Ordinary bars and required historical tick data remain allowed and
unaffected. Full record, cleanup manifest, and what was preserved vs. removed:
`research/system_master/DOM_PAUSE_CLEANUP_20260812.md`. The DOM01 collector
(`Dom01DepthRecorder_v1.cs`) now fail-closed defaults (`DomCollectionEnabled=false`) and will not
record anything until explicitly re-enabled with recorded owner authorization. Future
reconsideration should follow an improved resource architecture (more dedicated memory/storage or
an isolated compute environment), not simply "try again."

## SNAPSHOT UPDATE (2026-08-11, post-structural-invariance wave 1 CLOSED; DOM01 collecting)

**Supersedes every section below for anything it touches.** Full detail:
`research/system_master/ACTIVE_RESEARCH_QUEUE.md`, `RESEARCH_HANDOFF.md` (repo root).

- **EQV04 (NT8 canonical-object executable parity): PASS, bit-identical.** All three
  canonical/incumbent object pairs match trades and net P&L to the cent, two windows; Product A
  additionally bit-identical bar-by-bar across 165,861 bars. Specification finding only — incumbent
  files unchanged. `runs/EQV04_NT8_CANONICAL_PARITY/REPORT.md`.
- **B1 (frozen SIMPLE01 challenger, NT8 implementation): implementation-certified**, still frozen
  pending genuinely new confirmation. Diverges from the incumbent only and exactly where the
  one-line `mm`-forced-to-1.0 change predicts. Does **not** change B1's historical verdict (still
  INCONCLUSIVE on Sharpe) or open protected/locked-forward data.
  `runs/B1_NT8_IMPLEMENTATION_PARITY/REPORT.md`.
- **ACTIONMAP01 (Auction M5 action-value decomposition): CLOSED, CLEAN_INFORMATION_STATE /
  NO_CURRENT_ACTION_MAPPING.** No add/hold/reduce action space exists to decompose in this
  substrate — a definitional identity (no size term anywhere in the substrate), not an empirical
  failure. Auction is not retuned; M5's own univariate finding is preserved, unchanged, for future
  DOM interaction (sec146). `runs/ACTIONMAP01_AUCTION_ACTION_VALUE/REPORT.md`.
- **DOM01: genuinely collecting real Level-II depth** since 2026-08-11 (owner completed all 5
  start steps; `DataConnectionDisableL2Data=False`, live Tradovate connection verified, not
  Simulation). Not yet cleared for research use — see governance below.
- **New engineering infrastructure this wave**: `runs/DOM01_LIQUIDITY_STATE/collector/qc/
  dom01_qc_monitor.py` (feed/collection integrity QC only — file presence, timestamp
  monotonicity, malformed rows, crossed/locked-book incidence, heartbeat cadence, checksums; zero
  outcome/predictive computation); `research_sdk/session_boundary.py` (canonical
  `zoneinfo`-based timezone-aware NT8 window-boundary utility, replacing hand-picked seasonal UTC
  offsets — fixes the process-error class behind a near-miss during EQV04's smoke test where the
  wrong DST-season offset was used and only the CME weekend gap prevented an actual
  `LOCKED_FORWARD.md` boundary read); `research/data_forward_sealed/DOM01/
  DOM01_PROSPECTIVE_PROTOCOL.md` + `DOM01_DATA_GOVERNANCE.md` (exactly one DOM mechanism frozen —
  opposite-side depth withdrawal / adverse-selection quote-fade — with the full required
  preregistration template; zero DOM sessions read for any outcome purpose; data stays
  `SEALED_FORWARD` even once QC/sample-size readiness is met, pending explicit owner
  authorization, since `LOCKED_FORWARD.md` predates DOM01 and is read conservatively rather than
  as silent permission).
- **Zero incumbent code changed. Zero alpha promotions this wave.** Current honest state: core
  frozen, B1 frozen, protected evidence untouched, DOM accumulating, waiting for independent
  evidence — not a stall, the correct state per this wave's own owner directive.

## SNAPSHOT UPDATE (2026-08-09, SYSTEM ARCHITECTURE SCIENCE + ALPHA OPTIMIZATION campaign CLOSED)

**Supersedes the snapshot below for anything it touches.** The post-parity research campaign
(P0/R1/R2/R2V1, then the SYSTEM ARCHITECTURE SCIENCE MEGA DIRECTIVE's SA0/R3/R2B/R4/R5/R6/PA0/PA1)
ran to completion this same day. **Zero promotions. Both Product A (`SolarWaveSMMaster_v4`) and
Product B (`SolarWaveOneContractNQ_v5`/`SolarWaveOneContractMNQ_v5`) remain UNCHANGED.** Full
closing report: `research/system_master/SYSTEM_SCIENCE_20260809.md`. Architecture matrix:
`research/system_master/STRUCTURE_MAP.md`. Current-regime health (addendum):
`research/system_master/CURRENT_EDGE_HEALTH.md` — Product B assessed **HEALTHY** on the latest
available (non-locked) data, one WATCH flag (rolling-120 Sharpe, mechanically explained), no
decay evidence found; the short-side weakness that motivated the owner's April review is
temporally localized to Jan-May 2026 and reversed in the newly-available June-July data. Every
tested construction this pass either failed its own chronology/right-tail gate or was deferred as
a disclosed, not-yet-actionable lead — see `research/system_master/RESEARCH_FRONTIER.md` for the
per-family table. Project remains in RESEARCH MODE; no live-trading authorization exists or is
implied.

## SNAPSHOT (2026-08-09, repo consolidation pass — read this, skip the chronology below unless you need it)

**CURRENT BASELINES**: Product A = `SolarWaveSMMaster_v4.cs`. BEST_ONE_NQ = `SolarWaveOneContractNQ_v5.cs`.
BEST_ONE_MNQ = `SolarWaveOneContractMNQ_v5.cs`. Canonical record: `/BASELINE_MODELS.md` (repo root).

**CURRENT PARITY STATUS**: event-level decision mechanism proven correct for all 3 (DEFECT 3 —
a hardcoded-clock BMOM end-of-session flatten shared across all 3 objects — found via live-NT8
forensics and fixed). Full-history net-profit certification complete for all 3 (7-block chunked
harness, no gaps): BEST_ONE_NQ +4.13% vs Python (fully reconciled to two disclosed, non-defect
conventions), BEST_ONE_MNQ +4.41% (same), Product A +10.91% (directionally consistent with the
same conventions, not yet leg-proven to the dollar). See `runs/V1R4_NT8_PARITY/
FULL_HISTORY_CERTIFICATION.md`.

**CURRENT PERFORMANCE** (Python reference, full dev window 2022-01-03→2026-05-29): Product A net
$177,924.40 (Sharpe 1.1770, Sortino 2.3371, Calmar 2.2896, EOD MaxDD $17,192.90, CDaR95
$14,323.08). BEST_ONE_NQ net $301,915.92. BEST_ONE_MNQ net $28,587.10. Full battery for all 3:
`/BASELINE_MODELS.md`.

**CURRENT KNOWN LIMITATIONS**: Product A's full-history residual (+10.91%) not yet reduced to an
exact leg-level proof (continuous multi-contract FIFO sizing makes that materially more expensive
than for the binary one-contract objects). MNQ's older, independent 5-named-session gap is
CLOSED (traced to a different, already-superseded object; does not apply to current `_v5`).

**CURRENT RESEARCH STATUS**: S2_SELTIME adjudicated NOT PROMOTED for all 3 (own frozen R2 rule,
independently verified). All 8 named FINAL OPTIMIZATION DIRECTIVE families + Engine-3 cross-market
slate closed with disposition. No standing open-ended research queue.

**CURRENT NEXT PHASE**: `ENGINEERING / PARITY CAMPAIGN: CLOSED.` `PROJECT MODE: RESEARCH.` See
`/RESEARCH_HANDOFF.md` (repo root) for what's explicitly open and what should not simply be
rerun unchanged. No live-trading authorization exists or is implied.

---

_Full wave-by-wave chronology follows below, newest first, retained for audit history. The
snapshot above is the current-truth summary; nothing below should be read as more current than
it._

---

_Last update: 2026-08-09, **DEFECT 3 FOUND AND FIXED — EVENT-LEVEL FIRST-DIVERGENCE FORENSICS**
(same-day continuation, supersedes the S2 R2/parity section below for anything it touches). The
BEST_ONE_NQ ~18.8% Q1-2025 residual was driven to its exact first divergence via a leg-by-leg
(entry/exit timestamp + side + fill price, not just aggregate net profit) comparison against LIVE
NT8 trade output pulled through CrossTrade. Root cause: a real, previously-undiscovered
NinjaScript defect shared byte-for-byte across all 3 canonical objects' `BmomBar()` function --
the BMOM leg's own end-of-RTH flatten was still a HARDCODED CLOCK (`hm >= 155700`), never migrated
when the earlier C2/C3 work made the entry-block/forced-flat overlay session-relative. On a
holiday session ending before 15:57 ET (2025-02-17 Presidents Day: CME halts 13:00-18:00, matches
the raw data exactly), `hm` never reaches 155700, so a non-zero `bmomPos` survives stale into the
following overnight session -- confirmed on live NT8 output as an extra, wrong short entry at
2025-02-17 18:06 ET (M=-4.25 with the stale `bmomPos=-1`, vs the correct M=-1.42 at `bmomPos=0`).
11 of 44 early-close sessions in the dev window have `bmomPos != 0` at the truncation boundary and
would trigger this. **Fixed** with a one-line, non-signal change (`bmomPos` now also flattens on
`sessEnd`) in new versioned files `SolarWaveSMMaster_v4`, `SolarWaveOneContractNQ_v5`,
`SolarWaveOneContractMNQ_v5`, deployed to NT8 and independently re-verified against LIVE NT8
output: BEST_ONE_NQ's Q1-2025 leg-by-leg resync now finds **0 divergent decision episodes across
all 214 legs** (down from 1), and the residual net-profit gap reconciles EXACTLY, to the dollar,
to two already-understood, non-defect conventions (NT8's documented boundary trade-list
serialization quirk + Python's disclosed synthetic 1-tick fill convention) -- zero unexplained
residual. BEST_ONE_MNQ confirmed identically on live NT8 output (shared decision sequence).
Product A's instance of the same defect confirmed present in `_v3`'s source via direct grep and
fixed in `_v4` (smaller dollar impact there: continuous position sizing dampens a stale
`bmomPos`'s effect vs the one-contract objects' binary threshold). Full multi-year net-profit
certification remains open (CrossTrade long-job ceiling) but the event-level decision MECHANISM is
now proven correct, not merely "improved" -- see each object's updated certificate in
`runs/V1R4_NT8_PARITY/`. This is a genuine implementation-defect fix (one boolean OR clause), not
a re-optimization: every signal weight/threshold/formula is byte-identical to the pre-fix files.
Also this same session: 7 clearly-superseded stale NinjaScript files removed from the live NT8
Documents folder (repo history unaffected, nothing deleted from git).

_S2 R2 PROMOTION ADJUDICATION + CROSSTRADE PARITY header, retained: Last update 2026-08-09
(supersedes the
FINAL OPTIMIZATION DIRECTIVE close-out below for anything it touches). The owner restarted
NinjaTrader 8 and identified a process gap: S2_SELTIME's own frozen verdict rule required a
capital-map + parity R2 before any promotion decision, and that step had never actually run
before the campaign closed at "0 promotions". It has now run in full, separately for Product A /
BEST_ONE_NQ / BEST_ONE_MNQ, independently adversarially verified (3-agent parallel workflow, no
bug found) -- **NOT PROMOTED for all 3** (`runs/S2_SELTIME/R2_PRODUCT_A.md`, `R2_ONE_NQ.md`,
`R2_ONE_MNQ.md`): Product A fails gate_A/gate_B and narrowly fails gate_C; BEST_ONE_NQ/MNQ pass
gate_A alone but fail gate_B/gate_C decisively, traced to a real, mechanistically-understood
right-tail cost (a legitimately-suppressed +$7,625 winning entry on 2025-04-09's tariff-crash
volatility). Separately, a priority-zero forensic check RESOLVED the previously-reported 23%
Product A parity discrepancy as a warmup-state artifact (the original test compared an NT8
cold-start against a Python continuation-state run) -- a 9-month-warmup re-test converges to
0.71% residual. **Product A is now CERTIFIED for the spot-checked window**
(`runs/V1R4_NT8_PARITY/PRODUCT_A_CERTIFICATE.md`); BEST_ONE_NQ/MNQ improved substantially
(trade counts now match almost exactly) but remain NOT CERTIFIED pending a smaller, un-root-caused
~15-19% residual (`ONE_NQ_CERTIFICATE.md`, `ONE_MNQ_CERTIFICATE.md`). The CrossTrade long-job
session/result-retrieval ceiling (~20-25s of NT8 compute) is CONFIRMED to persist on the
freshly-restarted instance -- a genuine bridge characteristic, not a stale-connection artifact.
Registry now at seq 483. All 3 baseline objects remain architecturally UNCHANGED.

_FINAL OPTIMIZATION DIRECTIVE close-out header, retained: Last update 2026-08-09. 18
constructions tested across 8 named research families (S0 TOD autopsy, S1 arm_ER/arm_TOD, S2
SelTime, M3 entry/exit-S, M4 anchor, A1/A2 ATR audit, P4 churn selectivity, D-WINNER missed-
winner/give-back) plus a bounded 3-candidate Engine-3 slate (cross-market axis 15/15 failed
cumulative) and an X1/X2 execution/friction audit. 0 promotions at that point (S2's own R2 not
yet run -- see the section above, which supersedes this)._

**Full detail: `BASELINE_MODELS.md` (the 3 objects) and `FINAL_OWNER_DECISION_20260809.md` (the
closing status report) -- both are now the authoritative entry points and supersede this file's
own per-topic figures wherever they overlap.**

_Wave-19 header, retained: Last update: 2026-08-09, **Wave-19** (MEGA PROMPT V7 + the owner directive of the same day).
Registry at seq 471. Wave 19 consumed **ZERO** alpha budget - its primary work was the D7
diagnostic, which sec15 leaves uncapped - so both hypotheses remain available and the
multiple-testing position is unchanged from Wave 18. Read the Wave-19 section first; it
supersedes several Wave-18 statements below._

_Wave-18 header, retained: Last update 2026-08-09, **Wave-18** (MEGA PROMPT V7). Registry at seq 462.
Wave 18 consumed **both** permitted alpha hypotheses (§15 cap = 2): M1 and M5. Both closed
negative. Ten consecutive alpha hypotheses have now closed without a promotion — the §15
shift signal is **live** and is addressed in the Wave-18 section below. The deflation-adjusted
view of the incumbent is **unchanged** (standing: DSR 0.45–0.55 against a 0.90 bar;
Harvey–Liu-adjusted Sharpe of the incumbent's key comparison = 0.000)._

## Wave-19 verdict (MEGA PROMPT V7 + owner directive of 2026-08-09, seq 468-471)

**Owner directive R2 reprioritised the wave: the 106-session concentration is the headline, not
a footnote, and the primary work is a DIAGNOSTIC (uncapped, alpha budget 0), not a mechanism
test.** That was the right call and it produced the most consequential finding of the last three
waves. **Zero alpha budget consumed. Both hypotheses remain available.**

**1. D7 — the corrected top line, AFTER a red team that came back at the edge of REFUTED.**
The market variables do not merely fail to explain the concentration; **they point the wrong
way.** Regressing the Solar leg's daily net on the seven-variable market panel, fitted 2022-2025:

| | $/session |
|---|---:|
| in-sample mean actual (2022-2025) | +110.68 |
| 2026 stub **predicted** from market variables | **+172.14** |
| 2026 stub **actual** | **−72.05** |

The stub should have been a mildly *better*-than-average period. It was the worst on record. It
is also **not a multivariate outlier** (Mahalanobis D² 11.29, **93.7th** percentile against a 95th
bar) and **not novel** (nearest analog **2025-04-25 .. 2025-09-19**, 88.6th percentile, robust at
every window length 40-180 and under four distributional summaries). **Every regime-story reading
of the concentration is now excluded, not merely unsupported.**

**2. THE finding that changes how both Wave-18 failures must be read: the INCUMBENT is degraded
in the stub too.** Solar leg Sharpe **−0.387**, BEST_ONE_NQ **+0.073**, ES −1.046, YM −1.020.
In-stub challenger comparisons are therefore **low-power against a degraded reference**, not
evidence of challenger fragility. Corroborating: M1 was **helping** between the market break and
the stub (**+$8,073**), and YM — whose negative sign decided M5's 2-of-3 count — is **+$20,066**
in that same interval. M5's sign count was never a stable property.
This section is unaffected by the red team: `daily_from_fills` reconciles **exactly** to both
committed NT8 nets ($175,798.80 and $303,239.64), with flat-at-close and the roll rule verified.

**3. D1 — member collapse REJECTED.** Participation ratio 2026 = **3.52** of 13 against
3.37/3.61/3.93/3.78 for 2022-2025; survives bootstrap bands and equal-sample-size comparison; the
metric calibrates correctly (1.00 collapsed, 13.00 diverse). Mean |target| in 2026 is the
**highest** of any year, so exposure does not shrink either. **Correction from the red team:** the
report's supporting sentence used the *conditional* all-agree statistic (which conditions on an
event holding on 2.7% of bars); on the unconditional definition 2026 is **second highest, +23%
over 2025** — the direction the collapse hypothesis predicts. The rejection stands on the
participation ratio alone.

**4. The clamp figure is now pinned down, and the standing number was the wrong one.** Three
definitions were in circulation differing ~3×. The directives' figure (9.8/0.2/3.9/18.3/**39.2**%)
is the **widest member's** uncapped-30×σ460 rate — reproduced to two decimals, and unique among
28 candidate definitions tested. The ensemble-level rate is **12.94%**, and "any member pinned" is
**50.6%**. Quoting the widest member's rate as "the clamp binding rate" overstates the
ensemble effect roughly threefold. **Standing caution.**

**5. TWO HEADLINES WITHDRAWN, and one was true by construction.** (a) `EDGE = 0.10` in the frozen
changepoint spec placed the **entire 2026 stub outside the candidate set** — the stub starts at
index 1033, the last admissible index is 1024 — so "no changepoint in 2026" could not have come
out any other way. The conclusion survives (argmax unchanged at 2% and 5% edges) but *evaluated
at* the 2026 boundary three tests would detect, and "the argmax is elsewhere" is not "nothing
happened here". (b) "A monotone trend, not a break" is contradicted by BIC, which prefers **STEP**
for v6 by **73.8** and v6b by **29.3** — and the report's own yearly table shows both variables
*rising* into 2023, so "monotonically" was false on the face of the table it printed.
**(c) A real index bug:** PC1 and v2 were fitted on 1,120 rows and mapped back through the
1,139-row panel, so the estimated boundary is **2024-08-05, not 2024-07-09** (v2: 2025-01-24, not
2024-12-27). **And the boundary is weakly identified** — leave-one-variable-out moves it **545
days** against a 49-day CI. The successor spec must split on calendar years plus the 2026-01-02
convention and treat 2024-08-05 as a candidate, never as authoritative.

**6. Product A's stub resilience is NOT diversification, and that claim is withdrawn.** Decomposed
from the committed per-bar ledger: the Solar leg *inside* Product A is **+$6,079 / Sharpe +0.456**
in the stub (positive — not the same object as the plain E10 control), B-MOM adds **+$8,886**, and
of the ~$9k gap versus the plain control **+$7,243 is the short-halving overlay** — a fitted
in-sample constant — against **+$1,721** from the tilt. Two mechanisms of comparable size, one of
them not diversification. What survives is the narrower claim that B-MOM contributes positively
where Solar does not.

**7. R3 — the O1 aggregation choice was reviewed BLIND, and the reviewer AGREED.** It was given
the six conventions and the mathematics only: not told which was chosen, not told which raises a
score, not told a score existed, and forbidden to read any repo file. It independently chose the
**equal-weight mixture applied to both terms** — the repair's own choice — via decomposition
invariance and the observation that under min/max rules Monte-Carlo error becomes candidate-
dependent *bias*, so the rule's severity would be set by the number of bootstrap paths run.
**But it stated unprompted that the mathematics is only partly decisive**: the admissible set is
{mixture, Γ-minimax} and the choice rests on a classification that is not a theorem. **R3's
fallback therefore binds as policy: every score reports BOTH conventions, and any object whose
verdict flips is INCONCLUSIVE.** Product A's daily objective is **+0.124** under one and
**−0.126** under the other — **it flips, so it is INCONCLUSIVE and may not be quoted as a single
number.** O2 is unblocked on the aggregation question subject to that, and to four underspecified
items the reviewer raised (chiefly: is the fixed fraction optimised per candidate, which would
inject a selection bias no aggregation rule touches). **[SUPERSEDED 2026-08-09: the +0.124/−0.126
pair above is HAND ARITHMETIC on already-published v1 per-method components, not actual
`primary_objective_v2` module output — see `runs/O2_OWNER_UTILITY_READJUDICATION/REPORT.md`. The
real module output on the certified Product-A series is J=+0.0549 (mixture) / J=−0.2220
(Γ-minimax) — same sign pattern, still INCONCLUSIVE, materially different magnitude. Source:
`runs/O2_OWNER_UTILITY_READJUDICATION/out/o2_scoring_summary.csv`.]**

**8. R4 — the seal claim is now proven rather than asserted.** `src/analytics/seal_audit.py` is a
standing per-wave check: manifest in, max timestamp per artifact out, classified DEV / CONSUMED /
BREACH. **Wave 18: 21 artifacts, 0 locked-forward breaches, CLEAN. W19D7: 8 artifacts, CLEAN.**
It also sharpened the claim — two artifacts carry contents to 2026-07-31 and were *loaded then
sliced* to dev before any computation, which is permitted and was previously unstated.

**9. R1 carried forward as a standing statement:** this program has **no clean historical
out-of-sample data anywhere, for any sleeve** — not the Solar baseline, and since 2026-08-08 not
B-MOM or B1 either. The only virgin data is ≥2026-08-01 and it accrues one quarter per quarter.

**Wave-20 lead, and it is the only quasi-OOS check constructible for this question:** do M1 and
M5 also break in the named **2025-04-25 .. 2025-09-19** analog? Proposed, not run, not scored.

**Still open:** V1-R4 re-parity for all three objects; `SolarWaveSMOneLot_v1` propagation; V1g;
V5; the successor selectivity spec; O2 under the two binding conditions above.

---

## Wave-18 verdict (MEGA PROMPT V7, seq 459-462; runs/W18R1_M1_VOLSEASON + runs/W18R2_M5_XINST)

**The first wave in this program's V6/V7 era to run mechanism tests. Both failed, and both
failed informatively.** V7 §B's hard floor (≥1 Track-R spec frozen and run per wave) is met
with two.

**1. M1 — intraday volatility seasonality. arm_FULL FAILS 0/3 gates. The premise was
confirmed; the implementation of it was not.** The pre-registered falsification test was
decisively *not* triggered: `r_s = mean(|Δclose|/sigma460)` by 3-minute time-of-day slot spans
**0.372 (00:00 ET) to 4.105 (09:33 ET), an 11.04× spread** against a 1.5 bar, across 460 slots
each with ≥200 bars. The incumbent's threshold really is mis-scaled by an order of magnitude
across the day. But `arm_FULL` (sigma_adj = sigma460 × f, E[f]=1) fails every gate: Sharpe
0.5577 vs 0.7092, CDaR₀.₉₅ $35,498 vs $27,162, top-10-day retention **80.5%** vs a 95% floor.

**Root cause, measured rather than asserted, and it invalidates the spec's own claim.**
`S` is resampled **only at trend birth**, and flips concentrate in high-`f` slots:
**E[f | flip bar] = 1.536** against **E[f | all bars] = 1.000**. So mean `S` rises from 122.4
to 201.3 points (**+64%**) and member flips fall **46% in every cohort**, including overnight
where the mechanism was meant to *tighten*. The spec's statement that "because E[f]=1 this is a
pure re-allocation, the average threshold is unchanged" is **FALSE** — correction filed in the
run REPORT, never in the frozen spec (C6). `arm_FULL` is, by accident, partly a repeat of the
already-closed clamp-widening axis (SMV2AD/AG). **The null is therefore CONDITIONAL** on this
estimator and this application point, and saying otherwise would be dishonest.

**2. D4 (merged into M1 per V7 §C-2) — a selectivity result in its own right.** Incumbent P&L
by cohort: EVENING (18:00–23:59 ET) **26.0% of bars, −9.2% of P&L, net −$10,989**; OVERNIGHT
(00:00–08:59) 39.4% / +28.0%; RTH (09:00–16:59) 34.6% / **+81.2%**. Two-thirds of the clock
produces one-fifth of the money and the evening third loses. Independent of M1.

**3. M5 — ATR-blend cross-instrument replication. PARTIAL, which is pre-registered as NOT a
pass.** `arm_BLEND_75` (w = 0.75 frozen, no weight search) rebuilt on ES/RTY/YM 2022-2026 with
NQ as a KNOWN control. Sign agreement **2 of 3** new instruments (ES +0.0377/+5.75%, RTY
+0.0334/**+0.35%**, YM −0.0094/−1.84%) passes; pooled joint-date block bootstrap gives
P(mean ΔSharpe>0) = **0.9108 PASS** but P(mean ΔCDaR_ratio>0) = **0.7841 FAIL** against 0.85.

**The important number:** Wave 14 closed this lead having failed the *same prong* at **0.753**
on NQ alone, and diagnosed it as a power problem. Adding three instruments and **ESS 3.68 of 4**
of genuinely independent evidence moved that prong only to **0.784**. The power hypothesis has
now been tested and rejected. `arm_BLEND_75` stays CLOSED on two independent grounds and the
ATR/range family is closed for good.

**Two things a reader must carry from M5.** (i) **ES, RTY and YM all LOSE money** under this
construction (Sharpe −0.045 / −0.633 / −0.563 vs NQ's +0.838) — only the paired *increment*
replicates, the system does not port, and per C2 none of them may ever be a traded leg.
(ii) The **diff-series** cross-correlation is **0.029** while raw P&L correlates at **0.677** —
the mechanism's increment is nearly independent across instruments, which is why ESS is 3.68
and why the CDaR failure carries real weight.

**4. E-1 — the June/July 2026 window is CONSUMED, and V7 §E's premise is false.** Reported
directly per §18. `runs/SM11_HOLDOUT_READ` read exactly **2026-06-01 → 2026-07-31** on
**2026-08-08**, 45 sessions, six finalists scored and published (F1 SOLAR +$60,150 …
F5 PORT_TILT_532 +$45,833), with per-finalist daily vectors committed and registry seq 315. The
pre-registration order was verified independently by git, not taken on trust
(`FINAL_PACKAGE_SPEC.md` added at 03:58:02, SM11's report at 04:00:03 the same morning). The
campaign self-declares consumption in ~10 further artifacts, and the owner authorised the read
ex ante. **V7 §E-2 is therefore inapplicable — there is nothing left to seal.** Full evidence:
`research/system_master/HOLDOUT_DETERMINATION_20260809.md`. Scope correction carried there:
`LOCKED_FORWARD.md` is a campaign-#1/#2 artifact and on its own establishes only that the
window was already dirty *before* SYSTEM_MASTER started; SM11 is what consumed it for
SYSTEM_MASTER, **including for B-MOM and B1**, which `CONVENTIONS.md:23-28` had correctly noted
were still clean until then.

**5. §F warmup standard — and a correction to my own Wave-17 statement.** Measured, the Solar
leg re-synchronizes from a cold start in **2, 3 and 4 sessions** (fresh runs at 2023-01-03 /
2024-01-02 / 2025-01-02, target vectors compared bar-for-bar against the continuation;
0.16%/0.21%/0.62% of bars disagree). **Not ~460 bars.** §8b below attributes the start-state
gap primarily to `sigma460` warming over ~460 bars; that is wrong for the Solar core, because
`member_states` is a self-synchronizing directional-change machine and `sigma_series` uses an
**expanding** mean for t ≤ 460 so sigma is never absent, only noisier. **The binding constraint
is the HTF tilt**: `sign(session close − SMA50)` with `shift(1)` is undefined until **51
complete prior sessions**, and it is exact rather than asymptotic. This re-explains the Wave-17
gap correctly — a fresh 2026-01-01 run has **no tilt for its first 51 sessions**, about half the
Jan→May window. Standing rule: `research/system_master/WARMUP_STANDARD.md` (continuation basis
mandatory; discard ≥60 sessions from any fresh run; every Strategy Analyzer comparison must
state both start date and warmup convention).

**6. A record defect found while answering E-1, reported not tidied.** §8b below cites "a
from-scratch reproduction of **$75,449.60** on the nominally identical 2026-01-01→2026-08-07
window". A repo-wide search finds **no committed artifact** supporting that figure and **no run
with a `to` date of 2026-08-07**. Either a backtest was run into the locked-forward window and
never committed, or the figure was recorded in error; the record cannot discriminate. The
figure is **not deleted** (C7) but is marked **UNVERIFIED — DO NOT CITE**, the "$2,575 gap" is
withdrawn as an open research question, and a precautionary entry has been opened in the new
LOCKED-FORWARD ACCESS LEDGER in `HOLDOUT_DETERMINATION_20260809.md`. Registry seq 458 itself
stops at 2026-07-31 and is clean; the defect is confined to the §8b prose.

**7. §15 shift signal is LIVE.** With M1 and M5 closed, ten consecutive alpha hypotheses have
closed without a promotion. Per §15 that is a signal to change what is being searched, not to
search harder in the same space. The two highest-information findings of this wave both point
the same way and neither is an exposure idea: **D4's cohort structure** (the evening third of
the clock loses money and is 26% of bars) is a *selectivity* target, and **M1's root cause**
(the threshold is set once at trend birth and then frozen) says the Solar core's
**S-resampling rule**, not its sigma estimator, is the untouched surface. Every closed
core-challenge in this program has varied what sigma *measures* (ATR blend), what clock it is
measured on (1m, volume bars), or where the clamp sits (fixed, adaptive). **None has varied
when `S` is sampled.** That is the ranked lead going into Wave 19.

**Still open after Wave 18** (unchanged from Wave 17 unless noted): V1-R4 full NT8 re-parity for
both `_v4` objects — until it passes they stay `_v4`, not `_Final`; propagation of the
early-close + watchdog fixes to Product A (39 breaches) and `SolarWaveSMOneLot_v1`; V1g
intraday-path capital map; V5 MNQ bar-by-bar fill audit; O1 blind repair (in progress this wave,
Track E) and the O2 retro-scoring it blocks. **Withdrawn from the open list:** the $2,575
reconciliation (see 6).

---

_Wave-17 section follows. Registry was at seq 453 at that time._

_Last update: 2026-08-09, **Wave-17** (MEGA PROMPT V6). Registry at seq 453.
Wave 17 added **ZERO new alpha hypotheses** — every item was compliance, diagnostic,
execution or verification work, which §15 leaves uncapped and which costs no alpha budget.
The deflation-adjusted view of the incumbent is therefore **unchanged** from Wave 16
(standing: DSR 0.45–0.55 against a 0.90 bar; Harvey–Liu-adjusted Sharpe of the incumbent's
key comparison = 0.000). Wave 17 supersedes several Wave-16 statements below — read this
section first._

## Wave-17 verdict (MEGA PROMPT V6, seq 449-453; runs/W17_C4_COMPLIANCE + runs/W17B_C4_WATCHDOG)

**Product B is now C4-compliant for the first time, and Product A is not yet.**

| object | net (dev) | trades | C4 breaches before → after | status |
|---|---:|---:|---:|---|
| `SolarWaveOneContractNQ_v4` | **$303,239.64** | 1,976 | 16 → **0** | PASS, not yet parity-certified |
| `SolarWaveOneContractMNQ_v4` | **$28,705.20** | 1,976 | 1,077 → **0** | PASS, not yet parity-certified |
| Product A `SolarWaveSMMaster_v2` | $177,315 (unchanged) | — | **39, still open** | fix not yet propagated |

**1. V1-R1 — the flagship was never audited; it is now, and it is clean on normal sessions.**
`SolarWaveSMMaster_v2`: 962 positions open at the 16:39 decision bar → 962 flatten fills at
16:42 → **zero** bars holding at 16:42, at 16:45, or anywhere in 16:45-17:00. Product A does
NOT share the MNQ defect and its $177,315 / Sharpe 1.17 headline is **not** provisional on
that ground. It does carry the early-close defect (39 breaches) — see 4.

**2. V1-R2 — the MNQ root cause, established on the execution ledger.** A pre-registered
falsifiable prediction was tested: if `SubmitTarget` short-circuits, ~100% of MNQ exits must
be reversals or engine backstops. Measured **100.0%** (30.9% reversals + 67.6% at 17:00 +
1.4% at early-close session ends); **zero voluntary exits ever**, against an NQ control of
1,888 (95.6%). Hypotheses (b) wrong-series `hm` and (c) no fill bar were **refuted by
measurement**. The established cause is the **arrangement** recorded in KNOWN_ERRORS #7.
Narrowed claim, stated in the REPORT: the finer mechanism (stale position read vs unfilled
order) is NOT discriminated by any artifact in hand, and the fix does not depend on it.

**3. V1h — THE DIRECTIVE'S PREMISE IS FALSE, and the Wave-16 framing that produced it was
mine.** The 16 NQ trades exiting after 16:45 are not overnight positions: all 16 are entered
18:06-20:24 and exited 18:39-23:30 the **same evening**, inside the post-18:00 window where
intraday margin has resumed. Correct exposure test → `BEST_ONE_NQ` had **0** normal-session
breaches, not 16. "Exit time-of-day > 16:45" was simply the wrong test. Non-compliance aside,
all 16 are losses totalling ≈ −$33.5k — a real pattern, and a D2/D4 diagnostic lead.

**4. V1e — the real breach, previously undocumented, hitting all three objects.** 43 holiday
early-close sessions in dev (~10/yr: 31 at 13:00 ET, 9 at 13:15, 2 at 09:15 Good Friday, 1 at
09:30 = the 2025-01-09 Day of Mourning). The hardcoded `hm >= 163900` never fires on them, so
only the 30-second engine backstop closes the position — ~14.5 minutes **inside** the
initial-margin window. Fixed by making the schedule session-relative
(`sessionEnd − 30 min` / `− 21 min`, which equal 16:30 / 16:39 on a normal close, so all 1,095
normal sessions are unchanged by construction).

**5. The cost of compliance, reported and accepted.** NQ: **−$209.36 (−0.07%)** over 4.4
years. Per §13 rule 7 that is the price of the constraint; the 21-minute buffer was not moved
to recover it. MNQ post-fix is a **NEW OBJECT** and its $28,705.20 is not comparable to the
broken object's $28,900.70. Independent corroboration nobody optimised for: MNQ's trade count
is now **1,976, identical to NQ's** as the frozen rule requires, and its net sits **+0.09%**
from the canonical Python reference ($28,676.10) where the broken object was −0.78% off with
daily corr 0.8996. The reference did not move; the object moved toward it.

**6. Two self-caught defects, reported rather than quietly fixed.** (i) The first C4 audit
reported a phantom breach: position had been rebuilt from the ledger's `target` column, which
is not updated when the **engine** closes a position — now rebuilt from order actions.
(ii) `_v3`'s watchdog was a **silent no-op** and reproduced `_v2` to the cent; caught only
because the inertness prediction had been pre-registered as falsifiable. Cause: `Time`,
`Close` and `CurrentBar` are **BarsInProgress-relative**, so `Time[0]` inside the BIP-1
handler read the execution series, not the decision series. **Same error class as the original
MNQ bug** — code correct in one series arrangement, silently wrong in another, no exception,
no log line.

**7. V3-R5 — Wave 16's repo-exposure conclusion was overstated; corrected.** A local
`git rev-list` cannot test what the GitHub **remote** serves. Supported finding: *not
reachable via normal history traversal; remote retention UNVERIFIED*. Also newly established
and never previously recorded: the repository is currently **PUBLIC** (0 forks, 0 stars).
Parked in `OWNER_QUEUE.md` §OQ-1; no irreversible action taken.

**8b. START-STATE SENSITIVITY (seq 458) — a methodological finding that changes how every
recency-tier number in this program must be read.** Prompted by the owner asking why their own
Strategy Analyzer run shows a profitable 2026 while this wave reported ≈ −$47. Both are right;
they are different objects.

| `SolarWaveOneContractNQ_Final`, identical config | net | trades |
|---|---:|---:|
| FRESH run 2026-01-01 → 2026-05-29 | **+$7,426.36** | 174 |
| SLICED from the full 2022-2026 continuation, same end date | **−$46.60** | 185 |
| FRESH run 2026-01-01 → 2026-07-31 | **+$66,941.40** | 260 |

Two separate effects, and the second was not anticipated:
1. **Window.** Jun-Jul 2026 alone contributes **+$59,515.04** over 86 trades. The dev window
   stops at 2026-05-29, so nothing in this wave's tables ever saw it. The owner's UI run to
   2026-08-07 ($78,024.60) additionally picks up an Aug 1-7 sliver (~+$11,083) that is
   **LOCKED-FORWARD virgin data** and was deliberately not touched here.
2. **Start state.** On the *identical* Jan→May window the fresh run and the slice differ by
   **$7,473 and 11 trades**, purely because a run beginning 2026-01-01 has no history:
   `sigma460` warms from scratch (~460 bars ≈ 23h), `tiltState` needs 50 prior session closes,
   and B-MOM needs 14 RTH days of slot history. For roughly the first quarter of a fresh run
   the strategy operates on immature state.

**Consequence:** every recency-tier row in `V4_FRICTION.md` is a **continuation** number and
will NOT reproduce in the Strategy Analyzer from a same-year start. This must be stated
wherever those tiers are shown. It also further weakens the already-retracted 2026 collapse
claim — that figure is not even invariant to how the backtest is started.
**Still unexplained:** the $2,575 gap between the owner's $78,024.60 and a from-scratch
reproduction of $75,449.60 on the nominally identical 2026-01-01→2026-08-07 window.

> **CORRECTION APPENDED 2026-08-09 (Wave 18, seq 461-462). Two defects in the paragraphs
> above. Nothing is deleted; read the original text with these corrections attached.**
>
> **(a) The $75,449.60 figure has no provenance and the "$2,575 gap" is withdrawn.** A
> repo-wide search finds no committed artifact containing it and no run with a `to` date of
> 2026-08-07. Either a backtest was run into the LOCKED-FORWARD window (≥2026-08-01) and never
> committed, or the number was recorded in error — the record cannot discriminate. Status:
> **UNVERIFIED — DO NOT CITE**. It is removed from the open-questions list, because chasing a
> figure with no provenance is not research. A precautionary entry is open in the
> LOCKED-FORWARD ACCESS LEDGER in `HOLDOUT_DETERMINATION_20260809.md`. The $78,024.60 is the
> owner's own Strategy Analyzer number, supplied conversationally, and is not a repo read.
>
> **(b) The stated cause of the start-state gap is wrong for the Solar core.** "sigma460 warms
> from scratch (~460 bars)" implies the Solar leg is the slow part. Measured, it converges in
> **2–4 sessions** (seq 462): `member_states` is a self-synchronizing directional-change machine
> and `sigma_series` uses an **expanding** mean for t ≤ 460, so sigma is never absent, only
> noisier — 460 is the window length, not the convergence time. The binding constraint is the
> **HTF tilt at 51 sessions** (`sign(session close − SMA50)` with `shift(1)`), which is exact
> rather than asymptotic. A fresh 2026-01-01 run therefore has **no tilt at all** for roughly
> half the Jan→May window. The *conclusion* of §8b — that a sliced year and a fresh-start year
> are different objects, and that every recency tier is a CONTINUATION number — **stands
> unchanged and is if anything strengthened**. Standing rule: `WARMUP_STANDARD.md`.

**8a. RED TEAM (seq 454-457; full verdicts in `runs/W17_C4_COMPLIANCE/red_team/`).** Four
independent adversarial reviews, all **CONFIRMED-WITH-CORRECTIONS**, none REFUTED, 46 defects
logged. No compliance result was challenged — the C4 audit and the 0-breach outcomes were
measured by the orchestrator on NT8's own execution ledgers, outside these reviewers' scope.
Three corrections change what should be believed:
- **RETRACTED — the "2026 edge collapse" narrative.** BEST_ONE_NQ's 2026 partial net of
  −$46.60 is **0.001 SE from zero**; dropping the best trade of 185 gives −$13,307, dropping
  the worst gives **+$6,623**. No yearly per-trade gross mean is distinguishable from zero
  (Welch 2022-vs-2026 t = 0.89). The claim is withdrawn from `OWNER_STATUS.html` and here.
  Related silence also corrected: 45 excluded post-dev sessions run **+$34,997**, opposite to
  the retracted story (far too short to claim anything, and research-consumed, not clean OOS).
- **O1 IS NOT YET FIT TO SCORE ANYTHING**, and therefore **O2 retro-scoring is BLOCKED** —
  correctly. Two sign-flipping defects: `P_ruin` taken as the max over three bootstrap methods
  while `CE_g` is their arithmetic mean (asymmetry never pre-registered), and λ calibrated on a
  non-compounded growth convention while multiplying a compounded one. Construction,
  pre-registration and intraday machinery stand; the scalar does not.
- **V1f's "no crossover exists" is conditional on an unnamed assumption.** It applied 4× to
  *day* margin. Under 4× × *initial* margin Product A binds in **15 of 60** capital-map rows
  (min 0.503×); both Product B objects still clear. The Product B verdict survives; Product A's
  does not under the alternative reading.
- **Governance gap, and it was mine**: all four companion analyses were delivered into a run
  dir whose frozen spec covers only the C4 fix, and none was pre-registered. Recorded as such
  in registry rows 454-457 rather than tidied away. None proposes a promotion, so no alpha
  budget was consumed.
- **Standing data caution**: the NQ and MNQ 3-minute grids are not interchangeable — 13 NQ /
  11 MNQ dev sessions have internal gaps, and counting non-17:00 sessions *by bar shape* gives
  44, not 43. The 43-early-close figure is correct as a **calendar** statement and the C4 audit
  is unaffected (it keys on the session-close clock, not bar counts).

**8. Companion analyses, each independently red-teamed** — `V4_FRICTION.md` (friction share:
Product A 0.119 / BEST_ONE_NQ 0.028 / BEST_ONE_MNQ 0.066 commission-only, plus the house
`FS_house` definition and a commission sensitivity band, since the exact Lifetime all-in rate
is unconfirmed → `OWNER_QUEUE.md` §OQ-2); `O1_OBJECTIVE.md` (O1/O1a expected-log-growth
objective with bootstrap ruin penalty, pre-registered before any number was computed);
`V1F_EVENTDAY.md` (event-day 4X margin as a forward leverage constraint, with an explicit
provenance tier on every calendar date and 15 rows marked UNVERIFIED rather than guessed);
`V1D_CLOSURE.md` (**V1d = NOT-A-PROBLEM**: removing the 16:30 block entirely adds 3 entries
across 1,139 sessions, so there is no distribution to fit a cutoff to).

**Still open after Wave 17** (not fabricated, not silently dropped): V1-R4 full NT8 re-parity
for both `_v4` objects — until it passes they stay `_v4`, not `_Final`, and must not be
presented as certified; propagation of the early-close + watchdog fixes to Product A
(39 breaches) and to `SolarWaveSMOneLot_v1`; V1g intraday-path capital map; V5 MNQ bar-by-bar
fill audit (deferred deliberately — the fix changed the trade set, so it must run on the new
object); O2 retro-scoring; and all of W1–W4.

## Wave-16 W0 verification (MEGA PROMPT V5 rev2, seq 443-448) — SUPERSEDED IN PART BY WAVE 17
_Items 3 (V1h premise), the "0.81% residual" framing, and the V3 conclusion above are
corrected by the Wave-17 section. Left unedited below per the append-don't-rewrite convention._

## Wave-16 W0 verification — IN PROGRESS (MEGA PROMPT V5 rev2, seq 443-448 so far)
**HEADLINE: BEST_ONE_MNQ has a confirmed critical bug and is NOT currently a valid C4-
compliant deliverable.** Empirical audit of the real NT8 trades (`nt_trades_mnq.csv`, 1,561
trades) shows **67.7% of MNQ exits land at exactly 17:00 ET** (zero exits 16:27-17:00) —
the coded `hm>=163900` forced-flatten branch in `SolarWaveOneContractMNQ_Final.cs` computes
the correct target (0) but the resulting order is not filling before the session-close
backstop (`ExitOnSessionCloseSeconds=30`, bar-end-stamped ~17:00). This means 2/3 of MNQ
trades ride through the ENTIRE 16:45-17:00 NinjaTrader-initial-margin window the C4 hard
constraint exists to avoid. Root cause not yet isolated (suspect: cross-series order
routing, same bug class as `SolarWaveSMMaster_v1`'s KNOWN_ERRORS #7 arrangement bug that v2
fixed) — **not fixed yet, no blind patch attempted**. Every BEST_ONE_MNQ number reported to
date (net $28,900.70, Sharpe 0.921, the whole metric battery and capital map in
`runs/PRODUCTB_ONECONTRACT_FINAL/`) reflects this broken policy and must be treated as
**provisional, not the compliant Product B MNQ deliverable**, until fixed and re-parity'd.

**BEST_ONE_NQ, by contrast, is confirmed COMPLIANT**: the identical `hm>=163900` branch
(byte-identical code to MNQ's) fires and fills correctly — 668/1,975 exits cluster exactly
at 16:42 ET, and only 16/1,975 (0.81%) exit after 16:45, at scattered odd late-evening
times (19:57-23:30) that don't fit the "early-close backstop" explanation either — flagged
as a small open residual, not blocking (existing NQ parity-PASS stands unchanged; the
flatten mechanism it was measured on has not changed).

**16:39 vs the broker's 16:45 deadline**: not an error. `research/operational/
day_margin_variant/MARGIN_RULES.md` recommends an internal deadline ~16:38-16:40 ET (a
5-7 minute order-routing buffer ahead of the hard 16:45:00 external deadline); 16:39 is the
nearest 3-minute-bar boundary to that recommendation. Live-fetched NinjaTrader margin pages
(2026-08-09) confirm the existing repo's NQ/MNQ day-vs-initial margin figures exactly
(NQ $1,000→$43,433.67, MNQ $100→$4,343.38) and confirm the commission schedule is dated
2026-07-01 and updated quarterly, as the owner stated — the live filtered NQ/MNQ commission
table itself did not render via fetch, so the existing $2.18/$0.65-per-side convention is
neither independently confirmed nor contradicted this wave (V4a still open).

**V2 (overshoot ratio r, the MONITOR-01 statistic)**: NO ALARM on any window. Trailing-120-
session r = 1.2235 (all bands 1.2165-1.2492, comfortably above the 1.05 alarm floor);
matches the existing trailing-4-quarter reading (`monitor01_reading001.md`, dated
2026-08-07 — one day old, not "15 waves" as the prompt inferred, a premise correction worth
recording) and the full-history baseline exactly. Edge intact by this measure.

**V3 (repo exposure)**: `README.md` §6b is STALE. It states the vendor-DLL history rewrite
was never performed and risk is "contained, not erased." Direct git-history search finds
**zero `.dll` objects anywhere in `main`'s reachable history** (the only branch, local and
identical to the public `origin/main` — confirmed by a clean non-force push succeeding);
the original blob-adding commit hash no longer exists locally, consistent with a completed
`git filter-repo` rewrite. The remediation the old root `NEXT_HANDOFF.md` described as
"pending only the owner's force-push" **already happened and is already live on the public
remote**. No history rewrite performed or needed this wave.

**Still open from Wave-16 W0** (not yet done, not fabricated): the MNQ flatten bug fix +
rebuild + re-parity (top priority — blocks V1a's "re-run parity" requirement and blocks
everything in W2-W4 that touches BEST_ONE_MNQ); V1e (holiday early-close enumeration); V1f
(event-day 4x-margin exposure share + leverage ceiling); V1g (intraday-path capital
headroom, needs O1a machinery); V4 (full friction-share ledger for Product A); V4a (exact
live NQ/MNQ commission confirmation — owner offered to supply); V5 (MNQ 2025-04-07/09/11
fill audit); O1/O1a (new primary objective function); all of W1-W4. Continuing autonomously
per the directive's auto-chain instruction.

## Product B one-contract final deliverable (runs/PRODUCTB_ONECONTRACT_FINAL/, orchestrator-
## executed directly, no alpha changes) — 2026-08-08 framing, MNQ status SUPERSEDED above

## Product B one-contract final deliverable (runs/PRODUCTB_ONECONTRACT_FINAL/, orchestrator-
## executed directly, no alpha changes)
Built `SolarWaveOneContractNQ_Final.cs` / `SolarWaveOneContractMNQ_Final.cs` (behavior-
preserving SM14 seq-318 refactor). **BEST_ONE_NQ: Strategy Analyzer parity PASSED** (99.49%
trade-exact, daily corr 0.9990, net Δ 0.13% — reproduces the prior research-filename check
almost exactly). **BEST_ONE_MNQ: genuinely backtested via real Strategy Analyzer for the
first time ever** (net $28,900.70/Sharpe 0.921/1,561 trades), trade-level match excellent
(99.42%), but formal parity against the current Python reference misses the bar (daily corr
0.8996, net Δ 0.78%) — diagnosed, not a Final-file defect: the Python reference used for EVERY
prior "1 MNQ" number in this entire program fills at NQ-scaled prices, not genuine MNQU6
prints (a known residual class, documented precedent in EVIDENCE_MAP_RAW.md for a different
product). Full metric battery (Sharpe/Sortino/Calmar/CDaR/ES/EDaR/worst-week/month/quarter/
TUW/positive-%) and capital maps (historical + 1.25/1.5/2.0x stress, bootstrap band across 3
methods) computed for both instruments on the real NT8 numbers. Fixing MNQ's reference needs
genuine MNQ price data — attempted via GetBars this run, returned empty, root cause
undiagnosed, flagged as the concrete next step. BEST_ONE_CONTRACT_OVERALL not yet selected
(MNQ unresolved). Full detail: `runs/PRODUCTB_ONECONTRACT_FINAL/REPORT.md`.

## Wave-15 verdict (spec 6633114; red-team CONFIRMED-with-corrections — 3 disclosure-
## completeness corrections, zero numeric — verdict unaffected)
**SMV2AK_VOLUME_BARS (seq 438-442) — CONFIRMED-NOT-BENEFICIAL, CLOSED.** Expansion-pass EVI
rank #2: bars closing on cumulative volume instead of elapsed time, motivated by SMV2U/W's
inference that 5-minute nearly beat 3-minute via turnover-damping. Result: **fails all three
AND-rule legs decisively** — Sharpe 0.431 vs 0.709 (worse), CDaR₀.₉₅ $34,250 vs $27,162
(worse), top-10-day retention 94.2% (<95%). Portfolio-level also fails to beat the champion.
**The motivating hypothesis itself is contradicted, not just the outcome**: volume-bar
turnover (39.2/day) is HIGHER than the 3m incumbent's (33.0/day), the opposite direction from
both 5-minute arms (damped to 19.6-20.3/day) — root cause is a right-skewed bar-width
distribution (median 1.0 min, well below the 3-minute cadence, despite a mean width close to
the calibration target). A genuinely informative negative finding about *why*, not just
*that*, this didn't work. No second bite at this V without a genuinely new threshold-
selection mechanism (dollar-volume/tick-imbalance bars would count as new).
**Program state**: three of the mechanism-expansion pass's top candidates are now closed this
session (adaptive clamp #1, ATR-blend #3 — closest miss yet, volume bars #2), plus the
same-day circuit breaker (owner's direct question). Remaining ranked ideas (#4-9) are
flagged lower-EVI/higher-duplication-risk by the expansion pass itself. **Concurrently**:
Product B one-contract final deliverable (BEST_ONE_NQ/BEST_ONE_MNQ) is in progress —
runs/PRODUCTB_ONECONTRACT_FINAL/spec.yaml frozen, both Final NinjaScript files built and
syntax-verified, blocked on an NT8 NinjaScript Editor F5 (owner action required) before
Strategy Analyzer parity can run for either instrument.

## Wave-14 verdict (spec 8c030f8; red-team CONFIRMED, 2 prose-only corrections, no numeric/

## Wave-14 verdict (spec 8c030f8; red-team CONFIRMED, 2 prose-only corrections, no numeric/
## decision impact) — the closest an R2 confirmation has come to passing in this program
**SMV2AJ_ATR_BLEND_R2 (seq 433-437) — CLOSED, incumbent retained.** R2 confirmation of
SMV2AI's arm_BLEND_75 lead (75% incumbent sigma460 / 25% properly-rescaled ATR estimator),
tested at the actual DUAL-transformed decision object (confirmed via direct code read that
SMV2AI's own old-regime screen tested the raw pre-DUAL target, so this was a genuine unseen
re-test, not a duplicate). **Result: 1 of 5 required gates fails — Gate A (dev bootstrap),
and only on its CDaR_0.95 prong** (P(dSharpe>0)=0.932 clearly passes the 0.85 bar; P(dCDaR>0)
=0.753 falls short). **Gates B (LOYO 4/5, improving into 2025-26), C (old-regime, net gap
+$86,004 vs a −$10k floor, wider than SMV2AI's own raw-level screen), D (right-tail retention
100.14%), and E (portfolio: dSharpe +0.033/dCDaR +$318, both point-positive, with almost no
leg-vol sizing confound unlike SMV2T's challenger) all PASS, several with real margin** — this
is the strongest performance any core-challenge R2 has produced in this program (SMV2T failed
3/5 gates outright; this failed only 1, and only one prong of it). Gate F (new this wave:
bootstrap at neighbor blend weights w=0.70/0.80, disclosure-only) showed the point estimates
form a smooth, non-spiky local hump across w=0.70-0.80, but CDaR bootstrap significance is
weak across the WHOLE neighborhood, not just at w=0.75 — reinforcing, not contradicting, gate
A's failure: the mechanism looks real but its tail-risk improvement is not yet statistically
distinguishable from noise on 4.4 years of daily data. Per the frozen AND-rule, applied with
no discount for how close this came: **incumbent sigma460-only core retained. Lead CLOSED —
no third bite without a new mechanism that specifically targets the CDaR-tail effect** (not a
re-test of the same blend at a different weight). This is a genuinely different failure
pattern from every other closed core challenge in this program (which mostly failed on
old-regime melt-up capture or right-tail retention) — the mechanism itself may be real; only
its statistical confirmation on tail risk specifically fell short.

## Wave-13 verdict (specs d927ec6; red-team CONFIRMED-with-corrections on both — SMV2AH had 2

## Wave-13 verdict (specs d927ec6; red-team CONFIRMED-with-corrections on both — SMV2AH had 2
## narrative corrections [gate-1 object-attribution breakdown, a FLATTEN-worst-day
## overgeneralization], SMV2AI had 5 corrections [4 cosmetic/typo, 1 real prose mischaracterization
## of arm_BLEND_25's CDaR — none change either verdict]; both runs' only other gap was a missing
## REPORT.md, now written) — **arm_BLEND_75 is the first genuinely new Solar-core mechanism to
## pass a standalone AND-rule screen since the clamp-ceiling/clock-challenge series began closing.**
**SMV2AI_ATR_BLEND (seq 430-432) — QUEUE_R2_CONFIRMATION.** sigma460 is close-only and
structurally blind to intrabar wicks (99.3% of dev bars carry TR > |Δclose|, i.e. real wick
information sigma460 cannot see). Blending it 75/25 with a properly rescaled ATR (true-range)
estimator — `sigma_ATR_eff = ATR460/2.0255`, R measured with the same discipline SMV2AE used —
**uniquely qualifies**: standalone Sharpe 0.746 vs 0.709 control, CDaR₀.₉₅ $25,183 vs $27,162
(better), top-10-day retention 100.2% (comfortable margins, not borderline). The a priori churn
concern (ATR is noisier intrabar) is NOT confirmed — flip-count rises only 0.09%. At the
portfolio level (DAYONLY_DUAL6040 60/40) it also beats the champion (Sharpe 1.297 vs 1.264,
CDaR $14,004 vs $14,322). **Old-regime screen (2006-2021) passes with real margin, not
marginally** — net gap +$71,544 vs a −$10k floor, maxDD ratio 0.954 vs a 1.25× ceiling — the
exact floor that killed 3 of 5 prior core-challenge candidates in this program. Pure-ATR
replacement (arm_REPLACE, w=0) has the single best standalone CDaR of all 5 arms but fails on
Sharpe alone; w=0.25/0.50 both fail outright; the w-relationship is non-monotonic, disclosed
not explained. **No adoption this wave** — queues a full SMV2T-style R2_CONFIRMATION
(bootstrap significance, LOYO, right-tail, formal portfolio gate) next wave, the natural top
priority.
**SMV2AH_DAY_CIRCUIT_BREAKER (seq 426-429) — KILLED, CONFIRMED-NOT-BENEFICIAL.** Directly
answers the owner's stop-loss/day-loss-limit question from mid-wave-12: a same-day, portfolio-
level running-P&L circuit breaker (2 halt modes × 4 percentile-calibrated thresholds × 2
objects, 16 cells) was built and tested for the first time in this program (required new
intraday bar-by-bar MTM machinery, reconciled exactly against existing EOD curves before any
breaker logic ran). **0/16 cells qualify.** Decisive failure: in every single cell, the real
threshold-triggered rule's CDaR is *worse* than a matched placebo that halts the same number of
sessions at a random bar instead of the actual loss-triggered bar — a reactive rule structurally
captures less protection than random truncation, because it can only act after the loss has
already partly happened. This is now the THIRD distinct time-scale where loss-reactivity has
tested anti-edge in this program (per-trade MAE stops SM03/SM03B — dead, Solar's own reversal
already acts as one; cross-day streak throttle SM02B — anti-edge; now same-day — anti-edge, for
a cleaner mechanistic reason). Leg attribution: the deployed portfolio's triggers are genuinely
mixed (67-83% joint Solar+B-MOM negative days), not chasing one engine's noise.

## Wave-12 verdict (specs db39d56; red-team CONFIRMED-with-corrections on both — SMV2AF had one

## Wave-12 verdict (specs db39d56; red-team CONFIRMED-with-corrections on both — SMV2AF had one
## factual labeling fix in a comparison table (does not change the conclusion), SMV2AG had zero
## numeric corrections; both runs' only other gap was a missing REPORT.md, now written)
**SMV2AF_1MIN_RESCALE_R2 (seq 420-423) — 1-minute Solar is now CLOSED FOR GOOD.** R2
confirmation of SMV2AE's screen-level pass (rescaled 1m Sharpe 0.439). Gate A (dev bootstrap
significance) passed by a thin margin (P(Sharpe>0)=0.853 vs 0.85 bar, not corroborated by
Newey-West t=1.08). Gate B (LOYO chronology) **FAILED**: only 3/5 years same-sign (bar is
4/5). Gate C (old regime, newly built on a native 1-minute 2006-2021 substrate that turned out
to exist, a genuine finding of its own) showed the rescaled construction **losing money**
(net −$20,583, Sharpe −0.119, friction exceeding gross) — worse than even the mediocre,
already-REGIME_LOCAL 3m incumbent's own historical result. Gate D confirmed the a priori
expectation of high correlation with the deployed 3m signal (0.897) and found no
diversification value (a 50/50 blend beats neither Sharpe nor CDaR of the 3m-only leg). Per
the spec's own rule, a Gate B failure downgrades the screen result to noise-level: **1-minute
Solar is closed under every calibration convention this program has tried** (fixed-
StopMultiplier family, VolMult unscaled ×2 sigma-window conventions, VolMult rescaled) — no
further attempts without a structurally new signal-generation mechanism.
**SMV2AG_ADAPTIVE_CLAMP (seq 424-425) — CONFIRMED-NOT-BENEFICIAL, lead CLOSED.** The
mechanism-expansion pass's #1-ranked idea (a causal rolling-percentile clamp ceiling, floored
at the incumbent 1200t so it can only widen) hit the identical Sharpe-for-CDaR tradeoff SMV2AD
found for a fixed higher ceiling: every one of 6 cells (P∈{90,95,99}×N∈{460,920}) improved
Sharpe (+0.11 to +0.14), but only one cell also improved CDaR (+$138, the smallest possible
win) — and that cell failed the top-10-day retention floor (87.6% vs ≥95%). 0/6 qualify. The
ceiling genuinely widens more in high-vol periods (2025's tail is the most extreme on file) but
only as a thin upper-tail effect, not a broad regime shift — explaining why it buys Sharpe
without reliably buying CDaR. **Both the fixed-raise and adaptive-widen-only clamp-ceiling
mechanisms are now exhausted**; any future clamp idea needs a genuinely different shape (e.g.
one that can also tighten) to be worth a spec.
**Owner follow-up (mid-wave-12, addressed directly, no new autonomous wave launched for it
yet)**: owner asked what stop-loss/day-loss-limit mechanisms exist and whether they matter.
Audit confirmed: neither deployed strategy has a resting stop-loss, daily loss limit, or
kill-switch in code (only session-close flatten + the 16:39-18:00 ET margin-cliff ops rule).
Every classic stop/exit-engineering idea ever tested in this program (SM03/SM03B disaster
stops, split exits, resting stops, timed exits, trailing/break-even — `STOP_OVERLAY_FRONTIER.md`)
is DEAD, because the Solar state machine's own reversal logic already acts as a stop. Loss-
reactive cooldowns are ANTI-EDGE (SM02B: next-day expectancy is HIGHER after a loss day, not
lower). Windfall give-back (profit-lock) was KILLED at the policy level (C-P7). **Genuine,
confirmed-never-tested gap**: a same-day intraday circuit breaker (halt trading for the rest of
the session after a running-loss threshold) has never been built or backtested here under any
name — queued for a future wave. **Separately flagged risk-hygiene finding**: `SolarWaveSMMaster_v2.cs`
is coded realtime-fail-closed (never submits live orders); `SolarWaveSMOneLot_v1.cs` (SM14) has
no equivalent code-level guard — its fail-closed posture currently rests entirely on the
LIVE_READINESS_CHECKLIST's operating discipline, not on a safeguard inside the file itself.

## Wave-11 verdict (specs 2b2f88a; red-team SMV2AD CONFIRMED-with-corrections [2, both

## Wave-11 verdict (specs 2b2f88a; red-team SMV2AD CONFIRMED-with-corrections [2, both
## applied to the run REPORT — a missing-file deliverable gap and a tautology-framing fix,
## neither numeric], SMV2AE CONFIRMED with zero corrections) — owner-directed pivot back to
## genuinely new Solar-core mechanism ideas after the owner flagged wave 6-10 diagnostics as
## scope drift ("went too far? we only want best nq or mnq strategies"), then re-authorized
## full autonomy with the standing goal restated.
**SMV2AD_VOLMULT_CEILING (seq 415-417) — CONFIRMED-OPTIMAL-IN-RANGE, lead CLOSED.** The
1200t/300pt clamp on the slowest member (VolMult=30) binds 39.2% of Jan-May 2026 bars vs
9.8%/0.2%/3.9%/18.3% in 2022-2025 (SMV2R sub_381) — more binding now than any full historical
year, never before acted on. Raising the ceiling (1200/1600/2000/2400t) DOES mechanically
relieve the bind (10.93%→0.57% at 2400t) and DOES lift Sharpe monotonically (0.709→0.863
standalone) — but CDaR_0.95 (tail drawdown) worsens at every ceiling tested (+4.9-5.0%): the
unclamped slow member trades rarer, larger, fatter-tailed trend moves. 0/3 ceiling arms and
0/2 extended-slow-cohort arms (VolMult 34-50, add-18 or replace-fastest-13) qualify as
candidates (must improve Sharpe AND CDaR AND retain >=95% top-10-day sum). The current
1200t/VMS-6-30 design is a genuine local optimum on the Sharpe/CDaR frontier, not a historical
accident. Closed — no third bite at a *fixed*-value ceiling/cohort change without a new
mechanism. (Does NOT close the *adaptive*/percentile-ceiling idea — structurally different,
ranked #1 in the same-wave mechanism-expansion pass below, still open.)
**SMV2AE_1MIN_RESCALE (seq 418-419) — PASS-SCREEN, queues R2_CONFIRMATION.** SMV2U's two
prior 1-minute tests reused the 3m VolMult constants VERBATIM on 1m-scale sigma (confirmed by
code read) and both failed decisively (friction 102-128% of gross). The un-recalibrated axis —
VolMult's point-scale itself, since 1m |dClose| isn't point-comparable to 3m |dClose| even over
an identical time window — was measured directly (R=1.7301, tight and regime-stable across 5
years, medians 1.721-1.742) and applied. Result: net flips from -$3,163/Sharpe -0.018 (unscaled)
to **net $77,748/Sharpe 0.439**, friction share drops from 1.020 to 0.470. Clears the
pre-registered screen (Sharpe>0 AND friction<0.60) with a comfortable margin — but still trails
the 3m incumbent (Sharpe 0.709) on every metric, and NO bootstrap/LOYO/old-regime/portfolio
battery has been run yet (this was a screen, not a promotion attempt). Queued for R2 next wave.
**Mechanism-expansion research pass** (no spec, `deep_research/DR_V4_SOLARCORE_EXPANSION_
20260808.md`): 9 ranked Solar-CORE (not Engine-3) candidates, deduped against every closed
lead. Top 3 by EVI: (1) percentile/rolling-adaptive clamp ceiling (replaces the now-closed
FIXED ceiling idea with a genuinely different adaptive one), (2) volume bars as a new clock
mechanism (distinct from the 3x-killed fixed-time 1m/3m/5m family), (3) ATR/range-based
threshold estimator blended with sigma460 (captures intrabar wicks sigma460 structurally
cannot see). Candidates 4-9 ranked lower (thinner data, higher duplication risk vs closed
leads, or explicitly flagged as possible re-skins of killed ideas — one (#9) requires reviving
the T2/T3 layer already shown to add zero information and is included only to honestly close
the question, not as a promising lead).

## Wave-9 verdict (spec 0da78b6; red-team CONFIRMED, 2 trivial arithmetic corrections applied)
First cross-market Engine-3 slate — ES/NQ dispersion catch-up, duration-spread shock reaction,
quarterly roll basis convergence — **ALL THREE KILLED** (none clears its significance gate;
none shows the targeted joint-whipsaw complementarity). Combined with the three NQ-only slates:
**12 of 12 Engine-3 candidates across 4 slates now dead.**
**Refinement to the joint-whipsaw understanding**: the 23 SMV2Z-flagged weeks are NOT simply
losing weeks — champion mean weekly PnL is actually HIGHER there (+$2,465.90/wk vs +$652.10/wk
elsewhere), driven by high dispersion including some very large positive weeks. These are
high-variance, regime-uncertain weeks that have, on net, been GOOD for the champion so far —
sharpening (not contradicting) the wave-7/8 finding that they cannot be cheaply de-risked
without giving back disproportionate upside. Data note: RTY/YM substrates share a genuine
11-day gap (2023-04-06..04-14, consistent with the known boundary irregularity) that does not
touch any of the 23 flagged weeks. Remaining unexplored cross-market candidates (D1 ranks
3/4/6, D2 rank 1) are the next place to look before declaring cross-market exhausted.

## Wave-8 verdict (spec f6fb7d1; red-team CONFIRMED, zero issues) — smoothness-policy family
## closed with a coherent explanation, not four unrelated failures
Mandatory prerequisite diagnostic (does Solar respond differently from B-MOM during the
sigma460+ER150-flagged weeks?) FAILED before any policy cell ran: asymmetry ratio 1.04, far
short of the 1.3 bar. Both legs scale UP TOGETHER in flagged weeks (Solar vol +76%, B-MOM vol
+69% vs unflagged) — this is a JOINT whipsaw, not one engine misbehaving while the other holds
steady. Per the spec's own honest-stop design, the mix-shift policy cells were correctly never
run — a complete, valid, non-wasteful outcome.
**SYNTHESIS across all four smoothness-policy attempts (SMV2N, SMV2V, SMV2Z, SMV2AA — all
independently designed, all honestly killed):** the flagged/joint-loss weeks are periods where
Solar and B-MOM behave as CORRELATED expressions of the same underlying modern-regime
breakout-persistence factor, not diversifying ones. You cannot cheaply de-risk by cutting total
exposure (SMV2Z: costs more upside than downside saved) or by reallocating between the two
engines (SMV2AA: they move together, nothing to reallocate toward). This directly answers V4
§58 Q22 ("are Solar and B-MOM merely two expressions of the same regime factor?") for at least
this specific state — **yes, during these weeks they are.** Per V4 §51: this exposure/
reallocation-timing mechanism family is EXHAUSTED; a genuinely different mechanism (e.g. a
THIRD, structurally uncorrelated return source — which is exactly what Engine-3 has been
searching for) is required to actually shorten these episodes, not a smarter way to time the
existing two engines.

## Wave-7 verdict (spec fdd0e65; red-team CONFIRMED) — the KEY reason smoothness is hard here
The simplest possible policy on wave-6's finding (cut exposure when sigma460 AND ER150 both
sit in their historically-worse top tercile) **FAILED DECISIVELY at every scale tested**: CDaR
got WORSE (not better) at every cell, TUW was unchanged, and net retention/RTC collapsed
(0.85-0.96 / 0.89-0.97). The mechanism (FACT): the flagged weeks — only 9.9% of all days — hold
**30.3% of the strategy's TOTAL NET PnL**. The states that flag elevated downside risk ALSO
flag elevated total variance/opportunity — they are not "bad weeks," they are HIGH-VARIANCE
weeks, and cutting exposure into them gives back far more upside than it saves in downside.
This is the THIRD consecutive downside/smoothness policy to fail (after SMV2N windfall,
SMV2V ER-damper) — three independent, honestly-tested attempts, three failures, each for a
different underlying reason. The SMV2Y diagnostic finding itself (sigma460/ER150 forecast
next-week downside) still stands as valid information — it just cannot be cheaply monetized
into a risk-reduction policy without a disproportionate cost to the right tail. Per V4.1 §21,
this specific escalation path (sigma460/ER150 pair → exposure policy) is now EXHAUSTED.

## Wave-6 verdict (spec 51dbc45; red-team CONFIRMED) — FIRST VIABILITY STATE TO PASS
**sigma460 and ER150 both causally predict next-WEEK portfolio downside** (t_NW=−2.30/−3.05,
bootstrap same-sign 0.99/0.998, monotonic, same-sign on an E10-only old-regime proxy). This is
the first state test in the whole program (16 prior cells: VR/ER/Kalman/BOCPD, all killed) to
pass — the difference is the TARGET: next-week portfolio downside, not next-session Solar PnL.
No new data or features — same computed series, different (and correct, per V4 §21) dependent
variable. One open question flagged INFERENCE: ER150's FORWARD sign (high efficiency this week
→ worse NEXT week) is opposite SMV2Q's CONCURRENT finding (joint-loss weeks have low ER150
DURING themselves) — not a contradiction (different timing), but unexplained mechanistically.
**No policy has been tested yet** — this is DIAGNOSTIC only; a bounded 0/0.5/1 exposure policy
per V4 §21 is the natural next step, queued.

## Wave-5 verdicts (specs 7abeb79; both red-team CONFIRMED)
- **5m clock lead CLOSED**: SMV2W's confirmation FAILED 2 of 4 available gates (dev bootstrap
  confidence 0.64/0.55 < 0.85; LOYO only 3/5 years < 4/5-year bar) despite passing right-tail
  retention (0.924) and portfolio point-positivity. Old-regime gate BLOCKED-BY-DATA (5m is not
  causally derivable from the committed 3m hist substrate — a real data-coverage gap, not a
  dodge). **3m incumbent RETAINED — 5th consecutive challenge survived** (memory length,
  cohort structure, MA confirmation, T2/T3 signal layers, now clock).
- **Engine-3 is exhausted at the NQ-only, 3m-bar horizon**: slate 3 (shock-day continuation,
  post-FOMC/CPI drift, post-expiration breakout) — ALL THREE KILLED. Combined with slates 1-2,
  **9 candidates across 3 slates, 0 survivors**. Shock-continuation was even significantly
  NEGATIVE (−$29.2k, t=−2.22) — trading with a 3-sigma shock loses money at this horizon.
  Per V4 §51: next step is an ES/RTY/YM data export (mirroring the SM1M NQ 1m export) before
  any 4th slate — the remaining high-EVI candidates (cross-market lead-lag, 8 of them) all
  require it and are queued, not dropped.

## Wave-4 verdicts (specs 547d2d4; all red-team-verified — 3 CONFIRMED, 3 CONFIRMED-with-prose-fixes)
- **FAST-cohort removal lead CLOSED**: SMV2T's R2 confirmation FAILED 3/5 gates (dev bootstrap
  confidence 0.80/0.39 < 0.85; old-regime net gap −$16.7k breaches the floor; portfolio-level
  dCDaR actually worsens by $1,653). 13-member incumbent core RETAINED. No third bite.
- **ER150-damper policy KILLED**: risk metrics (CDaR/TUW) fail to beat count-matched random
  damping at every cell; the underlying information result (ER150-agreement → lower next-day
  Solar PnL, sign-preserved pre-2022) stands as a diagnostic, converts to no policy.
- **Clock challenge: 1m fails decisively** (friction exceeds gross PnL); **5m bar-matched
  near-misses** (LOYO only 3/5); **5m time-matched (VolPeriod=276, ~23h memory) EARNS an R2
  confirmation** — standalone Sharpe 0.793 vs 0.709, portfolio Sharpe 1.156 vs 1.120, CDaR
  better on both bases, LOYO 5/5 including leave-2022-out, and LOWER turnover than the 3m
  incumbent. R2 spec SMV2W frozen (same 0.85-confidence bar as every other core challenger —
  no double standard for a lead that looks good). One live MTF hypothesis logged (not policy):
  1m-vote disagreement AT ENTRY predicts a −$78/episode PnL gap (t=−2.09), unreplicated on the
  time-matched convention.
- **Engine-3 slate 2 obituary closes with 3 mechanism-expansion passes** (24 candidates,
  archived in full at deep_research/DR_V4_EXPANSION_PASSES_20260808.md). Slate 3 (SMV2X, frozen)
  selects the 3 highest-EVI NQ-only-computable, calendar-anchored CONTINUATION engines: vol-
  shock-day continuation, post-FOMC/CPI drift continuation, post-expiration gamma-unclamp
  breakout. Cross-market candidates (the largest remaining slice) are queued behind an ES/RTY/
  YM data export — not dropped.

## Wave-3 verdicts (specs 58dc2d2; 6/6 red-teams: 5 CONFIRMED, 1 CONFIRMED-with-prose-fixes)
- **C-P7 windfall policy KILLED** (risk reduction indistinguishable from random same-duration
  de-risking; info result stands). **Kalman + BOCPD KILLED** → the whole ranked DSP JOB1 slate
  is dead. **Engine-3 slate 2 ALL KILLED** (VA rotation significantly negative AND
  anti-complementary) → six-for-six reversion families dead; 3 mechanism-expansion passes now
  REQUIRED. **One-lot family #2 KILLED** (retention 0.84 vs 0.90 hard bar; 2nd consecutive) →
  one-contract frontier PAUSED for mechanism expansion; SM14 stays FINAL. **T2/T3 and MA30/59
  KILLED** (MA hard-confirmation costs 22% of net + 6.2% of right tail — pure lag).
- **Solar core re-earned most of its incumbency** (V4.1 §20): vol memory 460 = CONFIRMED
  PLATEAU; SLOW cohort load-bearing; clamp floor irrelevant / 1200t cap an active regularizer.
  ONE live lead: **removing the FAST cohort (vm6-12) improves Sharpe 0.768 vs 0.709 with
  churn halved and top-10-day retention 105.9%** — R2 confirmation spec next wave (thin CDaR
  margin flagged). Plus one HYPOTHESIS: ER150-damper (t=−3.27, over-extended efficiency
  mean-reverts next day).
- **Smoothness truth (permanent scorecard)**: master exec = 44.1% days / 56.1% weeks / 64.2%
  months / 83.3% quarters positive; the negative-period cause is IDENTIFIED — 50/230 joint-loss
  weeks own −$159.6k with a causal signature (LOW path efficiency t=−6.5, HIGH flip rate t=+3.0).
- **2026 recency (owner question)**: rolling-120 Sharpe percentiles at dev end — BMOM 52nd /
  MASTER 41st / DUAL 35th / SM14 27th / E10 17th, none near historical minima; Apr-May 2026 was
  a ~1x/yr-class joint-loss episode; consumed June was +$20.6k. INFERENCE: path variation, not
  decay evidence. Monitors MONITOR-01/SM13 remain the tripwires.

## Wave-2 verdicts (all red-team CONFIRMED; specs frozen at 0a9cf3f before any read)
- **A-dominant one-lot CONFIRMATION FAILED** (gate A P≈0.71/0.63 < 0.85 both instruments;
  gate B old-regime net floor breached; right-tail retention 77% < 90%). **SM14 retained as
  ONE_CONTRACT_FINAL.** All 12 point estimates favored the challenger — confidence failed, not sign.
- **C-P3 leverage disclosure**: at CURRENT champion size, P(2y maxDD > $25k) = 0.14-0.43 across
  bootstrap methods — the historical −$18k is one path. L* < 1.0; leverage add-ons dead.
- **60/40 retained** (C-P1 fit optima 0.50-0.55 but eval ordering not preserved — no move).
- **Killed**: drought-tilt (placebo-indistinguishable), VR + ER trend-quality states (0/12
  cells), Engine-3 slate 1 (failed-break fade SIGNIFICANTLY NEGATIVE t=−2.35 — sweep-reversal
  premium does not exist on modern NQ; small-gap fade negative; overnight drift ~zero).
- **Survivor**: C-P7 windfall give-back pre-test PASSED (fwd-10d −$136/d vs base +$162/d,
  p=0.0012) → bounded trim policy earns a frozen spec.
- **SMV2M master PARITY PASSED**: SolarWaveSMMaster_v2 (one consolidated strategy, fail-closed
  realtime) reconciled vs the true Strategy Analyzer engine — decision-path 99.99% ex the 23
  documented holiday-template days, daily corr 0.9992, net +0.33% ex-holiday. **EXECUTABLE
  HEADLINE (dev): net $177,315 / Sharpe 1.17 / maxDD −$18,894 / CDaR −$14,905 / worst month
  −$7,523** — these replace the research fractional numbers (V4 §16). Genuinely flat before the
  16:45 margin cliff (the research curve never was). New residual class documented: data-gap
  overnight hold (1 episode/4.6y, Δ≈$407). v1 arrangement bug = KNOWN_ERRORS #7.

## The system, in one paragraph
Solar (13-member SolarWave ensemble on NQ 3-min, graded 0-10 MNQ by vote) is the return
backbone. Its exposure is shaped by ONE daily HTF state (prior-session close vs SMA50):
agreement ×1.25 (SM08, passed), counter-HTF shorts ×0.5 (SMV2E c1_50, passed) —
together "SOLAR_DUAL_HTF". B-MOM (noise-band + VWAP intraday momentum, frozen W8-1,
causal-execution-audited) is the diversifying second engine. Best current portfolio:
**60/40 DUAL/B-MOM, day-only, flat before 16:45** — equal-vol maxDD −$18.1k vs the V1
champion's −$25.0k, Sharpe 1.26, worst month −$6.9k. B1 overnight was DEMOTED (failed
its ablation gate). One-contract: SM14 hysteresis rule remains FINAL holder; the
A-dominant policy family (B-MOM first, Solar only at strong consensus, on the DUAL
state) is the strong CHALLENGER (NQ DD −$38-47k vs −$58.5k, Sharpe 1.24-1.37).

## What was verified/corrected this wave
- −$27.2k (PORT_TILT_532) and −$58.5k (OneLot NQ) both REAL but never comparable:
  OneLot NQ runs 1.62× the vol. Equal-vol: −$27.2k vs −$36.2k. ~75% of the gap = size.
- B-MOM edge is NOT an execution artifact (E2 causal = E0 to 0.01t/trade; survives
  +2t/side). Realistic live band = E3-E4 (~Sharpe 1.20-1.26 standalone).
- Old leverage claim trimmed: 22.5% → 21.4%/yr worst-method (L5 was the conservative
  method; ordering PORT > day-only > OneLot > Solar robust across 7 block schemes).
- HTF tilt is a MECHANISM (7/8 neighbor states improve), not an SMA50 cell.
- SM14's original script was never committed; canonical replay differs ≤2.5% (logged).
- June/July 2026 is NOT pristine OOS for anything; no untouched holdout exists.

## Claim taxonomy (Directive V2 §2 labels, current)
- SOLAR_E10: ESTABLISHED HISTORICAL FAMILY-A REFERENCE (regime-local pre-2022).
- HTF_TILT / DUAL_HTF: conditional exposure enhancement, MECHANISM-CONFIRMED. Not alpha.
- BMOM: RECENT_REGIME INDEPENDENT-ENGINE — execution audit PASSED; regime risk stands.
- SOLAR_PLUS_BMOM (DAYONLY_DUAL6040): PRIMARY DAY-ONLY CHAMPION, candidate composition.
- B1_OVERNIGHT: EXPERIMENTAL DIVERSIFIER (demoted from CORE, SMV2C P=0.737).
- PORT_TILT_532: SUPERSEDED as champion; remains the V1 reference composite.
- SolarWaveSMOneLot_v1 (SM14): ONE_CONTRACT_FINAL holder; A-dominant family CHALLENGER.
- Nothing here is "robustly validated / production ready / OOS proven / optimal".

## Standing risks (unchanged)
Both engines are current-regime (post-2020 fuel). Regime death is the true risk model;
MONITOR-01 + SM13 decay floor are load-bearing. Right-tail concentration: B-MOM top-1%
trades = 56-63% of net; Solar winner-drought DDs are normal path statistics.

## Where everything lives
DRAWDOWN_RECONCILIATION / BMOM_EXECUTION_AUDIT / B1_ABLATION / LONG_SHORT_FRONTIER /
LEVERAGE_ROBUSTNESS / ONE_CONTRACT_FRONTIER / DAY_ONLY_FRONTIER / SYSTEM_SCORECARD /
KNOWN_ERRORS_AND_CORRECTIONS / SUPERSEDED_CONCLUSIONS / NEXT_RESEARCH_QUEUE (all in
this directory). Machine state: SYSTEM_FRONTIER.yaml. Specs+outputs: runs/SMV2*.

> ### CORRECTION APPENDED 2026-08-09, same day, after red team (seq 464-465). Three retractions from item 1 above.
>
> The M1 red team returned **CONFIRMED-WITH-CORRECTIONS** with **17 defects, 2 of them
> headline-flipping**, and it did the one thing a review of this program had not done before: it
> *ran the follow-up experiments I had queued instead of running*. Full verdict verbatim at
> `runs/W18R1_M1_VOLSEASON/red_team/RED_TEAM_m1_volseason.md`; ingestion and my own independent
> verification of the load-bearing numbers in that run's REPORT.
>
> **(a) RETRACTED — "the null is CONDITIONAL" and the Wave-19 lead built on it.** Both
> de-confounded constructions were run and both are **worse**, not better. Exposure-neutral
> `f / E[f|flip]` (flips restored to 67,765 vs the control's 58,701): Sharpe **0.411**, CDaR
> **$40,759**, 0/3. Per-bar `S` resampling in *both* arms — the clean re-allocation test, with
> mean `s_eff` confirmed unchanged: ΔSharpe **−0.303**, P(ΔSharpe>0) = **0.116**. Intraday
> seasonal normalization of the Solar threshold is therefore **CLOSED UNCONDITIONALLY** across
> all three constructions. **Item 7 below is withdrawn**: "vary when `S` is sampled" is not an
> untouched surface and is not a Wave-19 lead — it was tested and it is worse. The root-cause
> *diagnosis* is unaffected and is in fact strengthened (per-bar resampling moves flips **+8.1%**
> and re-allocates as predicted: EVENING +181%, OVERNIGHT +39%, RTH −31%).
>
> **(b) RETRACTED — the §5 axis declaration.** `arm_FULL` cuts mean ensemble exposure
> **−30.9%**, raises the flat fraction 18.9% → 35.3%, and cuts contracts/day 43.9 → 25.7, while
> net falls 26.8%. **Net per unit of exposure is essentially unchanged.** M1 was a de-risking
> rule implemented through a threshold, whatever the spec declared. This is independent support
> for §5's presumption that the exposure axis is exhausted.
>
> **(c) RETRACTED — the strength of the failure.** ΔSharpe **−0.150** has a block-bootstrap
> 5–95% of **[−0.637, +0.331]** with **P(ΔSharpe>0) = 0.303** (my own run, seed 20260808;
> the reviewer got 0.277). **74.5% of the −$31,902 gap is the 106-day 2026 stub**, and
> `arm_FULL` **beats** the incumbent in 2024 (0.967 vs 0.770) and 2025 (1.290 vs 1.206). The
> verdict stands under the pre-registered AND rule, but not "with wide margins" — (a) is what
> closes the axis, not this.
>
> **Further corrections to numbers in item 1:** "member flips fall 46% **in every cohort**" is
> false — −46% is the total; per cohort it is **−32.6% / −19.7% / −57.5%**. The **+64%** mean-`S`
> figure is time-in-trend weighted and therefore partly an *effect* of the flip collapse;
> flip-weighted it is **+38.9%** (79.58 → 110.52 points). The **80.5% top-10 retention** is a
> date-matching artifact — on its own dates `arm_FULL`'s top ten sum to **100.9%** of the
> control's. Newly measured and previously unreported: **81% of the loss sits in the OVERNIGHT
> cohort**, the one the mechanism was designed to fix, and member-bars pinned at the 1,200-tick
> clamp ceiling rise **4.0% → 29.7%**.
>
> **What the reviewer could not break:** the causal seasonal estimator, re-implemented from
> scratch with a different algorithm — **max absolute difference 0.0 across all 519,714 bars**.
> Gates reproduce to the last decimal; the control rebuild matches SMV2AD to the cent including
> contracts; no other merge in the codebase carries the dtype bug (all 16 sites audited);
> `arm_HALF`'s disclosure-only status leaked nowhere.
>
> **Net effect on the §15 shift signal (item 7):** the signal is still live at ten closures, but
> the direction proposed in item 7 is dead. What survives as evidence for Wave 19 is the **D4
> cohort structure** (RTH 34.6% of bars / 81.2% of P&L; the evening quarter loses $10,989) and
> the finding that exposure and net scale together almost exactly. No replacement lead is
> asserted here; asserting one on no evidence is what item 7 did wrong.

> ### CORRECTION APPENDED 2026-08-09, after the M5 red team and the O1 blind repair (seq 466-467).
>
> **M5 red team: CONFIRMED-WITH-CORRECTIONS, 12 defects, 1 headline-flipping. The reviewer
> rebuilt all four instruments × two arms from raw bars in a fresh process and matched every
> committed daily curve to max |deviation| = $0.0000000000.** Verdict verbatim at
> `runs/W18R2_M5_XINST/red_team/RED_TEAM_m5_xinst.md`.
>
> **(d) RETRACTED — "the Sharpe effect replicates".** The pooled statistic includes **NQ, the
> cell that generated the hypothesis**. On the three NEW instruments alone the prongs are
> **0.8223** and **0.7108**, *both* below 0.85, and **no new instrument clears 0.85 on either
> prong individually** (ES 0.833/0.698, RTY 0.820/0.797, YM 0.390/0.361). Including the
> generating cell was pre-registered and disclosed, so this is a framing error, not a protocol
> breach — but the correct statement is that **neither prong replicates**, which is a stronger
> closure than the split reported in item 3 above.
>
> **(e) The M5 result lives in the same 106-day 2026 stub that M1's does.** Dropping the last
> 106 sessions moves the pooled prongs from 0.9108/0.7841 to **0.7661/0.6547**. Every instrument
> including NQ is only **3 of 5** on yearly ΔSharpe sign — below the **4 of 5** LOYO bar this
> program applied to SMV2AF one wave earlier — and *which* instruments agree is period-dependent
> (2022-23: ES+RTY; 2024-26: ES+YM+NQ; only ES is stable). The spec should have pre-registered a
> chronology gate alongside the sign count and did not. **Two independent Track-R results in one
> wave are both carried by the same final 9% of the sample. That is now a standing caution.**
>
> **(f) Two "identical construction" claims corrected.** (i) The clamp is specified in ticks and
> the *rule* is identical, but the *object* is not: it binds on **13.5% of ES member-bars vs 2.9%
> on NQ**, floors ES's VolMult-6 member on 71.96% of bars, and leaves the two arms bit-identical
> on 13.3% of ES member-bars. (ii) RTY and YM carry an **undisclosed contiguous eight-session
> hole** (2023-04-05 truncated at 14:03, 04-06..04-14 absent, resuming 04-16) creating a ~50σ
> splice that perturbs sigma460 by +11% and ATR460 by +5.8% — *different* amounts, so the pairing
> breaks for ~460 bars. My pre-registered substrate gate (coverage ≥ 0.95) **structurally cannot
> see an 8-session hole**. Excising it changes no verdict and in fact helps RTY; the gate design
> is what is at fault.
>
> **(g) The "0.753 → 0.784" comparison was not like-for-like** (dollar-CDaR on the DUAL leg vs a
> pooled ratio on the raw leg) and is withdrawn as phrased. Like-for-like, NQ moved
> **0.753 → 0.7547** — nowhere — and the NEW-only pooled figure is **0.7108**. The conclusion it
> supported (the power hypothesis is rejected) survives on better grounds.
>
> **What the M5 reviewer could not break:** the `sm.TICK` per-instrument patch (bit-exact rebuild;
> and it is load-bearing — a stale `TICK` would have flipped YM's sign and produced a false 3-of-3);
> the turnover/friction alternative explanation (Δcommission is 2-4 orders of magnitude smaller
> than Δnet; ES traded *more* and improved anyway; it is a pure mean effect); **ESS 3.68**
> (Spearman 4.005, and the correlation of the bootstrap estimators themselves gives 3.63/3.66);
> and the pooling rule — **eight alternatives were tested and none flips the verdict**; only
> post-hoc deletion of YM passes, which is precisely what the pre-registration exists to prevent.
> The as-run rule is the **most generous** of the honest set, so the verdict is if anything too
> kind.
>
> ---
>
> **O1 BLIND REPAIR — done, and O2 stays BLOCKED, now for a different reason.**
> `src/analytics/primary_objective_v2.py` + `test_primary_objective_v2.py` (34/34, all fixtures
> synthetic, no candidate P&L loaded), with the argument written first in
> `runs/W17_C4_COMPLIANCE/O1_REPAIR_PREREGISTRATION.md`. **D1** resolved as an equal-weight
> mixture applied to *both* terms (the mixture is `J(F̄)` for one namable model; no max-based rule
> is `J(F)` for any `F`), with `J_worst = min_m J_m` always returned alongside a mandatory
> `model_determined_sign` flag. **D4**: λ **1.0 → 1.367725** — the shipped value was **73.1% of
> correct** — after two corrections, the compounded-vs-non-compounded convention *and* a
> horizon double-count the Wave-17 red team had missed. **D9** was three defects, not one, and
> one of them flips J's sign on a synthetic fixture.
>
> **The repair moves the daily objective UP, +0.0210 → +0.1241**, because the D1 fix (+0.161)
> dominates the λ fix (−0.058). The repairing agent disclosed, unprompted, that **the rule it
> chose is the most favourable of the four options it considered and that it could not be blind
> to this**, because v1 publishes every component. Applying §13 rule 11 — *something looks too
> good, assume a bug first* — **O2 retro-scoring remains BLOCKED**, no longer on "the objective
> is broken" but on "the aggregation choice that raised the score has not been independently
> reviewed." That review is the first Track-E item of Wave 19. The **O1a finding survives and is
> cleaner**: daily **+0.124** vs intraday **−0.140** on the same mixture. Note also that
> `model_determined_sign` fires for Product A (J = +0.124 while J_worst = −0.126), so under the
> repaired output contract **Product A's daily objective may not be quoted as a single number at
> all**.
>
> Governance defect, mine: `primary_objective_v2.py` was committed at `3e02b2f` as a side effect
> of a broad `git add -A` while the repair was still in flight, i.e. **the module was in the repo
> before its written justification was**. The pre-registration is committed now. Nothing imports
> v2 and O2 has not run, so no result was produced from the un-justified state.
>
> **[SUPERSEDED 2026-08-09: the +0.1241/−0.1259 (rounded +0.124/−0.126) pair disclosed above was
> HAND ARITHMETIC on the already-published v1 per-method components — `primary_objective_v2` had
> still never been run end-to-end on real candidate P&L at the time this was written. It has now
> been run, in `runs/O2_OWNER_UTILITY_READJUDICATION/`: the real module output on the certified
> Product-A legacy-proxy daily series is J=+0.0549 (mixture) / J=−0.2220 (Γ-minimax) — same sign
> pattern (still INCONCLUSIVE), but materially different magnitude from the hand-computed pair
> above. See `runs/O2_OWNER_UTILITY_READJUDICATION/REPORT.md` and
> `runs/O2_OWNER_UTILITY_READJUDICATION/out/o2_scoring_summary.csv`. Do not cite the hand-computed
> pair as current v2 output going forward.]**
