# SMV2AH_DAY_CIRCUIT_BREAKER — REPORT

_Frozen spec: `runs/SMV2AH_DAY_CIRCUIT_BREAKER/spec.yaml` (committed d927ec6 before any read).
Authored by the orchestrator from the execution agent's structured output — subagent Write
tool refused REPORT.md; every number independently reproduced bit-for-bit by red-team
(verdict: CONFIRMED-with-corrections, two narrative corrections applied below, both non-
numeric — the KILL verdict itself is unaffected)._

## Executive summary
**Verdict: KILL.** A same-day, portfolio-level, intraday running-P&L circuit breaker is
**CONFIRMED-NOT-BENEFICIAL**, in either halt mode (FREEZE/FLATTEN), at any of the four pre-
registered thresholds (1st/2nd/5th/10th percentile of worst intraday drawdown), for either the
standalone SOLAR_DUAL_HTF leg or the deployed DAYONLY_DUAL6040 60/40 portfolio. **0 of 16
sweep cells qualify as a CANDIDATE.** The decisive failure mode is gate 2: in **every single
cell**, the real threshold-triggered rule's CDaR_0.95 is worse than the median of 200 matched
placebos that halt the same number of sessions at a random bar instead of the actual loss-
triggered bar. This extends SM02B's cross-day anti-edge finding to the same-day case: **loss-
reactivity is anti-edge again, now confirmed intraday, not just across days.**

The mandatory first-step integrity gate — reconciling a newly-built bar-by-bar intraday
cumulative MTM series against the existing end-of-day daily P&L — **passed exactly**: max abs
deviation $0.00 for object A (SOLAR_DUAL_HTF) and $1.8×10⁻¹² (float noise) for object B
(DAYONLY_DUAL6040), over all 1,139 dev sessions. Red-team independently rebuilt this from
scratch and confirmed bit-for-bit, cross-validating object-A/B control baselines against three
unrelated prior runs' independently-computed numbers.

## Mandatory Step 1: intraday MTM construction + reconciliation gate
Built from `src/analytics/sm01_solarsim.py`'s existing 3-minute bar target/fill machinery,
extended (not reimplemented):
- **Object A (SOLAR_DUAL_HTF leg):** `e10_exec`'s already-instrumented `bar_pnl` output, cumsum'd
  per session, reset at every session open.
- **Object B (DAYONLY_DUAL6040 60/40 portfolio):** a newly-built bar-by-bar B-MOM leg executor
  reproducing `runs/SMV2B_BMOM_EXEC_AUDIT/smv2b.py`'s frozen E2 ledger bar-for-bar, combined
  with the Solar/DUAL leg via the same two constant scalars `runs/SMV2AD_VOLMULT_CEILING/src/common.py`'s
  `vm()`/60-40 blend already applies daily — applied bar-by-bar instead, reconciling exactly by
  linearity.

| check | max abs deviation |
|---|---|
| Object A: session-end intraday MTM vs existing daily net | **$0.000000** |
| Object B: session-end intraday MTM vs existing daily portfolio net | **$0.0000000000018** |
| Sanity: new B-MOM bar-executor's daily net vs the frozen E2 ledger | **$0.000000** |

**Gate PASSED**, independently reproduced by red-team.

## sub_426: threshold calibration (DIAGNOSTIC)
Worst intraday running drawdown per session (min of intraday cumulative MTM, not session's
final P&L) — pre-registered as sub_427's four threshold cells:

| object | p1 | p2 | p5 | p10 |
|---|---:|---:|---:|---:|
| A_SOLAR_DUAL_HTF | −$4,658.19 | −$4,190.43 | −$3,035.52 | −$2,320.64 |
| B_DAYONLY_DUAL6040 | −$4,962.27 | −$4,317.94 | −$3,209.07 | −$2,304.70 |

## sub_427: circuit breaker sweep (16 cells) + placebo comparison
Decisions at the 3-minute bar level; first bar where cumulative intraday MTM < threshold
triggers the mode for the rest of that session only. FREEZE = block increasing net exposure
beyond the level held at the moment of freeze (existing reversal/exit logic untouched); FLATTEN
= immediate flatten, no further entries that session.

| object | pct | mode | n_trig | %sess | net $ | net(ctrl) $ | CDaR₀.₉₅ $ | CDaR(ctrl) $ | worst-day $ | worst-day(ctrl) $ | top10 retention |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 1 | FREEZE | 12 | 1.05% | 139,986 | 138,280 | 20,183 | 20,447 | −8,698 | −9,233 | 100.0% |
| A | 1 | FLATTEN | 12 | 1.05% | 135,567 | 138,280 | 19,631 | 20,447 | −5,295 | −9,233 | 100.0% |
| A | 2 | FREEZE | 23 | 2.02% | 138,281 | 138,280 | 20,315 | 20,447 | −8,518 | −9,233 | 100.0% |
| A | 2 | FLATTEN | 23 | 2.02% | 127,892 | 138,280 | 19,800 | 20,447 | −5,230 | −9,233 | 100.0% |
| A | 5 | FREEZE | 57 | 5.00% | 129,731 | 138,280 | 20,640 | 20,447 | −9,331 | −9,233 | 100.0% |
| A | 5 | FLATTEN | 57 | 5.00% | 128,512 | 138,280 | 18,211 | 20,447 | −5,230 | −9,233 | 100.0% |
| A | 10 | FREEZE | 114 | 10.01% | 129,602 | 138,280 | 20,250 | 20,447 | −9,331 | −9,233 | 100.0% |
| A | 10 | FLATTEN | 114 | 10.01% | 130,348 | 138,280 | 16,910 | 20,447 | −5,230 | −9,233 | 100.0% |
| B | 1 | FREEZE | 12 | 1.05% | 179,999 | 194,416 | 14,853 | 14,322 | −7,824 | −7,824 | 94.1% |
| B | 1 | FLATTEN | 12 | 1.05% | 173,835 | 194,416 | 14,470 | 14,322 | −5,643 | −7,824 | 94.1% |
| B | 2 | FREEZE | 23 | 2.02% | 177,149 | 194,416 | 14,758 | 14,322 | −7,824 | −7,824 | 94.1% |
| B | 2 | FLATTEN | 23 | 2.02% | 155,391 | 194,416 | 24,533 | 14,322 | −5,643 | −7,824 | 88.5% |
| B | 5 | FREEZE | 57 | 5.00% | 176,689 | 194,416 | 14,671 | 14,322 | −7,834 | −7,824 | 94.1% |
| B | 5 | FLATTEN | 57 | 5.00% | 160,823 | 194,416 | 17,855 | 14,322 | −4,374 | −7,824 | 88.5% |
| B | 10 | FREEZE | 114 | 10.01% | 187,189 | 194,416 | 13,079 | 14,322 | −6,799 | −7,824 | 94.1% |
| B | 10 | FLATTEN | 114 | 10.01% | 178,473 | 194,416 | 16,425 | 14,322 | −3,811 | −7,824 | 88.5% |

### Placebo comparison (200 paths/cell, seed=20260808)
**CDaR_0.95: the real rule loses to the placebo median in all 16/16 cells** (worse by
$1,100–$11,800 depending on cell, exact min/max: A/p1/FREEZE $1,100.64, B/p2/FLATTEN
$11,772.51). Worst-day is mixed: FLATTEN's hard cutoff caps most single-day losses below their
placebo median, **but not universally** — the B/p1/FLATTEN and B/p2/FLATTEN cells actually have
a worse worst-day than their placebo median (red-team correction: the original narrative
overstated this as a clean FLATTEN-always-helps-worst-day pattern; it does not hold for two of
the eight FLATTEN cells).

**Mechanism interpretation**: because the real rule is reactive (acts only after the loss has
already partly happened) while the placebo's random cut is timing-blind, on the pre-selected
set of "this session eventually had a bad drawdown" sessions, a random truncation anywhere in
the session captures MORE of the day's avoidable damage on average than waiting for the
specific loss threshold to be crossed. The improvement over the no-breaker control is not
attributable to knowing *when* to halt — it's attributable to halting-at-all on a set of
sessions that, in hindsight, needed less exposure. A real-time policy cannot get this benefit
without foreknowledge.

### Verdict gates (all three required for CANDIDATE)

| gate | pass count / 16 |
|---|---|
| 1: improves CDaR_0.95 AND worst-day vs no-breaker control | **7/16** (6/8 object A + 1/8 object B — the B/p10/FREEZE cell; red-team correction: the original report mis-stated this as "all object A; 0/8 object B") |
| 2: beats matched-placebo's median CDaR_0.95 AND worst-day | **0/16** |
| 3: retains ≥95% of control's top-10-day sum | 8/16 (object A: 8/8 at exactly 100.0%; object B: 0/8, tops out at 94.1%) |
| **CANDIDATE (all three)** | **0/16** |

Two independent, mutually reinforcing reasons kill object B (the deployed product)
specifically: it never clears the placebo bar (gate 2), and it never clears the top-10-day
retention bar (gate 3) — every object-B cell clips winning days along with losing ones
(88.5–94.1%, below the 95% floor), consistent with every prior right-tail-clipping finding in
this program.

## sub_428: old-regime screen — NONE_QUALIFIED
sub_427 produced 0 CANDIDATEs, so per spec this screen is explicitly N/A (disclosed via
`status=NONE_QUALIFIED`, not silently skipped — a hard guard against silent skipping was
verified present in the code).

## sub_429: mechanism note — leg attribution (object B, always reported)

| threshold | n_trig | Solar-only | B-MOM-only | both-neg, Solar-dom | both-neg, BM-dom | both-neg, comparable | mean Solar share of loss |
|---|---:|---:|---:|---:|---:|---:|---:|
| p1 | 12 | 16.7% | 0.0% | 8.3% | 16.7% | 58.3% | 0.56 |
| p2 | 23 | 13.0% | 0.0% | 8.7% | 21.7% | 56.5% | 0.58 |
| p5 | 57 | 15.8% | 1.8% | 21.1% | 17.5% | 43.9% | 0.59 |
| p10 | 114 | 13.2% | 2.6% | 35.1% | 18.4% | 30.7% | 0.60 |

The breaker does not mostly react to one engine's bad days — it's a genuinely mixed trigger.
Both legs are negative simultaneously in the large majority of triggered sessions, and the
Solar/DUAL leg supplies a modest majority (0.56–0.60) of the combined shortfall on average.

## Disclosed interpretive calls
1. FREEZE mechanics: magnitude capped at the level held at the moment of freeze, same-direction
   only; unrestricted shrink/flip in the opposite direction; flat-at-freeze blocks new entries.
   Red-team noted this leaves FREEZE's flip-side uncapped, which if anything biases the test
   toward finding *less* apparent benefit from FREEZE, not more — does not inflate the KILL
   verdict artificially.
2. B-MOM round-trip cost booked entirely at the closing bar of each trade (verified no effect
   on daily totals).
3. Portfolio blend scalars held fixed at control-calibrated values across all 16 cells (a live
   trigger cannot use future full-sample statistics to decide today's halt).
4. Placebo's random-bar range = full session, not RTH-restricted.

## kill_or_keep
**0 of 16 cells qualify as CANDIDATE → a same-day intraday circuit breaker (either halt mode,
any threshold, either object) is CONFIRMED-NOT-BENEFICIAL for this system.** Fully consistent
with (extends, not contradicts) SM02B's cross-day anti-edge finding: this is now the **third**
distinct time-scale at which loss-reactivity has tested anti-edge in this program (per-trade
MAE stops SM03/SM03B — dead because Solar's own reversal already acts as one; cross-day streak
throttle SM02B — anti-edge; now same-day portfolio circuit breaker — anti-edge, for a cleaner,
mechanistically distinct reason: a reactive rule structurally cannot know "when" to halt before
the loss has already happened, so it captures less protection than an equal-count random halt).
No R2_CONFIRMATION queued (rule requires ≥1 candidate; none exists).

## Red-team disposition
Verdict: **CONFIRMED-with-corrections**. All quantitative substance (reconciliation, threshold
calibration, all 16 sweep cells, all 3,200 placebo paths, gate logic, leg attribution)
independently reproduced bit-for-bit. No lookahead, no gate-shopping, no post-hoc threshold
picking, no placebo asymmetry. Two narrative corrections applied above (gate-1 object
attribution 6/8+1/8 not 7/8+0/8; the FLATTEN-worst-day generalization softened for its two
exceptions) — neither changes the KILL verdict. This REPORT.md resolves the missing-deliverable
gap red-team flagged.

## Files
`out/intraday_mtm_construction_check.csv`, `out/threshold_calibration.csv`,
`out/circuit_breaker_sweep.csv`, `out/placebo_comparison.csv`, `out/old_regime_screen.csv`,
`out/leg_attribution.csv`, `out/leg_attribution_detail.csv`, `out/gates.csv`,
`out/sub426_reconcile_verdict.json`, `out/sub427_verdict.json`,
`out/worst_intraday_drawdown_per_session.csv`, `out/intraday_mtm_series.parquet`.
Code: `src/common_ah.py`, `src/sub426_reconcile_calibrate.py`, `src/sub427_sweep_placebo.py`,
`src/sub428_old_regime.py`, `src/sub429_leg_attribution.py`.
