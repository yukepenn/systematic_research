# WE_W65 — RELATIVE VALUE · REPORT

Preregistered; amendment 1 extended it to three wider pairs before that ran.
**The first two-legged position ever opened in this repo — and it is closed by its own stopping
rule at phase 1, for two scripts and 50 seconds.**

---

## 1. Why it was worth doing

A repo-wide search returned **zero instances** of pairs trading, statistical arbitrage, spread
mean-reversion, cointegration, hedge ratios or market-neutral positions in any campaign. Every
two-instrument study traded NQ **outright** while the other instrument fed a signal — stated
verbatim in `runs/SMV2AB_ENGINE3_S4/REPORT.md:6-8`. W56 had written the specification for what
this campaign needs: *an engine with a real edge whose underwater curve is not P1's.* A
dollar-neutral spread is decorrelated with a directional trend follower **by construction**,
which is the half this campaign has never been able to secure.

## 2. `FACT` — the divergence IS mean-reverting, and now it is measured

Causal beta from a trailing 390-minute regression (lagged), divergence = cumulative residual
return within a session, reset at each session open. Variance ratio with a **session-block
bootstrap**, because a variance ratio on 1.5 M overlapping observations looks precise and is not.

**NQ/ES — 1,557,681 exactly-matched minutes, 1,141 sessions, causal beta median 1.156:**

| horizon | variance ratio | bootstrap 5th–95th |
|---|---|---|
| 1 min | 1.0000 | 0.9845 – 0.9864 |
| 5 min | **0.8264** | 0.761 – 0.853 |
| 15 min | **0.7776** | 0.692 – 0.818 |
| 30 min | **0.7647** | 0.671 – 0.818 |
| 60 min | **0.7608** | 0.659 – 0.822 |
| 120 min | 0.7624 | 0.669 – 0.832 |

**Variance ratios near 0.76 with bootstrap intervals entirely below 1.0.** The divergence
reverts roughly a quarter of its random-walk variance. The repo's own prior — *"at best weakly
mean-reverting standalone"* — is **confirmed and quantified** rather than asserted.

All four pairs revert: best variance ratio NQ/ES 0.761, ES/RTY 0.785, NQ/RTY 0.873, NQ/YM 0.916.

## 3. `FACT` — and the reversion is smaller than the cost of two legs

Friction recomputed per pair from each instrument's own point value and tick size (carrying NQ's
numbers across is the error W43's read 1 was VOIDed for):

| pair | commission, both legs | 2 ticks, both legs | **stress floor** |
|---|---|---|---|
| NQ/RTY, NQ/YM | $8.72 | $20.00 | $28.72 |
| NQ/ES, ES/RTY | $8.72 | $35.00 | $43.72 |

Mean subsequent reversion in dollars on a dollar-neutral position, after the divergence exceeds
a **causal trailing quantile**:

| pair | best variance ratio | best net of **commission alone** | best net of **stress** | verdict |
|---|---|---|---|---|
| **NQ/ES** | 0.7608 | **+$4.04** | −$30.96 | no |
| ES/RTY | 0.7845 | −$8.88 | −$43.88 | no |
| NQ/RTY | 0.8733 | −$12.35 | −$32.35 | no |
| NQ/YM | 0.9159 | −$12.77 | −$32.77 | no |

The single best cell across all four pairs and all 24 threshold × horizon combinations is
**NQ/ES at the 99th percentile over 120 minutes: mean reversion $12.76 on 26,317 events, against
$8.72 of pure commission.** That is **+$4.04 before a single tick of slippage**, and −$30.96
once two ticks a leg are charged. On a ~$400,000 dollar-neutral position, $12.76 is **0.003 %**.

> **NO PAIR CLEARS TWO ROUND TURNS AT STRESS FRICTION AT ANY HORIZON OR THRESHOLD.**

## 4. The result, stated as a principle

**The divergences between US index futures are genuinely mean-reverting and are arbitraged to
inside transaction costs.** That is exactly what efficient-markets reasoning predicts for two
instruments whose constituents overlap and whose spread is traded by co-located participants —
and it is now *measured on 1.5 million minutes* rather than assumed. Relative value is closed at
the minute-to-hour frequency on the instruments this repo holds.

Note what this does **not** close: a spread held overnight or for days (the architecture forbids
holding through the session close, and roll and carry would contaminate it); a pair with a
genuinely different exposure on one leg (this repo holds no bond, gold, dollar or VX futures);
or a spread traded passively, where the reversion would be compared against a much lower floor —
though the scalping lab separately measured that passive fills lose to market fills on NQ
through adverse selection.

## 5. One observation worth carrying forward

At the 120-minute horizon the **median** reversion ($21.83) exceeds the **mean** ($12.76). The
distribution is **left-skewed** — most events revert more than average and a few blow out.

That is the classic relative-value payoff, and it is the **exact opposite shape to P1**, whose
37.8 % hit rate has rare winners carrying everything. W64 established that P1's real weakness is
its skew — mean ÷ median = 3.2 — and that raising the **median** week is what the owner's
objective actually needs. **A left-skewed sleeve is the right shape for that job.** The shape is
right; the magnitude is not. Any future candidate with a left-skewed payoff should be measured
against this specification.

## 6. Files
`out/relvalue.txt` `out/relvalue2.txt` `out/varratio.csv` `out/varratio_all.csv`
`out/reversion.csv` `out/reversion_all.csv` ·
code `research/weekly_edge/src/run_we_w65.py`, `run_we_w65b.py`
