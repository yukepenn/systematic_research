# 2026 parameter-panel TOPOLOGY reconstruction

Directive v4.0 §20. Written 2026-08-24. Pure image forensics on the FIXED 164-image corpus.
No backtests were run; no code under `src/` or `research/**/src/` was touched; originals were opened
read-only. Every claim below carries exactly one status token: **FACT / REPRODUCED / INFERENCE /
UNKNOWN / FALSIFIED**. Observation and interpretation are never mixed inside one sentence.

Companion machine-readable file: `2026_panel_rows.csv` (612 rows, one per visible panel row).

---

## 0. Scope and method

**FACT.** 22 images in the corpus show the NinjaTrader 8 Strategy Analyzer *Settings* pane with a
2026 report window: OTRIMG-0113, 0115, 0117, 0119, 0121, 0123, 0125, 0127, 0129, 0132, 0134, 0136,
0138, 0140, 0142, 0146, 0148, 0150, 0156, 0159, 0162, 0164.

**FACT.** All 22 are 1440x936 JPEGs, so pixel measurements are directly comparable between them.

**FACT.** Measurements taken for this note, per image: (a) the x-band of the Settings-pane scrollbar
lane; (b) the y-band of the scrollbar trough (track); (c) the y-band of the scrollbar thumb, taken
between the two dark border rows that delimit it; (d) the vertical pitch of the value-box grid
(21.7 px in every frame measured); (e) the full ordered sequence of visible rows, read from
Lanczos-magnified crops.

**INFERENCE (model M1).** The WPF scrollbar renders `thumb_height / track_height = viewport / extent`
and `thumb_top_offset / (track - thumb) = scroll_offset / (extent - viewport)`. Under M1,
`E_rows ≈ (T/21.7) x (T/h)` and the absolute index of the first visible row is
`1 + (s/(T-h)) x (E_rows - V_rows)`.

**REPRODUCED (validation of M1).** Endpoints: my pixel measurement of each frame's scrollbar
(this note) vs the row count of the NinjaTrader-8 standard settings tail that is directly visible in
OTRIMG-0127/0134/0142/0146 (Data Series 4 rows, Time frame 4, Setup 4, Historical fill processing 3,
Order handling 3, Order properties 2, plus 6 group headers = 26 rows). For 17 frames whose last
visible row can be located inside that known tail, M1's predicted "rows still below the viewport"
exceeds the directly countable remainder by a **constant +3 to +5 rows**, with no growth of the error
as E grows from 77 to 543 rows (0113: +3.3 at E=77; 0162: +6.8 at E=543). A multiplicative error in
M1 would have produced an error that scales with E. It does not.
**Consequence:** relative extents and scroll positions are trustworthy; absolute row counts carry a
systematic overestimate of roughly 4 rows plus about +/-1 px of thumb-edge noise (which is +/-3 rows at
h=87 and +/-14 rows at h=35).

**FALSIFIED.** The earlier reading recorded in `screenshot_forensics/VF_PANEL_COMPLETENESS_NOTE.md`
that "thumb SIZE is NOT proportionally trustworthy ... the NT8/WPF skin evidently renders a
near-minimum-size thumb" is falsified by the measurements above: thumb heights range 35-251 px (far
above any WPF minimum), they vary smoothly and monotonically with capture date, and the
proportional model reproduces the independently countable NT8 tail length in 17 frames. The earlier
note's own caution ("hidden-row COUNTS must NOT be derived from thumb size") is therefore withdrawn,
and the falsifier is retained here rather than deleting the earlier claim.

---

## 1. Per-image table: what is visible, and where in the list it sits

`T` = scrollbar track height (px). `h` = thumb height (px). `N = T/h` = how many viewport-heights of
content exist. `first row` = M1 estimate of the absolute list index of the topmost visible row.
Track/thumb bands are FACT (measured pixels); `N` is FACT (a ratio of measured pixels);
`E_rows` and `first row` are INFERENCE (M1-derived, ~4 rows high, see §0).

| image | date (report end) | machine | track y-band | T | thumb y-band | h | scroll pos | N=T/h | first row | E_rows | what the frame shows |
|---|---|---|---|---|---|---|---|---|---|---|---|
| OTRIMG-0113 | 2026-01-30 | dev | 118-764 | 647 | 377-627 | 251 | 65.4% | 2.58 | ~32 | ~77 | pre-VF custom tail + NT8 groups |
| OTRIMG-0115 | 2026-02-06 | mimi | 120-764 | 645 | 602-710 | 109 | 89.9% | 5.92 | ~132 | ~176 | same visible rows as 0113 |
| OTRIMG-0117 | 2026-02-13 | hp | 120-761 | 642 | 613-702 | 90 | 89.3% | 7.13 | ~163 | ~211 | head rows + VF-13 + NT8 groups |
| OTRIMG-0119 | 2026-02-20 | hp | 121-761 | 641 | 127-214 | 88 | **1.1% (TOP)** | 7.28 | ~3 | ~215 | list HEAD: 2 enums, gated numeric block, 2 checkbox banks |
| OTRIMG-0121 | 2026-02-27 | hp | 120-761 | 642 | 639-723 | 85 | 93.2% | 7.55 | ~182 | ~223 | mid-VF downward + NT8 groups |
| OTRIMG-0123 | 2026-03-06 | hp | 120-761 | 642 | 625-711 | 87 | 91.0% | 7.38 | ~173 | ~218 | 15 + full VF-13 + NT8 groups |
| OTRIMG-0125 | 2026-03-14 | dev | 118-765 | 648 | 689-754 | 66 | 98.1% | 9.82 | ~259 | ~293 | VF tail + all six NT8 groups (initials D./T../S../H./O./O.) |
| OTRIMG-0127 | 2026-03-21 | hp | 120-761 | 642 | 692-753 | 62 | 98.6% | 10.35 | ~274 | ~306 | complete NT8 tail, bottom of list |
| OTRIMG-0129 | 2026-03-27 | dev | 118-765 | 648 | 674-737 | 64 | 95.2% | 10.12 | ~260 | ~302 | VF from Trend Period down + NT8 groups |
| OTRIMG-0132 | 2026-04-02 | dev | 118-765 | 648 | 654-716 | 63 | 91.6% | 10.29 | ~255 | ~307 | head 30?/16/0/10/15 + VF-13 |
| OTRIMG-0134 | 2026-04-13 | hp | 120-752 | 633 | 690-746 | 57 | 99.0% | 11.11 | ~293 | ~324 | Signal Split row + all six NT8 groups, label initials visible |
| OTRIMG-0136 | 2026-04-17 | hp | 118-798 | 681 | 690-759 | 70 | 93.6% | 9.73 | ~257 | ~305 | head 16/0/9/15 + VF-13 |
| OTRIMG-0138 | 2026-04-29 | dev | 120-752 | 633 | 126-181 | 56 | **1.0% (TOP)** | 11.30 | ~4 | ~330 | list HEAD: same 2 enums, same gated block extended, two time-window quartets |
| OTRIMG-0140 | 2026-05-02 | dev | 120-748 | 629 | 671-722 | 52 | 95.5% | 12.10 | ~308 | ~351 | mid-VF downward + NT8 groups |
| OTRIMG-0142 | 2026-05-08 | dev | 119-752 | 634 | 696-746 | 51 | 99.0% | 12.43 | ~332 | ~363 | complete NT8 tail, bottom of list |
| OTRIMG-0146 | 2026-05-23 | dev | 119-749 | 631 | 676-721 | 46 | 95.2% | 13.72 | ~353 | ~399 | VF-13 with FULL LABELS + NT8 groups with full labels |
| OTRIMG-0148 | 2026-05-29 | hp | 119-746 | 628 | 695-740 | 46 | 99.0% | 13.65 | ~363 | ~395 | complete NT8 tail, bottom of list |
| OTRIMG-0150 | 2026-06-05 | dev | 119-749 | 631 | 460-504 | 45 | **58.2% (MIDDLE)** | 14.02 | ~221 | ~408 | mid-list: 30/70/2/20, gated block, time quartet, checkbox row |
| OTRIMG-0156 | 2026-06-26 | hp | 119-749 | 631 | 697-740 | 44 | 98.5% | 14.34 | ~383 | ~417 | VF tail 3/10/5 + NT8 groups |
| OTRIMG-0159 | 2026-07-10 | hp | 119-749 | 631 | 707-743 | 37 | 99.0% | 17.05 | ~463 | ~496 | complete NT8 tail, bottom of list |
| OTRIMG-0162 | 2026-07-31 | hp | 120-761 | 642 | 719-753 | 35 | 98.7% | 18.34 | ~507 | ~543 | complete NT8 tail, bottom of list |
| OTRIMG-0164 | 2026-08-14 | hp | 118-765 | 648 | 701-737 | 37 | 95.4% | 17.51 | ~472 | ~523 | head 15?/checkbox + VF-13 + NT8 groups |

**FACT.** Row-by-row contents of every frame are in `2026_panel_rows.csv`. Rows I could not read are
written `UNREADABLE`; no label or value in that file was supplied from imagination.

**FACT.** In every one of the 22 frames the strategy NAME is not visible anywhere on screen. The Jump
Desktop window title shows a machine name ("hp", "dev", "mimi"); the NT8 window title reads "Strategy
Analyzer".

**FACT.** In every one of the 22 frames the thumb occupies less than 39% of the track, so content is
hidden in every capture without exception.

**FACT.** Group separator rows render as an expander triangle plus a label. In the narrowed panes the
label is truncated to "..."; readable group text exists only in OTRIMG-0146 ("Data Series", "Time
frame", "Setup") and as single-letter initials in OTRIMG-0125 and OTRIMG-0134 (D. / T.. / S... /
H.. / O.. / O..).

**FACT (which group is first and last in each frame).** In all 17 bottom-scrolled frames the LAST
visible group is one of the six NT8 standard groups and the FIRST visible group is either a custom
group whose header is above the viewport or the "Data Series" group. In OTRIMG-0119 and OTRIMG-0138
the FIRST visible row is itself a group separator and the LAST visible group is a custom group. In
OTRIMG-0150 the first visible row belongs to a custom group whose header is above the viewport and
the last visible group is a custom group.

**FACT.** "template" (italic link) and the "Run" button sit BELOW the scrollbar trough in every frame,
including OTRIMG-0150 whose thumb is at 58%. They are a non-scrolling footer, not list rows, and are
excluded from the CSV row numbering.

---

## 2. Anchor rows (the rows that let slices be stitched)

**FACT — anchor VF13.** A contiguous 13-row run with byte-identical values appears in nine frames
(0117, 0121, 0123, 0129, 0132, 0136, 0140, 0146, 0164):
`enum | 60 | 5 | 20 | enum | 95 | 75 | 50 | 25 | 5 | 3 | 10 | 5`, always immediately followed by a
group separator.

**FACT — labels for anchor VF13 (OTRIMG-0146 only).** Volume Base = `BidAskPrice_RealVolume`;
Anchor Period (Minutes) = 60; VWAP Amount = 5; Trend Period = 20; Trend MA Type = `EMA`;
Max Percent = 95; Upper Percent = 75; Median Percent = 50; Lower Percent = 25; Min Percent = 5;
Signal Quantity Per Trend = 3; Signal Close Threshold (%) = 10; Signal Split (Bars) = 5. The next row
below is the group header "Data Series"; nothing sits between them.

**FACT — independent lower-boundary confirmation.** In OTRIMG-0134 the row immediately above the
"D.." separator carries the visible label initial `S.` and the value 5.

**FACT — anchor HEAD-A.** OTRIMG-0119 (2026-02-20) and OTRIMG-0138 (2026-04-29) both open with:
`SEP | enum | enum | SEP | checked | 10 | <n> | 14 | 198? | 180? | 140?`, where `<n>` = 26 in 0119 and
20 in 0138. The last three numerics are right-clipped by the box edge; their trailing digits are
UNREADABLE. In 0119 the group's connector line ends after `140?`; in 0138 the same group continues
with `checked | 16 | 6 | 9` before the next separator.

**FACT — anchor PREVF-TAIL.** OTRIMG-0113 (2026-01-30) and OTRIMG-0115 (2026-02-06) show an identical
15-row run: `75 | 20 | 46 | 30 | checked | checked | SEP | 1 | SEP | checked | 80 | SEP | checked | 0 | 2`,
followed by the NT8 standard groups.

**FACT — anchor NT8TAIL.** The six standard groups close the list in every bottom-scrolled frame, with
identical values throughout 2026: Value = 1, Break at EOD checked, Include commission UNCHECKED,
Commission template greyed/disabled, Bars required to trade = 20, Fill limit orders on touch
unchecked, Slippage = 0, Entries per direction = 2, Exit on session close checked.

**FACT — ambiguous anchor MOTIF-30-16-0.** The run `30 | 16 | 0` appears at OTRIMG-0132 rows 1-3 (a
bottom slice) and at OTRIMG-0150 rows 13-15 (a middle slice).
**INFERENCE.** Because the list evidently contains repeated blocks (see the two identical 7-checkbox
masks inside OTRIMG-0119 alone), a value-only match between distant slices does not establish that
the two runs are the same list row. Treated as ambiguous, never as a stitch point.

**FACT — ambiguous anchor BANK-MASK.** Within OTRIMG-0119 the two consecutive checkbox banks have
identical first seven states: unchecked, checked, checked, unchecked, unchecked, checked, checked.

---

## 3. Stitched hypothesis of the full parameter list

Two stitched hypotheses are given, one for the February-2026 build and one for the August-2026 build,
because the list demonstrably changes length between them (§4, cluster verdict V2).

### 3a. February 2026 (E ~ 210-225 rows; sources 0117 @89.3% and 0119 @1.1%)

| abs. index (INFERENCE) | content | status |
|---|---|---|
| 1-2 | UNKNOWN GAP — never captured. This is the only place a strategy-name row could live. | UNKNOWN |
| ~3 | group separator, label UNREADABLE | FACT (0119) |
| ~4-5 | two enum dropdowns, values UNREADABLE | FACT (0119) |
| ~6 | group separator, label UNREADABLE | FACT (0119) |
| ~7-13 | checked, 10, 26, 14, 198?, 180?, 140? | FACT (0119) |
| ~14 | group separator | FACT (0119) |
| ~15-22 | 8-checkbox bank: unchecked, checked, checked, unchecked, unchecked, checked, checked, checked | FACT (0119) |
| ~23 | group separator | FACT (0119) |
| ~24-30 | 7 checkboxes: unchecked, checked, checked, unchecked, unchecked, checked, checked (bank clipped at pane bottom) | FACT (0119) |
| **~31 to ~161** | **UNKNOWN GAP — approximately 130 rows never captured at any February date** | UNKNOWN |
| ~162 | numeric box, top-clipped, digits UNREADABLE | FACT (0117) |
| ~163-164 | unchecked, checked | FACT (0117) |
| ~165 | 15 | FACT (0117) |
| ~166-178 | anchor VF13 (13 rows, values in §2) | FACT (0117 values; 0146 labels) |
| ~179 | group separator "Data Series" | FACT (0146 label) |
| ~180-183 | Instrument, Price based on, Type, Value=1 | FACT (0117 shapes; 0146 labels) |
| ~184 | group separator "Time frame" | FACT (0146 label) |
| ~185-188 | Start date, End date, Trading hours, Break at EOD=checked | FACT |
| ~189 | group separator "Setup" | FACT (0146 label) |
| ~190-193 | Include commission=unchecked, Commission template=disabled, Maximum bars look back, Bars required=20 | FACT (0121/0123/0127) |
| ~194-197 | Historical fill processing: header, Order fill resolution, Fill limit on touch=unchecked, Slippage=0 | FACT (0127) |
| ~198-201 | Order handling: header, Entries per direction=2, Entry handling, Exit on session close=checked | FACT (0127) |
| ~202-204 | Order properties: header, Set order quantity, Time in force | FACT (0127) |

Coverage: about 41 of ~210 rows are observed. **UNKNOWN: ~80% of the February list.**

### 3b. August 2026 (E ~ 520-545 rows; sources 0164 @95.4%, 0162 @98.7%)

| abs. index (INFERENCE) | content | status |
|---|---|---|
| 1 to ~470 | UNKNOWN GAP — no 2026 frame later than 2026-04-29 shows the head, and none shows the middle after 2026-06-05 | UNKNOWN |
| ~472 | numeric, top-clipped; lower glyph halves only; UNREADABLE | FACT (0164) |
| ~473 | checkbox, checked | FACT (0164) |
| ~474-486 | anchor VF13, values unchanged from February | FACT (0164) |
| ~487-512 | the same 26-row NT8 standard tail as in 3a, values unchanged | FACT (0162/0164) |

Coverage: about 30 of ~525 rows are observed. **UNKNOWN: ~94% of the August list.**

### 3c. What the middle slice adds (OTRIMG-0150, 2026-06-05, rows ~221-248 of ~408)

**FACT.** `30 | 70 | 2 | 20 | SEP | unchecked, checked, checked, checked | 14 | 6 | checked | 30 | 16 | 0
| SEP | 3 | 0 | 12 | 0 | SEP | checked, unchecked, checked, checked, unchecked | 5 | checked`.
**INFERENCE.** The quartet `3 | 0 | 12 | 0` has the same shape as the two quartets `13 | 0 | 13 | 30`
and `15 | 0 | 15 | 30` in OTRIMG-0138, i.e. an hour/minute pair repeated twice. Not entailed by the
images; the labels are not visible.

---

## 4. Verdicts per panel cluster

The four options are: **A** different SCROLL SLICES of one long composite list, **B** different
VERSIONS of the same strategy, **C** DISTINCT strategies, **D** unresolved.

### V1 — Cluster FLAGSHIP-TAIL (17 frames: 0117, 0121, 0123, 0125, 0127, 0129, 0132, 0134, 0136, 0140, 0142, 0146, 0148, 0156, 0159, 0162, 0164) — internal relationship
**Verdict: A and B jointly. Confidence HIGH.**
- Pixel evidence for A: every thumb in this cluster sits at 89.3%-99.0% of its track, i.e. all 17 are
  bottom slices; their first visible rows differ by 1-13 rows, which is exactly what re-scrolling the
  same list produces. Directly verified content offset: OTRIMG-0123 row 1 = `15`, row 5 = `20`;
  OTRIMG-0121 row 1 = clipped box, row 2 = `20`. So 0121 begins 3 rows plus a partial row below 0123.
  Measured thumb-top difference 12.5 px over a 556 px travel; M1 predicts 3.9 rows. Agreement within
  one row.
- Pixel evidence for B: thumb heights inside this cluster fall from 90 px (2026-02-13) to 35 px
  (2026-07-31) while the track height stays 628-681 px. A single unchanging list cannot change its
  thumb height. The implied extent grows from ~211 to ~543 rows, i.e. **+12.7 rows per week**
  (least-squares slope over the 20 frames from 2026-02-13, residual spread -34 to +30 rows).
- Content evidence for B: the mutable head above VF13 changes shape between captures - Feb
  `[clipped, unchecked, checked, 15]` (0117); Apr-2 `[30?, 16, 0, 10, 15]` (0132); Apr-17
  `[16, 0, 9, 15]` (0136); Aug-14 `[15?, checked]` (0164, a checkbox now sits directly above Volume Base).
- Evidence against C: the VF13 block's 13 values are byte-identical in all nine frames that show it,
  and the 26-row NT8 tail is identical in all 17. Two distinct strategies would not share both.
- **Falsifier for V1:** a 2026 frame with a bottom-scrolled thumb whose height breaks the monotone
  Feb-to-Aug fall by more than +/-2 px at large h (or +/-4 px at h<50) while showing the same VF13 values
  would falsify B; a frame in this cluster whose first visible row cannot be reconciled with any
  bottom slice of a single list (for example one whose VF13 block is NOT immediately followed by the
  Data Series separator) would falsify A.

### V2 — Cluster TOP-SLICES {OTRIMG-0119, OTRIMG-0138} versus the FLAGSHIP-TAIL cluster
**Verdict: A. Confidence MEDIUM-HIGH.**
- Pixel evidence: OTRIMG-0119's thumb spans 127-214 in a 121-761 track. Its top edge is 6 px below the
  measured trough top, the same 6 px seen for OTRIMG-0138 (126 in a 120-752 track), and the trough
  graphic overshoots the scrollable region by that amount at the bottom too (verified on OTRIMG-0127,
  whose thumb bottom 753 sits 8 px above the measured trough bottom 761 while showing the last row of
  the list). Both top-slice frames are therefore at scroll position 0.
- Pixel evidence for identity of list length: OTRIMG-0119 h=88 in T=641 gives N=7.28; OTRIMG-0117
  (one week earlier, same machine "hp", same window geometry) gives h=90 in T=642, N=7.13. The
  difference is 2 px of thumb, inside the +/-1 px per-edge noise. OTRIMG-0138 (N=11.30, 2026-04-29) sits
  between OTRIMG-0136 (N=9.73, 04-17) and OTRIMG-0140 (N=12.10, 05-02) on the growth curve; its
  residual against the linear fit is -16 rows, well inside the cluster's own -34 to +30 residual spread.
- Cross-machine check: OTRIMG-0119 is machine "hp" like OTRIMG-0117/0121/0123; OTRIMG-0138 is machine
  "dev" like OTRIMG-0140/0142/0146. Extent tracks the DATE, not the machine (0127 "hp" N=10.35 sits
  between 0125 "dev" 9.82 and 0129 "dev" 10.12). So the top slices are not a different machine's build.
- Content evidence: both top-slice frames carry the -$2,600 largest-loss signature that runs through
  the flagship weeks (0119 all three columns; 0138 all and long).
- **Not proven:** no single frame shows both the head banks and the VF13 block. The link is by extent
  and position, not by a shared row.
- **Falsifier for V2:** an extent measurement for either top-slice frame that departs from the
  contemporaneous flagship frames by more than the cluster's own residual spread; or a re-read showing
  the top-slice frames' trough geometry differs from their neighbours (different pane height /
  different lane x-band) in a way that indicates a different window and therefore possibly a different
  analyzer tab.

### V3 — Cluster MIDDLE-SLICE {OTRIMG-0150} versus the FLAGSHIP-TAIL cluster
**Verdict: A. Confidence MEDIUM.**
- Pixel evidence: thumb 460-504 in track 119-749 = 58.2% of travel, with content demonstrably above
  (the first visible row's group connector line is cut at the pane's top edge) and below (the trough
  continues 240 px past the thumb). N=14.02 sits between OTRIMG-0148 (13.65, 05-29) and OTRIMG-0156
  (14.34, 06-26); residual against the fit is -5 rows.
- Content evidence: OTRIMG-0150's largest losing trade is -$1,890, i.e. smaller in magnitude than the
  -$2,600 cap. **INFERENCE:** a week whose worst loss is inside the cap is silent about whether the cap
  exists, so this frame does not contradict the flagship stop layer.
- Consequence: the prior classification of OTRIMG-0150 as a separate build "VARIANT-2 / VAR2026-V2-0605"
  in `screenshot_forensics/2026_VARIANT_LEDGER.csv` is not supported by the scroll evidence. It is
  retained there as a falsified-but-preserved reading; this note supersedes it.
- **Falsifier for V3:** measuring OTRIMG-0150's thumb at a height that puts its extent outside the
  0148-0156 bracket by more than the residual spread; or finding, in some other frame, a bottom slice
  dated 2026-06-05 whose extent disagrees with 14.02.

### V4 — Cluster PRE-VF {OTRIMG-0113, OTRIMG-0115} versus the FLAGSHIP-TAIL cluster
**Verdict: B. Confidence HIGH.**
- Content evidence: the last custom rows before "Data Series" are
  `75 | 20 | 46 | 30 | checked | checked | SEP | 1 | SEP | checked | 80 | SEP | checked | 0 | 2`
  in 0113/0115, and `head rows + VF13` in every frame from 0117 onward. The terminal content of the
  list changes between 2026-02-06 and 2026-02-13. Distinct terminal content means a distinct
  parameter list, not a different view of the same one.
- **Falsifier for V4:** a frame dated on or after 2026-02-08 that shows the 75/20/46/30 run immediately
  above "Data Series", or a frame dated on or before 2026-02-06 that shows VF13 immediately above it.

### V5 — OTRIMG-0113 versus OTRIMG-0115 (the two pre-VF frames)
**Verdict: B. Confidence HIGH.**
- Content evidence: the two frames show the SAME 15-row run in the SAME order with the SAME values;
  0115 shows one extra row at the bottom.
- Pixel evidence: 0113 h=251 in T=647 (N=2.58); 0115 h=109 in T=645 (N=5.92). Same visible tail, 2.3x
  the hidden content. Something on the order of a hundred rows was added ABOVE the visible tail in the
  week of 2026-02-01.
- **Falsifier for V5:** a re-measurement showing 0113's thumb is not ~251 px (e.g. if the light band I
  identify as the thumb were a different widget); the montage of all 22 lanes rules this out visually,
  but a different reader disagreeing on that band would break the verdict.

### V6 — Is any 2026 panel a DIFFERENT STRATEGY (option C)?
**Verdict: D (unresolved), leaning against C. Confidence LOW-MEDIUM on the "against".**
- Evidence against C: no frame in the corpus contains a strategy name, so no frame can be tied to a
  named strategy object. The shared VF13 values and the shared 26-row NT8 tail across all 17
  flagship-tail frames make "several distinct strategies" uneconomical, but they do not exclude it -
  two strategies compiled from the same source file with different names would look identical here.
- **Falsifier for V6:** any frame showing the NT8 Strategy Analyzer's strategy-selector row or the
  window's analysis-tab name. None exists in the 164-image corpus.

---

## 5. What this changes, and what it does not

**INFERENCE.** The 2026 Settings pane is one very long property list - on the order of 200 rows in
February and 500 rows in August - of which each capture shows about 29 rows (7%-39%). The visible
"different-looking panels" of 2026-02-20, 2026-04-29 and 2026-06-05 are most economically read as
the head, the head, and the middle of that same list rather than as three sibling builds.

**INFERENCE.** The list grows at roughly 12.7 rows per week between 2026-02-13 and 2026-08-14 while
the terminal 13-row VF block and the 26-row NT8 tail stay byte-identical. Growth therefore happens
above the VF block.

**UNKNOWN.** What occupies the ~130 uncaptured rows in February and the ~470 uncaptured rows in
August. The corpus is fixed and contains no frame covering them.

**UNKNOWN.** Whether the repeated shapes seen in the captured slices (checkbox bank + integer block +
hour/minute quartet) recur through the uncaptured region. The two identical 7-checkbox masks inside
OTRIMG-0119 and the reappearance of `30 | 16 | 0` at two very different scroll positions are
consistent with repetition but do not establish it.

**Retired terminology used correctly here.** No claim in this note is an ORIGINAL_PARITY claim; the
only REPRODUCED item is the internal validation of model M1 against countable NT8 tail rows
(endpoints named in §0). Nothing here says "bit-exact" or "ground-truth".

---

## 6. Provenance

Originals read-only from `research/original_trader_reconstruction/original_screenshot/`
(OTRIMG ids resolved through `screenshot_forensics/IMAGE_MASTER.csv`). Scrollbar geometry from
grayscale run-length scans of the Settings-pane lane (per-frame lane x-band located automatically,
then fixed: x = 1402-1424 depending on window placement). Row contents read from Lanczos x4-x10
magnified crops of every frame listed in §1; crops live in the session scratchpad only and are not
committed. Row-sequence cross-check against `screenshot_forensics/PARAMETER_PANEL_LEDGER.csv`; all 22
frames were re-read from pixels for this note and no discrepancy with that ledger was found.
