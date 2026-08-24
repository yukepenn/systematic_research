# PRE-AUDIT HYPOTHESIS FREEZE — committed BEFORE reading any original_screenshot image

Date frozen: 2026-08-24 (owner master continuation directive v2.0, §1).
Corpus at freeze time: `research/original_trader_reconstruction/original_screenshot/`
= 164 files (149 .jpg + 15 .png), all filenames `20260824_HHMMSSmmm_iOS.*` (iPhone
camera-roll export timestamps of TODAY — filename dates are EXPORT dates, not capture
dates; no image content has been inspected yet).

Purpose: protect against hindsight contamination. Everything below is the belief state
as of commit `3c932ca` (end of the H-B adjudication pass), BEFORE the image corpus is
consumed. After the audit, each item must be graded: CONFIRMED / REVISED / FALSIFIED /
STILL-OPEN, with image IDs as evidence.

Evidence-class convention (unchanged): A = directly observed; B = prior-validated
(e.g. recovered Solar math); C = labeled inference; D = unknown.

---

## A. EARLY SOLAR (2023 → late-2025)

Candidate identity: **SolarWindRKSelTime**, NQ 1-minute, Qty 1, params 90/179/5/10/10
(PullbackEarly believed true; from vendor-template convention). Engine believed to be
Solar Wave RK math (Class B — recovered: close-anchor state machine, flips at
anchor∓StopMult ticks, T1/T2/T3 signal taxonomy).

Wrapper candidate **OTR-S-CAND1** (Class C, MODERATE confidence):
- T1 + T3 entries when flat; stop-and-reverse on opposite flips
- SelTime entry window ≈ 04:00–16:00 ET, force-flat outside
- inclusive TrailingStop touch exit (S0-certified NT8 convention); session-close exit
- Known residual vs the ~$292k / 4,351-trade long-history screenshot: trades +7.2%,
  WR −0.5pp, PF −0.039, DD −0.7%, net −13.1%, hold −20.3% (hold is the out-of-band one).
- S13: regime-local (2023-25 strong, 2026 −78k on frozen params).
- "Unconditional T2 entries strongly disfavored" (NOT "author never used T2").
- RTH-only wrapper arithmetically impossible (759 in-market min/day required).

## B. LATE SOLAR (2025 evolution era)

[90, 180?, 3, 6, 9] read as an EXACT Solar Wave RK panel skeleton (Trend 90 / Stop 180 /
Slowdown Scan 3 / Weak-Weak Split 6 / [Pullback: Early bool] / Pullback: Split 9) —
a FASTER Solar retune present in the 2025 multi-block stack. Status: STRONG structural
inference (Class C), NOT yet image-confirmed. Might instead belong to another strategy
or component. Coexistence with 90/179/5/10/10 unknown.

## C. TRACK B (multi-block 2025 screenshots, EV-007 etc.)

Incumbent stack hypothesis (from vendor fingerprint DB + row maps, Class C):
- Super JumpBoo$t: [30,70,2,20] EXACT consecutive published-NQ values; [80] = 1-min
  Close Threshold. STRONG.
- Oscillator battery [65,30,75,20,46,36] = semantic MFI 65/30, RSI 75/20, Stoch 46/36 —
  STRONG semantically but contiguous in NEITHER Cosmik nor Multi-Osc panel (both share
  an identical 16-row osc section; Cosmik embeds Multi-Osc). Packaging (Cosmik Z-TP vs
  Multi-Osc OB/OS Overlap vs custom) UNDECIDED.
- [10, 26, 14, 19?, 18?, 14?] = Cosmik-contiguous rows 2-7 (Trend 10 / Stop 26 / MFI
  14/19/18 / RSI 14) MODERATE, with offset-unit caveat (10/26 plausible only as
  ninZaATR multipliers).
- [14, 6] = suspected Renko Brick/Trend pair (KingRenko$ / ninZaRenko). SECTION LOCATION
  UNPROVEN — could be primary Data Series, secondary series, indicator-internal, or crop
  artifact. This is a key discriminator to resolve from images.
- [450?, 200?] = SpaceGPS volume minimums OR a Max Daily Profit/Loss pair — OPEN.
- King Kong Trading RK (2023-10-19, Solar×Multi-Osc pullback architecture) believed to be
  the vendor-official DESIGN matching this stack. Whether author bought KK package,
  Cosmik, or assembled custom: UNKNOWN.
- ThunderZilla: DOWNGRADED (documented params ≠ blocks; Renko-only); ApexFlow / Infinity /
  Captain Optimus: SPECULATIVE meta-layers, no property evidence.

## D. TRACK V (2026 1-min system)

**VWAP Flux (ninZa, released 2026-01-09)**: 13/13 ordered param-label schema match
(EV-006): Volume Base = BidAskPrice_RealVolume | Anchor Period (Minutes) 60 | VWAP
Amount 5 | Trend: Period 20 | Trend: MA Type EMA | Levels 95/75/50/25/5 | Signal:
Quantity Per Trend 3 | Signal: Close Threshold (%) 10 | Signal: Split (Bars) 5.
Component identification HIGH CONFIDENCE (currently Class C+; expect image audit to
possibly raise to Class A). Internal signal formulas UNRESOLVED; our VF4
anchored-cumulative + quantile clone = HIGH-QUALITY BEHAVIORAL CLONE, not source-exact
(official language: "linear-based methodology"). Architecture choice (anchored-cumulative
layers, hourly rotation) was selected on vendor chart-image fidelity.

## E. RISK

- Repeated largest losses ≈ exactly −$2,600 (EV-017, multiple 2026 screenshots) currently
  attributed to a PERSONAL per-position hard stop ≈ 130 NQ pts = 520 ticks = $2,600
  (intrabar; VF2 reproduced exact −2600 tails; LossLimit-2500-bar-close REJECTED for the
  2026 family). Vendor-stop search HIGH-COVERAGE NEGATIVE (all published vendor stops
  10-150 ticks). Attribution to specific strategies/windows: PENDING — this audit must
  establish which families/windows actually show it.
- Separate concept: RKSelTimeDSTM… LossLimit 2500 / 4000 (SD era, late 2025) — believed
  session-level (weakly favored) or inert per-trade; DSTM meaning unknown.
- These two risk mechanisms must NOT be conflated (directive §30).

## F. ACCOUNT

- Author ran SEVERAL strategies simultaneously (AS-1, direct statement) — multi-sleeve
  account CONFIRMED conceptually; architecture E (independent sleeves) CONFIRMED at
  account level: June-2026 Trade Performance aggregates require ≥3 behavioral profiles
  (≈8/day-94m + 15-19/day-40m + short-hold-high-WR).
- Exposure netting (±1 net vs several ×1 gross) UNKNOWN (H1-H4 open, directive §28).
- Trade Performance commission ≈ $1.04/trade UNEXPLAINED vs author's "~$2 RT" statement.
- Capital: ~$60k stated; historical DD ~$30k+ (AS-11); sizing style ≈ 2×DD.

## G. TIMELINE BELIEFS (to be re-derived from images independently)

- 2023-01 → 2025: SolarWindRKSelTime era (90/179/5/10/10).
- Late 2025: DSTM (LossLimit) variants + multi-block King-Kong-style stack appears
  (SJB released 2025-04-10 = lower bound for stacks containing it).
- 2026-01: VWAP Flux released 01-09; author's system change follows within days;
  changepoint map v1 clusters 2026 weeks as V-like + ≥1 concurrent family.
- 2026-03-22→03-27: ≈ −$42,235 disaster window (identification gold, directive §62).
- Author 2025 self-reported ≈ $150k+; weekly Notes timeline has known 1/4-1/9
  discrepancy preserved in AUTHOR_REPORTED_NQ_RESULT_TIMELINE.csv (28 weeks).

## H. KNOWN PRIOR EVIDENCE OBJECTS (pre-image-corpus)

EVIDENCE_LEDGER.csv EV-001..EV-028 (transcribed text descriptions of screenshots the
owner previously relayed + vendor/public sources); AUTHOR_STATEMENTS.md AS-1..AS-12;
TARGET_WINDOWS.csv (22 windows); AUTHOR_REPORTED_NQ_RESULT_TIMELINE.csv (28 weeks).
The image corpus supersedes relayed descriptions wherever they conflict (original pixels
outrank secondhand transcription).

---

## Falsification watchlist (what would overturn each incumbent)

| Incumbent | Would be FALSIFIED / forced-revised by |
|---|---|
| OTR-S-CAND1 04:00–16:00 SelTime | a visible SelTime/session panel showing different times |
| Late-Solar [90,180,3,6,9] | readable labels showing a non-Solar product; or MFI/RSI labels around those values |
| Cosmik contiguous [10,26,...] | visible labels showing e.g. VWAP/volume params instead |
| Osc-battery semantic reading | labels showing the six values belong to a different section |
| SJB [30,70,2,20] | labels ≠ Extreme Neighborhood / Close Threshold / Qty Per Zone / Split |
| [14,6] = Renko | visible Data Series pane showing 1-min primary AND [14,6] in a non-bar context, or vice versa |
| VWAP Flux identity | the 13-label panel differing from ninZa's schema on any visible label/order |
| Personal $2,600 stop | a visible vendor/ATM template named with 520t/2600; or −2600 appearing in only ONE family (would weaken "cross-strategy personal") |
| Multi-sleeve account | evidence all results come from a single strategy |
| "consistently profitable" reading | capture-lag / retrospective-fit evidence showing key results are post-hoc backtests |

No image content has been read at freeze time. First-pass review will use
WORKING_NOTES.md; CURRENT_TRUTH.md will NOT be updated until 100% first-pass +
second-pass QC complete (directive §58).
