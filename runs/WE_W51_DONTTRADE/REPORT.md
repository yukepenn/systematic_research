# WE_W51 — "DO NOT BE LONG TODAY" · REPORT

Spec preregistered, amendments 1 and 2 preregistered before their own results.
Everything below is net of $4.36/RT on NQ 1-minute bars, 2022-07-01 → 2026-08-01, 1,012
sessions / 203 weeks. No data ≥ 2026-08-01 was touched.

**VERDICT: NOTHING ADOPTED.** One arm (E4) cleared the letter of its preregistered adoption
null and is still rejected, for a reason that is itself the most useful result of the wave.

---

## 1. Phase 1 — the ceiling by decision time (`FACT`, new)

W50 measured that standing aside on TREND-DOWN + RANGE sessions is worth **+4.36 pts/session**.
It never asked *when that money is still there to be saved*. A perfect oracle that knows the
session's final class can only act on P&L that has not happened yet:

| decide at (ET) | BLOCK new entries | % of the 4.36 | AUC of the causal signed-move feature |
|---|---|---|---|
| pre-session | **4.37** | 100 % | — |
| 20:01 | 4.26 | 98 % | 0.582 |
| 04:01 | 3.61 | 83 % | 0.614 |
| 08:01 | 2.82 | 65 % | 0.650 |
| 09:30 RTH open | 2.92 | 67 % | 0.678 |
| 10:00 | 1.54 | 35 % | 0.716 |
| 10:30 | 1.06 | 24 % | 0.738 |
| 11:30 | 0.32 | 7 % | 0.757 |
| 13:30 | 0.29 | 7 % | 0.769 |

The pre-session row reproduces the +4.36 target exactly — phase 1's own B1.

`INFERENCE`, and the sentence this wave exists to have produced: **the information about which
kind of day it is arrives at roughly the same rate as the opportunity to act on it disappears.**
By 10:00 ET the day is only just becoming half-readable (AUC 0.716) and 65 % of the prize is
already gone. That is not a statement about our features; it bounds *any* classifier.

## 2. Phase 2 — a-priori-signed price-location gates

Seven gates whose direction is fixed by mechanism (a long-only trend harvester should not be
long below its own reference level), plus four diagnostics whose direction is not. **No
adoptable arm beat the incumbent on both eff and MAR.** The closest, A1 (price ≥ session open),
cut max drawdown 18 % and raised MAR 16 % for 5 % less money, and its per-class ledger explains
why it is not the intended mechanism: it halves the TREND-DOWN loss (−3.05 → −1.18) and
**triples** the RANGE loss (−1.32 → −3.94), because on a range day it re-enters exactly when
price crosses back above the open.

It also raised the trade count 1,950 → 2,005: `pos = posL & allow` makes a gate an **exit rule
as well as an entry rule**. That was not the intended construction and it is corrected in §4.

## 3. The prior-session bit — `FALSIFIED` on its own preregistered terms

The strongest conditional in the phase-2 table was the prior session's sign, and its complement
was nearly empty, which is what separates a real conditional from an exposure cut: prev-DOWN
sessions carry **89.6 % of the money on 64.4 % of the exposure**; prev-UP carry 13.6 % on
35.4 %. Fixed-sign, it cut max drawdown 46 % and raised MAR 67 %.

Amendment 1 required the mechanism to be shown in the **market** before any of that was
defended, and required the sign to be re-derived **causally**, because `prev_ret` with a
mean-reversion sign is one of the quality score's five features and that sign was chosen by
W33/W34's full-sample scan on this same window.

| test | result |
|---|---|
| P(TREND-UP \| prev DOWN) vs prev UP | 23.6 % vs 18.7 %, **+4.9 pp, permutation p = 0.0635** — does not clear 0.05 |
| P(TREND-DOWN \| ·), same comparison | −0.8 pp, p = 0.781 — no effect at all |
| max drawdown, fixed sign → causal sign | $10,850 → **$20,245** = the incumbent's, exactly |
| MAR, fixed sign → causal sign | 25.26 → **13.43**, *below* the incumbent's 14.86 |
| nulls (N1 circular-shift, N2 exposure-matched count-matched) | causal versions **FAIL both** on max drawdown (25th/40th pct) and MAR (75th–83rd) |

The causal learner agreed with the full-sample sign on **87.2 %** of sessions and still lost the
entire drawdown advantage, because the drawdown the fixed-sign version dodged falls inside the
250-session warm-up where a causal learner has no opinion.

**Recorded conclusion (`FACT`): cutting the worst week is not cutting the drawdown.** The causal
versions *do* clear both nulls on worst week (98.8th/99.3rd), eff and CVaR-efficiency — they
just do not move the drawdown, because W50 already established the drawdown is an accumulation
across weeks rather than one bad session. `prev_ret` stays a **sizing** feature. Not promoted.

## 4. `FACT`, new — half the money is earned overnight

The object's 14.74 pts/session by **entry window**, never measured in 52 waves:

| entry window (ET) | pts/session | | entry window (ET) | pts/session |
|---|---|---|---|---|
| 18:00–20:00 | **+2.43** | | 09:30–10:30 | +1.39 |
| 20:00–00:00 | +1.63 | | 10:30–12:00 | **−0.06** |
| 00:00–04:00 | +2.04 | | 12:00–14:00 | **+2.97** |
| 04:00–08:00 | +1.07 | | 14:00–17:00 | +0.94 |
| 08:00–09:30 | +2.31 | | | |

**7.17 of 14.74 pts/session (49 %) is earned between 18:00 and 08:00 ET.** The best single
window is 12:00–14:00. The only dead window is 10:30–12:00. 09:30–10:30 has both the largest
TREND-UP contribution (+3.46) and the largest bad-day bill (−1.10 TREND-DOWN, −0.76 RANGE) —
the highest-variance hour of the day for this object. This opened **W53**.

## 5. E4 — the candidate that cleared its null and is still rejected

Re-run as **pure entry blockers** (the gate may not close a position it did not prevent), the
same price-location gates reverse their phase-2 verdict. E4 = *do not START a long while price
is in the lower half of the session's realised range so far*:

| | P1 incumbent | **E4** | change |
|---|---|---|---|
| pts/session | 14.86 | **15.38** | +3.5 % |
| weekly | $1,475 | $1,526 | +3.5 % |
| **exposure (contract-minutes)** | 100 % | **100.3 %** | — |
| max drawdown | $20,245 | $16,604 | −18 % |
| **mean of the 5 deepest drawdowns** | $14,266 | **$10,713** | **−25 %** |
| Ulcer index | $6,183 | $4,553 | −26 % |
| **MAR** | 14.86 | **18.75** | +26 % |
| annualised Sharpe | 2.26 | 2.38 | +5 % |
| CVaR-efficiency | 0.273 | 0.286 | +5 % |
| worst week | −$7,418 | −$7,623 | −3 % |
| trades | 1,950 | 1,779 | −9 % |

More money on the same exposure with a 25 % smaller drawdown distribution. Its per-class delta
lands where the wave aimed: **TREND-DOWN +0.76** of the +0.52 total, TREND-UP +0.20, RANGE −0.53.
In TREND-DOWN sessions it blocks 40 % of entries whose mean P&L is −$259; in TREND-UP sessions
it blocks 11 %, whose mean is +$422.

### Why it is rejected anyway

**(a) The production gain does not survive removing the sizing layer.** At a flat 1 lot:
P1 10.75 pts / MAR 10.98 versus E4 **10.29 pts / MAR 10.08**. Only the drawdown *shape*
survives (mean-top-5 $10,425 vs $12,590, Ulcer $3,916 vs $4,740). `pos_sess_range` correlates
0.66 with `dist_open` at entries, and `dist_open` is one of the score's five features with a
`+` sign, so removing low-location entries shifts the score's own trailing quantiles. A large
part of the headline is an interaction with the sizing layer, not the gate.

**(b) It fails the alignment null.** Preregistered N1 = the same mask rolled by a random offset
*within each session* — duty cycle and intra-session autocorrelation preserved, alignment with
price destroyed. E4 sits at the **38th percentile of 150 such draws on pts** (N1 mean 15.59
against E4's 15.38) and the 59th on MAR. The binding null N2 (wrong-day mask) it does clear —
96.7th on pts, 96.7th on MAR, 98.0th on mean-top-5 drawdown, 96.0th on CVaR-efficiency — which
is the letter of the adoption bar.

Amendment 2 also required *"a mechanism sentence that is not 'it traded less'"*. N1 says the
mechanism sentence cannot be **"because it is aligned with price"**, because a mask that is not
aligned with price does the same or better. Without that sentence the arm does not qualify,
regardless of N2. **Not adopted.** Filed in `PARKED_NOT_DEAD.md` with its revival condition.

**(c) The per-year delta is negative in 2 of 5 years** (2022 −2.18, 2025 −0.60; 2023 +2.47,
2024 +0.28, 2026 +2.43), and the threshold profile is a plateau on 0.4–0.5 with a cliff at 0.6
(MAR 17.14 / 18.75 / 13.22) — half a plateau, not a comfortable one.

**Correction to my own inference:** I proposed that E1's much worse worst week (−$12,525) was
caused by blocking small early losers so the −$1,300 session box never fires. Measured: the
box-halt rate goes 28.9 % → 26.4 % while its trades fall 17 %, i.e. the halt rate per traded
session barely moves. The hypothesis is `WEAK` and is not supported by this measurement.

## 6. The result that matters more than E4 (`FACT`, and the lead into W54)

The N1 null was supposed to be a floor. It is not:

> 150 randomly-rolled entry masks average **15.59 pts/session and MAR 17.80**, against the
> incumbent's 14.86 / 14.86 — on *less* exposure (92 %) and *fewer* trades (1,514 vs 1,950).
> Their mean-of-5-deepest drawdown is $12,702 against the incumbent's $14,266.

Blocking ~20 % of entries with roughly this duty cycle improves the object **whatever the mask
is aligned to**. Since a rolled mask mostly *delays* entries rather than removing the flip, and
since W42 independently measured that winners' median MAE is **0.81–0.86 ATR** (winners go
substantially against us before they work), the hypothesis this generates is:

> **The object's entries are systematically premature.** Entering k bars after the flip, or on
> the retrace, preserves the event count — so the unifying event-count law does not forbid it —
> and may capture most of what every gate in this wave was reaching for.

That is preregistered as **W54** and it is the first-priority wave.

## 7. Files
`out/donttrade.txt` `out/ceiling.csv` `out/gates.csv` `out/per_class.csv` `out/summary.csv`
`out/w51b.txt` `out/mechanism.csv` `out/tod.csv` `out/entryonly.csv` `out/causal.csv`
`out/nulls.csv` `out/w51c.txt` `out/e4_attrib.csv` `out/e4_robust.csv` `out/w51d.txt`
`out/e4_null_N1.csv` `out/e4_null_N2.csv` `out/e4_nulls_true.csv`
Code: `research/weekly_edge/src/run_we_w51.py`, `_w51b.py`, `_w51c.py`, `_w51d.py`.
