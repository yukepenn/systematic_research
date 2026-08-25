# WE_W05A — EXPLAIN · REPORT

Diagnostics only, on the **lag-corrected** (W03 amendment 1) candidates. No selection, no
promotion. All figures NET of $4.36/RT. `PORT` = S1 + S4.narrow6.gdl (two sleeves).

## Standing caveats that apply to every number below

1. **These years are IN-SAMPLE.** The candidates were chosen by looking at this same dev
   period. Yearly P&L here describes *the configuration we selected*, not what a frozen
   system would have earned going in blind. Only the virgin ≥ 2026-11-01 read can do that.
2. **Exposure asymmetry**: PORT can hold up to **2 NQ** (one per sleeve); his Strategy
   Analyzer records are 1 NQ (AS-9). Per unit of risk, halve PORT before comparing.
3. **Measurement asymmetry**: his figures are GROSS of commission and display-selected
   (R34); ours are net and frozen.

## R1 — yearly net (and % positive weeks)

| | 2022 | 2023 | 2024 | 2025 | 2026 (→07-31) |
|---|---|---|---|---|---|
| S1 | +$36,848 (56 %) | +$75,076 (56 %) | +$151,776 (58 %) | +$34,653 (52 %) | +$87,944 (52 %) |
| S4.narrow6.gdl | +$74,302 (56 %) | +$42,525 (63 %) | +$87,596 (60 %) | +$110,419 (63 %) | +$69,951 (55 %) |
| S4.all13.h1300.gdl | +$70,139 (52 %) | +$42,897 (58 %) | +$65,401 (58 %) | +$111,590 (65 %) | +$5,226 (45 %) |
| **PORT** | **+$111,150 (54 %)** | **+$117,601 (62 %)** | **+$239,372 (65 %)** | **+$145,072 (60 %)** | **+$157,895 (68 %)** |
| S5.vf | +$75,293 (54 %) | +$59,636 (63 %) | +$67,209 (63 %) | +$45,785 (54 %) | +$57,962 (57 %) |

Every sleeve is positive in every year. **No year is negative for any candidate** — but see
caveat 1. Note `S4.all13.h1300.gdl` collapses in 2026 (+$5,226, 45 % weeks): the tail-bar
config buys its small worst-week with a bad recent year.

## R2 — monthly (55 months pooled)

| | % positive months | mean | worst | best |
|---|---|---|---|---|
| S1 | 64 % | +$7,024 | −$31,946 | +$39,856 |
| S4.narrow6.gdl | 69 % | +$6,996 | −$21,333 | +$47,904 |
| **PORT** | **75 %** | **+$14,020** | **−$49,687** | +$81,787 |

**Answer to "每个月都在赚钱吗": NO.** 75 % of months for the best portfolio — one month in
four loses, and the worst lost $49,687.

## R3 — are the sleeves genuinely complementary? YES

Weekly-net correlations:

| | S1 | S4n.gdl | S4a.h1300.gdl | S5.vf |
|---|---|---|---|---|
| S1 | 1.00 | **0.19** | **0.06** | **0.10** |
| S4n.gdl | 0.19 | 1.00 | 0.56 | 0.38 |
| S5.vf | 0.10 | 0.38 | 0.34 | 1.00 |

S1 is near-orthogonal to everything (0.06–0.19) — different engine, different holding
horizon, different risk rule. The S4 variants correlate 0.56 with each other, as expected
(same engine): **stacking S4 variants is fake diversification; S1 + S4 is real.** This is the
quantitative justification for the portfolio, and it matches W01's P4 finding from the other
direction.

## R4 — head-to-head on his 21 displayed weeks

| | total | positive | worst week |
|---|---|---|---|
| **HIS** (gross, ≤1 NQ) | **$180,250** | 16/21 (76 %) | −$42,235 |
| PORT (net, ≤2 NQ) | $137,189 | 13/21 (62 %) | **−$26,120** |
| S4.narrow6.gdl (net, ≤1 NQ) | $18,124 | 10/21 (48 %) | −$28,985 |

**Answer to "比他多吗": on those 21 weeks, NO.** PORT earns 76 % of his gross total using up
to twice his contract exposure, and wins fewer weeks. What PORT does beat him on is the
**tail** (−$26k vs −$42k) and the disaster week itself (W13: PORT −$16,456 vs his −$42,235).
Single-sleeve at his exposure (S4n.gdl) is far behind.

His 21 weeks were an exceptional stretch for him; our same-period 2026 full-year figure
(PORT +$157,895, 68 % of weeks) is stronger than our own average — the comparison window is
favourable to both sides.

## R5 — is the money explainable? For the delta gate, YES

| | trades | net | $/trade | long | short |
|---|---|---|---|---|---|
| S4.narrow6 **ungated** | 7,759 | +$344,301 | +$44.4 | +$236,009 (3,600) | +$108,292 (4,159) |
| S4.narrow6 **+ delta gate** | 5,792 | +$384,792 | **+$66.4** | +$237,127 (2,612) | +$147,665 (3,180) |

**The gate removes 1,967 trades and ADDS $40,491.** That is the signature of a real filter,
not a curve fit: it earns by *declining* trades, keeps long P&L intact (+$1,118 on 988 fewer
longs) and improves the short book by +$39,373 on 979 fewer shorts. Mechanism as stated —
"don't fight the session's realized flow" — with the effect concentrated on the short side,
where fighting an up-flow was costing the most.

By contrast, the money of the sleeves themselves is *not* explained beyond "trend/reversal
state machines with truncated risk"; that is a description, not an explanation, and it stays
in the honest column.

## Verdict for W05

- Complementarity: **established** (R3).
- Explainability of the newest mechanism: **established** (R5).
- Weekly/monthly consistency: real but **not** "every week/every month" — 60–68 % of weeks,
  75 % of months, with −$50k months possible.
- Beating him: **not yet on his own weeks**, and not at matched exposure.
- Nothing is frozen or promoted; the arbiter remains the virgin forward read.
