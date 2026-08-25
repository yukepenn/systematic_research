# CURRENT_KNOWN — OTR campaign #6

**Authority**: derived mechanically from `CLAIM_REGISTRY.csv` (141 rows, 2026-08-24).
**Scope**: this file contains **only** claims whose registry status is `FACT` or `REPRODUCED`
(46 + 24 = 70 claims). Everything INFERENCE or UNKNOWN is in `CURRENT_HYPOTHESES.md`;
everything FALSIFIED is in `FALSIFIED_HYPOTHESES.md`.

**Reading rule for this file.** No sentence below explains, motivates, or attributes anything.
A bullet says what was read off an artifact, or what two named endpoints computed. If you find
yourself learning *why* something is the case from this file, that is a defect — report it.

**Two terms used throughout**
- `IMPLEMENTATION_PARITY` — agreement between artifacts **we** built (our Python ↔ our
  NinjaScript ↔ the NT8 engine). Established for the Solar/CAND2 half only (E-009).
- `ORIGINAL_PARITY` — agreement between us and the original trader. **Never tested anywhere in
  this campaign** (E-010, V-103). No bullet in this file asserts it.

---

## Section 1 — Directly observed (status FACT)

Directly readable in evidence: a label or number visible in a screenshot, a vendor-manual
sentence, an author statement, or a line of our own source code. No modelling.

### 1.1 The trader's Strategy Analyzer panels — early era (2023-01 … 2025-02)

- **E-001** — The NT8 Strategy Analyzer settings pane shows strategy name `SolarWindRKSelTime`
  with parameters labelled A1=90 A2=179 A3=5 A4=10 A5=10 and Quantity=1; instrument NQ MAR25;
  1-Minute Last; Tick Replay unchecked; commission template ON ($4.18/RT); MaxBarsLookBack 256;
  BarsRequiredToTrade 20; Standard (Fastest) fill; TradingHours = Use instrument settings;
  BreakAtEOD on. → `original_screenshot/OTRIMG-0007`; corroborating OTRIMG-0002 / 0012 / 0016;
  `screenshot_forensics/per_image/OTRIMG-0007.md`; EVIDENCE_LEDGER EV-030.
- **E-006** — The trader's own two-year Summary($) grid reads: net $292,172.82 (long $214,911.12 /
  short $77,261.70); 4,351 trades (2,166 L / 2,185 S); 40.29% profitable; PF 1.18; max drawdown
  ($32,677.42); avg trade $67.15; avg win $1,111.73; avg loss ($637.68); max consecutive 8W / 15L;
  largest win $7,705.82; largest loss ($4,449.18); avg time in market 94.15 min (L 105.85 /
  S 82.56); 8.26 trades/day; commission $18,187.18; slippage 0. Capture clock 2/2/2025 11:57 PM,
  remote machine titled `creator`. → `OTRIMG-0002`;
  `screenshot_forensics/per_image/OTRIMG-0002.md` §H; EV-029 / EV-030.
- **E-013** — The trader's per-day analysis table gives, for each of 11 January-2023 sessions,
  winner count, gross win, loser count, gross loss, largest win and largest loss at cent
  precision — e.g. 2023-01-03 = (4, $5,863.28, 8, −$6,163.44, LW $3,050.82, LL −$1,179.18);
  2023-01-16 = (2, $641.64, 1, −$34.18, LW $555.82, LL −$34.18). No per-trade rows are visible in
  that frame. → `OTRIMG-0003`; `screenshot_forensics/per_image/OTRIMG-0003.md`; EV-029.
- **E-028** — The per-day table gives 2025-02-27 = 90 trades, average loss −$331, inside a
  Feb–Mar series whose neighbouring days run 3–70 trades. The A-parameter panel on the 2025-02-28
  frame still reads 90/179/5/10/10. → `OTRIMG-0026` (rows), `OTRIMG-0029` (panel); EV-029.

### 1.2 The trader's Strategy Analyzer panels — 2025 St-group and A-group changes

- **E-024** — A5=10 is still visible on 2025-10-24; the top parameter group reads 3/6/9 on
  2025-11-07. A3–A5 therefore changed from 5/10/10 to 3/6/9 **between those two capture dates**
  (bracketed, not observed at the moment of change). A2 reads `180?` on the 2025-12-06 frame
  (trailing `?` = crop-edge digit, not certain). → `OTRIMG-0079`, `OTRIMG-0083`, `OTRIMG-0093`;
  `screenshot_forensics/PARAMETER_VERSION_TIMELINE.md`; EV-032.
- **E-032** — St-group panel values over time: [In 65 / Tr 30 / I 65 / M 20] on 2025-10-17 (label
  initials `In..` / `Tr..` / `I..` / `M..` legible) and unchanged on 2025-10-24; two further rows
  46 and 36 appear 2025-11-07; row 3 reads 75 on 2025-11-14 giving [65/30/75/20/46/36]; rows 5/6
  read 46/30 on 2026-01-17. A tail of the group is already present 2025-08-22 with values
  [65/30/65]. → `OTRIMG-0062, 0077, 0079, 0083, 0087, 0109, 0111`; EV-032.
- **E-033** — Largest-losing-trade cells in the trader's weekly reports: exact −1,300.00 appears
  2025-07 → 2026-01 **including after** the 2025-11-14 panel change (weeks of 11/9, 12/14, 1/18);
  exact −1,500.00 appears in the 1/4/2026 week short column; other era-B rows beyond −1,300 are
  mostly short-side (−1,410 / −1,490 / −1,500 / −1,385); no −2,600 row occurs anywhere in 2025
  (first is the 2026-02-01..06 week). → weekly frames incl. `OTRIMG-0081, 0113, 0115`;
  `screenshot_forensics/RISK_EVENT_LEDGER.csv`;
  `screenshot_forensics/derived/targets_weekly_2025S.csv`; EV-032 / EV-034.

### 1.3 Machine labels and code fragments visible in the corpus

- **E-021** — Machine identifiers are visible in the frames themselves: the Jump Desktop window
  title reads `creator` (Feb-2025); a new remote machine `hp` first appears Jul-2025; `dev` and a
  third machine `mimi` also appear (`mimi` first Feb-2026). Each weekly target row carries a
  per-frame machine annotation. → `OTRIMG-0002` (creator), `OTRIMG-0043` (hp), `OTRIMG-0115`
  (mimi); `screenshot_forensics/IMAGE_MASTER.csv`; EV-029.
- **E-019** — A code-editor window visible behind the Strategy Analyzer shows one partial
  NinjaScript line in coloured monospace: `if (Bars.IsFirstBarOfSession)`. The closing characters
  are cut off; the transcript grades legibility MEDIUM; the body of the if-block is **not
  visible**. → `OTRIMG-0053`; `screenshot_forensics/per_image/OTRIMG-0053.md` line 104; EV-029.

### 1.4 Facts about **our own** artifacts (not about the trader)

- **E-011** — In `src/ninjascript/OriginalTraderSolarCAND2_v2.cs`: input `TrendMultiplier` (A1) is
  assigned its default 90 at line 109, declared at lines 387–390, and read at **no other line**.
  `UpdateSolarWave()` (149–198) reads only `StopMultiplier` (151), `SlowdownScan` (191) and
  `WeakWeakSplit` (180/186/193). The `weak` state is set at 193 and cleared at 178/186 but never
  influences `signalTradeVal`, which receives a non-zero value only on a flip at line 179 and is
  the sole entry trigger read at line 295. No input named A5 or `PullbackSplit` exists in the file
  (grep returns zero hits).
- **E-016** — The constants X=1600, X2=2500, K=3, C=700, NoonMinute=720, EveningBlockMinutes=360,
  SessionTradeCap=20, CooldownBars=3 are **our** chosen point values, hard-coded as defaults at
  `OriginalTraderSolarCAND2_v2.cs` lines 115–122 and consumed by `GateAllows()` at lines 213–228.
  The file itself labels GateX / GateX2 / GateC `[INTERVAL-IDENTIFIED]` and GateK `[RIVAL: 4
  total]` at lines 30–32 and 413–429.
- **V-103** — No IMPLEMENTATION_PARITY has been established for any VWAP-Flux-family object: the
  VF clean-room exists only as Python (`vf_core.py` plus the R3/R7/R7b/R8 and VF1–VF4 drivers),
  with no NinjaScript port and no NT8-engine cross-check. → inventory of
  `vwap_flux_family/src/`; contrast `runs/OTR_R6_NT8_PARITY/` which covers CAND2 / Solar only.
- **V-104** — Separating the OTR-VF-CAND1 members requires Signal_Trade timestamps for any single
  day, or a per-day 2026 Analyzer table of the OTRIMG-0003 kind; neither exists in the fixed
  corpus. → `vwap_flux_family/SIGNAL_TRADE_HYPOTHESES.md`;
  `screenshot_forensics/CHART_CONTENT_FINDINGS.md`.
- **V-020** — A read-only search of the **researcher's** NinjaTrader 8 install found no VWAP Flux
  DLL, wrapper `.cs`, template, workspace reference, compile record, reflection-cache entry, or
  assembly-load log line. No binary was opened or decompiled. → `vendor_forensics/
  LOCAL_ARTIFACT_SEARCH_20260824.md`. *(What this does **not** license is recorded as V-021,
  FALSIFIED.)*
- **V-099** — The purchase gate for ninZa VWAP Flux ($300) is recorded CLOSED as of 2026-08-24,
  with three named reopen triggers: evidence the trader used Tick Replay or UpDownTick mode; any
  Signal_Trade-timestamp-bearing screenshot; or an explicit owner request for the vendor-distance
  bound. → `vendor_forensics/PURCHASE_GATE.md`.
- **V-101** — A pre-purchase parity kit is staged: exact settings to enter, data windows
  2026-05-10..22 / 2026-03-08..13 / 2026-03-22..27, a chart-attached exporter pattern writing
  per-bar level plots and Signal_* series, Tick Replay ON and OFF arms, and a bar-by-bar
  comparison script. → `vendor_forensics/PURCHASE_GATE.md` §Pre-purchase parity kit.

### 1.5 The 2026 parameter panel (VWAP-Flux era)

- **V-001** — OTRIMG-0146 (2026-05-23) displays 13 consecutive strategy-parameter labels running
  `Volume Base` → `Signal Split (Bars)`, immediately followed by the `Data Series` group header.
  Only frame in the corpus with FULL labels for the block. → `OTRIMG-0146`;
  `screenshot_forensics/VF_PANEL_COMPLETENESS_NOTE.md` §0 Q1a; `PARAMETER_PANEL_LEDGER.csv`.
- **V-002** — In every flagship frame from 2026-02-13 to 2026-08-14 the 13-field block reads
  `BidAskPrice_RealVolume / 60 / 5 / 20 / EMA / 95 / 75 / 50 / 25 / 5 / 3 / 10 / 5`, unchanged
  (≥9 independent frames). → `OTRIMG-0117, 0121, 0123, 0129, 0132, 0136, 0140, 0146, 0164`;
  `screenshot_forensics/2026_VARIANT_LEDGER.csv`.
- **V-010** — The 13-field block is witnessed CLOSED at both boundaries (nothing between
  `Signal Split (Bars)` and `Data Series`; contiguous run from `Volume Base`) in ≥9 independent
  frames; the lower boundary is label-confirmed twice (0146, and 0134 via row-initial `S.` = 5).
- **V-006** — No frame in the 164-image corpus shows any parameter label beginning `Zone`,
  `Static`, `Level`, `POC` or `Profile`. This is the absence of a **label**. →
  `VF_PANEL_COMPLETENESS_NOTE.md` §0 Q1a; `IMAGE_MASTER.csv`.
- **V-007** — Every 2026 settings pane in the corpus carries a vertical scrollbar whose thumb
  occupies 7–17% of the track, so rows outside the captured region exist in every 2026 capture.
  → grayscale run-length scans of the scrollbar lane (x≈1395–1436) on the original JPGs.
- **V-073** — The 13 VF-field values never change from 2026-02-13 to 2026-08-14 while the rows
  immediately **above** `Volume Base` change value, count and type: a numeric 15 adjacent in Feb
  (0117); `[30?,16,0,10,15]` on Apr 2 (0132); `[16,0,9,15]` on Apr 17 (0136); a checkbox directly
  above `Volume Base` by Aug 14 (0164). → `2026_VARIANT_LEDGER.csv`.
- **V-075** — OTRIMG-0138 (week 4/19-24) and OTRIMG-0150 (week 5/31-6/5) show panels with no VF
  field visible and different numeric vocabularies; the immediately adjacent weeks show the
  flagship stack again. → `OTRIMG-0138, 0140, 0148, 0150, 0156`; `2026_VARIANT_LEDGER.csv`.
- **V-078** — The first VF panel frame is dated 2026-02-13 (OTRIMG-0117); the vendor's
  Signal_Cum_Delta build is dated 2026-02-09. → `PARAMETER_VERSION_TIMELINE.md`;
  `vwap_flux_family/VWAP_FLUX_VERSION_TIMELINE.md` §1.
- **V-028** — The 164-image corpus contains **zero** author platform-chart imagery. The only
  price chart anywhere is a commenter's TradingView MNQ shot (OTRIMG-0130, no time axis). →
  `screenshot_forensics/CHART_CONTENT_FINDINGS.md`; `CHART_CONTENT_LEDGER.csv`.

### 1.6 Vendor documents (ninZa VWAP Flux)

- **V-003** — The ninZa VWAP Flux Trader Manual (vendor CMS `createdAt` 2026-02-02, SHA-256
  `d34b50da…`) lists the same 13 parameter labels in the same settings-UI order; 13/13 label+order
  match recorded as EV-019. → `vwap_flux_family/ninZaVWAPFlux-TraderManual.pdf`;
  `VWAP_FLUX_VERSION_TIMELINE.md` §3.
- **V-005** — The trader's values differ from every published ninZa preset: manual presets use
  Trend Period 14, Levels 100/70/50/30/0, Quantity Per Trend 5, Close Threshold 70, Split 15
  (Split 30 only on the ninZaRenko-12/4 preset). → EV-019;
  `VWAP_FLUX_VERSION_TIMELINE.md` §5 correction flag.
- **V-011** — The manual (§2.1 p5) states that in `BidAskPrice_RealVolume` mode with Tick Replay
  DISABLED the indicator performs **no calculations on historical data**. This sentence is the
  entire proven content of EV-039. → manual §2.1.
- **V-031** — The manual describes the five Level parameters as "thresholds within the VWAP
  bands". → EV-038; `vwap_flux_family/VF_CLEANROOM_SPEC.md` table.
- **V-039** — The 2026-02-02 manual documents `Signal_Trend` as 1 = bullish / −1 = bearish; the
  vendor product page read 2026-08-24 documents `Signal_Trend` as 2 / 1 / −1 / −2; the vendor
  changelog entry dated 2026-02-24 reads verbatim "Signal_Trend was upgraded." The changelog does
  not say what "upgraded" means. → `VWAP_FLUX_VERSION_TIMELINE.md` §1/§3; EV-038.
- **V-054** — The manual (§2.12) documents `Signal Close Threshold (%)` as a candle-close-location
  (CLV-family) filter; the trader's value is 10; every published ninZa preset uses 70. → EV-038;
  `OTRIMG-0146`.
- **V-059** — The manual defines `Signal Quantity Per Trend` (§2.11) as the maximum number of
  SAME-DIRECTION **signals** within one trend / S-R-zone episode, and `Signal Split (Bars)`
  (§2.13) as the minimum bar distance between consecutive SAME-DIRECTION **signals**. Both are
  defined over signals, i.e. inside indicator signal generation. → EV-038; `VF_CLEANROOM_SPEC.md`.
- **V-070** — The manual (§2.14) documents a `Zone Period` parameter and a static S/R zone module
  as part of the VWAP Flux product; the 2026-01-14 marketing microsite capture already advertises
  static S/R zones with POC, intra-zone VWAP and absorption/push classification. → EV-038;
  `VWAP_FLUX_VERSION_TIMELINE.md` §3 (capture S4).
- **V-066** — No public vendor material documents a 130-point, 520-tick or $2,600 stop; every
  documented vendor stop is 10–150 ticks. High-coverage negative: full forum API sweep, 399
  sitemap pages, every published NQ dialog read. → `vendor_forensics/PUBLIC_SOURCE_LEDGER.md`.
- **V-023** — ninZa's public product pages describe the VWAP layers as covering "the most recent
  30 minutes", "the previous 30 minutes" and "an earlier 30-minute period", and state that the
  tool "divides the market into smaller time segments and recalculates VWAP for each segment".
  → owner MASTER DIRECTIVE v4.0 (2026-08-24) quoting ninza.co.
  **⚠ PROVENANCE GAP — read this bullet with its caveat.** These verbatim strings are **not
  archived anywhere in this repo**: grep over `research/original_trader_reconstruction/**` returns
  zero hits, and the archived manual PDF, the changelog extraction and the 2026-01-14 microsite
  capture do not contain them. The row is sourced to the directive's quotation, not to a repo
  artifact. It is load-bearing (it is the whole evidentiary basis for reopening V-024), so it
  needs a re-fetch-and-archive pass to become independently checkable.

### 1.7 The 2026 risk signature and June-2026 execution reports

- **V-062** — Exactly −$2,600 appears as a largest-loss value in 18 weekly reports, first in the
  week 2026-02-01..06, and in **no** 2025 report. → EV-017; `RISK_EVENT_LEDGER.csv`;
  `2026_VARIANT_LEDGER.csv`.
- **V-064** — The −$2,600 signature first appears in OTRIMG-0115 (week 2026-02-01..06), one week
  **before** the first VF-layout frame (OTRIMG-0117, week 2026-02-08..13), on a pre-VF S-family
  panel. → `OTRIMG-0113`, `OTRIMG-0115`; `2026_VARIANT_LEDGER.csv` (VAR2026-PREVF).
- **V-068** — In real June-2026 execution the largest loss was −3,046.18 (week 6/7-12) and
  −1,426.18 (week 6/14-18). → `OTRIMG-0152`, `OTRIMG-0154`;
  `account_combination/JUNE_TP_RECONSTRUCTION.md`.
- **V-082** — OTRIMG-0152 and OTRIMG-0154 are NT8 **Trade Performance** reports (executed trades)
  covering 2026-06-07..12 (136 trades, WR 50.0%, avg hold 20.5 min, largest loss −3,046.18, net
  +11,860.30, commission $141.20) and 2026-06-14..18 (78 trades, WR 42.3%, avg hold 34.1 min,
  largest loss −1,426.18, net +8,503.24, commission $96.76). → `JUNE_TP_RECONSTRUCTION.md`;
  `screenshot_forensics/BACKTEST_VS_LIVE_AUDIT.md`.
- **V-094** — TP commission works out to $141.20 / 136 = $1.038 per trade, while the author states
  approximately $2 per round turn. → `account_combination/TRACK_P_NOTES.md`; EV-035.
- **V-089** — From approximately 2025-02-28 onward the weekly Strategy Analyzer reports show
  "Include commission" unchecked, so the posted weekly numbers are $0-commission single-strategy
  slices. → `BACKTEST_VS_LIVE_AUDIT.md`; EV-035; `2026_VARIANT_LEDGER.csv`.
- **V-098** — The weekly SA reports were generated contemporaneously (58/70 with capture-lag
  0 days on dual OS clocks; 66/70 within 3 days) but with **that week's** current parameters,
  which the panels show were repeatedly re-tuned. → `BACKTEST_VS_LIVE_AUDIT.md` findings 1–2;
  `PARAMETER_VERSION_TIMELINE.md`.

### 1.8 Author statements (verbatim, pixel-verified)

- **V-081** — The author states verbatim (2025-12-20) that he runs several strategies
  simultaneously and therefore uses Strategy Analyzer to analyze single-strategy performance. →
  `OTRIMG-0098`; EV-035; `screenshot_forensics/AUTHOR_COMMENT_LEDGER.csv`; `AUTHOR_STATEMENTS.md`.
- **V-083** — The author states verbatim (2025-12-27): $60k own capital, one contract per
  strategy, intraday flat before the close, ~$3k day margin, historical max drawdown ~$30k, and a
  separate day job. → EV-037; `AUTHOR_STATEMENTS.md`.
- **V-096** — The author states verbatim (2026-07-11) that the system is fully automated
  ("全自动") and that he is an amateur ("业余的"). Pixel-verified after ×6.4 stretch recovery of a
  black carousel frame. → EV-041; `OTRIMG-0160`; `CHART_CONTENT_FINDINGS.md`.
- **V-012** — The trader's 2026 frames consistently show Tick Replay OFF together with
  `Volume Base = BidAskPrice_RealVolume`, and the same frames' Strategy Analyzer reports contain
  full historical trade populations. → EV-039; `PARAMETER_PANEL_LEDGER.csv`;
  `2026_VARIANT_LEDGER.csv`.

---

## Section 2 — Reproduced by our code, with endpoints named (status REPRODUCED)

Every bullet in this section is a measurement produced by running our own code. The endpoint
pair is stated in each bullet. **A distance to a pixel-read original aggregate is not parity** —
where a bullet compares our output to the trader's posted numbers, it is a measured difference,
and the numbers differ.

> **Standing scope note on seven of these bullets.** V-041, V-045, V-047, V-049, V-050, V-052 and
> V-056 were all produced by code carrying the QtyPerTrend/Split implementation defect recorded as
> **V-060** (FALSIFIED, by code inspection of `run_r7_signal_id.py` lines 132–154). The
> measurements below are reported as they were computed; they must be re-derived before any of
> them is treated as a property of the trader's system.

### 2.1 Vendor-indicator recovery (campaign #1 inheritance)

- **E-004** — Our Python implementation reproduces the licensed Solar Wave RK indicator's own
  published series over 737,707 NQ 1-min bars: TrailingStop 100.000000%, TrendVector 100.000000%,
  Signal_Trade Type-1 100.000000% (all 5,405 trend starts), Signal_Trend 99.999864% (1
  uninitialised first bar), Signal_Wave 99.970585% (200 plot-slot collisions).
  **Endpoints — IMPLEMENTATION_PARITY**: our `src/analytics/solarwave.py` ↔ the licensed vendor
  indicator's own exported `Series<double>` (`RenkoKings_SolarWaveRK_NT8.dll` via
  `SolarWaveRKLedgerV1.cs` → `research/01_diagnostics/sw01_bar_ledger.csv`). This says nothing
  about the trader's build. → `research/03_reverse_engineering/SOLARWAVE_MATH.md` §0–1.

### 2.2 CAND2 — implementation agreement, and distance to the trader's aggregates

- **E-009** — Layer A (Jan-2023) cent-exact 91/91 trades and $6,815.00 == $6,815.00
  trade-for-trade; Layer B (2023-01..2025-02 master, commission 0) 4,592/4,592 trades,
  $279,655.00 == $279,655.00, DD −$30,305.00, consec 7/15, zero trade differences across ~735k
  bars (the single unserialized trade is the known NT8 data-boundary quirk); Layer C one weekly
  window EXACT, the others within a 1-trade data-source delta.
  **Endpoints — IMPLEMENTATION_PARITY**: our Python `otr_engine.py` ↔ our
  `src/ninjascript/OriginalTraderSolarCAND2_v2.cs` ↔ the NT8 Strategy Analyzer engine (invoked via
  CrossTrade `RunStrategyBacktest`). **The original trader is not an endpoint of this test.** →
  `runs/OTR_R6_NT8_PARITY/REPORT.md`.
- **E-008** — Our CAND2 best configuration produces, on the master window at $4.18/RT: n 4,598 |
  net $264,955 | WR 40.08 | PF 1.152 | DD −$31,934 | hold 95.56 min (L 109.6 / S 81.9) | consec
  7W/15L, against the observed 4,351 | $292,172.82 | 40.29 | 1.18 | −$32,677 | 94.15
  (105.85/82.56) | 8W/15L. That is **+5.7% trades and −9.3% net**, residual +247 trades / −$27.2k
  concentrated on the short side and in chop months. Largest win and largest loss reproduce to the
  cent. **Endpoints**: our Python `otr_engine.py` output ↔ the pixel-read OTRIMG-0002 aggregate
  cells. **This is a distance, not parity — the numbers differ.** →
  `runs/OTR_R1_SERIES/out/` (v3 gap-hunter {X1600 K3 C700 X2 2500 cap20 cd3});
  `solar_family/TRACK_S_REPORT.md` lines 132–136.
- **E-015** — Under the V3 configuration all 42 latent assignments across the 11 January-2023
  sessions remain simultaneously consistent and the number of per-day removals falls from 6 to 5.
  **Endpoints**: our `run_r1e_subsetdiff.py` output ↔ the OTRIMG-0003 per-day aggregate cells.
  Aggregate-level agreement only; not trade-level; not ORIGINAL_PARITY. *(What the 42 assignments
  are — CONDITIONAL_LATENT_LABELS, not observed labels — is E-014, INFERENCE.)* →
  `TRACK_S_REPORT.md` line 136; `runs/OTR_R1_SERIES/out/`.
- **E-022** — Frozen CAND2 without D/M halts, scored against 28 weekly target frames: dev-machine
  mean Δn +6.6%, mean |Δn| 11.1%, mean |Δhold| 6.8 min (n=9); hp-machine mean Δn +39.5%, mean |Δn|
  41.8%, mean |Δhold| 18.2 min (n=19). Adding literal D/M halts moves dev to −27.6% and hp to
  +13.5%. Within era B: hp |Δn| ≈31% vs dev ≈11%. No parameter was tuned in the run.
  **Endpoints**: our Python `run_r5_weekly.py` output ↔ pixel-transcribed weekly Strategy Analyzer
  target rows (`targets_weekly_2025S.csv`). Aggregate-level only. →
  `runs/OTR_R5_CAND2_WEEKLY_VALIDATION/`.
- **V-091** — Frozen CAND2 matches dev-machine-tagged late-2025 weeks at about ±7% mean
  trade-count error and overshoots hp-machine-tagged weeks by about +39.5%.
  **Endpoints**: our frozen Python CAND2 ↔ the trader's posted weekly SA aggregates. A distance to
  the original, not parity. → `runs/OTR_R5_CAND2_WEEKLY_VALIDATION/`.
- **E-025** — With our recovered Solar core, A3/A4/A5 have **no effect on the T1-flip trade
  stream**: the `old` (5/10/10) and `new179` (3/6/9) simulated streams are bit-identical over the
  R5 weekly windows. In event space the same intervention moves T3 strongly (count 3,466 → 4,803,
  Jaccard 0.70) and T2 modestly (6,286 → 6,475, Jaccard 0.91) while leaving T1 untouched except
  through A2 (Jaccard 1.0 for A3/A4/A5 alone; 0.905 for A2 179→180).
  **Endpoints**: our Python `run_r5_weekly.py` / `solar_wave_full()` under two parameter sets on
  identical bar data. A statement about **our** model only. →
  `runs/OTR_R5_CAND2_WEEKLY_VALIDATION/` verdict 2; `runs/OTR_R12_PARAM_INTERVENTION/out/
  event_family_deltas.csv` *(OPEN run, no REPORT.md yet)*.
- **E-034** — Over 11 era-B weeks, largest-loss-column hits within ±$50 were (long, short):
  L65S65 (8,5), L65S75 (8,6), L75S65 control (2,2) — the 75-point long control collapses the long
  column. Separately, a 65-point stop on 1 NQ contract produces exactly the −$1,300.00 cap
  signature, with 3–12 point overshoots consistent with 1-minute gap-through fills.
  **Endpoints**: our Python `run_r5_weekly.py` / `run_r2.py` output ↔ pixel-read largest-loss
  cells in the trader's weekly frames. Aggregate-cell agreement. → `runs/OTR_R2_STOPGROUP/out/`
  (G1); `runs/OTR_R5_CAND2_WEEKLY_VALIDATION/out/`.

### 2.3 VWAP-Flux clean-room: measurements on our own substrate

*(Both endpoints are ours in every bullet in this sub-section. No original-side data participates.)*

- **V-025** — Our clean-room constructor produces mean cloud width (Max−Min) of **47.0 pts under
  ANCHOR vs 106.0 pts under BLOCK** on NQ 1-min 2026-03-16..27 with P=60, A=5, levels
  95/75/50/25/5, close×volume. **Endpoints**: our Python `vf_core.vf_levels()` ↔ our NQ 1-min
  substrate (scalping_lab minute parquet). → `vwap_flux_family/VF_CORE_PARITY_REPORT.md`.
- **V-026** — In the same measurement: rails moving per in-period bar = 5.00 under ANCHOR vs 1.34
  under BLOCK; mean jump at the period boundary = 11.1 pts vs 21.2 pts. Same endpoints as V-025.
- **V-030** — The sorted rail population is not age-ordered (anchor-age concordance mean −0.17 on
  real data), so layer identity carries information the rails discard. **Endpoints**: our Python
  `vf_core` (`with_meta=True`) ↔ our NQ 1-min substrate. Metadata only — excluded from the
  reconstruction per directive §18/§42.
- **V-032** — On the adversarial population [100,101,102,103,140] the 75% level evaluates to
  103.0 (percentile-linear), 103 (nearest-rank) and 130.0 (min-max). **Endpoints**: our Python
  `vf_core` ↔ a synthetic population (no market data, no trader data). →
  `vwap_flux_family/src/vf_core.py::_tests()`.
- **V-033** — On real NQ data with A=5, min-max forces FairValue to sit exactly at the cloud
  midspan (Δ = 0.000 by construction) while the percentile FairValue deviates from midspan by
  mean 8.9 pts. **Endpoints**: our Python `vf_core` ↔ our NQ 1-min substrate, window
  2026-03-16..27. **Caveat recorded on the row**: computed under the ANCHOR construction; the
  reopening of V-024 weakens (does not void) the transfer of this discriminator to a BLOCK world.
- **V-044** — The trader's tick-level volume input is reconstructible to within a **1.7%
  trend-state disagreement bound** from 1-min bar data. **Endpoints**: our tick-derived trend
  states ↔ our bar-derived trend states, both on our own substrate (R3 addendum, two clean
  full-BBO sessions). → `VF_CORE_PARITY_REPORT.md`; `runs/OTR_R3_VF2026/`.

### 2.4 VWAP-Flux clean-room: distances to the trader's posted 2026 aggregates

*(Second endpoint is a pixel-read aggregate in every bullet. These are distances, never parity.
All carry the V-060 defect.)*

- **V-041** — Among four structurally distinct trend-state constructions, `T_C` (direction = close
  vs FairValue with EMA20(close) slope agreement, state held on disagreement) is the rank-stable
  leader in **13 of 17** leave-one-window-out rotations. 144-member × 17-window grid; no free
  numeric constants; PnL never a selection objective. **Endpoints**: our Python VF replica
  (`vf_core` + `run_r7`) ↔ the trader's posted weekly SA aggregates (`targets_weekly_2026V`). →
  `runs/OTR_R7_VF_SIGNAL_ID/REPORT.md`.
- **V-045** — A 208-member bounded structural grid (R7 144 + R7b 64, no free numeric constants)
  leaves a 4-member surviving cluster with mean §40 reconstruction distances **0.476 / 0.492 /
  0.501 / 0.514** across 17 weekly windows. The cluster is named OTR-VF-CAND1. **Endpoints**: our
  Python VF replica ↔ the trader's posted weekly SA aggregates 2026-01-25..05-29.
- **V-047** — On the held-out 2026-06-21..07-31 windows, all 12 frozen member × window §40
  distances fell in **0.327–0.668**, inside the preregistered band ≈0.35–0.65, and the strongly
  positive 6/21 week did not come out deeply negative for the leader. Preregistered prediction,
  zero knobs touched, readout after the prediction was committed. **Endpoints**: our frozen Python
  VF cluster ↔ the trader's posted June–July 2026 SA aggregates, on JUN26/SEP26 raw 1-min data
  exported by us. **This is a HELD_OUT_RECONSTRUCTION_WINDOW, not an out-of-sample test** (see
  V-048, FALSIFIED). → `runs/OTR_R8_JUNE2026/REPORT.md` Part A + `spec.yaml` prereg_note.
- **V-049** — The leader member `T_C|P_MED|C_DIR|H1a|X_OPP` produced n=194, net +7,985 (d=0.338)
  on the 2026-06-28..07-10 window whose target is n=162, net +8,630. **Endpoints**: our Python VF
  leader ↔ the trader's posted SA aggregate for that window.
- **V-050** — Member `T_D|P_IN|C_REC|H1c|X_FLIP` produced **−32,500** on the 2026-06-28..07-10
  window whose target is +8,630 — a swing of about −41k. Same endpoint form.
- **V-052** — In the 2026-03-22..27 failure week (target −42,235) every surviving member is
  loss-making, spanning −5,135 to −26,535 (23–63% of target magnitude), and the one profitable
  pretender was disqualified (`T_C|P_MED|C_REC|H1a|X_OPP`, mean 0.479 but +2,970 in the failure
  week). §32 failure-geometry discriminator, applied before ranking. Same endpoint form.
- **V-053** — The persistent residual is a win-rate gap (ours 26–35 vs his 39–45) plus missing
  edge in his two largest weeks; the same signature appears in-sample and on the held-out window.
  **Endpoints**: our Python cluster ↔ the trader's posted SA aggregates. *(Any account of why is
  V-046, INFERENCE.)*
- **V-056** — H1a members occupy the entire top-15 of the R7 pass-1 ranking by §40 distance; H1c
  members sit mid-pack (0.512 and worse) in pass 2. **Endpoints**: our Python members ↔ the
  trader's posted weekly SA aggregates. A measurement of **our composite wrapper's** fit — not a
  measurement of the vendor filter's definition (see V-057, FALSIFIED).
- **V-063** — An intrabar protective stop of **130 NQ points (= $2,600 at qty 1)** from the entry
  fill reproduces the exact −2,600 loss tails; the alternative reading (LossLimit 2500 evaluated
  at bar close with next-open fill) produces −2,785 / −3,190 overshoots. Qty-1 confirmed by the R3
  row discriminator (130 pt × 1, not 65 × 2). **Endpoints**: our Python wrapper on our NQ 1-min
  substrate ↔ the trader's posted largest-loss values. → `runs/OTR_VF2_STOP130`;
  `runs/OTR_VF3_MEDEXIT`; `runs/OTR_R3_VF2026`.
- **V-093** — On the 2026-06-07..12 week the VF leader produces n=93, WR 25.8, net −19,035 and
  CAND2-S produces n=88, WR 42.0, net +9,745, summing (under H1 account semantics) to n=181
  against the TP target n=136, WR 50.0, net +11,860. No weights fitted. **Endpoints**: our frozen
  Python VF leader and CAND2-S ↔ the trader's Trade Performance aggregate for that week. →
  `runs/OTR_R8_JUNE2026/REPORT.md` Part B addendum.

---

## Cross-check

| Status | Count |
|---|---|
| FACT | 46 |
| REPRODUCED | 24 |
| **Total in this file** | **70** |

Remaining 71 registry rows: 30 INFERENCE + 30 UNKNOWN (`CURRENT_HYPOTHESES.md`) and 11 FALSIFIED
(`FALSIFIED_HYPOTHESES.md`). 70 + 71 = 141 = `CLAIM_REGISTRY.csv` row count.
