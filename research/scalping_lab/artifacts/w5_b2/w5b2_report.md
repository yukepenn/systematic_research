# W5-B2 — Intraday-momentum correlation pre-gate (Program B)

Date: 2026-08-07 (analysis run). Spec: `research/scalping_lab/specs/W5_programs_wave.md` §B2 (frozen,
Amendment 6). Seed 20260808. Code: `research/scalping_lab/src/python/w5_b2_pregate.py`.
Scope discipline: **correlation structure only — no new alpha claims.** H-A1's kill of the
standalone Gao-style intraday-momentum effect stands and is not re-litigated here.

## Verdict (frozen gate)

| Deliverable | rho (Pearson) | N |
|---|---|---|
| **rho_full** (daily) | **+0.1344** | 1,095 days |
| **rho_losing** (Solar net_v1 < 0 days) | **−0.0649** | 641 days |
| **rho_monthly** (calendar-month sums) | **+0.3354** | 53 months |

**Frozen rule** (§B2): rho ≥ 0.5 → family rejected as diversifier; rho < 0.3 → build spec permitted
next wave. Gate rhos (full + losing-day, per the frozen deliverable list): **both < 0.3** and no
measured rho reaches 0.5.

**Gate outcome: BUILD SPEC PERMITTED next wave** — with one recorded caution: the
monthly-aggregated rho (+0.335) sits in the indeterminate band [0.3, 0.5). Daily-level
decorrelation partially attenuates under monthly aggregation, so any next-wave build spec must
treat the diversification benefit as a daily-horizon property and re-examine monthly co-movement
before portfolio claims. On Solar's losing days specifically, momentum P&L is uncorrelated to
slightly negative (−0.065) — the direction a diversifier needs.

## Definitions used (frozen / stated)

- **Data**: `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` (3-min bars, close-stamped, exchange ET).
  **Contamination rule enforced at load**: of 540,232 rows, 20,399 rows ≥ 2026-06-01 dropped
  unread (sealed holdout); kept range 2022-01-02 18:03 → 2026-05-31 23:57; last traded RTH day
  2026-05-29.
- **Reference prices** ("first bar with time ≥ T, its close" — same convention frozen in §B1):
  p0930 = first bar in [09:30, 09:45]; p1530 = first bar in [15:30, 15:45]; p1645 = first bar in
  [16:45, 17:00].
- **Gao-style daily P&L**: signal = sign(p1530 − p0930) (rest-of-day return 09:30→15:30);
  position = signal, 1 NQ, held p1530 → p1645; P&L = signal × (p1645 − p1530) × $20 − C1;
  friction C1 = 2.872 ticks = $14.36 per trade (one trade/day). Zero-signal days (1 occurrence)
  take no trade and no friction.
- **Solar ledger**: `runs/E10MASTER_V2/out/daily_v1_v2.csv`, column **net_v1 — the v1 frozen
  research champion** (per E10MASTER_V2/results.md, v1 is the analytics-continuity ledger; v2 is
  the ops ledger). 1,183 rows, 1,139 kept ≤ 2026-05-31. Overlap with momentum days: 1,095
  sessions (2022-01-03 → 2026-05-29).

## Supplementary robustness (context only, not gate inputs)

- rho_full 95% CI (circular block bootstrap, block = 10 days, 2,000 paths, seed 20260808):
  **[+0.0450, +0.2188]** — the CI excludes 0 (mild positive daily co-movement is real) and
  excludes 0.3 (comfortably inside the permit region).
- Spearman (full, vs net_v1): +0.0850 — the Pearson value is not driven by a few outlier days.
- Versus the v2 ops ledger: rho_full +0.1292; losing-day (net_v2 < 0, N = 637) −0.0616.
  Gate conclusion is ledger-invariant.

## Momentum P&L simple stats (CONTEXT ONLY — standalone claim already killed by H-A1)

Total +$2,835.16 over 1,095 days (1,094 traded); mean +$2.59/day (+0.518 ticks/day);
std $1,343.74/day; hit rate 48.35%; annualized Sharpe 0.031.

| Year | Days | Sum ($) | Mean ($/day) |
|---|---|---|---|
| 2022 | 250 | +47,705.00 | +190.82 |
| 2023 | 247 | −3,651.92 | −14.79 |
| 2024 | 249 | +9,003.72 | +36.16 |
| 2025 | 247 | −32,746.92 | −132.58 |
| 2026 (→05-29) | 102 | −17,474.72 | −171.32 |

Consistent with H-A1: the aggregate is one strong year (2022) followed by decay; nothing here
revises the standalone kill, and none of these numbers are inputs to the gate.

## Data hygiene

Calendar dates skipped for missing reference bars: 237 without a 09:30 bar (227 Sundays +
10 full-closure holidays: Christmas/New Year's/Good Friday observances) and 42 without a 15:30
bar (CME holiday early sessions closing 13:00 ET, plus day-after-Thanksgiving 13:15 closes, plus
2023-04-05 — the known bar-stamp-gap day already documented in `runs/E10MASTER_V2/results.md`).
0 days lacked a 16:45 bar given a 15:30 bar. The 44 Solar ledger days absent from the overlap are
exactly these no-15:30 sessions (+ edge days), where the 15:30→16:45 trade cannot exist.
Independent recomputation of all three rhos from the saved joined CSV reproduced the values to
full precision; a hand spot-check of 2024-03-14 (short signal, P&L −$1,594.36) reconciled exactly.

## Artifacts (all reported numbers appear here)

- `w5b2_stdout.txt` — full run log (every number above)
- `w5b2_stats.json` — machine-readable deliverables + supplementary + context stats
- `w5b2_momo_daily.csv` — per-day reference prices, signal, gross, net momentum P&L
- `w5b2_joined_daily.csv` — joined daily table (momo_pnl_usd, net_v1, net_v2, signal)
- `w5b2_monthly.csv` — monthly sums used for rho_monthly

Registry: this readout maps to a W5 registry row (S14–S21 block); registration handled at the
wave level, not by this section.
