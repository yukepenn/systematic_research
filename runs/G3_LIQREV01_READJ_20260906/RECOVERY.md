# LIQREV01 — RECOVERY (facts only, cited)

## Location of artifacts
No `runs/` directory exists (campaign-#5 one-shot convention). Everything lives in
`research/system_master/LIQREV01_STRESS_REVERSAL/`:
- `SPEC.md` (frozen 2026-08-19, commit 9775c0a, pre-result)
- `REPORT.md` (readout 2026-08-19, incl. 4-attacker red team)
- `src/01_liqrev01.py` (the exact frozen implementation)
- `out/liqrev01_results.json`, `out/liqrev01_trades.csv` (455 trades, 2007-03-02 → 2026-05-20 entries), `out/liqrev01_placebo_trades.csv`

Contemporaneous state: `research/system_master/CURRENT_TRUTH.md` lines 102–131. Provenance: ENGINE3_SCOUT_20260819 gatekeeper rank-1 (Nagel RFS 2012 / CGW 1993 / Brunnermeier-Pedersen). It consumed that wave's 2nd-and-final alpha hypothesis (cap 2/2).

## The exact frozen rule (SPEC.md; constants confirmed in src/01_liqrev01.py)
- Substrate: `research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet` (sha256_16 dfd017ef, ends 2026-05-29; back-adjusted, POINT arithmetic only).
- Trading day = calendar day with ≥200 minute bars in 09:30–15:58 ET; `sess_close(d)` = close of last bar ≤ 15:58. `ret(d) = sess_close(d) − sess_close(d−1)` (points).
- Vol state: `rv5(d)` = sqrt(sum over sessions d−4..d of squared 1-min point returns in RTH). **Stress(d)** = percentile rank of rv5(d) within its trailing 252-session window ≥ 0.90.
- Triggers from PRIOR data only: q20/q80 of {ret(d−63)..ret(d−1)} (shift(1)). **LONG iff Stress(d) AND ret(d) ≤ q20; SHORT iff Stress(d) AND ret(d) ≥ q80.**
- Execution: enter at sess_close(d) + 1 tick adverse; exit at sess_close(d+1) + 1 tick adverse (1-day hold, next trading day's close); 1 NQ; $2.18/side commission (C1 all-in $14.36/RT = commission + 2 ticks); consecutive signals = independent trades (double-costed).
- Frozen constants: STRESS_PCT 0.90, quantiles 0.20/0.80, VOL_WIN 5, PCT_WIN 252, RET_WIN 63, seed 20260819, 10,000 bootstrap reps.

## The 8 gates and observed values (liqrev01_results.json; ALL PASS on the letter)
| Gate | Spec | Observed |
|---|---|---|
| G1 N≥300 | pooled | 455 (243L/212S) PASS |
| G2 episode-block bootstrap CI_lo>0 | 75 episodes, seed 20260819 | net $263,646, $579.44/t, CI [+$155, +$1,061]; iid [+$213, +$965] PASS |
| G3 ≥5/7 stress clusters positive | named years | 2008-09 −$438 · 2010 +$1,012 · 2011 +$2,179 · 2015-16 −$692 · 2018 +$3,900 · 2020 +$78,053 · 2022 +$36,830 → 5/7 PASS |
| G4 calm placebo NOT significantly positive | iid CI_lo≤0 | n=1,646, −$42.79/t, CI [−$159, +$73] PASS |
| G5 3×3 plateau all positive | s{85,90,95}×q{20,25,30} | all 9 cells +$420…+$706/t, monotone in stress PASS |
| G6 tail safety | top-1%≤50%, single≤25% | top-1% 33.6%; max single 16.0%; worst trade −$23,134; ES5 −$7,536 PASS |
| G7 losing-day corr ≤0.25 vs Solar B_SYM | 96 overlap days | 0.062 (full corr 0.688; net on Solar losing days −$46,028, non-gating) PASS |
| G8b 2016-26 not significantly negative | gating | n=248, +$1,121/t, CI [+$462, +$1,800] PASS |
Non-gating reads: G8a ex-release $653/t (n=399); G8c 2-day hold $352/t; G8e ex-gap-flag $488/t (proxy — superseded by red-team correct flag: excluding 7 flagged trades netting −$18,881 **raises** per-trade to $631).

## Why it did not freeze (REPORT.md §2–3)
Red team (4 attackers, bit-exact reproductions) — survived: no lookahead; fill variants 15:59/16:03/next-open keep G2 (≥$528/t, CI_lo +$147); matched calm placebo (452/455 caliper-matched on signed move) −$162/t — the state carries ~$740/trade; 3× commission + 2-tick slip $561/t CI_lo +$136. Killed: (1) **all statistical evidence is post-2020** — pre-2020: 301 trades / 13 yrs / 47 episodes, +$12.2/t, CI [−171,+187]; post-2020: 154 trades, +$1,688/t, CI [+687,+2,546]; 98.6% of net post-2020; (2) **mechanism label wrong** — trailing-252 percentile assigns ZERO stress sessions to 2009 and 68/67 to calm 2014/2024; the Nagel-canonical clusters (2008-09, 2015-16) are NEGATIVE; honest object = "vol-acceleration-gated reversal worked 2020-2026", effective N≈5 macro events; (3) **engine-#3 diversification role REFUTED vs Solar** — profit lands on Solar's TOP-decile days (+$148,934 on 14 days), −$46,517 on Solar's bottom-decile days, ZERO trades inside Solar's 2025-04→07 maxDD window, worst combined day −$29,853 (76% worse than Solar-alone), combo ΔSharpe CI [−0.32,+0.70]; (4) standalone 20-yr grid Sharpe 0.680 with a 7.2-year underwater stretch 2011→2018. Disposition: **PARKED — REGIME-LOCAL(2020+)** under the pre-W115 regime-veto doctrine, which the owner later revoked (CLAUDE.md §4: "Old-regime failure is a RISK CLASSIFICATION, not a promotion veto").

## Post-2020 economics as measured (aggregated read-only from out/liqrev01_trades.csv + results.json; DISCOVERY_CONSUMED)
- Post-2020 (entries ≥2020-01-01): **154 trades, $259,974 net, $1,688.1/t** (≈$778/wk over the 334-week span, but extremely lumpy — see droughts). 2021+: 118 trades, $181,921 ($1,541.7/t). 2023+: 72 trades, $110,126 ($1,529.5/t).
- Per-year: 2020 +$78,053 (36t) · 2021 +$34,964 (22t) · 2022 +$36,830 (24t) · **2023 $0 (0 trades)** · 2024 +$24,374 (38t) · 2025 +$82,604 (29t) · 2026-through-May +$3,148 (5t). 2019 also 0 trades.
- Episode structure (calendar-approx, gap>9 days): 23 post-2020 episodes; top-3 (COVID 2020-02-24→04-02 +$83,971/25t; 2022-04-26→05-17 +$44,746/9t; 2025-02-27→03-19 +$41,846/10t) = **65.6% of post-2020 net** (REPORT's full-sample figure: 64.7% of net from 9.7% of trades). Worst episode −$6,349 (single trade 2025-10-17).
- **Max inter-trade drought post-2020: 661 days (2022-05-17 → 2024-03-08).** The stress gate was fully dark in calendar 2023.
- Tails: worst trade −$23,134 (long entered 2025-04-03, exit 04-04 — the day REPORT flags as worst combined with Solar); next −$14,374 (2020-03-11), −$11,539 (2020-03-06), −$11,419 (2024-08-02), −$9,864 (2022-01-28). Best +$42,081 (2025-04-08). ES5 −$7,536. Post-2020 Sharpe and maxDD were never published — recomputation is part of the design below.
- Known substrate defects (REPORT §2 defects): missing week 2014-01-27..31 + scattered weekdays; 11 entries/15 exits on 13:00-halt thin holiday sessions netting −$15,695 (conservative direction).

## What "shadow silently dropped" means operationally
2026-08-19 (commit 1093ba3, owner-authorized "授权并且给你随意权限"): `research/operational/MONITOR01_SHADOW_HTFDIR01.md` was amended pre-reading to add **LIQREV01 as a second frozen shadow construction** — at each quarterly MONITOR-01 reading, extend its trade ledger over new forward data, with frozen ADVANCE (forward net>0 AND forward P&L on Solar's forward losing days ≥0, once ≥20 forward trades) / KILL (forward net ≤ −$10,000, or Solar-losing-day P&L ≤ −$10,000, or <20 trades by 2028-08). During the 2026-08-28 rewrite of `MONITORING_CALENDAR.md`, both shadow rows were omitted — `grep -i liqrev` on the calendar returned **zero hits** while CURRENT_TRUTH still named them as the next information events (`runs/GENESIS_W1_FORENSICS_20260828/reports/a2_git_forensics.md` §1). GENESIS Wave 1 **restored the row 2026-08-28** (MONITORING_CALENDAR.md, "HTFDIR01 + LIQREV01 shadow readings" due 2026-11-01 with MONITOR-01 #2). No shadow reading has ever occurred; forward data (≥2026-08-01) is virgin and untouched for this object (LOCKED_FORWARD.md seal amendment explicitly preserves LIQREV01's 2026-11-01 reading). Current queue status: `research/genesis2/WORLD_ALPHA_ATLAS.md` carries it as MC-19 FORWARD-QUEUE; `research/genesis/GENESIS_PRIOR_RESEARCH_ATLAS.md` §3 ranks it "cheapest high-value fix in the repo".

## Reference ledger for the portfolio-marginal design
`runs/WE_W56_BREADTH/out/p1_daily.csv` — P1 daily P&L at 1 NQ, 2022-07-05 → 2026-05-29, 607 sessions, net $300,817; bottom-decile threshold −$1,795 (61 days), worst day −$5,783. Caveat: research-chain P1 is ~2.0% optimistic (we_fastctx.py:81 double-lagged ATR, GENESIS III verdict) — immaterial for correlation/geometry reads, disclosed. LIQREV overlap with this ledger: the 72 trades of 2024–2026 only (2022 trades end 05-17, 2023 empty).