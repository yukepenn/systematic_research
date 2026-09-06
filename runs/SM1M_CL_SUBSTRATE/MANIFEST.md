# SM1M_CL_SUBSTRATE — MANIFEST

**Run class:** $0 DATA EXTRACTION (data materialization with a MANIFEST, SM1M pattern; no
hypothesis, no preregistration, no signal, no P&L). Built 2026-09-06.

Materializes the **CL (WTI crude oil future) 1-minute surface** — a sixth member of the SM1M
substrate family (after NQ, MNQ, ES, RTY, YM, ZB). 🔒 **CL is a GENUINELY UNTOUCHED market for
this program**: no signal, return, or strategy has ever been computed on it here, and none is
computed in this run. **The coordinator will freeze a discovery/holdout boundary before any
signal research** — this run only lays down the raw substrate.

## Object

| | |
|---|---|
| parquet | `runs/SM1M_CL_SUBSTRATE/out/cl_1m_2022_2026.parquet` (24,940,827 bytes) |
| **sha256** | `e587486c23f5b61184b6a49aaeebc77f1a3e74e0731d8d0f4192087587adc137` (identical across two independent builds) |
| **rows** | **1,608,018** |
| **sessions** | **1,182** (18:00→17:00 ET label rule, `src/analytics/runlib.py` `session_date`; per-session bars median 1,372 / p10 1,344 / min 590 / max 1,380 — CL runs a near-24h grid, sparse minutes are genuine zero-trade minutes) |
| bar range | 2022-01-02 18:01:00 → 2026-07-31 16:59:00 (END-stamped ET, **no shift**) |
| session range | **2022-01-03 → 2026-07-31** |
| schema | `time, open, high, low, close, volume` — byte-identical column set to the other SM1M substrates (`time` datetime64[ns], OHLC float64, `volume` int64) |
| series | "CL 09-26" **merge back-adjusted front-month chain**, resolved **CLU6**, CL's MONTHLY roll. Anchor segment (CL 09-26) is effectively un-adjusted (median offset **+0.16 pts** over its 12 front-month sessions — the small residual is intraday close-timing, the 16:59 ET minute close vs the day bar's recorded close, not a back-adjustment offset). Earlier segments carry the expected cumulative monthly-roll offsets, **negative** for CL over this window (medians −10.9 → −39.5 pts, see profile). Volume is the true front contract's own (verified exact below). |

## ⭐ CL-specific: PRICE-GRID CHECK (read before using prices)

`SWMinuteExport_v1` formats prices with `ToString("F2")`. **CL's outright tick is $0.01 exactly**,
and back-adjustment adds a constant that is itself a whole multiple of $0.01 (a difference of two
on-grid prices), so the entire merge back-adjusted series lies on the 0.01 grid. F2 emits exactly
two decimals **= the 0.01 grid**, so **F2 is LOSS-FREE for CL** — unlike ZB, whose 1/32 (0.03125)
grid F2 destroyed and had to be restored. **No restoration was needed.** Measured on the full file
(program output, verbatim):

```
PRICE-GRID CHECK  (CL outright tick = $0.01 = F2 precision; F2 loss-free)
  max |csv - snapped-to-0.01|            0.0000000000   (must be <= half-tick 0.005: PASS)
  share of prices already on 0.01 grid   100.000000%    (F2 exactly encodes CL's 0.01 grid, nothing finer to destroy)
```

Snapping to 0.01 only removed IEEE-754 parse noise (residual measured 0.0), so the parquet stores
exact on-grid prices. Corroboration: every continuous-minus-day-store close offset is a whole
multiple of 0.01 (see cross-check).

## Provenance

1. `SWMinuteExport_v1` (`research/scalping_lab/src/ninjascript/`, sha256
   `48c21a775326b69a731fea27945c9b41b99ccec4553992bee5f75acd92cdc89d`). The class was **already
   installed** from the same-day MNQ/ZB extractions; the repo copy and the NT8
   `bin/Custom/Strategies/` copy were **sha256-VERIFIED IDENTICAL**, so **NO file was copied and
   NO `NinjaTrader.Custom.dll` recompile was triggered against the running real-money book.**
   Class resolved via `LookupNinjaScriptSymbol` in fresh assembly
   `40daedcc00a24a0ba7d83631d1c25d80`. No source ever left the machine.
2. CrossTrade `RunStrategyBacktest` job `2649a17d913f4c66` (engine `nt8_strategy_analyzer`,
   NT8 8.1.8.1, fingerprint `sha256:b4255f1b0dd7fba1`, **isolated Backtest account, 0 trades /
   0 orders / $0 commission**): instrument **CL 09-26** (resolved `CLU6`), Minute/1 Last,
   `from 2022-01-01T00:00:00Z`, `to 2026-07-31T21:59:59Z` = `session_close_boundary_utc(2026-07-31)`
   — **the §5 seal was applied at the export boundary**, before any row existed. CL's **own**
   primary trading hours were used (`trading_hours` was not overridden — NQ hours were NOT
   forced). Loaded **1,609,396 bars**.
3. Raw CSV `Documents/NinjaTrader 8/out/cl1m_2022_2026_1m.csv`
   (sha256 `3d7364ec1e7cd702933d25a23c11e6b8d314c47aa5394888a4eb038bc4609fd3`, kept outside the
   repo per the SM1M pattern). 1,608,018 data rows.
4. `src/build_cl_substrate.py` → price-grid check, gates, session labels, hard seal drop, parquet.
   Full program output: `out/build_log.txt`.

## SEAL assertion (program output, verbatim)

```
SEAL RULE (CLAUDE.md s5 / LOCKED_FORWARD): HARD-DROP session >= 2026-08-01
  rows dropped at build time             0   (export was already capped at the s5 boundary; 0 expected)
  max retained session date              2026-07-31
  ASSERT max retained session < 2026-08-01   PASS
```

Independent verification (fresh re-open): rows 1,608,018, sessions 1,182, bar span
2022-01-02 18:01:00 → 2026-07-31 16:59:00, session span 2022-01-03 → 2026-07-31, **max session
2026-07-31 < 2026-08-01 PASS**, time strictly increasing PASS.

## Gates and cross-checks (from `out/build_log.txt`)

- time strictly increasing / no stamps in (17:00,18:00] ET / OHLC sanity / volume ≥ 0 — all PASS.
- **Cross-source volume vs the TRUE unmerged day store** (`ncd_day.py`, format validated against
  GetBars; CL is monthly so "front" = the max-day-volume candidate around the date):
  - 2023-02-15 front `CL 03-23`: minute-sum **180,236 = 180,236** day-bar (exact)
  - 2024-05-14 front `CL 06-24`: minute-sum **166,746 = 166,746** day-bar (exact)
  - 2025-10-15 front `CL 11-25`: minute-sum 100,281 vs 100,288 day-bar, **rel 0.0070% MATCH**

  The merged minute series carries the true front contract's own volume, not a copy — the
  volume-crossover roll is visible, exactly as in the other substrates.
- All continuous-minus-day close offsets are whole 0.01 multiples (grid corroboration): PASS.

## Back-adjustment profile (documentation, not a gate)

Merged "CL 09-26" last-1m-close minus true day-store close, median per contract. Nonzero before
the last roll is the expected merge back-adjustment; the sign is **negative** for CL over this
window (its cumulative roll basis), the analogue of MNQ's positive profile.

```
CL 03-22: median(last-1m-close - day-close) over 25 sessions = -39.48 pts
CL 03-23: median(last-1m-close - day-close) over 24 sessions = -25.99 pts
CL 06-24: median(last-1m-close - day-close) over 23 sessions = -23.08 pts
CL 11-25: median(last-1m-close - day-close) over 23 sessions = -10.86 pts
CL 09-26: median(last-1m-close - day-close) over 12 sessions =  +0.16 pts   <- anchor, ~0
```

## 🔴 LIVE-STATE CHECK — before and after (real-money book intact)

The live real-money book is P1-only on account `2047681`. All export work ran on the **isolated
Backtest account**; nothing was placed/modified/enabled/disabled/ordered on any live account, and
no `Custom.dll` recompile was triggered (byte-identical exporter reused).

| | BEFORE (05:42 ET) | AFTER |
|---|---|---|
| `ListAllStrategies` count | 1 | 1 |
| `2047681` strategyCount | 1 | 1 |
| leg | `399562885` `WeeklyEdgeP1PCTMnq_v1` | same |
| state / enabled | Realtime / true | Realtime / true |
| position / qty | **Flat / 0** | **Flat / 0** |
| currentBars | `[357050, 355797]` | `[357050, 355797]` (**unchanged**) |
| ordersCount / active | 2 / 0 | 2 / 0 |
| params | populated (`MnqPerNq=3`, `ExpectInstrument "NQ 09-26"`, `ExpectMnq "MNQ 09-26"`, …) | **identical** |

CME session state at run time: **Sunday 2026-09-06 ~05:42 ET, pre-18:00 ET Globex open → session
CLOSED.** No stale `Finalized` shells; no second live row. **P1 intact.**

## 5-row sample

```
                   time   open   high    low  close  volume
0   2022-01-02 18:01:00  35.56  35.80  35.45  35.60     723
1   2022-01-02 18:02:00  35.59  35.67  35.52  35.64     168
2   2022-01-02 18:03:00  35.67  35.70  35.50  35.54     147
-3  2026-07-31 16:58:00  86.21  86.83  86.19  86.59     610
-1  2026-07-31 16:59:00  86.59  86.63  86.24  86.30     217
```

(Early-2022 prices ~$35 are the back-adjusted continuous, ~$40 below the then-real WTI ~$76 —
the expected large cumulative monthly-roll offset. Late-July-2026 prices ~$86 are near the true
CLU6 level, the un-adjusted anchor.)

## Notes

- **Window**: requested `from 2022-01-01`, so the first session is **2022-01-03** (Sunday
  2022-01-02 18:00 ET open) with **no pre-2022 rows** — unlike MNQ/ZB, which kept a few
  pre-window sessions. This directly satisfies the task window 2022-01-01 → 2026-07-31.
- CL's CME session (18:00 ET → 17:00 ET with a daily 17:00–18:00 ET break) shares the SAME
  structure as the index/rate substrates, so the SAME `session_date` label rule and the SAME
  "no stamps in (17:00,18:00] ET" gate apply. The instrument's OWN trading hours were used.
- Provider depth: the local day store holds CL monthly contracts `CL 01-09 … CL 12-27`,
  confirming the merge chain's back-history is real, not synthesized.
- No local minute-`.ncd` decode exists (`runs/VOLUME00_20260828`: "MINUTE LAYOUT NOT RESOLVED");
  the NT8-side export is the validated minute-extraction tooling.
- Side effects outside this run dir: one export CSV in `Documents/NinjaTrader 8/out/`
  (`cl1m_2022_2026_1m.csv`). No file copied into NT8, no recompile, no orders, no strategy
  enablement, no connection changes; the backtest ran on the isolated Backtest account only.
  Nothing in the repo outside `runs/SM1M_CL_SUBSTRATE/` was touched.
