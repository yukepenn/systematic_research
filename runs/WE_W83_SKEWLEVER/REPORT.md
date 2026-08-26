# WE_W83 — WHAT THE QUALITY SIZING LAYER ACTUALLY COSTS · REPORT

Preregistered. Six sizing maps over the **same** object, same score, same box, same fills — only
the map from causal score to contracts changes. Rolling test run before any full-sample table was
interpreted. All figures at both friction lines, since the arms differ in contract count.

> ## The layer's price, measured for the first time in 83 waves:
> ## **+19.3 % money at a fixed drawdown, −2.3 pp of positive weeks, +1.12 of weekly skew.**

---

## 1. Phase 0 — the premise holds, but the mechanism is not what I predicted (`FACT`)

| arm | avg size | RT/week | **weekly skew** | kurtosis |
|---|---|---|---|---|
| **Q1_flat (layer OFF)** | 1.00 | 10.00 | **0.98** | 1.74 |
| Q2_inverted (size 2 on score ≤1) | 1.58 | 13.33 | **1.05** | 2.48 |
| Q3_selective (size 2 on score ≥4) | 1.05 | 10.32 | 1.23 | 2.73 |
| Q5_graded | 1.42 | 11.99 | 1.52 | 4.35 |
| **Q0_incumbent (size 2 on ≥3)** | 1.18 | 11.12 | **2.10** | 8.91 |
| Q4_levered (size 3 on ≥3) | 1.35 | 12.13 | **3.06** | 18.20 |

Skew spread **2.08 units** — the premise holds; sizing is a real skew lever, and **the incumbent
layer more than doubles P1's weekly skew (0.98 → 2.10)**.

But the preregistered ordering `Q2 < Q1 < Q0 < Q4` came out **SCRAMBLED**: inverting the layer
(Q2, 1.05) does **not** push skew below flat (Q1, 0.98).

> `RECORDED`: **size DISPERSION itself adds skew, irrespective of direction; sizing on the score
> adds a great deal more.** Flat sizing is the skew floor and you cannot get below it by inverting.
> That refines W42's mechanism — the excursion forecast is why the *up* direction adds so much,
> but it is not the whole story.

## 2. The layer's measured price (`FACT`) — Q0 vs Q1, at W82's measured $14.65/RT

| | Q0 (layer on) | Q1 (layer off) | delta |
|---|---|---|---|
| **positive weeks** | **52.6 %** | **54.9 %** | **−2.3 pp** |
| weekly skew | +2.10 | +0.98 | **+1.12** |
| **money at a fixed $20,245 drawdown** | **$854** | $716 | **+19.3 %** |
| weekly Sharpe | 0.246 | 0.228 | +0.018 |
| max drawdown | $27,319 | $22,636 | +21 % |
| longest losing streak | 8 | **7** | worse |
| median week | $116 | **$296** | worse |

**This is the trade the campaign has been making since W37 without knowing its price:** the layer
buys roughly a fifth more money per unit of drawdown and pays for it in the metric the owner ranks
first, plus the median week and the losing streak.

Under the owner's stated ordering — consistency, then drawdown, then money — **this is not
obviously the right trade**, and it has never been presented as a trade at all.

## 3. Phase 1 — rolling windows, run first (`FACT`)

Fraction of 25 rolling 24-month windows in which each arm beats Q0, at $14.65/RT:

| arm | **positive-week %** | money @ fixed DD | mean top-5 DD | **ALL THREE** |
|---|---|---|---|---|
| Q1_flat | 64 % | 4 % | 64 % | **0 %** |
| Q2_inverted | 40 % | 0 % | 64 % | **0 %** |
| **Q3_selective** | **88 %** | 4 % | **84 %** | **0 %** |
| **Q4_levered** | 64 % | **100 %** | 36 % | **24 %** |
| Q5_graded | 80 % | 16 % | 80 % | **0 %** |

**Q3_selective (size 2 only at score ≥4) beats the incumbent on the owner's primary metric in
88 % of windows and on the drawdown distribution in 84 %** — and gives up money in 96 % of them.
It is the cleanest statement in the wave of what the layer's aggressiveness costs.

## 4. Q4_levered — passes this wave's bar, fails the campaign's (`stated both ways`)

By W83's own preregistered rule (beat Q0 on positive-week % in a majority of windows AND give up
≤10 % of money at fixed drawdown), **Q4 is a CANDIDATE**: 64 % of windows on the hit rate and
**149.9 %** of Q0's money at a fixed drawdown. In levels it makes **35 % more money with a 10 %
smaller maximum drawdown**.

**It should not be believed yet, for three specific reasons:**

1. Its **all-three rate is 24 %**, against the campaign's standard bar of a majority. That bar has
   now killed seven consecutive candidates.
2. Its maximum-drawdown advantage is **not** matched by its drawdown *distribution*: mean top-5
   DD is **$16,040 vs Q0's $13,674 — worse**, and its worst week is −$9,353 vs −$7,581. A better
   max with a worse top-5 is a single avoided episode, which is precisely the signature that
   failed in W78 (24 % of windows) and W79 (4 %).
3. It is the same signal sized harder. PRINCIPLES law 5 draws the line at *sizing on new
   information* — which the score is — but a 4× version was already rejected once, and "more of
   the thing that worked" is the easiest way to manufacture a full-sample winner.

**Not promoted. Queued for a proper champion-vs-challenger** with a walk-forward, per-year table
and null, on the same terms as W78/W79/W80.

## 5. `CORRECTION` — W74's exchange rate does not transfer to this family

W74 fitted `wk+% = 48.07 + 45.41·Sharpe − 2.99·skew` on 216 halt/target cells and validated it on
19 held-out objects at **R² +0.277**. These six sizing arms are a genuinely different family, in
neither set. Applying the frozen coefficients:

> **MAE 1.11 pp, bias −0.07 pp, but R² = −1.222.**

Negative R² again — the same failure mode as W74 read 1. The low MAE is an artifact of all six
arms clustering between 51.6 % and 54.9 %; the relation carries **no** cross-sectional information
here. It mispredicts Q4 by +3.6 pp in the direction that matters (predicting 50.4 % against a
measured 54.0 %).

> `RECORDED`: **W74's exchange rate is a within-family conversion for the halt/target grid, not a
> general law of this problem.** Its use in this wave's own spec — to argue that P1's +2.11 skew
> "costs 6.3 pp" — is **weakened**: the direction is right and the magnitude is not established.
> The direct Q0-vs-Q1 comparison in §2 (−2.3 pp measured) supersedes the regression's estimate.

## 6. Per year (positive-week %, at $14.65/RT)

| arm | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|
| Q0_incumbent | 42 % | 54 % | 55 % | **57 %** | 52 % |
| Q1_flat | 38 % | **62 %** | 58 % | 53 % | **58 %** |
| Q3_selective | 38 % | 56 % | **60 %** | 55 % | 55 % |
| Q4_levered | **50 %** | 54 % | 57 % | 55 % | 55 % |
| Q5_graded | 46 % | 54 % | **64 %** | 49 % | 52 % |

No arm dominates across years. Q1_flat is best in 2023 and 2026; Q0 is best in 2025 only.

## 7. What this wave establishes

- **The layer's price is now known and it is a real trade-off, not a free gain.** −2.3 pp of
  positive weeks, +19.3 % money per unit of drawdown, and a doubled weekly skew.
- **Flat sizing is the skew floor.** Inverting the layer does not go below it.
- **W74's exchange rate is narrower than it was stated to be** and is corrected here.
- Two arms deserve a proper head-to-head rather than a footnote: **Q3_selective** (88 %/84 % on
  the owner's two leading metrics, at a money cost) and **Q4_levered** (the only arm above 0 % on
  all-three in this session).

## 8. Files
`out/skew.txt` `out/console.log` · `out/rolling.csv` `out/panel.csv` ·
code `research/weekly_edge/src/run_we_w83.py`
