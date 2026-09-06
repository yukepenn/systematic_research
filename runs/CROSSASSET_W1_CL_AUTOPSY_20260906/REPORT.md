# CL MARKET AUTOPSY -- WTI crude oil (NYMEX), Cross-Asset Wave 1

**Run:** `runs/CROSSASSET_W1_CL_AUTOPSY_20260906/`
**Date:** 2026-09-06 - **Lane:** B (native market discovery) - **Protocol:** `NQ_RESEARCH_PLAYBOOK.md` sec.9 + transfer-checklist step 6
**Evidence status:** `DISCOVERY_CONSUMED`.
**This is DESCRIPTIVE SCIENCE, not a falsifiable test** -- no ledger trial, no strategy, no P&L, no promotion. Every number is a phenotype measurement. Nothing here touches the live book `2047681`.

---

## 0. Freeze / boundary assertion (printed by the program)

CL is the one genuinely untouched intraday futures market in the repo, so its OOS layer is protected (`runs/CL_HOLDOUT_FREEZE_20260906/SPEC.md`). The loader **hard-drops every session after 2025-06-30 and asserts it** -- verbatim console line:

```
[CL] FREEZE ok. raw rows=1,608,018 raw_last=2026-07-31 16:59:00
     dropped(sess>2025-06-30)=379,593 retained=1,228,425
[CL] retained sessions 2022-01-03 .. 2025-06-30  n=901
assert df["sess"].max() <= 2025-06-30   -> PASS
```

- **Discovery window read:** 2022-01-03 -> **2025-06-30** (901 sessions; 894 full pit sessions >=250 bars).
- **Frozen holdout (2025-07-01 -> 2026-07-31) and global virgin (>=2026-08-01): NOT read.** NQ was restricted to the same <=2025-06-30 window for the correlation.
- **Points basis only** (DELEV01 law -- the substrate is additively back-adjusted, absolute levels are shifted; every figure below is a POINT difference, never % of price, never a level threshold). **CL point value = $1,000/pt** ($10/tick, tick $0.01), so a "point" is a $1 oil move and 1-min magnitudes are small by construction.

---

## 1. Native session (determined from CL's own volume, NOT assumed)

CL trades the CME energy container **18:00 ET -> 17:00 ET** next day (maintenance halt 17:00-18:00; bar-count in the halt = 0). Its liquidity profile is unambiguous:

| feature | evidence | ET |
|---|---|---|
| **Pit / US day session (RTH-equivalent)** | 59.0% of daily volume in 5.5h | **[09:00, 14:30]** |
| **Pit open** | volume steps 0.16% -> 0.56% at the 09:01 bar (opens 09:00), 100% coverage | **09:00** |
| **Settlement** | peak single clock-minute 14:30 (1.07%), 14:29 (1.06%), 98% coverage | **14:30** |
| **EIA release spike** | 10:31 bar elevated (0.36%); Wed 10:30 volume 2.2x non-Wed | **Wed 10:30** |
| **European overlap** | 03:00-08:00 ET carries 18.2% of volume | 03:00-08:00 |

**Adopted partition:** PIT = `[09:01, 14:30]` end-stamps (open @09:00, settle @14:30); overnight/inter-pit = prev-settle->next-open. **This is NOT NQ's 09:30-16:00.** Two structural differences drive everything below: (1) CL's day session ends at a **hard 14:30 settlement** that concentrates physical-hedger flow; (2) CL's **overnight is genuinely liquid** (overnight range is 86% of pit range, vs near-dead for equity indices).

---

## 2. rho-to-NQ -- the diversification pre-read (the portfolio point)

Point-return correlation on 867 shared discovery sessions (correlation is scale-free; PV irrelevant):

| basis | rho |
|---|---|
| daily FULL (CL prev-settle->settle vs NQ prev-close->close) | **+0.049** |
| intraday session (CL pit vs NQ RTH) | +0.065 |
| Spearman (full) | +0.036 |

Per-year: 2022 +0.003, 2023 -0.009, 2024 +0.051, **2025 +0.274**. **Near-zero equity correlation is the prize** -- a CL engine expresses a different (energy/physical) factor and is close to orthogonal to the live NQ book. WARNING **Caveat:** the correlation is itself regime-dependent and *rose to +0.274 in the last 122 discovery sessions* (macro risk-coupling); a portfolio claim must be re-checked on the holdout, not assumed flat.

---

## 3. The three load-bearing descriptive facts

### FACT 1 -- CL's tradeable structure lives in VOLATILITY, not in returns.
- Returns are a **near-perfect random walk inside the pit**: 1-min return acf ~ 0 at every lag, variance ratio VR(2..60) = 0.997-1.010, sign persistence 48.9% (50% = none). Path efficiency is **very low** (Kaufman ER median 0.052, mean 0.061; tortuosity median 19.2) -- pit paths are choppy, not directional.
- Multi-day returns **mean-revert**: daily VR(10) = 0.838, daily sign persistence 46.7%, daily acf(5) = -0.078; E[PIT ret | prior PIT up] = -0.177 (reversal).
- **Volatility is strongly, long-memory persistent**: |1-min ret| acf = +0.287 (lag 1) still +0.204 at lag 330 (a whole session later); daily RV acf = +0.821 (lag 1), +0.560 (lag 10); pit-range acf(1) = +0.580.
- 1-min returns are **extremely fat-tailed** (excess kurtosis **61.5**), and daily returns are **negatively skewed** (pit -0.81, full-day -0.65 -- down-moves bigger than up-moves).
> Implication: price-trend / momentum-in-price families are unpromising here; **vol / range / event-timing** mechanisms are where the exploitable structure is.

### FACT 2 -- The EIA Wednesday 10:30 ET release is a clean, powered, scheduled VOLATILITY shock -- but carries NO directional edge.
- Release bar (10:30->10:31) mean |move| = **0.208pt on EIA-Wednesdays vs 0.068pt otherwise -> 3.08x**; the 10:29->10:30 bar is *not* elevated (0.98x), pinning the shock precisely at the 10:30 print.
- RV(10:30-11:00) = **0.572pt Wed vs 0.401 non-Wed -> 1.43x expansion, Welch t = +7.97** (decisively powered). Wednesday also has the highest daily pit dispersion (pit_std 1.67 vs ~1.4-1.6 other days).
- **Direction does NOT persist:** release-bar sign -> rest-of-window continuation P = 50.0%; -> rest-of-pit P = 51.1%; projected drift +0.013pt (noise). EIA is a **vol event, not a directional event.**
> This dovetails with the banked `G2_F12` fact (FOMC vol *expands* x5.66, the textbook "crush" is backwards): scheduled macro releases in this book expand realized vol. A "sell vol into the release" framing is pre-falsified.

### FACT 3 -- CL is severely regime-dependent in volatility, with heavy left-tail (physical-shock) risk -- the binding risk constraint.
- Daily pit RV collapsed monotonically: **2022 = 1.94 -> 2023 = 1.17 -> 2024 = 0.95 -> 2025 = 0.93**. The 2022 Russia-Ukraine oil shock year had ~2x the vol of 2024.
- Big-range-day frequency (>90th-pct pit range = 3.58pt): **2022 = 30.2% of days, 2024 = 0.4%**. Worst single pit day -8.72pt (2022); max pit range 15.9pt (2022).
- Jump character: the largest 1% of 1-min bars carry **17%-33%** of daily pit variance (33% in 2025) -- a strongly jump-driven, shock-punctuated market.
> Implication: any CL candidate must be **re-measured per-year** and shown robust across the 2022 shock regime and the 2024 calm regime; a pooled statistic here is dominated by 2022 (e.g. the pre-settlement drift below).

**Supporting structure (session):** overnight drift is positive and the pit drift is negative -- sum(overnight) = +100.6pt (t +2.31) vs sum(pit) = -83.5pt (t -1.84), full-day t = +0.26 (no net drift). Gross absolute move splits ~52% pit / 48% overnight. Small but significant **pre-settlement downward drift** 14:00->14:30 (mean -0.038, t -2.78) with a post-settlement rebound 14:30->15:00 (+0.020, t +2.55). Pit takes out the overnight high 57.4% / low 49.4% (only 8.2% of pits stay inside the overnight range); OR15 breaks *both* sides ~81% (largely geometric). NR7 gives no next-day range expansion (0.95x) -- the equity-index NR7 null replicates on CL.

---

## 4. Ranked preregisterable NATIVE mechanism families for Wave-2

Ranked by expected value. Each names the CL-specific economic reason, the cheapest falsifier, and the `FAILURE_MEMORY.md` closures it must clear (anti-rescue gate).

### H1 -- **EIA-cycle volatility mechanism** (Wednesday 10:30 ET). RANK 1 (highest EV).
- **Economic reason (CL-specific):** the EIA Weekly Petroleum Status Report is a scheduled, recurring (~52/yr; ~180 events in discovery), high-magnitude *fundamental* release unique to crude's ecosystem. The autopsy shows it is a **powered vol-expansion** (release-bar 3.08x, RV 1.43x, t +7.97) with **zero directional persistence** (50/51%). The mechanism is therefore a long-gamma / realized-vol capture around the release, or a **vol-timing overlay** that expands a risk budget only in the EIA window -- explicitly NOT a directional bet on the number.
- **Cheapest falsifier:** realized straddle/gamma P&L (or realized-vs-implied-proxy realized move) across the 10:30 Wed release vs its **matched unconditional control** (same-clock non-EIA weekdays), against a **dependence-preserving event-time-shift null**, with the valence **pre-stated as EXPANSION**. Net of the ALL_IN cost band (two-legged structure, MODELED CL spread+commission, conservative/stress rungs). Kill if the event-window vol premium <= MDE, or if it dies at +1 tick.
- **Must clear:** `G2_F1_TICK01` (rare-event regime-collapse) -- **state that EIA is NOT rare** (weekly, high-N; that is the material difference from the TICK/macro-mean closures). `G2_F12` (FOMC vol expands, "crush" backwards) -- valence pre-stated as expansion; sell-vol framing barred. `G2_F10` (NQ overnight hold into NFP/CPI NULL) -- materially different observable/timing: that was an *overnight directional premium*; this is an *intraday realized-vol* mechanism at a known clock. `AUCTREV` concentration + timing-teeth -- classify payoff shape (is the premium carried by a few blow-out Wednesdays?) with a pre-stated valence band; concentration is a classification, not a kill-gate (the incumbent itself fails at 236.8%).

### H2 -- **Shock overshoot / short-horizon mean-reversion** after large bars & abnormal volume. RANK 2.
- **Economic reason (CL-specific):** crude's info shocks (OPEC, geopolitics, outages) produce large 1-min bars, but the autopsy shows they **overshoot and partially revert**: P(continue) after a >99th-pct bar = 45.5% (baseline 42%); abnormal-volume bars (>3x/5x session median) P(continue) 43-45%; only the most extreme (>99.5th-pct) bars show weak 5-15 min continuation (+0.011 to +0.017pt). Combined with VR<1 multi-day and ER median 0.052, the market's character is liquidity-provision reversion at the shock, distinct from information-continuation. **This is the "key energy question" answered: at the 1-min scale CL shocks REVERT; genuine continuation is weak and only at the tail threshold over 5-15 min.**
- **Cheapest falsifier:** conditional next-1-to-3-min reversion return after |bar|>99.5th-pct *with* abnormal volume, vs a **matched unconditional same-clock/same-vol control** (must show the condition adds increment), dependence-preserving null; net of the ALL_IN band -- **the spread cost almost certainly dominates at this horizon, so decide economic viability first** (a candidate dead at +1 tick is fragile; likely uneconomic).
- **Must clear:** `G2_F2_SWEEP01` (post-cross MR is *generic*, not information) -- must show the abnormal-volume/large-bar condition beats the unconditional control, not just reproduce generic reversion. Fade graveyard / `W118` (7 fade geometries dead on NQ; continuation wins at the same bars) -- CL is a different market; pre-state this as an **ultra-short microstructure-overshoot fade** (1-3 min), not a session fade, and show it survives where NQ's died. `G2_F14`/`BREADTHPM01` (a conditioner that "adds nothing" hurts) -- the conditioning must earn increment. Dead-external seconds-scale OFI/cost-bar -- the reversion is at 1-3 min not sub-second, but the spread cost is the killer and must be cleared explicitly.

### H3 -- **Settlement-anchored intraday structure** (14:30 settlement clock / pre-settlement drift). RANK 3 (lowest EV).
- **Economic reason (CL-specific):** CL's hard 14:30 settlement concentrates physical-hedger and settlement-referenced flow (volume peaks 14:29-14:30). The autopsy shows a small but significant **pre-settlement downward drift** (14:00->14:30, t -2.78) and post-settlement rebound (t +2.55), plus the pit carries net-negative drift while positive drift lives overnight.
- **Cheapest falsifier:** pre-settlement window drift vs an **always-in control** and a time-shifted null, **per-year** (the pooled t -2.78 is very likely 2022-carried -- Fact 3); net of cost. Kill if it does not beat its always-in control or does not survive per-year decomposition.
- **Must clear:** `G2_F1_ORB01` (ORB NULL, **loses to its always-long control**, 2025 carries all, deep-era sign-flips) -- the CL OR breaks both sides ~81% (geometric), so any settlement/open-drive candidate faces the same brutal always-in control; **this is why H3 ranks last.** `G2_F2_CLAIMS01` IB-break=close-direction (definitional) -- an open/close-drive relationship must not be definitional. `W40` window-flattery + Fact 3 regime dependence -- must survive per-year, stating the 2022-carry risk. DELEV01 -- already points-basis (satisfied); keep every threshold in points.

---

## 5. Deliverables

| file | contents |
|---|---|
| `src/autopsy_cl.py` | full autopsy; freeze assertion in the loader; native-session determination; all sec.9 sections |
| `out/returns_by_tod.csv` | 30-min time-of-day 1-min point-return table (mean/std/sum/t) across the 24h container |
| `out/returns.txt` | ToD, day-of-week, session-vs-overnight, conditional continuation/reversal, settlement-clock drift |
| `out/distribution.txt` | skew/kurtosis/tails, gap dist, intraday-vs-overnight range, RV by year, extreme-day frequency by year |
| `out/dependence.txt` | return acf, sign persistence, variance ratio, vol autocorrelation, large-bar next-move |
| `out/path.txt` | efficiency ratio, tortuosity, MFE/MAE, captured-range fraction, range clustering / NR7 |
| `out/session.txt` | native-session determination (volume profile) + session structure (ON levels, OR, gap, prior-day levels) |
| `out/shock_response.txt` | (A) large-bar/vol-burst frequency & jump share, (B) EIA Wed-10:30 shock, (C) shock continuation vs reversal |
| `out/nq_correlation.txt` | daily/intraday rho-to-NQ, per-year, on shared discovery sessions |

**Evidence status: DISCOVERY_CONSUMED.** Discovery window (<=2025-06-30) only; holdout and virgin untouched. No promotion, no live change, $0.
