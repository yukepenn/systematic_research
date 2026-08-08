"""Emit REPORT.md for SMV2K_ENGINE3_S1 (spec-required output). All numbers sourced from out/*.csv."""
import io

REPORT = r"""# SMV2K_ENGINE3_S1 — R1 Family Test, Engine #3 slate (seq 368–370)

Executor: `runs/SMV2K_ENGINE3_S1/smv2k.py` (single deterministic script, re-run verified identical).
Artifacts: `out/e368_events.csv`, `out/e368_summary.csv`, `out/e368_plateau.csv`, `out/e369_events.csv`,
`out/e369_summary.csv`, `out/e369_plateau.csv`, `out/e370_trades.csv`, `out/e370_summary.csv`,
`out/complementarity.csv`, `out/gates.csv`, `out/session_table.csv`.
Every number below comes from those files. No bootstrap needed (NW t-stats only); no RNG used.

## Verdicts

| seq | engine | verdict | one-line reason |
|-----|--------|---------|-----------------|
| 368 | failed range-break fade (PDH/PDL/ONH/ONL/IBH/IBL) | **KILL** | expectancy significantly NEGATIVE: -$25.2/event net, t_NW -2.35, N=3093; all 9 plateau cells negative; both WF halves negative |
| 369 | small-gap fade | **KILL** | -$125.2/event net, t_NW -1.99 (need >= +2), N=627; both WF halves negative; all 3 plateau cells negative |
| 370 | overnight drift (designated cheap kill) | **KILL** (as pre-registered expectation) | conditional +$137.0/night t_NW 1.00 (N=506); unconditional +$100.1 t_NW 1.24 (N=1091); nowhere near t >= 2 |

Per `verdict_rule`: family killed. Next independent family from the DR pass A ranking
(H2 value-area rotation / H9 multi-day balance false-break) gets the next spec.
No parameter search beyond the frozen plateau grids was performed.

## Data hygiene (FACT)

- Substrate: `sm01_solarsim.load_bars_3m()` — max session in file 2026-07-31 (< 2026-08-01 VIRGIN wall,
  asserted in code); filtered to dev sessions <= 2026-05-31 immediately after load.
- Dev: 519,714 bars, 1,139 sessions, 2022-01-03 .. 2026-05-29. ATR14d valid on 1,124 sessions
  (first 15 excluded, causal prior-day-only); 1,136 sessions have RTH starting at stamp 0933
  (3 sessions have no RTH bars and are skipped). (`out/session_table.csv`)
- Costs: NET of $4.36/RT + 1 tick/side slippage via the canonical `_fill` convention, $20/pt NQ.
- Walk-forward split: sessions <= 2024-12-31 vs 2025-01-01..2026-05-31.

## e368 — failed range-break fade (`out/e368_summary.csv`, `out/e368_plateau.csv`)

Center cell (0.25 x ATR14d penetration cap, 15-min confirmation):

| cell | N | mean net $/event | t_NW(5) | t_cluster | t_iid |
|------|---|------------------|---------|-----------|-------|
| pooled_all | 3093 | -25.23 | -2.35 | -2.25 | -2.38 |
| pooled dedup (simultaneous entries) | 2971 | -24.22 | -2.28 | -2.17 | -2.23 |
| split 2022-24 | 2108 | -34.85 | -2.84 | | |
| split 2025-26 | 985 | -4.64 | -0.22 | | |
| PDH | 436 | -17.10 | -0.60 | | |
| PDL | 368 | -58.87 | -2.27 | | |
| ONH | 600 | -53.57 | -2.70 | | |
| ONL | 569 | -23.20 | -0.93 | | |
| IBH | 576 | -19.28 | -0.73 | | |
| IBL | 544 | +13.86 | +0.46 | | |

Gates: t_NW >= 2 **FAIL** (-2.35); N >= 300 pass (3093); split sign stable pass (both negative);
plateau all-same-sign pass (all 9 cells negative, mean -22.1..-28.0, t -2.04..-2.71). The family is not
merely insignificant — it is a *significantly negative* expectancy under its own preregistered gates.

- FACT: exit decomposition — stops (2 ticks beyond sweep extreme) fire on 1626/3093 events (52.6%) at
  -$386/event; VWAP-touch exits (1352, 43.7%) make +$365; 60-min time exits +$507 (N=103).
- FACT: 571 events had VWAP on the wrong side of price at confirmation (fade target already passed;
  mechanical near-immediate exit, preregistered fade side kept). Excluding them the pooled mean is
  still negative (-$16.2, t -1.24) — the kill is not an artifact of these events.
- INFERENCE: at 3m granularity the "sweep" pattern resolves as breakout-continuation more often than
  reversion — the 2-tick stop beyond the sweep extreme is hit in half the events. This is consistent
  with the campaign's standing finding that NQ pays a breakout premium (Solar/B-MOM side); the mirror
  fade side loses. Anti-dup rule forbids flipping the side; the fade family is killed, not redesigned.
- Disclosure: 243 events flagged simultaneous (same entry bar, multiple levels), 378 with interval
  overlap; dedup sensitivity above reaches the same conclusion. 246 events had the 09:30 open already
  outside the level (kept, literal spec). 12 late events force-exited at RTH end (`exit_rth_end`).

## e369 — small-gap fade (`out/e369_summary.csv`, `out/e369_plateau.csv`)

Center cell (|gap| < 0.5 x ATR14d, open inside prior RTH range):

| cell | N | mean net $/event | t_NW(5) |
|------|---|------------------|---------|
| pooled | 627 | -125.16 | -1.99 |
| split 2022-24 | 443 | -46.01 | -0.69 |
| split 2025-26 | 184 | -315.72 | -2.35 |
| filled (touched prior close) | 391 | +730.60 | +16.14 |
| unfilled (11:30 time-stop) | 236 | -1542.96 | -11.10 |

- FACT: event count 627; fill rate 62.4%; median time-to-fill 6 minutes (from the 09:33 entry).
- FACT: gates — t_NW >= 2 FAIL (-1.99), N >= 250 pass, split signs both negative, plateau
  {0.3, 0.5, 0.7} x ATR all negative (-91.7 / -125.2 / -120.9 $/event; t -1.42 / -1.99 / -1.94).
- INFERENCE: classic short-gamma profile — small wins when the gap fills fast, large losses on the
  37.6% of mornings when it never fills by 11:30. Net expectancy is negative and drifting *worse*
  in 2025-26. KILL.

## e370 — overnight drift cheap kill (`out/e370_summary.csv`, `out/e370_trades.csv`)

| cell | N | mean net $/night | total $ | t_NW(5) |
|------|---|------------------|---------|---------|
| conditional (post-down RTH day) | 506 | +136.98 | +69,314 | 1.00 |
| conditional 2022-24 | 348 | +87.77 | | 0.70 |
| conditional 2025-26 | 158 | +245.39 | | 0.72 |
| unconditional | 1091 | +100.14 | +109,253 | 1.24 |
| unconditional 2022-24 | 744 | +48.53 | | 0.64 |
| unconditional 2025-26 | 347 | +210.80 | | 1.08 |

- FACT: positive point estimates, but t far below 2 in every cell; the down-day conditioning adds
  nothing distinguishable from the unconditional drift (its t is *lower*).
- INFERENCE: consistent with the NY Fed 2026 prior (overnight drift ~ statistically zero since 2021).
  Recorded as the pre-registered KILL. HYPOTHESIS (not actionable, no gate): the 2025-26 uptick in the
  point estimate is regime beta, not an edge — it does not survive any significance read.

## Complementarity vs champion DAYONLY_DUAL6040 (`out/complementarity.csv`)

Champion daily curve = `60_40` column of `runs/SMV2H_ONECONTRACT/out/rerank_curves.csv` (1,139 dev days;
632 champion losing days; 113 bottom-decile days, champion mean on those -$2,950/day). Engine daily PnL
zero-filled on non-event days.

| engine | corr all days | corr champ-losing days | mean $/day on champ bottom decile |
|--------|---------------|------------------------|-----------------------------------|
| e368 center | -0.194 | -0.121 | +305.6 |
| e369 center | -0.295 | -0.101 | +400.7 |
| e370 conditional | +0.071 | +0.074 | -307.7 |
| e370 unconditional | +0.051 | +0.067 | -344.2 |

- FACT: the two fade engines are negatively correlated with the champion and make money on the
  champion's worst days — the V4 §25 strategic criterion would have been satisfied — but their
  standalone expectancy is significantly negative, so they are not addable.
- HYPOTHESIS (for the next family selection, not this run): the fade *direction* diversifies the
  breakout-premium book; a fade-family engine with >=0 expectancy (e.g., H2 value-area rotation) would
  be a strong portfolio candidate if one exists. This run provides the complementarity prior only.

## Conventions & implementation choices (disclosed)

1. 3m bars (spec discloses coarser than the external 1m prior); thresholds unchanged.
2. "HH:MM open" = the open occurring at wall-time HH:MM = open of the bar END-stamped HH:MM+3
   (anchored by the spec's "fade ... from 09:33 next-bar open"). e370: entry = open of 1645-stamped
   bar (wall 16:42), exit = open of 0936-stamped bar (wall 09:33). Event/decision windows are bar-close
   wall times (penetration bars stamped 0933-1530; 11:30 stop = close of the 1130-stamped bar).
3. Session VWAP: RTH-anchored cum(close*vol)/cum(vol) incl. current bar — the exact B-MOM convention
   reused from `runs/SMV2B_BMOM_EXEC_AUDIT/smv2b.py`.
4. e368 episode semantics: first inside->outside crossing opens an episode; confirmation = first close
   strictly back inside; qualifies iff within the confirmation window AND max sweep depth <= cap;
   disqualified episodes end and scanning continues; first qualifying episode per level per session.
5. Same-bar stop/target ambiguity resolved stop-first (conservative); entry-bar exits allowed;
   trades force-exited at the 1600-bar close if RTH ends first (12 events).
6. Newey-West lag = 5 sessions, Bartlett weights, clustered by session (spec fixes "by session" but
   not the lag; lag-0 cluster and iid t-stats are in the artifacts — sign and conclusion identical
   under all three for every gate).

## Bottom line

Three engines, three clean kills under their own frozen gates, with high-N evidence (3093 / 627 / 1091
events). The Engine #3 fade family is dead on NQ 3m dev data; the complementarity read (negative
correlation to the champion) is banked as a prior for the next independent family (H2 / H9).
"""

with io.open("runs/SMV2K_ENGINE3_S1/REPORT.md", "w", encoding="utf-8", newline="\n") as f:
    f.write(REPORT)
print("REPORT.md written,", len(REPORT), "chars")
