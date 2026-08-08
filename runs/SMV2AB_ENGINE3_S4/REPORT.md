# SMV2AB_ENGINE3_S4 — Engine #3 slate 4 (seq 410-412): first cross-market candidates, ALL KILLED

_Frozen spec: `runs/SMV2AB_ENGINE3_S4/spec.yaml` (committed 0da78b6 before any read). Authored
by the orchestrator from the execution agent's structured output — the subagent's Write tool
refused a direct REPORT.md write, same restriction seen on prior runs; every number below
traces to a committed `out/` artifact, independently reproduced by red-team. Traded instrument
is ALWAYS NQ; ES/RTY/YM feed only z-scores/consensus-sign/spread-direction, never a fill or a
P&L of their own — independently verified by red-team (code reading of every `net` expression)._

## Prerequisite: session-calendar check (`out/session_calendar_check.csv`)
ES 3m aggregation matches the NQ dev session-date set exactly (1139/1139). RTY and YM are each
missing the SAME 7 sessions (2023-04-06..2023-04-14) — a genuine 11-day gap confirmed directly
in the raw 1-minute source parquet files (2023-04-05 14:03 → 2023-04-16 18:01), not an
aggregation artifact, and consistent with the campaign's already-known 2023-04-05/06 boundary
irregularity. Not patched or interpolated (never rewrite raw evidence). The merged table drops
those 7 sessions via inner join (515,306 of NQ's 519,714 dev bars, 1132 of 1139 sessions).
**None of the 23 SMV2Z-flagged joint-whipsaw weeks fall in that gap** (all 23 are 2024-2026) —
confirmed in-run and independently by red-team.

## Engine 410 — cap-tier dispersion catch-up (ES+NQ consensus, RTY laggard) — KILLED
Center (z=1.5): N=1008 events, mean +$98.20/event, t_NW=1.71 (<2, gate fails). Walk-forward
sign FAILS: 2022-24 mean +$185.05 vs 2025-26 mean −$83.49 (opposite signs). Plateau across
z∈{1.25,1.5,1.75} is same-sign (all positive, t_NW improving monotonically with stricter
threshold: 0.65/1.71/1.82) — that gate alone passes. **Correcting the exec agent's own
arithmetic**: of the 4 gates (N≥60, t_NW≥2, WF same-sign, plateau), exactly **2 fail** (t_NW,
WF) and 2 pass (N, plateau) — the agent's structured output said "3 of 4 fail," which
contradicts its own `gates.csv` (2 False rows); red-team caught this. The final verdict is
unaffected either way (`verdict_rule` requires ALL gates to pass): **FAIL**.

## Engine 411 — duration-spread shock reaction (NQ shock, YM-quiet continuation) — KILLED
Center (YM-quiet<0.75, hold=60min): N=1094, mean +$54.84/event, t_NW=1.30 (<2, gate fails).
WF sign PASSES (2022-24 +$22.78 vs 2025-26 +$120.22, both positive). Plateau across
YM-quiet∈{0.5,0.75,1.0} PASSES (all positive). The core significance gate is the one that
fails — point estimates are consistently positive but not statistically distinguishable from
noise. **FAIL**.

## Engine 412 — quarterly roll basis convergence (ES-vs-(RTY+YM)/2 spread) — KILLED
17/17 quarterly 3rd-Friday cycles tradeable (N≥12 power floor passes). mean +$26.82/event,
t_NW=0.03 (essentially zero). WF sign FAILS (2022-24 mean −$418.94, n=12, vs 2025-26 mean
+$1,096.64, n=5 — thin but reported per spec's explicit instruction not to silently drop a
small-N WF read). **Only the N-floor gate passes; FAIL** on economic significance and
chronology.

**Material interpretive call (HYPOTHESIS, flagged not settled)**: the frozen spec's literal
direction rule ("enter NQ in the direction of the spread's roll-week drift") is logically
circular at a Monday-open entry — it would require using the week's own future realized drift
to pick that same week's entry direction, which cannot be implemented as a tradeable rule.
This run substituted a non-lookahead reading: direction from the 3 trading sessions
immediately BEFORE the roll week. Flagged explicitly as a redesign candidate if e412 is ever
revisited, not treated as a settled definition. Separately, "the actual NQ contract roll
session" has no discoverable calendar/date source anywhere in this repo; the run used the
spec's own disclosed fallback (exit at the expiration session's own close) uniformly.

## Joint-whipsaw complementarity (V4.1 §14, PRIMARY read for this slate)
**Important disclosed fact, correcting an implicit assumption from prior waves**: the 23
SMV2Z-flagged weeks are NOT simply losing weeks for the champion. The champion's mean weekly
PnL is actually HIGHER during flagged weeks (**+$2,465.90/wk**) than during the other 206 weeks
(+$652.10/wk), driven by high dispersion including some very large positive weeks (e.g. week
202515: +$33,517.52, independently recomputed by red-team — the exec agent's own figure of
"+$33,513" is corrected here, immaterial to any gate). This is fully consistent with SMV2Z's
own construction — an AND-gate built to target downside-risk metrics (CDaR/TUW), not a
mean-PnL classifier — but it sharpens the interpretation: these are high-VARIANCE,
regime-uncertain weeks that have, on net, been GOOD for the champion so far, not simply bad
weeks with occasional large losses buried in them.

| engine | mean $/wk, flagged weeks | mean $/wk, other weeks | events in flagged weeks |
|---|---|---|---|
| e410 dispersion catch-up | +$306.60 | +$446.30 | 22/23 weeks had events |
| e411 shock reaction | −$164.94 | +$309.68 | 23/23 weeks had events |
| e412 roll convergence | −$157.53 | +$19.80 | 3/23 weeks had events (thin) |

**None of the three engines hits the V4.1 §14 target outcome** (earn, or stay flat, SPECIFICALLY
during flagged weeks). e410 is the closest — it stays positive there — but is proportionally
weaker in flagged weeks than elsewhere, not selectively strong. e411 is mildly ANTI-complementary
(goes negative exactly where the target wanted flat-or-positive). e412's read is not meaningful
given only 3 flagged-week events.

## Verdict
**ALL THREE ENGINES KILLED.** This is the first cross-market Engine-3 slate, and it fails
cleanly rather than ambiguously — none clears its significance gate, and none shows the
targeted joint-whipsaw complementarity. Combined with the three NQ-only slates (SMV2K, SMV2P,
SMV2X — 9/9 killed), **12 of 12 tested Engine-3 candidates across 4 slates have now failed.**
Per the frozen spec's own next-step guidance, the remaining ranked cross-market candidates
(D1 ranks 3/4/6, D2 rank 1, plus the D2/D3 candidates flagged weaker by the deep-research
passes themselves) are the next place to look before declaring cross-market exhausted — that
requires a new frozen spec, out of scope for this run.

## Outputs
`out/e410_events.csv`, `out/e410_summary.csv`, `out/e411_events.csv`, `out/e411_summary.csv`,
`out/e412_events.csv`, `out/e412_expiry_calendar.csv`, `out/e412_summary.csv`, `out/gates.csv`,
`out/jointwhipsaw_complementarity.csv`, `out/session_calendar_check.csv`,
`out/merged_3m_dev.parquet`, `out/verdicts.json`, `out/redteam_notes.md`, `smv2ab.py`,
`run_log.txt`.
