# PROPERTY MATCH MATRIX — EV-007 multi-block screenshot vs vendor catalog (v1, 2026-08-24)

Method (directive §3): each product's settings-UI numeric-run structure + control types +
defaults + release timing + bar-type compatibility, matched against the transcribed
blocks. 17 products fingerprinted (VENDOR_PROPERTY_FINGERPRINTS.csv; manuals archived in
`../vendor_docs/`). NOTE: matching is on TRANSCRIBED blocks — the original screenshot
IMAGES would allow full §3 control-type verification (owner input welcome).

## Ranked verdicts per block

| Block (raw tokens) | Best match | Evidence quality | Runner-up |
|---|---|---|---|
| **[30, 70, 2, 20]** | **Super JumpBoo$t** (rel. 2025-04-10): Extreme Neighborhood=30 / Close Threshold=70 / Qty Per Zone=2 / Split=20 — EXACT 4 consecutive rows, AND equals the vendor's published 100-Tick suggested setting and staff NQ setting | **EXACT-CONSECUTIVE + published-value match** | none close |
| **[80]** | Super JumpBoo$t 1-Minute suggested Close Threshold = 80 | consistent | many (single number) |
| **[65, 30, 75, 20, 46, 36]** | **Cosmik Z-TP** (rel. 2023-12-08) oscillator threshold battery as tuned High/Low pairs: MFI 65/30, RSI 75/20, Stoch 46/36 (defaults 50/50; period/enum rows interleave exactly as the panel does) | STRONG-STRUCTURAL | ApexFlow contrived (rejected); Zephyrus Fib %s (weak) |
| **[10, 26, 14, 19?, 18?, 14?]** | **Cosmik Z-TP** rows 2-7: Offset Mult Trend=10 / Stop=26 / MFI Period=14 / MFI High=19? / MFI Low=18? / RSI Period=14 — both 14s land on factory-default-14 rows | STRONG-STRUCTURAL (default-value anchors) | Zenith-X (rel. 2025-07-22): Fast 10 / Slow 26 / Smooth 14 / Trailing 19 / Term 18 / Qty 14 |
| **[14, 6]** | **ninZaRenko / KingRenko$ bar-type pair** (Data Series pane): Brick 14 / Trend Threshold 6 | PLAUSIBLE-IDIOMATIC | TZ has no fit |
| **[450?, 200?]** | **SpaceGPS Satellite** (rel. 2024-11-09) Volume High/Medium Minimum (defaults 200/50) | PLAUSIBLE | HelloWin Money-Management pair Max Daily Profit / Max Daily Loss (Infinity/Captain; e.g. 4500?/2000? cropped) |
| **[30, 16, 0]** | Cosmik tail (Safe Reversal 30 / Qty Per Trend 16 / Qty Per Flat 0=off) | WEAK | ninZa Bar-Min/Max idiom (0=disabled) |
| **[3, 0, 12, 0]** | two Min/Max pairs (Bar Min/Max idiom, 0=disabled) | WEAK-AMBIGUOUS | Captain sessions EXCLUDED (single HHMMSS ints) |
| **[90, 180?, 3, 6, 9]** (EV-005) | unresolved: Solar-style offsets 90/180 head fits Cosmik/Solar lineage; tail 3/6/9 fits neither Cosmik oscillator rows nor Solar SS/WWS/PS cleanly | UNRESOLVED | keep POSSIBLE_LATE_SOLAR_VERSION open |

## Products positively EXCLUDED as block sources

ThunderZilla, ApexFlow Zignal (13-numeric single run + distinctive defaults absent),
Noble Cloud, NVI Pro / PVI Pro (5 numerics, max run 3), Order Flow Presentation v2
(signature values absent), Captain v1/v2 grids (1/2/3/4 ladder + 9999s + HHMMSS absent),
Infinity grid (7 numerics [2,100,100,999,0,5000,5000]), KingDOM$ (DOM window).

## Synthesis (working hypothesis, Class C — STRONG)

The EV-007 screenshot stack is most consistent with an NT8 panel showing
**Super JumpBoo$t + Cosmik Z-TP (×2 instances — the vendor's own "trend version + risk
version" recipe, forum d/280) on a ninZaRenko/KingRenko$ 14/6 chart**, possibly with a
SpaceGPS or a daily-P/L pair elsewhere in the stack. Dating: **no earlier than
2025-04-10** (SJB release) — consistent with the late-2025 evolution era.
**Implication: the "unknown multi-block family" is likely NOT one mystery strategy but a
MULTI-INDICATOR RENKO SLEEVE built from the same vendor's catalog** — which also
re-opens the door for a Renko-based sleeve in the account (TZ-adjacent ecosystem, though
TZ itself remains excluded on parameter structure).

## What would upgrade this to identification

(a) The original screenshot IMAGES (control-type/order verification per §3);
(b) any visible label fragment (a single word like "Extreme" or "MFI" clinches it);
(c) owner recollection whether those screenshots showed Renko bars.
Cosmik Z-TP and Super JumpBoo$t now join the purchase-priority list AHEAD of ThunderZilla
if Track-B identification is pursued with money (PURCHASE_GATE.md hierarchy updated).
