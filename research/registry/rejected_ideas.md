# Permanently rejected / deferred ideas (append-only; a rejected idea may not be renamed and retested without a genuinely new economic hypothesis)

Seeded from thesis §14 (2026-08-06):
- REJECTED for now: unrestricted A1–A5 full parameter optimization; strict 20/50/100-over-200 MA alignment gates for Type 1; fixed profit targets; immediate breakeven; multiple minute-level optimized time windows; treating 1m/2m/3m/5m Solar as independent strategies; optimizing toward the vendor author's screenshot profit/trade count.
- DEFERRED: continuous ATR-adaptive offsets; partial profits; profit-giveback locks; daily P/L locks; separate long/short parameter sets; opaque regime ML; leverage optimization.

## 2026-08-07 — Wave B01 (post-audit)

- **DR05-H1(b) / failed-flip conditional reversion (kills DR05-H2 unbuilt).** On
  19,311 DC segments (theta=179, 1-min closes, 2022-01→2026-07): failed flips
  (max 60-min overshoot < 45 ticks; 23.7% of flips) show median 60-min
  continuation only −2.0 ticks vs the unconditional cohort (preregistered
  requirement ≤ −10), sign stable 3/5 years (≥4 required), Mann-Whitney
  p = 0.171 (<0.05 required). The overshoot-deficit failure event carries no
  exploitable reversion information after costs. Arm (a) PASSED (yearly mean
  overshoot 204–218 ticks, in-band [89.5, 268.5] every year) — the scaling-law
  unit transfers; the conditioning premise does not. Evidence:
  research/04_complementary_family/b01a_h1_{report.md,ledger.csv.gz}.
  Per DR-05's frozen rule, the failed-flip fade (DR05-H2 / thesis FAIL-01
  re-cross variant) is dead unbuilt; re-testing requires a genuinely new
  failure definition, not re-tuned constants.
- **B01e/B02 gap rejection (seq 231-232).** The DR05-H5 null control REJECTED its
  null (633 fades, avg $118.63 slip-1, 4/5 years) but the preregistered
  escalation FAILED 3/6 gates: top-1% of trades = 90.1% of net (< 50% required),
  worst trade −$8,544 / trade-ES5 −$5,390 (stopless left tail; −$4,000/−$1,500
  bounds), 52.7% of active months positive (≥ 60% required). Roll-artifact and
  slip-2 checks PASSED (net_ex_roll Δ0.8%; slip-2 avg $108.63) and losing-day
  correlation with Family A was −0.08 with 101.7% top-10 retention — the event
  class is genuinely independent, but the P&L is a few giant gap-fill days plus
  a fat left tail. Axis CLOSED. A stopped/risk-managed variant would be a NEW
  hypothesis (tuned constants) requiring fresh preregistration in a future wave;
  it may not be built by adjusting this one after the read. Evidence:
  research/04_complementary_family/b02_gap_escalation_result.csv.

**WAVE B01 CONCLUSION (2026-08-07).** All DR-05 arms resolved: H1(b) FAIL, H2
dead unbuilt, H3 FAIL, H4 dead by dependency, H5 null-rejected then escalation
FAIL. Family B in its preregistered high-value forms (failed-DC reversion,
ORB-failure reacceptance, gap rejection) is FALSIFIED on 2022–2026 NQ under
frozen gates. 3 R1 trials consumed (seq 230–232) of the ≤12 budget. Untested
lower-prior variants (F04 overnight-range failure, F05 prior-day-range failure,
F07 balanced-value reversion, F08 session handoff) inherit negative evidence
from B01a/B01c and are deprioritized below PORTABILITY-01.
- **DR05-H3 / B01c ORB-failure + reacceptance fade (seq 230).** 1,037 events
  2022-2026, 696 vetoed by the frozen Solar-alignment veto (67%), 341 traded.
  Net -$22,534 at slip-1 (PF 0.839, avg -$66.08), -$19,124 even at slip-0;
  positive years 2/5; fails the first gate (net > 0). VWAP target hit 54% of
  trades but the 2.4:1 adverse stop distance dominates. Axis CLOSED; no
  constant adjustment permitted. Evidence:
  research/04_complementary_family/b01c_{event_census,trades_slip1}.csv.
  B01d (asymmetry read) dies by dependency: no qualifying event set remains.

## WAVE C01 Tier-0 closures (2026-08-07; constants frozen in C01_WAVE_SPEC.md pre-read; 0 R1 trials)
- **Short-side regime gating / crisis-conditioned shorts (SOLAR-01)**: ungated shorts are positive, regime cell sign-flips yearly, crisis retention fails. Shorts stay symmetric as crisis insurance. May not be re-tuned with different MA lengths/vol percentiles — the 200d/70th-pct constants were literature defaults, not searched.
- **DR03-H2 CUSUM drift allowance (k≠0)**: retrace-speed carries no significant next-trade information (p=0.35, rank-inverted, longs non-monotone). The LAST open threshold-mechanism axis is now closed; with T0-9's ARL result, threshold engineering as a class is permanently deprioritized.
- **Overnight conditional sleeve escalation beyond deferred status** requires new evidence, not re-tuned quantiles (25th-pct conditioning added no information over the unconditional base, Welch p=0.51).
- **Announcement-day exposure conditioning (either direction)**: significant FOMC-negative effect exists but 24.2% of top-1% P&L sits on announcement days — down-weighting violates the right-tail constraint; up-weighting failed its gate (announcement days underperform). A "skip post-release re-entries" microstructure variant would be a NEW hypothesis needing fresh preregistration; the day-level axis is closed.
