# NQ RESEARCH PLAYBOOK — how the live NQ system was actually discovered

**Cross-asset Wave 0 deliverable, 2026-09-06.** Reconstructed from the repository (run reports,
`CURRENT_BASELINE.md`, `FROZEN_INCUMBENT_20260827.md`, `FAILURE_MEMORY.md`, `THE_STRATEGY.md`,
`PRINCIPLES.md`, `research_sdk/`), not from memory.

> **This document is the transferable asset. The strategy `P1/PCT` is NOT.**
> A per-market pod does not port P1. It reruns the *process* below on its own instrument and lets
> that market grow its own engine. Every claim here cites the run that bought it, so a pod can see
> the shape of the evidence it must reproduce — not the parameter values it should copy.

Companion state docs (do not duplicate them here): `CAMPAIGN_STATE.md` (lanes/waves),
`FUTURES_ALPHA_MAP.md` (per-market results), `MECHANISM_TRANSFER_MATRIX.md` (universal vs native).

---

## 1. What actually produced NQ alpha

The live object is `P1/PCT`: a **13-member Solar volatility-ratchet ensemble → 32-config majority
vote → OR-gated with a B-MOM opening-momentum channel → long-only → range-throttle + delta gate →
causal-quality sizing → per-contract session box → flat at every session close**. Its research
figures: raw $1,394/wk, **$1,230/wk at a fixed $20,245 max drawdown**, 56.3 % positive weeks, maxDD
$22,931, t 4.16 (`runs/WE_W103_CONSOLIDATE/`).

### 1a. Mechanisms that MATERIALLY contributed (each with the run that established it)

| component | what it is | why it pays | establishing evidence |
|---|---|---|---|
| **Flip-event capture** (the core) | a ratchet flips direction when price retraces `S = clamp(VolMult·σ, 40, 1200 ticks)` from the leg extreme | the edge is in the **flip EVENT, not the trend STATE** | `WE_W31`: holding long *because the leg is up* earns 0.0025 pts/bar; holding *because the ratchet just flipped* earns 0.0603 — **24×**. `WE_W25`: a Donchian breakout on the same instrument is **−0.34 Sharpe**. This one fact closes every "hold longer / re-enter sooner" idea. |
| **Selection-free majority vote** | 32 configs (`4 member-sets × 4 throttles × delta-gate on/off`), take the majority | selecting the best config each quarter is noise; aggregating a near-exchangeable family is not | `WE_W19`: quarterly config selection churns **88 %** of picks and beats doing nothing by only +0.021 Sharpe. `WE_W20`: the vote beats the selector and naive at the **98th percentile of its own circular-shift null (p=0.020)**, robust to dropping any subfamily. |
| **Long-only** | `p == −1` on 0.00 % of bars | shorts earn ~⅓ the per-trade rate of longs on every sleeve | replicated **four independent times**: `WE_W16` (side split), `WE_W17` (the *only* finding to replicate on 2006–2021), `WE_W19` (hindsight-best config is long-only), `WE_W20` (long-only vote > both-sides). |
| **Session-level risk box** (−$1,300 halt / +$1,000 target) | halt/target the whole sleeve for the session on realised session P&L | losses accumulate **within** a session, not in single trades, so truncate the *accumulation process* | `WE_W02`: a 65-pt per-trade cap touches 142 of 13,301 trades and leaves the worst week unchanged. `WE_W28`: the halt is at the **98th percentile of its null**, halves the worst week *and* raises Sharpe. `WE_W48`: exact accounting shows the tail cannot be cut at trade level (value asymmetry beats count asymmetry). `RR_W005`: **every uniform relaxation is 16–41 % worse at fixed DD** and raises exposure 11–26 %. |
| **Per-contract box denomination (`PCT`)** — the single largest headline mover | denominate the box per contract, not per position | a dollar stop on a variable-size position halts a 2-lot at **half** the adverse point move of a 1-lot (55.68 pts size-1 vs 37.18 size-2) — a **unit mis-specification, not a tuning knob** | `WE_W98_BOXDENOM`: $885 → **$1,231/wk (+39.0 %)**, maxDD $26,388 → $22,931, t 3.58 → 4.16. The controls are the result: a *uniformly* looser box is worth +$6/wk (p=0.940); the size-conditional fix keeps +39.6 %. |
| **Causal quality sizing** | score 5 causal features against **trailing-250-entry** quantiles; `size=2` when `score≥3` (~20 % of entries) | grades the **event**; sizes up the trades that will have a **bigger excursion** (not a higher hit rate) | `WE_W42`: score forecasts MFE (1.3→5.5 ATR), win rate flat ~37 % across scores — that is why **sizing works and filtering destroys production** (`WE_W34`). `WE_W39`: beats a count-matched random-sizing control (100th pct on efficiency) and a random-5-feature control. `WE_W36`: 21 % of trades deliver 79 % of profit. |
| **B-MOM OR-gate** | opening RTH-breakout momentum term, OR-combined into the tilt | a second event generator, mildly decoupled from the ratchet inside drawdowns | `PRINCIPLES.md` / `WE_W56-W57`: underwater-curve correlation with P1 is **−0.171** (the number that makes a sleeve additive), not the weekly correlation. |
| **XM_CONFLICT** (the diversifier that doubled the book) | take NQ's opening drive **only on the ~34 % of sessions where the ES/RTY/YM composite moves the other way**; fill 09:46, hold to 15:45 | the idiosyncratic, tech-specific move (NQ moving *alone*) is the one with follow-through; when the broad index confirms, the move is already priced | `WE_W101_DIRECTION`: $685/trade, 57.77 % hit, **99.6th percentile** of a rate-matched subsample null, weekly ρ with P1 **−0.005**. `WE_W110_XMDIVERSE`: loss-diversifies P1 (ρ∣P1<0 = −0.165 at the 5.2nd pct; joint maxDD $11,489). |

### 1b. Looked promising but DIED (do not re-run these on NQ; test them fresh on a new market)

- **Skew / trailing exits** ("let winners run") — `WE_W01` F2, `WE_W42`: every variant destroys $/trade; stops are structurally incompatible with a low-hit-rate high-payoff object (winners' median MAE is 0.86 ATR, so any stop winners endure cuts the winners).
- **Pyramiding / range-ratio / vote-fraction sizing** — `WE_W06/W10/W22`: all scale with information the object *already trades on*; that is leverage, not edge.
- **Reversal / fade family (7 geometries)** — `WE_W108/W109/W118`; `G2_F2_SWEEP01`: the *momentum mirror* at the same trigger bars earns +$374 while the fade earns −$405. The fades were on the wrong side of a live momentum effect.
- **Turnover as a causal lever** — `WE_W121`: entry-count caps sit at the **0.0th percentile** of a count-matched random-halt placebo (removing entries *at random* does better).
- **Cross-market intraday support / 1-min participation** — `WE_W122` (matched Q5−Q1 −$157 vs a $503 family bar); `WE_W111` (anti-predictive).
- **The short sleeve as insurance / a second independent model** — `WE_W38/W61-W63`: best-decoupled candidate in the repo (daily ρ −0.003) but currently −10.62 pts/session; you cannot carry a hedge costing 65 % of weekly income.

### 1c. Diagnostics that were especially informative — see §4.

---

## 2. The productive research SEQUENCE

This is the order that actually worked on NQ. Each step names the concrete NQ example and the
**decision the step produced**. A new-market pod runs the same ladder.

1. **DESCRIPTIVE — map what you have and find the binding constraint.**
   `WE_W01_SLEEVE_MAP` measured every object you already own on one frozen window (dev + a small
   read-once holdout) at base *and* stress cost. Output: "the binding constraint of this whole
   library is the **left tail**" and "our own shipped product ported to 1-min is the best object we
   own." A market pod's Wave-1 autopsy is this step — descriptive science on **instrument-native
   sessions**, never NQ's 09:30–16:00 copied over.

2. **MECHANISM ISOLATION — ask *where does the money come from* before building anything.**
   `WE_W25` (ratchet beats breakout) and `WE_W31` (flip-event 24× trend-state) isolated the *actual*
   source of edge. This is the highest-leverage step: it closed an entire class of proposals
   ("hold longer") in one measurement and told the campaign what to protect.

3. **SELECTION → AGGREGATION — replace picking with combining.**
   `WE_W19` proved selection is noise (88 % churn); `WE_W20` replaced it with a vote that performs no
   runtime selection and is therefore immune to the W19 failure. Rule learned (`W59` boundary):
   aggregation helps when members are **near-exchangeable estimates of the same quantity** and
   dilutes when they are candidates for *different* quantities (`W39`: aggregating 42 features lost).

4. **CONDITIONAL EXPECTANCY — build simple context rules, each with its own null.**
   Range throttle (`WE_W13`, 95th pct of its null; `W23` shows the blocked bars would have lost
   $9,540), delta gate (weak, +0.041 Sharpe leave-one-out, kept and *never described as understood*),
   halt/target (`W27/W28`). Each context rule is a single preregistered test against a
   dependence-preserving null — not a grid search.

5. **SIMPLE RULE, DERIVED NOT CHOSEN — kill the free parameter.**
   The quality layer's `k=3` is "a majority of five", not a grid pick (`WE_W36`: choosing k from a
   grid churned 67 % and failed walk-forward). The cut horizon is the data's own trailing-median
   hold (23 bars). Deriving a threshold removes the churn a fitted one creates.

6. **NEIGHBORHOOD — map the surface, prefer a monotone response to an argmax.**
   `RR_W005` (box relaxations, monotone 16–41 % worse), `W59` (216 outer cells, incumbent ranks 4th
   on money-per-DD and 178th on the DD distribution — it *maximised one quantity*). A monotone
   response over 4–6 levels is far stronger than the best cell of 216.

7. **PREDICTOR BATTERY → ENGINE — find a new information source, then make it survive becoming an
   object.** `WE_W99` ranked the unmonetized session segments; `WE_W101` ran a 9-predictor × 3-time
   battery and found `XM_CONFLICT` as a *forecast* at the 99.6th percentile; `WE_W102` rebuilt it as
   an actual engine under the campaign's own conventions; `WE_W110` certified its diversification.
   **A forecast that survives becoming an engine is worth something; most do not.**

8. **COMBINATION — print the correlation matrix FIRST, weight parameter-free, disclose the
   selection.** `WE_W103_CONSOLIDATE`: the correlation matrix went at the top ("this is not five
   engines — it is roughly three information sources"); inverse-vol equal-risk weighting has no free
   parameter, so it was preregistered; `P1+XM` was a **best-of-six** pick and said so; an independent
   integer grid converged on the same "drop the pair". The one number that made it all work was
   **ρ(P1, XM_CONFLICT)=0.081**.

9. **PARITY / EXECUTION — validate the implementation against the research object, independently.**
   `WE_W44` (first independent NT8 check — every prior B1 check validated new code *against* the
   port, never the port); `WE_W52` (component-level parity, **99.985 %** decision agreement); MX01
   (MNQ port, decision-identical by sha256 over 61,600 bars). See §5.

10. **POST-HOC ACTION-VALUE — measure what the object's decisions are actually worth.**
    `RR_W001` (counterfactual replay: 59 % of individual decisions have *negative* marginal value;
    a minority of large positives carries it), `RR_W002A`/`RR_W004` (current information cannot
    separate action quality — a clean NULL), `RR_W006` (the coverage gap is 0.38 %, not "turnover").

---

## 3. What wasted time — skip these on a new market (or run once, cheaply, then stop)

The graveyard is half the playbook. A cross-asset pod should **not** re-derive these the slow way.

| dead approach | how it died | run(s) |
|---|---|---|
| **Volatility seasonality / diurnal RV forecasting** | collinear by construction — deseasonalizing over a fixed window barely reweights the raw sum (VIF 92.86, corr 0.9946); "NOT-IDENTIFIED (DEFECT)" | `G2_F11_MC54LEG2` |
| **NQ engine ported to ES/RTY/YM** | re-derived properly (clamp/box as each instrument's own σ/range) it still fails frictions: ES +$92/wk, RTY −$87, YM −$9 on 2,000 trades. "NQ-specific" is *supported*, not assumed | `WE_W43` |
| **ATR / entropy / path-organization representations** | closed; EVENTTIME closed | `WE_W114`+; `MECHANISM_TRANSFER_MATRIX` row |
| **Meta-labeling / sizing P1 on existing surfaces** | blocked-as-rescue of RR_W002A's NULL — no *new* surface, no test | `FAILURE_MEMORY` MC-35 ruling |
| **Fade / mean-reversion graveyard (7 geometries)** | mirror of a live momentum effect; continuation wins at the same bars | `WE_W108/W118`, `G2_F2_SWEEP01` |
| **Cross-market intraday state (ES↔NQ, ZB→NQ)** | ESNQ −$503/session; ZB makes the NQ RV forecast *worse* (−4.36 % QLIKE) — retires the last "new raw surface" flag | `WE_W122`, `G2_F13_MC57_ZBSTATE` |
| **Standalone cross-market engines** | **0-for-15**; only the *conditional* form (XM_CONFLICT) ever cleared a family-wise null | `WE_W101` §5.7 |
| **Vol-state as a sizing/growth timer** | tail-only benefit, below its own null; "throttle folklore −0.24 logW" | `G2_F3_VOLSIZE01` |
| **ORB / breakout baseline as a promotable object** | t 0.21, loses to its always-long control, 2025 carries all, deep-era sign-flips | `G2_F1_ORB01` |
| **Rare-event classes (TICK capitulation, macro-day means, overnight-hold-into-NFP/CPI)** | regime-collapse (events 44→2/yr) or absent premium (−$67/night, negative gross); calendar-bound, **no model or money moves an N-bound gate** | `G2_F1_TICK01`, `G2_F10_MC50` |
| **Day-of-week / calendar day-types / COT terciles / XSMOM / first-half-hour→last** | NULL at family bar (GENESIS I) — dead external effects with no decay story | `GENESIS_H2/H3/H4B/H7` |
| **Selection at every scale** (quarterly config, 216-cell, constrained) | 2.0th–18.7th percentile of random choice | `WE_W19/W59/W60` |
| **Trade-level stops / trailing / per-trade caps** | value asymmetry beats count asymmetry; the tail is a session-accumulation phenomenon | `WE_W48`, `WE_W02` |

**Meta-lesson for the map:** three times "we don't have X" turned out to mean "this repo hasn't
fetched X" (order flow, `$TICK` history, MNQ ticks). Before declaring a data class absent, verify.

---

## 4. The diagnostics that were especially informative

These specific instruments repeatedly told the truth when a naive read would have lied. **Port the
diagnostic, not just the strategy.**

1. **The fixed-DD random-thinning placebo (T2 / `research_sdk/eval_battery.py`).** Max drawdown is an
   *order statistic of the path*; deleting trades side-blind shrinks it faster than it shrinks
   return, manufacturing income from nothing. On M_11 an oracle "drop the worst 10 %" reads **12.7×
   native on fixed-DD, 21.8× on CDaR, but only 2.2–2.5× on weekly-vol**. The module makes a fixed-DD
   figure *raise `PlaceboRequired`* unless its placebo was run. **Lead with weekly-vol; never quote
   fixed-DD or CDaR without its rate-matched placebo.**

2. **Circular-shift / dependence-preserving nulls.** Every headline in the campaign faced a null that
   preserves both marginals and autocorrelation and destroys only the alignment (`WE_W20`, `WE_W110`
   §2 against 212 shifts). Effective `K = K/(1+(K−1)ρ̄)` for correlated families; one shared draw per
   session. Independent draws inside a correlated family set the bar far too high.

3. **Count-matched / rate-matched controls for any SIZING or SELECTION claim (`WE_W39`).** N1
   (alignment) and N2 (count-matched) are **not interchangeable**: the short continuous-size arm
   passed the circular-shift null at the 100th pct and *failed* count-matched random sizing at the
   69th. Alignment nulls cannot separate "sized the right trades" from "sized some trades." A
   selection claim needs the placebo where the *same number* of trades is removed at random.

4. **Class-conditional tables require their matched unconditional control in the same wave
   (`WE_W111b`).** The fade "signature" was definitional — an unconditional fade reproduced it
   exactly. Binding rule since. (Cross-asset corollary: an `XM_CONFLICT`-style conditional needs its
   unconditional `DRIVE` control, as in `WE_W101` §4.)

5. **Component-level parity ledgers (`WE_W52`).** Exporting a per-bar ledger of the *eight components*
   (nMem, throttle, delta, tilt, bmom, the four targets) localised a phase bug in **two** iterations;
   a trade/P&L comparison would only have said "close but not equal." **Compare decision series
   before dollars; every parity check exports components.** Parity bands (`W52`): ≥99 % decision
   agreement + trade counts within 2 % = VALIDATED.

6. **The residual-error / capture ledger (`WE_W103` §5, `RR_W006`).** Measuring `CEILING − CAPTURE`
   per session segment (against the correct break-even direction bar, ~50.5 %) told the campaign it
   monetizes **0.2 %–5.1 %** of a large, rising opportunity — and where the biggest holes are — while
   also killing the "turnover is the gap" story (the true coverage gap is 0.38 %).

7. **The action-value counterfactual replay (`RR_W001`) and its information null (`RR_W002A`).**
   Replaying the frozen engine to get `E[ΔU]` at every decision (not the trade's own P&L) revealed
   that 59 % of decisions are negative-marginal and that **current information cannot predict action
   value at all** — a clean, refit-inside-every-shift NULL that stopped a whole router branch.

8. **MDE-before-looking / power-first discipline (`WE_W57`, `DATAGATE_*`).** Compute the minimum
   detectable effect *before* opening a window. Event-response was **CLOSED-BY-DATA** at an MDE of
   9.8× the bar (~96× the effective N needed = ~220 years of calendar) before a feature was written.
   "A number with no information content is worse than no number, because it gets quoted."

9. **The semantic gate (CLAUDE.md §4, the CAP01 scar).** When a headline is a **probability**, one
   gate must state in words what event it is over and a second must compute that event a *different
   way*. CAP01 passed all four gates and still published 66 % where the truth was 6.5 % — every gate
   checked the arithmetic, none checked what the output *meant*. **A gate that checks arithmetic
   cannot catch a mislabelled statistic.**

10. **Built-in identity gates (`WE_W43` §4).** Design every cross-context wave so one arm *must*
    reproduce a known result exactly, and abort the run if it does not. This caught a fill-layer
    direction/size conflation that had inflated the NQ arm.

---

## 5. Governance / execution lessons (stated as transferable rules)

- **Spec first, always.** Every run gets `runs/<RUN_ID>/spec.yaml` committed *before* results exist,
  enforced by `research_sdk/prereg_guard.py` (the spec commit must be a strict git ancestor of the
  results commit). Never overwrite a run directory. ENGINEERING_ONLY / ZERO_ALPHA_BUDGET runs may
  bypass; everything alpha-bearing must pass.
- **Decide the falsifier in advance and code every clause of it.** Print a GATE / SPEC / OBSERVED /
  PASS-FAIL table *from the program*, never assembled by hand. A gate that fails is recorded failed;
  never redefine the population after seeing the result.
- **One hash-chained ledger; report all searches, not just winners; family-wise correction across
  the whole search** (including across instruments in cross-asset). Count failed searches. A
  best-of-N pick must disclose N and clear a best-of-N null (`WE_W101`, `WE_W103`).
- **Every metric carries an evidence-status tag**: FORWARD / PRE-FROZEN / DISCOVERY_CONSUMED /
  DIRECTLY_BURNED / LEGACY_DIAGNOSTIC. A/B are DISCOVERY_CONSUMED — mined for 123 waves; only sealed
  forward data is a clean test now.
- **Data seals are sacred.** ≥2026-08-01 VIRGIN; 2026-05-31→07-31 BURNED. Never tune on locked-forward
  data. Free-in-dollars ≠ free-in-governance (the "141 extractable sessions" *are* the frozen blind
  pool). Boundary math is `research_sdk/session_boundary.py` — DST resolved by `zoneinfo`, never a
  remembered manual offset (a hand-picked offset once caused a one-hour error, saved only by the
  weekend gap).
- **Cost carries a BASIS and EVIDENCE tag** (`research_sdk/cost_model.py`): COMMISSION_ONLY /
  SPREAD_ONLY / ALL_IN and MEASURED / MODELLED / BOUND / ASSUMED. A spread figure is never "all-in"
  (that one word understated NQ friction ~$59/wk). A research headline (commission + modelled spread)
  and an NT8 net (template + zero slippage) are **different quantities**. Every candidate carries an
  optimistic/base/conservative/stress cost band; one that dies at +1 tick is fragile.
- **Never let leverage, sizing, or a reduced risk denominator masquerade as information alpha.**
  Classify every improvement: NEW INFORMATION / MECHANISM-POLICY / REGIME ROUTING / DIVERSIFICATION /
  RISK SPECIFICATION / EXECUTION / LEVERAGE / SELECTION LUCK.
- **Old-regime failure is a RISK CLASSIFICATION, not a promotion veto** (post-W115). Recent
  effectiveness is mandatory; old-era weakness is disqualifying only as a label (`REGIME_LOCAL`), and
  it must state *why* (W98: a $1,300 box was 84 % of a 2006–2021 session range, 19 % now).
- **Parity discipline.** Compare decisions before dollars; never tune until P&L matches. Rename a
  class on every functional iteration (`_v2`, `_v3`) because NT8 may resolve a stale type — but
  **never rename a parity-certified class**. Verify by resolving the class, not by trusting a compile
  flag. EXECUTABLE, PARITY-CERTIFIED and LIVE-ENABLED are three separate statuses.
- **Roll science is a first-class cost.** The roll fail-safe's ~9-day blackout holds **19.7 % of net
  (~$437/wk)** — more than commission + spread + latency combined (`GENESIS_III_VERDICT`). Audit
  roll/back-adjustment on every candidate: additively back-adjusted series make cross-era *percent*
  thresholds invalid (`G2_F3_DELEV01` substrate trap). A candidate resting on a roll artifact is
  invalid.
- **The ghost-position class** (operational, but transferable): a strategy exit can open a naked
  position because NT8 tells the strategy what the *instance* did, not what the *account holds*; any
  restart holding a position guarantees a reconcile-break while every health surface reads green.
  Detection-only is provable; enforcement needs a dedicated account. Relevant to any future
  live deployment on a new market.
- **A NAME IS NOT AN OBJECT (`RR_W003`).** Two economically different objects carried `X9a` for many
  waves. Any reference to a stream must resolve to a *construction*: signal + wrapper + cost model +
  window.

---

## 6. THE TRANSFER CHECKLIST — how a per-market pod researches a new instrument with this depth

Ordered. Steps 1–5 are Wave-0/1 gates that stop a doomed campaign cheaply; 6–13 are the discovery
core; 14–20 are hardening and portfolio integration. Nothing here promotes or deploys — $0, no
sizing change, live book `2047681` untouched.

1. **Inventory the data honestly.** Confirm what 1-min / daily history actually exists on disk (do
   not trust a hard-coded `symbol="NQ"` — that hid MNQ ticks). Record depth and gaps in
   `FUTURES_ALPHA_MAP.md`. Markets without deep 1-min get a **daily-resolution** autopsy, not faked
   intraday history.
2. **Fix instrument-native sessions and the roll/back-adjustment convention** before any signal.
   Never copy NQ's 09:30–16:00. Audit whether the series is additively back-adjusted (percent
   thresholds then invalid). Use `session_boundary.py` semantics for the market's own hours.
3. **Build the market's cost model** in `cost_model.py` terms: tick/point value, commission,
   modelled spread with a MEASURED/MODELLED/ASSUMED tag and an optimistic/base/conservative/stress
   band. A candidate that dies at +1 tick is fragile — decide that now.
4. **Freeze a pristine forward seal** and a dev/burn window register before looking. Compute MDEs for
   the effects you intend to test; if an effect is calendar-bound (rare events), mark it
   UNDERPOWERED and *do not* spend a wave chasing it.
5. **Preregister** the wave's spec.yaml (committed via `prereg_guard.py`), the falsifier's every
   clause, and the one hash-chained ledger entry. Set the family for family-wise correction.
6. **DESCRIPTIVE autopsy (Lane B).** Measure the market's own phenotype: what does its session look
   like, where is P&L concentrated, what is the binding constraint (for NQ it was the left tail)?
   Print the correlation of every candidate object *first*.
7. **Run Lane A (the P1 transfer benchmark)** with minimal DoF and dimensionless transforms, and a
   hard **NQ-reproduction identity gate** (one arm must reproduce a known NQ result exactly, else
   abort). P1 failing means "P1 is not universal," never "this market has no alpha."
8. **MECHANISM ISOLATION.** Before building, ask *where would money come from* and test the mechanism
   directly (the flip-event-vs-trend-state style measurement). One such measurement can close a whole
   class of proposals.
9. **Screen mechanism FAMILIES cheaply** (trend/breakout/compression/shock/session-structure/
   cross-asset), each as a *single* preregistered test against a dependence-preserving null with its
   matched unconditional control — never a grid search. Check `FAILURE_MEMORY.md`: a proposal
   resembling a closed row must state what is *materially* different, or it is a rescue.
10. **For any survivor, derive the simple rule** (majority-of-N, data's own trailing median) instead
    of choosing a threshold from a grid; prefer a **monotone neighborhood response** over an argmax.
11. **Kill leverage disguises.** Run the count-matched random-sizing and rate-matched random-halt
    placebos on every sizing/selection claim. Classify the improvement (NEW INFORMATION vs LEVERAGE
    vs SELECTION LUCK).
12. **Predictor battery → engine.** If a new *information* source appears (a market's native
    cross-asset conditioner, an event structure), test it as a forecast against a best-of-N null,
    then rebuild it as a real object under the campaign's conventions and re-measure. Most forecasts
    do not survive becoming engines.
13. **Evaluate on SEVERAL risk bases, led by weekly-vol** (`eval_battery.py`). A fixed-DD or CDaR
    number is not quotable without its rate-matched random-thinning placebo — the module enforces it.
14. **Adversarial skeptic pass** (per winner): re-run every gate, hunt tail-carried payoffs
    (concentration is a *classification* of payoff shape, never a kill-gate by itself — the incumbent
    itself fails the 40 % bar at 236.8 %), check the semantic meaning of any probability headline
    with a second computation.
15. **Per-year and full-window re-measurement** is a precondition for any adoption; a window chosen
    for one purpose will flatter something else (`W40`). Old-regime failure is a risk label, not a
    veto — but state the mechanism for it.
16. **Cost-stress and roll-cost the survivor.** Recompute net at the conservative and stress cost
    rungs and subtract the roll blackout explicitly.
17. **Record the result in `FUTURES_ALPHA_MAP.md` and `MECHANISM_TRANSFER_MATRIX.md`** — every ✅/✗
    cites a run + ledger trial; never write a cell from intuition. A tested-no-edge is as valuable a
    cell as an edge.
18. **Cross-market learning.** When a market reveals a robust mechanism, test *that mechanism*
    cheaply on the others (controlled transfer), never blind parameter porting.
19. **Portfolio value (Lane D).** Judge the engine on **marginal** portfolio value under a simple
    parameter-free risk budget (equal-risk / inverse-vol), using the **underwater-curve correlation**
    (not weekly ρ) against the live NQ object. Orthogonality is a first-class objective: a Sharpe-0.8
    engine at ~0 NQ correlation can beat pushing NQ 1.2→1.25.
20. **If a candidate ever approaches deployment: parity before dollars.** Component-level ledger,
    ≥99 % decision agreement, trade counts within 2 %, class resolved (not a compile flag), distinct
    versioned class name. EXECUTABLE ≠ PARITY-CERTIFIED ≠ LIVE-ENABLED, and enabling is always an
    owner action.

---

_Sources: `research/weekly_edge/CURRENT_BASELINE.md`, `FROZEN_INCUMBENT_20260827.md`,
`THE_STRATEGY.md`, `PRINCIPLES.md`; `research/genesis2/FAILURE_MEMORY.md`;
`runs/WE_W01/W02/W13/W16-W20/W25/W28/W31/W34/W36/W39/W40/W42/W43/W44/W45/W48/W52/W56-W63/W98/W99/`
`W101/W102/W103/W108-W123/`; `runs/RR_W000-W006/`; `runs/G2_F1..F14/`;
`research_sdk/{eval_battery,prereg_guard,cost_model,session_boundary}.py`; `CLAUDE.md` §4._
