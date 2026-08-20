# BREADTH03 — Conditional volatility-risk-premium harvest (Simon-Campasano basis rule)

**Status: FROZEN before any signal/return statistic. Run class: PROTECTED_CONFIRMATION.
Campaign #5, spec #3 (third and last of the canonical style families: trend #1 closed,
carry #2 closed, this is VRP). Governed by `../CONVENTIONS.md`.**

## 1. Hypothesis

The VIX futures curve's contango pays a persistent premium to systematic short-vol
(Simon & Campasano, "The VIX Futures Basis: Evidence and Trading Strategies", JPM 2014;
Eraker-Wu 2017; Whaley 2013). Free-data expression: short the long-vol ETP (VIXY) only when
the term structure is in contango, flat otherwise. Mechanism: hedgers pay insurance premia;
the loser is the long-vol hedger, knowingly.

## 2. Power check (CONVENTIONS §1)

Sample: VIXY 2011-01 → 2026-05 mask ≈ 15.2y usable. Prior book Sharpe 0.6-0.9 (S-C's
pre-2013 numbers are far higher; post-2018 vol-market repricing discounts them; borrow drag
included). Primary gate (full-period year-block CI_lo>0): power ≈ 65% at Sharpe 0.6, ≈ 83%
at 0.75, ≈ 93% at 0.9. Clears the ≥60% bar across the whole prior range. ✓

## 3. Data (Yahoo daily, sha256 MANIFEST; analysis mask ≤2026-05-31)

VIXY (2011-01+, primary instrument), ^VIX and ^VIX3M (signal), SVXY (disclosure only —
leverage regime change 2018-02 makes it unusable as primary). Costs: 5 bps/side trading
+ **borrow 5%/yr on short notional** (named author constant; VIX-ETP hard-to-borrow range
documented 1-8%/yr); stress arm: 3× trading costs + 10%/yr borrow.

## 4. Construction (one rule, zero fitted constants)

- Signal on the last trading day of each month: contango ⇔ ^VIX3M close > ^VIX close.
  (Named deviation from S-C: they use front-future-minus-spot basis; the free-data analog
  is the 3-month-minus-spot index spread. Sign-equivalent in contango/backwardation terms.)
- Next month position (t+1 month-start execution, as BREADTH01/02): if contango, SHORT VIXY
  sized 0.10/σ (EWMA-60 ann vol), cap 4×; else FLAT. Monthly rebalance only.
- Book = the single stream (this is a one-asset book; it is a STYLE exhibit for the breadth
  decision, not a diversified book — disclosed).

## 5. Gates

- **G1** book history ≥ 15y (per this spec; one-asset style exhibit).
- **G2 (primary)** net ann mean > 0 AND year-block bootstrap CI_lo > 0 (B=10,000,
  seed=20260819).
- **G3-ERA (CONVENTIONS §2)** pre/post-2020 means both > 0; halves same sign; neither era
  CI_hi < 0.
- **G5** vs Solar concatenated ledger: ρ_full ≤ 0.25 AND ρ_losing ≤ 0.25 AND book return on
  Solar losing days ≥ 0 — required BOTH on the raw concat AND under era-wise Solar
  normalization (audit-prescribed robustness arm; disagreement = FAIL).
- **G6 (audit-hardened)** 50/50 risk blend vs Solar alone: blend Sharpe higher on the full
  overlap AND **dev-era (≥2022-01-01) blend CDaR5 (vol-units) ≤ 1.02× dev-era Solar-alone**
  (the BREADTH01 audit showed hist-era simulation can manufacture tail improvements — the
  modern-era prong is now binding).
- **G7** stress (3× trading + 10%/yr borrow): G2 holds.
- Disclosure: Feb-2018 and Mar-2020 episode P&L; % months in contango; per-year; skew/worst
  month; SVXY-long-expression comparison.

## 6. Decision rule (frozen)

ALL pass → red team → BREADTH-CANDIDATE status (forward-monitored; implementable-form spec
separate; no deployment). G2/G3/G7 fail → VRP family CLOSED one-shot on free data (threshold/
tenor/instrument re-skins ineligible). Only G5/G6 fail → REAL_NOT_COMPLEMENTARY; park.

## 7. Honest prior

The premium is real and documented, but this book's left tail is the program's worst-ever
(short-vol: Feb-2018 VIX +115% in a day). Vol-scaling at 0.10 target and monthly rebalance
tame size but not gap risk. The likeliest failure is G5/G6: VIX spikes co-occur with NQ
crash days, which sit inside Solar's losing set — ρ_losing may exceed 0.25, and the dev-era
CDaR prong is hard. Prediction: G2 more likely passes than not (60-80%); complementarity is
a genuine coin flip. Either way the style trilogy (trend/carry/VRP) is then fully adjudicated
on free data, and the owner's breadth decision is fully priced.
