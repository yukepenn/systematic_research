# G2_F3_EXECSTATE01 — RESULT: **NULL (no harvestable within-minute timing) — and the cost model VALIDATES in scope**

Spec committed `bb426af` pre-result. Trial G00023. Gates in `out/gate_table.txt`.

> **The within-minute NQ spread surface is flat**: boundary-second penalty +0.0034/+0.0037 tk vs
> the preregistered 0.25 tk bar — ~70× below it, and POWERED (MDE95 0.0069/0.0045 tk on 71k
> samples/bin). Bar-close-timed strategies pay no mechanical boundary tax on NQ; re-timing was
> not priced (FAIL is a FAIL). MC-47's external claim does not transfer to this instrument's
> tape.

Secondaries (banked):
- **No cost-model revision needed**: fitted f(spread, depth, hour) on P1's states = $21.71/ctrRT
  in the pre-burn scope, 13.2% divergence < 20% — consistent with EXEC01's era structure.
- OFI→mid slope is positive and monotone in spread state (0.10→0.18 tk/ctr) — a descriptive
  microstructure fact, execution-relevant only.
- ⭐ Matched-vol time-of-day: the sign FLIPS under matching — 15:00 looks 0.42 tk cheaper naively
  but is **0.35 tk dearer vol-matched**; afternoon "cheapness" is calm minutes, not deep books.
  (The W111b lesson, now in execution space.)

Defect disclosed: a µs-vs-ns cast bug in the first execution (P1-leg instants only) was fixed and
re-run; the primary gate reads the quote grid and was byte-identical across versions.

**Closure scope:** *second-of-minute effective-spread/markout timing on NQ, 52 pre-burn sessions.*
**`LIVE ENABLED = NO` · $0 · blind pools untouched (0 opened, enforcement printed).**
