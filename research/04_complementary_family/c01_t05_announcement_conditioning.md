# C01 T0-5 — Exogenous calendar test (announcement-day conditioning)

_Executed 2026-08-07 per `C01_WAVE_SPEC.md` §2 T0-5. Calendar
(`c01_announcement_calendar.csv`, 145 events / 144 unique dates, CPI+NFP 08:30 ET, FOMC 14:00 ET)
committed BEFORE analysis. Implementation constants fixed before first run (script header,
`t05_announce.py`): seed 20260807; 10,000 within-Fterc permutations; gate p is one-sided
(announcement > control), two-sided reported; halves H1 2022-07-01→2024-06-30 /
H2 2024-07-01→2026-06-30 by session label; DC segments assigned to the session of their closing
flip; a trade's session = session of its ENTRY; duplicate-date session uses earliest release for
the pre/post split. Tier-0 instrumentation — 0 R1 trials consumed._

## Verdict: **REJECT** — announcement sessions are *worse* than vol-matched controls, not ≥ 2× better. FOMC statement days are the significantly negative driver. No Tier-1 arm unlocked. Down-weighting is FORBIDDEN by the hard right-tail constraint (see §6).

Frozen gate: ann mean ≥ 2× matched non-ann mean, p < .05 after vol matching, same sign both halves.

| gate leg | required | observed | met? |
|---|---|---|---|
| ratio | ann ≥ 2× matched ctrl | −$138.0 vs +$213.7 (ratio −0.65) | **NO** |
| significance | perm p (one-sided) < .05 | 0.934 (two-sided 0.143) | **NO** |
| half consistency | same sign both halves | diff −$494 (H1) / −$221 (H2) — same sign, but NEGATIVE | sign yes, direction wrong |

## 1. Data

Session mapping: an 08:30 ET release on date D and a 14:00 ET FOMC on date D both fall inside the
NQ session that opened 18:00 ET on D−1, i.e. **session label = calendar date** (session_date rolls
hour ≥ 18 forward). 144/144 announcement dates matched to E10 sessions (2022-01-03 → 2026-07-31,
n = 1,184). Vol matching uses the T0-4 HAR-forecast tercile (`c01_t04_session_table.csv`, Fterc,
expanding breakpoints): matched universe 2022-09-15 → 2026-07-31, n = 1,002 (121 announcement /
881 control). Matched control mean = tercile means weighted by the announcement tercile mix;
permutations shuffle the announcement flag within tercile.

## 2. E10 daily P&L — raw and vol-matched ($/session)

| subset | n ann / ctrl | ann mean | ctrl mean | diff | p one / two |
|---|---|---|---|---|---|
| raw full 2022–2026 | 144 / 1,040 | −147.0 | +192.8 | −339.8 | — |
| **matched full** | 121 / 881 | **−138.0** | **+213.7** | **−351.7** | 0.934 / 0.143 |
| matched H1 | 56 / 406 | −374.2 | +119.5 | −493.7 | 0.990 / **0.031** |
| matched H2 | 62 / 455 | +50.4 | +271.6 | −221.2 | 0.695 / 0.594 |

Vol matching does not rescue the day: high HAR-forecast controls outperform announcement sessions
in the same tercile. In H1 the *negative* effect is two-sided significant.

## 3. Per-event-type (matched; exploratory beyond the 1 declared DoF)

| event | full diff (p two) | H1 diff | H2 diff |
|---|---|---|---|
| CPI (45) | −214.7 (0.564) | −165.8 | −282.9 |
| NFP (45) | −57.1 (0.874) | −585.0 | **+635.6** |
| **FOMC (32)** | **−1,013.0 (0.014)** | −929.1 (0.024) | −1,364.1 (0.050) |

FOMC statement sessions lose ≈ $820/session vs +$193 for matched controls — negative in BOTH
halves with two-sided p ≤ 0.05 in each. CPI is mildly negative both halves; NFP flips sign
(the only up-weight candidate, and it is not significant).

## 4. DC overshoot ratio r (θ = 179, 3-min closes)

| subset | r ann | r matched ctrl | diff | p one / two |
|---|---|---|---|---|
| full | 1.352 | 1.264 | +0.088 | 0.107 / 0.113 |
| H1 | 1.295 | 1.202 | +0.093 | 0.097 / 0.222 |
| H2 | 1.358 | 1.303 | +0.054 | 0.306 / 0.404 |

Directionally *higher* trend overshoot on announcement days (not significant) while strategy P&L is
worse: the price path trends more, but the flips it forces are badly timed — churn around the
release eats more than the extra overshoot pays.

## 5. Member-trade pre/post-release split (13 V3 ledgers, slip-1, net of commission; trade = entry→flat, assigned by entry time)

34,148 trades total; 4,877 on announcement sessions. Non-announcement mean **+$95.4/trade**.

| phase | n | mean $/trade | | event | pre mean | post mean |
|---|---|---|---|---|---|---|
| pre-release | 1,740 | **+74.3** | | CPI | +148.6 | −26.7 |
| post-release | 3,137 | **−111.0** | | NFP | +446.8 | −152.1 |
| | | | | FOMC | −238.9 | −241.6 |

The damage is post-release for CPI/NFP (pre-release trades are fine); FOMC sessions are bad in
both phases (the pre-14:00 drift chop hurts as much as the reaction). Halves: post-release mean
−$22.5 (H1) / −$185.4 (H2); pre-release −$262.4 (H1) / +$365.6 (H2).

## 6. Top-1% trade incidence (tail-safety quantification)

Pooled top-1% trades (n = 342, threshold +$8,923): **70 (20.5%) occur on announcement sessions**,
vs a 12.2% announcement share of sessions (incidence ratio 1.68); announcement days carry
**24.2% of total top-1% P&L**. Consequence: any m < 1 down-weight of announcement sessions would
put top-1% P&L share (20.5%) far above session share (12.2%) in the down-weighted state — a direct
violation of the wave's hard right-tail constraint. The preregistered rule was up-weight-only;
the up-weight premise failed the gate. **Both directions are therefore closed:** no up-weight
(gate REJECT), no down-weight (right-tail constraint), despite the significant FOMC negative.

## 7. Disposition

- C01-T0-5 REJECT recorded; announcement-day conditioning axis closed at Tier-0, 0 trials burned.
- The FOMC finding (−$1,013/session vs matched, p ≤ .05 both halves, wrong-side significant) is
  archived as descriptive evidence for the registry — actionable only via a mechanism that does not
  down-weight exposure (none preregistered; none opened here).
- Files: `c01_t05_results.csv` (all summary rows incl. GATE), `c01_t05_session_flags.csv`
  (per-session flags/terciles/events used).
