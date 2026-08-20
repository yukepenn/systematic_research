# BREADTH02 — Cross-asset carry book (bond curve carry + equity dividend-yield carry)

**Status: FROZEN before any signal or return statistic is computed. Run class:
PROTECTED_CONFIRMATION (literature-sourced constants; author-chosen constants named and
counted). Campaign #5, spec #2. Governed by `../CONVENTIONS.md` (binding, frozen before this
spec).**

## 1. Hypothesis and mechanism

Carry — the return earned if prices do not change — predicts returns within asset classes
(Koijen, Moskowitz, Pedersen, Vrugt, JFE 2018: FI slope carry Sharpe 1.03, equity carry 0.91
per-class in their sample; diversified 1.20). Mechanism: compensation for exposure to funding/
duration/dividend risk that price-inelastic hedgers pay. This is a genuinely different
mechanism family from the closed BREADTH01 trend construction (price-history-free signals).
The campaign goal remains complementarity to the NQ book.

## 2. Power check (CONVENTIONS §1, written before any data read)

Two correlated sleeves on US-heavy instruments is far below Koijen's 9-class diversification.
Honest prior book Sharpe: 0.3-0.7 (midpoint 0.5). Primary economic gate = full-period
year-block CI_lo > 0 over ~24y: power ≈ 45% at Sharpe 0.3, ≈ 68% at 0.5, ≈ 88% at 0.7
(t = S·√24). At the prior midpoint this clears the ≥60% bar of CONVENTIONS §1 — barely; the
spec accepts one-shot closure on a possibly-true-but-underpowered effect as the price of
adjudication, exactly as recorded for BREADTH01.

## 3. Data (official/free; sha256 MANIFEST; analysis mask ≤2026-05-31)

- Treasury constant-maturity yield curve, daily, 2002-2026: home.treasury.gov
  `daily_treasury_yield_curve` yearly CSVs (columns 3 Mo … 30 Yr).
- 13-week bill (already held: `../BREADTH01_TSMOM_REPLICATION/data/_RF_TREAS13W.parquet`).
- ETF daily adj/close (already held, BREADTH01 MANIFEST): TLT IEF (bond sleeve);
  SPY QQQ IWM EFA EEM (equity sleeve). No new price downloads.

## 4. Construction (all constants named)

- **Bond sleeve (TLT, IEF)**: signal on the last trading day of each month =
  sign(y10 − y3m) (10-year constant-maturity minus 3-month, the literature's slope carry;
  no roll-down estimate — simplest form, zero fitted constants). Long the ETF if slope > 0,
  short if < 0. Author-chosen: using BOTH TLT and IEF as duration expressions of one signal
  (counted: they are one bet, sized half each).
- **Equity sleeve (SPY QQQ IWM EFA EEM)**: signal per ETF = trailing-252-trading-day realized
  dividend yield − trailing rf(13w, annualized), where realized div yield is computed
  deterministically from the adjusted/unadjusted return identity:
  divyield12m = Π(1+r_adj)/Π(1+r_px) − 1 over the window. Long if > 0, short if < 0.
- Sizing/execution/costs identical to BREADTH01 §3 (0.10/σ_i EWMA-60 vol scaling, 4× cap,
  t+1 month-start execution, 5 bps/side, 3× stress arm) — reused verbatim, zero new choices.
- Book = equal-weight mean of the 7 stream returns (bond streams half-weighted so the sleeve
  = 1 bet); ≥2 live streams required.

## 5. Gates (per CONVENTIONS §2 — the corrected era gate for diversified books)

- **G1** book history ≥ 18y; both sleeves live ≥ 15y.
- **G2 (primary)** book net annualized mean > 0 AND year-block bootstrap (B=10,000,
  seed=20260819) CI_lo > 0.
- **G3-ERA (CONVENTIONS §2)**: pre/post-2020 era means both > 0; first/second-half Sharpes
  same sign; neither era CI_hi < 0.
- **G5 complementarity**: vs the Solar concatenated ledger — ρ_full ≤ 0.25 AND ρ_losing ≤
  0.25 AND book return on Solar losing days ≥ 0. (Subject to the pending scale audit; if the
  audit finds a scale defect, G5 uses the era-wise-normalized Solar leg it prescribes.)
- **G6** 50/50 risk blend vs Solar alone: blend Sharpe higher AND blend CDaR5 (vol-units)
  ≤ 1.02×.
- **G7** 3× cost stress: G2 holds.
- Disclosure: per-sleeve Sharpes and correlation between sleeves; per-year; 2013 taper /
  2022 inversion behavior; correlation to the (closed) BREADTH01 book series.

## 6. Decision rule (frozen)

ALL pass → red team → if confirmed, BREADTH-CANDIDATE status (forward-monitored on stored
post-mask data; implementable-form spec separate; no deployment). G2/G3/G7 fail → carry
construction CLOSED one-shot (no re-skins: tenor/window/universe variants ineligible).
Only G5/G6 fail → REAL_NOT_COMPLEMENTARY; park.

## 7. Honest prior

Bond slope carry: strong literature but the 2022 inversion regime is the acid test (signal
flips short duration mid-2022). Equity D/P−rf: the weakest link — largely a rates-level bet,
negative-carry years 2003-2007/2023+ mean the sleeve shorts equities in bull markets;
plausibly nets ≈0 alone. Book prior 0.3-0.7. Prediction: G2 is a genuine coin-flip-to-60/40;
complementarity (ρ vs Solar) likely passes (carry signals are price-history-free). FAIL
closes the carry family honestly; PASS gives the owner a second complementary-book exhibit.
