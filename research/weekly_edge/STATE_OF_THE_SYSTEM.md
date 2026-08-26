> Full component-by-component explanation with every parameter and its evidence:
> **`THE_STRATEGY.md`**

# STATE OF THE SYSTEM — WEEKLY_EDGE (campaign #7)

> ## 🚨 CURRENT TRUTH after W85 (2026-08-26) — CORRECTS THE BLOCK BELOW
>
> An independent 11-agent adversarial audit found, and I re-derived, three defects of mine.
> **Read these before ANY number further down.**
>
> ### 1. THE ROLLING GATE USED IN W78–W84 HAS NO POWER. FOUR VERDICTS REVERSE.
> Its drawdown leg was `top5 × DD_TARGET / maxdd` — a SHAPE RATIO sharing its denominator with
> the money leg. Oracle battery: **"P1 + $200 free money every session" scores ALL-THREE 0 %**
> while its raw max drawdown is better in 100 % of windows. Corrected leg (raw top-5 drawdown at
> matched nominal exposure) scores all four oracles at 100 %.
>
> | object | OLD ALL3 | **NEW ALL3** | |
> |---|---|---|---|
> | **W78 pair w=0.30** | 0 % | **84 %** | **PASS ← was FAIL** |
> | **W78 pair 2:1** | 0 % | **84 %** | **PASS ← was FAIL** |
> | **W79 clique equal** | 0 % | **68 %** | **PASS ← was FAIL** |
> | **W79 clique inverse-vol** | 0 % | **68 %** | **PASS ← was FAIL** |
> | X9a · Q1 · Q3 · Q4 | 0–24 % | 0–8 % | still FAIL |
>
> What the broken leg hid, at W82's measured $14.65/RT:
>
> | | wk+% | streak | wk$@fixed DD | RAW top-5 DD | RAW max DD | worst week |
> |---|---|---|---|---|---|---|
> | **P1 (champion)** | 52.6 % | 8 | **$853** | $18,458 | $27,328 | −$7,581 |
> | **pair w=0.30** | **58.7 %** | **4** | **$852** | **$12,188** | **$22,494** | **−$6,476** |
> | **clique inverse-vol** | **57.7 %** | **5** | $832 | **$9,489** | **$15,815** | **−$5,103** |
>
> **NOTHING IS PROMOTED ON THIS RE-SCORE** — a reversal caused by fixing my own error needs more
> scrutiny, not less. Both go to fresh champion-vs-challenger waves. W78's walk-forward failure
> (58 %, w=0.30 chosen 0/12) is independent of the gate but selected `w` on money alone, which is
> the wrong objective for the owner's stated ordering, and must be re-run.
>
> **RETRACTED UNCONDITIONALLY**: *"seven consecutive objects failed sub-period testing, always on
> the drawdown sub-metric"*. That was the instrument. (The enumeration was also wrong: W40, W41,
> W74 and W77 have no 24-month test at all.)
>
> ### 2. W76'S "NEVER-SEEN" WINDOW WAS NOT VIRGIN.
> `run_we_w01.py` docstring: *"holdout 2026-05-31 → 07-31, read once at the end"*, and
> `runs/WE_W01_SLEEVE_MAP/REPORT.md:38` names S4/SM14 *"the best object in the library"* **on
> holdout grounds**. `summary.csv`: vp460 and vp1380 **tie on dev Sharpe (0.160/0.160)** with
> vp1380 **ahead** on dev total ($303,386 vs $265,401), and separate **only** on the holdout
> (vp460 $79,524 / 77.8 % vs $64,746 / 66.7 %). **The campaign uses vp460 everywhere.**
> W76's "nothing was ever fitted, selected, screened or even LOOKED AT" and "P1's first genuine
> forward test" are **FALSE**. The −22.49 pts/session measurement stands; the label does not.
> 2026-05-31 → 07-31 is **BURNED**.
>
> ### 3. W74's "UNREACHABLE AT ρ ≥ 0.2 AT ANY K" IS FALSE.
> `run_we_w74b.py` ran K only to 24. Extended: ρ = 0.2 reaches **76.2 % at K = 60**, ceiling
> ~77.2 %. Correct: **≈6 at ρ = 0, ~9–10 at ρ = 0.1, ~60 at ρ = 0.2, unreachable at ρ ≥ 0.3**.
> Also: the census counted DAILY ρ while the K table is built on WEEKLY ρ — the short sleeve is
> weekly ρ **+0.158**, not −0.003. Every independence census must be recomputed on weekly ρ.
>
> ### Still standing after the audit
> every null (incl. W78's 98th-percentile drawdown specificity), every walk-forward, every
> per-year table, W82's fill cost, W80's deep-history run, W73's drift decomposition, W77's arms.


> ## ⚠️ CURRENT TRUTH after W72–W76 (2026-08-26) — supersedes everything below
>
> ### The campaign's problem is now a single number, and it is not a signal problem.
>
> `CAMPAIGN_STATE.md`'s binding target is **>76 % positive weeks / >$8,583 per week**. Measured
> against it:
>
> | | where we are | target | closable by contracts? |
> |---|---|---|---|
> | weekly $ **at his tail tolerance** (−$42,235 worst week) | **≈$8,398 net** at ~7.2 contracts | $8,583 **gross** | **already there** |
> | **positive-week rate** | **58.3 %** (2026: **68.2 %**) | 76 % | **never — it is scale-invariant** |
>
> **W74** (`FACT`, bootstrap from P1's own 204 empirical weeks, Gaussian copula, no
> distributional assumption): **76 % needs SIX genuinely independent streams at our quality; TEN
> at ρ = 0.1; and at ρ ≥ 0.2 it is unreachable at any K.**
> **W75** (census of 20 streams): ~~K_admissible = 2~~ **CORRECTED TO 1 by W79** (AXISB is 2025-only on the extended window), and the census used DAILY ρ where the K table uses WEEKLY ρ — see the W85 block at the top — stable
> at ρ < 0.15, 0.20 and 0.25. Only three streams in the whole repo are ρ<0.2 with P1, and two of
> them (SHORT, S_sig) fail the owner's 2025+2026 recency gate.
>
> > **We need six streams. We have two. The brief is now "find four more mechanisms", not
> > "find a better signal".** Decorrelation is a THRESHOLD, not a quality to maximise (W74 §5:
> > the short sleeve's consistency gain is GENERIC — it never reaches the 95th percentile of a
> > shuffle null that preserves both marginals and destroys only alignment).
>
> ### W72 — the OR slot: B-MOM is genuinely special, and the ANCHOR is the fragility
> Ten alternative occupants; **none reaches 90 % of production**, so the 51 % dependence is
> irreducible from outside as well as inside (W68). B-MOM beats its own session-shift null at the
> **100th percentile**. What it measures is now known: *price has travelled further from the
> 09:31 open than it typically does by this time of day*; the VWAP conjunction is worth ~12 % of
> production and has **no** durability (alone: pre-2022 t = −0.37).
> **The same rule anchored at the 18:00 session open is the ONLY durable channel of eleven**
> (pre-2022 t = 1.83 vs the incumbent's 0.93) and costs 28 % of production. Six anchor-combination
> arms; **0 of 22 rolling windows win on all three metrics.** Unfixable.
> **And all eleven gates are flat-or-negative pre-2022 and positive post-2022**, all sitting at
> the 85th–98th percentile of their own histories. **The fragility is a regime bet shared by the
> entire family — not diversifiable inside it.**
>
> ### W73 — the drift decomposition, first ever computed
> `net = drift + timing`. **P1: $300,817 = $33,365 drift + $267,452 timing (89 % timing).** We are
> not merely long a rising market. **SHORT sleeve: $121,454 = −$23,078 drift + $144,532 timing** —
> 54 % of the long side's skill, fighting a headwind. Per year the short's TIMING beat the long's
> in 2022 (+29,907 vs +27,458) and nearly tripled it in 2023 (+20,790 vs +7,387); it collapsed
> only in 2026 (−20,748, t = −1.55 on 22 weeks — not proven broken, but not delivering).
> H2 (mis-scaled σ) tested: signed-σ **hurts** the short side (4.79 vs 6.00 pts) and flattens the
> long side's year profile (2022 16.44 vs 11.59; 2023 6.90 vs 3.04) for 15 % less money at a fixed
> drawdown. Null still owed; nothing adopted.
>
> ### `CORRECTION`s recorded this session
> - **The substrate was silently truncated.** `load_deep` hardcoded a file ending **2026-05-29**
>   while every caller asked for 2026-07-31. **~46 sessions of 2026 have never been read by any
>   code.** Fixed with an opt-in `extend=` (overlap asserted bit-exact on all six columns);
>   W76 reads that window once, under a protocol written first.
> - **CLKRANGE and CLKVOL are contaminated and may not be quoted** — `we_clocks.size_for_rate()`
>   sets the range clock's bar size from a full-sample QUANTILE and the volume clock's from a
>   full-sample MEAN. They produced the two best 2026 figures in W75's census ($46,007 and
>   $60,833 vs P1's $33,467). Both void. Only CLK3/CLK5 are clean.
> - **The C1 stress line ($10/RT on top of commission) went unreported from W54 to W72.** No
>   published number is wrong — the fills have always charged commission only and the stress line
>   was always a separate column — but the column lapsed. Cost: **≈$95/week ≈ 6.4 %**
>   ($1,475 → $1,380). Both lines are quoted from W74 on.
> - **My W74 falsifier used the wrong statistic** (MAE, not R²) — third mis-specified stopping
>   rule of this campaign (W55, W57, W74). Every Cornish-Fisher number in W74 read 1 is withdrawn.
>
> ### The best object measured (`OBSERVATION`, not a promotion — no null yet)
> The 3-stream admissible clique **{AXISB, BMOM, w72:X9a}**, equal-weighted, mean pairwise
> |ρ| 0.069: **max drawdown $7,810 against P1's $20,245 (2.6× smaller)**, so at a matched
> drawdown **$2,346/week vs $1,475 (+59 %)**, median week $820 vs $455, weekly losing streak 6
> vs 8. Inverse-vol weighting: **61.8 % positive weeks, streak 4.** Queued for its own wave.
>
> ### Everything below this block is earlier truth, kept for the detail.

> ## ⚠️ CURRENT TRUTH after W67 (2026-08-26) — supersedes everything below
>
> ### THE OBJECT IS NOT WHAT THIS CAMPAIGN HAS BEEN CALLING IT.
>
> Every prior wave describes P1 as *"a selection-free majority vote over 32 long-only
> Solar-ratchet configurations"*. **W67 enumerated the combiner exactly and that description is
> wrong.** The six inherited constants collapse to one table — the members that must be net-long
> to enter:
>
> | tilt agrees | B-MOM | members needed | fraction |
> |---|---|---|---|
> | no | 0 | 6 of 13 | 46.2 % |
> | no | **+1** | **1 of 13** | **7.7 %** |
> | yes | 0 | 5 of 13 | 38.5 % |
> | yes | **+1** | **1 of 13** | **7.7 %** |
>
> **The object is a Solar ensemble OR-GATED WITH B-MOM.** B-MOM was long at 37.3 % of all
> entries; the median entry has only 5 of 13 members agreeing. The ±13 clamp is dead code, and
> four of the six constants cancel out of the decision entirely.
>
> ### `FACT`: B-MOM SUPPLIES 51 % OF THE OBJECT'S NET.
> Solar alone: **7.26 pts/session**. The object: **14.86**. Per year, B-MOM's contribution is
> +6.28 / −0.23 / **+13.93** / +12.22 / **+1.47** (2022→2026) — **collapsing**. The
> B-MOM-enabled share of net by year: 9.9 % / **82.4 %** / 17.3 % / 45.9 % / **−16.6 %**.
>
> ### And this repo has independently judged B-MOM regime-local, twice, without connecting it:
> the scalping lab parked it (PF **1.013** over the 16 unseen years 2006–2021); **W57** measured
> t = 0.27 pre-2022 against t = 2.66 after with no regime variable separating them; **W58** put
> its latest 24-month window at the **98th percentile of its own 234-window history**.
>
> **W57's conclusion therefore reads far more seriously than it did when written.** It said
> *"this repo holds no engine that diversifies P1"* — about a candidate. It is really about a
> component **we already depend on for half the net**, which is in-sample, at the top of its own
> historical range, and already negative in 2026.
>
> **This is a risk concentration to disclose, not a parameter to tune.** Measured alternatives:
> `w_bmom = 2.00` costs 10 % of production for a **25 % smaller mean top-5 drawdown, a 22 %
> smaller worst week** and a higher positive-week rate; `w_bmom = 0` is 7.26 pts/session, the
> honest floor if B-MOM's edge is a 4-year artifact. Neither is adopted.
>
> ### Everything else from W51–W66 stands as recorded below. Nothing has been adopted since W37.
>
> ## CURRENT TRUTH after W57 + CHARTER AMENDMENT 2 — superseded above, kept for the detail
>
> **THE OBJECT IS STILL P1 / P2, LONG-ONLY. W51–W57 adopted nothing.** Against the owner's
> ACTUAL objective (consistency, then drawdown — Sharpe is demoted to a diagnostic):
> **positive days 27.6 %, positive TRADED days 46.0 %, positive weeks 58.3 %**, median day ≈ 0,
> $1,475/week at a −$20,245 max drawdown, 14.86 pts/session per ~1.27 time-weighted contracts.
> **The 27.6 % positive-day rate is the campaign's weakest number against what the owner wants
> and no wave has ever attacked it.**
>
> **⚠️ TWO CLAIMS OF MINE ARE WITHDRAWN — see `OWNER_CHARTER_AMENDMENT_2.md`:**
> - **"IC is exhausted" / "the object cannot be improved from inside itself" — WITHDRAWN.**
>   What W55 supports: *sixteen features, each tested SINGLY, in five causal trailing-rank
>   buckets, against PER-TRADE per-unit P&L, did not exceed |ρ| = 0.11.* Multivariate
>   combinations, nonlinear learners, interactions, a session- or portfolio-level target,
>   features outside that set, other setups and other objects are all UNTESTED and open.
> - **W57's verdict — WITHDRAWN.** It gated on "does B-MOM work pre-2022?", and the owner's
>   criterion is **recent effectiveness is MANDATORY; old-era weakness is not disqualifying**.
>   W57's regime findings survive as attribution, not as a verdict.
>
> **WHAT STANDS as measurement:**
> - W56: a loosely-correlated *profitable* sleeve at w = 0.30 is worth **+43 % money at the same
>   $20,245 drawdown** with a slightly better drawdown distribution and a higher positive-week
>   rate. The number that makes it work is the **underwater-curve correlation** (B-MOM −0.171),
>   not the weekly ρ. This is the largest lever **measured so far**.
> - The only live objection to it is **statistical, not chronological**: 2022–2026 is B-MOM's own
>   development sample.
> - **W40 axis B is REOPENED**: its rejection cited "negative in 2024, flat in 2023", which the
>   corrected criterion voids, and its recent record is **+$1,946/wk in 2025 and +$846/wk in
>   2026** — a pass on the recency gate, not a fail.
>
> **ADOPTION CHRONOLOGY GATE (the only one): effective over roughly the trailing two years,
> reported with sessions/weeks/events and SE. Old-era weakness is not disqualifying. A regime
> explanation is valuable attribution, NOT a gate.**
>
> **New infrastructure**: `runs/WE_W56_BREADTH/out/p1_daily.csv` — P1's daily P&L series now
> exists on disk for the first time in 56 waves.
>
> **New binding method rules**: a weight scan may never be compared against an unscanned
> reference (W53 measured that best-of-21 inflates MAR ~20 % on structureless data); any scan
> over buckets/cells needs a permutation multiplicity check (W55, W57 — both of my own stopping
> rules were mis-specified without one and both were tightened before use).
>
> ## CURRENT TRUTH after W52 — superseded above, kept for the NinjaScript validation
>
> **THE OBJECT IS P1 / P2, LONG-ONLY.** Nothing else is adopted. The W41 clock basket adoption
> was **WITHDRAWN** on 2026-08-26 (see `runs/WE_W41_CLOCK2/amendment_2.yaml`): its range sleeve
> carried a FULL-SAMPLE quantile as its bar size — the 4th such casualty in this campaign.
>
> | | value |
> |---|---|
> | pts/session · weekly per ~**1.27 time-weighted contracts** | **14.72** · **$1,470** |
> | **annualised Sharpe** (weekly 0.311 × √52) | **2.25** |
> | max drawdown (weekly equity) · **MAR** | −$20,245 · **3.77** |
> | worst week · positive weeks · positive days | −$7,418 · 58.6 % · 27.6 % |
> | eff (weekly ÷ \|worst\|) — NEVER quote alone | 0.198 (P2 0.232) |
> | per year | 2022 $1,024/wk · **2023 $308/wk** · 2024 $1,951 · 2025 $2,265 · 2026 $1,521 |
>
> **NOW A VALIDATED NINJASCRIPT** (W52): `WeeklyEdgeP1_v3.cs`, confirmed through NT8's own
> Strategy Analyzer over the full window at **−0.64 % net, annualised Sharpe 2.24 vs 2.25,
> weekly series correlation 0.9752**, decision series 99.985 %.
>
> **WHAT IT CAPTURES** (W50): **+18.53 pts/session from the 20.9 % of days that TREND UP**
> (24.60 % capture there), minus 3.70 given back on the other 79 %. Being FLAT on TREND-DOWN and
> RANGE is worth **+4.36 pts/session** and needs no forecast except "do not be long today" —
> that is W51, preregistered.
>
> **"No look-ahead anywhere" is WITHDRAWN**: bar-level causality is clean, specification-level is
> not (W33 chose the five features on a full-sample scan). Bounded by W39's random-five-feature
> control (95th/97th) and W36's walk-forward on the same five (14.41).
>
> ## CURRENT TRUTH after W42 — superseded above, kept for the detail
>
> **Adopted since W39**: the **clock basket** (W41) — `long quality + 3-min clock + range clock`
> at w = 0.03 each, constant total exposure. eff 0.198 → **0.209**, CVaR-eff 0.272 → **0.282**,
> Sharpe 0.311 → **0.318**, worst week −$7,418 → **−$6,968**, for 0.7 % less money; better on
> eff in 4 of 5 years; every clock sleeve positive and stress-positive in **every** year.
> Binding count-matched null **95.0th percentile, p = 0.050 — it clears by nothing**.
> ⚠️ **Scale qualification**: w = 0.03 is 0.04 contracts. In tradeable integer form the basket
> improves both metrics only at **≥ 16 long : 1 : 1 (≈ $25,000/week)**; at 4 : 1 : 1 to
> 12 : 1 : 1 it improves Sharpe and CVaR-efficiency but worsens eff and the single worst week;
> below 4 : 1 : 1 there is no benefit. ⚠️ It is **sampling** diversification, not model
> diversification — every clock is the same Solar ratchet.
>
> **Closed since W38**: short-side quality (W38) · the short sleeve as tail insurance (W38) ·
> feature mining (W39) · four non-ratchet mechanisms (W40) · **exit engineering (W42)**.
> **Reopened and resolved**: W32's clock axis (W41 — its verdict was a harness artifact).
>
> **W42's payoff diagnostic, the campaign's first**: 37.8 % of trades win; the median trade
> gives back **more than its entire MFE**; winners keep only 41 % of theirs; winners' median
> MAE is **0.86 ATR**, which is *why* every stop fails here. The quality score forecasts
> **excursion size, not hit rate** (win % flat at 35–40 %, MFE 1.3 → 5.5 ATR across scores) —
> the mechanism behind sizing working and filtering failing.
>
> ## CURRENT TRUTH after W39 (2026-08-25) — superseded above, kept for the numbers
>
> **The recommended object is LONG-ONLY, scaled by contracts.** The short sleeve is no longer
> part of the production or risk-efficient object; it survives only as the CONSISTENCY object.
>
> | object | avg contracts | pts/session | weekly | wk + % | worst week | CVaR5 | Sharpe | **wk ÷ \|worst\|** |
> |---|---|---|---|---|---|---|---|---|
> | base vote + box | 1.00 | 10.62 | $1,060 | 59.1 % | −$7,487 | — | 0.305 | 0.142 |
> | **P1 causal quality sizing** | 1.18 | **14.72** | $1,470 | 58.6 % | −$7,418 | −$5,398 | 0.311 | 0.198 |
> | **P2 = P1 + causal 23-bar cut** | 1.11 | 13.50 | $1,347 | 56.7 % | **−$5,818** | — | 0.291 | **0.232** |
> | P1 scaled ×1.91 (same eff) | 2.26 | 28.13 | $2,807 | 58.6 % | −$14,170 | −$10,311 | 0.311 | 0.198 |
> | P1 + short sleeve (consistency object) | ~2.2 | 25.87 | $2,557 | **64.4 %** | −$14,606 | −$10,097 | **0.337** | 0.175 |
>
> **The quality layer is not leverage** (W39 amendment 2, the controls it had never faced):
> against 100 count-matched random-sizing draws it sits at the **97th percentile on
> pts/session (p = 0.030) and the 100th on profit-per-unit-of-tail (p = 0.000)**; against 100
> random five-feature scores of identical shape, the 95th and 97th. Decomposition:
> `base 10.62 → random sizing 12.03 (pure exposure) → random five features 12.62 →
> the incumbent five 14.72`; on eff `0.142 → 0.141 → 0.152 → 0.198`. **The specific features
> carry most of the genuine gain.** Sharpe is only *weak* against both controls (94th / 90th) —
> as W36 predicted, it penalises the upside variance the layer deliberately adds.
>
> **Feature mining is closed as a lever** (W39): 42 causal candidates, 8 classes; quarterly
> re-selection churns 62 % (top-5) or 80 % (t ≥ 2 admission) and every re-selection scheme
> loses to the fixed five; aggregating over all features loses too.
>
> **Distance to the owner's $10k/week**: at eff 0.198–0.232 that is ≈ 9 contracts and a worst
> week near −$43k. Reaching $10k/week at a −$15k worst week needs eff ≈ 0.67, i.e. **2.9× the
> current profit-per-unit-of-tail**. Contracts cannot deliver it; only diversification that
> lowers the tail can. That is why W40 (an independent second model) is the live wave.
>
> Stale below: the "sleeves + short vote = insurance" line in §1 (withdrawn, W38) and the
> "A3 17.78/0.338" and "A3 + S1 + short box" rows in §2 (A3 retired for threshold look-ahead).

## Original header — as of 2026-08-25 after 26 waves

Single reference. Everything here is measured, net of $4.36/RT, on NQ 1-minute bars,
out-of-sample within the modern regime (2022-07 → 2026-07, 205 weeks) unless stated.

## 1. What the system IS

**A selection-free, long-biased, volatility-regime-throttled Solar-ratchet trend harvester,
truncated in both directions at the session level.**

```
signal    32 Solar-ratchet configurations (4 member sets x 4 range-throttle settings
          x delta-gate on/off), LONG-ONLY, majority vote >= 50%, 1 contract
          -> no runtime parameter selection of any kind
context   range throttle: no new entry while the session's realised range through bar i-1
          is below 80% of its trailing-60-session time-of-day median   (W09, W13-audited)
          delta gate: 1-min up/down-tick cumulative delta must agree in sign  (weak, p=0.10)
risk      SESSION BOX: halt the sleeve at -$1,300 realised, stop it at +$1,000 realised
          (W22 + W26; both halves improve Sharpe AND the tail simultaneously)
sleeves   + S1 (CAND2 + D-gate, the 2023-derived wrapper, +-1)
          + short vote (same construction, mirrored) - insurance for hit-rate, not production
fills     decision at bar close, market at next bar open, flat at every session close
```

## 2. What it DELIVERS (measured, not projected)

| object | contracts | % days + | weekly | % weeks + | worst week | Sharpe |
|---|---|---|---|---|---|---|
| **P1 causal quality sizing (W37)** | ≤2, avg 1.18 | — | **$1,470** | 58.6 % | −$7,418 | **0.311** |
| **P2 = P1 + causal cut (best profit-per-tail)** | ≤2, avg 1.11 | — | $1,347 | 56.7 % | **−$5,818** | 0.291 |
| quarterly walk-forward of the layer (W36) | ≤2 | — | $1,545 | 59.3 % | −$7,418 | 0.303 |
| ~~A3 fixed (17.78 / 0.338)~~ | — | — | — | — | — | RETIRED: threshold look-ahead (W37) |
| **A3 + S1 + short box** | ≤4 | 51.8 % | **$3,737** | **64.9 %** | −$24,826 | 0.313 |
| (superseded) E5 box | 1 | 46.1 % | $1,060 | 59.1 % | −$7,487 | 0.305 |
| at his tail tolerance (−$42k) | ~2 of the pair | — | ~$4,900 | — | ≈ −$43,000 | same |

Per-year **with the session box** (W28 correction — the earlier "weak 2025 = 0.113" measured
the PRE-BOX object): 2022 0.102 · 2023 0.189 · 2024 0.376 · 2025 **0.311** · 2026 0.454 —
every year positive, and **per-trade expectancy rises monotonically $35.7 → $41.2 → $104.2 →
$160.9 → $207.4** (2026 is double his $103 gross; ~2.4× of the 5.8× is NQ's price level). The
weak year is **2022** — a bear year, structurally the worst case for a long-biased system.

## 3. What it is NOT

- **It is not a daily-profit machine.** 43–52 % of traded days are positive, the median day is
  near zero, **the best 5 % of days deliver >100 % of all profit**, and the longest losing
  streak is 9–17 trading days (W26).
- **It is not all-weather.** It earns in active-range sessions (16.8 % of sessions carry
  essentially all P&L) and stands aside in quiet ones. Three independent attempts to trade the
  quiet regime lost money (W11, W18 ×2).
- **It is not multi-model.** MODEL-RISK: every sleeve is the same Solar ratchet in different
  packaging. Non-Solar engines either lose (Donchian −0.34, genuinely orthogonal at 0.11) or
  are not orthogonal (EMA-cross 0.11–0.13 at corr 0.47–0.55). A decay of the ratchet takes
  everything at once (W25).
- **It is not multi-instrument.** The same engine loses on ES, RTY and YM (W11).
- **It is not proven outside 2022-2026.** On 2006-2021 the vote is +0.056 pooled, 8/16 positive
  years — positive but weak; the earlier fixed stack was −0.001 (W17, W21).

## 4. Versus the original trader

At **matched tail** (his displayed worst week −$42,235): ours ≈ **$4,923/week NET** across all
205 weeks against his **$8,583/week GROSS** across 21 curated, in-sample, version-churned
sheets. Efficiency per unit of tail: his 0.203 vs ours 0.117 — **1.74×**, not the 5–20× the
raw weekly figures suggest (W23).

## 4b. OUT-OF-SAMPLE VALIDATION (W29) — the quote is honest

Refitting **every free parameter** (halt, target, vote threshold, throttle q) quarterly on a
trailing year and trading only the next quarter:

| | walk-forward | fixed quote | naive | hindsight best |
|---|---|---|---|---|
| Sharpe | **0.290** | 0.300 | 0.214 | 0.304 |
| weekly | $1,034 | $1,042 | $1,114 | $1,045 |
| % weeks + | 60.3 % | 59.6 % | 60.1 % | 63.5 % |
| worst week | −$8,189 | −$7,797 | −$17,365 | −$7,257 |

**97 % of the fixed Sharpe survives an honest refit** (bar was 80 %), choice churn is 38 %
(against 88 % for the old select-one-config family), and `(1300, 1000, ·, ·)` is chosen in 15
of 17 refits. Walk-forward per-year: 0.353 / 0.062 / 0.410 / 0.248 / 0.490 — all positive.

## 5. Confidence, by evidence class

| claim | evidence |
|---|---|
| The vote beats selection and naive | out-of-sample walk-forward, W19/W20 |
| The vote is not noise | circular-shift null at the **98th percentile, p = 0.020** (W21) |
| Not a disguised selection | leave-one-subfamily-out spread 0.034 (W21) |
| Range throttle is real | own null at 95th pctile (W13) + blocked bars would have LOST $9,540 (W23) |
| Session HALT is real | own circular-shift null at the **98th percentile, p = 0.020** (W28) |
| Session TARGET | **weak, 88th percentile p = 0.120** (W27) — kept on its four-way improvement, never called proven |
| Vote hysteresis (0.6/0.4) | looked better on Sharpe and tail, **REJECTED at the 63rd percentile** (W28) |
| Mixed-model vote | **fails** — non-Solar voters cut Sharpe 0.305 → 0.23–0.24 (W27); model concentration is permanent |
| Long bias is real | replicated in four independent tests incl. the deep sample (W16/17/19/20) |
| Delta gate | weak (p = 0.10); kept on its leave-one-out cost, never described as understood |
| Everything else | see `PARKED_NOT_DEAD.md` |

## 6. Standing rules that produced these numbers
Gates carry decision-bar information only. Every gate reports its circular-shift percentile.
No runtime parameter selection. Any exposure rule that scales with a signal we already trade
is leverage, not edge (proved three times). Corrections propagate to every citing document.
