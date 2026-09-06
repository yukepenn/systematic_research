# G3_TSYROLL_20260906 — front-running the passive bond roll (G00087, family GENESIS3_EVENT)

**Verdict: CLOSED AT SCOPE (§28 block). G2 FAIL · G3 FAIL · G4 PASS · G5 FAIL · G6 MODERN-NEGATIVE —
the mechanical decision rule (`G2+G3+G4+G5 PASS and G6 not modern-negative -> candidate, else closed`)
closes TSYROLL01.** This is a **powered null**: the calendar-spread drift the mechanism predicts
does not exist even gross (−$22/cycle pooled, shift p 0.47, 51% of cycles positive — a coin flip),
against an MDE of $89/cycle.

Evidence status of every number in this report: **DISCOVERY** (first read of this representation;
consumed by this read). Wave 6 world-scan card #13. Program:
`src/tsyroll.py`; full program-printed output in `out/gate_table.txt` (= `run_stdout.txt`).

## The mechanism and the frozen object

Index funds roll ZN/ZB front→back on a schedule anchored to first notice (FN = last business day
of the month preceding delivery); the claim was that the calendar spread S = front − back drifts
DOWN during the heavy roll days — a premium paid by predictable flow that a LONG-back/SHORT-front
position entered at close FN−10 and exited at close FN−4 would collect. Per-contract day-store
work via `ncd_day.py` (both legs required simultaneously); FN realized on the front contract's own
trading calendar (self-correcting for month-end holidays: e.g. FN(2025-12 cycle) = 2025-11-28).

## Pairing coverage (measured honestly, as tasked)

- Census 140 root-cycles (70 deliveries 2009-03..2026-06 × 2 roots). **Usable for the primary:
  111** (ZN 55, ZB 56) across 56 quarters. 2 root-cycles have no leg data at all
  (`ZN 03-09`, `ZB 03-09` directories are empty), 27 lose a primary endpoint.
- The loss is **systematic, not random**: the store's Mar/Jun/Sep contracts of **2016, 2019, 2022,
  2025** carry only ~40–84 rows starting at/after the preceding FN, so the cycles for which they
  are the BACK leg (2016-03/06/09, 2019-03/06, 2022-03/06, 2025-03/06, and the Dec cycles
  2015-12/2018-12/2021-12/2024-12 whose back legs start in January) are unpairable. ZN also loses
  2026-06 (`ZN 09-26` starts 2026-06-30, after FN).
- Event-day pairing rate over the FN−15..FN panel: 79–80% at k=−15..−4, rising to 93% at FN.
  108/140 panels are fully paired 16/16. Placebo coverage: −1-month 106/140, +1-month 111/140.

## Gate-by-gate (all cells; program-printed table in `out/gate_table.txt`)

**G1 MDE first (PASS):** printed before any observed pooled mean. Quarter-pooled after-cost-cons
sd 0.2677 pt → **MDE (one-sided 5%, 80% power) = 0.0889 pt = $89/cycle** at N=111 root-cycles /
56 quarters (census 140; the shortfall is data absence, itemized above). ZN–ZB same-quarter
ρ = +0.265 → K_eff 1.58 legs/quarter.

**G2 drift (FAIL, all three clauses):** pooled gross **−0.02168 pt = −$21.68/cycle**; after-cost
CONS **−0.11571 pt = −$115.71/cycle**; quarter-block bootstrap 95% CI **[−0.196, −0.068] pt** —
excludes 0 on the WRONG side; shared-draw circular-shift null **p_1s = 0.4713** (z +0.29,
normal-approx 0.38 cross-check). The endpoint-close primary and the flagged-daily-change sum agree
(−0.02168 vs −0.02171 pt — the same event computed two ways). ZN gross +0.016 / ZB gross −0.059 pt.

**G3 sign consistency (FAIL):** after-cost-cons positive share **7.2%** (gate ≥60%); gross share
51.4% — indistinguishable from a coin flip.

**G4 placebo (PASS):** −1-month gross −0.0208 pt (n=106, CI [−0.082, +0.024]), +1-month gross
+0.0184 pt (n=111, CI [−0.026, +0.077]) — neither shows the drift. Consistent with the primary:
there is no drift anywhere. (+1-month anchors sit at the front's last trading day of the delivery
month, inside the notice period — measurement-only, disclosed.)

**G5 not-carry (FAIL):** carry control = per-cycle expected slide −6 × mean(ΔS over the FN−15..FN
panel). Carry-expected −0.0034 pt (carry mechanics are tiny, as expected for a treasury calendar);
excess after-cost-cons **−0.1123 pt**, CI [−0.183, −0.068] — the excess fails G2's clauses. (The
shift-null clause on the excess is identical to G2's by construction — the control is a per-cycle
constant anchored to FN — recorded, not re-tested.)

**G6 era (FAIL = modern-negative):** after-cost cons pre-2016 **−0.1445 pt** (n=52) / post-2016
**−0.0903 pt** (n=59) — negative in BOTH eras; post-2016 gross is +0.004 pt, i.e. one-sixteenth
of the conservative cost rung.

**G7 cost (PASS):** MODELED, SPREAD_ONLY, {1,2}-tick outright-equivalent band, 2 legs × 1 RT:
ZN $31.25/$62.50, ZB $62.50/$125.00 per cycle; cons rung gates. Info only (COMMISSION_ONLY,
non-gating): +2 × $4.36 = $8.72/cycle. Tick headers asserted == declared (ZN 1/64, ZB 1/32) on
all 140 loaded contracts.

**Decision (mechanical):** G2 FAIL, G3 FAIL, G4 PASS, G5 FAIL, G6 MODERN-NEGATIVE →
**CLOSED AT SCOPE**. Held every cycle it would COST $463/yr per 1-lot spread at the cons rung.

## What this means (attribution, no promotion)

1. **The predictable-flow premium is absent at daily-close granularity over FN−10→FN−4.** Not
   "there but under cost": gross is −$22/cycle pooled and +$16 even after dropping the three
   defective ZB panels (below), with shift p 0.47. The spread does not systematically cheapen the
   front during the heavy roll window.
2. **Carry mechanics are confirmed tiny** for these calendars (−0.003 pt per 6-day hold), so the
   null is not hiding behind a carry offset.
3. This closes world-scan card #13 at the daily-close representation; anything finer-grained needs
   data that does not exist locally.

## §28 closure block

```
Closed:  observable = per-contract ZN/ZB day-store calendar spreads (front minus back, both legs
  required simultaneously; ncd_day.py, contract-id keyed), FN = last business day of month
  preceding delivery, realized on the front's own trading calendar
representation = event-time spread panel FN-15..FN; primary = LONG back / SHORT front held
  close(FN-10) -> close(FN-4), pooled across roots (one shared draw)
event = quarterly passive index roll into first notice      horizon = 6 trading days
target = calendar-spread drift paid by predictable roll flow
execution = MODELED {1,2}-tick outright-equivalent band (SPREAD_ONLY), cons rung gates
sample = deliveries 2009-06..2026-06, 111/140 root-cycles pairable (systematic store gaps
  itemized), 56 quarters, MDE $89/cycle
reason = POWERED NULL: the drift does not exist even gross (-$22/cycle, +$16 excl 3 defective
  ZB panels; shift p 0.47; 51% of cycles positive gross). After cons cost -$116/cycle, 7%
  positive, CI [-$196,-$68] all-negative, both eras negative (modern-negative). G2/G3/G5 FAIL,
  G6 modern-negative; G4 placebos clean everywhere (no drift off-cycle either).
```
Adjacent-open: intraday roll-window microstructure (no local intraday rates data pre-2022-12);
ZT/ZF and WN/UB ends of the curve (never read at this representation); OI-timed roll windows
(blocked at $0 — the day store carries NO open interest, censused below).

## OI census sidecar (world-scan #14 step 1 — layout question only, no price analysis)

The NT8 day-store record **does not carry open interest**. The 48-byte record is fully accounted
for by six 8-byte fields — `int64 ticks | float64 open | high | low | close | int64 volume` —
verified two ways on `ZN 12-25/2025.Last.ncd`: (file_size − 28) % 48 = 0 over 135 records, and a
raw first-record hex decode (2025-06-16, O 110.484375 / H 110.671875 / L 110.265625 / C 110.40625,
volume 112) that consumes all 48 bytes with no residual field. Any OI-based roll-timing card
therefore needs an external OI source (free CME/Cboe OI or a paid feed); the local day store
cannot power it.

## Anomalies / disclosures

- **Three ZB panels carry defective leg data, kept AS-IS (spec froze no exclusion):**
  ZB 2009-06 (spread level +8..+14.6 pt with 3–5 pt/day back-leg swings — the only violently
  defective one; its −3.77 pt "primary" is 12× the next-largest magnitude in the whole panel),
  ZB 2009-09 (constant ≈ −11.9 pt offset) and ZB 2015-03 (constant ≈ −16 pt offset). Real ZB
  calendars sit under ~1.5 pt (panel median |S| 0.81 pt, 95th pct 1.61). The constant offsets are
  consistent with one leg's cached year-file carrying back-adjusted (merged-path) segments rather
  than true per-contract data — the exact contamination mode `ncd_day.py`'s header documents for
  the other NT8 transport. Because a constant offset cancels in a 6-day spread CHANGE, only
  ZB 2009-06 materially moves anything. **Sensitivity (non-gating): excluding all three, n=108,
  gross +0.01635 pt, net cons −0.07682 pt, share>0 net-cons 7.4% — every gate verdict unchanged.**
- Isolated bad rows (outside all windows, disclosed): `ZB 12-23` has a 2024-01-19 row at close
  2068.1 (off-band, off-grid, vol 1, past LTD); `ZB 12-20` has one zero-volume settlement row
  (2020-07-20). One 2009 panel includes a Memorial-Day (2009-05-25) bar — early-era data quality.
- The G4 "+1-month" anchor is the front's last trading date of the delivery month (its LTD,
  ~7 business days before month-end), not a true month-end — the uniform realized-calendar rule
  applied to a month in which the front dies; untradeable in reality, measurement-only.
- G5's carry control subtracts a trend measured over a panel that CONTAINS the primary window
  (conservative direction); moot here since the raw primary already fails.
- Frozen-interpretation notes recorded before results: G3 gated on after-cost cons (matching G2's
  after-cost primary; gross share also printed); G4 "shows the drift" = gross mean>0 AND
  quarter-block CI_lo>0 (gross basis is the stricter placebo detector).
- The ~140 anticipated root-cycles realized as 111 — the shortfall is store data absence
  (itemized), not population redefinition; MDE printed with the honest N.
- Seal asserted by the program: max loaded date 2026-07-31 < 2026-08-01; deliveries ≥ 2026-09
  excluded by construction (their FN windows are VIRGIN).
- REPORT.md could not be written by this pod (harness refusal on report files, not tunneled
  around per instruction); this document is returned in the structured output for the
  orchestrator to place at `runs/G3_TSYROLL_20260906/REPORT.md`.

## Outputs

- `out/gate_table.txt` — full program output incl. GATE/SPEC/OBSERVED/PASS-FAIL table
- `out/cycle_panel.csv` — the frozen event-time panel (root × delivery × event_day, both legs)
- `out/era_table.csv` — pre/post-2016 × root/pooled after-cost table
- `out/cycle_summary.csv`, `out/cycle_primary.csv` — per-cycle status/coverage and primary rows
- `out/verdicts.json` — machine-readable headline numbers and gate verdicts
- `src/tsyroll.py`, `run_stdout.txt`, `run_stderr.txt`