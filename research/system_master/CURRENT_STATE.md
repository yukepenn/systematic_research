# SYSTEM_MASTER — Current State

_Updated: 2026-08-08 (program opened)._

## Phase

**P0 — bootstrap.** Scaffold + conventions frozen (this commit). Next: canonical Python
substrate (SM01), then parallel tracks 1–8.

## Champion / challenger board

| class | holder | status |
|---|---|---|
| SOLAR_REFERENCE | executable R5-E10 (v1 session-close; v2 16:44 flatten = ops default) | FROZEN input |
| SOLAR_LOW_DD / MAX_SHARPE / MAX_GEOMETRIC | — | open (Tracks 1–3) |
| BMOM_RECENT_REGIME | frozen W8-1 B-MOM rule | challenger, no retuning |
| BEST_COMPLEMENTARY_ENGINE | — | open (Track 6; B1/B-FADE parked candidates) |
| BEST_TWO_ENGINE_PORTFOLIO … | — | open (Track 7) |
| BEST_OPERATIONAL_MASTER | — | open (Track 8) |

## Track status

| track | status | next action |
|---|---|---|
| 0 substrate | **in progress** | SM01: Python member simulator + parity gate vs h006 ledgers; trade-path anatomy tables |
| 1 drawdown autopsy | pending SM01 | episode/DD decomposition 2022–2026 dev |
| 2 stop/exit frontier | pending SM01 | spec SM02 (catastrophe/time/progress/MAE stops + re-entry) — SW02 catastrophe stop was preregistered in the old campaign and NEVER run |
| 3 ensemble confidence | pending SM01 | vote features; exposure-shape hypothesis (E10 target map is already linear in net vote — question is the SHAPE) |
| 4 indicator screen | can start | deep-research passes + conditional-information screen protocol |
| 5 B-MOM portfolio | can start now (ledgers exist) | Solar/B-MOM/50-50 matched-risk comparison on dev |
| 6 engine factory | after 5 | new mechanism specs, minute substrate 2006–2026 |
| 7 portfolio synthesis | after 5/6 | P0–P4 architectures |
| 8 NT8 master | last | multi-engine master spec + parity |

## Data/facts loaded (see EVIDENCE_MAP_RAW.md for full detail)

- Substrates: `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` (540,232 3-min bars, aligns 1:1 with
  `runs/E10MASTER_V2/out/e10m_v2_bars.csv` member positions); `runs/B01A_BARS_1M/…` 1-min
  2022–2026; `research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet` (6.47M
  1-min bars, actual start 2006-01-05). **Do not mix back-adjustment bases across sources
  within one analysis** (overlap alignment to be verified in SM01).
- Member NQ ledgers: `research/05_open_axes/h006/h006__tf3_…_vm{6..30}_….csv` (13 files) and
  `runs/AUDIT02_V3_SWEEP_B/ledgers/b2v3__…` (audited reproduction, 34,148 episodes).
- Champion daily: `runs/E10MASTER_V2/out/daily_v1_v2.csv` (net_v1 + net_v2, sessions
  2022-01-03→2026-07-31). B-MOM/B1/B-FADE ledgers under `research/scalping_lab/artifacts/`.
- σ definition (V3/E10 exact): trailing mean |ΔClose| over 460 bars, warmup<30 → 179t
  fallback, S=clamp(k·σ, 40t, 1200t) sampled at trend birth; V/S = 90/179.

## Standing constraints

- ≥2026-08-01 virgin (LOCKED_FORWARD). Dev ends 2026-05-31; June–July 2026 = joint-read
  holdout (CONVENTIONS §1, with the Solar increment-only caveat).
- Killed-axis filter mandatory before each spec freeze (EVIDENCE_MAP_RAW killed lists +
  both registries).
- NT8 engine available via CrossTrade MCP for final parity runs only; all research in Python.

## Log

- 2026-08-08: Program opened. Evidence map built (12 readers). Scaffold + CONVENTIONS
  frozen and committed before any new result read. Registry sequence resumes at 291.
