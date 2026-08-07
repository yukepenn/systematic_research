# RESEARCH_WAVE_B01 — failed directional change + value reacceptance

_Preregistered 2026-08-07 on branch `post_campaign_audit`, committed BEFORE any
B01 result is read. Seeds: `research/deep_research/DR-05.md` (H1–H5, constants
frozen there in 2026-08), thesis FAIL-01/VALUE-01/SESSION-01,
`reports/complementary_families.md` event definitions. Family-A comparators:
**executable R5-E10** and theoretical R4-21 (both audited)._

## Design resolution (preregistered)

The thesis FAIL-01 uses *opposite re-flip within 15/30/60 min* as the failure
trigger; DR-05's triage rules the re-flip **entry-useless** (by confirmation the
fade move is consumed; the re-cross of the flip price fires ~θ earlier) and
demotes it to invalidation/exit marker. **B01 adopts the DR-05 event set as
primary.** The thesis re-flip variant runs only as a labeled sensitivity arm
(B01b-S), never as a selection candidate, resolving the documented conflict.

## Arms, in execution order

### B01a — DR05-H1 overshoot / failed-flip calibration  [instrumentation, seq 0]
Data: `runs/B01A_BARS_1M/nq_1m_2022_2026.csv` (preregistered export), close-basis
DC at θ = 179 ticks, long and short episodes, full window 2022-01→2026-07.
Frozen constants (DR-05): failure = max overshoot beyond flip price < 0.25·θ
(45 ticks) within 60 min of flip confirmation; re-cross margin 10 ticks.
PASS requires BOTH:
(a) yearly mean overshoot ∈ [0.5θ, 1.5θ] every calendar year 2022–2026;
(b) failed flips are followed by median signed 60-min continuation ≥ 10 ticks
    WORSE than the unconditional post-flip cohort, sign stable in ≥ 4 of 5
    calendar years, pooled Wilcoxon p < 0.05.
FAIL on either ⇒ **B01b is not built** (DR-05 gate-conditionality is binding);
the wave proceeds directly to B01c (ORB failure is not H1-conditional).

### B01b — DR05-H2 failed-flip fade  [consumes trials; only if B01a passes]
Entry: after an H1-stamped failed flip, first 1-min close re-crossing the flip
price by ≥ 10 ticks, direction opposite the failed flip. Stop 10 ticks beyond the
post-flip extreme. Target: session VWAP (variant B: pre-flip anchor extreme).
120-min time stop; ≤ 1 trade/flip; forced exit if the flip direction re-achieves
overshoot ≥ 0.5θ. Stage 1 pure-Python vector backtest (fills next 1-min open,
slip 0/1/2, $4.36 RT); Stage 2 NT8 confirmation for survivors only.
Preregistered gates (DR-05, all eight): sleeve net > 0 at slip-1; PF ≥ 1.10;
avg trade ≥ $55; positive in ≥ 3/5 years including one of {2022, 2025};
daily-P&L correlation with Family A ≤ +0.25; no month > 40% of sleeve net;
Calmar ≥ 0.5; REJECT if profits concentrate in trades where the flip direction
later resumed (router-violation audit).
Right-tail protection (constitution §26): report Family-A top-decile retention of
the combined portfolio; a Family-B candidate that earns by fading Family-A's ten
best days is REJECTED regardless of standalone stats.

### B01c — DR05-H3 ORB failure + value reacceptance  [consumes trials]
As frozen in DR-05: 09:30–10:00 ET opening range; breakout close outside, close
back inside within 15 min, then 2 consecutive 1-min closes inside; fade toward
session VWAP; stop 10 ticks beyond failed extreme; ≤ 1 trade/side/session;
90-min time stop; BLOCKED when Solar Type-1 direction aligns with the breakout
AND current overshoot ≥ 0.5θ. Gates as in DR-05 (net > 0, PF ≥ 1.15, ≥ 3/5 years,
losing-day corr < 0.2, equal-risk combined Calmar above Family-A-only).
INCONCLUSIVE if n < 150 events (event count read before any P&L).

### B01d — DR05-H4 downside-asymmetry read  [0 DoF at read]
Stratified read over B01b/B01c event sets; PASS permits exactly one
side-eligibility bit in a future wave; FAIL freezes symmetric sides.

### B01e — DR05-H5 gap-fade null control  [preregistered negative control]
Gap ≥ 0.35% fade toward prior close, 11:30 ET stop. EXPECTED: no edge
(avg trade < $55 at slip-1 or < 4/5 years positive) ⇒ rejected_ideas.md.

## Accounting

Trial counter resumes at seq 230; every engine-run configuration gets a
pre-committed `runs/<run_id>/spec.yaml`. Python vector backtests over
preregistered constant sets count as R1 trials when their P&L is inspected
(rule R1) — B01b Stage 1 = 2 trials (target variants A/B at frozen constants),
B01b-S sensitivity = up to 3 (re-flip windows 15/30/60), B01c = 1, B01e = 1.
Budget for the wave: ≤ 12 R1 trials; exhaustion without a gate-passer marks the
failed-persistence family EXHAUSTED (constitution §18).

## Portfolio evaluation (fixed now, before any Family-B P&L exists)

For any gate-passing arm: equal-risk 50/50, 60/40, 40/60 combinations with
executable R5-E10 (primary) and theoretical R4 (secondary), scored on losing-day
correlation, drawdown overlap, ES5, TUW, worst week, and Family-A top-10-day
retention — per thesis PORT-01. No optimized weights.
