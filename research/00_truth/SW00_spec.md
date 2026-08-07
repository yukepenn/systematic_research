# SW00_BASELINE_PARITY_COST — Preregistered Specification

_Written and committed BEFORE any SW00 result is read. 2026-08-06._

## Hypothesis (H-001, falsifiable)
The canonical Type-1 Solar Wave baseline retains positive after-cost expectancy under realistic execution friction, and the CrossTrade→NT8 Strategy Analyzer pipeline is deterministic.

## Economic mechanism
NQ execution friction is additive per execution: 1 tick = $5, two market executions per round trip → ~$10/RT per tick of slippage, on top of $4.36/RT Lifetime commission. The baseline's edge (avg trade $50.24 including commission at slip 0) must clear realistic friction with margin. All entries and exits are market orders (bar-close signals), so slippage applies to every execution.

## Degrees of freedom added: 0
No logic, parameter, timeframe, or window changes. Slippage/fill settings are cost-model inputs; every run is logged in the registry.

## Fixed configuration (all runs unless stated)
Strategy `SolarWaveRKReplicaV0` (mtime 2026-08-06T01:42:49Z, hash recorded in runs); Type 1; TrendMultiplier 90, StopMultiplier 179, SlowdownScan 5, WeakWeakSplit 10, PullbackEarly true, PullbackSplit 10, EntrySignalType 1, EnableLong/Short true, UseTimeFilter false (StartTime 93000, EndTime 160000 inert); 1-Minute Last bars; NQ 09-26 → NQU6 back-adjusted; instrument-default trading hours; Lifetime commission; Standard fill; entries/direction 1; exit-on-session-close true (30 s); GTC; DefaultQuantity 1; window 2023-01-01T06:00:00Z → 2025-02-02T22:59:59Z; isolated Backtest account.

## Run matrix (13 runs)
| Run | Variation | Purpose |
|---|---|---|
| R01–R05 | none (slip 0) | Determinism ×5 + baseline artifacts + timing distribution |
| R06/R07/R08 | slippage 1/2/3 ticks per execution | Cost ladder |
| R09 | fill=High, window 2023-01-01→2023-01-28, timeout 180 s | Fill-resolution availability probe (quarantined: subwindow results not used for selection) |
| R10 | optimization sweep StartTime∈{93000,93001} (inert: UseTimeFilter=false), DefaultOptimizer, MaxNetProfit | Optimization-machinery test with ZERO information content — both combos are economically identical to canonical |
| R11 | window 2023-01-01→2023-04-01 (slip 0) | Engine-time vs bar-count scaling (quarantined subwindow) |
| R12+R13 | two canonical jobs submitted back-to-back without waiting | Parallel-submission safety: both must hash-match R01 |

## Benchmark measurements (per run where available)
Submission latency (client ms), queue latency (submit→started_at), engine duration (started→finished), payload bytes, local parse/ingest ms, ledger/metrics/equity hashes.

## Preregistered acceptance gates
1. **Determinism (integrity):** R01–R05 trade-ledger hashes and metric hashes identical, and identical to the parity run B ledger (recomputed with the same canonicalization). R12/R13 also identical, else parallel submission is banned and noted.
2. **Effective parameters:** echoed exactly in every run; else FAIL (parameter drift).
3. **Cost ladder:** slip1 net profit > 0 AND slip1 average trade > 0 (hard gate). Soft target: slip1 avg trade ≥ 2.5 × slip1 RT cost ($14.36) ≈ $35.90. slip2 net > 0 = "not structurally destroyed". slip3 reported descriptively.
4. **Fill realism:** slippage must appear as adverse per-execution price adjustment vs R01 fills (verify on matched trades); TotalSlippage accounting must reconcile.
5. **No impossible behavior:** exit ≥ entry time for every trade; no same-bar entry+exit at identical timestamp with nonzero P&L inconsistent with bar pricing; per-trade P&L ≡ direction × (exit−entry) × $20 − commission (±$0.005); session-close exits at 17:00:00 ET only; no trade spans a session boundary (flat-at-close structural check → no roll-gap exposure).
6. **Fill-resolution probe:** report availability/duration/result only; no gate (data may be absent).

## Rejection / phase-stop criteria
- Any unexplained nondeterminism → STOP, diagnose before any further research.
- slip1 average trade ≤ 0 → Solar promotion halts; campaign pivots to implementation repair (thesis Phase-0 stop rule).
- Effective-parameter drift or per-trade accounting identity violations → STOP.

## Outputs
Per run: `runs/SW00_Rxx/` = spec.yaml, raw_result.json (full payload for R01, R06–R11; hash-referenced dedup for identical determinism payloads R02–R05, R12, R13), metrics.json, trades.parquet, daily_equity.parquet, hashes.json, report.md, decision.json. Experiment-level: `research/00_truth/SW00_report.md` (cost attribution, determinism, benchmark, audits, temporal/side/hour decomposition, right-tail metrics), updates to registry/state/reports.

## Explicit deviations from the reference protocol (justified)
- 5 determinism reruns, not 10: bit-identical hashes across 5 independent reruns (plus parity run B = 6 observations) make runs 7–10 information-free; budget goes to the cost ladder instead. If ANY hash differs, extend to 10+ and diagnose.
- Playback/reload audit deferred: requires connection changes prohibited by the hard safety boundary (documented in CAMPAIGN_STATE; manual user action item).
- 3-minute timing benchmark replaced by window-length scaling of the canonical config: running the Phase-5 3m anchor now would contaminate its preregistration.
