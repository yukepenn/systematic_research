# TIER 2 VERDICT — 14 CHALLENGERS, **ZERO GATE PASSES**. `INCUMBENT CHANGE: NONE`.

2026-08-31, 9 agents across 6 challenger lanes + portfolio + 2 killers.
**This is a no-change verdict reached by measurement, not by default.**

> ## TOMORROW'S BOOK: **M_11 unchanged** — `P1/PCT` ×1 + `XM_CONFLICT` ×1, two independent legs.
> No third sleeve, no re-weighting, no parameter change.

⚠️ The lanes name `WeeklyEdgeP1PCT_v2` / `_v3` and the older deployment ids because they started
before the HD-16 swap. The economics are **identical** (parity 0/2,439 and 0/378), so the verdict is
unaffected; the live objects are now `P1PCT_v3` `dep_9c51536a7045` and `XMConflict_v4` `dep_27ff47e7e3b7`.

## EVERY CHALLENGER, AND HOW IT DIED

| challenger | verdict | the number that killed it |
|---|---|---|
| `XM_ASYMMETRIC` | **DEAD** | 0/4 gates. Nominal +$149/wk sits at the **60.4th pct of a random-deletion placebo whose own median is +$90/wk**. ⭐ **Mechanism REFUTED WITH THE SIGN REVERSED**: XM-long taken while P1 is *already* long is the **BEST** cell ($837/trade vs $493), not the redundant one |
| `XM_SHORT_ONLY` | **DEAD** | +$103/wk < the **+$139/wk that deleting the same trades AT RANDOM** delivers. 87.3 % of its money is 2024 alone; 5 trades = 82.1 % |
| `XM_LONG_ONLY` | **DEAD** | −$169/wk, 31.8th pct of its own placebo, 2/5 LOYO |
| `P1SZ_SMOOTH` | **DEAD** | 0.910× incumbent; block-bootstrap 90 % CI **[−$205.89, −$20.18] excludes zero on the LOSING side**. It cleared its own permutation null at the 99.8th pct and preserved the tail — a real sizing rule, just a worse one. **The 5-bit quantisation is load-bearing, not fragility** |
| `P1SZ_VOLN` | **DEAD** | 0.870×, 0/25 rolling, 0/5 LOYO |
| `P1_SIGMABOX_V1` | **NOT FROZEN** | Gate B failed ⇒ **zero economics computed**. The discipline held |
| both preregistered SHORTs | **DEAD** | failed their own gates |
| `MC01_PULLBACK_CONT` | **RESEARCH ONLY** | closest to surviving: alignment null **93.9th pct, bar is 95th**. Ex-top-5 % weeks the delta **flips negative** |
| `ORB30` | **RESEARCH ONLY** | standalone t **2.1944** is genuine, but **7.5th pct** on the common-grid alignment null, 1/5 LOYO, ex-top-5 −$665 |
| **Book 7** (M_11 + ORB30 + MC01) | **DEAD** | ⭐ see below |

## ⭐ THE CENTRAL CROSS-LANE FINDING — the multi-sleeve book is REFUTED, not merely unproven

**ρ(ORB30, MC01) = +0.32**, against +0.14 and +0.13 versus M_11.
**The two nominal survivors are ONE FACTOR sampled twice** — modern-regime intraday continuation —
not two independent diversifiers. Book 7 lands at the **33.0th percentile** of the alignment null
versus **93.9th for MC01 alone**: adding the second continuation sleeve makes the case **strictly
worse**. The book is dominated by its own subset.

## ⭐ THE RISK METRIC ITSELF WAS INDICTED

At N = 243 weeks, **max-drawdown-matching is not a valid common-risk basis**: randomly deleting the
same number of trades side-blind raises DD-matched income by a median **+$129 to +$139/wk** — *more
than any candidate moves it*. Under **weekly-vol matching**, which has no such defect, the ordering
**reverses and the incumbent wins outright** ($2,211/wk, Sharpe 2.26).

⇒ **Every fixed-DD gain in this repo must now be read beside its random-thinning placebo, or it is
uninterpretable.** This retroactively voids the most flattering numbers in the wave.

> ⚠️ **2026-09-01 — the RULE is upheld and CODIFIED; the specific NUMBER does not reproduce.**
> `research_sdk/eval_battery.py` re-ran side-blind random thinning on **M_11's** certified weekly
> series (243 weeks, 2,817 trades, $2,211/wk — all three reproduce exactly). DD-matched income
> came out **monotonically NEGATIVE at every deletion rate from 2 % to 70 %** (−$20, −$61, −$91,
> −$236, −$527, −$1,046). **The +$129…139/wk lift does not appear on this object.**
> Most likely because it was measured on **Book 7** (M_11 + ORB30 + MC01), not M_11 alone, and/or
> on a different period grid — grid choice moves max DD from **$45,086 weekly to $51,891 on
> sessions**. Recorded rather than tuned away.
>
> **The underlying indictment survives, and is now demonstrated directly instead of by proxy.**
> An *oracle* rule — drop the worst 10 % of trades, using knowledge nobody has — reads
> **2.2× native, 2.5× weekly-vol, 2.1× gross-exposure, but 12.7× fixed-DD and 21.8× fixed-CDaR.**
> The order-statistic bases carry 5–10× the dynamic range of the others for the identical rule.
> **That is the mechanism, and the governance rule now rests on it rather than on one number.**

## ⭐ A REAL OBJECT DIVERGENCE IN THE DEPLOYED CODE — verified by me from the lane's console

```
PHASE DIAGNOSTIC - at which bar is the causal quality score evaluated?
  fill_bar - 0    95.12%
  fill_bar - 1    99.04%   <- the EXECUTABLE object
  fill_bar - 2    95.67%
G0b recomputed size vs NT8 qty : 99.04% (2377/2400)          PASS
G0a recomputed score vs the RR_W001 RESEARCH ledger : 81.21%  (2,033 joined rows)
```

**The certified NinjaScript reads its quality score ONE BAR EARLIER than the Python research object.**
The executable and the research object agree on the *score* only **81.21 %** of the time. The original
parity run printed the symptom (94.209 % quantity agreement) into a console file and **gated only the
aggregate share**, so it was never recorded.

The lane handled it correctly: it adopted **PHASE = 1 because the spec object IS the executable
object**, selected by the preregistered G0b criterion **and not by P&L**. The divergence runs in the
direction that **favours the executable**, which is what we trade and what every headline in this
session was computed from. ⚠️ But **"the NT8 object and the Python object are the same object" is
now false** and must not be asserted again.

## ANTI-FILTER RECORD NOW **TEN FOR TEN**

XMDIR01 is the **tenth consecutive** exposure-reducing rule here to lose to its own random control —
and the first where the control also **indicted the metric**. Every lane correctly avoided the W77
trap: nothing was motivated by the June–July 2026 drawdown, and **ORB30 actually made that drawdown
worse** (−$11,996 while M_11 lost $5,120), so it was never available as a recent-DD rescue.

## THE HONEST CASE AGAINST THE INCUMBENT, NOT SUPPRESSED

No known mechanism (`CURRENT_REGIME_UNEXPLAINED`); large openly-accounted selection debt; top 10 % of
P1 trades = **255.8 %** of net while the other 2,195 lose **$552,310**; inter-leg scale-free ratio
**0.656 → 0.863**, past the ~0.708 independence benchmark; and **zero forward evidence** — Panel B is
empty and begins with the very session this decision covers. **P(edge ≈ 0) = 10–30 %.**

None of that argues for a substitute, **because no substitute cleared a gate.** It argues for letting
the forward record accumulate — which is exactly what running M_11 unchanged does.

## TWO CORRECTIONS PAID (documentation, not book changes)

1. **"$45,000" is RETIRED** in `DRAWDOWN_ANATOMY` and `STATE_20260831` in favour of **$75–90k**:
   2yr p90 DD is **$43,747 = 97 % of $45k**, and one measured margin-cliff event alone needs $43,434.
2. The **43.4 bp → 24.6 bp** box-drift figures were computed on a **BACK-ADJUSTED** series, so they
   are **not index basis points**. Direction right; on true index levels **the drift is LARGER**.

## THE ONE AUTHORISATION RECOMMENDED — research only, not a promotion

`MC01_PULLBACK_CONT` earns a **preregistered forward challenge as book M_13**, on the strength of its
**near-zero selection debt** (it is the mandatory same-trigger direction control of a reversal rule
W118 preregistered and killed — sign-positive in 9 of 9 grid cells, never chosen by comparing its own
outcomes) and its **two-sidedness** (194 long / 154 short), which is the only structural answer
offered to the book's own named defect: a long-only P1 plus an XM whose long share hit 63.3 % in 2026.

Its gate must include the alignment null it currently **fails**, an exposure-**ADDING** random-**SIGN**
placebo (not a random-halt one), and **G7: MC01's forward P&L on M_11's worst-decile weeks ≥ 0** —
the exact functional that **FOLLOW_MORNING and LIQREV01 both fail**. Joint forward evidence begins
**2026-09-01** (August is DIRECTLY_BURNED for P1/XM); first aggregate read at ≥52 joint weeks.

## OPEN ITEM FOR THE OWNER — cheap, and it could invalidate the forward cost programme

Verify whether the **"Simulated"** feed label on DEMO8383477 means fills are against NT8's *internal*
simulated feed. If they are, the forward shadow's **fill and spread evidence is not market evidence**,
which would defeat the planned FILLPX spread harvest. *(Counter-evidence so far: the connected
provider is `Provider31 "Simulation"` — a broker demo — while NT8's own `Simulated Data Feed`
(provider `Simulator`) is **Disconnected**, and quoted prices track the real NQ series. Not yet
conclusive.)*