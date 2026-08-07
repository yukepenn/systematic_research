# DC01 / DC02 — overshoot decomposition and threshold-invariance test

_2026-08-07 · `src/analytics/dc_overshoot.py` · data: 737,707 NQ 1-min closes, 2023-01-02 →
2025-01-31 · **zero configuration budget consumed** (this measures the price series, not a
strategy)._

Motivated by DR-01. Preregistered questions, both answered below:

- **DC01** — Is the observed edge a real deviation from the directional-change no-alpha null, and
  how large is it?
- **DC02** — Is the overshoot ratio scale-invariant in **tick** space (⇒ a fixed threshold is
  correct and H-006 is a distraction) or in **volatility** space (⇒ `S = k·σ` is correct)?

## 0. The identity being measured

Decompose the close path into alternating δ-trends. Segment *k* is entered at the flip
confirmation price and exited at the next flip:

```
pnl_k = ω_k − (δ + e_k)
```

where `ω_k` = overshoot from the confirmation price to the segment's close extreme, and
`e_k` = the **close-basis crossing excess** (how far past the ladder level the breaking bar
actually closed), `e_k ≥ 1 tick` by construction.

For a driftless diffusion the maximum before a δ-drawdown is `Exp(δ)` (Lehoczky 1977;
Zhang & Hadjiliadis 2009), so the null is `E[ω] = δ`, i.e. `r ≡ E[ω]/δ = 1`, giving
`E[pnl] = −E[e] < 0` **before commissions**. Note this is *sharper* than the version in DR-01,
which ignored `e`: on a discrete close grid the null is not break-even, it is strictly negative.

## 1. DC01 — the null is rejected, decisively, at every threshold

Null values: mean 1.0 · sd 1.0 · median 0.6931 · P(ω>δ) 0.3679 · P(ω>2δ) 0.1353.

| δ (ticks) | segments | **r = E[ω]/δ** | s.e. | **t vs r=1** | median | P(ω>δ) | mean excess (ticks) | mean pnl/segment |
|---|---|---|---|---|---|---|---|---|
| 60 | 28,557 | **1.3061** | 0.0099 | **31.0** | 0.767 | 0.427 | 17.9 | $2.41 |
| 90 | 15,984 | 1.2381 | 0.0117 | 20.3 | 0.756 | 0.418 | 20.0 | $7.08 |
| 120 | 10,337 | 1.2018 | 0.0138 | 14.7 | 0.750 | 0.414 | 21.5 | $13.76 |
| 150 | 7,224 | 1.1843 | 0.0157 | 11.7 | 0.747 | 0.413 | 23.4 | $21.38 |
| **179** | 5,404 | **1.1812** | 0.0176 | **10.3** | 0.765 | 0.418 | 23.5 | $44.57 |
| 200 | 4,547 | 1.1571 | 0.0189 | 8.3 | 0.745 | 0.411 | 24.6 | $34.13 |
| 230 | 3,597 | 1.1494 | 0.0210 | 7.1 | 0.761 | 0.412 | 25.3 | $45.18 |
| 260 | 2,929 | 1.1413 | 0.0237 | 6.0 | 0.754 | 0.404 | 25.6 | $55.58 |
| 300 | 2,327 | 1.1137 | 0.0263 | 4.3 | 0.730 | 0.395 | 27.0 | $35.78 |
| 360 | 1,685 | 1.1103 | 0.0309 | 3.6 | 0.725 | 0.388 | 27.6 | $60.50 |
| 440 | 1,211 | 1.0731 | 0.0347 | 2.1 | 0.721 | 0.378 | 28.3 | $19.57 |

**Findings.**

1. **`r > 1` at every threshold, with t = 31 down to t = 2.1.** NQ 1-minute closes carry genuine
   directional persistence beyond the martingale null. This is a much stronger statement than the
   backtest gives, because it is a property of ~28,000 events with no strategy, no exit policy and
   no parameter fitting.
2. **`r` falls monotonically with δ.** Persistence is *strongest at short thresholds* — the exact
   opposite of where the profitable plateau sits. The reconciliation is item 3.
3. **The shape of `r` is not the shape of the P&L.** The distribution is right-skewed exactly as
   the exponential null predicts: the median of `ω/δ` sits at 0.73–0.77 (null 0.693) while the
   *mean* is 1.07–1.31. The system loses on most segments and is paid by a fat right tail — which
   is precisely the measured 37–38 % win rate with PF ≈ 1.06. **Any exit rule that truncates the
   right tail attacks the only source of profit.** This is now a measured constraint, not a
   stylistic preference.
4. The segment-level economics reproduce the empirically-found plateau **without a backtest**:
   annualised rate `= n × (pnl − $13.89)` is −$328k at δ=60, −$109k at δ=90, ≈0 at δ=120,
   +$54k at 150, +$166k at 179, +$113k at 230, +$122k at 260, +$51k at 300. Break-even near
   δ≈120 and a broad optimum at 179–260 — matching the dense NT8 scans from an independent
   direction.

## 2. The biggest cost in this system is not commission or slippage

`e_k` is roughly **constant in δ** (17.9 ticks at δ=60 → 28.3 at δ=440, while δ grows 7×). It is
set by how far a 1-minute bar can travel past a level before it closes — a property of bar
volatility, not of the threshold. So it behaves like a **per-event tax**:

| δ | gross if filled at the ladder level | close-basis excess cost | commission | slip-1 | **excess share of friction** |
|---|---|---|---|---|---|
| 150 | $138.23 | $116.85 | $4.36 | $9.53 | **89 %** |
| **179** | **$162.15** | **$117.57** | $4.36 | $9.53 | **89 %** |
| 230 | $171.82 | $126.64 | $4.36 | $9.53 | **90 %** |
| 260 | $183.74 | $128.16 | $4.36 | $9.53 | **90 %** |

Read that row: at the canonical threshold a segment would be worth **$162** if both fills happened
at the ladder level, and **$30.68** after friction — and **89 % of that friction is the close-basis
trigger**, not commission ($4.36) and not slippage ($9.53) combined.

This retires a standing campaign assumption. The user's instruction "don't worry about slippage and
fees" turns out to be *correct for the wrong reason*: those costs are real but they are an order of
magnitude smaller than the execution-timing cost nobody had measured.

**New hypothesis H-011 (registered):** replace the market-on-close fill with a **resting stop order
at the ladder level**. This is not a free $118/segment — a resting stop fires on the intrabar
High/Low, so flips occur earlier and more often and the entire path changes; the effective filter
becomes intrabar-triggered rather than close-triggered. But given that the quantity being attacked
is ~4× the size of every other friction combined, it is now the highest-value execution experiment
on the frontier. It must be tested with honest stop-fill semantics (gap-through fills at the gap
price, plus slippage), and against the same neighbourhood-median standard as everything else.

## 3. DC02 — volatility normalisation wins, but only halves the drift

Per-bar σ (mean |Δclose| over a trailing session, causal): 2023 = 2.52 pts, 2024 = 3.01, 2025 = 4.31.
Median price: 17,558 → 21,138 → 22,881.

Across-year spread of `r` (max − min over 2023/2024/2025), averaged over the threshold grid:

| threshold measured in | mean across-year spread of `r` |
|---|---|
| **ticks (fixed, = the vendor design)** | **0.1164** |
| price (basis points) | 0.0848 |
| **volatility units (δ/σ)** | **0.0582** |

**Volatility normalisation halves the year-to-year instability of the overshoot ratio**, and beats
price normalisation. At matched δ/σ the three years agree to within 0.024–0.10 (best agreement at
δ/σ ≈ 12–14), versus 0.07–0.15 at matched tick thresholds.

**Verdict on H-006: the mechanism is real and the direction is confirmed.** `S = k·σ` is the right
functional form for stabilising the statistic the strategy actually monetises. This is now
evidence-based rather than an inference from the 41 %-selectivity-decay observation.

**But the honest caveat, stated before any strategy is run:** normalisation removes roughly half of
the drift, not all of it. `r` is genuinely higher in 2025 than 2023 *even at matched δ/σ*
(e.g. 1.1906 vs 1.1688 at δ/σ = 14). Something beyond volatility scale changed. So the
preregistered success signature for H-006 stands as written — stable event rate, stable S/σ,
better year and fold balance, cross-market portability — and **not** "higher full-history profit",
which this analysis does not predict and which would be a suspicious outcome.

A second caveat with teeth: the profitable operating point sits at δ/σ ≈ 10–18, where `r` is
1.15–1.25, but `r` is far higher (1.30) at δ/σ ≈ 4–6 where the excess tax makes trading impossible.
If H-011 succeeds in cutting the excess, **the optimal threshold moves down** into the
higher-persistence region, and H-006 and H-011 interact. They must be tested jointly, not
independently, and that is a design constraint on the next wave.

## 4. Reproduce

```
python - <<'EOF'
import sys; sys.path.insert(0,'src/analytics')
from dc_overshoot import dc_segments, exponential_fit_stats
EOF
```
Deterministic, no network, no NT8. Inputs: any close series; the canonical run used
`research/03_reverse_engineering/ledgers/t2_canonical_1m.csv`.
