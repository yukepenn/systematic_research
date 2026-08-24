# VWAP Flux — Vendor Signal & Usage Model (three layers, public evidence only)

**Compiled:** 2026-08-24. Companion to `VWAP_FLUX_VERSION_TIMELINE.md` (source register there; sources cited
below as S1…S9 plus additions S10-S12). All quotes verbatim from public vendor material. MARKETING labels mark
promotional prose that is **not** algorithmic proof. The three layers below must **never be conflated**:

- **Layer A** — what the licensed VWAP Flux *indicator* computes and exposes (vendor-documented).
- **Layer B** — how the *vendor* publicly teaches/ships consumption of those signals (wrapper patterns).
- **Layer C** — what the *trader's own custom wrapper* does (constrained, never determined, by A+B).

---

## Layer A — Raw VWAP Flux signals (vendor-documented indicator behavior)

### A.1 Input parameters (official Trader Manual, S2, uploaded 2026-02-02; panel labels from manual screenshots)

Settings-panel order (13 rows; matches trader's OTRIMG-0117 stack 13/13): `Volume Base` (implied §2.1, not
visible in the suggested-settings screenshots), then **Anchor Period (Minutes), VWAP Amount, Trend: Period,
Trend: MA Type, Level: Max (%), Level: Upper (%), Level: Median (%), Level: Lower (%), Level: Min (%),
Signal: Quantity Per Trend (%), Signal: Close Threshold (%), Signal: Split (Bars)** (+ `Zone Period`, §2.14,
not visible in any public panel screenshot).

| Parameter | Vendor definition (verbatim or near-verbatim, S2) | Module |
|---|---|---|
| Volume Base = **"BidAskPrice_RealVolume"** | "This mode should be used for instruments with real volumes (futures & stocks) … Buy Volume: If the price of a tick is greater than or equal to the ask price, the real volume of the tick is categorized as buy volume … Sell Volume: If the price of a tick is less than or equal to the bid price …". **Tick Replay required for historical computation:** "If Tick Replay is disabled, the indicator functions only on real-time data and there are no calculations on historical data. Any actions that lead to chart reloading will erase all calculations." | volume engine (feeds cloud + cum-delta) |
| Volume Base = "UpDownTick_RealVolume" | up/down-tick classification of real volume; works on historical + real-time but "historical and real-time calculations of the same bar may not be 100% identical" | volume engine |
| Volume Base = "UpDownTick_UnitVolume" | unit volume (1) per tick; "the one & only choice for instruments without real volumes (forex, CFDs, indices)" | volume engine |
| Anchor Period (Minutes) | "defines the time cycle, in minutes, used to recalculate the VWAP … when Anchor Period = 30, the indicator will recalculate the VWAP bands every 30 minutes" (1440-min cap removed 2026-01-17, S1) | cloud |
| VWAP Amount | "Defines the number of recent VWAP layers used to construct the VWAP bands … if VWAP Amount = 5, the indicator will use the five most recent VWAP layers to calculate the Highest, Upper, Median, Lower, and Lowest levels" | cloud |
| Trend: Period | "defines the averaging period of price used to determine the market trend" | trend |
| Trend: MA Type | "The moving average type (can choose from 11 popular moving-average types)" | trend |
| Level: Max/Upper/Median/Lower/Min (%) | each "defines the … threshold" for its plot within the VWAP bands; Median = "threshold for the Fair Value plot" | cloud |
| **Signal: Quantity Per Trend (%)** | "Specifies the maximum number of trade signals allowed to appear within the same support or resistance zone. For example, if Signal Quantity Per Trend = 4, it means that only 4 same-direction signals are allowed to appear within a single trend. Note: It is not recommended to set this value too high…" (anti-overtrading suppression *inside the indicator*) | signal |
| **Signal: Close Threshold (%)** | "Defines the minimum percentage of the candle's close relative to its full range (from Low to High) for the candle to qualify as a valid signal." Illustration: "Close − Low ≥ 70% → valid Sell signal"; bullets: "For a Sell signal, the candle is considered valid if its close lies within the upper 70% of the candle's range measured from the Low. For a Buy signal, the close must fall within the lower 70% of the range measured from the High." *(Note the sell/buy orientation as written — sell validity is measured from the Low upward. Take verbatim; do not "correct" it when modeling.)* | signal |
| **Signal: Split (Bars)** | "Specifies the minimum bar distance required between two consecutive signals in the same direction … if Signal Split (Bars) = 30, … the current Buy signal must be at least 30 bars away from the previous Buy signal" | signal |
| **Zone Period** | "defines the cycle used by the indicator to identify static S/R zones. A higher value results in fewer S/R zones, as stronger price movement over a longer cycle is required for a zone to form." | zones |

### A.2 Output signal series ("Dedicated NinjaScript Signals" — vendor-documented API)

Current (S1, read 2026-08-24; in force since 2026-02-24 per changelog):
- **`Signal_Trend`: 2 = uptrend strong, 1 = uptrend weak, -2 = downtrend strong, -1 = downtrend weak**
- **`Signal_Trade`: 1 = bullish, -1 = bearish, 0 = no signal**
- **`Signal_Cum_Delta`: 1 = positive, -1 = negative, 0 = no signal** (series added 2026-02-09)

Pre-2026-02-24 (S2, manual §4): "**Signal Trend:** 1 = bullish, -1 = bearish; **Signal Trade:** 1 = bullish,
-1 = bearish" — two-state trend, no cum-delta series. The ±2/±1 strong/weak encoding is therefore a
**post-Feb-24 feature** (inference MEDIUM-HIGH; see timeline §3).

Directive answer: the +2/+1/-1/-2 hypothesis for Signal_Trend is **CONFIRMED for the current build** and
**CONTRADICTED for builds before 2026-02-24** (they were ±1 only).

### A.3 Zones module — public UI answer

**YES**, public material shows a static S/R zone module: manual §2.14 "Zone Period" + manual pp.3-4
("Static Support/Resistance zones … derived from major swing highs and lows … Each static S/R zone is
analyzed with Buy/Sell volume … also reveal the internal POC and VWAP levels"). The launch-era microsite
(S4, captured 2026-01-14) already advertised absorption vs push zone classification, POC, intra-zone VWAP —
so the zone module existed at launch. Caveat: none of the four suggested-settings screenshots (S2 pp.13-15)
shows a `Zone Period` row — the visible panels end at `Signal: Split (Bars)`; whether Zone Period sits in a
separate panel group or was added between launch and the Feb-2 manual is **UNKNOWN** from public material.
No public evidence of a zone on/off checkbox or zone-count parameter beyond `Zone Period`.

### A.4 Suggested settings (manual pp.13-15 screenshots) — the "defaults" question

There is **no public statement of shipped factory defaults** (would require installing the product). The
manual publishes four *suggested presets* (all: Trend Period 14, Trend MA Type EMA, Signal Quantity Per
Trend 5, Signal Close Threshold **70**):

| Preset | Anchor | Amount | Levels Max/Up/Med/Low/Min | Qty/CloseThr/Split |
|---|---|---|---|---|
| 1-minute chart | 20 | 7 | 80/60/50/40/10 | 5/70/15 |
| 3-minute chart | 60 | 10 | 90/60/50/40/20 | 5/70/15 |
| 5-minute chart | 120 | 5 | **100/70/50/30/0** | 5/70/15 |
| 1000-volume ("Highly Recommend") | 30 | 5 | 80/60/50/20/10 | 5/70/15 |
| ninZaRenko 12/4 | 3 | 5 | 80/60/50/20/10 | 5/70/**30** |

Directive answers: **"100/70/50/30/0" is exactly the 5-minute-chart suggested preset** (not a proven factory
default). **"Close Threshold 80" appears nowhere in public material** — every preset shows 70 and the §2.12
example uses 70; the value 80 occurs only as *Level: Max* in the 1-min and Renko presets. (This corrects the
"manual-shown …/4/80/30" line in `TRACK_VF_REPORT.md`; the "4" there is §2.11's example sentence, not a
panel value.)

### A.5 What Layer A does NOT disclose (blocked internals — unchanged)

Public material documents the *architecture* but not the math: layer→level aggregation (how 5 layers map to
Max…Min at the Level % thresholds), Fair Value Plot definition, the trend triple-condition ("Price vs. Fair
Value Plot / Cloud Break / Cloud Slope" — MARKETING wording, S4/S5), and the exact Signal_Trade trigger
(beyond "pullback into the band while trend intact" + the three signal filters above). These remain the
identified missing mechanisms per `TRACK_VF_REPORT.md`.

---

## Layer B — Vendor wrapper patterns (how ninZa publicly consumes its own signals)

**B.1 Strategy Builder single-condition pattern (documented).** Manual §4 (S2): "You can rely on the signals
below to build your own strategy … Below is the example condition … based on the **Signal_Trade**: If
Signal_Trade equal to 1, you can enter long here. Conversely, if Signal_Trade equal to -1, you can enter
short here." + linked tutorial video `mtMNjOQtfQE` "Building an Auto Simple Strategy with ninZa.co Products
in NinjaTrader 8's Strategy Builder" (uploaded 2024-05-02). This is the vendor's canonical minimal wrapper:
**trade off Signal_Trade alone; exits left to the user/ATM.** Confidence HIGH.

**B.2 Cross-product two-series convention (documented).** ninZa signal products expose a *state* series +
an *event* series. Easy Trend (S8): "Signal_Trend: 1 = uptrend, -1 = downtrend; Signal_Trade: 2 = uptrend
Pullback, -2 = downtrend Pullback, 1 = uptrend start, -1 = downtrend start, 0 = no signal" (changelog
2024-09-10: "Signal_State was renamed to Signal_Trend; Signal_Trade was added"). The natural composed wrapper
— gate on Signal_Trend state, fire on Signal_Trade event — is *implied by the API shape* and by vendor
education (S7: "Use VWAP Flux to understand the market direction, important price zones, and the overall
trading context. Then use Quantum Vol-Delta to evaluate whether real buying or selling pressure supports the
setup … Delta should not be treated as an entry signal by itself."). Confidence HIGH for the convention;
the composed gating is an inference (MEDIUM), not shipped code.

**B.3 HelloWin two-stage window pattern (documented, ecosystem-level).** HelloWin (hellowin.io — ninZa sister
brand; ninZaResources changelog added the "HelloWin logo" 28 Nov 2022) ships **HelloWin Backtest**, whose
entry model is the published two-stage + maximum-bar-window pattern: "The software lets you define your
system's entries with **2 rounds of rules**: 1st round: You define the 'Hit Bar' with a set of user-defined
conditions. Each 'Hit Bar' will open up a **'Watch Period'** to scan for entries. For example, a Watch Period
of 30 bars means entry signals will be sought within 30 bars after the Hit Bar. 2nd round: You define the
**'Signal Bar'** (which fires an entry signal) with another set of user-defined conditions. Signal Bar is only
searched for within the Watch Period, and the Watch Period can witness the appearance of many Signal Bars."
(S10: https://hellowin.io/product/hellowin, fetched 2026-08-24). Confidence HIGH that this pattern is
published by the vendor family. **IMPORTANT LIMIT:** no public HelloWin/ninZa *code sample specifically
wiring VWAP Flux's SignalTrend-then-SignalTrade with a bar window* was found — the two-stage window pattern
is documented as a product concept, not as VWAP Flux example code.

**B.4 Infinity Algo Engine$ (vendor's modern no-code wrapper).** The VF automation videos (2026-02-02,
2026-02-05) are run by Infinity Algo Engine$ (S11: https://ninza.co/product/infinity-algo-engine; S5
microsite: "fully automated by the Infinity Algo Engine$" with ApexFlow Zignal + VWAP Flux). Published
capabilities: "multi-layered condition chains", "multiple entry scenarios, such as trend continuation,
pullbacks, failed breakouts", "Separate ATM … assigned to each signal type or condition set … Each strategy
logic can have its own stop, target, and trade management rules", plus daily-loss-type protections
("Max Dai[ly] …"). **Exits in every published vendor wrapper are ATM-style stop/target/management — no
trend-flip or signal-based exit is documented anywhere public.** Confidence HIGH (feature list), MARKETING
for performance claims.

**B.5 Free-strategy packages.** hellowin.io/free-ninjatrader-strategies (S12) publishes combo recipes (e.g.
"Double Dragons": Solar Wind signal generator + MA Crossover trend identifier) — establishes the vendor's
standard *signal-generator + trend-filter* composition template, but references Solar Wind, not VWAP Flux.

---

## Layer C — The trader's custom wrapper (what public evidence can and cannot constrain)

Internal evidence (not repeated here): 13/13 VF parameter-label match in OTRIMG-0117 (2026-02-13); custom
values Anchor 60 / Amount 5 / Trend 20 / Levels 95-75-50-25-5 / Qty 3 / CloseThr 10 / Split 5; checkbox
banks from 2026-02-20; −$2,600 ≈ 130-pt intrabar stop (TRACK_VF_REPORT).

What the **public** record contributes to Layer C:

1. **The wrapper's raw inputs are now enumerable.** Everything a NinjaScript wrapper can read from VF without
   decompilation is the documented series set: `Signal_Trade` (1/-1/0), `Signal_Trend` (±1 before 02-24,
   ±2/±1 after), `Signal_Cum_Delta` (1/-1/0, exists only from 02-09), plus the plotted band/zone values.
   Any reconstruction using other VF internals is unsupported.
2. **Signal suppression is Layer A, not Layer C.** `Signal Quantity Per Trend`, `Signal Split (Bars)`, and
   `Signal Close Threshold` throttle signals *inside the indicator*. The trader's 3/10/5 setting means the
   raw `Signal_Trade` stream he consumed was already thinned/filtered by the vendor's logic — a wrapper-side
   re-implementation of these filters would double-count them. Do not conflate.
3. **The trader's parameter deltas are aggressive Layer-A tuning**, not wrapper logic: CloseThr 10 (vs 70
   suggested) ≈ near-disabling the close-position filter; Split 5 (vs 15) and Qty 3 (vs 5) reshape signal
   density; Levels 95-75-50-25-5 widen the band vs every preset. Public material says nothing about these
   values — they are the trader's own choices (Class-A internal finding).
4. **Two-stage entry in the trader's wrapper is HYPOTHESIS.** Supported analogies: vendor API shape
   (state + event series, B.2) and the HelloWin Hit-Bar/Watch-Period pattern (B.3). But no public VF-specific
   two-stage sample exists; the manual's own example is single-stage (B.1). Any
   SignalTrend-then-SignalTrade-within-N-bars reconstruction must be labeled trader-side hypothesis.
5. **Exits are the trader's own.** No public vendor wrapper documents signal-based exits; vendor practice is
   ATM stop/target (B.4). The trader's identified 130-pt stop is consistent with vendor ATM practice; his
   *profit-taking / exit rule remains unidentified by both public and internal evidence* (open item in
   TRACK_VF_REPORT).
6. **Version sensitivity (link to timeline §5).** If the wrapper gates on `Signal_Trend`, the 2026-02-24
   2-state→4-state upgrade would silently change behavior (e.g. `== 1` stops matching strong uptrends).
   If it reads `Signal_Cum_Delta`, the wrapper cannot predate 2026-02-09. Both are HYPOTHESES aligned with
   the trader's late-Feb behavior shifts.
7. **Data-mode constraint (hard, documented).** In `BidAskPrice_RealVolume` mode VF has **no historical
   values without Tick Replay** (A.1). Whatever mode the trader ran determines whether his wrapper could
   ever backtest vs run live-only — a reconstruction detail that public documentation pins down exactly.

**Additional sources for this file:** S10 https://hellowin.io/product/hellowin (fetched 2026-08-24);
S11 https://ninza.co/product/infinity-algo-engine (fetched 2026-08-24); S12
https://hellowin.io/free-ninjatrader-strategies (fetched 2026-08-24). S1-S9: see
`VWAP_FLUX_VERSION_TIMELINE.md` §6.
