# PUBLIC_ANALOGUE_MAP — open-source analogues of rolling/anchored-VWAP percentile channels

Directive §13 deliverable. Compiled 2026-08-24. Purpose: catalogue lawful open-source
implementations of the "population of anchored VWAPs → percentile rails" construction to
inform a clean-room VWAP Flux reconstruction. This is a study of publicly licensed code
and published concepts only. **No claim is made or implied that ninZa's VWAP Flux copies
any of these sources or vice versa** — convention coincidences are recorded purely as
evidence for which mathematical conventions are standard in the wild.

Retrieval method (reproducible): TradingView open-source scripts were fetched through the
public pine-facade endpoint for scripts published as `open_no_auth`
(`https://pine-facade.tradingview.com/pine-facade/get/PUB%3B<id>/last`); PUB ids recorded
per source below. GitHub sources fetched from raw.githubusercontent.com. No credentials,
no scraping of protected/invite-only source, no decompilation.

## License register / legal hygiene

| # | Source | Author | URL | License (verbatim from source header or repo) | Full source obtained? |
|---|--------|--------|-----|-----------------------------------------------|----------------------|
| 1 | Rolling VWAP Channel [LuxAlgo] | LuxAlgo | https://www.tradingview.com/script/nG3Tjpz2-Rolling-VWAP-Channel-LuxAlgo/ | "This work is licensed under a Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)" | YES (PUB;472fe483653a4d2dab20d8b066def6b5, created 2025-06-11, 6,179 chars) |
| 2 | Rolling VWAP (built-in) | TradingView | https://www.tradingview.com/script/ZU2UUu9T-Rolling-VWAP/ | Mozilla Public License 2.0 (header: "subject to the terms of the Mozilla Public License 2.0") | YES (PUB;043320bb572a4bb08853f40189c57586, v5 2026-01-09) |
| 3 | Multi-Anchor VWAP \| Trade Symmetry | TradeSymmetry | https://www.tradingview.com/script/2VUW4Xol-Multi-Anchor-VWAP-Trade-Symmetry/ | Mozilla Public License 2.0 | YES (PUB;98921a6ff8ef49e1891c93da6619e7bc) |
| 4 | VWAP Periodic Close [LuxAlgo] | LuxAlgo | https://www.tradingview.com/script/yEBIUAAK-VWAP-Periodic-Close-LuxAlgo/ | CC BY-NC-SA 4.0 (same header wording as #1) | YES (PUB;01f0bd68836842898bb214612e199626) |
| 5 | pandas-ta-classic `vwap` | pandas-ta contributors / xgboosted | https://github.com/xgboosted/pandas-ta-classic (`pandas_ta_classic/overlap/vwap.py`) | MIT ("The MIT License (MIT), Copyright (c) 2021+ pandas-ta contributors") | YES |
| 6 | Varadi percentile channels (R replication) | Ilya Kipnis (QuantStrat TradeR) / David Varadi (CSSA concept) | https://www.r-bloggers.com/2015/02/an-attempt-at-replicating-david-varadis-percentile-channels-strategy/ | Blog code, **no explicit license** → treat as all-rights-reserved; concepts only | Code lines quoted in blog |
| 7 | EdgeXplorer – VWAP Cloud Runner | EdgeXplorer | https://www.tradingview.com/script/m9fEBkbA-EdgeXplorer-VWAP-Cloud-Runner/ | Was listed as open-source; **publication now returns "Publication not found" (checked 2026-08-24)** | NO — description only (search caches) |

Hygiene rules for the reconstruction:
- **Math and conventions are not copyrightable; expression is.** We may freely reimplement
  the mathematical ideas below. We must NOT paste LuxAlgo (CC BY-NC-SA: NonCommercial +
  ShareAlike would attach to a derivative) or the unlicensed blog code into our codebase.
  MPL-2.0 (#2, #3) and MIT (#5) code could legally be adapted with notices, but the plan
  is an independent implementation from the target's own screenshots; these sources serve
  as convention references only. Short excerpts below are quoted for analysis/attribution
  under the respective licenses.
- Anything conceptually reused in reconstruction code gets a `// convention ref:` comment
  naming source + license, per directive.

---

## 1. Rolling VWAP Channel [LuxAlgo] — the priority target (full source recovered)

**This is the closest public embodiment of the VWAP-Flux-style construction**: a rolling
population of anchored VWAPs reduced to channel rails by percentile interpolation.
Pine v5, `overlay=true`, `calc_bars_count=10000`.

**Inputs / defaults:** Anchor Period = timeframe `"60"`; VWAP Source = `hlc3`
(user-selectable `input.source`); VWAP Amount = 20 (min 1, **max 500**); five rails with
default percentiles **100 (Max) / 70 (Upper) / 50 (Median) / 30 (Lower) / 0 (Min)**, each
independently toggleable with its own percentile input (0–100 float).

**Anchor lifecycle (VF-ANCHOR, verbatim mechanics):**
- Trigger: `new_tf = timeframe.change(anchor)` — every new anchor-period boundary starts
  a new VWAP accumulator (parallel arrays `vwaps_num`, `vwaps_den`, `vwaps`).
- Fill phase: while `vwaps.size() < vwapNum`, each boundary `push`es a new accumulator
  initialized with the boundary bar's `(volume*src, volume, src)`.
- Rolling phase: a cyclic counter selects the **oldest slot and re-initializes it in
  place** at each boundary; nothing is ever frozen. Core loop (CC BY-NC-SA 4.0, © LuxAlgo,
  quoted for analysis):

```pine
for [idx,value] in vwaps
    if idx == count and new_tf
        vwaps_num.set(idx, volume * src)
        vwaps_den.set(idx, volume)
        vwaps.set(idx, src)
    else
        vwaps_num.set(idx, vwaps_num.get(idx) + volume * src)
        vwaps_den.set(idx, vwaps_den.get(idx) + volume)
        vwaps.set(idx, vwaps_num.get(idx) / vwaps_den.get(idx))
```

- **Every retained anchor keeps updating on every bar** (the `else` branch runs for all
  non-reset slots, every bar, including intra-period bars). Retention = `vwapNum` slots.
- Implementation quirks worth knowing (so we don't over-idealize "the" convention):
  (a) counter wraps via `count == vwapNum => count := 0`, so `count` takes `vwapNum+1`
  distinct values against `vwapNum` slots — once per cycle a boundary resets **no** slot
  and every VWAP simply keeps accumulating (a pool of 20 effectively spans 21 anchor
  periods once per rotation); (b) during the initial fill phase the freshly pushed slot
  also falls through the `else` branch on its birth bar, so the first bar of each VWAP is
  double-weighted until rolling begins. Neither detail changes steady-state behavior
  materially, but both show that published implementations tolerate small boundary
  idiosyncrasies — our fit should too.

**Rails from the population:** each bar, the five rails are read directly off the live
population: `vwaps.percentile_linear_interpolation(p)` for p ∈ {100, 70, 50, 30, 0}.
That is Pine's built-in **sorted percentile with linear interpolation between the two
nearest ranks** (official reference wording). No windowing, no weighting — the population
is exactly the current values of the live VWAPs.

**Price/volume input:** default `hlc3` typical price × real bar `volume`; source is a
free input (close, hl2, etc. selectable).

**Fair-value / median:** simply the 50th-percentile rail of the same population — no
separate average-of-VWAPs line.

**Smoothing:** **none on any rail.** A one-pole recursive smoother
(`smoothed += (val - smoothed)/interval`, interval = bars per anchor period) exists in the
script but is used **only for the gradient fill colors**, never for plotted levels.

**Reset conventions:** purely rolling by anchor timeframe (60-min default). No session
reset; setting Anchor Period to `"D"` yields daily anchors. Anchor boundaries are marked
with a background highlight (`bgcolor` on `new_tf`).

**Relevance:** direct VF-ANCHOR embodiment; the default rail set 100/70/50/30/0 and the
"Anchor Period / VWAP Source / VWAP Amount" parameter vocabulary coincide with the
parameter families visible in the VWAP Flux manual (EV-019: manual defaults show levels
100-70-50-30-0; trader ran 95-75-50-25-5, Anchor 60, Amount 5). Coincidence of
conventions recorded as evidence of a standard construction; **no copying claim either
direction.**

## 2. Rolling VWAP — TradingView built-in (MPL 2.0)

A different family: **single sliding-time-window VWAP**, not a population. Included
because it defines what "rolling VWAP" means in the other dominant public convention.

- **Anchor lifecycle:** no anchors at all; one accumulator over a **time window in
  milliseconds** (auto-scaled by chart TF: 1min→1h, ≤5min→4h, ≤60min→1D, ≤4h→3D,
  ≤12h→7D, ≤1D→30.4375D, ≤1W→90D, else 365D; or fixed D/H/M inputs). Old bars **drop out
  of the sums** as they age past the window (queue-based `totalForTimeWhen` from the
  PineCoders `ConditionalAverages` library, with a minimum-bars floor, default 10).
- **Rails:** not percentiles — **standard-deviation bands**, `VWAP ± k·σ` for up to three
  user multipliers, with `variance = E[x²] − E[x]²` computed from volume-weighted sums
  (`sumSrcSrcVol/sumVol − rollingVWAP²`, clamped at 0).
- **Input:** `hlc3` default source × real volume; hard runtime error if the symbol has no
  volume.
- **Median/smoothing:** none; the VWAP line itself is the center.
- **Relevance:** if VWAP Flux ever had a "true sliding window" mode this is the public
  convention for it; also the variance-of-weighted-sums identity is the standard way to
  get bands without a second pass.

## 3. Multi-Anchor VWAP | Trade Symmetry (MPL 2.0)

Classic **multi-granularity concurrent anchors**: five simultaneous VWAPs at Session(D)/
Week/Month/Quarter(3M)/Year(12M).

- **Anchor lifecycle:** one accumulator **per granularity**, reset in place at its own
  `timeframe.change(...)` boundary (`if isNewPeriod: sumSrc := src*volume; sumVol :=
  volume; else sumSrc += ...`). Old anchors are not retained — each granularity keeps
  exactly one live VWAP. Data-gap guard: `na(src[1])` forces all anchors to re-anchor.
- **Rails:** none (five independent lines, no population statistics).
- **Input:** `hlc3` default source × real volume. No smoothing, no median.
- **Relevance:** shows the *other* common meaning of "multiple VWAPs" (heterogeneous
  calendar anchors) vs. the homogeneous rolled-anchor population of #1. VWAP Flux's
  manual-documented "Amount" of same-period layers matches #1's convention, not this one.

## 4. VWAP Periodic Close [LuxAlgo] (CC BY-NC-SA 4.0) — the VF-BLOCK analogue

- **Anchor lifecycle:** per period (D/W/M/3M/12M): a standard Pine anchored VWAP,
  `vwap = ta.vwap(source, timeframe.change(period))` — cumulative from period start,
  resets at each boundary. At each boundary the **completed period's final VWAP value
  `vwap[1]` is frozen** as a horizontal level (`line.new(bar_index[1], vwap[1], ...)`)
  with a label; the polyline of the completed VWAP path can also be kept.
- **Retention:** a user "Historical Closes" count per period (default 1); oldest frozen
  level `shift()`ed off when the count is exceeded. So: **frozen blocks, finite retained
  history** — exactly the VF-BLOCK lifecycle.
- **Rails:** none computed **over** the frozen population — the frozen closes are plotted
  as discrete support/resistance levels, not aggregated into percentile rails.
- **Input:** `hlc3` default source per period × real volume; no smoothing.
- **Relevance:** the cleanest public example of "completed blocks freeze." Note what it
  does NOT do: nobody in this sample computes percentile rails over *frozen* block
  values — see the final section.

## 5. pandas-ta-classic `vwap()` (MIT) — the Python research convention

```python
typical_price = hlc3(high, low, close)
wp = typical_price * volume
vwap  = wp.groupby(wp.index.to_period(anchor), observed=True).cumsum()
vwap /= volume.groupby(volume.index.to_period(anchor), observed=True).cumsum()
```

- **Anchor lifecycle:** calendar-period groupby (`anchor` = pandas offset alias, default
  `"D"`); cumulative within each period; the output series naturally preserves each past
  period's *path* (values as they stood bar-by-bar), and only the current period is live.
  One anchor granularity at a time; no population, no rails.
- **Input:** hlc3 × real volume, hard-coded typical price.
- **Relevance:** this is the convention our own Python-side replication harness should
  mirror for single-anchor legs; also the natural building block for a VF simulator
  (N shifted groupby anchors → column-wise percentile = #1's construction vectorized).

## 6. Varadi percentile channels (CSSA concept; R replication by QuantStrat TradeR)

Percentile-channel construction over a *price* population (not VWAPs) — included for the
rail math, which is the same statistical operation as #1's.

- **Rails:** running quantiles of price over rolling windows:
  `upperQ <- rollapply(prices, width=dayLookback, quantile, probs=0.75)` and
  `lowerQ <- ... probs=0.25`, with lookbacks **60/120/180/252 days**; signals ±1 on
  channel breaks, averaged across the four lookbacks (an *ensemble of windows*, which
  rhymes with our campaign-#1 ensemble findings). R's `quantile()` default is **type 7:
  linear interpolation, rank = 1 + p·(n−1)** — same family as Pine's
  `percentile_linear_interpolation`.
- **Relevance:** establishes that "sorted-population percentile with linear
  interpolation" is the standard rail construction across ecosystems (Pine, R); the
  concept (Varadi 2015) long predates every VWAP-population script here.
- License caution: blog R code has no explicit license → concepts only, no code reuse.

## 7. EdgeXplorer – VWAP Cloud Runner (publication removed; description only)

Was described as "a complete cloud system of **rolling anchored VWAPs**, statistically
evaluated and plotted across multiple quantiles," computing **"statistical percentile
levels (Max, High, Median, Low, Min) across the set"** of time-anchored VWAP layers.
The TradingView publication now 404s ("Publication not found," checked 2026-08-24 on
www/tw/my mirrors), so mechanics could not be verified from source. Recorded only as
corroboration that the #1 construction (VF-ANCHOR population + 5 named quantile rails,
Max/High/Median/Low/Min) had at least one independent open re-implementation in the wild
(July 2025). Do not rely on any unverifiable detail from it.

### Reference: exact Pine built-in semantics used by these scripts

- `ta.vwap(source, anchor)` — cumulative `Σ(source·volume)/Σ(volume)` reset when `anchor`
  is true. Real volume only.
- `array.percentile_linear_interpolation(arr, p)` — official reference: percentile "using
  method of linear interpolation between the two nearest ranks" on the sorted array.
  The precise variant (inclusive/type-7 `rank = 1 + (p/100)(n−1)` vs exclusive/NIST
  `(p/100)(n+1)`) is **not pinned down in the official docs**; for tiny populations
  (N = 5 layers!) the variants differ materially at p = 95/5 — treat the interpolation
  variant as a **free parameter to fit against screenshot rail positions**, not an
  assumption. (With type-7 and N=5: p95 → rank 4.8 → 0.8 of the way from 4th to 5th
  sorted value; p50 → exactly the 3rd (middle) value; p5 → 0.2 above the minimum.)
- `array.percentile_nearest_rank(arr, p)` — the no-interpolation alternative; returns an
  actual population member. A competing convention to test.
- `timeframe.change(tf)` — true on the first bar of each new `tf` period; the universal
  anchor trigger in all Pine sources above.

---

## Conventions most likely for VWAP Flux (synthesis for the clean-room build)

Definitions (per directive): **VF-ANCHOR** = all retained anchors keep updating
cumulatively with every new bar (rails drift smoothly, jump at rotation); **VF-BLOCK** =
completed blocks freeze at their final value (rails form staircases between boundaries).

**Support in the wild:**

| Convention | Public support found | Notes |
|---|---|---|
| VF-ANCHOR population + percentile rails | **STRONG**: #1 (full source), #7 (description) | The only published pattern that computes percentile rails over a VWAP population does it over **live, still-updating anchored VWAPs**. |
| VF-BLOCK frozen values | PARTIAL: #4 freezes completed-period VWAP closes as discrete levels | **No public source found that computes percentile rails over frozen block values.** The frozen-value pattern exists, but only as horizontal S/R levels. |
| Sliding-window single VWAP | #2 (built-in) | Different family; bands are σ-based, not percentile. |
| Heterogeneous calendar anchors | #3, #5 | One VWAP per granularity, in-place reset; no population statistics. |

This asymmetry independently supports the VF4/owner ruling (TRACK_VF_REPORT 2026-08-24b):
the ANCHORED-CUMULATIVE (VF-ANCHOR) reading with quantile-of-layers levels is not only
what the vendor chart images show, it is also the only construction with precedent in
public code. The frozen-segment staircase (VF1) reading has no public analogue as a
*channel* construction — consistent with its rejection.

**Most-likely per-element conventions for the reconstruction (with confidence):**

1. **Anchor lifecycle:** every Anchor-Period boundary (trader: 60 min) starts a new
   cumulative VWAP; a fixed pool (trader: Amount = 5) is maintained; at each boundary the
   oldest is dropped/re-initialized; **all retained layers keep accumulating every bar**
   (HIGH — image evidence + sole public precedent #1). Boundary quirks (which slot
   resets when; whether a rotation is skipped once per cycle as in #1) are second-order
   free parameters.
2. **Rails:** per bar, sort the N live layer values and take configured percentiles
   (trader: 95/75/50/25/5; manual default 100/70/50/30/0). Interpolation variant
   (linear-inclusive vs linear-exclusive vs nearest-rank) is a **fit parameter**; with
   N = 5, p50 is the middle layer under every variant, so the median rail is
   variant-independent — anchor the fit on the extreme rails (95/5), where variants
   diverge most (MEDIUM-HIGH that it is linear interpolation, per #1/#7 precedent and
   VF4's "quantile-of-layers beats range interpolation" result).
3. **Price/volume input:** typical price `hlc3` × real volume is the overwhelming public
   default (#1, #2, #3, #5 all default hlc3; #1/#3 make it selectable). Close × volume is
   the main alternative to test (MEDIUM-HIGH for hlc3-or-close; test both).
4. **Fair-value/median line:** the 50th-percentile of the same population, i.e. the
   middle layer when N = 5 — not a separate average (MEDIUM-HIGH; #1 precedent; VWAP Flux
   manual's "fair value" language fits a median rail). No public analogue smooths rails;
   if screenshots show smoother rails than raw percentiles produce, first suspect a light
   one-pole/EMA smoother of the #1 fill-helper form, else layer-count misread (LOW prior
   on any smoothing).
5. **Reset conventions:** rolling anchor-period only (no session reset) in every public
   population analogue. BUT: Pine has no session concept beyond timeframe boundaries,
   while a NinjaTrader implementation naturally sees session breaks; whether VWAP Flux
   clears its pool at session open (NQ 18:00 ET) is **unresolved and observable** —
   discriminate via the first hour after the session open in screenshots: a cleared pool
   collapses all rails onto few layers (degenerate/narrow cloud); a persistent pool
   carries overnight layers across the boundary (MEDIUM prior on rolling-only, per
   analogues).

**Discriminating observables for R1–R4 screenshot passes:**
- Smooth intra-hour rail drift + discrete jumps on the hour → VF-ANCHOR confirmed (jump
  size = effect of one layer being replaced in the sorted set).
- Rail staircase flat between hours → VF-BLOCK (would contradict current ruling; keep as
  falsifier).
- Median rail exactly tracking one identifiable layer (N = 5 ⇒ middle layer) → percentile
  (any variant), not mean-of-layers.
- Extreme rails (95/5) strictly inside the min/max layer envelope → linear interpolation;
  extreme rails coinciding with actual min/max layers → nearest-rank (or 100/0-style
  clamping).
- Rails pinned to population extremes when price runs (Max rail = newest layer ≈ src) →
  matches #1's `src == max` display edge case; confirms live-layer population.

**License note for the build:** implement from the math above + screenshot fits only.
Cite this file in the reconstruction source header as the convention provenance; do not
port Pine code verbatim from #1/#4 (CC BY-NC-SA) into campaign code.
