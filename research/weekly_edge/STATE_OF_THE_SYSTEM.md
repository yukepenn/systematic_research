# STATE OF THE SYSTEM — WEEKLY_EDGE (campaign #7), as of 2026-08-25 after 26 waves

Single reference. Everything here is measured, net of $4.36/RT, on NQ 1-minute bars,
out-of-sample within the modern regime (2022-07 → 2026-07, 205 weeks) unless stated.

## 1. What the system IS

**A selection-free, long-biased, volatility-regime-throttled Solar-ratchet trend harvester,
truncated in both directions at the session level.**

```
signal    32 Solar-ratchet configurations (4 member sets x 4 range-throttle settings
          x delta-gate on/off), LONG-ONLY, majority vote >= 50%, 1 contract
          -> no runtime parameter selection of any kind
context   range throttle: no new entry while the session's realised range through bar i-1
          is below 80% of its trailing-60-session time-of-day median   (W09, W13-audited)
          delta gate: 1-min up/down-tick cumulative delta must agree in sign  (weak, p=0.10)
risk      SESSION BOX: halt the sleeve at -$1,300 realised, stop it at +$1,000 realised
          (W22 + W26; both halves improve Sharpe AND the tail simultaneously)
sleeves   + S1 (CAND2 + D-gate, the 2023-derived wrapper, +-1)
          + short vote (same construction, mirrored) - insurance for hit-rate, not production
fills     decision at bar close, market at next bar open, flat at every session close
```

## 2. What it DELIVERS (measured, not projected)

| object | contracts | % days + | weekly | % weeks + | worst week | Sharpe |
|---|---|---|---|---|---|---|
| **E5 box** | 1 | 46.1 % | $1,060 | 59.1 % | **−$7,487** | **0.305** |
| **E5 box + S1 + short box** | ≤3 | 52.7 % | **$3,030** | **64.9 %** | −$23,374 | 0.285 |
| at his tail tolerance (−$42k) | ~2 of the pair | — | ~$4,900 | — | ≈ −$43,000 | same |

Per-year **with the session box** (W28 correction — the earlier "weak 2025 = 0.113" measured
the PRE-BOX object): 2022 0.102 · 2023 0.189 · 2024 0.376 · 2025 **0.311** · 2026 0.454 —
every year positive, and **per-trade expectancy rises monotonically $35.7 → $41.2 → $104.2 →
$160.9 → $207.4** (2026 is double his $103 gross; ~2.4× of the 5.8× is NQ's price level). The
weak year is **2022** — a bear year, structurally the worst case for a long-biased system.

## 3. What it is NOT

- **It is not a daily-profit machine.** 43–52 % of traded days are positive, the median day is
  near zero, **the best 5 % of days deliver >100 % of all profit**, and the longest losing
  streak is 9–17 trading days (W26).
- **It is not all-weather.** It earns in active-range sessions (16.8 % of sessions carry
  essentially all P&L) and stands aside in quiet ones. Three independent attempts to trade the
  quiet regime lost money (W11, W18 ×2).
- **It is not multi-model.** MODEL-RISK: every sleeve is the same Solar ratchet in different
  packaging. Non-Solar engines either lose (Donchian −0.34, genuinely orthogonal at 0.11) or
  are not orthogonal (EMA-cross 0.11–0.13 at corr 0.47–0.55). A decay of the ratchet takes
  everything at once (W25).
- **It is not multi-instrument.** The same engine loses on ES, RTY and YM (W11).
- **It is not proven outside 2022-2026.** On 2006-2021 the vote is +0.056 pooled, 8/16 positive
  years — positive but weak; the earlier fixed stack was −0.001 (W17, W21).

## 4. Versus the original trader

At **matched tail** (his displayed worst week −$42,235): ours ≈ **$4,923/week NET** across all
205 weeks against his **$8,583/week GROSS** across 21 curated, in-sample, version-churned
sheets. Efficiency per unit of tail: his 0.203 vs ours 0.117 — **1.74×**, not the 5–20× the
raw weekly figures suggest (W23).

## 5. Confidence, by evidence class

| claim | evidence |
|---|---|
| The vote beats selection and naive | out-of-sample walk-forward, W19/W20 |
| The vote is not noise | circular-shift null at the **98th percentile, p = 0.020** (W21) |
| Not a disguised selection | leave-one-subfamily-out spread 0.034 (W21) |
| Range throttle is real | own null at 95th pctile (W13) + blocked bars would have LOST $9,540 (W23) |
| Session HALT is real | own circular-shift null at the **98th percentile, p = 0.020** (W28) |
| Session TARGET | **weak, 88th percentile p = 0.120** (W27) — kept on its four-way improvement, never called proven |
| Vote hysteresis (0.6/0.4) | looked better on Sharpe and tail, **REJECTED at the 63rd percentile** (W28) |
| Mixed-model vote | **fails** — non-Solar voters cut Sharpe 0.305 → 0.23–0.24 (W27); model concentration is permanent |
| Long bias is real | replicated in four independent tests incl. the deep sample (W16/17/19/20) |
| Delta gate | weak (p = 0.10); kept on its leave-one-out cost, never described as understood |
| Everything else | see `PARKED_NOT_DEAD.md` |

## 6. Standing rules that produced these numbers
Gates carry decision-bar information only. Every gate reports its circular-shift percentile.
No runtime parameter selection. Any exposure rule that scales with a signal we already trade
is leverage, not edge (proved three times). Corrections propagate to every citing document.
