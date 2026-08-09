# U3 — hold/exposure continuation-value science

**Disposition: DIAGNOSTIC COMPLETE — no candidate constructed.** Two real leads were found; both
fail the standing right-tail/chronology bar. (Persisted here by the orchestrating session from
the subagent's returned text — its Write tool blocked direct creation of this file.)

## Point 1 — continuation-value maps (`out/continuation_by_bucket_{B,A}.csv`)

Baseline (canonical, HOLD bars): mean forward value small but positive at every horizon (B
`fwd_1`=+$1.68/bar n=192,723 t=2.68, `fwd_20`=+$29.33 t=11.25; A `fwd_1`=+$0.49 t=2.77,
`fwd_20`=+$9.09 t=11.55) — with n in the hundreds of thousands, t-stats are large for
economically tiny effects, so effect size/chronology/right-tail (not t-stat) drive the verdict.
Largest cross-leg bucket spreads at `fwd_5`: `side` (long>short: B $14.20 vs $2.63, A $3.09 vs
$1.56 — reproduces SA0's known asymmetry, not new), `vote_dispersion_tercile` (high>low: B
$14.71 vs $1.45, A $4.81 vs $1.78), `B_engaged`/B-MOM live (B $12.99 vs $4.21, A $6.85 vs $0.48 —
reproduces SA0's known B-MOM quality, not new), and `session_phase=RTH_CLOSE` as a negative
outlier (B -$11.33 t=-1.45 n=7,808; A -$9.69 t=-2.82 n=10,210). `age_bucket`/`giveback_tercile`/
`clv_tercile`/`rejection_aligned` show weak, non-monotonic patterns — no usable signal.

## Point 2 — session-transition value (`out/transition_analysis_{B,A}.csv`)

Strongest, most concrete finding: positions entered overnight (ETH_ASIA/ETH_EUROPE) show
markedly worse forward continuation **while still in the overnight session** than after the
session transitions into RTH:

| leg | state | n | fwd_1 | fwd_5 | fwd_10 | fwd_20 |
|---|---|---:|---:|---:|---:|---:|
| B | still overnight | 53,456 | $0.07 | $1.02 | $3.12 | $12.95 |
| B | transitioned to RTH | 22,460 | $2.83 | $13.35 | $24.42 | $42.57 |
| A | still overnight | 140,527 | -$0.11 | -$0.54 | -$0.96 | -$1.25 |
| A | transitioned to RTH | 29,877 | $3.00 | $14.15 | $30.11 | $58.85 |

RTH→POST_RTH transition shows the same direction but weaker/less clean (A consistently lower
after; B mixed by horizon).

## Point 3 — hazard framing (`out/hazard_table_{B,A}.csv`)

Mirrors the dollar finding in probability terms: `P(fwd_20>0)` still-overnight vs transitioned:
B 0.4844 vs 0.5188, A 0.4530 vs 0.5050.

## Point 4 — chronology + 2026 extension (`out/chronology_overnight_hold_{B,A}.csv`)

"Transitioned > still-overnight" holds **5/5 canonical years, both legs** (2022-2026 Jan-May) —
the one genuinely stable relationship found. June-July-2026 health-only extension (reported
separately, not blended): consistent direction, even larger gap for B ($8.26 vs $161.71).

## Right-tail check — BOTH candidates FAIL (mandatory per standing rigor)

- **Overnight-hold transition**: 9/20 top-20 all-time-winning blocks (each leg) were entered
  overnight. Checking their OWN bar-level P&L during their own "still overnight" phase: only
  **1/9 (B)** and **2/9 (A)** were net negative there — the rest were net positive, several by
  four-figure sums (B block 3591: +$4,275). A naive de-risk-while-overnight rule would cost real
  dollars from most of the campaign's biggest winners.
- **vote_dispersion** (secondary candidate, `out/votedispersion_*`): fails chronology (high>low
  only 4/5 years B, **only 3/5 years A** — not stable) AND right-tail: top-20 winners' hold-bars
  are OVER-represented in the "weak" low-dispersion tercile (B 57.6% vs 37.3% population
  baseline) and **0/14 (B), 1/13 (A)** of the top-20 winners' own low-dispersion bars were net
  negative, several by five-figure sums (B block 3423: +$19,380 during its own low-dispersion
  bars) — the aggregate direction is actually inverted for the biggest winners, the same
  tail-blindness pattern R5's `direction_x_volume` showed.

## Verdict

No genuine, tail-safe, chronologically-stable hold/continuation state signal was found and
authorized for construction. The overnight-transition finding is real, mechanistically sensible
(refines R3's own "hold-time not entry-quality" mechanism), and chronologically stable — but
fails the right-tail test decisively. vote_dispersion fails both gates independently.

## NOT YET TESTED / NOT AUTHORIZED FOR CONSTRUCTION THIS RUN

A materially narrower future candidate — conditioning the overnight-hold state on a SECOND,
already-validated quality signal (e.g. R4's `clv_aligned`, or entry-bar `M_abs` strength) rather
than session-phase alone — could plausibly separate genuinely-stalling overnight holds from
temporarily-flat big winners. This is a new two-dimensional hypothesis requiring its own
preregistration and full right-tail workup; not built, sketched, or implied promising beyond
"worth a dedicated future family" here.

Consistent with, and extends, R1/R3's prior closures on this same hold/exit layer. Zero
trading-rule changes.
