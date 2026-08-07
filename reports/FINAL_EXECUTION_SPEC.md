# FINAL EXECUTION SPEC — exact executable recipe for R5-E10

_DRAFT 2026-08-07 · branch `post_campaign_audit`. This is the complete, self-contained recipe to
reproduce the champion's numbers and (eventually) implement it. It contains no discretion: every
value is frozen. Research/backtest use only — the hard safety boundary forbids any live, Sim101,
or order-placing activity._

---

## 0. WARNING — read first

**No master-strategy NinjaScript implementation of the E10 layer has been written or validated.**
The champion's published numbers ($179,361.36 / Sharpe 0.9671 TRUE_MTM) come from the **audited
Python simulator** `src/analytics/audit04_executable.py` (physical-instant timeline, open-phase
vs session-close-phase execution, slippage-cap-aware raw prices) running over the 13 member
ledgers that were **exactly reproduced fill-by-fill** by the audit
(`research/audit/R5_REPRODUCTION.md`, 13/13 EXACT). Anyone writing the master strategy must
gate-check it against these numbers before any of its output is read as evidence.

## 1. Gate check (mandatory, before anything else)

Run `SolarWaveRKReplicaV0` (vendor) **or** `SolarWaveOpenV1` (vendor-free — preferred; the vendor
assembly is not required for anything in this spec) on:
NQ 09-26 back-adjusted merge, 1-minute Last, canonical window
2023-01-01T06:00:00Z → 2025-02-02T22:59:59Z, Type 1, 90/179/5/10/true/10, NinjaTrader Brokerage
**Lifetime** commission, Standard fill, slip-0, exit-on-session-close, DefaultQuantity=1.

The five-number check must match **to the penny**:

```
Net $146,440.60 | 2,915 trades | DD −$22,066.60 | PF 1.132213 | commission $12,709.40
```

Any mismatch = engine/data drift; STOP, do not proceed (re-verified 2026-08-07 by
`runs/AUDIT_GATE_R01`/`R02` on NT8 8.1.8.1 / CrossTrade v1.13.9, engine fingerprint
sha256:b4255f1b0dd7fba1).

## 2. The 13 virtual members

Strategy class: `SolarWaveOpenV3` (`src/ninjascript/SolarWaveOpenV3.cs`, sha256
`60d584c5c820d8fe131eb889a37d1e07d6e746ed5f3919b8d47d0ba7d74df167`). HOT-RELOAD caution: if the
class is recompiled/modified, rename it per iteration — NT8 may resolve a stale type.

Data series (shared by all members): **NQ 09-26 back-adjusted merge, 3-minute bars, Last**,
2022-01-01T06:00:00Z → 2026-07-31T21:59:59Z (per the "To = one second before next 18:00 ET open"
convention). The NT8 historical cache for this series is bit-stable (540,233 bars) between the
campaign and the audit.

Effective parameters, identical for every member (all must be serialized in any future exporter —
the V3 ledger header omits StartUp, a known deficiency):

```
StartUp         = false        <- CRITICAL. The published README recipe said true;
                                  true does NOT reproduce any committed ledger.
TrendMultiplier = 90           StopMultiplier = 179     (both inert under ThresholdMode 1)
SlowdownScan    = 5            WeakWeakSplit  = 10      (inert for Type-1)
AnchorMode      = 0            (running CLOSE extreme)
ThresholdMode   = 1            (S = VolMult * sigma, frozen at trend birth)
VolPeriod       = 460          SMinTicks = 40           SMaxTicks = 1200
ExitMultiplier  = 0            EntrySignalType = 1      (Type-1 only)
EnableLong      = true         EnableShort = true       UseTimeFilter = false
Slippage        = 1 (tick/execution)                    Commission: Lifetime template
Exit-on-session-close = true (30 s)                     DefaultQuantity = 1
```

Member sweep: **VolMult = 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30** (13 members).
Preregistered per-cell reproduction expectations (NetProfit to the cent): vm6 $166,144.88 …
vm30 $249,256.52 — full diff table `research/audit/v3_reproduction_diff.csv`.

The members are **virtual**: they place no orders. Only their per-bar positions
(∈ {−1, 0, +1}) feed the target layer.

## 3. The E10 target layer

1. At each 3-minute bar close, compute `mean = (1/13) * Σ member_position_i`.
2. **Target = round(10 × mean) MNQ contracts**, bounded to [−10, +10]
   (10 MNQ = 1 NQ-equivalent; "round" = banker's-agnostic nearest-integer — the audited
   sensitivity shows round and floor(-toward-zero) both pass gates; ceil fails; the designated
   rule is **round**, `research/audit/e10_sensitivity.csv`).
3. Submit only the **net change** (target − current position) as a market order filled at the
   **next bar open**.
4. **Session-close flatten**: at each session close (18:00 → 17:00 ET sessions), flatten to zero
   via the session-close-phase fill (see §5). The strategy is flat across every session boundary
   and every roll.

## 4. Cost stack (frozen, verified)

| component | value | provenance |
|---|---|---|
| MNQ commission | **$0.65/side ($1.30/RT)** per contract | verified empirically, constant across 704 fills, `runs/AUDIT04_MNQ_PROBE` |
| Slippage | **1 tick per execution per contract** on net target changes (MNQ tick = 0.25 pt = $0.50) | campaign convention; stress at 2 ticks retains 87.4% at member level |
| Realized totals 2022-01 → 2026-07 | commission $33,881.90; slippage $26,063.00; 52,126 contracts | `research/audit/executable_ensemble_metrics.csv` |

Monitoring hook (binding): **re-verify the MNQ commission whenever the broker plan changes** —
a ≥$0.10/side increase fails the champion's preregistered gate (`SECOND_RED_TEAM.md` §4).

## 5. Fill semantics (as validated by the audit)

- Entries/changes fill at **next bar open ± 1 tick** of modeled slippage, with the slippage
  **capped by the bar's range** (NT8 Standard behaviour; the cap is why slip-N extrapolation is
  a floor, not a line).
- Session-close exits fill at the session's last-bar close; **zero fill-resolution differences
  occur on session-close fills**.
- **Ledger timestamps are the fill-bar's close time**, not the open — any reconciliation code
  must join on that convention (validated against the exported engine bar series
  `runs/AUDIT03_BARS/nq_3m_2022_2026.csv`, 540,232 bars + 1 known missing boundary bar).
- Standard vs High fill resolution: sequences identical, price differences in ≤2.1% of fills
  (almost all exactly 1 tick, both signs, net effect ≤1.1%); Standard is fair and slightly
  conservative. Playback adds nil information for market-only orders (explicit non-run).
  `research/audit/FILL_AND_TAIL_AUDIT.md`.

## 6. NT8 / CrossTrade reproduction steps

1. **Gate check** (§1). STOP on any mismatch.
2. Confirm commission templates installed: "NinjaTrader Brokerage Free/Lifetime/Monthly"
   (there is no plain "NinjaTrader Brokerage"); use **Lifetime**.
3. Run the 13-cell V3 sweep per §2 (isolated Backtest account, Standard fill, qty 1, slip-1),
   window 2022-01-01T06:00:00Z → 2026-07-31T21:59:59Z. The audit executed this via CrossTrade
   `RunStrategyBacktest` sweeps; specs `runs/AUDIT02_V3_SWEEP_B/spec.yaml` (preregistered at
   `124af95`) are the template.
4. Diff every cell fill-by-fill against `research/05_open_axes/h006/` ledgers (or against
   `research/audit/v3_reproduction_diff.csv` expectations). Required verdict: 13/13 EXACT —
   every fill timestamp, action, price, commission, quantity.
5. Ingest ledgers and run the executable simulation:
   `src/analytics/audit04_run.py` / `audit04_executable.py`. Required outputs: E10 net
   $179,361.36, Sharpe 0.9671 (session basis), daily corr with E0 0.9985, matching
   `research/audit/executable_ensemble_metrics.csv` row `R5_adaptive_13,E10`.
6. Any future master-strategy NinjaScript must reproduce the simulator's daily vector
   (`research/audit/e_variant_daily_vectors.csv`, column `E10_round_session`) before its output
   is used for anything. Its run requires a pre-committed `runs/<run_id>/spec.yaml` with
   `source_commit`, `strategy_source_sha256`, `engine_version`, `parameter_hash`, inline
   pass/reject criteria, and `counts_as_trial` declared up front (registry rule (e),
   `research/audit/REGISTRY_GAP_ASSESSMENT.md`).

## 7. Session/margin operational note (informational, not part of the champion)

The champion holds to the 17:00 ET session close, which is 15 minutes past the verified 16:45 ET
NinjaTrader day-margin cutoff; under day-margin sizing every 16:45–17:00 position requires full
initial margin (NQ ≈ $43.4k, MNQ ≈ $4.3k as listed 2026-08-07). A DAY_MARGIN_FLAT variant
(16:40 ET flatten) is a separate preregistered measurement (`runs/DM01_DAYMARGIN_SWEEP/spec.yaml`,
seq 272–284, in flight at draft time); it may NOT replace the champion unless it dominates on
both Sharpe and right-tail retention. Facts and re-verification list:
`research/operational/day_margin_variant/MARGIN_RULES.md`.

## 8. What may not be changed

Everything in §§2–5 is frozen. Changing any value (grid, clamp, VolPeriod, rounding rule, cap,
costs, session handling) creates a NEW configuration requiring a pre-committed spec, a sequence
number, and fresh gates — it is not the champion. Solar parameter optimization is CLOSED.
