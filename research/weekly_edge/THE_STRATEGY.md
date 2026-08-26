# THE STRATEGY — every component, every parameter, and why (2026-08-25, after 37 waves)

Written for the owner's question: *"解释一下目前我们具体策略，每个具体参数，以及为什么是这样，
以后怎么进步，这样为什么我们最想要的赚最多的。"*

Companion documents: `STATE_OF_THE_SYSTEM.md` (headline numbers), `PRINCIPLES.md` (mechanism
record), `PARKED_NOT_DEAD.md` (everything stopped, and what would revive it).

---

## 0. The one-sentence description

**A selection-free majority vote of 32 volatility-scaled trend-reversal detectors on NQ
1-minute bars, long-biased, blocked out of quiet intraday regimes, truncated in both
directions at the session level, and sized up on flips whose surrounding state scores well
against a causal quality rule.**

---

## 1. THE SIGNAL — 32 Solar ratchets, majority vote

### What one member does
A "ratchet" carries an anchor and a threshold `S`:

```
if in an UP leg:   anchor = max(anchor, close)
                   if close < anchor - S  ->  FLIP DOWN, reset anchor and S
if in a DOWN leg:  anchor = min(anchor, close)
                   if close > anchor + S  ->  FLIP UP,   reset anchor and S
```
`S = clamp(VolMult × σ, 40 ticks, 1200 ticks)` where `σ` = trailing mean |Δclose| over
**460 one-minute bars**.

| parameter | value | why this value |
|---|---|---|
| `VolMult` per member | 6, 8, 10, 12, 14, 16 (the "narrow6" set) | inherited from the shipped product; W13's leave-one-out found the member set is a **real sensitivity** (narrow7 costs −0.038 Sharpe), so it is treated as fitted, not structural |
| `σ` window | 460 bars | inherited from `SolarWaveOneContractNQ_v5`; W32 tried other clocks and they were worse |
| `S` clamp | [40, 1200] ticks | inherited; never re-tested in isolation |
| flip test | strict crossing | campaign #6 proved INCLUSIVE gives zero valid solutions on the 2023 reconstruction |

### Why a ratchet and not a breakout
W25 measured a Donchian breakout — *"close above the N-bar high"* — at **−0.34 Sharpe** on the
same instrument where the ratchet earns. W31 then measured why: holding long because the leg
is nominally up earns **0.0025 points per bar**; holding long because the ratchet has just
**flipped** earns **0.0603** — **24×**. **The edge is in the flip EVENT, not the trend STATE.**
This single fact explains both results and closes every "hold longer / re-enter sooner"
proposal.

### Why 32 voters and a majority, not one configuration
W19 walk-forwarded "pick the best single configuration each quarter": **88 % of quarters
changed the pick and it beat doing nothing by only +0.021 Sharpe**. Selection is noise.
W20 replaced selection with aggregation — a one-contract **majority vote** — and the result
beat both the selector and naive, at **the 98th percentile of its own circular-shift null
(p = 0.020)**, robust to dropping any subfamily (spread 0.034).

The 32 voters are `4 member-sets × 4 throttle settings × delta-gate on/off`.

### Why long-only
Replicated **four independent times**: W16 (side split: shorts earn ~⅓ the per-trade rate of
longs on every sleeve), W17 (the ONLY finding to replicate on 2006-2021: +0.072 vs −0.008),
W19 (the hindsight-best fixed config is long-only), W20 (long-only vote 0.214 > both-sides
0.200 with half the tail). Shorts are kept as a **separate insurance sleeve**, not production.

---

## 2. THE CONTEXT FILTERS

| filter | rule | parameter | evidence |
|---|---|---|---|
| **range throttle** | no new entry while the session's realised range through bar *i−1* is below **q × its trailing-60-session same-minute median** | **q = 0.8** | **95th percentile of its own null (W13)**; and W23 measured that the bars it blocks would have **lost $9,540** if traded. It declines losses, not opportunity. Sharpe is flat across q ∈ {0.7, 0.8, 0.9} — not knife-edge |
| **delta gate** | long only when the session's 1-minute up/down-tick cumulative delta (lagged) is ≥ 0 | on/off across voters | **weak (p = 0.10)**. Kept on its leave-one-out cost (+0.041 Sharpe) and never described as understood. W15 showed true tick delta beats the proxy by +32 %/trade but misses the 25 % bar, so buying tick data was refused |

---

## 3. THE RISK BOX — the session's two walls

| wall | rule | value | evidence |
|---|---|---|---|
| **halt** | stop the sleeve for the rest of the session once realised session P&L ≤ −H | **H = $1,300** | **98th percentile of its own null, p = 0.020 (W28)**. Halves the worst week AND raises Sharpe simultaneously — almost nothing else in this campaign does both |
| **target** | stop the sleeve for the rest of the session once realised session P&L ≥ +T | **T = $1,000** | **weak (88th percentile, p = 0.12, W27)** — kept because it improves daily hit rate, weekly Sharpe, worst week and concentration at once, but it is NOT proven |

**Why session-level and not per-trade**: W02 measured that a 65-point per-trade cap touches
only **142 of 13,301 trades** and leaves the worst week unchanged. Our losses are **intra-week
accumulation**, not single catastrophes — so the truncation must be applied to the
accumulation process. The trader's own −$2,600 per-trade unit does not transplant.

---

## 4. THE QUALITY LAYER (newest, W33–W37)

At each flip, five **causal** features are scored against the quantiles of the **trailing 250
prior entries** (never the full sample — that was a look-ahead worth 3.05 pts/session, found
and fixed in W37):

| feature | favourable when | why it is admissible |
|---|---|---|
| distance from session open ÷ ATR | high | not used anywhere else in the object |
| **prior session's return** | **low** (contrarian) | a mean-reversion conditioner on a trend system |
| run length of same-direction closes | high | — |
| distance from session VWAP ÷ ATR | high | — |
| \|cumulative delta\| ÷ average volume | high | magnitude, distinct from the delta gate's sign |

`score` = how many of the five are favourable (0–5).
**`size = 2 contracts when score ≥ 3, else 1`** — and **k = 3 is not a chosen parameter, it is
"a majority of five"**. W36 showed that choosing k from a grid produced 67 % quarterly churn
and failed the walk-forward; deriving it removes the churn entirely.
**`cut`**: entries with a low score are closed after the base object's own **trailing median
hold, which the data sets to 23 bars** — again derived, not chosen.

### Why sizing and not filtering
Filtering to the good flips **destroys production** (10.62 → 2.86–3.61 pts/session): quality
rises, quantity collapses. Sizing keeps every trade and adds contracts only where the evidence
is. Attribution (W36): **21 % of trades — those with score ≥ 3 — deliver 79 % of the profit**
at $619–729 per trade, while score-0 trades **lose** money.

### Why this is not the "leverage" this campaign rejected three times
W06 (pyramiding on unrealised profit), W10 (sizing on the range ratio) and W22 (sizing on the
vote fraction) all scaled with information the object **already trades on** — doubling the same
bet. The five features above are used **nowhere else**. W35 proved the distinction empirically:
the identical score lifts the Solar vote **+49 %** but EMA-cross only +2.6 % (Sharpe down) and
random entries not at all. **It grades the event; it is not a market-state edge.**

---

## 5. WHAT IT DELIVERS (honest, causal, out-of-sample within the regime)

| object | contracts | pts/session | weekly | % weeks + | worst week | Sharpe | weekly ÷ \|worst\| |
|---|---|---|---|---|---|---|---|
| base vote + box | 1 | 10.62 | $1,060 | 59.1 % | −$7,487 | 0.305 | 0.142 |
| **+ causal quality sizing (P1)** | ≤2, avg 1.18 | **14.72** | $1,470 | 58.6 % | −$7,418 | 0.311 | 0.198 |
| **+ causal cut (P2)** | ≤2, avg 1.11 | 13.50 | $1,347 | 56.7 % | **−$5,818** | 0.291 | **0.232** |
| quarterly walk-forward of the layer | ≤2 | 14.41 | $1,545 | 59.3 % | −$7,418 | 0.303 | 0.208 |
| + S1 + short box (multi-sleeve) | ≤4 | ~37 | ~$3,700 | ~65 % | ~−$24,800 | ~0.31 | — |

**Two independent honest paths agree**: the quarterly walk-forward (14.41) and the causal fixed
rule (14.72). The earlier 17.78 / 0.338 was threshold look-ahead and is retired.

---

## 6. WHY THIS SHAPE IS THE ONE THAT MAKES THE MOST MONEY

1. **Production comes from event quality, not from time in the market.** We hold a position on
   only ~13 % of bars. W31 proved that raising that to 21–24 % by holding trend state
   *collapses* production (0.70–3.93 pts/session). So money is made by being **more right when
   we act**, and the quality layer is the only lever that has ever done that.
2. **The tail is truncated where it is actually formed.** Losses accumulate within a session,
   so a session halt cuts the worst week in half while *raising* Sharpe. Nothing else the
   campaign tested does both.
3. **The quiet regime is defence-only** — three independent attempts to trade it lost money
   (W11, W18 ×2). But with the box and the quality layer, the 83 % of sessions that used to
   bleed **−$102k now deliver 65 % of the profit** at $122/trade (W36). Defence turned the
   majority of sessions from a cost into the larger half of the income.
4. **Exposure is the owner's dial, not a research claim.** Sharpe is exposure-invariant, so
   contracts scale profit and tail together: 1 → $1,347/wk at −$5,818; ~4 sleeves → ~$3,700/wk
   at ~−$24,800. The research job is to raise **profit per unit of tail**, and that number has
   gone **0.142 → 0.232 (+63 %)**.

---

## 7. HOW IT IMPROVES FROM HERE (ranked, with what is already known)

1. **Short-side quality**, properly. W35 measured short quality sizing at +15 % production but
   a worse tail; the short sleeve is Sharpe 0.162 with the box (corrected from 0.067). A
   short-specific score — not the mirrored long one — has never been built.
2. **More quality features.** The current five were the survivors of 16 candidates in one pass.
   The R29 protocol can screen dozens more; each admitted feature raises the resolution of the
   score, which is the mechanism that actually pays.
3. **A second, genuinely independent model.** W25 established that everything we own is the
   same Solar ratchet, and that orthogonal engines lose while profitable ones correlate. This
   is the campaign's largest standing risk: a decay in the ratchet takes every sleeve at once.
4. **The multi-clock axis is only PROVISIONALLY closed** — W32's harness dropped the tilt,
   hysteresis and combiner and scored 4.85 against the real object's 10.62. It deserves a
   re-run on the true engine before being written off.
5. **VWAP Flux (~$300)**, per campaign #6's R33: not proof of anything, an instrument that
   collapses the entry-information hypothesis space. Its delta argument was weakened by W15;
   its Fair Value / rails / `Signal_Trade` argument stands.

---

## 8. WHAT WOULD MAKE ME ABANDON THIS SHAPE
- the flip-event finding failing a replication on new data (it is the load-bearing mechanism);
- the quality layer failing a virgin-forward read after 2026-11-01;
- a genuinely orthogonal second model appearing that earns — which would make the current
  single-model concentration a choice rather than a constraint.
