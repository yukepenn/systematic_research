# ONRANGE02 — Open-vs-ON-midpoint, trade toward the nearer overnight extreme (owner-directed)

**Status: FROZEN before ANY conditional probability or P&L statistic is computed (the
ONRANGE01 diagnostic measured only unconditional break rates; the conditionals the owner asks
about are unread). Run class: BOUNDED_SELECTION. Alpha budget 2/2, wave 2026-08-20. One shot.**

Owner direction 2026-08-20: "如果开盘时在ON session middle price以下去short直到break ON low,
反之呢?这个概率还会赚钱是多少?" — distinct construction from the closed ONRANGE01 family
(entry at the open, direction from the open's position in the range, TARGET exit at the level;
not a break-triggered continuation).

## 1. Strategy (frozen)

Universe: RTH days with ≥60 ON bars, RTH open STRICTLY inside the ON range and ≠ midpoint.
Levels: ONH/ONL from 18:00 prev cal day → 09:29; mid = (ONH+ONL)/2. Substrate
`nq1m_2005_202605.parquet`; PV $20, tick 0.25, commission $4.36/RT, 1t/side slippage.

- open < mid → **SHORT at the 09:30 open** (fill open −1t); target = ONL: buy-to-cover limit,
  fill on the first bar with low < ONL at **min(bar open, ONL) +1t** (gap-through fills at
  the better open price — the ONRANGE01 execution lesson, applied). If no target by 15:58 →
  exit at 15:58 close +1t.
- open > mid → mirror LONG, target ONH, fill max(bar open, ONH) −1t; else 15:58 close −1t.
- **ARM_A (primary)**: no stop (the owner's rule as stated).
- **ARM_B (disclosure)**: stop at the OPPOSITE ON level (same fill convention), else as A.

## 2. Readouts (all frozen here; the "概率" answers)

P(hit target same day | short side) and (| long side); P(hit target BEFORE the opposite level
breaks); win rate; median time-to-target; median favorable distance (open→target, points);
P&L battery below. Disclosure splits: by side; by open's depth in the range (quartiles of
(open−ONL)/(ONH−ONL)) — descriptive only, NO cell selection.

## 3. Gates (ARM_A adjudicated; ALL AND-required)

- **G1** N ≥ 2,000.
- **G2** net > 0 AND iid CI_lo > 0 AND year-block CI_lo > 0 (B=10,000, seed=20260820).
- **G3-SPLIT** standing per-event form (both era means > 0; ≥1 era CI_lo > 0; no CI_hi < 0).
- **G7** concentration: top-1% ≤ 50% of |net|; single best/worst ≤ 25%.
- **G8** Solar losing-day ρ ≤ 0.25 (B_SYM dev ledger); level disclosure (net on Solar losing
  days) reported and, per the LIQREV lesson, a NEGATIVE level ≤ −$100k is itself disqualifying
  for any complementary-role claim regardless of ρ.
- **G9** stress 2t/side + 3× commission: G2 holds.

## 4. Decision rule (frozen)

ALL pass → red team → candidate path. ANY fail → family CLOSED one-shot (midpoint-threshold/
target-offset/exit-time re-skins ineligible) and the OHLCV pause resumes.

## 5. Honest prior

The target is the NEARER extreme, so the hit probability will be high (unconditional break
rates 60-65%; conditioning on proximity should push 70-85%) — but this is a
high-win-rate/negative-skew shape: small wins (open→nearer-edge distance, order of 10-15 pts
on a median-33.5-pt range) against occasional large hold-to-close losses when the day runs
the other way with no stop. Direction-wise it CONTINUES the overnight drift (open in lower
half ⇒ overnight drifted down ⇒ short) — adjacent priors are unfriendly (overnight drift
~zero seq-370; MOM01 null; ONRANGE01's long-only-beta finding). Prediction: hit probability
70-85% will look impressive; expectancy after $14.36 likely ≈ 0 or negative; G7/G8-level
likely killers if G2 somehow passes. FAIL more likely than PASS. Either way the owner's
question gets exact numbers.
