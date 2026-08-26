> Full component-by-component explanation with every parameter and its evidence:
> **`THE_STRATEGY.md`**

# STATE OF THE SYSTEM — WEEKLY_EDGE (campaign #7)

> ## CURRENT TRUTH after W52 (2026-08-26) — supersedes everything below
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
