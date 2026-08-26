# WE_W85 — THE GATE WAS BROKEN. FOUR VERDICTS REVERSE. · REPORT

Found by an independent 11-agent adversarial audit; **every claim below re-derived by me before
being written down.** Preregistered fix, mandatory power check run first.

> ## **The rolling gate I used to reject candidates in W78, W79, W80, W83 and W84 cannot pass an
> ## object that is strictly better than the champion in every respect.**
> ## **Four of eight rejections reverse. This is the largest error of the campaign.**

---

## 1. The defect

Every rolling verdict used three legs:

```
x1  weekly_dd = mean(weekly) × DD_TARGET / maxdd      (higher better)
x2  positive-week %                                    (higher better)
x3  dd5       = mean_top5_drawdown × DD_TARGET / maxdd (lower better)   ← DEFECTIVE
```

**x1 and x3 divide by the same window-realised maximum drawdown.** So x3 is not a drawdown
*level* — it is the shape ratio `top5/maxdd`. An object whose drawdowns are uniformly smaller has
the same ratio and earns nothing. An object handed **free money that shrinks its drawdown scores
WORSE**, because `maxdd` falls faster than `top5`.

## 2. The oracle battery — the power check that should always have existed (`FACT`)

| oracle (strictly dominant by construction) | **OLD gate ALL-THREE** | **CORRECTED** | raw max DD genuinely better |
|---|---|---|---|
| P1 **+ $200 free every session** | **0 %** | **100 %** | 100 % |
| P1 with every losing week **halved** | **20 %** | **100 %** | 100 % |
| P1 + $500 free every session | **0 %** | **100 %** | 100 % |
| P1 with losses × 0.75 | **0 %** | **100 %** | 100 % |

**A gate that scores free money at 0 % cannot reject anything.** The corrected gate — x3 = **raw**
mean top-5 drawdown at matched nominal exposure — passes all four at 100 % and still discriminates
(it rejects four of the eight real objects below).

> **New standing requirement: no gate is preregistered in this campaign again without an oracle
> battery run against it first.**

## 3. The re-adjudication (`FACT`)

At W82's measured $14.65/RT:

| object | money leg | wk+% leg | OLD dd-leg | **OLD ALL3** | NEW dd-leg | **NEW ALL3** | |
|---|---|---|---|---|---|---|---|
| **W78 pair w = 0.30** | 84 % | **100 %** | 12 % | **0 %** | **100 %** | **84 %** | **PASS ← was FAIL** |
| **W78 pair 2:1** | 84 % | **100 %** | 12 % | **0 %** | **100 %** | **84 %** | **PASS ← was FAIL** |
| **W79 clique equal** | **92 %** | 72 % | 4 % | **0 %** | **100 %** | **68 %** | **PASS ← was FAIL** |
| **W79 clique inverse-vol** | 84 % | 72 % | 4 % | **0 %** | **100 %** | **68 %** | **PASS ← was FAIL** |
| W80 X9a | 16 % | 52 % | 64 % | 0 % | 28 % | 8 % | still FAIL |
| W83 Q1 layer OFF | 4 % | 64 % | 64 % | 0 % | 60 % | 4 % | still FAIL |
| W84 Q3 score ≥ 4 | 4 % | 88 % | 84 % | 0 % | 8 % | **0 %** | still FAIL |
| W83 Q4 size 3 | 100 % | 64 % | 36 % | 24 % | 0 % | 0 % | still FAIL |

## 4. What the broken leg was hiding (`FACT`)

Raw drawdowns, full window, $14.65/RT:

| object | week + % | streak | weekly $ | **wk $ @ fixed DD** | **RAW top-5 DD** | **RAW max DD** | worst week |
|---|---|---|---|---|---|---|---|
| **P1 (champion)** | 52.6 % | **8** | **$1,152** | **$853** | **$18,458** | **$27,328** | −$7,581 |
| **pair w = 0.30** | **58.7 %** | **4** | $946 | **$852** | **$12,188** | **$22,494** | **−$6,476** |
| pair 2:1 | **59.6 %** | **4** | $924 | $818 | **$11,837** | $22,865 | −$6,472 |
| clique equal | 56.8 % | 6 | $697 | $824 | **$9,778** | **$17,130** | −$6,108 |
| **clique inverse-vol** | **57.7 %** | **5** | $650 | $832 | **$9,489** | **$15,815** | **−$5,103** |

**The pair at w = 0.30 delivers the same money at a fixed drawdown as the champion ($852 vs $853)
with +6.1 pp of positive weeks, a losing streak of 4 instead of 8, a 34 % smaller top-5 drawdown
and an 18 % smaller maximum drawdown.**

**The inverse-vol clique gives up 2.5 % of money for +5.1 pp of positive weeks, a 49 % smaller
top-5 drawdown, a 42 % smaller maximum drawdown and a worst week of −$5,103 against −$7,581.**

These are not marginal. They were rejected because my drawdown leg measured a shape ratio.

## 5. `RETRACTED UNCONDITIONALLY`

> **"Seven consecutive objects showed full-sample dominance and failed sub-period testing, always
> on the drawdown sub-metric (4–24 % of windows)."**

That was **the instrument, not the data**. The 4–24 % band was the shape ratio refusing to credit
smaller drawdowns. It is withdrawn from `STATE_OF_THE_SYSTEM.md`, from the campaign memory, and
from W80's phase ordering, which it caused.

The audit also confirmed the enumeration was wrong independently of the gate: W40, W41, W74 and
W77 have **no 24-month test at all**, so they could not have failed one.

## 6. What is NOT invalidated

- **Every null.** W78's finding that the pair's drawdown benefit is **SPECIFIC at the 98th
  percentile** stands — and now reads very differently. W79's and W84's generic results stand.
- **Every walk-forward, per-year table and full-sample panel.**
- W82's fill cost, W80's deep-history run, W73's drift decomposition, W77's arms (all ten failed
  independently of the gate).

## 7. Nothing is promoted here, and that is deliberate

A reversal produced by fixing my own error deserves **more** scrutiny, not less. Each flipped
object goes to a fresh champion-vs-challenger. Two things must be re-examined there:

1. **W78's walk-forward failed at 58 % retention with w = 0.30 chosen 0 of 12 times** — but it
   selected `w` by maximising money-at-fixed-drawdown alone. On the owner's stated ordering
   (consistency, then drawdown, then money) that objective is wrong, and the walk-forward must be
   re-run on the right one.
2. **The clique's members are individually flawed** (AXISB is 2025-only; BMOM is regime-local) and
   that has not changed.

## 8. Two further defects confirmed in the same audit, both mine

- **W76's "never-seen" window was not virgin.** `run_we_w01.py`'s own docstring: *"Dev 2022-01-02
  → 2026-05-29; **holdout 2026-05-31 → 07-31, read once at the end**"*, and
  `runs/WE_W01_SLEEVE_MAP/REPORT.md:38` calls S4/SM14 *"the best object in the library"*
  **on holdout grounds**. `summary.csv` shows the vol_period choice separating **only** there:
  vp460 and vp1380 tie on dev Sharpe (0.160/0.160) with **vp1380 ahead on dev total**
  ($303,386 vs $265,401), while on the 9 holdout weeks vp460 wins ($79,524 / 77.8 % vs
  $64,746 / 66.7 %). **The campaign uses vp460 everywhere.** W76's "nothing was ever fitted,
  selected, screened or even LOOKED AT" and "P1's first genuine forward test" are **FALSE**.
  The measurement stands; the label does not. I checked that the *data* was unsealed and never
  checked whether the *window* had been read — method rule 26 exactly.
- **W74's "unreachable at ρ ≥ 0.2 at any K" is FALSE.** `run_we_w74b.py` ran K only to 24 and
  printed `"> 24 (or never)"`. Extended: ρ = 0.2 reaches **76.2 % at K = 60** and converges to
  ~77.2 %. Correct: **≈6 at ρ = 0, ~9–10 at ρ = 0.1, ~60 at ρ = 0.2, unreachable at ρ ≥ 0.3
  (ceiling ~71.3 %).**

## 9. Files
`out/gatefix.txt` `out/console.log` · `out/power.csv` `out/readjudication.csv` ·
code `research/weekly_edge/src/run_we_w85.py`
