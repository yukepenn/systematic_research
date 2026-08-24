# TRACK B ROW MAP — H-B1 / H-B2 / H-B3 literal adjudication (2026-08-24, owner correction directive)

Sources verified BY DIRECT IMAGE READING (not agent claims): Cosmik Z-TP settings dialog
(family.ninza.co d/95 post 1462, NQ DEC25 KingRenko$ 12/2 — read by me line-by-line);
Multi-Osc dialogs (staff, d/200 p931 + d/123 p811, two independent screenshots, identical);
Solar Wave RK staff templates (d/200, d/224, Apr-2025); Cosmik Trader Manual §§1.1-1.6
(archived `vendor_docs/cosmik.pdf`); Multi-Osc Trader Manual pp.1-2 (2-page PDF).

## Verified panels (exact vertical order; [e]=enum, [b]=bool, rest numeric)

**Cosmik Z-TP** (manual §1.1-1.6 + dialog): Offset: Unit[e] | Offset: Multiplier Trend |
Offset: Multiplier Stop | MFI: Period | MFI: Threshold High | MFI: Threshold Low |
RSI: Period | RSI: Smooth | RSI: Plot[e] | RSI: Threshold High | RSI: Threshold Low |
Stoch: Period D | Stoch: Period K | Stoch: Smoothing Method[e] | Stoch: Smoothing Period |
Stoch: Plot[e] | Stoch: Threshold High | Stoch: Threshold Low | Safe Reversal Period |
Signal: Quantity Per Trend | Signal: Quantity Per Flat | Level: Qualifying Flat Age (Bars) |
Level: Broken On Body Touch[b]. (Staff NQ values: Tick,60,100,14,50,50,14,3,RSI,50,50,7,14,SMA,3,D,50,50,3,8,2,5,off.)

**Multi-Osc OB/OS Overlap** (2 staff dialogs + manual): MFI: Period | MFI: Threshold High |
MFI: Threshold Low | RSI: Period | RSI: Smooth | RSI: Plot[e] | RSI: Threshold High |
RSI: Threshold Low | Stoch: Period D | Stoch: Period K | Stoch: Smoothing Method[e] |
Stoch: Smoothing Period | Stoch: Plot[e] | Stoch: Threshold High | Stoch: Threshold Low |
Safe Reversal Period. **Identical to Cosmik's oscillator section — Cosmik embeds Multi-Osc.**

**Solar Wave RK** (staff templates + our local vendor templates EV-022): Offset: Multiplier
Trend | Offset: Multiplier Stop | Slowdown Scan (Bars) | Weak-Weak Split (Bars) |
Pullback: Early[b] | Pullback: Split (Bars). Staff Renko ladder: 30/70, 30/80, 50/120,
70/150 (all /5/10/checked/10); trader's 1-min: 90/179/5/10/true/10.

## Block-by-block adjudication

| Block | H-B1 Cosmik | H-B2 Solar+Multi-Osc (King Kong) | Verdict |
|---|---|---|---|
| **[90, 180?, 3, 6, 9]** | IMPOSSIBLE — Cosmik has only 2 offset numerics before MFI; and MFI H=6 < L=9 invalid | **EXACT Solar RK skeleton**: Trend 90 / Stop 180 / SS 3 / WWS 6 / [PE bool] / PS 9 — bool position matches; a faster Solar retune | **Solar RK panel PRESENT (STRONG)** — favors H-B2/H-B3 |
| **[10, 26, 14, 19?, 18?, 14?]** | **CONTIGUOUS fit** rows 2-7: Trend 10 / Stop 26 / MFI P 14 / MFI H 19 / MFI L 18 / RSI P 14 — block boundary lands on RSI Plot[e] ✓; both 14s on rows whose staff value is 14 ✓. CAVEAT: offsets 10/26 ticks are far below every published Solar/Cosmik offset (30-150) — sane only under Offset: Unit=ninZaATR (multipliers) | Multi-Osc head run is only 5 numerics (P,H,L,P,Smooth) — 6-block does NOT fit | **Cosmik-shaped (MODERATE; unit caveat)** — favors H-B1/H-B3 |
| **[65, 30, 75, 20, 46, 36]** | NOT contiguous as thresholds (periods/enums intervene); contiguous only as tail run Stoch H 65/L 30/SafeRev 75/QtyT 20/QtyF 46/FlatAge 36 — semantically ugly (SafeRev 75, QtyF 46) | NOT contiguous either (same section layout) | **Semantic reading (MFI 65/30, RSI 75/20, Stoch 46/36) remains STRONG but requires a values-skipping transcription in EITHER product — cannot discriminate H-B1 vs H-B2.** Needs the screenshot IMAGE |
| **[30, 70, 2, 20]** | — | — | **Super JumpBoo$t EXACT consecutive + published-NQ-value match (unchanged)** |
| **[80]** | — | — | SJB 1-min Close Threshold (consistent) |
| **[14, 6]** | — | — | Renko Brick/Trend pair hypothesis; SECTION LOCATION in the screenshot (Data Series vs indicator group) is the §2 discriminator — needs image |
| **[450?, 200?]** | — | — | SpaceGPS vol minimums OR Max Daily P/L pair — open |
| **[30, 16, 0] / [3, 0, 12, 0]** | Cosmik tail (SafeRev/QtyT/QtyF) weak | — | ambiguous; Bar Min/Max idiom alive |

## Synthesis (honest, not forced)

The stack demonstrably contains: **(a) a Solar RK panel retuned faster (90/180/3/6/9)
[STRONG]; (b) an MFI+RSI+Stoch OB/OS battery — packaged either as Cosmik or as Multi-Osc
[STRONG semantically, packaging UNDECIDED]; (c) Super JumpBoo$t [EXACT]**. That is the
**King Kong decision stack** (vendor's own architecture: Multi-Osc reversals filtered by
Solar Wave trend → pullback signals, + zone/location layer) — whether assembled from the
KK package components or via Cosmik (which productizes the same stack in one indicator).
H-B3 (custom strategy reading multiple vendor signal series) remains fully consistent and
is what the Trade-Performance aggregates independently suggest.

**Not decided:** Cosmik-vs-Multi-Osc packaging; [14,6] location; whether all blocks are one
strategy panel or a stacked indicators dialog. The single most valuable unlock remains the
original screenshot IMAGES.

## Stop-search verdict (owner task 3, closed)

High-coverage NEGATIVE: no 130-pt / 520-tick / $2,600 stop exists anywhere in public
RenkoKings/ninZa material (full forum search API sweep + all 399 renkokings.com sitemap
URLs + all published NQ settings screenshots read). Every published vendor stop is 10-150
ticks; the only "$2,600" in the ecosystem is a license price. **The repeated −$2,600 is
the trader's PERSONAL hard risk cap (520-tick ATM/custom stop), not a vendor template —
a cross-strategy personal fingerprint** (consistent with his $60k/2×DD sizing style, AS-11).
