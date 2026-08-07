# R5 reproduction certificate — POST_CAMPAIGN_AUDIT_01, AUDIT-02

_2026-08-07 · independent re-execution through CrossTrade v1.13.9 / NT8 8.1.8.1
(engine fingerprint sha256:b4255f1b0dd7fba1) on branch `post_campaign_audit`._

## Verdict

**R5 member ledgers: `EXACT_REPRODUCTION` (13/13 cells fill-by-fill identical).**
**R5 recipe as documented: `RECONCILED_WITH_DOCUMENTED_DIFFERENCE` — the README /
`src/ninjascript/README.md` reproduction recipe states `StartUp=true`; the committed
campaign ledgers were produced with `StartUp=false` (the V3 default). Anyone following
the published recipe verbatim gets systematically different numbers in every cell.**

## Chain of evidence

1. **Determinism gates** (`runs/AUDIT_GATE_R01`, `runs/AUDIT_GATE_R02`, preregistered
   at `b811a21`): both `SolarWaveRKReplicaV0` (vendor) and `SolarWaveOpenV1`
   (vendor-free) reproduce the frozen canonical baseline **exactly** on today's data
   cache — Net $146,440.60 | 2,915 trades | DD −$22,066.60 | PF 1.132213 |
   commission $12,709.40. Engine, data (1-minute, canonical window), and commission
   template are unchanged since the campaign.

2. **A-arm** (`runs/AUDIT02_V3_SWEEP`, StartUp=true per the README recipe):
   **FAILED reproduction in all 13 cells** — 8 cells differ in fill count (2–8 fills),
   5 cells match counts but differ in exactly 4 early fills. Fill-level diff shows the
   committed vm30 ledger opens `Long Buy 2022-01-02T20:03 @19781.25` (a StartUp=false
   first-flip signature) while the StartUp=true rerun opens
   `Short SellShort 2022-01-03T09:03 @19751.25`; both paths converge at the first
   common flip (2022-01-04T10:06). The two divergent early trades explain the vm30
   net gap to the dollar (committed −$449 vs rerun −$2,219 ≈ Δ$1,770.52 observed).

3. **B-arm** (`runs/AUDIT02_V3_SWEEP_B`, StartUp=false, preregistered at `124af95`):
   **13/13 cells EXACT** — every fill timestamp, order action, price, commission,
   quantity, and even the wave/signal attribution metadata identical to
   `research/05_open_axes/h006/`. Per-cell NetProfit matches the preregistered
   expectations to the cent (vm6 $166,144.88 … vm30 $249,256.52).
   Diff table: `research/audit/v3_reproduction_diff.csv`.

## What this establishes

- R5's 13 member trade paths are **deterministically reproducible from a clone**
  (given NT8 + the committed `SolarWaveOpenV3.cs` + the NQ 09-26 back-adjusted series)
  once `StartUp=false` is specified.
- The NT8 historical data cache for NQ 09-26 3-minute, 2022-01→2026-07-31 (540,233
  bars) is bit-stable between the campaign runs and this audit.
- The `MaximumBarsLookBack=256` vs `VolPeriod=460` sigma-recompute hazard flagged in
  the code review does NOT break determinism on this engine build (exact fills
  reproduce, including every adaptive-threshold flip).

## Corrections required (carried to AUDIT-06)

1. `src/ninjascript/README.md` R5 recipe: `StartUp=true` → **`StartUp=false`**.
2. `reports/final_system_design.md` §7 must state StartUp explicitly.
3. The V3 ledger header format omits StartUp — noted as an exporter deficiency
   (any future exporter must serialize every effective parameter; the audit-era
   spec.yaml requirement already enforces this at the registry level).

## Not covered here

The V4 arm and the V3/V4 equivalence question — including the newly discovered
**StartUp confound in the published comparison** — are in
`research/audit/V3_V4_VERDICT.md`.
