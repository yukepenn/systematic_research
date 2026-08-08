# RED TEAM NOTES — SMV2K_ENGINE3_S1 (statistical red team, V4 §48)

Date: 2026-08-08. Reviewer: independent red-team agent. Verdict: **CONFIRMED**.

## 1. Spec letter-exactness (PASS)

- spec.yaml frozen in commit `0a9cf3f` ("wave-2 specs FROZEN before any read ... SMV2K engine-3
  slate 1 (seq 368-370)"); zero diff between the frozen commit, HEAD, and the working tree.
- e368: levels PDH/PDL/ONH/ONL/IBH/IBL; penetration <= 0.25xATR14d; close-back-inside within
  5 bars; events restricted to 09:33-15:30 bar-close stamps (>=10:33 for IB levels — causally
  forced, IB completes 10:30); one event per level per session (first qualifying); entry toward
  VWAP at next 3m open; stop 2 ticks beyond sweep extreme; VWAP-touch / 60-min time-stop exits.
  All verified in code line-by-line against spec lines 14-24.
- e368 gates in `gates.csv` are the spec's gates verbatim: t_NW>=2, N>=300, split sign stable,
  plateau all-same-sign. Plateau is exactly the frozen 3x3 {0.15,0.25,0.35}x{9,15,21}; the
  center cell (N=3093, -25.228, t -2.354) equals the headline pooled run — grid used as plateau
  check only, no selection, no extra cells.
- e369: gap = 09:30 open - prior RTH close; strict |gap| < mult*ATR14d; open strictly inside
  prior RTH range; entry at 09:33 next-bar open; exit prior-close touch or 11:30 stop; gates
  t>=2 / N>=250 / WF sign / plateau {0.3,0.5,0.7} — all verbatim.
- e370: long 16:42 3m open after down RTH day (16:00 close < 09:30 open), exit next 09:33 open;
  unconditional as context; no pass gate (diagnostic cheap kill) — KILL recorded per
  preregistered expectation, correctly, despite positive point estimates.
- Timestamp convention ("HH:MM open" = open of the bar END-stamped HH:MM+3) is internally
  consistent, anchored by the spec's own "09:33 next-bar open" phrasing, and disclosed.

## 2. Independent recomputation (PASS — all match)

Recomputed from `out/` artifacts with an independently written NW(5) Bartlett session-clustered
t-stat, and by re-simulating single events from raw bars (`load_bars_3m`):

| quantity | reported | recomputed |
|---|---|---|
| e368 pooled N / mean / t_NW | 3093 / -25.23 / -2.35 | 3093 / -25.23 / -2.354 |
| e368 dedup N / t | 2971 / -2.28 | 2971 / -2.276 |
| e368 splits | -34.85 / -4.64 | -34.85 / -4.64 |
| e368 stop rate; exit decomposition | 52.6%; 1626 stops -$386, 1352 vwap +$365, 103 time +$507, 12 rth_end | 52.57%; identical |
| e368 excl wrong-side VWAP | N 2522 (571 excl), -16.2, t -1.24 | -16.20 / -1.237 / 571 |
| e368 plateau | 9/9 negative, t -2.04..-2.71 | 9/9 negative, t -2.039..-2.706 |
| e369 N / mean / t_NW | 627 / -125.16 / -1.99 | 627 / -125.16 / -1.990 |
| e369 fill rate / median fill | 0.624 / 6 min | 0.6236 / 6.0 |
| e369 filled / unfilled cells | +730.60 t +16.14 / -1542.96 t -11.10 | identical |
| e370 cond / uncond | 506 +136.98 t 1.00 / 1091 +100.14 t 1.24 | 0.998 / 1.242, totals 69,314 / 109,253 |
| complementarity (all 4 rows) | corr -0.194/-0.295/+0.071/+0.051; bottom-decile +305.6/+400.7/-307.7/-344.2 | identical to 4 decimals |
| session table | 1139 sessions 2022-01-03..2026-05-29, ATR valid 1124, rth933 1136 | identical |

Hand-verified one event per engine fully from raw bars (level value, penetration, confirmation
window, sweep extreme, entry fill, stop/target exit price, gap arithmetic, time-to-fill, down-day
flag, net $): every field matched the CSV exactly (e368 ONH stop event 2022-03-09 net -494.36;
e369 filled long 2023-02-14 net +2610.64; e370 trade 2024-01-08→09 net -1769.36).

## 3. Lookahead / leakage scan (PASS)

- ATR14d: `rolling(14).mean().shift(1)` — prior 14 sessions only, causal.
- PDH/PDL/prior-close: `shift(1)`. ONH/ONL: same-session pre-09:30 bars only. IB levels only
  scanned from stamp 1033 (after IB completes). All causal.
- Decisions at bar close, fills at next bar open via `_fill` (1-tick adverse slip capped by bar
  range); stop-first on same-bar ambiguity (conservative for these fade engines).
- No full-sample scaling or normalization anywhere; burn-in enforced via ATR NaN (first 15
  sessions dropped for e368/e369).
- VIRGIN wall: asserted `max sess < 2026-08-01` (file max 2026-07-31), then filtered to
  <= 2026-05-31; max session date in every artifact is 2026-05-29. Champion curve read-only from
  SMV2H_ONECONTRACT, dev-filtered.
- No RNG, deterministic; re-run reproducibility claim consistent with my exact event-level
  reproductions.

Minor non-material observations (none affect any verdict):
1. VWAP-touch exit compares bar i's low against a VWAP that includes bar i's own close/volume —
   mild intrabar approximation, but it is the disclosed, previously-frozen B-MOM convention and
   the engine it touches was killed as *significantly negative*.
2. e369 silently skips gap == 0 sessions (no fade direction exists; logically forced; min |gap|
   in events is 0.25 pts). Immaterial, would have been nice to disclose.
3. NW lag 5 was the executor's choice (spec silent); lag-0 cluster and iid t-stats are in the
   artifacts and agree in sign and conclusion for every gate — properly disclosed.

## 4. Report language (PASS)

FACT / INFERENCE / HYPOTHESIS labels used and used correctly; three kills recorded honestly
(e370 recorded KILL despite positive point estimates, per preregistration); complementarity
framed strictly as a banked prior, explicitly NOT as addability; no overclaim found. RTC /
right-tail checks not required by this spec (class R1_FAMILY_TEST, no promotion possible).

## 5. Blocked items

None reported; none found.

## Housekeeping for the orchestrator (not defects)

- Run outputs (smv2k.py, gen_report.py, REPORT.md, out/) are still untracked — commit after this
  red-team pass per workflow.
- `research/registry/tested_configs.csv` ends at seq 357; rows for seq 368-370 (and the rest of
  wave 2) still need to be appended.
