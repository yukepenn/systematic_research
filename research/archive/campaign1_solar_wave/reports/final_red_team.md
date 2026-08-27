# Final red team — the strongest case against every finalist

_2026-08-07 · Full audit: [`research/06_red_team/RED_TEAM_WAVE1C_WAVE2.md`](../research/06_red_team/RED_TEAM_WAVE1C_WAVE2.md)
(four independent reviewers, every severe claim re-verified by the controller with independent
code) · plus the 2026-08-07 integrity audit of the reports themselves._

The campaign rule is that the agent which produced a candidate may not be its only reviewer. This
document is the consolidated case **against** the campaign's own conclusions.

## 1. What the red team actually overturned

These were my results, and the audit killed them. All were accepted without dispute.

| claim | original | after audit |
|---|---|---|
| **H-006** adaptive threshold beats fixed | PASS, ΔSharpe +0.210 | **INCONCLUSIVE.** The fixed family had been split into two half-range ensembles while adaptive got its full sweep. Scored fairly, Δ falls to **+0.087**, P(Δ ≤ 0) = 0.358; ex-2025 it is +0.046 |
| **All DSR figures** | DSR 0.832 | **WITHDRAWN.** Paired `n_trials = 255` with a variance drawn only from *surviving* cells (std 0.216 vs an honest 0.40–0.50) — an internally inconsistent (N, V) pair that inflated every figure |
| **R4 = the 8-cell plateau** | hand-drawn plateau | **REDEFINED** as all 21 tested cells. The boundary was itself an in-sample selection; the full range is better on **both** Sharpe (0.892 vs 0.773) and drawdown (−$35,669 vs −$53,689) |
| "$216,922 exposure-matched" | quoted as dollars | **WITHDRAWN.** A daily-tilt convention; minute-level reconstruction puts it near $188k. Never should have been presented as achievable |
| Two risk disclosures | absent | **ADDED.** Top 1 % of trades = 160–214 % of net; the short side has no standalone edge |

**The pattern is worth stating plainly: every single one of my headline comparative claims that the
red team examined was either wrong or overstated.** The absolute-edge claims survived; the
comparative ones did not.

## 2. The integrity audit of the reports (2026-08-07)

A second pass, on the documents rather than the research, found:

| defect | severity | resolution |
|---|---|---|
| Four of six `reports/` files were stale by a full campaign (Wave-1 era numbers presented as current) | **high** | rewritten |
| `final_pareto.csv`'s C2 row used a **skipna mean** instead of the binding strict-1/N rule — the one row not produced by `ensembles.py` | **high** | rebuilt; C2 was the rejected candidate, so no ranking changed |
| `final_pareto.csv` mixed a 1,374-session calendar with a header claiming 1,370 | medium | one stated calendar (1,424), all rows recomputed |
| Vendor-parity bar count reported as 1,436,860; true count is **2,035,869** | medium | corrected everywhere (the error *understated* the evidence) |
| `registry/tested_configs.csv` stops at Wave 1b (seq 90 of ~316); `experiments.yaml` has 2 of ~12 entries | **high** | **OPEN** — see §5 |
| `runs/<run_id>/` convention lapsed after `RE01_open_parity` | **high** | **OPEN** — see §5 |
| `hypotheses.md` still recorded H-006 as PASS with a withdrawn DSR | medium | corrected |
| Daily P&L bucketed by calendar date, not NT8 session date | low | disclosed; the published basis is ~6 % **conservative**, both now reported |

## 3. The strongest case against R5

1. **It is not separable from R4.** ΔSharpe +0.087 with P(Δ ≤ 0) = 0.358. Ex-2025 it is +0.046.
   The entire effect sits in one calendar year, and adaptive *underperforms* fixed in the
   low-volatility tercile — the opposite of its claimed mechanism. R5 is ranked first on point
   estimates plus a confirmed mechanism, not on a demonstrated advantage.
2. **It does not travel.** ES ensemble Sharpe −0.329, P(Sharpe ≤ 0) = 0.829. Under the campaign's
   own constitution (§16) a mechanism that works at one instrument's absolute scale earns a large
   overfitting penalty. That penalty is applied, not explained away.
3. **Deflation cannot certify it.** DSR 0.45–0.55 against a 0.90 bar; Harvey–Liu haircut Sharpe
   **0.000**. A defensible alternative variance pool gives 0.96 — meaning the answer is dominated
   by a judgement call, not by data. Deflation adjudicates nothing here **in either direction**,
   and that cuts against R5 as much as for it.
4. **64 % of net comes from ten days.** Remove them and $198,059 becomes $71,923.
5. **~316 configurations consumed and no clean out-of-sample window remains.** Nothing in the
   package is out-of-sample.
6. **The edge is ~3 % from a no-alpha null.** A driftless diffusion gives E[ω] = δ exactly; the
   entire campaign rests on r exceeding 1.0 by about three percent.

## 4. Where the red team failed to find a problem

Stated for balance — these were attacked and held:

- **Determinism.** 7 bit-identical canonical runs including 2 concurrent; optimizer iterations
  bit-identical to standalone.
- **The absolute edge.** Circular block bootstrap P(Sharpe ≤ 0) = 0.0020 (R5), 0.0051 (R4). This
  survived every reviewer.
- **The overshoot excess.** r > 1 at *every* threshold, t = 31 → 2.1. Independent of any strategy.
- **The recovery itself.** 2,035,869 bars, 9 configurations, zero mismatches — and the one
  unresolved regime (`V > S/2`) provably never touches a Type-1 signal.
- **Ensembles over selection.** PBO 0.48–0.90 with a negative IS→OOS slope in every family;
  walk-forward argmax earned $16,131 where the median config earned $121,373. The ensemble finding
  is the campaign's most robust result and no reviewer dented it.
- **The block-vs-iid drawdown check.** Ratio 0.987 — the iid assumption was not hiding tail risk.

## 5. Unresolved objections

Two remain open and neither has a good answer.

**The registry gap.** ~226 of ~316 configurations were never entered in
`registry/tested_configs.csv`, and the `runs/<run_id>/spec.yaml` convention lapsed after Waves 1c–3
began. Raw evidence survives — ~300 execution ledgers under `research/` — so results are
reproducible. But the campaign's own guarantee that *the spec was committed before the results were
read* is **not verifiable** for those waves. Since that guarantee is the primary defence against
post-hoc metric selection, the honest position is that Waves 1c–3 rest on my discipline rather than
on the record. A reviewer is entitled to discount them accordingly.

**No portfolio, no complementary family.** Families B–E were never built (see
[`complementary_families.md`](complementary_families.md)). The mandate's endpoint was a portfolio;
the delivered endpoint is a single family. The stop condition fired first, which is a legitimate
reason to stop but does not convert the gap into a result.

## 6. Verdict

**Do not treat this as a validated edge.** The defensible output is: an exactly recovered
indicator, a well-characterised thin edge with a confirmed mechanism, a fully open implementation,
a known dominant risk, one failed portability test, and an incomplete research programme that
stopped on its own rule.

The single most useful next action is also the cheapest: **monitor the overshoot ratio `r`
quarterly.** It requires no trading, no configurations, and no new data licence, and it is the
system's own early-warning statistic.
