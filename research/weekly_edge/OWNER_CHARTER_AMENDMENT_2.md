# OWNER CHARTER — AMENDMENT 2 (issued 2026-08-26, binding)

**Corrects AMENDMENT 1, which misread the owner.** Amendment 1's framework is withdrawn where
it conflicts with this document. Amendment 1's *withdrawal* of the every-year-positive gate
stands; what it built in place of that gate was wrong.

## 1. The misreading, stated plainly

Amendment 1 recorded the owner's position as: *"a recency-concentrated edge is admissible if
it tracks a causal regime variable."* That is not what the owner said. His correction:

> 我的意思不是说必须近两年才有。我的意思是**近两年必须要有效**。

**The recent two years are a REQUIREMENT, not a permission.** I turned a mandatory condition
into an optional allowance and then built a regime-variable framework on top of it. Nobody
asked for that framework.

## 2. The criterion, as the owner actually stated it

**(a) RECENT EFFECTIVENESS IS MANDATORY.** An arm must be effective over roughly the trailing
two years. This is a gate, and it is the only chronology gate. Report the sub-period's
sessions, weeks, events, mean and standard error — an arm that is flat or negative recently
does not qualify, however good its full-window average looks.

**(b) OLD-ERA WEAKNESS IS NOT DISQUALIFYING.** An arm that did nothing in 2006–2021, or that
was flat in 2022–2023, is not thereby rejected. Markets change. Requiring uniformity across the
measurement window is itself a fit to the measurement window.

**(c) A REGIME EXPLANATION IS VALUABLE, NOT REQUIRED.** Finding a causal variable that explains
why an edge exists now is good research and belongs in the attribution section the charter
already demands. **It is not an adoption gate and Amendment 1 was wrong to make it one.**

**(d) THE IN-SAMPLE OBJECTION SURVIVES, because it is statistical and not chronological.** If an
arm was *developed* on the same recent window that is now being used to prove it, that window is
not evidence. This is unchanged by anything above; it is the reason walk-forward and forward
reads exist.

## 3. What this reverses immediately

**W57's verdict is WITHDRAWN.** It asked "does B-MOM work pre-2022?" and answered no, then
closed the case. Under (b) that question was never a gate. What survives from W57 is a
measurement, not a verdict: no regime variable in that list explains the era split, and the
mechanically obvious one (fixed friction falling from 1.70 % to 0.28 % of the median daily
range) does not rescue the pre-2022 era. That is attribution, and under (c) it is not decisive.

**W56's +43 % returns to live-candidate status**, subject to (a) and (d):
- (a): B-MOM's trailing-two-year record must be measured explicitly. Not yet done.
- (d): 2022–2026 is B-MOM's own development sample. That objection is real and unresolved,
  and it is now the *only* live objection.

**W40 axis B is reopened.** Its stated rejection included "negative in 2024 and flat in 2023",
which (b) voids, and its recent record is the opposite of its full-window one: **+$1,946/wk in
2025 and +$846/wk in 2026**. Under (a) it is a *pass* on the chronology gate, not a fail. Its
real remaining objections are the 92nd-percentile count-matched null and its near-zero
full-window expectancy — both statistical, both testable.

## 4. The second correction — my "ceiling" claim is WITHDRAWN

The owner:

> 你怎么就硬说现在就目前根据这个回撤收益已经到顶了。从第一性原理出发我们永远可能有最优得，
> 而且目前都不一定是最优的… 永远要尝试否认自己去提升。

He is right and this is exactly the quantifier hallucination the charter exists to prevent.

| what I wrote | what the artifact supports |
|---|---|
| "IC is exhausted" | **sixteen features, each tested SINGLY, in five causal trailing-rank buckets, against PER-TRADE per-unit P&L, on the P1 object, did not exceed \|ρ\| = 0.11** |
| "the object cannot be improved from inside itself" | untested and unlicensed |
| "portfolio arithmetic is the largest lever" | the largest lever **measured so far** |

**Explicitly NOT tested, and therefore open:**
multivariate combinations of those same features · nonlinear learners · interaction terms ·
a different prediction target (portfolio-level or session-level rather than per-trade) ·
features outside the tested set · different entry/exit setups · different objects entirely ·
parameter and portfolio management as its own axis · combinations of any of the above.

**Standing instruction, restated in the owner's words:** *永远要尝试否认自己去提升* — always try
to falsify yourself in order to improve. Nothing in this campaign is assumed optimal, including
the current object, including the current framing of the question, and including any sentence
in this file.

## 5. The objective function, corrected (third owner correction, same day)

> 我也不在乎什么年 sharpe。你知道的我只在乎我们能不能 **constantly 每天每周赚钱**。

**Annualised Sharpe is demoted. It is a diagnostic, not the objective.** The objective is
CONSISTENCY OF PROFIT plus small drawdown. Every report from here leads with, in this order:

1. **% of days positive** and **% of TRADED days positive** — P1 is 27.6 % / 46.0 %, and the
   first of those is the campaign's weakest number against this objective.
2. **% of weeks positive** — P1 is 58.3 %.
3. **longest losing streak**, in trading days and in weeks.
4. **median day and median week** (P1's median day is near zero — a direct consequence of
   being flat most days).
5. **weekly dollars at a fixed max drawdown** (the W56 convention).
6. drawdown distribution: 5 deepest, mean of top 5, Ulcer, % of weeks under water.

Sharpe, eff and CVaR-efficiency are still computed — they catch things consistency metrics
miss — but they no longer decide, and no arm is rejected for Sharpe alone.

**Consequence that must be acted on, not just noted:** the charter's Pareto frontier already
names a CONSISTENCY object and this campaign has never actually built one. Every wave so far
optimised production or tail. A consistency-first object is a *different* object — it would
trade more days, accept lower per-day expectancy, and be judged on positive-day rate and
streak length. That is now a first-class research axis, not a footnote.

## 6. What does not change

Spec-first commits · decision-bar causality · B1 reproduction · circular-shift and
count-matched nulls · exposure matching in contract-minutes · scan-matched nulls · permutation
multiplicity on any bucket scan · causal re-derivation of every threshold · no data
≥ 2026-08-01 · the evidence vocabulary · negative results kept with revival conditions.
