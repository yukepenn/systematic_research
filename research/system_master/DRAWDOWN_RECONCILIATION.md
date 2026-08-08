# DRAWDOWN_RECONCILIATION — why PORT_TILT_532 shows −$27.2k and OneLot 1-NQ shows −$59k

_SMV2A audit, 2026-08-08. All seven objects rebuilt on ONE calendar (1,139 dev sessions
2022-01-03 → 2026-05-29), one DD algorithm (cummax − equity), EOD and bar-level.
Code: `runs/SMV2A_DD_RECONCILE/smv2a.py` (committed). Data: `runs/SMV2A_DD_RECONCILE/out/`._

## 1. Verification of the two contested numbers — both REAL, but NOT comparable

| object | net (dev) | ann vol | Sharpe | maxDD EOD | maxDD bar-level | avg gross (MNQ-eq) | time in mkt |
|---|---|---|---|---|---|---|---|
| A Solar E10 | $119,009 | $37.1k | 0.71 | **−$40,208** | −$41,628 | 2.73 | 81% |
| B Tilt-Solar | $130,534 | $37.5k | 0.77 | −$37,572 | −$39,067 | 2.77 | 81% |
| C Solar+BMOM day-only | $228,445 | $44.3k | 1.14 | −$33,297 | −$46,900 | 2.96 | 83% |
| D PORT_532 | $197,881 | $37.1k | 1.18 | −$28,678 | −$30,165 | 4.04 | 99% |
| E PORT_TILT_532 | $205,036 | $37.1k | 1.22 | **−$27,209** ✓ | −$30,042 | 4.05 | 99% |
| F OneLot 1 MNQ | $27,974 | $6.0k | 1.03 | **−$5,963** | −$6,391 | 0.38 | 38% |
| G OneLot 1 NQ | $296,885 | $60.0k | 1.09 | **−$58,517** ✓ | −$62,768 | 3.76 (RMS 6.13) | 38% |

- The **−$27.2k PORT_TILT_532 claim is confirmed** (−$27,209 EOD; −$30,042 if you mark
  every 3-min bar). PORT daily curves were re-derived from raw components and match the
  stored series with corr 1.000000.
- The **−$59k OneLot NQ claim is confirmed** (−$58,517 EOD / −$62,768 bar-level on the
  canonical replay).
- **CORRECTION (logged in KNOWN_ERRORS):** the original SM14 script was never committed.
  The committed spec-literal replay gives slightly different numbers than the SM14
  results table (MNQ net $27,974 vs $27,287; maxDD −$5,963 vs −$6,374; NQ $296,885 vs
  $298,040 — ≤2.5% deltas from ops-window micro-semantics). The committed replay is
  canonical from now on.

## 2. THE ANSWER: the difference is ~75% position size, ~25% lost diversification/grading

**PORT_TILT_532 runs $37.1k annualized vol. OneLot 1 NQ runs $60.0k — 1.62× the risk.**
The two DD numbers were never measured at the same risk. On the equal-volatility basis
(every curve scaled to Solar's $37.1k ann vol):

| object | maxDD at equal vol | vs native |
|---|---|---|
| E PORT_TILT_532 | **−$27.2k** | unchanged (already at that vol) |
| C Solar+BMOM day-only | −$27.9k | from −$33.3k |
| G OneLot 1 NQ | **−$36.2k** | from −$58.5k |
| F OneLot 1 MNQ | **−$36.8k** | from −$5.9k (!) |
| B Tilt-Solar | −$37.2k | |
| A Solar E10 | −$40.2k | |

Reading:
1. **~$22k of the $31k gap (E vs G native) is pure size.** Scale OneLot NQ down to
   portfolio vol and its DD is −$36.2k, not −$58.5k.
2. **The remaining ~$9k is the one-contract information loss**: no graded sizing, no
   fractional diversification. At matched risk the OneLot policy still beats raw Solar
   (−$36.2k vs −$40.2k) because the M-state embeds tilt + B-MOM, but it cannot match
   the fractional portfolio (−$27.2k).
3. **OneLot MNQ's famous "−$6.4k DD" is small because the position is small, not because
   the strategy is safer.** At matched risk it is −$36.8k — same animal as the NQ
   version (the tiny extra is MNQ's 3× commission drag). Never sell the MNQ number as
   risk engineering.

## 3. Decomposition ladder (all dev, EOD DD)

| step | net | ann vol | maxDD | Sharpe | isolates |
|---|---|---|---|---|---|
| L0 PORT_TILT_532 | $205.0k | $37.1k | −$27.2k | 1.22 | reference |
| L1 drop B1 (0.5T+0.3B, no renorm) | $182.8k | $35.4k | −$26.6k | 1.15 | **B1 does NOT reduce DD** (it adds return + adds back risk) |
| L2 full-size tilt-Solar | $130.5k | $37.5k | −$37.6k | 0.77 | diversification + fractional sizing worth ~$11k DD |
| L2b full-size untilted Solar | $119.0k | $37.1k | −$40.2k | 0.71 | tilt worth ~$2.6k DD |
| L3 sign(vote)×10 MNQ (no grading) | $132.6k | $73.0k | **−$97.1k** | 0.42 | **graded sizing is the single biggest DD control we own** |
| L4 OneLot MNQ ×10 | $279.7k | $60.1k | −$59.6k | 1.03 | hysteresis dead-band + B-MOM recover most of L3's damage |
| L5 OneLot 1 NQ | $296.9k | $60.0k | −$58.5k | 1.09 | NQ friction $17.2k cheaper than 10×MNQ over dev |

## 4. Component decomposition of the E−G gap (per §4 of the directive)

- **Size/notional effect:** −$22.3k of DD (equal-vol table). Dominant term.
- **Diversification + graded-size effect:** −$9.0k (36.2 → 27.2 at matched vol). Of
  this, grading (vote-proportional 0..10) is the larger part per L3; fractional B-MOM
  blending the rest.
- **B1 inclusion:** ≈ 0 for DD (−$0.6k, sign varies by basis). B1 is a return/Sharpe
  item, not a DD item. (Full ablation: SMV2C.)
- **Sign/hysteresis compression:** cost ≈ $9k equal-vol DD vs fractional portfolio, but
  GAIN ≈ $37k vs naive sign(vote) full-size — the dead-band (flat 62% of the time) is
  doing real work.
- **NQ vs MNQ commission:** $17.2k net over dev in favor of 1 NQ vs 10 MNQ ($4.36/RT
  vs $13.00/RT per 10-MNQ-equiv; slip identical at $5/tick-equiv). This is ~all of the
  MNQ Sharpe drag (1.03 vs 1.09) — answers directive §9.
- **Daily vs intraday DD definition:** adds 5-10% (E: −27.2 → −30.0; G: −58.5 → −62.8).
  C (day-only with B-MOM at 1.79× leg scale) is the outlier: −33.3k EOD but −46.9k
  bar-level — B-MOM rides large intraday excursions that EOD marking hides.
- **16:44 flatten / signal differences:** second-order here; both OneLot variants carry
  identical signals by construction.

## 5. Standing implications for the program

1. **Any DD target must name its risk basis.** "DD < $20k" is meaningless without vol.
   The correct objective going forward: minimize equal-vol DD (and CDaR/TUW) at fixed
   $37.1k ann vol reference, then choose the capital scale.
2. The one-contract frontier's theoretical floor is bounded by the fractional
   portfolio's equal-vol DD (−$27.2k at $37.1k vol). Better {−1,0,+1} policies (SMV2
   one-contract track) can close part of the $9k compression gap, not all of it.
3. B1's DD contribution ≈ 0 → its CORE membership rides entirely on the SMV2C ablation.
4. Graded sizing is the program's strongest DD technology. Anything that discretizes
   exposure (one-contract) pays for it in DD; anything that improves the grading signal
   is high-leverage.
5. Intraday (bar-level) DD reporting is now mandatory for candidates with intraday
   engines (C's 41% intraday excess).

_Approximations disclosed: tilt bar-level curve rebuilt at corr 0.9994 (state-definition
micro-diff vs SM08's stored daily; stored daily remains canonical). B1 intraday marked
as nightly steps (no intraday M2M for the overnight leg). B-MOM bar-level rebuilt exact
(1,333/1,333 trades, corr 1.000000)._
