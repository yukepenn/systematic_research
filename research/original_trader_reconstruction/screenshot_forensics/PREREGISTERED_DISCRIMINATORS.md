# Preregistered forensic discriminators (directive §65 — written BEFORE targeted evidence inspection)

Committed before the first-pass agent transcriptions are read back and before any
targeted deep-read/crop of specific panels. Each test states what each hypothesis
PREDICTS so the observation cannot be reinterpreted post-hoc.

## T1 — Cosmik Z-TP vs Multi-Osc OB/OS Overlap packaging (osc battery)
Verified panel layouts (TRACK_B_ROWMAP.md):
- Under H-B1 (Cosmik): the oscillator rows are PRECEDED, in the SAME property group,
  by "Offset: Unit"[enum] + "Offset: Multiplier Trend"[num] + "Offset: Multiplier
  Stop"[num], and FOLLOWED by "Signal: Quantity Per Trend / Per Flat" + "Level:
  Qualifying Flat Age (Bars)" + "Level: Broken On Body Touch"[bool].
- Under H-B2 (Multi-Osc standalone): the visible group STARTS at "MFI: Period" (no
  Offset rows above it in the same group) and ENDS at "Safe Reversal Period" (no
  Signal:/Level: rows below).
- DISCRIMINATOR ROW: whatever sits immediately ABOVE the first "MFI:" label and
  immediately BELOW "Safe Reversal Period" inside one bordered group. Enum row above
  MFI ⇒ Cosmik. Group boundary above MFI ⇒ Multi-Osc.
- If only numbers (no labels) are visible: Cosmik predicts 2 numerics + 1 enum above
  MFI: Period; Multi-Osc predicts a section header/indicator name above MFI: Period.

## T2 — [14, 6] identity
- H-A (primary Renko Data Series): [14,6] appears in a Data Series/chart header
  context ("KingRenko$ 14, Trend 6" idiom or bar-type descriptor near instrument
  name), NOT inside a strategy parameter group; SA "Data series" pane would show a
  Renko-type bar with value(s).
- H-B (secondary/indicator-internal): [14,6] appears INSIDE an indicator/strategy
  property group whose neighbors are non-bar-type parameters; primary Data Series
  elsewhere shows 1 Minute.
- H-C (unrelated pair/crop artifact): the two numbers are not vertically adjacent
  rows of one group, or belong to labels inconsistent with brick/trend.
- PREDICTION under incumbent (D open): if the 2025 multi-block screenshots show a
  visible Data Series value "1 Minute" AND [14,6] in a parameter group, H-B wins;
  if bar rendering in any co-located chart is uniform-brick, H-A gains.

## T3 — Late-Solar [90, 180?, 3, 6, 9]
- H-Solar-retune predicts: 5-6 numeric rows in one group, order Trend/Stop/
  Slowdown/WeakWeak/[bool]/Split, with a CHECKBOX between the 4th and last numeric
  (Pullback: Early), labels starting "Offset:"/"Pullback:".
- H-other-product predicts: labels not matching that skeleton (e.g. MFI/RSI labels,
  or VWAP labels) around those numerics.
- KEY ROW: the presence and position of a lone checkbox inside the numeric run.

## T4 — SelTime window (OTR-S-CAND1 says entries 04:00–16:00 ET)
- If any settings panel shows time-type controls (time pickers / HHMM numerics):
  record EXACTLY. CAND1 predicts a start ≈ 04:00 and end ≈ 16:00 (ET) or an
  equivalent pair in another timezone base (e.g. 03:00/15:00 CT). A materially
  different pair FORCES wrapper revision (directive §29). Two numerics 4/16 or
  400/1600 in a group with time-like labels count.

## T5 — −$2,600 attribution
- H-personal-cap (incumbent) predicts: largest-loss ≈ −2,600 appears in ≥2 DIFFERENT
  strategy families / report types, and NO settings row anywhere shows a vendor stop
  labeled 520/2600.
- H-family-stop predicts: −2,600 confined to ONE family (e.g. only VF-era reports).
- H-LossLimit-overshoot predicts: largest losses scatter ABOVE 2,600 (−2,7xx/−3,1xx)
  rather than repeating exactly.
- Measurement: RISK_EVENT_LEDGER.csv largest-loss column across all transcribed
  reports, clustered by family + era.

## T6 — VWAP Flux panel (13-label schema)
- Incumbent predicts, in exact order: Volume Base[enum] / Anchor Period (Minutes) /
  VWAP Amount / Trend: Period / Trend: MA Type[enum] / Level: Max (%) / Level:
  Upper (%) / Level: Median (%) / Level: Lower (%) / Level: Min (%) / Signal:
  Quantity Per Trend / Signal: Close Threshold (%) / Signal: Split (Bars), values
  60/5/20/EMA/95/75/50/25/5/3/10/5.
- ANY visible label deviation (name or order) on an otherwise-matching panel
  FALSIFIES the product identification (not just weakens).
- First-appearance test: no VF-schema panel may appear in a report window ending
  before 2026-01-09 (product release). One earlier appearance falsifies.

## T7 — Commission regime
- EV-002 era (long history): commission INCLUDED ≈ $4.18/trade (observed in
  OTRIMG-0002: $18,187.18 / 4,351).
- Weekly 2025-08 sample (OTRIMG-0058): commission $0.00.
- PREDICTION to test: weekly SA screenshots systematically omit commission ($0)
  while long-history and Trade Performance include it; author's "~$2 RT" refers to
  per-side ≈ $2.09 (i.e. $4.18 RT) — if instead many reports show ≈$2.xx/trade
  totals, the per-side reading is wrong.

## T8 — Live vs backtest
- Contemporaneous-weekly-monitoring predicts: CAPTURE_LAG (menu-bar date minus
  report end date) ≤ 3 days for most weekly SA screenshots (like OTRIMG-0002: 0d).
- Retrospective-rerun predicts: clusters of large positive lags, and/or the same
  report window appearing with different settings-column values in different images.
- Measurement: per-image capture-lag table + same-window duplicate diffing.
