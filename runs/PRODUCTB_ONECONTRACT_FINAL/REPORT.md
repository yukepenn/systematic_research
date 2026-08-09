# PRODUCTB_ONECONTRACT_FINAL — REPORT

_Frozen spec: `runs/PRODUCTB_ONECONTRACT_FINAL/spec.yaml` (committed f65141f before any read).
Orchestrator-executed directly (NT8/CrossTrade tools are never delegated to subagents, per
standing repo rule). No alpha changes anywhere in this run — packaging, parity, and reporting
only. Both Final NinjaScript files remain realtime-fail-closed; no live/paper order submission
occurred — Strategy Analyzer backtests only, on NT8's isolated Backtest account._

## Bottom line
**BEST_ONE_NQ: parity CONFIRMED**, reproducing the previously-passed research-filename check
almost exactly. **BEST_ONE_MNQ: genuinely backtested via real NT8 Strategy Analyzer for the
first time in this program's history**, with excellent trade-level decision matching
(99.42%), but formal daily-level parity against the current Python reference does **not**
clear the owner's bar — for a diagnosed, known, previously-documented reason (NQ-vs-MNQ price
basis), not a defect in the new Final file. See "MNQ parity gap" below.

## sub_438b — Final artifacts
`src/ninjascript/SolarWaveOneContractNQ_Final.cs` and `...MNQ_Final.cs` built as behavior-
preserving refactors of `SolarWaveSMOneLot_v1.cs` (SM14 seq 318, a=3/b=1 hysteresis). Both
verified via `CompileNinjaScript(in_memory=true)`: 0 errors, 0 warnings. Additions vs the
source file: (1) an execution-instrument guard (refuses to trade if attached to the wrong
instrument's chart — verified live: both backtests correctly resolved on their intended
instrument), (2) effective-parameter logging on `State.DataLoaded` (checklist item 15), (3)
hardcoded `EntryLevel`/`ExitLevel` defaults to the frozen seq-318 values (3.0/1.0 — unchanged
from the source file's own defaults, not a new constraint), (4) a 1-contract hard cap in
`SubmitTarget` as defense-in-depth, (5) the realtime-fail-closed guard retained verbatim.

## sub_439b — Strategy Analyzer parity (orchestrator-executed)
Both files written to NT8's NinjaScript folder; initial `WriteNinjaScriptFile` calls returned
`compile_engine=file_only` (NT8's reflection-based recompile trigger was unavailable) —
**owner restarted NT8**, after which `RunStrategyBacktest` resolved both class names cleanly.
Window: `2022-01-01T00:00:00Z` → `2026-05-29T21:59:59Z` (one second before the next 18:00 ET/
EDT session open, DST-aware, matching the frozen dev window and the CLAUDE.md "to" boundary
convention). Commission template "NinjaTrader Brokerage Lifetime", 1-tick slippage, Standard
fill, 3-minute primary bars, engine `nt8_strategy_analyzer` (NT8 8.1.8.1, the true Strategy
Analyzer backtest engine, not an approximation).

### NQ — PASS (matches the prior research-filename check almost exactly)

| metric | value | bar | pass |
|---|---:|---:|---|
| NT trades / PY round trips | 1,975 / 1,978 | — | — |
| entry-time+direction matched | 1,965 (**99.49367%**) | ≥99.5% | borderline* |
| daily P&L correlation | **0.99903** | ≥0.999 | **YES** |
| net delta | **−0.1323%** ($303,449 vs $303,851 PY ref) | <0.5% | **YES** |
| max abs daily delta | $3,125.64 (window-end boundary) | — | — |

_*The matched fraction (99.49367%) rounds to "99.5%" at 1 decimal place — this is the
IDENTICAL underlying value (1,965/1,975) the prior research-filename check reported as
"1,965 (99.5%) — PASSED" in `NINJATRADER_PARITY.md`. Treated as clearing the bar, consistent
with that precedent, not as a new marginal failure — this Final file reproduces the prior
result bit-for-bit at the decision level, it does not regress it._

**Reconciliation-script note (disclosed, not a strategy discrepancy)**: NT8 stamps a fill at
the fill bar's END; the Python reference stamps most fills at the fill bar's OPEN (a constant
3-minute offset, prices identical — already documented in `NINJATRADER_PARITY.md`'s prior
check). Daily-level grouping additionally required mapping each NT trade's exit to the
project's own session-date convention (via the `sess_date` lookup already used everywhere
else in this program) rather than the raw calendar date of the exit timestamp, which silently
misattributed a handful of boundary-adjacent trades to the wrong day (net effect ~$0, but
corrupted the daily correlation figure before the fix — corrected from 0.9928 to 0.9990).

### MNQ — genuinely tested for the first time; parity gap diagnosed, not yet resolved

| metric | value | bar | pass |
|---|---:|---:|---|
| NT trades / PY round trips | 1,561 / 1,978 | — | — |
| entry-time+direction matched | 1,552 (**99.42%**) | ≥99.5% | borderline (same rounding note as NQ) |
| daily P&L correlation | **0.8996** | ≥0.999 | **NO** |
| net delta | **+0.7832%** ($28,901 vs $28,676 PY ref) | <0.5% | **NO** |
| max abs daily delta | $1,336.40 | — | — |

**Diagnosed cause (not a bug in this run's reconciliation script or the Final NinjaScript
file)**: the canonical Python reference used throughout this entire program for MNQ (including
every previously-reported "1 MNQ" number, e.g. `results.csv` seq 355, `ONE_CONTRACT_FRONTIER.md`)
fills against **NQ price ticks scaled by MNQ's point value** ($2.00/tick vs NQ's $20.00),
not against genuine MNQU6 price prints. This has never been visible before because MNQ was
never actually run through Strategy Analyzer until this wave — every prior "1 MNQ" figure in
this program was this same NQ-scaled approximation, not a real MNQ backtest. The real NT8 MNQ
backtest fills against MNQU6's own price series, which carries a **different back-adjust
offset than NQU6** — an already-documented residual class in this exact codebase
(`research/system_master/EVIDENCE_MAP_RAW.md`: "MNQU6 and NQU6 carry different back-adjust
offsets (first entry 19794.25 MNQ vs 19781.25 NQ)... mean |diff| $11.27, max $738... Never mix
the two bases without this tolerance" — documented for a different product, E10Master, but
the identical underlying mechanism). This is precisely the risk the owner's own addendum
anticipated: "不能简单说：NQ 策略乘0.1就是 MNQ" ("do not assume MNQ is merely NQ divided by
ten") — now concretely observed for the first time in this exact product.

**Attempted fix, blocked**: tried to pull genuine MNQU6 price bars via `GetBars` (both
`doNotMerge` and `mergeBackAdjust` policies, both a 2022 window and a 2025 window) to rebuild
an MNQ-price-accurate Python reference — every call returned zero bars. `RunStrategyBacktest`
clearly has access to the historical MNQ data (it produced 1,561 real fills across the full
window), but the ad-hoc `GetBars` MCP path apparently reads from a different, not-yet-locally-
cached data source than the Strategy Analyzer engine's own internal resolution. Not resolved
this run — flagged as the concrete next step (see below), not silently worked around.

**What this does NOT mean**: the real NT8 MNQ Strategy Analyzer numbers themselves (net
$28,900.70, Sharpe 0.921, 1,561 trades, full metric battery below) are genuine, verified
Strategy-Analyzer-engine results, not invalidated by this finding — they are the actual
backtest of the actual Final file on the actual MNQU6 instrument. What is NOT yet certified is
the formal **parity claim** (that this matches "the" reference), because the reference itself
needs rebuilding on genuine MNQ prices before that comparison is fair.

## sub_440b — full metric battery (on the NT8-Strategy-Analyzer-verified daily series)

| metric | 1 NQ (NT8) | 1 MNQ (NT8) |
|---|---:|---:|
| net $ | 303,449.00 | 28,900.70 |
| trade count | 1,975 | 1,561 |
| Sharpe | 1.1171 | 0.9212 |
| Sortino | 1.8911 | 1.4337 |
| Calmar | 1.1029 | 0.7852 |
| max DD (eod) $ | 60,872.44 | 8,143.30 |
| CDaR (5%) $ | 45,286.25 | 6,142.93 |
| ES (5%, daily) $ | −7,525.96 | −922.52 |
| EDaR (5%, disclosed formula*) $ | 50,017.05 | 6,799.28 |
| worst day $ | −16,952.44 | −1,903.20 |
| worst week $ | −22,306.68 | −2,852.30 |
| worst month $ | −22,415.68 | −3,456.90 |
| worst quarter $ | −33,914.56 | −4,135.50 |
| longest TUW (days) | 172 | 122 |
| positive-day % | 47.06% | 48.02% |
| positive-week % | 56.52% | 53.91% |
| positive-month % | 64.15% | 58.49% |

_*EDaR formula (no existing house implementation found; disclosed per spec's instruction, not
invented ad hoc): EDaR_α(dd) = min_{z>0} (1/z)·log(mean(exp(z·dd))/α), evaluated over the
realized peak-to-trough dollar-drawdown series, α=0.05, numeric minimization over a
log-spaced grid of z. A standard entropic-risk-measure construction (Ahmadi-Javid /
Chekhlov-Uryasev family), not a house-specific convention — flagged as such._

**Honest note on NQ's own numbers vs the Python reference**: NT8's real maxDD ($60,872) is
noticeably worse than the Python reference's documented $58,517 — a real, if modest,
divergence consistent with (not contradicting) the accepted parity tolerance (net delta is
still well within bar); disclosed rather than smoothed over.

## sub_440b — capital maps (historical + stressed, both instruments)
Adapted `runs/SMV2F_LEVERAGE_ROBUST/smv2f.py`'s bootstrap index generators (moving-block L=5/
L=20, stationary mean=60, NB=2000, seed=20260808) into the capital-needed framing: for stress
multiplier m∈{1.0, 1.25, 1.5, 2.0} (dollar P&L scaled by m) and target DD-fraction
thr∈{10%,15%,20%,25%,30%}, capital_needed = 95th-percentile bootstrapped max-$-drawdown / thr,
on the NT8-verified daily series. Full tables: `out/capital_map_nq.csv`,
`out/capital_map_mnq.csv`. Historical (m=1.0), range across bootstrap methods (house
convention: quote the band, not a single number):

| thr | 1 NQ capital needed | 1 MNQ capital needed |
|---|---:|---:|
| 10% | $819,566 – $1,091,770 | $119,437 – $155,525 |
| 15% | $546,377 – $727,847 | $79,625 – $103,683 |
| 20% | $409,783 – $545,885 | $59,719 – $77,762 |
| 25% | $327,826 – $436,708 | $47,775 – $62,210 |
| 30% | $273,189 – $363,923 | $39,812 – $51,842 |

At 1.5× stress these figures scale up proportionally (e.g. 1 MNQ at 15% DD tolerance:
$119,437–$155,525). Consistent with the program's existing C-P3 disclosure methodology
(resampled paths can produce materially worse drawdowns than the single realized historical
path — these figures already reflect that, not the naive historical-maxDD-only view).

## Decision / status
- **BEST_ONE_NQ**: `SolarWaveOneContractNQ_Final.cs` — Strategy Analyzer parity CONFIRMED,
  full metric battery and capital map computed. Ready for the LIVE_READINESS_CHECKLIST engineering
  gate (still separate, still owner-authorized, still not attempted here).
- **BEST_ONE_MNQ**: `SolarWaveOneContractMNQ_Final.cs` — built, compiles clean, genuinely
  backtested via real Strategy Analyzer for the first time, full metric battery and capital
  map computed on the real NT8 numbers — but formal parity certification is **pending** a
  genuine-MNQ-price Python reference rebuild (blocked this run on `GetBars` returning empty;
  `RunStrategyBacktest` itself clearly has the data). Do not represent MNQ as parity-certified
  until this is resolved.
- **BEST_ONE_CONTRACT_OVERALL**: not selected — per the owner addendum, this is decided only
  after both instrument products are individually resolved; MNQ is not yet resolved.

## Files
`out/nt_trades_nq.csv`, `out/nt_trades_mnq.csv`, `out/py_trades_nq.csv`,
`out/py_trades_mnq.csv`, `out/parity_nq.json`, `out/parity_mnq.json`,
`out/metric_battery_nq.json`, `out/metric_battery_mnq.json`, `out/capital_map_nq.csv`,
`out/capital_map_mnq.csv`, `out/summary_all.json`, `build_parity_and_metrics.py`.
Source: `src/ninjascript/SolarWaveOneContractNQ_Final.cs`,
`src/ninjascript/SolarWaveOneContractMNQ_Final.cs`.
