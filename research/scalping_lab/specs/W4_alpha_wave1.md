# W4 — ALPHA THROUGHPUT wave 1: five parallel families (frozen before readout)

Date: 2026-08-08. Mode: Amendment 5 (ALPHA THROUGHPUT). Data: 37 L2 discovery sessions,
`substrate/sechilo/NQ` + `substrate/grid1s/NQ`. Common rules for ALL families: 1s clock,
RTH decisions, quote-alive filter, conservative same-second-both-crossed→adverse barrier,
sequential episode simulation (no overlap), C1=2.872t / C2=4.872t RT for market-market,
day-clustered 95% CIs (session bootstrap, seed 20260808), episodes+unique-days reported.
KPI per family: a real trade readout (A) or definitive kill (B). Neighbors reported
always, never selected on. Code `src/python/w4_*.py`, artifacts `artifacts/w4_*/`.

## W4-A — FSS-1: impulse → shallow pullback → rebreak (Zone F) [DoF 8]
LONG: impulse = mid(t)−mid(t−w) ≥ I with efficiency ret/TV_w ≥ 0.5, w=30s, I=12t
(neighbors w=15; I∈{8,16}); track impulse high IH (running max ≤30s after impulse);
pullback = mid dips to depth d = IH−mid ∈ [3t, 0.5·I] within 30s (deeper than 0.6·I
cancels); rebreak = mid > IH within 60s of pullback start → MARKET entry. SHORT symmetric.
Brackets (24,8) and (32,10), cap 300s, cooldown 30s.
PASSIVE variant (owner limit-order intuition, quantified): during pullback place limit at
IH − 0.4·I; filled only on strict trade-through (mid_low < limit − 1t); same brackets
from limit price; friction C1p = 0.872t commission + 1t exit slip = 1.872t RT (entry
passive, exit market; decomposition reported; adverse selection is captured naturally by
the sequential sim). Verdict rule: any config passes iff net C1 (or C1p) > 0 with CI
lower bound > −0.5t; family verdict = plateau logic.

## W4-B — S2a python analog (owner seed, frozen params; STRUCTURAL boundary) [DoF 5 holds]
1-min completed bars aggregated from sechilo mid (O/H/L/C per minute). LONG: close >
max(prior 20 bars' highs) AND CLV=(C−L)/(H−L) ≥ 0.70 (skip zero-range); 1–3 completed
pullback bars, every close ≥ broken level, ≥1 close < prior close; trigger: 1s mid >
max(pullback highs) + 1t, strictly after pullback bar close; window 10:15–15:15 ET;
cooldown 2 completed bars; one trade per impulse. SHORT symmetric (CLV ≤ 0.30).
Exits: fixed-time {1,2,3,5,8} min at market (primary = 3 min, others diagnostic);
brackets (24,8)/(32,10) as secondary diagnostic. C1/C2. This is the Tier-0 python
analog on mid; NT8 engine parity required before any Tier-1 claim.

## W4-C — FSS-5: level sweep → reclaim (Zone F/S) [DoF 8]
Causal levels per session: ONH/ONL (18:00→09:30 extremes), OR15H/OR15L (09:30–09:45),
running RTH high/low (prior-day levels unavailable in the non-contiguous discovery
sample — documented limitation). LONG at a low-side level L ∈ {ONL, OR15L}: sweep =
mid_low ≤ L − 2t, reclaim = mid_last ≥ L + 1t within 60s of the sweep → MARKET entry.
SHORT symmetric at {ONH, OR15H}. Brackets (16,6) and (24,8), cap 300s, cooldown 60s,
one trade per level-sweep episode. Neighbors: pierce {1t,4t}, window {30s,120s}.
Verdict rule as W4-A.

## W4-D — H-B5: spike continuation vs reversal (classification → at most one rule) [DoF 2]
Spike: |mid(t)−mid(t−10s)| ≥ 16t, episode collapse 60s. Outcome from spike-end second:
CONT = same-direction +12t before −8t within 300s; REV = mirror. Conditioners (each
univariate): scheduled-news proximity (±5 min, research/04_complementary_family/
c01_announcement_calendar.csv), pre-trend alignment (sign of ret_300s before spike vs
spike dir), spread_t at spike, first-10s retracement fraction, time block. FROZEN rule
trigger: if any conditioner cell shows |P(CONT)−pooled| ≥ 10pp with n ≥ 100 episodes
across ≥ 15 sessions, run exactly ONE trade readout: enter the favored direction at
spike-end+10s with (24,8), C1/C2. No cell shopping beyond the frozen criterion.

## W4-E — CLEAN_MOVE labels + path ordering (label family feeding next wave) [census]
CLEAN(H=60s): MFE ≥ M ∈ {16,20,24,32} with pre-target MAE ≤ K ∈ {6,8}, both dirs.
Frequency map (episodes/day, block mix). Path ordering on the 30s clock: time-to-first
+8 vs first −4, pre-target drawdown distribution, time-underwater. Directional
characterization: UP-clean vs DOWN-clean on the census feature set (reuse
opportunity_census.py machinery). Labels only — any rule needs a new frozen spec.
