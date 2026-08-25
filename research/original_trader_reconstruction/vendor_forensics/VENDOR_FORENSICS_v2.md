# VENDOR FORENSICS v2 — label/order adjudications

Directive v5.0 §5–§16, §43, §52. Written 2026-08-25. All vendor facts are from **public**
sources: official ninZa/RenkoKings product pages, the publicly-hosted Trader Manual PDFs, the
sites' own embedded product records, public changelogs, Wayback snapshots. No decompilation, no
purchase, no license bypass. Access date 2026-08-25 throughout.

§5 is binding: numeric coincidence yields OPEN_VENDOR_CANDIDATE at most. §43 LEVEL A requires a
direct class/product name or a near-exact property-label/order/UI match.

---

## 0. The method breakthrough that makes this pass different

The previous pass concluded "no evidence found" for most products. That was wrong in an important
way: **ninZa/RenkoKings host their official Trader Manual PDFs publicly and without
authentication**, and several contain complete ordered parameter lists — two of them with actual
rendered NT8 property-grid screenshots. `ninza.co` returns 403 to plain fetchers (Cloudflare),
which is evidently why the earlier pass came up empty.

That converts several adjudications from "absence of evidence" into **positive contradiction**,
which is a far stronger epistemic position.

Reusable asset: 20+ manuals are at predictable URLs under
`forestcms.nyc3.digitaloceanspaces.com/media/*-TraderManual.pdf`.

---

## 1. THE HEADLINE — the VF13 block is the trader's OWN declarations, not the vendor's grid

**Status: FACT (label + order evidence, LEVEL A).**

ninZa's own manual shows VWAP Flux's rendered property grid. Set against the trader's panel
(OTRIMG-0146, the one frame with legible labels; label tails re-read from pixels for this note):

| # | trader's rendered label | ninZa's rendered label | agree? |
|---|---|---|---|
| 1 | **Volume Base** (FIRST) | `Volume Base` (LAST, after `Zone Period`) | **order differs** |
| 2 | Anchor Period (Minutes) | `Anchor Period (Minutes)` | yes |
| 3 | VWAP Amount | `VWAP Amount` | yes |
| 4 | Trend Period | `Trend: Period` | colon |
| 5 | Trend MA Type | `Trend: MA Type` | colon |
| 6–10 | **Max / Upper / Median / Lower / Min Percent** | `Level: Max (%)` … `Level: Min (%)` | **different strings** |
| 11 | **Signal Quantity Per Trend** (no `(%)`) | `Signal: Quantity Per Trend (%)` | **different string** |
| 12 | Signal Close Threshold (%) | `Signal: Close Threshold (%)` | colon only |
| 13 | Signal Split (Bars) | `Signal: Split (Bars)` | colon only |
| — | **absent** | `Zone Period` | **property missing** |

Four independent differences: rows 6–10 end in the word **"Percent"** where the vendor's end in
**"(%)"**; row 11 carries **no `(%)` suffix** where the vendor's does; `Volume Base` sits at the
**opposite end** of the block; and `Zone Period` **does not exist** in his panel at all.

**This is decisive, and it is also what NinjaTrader's architecture requires.** An indicator
instantiated inside a strategy does **not** surface its properties in that strategy's property
grid — the author must re-declare each one as a strategy input and pass it through. So the mere
appearance of VWAP-Flux parameters in his *Strategy Analyzer* panel already proves re-declaration;
the label differences confirm it and show he named them from concept ("Max Percent") rather than
copying the vendor's strings ("Level: Max (%)").

**Consequences.**
- §55 Q6 ("is licensed direct use proven?") — **NO, and the panel can never prove it**, because
  the panel only ever shows the author's own declarations.
- The 13 labelled rows are **his wrapper's inputs**. So are, necessarily, all ~497 custom rows.
- **"Which vendor product does this block belong to?" is the wrong question for every block.**
  The right question is "which vendor's *concepts* did he choose to re-expose". §4's matrix is
  reframed accordingly.
- It does **not** decide whether the underlying computation is the licensed DLL or his own
  reimplementation. EV-039 remains open; H1–H5 all stay live.

---

## 2. Adjudication A — Multi-Osc / King Kong: **CONTRADICTED on label order**

Official manual (`ninzamultioscobosoverlap-tradermanual_4.pdf`), §1 "Parameters", 16 rows:

```
MFI: Period | MFI: Threshold High | MFI: Threshold Low
RSI: Period | RSI: Smooth | RSI: Plot [ENUM] | RSI: Threshold High | RSI: Threshold Low
Stoch: Period D | Stoch: Period K | Stoch: Smoothing Method [ENUM] | Stoch: Smoothing Period
   | Stoch: Plot [ENUM] | Stoch: Threshold High | Stoch: Threshold Low
Safe Reversal Period
```

**The three High/Low threshold pairs are never contiguous.** MFI's sit at 2–3, RSI's at 7–8, and
Stoch's at 14–15 — separated by `RSI: Plot`, `Stoch: Smoothing Method` and `Stoch: Plot`, all
**dropdown enums**. A six-cell contiguous numeric run `65|30|75|20|46|36` **cannot** be produced
by this panel. Multi-Osc also exposes **zero checkboxes**.

The old `65/30, 75/20, 46/36` → MFI/RSI/Stoch mapping stays **FALSIFIED**, and is now falsified by
positive label/order evidence rather than by absence.

Weak consistency worth recording, not an identification: ninZa's convention *is* Threshold High
before Threshold Low, so the High>Low orientation is consistent, and the MFI→RSI→Stoch order is
confirmed.

**King Kong Trading RK has no property panel at all** — it is a four-product *bundle*
(Multi-Osc + Solar Wave RK + KingRenko$ + Superfast One-Click). The "King Kong panel" hypothesis
is structurally void. `ninza.co/product/king-kong-trading-rk` 301-redirects to the non-RK page.

**Caveat that keeps this honest:** this rules out "the observed rows *are* the vendor's panel"
(which §1 already rules out universally). It does not rule out that he *used* Multi-Osc.

## 3. Adjudication B — Cosmik Z-TP: feature set **CONFIRMED**, panel shape **CONTRADICTED**

Cosmik's manual documents 27 rows (28 in ninZaATR mode) and — uniquely — embeds a **numbered NT8
grid screenshot** (rows 24–27 with the vendor's own red numbering), which proves manual order =
grid order and that ninZa uses explicit `Display(Order=…)`, not alphabetical sort.

It genuinely exposes all five things the adjudication asked about: `MFI: *`, `RSI: *`, `Stoch: *`,
**`Offset: Multiplier Stop`**, **`Offset: Multiplier Trend`**. Architecturally it is
Solar Wave + Multi-Osc + a signal-quantity limiter + an S/R level layer in one script.

But its shape contradicts every observed motif: **exactly 2 checkboxes, maximum adjacency 2**, the
list **terminates at 27**, and ninZa uses flat `Prefix: Name` labels with **no NT8 group headers**.
The demoted identity claim stays demoted.

## 4. Super JumpBoo$t — **STRONG OPEN CANDIDATE (upgraded), not an identification**

This is the one genuine upgrade in the pass. SJB's `Parameters` group **terminates** in exactly
four consecutive numerics, in this documented order:

`Extreme: Neighborhood (Bars)` → `Signal: Close Threshold (%)` → `Signal: Quantity Per Zone` → `Signal: Split (Bars)`

and the vendor's official **100-Tick preset** for those four rows is **30 | 70 | 2 | 20**,
immediately followed by a group boundary. The observed Jun-2026 run (OTRIMG-0150) is
**`30 | 70 | 2 | 20 | [SEP]`** — matching on values 4/4, ordinal position, control-type sequence
*and* group-terminal placement. That is materially more than numeric coincidence.

**Two problems recorded honestly, because they matter:**

1. **Preset mismatch on his own bar type.** SJB's **1-Minute** preset is `30 | 80 | 2 | 20`. His
   primary series is NQ 1-Minute. The observed `70` matches the **100-Tick** preset, not the
   1-Minute one — so the match is 4/4 against a preset for a chart he does not use, and 3/4
   against the preset for the chart he does. He may of course have tuned it; but he demonstrably
   *does* tune (his VF Close Threshold is 10 against a universal preset of 70).
2. **The named falsifier is untestable in this corpus.** The prediction was that the eight rows
   above the `30` must read `[✔] | 1 | 2 | 3 | 4 | 5 | 2 | 100`. Re-examining OTRIMG-0150's top
   edge at ×5: the `30` is the **first visible row**, sitting directly under the "Settings" header
   with its group connector cut at the pane edge. Nothing above it was photographed, and no other
   frame covers that region. **The test cannot be run.** Recorded rather than quietly dropped.

Timeline compatible (SJB released 2025-04-10). Status: **OPEN_VENDOR_CANDIDATE, leading.**

## 5. ApexFlow Zignal — **DOWNGRADED**

Its grid is now fully known: **14 rows, 1 enum + 13 numerics, and not a single checkbox.** All the
"tick the conditions you want" behaviour lives in **separate modal dialogs**, which never render
as property-grid rows. The observed checkbox banks therefore **cannot** be ApexFlow toggles.
Released 2026-01-22 — after the pre-VF builds it was hoped to explain.

## 6. ThunderZilla — **explicit negative, no upgrade**

**Its property list is not published anywhere.** The ninza.co page has been retired (slug
308-redirects to `/trading-systems`); it survives only as marketing copy; no Trader Manual exists
in the vendor's file records; the changelog has exactly two entries (released 2024-02-14;
`Signal: Quantity Per Trend` added 2025-08-11). Total confirmed property labels: **one**.

**Renko requirement: NOT DOCUMENTED** — Renko appears only as a marketing tag. So his 1-Minute
primary neither confirms nor refutes it. Do not promote.

## 7. Timeline facts that constrain everything (§33)

| date | event |
|---|---|
| 2025-04-10 | Super JumpBoo$t released |
| 2025-08-11 | ThunderZilla gains `Signal: Quantity Per Trend` |
| **2026-01-09** | **VWAP Flux page published** |
| **2026-01-14** | **VWAP Flux "the parameters were rearranged"** |
| 2026-01-22 | ApexFlow Zignal released |
| **2026-02-09** | **VWAP Flux gains `Signal_Cum_Delta`** |
| **2026-02-13** | **the trader's VF13 block first appears** |
| 2026-02-24 | VWAP Flux `Signal_Trend` upgraded |
| 2026-06-25 | Captain Optimus Strong **v2** released |

**He adopted VWAP-Flux-shaped parameters within ~5 weeks of the product's public release**, and
four days after `Signal_Cum_Delta` was added. That is an early adopter tracking the product
closely — the single strongest circumstantial link to the vendor in the corpus. It is
circumstantial: it is timing, not a label.

**Nothing dated 2026 exists for Multi-Osc, Cosmik, King Kong, NVI/PVI or Solar Wave** (all frozen
2023–2025), so no 2026 vendor feature can explain a 2026 motif change in those families.

## 8. The motif verdicts, consolidated

| motif | verdict |
|---|---|
| Jun-2026 `30\|70\|2\|20\|[SEP]` | **STRONG OPEN CANDIDATE: Super JumpBoo$t group tail** (values 4/4 + order + control types + group-terminal). Falsifier untestable. |
| Jun-2026 4- and 5-checkbox banks | **CONTRADICTED** for ApexFlow (0 grid checkboxes), VWAP Flux (0), SJB (1, at top), Cosmik (2, max adjacency 2), Multi-Osc (0), OFP2 (trailing only). No ninZa target produces runs of 4–5 adjacent checkboxes. |
| `14 \| 6` adjacent pair | **CONTRADICTED** for ninZaRenko (vendor's own rule requires brick size to be a *multiple* of trend threshold: 8/4, 12/4, 20/5 — 14/6 violates it) and for VWAP Flux (`Trend: Period`=14 is followed by an **enum**, not 6). Weak numeric-only candidates remain in ApexFlow and Cumulative Delta. The "KingRenko primary bars" reading stays **FALSIFIED**. |
| Jan/Feb-2026 15-row tail (4 groups) | **NO EVIDENCE FOUND**; CONTRADICTED for every product with a published grid — all expose a **single** group, his run spans four. |
| head-of-list `[SEP] enum enum [SEP] …` | **CONTRADICTED / NO EVIDENCE FOUND.** No ninZa target has a standalone two-enum group at its head. |

## 9. The structural conclusion these share

Every observed motif has at least one feature **no ninZa indicator panel possesses**: banks of
4–8 adjacent checkboxes, NT8 group separators (ninZa uses flat `Prefix: Name` labels and no group
headers), multiple groups per block, and a total length of ~497 rows against a ninZa maximum of 27.

Combined with §1, this is coherent and it is the working model directive v5.0 asked for:

> **The ~497 rows are the trader's own NinjaScript wrapper.** Vendor products, where used, are
> called from inside it and contribute *concepts and signal series*, never panel rows. Searching
> the panel for a vendor's property layout is therefore searching for something that cannot be
> there — which is why five motifs all came back CONTRADICTED or NO EVIDENCE.

This does not say he wrote everything himself. Every ninZa manual examined explicitly invites it —
verbatim, *"you can rely on the signals below to build your own strategy"* — with dedicated
Strategy Builder tutorial videos per product. Consuming `Signal_*` series from a licensed
indicator inside a large private wrapper is the vendor's own documented workflow, and it is
exactly the architecture the evidence supports.

## 10. The head of the list is NT8's OWN group — and the strategy name is unrecoverable

**Status: FACT (re-read from pixels for this note, OTRIMG-0119 and OTRIMG-0138 at ×7).**

The `[SEP] | enum | enum | [SEP]` opening is **not** a custom block. It is the Strategy Analyzer's
own **General** group: `Backtest type`, then `Strategy`. NT8's Help Guide
(`backtest_a_strategy.htm`) documents exactly this pair, and `PARAMETER_PANEL_LEDGER.csv`
independently shows the identical opening on OTRIMG-0002 (Feb-2025), where rows 5–9 are the
known Solar A-params.

**Correction to `ALL_VISIBLE_PARAMETER_ORIGIN_MATRIX.csv`:** HEAD-A slots 1–4 are
`IDENTIFIED_PLATFORM_SETTING`, not custom rows. His own parameters begin at HEAD-A slot 5
(`checked | 10 | 26 | 14 | 198? | 180? | 140?`).

**The `Strategy` enum is the single most valuable cell in the corpus — and it is unrecoverable.**
Both top-scrolled frames were re-examined at ×7. The Settings pane in both is narrower than the
value text, so NT8 renders the combo box as **a bare chevron with no string at all**. This is a
rendering limit, not a resolution limit: the characters were never drawn. No amount of
magnification, sharpening or super-resolution can recover text that does not exist in the pixels.

Consequence: **the strategy name cannot be obtained from this corpus by any image method.** The
prior record of "not visible anywhere on screen" is upgraded from an observation to a *proof of
impossibility*, and this line of attack is closed.

## 11. A challenge to the extent premise — raised, tested, REFUTED

The vendor pass raised a serious objection: NT8's **Optimization** backtest type expands every
strategy parameter into four grid rows (the parameter plus `Min.`, `Max.`, `Increment`). If the
panel were in Optimization mode, ~523 rows would mean only ~131 real inputs and the growth rate
would be ~3.2 inputs/week, not 12.7. That would change every conclusion drawn from the extent
series.

**It is refuted directly, and by the cleanest possible evidence.** In OTRIMG-0146 the VWAP block
renders as **exactly 13 rows carrying exactly 13 single values** — `BidAskPrice_RealVolume, 60, 5,
20, EMA, 95, 75, 50, 25, 5, 3, 10, 5` — mapping one-to-one onto the 13 labels. Under Optimization
mode those 13 parameters would occupy 39–52 rows with Min/Max/Increment triplets. Corroborating:
no parameter row in any frame carries an expander triangle (only group headers do), and the
26-row standard tail matches the Standard-backtest tail exactly.

**Verdict: Standard backtest mode. One row per declared property. The extent series stands.**

A second objection cited `screenshot_forensics/VF_PANEL_COMPLETENESS_NOTE.md` ("thumb SIZE is NOT
proportionally trustworthy"). That note was already **falsified in writing** by
`2026_PANEL_TOPOLOGY.md` §0, which measured thumb heights of 35–251 px — far above any WPF minimum
— and validated the proportional model against the independently countable NT8 tail in 17 frames.
The objection is answered by an existing committed falsifier.

**What this makes load-bearing:** NT8 has *no documented mechanism to add property rows at
runtime* — the grid is static and populated by reflection over properties declared at compile
time. ~497 custom rows therefore means **~497 properties declared in his source**. That is an
author, not a purchase, and it is now supported by platform documentation rather than inference.

## 12. Meta-layer targets — both EXCLUDED on direct evidence

| product | custom rows | verdict |
|---|---|---|
| **Infinity Algo Engine$** | **19** (3 groups, complete list verified from the manual's grid screenshot) | **EXCLUDED** |
| **Captain Optimus Strong v2** | **~43** | **EXCLUDED** (count *and* date) |
| Multi-Instrument Synergy / Multi-Timeframe Fu$ion | capped at 5 blocks | not candidates |
| **largest ninZa grid found anywhere** | **43** | — |

Infinity Algo Engine$ is doubly excluded: its manual **never mentions the Strategy Analyzer** — it
is a live on-chart execution engine with no backtest path, so it cannot be the object in a
Strategy Analyzer settings panel. Captain Optimus Strong **v2 released 2026-06-25**, four months
after the growth curve began, so it cannot explain Feb–Jun 2026.

**Why "unlimited indicators" does not mean unlimited rows** — answered by a picture, not
inference: the COS v2 manual shows its Strategy Setup Window rendering each selected indicator's
parameters **inside that window**, never in the NT8 property grid.

**No repeated numbered blocks reach the NT8 grid in any ninZa product beyond a cap of 5** — while
his panel shows banks of 4, 5, 7 and 8 adjacent checkboxes, with BANK-1 and BANK-2 sharing an
identical seven-state mask.

**One pathway left open, and it is date-excluded:** COS v2's `Generate Strategy` writes a strategy
file for the Strategy Analyzer, and the *generated* strategy's property grid is undocumented. It
could in principle be large. But v2 postdates the growth curve, so it cannot be the explanation
for Feb–Jun 2026.

## 13. Bonus — Solar Wave's vendor property list, in vendor order

The COS v2 manual (p.25) publishes it verbatim: `Input` · `Offset: Multiplier Trend` ·
`Offset: Multiplier Stop` · `Offset: ninZaATR Period` · `Reference Price: Period` ·
`Reference Price: Close Weight` · `Slowdown Scan (Bars)` · `Weak-Weak Split (Bars)` ·
`Pullback: Early` (checkbox) · `Pullback: Split (Bars)`.

The frozen truth **90 / 179 / 5 / 10 / true / 10** matches six of these by type and relative order
(Multiplier Trend, Multiplier Stop, Slowdown Scan, Weak-Weak Split, Pullback: Early [bool],
Pullback: Split), skipping `ninZaATR Period` and the two `Reference Price` rows. The Solar Wave
manual independently states the Trailing Stop offset *"should roughly double"* the Trend Vector
offset, and 179 ≈ 2 × 90.

**This corroborates parameter NAMES and ORDER. It is not a vendor statement of his values, and
the positional mapping is inference.**

⚠️ **Trap recorded so it is never mistaken for evidence:** that same manual page's worked example
reads `Solar Wave by ninZa.co (NQ 09-26 (1 Minute))` — this campaign's exact instrument and
timeframe. That is vendor marketing picking the most popular contract. It says **nothing** about
the anonymous trader and must never be logged as if it did.

## 14. What could not be found (§44, preserved)

- No property list for **NVI Pro**, **PVI Pro**, **Volume Delta**, **ThunderZilla** (~25 filename
  variants probed against both vendor buckets; verified against known-good manuals).
- No **complete** NT8 grid for *any* product — manuals document only the calculation "Parameters"
  section. Visual/alert/marker properties provably exist but are enumerated nowhere.
- No published defaults except Cosmik rows 24–27 and Solar Wave RK's 60/30 ticks.
- **No NT8 group-header names** documented for any ninZa product.
- No product-grid source for the Jan/Feb-2026 tail motif or the head-of-list two-enum group.
- No documented adjacent property pair taking 14 and 6.
- "LOFI" — **no such ninZa product exists** (full 318-product sitemap enumerated).
