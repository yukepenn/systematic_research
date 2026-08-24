# FAMILY MAP — strategy families and their evidence state

Classes: A = directly observed; B = validated by our prior research; C = high-confidence
inference (labeled); D = unknown. Never silently promote C/D → A.

---

## EARLY FAMILY S — SolarWindRKSelTime

- Name directly observed: `SolarWindRKSelTime` [A]
- Config [A]: NQ, Last, 1-minute, Value=1, Quantity=1, Tick Replay OFF
- Core parameters [A]: A1=90, A2=179, A3=5, A4=10, A5=10
- NT8 settings observed [A]: Max bars lookback 256; Bars required to trade 20; Historical
  fill Standard (Fastest); Fill limit on touch generally OFF; Slippage 0; Entries per
  direction 1; Entry handling All entries; Exit on session close ENABLED; Set order
  quantity Strategy; TIF GTC; Trading hours: Use instrument settings; Break at EOD often
  enabled (NOT proven invariant across versions). Include Commission: some screenshots
  selected, others not; some reports display Commission=0 regardless — handle at
  screenshot-parity level, not by assumption.
- Parameter semantics [B, prior recovered knowledge — verify vs local source in Phase 0]:
  A1=Trend Vector offset (90 ticks = 22.5 pts); A2=Trailing-Stop/trend-reversal offset
  (179 ticks = 44.75 pts); A3=Slowdown Scan; A4=Weak-Weak Split; A5=Pullback Split.
  State machine: directional running close-extreme anchor; uptrend: new closing high
  updates anchor, sufficiently large downside breach flips; downtrend mirror. Trend Vector
  and trailing/reversal stop derive from the same evolving extreme.
  Signal_Trend: +2/+1/−1/−2 (strong up / weak up / weak down / strong down).
  Signal_Trade: ±1 trend starts, ±2 pullback, ±3 strengthening/resumption.
  Signal_Wave: ±1, ±2, ±3, …
- Target fingerprint: EARLY_LONG (2023-01→2025-02): ~$292k / ~4,351 trades / ~40.29% WR /
  ~1.18 PF / ~$32.7k DD / ~$67 avg / ~8.26 trades/day / ~94m hold [A, screenshot tolerance]
- Our Type-1 replica baseline [B]: $146,441 / 2,915 / 39.31% / 1.132 / $22,067 / ~$50 /
  5.56/day / ~108m — WR matches, count/frequency/hold/net do not → mechanism largely
  recovered, WRAPPER not recovered.
- UNKNOWN [D]: SelTime logic; T1/T2/T3 arbitration; pullback timing (PullbackEarly not
  directly observed); exit details; re-entry policy; long/short asymmetry.

## SOLAR RISK VARIANT SD — RKSelTimeDSTM…

- Truncated name observed: `RKSelTimeDSTM...` — remainder UNKNOWN, never invent [A/D]
- Core remained 90/179/5/10/10, Quantity=1 [A]
- Additional parameter [A]: LossLimit=2500 (one screenshot); LossLimit=4000 (another)
- LossLimit semantics [D] — bounded family to test (§13): A per-trade stop cap; B realized
  session loss cap; C realized+unrealized session cap; D daily kill switch; E max
  strategy-loss threshold; F flatten+disable until next session. Also examine Break-at-EOD
  interaction, per-session reset, post-breach signal handling. → LOSSLIMIT_SEMANTICS.md
- DSTM expansion [D]: unknown.

## POSSIBLE_LATE_SOLAR_VERSION (evidence entry, NOT a family)

- Later screenshots appear to show Solar-shaped sequence ~ 90 / 180? / 3 / 6 / 9 [A raw,
  association unproven; second value possibly cropped]
- RULE: do NOT treat as retuned 90/179/5/10/10 by assumption; use only if independent
  repository/source evidence supports the mapping; NEVER optimize early Solar toward these.

## VOLUME FAMILY V — BidAskPrice_RealVolume (2026)

- All parameter labels+values visible [A]:
  Volume Base = BidAskPrice_RealVolume; Anchor Period (Minutes) = 60; VWAP Amount = 5;
  Trend Period = 20; Trend MA Type = EMA; Max Percent = 95; Upper Percent = 75; Median
  Percent = 50; Lower Percent = 25; Min Percent = 5; Signal Quantity Per Trend = 3; Signal
  Close Threshold (%) = 10; Signal Split (Bars) = 5. Instrument NQ, 1-minute [A].
- Exact algorithm [D]. Architecture inference [C]: volume-derived state, 60m anchor,
  VWAP-related structure, EMA20 trend context, percentile ladder 95/75/50/25/5, ≤3 signals
  per trend, close threshold 10%, 5-bar signal separation.
- Open questions [D]: what "VWAP Amount = 5" is; what distribution is percentile-ranked;
  what defines "trend"; what creates a signal; what Signal Close Threshold 10% applies to;
  exact meaning of Signal Quantity Per Trend = 3 [C: likely max three signal events per
  trend episode — labeled inference]; what Signal Split = 5 bars enforces.
- Identification windows: A = 2026-05-10→05-22 (confirmed params, net −$4,055); B =
  2026-08-02→08-14 (strong fingerprint, +$24,145; our data ≥2026-08-01 LOCKED — blocked).
- Data gate (§17): exact reconstruction requires true bid/ask volume classification. If
  unavailable → V-EXACT = BLOCKED PENDING DATA; V-PROXY runs separately; never conflate
  proxy parity with exact parity.

## MULTI-BLOCK FAMILY B — unknown

- Raw visible value groups [A, stored verbatim; ?-marked tokens possibly clipped]:
  `10 / 26 / 14 / 19? / 18? / 14?` ; `90 / 180? / 3 / 6 / 9` ; `450? / 200?` ;
  `65 / 30 / 75` ; `65 / 30 / 75 / 20 / 46 / 36` ; `80` ; `30 / 70 / 2 / 20` ;
  `14 / 6` ; `30 / 16 / 0` ; `3 / 0 / 12 / 0` ; plus multiple booleans/dropdowns.
- RULE: store RAW_VISIBLE_TOKEN and POSSIBLE_INTERPRETATION separately; never silently
  convert 45?→450 or 18?→180 without independent evidence.
- Mechanism [D]. Candidate window: 2026-05-31→06-05 (likely different family per
  directive). Hypothesis families (NOT evidence): trend following / breakout / adaptive
  trend / vol channel / momentum / mean reversion / regime filters / time filters.
  Kaufman book = lineage clue only.
- If unidentified after bounded search: retain FAMILY_B = UNKNOWN MULTI-BLOCK.

## TRACK VF — VWAP Flux hypothesis (opened 2026-08-24, PRIMARY Track-V interpretation)

- External evidence [A, EV-014]: ninZa VWAP Flux docs — AnchorPeriodMinutes = per-layer
  duration; Amount = number of recent VWAP layers retained; 5-level value map
  Highest/Upper/Median/Lower/Lowest; Signal_Trend; Signal_Cum_Delta added 2026-02-09.
  Structure matches EV-006 (Anchor 60 / VWAP Amount 5 / 95-75-50-25-5) closely.
- Working reading [C]: the trader's 2026 "Volume" strategy is built on VWAP Flux (or a
  close relative) — NOT an invented volume-percentile ladder. The 08-23 V-proxy
  (prev-hour percentile ladder, runs OTR_V1..V3) is preserved as a behavioral-mimic
  artifact but demoted.
- To resolve [D]: exact layer mechanics (rolling vs segmented; live vs frozen layers);
  what the Percent parameters position; Signal Close Threshold/Split semantics in Flux.

## TRACK TZ — ThunderZilla hypothesis (opened 2026-08-24, high-EVI, unconfirmed)

- External evidence [A, EV-015]: RenkoKings ThunderZilla changelog 2025-08-11 adds
  "Signal: Quantity Per Trend" — near-verbatim match to the EV-006 label; TZ =
  trend/pullback/momentum/trailing-stop system exposing Signal_Trend/Signal_Trade; same
  vendor ecosystem as Solar; forum NQ settings exist (VWMA or EMA trend).
- Hypothesis [C]: some late-2025/2026 multi-block screenshots (Track B's raw token
  groups) may be ThunderZilla or a strategy wrapping it. NOT concluded as used.
- Adjudication path: match public property list/ordering + defaults against the raw
  visible blocks (EV-007); search local NT8 templates/configs/logs for artifacts;
  behavioral test only if the mechanism is publicly documented well enough.

## ACCOUNT / COMBINATION P

- Trade Performance reports 2026-06-07→12 (136 trades, 32.83/day, 20.49m hold, WR 50%)
  and 2026-06-14→18 (78 trades, 34.10m hold) = POSSIBLE_ACCOUNT_OR_MULTI_STRATEGY_EVIDENCE
  [A]; exact TP filters UNKNOWN [D].
- Architecture hypotheses (§27, test both): H1 = total account exposure ±1 NQ; H2 = each
  strategy qty=1 with possible overlap. Adjudicate via TP frequency/WR/hold/commission/side
  counts, not preference.
- Phase 9 only after individual families have credible candidates. No Sharpe-maximizing
  portfolio weights — identification only.
