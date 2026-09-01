> ⚠️ **Written 2026-08-31, one day before the book went live. Every capital and drawdown
> figure below is at 1 NQ + 1 NQ (FULL SIZE).** The live book runs at **0.30 scale** on a
> $10,206.86 account — multiply by 0.30 before comparing. See
> `research/operational/CURRENT_LIVE_TRUTH.md`. Body unaltered.

# WHY THE BOOK DRAWS DOWN, AND WHAT MAY LEGITIMATELY BE IMPROVED

Owner asked, 2026-08-31: *"why did the combined book have such large drawdowns — July this year and
other months? What can improve current live performance IN THE RIGHT WAY? Have we done this research
before? If not, do it properly."*

12-agent audit (5 diagnostic lanes → ranked candidates → 6 adversarial killers). **Load-bearing
numbers below were recomputed by the orchestrator.** Paper book. LIVE real money = NO.

> ## THE ANSWER: there is **no legitimate signal improvement available from existing data.** The
> ## correct action is to fix the plumbing, correct the risk accounting, keep both signals frozen,
> ## and let the forward record accumulate. **16 candidates were generated; after adversarial attack,
> ## 2 survived — and one of them is "do nothing".**

---

## 1. ⭐ THE DEEPEST DRAWDOWN IN THE RECORD IS AN ARTIFACT

| record | sessions | net | **max DD** | when |
|---|---:|---:|---:|---|
| full | 874 | $537,353 | **$51,891** | 2022-03-15 |
| **warm only** (from 2022-03-16) | 837 | **$581,091** | **$36,943** | **2026-07-29** |
| frozen discovery window | 791 | $548,112 | $36,943 | 2026-07-29 |

The $51,891 / 247-day-recovery drawdown is the **un-warmed backtest start**. Excluding those 37
sessions the book nets **$43,738 MORE** and max DD falls to $36,943.

⇒ **The true worst drawdown is July 2026.** And this is the second independent confirmation that a
cold start is worth ~$45k of drawdown — it is the deepest hole in the record.
⚠️ 🔴 **CORRECTED 2026-08-31 — the "$45,000" capital line written here is RETIRED. Plan $75,000–90,000.**
The Tier-2 wave measured **2-year p90 DD = $43,747 — 97 % of $45k** — and a single observed
margin-cliff event alone needs **$43,434**. $45k was the in-sample *sample maximum* on the most
optimistic cost basis; planning at a sample max is planning to be exhausted. *(What remains true is
the original point: a redeploy without `DaysToLoad = 365` reproduces roughly that drawdown — that is
an argument about the un-warmed hazard, not a capital plan.)*

## 2. JULY 2026 IS **FOUR DAYS**, AND THEY ARE FOUR JOINT-LOSS DAYS

| session | P1 | XM | combined |
|---|---:|---:|---:|
| 07-07 | −1,059 | **−5,694** | −6,754 |
| 07-17 | −1,722 | **−7,524** | −9,247 |
| 07-20 | −2,764 | **−6,229** | −8,993 |
| 07-29 | −2,388 | **−8,864** | −11,252 |
| **those four** | | | **−36,246** |
| the other 13 sessions | | | **+6,107** |

- **XM's July is 4 trades.** Those four lost $28,311; its other five made +$12,987. Worst single
  trade **−$8,864**. In the all-time worst-session table, **07-29 ranks #1, 07-17 #3, 07-20 #4.**
- **P1's July is a grind.** 38 trades, win rate **23.7 %** (vs 37.6 % historical), worst single trade
  only −$2,014.
- XM was **LONG on 6 of 9 July days** in a month NQ fell 9.0 % across the episode.

## 3. ⭐⭐ THE STRUCTURAL FINDING — the diversification was always a MIXTURE, and 2026 flipped the mix

**Orchestrator-computed, independently of the agents**, session-level correlation between P1's daily
P&L and XM's trade P&L on the 378 days XM traded:

| | n | **ρ** |
|---|---:|---:|
| all days XM traded | 378 | +0.204 |
| **XM went LONG** | 197 | **+0.408** |
| **XM went SHORT** | 181 | **−0.204** |

**XM's long share by year: 2022 62.0 % · 2023 57.7 % · 2024 42.5 % · 2025 45.5 % · 2026 63.3 %**

**This is an identity, not a mined regularity.** P1 is long-only. When XM goes long, both legs are the
**same trade in the same instrument** and the book is a levered long. When XM goes short, it genuinely
hedges. The advertised "ρ = +0.081, they diversify" is the **average of a +0.41 regime and a −0.20
regime** — and in 2026 the mix swung to 63 % long.

⇒ **That is why July's four worst days were joint.** It is not decay and it is not a broken signal;
it is a portfolio that is risk-budgeted as two streams while behaving, roughly two-thirds of the
time, as 2× one factor.

Scale-free confirmation: `sd(P1+XM) / (sd P1 + sd XM)` went **0.656 → 0.863** against an independence
benchmark of ~0.708. **The book used to be better than two independent streams and is now 1.22×
worse.** Before 2026 the deep drawdowns were single-leg (2025-02→04 was P1's $22,223 while XM made
+$4,094); **both 2026 episodes are joint.**

⛔ **This is not fixable by a filter and not fixable by re-weighting on consumed data.** It is exactly
what the preregistered correlation tripwire (frozen 2026-08-30, one day before the question) exists
to adjudicate — **on forward data only, earliest read ~2027-03-01.**

## 4. OTHER DIAGNOSTIC FACTS WORTH KEEPING

- **Being in drawdown is this book's normal state**: 677 of 873 traded sessions (77.5 %) sit below the
  running equity peak; 114 separate episodes; only 47.4 % of sessions positive.
- **The two legs fail differently.** P1 supplies the frequent shallow drawdowns (larger contributor in
  75 of 114 episodes) — it is long-only and its *entire* net comes from TREND-UP sessions
  (+$488,922); RANGE −$44,186, REVERSAL −$31,172, TREND-DOWN −$96,547. **XM supplies the deep ones**:
  13.4 % of trades, present in **10 of the 10 worst sessions in history**. 17 XM trades lose >$5,000
  against **zero** P1 trades.
- ⚠️ **CORRECTION to something stated earlier in this session:** P1's session box is **not a stop**.
  It is a re-entry lockout evaluated only when a trade **settles** (`:918-923`), so it can never bind
  while a position is open. P1's smaller tail comes from **short holds**, not from a bound.
- **Volatility does not make the book lose — it doubles the swing both ways.** P&L per session by vol
  quintile is flat ($562/$878/$481/$621/$492) while the worst session goes −$4,993 → −$11,252.
  This is why "stand aside when it gets wild" is the wrong lesson (see §5, W77).
- **The only risk denominator has silently tightened ~1.8× (⚠️ CORRECTED: the 43.4/24.6 bp figures were computed on a BACK-ADJUSTED price series, so they are NOT index basis points. The direction is right and on true index levels the drift is LARGER, not smaller.)** P1's fixed $1,300 box was **43.4 bp** of
  index in 2022 and is **24.6 bp** now; it binds on **80.7 %** of traded sessions vs 50.0 % in 2023 —
  and not from churn (trades/session fell 3.68 → 2.50). Nobody chose that.
- **The book has not decayed**: adverse excursions widened in points (p90 181 → 380) but are flat in
  basis points (121 → 128 bp) because NQ roughly doubled.

## 5. YES, WE HAVE DONE THIS RESEARCH — AND IT FAILED, EXPENSIVELY

| proposal | verdict | cost of having adopted it |
|---|---|---|
| **W77 volatility/regime stand-aside** | REFUSED | **−$555/wk at fixed DD (−37.6 %, ≈−$101,807)** — and its held-out window **IS Jun–Jul 2026**, which it turns from −$20,061 to **+$15,785**. It erases exactly the month being asked about. Its Phase-0 falsifier had already fired: P1's net **rises monotonically across all ten range deciles**. |
| W113 regime/state veto | REFUSED | −$125,844, and max DD **rises in every cell** |
| W121 turnover cap | REFUSED | −$55k, and sits at the **0.0–4.0th percentile** of a count-matched random-halt placebo — **removing the same trades at random does better** |
| Day circuit breakers | REFUSED | **0 for 16** against their own placebo |
| W102 stops on XM (11 distances, 20–300 pts) | REFUSED | all worse; 3 preregistered arms made the portfolio **21–36 % worse** at fixed DD |
| Six frozen objects vs the book's losing weeks | **zero survivors** | incl. ALWAYS_SHORT at −$23 |

> **Finding a filter that would have avoided July is trivially easy and worth less than nothing.**
> The track record of exposure-reducing rules against their own random controls in this repo is
> **nine for nine in the wrong direction.**

## 6. THE CANDIDATE LIST AFTER ADVERSARIAL ATTACK

16 generated, 6 attacked, **2 survived**:

| | candidate | outcome |
|---|---|---|
| ✅ | **Do nothing to either signal; let the forward record accumulate** | **SURVIVES — and is the answer** |
| ✅ | **Arm P1's `ExpectInstrument`** (currently `""` = guard disabled) | **SURVIVES.** Free, deploy-time input, no code change. XM's equivalent guard has already caught a real mismatch. |
| ❌ | Fix the roll-block latch (claimed 12.9 % of the year) | **KILLED on arithmetic.** The window is created by `RollLeadDays = 8`, **not by the latch**; a re-resolving guard recovers only **~1 trading day per quarter** ≈ 1.65 % of the year, not 12.9 %. The claim and its own guardrail ("do not tune the lead days") are mutually inconsistent — the lead days *are* the window. |
| ❌ | Disaster stops at zero-trigger levels | **KILLED.** (a) It buys **no bound**: there is no resting order anywhere — it detects at bar close and exits **market at the next bar's open**, so fill distance is unbounded exactly in the fast move it is bought for, a stalled feed disarms it, and **it dies with the strategy** — which is the dominant unsampled tail. (b) It **already failed a preregistered gate two days ago** (`G2_F1_MAE01_20260829`: clause 2 FAIL, "RECORD AND STOP"), and a level chosen to fire zero times **cannot pass clause 2 at any level, analytically**. |
| ❌ | Harvest `FILLPX` lines / correct the risk accounting | killed as *proposals*; the underlying **measurements and corrections stand** and are folded into §7 |
| ❌ | Re-weight to 2:1 · any July-avoiding filter · portfolio daily loss limit · demote XM | **REFUSED** — selection, or already 0-for-16, or (for demoting XM) sits at only the **17.8th percentile** of a count-matched random-removal control. ⚠️ On the **warm-up-contaminated** series the same test returns the 99.2nd percentile — **the un-warmed prefix alone would manufacture a "demote XM" verdict out of nothing.** |

## 7. WHAT TO ACTUALLY DO

**Signals: change nothing. Both legs stay exactly as certified.**

**Now (free, no fitting, no code):**
1. Set P1's `ExpectInstrument` — `"NQ 09-26"` now, `"NQ 12-26"` at the roll.
2. Start harvesting the `FILLPX assumed=/actual=` lines the strategies already emit — the only clean
   read on whether the Jun–Jul 2026 **$28.69/ctrRT** spread regime persisted.
3. Add a **>10-second feed-loss alarm**. With `ConnectionLossHandling = Recalculate` a long loss
   silently stops and re-warms the strategy while the grid still reads Enabled/Realtime — and every
   stop here is synthetic, so an open position would be unmanaged throughout.

**Accounting corrections (cost nothing, prevent over-sizing):**
4. **Retire "$11,489 max DD / adding XM roughly halves drawdown"** for the deployed book. That was
   **SIZE, not diversification** — inverse-vol B holds 1.0 contract gross against the 1:1 book's 2.0,
   and gross-matched the drawdowns are indistinguishable ($22,979 vs $22,246). Exactly the "reduced
   risk denominator masquerading as information alpha" the method forbids. *(The scale-invariant
   fixed-DD claim $1,230 → $2,012/wk is unaffected and stays quotable.)*
5. Budget drawdown near the **sum of the legs (~$39,500)**, size capital at **$75,000-90,000** ⚠️ (CORRECTED 2026-08-31: the $45,000 line is RETIRED - 2yr p90 DD is $43,747 = 97% of it, and one measured margin-cliff event alone needs $43,434) — not the
   mapping table's $21,740, whose window structurally **excludes** the book's worst drawdown.

**The roll (6 days away, highest-risk item on the calendar):**
6. ⛔ **Do not roll early.** ~~Safe re-enable **P1 ≥ 2026-09-17, XM ≥ 2026-09-19**, on NQ 12-26 with
   all four XM series moved together~~ and `DaysToLoad = 365`.
   🔴 **CORRECTED 2026-09-01 (text above preserved as written):** **both legs ≥ 2026-09-19** (practically Mon 2026-09-21) — P1's MNQ series rolls **09-18**, two days after NQ's, and the LIVE book
   has **five** series, not four. Authority: `research/operational/CURRENT_LIVE_TRUTH.md` §ROLL. Record the ~10-day new-entry gap in the
   shadow ledger so it is never read as a signal drought.

**Research — preregister exactly two, and neither can be alpha:**
7. **σ-scaled session-box specification test on 2006–2021**, falsifier = regime **INVARIANCE**, not
   profit. Motivated by the 1.8× silent tightening in §4. W98 already answered the *money* question
   (a uniformly looser box is worth **+$6/wk, p = 0.940**); this is the *specification* question,
   which is different and unasked.
8. **Audit XM's spread** — never measured. P1's audit found the model optimistic ($20.65 vs $14.44).

**Then wait.** First legitimate read of the XM correlation tripwire is **~2027-03-01**.

## 8. THE HONEST FRAME

At a true $1,200–1,600/wk there is a **~70 % chance the first two forward years produce no
statistically significant result**; 80 % power needs ~2.9 years at $1,600/wk and **~5.2 years at
$1,200/wk**. ⚠️ And mark the forward expectation **down ~13 %** for as long as the roll guard stays as
coded — the headline was computed on an object that traded the roll weeks.

> July 2026 was a concentrated payoff landing the wrong way, **plus a hedge that had quietly stopped
> hedging**. The right response is to fix the plumbing, correct the accounting, keep the signals
> frozen, and let the forward record accumulate. That is a real answer, not a refusal to give one.
