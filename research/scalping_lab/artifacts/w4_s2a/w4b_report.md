# W4-B — S2a python analog (owner seed, frozen params): readout

Spec: `research/scalping_lab/specs/W4_alpha_wave1.md` §"W4-B" (frozen before readout).
Code: `research/scalping_lab/src/python/w4b_s2a.py`. Seed 20260808, 1000 bootstrap reps,
session (day-clustered) resampling. Data: 37 L2 discovery sessions, sechilo + grid1s.
Costs: C1 = 2.872t RT, C2 = 4.872t RT. All numbers below appear in
`w4b_stdout.txt` / `w4b_pooled.csv` / `w4b_trades.csv` (FACT unless labeled INFERENCE).

## VERDICT: KILL (definitive kill, KPI outcome B)

PRIMARY (frozen): 3-min fixed-time exit, long+short pooled, net C1.

- **fix3 all: n=109 trades (2.95/day, 35 unique days), win 49.5%, avg gross +1.197t,
  net C1 = −1.675t, day-clustered 95% CI [−12.346, +10.968], net C2 = −3.675t.**
- Point estimate NEGATIVE at C1; CI is wide and straddles zero. Owner-gate spirit
  (positive net C1 with CI lower bound > −0.5t) is decisively not met: CI_lo = −12.346t.
- No re-tuning performed; params were frozen (20-bar lookback, CLV 0.70/0.30, 1–3
  pullback bars, +1t trigger, 10:15–15:15, cooldown 2 bars, one trade per impulse).

Supporting evidence for kill (FACT):
1. Secondary bracket diagnostics are negative with CI entirely below zero:
   brk24_8 all n=120, P(tgt-first)=0.2101, net C1 −3.989t CI [−6.047, −1.810];
   brk32_10 all n=120, P(tgt-first)=0.2017, net C1 −4.239t CI [−6.940, −1.440].
   INFERENCE (arithmetic, in stdout addendum): required break-even P(tgt) at C1 is
   0.3397 for (24,8) and 0.3065 for (32,10) — realized ~0.20–0.21 is far below both.
2. The LONG side is negative at every one of the 7 exit variants, with CI upper bound
   < 0 in 5 of 7: fix1 −9.815 [−15.333, −4.379]; fix2 −10.800 [−19.170, −2.479];
   fix3 −11.577 [−22.493, −0.889]; fix5 −9.804 [−25.411, +3.436];
   fix8 −6.302 [−26.749, +13.520]; brk24_8 −4.647 [−7.708, −1.006];
   brk32_10 −5.971 [−9.547, −2.085]. Breakout-acceptance rebreak LONG on NQ at this
   frequency is adverse selection, not edge (INFERENCE).

## Pooled results per exit variant (net ticks/trade, day-clustered 95% CI on net C1)

| variant | side | n | n/day | days | win% | gross | net C1 | CI lo | CI hi | net C2 |
|---|---|---|---|---|---|---|---|---|---|---|
| fix1 | all | 116 | 3.14 | 35 | 43.1 | −0.302 | −3.174 | −9.923 | +3.177 | −5.174 |
| fix1 | long | 70 | 1.89 | 32 | 40.0 | −6.943 | −9.815 | −15.333 | −4.379 | −11.815 |
| fix1 | short | 46 | 1.24 | 23 | 47.8 | +9.804 | +6.932 | −6.979 | +20.591 | +4.932 |
| fix2 | all | 113 | 3.05 | 35 | 48.7 | −3.965 | −6.837 | −15.905 | +2.815 | −8.837 |
| fix2 | long | 69 | 1.86 | 32 | 46.4 | −7.928 | −10.800 | −19.170 | −2.479 | −12.800 |
| fix2 | short | 44 | 1.19 | 23 | 52.3 | +2.250 | −0.622 | −18.444 | +20.537 | −2.622 |
| **fix3 (PRIMARY)** | **all** | **109** | **2.95** | **35** | **49.5** | **+1.197** | **−1.675** | **−12.346** | **+10.968** | **−3.675** |
| fix3 | long | 66 | 1.78 | 32 | 40.9 | −8.705 | −11.577 | −22.493 | −0.889 | −13.577 |
| fix3 | short | 43 | 1.16 | 23 | 62.8 | +16.395 | +13.523 | −7.548 | +36.545 | +11.523 |
| fix5 | all | 110 | 2.97 | 35 | 46.4 | −1.641 | −4.513 | −17.724 | +8.000 | −6.513 |
| fix5 | long | 66 | 1.78 | 32 | 45.5 | −6.932 | −9.804 | −25.411 | +3.436 | −11.804 |
| fix5 | short | 44 | 1.19 | 23 | 47.7 | +6.295 | +3.423 | −16.931 | +26.656 | +1.423 |
| fix8 | all | 107 | 2.89 | 35 | 47.7 | +3.519 | +0.647 | −18.198 | +22.256 | −1.353 |
| fix8 | long | 64 | 1.73 | 32 | 48.4 | −3.430 | −6.302 | −26.749 | +13.520 | −8.302 |
| fix8 | short | 43 | 1.16 | 23 | 46.5 | +13.860 | +10.988 | −25.525 | +51.485 | +8.988 |
| brk24_8 | all | 120 | 3.24 | 35 | 21.7 | −1.117 | −3.989 | −6.047 | −1.810 | −5.989 |
| brk24_8 | long | 71 | 1.92 | 32 | 19.7 | −1.775 | −4.647 | −7.708 | −1.006 | −6.647 |
| brk24_8 | short | 49 | 1.32 | 23 | 24.5 | −0.163 | −3.035 | −6.042 | −0.205 | −5.035 |
| brk32_10 | all | 120 | 3.24 | 35 | 20.8 | −1.367 | −4.239 | −6.940 | −1.440 | −6.239 |
| brk32_10 | long | 71 | 1.92 | 32 | 16.9 | −3.099 | −5.971 | −9.547 | −2.085 | −7.971 |
| brk32_10 | short | 49 | 1.32 | 23 | 26.5 | +1.143 | −1.729 | −6.284 | +3.215 | −3.729 |

n/day = trades / 37 sessions; days = unique sessions with ≥1 trade; win% for fixed-time
= P(gross > 0), for brackets = P(gross > 0) (target hit); trade counts differ slightly
across variants because the cooldown (2 completed bars after exit) shifts the sequential
episode stream with the exit horizon.

Bracket outcome detail (FACT): brk24_8 all tgt=25 adv=94 cap=1; long tgt=13 adv=57 cap=1
P(tgt-first)=0.1857; short tgt=12 adv=37 P=0.2449. brk32_10 all tgt=24 adv=95 cap=1;
long tgt=11 adv=59 cap=1 P=0.1571; short tgt=13 adv=36 P=0.2653.

## Fixed-time gross distribution quartiles (ticks)

| variant | side | min | p25 | p50 | p75 | max |
|---|---|---|---|---|---|---|
| fix1 | all | −75.50 | −22.00 | −4.25 | +11.25 | +135.50 |
| fix2 | all | −204.00 | −28.00 | −1.00 | +22.00 | +167.50 |
| fix3 | all | −210.50 | −37.00 | 0.00 | +37.00 | +173.50 |
| fix3 | long | −122.00 | −42.00 | −6.50 | +19.75 | +91.00 |
| fix3 | short | −210.50 | −22.75 | +21.50 | +64.25 | +173.50 |
| fix5 | all | −279.50 | −43.88 | −3.00 | +32.88 | +214.50 |
| fix8 | all | −314.50 | −53.25 | −2.00 | +61.75 | +269.00 |

(Full per-side quartiles for every fixed variant are in `w4b_stdout.txt` lines 66–82.)
The fix3 distribution is wide (IQR 74t) around a ~0 median — per-trade dispersion is
~25–50x the cost hurdle, so the n=109 sample cannot resolve a small edge either way
(INFERENCE); what it does resolve is that the frozen configuration is not positive.

## Observations for the record (NOT selectable — frozen family, no re-tuning)

- SHORT side shows positive point estimates on fixed exits (fix3 short +13.523t, n=43,
  23 days, win 62.8%) but every short CI straddles zero (fix3 short CI [−7.548, +36.545])
  and the short bracket readouts are negative-to-flat (brk24_8 short −3.035t CI
  [−6.042, −0.205]). INFERENCE: consistent with a few large favorable tails (max +173.50t
  at fix3) rather than a reliable per-trade edge; picking the short side post hoc would
  be side-shopping on ~43 trades. If any successor is ever specced, it must be a NEW
  frozen spec (short-only S2a) tested on fresh eyes, per house rules.
- Impulse candidate bars across 37 sessions: 2455 long / 2016 short (FACT); the
  pullback-acceptance + trigger + window + cooldown funnel reduces this to ~3 trades/day.
- Tier-0 caveat (per spec): this is the python analog on mid; NT8 engine parity would be
  required before any Tier-1 claim — moot given the kill.

## Verification (all FACT, output saved to `w4b_verify_stdout.txt` in this dir)

- 0 overlapping episodes, 0 cooldown violations, 0 entries outside 10:15–15:15.
- Fixed exits at exactly {60,120,180,300,480}s after entry for all trades.
- 10/10 randomly sampled trades (5 long, 5 short) independently recomputed from raw
  parquets: 20-bar breakout level, CLV threshold, pullback-close validity, ≥1
  down(up)-close, +1t trigger past pullback extreme, entry price, and gross P&L all match.

## Artifacts

- `research/scalping_lab/artifacts/w4_s2a/w4b_stdout.txt` — full run stdout (+ BE addendum)
- `research/scalping_lab/artifacts/w4_s2a/w4b_trades.csv` — 795 trade-level rows, all variants
- `research/scalping_lab/artifacts/w4_s2a/w4b_pooled.csv` — pooled table above
- `research/scalping_lab/artifacts/w4_s2a/w4b_impulse_counts.csv` — per-session impulse-bar counts
- `research/scalping_lab/artifacts/w4_s2a/w4b_verify_stdout.txt` — independent spot-check output
- `research/scalping_lab/src/python/w4b_s2a.py` — simulation code
