# Wave 1c — Tier-2 confirmation, statistical validation, and two falsifications

> **ERRATA — 2026-08-07, after independent red-team review.** The ensemble result in §4 was
> independently reproduced to the dollar and **stands**; PBO/CSCV was verified at 8/12/16/24 blocks
> with every IS→OOS slope negative. Two corrections: (a) **the DSR figures in §4c are withdrawn** —
> they used n_trials = 170 against a variance pool drawn only from surviving cells; under an honest
> pool they fall by roughly half. (b) The archived `wave1c_table_daily.csv` calendar holds 1,285
> traded dates but the union across all campaign families is **1,348**; it omits ~52 Sunday-evening
> and holiday sessions, so it must not be reused as a cross-family calendar. Also disclosed here
> rather than left implicit: **the top 1 % of trades contribute 248 % of this family's net P&L**,
> i.e. the bottom 99 % lose money in aggregate. See `research/06_red_team/RED_TEAM_WAVE1C_WAVE2.md`.


_2026-08-07 · Instrument `SolarWaveOpenX2` (open reconstruction, **zero vendor dependency**;
gate-checked against the frozen baseline to the penny) · NQ 09-26 back-adjusted · full history
2022-01-01T06:00:00Z → 2026-07-31T21:59:59Z · NinjaTrader Brokerage Lifetime commission ·
**real NT8 slippage at 0, 1 and 2 ticks per execution** (not analytic overlays) · 87 execution
ledgers, 80 distinct configurations · analytics `src/analytics/{execledger,wave1c,validation}.py`._

## 0. Method note — why this wave could be run at all

The engine payload for one full-history run is >3 MB of JSON, so 80 of them was not viable.
`SolarWaveOpenX2` instead writes every fill from `OnExecutionUpdate` to a compact CSV named from
the effective parameters, so **one NT8 optimization sweep yields one fill-level ledger per cell**.
Two integrity gates were passed before any result was read:

- the exec-ledger pipeline reproduces the frozen canonical baseline exactly — 2,915 trades,
  $146,440.60, PF 1.132213, commission $12,709.40, long 1,386 / $103,162.04, short 1,529 / $43,278.56;
- each sweep cell reproduces the engine's own summary (e.g. 3m SM 230 slip-1: 5,443 trades,
  $249,933.52, PF 1.0797954 — identical from the ledger and from `RunStrategyBacktest`).

**Incidental finding worth recording:** slippage does not change the trade sequence. Slip-0 and
slip-1 runs have byte-identical entry/exit timestamps, because every signal is close-based. The
realised cost is **$9.5352 per round trip**, distributed {0, 5, 10} rather than a flat $10 —
session-close and some boundary fills take none. This retro-validates the campaign's $9.53
analytic overlay and means cost ladders never need path re-derivation.

## 1. FALSIFICATION 1 — the 16:30 timed exit does **not** dominate

SW02a concluded on the canonical window (2023-01 → 2025-02) that exiting ≈16:31 beat holding to
the session close (102.4 % of net, smaller drawdown), and Wave 1 carried that forward as a live
exit-architecture candidate. On the **full 2022–2026 history with real slippage** it fails:

| | session close | ≈16:31 timed exit |
|---|---|---|
| matched (tf, SM, slip) pairs | 28 | 28 |
| timed exit wins | — | **4 / 28 (14 %)** |
| mean Δ (timed − close) | — | **−$11,247** |
| median Δ | — | **−$12,476** |

The SW02a result was a property of the shorter window, not of the strategy. **SW02a's primary
conclusion — no session-close fill artifact — still stands** (that was a collapse test, and it did
not collapse). Only the bonus finding is withdrawn. 16:30-exit is removed from the frontier as a
default and demoted to a conditional-sleeve idea.

## 2. FALSIFICATION 2 — the "46 % untaken signals" are not an opportunity set

The frozen wrapper exits on a flip bar and `return`s before the entry block, discarding that bar's
entry. Every prior wave treated the resulting 46 % of unfilled Type-1 signals as recoverable
opportunity (it is the explicit premise of SW03). A controlled three-arm test settles it —
`SolarWaveStopExecV1`, same ladder, one policy change per arm, 3-minute, full history, real slip-1,
dense SM 170–260:

| arm | policy | cells | trades | net (sum) | avg/trade | median Sharpe |
|---|---|---|---|---|---|---|
| **A** | market on close, flip-bar entry skipped (= baseline) | 10 | 61,714 | **+$1,739,242** | **+$29.49** | **+0.681** |
| **B** | market on close, always-in stop-and-reverse | 10 | 115,865 | +$1,249,474 | +$11.48 | +0.345 |
| **C** | resting stop at the ladder level, always-in (H-011) | 10 | 117,397 | **−$1,881,776** | −$15.52 | −0.404 |

**B − A isolates the skipped entries.** Taking them adds 54,151 trades that collectively lose
$489,768 — **−$9.04 per marginal trade** after costs. B beats A in only 3 of 10 cells (median
−$51,779). The skipped-entry behaviour, which was recorded as an accident of our wrapper, is
**worth roughly half a million dollars over the period**. SW03's premise is withdrawn; a Type-3
re-entry sleeve must now justify itself against this measurement rather than against an assumed
opportunity set.

## 3. H-011 (stop-order execution) — **REJECTED**, and the reason matters

DC01 measured that the close-basis crossing excess is ~23.5 ticks ($117.57) per segment, i.e.
**89 % of all friction** — four times commission plus 1-tick slippage combined
(`research/deep_research/DC01_DC02_RESULTS.md`). H-011 attacked it directly: rest a stop at the
ladder level instead of sending a market order after the breaking bar has closed.

Arm C is negative in **10 of 10 cells**, median −$282,803 versus arm B. Not marginal — catastrophic.

The mechanism is instructive and is the real deliverable. A resting stop fires on the **intrabar**
High/Low, but the ladder state still advances on **closes**. So the position flips while the ladder
does not, and the two desynchronise: the strategy ends up short while the ladder still reads "up",
then re-arms an entry stop on the wrong side of the market. The signature is visible in the payoff
shape — arm C's win rate *rises* (0.406 vs 0.384) while its average trade collapses to −$15.52:
many small wins financed by a fat left tail, the exact inverse of the trend-following profile the
system depends on.

**Conclusion: the close-basis excess is not recoverable by changing execution alone. It is
intrinsic to holding close-based state.** Capturing it would require making the *filter* intrabar
(a High/Low anchor), which is H-008 — a different hypothesis with different signal statistics, not
an execution tweak. H-011 is closed as FAILED and H-008's priority is raised accordingly.

## 4. The central result — you cannot select a StopMultiplier, so stop trying

### 4a. PBO says selection is worse than a coin flip

CSCV over 16 chronological blocks (12,870 half/half splits) on the archived T×N daily-P&L matrix
(1,318 trading days):

| family | configs | **PBO** | P(OOS Sharpe < 0) | IS→OOS slope |
|---|---|---|---|---|
| 3m, session close, slip-1 | 8 | **0.625** | 0.094 | **−1.031** (r = −0.79) |
| 1m, session close, slip-1 | 10 | **0.556** | 0.116 | −0.710 (r = −0.56) |
| all slip-1 | 38 | **0.658** | 0.158 | −0.908 (r = −0.67) |

PBO above 0.5 against a conventional ≤0.20 bar, and — more damning — a **negative** in-sample →
out-of-sample slope. The configuration that looks best in-sample tends to be *worse* than average
out-of-sample. This is not a claim about the strategy; it is a claim about the **selection step**.

Walk-forward confirms it directly (train 378d / test 126d / step 63d / 1-day embargo, 13 folds):

| family | selector | OOS net | positive folds | vs. median config | vs. best possible |
|---|---|---|---|---|---|
| 3m | argmax | $170,716 | 69 % | $152,357 | $458,857 |
| 3m | **neighbourhood median** | **$192,811** | **77 %** | $152,357 | $458,857 |
| 1m | argmax | **$16,131** | 77 % | $121,373 | $551,047 |
| 1m | **neighbourhood median** | **$77,007** | 62 % | $121,373 | $551,047 |

On 1-minute, picking the in-sample winner earns **$16k where picking blindly earns $121k**.
**DR06-H4 is CONFIRMED** — neighbourhood-smoothed selection dominates argmax on both timeframes —
but neither selector beats simply not choosing.

### 4b. What works instead: hold the whole plateau

Equal risk across every member of the connected plateau (1/N of one contract each), full history,
real slip-1:

| | 3m ensemble (8) | 1m ensemble (10) | 1m+3m (18) |
|---|---|---|---|
| net (per contract-unit) | $180,479 | $151,369 | $164,307 |
| **daily Sharpe** | **+0.803** | +0.717 | +0.786 |
| max drawdown | −$53,689 | −$57,484 | −$55,797 |
| Calmar | 0.643 | 0.503 | 0.563 |
| PSR | 0.969 | 0.951 | 0.966 |
| **positive in all 5 years** | **yes** | **yes** | **yes** |

Against its own members, exposure-matched (the ensemble runs 17–24 % less *net* directional
exposure because members disagree; gross exposure is identical, ratio 1.000, and Sharpe is
scale-free so the comparison is fair):

| 3m | net | Sharpe |
|---|---|---|
| ensemble, exposure-matched | **$216,922** | **+0.803** |
| mean single member | $180,479 | +0.668 |
| median single member | $189,346 | +0.693 |
| best single (**unknowable ex ante** — see 4a) | $249,934 | +0.947 |
| worst single | $97,390 | +0.368 |

- The ensemble beats **88 %** of its own members on Sharpe (70 % on 1m).
- **Only 3 of 8** 3m members are positive in all five years; **the ensemble is**. Worst
  member-year is −$16,845 (3m) and −$81,106 (1m); the ensemble has no negative year.
- The diversification is genuine, not an averaging illusion: all members agree on direction on
  only **53.6 %** of days (3m) and **35.7 %** (1m). Path chaos is idiosyncratic across
  StopMultiplier, so averaging cancels a large part of it — which is exactly what a discontinuous
  threshold recursion predicts.

**This reframes the campaign deliverable.** The output is not a parameter; it is a *region held as
an ensemble*. That is also the only honest response to PBO 0.63.

### 4c. DSR survives the multiple-testing haircut

Deflated Sharpe with `n_trials = 170` (all configurations logged campaign-to-date, including this
wave) and the empirical cross-sectional Sharpe variance: top cells reach **DSR 0.83**
(3m SM 230: Sharpe 0.947, PSR 0.986, DSR 0.832; 1m SM 200: 0.935 / 0.985 / 0.824). Twenty of 38
slip-1 configurations hold DSR ≥ 0.55. **The family's edge survives deflation even though the
choice within the family does not** — those two statements are consistent and together are the
correct summary of this wave.

### 4d. One preregistered hypothesis fails cleanly

**DR06-H5 REJECTED.** IID trade shuffling was predicted to materially understate tail risk versus
a stationary block bootstrap. Measured on the 3m ensemble: 5th-percentile max drawdown −$98,159
(iid) vs −$96,894 (block, mean block 20 days) — **understatement ratio 0.987**. No material
difference. Daily P&L autocorrelation is too weak for block structure to matter at this horizon;
iid resampling is adequate for this system's drawdown inference.

## 5. Per-year reality check

Positive-year frequency across the plateau at real slip-1 (this is the number that matters, and it
is *worse* than the campaign state's "positive every year" claim, which was a property of one
cherry-picked cell):

| | 2022 | 2023 | 2024 | 2025 | 2026 (7mo) |
|---|---|---|---|---|---|
| 1m cells positive | 90 % | **55 %** | 100 % | **55 %** | 80 % |
| 3m cells positive | 83 % | **61 %** | 89 % | 78 % | 94 % |

2023 is the weakest year for both timeframes, and 2025 is weak on 1-minute. 3-minute is better
year-balanced on four of five years, which is an additional reason to prefer it beyond its higher
average trade.

Slip-2 stress: the 3m plateau stays positive in every cell (net $33k–$198k), roughly half of slip-1.
The system survives a doubling of assumed slippage; it does not survive it comfortably.

## 6. Status and what this changes

| item | verdict |
|---|---|
| Wave-1c Tier-2 confirmation | **COMPLETE** |
| 16:30 timed exit dominance | **FALSIFIED** on full history |
| "46 % untaken signals = opportunity" (SW03 premise) | **FALSIFIED** (−$9.04/marginal trade) |
| H-011 stop-order execution | **REJECTED** (close ladder + intrabar fills desynchronise) |
| DR06-H4 neighbourhood > argmax selection | **CONFIRMED** |
| DR06-H5 iid understates tail risk | **REJECTED** |
| StopMultiplier selection | **not learnable** — PBO 0.63, negative IS→OOS slope |
| Plateau ensemble | **PROMOTED** — the new reference architecture (R4) |

Configurations consumed this wave: 80 (Wave-1c matrix) + 30 (H-011 three arms) = **110**;
campaign running total now **≈170**, which is the `n_trials` used in the DSR above.

## 7. Next

1. Re-run the ensemble construction on the H-006 adaptive family — the DC02 result says
   σ-normalisation stabilises the ratio the strategy monetises, and the ensemble is now the
   evaluation unit, so H-006 must be judged as *adaptive ensemble vs fixed ensemble*, not
   cell-vs-cell.
2. H-008 (High/Low anchor) inherits H-011's priority: it is the only route to the 89 % friction.
3. H-007 (split exit/reversal) — now the strongest remaining structural idea, and DR-03 gives it
   independent theoretical support.
4. Red-team pass on the ensemble result by an agent that did not produce it.
