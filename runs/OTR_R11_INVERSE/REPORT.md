# OTR_R11_INVERSE — report

Spec preregistered 2026-08-24 before any readout; amendments 1–4 each committed before the
readout they authorise. Directive v4.0 phases P1–P3 (sections 5–13).
**No P&L objective appears anywhere in this run.** Every adjudication is by feasibility
against exact daily labels.

## What this run was for

Replace the R1e "which of our trades must be REMOVED" formulation — which presupposed the
original trades are a *subset* of one candidate stream — with a **set-valued inverse
trade-path reconstruction** constrained by every metric visible in the trader's NT8 Daily
Analysis table, including the previously unused path statistics **avg_MAE / avg_MFE**.

The old premise was not merely loosely worded, it was **structurally false**: on 2023-01-13
and 2023-01-17 the incumbent stream produces *fewer* trades than the report, and no removal
can create a trade.

## P1 — platform semantics (`../../research/.../platform_semantics/NT8_DAILY_ANALYSIS_SEMANTICS.md`)

- **MAE/MFE certified 90/90 exact** against NT8's own serialised `MaeCurrency`/`MfeCurrency`
  (8 candidate definitions tested). The winning rule is fill-type aware, which is forced by
  the fact that NT8 has no intrabar path without Tick Replay.
- **ETD = MFE − net profit**, 90/90 — a derived display carrying no extra information.
- The **$5-tick lattice** turns two rounded display cells per day into two exact integers,
  and recovers every cropped cell as a unique lattice point. **22 new exact constraints.**
- Commission read off the report: **$4.18/RT (2023)**, **$5.68/RT (Feb-2025)**.
- By-product: our parquet substrate reproduces NT8's **High and Low**, not just its closes
  (MAE/MFE depend on H/L; net P&L does not).

## P2/P3 — the inverse (`../../research/.../solar_family/inverse/UNIVERSE_ADJUDICATION.md`)

132 cells (6 event universes × 2 exit rules × 11 days), nine simultaneous exact constraints
each. Headline:

| | days explained / 11 |
|---|---|
| INCLUSIVE exit, session-date rows | 5 |
| **STRICT exit**, session-date rows | **8** (each a *unique* path) |
| **STRICT exit, CALENDAR-date rows** | **11** |

Three mechanism findings, each predicted or falsified rather than fitted:

1. **The exit test is STRICT** (`close < TrailingStop`), equivalent to "exit only on a
   genuine trend flip". Predicted in advance from two days whose *only* defect was one
   trade's exit price while sum-MAE and sum-MFE were already exact — he reversed where we
   exited early. The two rules differ only on exact-touch bars, which is why no aggregate
   statistic could ever have separated them.
2. **T2 and T3 entries are not used by the 2023 build.** Every feasible day in every
   universe solves with `min_extra = 0`. This removes the entry-layer conclusion from the
   standing "A3-A5 implies a pullback layer" story (R12 had already redirected it from T2 to
   T3 on event-sensitivity grounds).
3. **The daily row is a CALENDAR exit date, not a trading-session date** — the single change
   that takes 8/11 to 11/11. Previously recorded NOT SEPARABLE; that was premature, and the
   three unexplainable days are exactly what separates the readings.

Mechanisms tested and eliminated for the three hard days before the calendar rule was found:
T2 (both PullbackEarly settings), T3, fixed intrabar stops 70–200 pts (26 configurations,
zero solutions), and contract/merge policy (analytically impossible — no roll in Jan-2023,
and P&L/MAE/MFE are all differences, so a back-adjustment offset cancels identically).

## P4 — the gate (`../../research/.../solar_family/CAND2_REAUDIT.md`)

Re-adjudicated against **15 unique-path invariant labels** (10 TAKE / 5 SKIP), not P&L:

- **X NECESSARY**, **C's trigger SUPPORTED but only as an interval (30.08, 1148.52]**.
- **C's 360-minute scope FALSIFIED** — no duration can block 01-05 at MfO 334 while allowing
  01-13 at MfO 154 with a *worse* prior session.
- **K, cap, cooldown UNIDENTIFIED** — they never bind on the labels. They had been retained
  on master-window P&L, which directive section 13 forbids as a retention criterion.
- One apparent "skip" was **`BarsRequiredToTrade = 20`**, a platform effect, and it
  independently confirms the backtest starts at the 2023-01-03 session (18:00 on 01-02).
- **Structural**: on a T1 flip bar the anchor resets to the close, so `close − TrendVector ≡ ±V`,
  `close − TrailingStop ≡ ±S` and `Signal_Trend ≡ ±2` always. **Any strength-based or
  distance-based ENTRY filter is inert for T1 entries** — a whole family of candidate
  wrapper rules is ruled out at zero cost.

## Preregistered predictions, as they landed

| prediction | source | outcome |
|---|---|---|
| MAE/MFE definition recoverable to 90/90 | spec H-R11-1 | **PASS** |
| day-grouping separable? | spec H-R11-2 | recorded NOT SEPARABLE, then **OVERTURNED** by amendment 4 → CALENDAR |
| some universe explains every day | spec H-R11-3 | **PASS only after** the calendar correction |
| STRICT moves master count/hold toward target | amendment 1 | **FAIL** (+5.2 %→+7.8 %, +1.4 %→+2.8 %). Confounded: the gate was fitted under INCLUSIVE and is now partly falsified. Recorded, not explained away. |
| every gate component necessary | amendment 2 | **FAIL** — 3 of 6 unidentified, 1 falsified |
| an early fixed stop explains the hard days | amendment 3 | **FALSIFIED** |
| a global single path exists under CALENDAR | amendment 4 | see `out/r18_global_log.txt` |

## Status vocabulary changes this run forces

- "42/42 cent-exact ground-truth trade labels" → **RETIRED**. Replaced by 15
  **INVARIANT_LABELS** that are stronger (unique within the universe) but still conditional
  on (universe = T1-only, exit rule = STRICT, day rule = calendar).
- CAND2 ↔ NT8 remains **IMPLEMENTATION_PARITY** only. Nothing in this run establishes
  ORIGINAL_PARITY.
- 2023-01-04 / 12 / 17 moved from "assumed explicable" → "explicable only under the
  CALENDAR reading".

## Artefacts

`out/mae_mfe_calibration.json`, `out/gate_labels.csv`, `out/gate_component_scores.csv`,
`out/r11b_log.txt`, `out/r13_master_exitrule.csv`, `out/r15_stop_sweep.csv`,
`out/r16_log.txt`, `out/r17_log.txt`, `out/r18_global_log.txt`,
`out/feasible_paths.json`, `out/r18_global_paths.json`.
Code: `solar_family/src/inverse_core.py`, `inverse_multiday.py`, `run_r11a_maemfe_calib.py`,
`run_r11b_inverse.py`, `run_r13_strict_master.py`, `run_r14_gate.py`, `run_r18_global.py`.
