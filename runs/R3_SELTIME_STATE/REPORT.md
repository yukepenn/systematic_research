# R3 — SelTime as continuous/conditional state — RESULTS

Per `spec.yaml`'s construction gate. **Disposition: CLOSED — CONFIRMED-NOT-BENEFICIAL at the
entry-eligibility layer. No candidate constructed.** Full evidence: `src/`, `out/`.

## The central finding: S2's own diagnostic motivation does not mean what its construction assumed

Diagnostic 1 (entry-level attribution — a block's ENTIRE net_pnl assigned to its entry hm) found
**EUROPE_PREUS (02:00-08:00 ET) new entries are net POSITIVE: +$79,924.82 pooled, positive in
4 of 5 years** (2022 +$58,818, 2023 +$9,690, 2024 -$4,175, 2025 +$6,318, 2026 +$9,274) — the
opposite sign from S2's own spec.yaml pre-screen ("Solar's EUROPE_PREUS net P&L by year: 5/5
years negative, -$4,847 to -$6,461").

Diagnostic part 2 (`02_bar_level_vs_entry_level.py`) reconciles this by replicating S0/S2's own
**bar-level** attribution convention (each 3-min bar's own realized P&L assigned to its own clock
slot, regardless of when the position was entered — the standard convention this repo uses for
every prior time-of-day autopsy, e.g. Wave-18's D4 cohort table): bar-level P&L inside the
EUROPE_PREUS clock slot is genuinely negative, **-$14,868.96** pooled (year-by-year 2022 +$3,210,
2023 -$6,229, 2024 -$13,617, 2025 -$2,888, 2026 +$4,656 — not an exact match to S2's own figures,
which used a plainer Solar-only diagnostic construction rather than this run's full certified
incumbent bar_pnl, but the same order of magnitude and mostly the same sign, confirming this is
the same real, measured phenomenon under a different base object).

**These two measurements are not in conflict — they are answering different questions, and the
gap between them IS the finding.** Decomposing the bar-level bleed by where the carrying block was
entered: of the 136,482 bars inside the window, 20,248 bars (-$9,675) belong to blocks that were
ALSO entered inside the window, and 24,856 bars (-$4,475) belong to 246 blocks entered OUTSIDE the
window and simply **held through** it. The 246 carried-over blocks have a 47.2% whole-trade win
rate and a mean net_pnl of +$542.56 — **unremarkable at the whole-trade level**; their specific
bars ticking through 02:00-08:00 just happen to often be a temporary drawdown/consolidation phase
of an otherwise-ordinary trade, not a sign the trades themselves are bad.

**Conclusion: the EUROPE_PREUS bar-level bleed S0/S2 diagnosed is real, but it is a HOLD-TIME
phenomenon (positions sitting through a low-liquidity window, wherever they were entered), not an
ENTRY-QUALITY phenomenon.** S2's constructed rule (block NEW ENTRIES/FLIPS during the window) was
mechanistically mismatched to its own diagnostic: entries commenced during the window at the
block level are fine (positive, 4/5 years), so blocking them removes real edge without addressing
the actual holding-cost mechanism — this is a specific, evidenced, mechanistic explanation for WHY
S2 failed the right-tail gate (`R2_ONE_NQ.md`: a real +$7,625 winner suppressed on 2025-04-09),
not merely a restatement that it did.

## Full-clock state-interaction scan (diagnostic 2, `out/diag2_clock3h_x_Mstrength.csv`)

No clock×M-strength cell shows a clean broad/monotonic/multi-year pattern outside noise. The
single largest negative cell is **09:00-12:00, weak-M tercile**: mean -$191.53, sum -$44,627
(233 trades) — vs the SAME clock bin's strong-M tercile at mean +$684.73, sum +$218,428 (319
trades). This is the most promising-LOOKING lead in the whole scan.

## Why the promising-looking lead is not constructed: right-tail veto

The natural generalization — "block weak-conviction (M-strength bottom tercile) entries" as a
state-only (not time-conditioned) eligibility rule — was checked directly against this campaign's
non-negotiable right-tail preservation standard (directive sec39) BEFORE any chronology/bootstrap
work: **8 of the top-20 all-time winning blocks are themselves in the weak-M tercile**
(`M_abs` between 3.54 and 4.25, just past the `EntryLevel=3.0` gate — includes a **$14,287.82**
and a **$12,192.82** winner). A blanket weak-M eligibility filter would remove nearly 40% of the
campaign's largest winners. This alone disqualifies the construction under the SAME standard R1
and R2V1 were held to — no chronology or bootstrap work is needed to reach a verdict once the
right-tail check fails this decisively.

The narrower version (weak-M AND specifically 09:00-12:00) was considered and explicitly
**rejected as construction** rather than tested: it is a single cell hand-picked after seeing the
full interaction table (`out/diag2_clock3h_x_Mstrength.csv` has 19 populated cells; this is the
most extreme one), exactly the "isolated point, assume overfit" pattern directive sec43 warns
against, and the campaign's own R2V1 experience already demonstrated how an attractive-looking
narrow cell can fail chronology once actually tested. Per spec.yaml's construction gate ("no rule
is forced into existence to fill the slot"), it is recorded here as a disclosed near-miss, not
built.

## Diagnostic 3 — within-EUROPE_PREUS substate breakdown (`out/diag3_europreus_substates.csv`)

Cross-tabulating M-strength × consensus × vol WITHIN the window (entry-level) finds no single
substate cleanly explains the window's bar-level bleed — the worst entry-level substate found
(`strong_M__mid_consensus__high_vol`, 14 trades, sum -$20,286) is negative in 3 of 4 years it
appears in, but at n=14 total across 4.5 years it is far too sparse to generalize (< 1 year_bar
per year), and — consistent with the bar-vs-entry reconciliation above — entry-level substates
are the wrong lens for a bar-level (hold-time) phenomenon in the first place.

## What R3 rules out, and what it leaves open

**Ruled out** (entry-eligibility layer, per this run's own spec):
- Re-testing S2's exact blanket window — not attempted, per standing discipline.
- A state-conditioned variant of S2's window (weak-M entries, EUROPE_PREUS or 09-12 specifically)
  — right-tail veto, disqualified before further testing.
- A pure M-strength (conviction magnitude) entry filter, any time of day — same right-tail veto.

**Left open, NOT pursued in this run (would be a different layer, per directive sec37's
separation-of-layers rule, requiring its own preregistration)**:
- A HOLD/EXPOSURE-layer mechanism specifically targeting the 02:00-08:00 bar-level bleed (e.g.
  reduced size or tighter risk while holding through this window, regardless of entry time) — this
  is mechanistically well-motivated by this run's own bar-vs-entry decomposition, but is an
  EXIT/HOLD mechanism, not an ELIGIBILITY mechanism, and R1 (the prior hold/exit family) tested a
  different state variable (giveback, not time-of-day) and is CONFIRMED-NOT-BENEFICIAL for that
  variable specifically — a time-conditioned hold mechanism has NOT been tested and is a
  legitimate candidate for a FUTURE, separately preregistered family. Not built here.

## Disposition

**R3: CLOSED — CONFIRMED-NOT-BENEFICIAL at the entry-eligibility layer.** No candidate
constructed, per spec.yaml's own construction gate (no cell cleared the right-tail-safety bar).
The mechanistic finding (S2's diagnostic motivation was bar-level/hold-time, but its construction
targeted entries) is a genuine addition to the record, not merely a repeat of S2's closure.
Continuing automatically to R2B per directive priority order.
