# WE_W17 — DEEP HISTORY · REPORT

**The most important result of this campaign, and it is a FAIL.**

The frozen stack was run on 2006-01-05 → 2021-12-31 — sixteen years of NQ 1-min the campaign
had never touched. No parameter was changed. Judged on Sharpe / %positive / sign, never on
dollars (NQ traded at ~1/10 of today's level).

| object | weeks | wk mean | % pos | worst | **pooled Sharpe** | positive years | verdict |
|---|---|---|---|---|---|---|---|
| **PORT (S1q07+S4n+ASIA)** | 828 | −$5 | 44.3 % | −$30,494 | **−0.001** | 9/16 | **FAIL** |
| S4n | 827 | −$17 | 45.5 % | −$19,991 | **−0.008** | 8/16 | **FAIL** |
| S1 | 672 | +$35 | 50.7 % | −$18,086 | +0.013 | 7/16 | PARTIAL |
| ASIA | 685 | +$41 | 40.0 % | −$8,675 | +0.033 | 8/16 | PARTIAL |
| **S4n LONG-ONLY** | 792 | +$94 | 48.1 % | −$7,177 | **+0.072** | 9/16 | PARTIAL |
| PORT with long-only S4n | 818 | +$103 | 47.2 % | −$23,098 | +0.031 | 8/16 | PARTIAL |

**Our 2022–2026 numbers (portfolio Sharpe 0.28, $3,400/week) do not replicate.** The stack is
approximately zero-Sharpe across sixteen untouched years.

## The scale excuse does not hold

One could argue the 10× price-level change breaks fixed-dollar parameters (the D-gate's
C=700 / X=1600 / X2=2500). But **2021 — the year immediately before the calibration sample,
at nearly modern price levels — is the WORST year in the whole deep sample** (PORT −0.118,
−$54,186), and 2018-2021 as a block sits at zero. There is no scale alibi.

## What survives, and it is not nothing

1. **LONG-ONLY beats both-sides in BOTH samples** — deep +0.072 vs −0.008, modern 0.229 vs
   0.210. The preregistered check calls this **STRUCTURAL, not drift**. It is the only finding
   in this campaign to replicate on untouched data.
2. **The winning years are the volatile, trending ones** (2008 +0.149, 2015 +0.196,
   2020 +0.055 with long-only +0.256 and ASIA +0.159); the losing years are the quiet ones
   (2010 −0.162, 2012, 2014, 2017 for ASIA, 2021 −0.118). Combined with W08's measurement that
   ~all P&L comes from the 16.8 % of sessions that are big-range days, the honest description
   of what we own is: **a long-volatility trend harvester, not an all-weather system.**

## What this changes

- No promotion of anything. The challenger set is **withdrawn** pending W18.
- The 2022-2026 improvements (delta gate, range throttle, ASIA, wave gate) must now be
  described as *calibration-sample improvements of unknown out-of-sample value*, with the
  single exception of long-only.
- The campaign's target ("weekly profit in all conditions") cannot be met by tuning this
  family further. It needs a genuinely complementary QUIET-REGIME engine — and W11's fade
  test, which failed, was run only on the 2022-2026 volatile sample. Testing a fade sleeve
  **in the quiet deep-history years** is the correct next experiment, and it is preregistered
  as W18.
