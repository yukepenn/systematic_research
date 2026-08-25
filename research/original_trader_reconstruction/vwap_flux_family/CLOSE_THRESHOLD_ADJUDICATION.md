# CLOSE THRESHOLD — ADJUDICATION (directive v4.0 §24)

**Written** 2026-08-24. **Scope:** the vendor semantics of `Signal: Close Threshold (%)`
and the status of our competing readings. **Discipline:** every claim carries exactly one
status token — FACT / REPRODUCED / INFERENCE / UNKNOWN / FALSIFIED. Backtest score is
**not** admissible as evidence of vendor semantics (owner ruling, adopted below).

---

## 0. Ruling adopted

> **BACKTEST SCORE IS NOT EVIDENCE OF VENDOR SEMANTICS.**

Consequences enacted in this file:

1. The prior conclusion "H1a dominates" (`runs/OTR_R7_VF_SIGNAL_ID/REPORT.md` pass-1
   verdict 1) is **downgraded from a semantic finding to a fit observation**. It is not
   retracted as a fit; it is stripped of its semantic authority.
2. At least two rivals stay alive. In fact **four** must stay alive, because §2.12 of the
   vendor manual is internally inconsistent in three separate ways (§2 below) and the
   owner's two named rivals ("H-MANUAL", "H-STRICT") do not exhaust the literal readings.
3. The poor fit of the manual-literal reading is treated as **a diagnostic pointing at our
   own upstream**, not as a refutation of the manual (§7, the inversion).

---

## 1. Primary source, re-verified today (FACT)

Source: `research/original_trader_reconstruction/vwap_flux_family/ninZaVWAPFlux-TraderManual.pdf`
(15 pp.; CMS `createdAt` 2026-02-02; SHA-256 recorded in `VWAP_FLUX_VERSION_TIMELINE.md` §S2).
Text extracted and pages re-rendered in this pass; nothing below is quoted from an internal
summary.

**§2.12 "Signal Close Threshold", p.11 — three distinct statements:**

- **(a) Headline sentence, verbatim:**
  > "Signal Close Threshold": Defines the **minimum percentage** of the candle's close
  > relative to its full range (from Low to High) for the candle to qualify as a valid signal.

- **(b) Figure caption, verbatim (rendered text inside the chart image):**
  > Close − Low ≥ 70% → valid Sell signal

- **(c) Two prose bullets, verbatim:**
  > For a **Sell** signal, the candle is considered valid if its close lies within the
  > **upper 70%** of the candle's range measured from the Low.
  > For a **Buy** signal, the close must fall within the **lower 70%** of the range
  > measured from the High.

**§4 signal alphabet, p.15, verbatim:** "Signal Trend: 1 = bullish, -1 = bearish /
Signal Trade: 1 = bullish, -1 = bearish". (No `0`; no ±2. Manual predates the 2026-02-09
and 2026-02-24 builds.)

**Suggested settings, pp.13–15 — all FIVE presets re-verified pixel-by-pixel today
(FACT):**

| preset | Anchor | Amount | Trend Period / MA | Max/Up/Med/Low/Min | Qty | **CloseThr** | Split |
|---|---|---|---|---|---|---|---|
| 1 Minute chart | 20 | 7 | **14 / EMA** | 80/60/50/40/10 | 5 | **70** | 15 |
| 3 Minute chart | 60 | 10 | **14 / EMA** | 90/60/50/40/20 | 5 | **70** | 15 |
| 5 Minute chart | 120 | 5 | **14 / EMA** | 100/70/50/30/0 | 5 | **70** | 15 |
| 1000 Volume ("Highly Recommend") | 30 | 5 | **14 / EMA** | 80/60/50/20/10 | 5 | **70** | 15 |
| ninZaRenko 12/4 | 3 | 5 | **14 / EMA** | 80/60/50/20/10 | 5 | **70** | 30 |

Minor correction to internal record: `VENDOR_SIGNAL_USAGE_MODEL.md` §A.4 calls these
"four suggested presets"; there are **five** (p.13 ×2, p.14 ×2, p.15 ×1). The preset panels
show 12 rows beginning at `Anchor Period (Minutes)` — **no `Volume Base` row and no
`Zone Period` row is visible in any preset screenshot** (FACT). Panel label is
`Signal: Quantity Per Trend (%)` — a `(%)` suffix on what §2.11 describes as a count (FACT;
noted, not explained).

---

## 2. NEW EVIDENCE — the §2.12 figure contradicts the §2.12 text (FACT, measured)

The chart image embedded on p.11 marks one worked example: a yellow "VF ▼" **Sell** marker
above a red candle. I measured that candle in the image's native raster (embedded XObject,
1026 × 548 px, DCTDecode; signal candle occupies columns 298–307):

| feature | image row | note |
|---|---|---|
| upper dotted reference line | 175–176 | passes through the candle top; no upper wick above it |
| red body top (= High = Open) | 177 | |
| red body bottom (= **Close**) | ≈261 | |
| lower dotted reference line (= **Low**) | 267–268 | short lower wick occupies rows ≈262–266 |

**Derived (FACT, ±3 pp for edge/antialias ambiguity on a 92-px range):**

- Range = 92 px.
- **(Close − Low) / Range ≈ 7 %.**
- (High − Close) / Range ≈ 93 %.

**Therefore the vendor's own illustrated "valid Sell signal" candle closes ≈7 % above its
low — a near-maximal bearish close.** It satisfies **neither** the figure's own caption
("Close − Low ≥ 70 %") **nor** the Sell prose bullet (which requires the close in the upper
70 % region, i.e. ≥ 30 % from the Low). This is a documented inconsistency inside a single
section of the vendor manual, reproducible by anyone re-rendering p.11.

**Secondary measurement, status AMBIGUOUS (deliberately not resolved):** the vertical
double-headed "100%" arrow sits at columns ≈286–290 with arrowhead tips at rows ≈178 and
≈261. Two readings survive and I keep both:
- **(i)** it spans High → **Close** and annotates *this candle's score* as 100 % (measured
  93 %); or
- **(ii)** it spans High → Low with ~5–7 px symmetric inset and annotates *the full range*
  as the 100 % denominator.
The inset magnitudes (5 px top, 7 px bottom) are near-symmetric, which mildly favours (ii).
**The contradiction in the paragraph above does not depend on which reading is correct** —
(Close − Low) is ≈7 % of the range either way.

**Geometry of the same bar relative to the cloud (FACT, measured at column 312, one bar
right of the signal):** the coloured band spans rows ≈118–205 (cyan 118–144, purple
146–205). The signal bar's High (176) lies **inside** the band's lower third; its Close
(261) lies ≈56–70 px **below** the band's lower edge, i.e. ≈0.6–0.75 bar-ranges outside it.
The preceding candles are drawn inside the band. **INFERENCE (MEDIUM, one low-resolution
marketing figure):** the illustrated trigger is a rally *into* the lower band region that is
rejected and closes back *outside* it — consistent with a Min/Lower-rail touch plus a
close-beyond-the-rail confirmation (our `P_IN` + `C_REC`), and **inconsistent with a
pullback all the way to the Median / Fair Value rail on that bar** (our leader's `P_MED`).
Recorded here because it is the same figure; see `TREND_MODEL_ADJUDICATION.md` §9.

---

## 3. The reading space, stated formally

Let **x ≡ (Close − Low) / (High − Low)** ∈ [0, 1] (x = 1 → close at the high), and
**T ≡ CloseThreshold / 100**. Every candidate reading is a choice on two independent axes:

- **Orientation** — must the close sit *toward* the signal direction (sell → low close) or
  *against* it (sell → high close)?
- **Comparator** — is T a **minimum score** the candle must reach (higher T ⇒ stricter), or
  an **extremal window width** (higher T ⇒ looser)?

That is a 2 × 2. All four cells are named; two were already in our grids under other names.

| cell | rule (SELL / BUY) | ≡ our label | admits at T=70 | admits at T=10 | vendor-text warrant |
|---|---|---|---|---|---|
| **C1** contrarian × minimum | x ≥ T / x ≤ 1−T | **H1c** ("manual-verbatim") | ~30 % | ~90 % | headline (a) + caption (b) |
| **C2** contrarian × window | x ≥ 1−T / x ≤ T | **H1b** ("extreme against") | ~70 % | ~10 % | prose bullets (c) read as regions |
| **C3** momentum × minimum | x ≤ 1−T / x ≥ T | **NEW — H-FIGURE** | ~30 % | ~90 % | headline (a) + the drawn example |
| **C4** momentum × window | x ≤ T / x ≥ 1−T | **H1a** ("strict momentum-close") | ~70 % | ~10 % | none in vendor text |

(Admission percentages are of the *CLV axis*, not of the empirical bar population; the true
pass rate depends on the CLV distribution of 1-min NQ bars, which is not uniform. The
"≈90 % of candles pass" figure for C1 at T=10 is REPRODUCED from
`runs/OTR_R7_VF_SIGNAL_ID/REPORT.md` amendment 1, not re-measured here.)

### 3.1 Arithmetic facts that need no backtest (FACT)

1. **C1 ≡ ¬C4 and C2 ≡ ¬C3**, exactly, at every T — except on the boundary set x = T.
   Our two most-tested members (H1a, H1c) are **exact logical complements**: they partition
   the candidate bar set. A grid that "prefers H1a over H1c" is reporting *which half of the
   candidate set carries the fit*, not which sentence the vendor wrote.
2. The boundary set is **not** measure-zero on a discrete tick grid: a 10-tick-range bar
   closing exactly 1 tick off its low has x = 0.10 = T exactly. Both members currently use
   non-strict `≤` / `≥`, so such bars pass **both** rules. Small, but it means the partition
   in (1) is a partition-with-overlap and the overlap grows as bar ranges shrink.
3. **C1 ↔ C2 and C3 ↔ C4 are related by T → 1−T.** The orientation axis is the only
   genuinely new degree of freedom; the comparator axis is a reparameterisation.
4. **The word "minimum" in the headline is a monotonicity claim.** Under C1/C3, raising T
   raises the bar (stricter) — consistent. Under C2/C4, raising T *loosens* the filter —
   the parameter would run backwards relative to its own definition sentence. **Our
   empirically preferred H1a (C4) contradicts the manual's headline sentence on
   monotonicity.** This is a semantic argument with no backtest content.

### 3.2 Vendor-text support tally

| §2.12 element | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| (a) headline "minimum … to qualify" | ✔ | ✘ | ✔ | ✘ |
| (b) caption arithmetic "Close − Low ≥ 70 %" | ✔ | ✘ | ✘ | ✘ |
| (c) prose bullets as regions | ✘ | ✔ | ✘ | ✘ |
| the drawn example (x ≈ 0.07 = valid Sell) | ✘ | ✘ | ✔ | ✔ |
| preset T=70 behaves like a real filter | ✔ | ~ | ✔ | ~ |

**No cell is supported by all four elements.** C1 and C3 each carry two supports; C2 and C4
each carry one. **FACT: the vendor document does not determine its own parameter.**

---

## 4. Adjudicated status of each reading

- **C1 / H1c — ALIVE, co-leading on vendor warrant.** This is the owner's "H-MANUAL" in its
  strongest form (headline + caption). Tested (R7 pass 2). Currently mid-pack on fit.
- **C3 / H-FIGURE — ALIVE, co-leading on vendor warrant, NEVER TESTED.** Newly promoted by
  §2 of this file. It is the only cell that honours the headline's monotonicity *and*
  matches the vendor's single worked example. **Highest-value untested member in the whole
  VF programme.** Note: at the trader's T=10 it is near-non-binding, exactly like C1.
- **C4 / H1a — ALIVE as an empirical member, DEMOTED as a semantic claim.** Retains the best
  aggregate fit; retains one vendor support (the drawn example's orientation); contradicts
  the headline's monotonicity. Status of "H1a dominates": **FALSIFIED as a semantic claim,
  REPRODUCED as a fit ranking.**
- **C2 / H1b — REINSTATED from "REJECTED (degenerate)" to ALIVE-but-disfavoured.** Correction
  on record: H1b is not an arbitrary strawman — **it is the manual's two prose bullets read
  as regions.** It was rejected on the grounds that it produced near-zero trades, i.e. on
  fit, which the ruling forbids as a semantic verdict. It stays disfavoured because the
  drawn example contradicts it and because its near-zero trade count is itself a *structural*
  incompatibility with a ~1,214-trade target (a count argument, admissible), not merely a
  worse score.

**Owner's two named rivals, mapped:** H-MANUAL := {C1, C2} (the two literal-text readings,
kept separate because the text is inconsistent); H-STRICT := C4. **Both alive, as directed,
plus C3.**

### 4.1 Correction to an internal description (FACT)

`SIGNAL_TRADE_HYPOTHESES.md` line 9 glosses H1c as "exclude only the 10 % extreme AGAINST —
nearly-open". **That is backwards.** C1/H1c at T = 10 rejects a Sell when x < 0.10, i.e.
when the close sits in the bottom 10 % of the range — which for a Sell is the extreme
**TOWARD** the signal (a maximal down-close), and is precisely the set H1a *requires*. The
complementarity in §3.1(1) makes this unavoidable. The gloss should read: *excludes only the
10 % extreme toward the signal.* Fix on next edit of that file.

---

## 5. What the R7/R7b evidence actually says (re-derived from stored results)

Re-read of `runs/OTR_R7_VF_SIGNAL_ID/out/r7_summary.csv` and `r7b_summary.csv`. No backtest
was run; no `.py` file was touched.

**(i) The pass-1 "domination" was against a strawman (FACT).** `run_r7_signal_id.py` line 195
enumerates `H in ("H1a","H1b")` only. C1/H1c was **not in the pass-1 grid at all**. So
"the entire top-15 is H1a" means "H1a beat H1b" — i.e. the momentum-window cell beat the
contrarian-window cell. It says nothing about the minimum-comparator row, which contains
both best-warranted readings.

**(ii) In the matched pass-2 design, H1a's edge is small and not established (FACT).**
r7b contains 48 cells in which (trend, pullback, close-confirm, exit, gate) are held fixed
and only H1a ↔ H1c varies:

| statistic | value |
|---|---|
| cells where H1a beats H1c | **28 of 48** (58 %) |
| sign test, two-sided | **p = 0.31** — not significant |
| **median** paired Δ(H1c − H1a) mean-distance | **+0.0095** |
| mean paired Δ | +0.047 (sd 0.115); driven by 5 outlier cells (Δ ≥ 0.217) |
| trimmed mean Δ (drop those 5) | +0.020 |
| cells with \|Δ\| < 0.05 | 22 of 48 |

For scale: the entire surviving OTR-VF-CAND1 cluster spans mean distance **0.476 – 0.514**.
A median matched-cell gap of **0.0095** is *inside* the cluster's own width.
A naive paired t on the 48 cells gives t ≈ 2.8, but the cells share only six trend/pullback
structures and 17 overlapping windows, so neither the t nor the sign test has a valid null.
**The defensible statement: H1a's advantage is small relative to the plateau and is NOT an
established separation.** The owner's ruling and the arithmetic agree.

**(iii) Where H1c is better (FACT).** Best catastrophe geometry in the entire cluster belongs
to a **C1/H1c** member: `T_D|P_IN|C_REC|H1c|X_FLIP` reproduces −26,535 in the 3/22–27 week
against the −42,235 target (**63 %**), versus the H1a leader's −9,730 (**23 %**). Reproducing
the trader's worst week is the hardest single fingerprint to fake, and the manual-orientation
member is the only one that comes close. (Counterweight, also FACT: that member swung to
−32.5k on a +8.6k target week in the R8 true-OOS test and was demoted for instability —
`runs/OTR_R8_JUNE2026/REPORT.md` verdict 3.)

---

## 6. The Close-Threshold-70 correction, carried forward (FACT, re-verified)

- **All public ninZa material shows Close Threshold = 70**, never 80: all five suggested
  presets (§1 table, re-verified today) and the §2.12 worked example.
- **"80" appears in public VF material only as `Level: Max (%)`** (1-Minute and ninZaRenko
  presets). The earlier internal line "manual-shown …/4/80/30" in `TRACK_VF_REPORT.md` §1 is
  **wrong on all three numbers**: "4" is §2.11's *example sentence* ("if Signal Quantity Per
  Trend = 4 …"), 80 is a Level value, and 30 is the Split of the ninZaRenko preset only
  (every other preset shows 15). This correction is now re-verified from the PDF, not merely
  inherited.
- **There is no public statement of shipped factory defaults** — establishing one would
  require installing the product (UNKNOWN, and gated: purchase gate CLOSED per EV-039).
- **The trader's panel reads Close Threshold = 10** (OTRIMG-0146, 2026-05-23, full labels
  legible; consistent with OTRIMG-0132, 2026-04-02) — a deliberate customisation under
  **every** reading in §3.

### 6.1 Same keystroke, opposite intent

This is the load-bearing consequence and it must not be smoothed over:

| reading | what "10" does |
|---|---|
| **C1 / C3** (minimum comparator) | **turns the close filter essentially OFF** (~90 % of candles qualify) |
| **C4** (our H1a) | **turns the close filter to MAXIMUM strictness** (~10 % qualify) |
| **C2** | maximum strictness in the *contrarian* direction |

The two best vendor-warranted cells (C1, C3) both say **the trader disabled the vendor's
close-location filter.** Our fitted model assumes he maximised it. These are not shades of
the same claim; they are opposite behavioural inferences from one number, and they license
opposite downstream research.

**INFERENCE (MEDIUM), for the "disabled" branch:** if he turned this filter off, the
selectivity in his real system lives somewhere we are not modelling — most plausibly the
mutable wrapper head rows above `Volume Base` (Feb `[?, unchecked, checked, 15]` → Apr-2
`[30?, 16, 0, 10, 15]` → Apr-17 `[16, 0, 9, 15]` → Aug-14 `[cut-num, CHECKBOX]`, per
`screenshot_forensics/VF_PANEL_COMPLETENESS_NOTE.md` §Q1c). Coherence check, **non-decisive
in both directions:** his other deltas are mixed — Split 5 (vs 15) and Levels 95-75-50-25-5
(wider than every preset) *increase* signal availability, consistent with "loosen the
indicator, filter in my own code"; Qty 3 (vs 5) *decreases* it. Coherence does not adjudicate.

---

## 7. THE INVERSION — a poor manual fit indicts our upstream, not the manual

**Stated explicitly, as directed.**

The premise that makes this work: **under C1/C3 at T = 10 the close filter is a near-no-op.**
A near-no-op filter does not shape the output — it *exposes* whatever the upstream produced.
Under C4 at T = 10 the filter removes ~90 % of candidates and therefore *masks* upstream
over-generation. Consequently:

> If our cloud, trend state, pullback trigger, or wrapper over-generates candidates, then
> **only the strict cell can hit the trader's trade count**, and the grid will select C4 for
> reasons that have nothing to do with what the vendor meant. C4 would be functioning as a
> **count-calibration surrogate for a missing upstream selector.**

**This is not hypothetical; the stored numbers show the signature (FACT):** across the 48
matched cells, mean realised trades are **1,259 (H1a) vs 1,744 (H1c)** against a **~1,214**
target. The manual-orientation members overshoot; the strict members land near target. The
correct inference from that pair is **"our upstream over-generates by roughly 40 % once the
close filter is neutralised"** — a statement about our upstream, not about the manual.

**Note the compression, which is itself diagnostic (FACT):** C1 vs C4 differ by ~9× on the
CLV axis but only ~1.39× in realised trades, because `QtyPerTrend = 3` and `Split = 5`
saturate the stream. Two consequences: (1) the weekly trade-count metric has **low power** to
separate these readings — a further reason the fit ranking is weak evidence; (2) whatever
selectivity the trader actually used, most of it was already spent by the suppression
parameters before the close filter ever bound.

### 7.1 Named upstream suspects (each documented, each absent or unresolved in our clone)

| # | suspect | status |
|---|---|---|
| U1 | **Static S/R zone module.** §2.14 `Zone Period` is a real, documented module; §2.11's *definition* sentence scopes the Quantity cap to "the same **support or resistance zone**" while its *example* sentence says "within a single **trend**". Our clone has **no zones**, so it caps per trend-episode. Wrong suppression scope inflates candidates. | absent from clone; vendor text self-ambiguous |
| U2 | **The real `Signal_Trade` trigger.** "Pullback signals" is all the public record gives; `P_IN / P_Q75 / P_MED` are our guesses. §2's figure geometry disfavours `P_MED` for the one worked example. | UNKNOWN |
| U3 | **Trend model.** `T_C` substitutes an EMA-slope for the vendor's *cloud* slope and introduces an undeclared 1-bar lookback; trend boundaries also set the Qty-cap episodes. | see `TREND_MODEL_ADJUDICATION.md` |
| U4 | **Rail formula.** percentile-linear vs min-max unresolved (`VF_CLEANROOM_SPEC.md`); min-max rails are materially wider, changing touch frequency. | OPEN |
| U5 | **Volume/delta input class.** Per EV-039 his build most plausibly computes from bar data; our delta proxy is `sign(close−open)·volume`. | OPEN |
| U6 | **Wrapper head rows** — e.g. entries-per-direction = 2 and the mutable head block; not implemented. | absent from clone |

### 7.2 Falsifiable predictions (these, not the fit ranking, decide the question)

- **P1 (decisive).** Add *any* correct upstream selector (a zone module for U1; a stricter
  trigger for U2). If the H1a preference is a count-calibration artefact, **C1/C3 members
  should improve more than C4 members and the ordering should narrow or invert.** If C4
  keeps its edge after the upstream tightens, that is genuine evidence for the momentum-window
  orientation.
- **P2.** Sweep T for C1/C3 from 10 → 70 with everything else frozen. Under the
  minimum-comparator readings, selectivity must return monotonically. If a mid-T value
  reproduces the trader's fingerprint far better than his own panel value of 10, that is
  evidence the *panel number is not being consumed with vendor semantics* — i.e. support for
  the reimplementation branch (H3/H4), where his "Close Threshold" field need not mean what
  ninZa's means.
- **P3.** Test **C3 / H-FIGURE**, which no grid has ever contained. It is one boolean flip
  from existing code paths.
- **P4 (image, cheap, no backtest).** Manual p.9 shows the *same* NQ MAR26 1-minute window
  twice, at `VWAP Amount = 5` and `= 10`, with "▲ VF" buy markers drawn in both panels. **Do
  the markers sit on the same bars?** If yes, `Signal_Trade` placement is invariant to band
  width — a first-order constraint on U2 and U4. **UNKNOWN — attempted in this pass and not
  resolved** (white-blob detection was contaminated by the overlay text boxes; needs a proper
  marker-template match).
- **P5 (verification debt).** Re-read the §2.12 figure at higher magnification to settle the
  "100 %" arrow ambiguity of §2 (i) vs (ii). Does not change the contradiction, but would
  strengthen or weaken C3's warrant relative to C1's.

---

## 8. Status ledger

| claim | status |
|---|---|
| §2.12 headline / caption / bullets as quoted in §1 | **FACT** (re-extracted from the PDF today) |
| All five presets show CloseThr 70, Trend Period 14, MA Type EMA | **FACT** (re-verified pixel-level today) |
| "Close Threshold 80" appears nowhere in public VF material | **FACT** |
| Trader's panel: Close Threshold = 10 | **FACT** (OTRIMG-0146; OTRIMG-0132) |
| The §2.12 worked-example Sell candle has x ≈ 0.07 | **FACT** (measured, ±3 pp) |
| §2.12's figure contradicts §2.12's caption and Sell bullet | **FACT** |
| The "100 %" arrow spans High→Close vs High→Low | **UNKNOWN** (both kept) |
| C1 ≡ ¬C4, C2 ≡ ¬C3 (excluding x = T) | **FACT** (arithmetic) |
| C4/H1a contradicts the headline's monotonicity | **FACT** (arithmetic + text) |
| H1a's fit advantage over H1c is small and unestablished | **FACT** (28/48, p = 0.31, median Δ 0.0095) |
| "H1a dominates" as a statement about vendor semantics | **FALSIFIED** |
| "H1b is degenerate and rejected" as a semantic verdict | **FALSIFIED** — H1b is the prose-bullet reading; kept, disfavoured |
| C3 / H-FIGURE is the best-warranted untested cell | **INFERENCE (HIGH)** |
| Our upstream over-generates ~40 % once the close filter is neutralised | **INFERENCE (MEDIUM-HIGH)** — from matched trade counts |
| The trader disabled (rather than maximised) the close filter | **INFERENCE (MEDIUM)** — follows under C1/C3, i.e. under the two best-warranted cells |
| Which cell the trader's own build implements | **UNKNOWN** — under H3/H4 his field need not carry vendor semantics at all |

**Companion files:** `SIGNAL_TRADE_HYPOTHESES.md` (cluster membership),
`VENDOR_SIGNAL_USAGE_MODEL.md` (three-layer separation),
`TREND_MODEL_ADJUDICATION.md` (§25 sibling ruling),
`runs/OTR_R7_VF_SIGNAL_ID/REPORT.md`, `runs/OTR_R8_JUNE2026/REPORT.md`.
**No `.py` file, backtest, or original screenshot was modified in producing this file.**
