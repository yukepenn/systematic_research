# Hypothesis Frontier — living document

> _Pointer (2026-08-18): statuses in this file are frozen at 2026-08-07 vintage; most families
> listed as open were killed/closed in W1-W10. Authoritative live status:
> `registry/hypothesis_ledger.csv` + `registry/tested_configs.csv` + `REJECTED_IDEAS.md`;
> final phase state: `CAMPAIGN_STATE.md` (PHASE COMPLETE entry) + `ALPHA_SCOREBOARD.md`._

Status key: SEED (from mandate) | HOUSE (our own, from first principles / Solar findings) |
DR (from deep research) | T0/T1/T2/T3 (tier reached) | BLOCKED_BY_DATA | REJECTED (→ REJECTED_IDEAS.md)

## Seed families (mandate §14 — starting points, not a menu)
S1 micro momentum · S2 breakout/pullback/rebreak · S3 velocity/impulse burst ·
S4 failed break/snapback · S5 compression→expansion · S6 liquidity vacuum (data-gated) ·
S7 absorption (data-gated) · S8 queue/microprice (data-gated) · S9 OFI/trade-flow (data-gated) ·
S10 spread/liquidity state (data-gated) · M1 VWAP/value · M2 opening auction/ORB ·
M3 overnight inventory · X1 ES→NQ lead-lag · X2 NQ/ES relative state · X3 cross-index
confirmation · T1 session conditioning · E1 scheduled-event state

## HOUSE hypotheses (added at bootstrap, 2026-08-07 — before any data was read)

**Z1 — DC-overshoot scale transfer.** We hold a validated in-house scaling law nobody else
has: NQ directional-change overshoot ratio r = E[ω]/δ ≈ 1.29 at θ=179 ticks, σ-banded and
within-session (DC02b, T0-9). Question: what is r(θ) for θ ∈ {5..80} ticks, and does net
$/cycle after C1 turn positive anywhere? At θ=179 net was +$10.91/cycle (94.6th pct of
surrogate null, sub-threshold). Small θ → more cycles/day (scalp frequency) but friction is
fixed per cycle. Existing tooling: `src/analytics/dc_overshoot.py`, numba DC ladder.
Mechanism: same within-session continuation that funds Family A, harvested at micro scale.
Falsifier: r(θ)−1 shrinks below friction-implied breakeven for all θ<100.

**Z2 — Speed-conditional continuation.** Time-to-travel-N-ticks as the state variable:
moves that cover N ticks unusually fast (vs same-session σ) continue; unusually slow
grinds revert. Mechanism: fast traverse = one-sided liquidity consumption; slow traverse =
two-sided rotation. Price-only, Level-1 sufficient. Distinct from S3 (conditions on
duration percentile, not raw velocity).

**Z3 — Grid/round-number microstructure.** NQ 25/100-point levels as resting-liquidity
magnets: approach dynamics (accept/reject) at these levels at second-scale. Mechanism:
human/algo order clustering at round numbers. Price-only. Risk: folklore; needs matched
null at pseudo-levels (e.g. xx37.5) to survive.

**Z4 — Cash-close mechanical window.** 15:45–16:00 ET (US cash equity close, MOC imbalance
processing) creates mechanical index-arb flow in NQ. Test conditional drift/reversal around
15:50 imbalance-proxy moves. Calendar-causal, repeats daily.

**Z5 — RTH-open liquidity transition.** First seconds/minutes after 09:30 ET: overnight
inventory unwind meets cash-open price discovery. Separate continuation vs failure of the
overnight direction (links M2/M3 but at second-scale with explicit latency surface).

**Z6 — Session-open (18:00 ET) micro-drift.** Globex reopen after the 17:00–18:00 halt:
gap-settle dynamics in the first minutes; thin book → measurable but possibly untradable
(spread state must be checked — honest C1 accounting will likely kill it; cheap to test).

## DR batch 1 synthesis (2026-08-07; full blocks in deep_research/DR_A..D)

**Zone priors (REVISED per MANDATE_AMENDMENT_1 §1 — literature is a prior, not a local
verdict):** pure next-tick / simple top-of-book harvesting has a LOW PRIOR of surviving our
retail friction (external estimates: 0.1–1 tick gross vs 2.872-tick floor). Millisecond
cross-market price lead-lag: NON_RETAIL prior. Neither is a closed axis: seconds-to-minutes
NQ research continues empirically on our own L1/L2 data, especially conditional and
high-magnitude states, and every microstructure feature is evaluated in THREE separate roles
(A directional alpha / B selectivity-meta-labeling / C execution alpha) — a 0.5-tick signal
can fail A and still be valuable as C. Higher-prior zones: structural horizons, mechanical
windows, large-magnitude events, cost-side engineering. Unexpectedly strong micro results
get extra scrutiny (illusion checklist), not automatic dismissal.

**Priority-1 (Tier-0 candidates), merged and deduplicated:**
- **H-A1/H-D5 — last-30-min hedging momentum**: rest-of-day (or first-30-min) NQ return
  predicts last-30-min return; gamma/leveraged-ETF rebalancing mechanism; documented in
  futures panels; tens of ticks conditional; 1 trade/day; L1 MINUTE data → 20-yr history.
- **H-A2 — noise-area breakout**: practitioner replication claims +6bp/trade net on NQ;
  adversarial replication under C1/C2 + PBO (flat 2010–2017 is a feature to verify, not hide).
- **H-B5 — endogenous vs exogenous spike fade**: no-news spikes (vol-foreshock) revert more
  than scheduled-news spikes; 20–100+ tick magnitudes clear C1 outright; uses our committed
  announcement calendar (c01_announcement_calendar.csv).
- **H-B1 — anti-chase execution rule**: post-flow-burst transient impact (0.3–1.0 tick)
  reverses within ~1s; delaying marketable entries 1–3s cuts cost on trades we already take.
  Cost-side: benefits ANY strategy including Family A execution.
- **H-B3 — book-fragility veto**: spread widening/quote flicker precede liquidity-gap moves;
  direction-free risk filter; L2 (CONFIRMED available by DATAPROBE01).
- **H-D1 — ES flow → NQ continuation (30s–5min)**: flow, not price, survives; gated on ES
  tick download + the mandatory sync known-answer test (xcorr peak must sit at lag≈0).
- **H-D3 ≈ Z4 — cash-close mechanical window (15:50–16:00 ET)**: imbalance-leak into NQ;
  academically under-documented; calendar-causal, daily.
- **H-A3 — Roll-bounce guardrail (instrumentation)**: quantify mechanical ~½-tick fake
  reversion in Last-trade data; GATES all sub-minute reversion claims.
- **H-EXEC-1/2 ≈ S10 — NQ spread-state map (instrumentation)**: % of time 1-tick wide by
  session/vol; no published number exists; foundational for every cost model.

**Adopted guardrails (from DR-C, now binding):** fill = first print ≥ t+250ms (decay curve
at next-event/500ms/1s always reported); brackets tick-resolved, stops fill at through-print;
ETH → C2-or-excluded; ±2min news windows → C2; level signals (Z3) on UNADJUSTED single
contracts only; 1-tick-against shift test for any reversion edge; DSR/PBO at promotion.
**Do-not-adopt:** VPIN/bulk-volume classification (worse than tick rule on e-minis).
**Deferred:** passive execution (needs MBO), micro-price overlay (L3, live-forward only),
iceberg absorption (P3, data purchase = banned).

## Discovery queue (append below with mechanism/observable/horizon/falsifier)

**S2a — breakout-acceptance pullback rebreak (owner seed, 2026-08-07; STRUCTURAL_SCALP /
ADJACENT boundary).** Concretization of S2: completed 1-min bar closes beyond the prior
20-bar extreme with close-location ≥ 0.70 (≤ 0.30 short); 1–3 completed pullback bars all
holding the broken level, ≥ 1 down-close; entry = tick-series rebreak of pullback extreme
+1 tick with a strictly-later-timestamp guard; Tier-0/1 exits = fixed horizon {1,2,3,5,8}
min (primary 3). Mechanism: initiative flow still active after acceptance + retracement.
Owner-supplied notes filtered per Amendment 1: commission is $2.18/side (their $1.09 figure
is wrong), our tier gates and split geometry apply (not their 20-session runbook), no
Playback/Sim101 progression (banned), OnBarClose + explicit 1-tick series architecture and
the same-timestamp look-ahead guard are adopted as written. Vulnerable to: bar-close
fantasy, session artifacts, back-adjustment (uses relative levels — low), event clustering.
