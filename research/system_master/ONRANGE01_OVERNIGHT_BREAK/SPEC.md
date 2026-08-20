# ONRANGE01 — Overnight-range first-break continuation (owner-directed, 2026-08-20)

**Status: FROZEN before any post-break return/P&L statistic is computed (the 00_diagnostic
step measured break FREQUENCIES/timing only — committed alongside this spec). Run class:
BOUNDED_SELECTION. Alpha budget 1/2, wave 2026-08-20a. One shot.**

Owner direction 2026-08-20 ("现在用我们的数据测试一下这个claim … 并且看是否有交易策略赚钱")
reopens one OHLCV shot notwithstanding the 2026-08-19d pause (the pause's own terms: pending
new information or owner direction).

## 1. Established facts (diagnostic, no P&L)

P(RTH breaks ON high or low) = 96.2% over 5,183 days 2006-2026 (owner's ~95% claim TRUE);
first break median 09:41, 84% by 10:30; open inside ON range 99.7%; first side ≈ coin flip
(51.4/44.8). The probability is near-mechanical; profitability rests entirely on post-break
drift — untested here until this spec froze.

## 2. Strategy (frozen)

Universe: all RTH days with ≥60 ON bars and RTH open inside the ON range. Levels: ONH/ONL
from 18:00 (prev cal day) → 09:29. Substrate: `nq1m_2005_202605.parquet`, POINT space,
PV=$20, tick 0.25, commission $4.36/RT.

- **ARM_A (primary — the claim's direct monetization)**: OCO stop entries at ONH+1t (long) /
  ONL−1t (short); first 1-min bar whose high/low crosses a level triggers that side (if both
  levels cross within the same bar, skip the day; count disclosed). Entry fill = level ±2t
  (1t trigger offset + 1t slippage). Exit at the 15:58 bar close ∓1t. No intraday stop.
- **ARM_B (disclosure)**: as A, plus stop-loss at the opposite ON level (fill = level ∓2t on
  the first crossing bar); else 15:58 exit.
- **PLACEBO (mechanism falsification, required)**: as ARM_A but using the PREVIOUS valid
  day's ONH/ONL (stale levels). If stale levels earn statistically the same as fresh ones,
  the "overnight level" carries no specific information (any nearby trigger band would do).
- No other variant may be computed. Fade arms are ineligible (adjacent to the closed
  failed-break-fade family, seq 368-370 precedent).

## 3. Gates (ARM_A adjudicated; ALL AND-required)

- **G1** N_triggered ≥ 2,000.
- **G2** net > 0 AND iid bootstrap CI_lo > 0 AND year-block CI_lo > 0 (B=10,000,
  seed=20260820).
- **G3-SPLIT (standing per-event form)** pre/post-2020 means both > 0; ≥1 era CI_lo > 0;
  neither CI_hi < 0. Power note (CONVENTIONS-style honesty): per-trade σ ≈ $1,500-2,500;
  at N≈5,000 the full-sample gate detects ≥ ~$55/trade; costs are $14.36 — a real edge of
  the size worth trading is detectable; a sub-$50 edge will (correctly) fail.
- **G4** placebo: ARM_A mean > PLACEBO mean AND the paired daily difference (days where both
  triggered) has t_NW(lag 5) ≥ 2.
- **G7** concentration: top-1% of trades ≤ 50% of |net|; single best/worst ≤ 25%.
- **G8** vs Solar (`HTFDIR01/out/daily_ledgers_dev.csv` B_SYM): losing-day ρ ≤ 0.25; net on
  Solar losing days disclosed.
- **G9** cost stress 2t/side + 3× commission: G2 holds.
- Disclosure: by first-break side; by break time (≤10:30 vs after); per-year; ARM_B battery;
  both-levels-same-bar skip count.

## 4. Decision rule (frozen)

ALL pass → adversarial red team → if confirmed, engine-3-style candidate path (separately
preregistered confirmation; frozen baselines untouched). ANY fail → family CLOSED one-shot
(entry-offset/exit-time/level-window re-skins ineligible), and the OHLCV pause resumes.

## 5. Honest prior

For continuation: SMV2K's failed-break fade was SIGNIFICANTLY negative (t=−2.35) — swept
levels continue on modern NQ. Against: MOM01 (all-days intraday momentum) CLEAN_NULL;
hold-to-close long/short NQ is Solar-adjacent in character (G8 risk real); a 96%-mechanical
trigger means the entry carries almost no selection — the strategy is close to "buy the
first-hour direction, hold to close", which B-MOM-family evidence says is regime-local at
best. Prediction: gross positive, net after $14.36 marginal, G3-SPLIT and/or G8 the likely
killers. FAIL more likely than PASS; either way the owner's question gets a decisive,
preregistered answer.
