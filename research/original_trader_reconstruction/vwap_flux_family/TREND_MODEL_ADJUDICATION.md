# TREND MODEL — ADJUDICATION (directive v4.0 §25)

**Written** 2026-08-24. **Scope:** what official material actually constrains about VWAP
Flux's trend, an honest audit of our `T_C` implementation, and a small *literal* family to
test. **Discipline:** one status token per claim — FACT / REPRODUCED / INFERENCE / UNKNOWN /
FALSIFIED. Fit score never selects a vendor semantic.

---

## 0. The three objects that must never be blended

The directive names them; this file keeps them apart everywhere.

| # | object | whose behaviour | evidence class available |
|---|---|---|---|
| **O1** | **Vendor trend DIRECTION** — what makes `Signal_Trend` positive or negative | ninZa's indicator | manual §2.4/§2.5, §1 overview, microsite wording, product-page alphabet |
| **O2** | **Vendor trend STRENGTH** — what makes `Signal_Trend` ±2 rather than ±1 | ninZa's indicator, **only from 2026-02-24** | product-page alphabet (endpoints) + manual §1 sentence; mechanism undocumented |
| **O3** | **The ORIGINAL STRATEGY's USE of trend** — what the trader's wrapper does with the series | the trader | screenshots, weekly fingerprints; no code, no oracle |

**FACT (code audit):** in `vwap_flux_family/src/run_r7_signal_id.py` a **single** array `tr`
performs three jobs at once — signal direction and rail selection (lines ~117–131),
`QtyPerTrend` episode reset (lines 111–113), and optionally the exit (lines 137–142).
`run_r7b_signal_id.py` inherits the same coupling. **Therefore no result we currently hold
separates O1 from O3, and the Quantity-cap schedule is silently determined by whichever O1
member is selected.** Every trend conclusion in `SIGNAL_TREND_IDENTIFICATION.md` is a
conclusion about the *composite*, not about O1.

---

## 1. What official material actually constrains (FACT unless marked)

**Manual §2.4, verbatim:**
> "Trend Period": defines the **averaging period of price** used to determine the market trend.

**Manual §2.5, verbatim:**
> "Trend MA type": The moving average type (can choose from 11 popular moving-average types)

**Manual §1 overview, verbatim — this is the O1/O2 split, stated by the vendor:**
> **Trend**: Helps traders identify the **current trend** and evaluate its **strength**
> through the **accumulated volume reflected in the Fair Value Plot**.

**Manual §2.8, verbatim:** `"Level: Median (%)"`: defines the threshold for the **Fair Value
plot** within the VWAP bands. → **FairValue ≡ the Median-level rail** (FACT). Trader's
Median = 50.

**Manual §4 alphabet (p.15), verbatim:** `Signal Trend: 1 = bullish, -1 = bearish`.
Current product page (S1, read 2026-08-24, REPRODUCED from `VWAP_FLUX_VERSION_TIMELINE.md`):
`Signal_Trend: 2 = uptrend strong, 1 = uptrend weak, -2 = downtrend strong, -1 = downtrend weak`.
**Neither alphabet contains 0** (FACT) — see §5.1.

**Microsite/marketing triple:** "Price vs. Fair Value Plot / Cloud Break / Cloud Slope".
**Status: REPRODUCED from `VENDOR_SIGNAL_USAGE_MODEL.md` §A.5, labelled MARKETING there,
sourced to S4/S5. I did not re-fetch the microsite in this pass, and no verbatim capture of
that sentence exists in-repo beyond that line.** Treat the *three ingredient names* as the
constraint; treat any combination rule as unsourced.

**So the binding constraints are:**
- O1 direction is built from: **price vs Fair Value**, **price vs the band (break)**, and
  **band slope**.
- **`Trend Period` averages PRICE** — it does not smooth the cloud, and it is not documented
  as a slope lookback.
- O2 strength comes from **cumulative volume/delta alignment**, surfaced via the Fair Value
  Plot.
- **The panel contains no strength threshold, no slope lookback, and no hysteresis
  parameter** (13 fields, re-verified from the preset screenshots pp.13–15 and from
  OTRIMG-0146). Anything we add on those axes is a free constant we invented.

---

## 2. Is `T_C` a faithful reading or a convenient one?

**`T_C` as implemented** (`run_r7_signal_id.py`, `trend_states`, lines 57–62):
`slope = ema20[i] − ema20[i−1]`; latch **up** iff `close > FairValue AND slope > 0`; latch
**down** iff `close < FairValue AND slope < 0`; otherwise **hold**; initial state `0`.

**Honest verdict: CONVENIENT, not faithful.** It is not *contradicted* by any vendor
sentence, but it is not a reading *of* them either. Itemised:

| # | issue | severity |
|---|---|---|
| 1 | **It substitutes the slope of a price MA for the vendor's "Cloud Slope".** The vendor names the cloud and the MA as *different objects*; we conflated them. This is the single largest liberty. | **high** |
| 2 | **It drops "Cloud Break" entirely.** The break condition was tested as a *separate rival member* (`T_A`) rather than as a *conjunct*, so the vendor's three-ingredient description was never actually implemented as a three-ingredient rule. | **high** |
| 3 | **The slope lookback is 1 bar — an undeclared free constant.** Nothing in the panel or manual says 1. On 1-min bars a one-bar difference of an EMA20 is a near-noise quantity; `Trend Period` therefore enters O1 only through the EMA's smoothing, not through any documented role. | **high** (violates the R7 spec's "no free constants" claim) |
| 4 | **"Hold when the two clauses disagree" was introduced without warrant.** *Partially rehabilitated* — see §5.1: the documented alphabet has no 0, so a latch is in fact *implied*. But the specific hold rule (hold on disagreement of an invented pair) is still ours. | medium |
| 5 | **A `0` warm-up state exists in our code and gates signals off (`if ti != 0`).** The vendor alphabet admits no 0 state. | medium |
| 6 | It uses raw `close` against Fair Value while also computing an EMA — i.e. the MA is used for one clause and ignored for the other, with no stated reason. | medium |

**What `T_C` gets right (FACT):** it uses the documented Fair Value object; it treats
`Trend Period` as an average of **price** and never lets the EMA touch the cloud geometry
(the constraint recorded in `VF_CLEANROOM_SPEC.md`); it produces a signed, persistent state
series as the alphabet requires.

**Countervailing note against over-correcting:** `SIGNAL_TREND_IDENTIFICATION.md` records
that structurally *diverse* trend members all plateau at 0.48–0.52, i.e. the weekly-aggregate
metric has little power on this axis. **That is a reason to choose the trend rule on vendor
warrant rather than on fit — which is exactly what the ruling directs.** It is not a reason
to keep `T_C` because it happened to rank first.

---

## 3. Free-constant audit of the current trend layer (FACT)

The R7 spec asserts "no free constants; only STRUCTURE varies". Undeclared constants
actually present:

| constant | where | documented? |
|---|---|---|
| EMA slope lookback = **1 bar** | `T_C`, line 58 | no |
| CVD slope lookback = **20 bars** | `run_r7b_signal_id.py` line 139 | no |
| Delta proxy = `sign(close − open) × volume` | `run_r7b_signal_id.py` line 130 | no (a bar-data stand-in; vendor defines delta per tick vs bid/ask) |
| Warm-up state `0` gating signals off | `trend_states` / `run_member` | contradicts the alphabet |
| EMA seed `out[0] = x[0]` | `ema()` | convention only |

Disclose these in the next spec; the "no free constants" claim as written is **FALSIFIED**
for the trend layer.

---

## 4. O1 — a SMALL literal family of direction rules to test

Design rules: every member uses only documented objects (the five rails, Fair Value = Median
rail, `Trend Period`, `Trend MA Type`); every member has **zero free constants**; every
member latches (§5.1). Six members, plus the incumbent kept for continuity.

| id | rule (up-state; down mirrored) | vendor warrant | free consts | status |
|---|---|---|---|---|
| **TD-0** *(incumbent)* | `close > FV` ∧ `EMA(TP)` rising over 1 bar; hold on disagreement | partial (§2) | 1 | = `T_C`; keep for continuity, **not** literal |
| **TD-1** SMOOTH-FV | `MA(close, TrendPeriod, MAType) > FV` | §2.4 + §2.8 + triple-ingredient "Price vs Fair Value Plot" | 0 | = `T_D`, already in the cluster — **arguably the most literal single-condition member we have** |
| **TD-2** RAW-FV | `close > FV` | "Price vs Fair Value Plot" read as raw price | 0 | **control**: makes `Trend Period` inert. If it matches TD-1, the panel's Trend fields are doing nothing in our clone — worth knowing |
| **TD-3** CLOUD-BREAK | latch up on `close > Max` rail, down on `close < Min` rail | "Cloud Break" | 0 | = `T_A`, already in the cluster |
| **TD-4** CLOUD-SLOPE | `FV[i] > FV[i − TrendPeriod]` | "Cloud Slope"; reuses the panel's own number as the lookback | 0 | **NEW — never tested.** The only member that makes "cloud slope" quantitative without inventing a constant. Caveat: reads `Trend Period` as a lookback, which strains §2.4's "averaging period of price" |
| **TD-5** TRIPLE-AND | latch up only when **all three** hold: `MA(close,TP) > FV` ∧ `close > Max` ∧ `FV[i] > FV[i−TP]`; mirror for down; hold otherwise | the marketing triple read as a **conjunction** | 0 | **NEW — never tested.** This is the first time the vendor's three-ingredient description would actually be implemented as three ingredients |
| **TD-6** TRIPLE-COUNT | `score = (#up conditions) − (#down conditions)` over the same three; latch on \|score\| ≥ 2 | the triple read as a **score** | 0 | **NEW — never tested.** See §5.2: it also produces the 4-state alphabet with no new parameter |

**Secondary axis, one flip, only if a member wins on warrant:** `MAType` ∈ {EMA (trader's
panel), SMA}. The trader's field reads **EMA** (FACT, OTRIMG-0146), so EMA is the default and
SMA is a robustness check, not a search dimension.

**What each member would falsify.** TD-2 matching TD-1 ⇒ `Trend Period` is inert in our clone
(a defect, not a finding). TD-5/TD-6 beating TD-1 on the catastrophe-week and count
fingerprints ⇒ the triple is real and our single-condition members were under-specified.
TD-4 alone performing well ⇒ the trend is a cloud-geometry object, not a price object, and
§2.4 is being consumed differently than we assume.

---

## 5. O2 — strength, kept strictly separate

### 5.1 The alphabet forces a latch (FACT, and it rehabilitates one of our choices)

Both documented `Signal_Trend` alphabets — `{1, −1}` before 2026-02-24 and `{2, 1, −1, −2}`
after — **contain no 0**. `Signal_Trade` has a documented `0` on the current product page;
`Signal_Trend` never does. Therefore the vendor's trend series is *always signed*, which
means **some hysteresis / latch rule is required by the specification itself.** Our "hold the
state" choice is thereby upgraded from invention to alphabet-implied; only the *particular*
hold condition remains ours. Conversely, our warm-up `0` state (§3) is **not** admissible and
should be replaced by a first-classification rule.

### 5.2 Strength members

Applicable **only from 2026-02-24** (before that date, O2 does not exist and the correct
model is TS-0 by construction).

| id | rule | vendor warrant | free consts | status |
|---|---|---|---|---|
| **TS-0** NONE | no strength dimension | manual §4 alphabet; mandatory for 2026-01-11 → 2026-02-23 | 0 | baseline |
| **TS-1** CVD-SLOPE-AGREE | strong iff `sign(CVD[i] − CVD[i−20]) == direction` | §1 "strength through the accumulated volume" | **1** (the 20) | = existing `strong_only`; **disfavoured on the parameter-count argument below** |
| **TS-2** CVD-LEVEL-SIGN | strong iff `sign(session-anchored CVD level) == direction` | §1 + the series' own words `Signal_Cum_Delta: 1 = positive, −1 = negative` — "positive/negative" reads as a **level** sign, not a slope | 0 | **NEW — never tested; strictly more literal than TS-1** |
| **TS-3** CONDITION-COUNT | strong iff all three TD-5 conditions hold; weak iff exactly two | the triple read as a score (TD-6) | 0 | **NEW — never tested** |

**The parameter-count argument (INFERENCE, HIGH).** The 13-field panel contains **no strength
threshold** (FACT, re-verified). Whatever the vendor computes for ±2 vs ±1 must therefore be
**parameter-free**. TS-2 and TS-3 satisfy that; TS-1 does not (its 20-bar window is ours).
This is a structural constraint, entirely independent of any backtest.

**Two rival explanations of the 2026-02-24 "Signal_Trend was upgraded" entry — KEEP BOTH:**
- **(A) delta-based strength** — favoured by manual §1's own sentence and by the fact that
  `Signal_Cum_Delta` had just been added (2026-02-09), 15 days earlier.
- **(B) condition-count strength (TS-3)** — favoured because it needs no new parameter and
  because manual §1 describes the *display* (Fair Value Plot intensity), which predates the
  upgrade and so cannot by itself explain a *series* change.
Neither is decidable from public material. **UNKNOWN.**

**REPRODUCED (do not re-litigate on fit):** the existing `strong_only` gate moved the leader
from 0.476 → 0.492 in-sample and gave mixed OOS results (`runs/OTR_R8_JUNE2026/REPORT.md`
Part A). `SIGNAL_TREND_IDENTIFICATION.md`'s conclusion stands: **the strength dimension is
not identifiable from weekly aggregates on 1-min bars.** It should therefore be fixed by
warrant (TS-2/TS-3 over TS-1) and then held constant, not searched.

---

## 6. O3 — the trader's USE of trend

| id | rule | precedent | status |
|---|---|---|---|
| **TU-0** SIGNAL_TRADE-ONLY | enter on `Signal_Trade`; wrapper never reads `Signal_Trend`; exits = stop + session only | **the vendor's own canonical wrapper**: manual §4 "If Signal_Trade equal to 1, you can enter long here" + tutorial `mtMNjOQtfQE`; and B.4 — every published vendor wrapper exits via ATM stop/target | **never tested under the R7 clean-room cloud.** Every R7/R7b member carries a rule-based exit (`X_OPP`/`X_FLIP`/`X_MED`). A stop-and-session-only exit was tried in the *pre-clean-room* VF1–VF3 passes and rejected there (`TRACK_VF_REPORT.md`), on a cloud we have since replaced |
| **TU-1** TREND-GATE | take `Signal_Trade` only when `Signal_Trend` agrees | none documented | **flag: probably redundant.** §2.11's cap counts "same-direction signals … within a single trend", i.e. the indicator already emits signals inside a trend context. A wrapper re-gate would double-count — the same error class flagged for Qty/Split/CloseThr in `VENDOR_SIGNAL_USAGE_MODEL.md` Layer-C item 2 |
| **TU-2** TREND-FLIP-EXIT | exit when `Signal_Trend` flips | **no vendor precedent** (B.4: exits are ATM) | = `X_FLIP`; kept because the trader is not the vendor, but it must be labelled trader-side hypothesis |
| **TU-3** STRENGTH-SELECT | trade only \|`Signal_Trend`\| = 2 | possible **only from 2026-02-24** | = `strong_only`; carries a dated prediction, see §7 |

**INFERENCE (MEDIUM) worth recording:** the trend module is the **least customised** part of
the trader's panel. He matched the vendor's suggested `MA Type` exactly (EMA) and moved
`Trend Period` only 14 → 20, while overriding every other group aggressively (Levels
95-75-50-25-5 vs every preset; Qty 3 vs 5; Split 5 vs 15; CloseThr 10 vs 70). If he accepted
the vendor's trend semantics roughly as shipped, then **getting the vendor's trend model
literally right matters more than fitting our own** — which is precisely the directive's
instruction, arrived at independently.

---

## 7. Version discipline (binding on every trend claim)

| window | O1 | O2 | O3 |
|---|---|---|---|
| 2026-01-11 → 2026-02-08 | direction only | **does not exist** | `Signal_Cum_Delta` unavailable |
| 2026-02-09 → 2026-02-23 | direction only | **does not exist** as a `Signal_Trend` state | `Signal_Cum_Delta` readable |
| 2026-02-24 → present | direction | ±2/±1 available | TU-3 possible |

Trader's first visible VF panel: **2026-02-13** (OTRIMG-0117) — inside the middle band.
Any strength-gated member fitted across the full in-sample window is **anachronistic for the
first ~6 of 17 weeks**. **Credit where due (FACT):** `run_r7b_signal_id.py` handles this
correctly — `UPGRADE = 2026-02-24` and the gate applies only when `post[i]` (lines 24, 90–92).
Preserve that discipline in every successor run.

**Dated prediction (falsifiable):** if the wrapper reads `Signal_Trend` at all (TU-1/TU-2/TU-3),
the 2-state → 4-state change should leave a **behavioural discontinuity at 2026-02-24** —
e.g. code testing `== 1` would, post-upgrade, match only *weak* uptrends. The trader's
late-February behaviour shift is already on record as date-aligned
(`VWAP_FLUX_VERSION_TIMELINE.md` §5, status HYPOTHESIS). A member family that reproduces
that discontinuity *without* being tuned to it would be strong evidence for O3 reading
`Signal_Trend`.

---

## 8. Correction carried forward — "Trend Period 14" (FACT, re-verified today)

- **14 / EMA is the value shown in all FIVE suggested-settings screenshots** (manual pp.13–15;
  re-verified pixel-level in this pass). It is a *suggested-preset* value.
- **It is not a proven shipped factory default.** No public statement of factory defaults
  exists; establishing one requires installing the product (UNKNOWN; purchase gate CLOSED per
  EV-039).
- **Distinguish this from the CloseThreshold-80 case:** 80 appears **nowhere** in public VF
  material as a Close Threshold (see `CLOSE_THRESHOLD_ADJUDICATION.md` §6), whereas 14 appears
  in every preset. "14 is an example value" is right in spirit; the precise statement is
  "14 is the value in all five published presets, with no factory default published".
- **The trader's panel reads `Trend Period` = 20 and `Trend MA Type` = EMA** — FACT,
  full labels legible in OTRIMG-0146 (2026-05-23), consistent with OTRIMG-0132 (2026-04-02).
  Earlier internal notes carrying "EMA?" with a question mark are superseded.
- Net: a **mild** customisation (+6 bars, same MA type) against a backdrop of aggressive
  customisation elsewhere. See §6.

---

## 9. Cross-file evidence: the manual's one worked example constrains the trigger, not just the close

Measured this pass from the §2.12 figure (full provenance in
`CLOSE_THRESHOLD_ADJUDICATION.md` §2): the illustrated **Sell** bar's High penetrates the
band's **lower third** (band rows ≈118–205; bar High row 176), while its Close (row 261)
finishes ≈0.6–0.75 bar-ranges **below** the band's lower edge; the preceding bars trade
inside the band.

**INFERENCE (MEDIUM; one low-resolution marketing figure, unknown preset, unknown prior
trend context):** consistent with a **Min/Lower-rail touch + close-beyond-the-rail
rejection** (`P_IN` + `C_REC`), and **inconsistent with a pullback to the Median / Fair Value
rail** on that bar — which is what the current cluster **leader** (`T_C|P_MED|C_DIR|H1a|X_OPP`)
uses. This does not overturn the leader; it means the leader's pullback depth has one piece
of vendor-figure evidence against it and none for it. Add to the discriminator list.

**Cheap image test, not yet run (UNKNOWN):** manual p.9 shows the same NQ MAR26 1-minute
window twice at `VWAP Amount = 5` and `= 10`, with "▲ VF" buy markers drawn in both panels.
If the markers sit on the **same bars**, `Signal_Trade` placement is invariant to band width
— a first-order constraint on both the trigger and the rail formula. Attempted in this pass
and **not resolved** (blob detection contaminated by the overlay text boxes); needs a proper
marker-template match.

---

## 10. Status ledger

| claim | status |
|---|---|
| §2.4 / §2.5 / §1 / §2.8 / §4 quotations in §1 | **FACT** (re-extracted from the PDF today) |
| `Trend Period` averages PRICE; the MA does not smooth the cloud | **FACT** (§2.4) + REPRODUCED (`VF_CLEANROOM_SPEC.md`) |
| FairValue ≡ the Median-level rail | **FACT** (§2.8) |
| Direction ingredients = price-vs-FV, cloud break, cloud slope | **REPRODUCED** from `VENDOR_SIGNAL_USAGE_MODEL.md` §A.5; MARKETING-sourced; **not re-fetched this pass** |
| Strength comes from accumulated volume via the Fair Value Plot | **FACT** (manual §1) |
| `Signal_Trend` alphabet contains no 0 in either build ⇒ a latch is required | **FACT** |
| `Signal_Trend` upgrade 2026-02-24 = 2-state → 4-state | **INFERENCE (MEDIUM-HIGH)** — two documented endpoints; changelog does not say |
| Mechanism of strength (delta vs condition-count) | **UNKNOWN** — both kept |
| `T_C` is a faithful reading of vendor material | **FALSIFIED** — it is a convenient composite (§2) |
| `T_C`'s 1-bar slope lookback and TS-1's 20-bar window are undeclared free constants | **FACT** (code audit) |
| "R7 varied structure only, no free constants" | **FALSIFIED** for the trend layer |
| One `tr` array serves direction + Qty-episode + exit ⇒ O1 and O3 unidentified | **FACT** (code audit) |
| §2.11's cap scope: zone-episode vs trend-episode | **UNKNOWN** — the vendor's own definition and example sentences disagree |
| Trend members all plateau at 0.48–0.52 ⇒ weekly aggregates lack power on this axis | **REPRODUCED** (`SIGNAL_TREND_IDENTIFICATION.md`) |
| TD-4 / TD-5 / TD-6 / TS-2 / TS-3 / TU-0 | **never tested** |
| All five presets show Trend Period 14 / MA Type EMA | **FACT** (re-verified today) |
| Trader's panel: Trend Period 20, MA Type EMA | **FACT** (OTRIMG-0146; OTRIMG-0132) |
| Trend is the least-customised group in the trader's panel | **FACT** (values) / **INFERENCE (MEDIUM)** (its significance) |
| Which trend rule the trader's build actually computes | **UNKNOWN** — under H3/H4 (EV-039) it may be his own reimplementation, in which case vendor semantics constrain but do not determine it |

**Companion files:** `SIGNAL_TREND_IDENTIFICATION.md`, `SIGNAL_TRADE_HYPOTHESES.md`,
`VENDOR_SIGNAL_USAGE_MODEL.md`, `VF_CLEANROOM_SPEC.md`, `VWAP_FLUX_VERSION_TIMELINE.md`,
`CLOSE_THRESHOLD_ADJUDICATION.md`, `runs/OTR_R7_VF_SIGNAL_ID/REPORT.md`,
`runs/OTR_R8_JUNE2026/REPORT.md`.
**No `.py` file, backtest, or original screenshot was modified in producing this file.**
