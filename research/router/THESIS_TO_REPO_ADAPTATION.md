# THESIS → REPO ADAPTATION

_Adjudicates the owner-supplied [`Regime_Router_Research_Thesis.txt`](Regime_Router_Research_Thesis.txt)
(sha256 `6c7df1a6…32638e`, 95,431 bytes, moved intact from repo root 2026-08-27) against committed
campaign-#7 evidence._

> ### The semantic rule this file exists to enforce
> **THESIS = research prior / architecture hypothesis. `CURRENT_BASELINE.md` = empirical truth.**
> The thesis is a strong, well-argued external document written **without access to this repo's
> data or its 123 waves of results.** It is not allowed to override committed falsification.
> Where it recommends something this repo has already measured, the measurement wins.

**This file does not repeat the thesis.** Read the thesis for the argument; read this for what
campaign #7 will actually do with it.

---

## 1. Adjudication

| # | thesis recommendation | disposition | why |
|---|---|---|---|
| 1 | **Do not build one master TREND/RANGE/CHOP classifier** | **ADOPT** | Independently confirmed here. W117 built an ex-post weekly class mix, it was read as a mechanism, and W118 then lost **−$405/trade** to its own **+$374** same-trigger continuation mirror. The class label described the weather. |
| 2 | **Target strategy-specific utility `E[U_i\|X]`, not `P(regime)`** | **ADOPT — this is the campaign's central object** | The single most valuable import. Everything this repo has tested routed on a *state label*; nothing has ever modelled the conditional value of the *action*. |
| 3 | **Cash / abstain is a real expert** | **ADOPT** | |
| 4 | **Soft routing beats hard gating** | **ADAPT — and this is the one genuinely untested variant** | W109/W113 killed **binary vetoes** built on real state information. A soft, uncertainty-weighted allocation on the same information has **never been run here.** See §2.1. |
| 5 | **Train-only minute-of-session normalization** | **ADOPT** | No conflict. Binding for every new intraday feature. |
| 6 | **Counterfactual at each expert's genuine eligible decision time** | **ADAPT — thesis is INSUFFICIENT** | The thesis handles cross-strategy conflict but **not intra-strategy path dependence.** P1/PCT's session box, halt latch and causal sizing make one entry's removal change later eligibility. See §2.2. |
| 7 | **One row per genuine opportunity, not per minute** | **ADOPT** | Already repo doctrine. W122 built exactly this shape (2,131 P1 entry events). |
| 8 | **Report the ex-post oracle so realizable ≪ oracle stays visible** | **ADAPT — must be expressed in the BINDING vocabulary** | `OPPORTUNITY_LANGUAGE.md` is binding and already has four levels. The directive's A/B/C/D/E is a second hierarchy. They must be **reconciled, not stacked.** See §3. |
| 9 | **Matched placebos: random router, matched activity, matched exposure, shuffled labels, time-shift** | **ADOPT — but the repo's are STRONGER and take precedence** | Thesis proposes independent-draw placebos. This repo measured that independent draws inside a correlated family inflate a best-of-K bar **1.65×** (W116b) and now requires dependence-preserving family nulls, circular shifts and effective `K = K/(1+(K−1)ρ̄)`. |
| 10 | **Right-tail retention ≥ 85–90 %** | **ADOPT** | Sharply relevant: **~20 of 348 XM trades carry 85 % of its money**; dropping its top 5 costs 28 %. Any router that smooths this is destroying the asset. |
| 11 | **Decompose every uplift (alpha / exposure / vol / tail / diversification / cost)** | **ADOPT** | |
| 12 | **HMM / HSMM / latent state as CHALLENGER only, filtered-not-smoothed, must beat raw features** | **ADOPT, deferred** | Agreed by thesis *and* directive §30. Not before the direct model exists. |
| 13 | **Hurst LOW PRIORITY; no Transformer / RL / HDP-HMM / VAE now** | **ADOPT** | |
| 14 | **BOCPD / CUSUM transition layer as a confidence discount, never an auto-reversal** | **ADOPT, deferred** | Thesis's own synthetic run gives BOCPD F1 0.251 at ~8 alarms/session — auxiliary at best. |
| 15 | **Tier-A feature: relative volume, volume acceleration, volume–price agreement** | **⚠️ FALSIFIED IN CURRENT FORM** | **W111**: 1-minute participation is **−$233/trade at the 0.0th percentile**, with three of five mechanisms *below the 5th percentile* of a volume-decile-matched null — i.e. **anti-predictive**. Admissible as a **CONTROL** column only. Never as a claimed information source. |
| 16 | **Tier-B feature: cross-market context (ES relative move, NQ–ES divergence)** | **⚠️ SPLIT — SUPPORTED at the opening auction, NULL intraday** | `XM_CONFLICT` is the campaign's one cross-market success and it lives at **09:45 only**. **W122** tested 5 primitives × 3 windows at P1's own entry events: matched Q5−Q1 **−$157** against a **$503** dependence-preserving family bar, **all four gates fail.** What existed was NQ momentum relabelled. |
| 17 | **Tier-B/C: order-flow imbalance, quote imbalance, depth, cumulative delta** | **DATA-BLOCKED** | `DATAGATE_ORDERFLOW_20260827`: order flow covers **71 of 2,131 P1 entries (3.3 %)** at an MDE of **$564/entry = 4× the mean**. Closed **by data, before a feature was written.** Owner funding decision OQ-5. |
| 18 | **Tier-D / later: Level-II queue reconstruction** | **DATA-BLOCKED + OWNER-PAUSED** | No history exists, and DOM/L2 capture is under an owner risk-control pause (2026-08-12) that must not be lifted autonomously. |
| 19 | **Tier-A/C: VWAP distance, slope, crossings, acceptance, excursion-reentry** | **ALREADY TESTED / LIMITED** | `VWAP_RECLAIM` closed (W108). But VWAP displacement **is** a real class detector (**AUC 0.621**, W109). Admissible as a **state input**, never as a standalone policy. |
| 20 | **Market internals (TICK/ADD/TRIN), VIX/VXN, Treasuries, semis basket** | **NO DATA** | `DATA_CENSUS`: market internals **NONE**. Not blocked-by-money — simply absent. |
| 21 | **Use individual listed contracts as primary truth; test roll conventions** | **LATER — separate DATA ROBUSTNESS study** | Directive §52 is explicit: do **not** change the substrate while judging router value. Every frozen expert and both parity certifications depend on `load_deep(..., extend=True)`. Mixing a new substrate into a router verdict would make the result unattributable. |
| 22 | **Final untouched 18–24-month holdout; 3–5 yr train / 6 mo val / 3 mo test** | **⚠️ IMPOSSIBLE AS WRITTEN** | The thesis assumes a luxury this repo does not have. See §2.3. |
| 23 | **Acceptance gates in Sharpe (+0.15) and % of folds** | **ADAPT — translate to the binding metric** | Campaign #7's headline is **weekly $ at fixed $20,245 max drawdown** (scale-invariant, cannot be inflated by leverage). A Sharpe gate is not this repo's currency; it will be reported, not decided on. |
| 24 | **Boosted models, LightGBM/CatBoost, depth 2–4, leaves 7–31** | **ADAPT — sample-size gated** | Fine for P1 (**2,131** decisions). **Prohibited for XM (346)**: directive §21 and W123's small-N discipline. XM gets regularized linear only. |
| 25 | **Offline teacher (PELT / smoothed HSMM) → causal student** | **LATER CHALLENGER** | Thesis rates it a diagnostic itself. Adds a teacher-error channel before the direct path is measured. |

---

## 2. The four places the thesis and this repo genuinely disagree

### 2.1 The thesis assumes state-conditioned routing is untested here. It is not — but the *form* it recommends is.

This repo has killed the causal state layer **twice**:

- **W109** — three causal states known at 11:48 separate ex-post TREND from RANGE/MIXED at
  **AUC 0.613–0.621**, at the 100th percentile of 2,000-draw permutation nulls. **The information is
  genuine.** The **binary veto** built on it removes good and bad sessions in equal proportion —
  **selectivity 0.74–1.12 across all 18 cells.**
- **W113** — the same layer fails again on the *profitable* P1/PCT baseline, not just on losing fades.
- **W112** — the only direct measurement of the causal model frontier: ridge **OOS R² −0.024**,
  directional accuracy **53.58 % — below always-long's 55.04 %**, boosted trees **47.74 %**, and the
  best fitted cell (**$229/session**) beaten by an **unfitted one-line momentum control ($190)**.

> **The standing repo conclusion is `REAL INFORMATION, NULL POLICY`.**
> The thesis's contribution is that **every one of those policies was a hard gate on a state label.**
> Soft allocation on a *calibrated action-value score* is a different object and has never been run.
> That is a legitimate open question — **and it is also exactly the kind of question that produces a
> false positive by re-testing a dead family in a new costume.** It therefore does not get a free
> pass: it must clear the matched-random-router placebo before any part of it is believed.

### 2.2 The thesis's counterfactual is not strong enough for P1/PCT.

The thesis says: evaluate the frozen rules at each eligible decision time. That is correct for a
one-shot expert. It is **wrong for P1/PCT**, and the engine proves it. `gfills`
(`research/weekly_edge/src/run_we_w98.py:59`) is a **sequential bar loop** carrying:

```
spnl     session box P&L, per-contract          →  halt −1300 / target +1000
stopped  a LATCH: once set, want is forced to 0 for the rest of the session
p, u     position and size
```

Removing one entry changes `spnl`, which changes whether `stopped` latches, which changes **which
later entries exist at all.** A second channel runs *across* sessions: `causal_score`
(`run_we_w37.py:34`) scores entry *j* from the quantiles of the prior 250 **entries** — so deleting an
entry shifts every later entry's window membership and can change its **size**.

> **A P1 trade's historical PnL is therefore NOT its causal action value**, and directive §10 is
> right where the thesis is silent. RR_W001 must build a real replay, and must certify it by
> reproducing the frozen engine **byte-identically** — the checker already exists as
> `run_we_w98.same()`.

XM is the easy case: one decision at 09:45, one exit at 15:45, no box, no latch, size 1 —
**trade-vs-cash is a clean one-shot label.**

### 2.3 There is no pristine holdout, and the thesis's validation design silently assumes one.

| pool | span | status |
|---|---|---|
| 2022-07-01 → 2026-05-30 | ~200 weeks | **DISCOVERY_CONSUMED** — 123 waves |
| 2026-05-31 → 2026-07-31 | 9 weeks | **BURNED** |
| **≥ 2026-08-01** | **~19 sessions as of today** | **VIRGIN / SEALED** |

The thesis asks for a final untouched 18–24 months. **It does not exist and cannot be manufactured.**
The virgin pool is under a month long and grows one session a day. Consequences, binding:

1. Every in-history result is **chronological / prequential / discovery-consumed validation.**
   **Never "OOS", never "out-of-sample", never "holdout".**
2. The seal is opened once, under a committed opening spec, after the architecture is frozen —
   and **not** during architecture discovery.
3. Because the virgin pool is tiny, **it can adjudicate a direction, not a magnitude.** Any plan
   that needs the seal to *estimate* an effect is not a plan.

### 2.4 The thesis's placebo suite is weaker than this repo's. The repo's wins.

Thesis: shuffled labels, time-shifted features, matched-activity random router.
Repo, already binding and each bought with a measured failure:

- **dependence-preserving family nulls** — one shared draw per session across the whole family;
  independent per-cell draws inflated a best-of-K bar **1.65×** (W116b).
- **count-matched random deletion** — W121's caps sat at the **0.0/4.0/1.0/0.0th percentile** of it.
  *Removing the same entries at random beat removing them by the rule.*
- **circular shifts** for time series; effective `K = K/(1+(K−1)ρ̄)`.
- **a class-conditional table requires its matched unconditional control in the same wave** (W111b).
- **the same-trigger continuation mirror** is mandatory for any fade/reversal (W118, `MIRROR_CONT`).

---

## 3. Vocabulary — do NOT create a second oracle hierarchy

`OPPORTUNITY_LANGUAGE.md` is **binding** and owns a four-level hierarchy over **market direction**.
The directive introduces A–E over **actions**. These are two branches of one tree, not rivals.
**Every number this campaign emits must name a cell in this table or it is not quotable.**

| branch | level | knows | this campaign's name |
|---|---|---|---|
| direction | 1 `EX_POST_PATH_ORACLE` | the whole path | *(diagnostic only — unchanged)* |
| direction | 2 `EX_POST_EXECUTION_FEASIBLE_ORACLE` | each segment's future direction | *(unchanged — `SIGN_ORACLE`)* |
| direction | 3 `CAUSAL_MODEL_FRONTIER` | only `I_t` | *(unchanged — measured once, W112, negative)* |
| direction | 4 `REAL_SYSTEM_CAPTURE` | what our objects knew | *(unchanged)* |
| **action** | **A** | the outcome of toggling **one** frozen action, full downstream replay | `LOCAL_MARGINAL_ACTION_ORACLE` |
| **action** | **B** | the best bounded set of within-session decisions | `SESSION_POLICY_ORACLE` |
| **action** | **C** | the best allocation over eligible experts + cash | `CONSTRAINED_PORTFOLIO_ORACLE` |
| **action** | **D** | only `I_t`, over actions | `CAUSAL_ACTION_MODEL_FRONTIER` |
| **action** | **E** | what an implementable frozen router knew | `REAL_ROUTER_CAPTURE` |

> ### **A, B and C are EX-POST. They are ceilings, not opportunity.**
> They stand to the action branch exactly as level 2 stands to the direction branch, and the same
> prohibition applies: **A − E is not "money we failed to collect."** The meaningful research gap is
> **D − E**. W112 already made this mistake's cost concrete on the direction branch, and
> `OPPORTUNITY_LANGUAGE.md` §"Do not quote $229" is the record of it.

---

## 4. What the thesis contributes that this repo did not have

1. **The action-value target itself.** Every campaign-#7 routing attempt predicted a *state*. None
   predicted `E[ΔU_i | X_t]`. This is the actual reframing, and it is why §3d of `CURRENT_BASELINE`
   already names "new causal information about action/signal quality" as the open gap — the thesis
   supplies the machinery for the object the repo had already identified by elimination.
2. **Separating upside from downside as parallel targets** — `E[U]`, `P(U>0)`, `q10(U)`, MAE/MFE —
   instead of collapsing to one score. Directly relevant to XM, whose loser tail W123 showed is
   **not** identifiable (AUC 0.513, p = 0.380) while its winner tail **is** (0.727, p = 0.000).
3. **Portfolio-relative value as a separate target from standalone value.** The repo already knows
   why this matters — `XM_CONFLICT` diversifies the book's *losses*, `FOLLOW_MORNING` diversifies its
   *wins*, and that difference is the entire reason one is active and the other is not. The thesis
   supplies the formalism to *model* it rather than only measure it after the fact.
4. **State alignment across refits** (Hungarian assignment on centroid + transition + duration +
   payoff distance) — a real protocol the repo would otherwise have improvised.
5. **The synthetic falsification** (Part IX): the best state classifier (ARI 0.362) was **not** the
   best router, and every causal method recovered only **3.3–7.6 %** of the ex-post oracle. That is
   an honest, load-bearing negative result and it lowers the prior on the whole latent-state branch.

## 5. What this repo knows that the thesis could not

The thesis was written without the data. These are not disagreements — they are constraints it had
no way to apply, and they are why §1 rows 15–20 exist.

- 1-minute volume is **anti-predictive** here, not merely weak.
- Intraday cross-market support is **NQ momentum wearing a label**.
- Turnover is a **symptom**, and count caps lose to random deletion.
- Order flow is **3.3 % covered** — the question is unaskable, not unanswered.
- The state layer's information is **real and its policy is null**, twice, independently.
- Market internals **do not exist** in this repo at all.

> **Net:** the thesis's Tier-A feature list is largely already measured here, and the parts of it
> that are new information are exactly the parts that are data-blocked. **The router will therefore
> be built on features the repo already holds, and its honest job is to test whether a better
> TARGET and a softer ALLOCATION extract value that a state label and a hard gate could not.**
> If the answer is no, that is a real answer and it redirects the program to new-information
> discovery — which directive §45 explicitly authorizes without asking.

---

## 6. Disposition summary

| disposition | count | rows |
|---|---|---|
| **ADOPT** | 11 | 1, 2, 3, 5, 7, 9, 10, 11, 12, 13, 14 |
| **ADAPT** | 6 | 4, 6, 8, 22, 23, 24 |
| **ALREADY TESTED / LIMITED** | 2 | 16 *(split)*, 19 |
| **FALSIFIED IN CURRENT FORM** | 1 | 15 |
| **DATA-BLOCKED / NO DATA** | 3 | 17, 18, 20 |
| **LATER CHALLENGER** | 2 | 21, 25 |

**Nothing in the thesis changes any committed result, status or evidence label.**
Current truth remains [`CURRENT_BASELINE.md`](../weekly_edge/CURRENT_BASELINE.md);
execution truth remains [`EXECUTION_MANIFEST.md`](../operational/EXECUTION_MANIFEST.md).
