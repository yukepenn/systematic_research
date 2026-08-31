# G3_EXECTRUTH_02 - EXECUTABLE OBJECT TRUTH, SECOND ATTEMPT

**Run:** `G3_EXECTRUTH_02_20260831` - spec committed before any corrected-arm statistic was
recomputed - GENESIS III Wave A, EXECUTABLE TRUTH lane
**LIVE ENABLED = NO - $0 spent - no order, deploy, enable, backtest or CrossTrade call of any kind**
**Evidence status:** VERIFICATION. Nothing is selected, tuned or promoted by this run beyond the
economics Q4 was preregistered to unlock on a Q1 pass.

---

## 1. The Q1 verdict, in one sentence

**H_CORRECTED - the research chain's context with the second ATR lag at `we_fastctx.py:81` removed
and nothing else touched, read at the stale index shift - reproduces the deployed object's quality
score and size on 397 of 397 evaluated entries, 100.000 % on both, strictly beating all three
preregistered controls (C1 96.977 %, C2 87.909 %, C3 96.725 % on score), so Q1 is recorded PASS
against its raised 99.5 % bar and the executable object is REPRODUCED EXACTLY.**

The predecessor's failure is not reinterpreted by this. `G3_EXECTRUTH_01`'s P3 verdict was and
remains **FAILED**: its arm family was one-dimensional and could not express a mixture. This run
tested a different hypothesis about the object's structure, stated in advance, with zero free
parameters, and it survived a bar that was deliberately raised.

---

## 2. The gate table (printed by the program - `out/console.txt` section 10)

| GATE | SPEC | OBSERVED | VERDICT |
|------|------|----------|---------|
| Q0 | reproduce predecessor H_STALE 96.977 % / 98.992 % within 0.05 pp | 96.977 % / 98.992 % (delta 0.0003 / 0.0004 pp) | **PASS** |
| Q1 | score >=99.5 % AND size >=99.5 % AND H_CORRECTED strictly beats C1, C2, C3 | score **100.000 %**, size **100.000 %**; C1 96.98, C2 87.91, C3 96.73 | **PASS** |
| Q2 | WARM: voteOK >=99.5 %, t0..t3 >=99.5 %, entry Jaccard >=0.99, count within 2 % | voteOK 99.921 %; t0..t3 99.82/99.86/99.90/99.85; J 0.99065; +0.313 % | **PASS** |
| Q3 | >=95 % of residual disagreements assigned to a named, evidenced cause | 201,247 / 211,136 = **95.316 %** assigned; **4.684 % unexplained** | **PASS** |
| Q4 | runs only if Q1 passes | computed - section 6 | **PASS** |

The realtime column is **UNDECIDABLE with n = 0** after the seal, exactly as in the predecessor.
No gate is decided on it and none is reported as a rate. **No p-value appears anywhere.**

---

## 3. Q1 - the deciding gate, in full

Population: the **397** bars on which the export shows the executable evaluated an entry
(`myQty == 0 && wantLong && UseQualitySize`, derived from the export's own `qty` / `voteOK` /
`stopped` columns), exec-native framing - qCount from 0, `QualMinHist` 100, `QualWindow` 250 -
identical to the predecessor's. All 397, including the 100 the executable zeroes by warm-up.

| arm | construction | score agree | size agree | score (qC>=250) | size (qC>=250) | disagreeing entries |
|---|---|---|---|---|---|---|
| **H_CORRECTED** | atr b-1, features b-1 | **100.000 %** | **100.000 %** | **100.000 %** | **100.000 %** | **0** |
| C1 (predecessor H_STALE) | atr b-2, features b-1 | 96.977 % | 98.992 % | 96.599 % | 98.639 % | 12 |
| C2 (fresh index shift) | atr b-1, features b | 87.909 % | 97.733 % | 83.673 % | 97.279 % | 48 |
| C3 (both ATR lags removed) | atr b, features b-1 | 96.725 % | 99.496 % | 96.599 % | 100.000 % | 13 |

"Strictly beats" was **defined before it was measured** (console section 2b): strictly greater
agreement, a tie counts as a loss, on **both** metrics against **all three** controls. Both strict
wins hold.

Note C3: removing *both* ATR lags reaches 99.496 % on size and would have passed a size-only
threshold. It fails the score clause and loses to H_CORRECTED on both, which is what the control was
there to detect - the correction is a **single** lag, not "as few lags as possible".

### Why this is a hypothesis and not a fit

H_CORRECTED has **zero free parameters** and is fully determined by two source files that can be
read without any data at all:

- `we_fastctx.py:46` (and `run_we_w09.intraday_features`, whose own docstring says "ATR14 at i-1")
  returns `atr14` already lagged one bar.
- `we_fastctx.py:81` / `we_quality.py:44` lag the already-lagged array **a second time**, so
  `X['atr_l'][j]` is the ATR through bar **j-2** while `c_l[j]` and `vwap_l[j]` are bar **j-1**.
- `WeeklyEdgeP1PCT_v3.cs` `CacheLagged()` `:1214-1218` enqueues **this** bar's true range and sets
  `lagAtr = trSum/trQ.Count`; `:1237` sets `lagClose = c`. Both are frozen at the same instant, so
  the executable's numerator and denominator share one bar. **There is no asymmetry on that side.**

The honesty requirement that travels with it, stated in the spec and honoured here: this arm was
**first observed post-hoc in the predecessor**, so its 100 % there did not confirm it. What makes it
testable is that it moves no threshold, no window, no feature and no sign - it removes one line - and
this run stated the prediction in advance and let it fail against a bar raised from 99.0 % to 99.5 %.

### Harness identity (so the two runs are comparable)

`Q0` reproduces the predecessor's H_STALE arm to **0.0003 pp** on score and **0.0004 pp** on size.
Seven harness checks pass before any statistic: A (votes copy bit-identical to `run_we_w97.votes`),
B (the 32-voter identity), C (`causal_score_lag(0)` == `run_we_w37.causal_score`), D (`gfills_path`
byte-identical to `run_we_w98.gfills`), E (`per_ctr = True`), **F** (the parameterised context at
`extra_atr_lag=True` is bit-for-bit `we_fastctx.fast_build_context`), **G** (re-applying the removed
line to the no-lag ATR restores the canonical `atr14`). Harness H confirms the three contexts differ
in `atr_l`, `dist_open` and `dist_vwap` **and nothing else**, and that
`lag(XC.atr_l) == X.atr_l` and `lag(XN.atr_l) == XC.atr_l`.

---

## 4. Q2 - state and action parity on the declared WARM sub-span

WARM is `export session index >= 51`, derived from `.cs:1067` (`tilt` is identically 0 until
`sessCloses.Count > TiltSma = 50`) - **taken unchanged from the predecessor, which fixed it from
source before computing anything**. 254,874 of 325,006 joined bars (78.4 %), from 2025-11-10 18:01.

| clause | spec | observed | verdict |
|---|---|---|---|
| voteOK agreement (WARM) | >= 99.5 % | 99.9207 % | pass |
| t0 / t1 / t2 / t3 (WARM) | >= 99.5 % | 99.8187 / 99.8576 / 99.9027 / 99.8458 % | pass |
| entry-bar Jaccard (WARM) | >= 0.99 | 0.99065 | pass |
| trade-count difference (WARM) | <= 2 % | +0.313 % (320 vs 319) | pass |

Identical to the predecessor's WARM diagnostic to every printed digit, as it must be - the harness
did not change. WARM exit-bar Jaccard is 0.93636, reported but not gated.

**The FULL-SPAN entry Jaccard of 0.85176 (+1.795 % count) is recorded and NOT re-litigated.** It is
a warm-up artefact of the executable itself: 33 of 35 C#-only entries and 27 of 28 Python-only
entries are pre-warm. It did not pass in the predecessor, it does not pass here, and this run does
not claim it does.

---

## 5. Q3 - every residual assigned to a named, evidenced cause

The population is the same one the predecessor tabulated: every (bar, field) disagreement in the
eleven exported state fields on the joined bars, plus every entry/exit-bar action mismatch, plus
every score/size mismatch under H_CORRECTED. **211,136 residuals.** The taxonomy and its priority
order were fixed in console section 2(d) **before any of it was computed**.

Causes 1-4 are decided by **forward simulations of named `.cs` blocks**, run over the export's own
bars from the export's first row - i.e. over the deployed instance's own 365-day load span, which is
not the campaign's history. A cause is assigned only when the simulation **reproduces the
executable's own value** on that bar.

| simulation | source block | reproduces the export column on |
|---|---|---|
| `norm` / `ratio` | `.cs:963-970`, `:1116-1119`, `:1210-1212` | 98.713 % of all joined bars |
| `tilt` | `.cs:1064-1073` | 99.569 % |
| `dL` / cumDelta | `.cs:975`, `:1126`, `:1220-1222` | 99.968 % |
| `bmom` | `.cs:1023-1059` | **100.000 %** |
| `nThr` from the simulated `norm` | `.cs:1121-1124` | 99.998 % |

A fifth instrument, the **hybrid vote**, re-runs the canonical Python chain with five inputs replaced
on the joined window by the executable's own values (`tilt`, `bmom`, `ratio`, simulated `norm`, `dL`)
and nothing else changed:

| field | Python agrees with .cs | hybrid agrees with .cs |
|---|---|---|
| nMem | 96.4948 % | 99.5649 % |
| nThr | 95.1527 % | 99.9982 % |
| dL | 99.9194 % | 100.0000 % |
| voteOK | 99.1726 % | 99.7674 % |
| t0 / t1 / t2 / t3 | 97.52 / 99.00 / 98.12 / 98.02 % | 99.52 / 99.63 / 99.55 / 99.57 % |

### Assignment

| cause | n | share |
|---|---|---|
| `TILT_WARMUP_LT_51_SESSIONS` | 70,131 | 33.216 % |
| `NORM_OWN_LOAD_SPAN_SIM` | 48,822 | 23.123 % |
| `CS_INPUT_TILT` | 31,114 | 14.736 % |
| `NORM_NOT_YET_AVAILABLE` | 27,535 | 13.041 % |
| `NTHR_FOLLOWS_NORM_SIM` | 15,754 | 7.462 % |
| **`UNEXPLAINED`** | **9,889** | **4.684 %** |
| `BMOM_WARMUP_LT_14_RTH_DAYS` | 4,775 | 2.262 % |
| `DATA_COVERAGE` | 2,274 | 1.077 % |
| `BMOM_OWN_SLOTHIST_SIM` | 239 | 0.113 % |
| `CS_INPUT_BMOM` | 180 | 0.085 % |
| `CUMDELTA_OWN_SESSION_PATH_SIM` | 158 | 0.075 % |
| `ACTION_PRE_WARM` | 116 | 0.055 % |
| `CUMDELTA_VOLUME_SERIES_DIFFER` | 104 | 0.049 % |
| `CS_INPUT_RATIO_NORM` | 31 | 0.015 % |
| `ACTION_FOLLOWS_VOTEOK` | 12 | 0.006 % |
| `CS_INPUT_DL` | 2 | 0.001 % |
| **ASSIGNED** | **201,247** | **95.316 %** |

**Q3 PASS at 95.316 %, with 4.684 % (9,889 residuals) UNEXPLAINED. That fraction is not rounded
away and no rule was added after the counts were seen.** The margin over the bar is 0.32 pp; this is
the weakest gate in the run and it is reported as such.

### The three questions inherited from the predecessor

**(a) `ratio` - ANSWERED.** 76,357 of 80,539 (**94.81 %**) are reproduced by simulating the `.cs`'s
own `rngHist` over its own load span - 27,535 where the `.cs` has fewer than 20 prior observations of
that minute-of-day and writes `ratio = 1.0000` exactly, and 48,822 where both sides have a `norm` and
the `.cs`'s own 60-observation median over its own 239 sessions reproduces its value. The predecessor
could only *localise* this to `norm`; it is now **assigned to a mechanism**, and the mechanism is the
deployed instance's `DaysToLoad = 365` history, not a logic difference.

**(b) `dL` - BOUNDED, and the answer is that the volume series DO differ, on 104 bars.** Re-running
the `.cs`'s own cumDelta recursion on the **Python** volume series reproduces the `.cs` on **158** of
the 262 mismatches (so those are the `.cs`'s own session-local reset path, not a data difference) and
reproduces **Python** on **104** (so on those 104 bars no recursion on the Python volume can produce
the `.cs`'s value - the two volume series differ there). The export writes no volume column, so this
is the strongest statement the snapshot permits; it converts an open question into a bounded one.
104 bars of 325,006 is 0.032 %, and `dL` moves no action on any of them.

**(c) coverage - PARTLY ANSWERED, and my declared carry was too short.** 2,274 residuals fall in a
mismatched-minute session or the one immediately after. Of the 202 voteOK mismatches inside WARM, 17
are coverage and 38 are unexplained.

### The unexplained residual, characterised (description, not assignment)

The 9,889 unexplained residuals are highly structured, and naming where they sit is not the same as
assigning them - none of the following was used to raise the assigned fraction:

- **`ratio`, 3,184, every one of them on 2026-07-21 ... 2026-07-30** (export sessions 230-237), i.e.
  strictly *after* the one-session carry I declared for the 2026-07-17 coverage hole. The 65
  export-only minutes of 2026-07-17 change that session's running range from 10:54 onward, and those
  corrupted values enter the `.cs`'s per-minute-of-day `rngHist` permanently. **The declared
  one-session carry underestimates how long a coverage hole persists in a per-tod history** - that is
  a defect in my taxonomy, recorded, not repaired after the fact.
- **`tilt`, 1,380, all inside one session** (2025-12-21 18:01 -> 2025-12-22 17:00, plus one bar). The
  tilt simulation reproduces the executable on **238 of 239 sessions**. The single failure is the
  session close of **2025-12-19**, where `close - SMA50` is **-6.11 points on an SMA of 26,094.61** -
  **the smallest margin in the entire 239-session span** (the next smallest is 9.93). It is a sign
  flip on a knife edge, not a different computation.
- **vote-family (`nMem`/`t0..t3`/`voteOK`), 5,316, of which 4,384 are on 2025-08-31 and 2025-09-01** -
  the export's **first two sessions**, where the `.cs`'s 13 virtual SolarWave members are themselves
  cold (`.cs:1015` freezes `mPend` while `barCount < 20`). `mem` was **not** one of the five inputs
  the hybrid substitutes, so the hybrid cannot reproduce those bars by construction.
- **`EXIT_BAR`, 9**, every one at the session flatten minute (`16:41`, once `12:41`).

---

## 6. Q4 - ECONOMICS. A CORRECTION TO THE RECORD, NOT A CANDIDATE.

Unlocked only by the Q1 PASS. Computed on the **T2_P1SIZE01 size-invariance identity**
(`pnl_i = s_i * pnl_per_contract_i`, verified there at max error 0.00e+00), **asserted here, not
assumed**: the trade schedule `(et, xt, direction)` is identical for all 2,401 trades under every
size vector compared, so the same schedule is genuinely being repriced.

262 trades entered before the canonical scoring window opens (2022-07-01); both size vectors assign
them 1 by construction and their contribution to the difference is **$0.00**. They are excluded so
the net levels are the levels the campaign quotes.

| | canonical window 2022-07-01 -> 2026-08-01 | pre-burn (entries < 2026-05-31) | companion: export overlap |
|---|---|---|---|
| trades / weeks | 2,139 / 211 | 2,072 / 202 | 390 / 49 |
| trades sized differently | 95 (4.44 %) | 93 (4.49 %) | 11 (2.82 %) |
| their share of the research-chain net | 3.07 % | 3.34 % | -3.63 % |
| their share of the H_CORRECTED net | 1.11 % | 1.26 % | -3.46 % |
| **research chain as quoted** (ATR double-lagged) | **$331,241** ($1,570/wk) | $337,952 ($1,673/wk) | $56,191 ($1,147/wk) |
| **H_CORRECTED** (the executable's semantics) | **$324,674** ($1,539/wk) | $330,826 ($1,638/wk) | $56,285 ($1,149/wk) |
| **difference** | **-$6,567 (-$31/wk)** | **-$7,126 (-$35/wk)** | +$93 (+$2/wk) |
| top decile by abs(per-contract P&L) | -$5,719 = 87.1 % of the total (214 trades) | -$7,074 = 99.3 % (208 trades) | $0 = 0.0 % (39 trades) |
| the remaining trades | -$848 (1,925 trades) | -$51 (1,864 trades) | +$93 (351 trades) |

Decomposition of the two components of the correction, on the canonical window:
phase only (C1, ATR left uncorrected) **$319,250**; ATR only (C2, fresh phase) **$331,388**; both
together (H_CORRECTED) **$324,674**. Neither component alone is the executable.

**Reading.**

1. The correction is **small and negative**: the quoted P1 research figure sits about **2.0 % above**
   the executable's on the canonical window, **$31 per week** against an object quoting ~$1,570/week.
2. **It does NOT concentrate in the burned period.** The pre-burn difference (-$7,126) is *larger in
   magnitude* than the full-window difference (-$6,567), so the burned window 2026-05-31 -> 2026-07-31
   contributes **+$559** back. A reader asking "is this an artefact of the burned data?" gets no.
3. It is **almost entirely a top-decile phenomenon** - 87.1 % of the difference on the canonical
   window and 99.3 % pre-burn sits in the 10 % of trades with the largest per-contract P&L. The
   ranking is taken on the **size-invariant** per-contract P&L so the decile cannot itself be moved
   by the size vector under test.
4. **This is a correction to the record, not an improvement and not a `P1_vNext`.** The deployed
   strategy has *always* used the corrected semantics; it was never using the defect. That the
   research representation earns $6,567 more over four years than the object it claims to represent
   is a **measurement of representation error**, and its sign carries no recommendation. Changing
   what the deployed strategy does remains a separate locked challenge that this run may not open.

---

## 7. What this run establishes and what it does not

**ESTABLISHED.** Which object we trade, bar for bar. The deployed executable's quality score and size
are reproduced **exactly** - 397 of 397 - by the research chain's own code with one line removed. The
research chain's **double-lagged ATR is now a CONFIRMED DEFECT**: `X['atr_l'][j]` is the ATR through
bar j-2 while the numerators it divides are bar j-1 quantities, in *every* wave that has ever called
`build_context`, contradicting the intent stated in `intraday_features`' own docstring. Every P1
figure produced by that chain carries the correction as a known offset, now measured at -2.0 % of net
over the canonical window.

**NOT ESTABLISHED.**

- **Agreement is not correctness.** If both objects were wrong in the same way, every gate here would
  still pass. This run says nothing about whether the traded object is good.
- **Nothing about the live realtime object.** 100 % of the evidence is NT8 *historical* replay; the
  entire realtime tail (112 rows) is inside the seal and was dropped. If historical and realtime
  processing differ, nothing here detects it.
- **Nothing that authorises modifying the deployed strategy.** A defect in the research chain is not
  evidence the executable should change - the executable never had the defect. Patching
  `we_fastctx.py:81` would change 100+ historical runs and is its own decision with its own record.
  **Nothing was patched here.**
- **Nothing about `DaysToLoad` as a free parameter.** The finding that the deployed instance's
  quality and range histories are truncated to its own 365-day load - now the *measured* cause of
  94.81 % of the `ratio` residual - is recorded, not acted on.
- **4.684 % of the residual population remains unexplained**, and one of my own declared rules (the
  one-session coverage carry) is now known to be too short.

---

## 8. Artifacts

| file | contents |
|---|---|
| `src/exectruth2.py` | the whole program; the predecessor's harness reused verbatim, plus one parameterised line in a copy of `fast_build_context`, plus five forward simulations of named `.cs` blocks |
| `out/console.txt` | full program output including the gate table printed by the program |
| `out/gates.json` | machine-readable gate results, all arms, all simulations, all Q4 blocks |
| `out/residual_classes.csv` | 211,136 rows - every residual disagreement with both sides' values and its assigned cause |
| snapshot | `runs/G3_EXECTRUTH_01_20260831/out/cs_export_snapshot.csv`, sha256 `403131d1...99999`, 33,497,518 bytes - **verified, not re-taken** |

## 9. Prohibitions honoured

No order, deploy, enable, disable, stop or modify on any account. **No CrossTrade or NinjaTrader tool
call of any kind.** No edit to any `.cs` file and no edit to anything under
`research/weekly_edge/src/` - the double lag is diagnosed here, never patched. No read of any session
>= 2026-08-01: **28,819 rows dropped and counted before the first statistic**, 325,072 retained. The
export was not re-snapshotted; its sha256 was verified against the spec and asserted. No parameter
fitted - zero free parameters by construction. No promotion. No p-value anywhere.
