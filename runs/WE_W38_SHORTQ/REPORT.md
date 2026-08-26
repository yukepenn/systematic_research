# WE_W38 — SHORT-SIDE QUALITY · REPORT

Spec `307b818` + amendment 1 (arm S5, appended after read 1, before S5 was run).
**B1 PASS**: the long P2 object reproduced at 13.50 pts/session, Sharpe 0.291, data-derived
cut 23 bars — identical to W37. Fill layer cross-checked: `sfills` is byte-identical to
`fills_daily` on the short base.
SEL = 2022-07 → 2024-07 (screen, signs, hour set). EVAL = 2024-07 → 2026-08 (every quoted
number). Net $4.36/RT; stress line $14.36/RT.

---

## 1. Q1 — can short flips be graded? **FALSIFIED as posed** (`FALSIFIED`)

The SEL screen ran 16 candidates × 2 signs on 1,298 short entries and **admitted none**
(max |t| = 1.48, `prev_range_rel` sign −1). K = 0, so arm S2 collapsed to the base by
construction, exactly as the spec specified.

Amendment 1 then removed the per-feature significance gate — because the LONG score has never
had an individually significant feature either; it works by combining five weak ones. Arm S5
took the top five SEL features at their SEL-chosen signs:

| feature | sign | SEL t | SEL effect | halves |
|---|---|---|---|---|
| prev_range_rel | −1 | 1.48 | +$79.79/trade | +97.86 / +61.22 |
| dist_open | **+1** | 1.34 | +$77.05 | +47.69 / +104.37 |
| mom60 | −1 | 1.13 | +$66.38 | +110.87 / +22.55 |
| delta_mag | +1 | 1.10 | +$60.38 | +48.12 / +71.83 |
| upvol_share | −1 | 1.10 | +$54.95 | +176.09 / −65.23 |

**S5 fails the EVAL gate.** It buys production with tail, which is the signature of leverage,
not of a ranking:

| arm | pts/session | $/trade | worst week | CVaR5 | Sharpe | wk÷\|worst\| |
|---|---|---|---|---|---|---|
| S0 base short | 6.49 | 69.5 | −$8,269 | −$6,410 | 0.153 | **0.079** |
| S1 mirrored long score | 6.89 | 81.8 | −$11,892 | — | 0.129 | 0.059 |
| S5 combined short score | 8.22 | 95.8 | −$12,520 | −$8,199 | 0.151 | **0.066** |
| S6 = S5 + hour block | 10.09 | 117.1 | −$12,232 | −$8,303 | 0.189 | 0.083 |

The overfit signature is explicit in the split: on SEL, S5 *improves* efficiency 0.081 → 0.104;
on EVAL it *degrades* it 0.079 → 0.066. The SEL-chosen signs do not transfer.

**Power** (so the negative is informative, not merely empty): the screen resolves per-trade
effects of ≈$110 at t = 2 on 1,298 entries. The long score separates by **$600+ per trade**
(score ≥ 3 earns $619–729 while score 0 loses money). An effect of the long side's size would
have been found easily. `SUPPORTED`: short flips do not carry a comparably gradeable
pre-entry signal in this feature universe.

### The one mechanistic reading worth keeping (`INFERENCE`, below significance)
The SEL signs are **anti-mirror on the two features that matter most**: shorts do better far
**ABOVE** the session open (+1) and far **ABOVE** VWAP (+1), where the mirrored long score uses
−1 on both. So the mirror score was sizing up precisely the entries SEL says are worst — a
mechanism for why S1 widened the worst week from −$8,269 to −$11,892. If the short side has
anything, it is a **fade-extension** problem, not a mirrored-trend problem. This is a
hypothesis for W39's better-powered screen, not a result.

## 2. Q2 — is it a regime/hour problem instead? **NOT EVIDENCE** (`FALSIFIED`)

The SEL-derived block (06, 10, 15, 18, 20, 21 ET) lifted EVAL production 6.49 → 8.25
pts/session with a slightly better worst week — and then failed its binding null at the
**65th percentile, p = 0.350** (null mean 0.087 vs the real 0.102; p95 0.132). Circularly
shifting the block schedule to arbitrary hours produces the same lift on average.
**What the hour block does is reduce exposure, not select hours.** Demoted per the standing
rule, regardless of how the table looked.

## 3. The result nobody asked for, and the one that matters (`REPRODUCED` on both halves)

At **matched exposure**, adding the short sleeve to the long object is a bad trade under the
owner's objective ordering:

| EVAL object | avg contracts | pts/session | weekly | wk + % | day + % | worst week | CVaR5 | Sharpe | wk÷\|worst\| |
|---|---|---|---|---|---|---|---|---|---|
| long P2 ×1 | 1.11 | 20.22 | $2,026 | 61.6 % | **52.9 %** | −$5,818 | −$5,025 | **0.350** | **0.348** |
| **long P2 ×2** | 2.22 | **40.44** | **$4,052** | 61.6 % | 52.9 % | −$11,636 | −$10,049 | **0.350** | **0.348** |
| P2 ×1 + S0 short ×1 | 1.07 (×2 sleeves) | 26.71 | $2,650 | **66.0 %** | 49.4 % | −$12,062 | −$9,850 | 0.320 | 0.220 |
| P2 ×1 + S5 short ×1 | 1.16 (×2 sleeves) | 28.44 | $2,821 | 66.0 % | 49.7 % | −$13,483 | −$11,030 | 0.298 | 0.209 |

Efficiency and Sharpe are exposure-invariant, so `P2 ×2` and `P2 ×1` share them by
construction — that is the point: **running the long object larger produces more money at the
same tail than adding the short sleeve does.** At ≈2.2 contracts the long-only object makes
$4,052/week against −$11,636; the long+short pair at the same exposure makes $2,650–2,821
against −$12,062…−$13,483.

The short sleeve buys **+4.4 pp of weekly positive rate** (61.6 → 66.0 %) and costs **37 % of
profit-per-unit-of-tail** (0.348 → 0.220) — and it *lowers* the daily positive rate
(52.9 → 49.4 %). It replicates on the full window too (long-only 0.232 vs combined 0.098–0.102),
so this is not an EVAL artifact.

**The description "the short sleeve is insurance" is withdrawn.** Insurance reduces the tail;
this widens it. It is a *consistency* purchase, priced in production.

## 4. Consequences (charter §3 Pareto frontier)

- **PRODUCTION object** and **RISK-EFFICIENT object**: long-only, scaled by contracts.
  This is now the recommended shape for the owner's stated ordering.
- **CONSISTENCY object**: keep long + short, and quote its real price (−37 % efficiency).
- The **long-only** prior is **not** overturned — but its status is refined: the four earlier
  replications compared per-trade rates; this wave shows the portfolio-level reason, which is
  that long and short drawdowns co-occur rather than offset.
- The **"sizing on new information is edge"** law is narrowed by measurement to
  **"the score grades LONG flips"**. On the short side the same construction behaves like
  leverage. That narrowing is the honest reading and is now recorded in PRINCIPLES.

## 5. Caveat that must travel with these numbers

EVAL is the **stronger half for the long object** (20.22 pts/session vs 13.50 full-window;
SEL is the weak half). EVAL-only figures for the long object flatter it. The *comparisons*
above are within-window and therefore unaffected, but the level is not the campaign headline —
the campaign headline remains the full-window causal figure of 13.50–14.72 pts/session.

## 6. What is now queued
W39 (feature discovery) re-screens the short side with the same protocol at higher power and
tests the fade-extension hypothesis explicitly; W40 (independent second model) is the wave the
tail arithmetic above actually argues for — diversification that *lowers* the tail has still
not been found, and adding correlated exposure is not it.
