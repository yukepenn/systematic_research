# C01 T0-7 — Overnight/Intraday Decomposition (Family D stage 1)

_Executed 2026-08-07. Constants frozen in `C01_WAVE_SPEC.md` before any read. Data:
`runs/B01A_BARS_1M/nq_1m_2022_2026.csv` (1-min, ET stamps, bar time = close time),
`research/audit/e_variant_daily_vectors.csv` (E10_round_session). Session CSV companion:
`c01_t07_overnight_sessions.csv` (per-session r_on/r_id/trigger/sleeve_net)._

## VERDICT: REJECT — stage-1 gate NOT met; Tier-1 sleeve sim NOT unlocked

Frozen gate (task packet): PASS requires conditional r_on positive with pooled t ≥ 2 AND ≥ 3/5
years positive. Result: pooled conditional mean **+7.72 bps, t = 1.20** (Newey-West lag-5 t = 1.36)
— fails t ≥ 2. Years positive: 3/5 (2023, 2024, 2026) — that leg alone was met.

Hard axis-close clause ("REJECT if unconditional mean ≤ 0 AND conditional t < 2") is **not**
jointly triggered: unconditional r_on mean is +1.70 bps (t = 0.76 — statistically zero, i.e.,
the NY Fed falsifier is UPHELD, but the sign is positive). So: no promotion, and the letter of
the permanent-close clause is not satisfied either. Practical status: overnight axis produces no
Tier-1 unlock from this evidence; any reopening requires a new preregistered mechanism, not a
re-tune of this one (frozen-constant discipline).

Gate-divergence note (flagged for adjudication, does not change my verdict): the C01 spec's own
T0-7 line ("conditional after-cost Sharpe ≥ 0.3, ≥ 3/5 years, corr ≤ +.25, no month > 40%")
would nominally pass on these numbers (all-days after-cost Sharpe 0.64; 4/5 sleeve-net years
positive; corr 0.066; max month 27.5%). The task packet's stricter t ≥ 2 stage-1 gate governs
this item and fails. Both are reported so neither can be cherry-picked later.

## Spec correction (made BEFORE reading results — market reality, not tuning)

The source packet wrote the sleeve entry as **17:59 ET. That timestamp is impossible**: CME
equity-futures maintenance halt is 17:00–18:00 ET; there is no 17:59 trade or bar (verified —
no bars exist in 17:00–18:00 in the file). The overnight leg is therefore defined
**close-to-open: prior RTH close 16:00 → RTH open 09:30**, exactly as specified in the frozen
definitions used here: r_on = log(open_09:30 / prior close_16:00), r_id = log(close_16:00 /
open_09:30). The Tier-1 sim line "17:59→09:31" would, if ever unlocked, mean "first tradable
moment after the prior 16:00 anchor", i.e., entry at/after 18:00 reopen — noted, moot given
REJECT.

## Data hygiene

- 1,181 sessions with RTH bars, 2022-01-03 → 2026-07-31. Session date = ET stamp with hour ≥ 18
  rolled to next day. Every session's first RTH bar is stamped 09:31 (bar close-time convention;
  its open = the 09:30:00 print). Zero sessions excluded.
- 43 early-close sessions (last RTH stamp 13:00 ×33, 13:15 ×9, 14:03 ×1 — holiday half-days);
  kept, with the actual last bar ≤ 16:00 as that day's RTH close.
- No overnight leg spans > 4 calendar days.
- Caveat: prices are the back-adjusted continuous merge, so log-return magnitudes are damped in
  early years (adjusted 2022 level ≈ 19,700 vs actual ≈ 16,500); point-difference dollar P&L is
  exact. t-stats/Sharpes on log returns are scale-free per day and unaffected to first order.

## Unconditional decomposition, 2022–2026 (per session, log returns, bps)

| Series | Slice | n | mean (bps) | t | Sharpe (ann.) |
|---|---|---|---|---|---|
| r_on | pooled | 1,180 | +1.70 | 0.76 | 0.35 |
| r_on | 2022 | 257 | −8.29 | −1.54 | −1.53 |
| r_on | 2023 | 257 | +2.03 | 0.62 | 0.62 |
| r_on | 2024 | 259 | +7.23 | 1.79 | 1.76 |
| r_on | 2025 | 257 | +4.08 | 0.74 | 0.74 |
| r_on | 2026 (→Jul) | 150 | +4.59 | 0.62 | 0.80 |
| r_id | pooled | 1,181 | +1.38 | 0.46 | 0.21 |
| r_id | 2022 | 258 | −4.61 | −0.55 | −0.55 |
| r_id | 2023 | 257 | +10.31 | 2.09 | 2.07 |
| r_id | 2024 | 259 | −1.40 | −0.28 | −0.28 |
| r_id | 2025 | 257 | +1.25 | 0.17 | 0.17 |
| r_id | 2026 (→Jul) | 150 | +1.45 | 0.19 | 0.24 |

**Falsifier upheld**: unconditional overnight drift on NQ 2022–2026 is +1.7 bps/session with
t = 0.76 — indistinguishable from zero, exactly as the NY Fed literature says for post-2021.
Neither leg of the session carries an unconditional edge over this window.

## Conditional variant — r_on after prior r_id ≤ 25th pct (rolling 250d, no lookahead)

Trigger: r_id(t−1) ≤ 25th percentile of the trailing 250 r_id observations ending at t−1
(`shift(1).rolling(250, min_periods=250).quantile(0.25)`). Signal live from 2022-12-20.
Trigger rate 216/931 = 23.2% (sane for a 25th-pct rule).

| Slice | n | mean (bps) | t | Sharpe (ann., active days) |
|---|---|---|---|---|
| pooled | 216 | +7.72 | **1.20** | 1.29 |
| 2022 (tail) | 2 | −39.3 | n/a (n=2) | n/a |
| 2023 | 45 | +14.81 | 2.03 | 4.81 |
| 2024 | 66 | +7.20 | 0.61 | 1.20 |
| 2025 | 60 | −2.22 | −0.16 | −0.33 |
| 2026 (→Jul) | 43 | +17.15 | 0.97 | 2.36 |

- Newey-West (5 lags) pooled t = 1.36; still < 2.
- Split-half (global-gate convention): half-1 +8.48 bps (t = 1.38, n = 74); half-2 +7.32 bps
  (t = 0.79, n = 142). Same sign — but neither half significant.
- **The conditioning itself carries no significant information**: triggered vs non-triggered
  r_on over the live window, Welch t = 0.66 (p = 0.51); unconditional r_on over the same live
  window is already +4.25 bps (t = 1.76). The condition roughly doubles the per-day mean but on
  ¼ of the days, and the difference is noise.

## Hypothetical conditional-overnight sleeve (context only, not a promotion)

Long 1 NQ at prior 16:00 close, exit 09:30 open, triggered days only, $4.36 RT + 2 ticks
($14.36 all-in): 216 trades, net **+$80,903**, $374.55/trade; active-day Sharpe 1.34, all-days
Sharpe (zeros when flat) 0.64. By year: 2023 +$22.6k (45), 2024 +$21.2k (66), 2025 **+$153**
(60 trades — a wash), 2026 +$39.2k (43). Max month +$22.2k = 27.5% of net (2024-07); worst
month **−$20.3k (2025-04)** — the rule is long-equity-after-weak-days, i.e., it eats crash
overnights; 2025's tariff-gap cluster wiped that year to zero. This left-tail signature is the
economic reason the t-stat is weak: the mean is carried by calm-regime gap-up runs and given
back in one bad month.

## Correlation vs E10 (gate ≤ +0.25): PASSES (moot)

Conditional-overnight daily P&L (zeros when flat) vs E10_round_session (NaN→0), common sessions
from signal start (n = 931): **corr = +0.066**. Active trigger days only (n = 216): +0.104.
Overnight P&L would be genuinely complementary to Family A — the diversification premise of
Family D is real; the standalone edge is just not statistically there under the frozen gate.

## Registry disposition

- C01-T0-7 → `hypotheses.md`: tested, stage-1 gate FAILED (t = 1.20 < 2); axis produces no
  Tier-1 unlock; hard permanent-close clause not jointly triggered (unconditional mean > 0 but
  t = 0.76). Instrumentation row (counts_as_trial: no). 0 R1 trials consumed.
- Files: this report; `c01_t07_overnight_sessions.csv` (1,181 sessions: rth_open, rth_close,
  prev_close, r_on, r_id, on_points, trigger, sleeve_net, stamps, bar counts).
