# W8-2 — B-FADE: release-day fade readout

Frozen spec: `research/scalping_lab/specs/W8_programs_final.md` §W8-2 (committed cf7041f).
Code: `research/scalping_lab/src/python/w8_bfade.py`. Every number below appears in
`stdout.txt` / the CSVs in this directory. Seed 20260808, 1000 day-clustered bootstrap
reps, C1 = 2.872t RT, dev window 2022-01 → 2026-05-31 only.

## HONESTY CLAUSE (binding)

The fade direction was **observed on this same dev sample** (W7-3 continuation
net −53.0t@15min ⇒ implied fade ≈ +47t@15min). **Every performance table in this
report is IN-SAMPLE CHARACTERIZATION, NOT CONFIRMATION.** No promotion from this
wave. The frozen confirmation plan is pre-2022 (2005–2021) unseen minute data;
sealed holdout only at Tier-3 if pre-2022 passes.

## Rule (frozen)

On 08:30-release days (NFP/CPI from the calendar), at the 09:30 3-min bar close
enter **against** sign(09:30 close − pre-release 08:27 close); market exits at
{15, 30, 60} min (bar close); C1 friction. Placebo: identical rule on non-release
days (FOMC-only 14:00 days excluded from both groups, reported as sensitivity —
same grouping as W7-3).

## Sample (FACT)

- CSV rows read 540,232; kept 519,833 (dev guard < 2026-06-01), range 2022-01-02 18:03 → 2026-05-31 23:57 ET.
- Days simulated 1,134 (skipped: no_pre 9, no_entry 2, no_exit 1, zero_sig 1); pre-release anchor bar end-stamp = 08:27 on all 1,134 days.
- Groups: release 102, placebo 998, fomc_only 34. Calendar dev window: 104 08:30-release days (52 CPI, 52 NFP, zero same-day NFP+CPI), 34 FOMC-only.

## Pooled results — IN-SAMPLE CHARACTERIZATION

net C1 ticks/trade, day-clustered 95% CI (`w8bfade_summary.csv`):

| group | h (min) | n | net C1 (t) | CI lo | CI hi | gross (t) | win % |
|---|---|---|---|---|---|---|---|
| release | 15 | 102 | **+47.26** | −5.37 | +91.98 | +50.13 | 58.8 |
| release | 30 | 102 | +42.00 | −22.78 | +107.47 | +44.87 | 55.9 |
| release | 60 | 102 | **+98.99** | **+12.16** | +183.80 | +101.86 | 56.9 |
| placebo | 15 | 998 | −15.08 | −30.76 | −0.28 | −12.20 | 47.0 |
| placebo | 30 | 998 | −8.18 | −29.71 | +11.98 | −5.31 | 49.7 |
| placebo | 60 | 998 | −17.88 | −44.01 | +6.23 | −15.01 | 48.6 |
| fomc_only | 15 | 34 | +17.54 | −41.11 | +72.31 | +20.41 | 58.8 |
| fomc_only | 30 | 34 | +12.04 | −47.14 | +74.84 | +14.91 | 50.0 |
| fomc_only | 60 | 34 | −24.34 | −127.77 | +76.72 | −21.47 | 47.1 |

Only the 60-min horizon has CI_lo > 0 (+12.16). The 15-min CI straddles zero
(−5.37). The placebo is **negative** at every horizon (significantly at 15 min,
CI −30.76 to −0.28) — i.e., fading the 08:27→09:30 move on ordinary days loses;
the fade profile is specific to release days on this sample. That placebo
separation is the one encouraging structural feature — but per the honesty
clause it carries no confirmatory weight.

## Reconciliation vs W7-3 (required, PASS)

Expected identity: fade_net(h) = −cont_net(h) − 2×C1 (flipped sign minus double
friction), with identical n. All nine group×horizon cells match to < 1e-13 t:

| group | h | W7-3 cont net | expected fade | this run | diff |
|---|---|---|---|---|---|
| release | 15 | −52.999 | +47.255 | +47.255 | −6.4e-14 |
| release | 30 | −47.745 | +42.001 | +42.001 | −2.1e-14 |
| release | 60 | −104.735 | +98.991 | +98.991 | +8.5e-14 |
| placebo | 15 | +9.332 | −15.076 | −15.076 | −1.8e-14 |
| placebo | 30 | +2.437 | −8.181 | −8.181 | −1.2e-14 |
| placebo | 60 | +12.140 | −17.884 | −17.884 | −7.1e-15 |
| fomc_only | 15 | −23.284 | +17.540 | +17.540 | −1.1e-14 |
| fomc_only | 30 | −17.784 | +12.040 | +12.040 | −1.1e-14 |
| fomc_only | 60 | +18.599 | −24.343 | −24.343 | −3.6e-15 |

**RECONCILIATION: PASS** — this study is the exact preregistered mirror of the
W7-3 event join (same days, same bars, same exits).

## By event type — IN-SAMPLE CHARACTERIZATION

| type | h | n | net C1 (t) | CI lo | CI hi | win % |
|---|---|---|---|---|---|---|
| CPI | 15 | 52 | +23.49 | −33.00 | +79.85 | 59.6 |
| CPI | 30 | 52 | +21.11 | −57.64 | +111.26 | 51.9 |
| CPI | 60 | 52 | +39.26 | −66.42 | +148.42 | 51.9 |
| NFP | 15 | 50 | +71.97 | −3.64 | +144.40 | 58.0 |
| NFP | 30 | 50 | +63.73 | −37.74 | +164.07 | 60.0 |
| NFP | 60 | 50 | **+161.11** | **+30.80** | +299.88 | 62.0 |

No same-day NFP+CPI days exist in the dev calendar (n=0), so the "both" cell is
empty by construction. The effect is NFP-heavy: NFP@60min is the only
event-type cell with CI_lo > 0; CPI is positive but CI-straddling everywhere.

## Stability by year — IN-SAMPLE CHARACTERIZATION

Release fade (placebo mean alongside), net C1 t:

| year | h=15 (n) | h=30 | h=60 | placebo h=15 |
|---|---|---|---|---|
| 2022 | +106.42 (24) | +38.21 | +98.63 | −22.80 |
| 2023 | +15.56 (23) | +43.26 | +75.87 | −13.30 |
| 2024 | +72.42 (24) | +78.38 | +135.55 | −19.28 |
| 2025 | −0.10 (22) | **−54.28** | **−49.46** | −21.12 |
| 2026* | +19.13 (9) | +187.24 | +424.46 | +24.26 |

*2026 is a 5-month partial (n=9). **2025 is a failed year at 30/60 min** — the
effect is not year-uniform, and 2026's strong partial (best trade 2026-02-11,
+1365.1t@60) does heavy lifting in the pooled 60-min result. This is exactly the
kind of instability the pre-2022 confirmation must adjudicate.

## Equity path, drawdown, worst trade, concentration — IN-SAMPLE CHARACTERIZATION

Full paths in `w8bfade_equity.csv`; summary in `w8bfade_concentration.csv`
($ at 1 NQ = $5/tick, context only):

| h | total net (t) | $ (1 NQ) | max DD (t) | DD trough | worst trade | best trade | top-5 share of total |
|---|---|---|---|---|---|---|---|
| 15 | +4,820.1 | +$24,100 | −1,208.2 | 2025-02-07 | −672.9t 2025-08-01 (NFP) | +764.1t 2022-11-04 | 54.6% |
| 30 | +4,284.1 | +$21,420 | −2,742.2 | 2025-11-20 | −837.9t 2022-05-06 (NFP) | +919.1t 2026-05-08 | 82.6% |
| 60 | +10,097.1 | +$50,485 | −2,733.8 | 2025-08-12 | −828.9t 2025-05-13 (CPI) | +1,365.1t 2026-02-11 | 53.1% |

Concentration is high: top-5 winners are 53–83% of total net (21.5–22.5% of
gross wins). Single-trade tails are fat both ways (worst ≈ −840t ≈ −$4,190 at
1 NQ on one release). Max drawdown at 60 min is −2,733.8t (−$13,669) against
+10,097t total — a rough 3.7:1 net-to-DD over 4.4 years at 1 trade/month-pair
cadence.

## Confirmation plan status (dependency found)

- **FACT:** `c01_announcement_calendar.csv` starts **2022-01-07** (ends
  2026-07-29). It contains **0** pre-2022 08:30 releases.
- **DEPENDENCY:** the frozen pre-2022 confirmation therefore requires **two**
  inputs, not one: (1) SWMinuteExport_v1 1-min data 2005+ (already in the W8
  blocked queue), **and (2) a 2005–2021 historical 08:30 release calendar
  (NFP + CPI dates from BLS archives) — not yet built.** Add it to the blocked
  queue alongside the exporter.
- **INFERENCE (estimate, not a count):** if built, ~12 NFP + ~12 CPI per year ×
  17 years ≈ **~408 release days**, ~4× the dev n of 102 — ample power for the
  frozen CI_lo > 0 test.

## Verdict scope

CHARACTERIZATION ONLY (honesty clause binding). Suggestive profile: positive on
release days at all horizons (CI_lo > 0 only at 60 min, driven by NFP), negative
placebo, but a failed 2025 and 53–83% top-5 concentration. Nothing is promoted;
the pre-2022 test (data + calendar dependencies above) is the only path forward.
