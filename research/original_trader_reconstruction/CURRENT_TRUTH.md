# OTR CURRENT TRUTH (prepend-newest)

## 2026-08-24j — NT8/CrossTrade UNLOCKED: R6 parity BIT-EXACT; June-July data ingested; VF-CAND1 survives TRUE OOS

Owner re-authorized CrossTrade (recorded in runs/OTR_R6_NT8_PARITY/spec.yaml);
full self-serve loop now: sandbox compile -> Strategy Analyzer backtest via MCP.
- **R6 PARITY (PHASE C3 §8): PASS.** Layer A Jan-2023 cent-exact 91/91,
  $6,815.00 == $6,815.00, trade-for-trade. Layer B two-year master BIT-EXACT:
  4,592/4,592 trades, $279,655.00 net, DD −30,305.00, consec 7/15, ZERO trade
  differences across 735k bars (the 1 unserialized = known boundary quirk).
  Layer C: one window EXACT, others ≤1-trade data-source deltas. §51-E CLOSED:
  Python ↔ NinjaScript ↔ NT8 Analyzer end-to-end. (v1 port had an int-overflow
  cooldown bug caught by zero-trade smoke; fixed in v2, class renamed.)
- **R6-DATA**: June-July 2026 per-contract 1-min exported via SA runs
  (JUN26 + SEP26, pre-seal, hashed into research/original_trader_reconstruction/data/).
- **R8-A TRUE OOS: OTR-VF-CAND1 cluster survives** (preregistered prediction
  held; all distances 0.327-0.668). Leader T_C|P_MED|C_DIR|H1a|X_OPP stable
  (6/28 window d=0.338, net 7,985 vs 8,630); T_D|H1c member DEMOTED (−32.5k
  swing on a +8.6k week). −2,600 stop reproduces OOS. Residual unchanged in
  kind: WR gap + missing extra edge in his biggest weeks.
- **R8-B**: 6/14-18 TP week is flagship-sized by count (VF 72 vs TP 78) but
  carries a REAL-EXECUTION 65-pt-class stop (LL −1,426.18) → some 65-pt-stop
  sleeve still live in June. 6/7-12 (n136, WR50, hold 20.5) stays
  UNDER-EXPLAINED — the fast/tight layer (variant-2 era) is the missing
  carrier. No weights fitted.

## 2026-08-24i — CONVERGENCE PASS (directive v3.0 C3/C4/V1-V5 + recon): NT8 port, VF clean-room, OTR-VF-CAND1, purchase-EVI downgrade

- **C3**: OriginalTraderSolarCAND2_v1.cs written (research-only, fail-closed);
  parity protocol staged (CAND2_NT8_PARITY_PROTOCOL.md; analyzer execution
  owner/UI-gated). Gate-semantics member test R1.j: fill-bar vs decision-close
  IDENTICAL on the whole master (0 stream diff) — NT8-native semantics adopted
  free. Directional-stop test: long Initial=65 CONFIRMED; short stop
  TIME-VARYING 65↔75 in era B (exact −1385/−1500 hits vs exact −1300 caps in
  different weeks; both members kept).
- **C4**: RISK_STATE_MACHINE_2025.md (layered stack; D/M literal REJECTED for
  dev build) + FEB2025_FAST_BUILD.md (DSTMa fast layer: freq 4-10× with A-panel
  UNCHANGED → additional tight-risk entry layer; slowed to 8.4 t/day by May;
  the SAME layer family whose knobs (A3-A5) the Nov retune touched).
- **V1/V2**: vf_core clean-room (ANCHOR vs BLOCK quantified: width 47 vs 106
  pts, movers 5.0 vs 1.3/bar; percentile-vs-minmax discriminator = FVP-midspan
  offset 8.9 pts vs ≡0). PUBLIC_ANALOGUE_MAP: VF-ANCHOR+percentile is the only
  publicly-precedented construction (LuxAlgo full source, license recorded).
- **V3-V5 (R7/R7b, 208 members, no free constants): OTR-VF-CAND1** = trend
  close-vs-FairValue+EMA20-agreement → pullback to Median/rail → close-quality
  confirm (H1a extreme-toward reading dominates; manual-verbatim H1c mid-pack;
  H1b rejected) → SAR/flip exit; QtyPerTrend 3, Split 5, 130-pt stop. Leader
  mean §40 distance 0.476 (LOWO 13/17); failure week 3/22-27 right SIGN in all
  survivors, 23-63% magnitude; one member DQ'd for failure-week profit (§32).
  4-member cluster INSEPARABLE (§6) — separation needs Signal_Trade timestamps
  or per-day 2026 labels.
- **Vendor-model finding (EV-038/039 + img/pub recon)**: manual pins Split/
  QtyPerTrend/CLV-family semantics; official changelog verbatim (2/9
  Signal_Cum_Delta added; 2/24 Signal_Trend 2→4-state). **EV-039: in the
  trader's displayed mode (BidAskPrice_RealVolume, Tick Replay OFF) the
  licensed indicator computes NOTHING historically → his SA backtests cannot
  be the embedded licensed indicator in that mode.** With the frozen VF-13
  block amid mutating neighbor head fields, no Zone Period in ANY frame, and
  zero local artifacts: **own-implementation (H3/H4) now leads**; prior
  "custom wrapper on licensed VWAP Flux" wording downgraded. PURCHASE GATE
  stays CLOSED with EVI downgraded (oracle would answer vendor semantics, not
  his build's).
- **Recon extras**: −$2,600 cap PRE-DATES the first VF frame (2/1-6 week, old
  S-family tail — wrapper/account-level stop, not VF-module); THIRD machine
  "mimi" identified; 2026_VARIANT_LEDGER.csv (6 variants); variant-2 week LL
  −1,890 (cap absent), one −2,820 pierce in a live-slippage window.

## 2026-08-24h — R5 WEEKLY VALIDATION: CAND2 passes dev-machine OOS; residual is MACHINE-correlated (directive v3.0 PHASE C1)

Full-fingerprint, version-aware run of frozen CAND2 against all 28 late-2025
weekly targets (runs/OTR_R5_CAND2_WEEKLY_VALIDATION/). Prestate frozen in
OTR_CONVERGENCE_PRESTATE.md. Key results:
- **CAND2 (noDM) matches every dev-machine week at ±7% mean count error, holds
  within ~7 min, LL structure correct — 9 windows, fully OOS.** Near-exact weeks:
  10/26 (50/50 trades, net −3,310 vs −3,330), 11/23 (−15,405 vs −15,365), 1/4/26.
- **hp-machine weeks are a sibling build**: +39.5% overtrade vs targets, longer
  holds, much larger winners (both +18.5k trend weeks are hp; missed by −20/−25k).
  Leading hypothesis (partly era-confounded; 10/26 hp fits CAND2): EV-035
  multi-strategy per-machine split. 12/21 Christmas stand-down (tgt 9 vs sim 17).
- **Literal D/M halts (M2000/D4500) REJECTED for the dev/CAND2 build**
  (over-suppresses −27.6%); partially explanatory but erratic for hp.
- **A3-A5 retune (→3/6/9, 11/7) is INVISIBLE to a T1-only model (old≡new179
  streams bit-identical) → the trader's build contains an ACTIVE pullback layer**
  whose frequency those params control. Confirms the master-residual reading.
- **St-row3 65→75 (11/14) is NOT the Initial stop**: exact −1,300 rows persist
  through Jan; −1,500.00 exact appears 1/4 week short side; era-B LL>1300 rows
  are mostly SHORT-side → directional/second stop tier OPEN.

## 2026-08-24g — R1-R4 RECONSTRUCTION EXECUTED; OTR-S-CAND1 RETIRED → OTR-S-CAND2 (verified model class)

Cent-level identification against the trader's own per-day table (OTRIMG-0003).
- **Engine/data/conventions validated TO THE CENT** (whole days trade-for-trade;
  master largest-loss −4,449.18 and largest wins reproduce exactly).
- **FALSIFIED: 04:00-16:00 SelTime window; T3-entry participation; vendor-mode T2
  at the decoded resume bar (armed-latch arithmetic); first-bar-breakout as a
  global gate; always-on 30-pt trail; 65×2 microstructure for the 2026 −2600.**
- **OTR-S-CAND2** (solar_family/TRACK_S_REPORT.md): T1-flip stop-and-reverse chains
  + B1 first-bar drop + session equity wrapper (evening-after-red ≤−C; armed at
  high≥X≈1600 past noon: cum<0 stops all, K=3 same-side consec losses stops side;
  X2≈2500 pre-noon; ~20/session cap; 3-bar cooldown) + early-close-evening resume
  via SECOND-BREAKDOWN LATCH (fill decoded to the cent; reference level ambiguous
  among 4 candidates). Adversarially re-implemented: 42/42 cent-certain labels;
  structure confirmed, constants interval-identified; one equally-consistent rival
  member (4 TOTAL same-side losses) not separable on available data.
- **Master fit (best config): n +5.7%, net −9.3%, WR −0.2pp, PF −0.03, DD −2.3%,
  holds L/S 109.6/81.9 vs 105.9/82.6, consec 7/15 vs 8/15** — band-edge across the
  board (CAND1 was net −13% / hold −20%). Residual (+247 tr, −27.2k, short-side,
  chop-months) = his hard-coded pullback/resume signal layer, not more gating.
- **R2**: St-group In=65 = 65-pt intrabar initial stop CONFIRMED (−1300.00-cap
  signature; gap-through overshoots); always-on trail falsified; +20pt-activation
  trail viable. **R3**: 2026 −2600 = 130-pt × qty-1 CONFIRMED (row discriminator);
  onset week 2/1-6 incl. per-side columns; variant-B week uncapped; LIVE TP shows
  −3,046.18 = ~22-pt stop slippage; tick-true input fidelity bound: trend-state
  disagreement only 1.7% → VF residual is the proprietary trigger, not inputs.
- **R4**: real ≈ posted ×0.79 (2025) / ×0.89 (2026) at $2.08/RT + 1-tick slippage.
- Late-Feb-2025 DSTMa transitional build diverges (90-trade day, avg loss −$331)
  — documented, out of CAND2 scope. Runs: OTR_R1_SERIES (3 amendments), R2, R3;
  hunts/verifications in runs/OTR_R1_SERIES/out/ (hunt_*, v_*).

## 2026-08-24e — ORIGINAL-SCREENSHOT CORPUS AUDIT COMPLETE (164/164; owner directive v2.0, phases IMG-0..15)

Formal truth update after 100% first-pass transcription + >11% pixel-level QC.
Authoritative artifacts: `screenshot_forensics/` (IMAGE_MASTER, per_image/×164,
PARAMETER_VERSION_TIMELINE, CHANGEPOINT_MAP_v2, STRATEGY_EVOLUTION_TREE,
SCREENSHOT_AUDIT_REPORT [45 Q], BACKTEST_VS_LIVE_AUDIT, CONTRADICTION_LEDGER,
AUTHOR_RESEARCH_PROCESS, POST_SCREENSHOT_RECONSTRUCTION_PLAN + 7 CSV ledgers).

**Class-A identity (pixels):** Strategy `SolarWindRKSelTime`, params obfuscated
**A1=90 A2=179 A3=5 A4=10 A5=10, Quantity=1**, NQ front 1-Minute Last, TickReplay
off, Break-at-EOD ✔, lookback 256, BarsRequired 20, Standard(Fastest), trading hours
= instrument default → **SelTime window is HARD-CODED (no time params exist)**.
Master 2023-01→2025-02-02 = +$292,172.82 / 4,351 tr / comm $4.18/RT INCLUDED,
captured 2/2/2025 23:57, live next morning. Renamed `RKSelTimeDSTMa` + LossLimit
4000→2500 by 2/18; commission $0 from 2/28 (author-admitted laziness, 0098).

**Track-B REFRAMED (falsifications):** the multi-block panels are the SAME A-param
strategy accreting THE AUTHOR'S OWN groups: M…(E✔,D 4500,M 2000 daily money pair),
**St…= STOP group (In 65/Tr 30/I 65/M 20 — label initials read; −$1,300=65-pt caps
in 2025 reports)**, U…(E✔,80), later [☑10/26/14/**198?/180?/140?** (3-digit!)];
A3-A5 retuned 5/10/10→**3/6/9** between 10/24 and 11/7/2025. → **Cosmik, Multi-Osc,
SJB-as-product, King-Kong-as-package: FALSIFIED as sources** (osc-threshold reading
impossible: values >100 + stop-group labels). [30,70,2,20] and [14,6] live inside a
2026-06-05 custom variant panel; **[14,6] is NOT a Data Series setting**.

**2026 flagship (Class A):** author's custom strategy embedding licensed **ninZa
VWAP Flux** — full labeled stack read (Volume Base=BidAskPrice_RealVolume, 60/5/20
EMA, 95/75/50/25/5, Signal Qty/Trend 3, Close Threshold 10%, Split 5 Bars; colon-less
near-ninZa names + vendor enum string) — first visible 2/13/2026 (≤5 wks after
release), FROZEN 5/23→8/14/2026. Variants tested ~1 week each (4/29: +[16/6/9]+
windows 13:00-13:30 & 15:00-15:30; 6/5: 30/70/2/20+[14,6]+[3,0,12,0]).

**−$2,600 (T5 RESOLVED):** exactly −2,600 in 18 reports, first = week 2026-02-01..06,
across BOTH 2026 panel families, NEVER in 2025 → 2026 wrapper/account fixed stop
(130 pt, or 2×65 pt w/ Entries-per-direction=2 from mid-Jan); −$1,300 precursor caps
(65-pt St Initial) already in 2025-10 reports. LossLimit 2500/4000 = Feb-2025 DSTM
only; D/M 4500/2000 = separate daily money pair. Three risk mechanisms, three eras.

**Live-vs-backtest (T8):** 58/70 capture-lag=0 (dual OS clocks) → contemporaneous
weekly Friday ritual; but weekly SA numbers are **single-strategy $0-commission
slices** (author verbatim 0098: several strategies run concurrently, SA per-sleeve;
real ≈ posted ×0.9 wins /×1.1 losses; real comm ≈$1.04/side = "$2一个来回" ✓ TP
mystery solved). June 2026 gap weeks were posted from real TRADE PERFORMANCE
(+11,860.30 / +8,503.24). Non-overlapping posted totals: 2025 ≈ +$232.1k, 2026→8/14
≈ +$227.8k; author's stated 2025 "~$150k+" ≠ posted slices (C-3 open).

**Author (identity/process):** rednote "mac studio" ID 1384856832; bilingual US IT
contractor, amateur ("业余的"), ex-$200k stock/options loser, $60k→$100k own capital,
day-margin ~3k, flatten 16:59:30 ET daily, never over 17-18 break/weekends; codes
own NinjaScript (VS Code, class-per-iteration renames, A-label obfuscation for
public posting), recommends Kaufman TSM to learners; machines creator/hp/dev/mimi.

**Corrections to prior passes:** rn-agent year fits 2020-21 → 2025-26 (PnL
cross-match); 2026-08-24d's "packaging undecided (Cosmik vs Multi-Osc)" → both
falsified; "[90,180?,3,6,9] = second Solar panel" → same strategy's A-params
retuned; SpaceGPS/MaxDailyPL readings of [450?,200?] → D/M 4500/2000 money pair.
Purchase gate: still CLOSED; only VWAP Flux ($300) remains justified, and only if
R3 residuals persist (POST_SCREENSHOT_RECONSTRUCTION_PLAN).

## 2026-08-24d — H-B1/H-B2/H-B3 adjudication + stop-search verdict (owner correction executed)

- **Row-map adjudication (vendor_forensics/TRACK_B_ROWMAP.md, panels verified by direct
  image reading):** Multi-Osc's 16-row panel is IDENTICAL to Cosmik's oscillator section
  (Cosmik embeds Multi-Osc) → threshold-triple [65/30, 75/20, 46/36] is semantically
  STRONG (MFI/RSI/Stoch H/L) but contiguous in NEITHER product — packaging (Cosmik vs
  Multi-Osc) UNDECIDED, needs screenshot images. Decisive splits: **[90,180?,3,6,9] =
  EXACT Solar RK panel skeleton (bool position included) — a faster Solar retune is
  PRESENT in the stack**; [10,26,14,19?,18?,14?] = Cosmik-contiguous fit (both 14s on
  default-14 rows; offset-unit caveat). SJB [30,70,2,20] EXACT unchanged.
- **King Kong Trading RK confirmed as the vendor-official architecture** (rel. 2023-10-19:
  Solar Wave RK trend filter × Multi-Osc reversals → pullback signals + KingRenko$ +
  one-click execution); staff Solar-RK Renko templates 30/70→70/150 all /5/10/checked/10.
  The owner's hypothesized decision stack (trend → reversal quality → location → risk) is
  vendor-canonical, not our invention.
- **Stop search CLOSED (high-coverage negative):** no 130-pt/520-tick/$2,600 stop exists
  in any public vendor material (full forum API sweep + 399 sitemap pages + every
  published NQ dialog read). All vendor stops 10-150 ticks. **−$2,600 = the trader's
  PERSONAL hard risk cap — a cross-strategy personal fingerprint.**
- **VF language corrected per owner:** quantile implementation = HIGH-QUALITY BEHAVIORAL
  CLONE, not source-exact (official docs say "linear-based methodology").
- **ARCHITECTURE_CANDIDATES.md v1:** E (independent simultaneous sleeves) CONFIRMED at
  account level; C (Solar+osc battery+SJB King-Kong stack) LEADING for the multi-block
  sleeve; D (1-min VF + secondary Renko) attractive-unproven pending [14,6] location.
- Multi-Osc manual archived (17 products now in DB). Free unlocks unchanged: screenshot
  IMAGES > −2,600 week attribution > Renko recollection.

## 2026-08-24c — BUILD-FIRST pass: Track-B candidate-CRACKED; VF architecture advanced; no purchases

- **Track B breakthrough (EV-023/024/025, PROPERTY_MATCH_MATRIX.md):** the multi-block
  screenshot stack is most consistent with **Super JumpBoo$t + Cosmik Z-TP ×2 on a
  ninZaRenko/KingRenko$ 14/6 chart**: [30,70,2,20] = EXACT consecutive-row + published-
  value match to SJB (also the vendor's own recommended NQ values); [65,30,75,20,46,36]
  and [10,26,14,19?,18?,14?] land structurally on Cosmik's oscillator battery and
  offset/period rows (both 14s on factory-default-14 rows); [14,6] = Renko bar pair;
  [450?,200?] = SpaceGPS volume minimums OR a Max-Daily-P/L pair. Dates the stack
  ≥2025-04-10. **Cosmik's head params are literally "Offset: Multiplier Trend/Stop" —
  Solar naming — the trader's ecosystem evolution path is now visible end-to-end.**
  Excluded as sources: TZ, ApexFlow, Noble Cloud, NVI/PVI, OFP v2, Infinity/Captain
  grids, KingDOM$. 17-product fingerprint DB built; 12 more manuals archived.
- **VF4 (image-fidelity architecture):** vendor chart images select ANCHORED-CUMULATIVE
  layers (smooth drift + hourly rotation jumps); staircase reading rejected. Best cell
  D=3.398 with net/hold/avg-win ✓; residual isolated to Signal_Trade trigger + exit.
  QLEV (quantile-of-layers) level math favored. OF2: ninZa-verbatim delta (inside
  EXCLUDED) certified on both clean sessions.
- **Purchase gate (§17-18): NOT YET for anything.** VWAP Flux pre-purchase parity kit is
  ready (`vendor_forensics/PURCHASE_GATE.md`); Cosmik Z-TP + Super JumpBoo$t now rank
  ABOVE ThunderZilla in the eventual-purchase hierarchy for Track B. TZ formally
  MEDIUM/CONDITIONAL (`thunderzilla_family/TRACK_TZ_STATUS.md`); Infinity/Captain
  property grids positively absent from the screenshots
  (`vendor_forensics/INFINITY_COMPATIBILITY_HYPOTHESIS.md`).
- Highest-value free owner inputs unchanged + one new: the original screenshot IMAGE
  files themselves (control-type/layout verification would convert the Track-B
  STRONG-STRUCTURAL match into an identification).

## 2026-08-24b — Forensics + VF passes 1-3 + OF1 + changepoint map v1

- **VWAP Flux = the 2026 Track-V vendor product, IDENTIFIED at parameter-layout level**
  (EV-019: 13/13 labels in exact UI order from the official manual; release 2026-01-09
  aligns with his 2026 system change; trader tuned every parameter group vs manual
  values). Manuals archived in `vendor_docs/`.
- **The 2026 risk wrapper IDENTIFIED: intrabar ~130-pt ($2,600) protective stop** —
  VF2/VF3 reproduce EV-017's "repeatedly ≈ −$2,600 largest losses" as EXACT −2600 tails;
  the LossLimit-2500-at-bar-close alternative produces −2,785/−3,190 overshoots and is
  REJECTED for the 2026 family.
- **VF signal internals: BLOCKED BY MISSING MECHANISM INFO** after 21 bounded cells
  (VF1-3): entry-stream count matches window A (178/183) but no bounded exit reaches the
  WR-38/W-L-1.58/hold-40m geometry; the manual documents architecture, not math.
  **Unblock = owner purchase of VWAP Flux ($300)** → read its public Signal_* series on
  our data → identification becomes direct observation. Escalated per §50.
- **ThunderZilla weakened for Track B** (EV-020): documented parameter structure does
  NOT match the EV-007 multi-block groups; TZ is Renko-exclusive; hypothesis retained
  only for the unseen below-crop parameters. Not installed locally (EV-021).
- **OF1**: causal quote-rule classifier certified on both full window-A tick sessions
  (delta-return corr 0.66/0.67). DATA DEFECT: v3 exporter recorded quotes from a
  different contract (median 892-tick offset, all 8 batch-1 sessions suspect) — salvaged
  by rolling-median offset correction; flagged to scalping_lab.
- Vendor Major/Minor templates (EV-022) = Class-A confirmation of signal-type-selection
  design + PullbackEarly=true vendor default (Track-S relevance).
- **CHANGEPOINT_MAP.md v1**: frequency+hold clusters separate S-like (5-9 tpd, 70-115m) /
  V-like (15-19 tpd, 33-50m) / TP-aggregates (20-33 tpd); minimum consistent model by
  mid-2026 = V (confirmed) + ≥1 concurrent family; 2025-12-28 high-WR week = UNKNOWN,
  immediately pre-dates the Flux release.
- Owner asks that would sharpen identification: (1) which weeks showed the −$2,600
  largest losses; (2) the $300 VWAP Flux decision; (3) any fuller Track-B screenshots.

## 2026-08-24 — OWNER CORRECTION DIRECTIVE: package → INTERIM; retractions; TZ/VF opened

**RETRACTIONS (over-strong claims corrected; append-only, originals preserved below):**
1. ~~"2026 headline weeks are NOT Family S"~~ → **"The frozen OTR-S-CAND1 does not
   explain the 2026 screenshot fingerprints."** The trader ran several strategies
   simultaneously and modified them; Solar may have persisted with changed
   parameters/wrapper or in combination. ACCOUNT(t) = time-varying combination of
   families; no clean regime switch is established.
2. ~~"the trader migrated from Solar to Volume in 2026"~~ → retracted as a narrative;
   S13's fact stands only as: the FROZEN candidate loses −$78k in 2026.
3. ~~"T2 is NOT part of the system"~~ → **"simple/unconditional T2 entry is strongly
   disfavored"** — conditional T2 (wave/time/state-gated) is untested and cannot be
   excluded without source.

**STOP-RULE AMENDMENT (supersedes the §49 reading used on 08-23):** this is system
identification of a known external target. The three-failed-pass closure applies ONLY
when all available DIRECT screenshot/vendor/property evidence is consumed, no
identifiable parameter/property clue remains, and remaining alternatives are
observationally equivalent. New external evidence AUTOMATICALLY reopens a family.

**NEW EXTERNAL EVIDENCE (EV-014..EV-017):** VWAP Flux (ninZa) public docs match the
2026 Track-V parameter block closely (AnchorPeriodMinutes, Amount=N recent VWAP layers,
5-level Highest/Upper/Median/Lower/Lowest map; Feb-2026 changelog adds Signal_Cum_Delta,
upgrades Signal_Trend). ThunderZilla (RenkoKings) changelog 2025-08-11 adds "Signal:
Quantity Per Trend" — near-verbatim match to the screenshot label; same vendor ecosystem
as Solar. ninZa delta indicators expose Volume Base = BidAskPrice_RealVolume verbatim →
the 2026 systems likely REMAIN in the ninZa/RenkoKings ecosystem. Repeated ~−$2,600
largest losses across 2026 screenshots = new identification fingerprint.

**FRONTIER RESHAPED:** Track V reopened as **TRACK_VF (VWAP Flux architecture)** — the
08-23 V-proxy (prev-hour percentile ladder) is DEMOTED to a preserved
behavioral-mimic artifact, no longer the primary interpretation. **TRACK_TZ
(ThunderZilla)** opened as high-EVI identification hypothesis for the late-2025/2026
multi-block screenshots (not concluded as used). Order-flow classification from the 2
stored full BBO sessions authorized NOW (no CrossTrade). Track S: CAND1 remains
incumbent (moderate-confidence wrapper candidate); residual program per directive §6.

## 2026-08-23c — Tracks SD / B / V / P adjudicated; Phase-13 old-history stress done

- **Track SD (LossLimit)**: PARTIALLY IDENTIFIED. Per-trade semantics INERT at 2500/4000
  (binds 1-3 trades in 25 months → a trader doesn't tune an inert knob); session-level
  (B stop-new-entries / C flatten+disable) both consistent with late-2025 weeklies;
  C@2500 mildly disfavored (damages W20251228). `solar_dstm_family/LOSSLIMIT_SEMANTICS.md`.
- **Track B**: UNKNOWN MULTI-BLOCK confirmed — zero repo/source hits for any raw token
  group; no mechanism guess admitted (§22). `multiblock_family/TRACK_B_STATUS.md`.
- **Track V**: V-EXACT BLOCKED BY MISSING DATA (bid/ask real volume: only 2 full tick
  sessions inside window A; re-export = CrossTrade, excluded). V-PROXY: 3 bounded passes;
  pass 3 met the frozen success rule (D 2.431 < 5.203) with `PREV|T_LVL|X_MED|C2`:
  **breakout of the PREVIOUS hour's static volume-percentile ladder in EMA20 trend
  direction, not-extended-10% entry gate, median-line exit** → count 189/183, net −5,445
  vs −4,055, hold 36/40m all ✓; WR −8pp and avg-loss −37% out of band; March/April
  cross-window signs unresolved (family membership unknown). Classification:
  BEHAVIORALLY MATCHED — PARTIAL. Running-intra-hour ladder and hourly-EMA20 trend
  FALSIFIED. `volume_vwap_family/TRACK_V_REPORT.md`.
- **Track P**: UNDERDETERMINED. June TP aggregates (32.8 trades/day @ 20.5m, WR 50%)
  need a short-hold high-WR component beyond V+S → corroborates multiple strategies incl.
  unidentified Family B; H1 vs H2 not discriminable; TP commission $1.04/RT is a new
  unresolved evidence item. `account_combination/TRACK_P_NOTES.md`.
- **Phase 13 (S13)**: OTR-S-CAND1 over 2006-2026 = REGIME-LOCAL(recent): sweet spot
  2023-2025 (+$93.5k/+$143.2k/+$26.3k), 2026 Jan-May **−$78.1k** — the reconstructed
  Solar family dies exactly when the trader migrated to the Volume family. Fixed-tick
  params are price-level-dependent; pre-2018 counts are structurally tiny.
- Remaining phases: 10-11 (NinjaScript ports + parity for S-CAND1/V-proxy), final
  package (Phase 14). Window B (2026-08) stays governance-blocked.

## 2026-08-23b — Track S CLOSED: PARTIALLY RECONSTRUCTED (moderate-confidence wrapper)

- **S0 PASS**: pure-Python loop reproduces the canonical Type-1 NT8 run trade-for-trade
  (2,914/2,915 exact; 1 documented boundary-bar diff). Load-bearing discovery: V0 exits on
  an INCLUSIVE touch of the end-of-bar TrailingStop — a touch exits WITHOUT flipping.
- **Candidate OTR-S-CAND1** = E13_R1|W_0400_1600|FF: T1+T3 entries, stop-and-reverse on
  flips, entries 04:00–16:00 ET force-flat outside, touch-exit + session-close. Fit vs
  EARLY_LONG: trades +7.2%, WR −0.5pp, PF −0.039, DD −0.7%, net −13.1%, hold −20.3% (the
  one out-of-band residual). D-score path: 3.52 (V0) → 1.67 (S1) → 1.34 (S3) → 1.15 (S3B);
  S4/S5B/S6 all failed to improve → closed at the frozen §49 three-pass stop rule.
- **Structural findings (high confidence)**: the original wrapper REVERSES at flips; a
  SelTime window blocks roughly 16:00→02:00-04:00 ET (he traded overnight-morning + RTH,
  ~759 in-market min/day — RTH-only is arithmetically impossible); pullback (T2) entries
  are NOT part of the system (every T2 cell crushes WR); WR/PF are engine properties, not
  wrapper properties.
- **S8 cross-window (frozen candidate)**: late-2025 windows consistent (counts/holds in
  range, 3/4 sign agreement) — trader plausibly still ran an S-variant; 2026 windows
  STRONGLY inconsistent (2× counts, half holds) — **2026 headline weeks are NOT Family S**.
- **Layer-2 economics**: $253.7k screenshot-parity → $186.7k at $4.36/RT + 1 tick/side
  (25 months). Behavior survives honest costs in-window.
- S5 pass was VACUOUS (tautological T3 gates) — logged as my spec-design error.
- Ledger: HYPOTHESIS_LEDGER rows OTR-S1-001..OTR-S8-001 (~100 cells, no cherry-picks).
  Full report: `solar_family/TRACK_S_REPORT.md`.

## 2026-08-23 — Campaign opened (OWNER MASTER DIRECTIVE v1.0)

- OTR is the SOLE active research mission; all prior products/campaigns frozen reference.
- Phase 1 scaffold complete: evidence ledgers transcribed from directive (AUTHOR_STATEMENTS,
  EVIDENCE_LEDGER EV-001..013, TARGET_WINDOWS 22 windows, AUTHOR_REPORTED_NQ_RESULT_TIMELINE
  28 weeks, FAMILY_MAP 5 families, IDENTIFICATION_OBJECTIVE, COST_MODEL, UNKNOWN_FIELDS).
- Phase 0 repo/evidence bootstrap running (Solar legacy read + wrapper/TrackV/TrackB
  string search + data audit). DATA_AUDIT.md pending its results.
- Governance notes: LOCKED_FORWARD respected — Track V window B (2026-08-02→08-14) readout
  BLOCKED (≥2026-08-01 virgin); 2026-06/07 data previously consumed → usable for
  reconstruction (not claimable as pristine OOS). CrossTrade excluded from campaign.
- Known reference gap (ORIGINAL vs our Type-1): WR/PF ≈ match, trades 4,351 vs 2,915,
  hold 94m vs 108m, net $292k vs $146k → wrapper unidentified (RECONSTRUCTION_SCORECARD.md).
