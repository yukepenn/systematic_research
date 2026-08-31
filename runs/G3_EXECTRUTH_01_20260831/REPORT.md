# G3_EXECTRUTH_01 - EXECUTABLE OBJECT TRUTH

**Run:** `G3_EXECTRUTH_01_20260831` - spec committed before any comparison existed - GENESIS III
Wave A, EXECUTABLE TRUTH lane
**LIVE ENABLED = NO - $0 spent - no order, deploy, enable, backtest or CrossTrade call of any kind**
**Evidence status:** VERIFICATION. Nothing is selected, tuned, promoted or unlocked by this run.

---

## 1. The P3 verdict, in one sentence

**H_STALE wins both score and size agreement outright and the named control loses - the deployed
object does read its quality features one bar staler than the Python research object, exactly as the
spec's source read predicted - but H_STALE reaches only 96.977 % score agreement against the 99.0 %
bar, so P3 is recorded FAIL and the executable is NOT REPRODUCED BY ANY OF THE THREE PREREGISTERED
ARMS; no economics are quoted anywhere in this run.**

The source read of spec section 0 is **not** retracted: H_FRESH loses in both framings, by 9.1 and
3.3 percentage points respectively. What the spec's arm set could not express is that the executable
is a **mixture**, and the reason is a second, previously unrecorded defect described in section 6.

---

## 2. The gate table (printed by the program - `out/console.txt` section 10)

| GATE | SPEC | OBSERVED (full in-window) | FULL | REALTIME |
|------|------|---------------------------|------|----------|
| P0 | join >=95 % AND monthly sd(close_cs-close_py) after removing that month's median <= 0.25 pt | join 99.980 %; worst month sd 0.0482 | **PASS** | n=0 SEALED |
| P1 | voteOK >=99.5 % AND t0..t3 each >=99.5 % | voteOK 99.173 %; t0..t3 97.52/99.00/98.12/98.02 % | **FAIL** | n=0 SEALED |
| P2 | entry-bar Jaccard >=0.99 AND abs(trade-count diff) <=2 % | Jaccard 0.85176; count diff +1.795 % | **FAIL** | n=0 SEALED |
| P3 | H_STALE wins score AND size outright, score >=99.0 %, H_STALE2 loses | win = H_STALE/H_STALE; H_STALE score 96.977 % | **FAIL** | n=0 SEALED |
| P4 | only if P3 passes | not computed | - | - |

**No gate is reported SPLIT.** A SPLIT requires two decidable columns; there is only one. The
realtime tail is 112 rows, **every one of them >= 2026-08-01**, and all 112 were dropped by the seal
before any statistic was computed. Post-seal realtime n = 0.

### Declared diagnostic second column (declared in section 2a of the console BEFORE any result)

The .cs cannot agree with a fully-warm Python object during its own warm-up:
`WeeklyEdgeP1PCT_v3.cs:1067` leaves `tilt` identically 0 until `sessCloses.Count > TiltSma = 50`.
The split at export-session >= 51 (from 2025-11-10 18:01) is derived from that source constant alone.

| GATE | OBSERVED (WARM sub-span, 78.4 % of joined bars) | WARM |
|------|-------------------------------------------------|------|
| P1 | voteOK 99.921 %; t0..t3 99.82/99.86/99.90/99.85 % | pass |
| P2 | entry Jaccard 0.99065; count diff +0.313 % | pass |
| P3 | H_STALE score (qCount >= 250) 96.599 % | fail |

**The gate verdicts above are the FULL ones.** The WARM column is a diagnostic and does not
overturn anything.

---

## 3. What is now known about WHICH OBJECT WE TRADE

1. **The two objects are on the same bars, and the price series are not merely close - they are
   identical.** The spec expected a constant per-contract-regime back-adjustment offset. The
   measured offset is **exactly zero** (mean, median and sd all 0.0000) in **10 of the 12 calendar
   months**, and only **2 bars out of 325,006** differ at all (2026-06-11 and 2026-07-17, the two
   dates where the two files do not even hold the same minutes). P0's tolerance was never tested.

2. **Once the deployed instance finishes its own warm-up, it is the same decision object as the
   research chain.** Inside the declared WARM sub-span, voteOK agrees on 99.921 % of bars, every
   per-set target t0..t3 agrees on >= 99.82 %, entry-bar Jaccard is 0.99065 and the trade counts are
   0.31 % apart - that is VALIDATED on the repo's binding WE_W52 band.

3. **The deployed object's quality score is one bar staler than the research object's.** In both
   framings and on every metric, H_STALE beats H_FRESH and beats the H_STALE2 control:

   | framing | H_FRESH | **H_STALE** | H_STALE2 (control) |
   |---|---|---|---|
   | EXEC-NATIVE score | 87.909 % | **96.977 %** | 84.635 % |
   | EXEC-NATIVE size | 97.481 % | **98.992 %** | 97.229 % |
   | RESEARCH-CHAIN score | 65.193 % | **68.508 %** | 62.155 % |
   | RESEARCH-CHAIN size | 91.160 % | **92.818 %** | 91.713 % |

   The research object has therefore been crediting its sizing layer with an information set the
   deployed strategy does not have. That claim is now measured, not inferred from source.

4. **The executable IS exactly reproducible - but not by any arm this spec preregistered.** With one
   further correction taken from source (section 6), score agreement goes to **100.000 %** and size
   agreement to **100.000 %** on all **397** entries the executable evaluated, including all 100
   warm-up zeros. Zero disagreeing entries. That is an explanation, not a preregistered result.

5. **The deployed instance's quality history is not the campaign's history, and that matters more
   than the phase does.** The strategy was redeployed with `DaysToLoad=365`, so its trailing
   250-entry quantile window is built from its own 365-day replay, not from 2022 onward. Correcting
   the ATR inside the RESEARCH-CHAIN framing moves score agreement only 68.508 % -> 69.890 %; and
   even after excluding the 100 entries the executable zeroes by warm-up (`qCount < QualMinHist`),
   the research chain still reaches only **81.017 %** (n = 295) against the executable's
   **100.000 %**. That 81.017 % sits within 0.2 pp of the 81.21 % score agreement `T2_P1SIZE01`
   reported against the `RR_W001` ledger - this run supplies the mechanism for a number that was
   previously unexplained.

6. **Every action the executable takes is the action its own state predicts.** The bars where the
   .cs evaluated an entry (`myQty==0 && wantLong && UseQualitySize`, derived from the export's own
   `qty` / `voteOK` / `stopped` columns) number **397**, and the export's `qty` path shows exactly
   **397** ENTER events - difference 0. Off the mask, `score != 0` on 0 bars and `size != 1` on 0
   bars. The mask is right.

---

## 4. What did NOT reproduce - stated bluntly

- **P1 fails on the full in-window span.** voteOK 99.173 % against a 99.5 % bar; t0 is the worst
  action-bearing field at 97.525 %. **88.8 % to 95.9 % of every action-bearing mismatch lies before
  the declared warm boundary**, but the gate is on the full span and the gate fails.
- **P2 fails on the full in-window span, and fails badly enough to matter.** Entry-bar Jaccard is
  0.85176 - **below the 0.90 line at which WE_W52 says "it is not the same object"**. The
  trade-count clause passes (+1.795 %) but the Jaccard clause does not. 33 of 35 C#-only entries and
  27 of 28 Python-only entries are pre-warm, so the classification is clean, but the number stands.
- **P3 fails.** 96.977 % against 99.0 %. With n = 397 evaluated entries, 99 % permits at most three
  disagreements; there were twelve.
- **P4 was not computed and no dollar figure exists in this run.** The spec's `if_none_reaches_99`
  clause is binding: *"state plainly that the executable object is NOT YET REPRODUCED. No economics
  are quoted in that case."* Both are honoured. The `H_STALE_CSATR` 100 % result does **not** unlock
  P4, because it is not one of the three arms the spec fixed in advance.
- **The `ratio` diagnostic disagrees on 24.8 % of all bars and still on 5.7 % inside WARM.** It does
  not move `nThr` (99.759 % inside WARM) and therefore does not move an action, but it is the
  largest unexplained-by-warm-up field in the run. It is localised to `norm`, the trailing
  time-of-day range median: on 27,554 bars the .cs has no `norm` yet while Python does; on 52,918
  bars both have one and the implied `norm_cs/norm_py` has median 0.9975 with p10 0.9309 /
  p90 1.0329 - the .cs holds at most 239 sessions of time-of-day history against Python's 1,187.
- **This run cannot say one word about realtime processing.** The entire realtime tail is sealed.
  100 % of the evidence here is NT8 **historical** replay. Spec trap 1 is therefore *unresolved*,
  not resolved: if historical and realtime processing differ, nothing in this report detects it.
- **Two data-coverage holes exist between the two files and are not logic differences.** 65 export
  minutes on 2026-07-17 10:54-11:58 are absent from the Python substrate, 12 substrate minutes on
  2026-06-11 10:33-10:44 are absent from the export, and the substrate lacks the export's
  2026-07-31 17:00 bar. **155 of the 202 voteOK mismatches inside WARM (77 %) fall on 2026-07-17 and
  the session immediately after it.**

---

## 5. The snapshot

| field | value |
|---|---|
| source | `C:\NT8_ForwardLogs\export\we_p1pct_p1pct.csv`, opened FileShare.ReadWrite, never written |
| snapshot | `out/cs_export_snapshot.csv` |
| sha256 | `403131d10ab7027d7bbb904204f3409ff6b993daa0a947e703e26ff34ce99999` |
| bytes | 33,497,518 |
| data rows | 353,891 (the spec quotes 353,878; a live strategy has appended since - **the entire delta is inside the seal**) |
| span | 2025-08-31 18:01:00 -> 2026-08-31 14:19:00 ET |
| duplicates / non-monotonic | 0 / 0 |
| **rows dropped by the seal (>= 2026-08-01)** | **28,819** |
| rows retained | 325,072 |

Timestamp alignment was verified on six real session boundaries spread across the span before the
join was trusted: the C# first bar of session and the Python first bar of session are the *same*
timestamp (18:01 ET after an 18:00 open, both bar-END stamped) and the C# `sessPnl` is exactly 0.00
on that bar. No +/-1-minute shift is applied anywhere in this program.

---

## 6. POST-HOC - the mechanism of the residual (NOT preregistered)

The spec's `if_none_reaches_99` branch requires the disagreeing rows to be characterised and the
feature that flips to be named. Doing so found a source asymmetry that **no single index shift can
express**, which is why all three preregistered arms had to miss:

- `run_we_w09.intraday_features` (and its vectorised twin `we_fastctx.fast_intraday_features:45-46`)
  already returns `atr14` **lagged one bar** - its own docstring says "ATR14 at i-1".
- `we_quality.build_context:44` / `we_fastctx.py:81` then lag it **a second time**:
  `atr_l = concat([[atr14[0]], atr14[:-1]])`.
- So `X['atr_l'][j]` is the ATR through bar **j-2**, while the numerators it divides - `c_l[j]` and
  `vwap_l[j]` - are bar **j-1** quantities. `dist_open` and `dist_vwap` are built from a
  one-bar-staler denominator than numerator. Verified numerically in the console: CONFIRMED.
- `WeeklyEdgeP1PCT_v3.cs:1136-1140` has no such asymmetry - `lagClose`, `lagVwap` and `lagAtr` are
  all frozen at the same instant by `CacheLagged()` (`:1198`).

Consequence: **the executable is a mixture of the two preregistered arms.** H_STALE matches the
.cs on the numerators and misses the ATR by one bar; H_FRESH matches the ATR and misses the
numerators by one bar.

One post-hoc arm, `H_STALE_CSATR` - identical to H_STALE except that `dist_open` and `dist_vwap` are
divided by the ATR the .cs actually holds; same mask, same entry sequence, same window, same
history construction, **one denominator and nothing else**:

| arm | score agreement | size agreement | disagreeing entries |
|---|---|---|---|
| H_FRESH_CSATR | 87.909 % | 97.733 % | 48 / 397 |
| **H_STALE_CSATR** | **100.000 %** | **100.000 %** | **0 / 397** |
| H_STALE2_CSATR | 86.146 % | 97.481 % | 55 / 397 |

**Status of this finding: a post-hoc explanation with zero free parameters, derived from two lines
of source. It changes no verdict in this run, quotes no economics, and promotes nothing. Confirming
it requires its own preregistered run whose arm set includes the mixed phase.**

It is also, separately, a **defect in the research chain** rather than a parity artefact: the
research object divides a bar-(j-1) numerator by a bar-(j-2) ATR in *every* wave that has ever used
`build_context`, contradicting the intent stated in `intraday_features`' own docstring. Whether that
should be corrected is a question for a locked challenge, because correcting it changes the research
object.

---

## 7. What this run does NOT establish

- **Agreement is not correctness.** If both objects are wrong in the same way, P0-P3 all pass. This
  run establishes *which object we trade*. It says nothing about whether that object is good.
- **Nothing about the live realtime object.** See section 4.
- **Nothing economic.** No dollar figure, no weekly figure, no promotion, no candidate. P4 is
  unreached by construction.
- **Nothing about DaysToLoad as a free parameter.** The finding that the deployed instance's quality
  history is truncated to 365 days is *recorded*, not acted on. Changing `DaysToLoad` would change
  the traded object and requires its own locked challenge.

---

## 8. Artifacts

| file | contents |
|---|---|
| `src/exectruth.py` | the whole program; three chain functions copied verbatim with one added output/index each, every copy asserted bit-identical to its canonical original before use (harness checks A-E, all PASS) |
| `out/console.txt` | full program output including the gate table |
| `out/gates.json` | machine-readable gate results, including the post-hoc block under its own key |
| `out/parity_bars.csv` | 325,006 joined bars: both closes, both voteOK, both t0..t3, both qty, both action codes, the C# score/size, the evaluation mask and the warm flag |
| `out/disagreements.csv` | 211,148 rows - every disagreeing bar in every compared field with both sides' values, plus every entry/exit-bar mismatch and every P3 score mismatch |
| `out/cs_export_snapshot.csv` | the read-only snapshot the whole run is computed from |

---

## 9. Prohibitions honoured (spec section 4)

No order, deploy, enable, disable, stop or modify on any account. No edit to any .cs file or to
anything under `research/weekly_edge/src/`. No read of any session >= 2026-08-01 - 28,819 rows
dropped and counted before the first statistic. No Databento, no DOM / Level-II / Market Replay. No
parameter fitted; zero free parameters by construction. No promotion. **No p-value anywhere** - with
n ~ 325,006 the gates are agreement thresholds, as the spec requires.
