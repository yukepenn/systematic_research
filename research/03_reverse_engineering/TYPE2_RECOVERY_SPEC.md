# TYPE2_RECOVERY_SPEC — preregistered before any new export is read

_2026-08-07 · Author: research controller · Status: registered before data collection_

## Objective

Recover the **exact** Type-2 ("Pb"/pullback) rule of RenkoKings Solar Wave RK, and the exact
signal-priority behaviour when Type 2 coincides with Type 1/3 — completing the open model so
that `Signal_Trade` is reproducible bar-for-bar at 100%, across multiple parameter
combinations, not only the canonical one.

## Provenance boundary (unchanged)

Ground truth = the licensed indicator's **published `Series<double>` outputs**, observed by a
read-only exporter strategy. No decryption, unpacking, patching, memory dumping, or any other
circumvention of the Agile.NET protection. The vendor assembly is not modified. The recovered
rule is behavioural mathematics, not vendor source code.

## What is already known (from SOLARWAVE_MATH.md, fixed)

- Core ladder + Type 1 + Type 3 + wave/weak automaton: recovered exactly (close-only).
- Type-2 retrace distribution vs anchor: median ≈ 89 ticks ≈ `OffsetMultiplierTrend − 1 tick`
  ⇒ prime hypothesis: Type 2 tests an intrabar excursion (High/Low) against **TrendVector**.
- On collision bars the plot shows Type 2 over Type 3 (200 such bars in the canonical window).
- `PullbackEarly` and `PullbackSplit` feed only the Type-2 branch (empirically inert elsewhere).

## Instrument: SolarWaveRKLedgerV2 (new class; V1 untouched)

Read-only exporter, trades nothing. Adds to V1: **Open/High/Low**, volume, bar index, tick
size, session-first-bar flag, and a `#`-comment header echoing every effective vendor
parameter. All six vendor constructor args + export path are `[NinjaScriptProperty]` inputs so
probe runs vary parameters **without recompiling** (no hot-reload hazard; one compiled class).

Columns:
`time,bar,open,high,low,close,volume,first_bar_of_session,signal_trade,signal_trend,signal_wave,trailing_stop,trend_vector`

## Preregistered export matrix

| Job | Params (TM/SM/SS/WWS/PE/PS) | TF | Window (UTC) | Purpose |
|---|---|---|---|---|
| E1 | 90/179/5/10/true/10 | 1m | 2023-01-01T06:00:00 → 2025-02-02T22:59:59 | canonical, row-aligned with sw01 ledger; main decode set |
| E2 | 90/179/5/10/**false**/10 | 1m | 2024-01-01T06:00:00 → 2024-07-01T21:59:59 | PullbackEarly semantics |
| E3 | 90/179/5/10/true/**3** | 1m | same probe window | PullbackSplit small |
| E4 | 90/179/5/10/true/**25** | 1m | same probe window | PullbackSplit large |
| E5 | **45**/179/5/10/true/10 | 1m | same probe window | does the T2 trigger move with TrendVector? |
| E6 | **135**/179/5/10/true/10 | 1m | same probe window | same, opposite direction |
| E7 | 90/**240**/5/10/true/10 | 1m | same probe window | S-dependence of T2 |
| E8 | 90/179/**8**/**15**/true/10 | 1m | same probe window | weak-state interplay with T2 |
| E9 | 90/179/5/10/true/10 | **3m** | same probe window | timeframe generality |

Probe window = 2024-01-01T06:00:00Z → 2024-07-01T21:59:59Z (6 months; EDT boundary rule:
`to` = one second before next 18:00 ET open). E2–E9 are cheap; E1 is the workhorse.

## Hypothesis space (tested exhaustively, no favourite assumed)

For each candidate trigger T, gates G, and re-arm R, simulate and score:
- **T:** Low/High touches vs strictly breaks TrendVector; same vs TrailingStop-relative retrace;
  close-based retrace; retrace measured from anchor in ticks; intrabar excursion vs
  close-confirmed.
- **G:** direction (with-trend pullback only?); weak vs strong state; wave index; bars since
  flip; bars since last extreme; PullbackEarly toggling touch-vs-break or intrabar-vs-close.
- **R:** PullbackSplit as min bars between consecutive T2s (WeakWeakSplit-analogue); re-arm on
  new extreme; re-arm on T1/T3.
- **Priority:** ordering when T2 collides with T1 or T3 on the same bar.

## Exact-match metrics (event level, not accuracy percentage)

1. Type-2 timestamp set: precision AND recall must both be 1.0000.
2. Type-2 sign: 100%.
3. Full `Signal_Trade` per-bar parity: 100% (after applying recovered priority rule).
4. `Signal_Wave`/`Signal_Trend` residual mismatches: 0 after collision handling.
5. All of the above on **every** probe config E2–E9, not just E1.

A high-but-imperfect match with *systematic* residual structure (e.g. all misses near session
boundaries, or all one bar late) is a WRONG rule per the campaign standard — iterate, do not
accept.

## Pass/fail gates

- **PASS:** all five metrics at 100% on E1–E9 ⇒ update `solarwave.py`, build `SolarWaveOpenV2`
  (complete indicator + strategy wrapper), then the multi-parameter multi-period parity gate.
- **FAIL/BLOCKED:** if close+OHLC observables cannot separate surviving hypotheses, design
  additional legal probes (different parameter corners); if still inseparable, document the
  ambiguity class precisely and mark INCONCLUSIVE with the surviving-rule set.

## Config accounting

Exporter runs are instrumentation (seq 0), not candidate-search points. Registered in
experiments.yaml as RE02.
