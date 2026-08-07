# E10MASTER_V1 — SolarWaveE10Master_v1 engineering validation

_2026-08-07 · run `runs/E10MASTER_V1/` (spec committed before build/run) · engine NT8 8.1.8.1 /
CrossTrade v1.13.9 / engine_fingerprint sha256:b4255f1b0dd7fba1 · backtest job `d1649fa25ab0453e`
(completed 2026-08-07T19:32:29Z, 34.4 s) · Backtest account only, never enabled/deployed._

## What was built

The R5-E10 executable champion as **one** NinjaScript strategy:
`src/ninjascript/SolarWaveE10Master_v1.cs` — 13 virtual `SolarWaveOpenV3` member state machines
(VolMult 6..30 step 2, ThresholdMode 1, VolPeriod 460, clamp 40–1200 ticks, AnchorMode 0,
EntrySignalType 1, StartUp=false, SM 179 retained as the <30-sample sigma-warmup fallback) updated
per primary NQ 3-min bar close, shared sigma460, physical target = round(10 × mean virtual
position) clamped ±10 MNQ, executed as net changes on an added MNQ 09-26 3-min series
(managed `barsInProgressIndex=1` orders), `IsExitOnSessionCloseStrategy=true/30 s`.

Virtual fill mechanics were fixed from ledger evidence before coding (not tuned): decision at bar
N close → fill at bar N+1 open; orders pending at a session's last bar close are dropped (zero
first-bar-of-session fills in 16,984 AUDIT02_V3_SWEEP_B member executions); members zeroed at the
session's last bar (engine session-close exits execute at the close). The vol/anchor/signal code is
transplanted verbatim from V3 (same arithmetic order, same `MaximumBarsLookBack`) for bit-identical
doubles; target rounding `(sum/13.0)*10.0` + `Math.Round` (to-even) is IEEE-identical to numpy's
`(mean*10).round()`.

Backtest config: primary NQ 09-26 back-adjusted merge, 3-min Last, 2022-01-01T06:00:00Z →
2026-07-31T21:59:59Z, commission template "NinjaTrader Brokerage Lifetime", slippage 1 tick,
Standard fill. MNQ 09-26 resolved (MNQU6); MNQ fills present from 2022-01-02 → full data coverage.

## Verdicts per preregistered gate (spec `runs/E10MASTER_V1/spec.yaml`)

| gate | requirement | observed | verdict |
|---|---|---|---|
| **V1 target parity** | per-bar target sequence == Python simulator (audit04_executable on the 13 AUDIT02_V3_SWEEP_B ledgers) | **540,232 bars, 0 target diffs, 0 member-position diffs (100.000%)** | **EXACT** |
| **V2 engine vs audit** | corr ≥ 0.995 AND net within ±5% of `e_variant_daily_vectors.csv` E10_round_session | **corr 0.999921; net $181,079.10 vs $179,361.36 = +0.96%** | **CLOSE_WITHIN_TOLERANCE** (PASS) |
| **V3 costs** | MNQ commission $0.65/side observed; 1-tick slippage | **all 39,903 executions exactly $0.65/side/contract; total $33,881.90 = 52,126 × $0.65** | **EXACT** |

**Overall: PASS — the champion is executable as a single NinjaScript strategy.**

## Headline engine numbers (session basis, from engine-written fill ledger)

- Net (incl. commission, slippage embedded in fills): **$181,079.10** over **1,184 sessions**
- Daily Sharpe: **0.9762** (audit reference 0.9671)
- Max drawdown (session-close equity): **−$40,866.20** (reference −$41,252.20 bar-level)
- Worst day: −$12,667.20 (reference −$12,723.70)
- 39,903 executions, **52,126 contracts traded — identical to the simulator's E10 contract count**
  (commission $33,881.90 and 1-tick slippage $26,063.00 reproduce the audit cost stack exactly)
- 1,058 engine session-close exits; 848 managed-reversal close legs; flat at every session close
  (verified from the ledger — zero non-flat sessions)
- Physical position tracked the prior-bar target with **zero** non-boundary mismatches

## Every deviation found (itemized)

1. **V1: none.** Target and all 13 member positions match the simulator on every one of 540,232
   exported bar closes (`e10master_target_parity_diffs.csv` is empty).
2. **V2 daily differences are MNQ-vs-NQ print basis only** (the tolerance the spec names): mean
   |daily diff| $11.27; max $738.00 (2023-01-12); only 1 of 1,184 sessions differs by >|$500|.
   Net +$1,717.74 in the engine's favor. MNQU6 and NQU6 carry different back-adjust offsets
   (e.g., first entry raw 19794.25 MNQ vs 19781.25 NQ), so identical decisions print different
   dollars. Full vector: `e10master_daily_parity.csv`.
3. **Engineering quirks (no gate impact):**
   - Full-run `GetMcpJob` payload exceeds the MCP transport (repeatable "session expired");
     `ListMcpJobs` confirms job completion. Raw evidence = the strategy's own engine-written
     exports `runs/E10MASTER_V1/out/e10m_v1_{bars,fills}.csv` (smoke-run payload at 2 months
     retrieved fine and cross-checked).
   - The final 17:00 boundary bar (2026-07-31) is absent from the per-bar export — OnBarClose
     never fires at data end; same known quirk as the AUDIT03 bar exporter (whose `load_bars()`
     boundary patch the validator reuses). The final session-close exit IS in the fills ledger.
   - `WriteNinjaScriptFile` returned `compile_engine=file_only`; the backtest ran the type from
     the sandbox-compiled assembly (`CompileNinjaScript in_memory=false`, clean, 0 warnings).
     The `.cs` is in `Documents\NinjaTrader 8\bin\Custom\Strategies\`; press F5 (or restart NT8)
     before the strategy appears through NT8's own compiled path.

## What a _v2 would need

Nothing — all three gates pass with V1/V3 exact. No open defects.

## Artifacts

- Strategy source (committed-ready): `src/ninjascript/SolarWaveE10Master_v1.cs`
- Run dir: `runs/E10MASTER_V1/` (spec.yaml, validate.py, out/e10m_v1_bars.csv 36.6 MB,
  out/e10m_v1_fills.csv 2.9 MB)
- Parity CSVs: `research/04_complementary_family/e10master_target_parity_diffs.csv` (empty = exact),
  `research/04_complementary_family/e10master_daily_parity.csv` (1,184 sessions, eng/ref/diff)

## Safety

Backtest-only throughout: isolated Backtest account, strategy never enabled or deployed, no
Sim101/live contact, no vendor assembly involvement.
