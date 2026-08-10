# EXEC01 -- Product A period selection for leg-by-leg dollar attribution

**Status: SELECTION ONLY.** No reconciliation performed yet. This document is written and frozen
*before* any period is reconciled against NT8, per the task's own disclosure requirement.

## 0. What already exists (read first, per task instructions)

Read in full before this selection was made:

- `runs/V1R4_NT8_PARITY/FULL_HISTORY_CERTIFICATION.md`
- `runs/V1R4_NT8_PARITY/out/PRODUCT_A_CERTIFICATE.md` (via `runs/V1R4_NT8_PARITY/PRODUCT_A_CERTIFICATE.md`)
- `runs/V1R4_NT8_PARITY/REPORT.md`
- `runs/V1R4_NT8_PARITY/spec.yaml`
- `runs/V1R4_NT8_PARITY/out/producta_v4_2024apr_2025mar.json`
- `runs/V1R4_NT8_PARITY/out/q1_2025_producta_spotcheck.json`

**Confirmed current state (verbatim from the file, not restated from memory):** Product A's
full-history net-profit residual is **+10.91%** (`$197,329.70` NT8 stitched vs `$177,924.40`
Python mark-to-market, diff `+$19,405.30`), stated in `FULL_HISTORY_CERTIFICATION.md` L59-68 and
matched exactly in `PRODUCT_A_CERTIFICATE.md` L104. Verified this is NOT yet reduced to an exact
leg-by-leg proof for Product A -- `FULL_HISTORY_CERTIFICATION.md` L70-75 and L83, and
`PRODUCT_A_CERTIFICATE.md` L71-77 and L104-109, both say so explicitly ("Not reduced to an exact
leg-by-leg proof the way NQ/MNQ are... a plausibility argument, not a proof"). No restatement in
the task brief needed correction -- the figure and its unproven status both check out.

**What NT8 output already exists on disk for Product A (no new NT8 run needed for any of it):**

| source | window | granularity |
|---|---|---|
| `runs/V1R4_NT8_PARITY/out/chunks/A_E1..E7_{summary,trades}.json` | 2022-01-03 -> 2026-05-29 (full canonical window, 7 non-overlapping chunks, 1139 sessions, no gaps) | round-trip trades: `entry_t, exit_t, entry_px, exit_px, side, pnl, comm` -- no explicit `quantity` field, but exactly recoverable as `comm / 0.65 / 2` (verified below, exact to the trade) |
| `runs/V1R4_NT8_PARITY/out/producta_v4_2024apr_2025mar.json` | 2024-04-01 -> 2025-03-31 (12 months, subset of chunks E4/E5) | full NT8 trade objects: explicit `Quantity`, `entry.quantity`/`exit.quantity`, `MaeCurrency`/`MfeCurrency`, order names (`L`/`S`/`XL`/`XS`), `order_id`, per-side commission -- the richest already-available Product A dataset |
| `runs/V1R4_NT8_PARITY/out/q1_2025_producta_spotcheck.json` | 2025-01-01 -> 2025-03-31 | aggregate only (`NetProfit`, `TradesCount`, etc.); **this is `SolarWaveSMMaster_v3`, the pre-DEFECT-3-fix object** -- historical context only, not usable as a `_v4` reconciliation source |

Both the E1-E7 chunk trades and the rich Apr2024-Mar2025 job are `SolarWaveSMMaster_v4`
(DEFECT-3-fixed, current object) output -- confirmed by re-deriving day-level trade count, PnL,
and commission from both sources independently for every day in `2025-01-06..2025-01-10` (a
window covered by both) and finding **byte-identical trade counts, PnL, and commission per day**
(see `runs/EXEC01_PRODUCT_A_DOLLAR_ATTRIBUTION/src/00_select_periods.py` output; also confirms the
`comm / 0.65 / 2 = quantity` inference used for the chunk-only periods below is exact, not
approximate, on every one of the 78 trades cross-checked that day span).

Product A executes on **MNQ**, not NQ (`runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/
01_dual_truth_repricing.py`: `PV_MNQ_A, COMM_MNQ_A = 2.0, 0.65`, target exposure clipped to
`+/-13` contracts) -- confirmed against `PRODUCT_A_CERTIFICATE.md`'s own stated commission
resolution ($0.65/side MNQ). NQ is signal-only (the primary/chart series feeding the tilt/B-MOM
decision layer); MNQ is what actually gets bought and sold.

## 1. Selection method (disclosed before any reconciliation)

**The selection criteria (turnover, exposure, scale-in/down, reversal, best/worst day) were
computed entirely from the Python-side decision-layer position/PnL series -- never from where
NT8 and Python happen to disagree.** Concretely:

1. Re-ran Product A's certified decision layer (`product_a_exec_generalized`, copied
   byte-for-byte from `runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_repricing.py`'s own
   function of that name -- reused per the task brief, not re-derived) against the already-built,
   already-certified substrate (`runs/SA0_SYSTEM_STRUCTURE/current_health/src/health_substrate.py`,
   the same substrate PRICE01 itself imports). Script:
   `runs/EXEC01_PRODUCT_A_DOLLAR_ATTRIBUTION/src/00_select_periods.py`.
   - Correctness gate (built into the script, must pass before any output is trusted): canonical-
     window net must equal the certified **$177,924.40** exactly. **PASS** (`177924.40` to the
     cent).
   - Imported `health_substrate` directly (read-only, verified by inspection to contain no file
     writes) rather than importing `01_dual_truth_repricing.py` itself, because that module's own
     top-level code unconditionally writes into `runs/PRICE01_PRODUCT_A_GENUINE_MNQ/out/` --
     forbidden by this task's read-only constraint on that directory. Nothing under
     `runs/V1R4_NT8_PARITY/` or `runs/PRICE01_PRODUCT_A_GENUINE_MNQ/` was written by this pass
     (script writes only under this run's own `out/`).
2. Restricted to the canonical window (`sess_date <= 2026-05-29`) -- the window fully covered by
   already-run NT8 output (chunks E1-E7), so every candidate day considered is guaranteed
   reconcilable without a new NT8 job.
3. Computed, per session, from the Python bar-level target-exposure series alone: net mark-to-
   market PnL, max |position|, turnover (sum of |bar-to-bar position changes|, in contracts),
   count of scale-in bars (same-sign, size increases), count of scale-down bars (same-sign, size
   decreases), count of reversal bars (direct sign flip, both sides nonzero -- these ARE possible
   bar-to-bar since the target can jump straight from e.g. +9 to -4 without stopping at 0).
4. Cross-referenced the independently-built CME early-close session calendar already on disk
   (`runs/W17_C4_COMPLIANCE/out/v1d_session_calendar.csv`, 44 early-close sessions flagged by
   `nbars < 400` in the full canonical window) -- not re-derived, reused as-is.
5. Ranked all 1,139 canonical sessions by each criterion independently and selected windows from
   the **top of each ranking**, choosing windows (not single isolated days) so that adjacent days
   around each extreme are included for realistic reconciliation context (position state carries
   information from the prior bar/day even though the strategy is flat at every session close).
6. Deliberately spread selections across chunks (E1, E3, E5, E6, E7) rather than clustering all of
   them in one chunk, so the sample is not accidentally representative of only one NT8 job's
   behavior. **Known gap, disclosed rather than hidden:** chunks E2 (2022-09-01..2023-05-01) and
   E4 (2024-01-01..2024-09-01) are not independently represented among the 9 periods below -- none
   of the top-ranked extremes on any criterion happened to fall there this pass. If reconciliation
   of the 9 selected periods surfaces a chunk-specific pattern, E2/E4 are the natural next-pass
   add.
7. This document was written, and the criteria/rankings above computed and frozen, **before**
   opening a single NT8 trade record from the selected periods to compare against Python. No
   period below was chosen, adjusted, or swapped after looking at a reconciliation result.

Full per-session table (all 1,139 canonical sessions, every column above): `out/day_stats.csv`.
Per-period summary (below, machine-readable): `out/periods_selected.csv`.

**One honest finding surfaced by this computation, disclosed here because it changes what "near
the cap" means for period selection:** the Python decision layer's actual position **never once
reaches 12 or 13 contracts** anywhere in the full 4.5-year canonical window (distribution: 51
sessions touch 11, the rest are lower; zero sessions touch 12 or 13). "High exposure near the
+/-13 cap" below therefore means the actual observed ceiling of **11 contracts (85% of the
nominal cap)**, not a literal cap-touch, which structurally does not occur in this window.

## 2. Selected periods

| ID | Window | Sessions | NT8 source (already on disk) | Criteria covered |
|---|---|---|---|---|
| P1 | 2022-04-25 -> 2022-05-06 | 10 | `chunks/A_E1_trades.json` (comm-inferred qty) | high exposure (11, 4/26), scale-in **and** scale-down single-day champion for this whole cluster (4/27: 20 in / 21 down), high turnover (5/6: 66), 1 top-10 win (4/26: +$9,791.2), 1 top-10 loss (5/6: -$4,681.4); earliest-history representative (E1) |
| P2 | 2023-10-16 -> 2023-10-20 | 5 | `chunks/A_E3_trades.json` (comm-inferred qty) | **single most reversal-dense session in the entire canonical window** (10/18: 10 reversals) plus an adjacent high-reversal day (10/19: 4) and high turnover (62, 68); fills the E3 gap |
| P3 | 2024-11-26 -> 2024-11-29 | 4 | `producta_v4_2024apr_2025mar.json` (RICH, explicit qty) | **two consecutive early-close sessions** (Thanksgiving-week abbreviated session 11/28, Black-Friday abbreviated session 11/29 -- both `nbars<400` per the CME calendar) back to back, stress-testing the C4 session-relative flatten on consecutive short sessions |
| P4 | 2025-01-06 -> 2025-01-10 | 5 | `producta_v4_2024apr_2025mar.json` (RICH, explicit qty) | early-close session (1/9: National Day of Mourning, 310 bars, ends 09:30 ET) -- the exact session previously flagged (`REPORT.md` L64-78) as the likely partial cause of `_v3`'s 23% Q1-2025 gap; direct, in-place follow-up test of whether `_v4`'s DEFECT-3 fix (session-relative flatten, not hardcoded clock) now handles it correctly -- Python-side net on 1/9 is a quiet -$322.2 / 8 contracts turnover, consistent with correctly-restricted entries on an abbreviated session, a useful independent pre-check before NT8 comparison |
| P5 | 2025-03-06 -> 2025-03-13 | 6 | `producta_v4_2024apr_2025mar.json` (RICH, explicit qty) | extreme-volatility week: 1 top-10 win (3/10: +$8,989.5) and **three** top-10 losses in four sessions (3/7: -$4,905.6; 3/11: -$6,481.5, the #2 worst session in-sample; 3/12: -$4,698.1), heavy reversals (3/11: 5) and scale activity throughout |
| P6 | 2025-03-24 -> 2025-03-28 | 5 | `producta_v4_2024apr_2025mar.json` (RICH, explicit qty) | **single scale-down-densest session in-sample** (3/27: 19 scale-down bars) coinciding with a top-10 loss (-$4,672.5); adjacent high-exposure day (3/26: 11 contracts, 13 scale-ins, +$4,644.9) |
| P7 | 2025-04-04 -> 2025-04-11 | 6 | `chunks/A_E5_trades.json` (comm-inferred qty) | **single highest-turnover session in-sample** (4/7: 96 contracts) plus the **2nd-highest** (4/9: 92 contracts); two of the **top-3 winning sessions** in-sample (4/8: +$14,620.5; 4/9: +$13,093.2), both also near-max exposure (11 and 8 contracts) with reversals; coincides with the real April-2025 tariff-driven volatility spike -- a naturally occurring stress period, not manufactured |
| P8 | 2025-11-17 -> 2025-11-25 | 7 | `chunks/A_E6_trades.json` (comm-inferred qty) | **single largest winning session in the entire canonical window** (11/20: +$17,629.9, 11 contracts, 44 turnover), immediately preceded by the 2nd-most reversal-dense session in-sample (11/19: 8 reversals) and followed by two more large losses (11/21: -$6,258.4, #3 worst in-sample; 11/25: -$4,982.5, #5 worst, also 11 contracts) |
| P9 | 2026-05-14 -> 2026-05-22 | 7 | `chunks/A_E7_trades.json` (comm-inferred qty; **terminal chunk, caveat below**) | **single largest losing session in the entire canonical window** (5/19: -$7,408.6, 4 reversals, 44 turnover), inside a week-long losing stretch (5/15: -$3,254.7; 5/18: -$1,689.2; only 5/20 positive) |

Machine-readable version with per-period sums: `runs/EXEC01_PRODUCT_A_DOLLAR_ATTRIBUTION/out/periods_selected.csv`.

**Session boundaries, as a criterion, are structurally satisfied by every period above, not by a
dedicated period:** Product A is forced flat at every session's C4 boundary (`forced_flat_c4`),
so every one of the 55 selected sessions independently exercises entry-block/forced-flat logic
across its own two session boundaries (open and close). P3 and P4 additionally exercise the
early-close variant of that same boundary logic (shortened `entry_blocked`/`forced_flat` windows
relative to an earlier session close).

## 3. Disclosed caveats for the reconciliation phase (not resolved here)

- **P9 sits in the terminal chunk (E7)**, which `FULL_HISTORY_CERTIFICATION.md` flags with a
  known **aggregate** boundary-serialization anomaly (E7's overall NQ/MNQ residual flips to
  -76%/-96%, attributed to a position still open at the *literal last bar of the whole certified
  window*, 2026-05-29, being invisible to NT8's own serialized trade list). P9's own window
  (5/14-5/22) ends **7 sessions before** that boundary, so it should not itself be the position
  affected by that quirk -- but this has not been independently confirmed for Product A
  specifically, and is flagged here in advance rather than discovered mid-reconciliation.
- **Day-bucketing convention mismatch, already known from the certification docs, will recur
  here:** NT8's native convention buckets a trade's whole PnL onto its **entry date**; Python's
  `bar_pnl` series used for this selection is **mark-to-market**, splitting PnL across every day a
  position is held. A cross-check on 2025-01-06..10 already shows this concretely: NT8's
  entry-date-bucketed net for 1/9 is -$530.5 (`producta_v4_2024apr_2025mar.json` and
  `A_E5_trades.json` agree exactly) vs. Python's mark-to-market net of -$322.2 for the same
  calendar date -- a real, expected, already-documented convention difference, not a defect, and
  not something this selection step attempts to reconcile.
- **Quantity inference for the 4 chunk-only periods (P1, P2, P7, P8, P9)** uses
  `quantity = comm / 0.65 / 2` (MNQ Lifetime commission, $0.65/contract/side, 2 sides per round
  trip). This was verified **exact** (not merely close) against the RICH job's explicit `Quantity`
  field for every one of the 78 trades in the 2025-01-06..10 overlap window (5 days, both sources
  agree to the trade). Not independently re-verified for P1/P2 specifically (outside both the RICH
  job's coverage and any other explicit-quantity source), so this remains a verified-elsewhere,
  not verified-in-place, inference for those two periods -- disclosed rather than assumed.
- **Product A's leg-level decision layer has NOT been independently trade-count-verified in any
  prior wave** (`PRODUCT_A_CERTIFICATE.md` L73-77: "trade-count and gross-shape agreement were not
  separately re-verified for Product A specifically in this pass"). Unlike BEST_ONE_NQ/MNQ (which
  have an exact, proven leg-by-leg match on the Q1-2025 window via
  `runs/V1R4_NT8_PARITY/src/one_nq_event_forensics.py` / `mnq_5session_forensics.py`), **none** of
  the 9 periods above have been leg-verified for Product A before this task -- this selection is
  the first attempt at that for this object.

## 4. What this document does NOT do

No NT8 trade record and no Python leg was compared in the writing of this document. No new NT8
backtest was run or requested. All 9 periods above reconcile exclusively against NT8 output
already resident on disk (the E1-E7 chunk trades and/or the rich Apr2024-Mar2025 job); no period
was chosen that would require a fresh `RunStrategyBacktest` call.
