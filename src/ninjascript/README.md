# NinjaScript strategy source

_Added 2026-08-07. These files previously existed **only** in
`Documents\NinjaTrader 8\bin\Custom\Strategies\` and were not in the repository, which meant no
campaign result — including R5 — was reproducible from a clone. That gap is closed here._

Drop these into `Documents\NinjaTrader 8\bin\Custom\Strategies\` and compile (F5).

## Provenance

**None of this is vendor source code.** The `SolarWaveOpen*` files are an independent
reimplementation of behaviour recovered by observing the RenkoKings Solar Wave RK indicator's own
**published output** — the series it plots and the values it exposes. No decryption, unpacking,
patching, memory dumping or protection bypass was performed at any point, the vendor assembly was
never modified, and the recovered logic is a behavioural reimplementation rather than a copy of the
vendor's implementation. Derivation and proof of equivalence:
[`research/03_reverse_engineering/`](../../research/03_reverse_engineering/) and
[`research/00_truth/OPEN_MODEL_VALIDATION.md`](../../research/00_truth/OPEN_MODEL_VALIDATION.md).

## Files

| file | vendor DLL required? | role |
|---|---|---|
| `SolarWaveOpenV1.cs` | **no** | first open reconstruction; reproduces the frozen baseline exactly (`runs/RE01_open_parity/`) |
| `SolarWaveOpenV1X.cs` | **no** | V1 + fill-level execution ledger |
| `SolarWaveOpenX2.cs` | **no** | ledger with parameter-named output, one CSV per sweep cell |
| **`SolarWaveOpenV3.cs`** | **no** | **produced R5.** Adds AnchorMode / ThresholdMode / ExitMultiplier |
| `SolarWaveOpenV4.cs` | **no** | V3 + ThresholdMode 2 (price-proportional, H-014). **Not equivalent to V3 at ThresholdMode 1** — see below |
| `SolarWaveStopExecV1.cs` | **no** | H-011, three execution arms |
| `SolarWaveSleeveV1.cs` | **no** | signal-mask sleeves (C2/C4) and wave conditioning |
| `SolarWaveRKReplicaV0.cs` | yes | the **frozen baseline** wrapper around the licensed indicator |
| `SolarWaveRKLedgerV1/V2.cs` | yes | OHLC + indicator-series exporters used to recover the model |
| `SolarWaveRK1.cs` | yes | pre-campaign Strategy Builder file, kept for provenance |

The seven `no` files are the deliverable: they need no RenkoKings assembly at all. The four `yes`
files exist only to establish parity with, and recover the behaviour of, the licensed indicator —
they require a valid RenkoKings licence and are useless without one.

## Reproducing R5

**Use `SolarWaveOpenV3`, not V4.** V4's `ResolveS()` snaps `S` to the tick grid and V3 does not, so
at `ThresholdMode = 1` they are different strategies — verified fill-by-fill, zero of 13 cells
match. Every published R5 figure was measured on V3. The two are statistically indistinguishable at
the ensemble level (ΔSharpe +0.029, P(Δ ≤ 0) = 0.247) but individual cells move by up to 44 %.
Full analysis: [`research/10_v3v4_equivalence/V3_V4_EQUIVALENCE.md`](../../research/10_v3v4_equivalence/V3_V4_EQUIVALENCE.md).

```
Strategy    : SolarWaveOpenV3
Instrument  : NQ 09-26 back-adjusted, 3-minute, Last
ThresholdMode = 1 | VolPeriod = 460 | SMinTicks = 40 | SMaxTicks = 1200
AnchorMode = 0 | ExitMultiplier = 0 | EntrySignalType = 1 | StartUp = true
TrendMultiplier = 90 | StopMultiplier = 179   (both inert at ThresholdMode 1)
SlowdownScan = 5 | WeakWeakSplit = 10 | UseTimeFilter = false
Commission  : NinjaTrader Brokerage Lifetime      Slippage: 1 tick     Fill: Standard
Exit on session close = true

VolMult     : sweep 6, 8, 10, ... 30  -> 13 cells, held at EQUAL RISK (1/N)
              DO NOT select a single VolMult. PBO for that choice is 0.898.
```

The 13 cells are one optimization job. **The ensemble is not** — NT8 has no
portfolio-of-parameterisations backtest, so the 1/N aggregation happens in
[`src/analytics/ensembles.py`](../analytics/ensembles.py). No Strategy Analyzer window anywhere
will show R5's headline numbers.

## Gate check before trusting any run

Every strategy here was verified to reproduce the frozen canonical baseline **to the penny** before
its results were read:

```
SolarWaveRKReplicaV0, Type 1, 90/179/5/10/true/10, 1-minute Last, NQU6,
NinjaTrader Brokerage Lifetime, 2023-01-01T06:00:00Z -> 2025-02-02T22:59:59Z
=> Net $146,440.60 | 2,915 trades | DD -$22,066.60 | PF 1.132213 | commission $12,709.40
```

Run that first. If it does not match exactly, stop — something in the data or settings differs and
no downstream number can be trusted.

## Safety

Research and backtesting only. These strategies must never be enabled, deployed, or connected to
Sim101 or any brokerage account. Backtests run on NT8's isolated `Backtest` account.
