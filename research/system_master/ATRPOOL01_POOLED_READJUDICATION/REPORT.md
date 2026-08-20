# ATRPOOL01 — REPORT (readout 2026-08-19; spec frozen at 5db5318 BEFORE any pooled statistic)

_Date note: the frozen SPEC's header labels this "wave 2026-08-20" — a calendar slip (actual
date 2026-08-19, third wave of a two-day sequence). Cosmetic only; the seed (20260820) and
every constant are exactly as frozen._

**Verdict: FAIL — G1's pooled CDaR confidence lands at 0.8910 against the preregistered 0.90
bar. Per the frozen decision rule, the sigma-ESTIMATOR axis (ATR/range/semivariance/vol-of-vol
blends, DR_V4 candidates 3/6/8) is PERMANENTLY CLOSED, and instrument-level re-adjudication of
closed leads is exhausted program-wide (this was, by its own §2.5, the one-time transitional
case — win or lose). No shadow slot. Alpha budget 1/2 spent this wave.**

## Numbers (all gates, frozen constants, seed 20260820, B=10,000)

| gate | requirement | result | verdict |
|---|---|---|---|
| G0 integrity | 8 published endpoints reproduce | all exact (±$0.02 / ±0.0001) | PASS |
| **G1 pooled (n=5,269)** | P(dSharpe>0)≥0.90 AND P(dCDaR>0)≥0.90 | **0.9963 / 0.8910** | **FAIL** |
| G2 era consistency | era dSharpe>0 both; era P(dCDaR)≥0.55 both | dev 0.7584 / hist 0.8902 | PASS |
| G3-SPLIT | both era means>0; ≥1 CI_lo>0; no CI_hi<0 | pre-2020 +$13.39/d CI [+0.48,+26.39]; post-2020 +$26.66/d CI [−3.29,+56.70] | PASS |
| G4 pooled right tail | retention ≥0.95 | 1.0065 (top-10 incl. 2020-03-13, 2018-12-26) | PASS |
| G5 stratified convention | both prongs ≥0.85 | 0.9967 / 0.8903 | PASS (its own bar) |
| G1↔G5 agreement | same pass/fail direction | disagree (bar artifact: 0.8910 vs 0.90 / 0.8903 vs 0.85) | flagged |

Pooled point estimates (disclosure): Sharpe 0.3352 → 0.3875; CDaR5 (k=263) $213,319 →
$184,738 (−13.4%); hist-era CDaR5 (k=206) $215,276 → $186,811 (−13.2%).

## What the program bought with this shot

1. **The effect is very probably real — and that is not enough.** Every direction-consistency
   check passed: hist-era tail confidence 0.8902, pre-2020 daily-diff CI entirely above zero,
   pooled Sharpe confidence 0.9963, right tail untouched across 20 years. Under SMV2AJ's
   ORIGINAL 0.85 bar both prongs would have cleared (0.9963/0.8910). But that bar was spent in
   SMV2AJ; the second look was priced at 0.90 in the frozen spec, with permanent closure
   accepted in advance. 0.8910 < 0.90. The rule, not the narrative, decides. Closed.
2. **The instrument finding stands regardless of the verdict** (power audit, §5 of SPEC):
   the dev-only CDaR prong had power 0.207 against its own point effect, and its median
   simulated outcome (0.7533) matches SMV2AJ's observed 0.7529 almost exactly. **Prospective
   protocol amendment (now standing): every future R2 confirmation runs its confidence gate on
   the pooled dev+hist instrument from the start wherever a hist substrate exists.** Future
   candidates will never again be closed by an instrument with one-in-five power — they will
   face one adequately-powered bar, once.
3. **CLOCKHIST01 (5m-clock old-regime completion) is dead by the same protocol note** — worth
   recording so nobody re-derives it: SMV2W's dev confidence gate failed on its own terms
   (P(dSharpe)=0.642), so completing its structurally-blocked old-regime gate could only
   matter via a pooled re-adjudication, which §2.5 has now exhausted program-wide. Do not
   queue it.
4. Solar-core mechanism ledger after this wave: the core has now survived **six** independent
   challenge families (memory-460, cohorts, MA30/59, T2/T3, clock ×3, sigma-estimator) — the
   last one at a bar harsher than the one that first closed it, with 4.6× the data. The
   incumbent sigma460-only core is not an untested default; it is the repeatedly re-earned
   winner of every funded alternative on 20 years of evidence.

## Red-team disposition

**CONFIRMED** (`out/redteam_verification.json`). Independent fresh reimplementation reproduced
G1 bit-exact (0.9963 / 0.8910), and the same independent code fed SMV2AJ's dev pair with the
original seed 20260808 reproduces the published 0.9316 / 0.7529 exactly — battery-verbatim
equivalence proven end-to-end. **Seed sensitivity (disclosure, house convention): seeds
{1, 2, 3, 20260808, 777} give P(dCDaR>0) = 0.8915 / 0.8878 / 0.8884 / 0.8921 / 0.8890 — no
seed reaches 0.90**; MC SE ≈ 0.0031, the frozen 0.8910 sits 2.9 SE below the bar (pooling all
six draws: 0.8900 ± 0.0013, ~7.9 SE below). The FAIL is not a Monte-Carlo artifact, and it is
overdetermined (the G1↔G5 convention-disagreement clause independently forces FAIL).

Two non-verdict-affecting corrections, disclosed: (1) G2/G3/G5 used derived seeds
(SEED+1…+5) where the SPEC text literally says seed=20260820 — zero post-hoc freedom (the
executed script was frozen in the SAME prereg commit 5db5318 and is byte-identical), and every
affected gate passes under either seed interpretation with unflippable margins (G3 pre-2020
CI_lo positive across all 8 seeds tested, 0.479-0.897; G5 ~13 MC SE above its bar).
(2) SPEC §4's aside that dev P(dCDaR)=0.7529 "will reproduce" was wrong verbatim — that value
is seed-20260808-specific; the derived seed gives 0.7584. Same conclusion either way.

## Artifacts

`out/power_audit.json` (pre-freeze instrumentation), `out/atrpool01_results.json` (one-shot
readout), `out/redteam_verification.json`. Code: `src/00_power_audit.py`, `src/01_atrpool01.py`.
Data: SMV2AJ committed curves only; no simulator run; LOCKED_FORWARD untouched (artifacts end
2026-05-29).
