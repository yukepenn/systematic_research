# VF Panel Completeness Note — is the 2026 flagship panel a full ninZa VWAP Flux surface?

Written 2026-08-24. Scope: re-inspection of all 2026-era parameter-panel frames
(OTRIMG-0113/0115/0117/0119/0121/0123/0125/0127/0129/0132/0134/0136/0138/0140/0142/0146/0148/0150/0156/0159/0162/0164)
at pixel level, including magnified crops of every settings-pane scrollbar lane.
Directive context: the public ninZa VWAP Flux UI reportedly contains MORE fields than the 13 observed
(notably a "Zone Period" and possibly other zone/static-level controls). This note records what the
originals can and cannot establish. All statements below are image evidence only; no vendor software
was inspected, and nothing here should be read as a claim about the vendor assembly's internals.

## 0. Direct answers to the two directive questions

**Q1a — Does ANY original screenshot show "Zone Period" or other zone-related controls?**
NO. No frame in the corpus shows any parameter label beginning `Zone`, `Static`, `Level`, `POC`, or
`Profile`. Labels are legible in only two-and-a-half frames:
- OTRIMG-0146 (May 23): full labels for 13 fields — `Volume Base` … `Signal Split (Bars)` — followed
  immediately by the `Data Series` group header. Nothing between `Signal Split (Bars)` and `Data Series`.
- OTRIMG-0134 (Apr 13): row-label initials; the last strategy row before the `D..`(ata series) group is
  `S.` with value 5 → `Signal Split (Bars)` = 5. Confirms the block's lower boundary independently.
- OTRIMG-0125 (Mar 14): group initials `D./T../S../H./O./O.` for the six standard NT8 groups.
Everywhere else only value boxes are visible (labels cropped by the narrowed settings pane).

**Q1b — Scroll-below/above hints?**
YES, in every frame. Every 2026 settings pane carries a thin vertical scrollbar whose thumb is SMALL
(≈40–105 px within a ≈600–640 px track, i.e. 7–17%), so hidden rows exist in EVERY capture. Measured
thumb bands (grayscale run-length scan of the lane column, y-pixels):

| frame | thumb (y-band) | track (y-band) | position | what is visible |
|---|---|---|---|---|
| 0119 | 120–212 | 120–755 | TOP | dropdown pair + gated 10/26/14/198?/180?/140? + two checkbox banks |
| 0138 | 120–179 | 120–743 | TOP | gated blocks + two time windows (4/29 variant) |
| 0150 | 454–502 | 120–743 | MIDDLE (~55%) | 30/70/2/20 variant mid-stack |
| 0115 | 602–708 | 121–758 | low-middle | pre-VF S-tail |
| 0117 | 609–700 | 121–755 | low-middle | head [?,unchk,chk,15] + full VF-13 |
| 0123 | 621–709 | 126–755 | near-bottom | 15 + VF-13 (4 rows above 0121's view) |
| 0121 | 633–721 | 121–755 | near-bottom (12 px below 0123) | mid-VF downward |
| 0132 | 649–714 | 120–759 | near-bottom | head 30?/16/0/10/15 + full VF-13 |
| 0129/0140/0146/0164 | 669–735 / 672–720 / 671–719 / 696–735 | ≈120–743..758 | near-bottom | VF tail + standard groups |
| 0125/0127/0134/0136/0142/0148/0156/0159/0162 | 683..714–753..756 | ≈118–755 | bottom | standard-group tail |

Two consequences:
1. **Thumb position is informative and coherent**: top-scrolled frames show head content, mid-scrolled
   show mid-stack, bottom-scrolled show the tail; 0123 vs 0121 (scrolled 4 rows apart) differ by 12 px
   of thumb travel in the expected direction.
2. **Thumb SIZE is NOT proportionally trustworthy**: a 24–28-row viewport with plausibly 10–30 hidden
   rows should give a thumb of 45–70% of track, not 7–17%. The NT8/WPF skin evidently renders a
   near-minimum-size thumb. Therefore hidden-row COUNTS must NOT be derived from thumb size; only
   ordering/position may be used. (This kills any "the tiny thumb proves ~300 hidden rows" reading.)

**Q1c — Any field beyond the 13 known ones?**
Within the VF-like block: NO — the run `[Volume Base] 60 5 20 [EMA] 95 75 50 25 5 3 10 5 → Data Series`
is witnessed contiguous and closed in ≥9 independent frames (0117, 0121, 0123, 0129, 0132, 0136, 0140,
0146, 0164), with the lower boundary label-confirmed twice (0146, 0134).
ABOVE `Volume Base`: YES — extra rows exist, but they read as the trader's own head controls, not zone
controls: Feb [~num?, unchecked, checked, 15] (0117) → Apr-2 [30?, 16, 0, 10, 15] (0132) → Apr-17
[16, 0, 9, 15] (0136) → Aug-14 [cut-num, CHECKBOX] directly above Volume Base (0164). The head mutates
(values, count, and type) week-to-week while the 13 VF fields stay frozen for six months.

**Q2** — see `2026_VARIANT_LEDGER.csv` (same directory).

## 1. Hypotheses

### H1 — The full licensed VWAP Flux strategy/indicator panel is instantiated as-is
FOR:
- The 13 field names in 0146 match VWAP Flux vocabulary exactly, including the enum literal
  `BidAskPrice_RealVolume` and the compound labels `Signal Quantity Per Trend`, `Signal Close
  Threshold (%)`, `Signal Split (Bars)`.
AGAINST:
- If the public VF UI carries additional zone/static-level controls (Zone Period etc., per the
  directive's description of the vendor page), a faithfully instantiated full panel should show them
  adjacent to the other VF fields. In 9+ frames the block is closed at 13 fields with both boundaries
  witnessed; no zone-labeled row appears anywhere in the corpus.
- The rows bordering the block above are trader-mutable (a numeric `15` sits adjacent Feb–Apr; a
  checkbox sits adjacent by Aug-14; the 10→9 retune on ~4/17 changes a head row, not a VF row). A
  vendor panel does not gain/lose/retype neighbor rows between weekly runs.
- No frame shows a vendor-branded dialog, a license row, a ninZa group header, or the strategy name.
- The strategy plainly carries non-VF machinery the vendor panel does not describe: the recurring
  −$2,600 largest-loss cap (which appears 2/1–2/6, one week BEFORE the first VF-layout frame),
  entries-per-direction=2, session-close exit, and (if the 0119 scroll-top view belongs to the same
  panel) legacy gated blocks and checkbox banks above the head.
VERDICT: **Disfavored.** Not excluded outright only because the head above `Volume Base` is never
fully captured with labels (see §2).

### H2 — Custom strategy exposing selected VF constructor fields (wrapper republishing vendor inputs)
FOR:
- Exact vendor-style names + enum literal, frozen as a contiguous sub-block while surrounding custom
  rows mutate — the signature of a wrapper that re-declares pass-through properties feeding an inner
  component.
- The wrapper would naturally expose only the inputs it uses and omit zone/static-level extras —
  matching the observed closed 13-field surface.
- Composite-panel evidence: 0119 (scroll-top) shows legacy gated blocks + checkbox banks with the SAME
  −$2,600 stop signature as the VF weeks, machine-consistent (hp), sandwiched between VF frames
  (2/8–13 and 2/22–27) — consistent with one large panel whose top is legacy machinery.
AGAINST:
- Nothing in the images distinguishes H2 from H3/H4; no frame shows the inner component. Contiguity of
  0119's banks with the VF block is UNPROVEN (no single frame shows both).
VERDICT: **Consistent with all image evidence; not proven.**

### H3 — Only signal outputs copied (strategy calls the licensed indicator, consumes its signal series)
FOR: Identical panel appearance to H2 — a caller must still surface the indicator's inputs it sets, so
the 13 re-declared fields are equally expected.
AGAINST: Indistinguishable from H2 at panel level; internals unobservable from screenshots.
VERDICT: **Equally consistent; the screenshots cannot separate H2 from H3.**

### H4 — Clean-room reimplementation with similar names
FOR:
- The omission of the vendor's additional zone controls fits someone reimplementing only the subset he
  needed. The trader demonstrably writes NinjaScript (code editor visible in OTRIMG-0053-era frames;
  years of self-modified S-family panels).
AGAINST:
- Verbatim replication of 13 labels including punctuation style and the `BidAskPrice_RealVolume` enum
  literal is more naturally a pass-through of an existing type than re-typed clean-room code (though
  copying names from the vendor's public docs is possible).
VERDICT: **Possible; slightly less economical than H2/H3 given exact-name replication, but not
excludable from images.**

## 2. What would settle it, and standing cautions
- A capture showing the strategy NAME row, or the rows between the 0119-style banks and the
  `30?/16/0/10/15` head, would close the composite-panel question. No such frame exists in the corpus.
- Because every frame hides content above `Volume Base`, a 14th VF field hiding in the unlabeled head
  cannot be strictly ruled out; however the head rows read as small ints/booleans that MUTATE
  (10→9 on ~4/17; checkbox inserted by 8/14), behavior incompatible with a fixed vendor field set.
- **Do NOT conclude "licensed VWAP Flux embedded" from these images.** No image proves direct
  component use. The defensible statement is: *the 2026 flagship exposes a frozen 13-field surface
  whose names match VWAP Flux vocabulary, embedded inside a mutable custom panel; whether the inner
  engine is the licensed component (H2/H3) or a reimplementation (H4) is not established by the
  screenshot corpus.*
- Stop-layer note for reconstruction: the −$2,600 cap is a property of the trader's wrapper era
  (first seen 0115, pre-VF; survives the 0138 structural variant; absent in 0150's variant-2 week
  −1,890; pierced once at −2,820 short in 0162's 3-week window).

## 3. Provenance
Pixel measurements: grayscale run-length scans of settings-pane scrollbar lanes (x≈1395–1436) on the
original JPGs; magnified crops (Lanczos ×4–×6) of 0146 (lane, top-right, bottom-right) and 0132 (head).
Originals untouched (read-only); crops in session scratchpad only. Ledger sources:
`PARAMETER_PANEL_LEDGER.csv`, `IMAGE_MASTER.csv`, `per_image/OTRIMG-*.md`, plus direct Read of every
2026 panel frame listed at top.
