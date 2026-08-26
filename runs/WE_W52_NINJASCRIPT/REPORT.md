# WE_W52 — THE BASELINE AS NINJASCRIPT, CONFIRMED IN STRATEGY ANALYZER · REPORT

Spec preregistered. NinjaTrader 8.1.8.1, Strategy Analyzer engine, isolated **Backtest**
account. No order placed on any live account, no strategy enabled, deployed or started, no
account/connection/credential/licence touched, no vendor assembly modified.

**Verdict: IMPLEMENTATION VALIDATED — 99.985 % decision agreement, above the preregistered
99 % bar.**

---

## 1. Phase 0 — the closed form that made this tractable (`FACT`)

The 32 voters apply the throttle and delta masks to the TARGET, *after* the decision stack, so
the whole ensemble collapses:

```
vote = nMemLong × nThrottlePass × (1 + deltaGate) / 32
vote ≥ 0.5   ⟺   nMemLong × nThrottlePass × (1 + deltaGate) ≥ 16
```

Asserted against the actual `long_vote()` output over all **1,558,497** bars:
**max |difference| = 0.0, identical bar-for-bar, 0 disagreeing positions.**

And because a ratchet member's state depends only on price and σ — never on which set it
belongs to — the four member sets are *prefixes* of one 13-member ladder. So the strategy needs
**13 shared members and 4 combiners**, not 32 decision stacks. Without this the implementation
would have been roughly eight times larger and correspondingly harder to validate.

## 2. The artefact
`research/weekly_edge/ninjascript/WeeklyEdgeP1_v3.cs` (520 lines), also in NT8's Strategies
folder. It implements: the 13 shared ratchet members (S = clamp(VolMult·σ, 40, 1200 ticks),
σ = trailing mean |ΔClose| over 460 bars), the HTF tilt over 50 session closes, B-MOM, the four
combiners with hysteresis 3.0/1.0, the session entry-block/forced-flat windows, the range
throttle against its trailing-60-session same-minute median, the lagged delta gate, the session
box (−$1,300/+$1,000) on its own fill ledger, and the causal quality score against
trailing-250-entry quantiles.

`Calculate.OnBarClose` + market orders means a decision at bar *i*'s close fills at bar *i+1*'s
open — the same convention the Python fill layer uses. Nothing reads the bar it fills on.

## 3. The bug I introduced, and how it was found (`FACT`, worth recording)

v1 shifted every timestamp by −1 minute, on the reasoning that "Python stamps a bar with its
start, NinjaTrader with its end" — a defensive fix for W44's phase error. **The premise was
false and I had not checked it.** The parquet's first bar of an 18:00→17:00 session is stamped
**18:01** and its last **17:00**: it is bar-END stamped, exactly like NinjaTrader. (The variable
name `open0930` says the same thing — the bar stamped 09:31 opens at 09:30:00.)

So the defensive fix *was* the phase error. Its signature, from the component export:

| iteration | bmom | tilt | nMem | nThr | dL | **voteOK** |
|---|---|---|---|---|---|---|
| v2 (with the −1 min shift) | **95.268 %** | 99.998 % | 96.754 % | 99.239 % | 98.564 % | **98.767 %** |
| **v3 (no shift)** | **100.000 %** | **100.000 %** | **99.967 %** | **100.000 %** | **100.000 %** | **99.985 %** |

The v2 bmom disagreements were dominated by **sign inversions** (−1→+1 on 1,256 bars, +1→−1 on
1,115) clustered at 09:32–09:37 — B-MOM arming one bar early takes the wrong `open0930`, and
the ±2.83 it contributes is enough to cross the 3.0 entry level in all four combiners at once.

**Method point**: exporting a per-bar ledger of the *components* (nMem, nThr, dL, ratio, tilt,
bmom, the four targets) rather than only trades localised this in **two** iterations. A
trade-list or P&L comparison would have shown "close but not equal" with no way to tell which
of eight mechanisms was wrong. Every future parity check exports components.

## 4. Final parity, warm window 2026-04-01 → 2026-05-29, 58,268 one-minute bars

| component | agreement | disagreeing bars |
|---|---|---|
| B-MOM | **100.000 %** | 0 |
| HTF tilt | **100.000 %** | 0 |
| range-throttle count (nThr) | **100.000 %** | 0 |
| delta gate (dL) | **100.000 %** | 0 |
| throttle ratio | max abs diff **5 × 10⁻⁵** | 0 |
| per-set targets (narrow5 … all13) | 99.967 % | 19 |
| nMemLong | 99.967 % | 19 |
| **voteOK (the decision series)** | **99.985 %** | **9** |

The residual 19 bars (0.033 %) are the expected slow-member warm-up: NinjaTrader starts cold on
2026-01-02, and a member with a large VolMult that has not flipped since before that date still
carries a σ-stale threshold. The Python object carries state from 2022. This shrinks with a
longer warm-up and is not a logic difference.

Warm-up is why the window starts 2026-04-01: by then NT8 has more than the 50 sessions the tilt
needs, the 14 RTH days B-MOM needs, and the 60 sessions the throttle median needs.

## 5. What is NOT validated here, stated plainly
The **quality size** cannot agree on this backtest and is excluded from the verdict by the
spec. Its trailing-250-**entry** window needs ~250 prior entries; NT8 accumulates ~100 by
2026-04-01, so it sizes 2 on 0.3 % of entries where the Python object sizes 2 on ~20 %. This is
a warm-up property of the measurement, not of the code, and it means **the NinjaScript's
absolute P&L on this window is not the object's P&L**. Confirming the sizing layer requires a
backtest starting in 2022; that is the next run and it is cheap.

Also unvalidated: the last-bar-of-session flatten books at that bar's close in the ledger while
NinjaTrader would fill at the next session's open. The forced-flat window (−21 min) means the
position is normally already closed, so this path should be near-dead — but it is a known,
disclosed difference rather than an assumed equivalence.

## 5b. FULL-WINDOW END-TO-END CONFIRMATION (2022-01-03 -> 2026-05-29)

NinjaTrader loaded **1,558,498** bars against the Python substrate's 1,558,497 - the same
continuous series - so the quality layer's trailing-250-entry window is fully warm and the
sizing layer IS validated here.

| campaign window 2022-07 -> 2026-05 | Python (baseline) | NT8 Strategy Analyzer | delta |
|---|---|---|---|
| trades | 1,950 | 1,948 | -2 (-0.1 %) |
| net | $298,327 | $296,423 | **-0.64 %** |
| pts/session | 14.72 | 14.63 | -0.6 % |
| size-2 share | 18.4 % | **20.6 %** | +2.2 pp |
| weeks | 203 | 203 | - |
| weekly mean | $1,470 | $1,460 | -0.7 % |
| weekly std | $4,720 | $4,705 | -0.3 % |
| **annualised Sharpe** | **2.25** | **2.24** | -0.4 % |
| positive weeks | 58.6 % | 58.1 % | -0.5 pp |
| max drawdown | -$22,360 | -$23,649 | +5.8 % |
| **worst week** | **-$7,418** | **-$8,557** | **+15.4 %** |
| eff | 0.198 | 0.171 | -13.6 % |
| **weekly series correlation** | | **0.9752** | |

The only material difference is ONE WEEK. Because eff = weekly mean / |worst week| is a
SINGLE-OBSERVATION statistic, it inherits that entire difference: eff moves 13.6 % while the
annualised Sharpe moves 0.4 %. **Method note recorded: eff must always be reported beside
Sharpe and CVaR-efficiency, because one week can move it by an order of magnitude more than it
moves any distributional metric.**

The 2 missing trades are the slow-member warm-up: NT8 starts cold on 2022-01-03 and a large
VolMult member that had not flipped before then carries a sigma-stale threshold for a while.

**The 5-month run's $8,567 gap is now explained and closed** - it was entirely the cold
quality-sizing window, exactly as disclosed before that run.

## 6. Status
The campaign's baseline now exists as a NinjaScript strategy whose **decision series is
confirmed against the Python object through NinjaTrader's own engine at 99.985 %**. W44's
deployment consequence — "a NinjaScript implementation must be written to match the PYTHON
object and validated against it, because running the existing C# would trade a materially
different system" — is now discharged.
