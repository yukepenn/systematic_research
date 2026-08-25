# EV-039 RE-AUDIT — narrowing an over-reaching inference

Written 2026-08-24 under MASTER DIRECTIVE v4.0. Owner adjudication: the CONCLUSION
attached to EV-039 ("therefore his 2026 stack is his OWN reimplementation, not the
licensed indicator") is TOO STRONG and is withdrawn. This document rebuilds the
argument from the sources, separates observation from interpretation, keeps five
hypotheses alive, retracts one line of invalid evidence, and states the narrow claim
that survives.

Status vocabulary used strictly, one per claim: **FACT / REPRODUCED / INFERENCE /
UNKNOWN / FALSIFIED**. No backtest P&L is used anywhere below to select a vendor
semantic.

Scope note: nothing in this document changes any model, any parameter, or any run.
It changes only what we are entitled to say.

---

## 0. The document under audit

**FACT.** The source is `research/original_trader_reconstruction/vwap_flux_family/ninZaVWAPFlux-TraderManual.pdf`.
- 15 pages; SHA-256 `d34b50daa2db4caa28077efdccc6427263b57bdd0fd84ddc422b9d96e500390b`.
- Embedded PDF metadata: `author = "TRDpremium 01"`, `creator/producer = Microsoft® Word 2016`,
  `creationDate = modDate = D:20260128180445+07'00'` (2026-01-28 18:04:45, UTC+07:00).
- Section 2.1 ("Volume Base") begins on page 5 and ends on page 6 immediately before
  "2.2. Anchor Period (Minutes)". Page 5 additionally carries two embedded raster
  images (501×385 px and 491×34 px). Page 6 carries no images.

**FACT (correction to an existing ledger note).** `vwap_flux_family/OWNER_REPORT_RECONCILIATION.md`
line 14 dates the manual "2026-02-02". The PDF's own embedded creation timestamp is
**2026-01-28**. Both are recorded; the embedded timestamp is the stronger source. The
difference is immaterial to any argument here but the discrepancy is logged rather than
silently resolved.

**INFERENCE (version scope, load-bearing later).** A manual authored 2026-01-28
describes the product as of that date. EV-019 records the vendor changelog as adding
`Signal_Cum_Delta` on 2026-02-09 and upgrading `Signal_Trend` from 2-state to 4-state on
2026-02-24. The trader's VWAP-Flux-layout frames run 2026-02-13 → 2026-08-14. So the
manual we hold **predates the trader's entire observed VF era except its first five days**.
Whether §2.1's historical-calculation behaviour was itself changed after 2026-01-28 is
**UNKNOWN** — the changelog entries we hold do not mention it, and absence of a
changelog line is not evidence of absence of a change.

---

## PART A — WHAT THE MANUAL PROVES

### A.1 Section 2.1, quoted completely and verbatim

Transcribed by text extraction (PyMuPDF + pdftotext, identical results). The only
alteration is that the bullet glyph, which is the Wingdings-mapped private-use
character U+F0B7, is rendered here as `•`; the sub-bullet glyph is the literal
letter `o` in the source and is reproduced as such. Line breaks follow the source.

> **2. Parameter**
>
> **2.1. Volume Base**
>
> • "BidAskPrice_RealVolume": This mode should be used for instruments with real
> volumes (futures & stocks).
>
> Buy volume & sell volume are defined as follows:
> o Buy Volume: If the price of a tick is greater than or equal to the ask price, the real
> volume of the tick is categorized as buy volume and added to the total buy volume
> of the bar that the tick belongs to.
> o Sell Volume: If the price of a tick is less than or equal to the bid price, the real
> volume of the tick is categorized as sell volume and added to the total sell volume
> of the bar that the tick belongs to.
> In this mode, if Tick Replay is enabled, the indicator functions on both historical &
> real-time data. Please visit https://ninjatrader.com/support/helpGuides/nt8/en-
> us/?tick_replay.htm for instructions on how to enable Tick Replay.
> If Tick Replay is disabled, the indicator functions only on real-time data and there are
> no calculations on historical data. Any actions that lead to chart reloading will erase all
> calculations.
>
> *[page break, p5 → p6]*
>
> • "UpDownTick_RealVolume": This mode should be used for instruments with real
> volumes (futures & stocks).
>
> Buy volume & sell volume are defined as follows:
> o Buy Volume: If a tick is up or remains up, the real volume of the tick is categorized
> as buy volume and added to the total buy volume of the bar that the tick belongs
> to.
> o Sell Volume: If a tick is down or remains down, the real volume of the tick is
> categorized as sell volume and added to the total sell volume of the bar that the
> tick belongs to.
> In this mode, the indicator functions on both historical & real-time data. However,
> please be advised that historical and real-time calculations of the same bar may not be
> 100% identical, due to technical limitations.
>
> • "UpDownTick_UnitVolume": This mode is the one & only choice for instruments
> without real volumes (forex, CFDs, indices).
>
> Buy volume & sell volume are defined as follows:
> o Buy Volume: If a tick is up or remains up, a unit volume (1) is credited as buy
> volume for the tick and added to the total buy volume of the bar that the tick
> belongs to.
> o Sell Volume: If a tick is down or remains down, a unit volume (1) is credited as sell
> volume for the tick and added to the total sell volume of the bar that the tick
> belongs to.
> In this mode, the indicator functions on both historical & real-time data. However,
> please be advised that historical and real-time calculations of the same bar may not be
> 100% identical, due to technical limitations.

That is the entirety of §2.1. Nothing has been omitted, paraphrased, or joined.

**The single sentence on which EV-039 rests, isolated:**

> "If Tick Replay is disabled, the indicator functions only on real-time data and there are
> no calculations on historical data."

**The immediately preceding sentence, which must be quoted with it:**

> "In this mode, if Tick Replay is enabled, the indicator functions on both historical &
> real-time data."

### A.2 The rest of page 5 (non-text context, so the quote is not read in isolation)

**FACT.** Page 5's larger embedded image (501×385) is a screenshot of the **vendor's own
parameter grid** for the product. Read directly from the image, its rows are:

`Parameters` group — Volume Base = `BidAskPrice_RealVolume` | Anchor Period (Minutes) = 20 |
VWAP Amount = 5 | Trend: Period = 14 | Trend: MA Type = `EMA` | Level: Max (%) = 100 |
Level: Upper (%) = 70 | Level: Median (%) = 50 | Level: Lower (%) = 30 | Level: Min (%) = 0 |
Signal: Quantity Per Trend = 4 | Signal: Close Threshold (%) = 80 | Signal: Split (Bars) = 30
— then a separate `General` group header — Zone Period = 3.

The smaller image (491×34) is a close-up of the single `Volume Base` row showing the value
`BidAskPrice_RealVolume`.

**FACT.** The vendor's own labels carry **colons** — `Trend: Period`, `Trend: MA Type`,
`Level: Max (%)`, `Signal: Quantity Per Trend`, `Signal: Close Threshold (%)`,
`Signal: Split (Bars)`. The trader's panel labels, read from OTRIMG-0146, are
**colon-less** — `Trend Period`, `Trend MA Type`, `Max Percent`, `Upper Percent`,
`Median Percent`, `Lower Percent`, `Min Percent`, `Signal Quantity Per Trend`,
`Signal Close Threshold (%)`, `Signal Split (Bars)`.

**FACT.** In the vendor grid, `Zone Period` sits under a **separate `General` group
header**, not inside the `Parameters` block.

### A.3 Section 4, page 15 — the vendor's documented intended architecture

**FACT.** Verbatim, complete:

> **4. NinjaScripts Signals**
> You can rely on the signals below to build your own strategy:
> • Signal Trend: 1 = bullish, -1 = bearish
> • Signal Trade: 1 = bullish, -1 = bearish
> Below is the example condition for this indicator based on the Signal_Trade:
> If Signal_Trade equal to 1, you can enter long here.
> Conversely, if Signal_Trade equal to -1, you can enter short here.
> Please follow the link below to find more information about Strategy Builder.
> https://youtu.be/mtMNjOQtfQE

### A.4 What Part A therefore establishes — and only this

**FACT (V-011).** The manual, as of 2026-01-28, states that in `BidAskPrice_RealVolume`
mode with Tick Replay disabled, **the indicator** functions only on real-time data and
performs no calculations on historical data.

**FACT.** The manual states the other two Volume Base modes function on both historical
and real-time data without any Tick Replay condition.

**FACT.** The manual's own §4 tells the customer to **build his own strategy** around
`Signal_Trend` / `Signal_Trade`. A user-authored NinjaScript strategy consuming vendor
signal series is the vendor's **documented, supported, recommended** usage pattern, not a
deviation from it.

**What Part A does NOT establish, and the manual nowhere addresses:**
1. What happens when the indicator is **instantiated from inside a strategy** rather than
   attached to a chart. §2.1 says "the indicator". Hosting context is not discussed
   anywhere in the 15 pages. **UNKNOWN.**
2. What happens under the **Strategy Analyzer** specifically. The Strategy Analyzer is
   never mentioned in the manual. **UNKNOWN.**
3. What the `Signal_*` series **contain** when no historical calculation occurs — zero,
   the neutral value, a stale carry, or an exception. **UNKNOWN.**
4. Whether the behaviour described on 2026-01-28 still held in the builds shipped after
   2026-02-09 and 2026-02-24. **UNKNOWN.**
5. Anything at all about what the original trader owned, installed, wrote, or ran.

---

## PART B — WHAT THE SCREENSHOTS SHOW

### B.1 Where a Tick Replay state is actually READ

**FACT.** The Tick Replay checkbox is read at pixel level in exactly **seven** frames.
All seven are 2025, S-ERA (SolarWind `A1..A5` = 90/179/5/10/10 family):

| Image ID | Capture date | Report window | Tick Replay | Source line |
|---|---|---|---|---|
| OTRIMG-0007 | Wed Feb 5, 2025 | 2/4/2025→2/5/2025 | unchecked | `screenshot_forensics/PARAMETER_PANEL_LEDGER.csv:75` (row 16); `per_image/OTRIMG-0007.md:28,48` |
| OTRIMG-0012 | Tue Feb 11, 2025 | 2/9/2025→2/11/2025 | unchecked | `PARAMETER_PANEL_LEDGER.csv:104` (row 16); `per_image/OTRIMG-0012.md:24,43` |
| OTRIMG-0014 | Thu Feb 13, 2025 | 2/12/2025→2/13/2025 | unchecked | `PARAMETER_PANEL_LEDGER.csv:136` (row 12); `per_image/OTRIMG-0014.md:23,38` |
| OTRIMG-0016 | Tue Feb 18, 2025 | 2/15/2025→2/18/2025 | unchecked | `PARAMETER_PANEL_LEDGER.csv:171` (row 17); `per_image/OTRIMG-0016.md:24,44` |
| OTRIMG-0018 | Thu Feb 20, 2025 | 2/19/2025→2/20/2025 | unchecked | `PARAMETER_PANEL_LEDGER.csv:191` (row 8); `per_image/OTRIMG-0018.md:23,34` |
| OTRIMG-0022 | Mon Feb 24, 2025 | 2/23/2025→2/24/2025 | unchecked | `PARAMETER_PANEL_LEDGER.csv:248` (row 6); `per_image/OTRIMG-0022.md:23,32` |
| OTRIMG-0024 | Wed Feb 26, 2025 | 2/25/2025→2/26/2025 | unchecked | `PARAMETER_PANEL_LEDGER.csv:281` (row 10); `per_image/OTRIMG-0024.md:27,41` |

(OTRIMG-0002 shows an unchecked box in the right-cropped Data Series strip; recorded in
`per_image/OTRIMG-0002.md:26` as "not directly legible" and therefore excluded here.)

### B.2 Where `Volume Base = BidAskPrice_RealVolume` is actually READ

**FACT.** The Volume Base value is label-confirmed in **one** frame and value-confirmed by
position in the flagship series:

| Image ID | Capture date | Reading | Source line |
|---|---|---|---|
| OTRIMG-0146 | Sat May 23, 2026 | `enum:BidAskPrice_RealVolume (Volume Base)`, panel row 1, **full labels legible** | `PARAMETER_PANEL_LEDGER.csv:1800`; `per_image/OTRIMG-0146.md:31` |
| OTRIMG-0164 | Fri Aug 14, 2026 | `enum:unreadable (Volume Base)`, panel row 3 — position-inferred, **value not legible** | `PARAMETER_PANEL_LEDGER.csv:1978`; `per_image/OTRIMG-0164.md:27` |
| OTRIMG-0117 | Fri Feb 13, 2026 | `enum:unreadable`, panel row 5 — position-inferred | `PARAMETER_PANEL_LEDGER.csv:1420` |
| flagship set 0117/0121/0123/0125/0127/0129/0132/0134/0136/0140/0142/0146/0148/0156/0159/0162/0164 | 2026-02-08 → 2026-08-14 | 13-field block value-identical throughout | `2026_VARIANT_LEDGER.csv:3` (VAR2026-FLAGSHIP); claim V-002 |

### B.3 The decisive observation this re-audit adds

**FACT.** **No frame in the corpus shows a Tick Replay state and `Volume Base =
BidAskPrice_RealVolume` together.** The two populations in B.1 and B.2 are disjoint in
time by roughly twelve months and belong to different strategy families.

**FACT.** In every 2026 V-ERA frame whose Data Series group is transcribed, **there is no
Tick Replay row at all**. The transcribed sequence runs Instrument → Price based on →
Type → Value=1 → group separator, with no checkbox between `Value` and the `Time frame`
header:
- OTRIMG-0146: `PARAMETER_PANEL_LEDGER.csv:1814-1819` (rows 15,16,17,18,19) and
  `per_image/OTRIMG-0146.md:45-49` (numbered rows 15–19). The transcript is an exhaustive
  29-row enumeration; a visible checkbox row would have been numbered.
- OTRIMG-0117: `PARAMETER_PANEL_LEDGER.csv:1435-1438` (rows 20,21,22 then `num:1`, then SEP).
- OTRIMG-0164: `PARAMETER_PANEL_LEDGER.csv:1992-1996` (rows 17,18,19, `num:1`, SEP).

**FACT.** A case-insensitive search for `tick replay` / `tickreplay` across the entire
`original_trader_reconstruction/` tree returns hits in only the seven 2025 frames listed
in B.1, plus prose in our own analysis documents. No 2026 frame records the control in
either state.

**UNKNOWN.** Why the row is absent from the 2026 captures. Candidate readings, none
separable from the corpus: (a) the row is present but cropped by the narrowed settings
pane; (b) a different NT8 build renders the Data Series group differently; (c) the row is
present and was not transcribed. We do **not** know which, and we must not pick one.

**FACT.** The 2026 flagship Strategy Analyzer reports contain full historical trade
populations over historical windows — e.g. OTRIMG-0146: 183 trades over 5/10/2026→5/22/2026
(`per_image/OTRIMG-0146.md:81`, window at lines 50-51); OTRIMG-0164: 102 trades over
8/2/2026→8/14/2026 (`derived/first_pass_index.csv:165`).

**FACT.** The 2026 panel exposes a mutating head **above** `Volume Base` and never shows a
`Zone Period` row, while the 13 VF-named fields stay frozen 2026-02-13 → 2026-08-14
(`VF_PANEL_COMPLETENESS_NOTE.md` §0 Q1a/Q1c; `2026_VARIANT_LEDGER.csv:3`; claims V-002,
V-010, V-073).

---

## PART C — WHAT IS INFERRED

Everything in this part is interpretation. None of it is observation.

**C.1 — INFERENCE (previously stated as if observed).** "The trader's 2026 frames
consistently show Tick Replay OFF." This is **not** an observation. It is an extrapolation
from the seven 2025 S-ERA frames (B.1) onto the 2026 V-ERA panels (B.2), across a
strategy-family change, a machine change, and a twelve-month gap. Claim **V-012** in
`CLAIM_REGISTRY_2026.csv:13` is currently typed `FACT`; on the evidence in B.3 its first
conjunct is **not** a FACT and V-012 must be re-typed. Its second conjunct (backtests full
of historical trades) remains FACT.

**C.2 — INFERENCE.** "A directly-embedded licensed VWAP Flux running in exactly the
displayed configuration would produce empty backtests." This follows from V-011 only if
one additionally assumes: (i) the displayed configuration was the computing configuration;
(ii) the manual sentence extends from chart-hosted indicators to strategy-hosted
indicators under the Strategy Analyzer; (iii) the sentence still described the build he ran
in Feb–Aug 2026; and (iv) "no historical calculation" implies "no historical signals"
implies "no historical trades". Assumptions (i)–(iv) are each **UNKNOWN**. This is claim
V-013 and it is correctly typed INFERENCE at `CLAIM_REGISTRY_2026.csv:14`.

**C.3 — FALSIFIED.** "Therefore his 2026 stack is his OWN reimplementation, not the
licensed indicator." This is the over-reach the owner adjudicated. It is not entailed by
V-011 + V-012 even if both were FACT, because C.2 disposes of at most **one** embedding
scenario, whereas "own reimplementation" is a claim about **all** embedding scenarios.
Recorded as FALSIFIED at `CLAIM_REGISTRY_2026.csv:23` (V-022). The wording appears, and
must be corrected, at:
- `EVIDENCE_LEDGER.csv:40` — EV-039 notes field: *"leading resolution: his 2026 stack is his
  OWN reimplementation (or heavily adapted variant) computing from bar data"*.
- `CURRENT_TRUTH.md:97-104` — *"own-implementation (H3/H4) now leads"*.
- `CONVERGENCE_PASS_ANSWERS_20260824.md:107-113` — *"his stack is most plausibly his OWN
  implementation"*.
- `vwap_flux_family/VF_CORE_PARITY_REPORT.md:44-52` — *"H4/H3 > H1"* and *"Our bar-level
  clone is therefore the SAME input class as his build, not an approximation of it."*
- `vwap_flux_family/VF_CLEANROOM_SPEC.md:33-48` — *"The EV-039 embedding contradiction (new,
  load-bearing)"*.
- `vwap_flux_family/OWNER_REPORT_RECONCILIATION.md:34-36` — *"→ his stack is most plausibly
  his OWN bar-data implementation (H3/H4), not the embedded licensed indicator."*
- `HYPOTHESIS_LEDGER.csv:149` (OTR-R7-003) — verdict `H1_DISFAVORED`.
- `vendor_forensics/PURCHASE_GATE.md:13-22`.
- Independently flagged as over-claiming by `TERMINOLOGY_SWEEP.md` rows C5-01, C5-04, C5-06
  (all still `NEEDS_HUMAN_JUDGEMENT`).

**C.4 — INFERENCE, and it cuts the other way.** The manual's §4 (A.3) documents "build your
own strategy" around `Signal_Trade` as the intended architecture. In NT8, a strategy
declares its own parameter surface; it does not inherit the hosted indicator's property
grid. This explains, without any reimplementation, both (a) the colon-less relabelling
observed in A.2 vs OTRIMG-0146, and (b) the absence of `Zone Period` — a wrapper author
exposes the inputs he uses and omits the rest. This is a **pro-H1/H2** reading of the same
observations that were previously read as pro-H3/H4. Both readings survive; neither is
selected.

**C.5 — INFERENCE.** The 13 frozen VF-named fields sitting inside a head that changes
value, count and type week to week is equally consistent with "vendor block passed through
a wrapper whose own controls he keeps retuning" (H1/H2) and with "a re-typed block he
never retunes" (H3/H4). It does not discriminate.

---

## PART D — THE FIVE HYPOTHESES, ALL LIVE

None of the five is currently favoured. `CLAIM_REGISTRY_2026.csv:15` (V-014) records the
engine as **UNKNOWN**; V-015..V-019 carry the five members.

### H1 — Official VWAP Flux component + custom wrapper / hosting behaviour
The trader licensed and installed the real component, and hosts it inside his own
NinjaScript strategy; some property of that hosting (strategy-hosted rather than
chart-hosted, an explicit `AddDataSeries`, a Tick-Replay-enabled Analyzer arm, a
`Calculate` mode, a data-series configuration we cannot see) lets it compute historically.

- **FOR:** the manual's own §4 prescribes exactly this architecture (A.3); 13/13 ordered
  label+vocabulary match including the enum literal `BidAskPrice_RealVolume` (EV-019, V-002);
  relabelling and field-subsetting are what an NT8 wrapper inherently does (C.4); the
  trader's actual Tick Replay state in 2026 is unobserved (B.3), so the premise that
  disfavoured H1 is not in evidence.
- **CONFIRMED BY:** a frame showing the strategy-name row with a vendor-derived name; a
  vendor-branded or licensing dialog in any capture; a ninZa group header; an author
  statement naming the component; or vendor confirmation that a strategy-hosted instance
  computes historically in this mode.
- **REFUTED BY:** vendor confirmation that **no** hosting arrangement of the licensed
  component computes historically in `BidAskPrice_RealVolume` with Tick Replay off,
  **combined with** direct evidence that his 2026 runs had Tick Replay off. Both halves
  are required; we hold neither.

### H2 — Official component or signals + author-supplied historical volume handling
He consumes the official `Signal_Trend`/`Signal_Trade` (or the official plots) but feeds or
substitutes the volume input himself — e.g. an alternative volume series, a bar-data
proxy, or a second data series — so the stack computes over history.

- **FOR:** requires no reimplementation of the cloud, rail or signal math, only of the
  input plumbing; the vendor exposes signal series precisely for downstream consumption
  (A.3); it explains V-011 and full backtests simultaneously without discarding either.
- **CONFIRMED BY:** any frame or statement showing a second data series, a volume-source
  parameter, or an added input row in the mutating head above `Volume Base`; vendor
  documentation of an injectable volume source.
- **REFUTED BY:** vendor documentation showing the component cannot accept an alternative
  volume source **and** that its signal series are inert whenever historical volume
  classification is unavailable.

### H3 — Official concepts partly reimplemented by the author
He owns or has seen the product and re-implemented some layers (e.g. the volume/VWAP
plumbing) while using vendor semantics and vendor names for the rest, or vice versa.

- **FOR:** his parameter values (60/5/20 EMA/95-75-50-25-5/3/10/5) differ from every
  published vendor preset, most sharply `Close Threshold = 10` against the presets'
  universal 70/80 (A.2; `OWNER_REPORT_RECONCILIATION.md:31-35`); `Zone Period` never
  appears; the head rows are plainly his own.
- **CONFIRMED BY:** a per-bar or per-trade artefact whose values match vendor semantics on
  some layers and deviate systematically on others; an author statement to that effect.
- **REFUTED BY:** bar-exact agreement with a licensed instance on **all** layers (→ H1/H2),
  or systematic disagreement on all layers (→ H4).

### H4 — Full clean-room / private author implementation
He wrote the whole stack himself, borrowing only the vocabulary.

- **FOR:** he is documented writing his own NinjaScript (A1..A5 obfuscated parameters,
  EV-030; VS Code + NinjaScript editor on his machines, `CONTRADICTION_LEDGER.md:5`); his
  self-description "自己开发的动量指标" (self-developed momentum indicator), same line; his
  non-VF machinery — the −$2,600 / 130-pt cap that **pre-dates** the first VF frame,
  entries-per-direction = 2, session-close exit — is his own.
- **CONFIRMED BY:** a strategy-name row with a non-vendor name plus per-bar output that
  deviates systematically from a licensed instance; source or an author statement.
- **REFUTED BY:** any vendor-branded artefact in his environment, or bar-exact agreement
  with a licensed instance.

### H5 — Vendor, version or hosting behaviour we do not fully understand
The manual's §2.1 sentence does not describe the build, version, or host configuration he
actually ran, and the apparent contradiction dissolves on contact with the real software.

- **FOR:** the manual is dated **2026-01-28** and the vendor shipped changes on 2026-02-09
  and 2026-02-24 (EV-019) — i.e. during the trader's VF era; the manual never mentions
  Strategy Analyzer or strategy-hosted instantiation (A.4); the Tick Replay row is absent
  from every 2026 capture for reasons we cannot determine (B.3); §2.1's own wording ("Any
  actions that lead to chart reloading will erase all calculations") is **chart**-framed
  throughout.
- **CONFIRMED BY:** a licensed instance computing historically under settings the manual
  says it cannot; a vendor changelog or support statement revising the behaviour; a build
  difference between versions.
- **REFUTED BY:** a licensed instance of the era-matched build reproducing the documented
  behaviour exactly under every hosting arrangement tested.

**H5 is the hypothesis EV-039's original conclusion implicitly assumed away**, by treating
one dated sentence about one host context as a timeless property of the product.

---

## PART E — RETRACTION: the local-artifact argument is INVALID EVIDENCE

**RETRACTED.** The argument *"there are zero VWAP Flux artifacts on our research machine,
therefore the trader more likely wrote his own"* is structurally invalid and is withdrawn.
The researcher's NinjaTrader install is not the original trader's environment; the two
populations are causally unrelated. A search of our machine has exactly zero probative
weight on what he owned, installed, or ran. It bears only on whether **we** have a local
oracle.

Already recorded as **FALSIFIED** at `CLAIM_REGISTRY_2026.csv:22` (V-021: *"The absence of
vendor artifacts on OUR research machine is evidence about what the ORIGINAL TRADER owned or
ran"* — "RECORDED AS INVALID EVIDENCE. Must not be cited in support of H3/H4 or against
H1/H2").

**Where the invalid argument was used — file and line:**

| File | Line(s) | Text |
|---|---|---|
| `research/original_trader_reconstruction/HYPOTHESIS_LEDGER.csv` | 149 (row OTR-R7-003) | *"...+ no Zone Period in any frame **+ no local artifacts** -> own implementation with vendor-style names is leading"* — verdict field `H1_DISFAVORED` |
| `research/original_trader_reconstruction/CURRENT_TRUTH.md` | 101-102 | *"...no Zone Period in ANY frame, and **zero local artifacts**: **own-implementation (H3/H4) now leads**"* |
| `research/original_trader_reconstruction/CONVERGENCE_PASS_ANSWERS_20260824.md` | 111-112 | *"...no Zone Period anywhere, and **zero local artifacts**, his stack is most plausibly his OWN implementation"* |

**Where the same search is cited legitimately, and stays:**

| File | Line(s) | Why it is valid |
|---|---|---|
| `vendor_forensics/LOCAL_ARTIFACT_SEARCH_20260824.md` | 96-103 | Conclusion is scoped to *"Local oracle path short of purchase: NONE"* — a statement about **our** options, not about him. The file also states its own scope correctly at lines 6-7: *"All paths below are on the researcher's machine — none of this is the original trader's environment."* |
| `CLAIM_REGISTRY_2026.csv` | 21 (V-020) | Types the search result as a FACT about the researcher's install only. |
| `CONVERGENCE_PASS_ANSWERS_20260824.md` | 116-119 (answer U) | Uses it to close **our** order-flow purchase gates. Valid. |

**Required correction (not applied here — this document does not edit other ledgers):** the
three rows in the first table must have the local-artifact clause struck from their
reasoning, and OTR-R7-003's verdict re-typed from `H1_DISFAVORED` to `INCONCLUSIVE`.

---

## PART F — THE NARROW CLAIM THAT SURVIVES

### F.1 What the manual weakens

> **NARROW CLAIM.** The ninZa VWAP Flux Trader Manual dated 2026-01-28, §2.1, weakens
> **one specific model of the trader's 2026 stack**: an *unmodified pass-through of the
> licensed VWAP Flux component, computing in `BidAskPrice_RealVolume` mode, with Tick
> Replay disabled, in a host context to which the manual's chart-framed statement applies,
> in a build whose behaviour matches the 2026-01-28 documentation* — since such a
> configuration is documented to perform no historical calculation, and his Strategy
> Analyzer reports are demonstrably full of historical trades.

Even this is **conditional**, because premise 2 (Tick Replay disabled in 2026) is
**UNKNOWN**, not observed (B.3). The honest form is: *if* his 2026 runs had Tick Replay
off, *and* the manual's sentence extends to his host and build, *then* that one
configuration is excluded. Status: **INFERENCE, conditional on two unverified premises.**

### F.2 What the manual does NOT weaken

1. **That he licensed and owned VWAP Flux.** Ownership is untouched by any statement about
   calculation modes.
2. **H1** in any form other than the exact pass-through configuration named above —
   including every wrapper, hosting, data-series, `Calculate`-mode or Tick-Replay-enabled
   arrangement. The manual's own §4 recommends a wrapper.
3. **H2** entirely. Author-supplied volume handling is precisely the workaround the §2.1
   constraint would motivate; the constraint is a *reason for* H2, not against it.
4. **H3** or **H4** — the manual provides no positive evidence for them either. Excluding
   one member of H1's family does not promote H3/H4; it redistributes over the remaining
   four hypotheses, which include the rest of H1.
5. **H5** — the manual cannot bound its own completeness or its own version scope.
6. **Any of the trader's parameter values, his signal semantics, his exit rule, his risk
   cap, or any reconstruction result.** EV-038's semantic pins (Split, QtyPerTrend,
   CloseThreshold family, Zone Period existence) are untouched; EV-040's rail-geometry
   finding is untouched. This re-audit is confined to the engine-provenance question.
7. **The value of a purchase as a vendor-semantics oracle.** It bounds what a purchase can
   answer (vendor semantics, not his private build), which was already recorded; it does
   not bear on whether that bound is worth $300.

### F.3 The one operational consequence that survives intact

**FACT (protocol).** Any post-purchase oracle run must use Tick Replay or one of the
`UpDownTick` modes for the licensed indicator to compute over history at all. This follows
directly from A.1 with no additional assumptions and is already recorded in
`vendor_forensics/PURCHASE_GATE.md` ("Pre-purchase parity kit" — "Tick Replay ON and OFF
arms") and `CLAIM_REGISTRY_2026.csv:102` (V-101). It is **unaffected** by this re-audit.

---

## PART G — IS THE QUOTE COMPLETE ENOUGH? (honest answer: for its own terms yes, for the argument no)

**Completeness of the text — YES.** §2.1 is quoted in full at A.1 from the repo's own PDF,
character-exact, with both the Tick-Replay-enabled and Tick-Replay-disabled sentences and
all three Volume Base modes. Nothing is missing and nothing is paraphrased. The sentence is
unambiguous within its own frame of reference.

**Sufficiency for the narrow claim — FLAGGED. Four gaps, in descending severity.**

1. **The trader-side premise is absent, not weak.** No frame shows his 2026 Tick Replay
   state (B.3). The narrow claim's second premise rests on extrapolation from 2025
   SolarWind-era frames across a family change and twelve months. **This is the most
   serious defect and it is on our side, not the manual's.** Until a 2026 frame shows the
   control, or the row's absence is explained, the narrow claim is conditional.
2. **Host-context scope.** §2.1 says "the indicator" and its closing sentence is
   chart-framed ("Any actions that lead to chart reloading will erase all calculations").
   The manual never discusses strategy-hosted instantiation or the Strategy Analyzer. The
   claim needs the sentence to transfer to a host the document does not mention. It may;
   we cannot show it does.
3. **Version scope.** The manual is dated 2026-01-28; the vendor shipped signal-layer
   changes on 2026-02-09 and 2026-02-24, i.e. within days of the trader's first VF frame
   and six months before his last. We hold no evidence the §2.1 behaviour was stable
   across those builds — nor that it changed.
4. **The signal-to-trade link.** "No calculations on historical data" is not stated to
   imply "signal series are inert" nor "no orders are generated". A strategy could carry
   entry logic beyond `Signal_Trade`. The manual gives us nothing on this.

**Would more text fix it?** Partly. What would materially help, in order: (a) any vendor
statement about strategy-hosted or Strategy-Analyzer behaviour; (b) a version-stamped
changelog line touching historical calculation; (c) the vendor's product FAQ or forum
thread on Tick Replay. What would fix it completely is on the **trader** side, not the
vendor side: a 2026 frame showing the Data Series group with its Tick Replay row legible.

---

## PART H — LEDGER DELTAS THIS RE-AUDIT REQUIRES

Recorded here; applying them is a separate, explicitly authorised edit.

| Target | Current | Required |
|---|---|---|
| `EVIDENCE_LEDGER.csv:40` (EV-039 notes) | narrative asserts "leading resolution: his 2026 stack is his OWN reimplementation" and "alternatives ... contradicted by frames" | Split into `FACT:` (manual sentence) and `INFERENCE (conditional):` (the one excluded configuration). Delete "contradicted by frames" — B.3 shows the frames are silent. Add the 2026-01-28 date and the Tick-Replay-unobserved caveat. |
| `CLAIM_REGISTRY_2026.csv:13` (V-012) | typed `FACT` | Re-type: first conjunct → `INFERENCE` (extrapolated from 2025 S-ERA frames); second conjunct stays `FACT`. Add the B.3 disjointness observation. |
| `HYPOTHESIS_LEDGER.csv:149` (OTR-R7-003) | verdict `H1_DISFAVORED`; reasoning cites "no local artifacts" | Verdict → `INCONCLUSIVE`; strike the local-artifact clause (Part E). |
| `CURRENT_TRUTH.md:97-104` | "own-implementation (H3/H4) now leads" | Replace with the Part F narrow claim + all five hypotheses live; strike "zero local artifacts". |
| `CONVERGENCE_PASS_ANSWERS_20260824.md:107-113` | "most plausibly his OWN implementation" | Same; strike "zero local artifacts". |
| `VF_CORE_PARITY_REPORT.md:44-52` | "H4/H3 > H1"; "the SAME input class as his build" | Re-hedge per `TERMINOLOGY_SWEEP.md` row C5-01. |
| `VF_CLEANROOM_SPEC.md:33-48` | heading "The EV-039 embedding contradiction (new, load-bearing)" | Re-title to name the single excluded configuration; keep the §2.1 semantic pin at line 22, which is correct. |
| `OWNER_REPORT_RECONCILIATION.md:34-36` | one sentence spans observation and conclusion across a `→` | Split at the arrow per `TERMINOLOGY_SWEEP.md` row C5-06. |
| `PURCHASE_GATE.md:13-22` | "the leading reading ... is his OWN implementation" | Replace with the narrow claim. The **gate decision itself is unaffected**: it also rests on the oracle-answers-vendor-semantics argument (F.2 item 7), which stands. |
| New evidence row | — | Register the 2026-01-28 manual date, the SHA-256, the p5 vendor-panel image reading (A.2), and §4's documented wrapper architecture (A.3) as their own evidence line, since they now carry argumentative weight. |

---

## SUMMARY OF STATUS ASSIGNMENTS

| # | Claim | Status |
|---|---|---|
| 1 | Manual §2.1 (2026-01-28): BidAskPrice_RealVolume + Tick Replay disabled → indicator functions only on real-time data, no calculations on historical data | **FACT** |
| 2 | Manual §4: vendor instructs customers to build their own strategy on `Signal_Trend`/`Signal_Trade` | **FACT** |
| 3 | Vendor's own panel labels carry colons; trader's are colon-less; `Zone Period` sits in a separate `General` group | **FACT** |
| 4 | Tick Replay state read in 7 frames, all Feb-2025 S-ERA, all unchecked | **FACT** |
| 5 | `Volume Base = BidAskPrice_RealVolume` label-confirmed in 1 frame, OTRIMG-0146 (2026-05-23) | **FACT** |
| 6 | No frame shows both; no 2026 frame records a Tick Replay row at all | **FACT** |
| 7 | 2026 Strategy Analyzer reports contain full historical trade populations | **FACT** |
| 8 | Trader's 2026 runs had Tick Replay off | **UNKNOWN** (was asserted as FACT) |
| 9 | §2.1 applies to strategy-hosted instances / Strategy Analyzer | **UNKNOWN** |
| 10 | §2.1 behaviour unchanged in the builds he ran (Feb–Aug 2026) | **UNKNOWN** |
| 11 | The one pass-through configuration named in F.1 is excluded | **INFERENCE**, conditional on 8 and 9 |
| 12 | His 2026 stack is his own reimplementation | **FALSIFIED as a conclusion from EV-039** (the proposition itself remains UNKNOWN) |
| 13 | Absence of VF artifacts on our machine is evidence about him | **FALSIFIED** |
| 14 | What his 2026 computing engine is | **UNKNOWN** — H1..H5 all live |
| 15 | Oracle protocol must use Tick Replay or UpDownTick to compute historically | **FACT** (unaffected) |

*Sources: `vwap_flux_family/ninZaVWAPFlux-TraderManual.pdf` (text + embedded images, read-only);
`EVIDENCE_LEDGER.csv`; `CLAIM_REGISTRY_2026.csv`; `HYPOTHESIS_LEDGER.csv`;
`screenshot_forensics/PARAMETER_PANEL_LEDGER.csv`, `2026_VARIANT_LEDGER.csv`,
`VF_PANEL_COMPLETENESS_NOTE.md`, `derived/first_pass_index.csv`, `per_image/*.md`;
`vendor_forensics/LOCAL_ARTIFACT_SEARCH_20260824.md`, `PURCHASE_GATE.md`;
`vwap_flux_family/OWNER_REPORT_RECONCILIATION.md`, `VF_CLEANROOM_SPEC.md`,
`VF_CORE_PARITY_REPORT.md`; `CURRENT_TRUTH.md`; `CONVERGENCE_PASS_ANSWERS_20260824.md`;
`TERMINOLOGY_SWEEP.md`. No .py file was modified, no backtest was run, no original
screenshot was altered.*
