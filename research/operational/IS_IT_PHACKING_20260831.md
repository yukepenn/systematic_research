# IS THE EDGE REAL, OR IS IT SELECTION? — owner audit, 2026-08-31

Owner asked: *"explain the strategies in depth. WHY do they work, rather than being p-hacking?"*
Answered by an 8-agent audit with an explicit **prosecution** lane and two adversarial reviewers
pointed in **opposite** directions (one told to push the estimate down, one up). Load-bearing numbers
below were **recomputed by the orchestrator**, not taken from the agents.

**Verdict: it is not p-hacking, it is not proven, and the honest number is roughly half to
two-thirds of the backtest headline.**

---

## ⭐ 1. THE PIVOT NUMBER — I recomputed it and the synthesis was WRONG in the book's favour

The adjudicator's whole verdict rested on a multiplicity-deflation grid concluding that at the
measured spread *"the edge survives only if effective trials < ~100, and fails at the repo's own
stated count (p = 0.178 at K = 700)."* **That is arithmetically wrong twice over**, as the
"too-harsh" reviewer alleged and I confirmed:

1. It deflated **P1 alone**, not the **P1+XM book** the owner actually trades. Diversification
   raises t.
2. Even on P1 alone the arithmetic was off by ~3× (t 3.92 ⇒ p×700 = **0.062**, not 0.178).

**My own computation, from the two certified NT8 trade lists, weekly series on session date:**

| cost basis | n wk | mean/wk | **t** | p (2-sided) | **×700 (Bonferroni)** |
|---|---:|---:|---:|---:|---:|
| NT8 only (commission in) | 243 | $2,211 | **4.88** | 1.06e-06 | **0.00074** |
| + research spread (14.44 / 12.50) | 243 | $2,017 | 4.45 | 8.59e-06 | 0.00602 |
| **+ MEASURED $20.65 both legs** | 243 | **$1,929** | **4.26** | 2.05e-05 | **0.0143** |
| + hostile $28.69 both legs | 243 | $1,820 | 4.01 | 6.07e-05 | **0.0425** |
| frozen window, NT8 only | 218 | $2,514 | 5.29 | 1.23e-07 | 0.00009 |
| frozen window, + measured | 218 | $2,231 | 4.70 | 2.60e-06 | 0.00182 |

⇒ **The book clears a Bonferroni correction for 700 independent trials at EVERY cost basis tested**,
the worst cell being **p = 0.0425** with a hostile spread charged to both legs across the full record
*including* the un-warmed first quarter.

⚠️ **But do not over-read this, because the t-test is the wrong instrument here.** A t-statistic
assumes roughly normal weekly returns. This series is dominated by outliers — **22 of 213 weeks carry
78.9 % of P&L**, sd is $7,071 against a $2,211 mean. **The concentration objection is not answered by
the deflation; it survives it.** See §4.

## 2. WHAT THE STRATEGIES ACTUALLY ARE

**P1/PCT — long-only, intraday, flat every night, no stop.** 13 "ratchet" members trail the running
high; each releases when price retraces a distance set as a **multiple of recent volatility**
(6×…30× the mean |1-min change| over 460 bars, clamped 10–300 pts), so all 13 widen in fast markets
automatically. A member goes long **only on a fresh flip**, never re-entering until a new one. Four
nested groups × range filter × delta filter = 32 configurations collapsing to one integer rule:
`nMemberLong × nThrottlePass × (1+deltaGate) ≥ 16` — re-derived against the frozen Python with
**0 disagreements over 1,620,044 bars**. A per-contract session box stops the day at −$1,300/+$1,000.
Causal quality sizing scores 5 features against quantiles of the **last 250 prior entries** and buys
2 contracts on a majority.

**XM_CONFLICT — one question a day.** At 09:45 ET: *has NQ moved one way since the open while
ES, RTY and YM moved the other?* If yes, bet on **NQ's** direction, exit 15:45, one contract, no stop.
Each index is normalised by **its own** 60-session sigma before averaging, and today's observation is
appended **after** it is used. Stale feeds disqualify the session; half-days are declined. ~34 % of
sessions qualify ⇒ 378 trades in 4.7 years.

## 3. ⚠️ THERE IS NO ESTABLISHED MECHANISM FOR P1 — and that is the repo's own position

`CURRENT_BASELINE.md:58` classifies `P1/PCT` as **`CURRENT_REGIME_UNEXPLAINED`**. No story about
dealer hedging, stop cascades or liquidity provision exists anywhere in 435 run directories.

What *is* measured is **what the bet is**, and it is not what most would guess. Holding long because
the ratchet's leg is nominally up earns **0.0025 pts/bar**; holding because it has **just flipped**
earns **0.0603 — 24× more**. Extending the hold collapsed production 10.62 → 0.70 pts/session. A
Donchian breakout on the same instrument is **−0.34 Sharpe**. ⇒ **It is an event edge, not a state
edge**: the money is in the minutes right after a volatility-scaled reversal, not in the trend.

XM does have a testable story, and it delivers a number exactly: all of NQ's opening-momentum edge
lives in the third of days it **disagrees** with the complex (**$685/trade**) and none in the
two-thirds it agrees (**$34**) — and (664×34 + 341×685)/1,005 = **$255**, closing to the dollar.

## 4. WHAT IS GENUINELY ESTABLISHED

1. **The deployed code IS the tested code** — 0 of 2,439 P1 rows and 0 of 378 XM rows differ.
2. **P1's timing carries information.** Slide P1's exact exposure pattern onto every other possible
   day-offset (1,057 of them): the real result beats **all 1,057** (p = 0.0009). This kills
   *"it just made money because NQ went up."*
3. **It beats every trivial rule at matched risk** — 3.5× the best (opening-range breakout) and 8×
   buy-and-hold at a common $20,245 drawdown.
4. **The scary constants are cosmetic.** 0.7086 gives bit-identical output anywhere in [0.648, 0.729];
   0.9026 in [0.9000, 0.9167]. And `VolPeriod 460` sits on an **upward slope, not a peak** — 552 makes
   more money. **An optimiser would have moved it.**
5. **The signal core was inherited, not fitted here** — VolPeriod, the ladder, the clamp, TiltSma 50
   and the 3.0/1.0 levels appear verbatim in a prior **closed** campaign.
6. **The process kills its own favourites** — ~700 experiments, 2 survivors; a 44-trial re-hunt this
   month promoted **zero**; a $5,125/session star was killed over an int32 overflow that read 2.065 s
   into the future.
7. **Preregistration is a git fact** — 269 of 306 runs committed the spec in a strictly earlier commit,
   and **100 % of the runs supporting what is traded**.

## 5. WHAT IS SELECTION-CONTAMINATED

- **The discovery window IS the evaluation window**: 2022-07 → 2026-07-31, mined **123 waves /
  ~700 experiments, with no campaign-wise deflator ever applied** until §1 above.
- **Portfolio choice cost $245.71/wk (13.9 %)** — the selected {P1+XM} beat the *preregistered*
  {P1+PAIR+XM}. Measured and disclosed.
- **XM stacks three selection layers**: best of 27 cells, then 6 composite forms, then 6 blends.
- **The +39 % per-contract box is p = 0.058**, and 90.8 % of its gross difference lives in **53 of
  1,058 sessions**. On 2006-2021 it **reverses (−31.4 %)**.
- **The quality-sizing layer is the one genuinely fitted component**: 5 features from a 59-filter
  screen where 3.0 survivors were expected by chance and 7 appeared. Its own controls decompose the
  gain as ~34 % pure exposure, ~14 % rule shape with **random** features, ~51 % the specific five.

### ⚠️ 5a. A number in circulation that is WRONG — "87 % of the edge is quality sizing"

That conflates a P&L slice with a counterfactual. Because the session box is denominated **per
contract** (`:918-919`, `:1147-1148` — `sessPnl` has no `myQty` factor), forcing every size-2 trade to
size 1 leaves entry/exit timing **bit-identical** and exactly halves those trades. So: qty-2 trades
net $308,570; at size 1 they would net $154,285; an all-size-1 book nets $200,291. **The second
contract is worth $154,285 = 43.5 % of delivered net (a +77 % uplift), not 87 %.** Do not use the
87 % figure to argue for more size.

Also: **the score does not find likelier winners.** Win rate is flat at 35–40 % across every score
level; what changes is **excursion size** (MFE 1.30–1.51 ATR at score 0–1 vs 3.10–5.45 at score 3–4).
It doubles the bet on **magnitude**, not on being right — which is why *filtering* on it destroys the
strategy while *sizing* on it works.

## 6. ⚠️ RECLASSIFIED 2026-08-31 — this is a DOCUMENTATION error, **NOT a live defect**

> **CORRECTION.** This section originally reported a "live defect." A later audit checked the thing
> this one did not: the **Python research substrate**. `research/weekly_edge/src/we_quality.py:102`
> uses `2/3` for `delta_mag` — **identical to the C#**. So NT8 and the substrate **agree with each
> other**; the mismatch is the **spec TEXT versus BOTH implementations**.
>
> Consequences: the **tercile object is the only object that has ever been measured** — W34's own
> result, W35/36/37/39, the parity certification and the entire backtest headline are all tercile.
> There is **no divergence between the deployed code and the tested code**, which is what "live
> defect" would have meant. ⛔ **Do not change the code.** Fix the spec text to record what was
> actually built and tested.

### The original finding, retained for the record — spec says DECILE, both implementations use TERCILE

**Confirmed by the orchestrator, not just reported.** `runs/WE_W34_QUALITY/spec.yaml:22-23`
preregisters five features; four match the code exactly:

| feature | spec | `WeeklyEdgeP1PCT_v2.cs` | |
|---|---|---|:--:|
| F5 dist-from-open | top tercile | `:1127` `2.0/3.0` | ✅ |
| F11 prior-session return | **bottom** tercile | `:1128` `1.0/3.0` | ✅ |
| F14 run length | top decile | `:1129` `0.9` | ✅ |
| F4 dist-from-VWAP | top tercile | `:1130` `2.0/3.0` | ✅ |
| **F2 \|delta\|/volume** | **top DECILE** | `:1131` **`2.0/3.0` = tercile** | ❌ |

W33 scored the **decile** at the 96.0th percentile (*"EVIDENCE"*) and the **tercile** at 94.5
(*"weak"*). **The version that got built is the version that failed its own preregistered bar.**

⛔ **Do NOT hot-fix this on the live book.** The deployed object is parity-certified *as the tercile
version*; changing it de-certifies it and would be exactly the un-preregistered post-hoc edit this
project forbids. Correct handling: preregister a spec, test both arms on already-consumed data,
and treat any change as a new object requiring its own certification.

## 7. TWO CORRECTIONS **IN THE BOOK'S FAVOUR**

- **"The only unfitted data is negative" is substantially a WARM-UP ARTIFACT.** Splitting on each
  engine's *own declared minimum-history requirement*: P1 pre-window **under-warm** −$145.51/trade
  (126 trades) vs pre-window **warm +$216.99** (136 trades) vs in-window $155.17. **P1 earns MORE on
  unfitted, fully-warm 2022 data than in-sample — in the worst bear market of the record, on a
  long-only system.** Sweeping the cut date gives $117–$307 throughout.
- **Adding those unfitted weeks barely moves the headline**: frozen 213 wk $1,776/wk at fixed DD vs
  warm-fair 225 wk **$1,749** — under 2 %.

## 8. THE STRONGEST REASON TO DOUBT — concentration, not selection

- Top 10 % of P1's trades carry **236.8 %** of net; **the other 1,917 trades sum to −$456,493**.
- Top 22 of 213 weeks = **78.9 %**; one day (2025-04-09) = **11.1 %** of 4.5 years.
- Trade win rate **37.6 %**; only 292 of 638 traded sessions positive.
- XM is worse: top 20 of 378 trades = **94.0 %** of net.

**Why this is the fatal-flaw candidate:** it makes the book nearly unfalsifiable on any horizon you
will live through. The monitoring protocol's own power: **t = 1.03 at 60 sessions, 1.49 at 126,
2.10 at 252.** A *worthless* strategy passes the one-year invalidation threshold about half the time.
Combined with the doctrine that quiet quarters are expected and that old-regime failure is "a risk
classification, not a veto," **no realistic amount of bad forward performance triggers a stop.** Each
rule change was individually defensible; the pattern is not.

## 9. HONEST FORWARD EXPECTATION

| source | range | centre |
|---|---|---|
| adjudicator | $900 – $1,900/wk | $1,300–1,500 |
| reviewer pushing DOWN | $300 – $1,700/wk | $850–1,100 |
| reviewer pushing UP | $1,000 – $2,200/wk | $1,500–1,700 |
| **orchestrator, after recomputing §1** | **$900 – $1,900/wk** | **$1,300–1,600** |

P(true forward edge ≈ 0 after real friction): **10–30 %** (the reviewers split 10-15 % vs 30-35 %).

**⚠️ SIZE THE DRAWDOWN AT $45,000, NOT $21,740.** $45,138 is the full NT8 record; $28,201 is the warm
book; ~$21,700 is the research figure at a different cost basis. The gap between $45k and $28k is
**entirely the un-warmed quarter** — i.e. it is what a restart without `DaysToLoad=365` actually
produces. Every "dollars at fixed drawdown" headline divides by the smaller number.

**⚠️ POWER, which is a different number from edge:** even if the edge is entirely real at
$1,200–1,400/wk, there is a **~70 % chance the first two forward years do not produce a
statistically significant result**. 80 % power needs ~2.9 years at a true $1,600/wk and **~5.2 years
at $1,200/wk**. Plan for four to five years of forward evidence, not two.

## 10. WHAT WOULD SETTLE IT

The forward paper stream, and only it — every historical window is now consumed. Watch: whether the
quality score reproduces its ~$235/contract gap forward; whether XM's conflict decomposition holds;
whether ρ(P1, XM) stays at the 2026 level of **+0.425** (if it does, the book is one factor sized as
two); and whether the measured spread stays near June–July 2026's **$28.69/ctrRT**.

> **The one-sentence answer:** you own a carefully measured, null-tested, parity-certified regularity
> in the 2022-2026 NQ market, with a large and openly-accounted selection debt, **no known reason why
> it works**, and a payoff so concentrated that the next two years will be decided by whether three
> or four outlier days land inside them rather than by whether the edge is real.

---

⚠️ **Correction to an agent artifact:** the audit's verdict text says *"roll both legs by Friday
2026-09-04."* **That instruction was WITHDRAWN on 2026-08-30** — the roll fail-safe latches, and
re-enabling inside the block window kills the book permanently. Safe re-enable is **P1 ≥ 09-17,
XM ≥ 09-19**. See `NT8_OPERATING_MODEL.md` §0.
