# FINAL_CAMPAIGN_BASELINE — written 2026-08-09, before any new hypothesis is tested

Written per the owner's FINAL OPTIMIZATION DIRECTIVE §0, before touching any new spec. This is a
reconciliation snapshot, not a new claim — every figure below is pulled from an existing committed
artifact and cited. Where two documents disagree, the more recent one governs and the conflict is
flagged explicitly rather than silently resolved.

**Authority chain.** `research/CAMPAIGN_STATE.md` declares itself CLOSED as of 2026-08-07 and
covers a *different, earlier* campaign (vendor reverse-engineering, CSCV/PBO, the original
Solar-only ensemble search). It contains zero references to SYSTEM_MASTER. `research/system_master/`
is a separate, later program (opened 2026-08-08) that consumes that closed campaign's outputs as
fixed inputs (the champion executable, the reverse-engineered indicator math) but is not governed by
its CLOSED status. **For everything below, `research/system_master/CURRENT_TRUTH.md` — specifically
its Wave-19 section, which supersedes Waves 17-18 below it — is the authoritative record.**
`SYSTEM_SCORECARD.md`, `CLAIM_LEDGER.md`, `SYSTEM_FRONTIER.yaml`, `NINJATRADER_MASTER_SPEC.md` and
`NINJATRADER_PARITY.md` are all **stale** (last updated Wave 4-8, before the C4 compliance fixes)
and must not be cited for current parameters or metrics.

---

## 1. Exact current Product A incumbent

**File**: `src/ninjascript/SolarWaveSMMaster_v3.cs`. Two-leg architecture (DAYONLY_DUAL6040 — the
"60/40" label refers to dollar-weight construction, not literal leg count of 2):

```
M   = round(KSolar·Tpp + KBmom·B), clamp ±13
Tpp = clamp(round(T·m·s·TiltRescale), ±13)
T   = clamp(round(10·mean(13 member pending pos)), ±10)          [Solar E10 leg]
m   = 1.25 (TiltMult) iff T≠0 and sign(T) == prior-session SMA50(session closes) state, else 1.0
s   = 0.5 (ShortHalf) iff T<0 and prior-session HTF state is UP  [c1_50 short-halving overlay]
B   = frozen W8-1 B-MOM position in {-1, 0, +1}
KSolar = 0.728654, KBmom = 2.934159, TiltRescale = 0.9026, TiltSma = 50, ShortHalf = 0.5
```

No B1 leg (demoted from CORE, P=0.737 < 0.9 gate). No third engine — Engine #3 search is 12/12
killed (§8 below).

**Status**: candidate/champion composition, **not a formally promoted final** — parity vs NT8 not
yet re-certified since the C4 fix, hence the file stays `_v3`, not `_Final` (V1-R4 open).

**Metrics, canonical dev window (2022-01-03 → 2026-05-29)**: net **$175,798.80**, 16,241 trades,
C4-compliant (0/39 breaches; cost of the compliance fix vs the pre-fix v2 object was **−$1,516.30**,
−0.86%, accepted). Sharpe/maxDD/CDaR were **not restated for v3** anywhere in the repo — the last
full metric battery (Sharpe 1.17, maxDD −$18,894, CDaR₀.₉₅ −$14,905) is on **v2**, pre-compliance-fix,
and must not be quoted as v3's number without restating.

**Objective-function status**: O1a daily objective is **INCONCLUSIVE** — +0.124 under the
equal-weight-mixture aggregation convention, −0.126 under Γ-minimax. The blind review (R3) confirmed
both conventions are mathematically admissible; per the binding fallback, an object whose verdict
flips across them may not be quoted as a single number.

**2026-stub behavior** (106 sessions, 2026-01-02 → dev end): Solar leg *inside* Product A is
**+$6,079 / Sharpe +0.456** — positive, not the same object as the plain E10 control. Of Product
A's ~$9k resilience edge over the plain control in that window, **+$7,243 is a fitted in-sample
constant (the c1_50 short-halving overlay)**, not diversification; **+$1,721** is the tilt.

## 2. Exact current BEST_ONE_NQ incumbent

**File**: `src/ninjascript/SolarWaveOneContractNQ_v4.cs`. SM14 hysteresis(3,1):

```
M  = WSolar·T' + WBmom·B         (WSolar = 0.7086, WBmom = 2.83)
T' = clamp(round(T·m·TiltRescale), ±13)
m  = 1.25 iff sign(vote) == prior-session HTF state, else 1.0
TiltSma = 50, TiltRescale = 0.9026, EntryLevel = 3.0, ExitLevel = 1.0
```
LONG 1 when flat and M ≥ EntryLevel; SHORT 1 when flat and M ≤ −EntryLevel; exit flat when M
retreats through ExitLevel. No pyramiding, no c1_50 term (unlike Product A).

**Status**: FINAL holder for the one-contract NQ slot, C4-compliant, not yet re-parity-certified
(V1-R4 open — the last PASSED parity run, 99.49% trade-exact / corr 0.9990 / net Δ 0.13%, was on the
now-superseded pre-C4-fix `_Final` object, not on `_v4`).

**Metrics**: net **$303,239.64**, 1,976 trades, 0/16 C4 breaches.

The **A-dominant policy** (B-MOM priority, Solar only at |T″| ≥ 5) remains a challenger only — its
confirmation gate failed (P ≈ 0.83 vs 0.85 required) — and must not be silently reintroduced as if
promoted.

## 3. Exact current BEST_ONE_MNQ incumbent

**File**: `src/ninjascript/SolarWaveOneContractMNQ_v4.cs`. **Parameters are byte-identical to
BEST_ONE_NQ's** (verified by direct diff — WSolar, WBmom, TiltSma, TiltMult, TiltRescale,
EntryLevel, ExitLevel all match exactly). Only the traded instrument (and its commission/tick
economics) differs.

**This is the exact condition the new directive rules out going forward** (§15: "Do not force NQ
and MNQ to use identical final parameters if genuine instrument-specific evidence supports
otherwise" / "never fill at NQ price × economic scale"). It is flagged here as an open item, not
silently carried forward as acceptable.

**Metrics**: net **$28,705.20**, same 1,976 trades (frozen-rule requirement), 0/1077 C4 breaches.

**Open data-quality gap**: the Python reference used for every MNQ number to date fills at
NQ-scaled prices, not genuine MNQU6 prints. A genuine-price reference run produced daily correlation
**0.8996** against the ≥0.999 parity bar (root cause undiagnosed; `GetBars` attempts for real MNQ
history returned empty). BEST_ONE_MNQ cannot be *separately optimized* on genuine economics until
this is resolved — Track E, does not block Track R for NQ-side research.

## 4. Executable filenames and compile/parity status

| object | path | C4 | NT8 parity vs current object |
|---|---|---|---|
| Product A | `src/ninjascript/SolarWaveSMMaster_v3.cs` | PASS 0/39 | **not certified** (V1-R4 open) |
| BEST_ONE_NQ | `src/ninjascript/SolarWaveOneContractNQ_v4.cs` | PASS 0/16 | **not certified** (V1-R4 open) |
| BEST_ONE_MNQ | `src/ninjascript/SolarWaveOneContractMNQ_v4.cs` | PASS 0/1077 | **not certified**, plus the genuine-price gap above |
| Product B one-lot (older, pre-C4) | `src/ninjascript/SolarWaveSMOneLot_v1.cs` | not C4-audited | PASSED 2026-08-08 on its own (pre-C4) basis |

## 5. Parity status

No current C4-compliant executable has a completed Strategy-Analyzer-vs-Python-twin
reconciliation. `NINJATRADER_PARITY.md` only has entries for the pre-C4-fix objects. This is Track
E and does not block the research families below, but no artifact from this campaign may be called
"final" or promoted to live-adjacent status until it closes.

## 6. Dev/evaluation windows (`research/system_master/CONVENTIONS.md`)

| window | range | role |
|---|---|---|
| CURRENT (dev) | 2022-01-01 → 2026-05-31 (last session 2026-05-29) | primary; all development/selection |
| JOINT-READ HOLDOUT | 2026-06-01 → 2026-07-31 | **CONSUMED** 2026-08-08 by `SM11_HOLDOUT_READ`; no pristine OOS remains through this date, for any sleeve |
| TRANSITION | 2018-01-01 → 2021-12-31 | diagnostic only, never selection |
| HISTORICAL | 2006-01-05 → 2017-12-31 | mechanism sign / failure-mode falsification only, never magnitude |
| VIRGIN | ≥ 2026-08-01 | untouchable except quarterly MONITOR-01 (next ≥2026-11-01) or annual frozen-champion read (≥2027-08-01) |

**D7 structural boundary** (market-variable changepoint, corrected for an off-by-19 index bug):
**2024-08-05** (CI 2024-07-11..2024-08-28) — but **weakly identified**: leave-one-variable-out
re-estimation moves it up to 545 days against a 49-day CI. Treat as a **candidate boundary only**,
never authoritative; primary splits should also use calendar years + the 2026-01-02 convention.
This is a *different* boundary from the 106-session 2026 P&L-concentration window (2026-01-02 →
dev end), which no market-variable changepoint procedure lands on even at corrected candidate-set
edges (though evaluated *at* that boundary rather than at argmax, 3 of 8 variables would detect a
shift).

**Regression finding (D7, survives red team)**: the 2026 stub is not a multivariate outlier (93.7th
percentile) and is not novel (named analog 2025-04-25..2025-09-19); a regression of the Solar leg's
daily P&L on the 7-variable market panel, fit 2022-2025, predicts the stub should have earned
+$172/session — it earned −$72/session. **The incumbent (not just challengers) is itself degraded
in the stub**: Solar leg Sharpe −0.387. In-period challenger comparisons are therefore low-power
against a degraded reference, not necessarily evidence of challenger fragility.

## 7. Cost assumptions (frozen)

| object | cost |
|---|---|
| Solar member (NQ) | $2.18/side ($4.36/RT), Lifetime commission, 1 tick/execution embedded |
| E10 executable (MNQ) | $0.65/side ($13.00/RT per 10-MNQ) |
| New minute-bar engine stress (NQ) | C1 = 2.872 ticks/RT primary; C2 = 4.872 ticks/RT stress |
| Directly measured slippage (W17-V4) | $9.72/RT NQ, $0.97/RT MNQ (1 tick adverse, empirical) |

B-MOM daily artifacts carry the C1 (2.872t/RT) stress friction rather than actual NQ commission
(0.872t) — every B-MOM number in the repo is friction-conservative by ~$10/trade.

## 8. Last registry sequence and recent rows

**Last sequence: 471** (`d7_red_team`, 2026-08-09). Rows 462-471: warmup convergence measurement;
Product A C4 propagation (463); M1 red team (464); M5 red team (465); stub-concentration standing
caution (466); O1 blind repair (467); seal audit standing check (468); D7 regime diagnostic (469);
O1 blind-review agreement (470); D7 red team (471).

## 9. Currently open or grandfathered research specs

- **`runs/W19R1_SELECTIVITY/`** — frozen (`d4926a4`), **never executed**, superseded same-day by the
  D7-first reprioritization. Content (arm_ER = ER150 causal selectivity score at constant exposure;
  arm_TOD = cross-instrument ES/RTY/YM time-of-day score; gate_0 exposure neutrality invalidation;
  gate_A legacy triple; gate_B chronology ≥4/5 years + 106-session-excision survival; gate_C
  cross-instrument for arm_ER only) carries forward unchanged. Per the new directive §5 S1, this
  spec is to be **run exactly as frozen**, with the D7-boundary split and low-power caveat added via
  a separate addendum rather than by rewriting it.
- **V1-R4** — NT8 re-parity for all three current objects. Track E, open.
- **`SolarWaveSMOneLot_v1` C4-fix propagation** — open.
- **V1g** — intraday-path capital map. Open since Wave 17.
- **V5** — MNQ bar-by-bar fill audit against genuine MNQU6 prices. Open, blocks BEST_ONE_MNQ
  separate optimization.
- **O2 retro-scoring** — unblocked on the aggregation question, conditional on reporting both
  {mixture, Γ-minimax} and treating flips as INCONCLUSIVE; four items the blind reviewer raised
  (chiefly: is the fixed fraction `f` optimised per candidate, a possible selection-bias channel)
  remain unanswered.
- **Wave-20 lead, proposed not run**: do M1 and M5 also break in the named 2025-04-25..2025-09-19
  analog — the only quasi-OOS check this program can construct.

## 10. Closed/rejected mechanism families — must NOT be rediscovered

- **Generic de-risking / cooldown / loss-triggered throttling / daily-cross-day loss stops /
  regime exposure scaling / arbitrary clamp widening** (as a *class*): repeatedly shown to move
  both tails together. SM02B loss-reactive cooldown is ANTI-EDGE (next-day expectancy is *higher*
  after a loss). Windfall give-back / profit-lock (4/4 variants) indistinguishable from random
  de-risking. VolMult clamp-ceiling raise (fixed and adaptive): buys Sharpe, always worsens CDaR.
- **Intraday time-of-day volatility seasonality applied to the Solar threshold (M1)**: CLOSED
  unconditionally across 3 constructions (multiplicative session-mean; exposure-neutral
  flip-normalized; per-bar S resampling). **This is a continuous re-scaling, not discrete
  eligibility — it does NOT close the SelTime/discrete-eligibility question**, which remains open
  (§11 below).
- **ATR/true-range blended with sigma460 ("ATR 75/25", SMV2AI/AJ, M5)**: CLOSED on two independent
  grounds — NQ Gate-A CDaR prong fails (0.753 < 0.85); cross-instrument replication also fails
  (new-instruments-only 0.8223/0.7108, no single new instrument clears 0.85 on either prong). Do
  not retune 0.75 or search nearby weights; "any future range idea needs a genuinely different
  construction targeting CDaR directly, not another estimator blend."
- **1-minute and 5-minute Solar clocks, volume-bar clock**: all CLOSED (friction, LOYO failure, or
  turnover regression).
- **T2/T3 signal layers / MA confirmation, same-day circuit breaker (SMV2AH), stop-loss/exit
  engineering as a class (STOP_OVERLAY_FRONTIER), FAST-cohort removal**: all CLOSED.
- **Engine #3 / complementary sleeves — 12 of 12 KILLED across 4 slates**: failed-range-break/sweep
  fade, small-gap fade, overnight drift (slate 1); VA-rotation, multi-day balance false-break,
  month-end flow (slate 2); shock-day continuation, post-FOMC/CPI drift, post-expiration
  gamma-unclamp breakout (slate 3); ES/NQ dispersion catch-up, duration-spread shock reaction,
  quarterly roll-basis convergence (cross-market slate). Unifying diagnosis: joint Solar/B-MOM loss
  weeks are correlated-regime whipsaw (vol-ratio asymmetry ≈1.04) — no re-timing/re-weighting of
  the *existing two* engines can fix that; a genuinely new *third* engine is the only lever, and
  none has passed since Wave 9.
- **Variance ratio / efficiency ratio as a next-session trend-quality gate**: 0/12 cells, killed.
  (ER150 as next-*week* downside predictor is a separate, still-valid diagnostic — it feeds arm_ER
  above, which is a selectivity construction, not the killed policy-conversion attempt.)
- **A-dominant / HTF-gated one-lot family**: confirmation-failed every attempt (0.83 vs 0.85),
  challenger status only, never promoted.
- **Raw High/Low anchor (H-008)**: this is **pre-SYSTEM_MASTER** (original campaign) evidence —
  REJECTED, Sharpe 0.527, "the ladder chases wicks." Close-confirmed variant passed standalone but
  was redundant with an existing rule. **M4 (§ below) is a new test and must not silently
  reproduce H-008's exact construction without acknowledging this prior result.**
- **Kalman innovation whiteness, BOCPD regime age**: no incremental information, closed.

## 11. What SelTime work has and has NOT been done

Confirmed: **no prior wave tested discrete session/time-eligibility as a hard gate.** M1 tested a
continuous multiplicative rescaling of the *volatility threshold* by time-of-day and was diagnosed
as an accidental exposure change; it does not touch trade-eligibility as a class. D4's cohort
finding (EVENING 26.0% of bars / −9.2% of P&L / net −$10,989) is descriptive only, never converted
into a tested policy. `arm_TOD` in the never-executed W19R1_SELECTIVITY spec is the closest
existing construction to a time-selectivity test and has not been run. **No repo artifact contains
a hard discrete "trade only during hours X–Y" rule test.** SelTime as a structural selection
problem is genuinely open.

## 12. Session structure (for S0's partition)

The frozen baseline trades the **full NT8 session (18:00 ET → 17:00 ET next day, ETH)**, not
RTH-only. The day-only overlay used in Product A / BEST_ONE_NQ / BEST_ONE_MNQ restricts *new
entries* starting 30 min before session close and forces flat 21 min before close (≈16:30/16:39 on
a normal 17:00 close) for the C4/margin requirement — it truncates the tail of the full session, it
is not an RTH-only design. RTH (09:00-16:59) is 34.6% of bars but 81.2% of P&L (D4).

## 13. ATR 75/25 — precise standing numbers (not misquoted)

Wave 13 screen: standalone Sharpe 0.746 vs 0.709 control; CDaR₀.₉₅ $25,183 vs $27,162 (better);
top-10-day retention 100.2%. Wave 14 confirmation: **Gate A prong 1 (P(ΔSharpe>0)) = 0.932 PASS;
prong 2 (P(ΔCDaR>0)) = 0.753 FAIL** against the 0.85 bar; Gates B/C/D/E all PASS. Wave 18
cross-instrument (red-team-corrected): new-instruments-only 0.8223/0.7108, both fail; no single new
instrument clears 0.85 on either prong. **Status: NQ-LOCAL / REGIME-SENSITIVE CANDIDATE, closed as
a direct-weight-search family, open only to the drawdown-complementarity re-framing in A1/A2/A3.**

## 14. M3 / M4 status

**Neither has been tested under SYSTEM_MASTER.** No spec, report, or registry row anywhere uses
"entry-S vs exit-S" or "high/low vs close anchor" as a SYSTEM_MASTER hypothesis label. Both are
genuinely open (M4 must be read against the pre-SYSTEM_MASTER H-008 result, §10 above, before
running).

## 15. Missed-winner / winner-giveback

Winner give-back (profit-lock after a win) was tested and killed as a policy (C-P7, indistinguishable
from random de-risking). **Missed-winner capture has never been tested** — named as an open
candidate since Wave 17, never run.

---

_This document is a snapshot, not a living record. State updates continue in `CURRENT_TRUTH.md`;
this file is not revised in place — a future baseline gets a new dated file._
