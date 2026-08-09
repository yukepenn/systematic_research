# W19R1_SELECTIVITY — SUPERSEDED BEFORE EXECUTION. Nothing was run; nothing is deleted.

> **NOTE added 2026-08-09, 89 minutes after this file was written (red-team-flagged staleness):**
> this file's claim was true when written but is no longer true of the directory it sits in — the
> spec below WAS later run, unmodified, per a same-day owner directive that superseded the
> reprioritization that produced this file. See `REPORT.md` for the executed run and results.

**Dated 2026-08-09.** This spec was frozen and committed at `d4926a4`. **No code was written
against it, no data was read, no result was produced.** It is superseded before execution by
owner directive R2/R5 of the same day, which reprioritises Wave 19 to put the D7 regime
diagnostic (`runs/W19D7_REGIME_2026/`) ahead of any mechanism test.

Per §13 rule 8 a frozen spec is not amended mid-flight, so it is not amended here either. The
spec file is left exactly as committed. The successor spec will be frozen separately once D7
delivers, and will carry a different `run_id`.

## Why it is superseded rather than run as written

Directive R5 requires that **every arm's result be reported split at whatever boundary D7
establishes**, alongside the full-window number, and that a verdict which depends on which side
of that boundary you look at be reported as *the* finding rather than as a pooled statistic.
That boundary does not exist yet. Running the selectivity test first would produce exactly the
pooled number the standing caution (seq 466) says not to trust.

## What carries forward unchanged, and was endorsed by the owner

- **Exposure neutrality as an INVALIDATION gate checked before any P&L is scored** (gate 0). An
  arm outside ±5% of the control's total exposure is not scored at all. This is the direct
  lesson of M1, which shipped a "selectivity" result that measured a 30.9% exposure reduction.
- **arm_TOD's score built from ES/RTY/YM P&L and never from NQ's**, so that Wave 18's D4 cohort
  finding on NQ becomes an out-of-sample confirmation of the score rather than the thing being
  fitted, with the resulting circularity in gate C declared in advance and gate C recorded
  NON-BINDING for that arm.
- **arm_ER**: ER150 as a causal selectivity score at constant exposure, BETA = 0.5 frozen on a
  mechanical clamp-headroom argument, no grid anywhere.
- **The chronology gate (≥ 4 of 5 yearly sign agreement, plus survival of excising the final 106
  sessions)** — already present as `gate_B_chronology` in the superseded spec, and it satisfies
  directive R5's first addition. Recorded here so the successor spec does not treat it as new.

## What must be ADDED to the successor spec

1. Every arm's result reported **split at D7's estimated boundary** (or, if D7 reports that the
   data cannot locate one, at the calendar 2026-01-02 boundary **labelled as a convention, not a
   finding**), alongside the full-window number.
2. An explicit statement of what it means if an arm's verdict flips across that boundary:
   per R5, that flip **is** the finding, and the pooled statistic is not to be led with.
3. Whatever D7's §4 (D1 effective diversity) and §5 (incumbent decomposition) establish about
   whether the incumbent is itself degraded in the period — because if it is, in-period
   challenger comparisons are low-power rather than adverse, and the successor spec's power
   analysis has to say so before the run rather than after.

## Alpha budget

The superseded spec declared 2 of 2 alpha hypotheses consumed. **Since it never executed, no
alpha budget was spent and none is charged to Wave 19 for it.** The successor spec charges the
same two hypotheses (arm_ER, arm_TOD) when it runs. D7 charges nothing — diagnostics are
uncapped under §15.
