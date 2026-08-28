# RESEARCH FRONTIER — ranked by expected value of information

_Owner directive §44. **Rewritten after every wave, not appended to.** The next wave is always the
highest-EVI **runnable** row — not the most interesting one, and not the one a previous plan named._

**CURRENT AS OF 2026-08-28 (second revision, after the volume campaign), after `MS01` · `MS01A` · `INT01` · `INT02` · `FWD_BOOTSTRAP_V2` ·
`DATA_ASSET_REGISTRY` · `RECENT_REGIME_PANEL` · `MICRO_DISCOVERY_CONFIRMATION_SPLIT` ·
`MSLAST_CONTRACT` · `TSMOM_V1/V2` · `ABS_PCT_ADJUDICATION` · `PORTFOLIO_B_RECONCILIATION` ·
`TSMOM_TAIL_H1` · `MSBBO_V1` (**VOID**) · `MSBBO_DEPLOYMENT_FREEZE` · `CARRY00` · `CARRY_V1` ·
`ESNQ00` · `ENGINE_HARDENING` · `BBO_COMPLETENESS_RECENSUS_V1` · `ASSET_CENSUS` ·
`VOLUME00` · `VOLUME_LIQUIDITY_V1` · **PROGRAM B** (`REFERENCE_TRADER_FINGERPRINT` ·
`OPPORTUNITY_DENSITY_GAP` · `NQ_OPPORTUNITY00`).** Any earlier "as of" wording
below this line is historical narrative, not a timestamp.

> **There is exactly ONE current ranking — §"EVI RE-RANK" below.** Every other table in this file is
> a per-family **closure record** and is labelled HISTORICAL. If a row appears twice, the current
> block wins.

```
EVI  ~  economic ceiling x information novelty x P(learnable) x portfolio usefulness x data quality
        ---------------------------------------------------------------------------------------
                                  research + engineering cost
```

Inputs are **qualitative and labelled qualitative.** No fake precision.

---

## ⚠️ HISTORICAL — the RR_W001-era ranking, kept as the per-family closure record

> **This table is NOT the current ranking.** Rows 16, 17, 18a and 18b below were superseded on
> 2026-08-27 by the EVI block further down: TSMOM V1 failed development, TSMOM V2 failed
> validation, INT02 produced no candidate, and MS-LAST-V1 is closed at its own scope. The table
> is retained because it is the authoritative closure record for the families it lists.

| # | question | EVI | status |
|---|---|:--:|---|
| — | ~~Is there enough ACTION-VALUE DISPERSION to justify routing?~~ | — | ✅ **CLOSED** · `runs/RR_W001_ACTION_VALUE_LEDGER/` |
| — | ~~Does EVENT RESPONSE carry incremental action-value information?~~ | — | ✅ **CLOSED-BY-DATA** · `runs/DATAGATE_EVENTRESPONSE_20260827/` |
| — | ~~Do causal features predict FULL-HORIZON `delta_action_value`?~~ | — | ✅ **CLOSED — NULL** · `runs/RR_W002A_ACTION_VALUE_INFORMATION/` |
| — | ~~Is `X9a` a coherent standalone expert?~~ | — | ✅ **CLOSED — NOT ADMITTED** · `runs/RR_W003_X9A_CONTRACT/` |
| — | ~~Does HIGHER-TIMEFRAME state carry anything at P1's decision events?~~ | — | ✅ **CLOSED — NULL** · `runs/RR_W004_HTF_INCREMENT/` |
| — | ~~Is SELECTIVE box un-latching worth anything?~~ | — | ✅ **CLOSED** · `runs/RR_W005_BOX_LATCH_VALUE/` |
| — | ~~Is book COVERAGE actually a gap?~~ | — | ✅ **CLOSED — 0.38 %** · `runs/RR_W006_COVERAGE/` |
| 6 | Does a soft allocation with cash beat the static book? | — | **DE-PRIORITISED by RR_W001** · gated on #1 |
| 7 | Does latent state add information beyond raw features? | — | **NOT RUN** — RR_W001's continuation rule forbids it |
| 8 | Does transition uncertainty carry risk information? | — | blocked on #6 |
| **9** | Does BBO / order flow separate P1 entry quality? | **HIGH ceiling** | ⚠️ **EXTRACTED, THEN RE-CLOSED ON POWER** · 98 quote-complete sessions extracted free; gate re-run at 141 of 2,139 entries, MDE **4.61×** the mean. **Primary target needs 998 sessions and 713 exist — unreachable at ANY coverage.** Session-scoped needs ~455 · `runs/DATAGATE_ORDERFLOW_V2_20260827/` · `runs/DATA_CAPABILITY_AUDIT_20260827/` |
| 10 | Does options / dealer-gamma state carry NQ information? | MEDIUM | **OWNER-GATED** · owner OQ-5 · **confirmed by probe** — no option-chain surface exists in this tool set at all |
| 11 | Do more event TYPES reopen the event-response lane? | MEDIUM | **DATA-BLOCKED** · owner OQ-5 · free-source construction not yet probed |
| **16** | Does a multi-market TSMOM / carry book add marginal portfolio value? | **HIGH ceiling** | ✅ **RUNNABLE — UNIVERSE ESTABLISHED** · **24 roots · 6 sectors · 2016–2025 · $0** · next step is the contract-level substrate with an explicit roll · `runs/MULTIMARKET_INVENTORY_20260827/` |
| — | ~~Do market internals predict P1 ACTION VALUE?~~ | — | ❌ **CLOSED — NULL** · `INT01`: 37.5th pctile of its own refitted null, G3+G5 fail, `NEGCTRL` behaviour matches `RR_W002A`/`RR_W004` · `runs/INT01_STAGE_A/` |
| **17** | Do market internals predict **DIRECT RTH NQ RETURN**? | MEDIUM | ✅ **RUNNABLE · NOT CLOSED BY `INT01`** — different target, different variance (§41 scope discipline) · needs its own preregistration |
| **18a** | Can **LAST-ONLY** trade data generate STANDALONE NQ alpha at 60 s? | **HIGHEST** | ✅ **RUNNABLE · THE ONLY CONFIRMABLE MICROSTRUCTURE LANE** · 243 usable sessions, 102 consumed for discovery, **141 never extracted and now frozen blind** · `runs/MICRO_DISCOVERY_CONFIRMATION_SPLIT/` |
| **18b** | Can **BBO** generate STANDALONE NQ alpha at 60 s? | HIGH info, **LOW claim ceiling** | ⚠️ **DISCOVERY-GRADE ONLY · NO BLIND HOLDOUT EXISTS** · `MS01A` certified the contract: freshness PASSES, **ordering FAILS** (81.1 % same-ms), **quote size NOT CERTIFIED** · all ~99 quote-complete sessions have had their outcomes consumed · `runs/MS01A_BBO_SEMANTICS_AUDIT/` |
| 12 | Does an individual-contract substrate change any verdict? | LOW | DEFERRED by design · directive §52 |
| 13 | Does the frozen architecture survive the sealed forward pool? | — | **CALENDAR-GATED** · needs an architecture freeze |
| 14 | Can position management (exit / reversal) be routed? | UNKNOWN | **EXCLUDED from V1** · directive §7 |
| 15 | What integer-contract mapping implements portfolio B? | — | **OWNER CAPITAL DECISION** · OQ-6 |

> ### ⚠️ **WITHDRAWN 2026-08-27: "NO RUNNABLE ROW REMAINS" WAS A LEVEL-1 CLAIM
> ### PRESENTED AS A LEVEL-2 ONE.**
>
> It quantified over **materialized substrate files** — a strictly narrower population than
> **"what the owner's already-paid, already-connected sources can serve."** The second was
> never probed. `runs/DATA_CAPABILITY_AUDIT_20260827/` probed it, and **three lanes reopened at zero cost**.
>
> | level | question | status |
> |---|---|---|
> | **1** | answerable from **materialized substrates** | **largely exhausted** — the old claim, still true |
> | **2** | answerable from **existing connected sources** | ⚠️ **NOT exhausted** — rows 9, 16, 17 |
> | **3** | requires **new paid data** | owner-gated — and **smaller than it was** |
> | **4** | requires **calendar time** | calendar-gated — unchanged |
>
> **Nothing measured is retracted.** `RR_W002A`, `RR_W004`, `RR_W005`, `RR_W006` all stand
> exactly as recorded. What is withdrawn is the *scope word* attached to them: those waves
> exhausted the **information this repo had materialized**, not the information it can reach.

---

## EVI RE-RANK — 2026-08-28, after `VOLUME00` and `VOLUME_LIQUIDITY_V1`

> ### ⚠️ **THE MICROSTRUCTURE PROGRAM IS NOW TWO SCIENTIFICALLY DIFFERENT LANES.**
> They must never share an evidence class.
>
> | | **MS-BBO** | **MS-LAST** |
> |---|---|---|
> | information | **richer** — quotes, spread, side | weaker — trades only |
> | usable sessions | ~99 quote-complete | **243** |
> | blind confirmation pool | ❌ **NONE EXISTS** — every quote-complete session has had its price outcomes consumed by AUCTION01–04, ACTIONMAP01, FLOW01, U9/U9B | ✅ **141 sessions, never extracted**, frozen with hashes at `fd7b05f` |
> | best attainable claim | **DISCOVERY-GRADE**, needs *prospective* confirmation | **BLIND-HISTORICAL-CONFIRMED** |
>
> **The weaker data supports the stronger claim.** Richer features do not outrank cleaner evidence.

| # | runnable row | why it ranks here |
|---|---|---|
| — | ~~**`MS-BBO-CANDIDATE-1`**~~ | ⛔ **VOID — IT READ THE FUTURE.** int32 overflow; 15 of 30 offsets positive, **+2.065 s** past the decision instant. Leak **134.8 %** of the reported result; causal object **−$1,785.88/session** · `runs/MSBBO_DEPLOYMENT_FREEZE_20260828/` |
| — | ~~**`CARRY_V1`**~~ | ❌ **FAILED C6/C7 → CLOSED.** Sharpe 0.719 but **SI alone 84.1 %** of positive root contribution. Validation and final holdout **NOT READ** · `runs/CARRY_V1_20260828/` |
| — | ~~**`ESNQ_V1`**~~ | ❌ **DEVELOPMENT FAILED X1/X7 → CLOSED.** Net **−$18,113.79**, **−$503.16/session**, **OOF corr +0.0034**, 0 of 4 quartiles positive; NQ-only control also negative. P0-3 completed **44/44 with ZERO action disagreement**. **Blind `EFFECTIVE_14` UNSPENT** · `runs/ESNQ_V1_20260828/` |
| — | ~~more carry roots~~ | ❌ **CLOSED-BY-DATA** — 10 of 13 extra `db/day` roots are **micros of existing roots**; none of the rest has ≥10 contracts |
| — | ~~**`VOLUME_LIQUIDITY_V1`**~~ | ❌ **DEVELOPMENT FAILED 10 of 12 GATES → CLOSED.** Gross **−$17,033.50 before any cost**; net **−$54,330.30**, Sharpe **−0.486**, drawdown lasting **438 of 458 weeks**, **all 21** leave-one-root-out negative, and the object sits at the **56.5th / 39.8th** percentile of its own two nulls. **The mirror also loses (−$20,263.30)** — same |positions|, same $37,296.80 of turnover — so there is nothing to invert. `VOLUME00` was **`DATA-CAPABLE`** and the field is genuinely contract-specific; **the data was fine and the hypothesis was wrong** · `runs/VOLUME_LIQUIDITY_V1_20260828/` |
| **1** | **PROSPECTIVE SHADOW ACCUMULATION** (incumbent roster) | ⬆️ **PROMOTED FROM 6 TO 1 — and not because anything got better.** It is now the **only lane that manufactures an evidence class this project owns none of.** Every other row either is closed, costs owner money, or spends an irreversible asset. It spends **nothing but calendar time**, and the architecture now **exists and is tested** — `research_sdk/shadow_ledger.py`, decision/outcome separated, hash-chained, backfill-refusing, **9/9 self-test including a deliberate tamper**. Roster `P1/PCT` · `XM_CONFLICT_v2` · `P1/ABS`, all parity-certified and hashed. `SHADOW_START = 2026-09-01 18:00 ET`, **not moved backward** · `research/operational/PROSPECTIVE_SHADOW.md`. ⚠️ **Remaining owner action: starting it.** It must run on the owner's machine at a wall-clock time; nothing in this repo can schedule that |
| **2** | ⭐ **FREE UNACQUIRED DATA — the free tier is NOT exhausted** | ⚠️ **THIS ROW EXISTS BECAUSE THE PREVIOUS VERSION OF IT WAS WRONG.** `INFORMATION_FRONTIER_00` found, at **$0**: **VX/VXM futures daily AND 1-minute OHLCV already in NT8** — the VIX term structure, **never named in any repo data document**; **`$TICK` 1-minute back to ~2013** on the existing connection (repo believes 2022 — **~9–13 free years**); **MNQ tick, 187 dates / 128 pre-burn, never read**, invisible only because `build_registry.py:197-206` hard-codes `symbol="NQ"`; **nine unextracted 1-min futures stores** with `evidence_class = unclassified`; free Cboe `VIX_History` 1990→ and CFE **open interest** 2004→; **CFTC COT**, unprobed · `research/information_frontier/` |
| **3** | **Owner-gated acquisition** — ⭐ **rank-1 candidate now NAMED: CME NQ depth + order-level history (Databento `GLBX.MDP3`)** | the **only candidate that reverses a recorded permanent closure** (see the order-flow correction below), best causal quality in the map (**`ts_recv`**), 23-hour coverage, **LOW irreversibility**, and its **exact price is obtainable for $0** via `metadata.get_cost`. ⚠️ **`mechanism_prior` only MEDIUM** — four consecutive negatives in the adjacent lane. Ceiling **`DISCOVERY-GRADE`** declared in advance; **P0-3 parity blocking**. ⛔ **§89 still applies and now bites harder: the free surfaces are NOT exhausted, so rank 2 comes first** |
| **4** | **Remaining unread ES BBO** | **20 sessions genuinely unread and outside any blind manifest** (asset = **79**: 44 consumed by ESNQ + 15 blind + 20 unread, exact). ⚠️ **An ASSET, not a question — and the prior is LOW**: NQ price-side at 60 s returned corr 0.0072, ESNQ cross-market 0.0034. **Do not spend a pristine asset to re-learn a null**, and do not spend one because the shelf is empty |
| **5** | **NQ BBO 19-session blind asset** | **19 outcome-unconsumed · 18 pristine · 1 metadata-exposed.** Falsifier-grade (MDE $2,996/session at n = 19), **not** a validator. An asset, not a question — **no BBO-class candidate exists** |
| **6** | **NQ Last-only 141-session blind pool** | **an ASSET, not a question.** No quotes, so the execution contract every microstructure object here uses cannot be priced on it. Spend only behind a genuinely new frozen Last-only mechanism — **none is on the table** |

> ### ⚠️ **AND PROGRAM C PARTLY REVERSES THE PROCUREMENT CONCLUSION THAT FOLLOWED FROM IT.**
> Program B's "the bottleneck is INFORMATION" was read as *"therefore we must buy something."*
> **`INFORMATION_FRONTIER_00` found that the highest-EVI next actions are FREE and already
> reachable** — the VIX/VX term structure sitting unread in NT8, ~9–13 years of `$TICK`, an entire
> MNQ tick store hidden by a hard-coded symbol filter. **§89's "exhaust the free surfaces first"
> now bites harder, not less.** ⛔ **No money should be spent yet, and none has been.**

> ### ⭐ **PROGRAM B'S CLOSURE SHARPENS THE FRONTIER RATHER THAN EXTENDING IT.**
> `RR_W002A` established that **no tested current information surface separates P1 action quality**.
> `NQ_OPPORTUNITY00` now says the matching thing about **coverage**: the incumbent is blind on 39.7 %
> of sessions, those sessions are **full of movement**, and **both ways to un-blind it are already
> closed**. ⇒ **The bottleneck is INFORMATION — not policy, not clock, not turnover.** The next real
> gain needs an input this repo does not yet have, not a rearrangement of the ones it does. That is
> an argument **for** rank 1 (accumulate a new evidence class) and **for** rank 2 (owner-gated
> acquisition), and **against** re-parameterising anything already owned.

> ### ⚠️ **"NO CURRENT CANDIDATE" IS NOT "NO UNTESTED INFORMATION SURFACE".**
> An earlier report said *"every reachable materialized surface is closed."* **That was too strong
> and was retracted, and the retraction is NOT being quietly reversed now that volume has closed
> too.** What is true: **every tested formulation is closed, the last identified free untested
> surface has been measured, and the campaign has no candidate.** What remains false: that nothing
> untested exists. ⚠️ **The sentence that used to sit here — "multi-market volume / liquidity is
> present in the existing substrate and has never been alpha-tested" — was true on 2026-08-27 and
> is FALSE as of 2026-08-28.** `VOLUME_LIQUIDITY_V1` tested it and closed it, and the honest
> replacement is the bounded statement above: **no effect detectable at `|r| ≈ 0.02` per week
> exists in that specification**, which is not the same as none existing.

> ### ⚠️ **Why rank 1 is not "another BBO model".**
> `MS-BBO-V1`'s corrected feature set has **paid its discovery budget**. Re-running it — repaired,
> re-tuned, or on new sessions — would be a **new discovery object on already-consumed data with
> additional selection debt**, and the void does not reset that. What ES↔NQ proposes is a
> **different mechanism** (information transfer between two correlated liquid contracts), which is
> why it is allowed to exist at all.

> ### ⚠️ **Why rank 1 is not the 141-session Last-only pool.**
> A blind pool is an **asset**, and an empty candidate shelf is **not** a reason to spend one. It
> would also be the wrong instrument: with no quotes, the execution contract every microstructure
> object here uses cannot be priced on it.

> ### ⚠️ **`MS01A` COMPLETED — it is no longer a blocker, and it CONSTRAINED the lane.**
> **PASSES:** quote freshness (median 0 ms, p99 16 ms) and spread invariance across freshness filters.
> **FAILS:** event ordering — **81.1 %** of adjacent events share a millisecond, and exchange sequence
> inside one millisecond is **not recoverable**. **NOT CERTIFIED:** quote size (median 2.0).
>
> **Binding consequence.** Any admitted feature must be **invariant to permutation of rows sharing a
> timestamp**, or be built only from **prior DISTINCT timestamps**. An export-row order is not a trade
> sequence. **Blocked without new evidence:** true aggressor side, queue position, quote-then-trade
> causality, displayed-liquidity absorption, BBO size imbalance, true microprice, depth sweep.
>
> An `np.isclose` default `rtol` once made "at bid" / "at ask" / "inside" sum to **158 %** in this very
> audit — caught only because disjoint categories cannot exceed 100 %. That assertion is now permanent.

**Deliberately NOT ranked:** live enablement. ⚠️ **"Requires calendar time" is no longer a reason
to exclude a row** — that exclusion is exactly what kept the project with zero prospective evidence
for seven campaigns, and rank 1 now *is* a calendar-time lane. **Owner spend is still ranked but
still not authorised.**

> ### ⚠️ **WHAT THE VOLUME CLOSURE DOES AND DOES NOT ENTITLE THIS FILE TO SAY.**
> **Multi-market volume / liquidity was the last IDENTIFIED free untested surface in the
> materialized substrate, and it is now measured.** That is a statement about *identified* surfaces.
> **The 2026-08-27 retraction still stands and is not being quietly reversed:** *"no current
> candidate"* is not *"no untested information surface"*, and this campaign has no privileged view
> of what it has not thought of.
>
> **And the volume negative is BOUNDED, not absolute.** The week-clustered SE on the signal-return
> correlation is **0.0101**, so any weekly cross-sectional effect below **|r| ≈ 0.02** is invisible
> at n = 444 weeks. **What is closed is the frozen specification, not participation as a concept.**
>
> **Multiplicity debt incurred:** 2010–2018 now carries the volume family's first computation, on
> top of TSMOM development and CARRY development. Any future volume hypothesis must state that debt.

> ### ⚠️ **`54.16 %` IS RETIRED AS AN ADMISSION GATE.**
> `MS01`'s `p* = 0.5 + friction / (2·E|move|)` is interpretable **only under a symmetry
> assumption** — that correct predictions are comparable in magnitude to wrong ones. **Accuracy
> does not determine P&L**: a strategy right 60 % of the time that is wrong on the big moves loses
> money. It survives as a **descriptive heuristic** and nothing more.
>
> **The admission object is direct executable net P&L**, built from `Ask_t → Bid_{t+h}` for longs
> and `Bid_t → Ask_{t+h}` for shorts, which carries entry spread, exit spread, spread variation,
> direction and magnitude automatically — with no median spread subtracted a second time.

> ### ⚠️ **WHAT `MS01` DID AND DID NOT ESTABLISH.**
> **DID:** the standalone question is not obviously killed by arithmetic friction or power.
> **DID NOT:** that a 54.16 %-accuracy strategy would make money; that the quoted-spread
> reconstruction is correct; that **effective N = 12,442** is a fact; or that microstructure
> contains alpha. The effective-N figure rests on a scalar-ICC design effect that is acceptable for
> feasibility scoping and **not sufficient for any promotion claim**.

> ⚠️ **A note against this campaign's own optimism (§53).** The owner doctrine now prefers
> current-regime profitability over decades of robustness. That preference is **itself a hypothesis**,
> and its failure mode is recency overfitting. Every regime-local promotion must answer: *was the
> window chosen after seeing it? did performance begin before the window? does the mechanism
> plausibly depend on current structure? does an adjacent earlier window agree?* **The doctrine does
> not get a free pass because the owner stated it.**
>
> ### ⚠️ **The action-value information question is now ASKED and ANSWERED: NULL.**
> `RR_W002A` fitted it directly against a refitted dependence-preserving null and every gate but the
> integrity check failed. Direct routing is de-prioritised **on evidence**, not on the letter of a
> power gate. The **HMM stays NOT RUN**.
>
> **This tests the information THIS REPO HELD AT THE TIME.** Order flow, options and a wider event
> calendar were untested because they were **unavailable**, not because they failed — rows 9–11,
> and the only rows left with genuinely high ceilings.
>
> ⚠️ **`DATA_CAPABILITY_AUDIT_20260827` has since falsified the "unavailable" premise for row 9.**
> See the Level-1/2 hierarchy below — the audit was run precisely because "this repo holds no such
> file" is **not** the same claim as "the owner's connections cannot serve it."
>
> **Higher-timeframe (row 2) is CLOSED, not `LIGHT`** — `RR_W004` closed it the same day; the
> sentence that once said otherwise here was stale and is corrected.

---

## ✅ CLOSED — action-value DISPERSION, and the ECONOMIC router (`RR_W001`)

_Closed: the dispersion measurement and the full economic router. **Not** closed: whether causal
features predict action value — that is row 1 and was never asked here._

**G1 PASS · G2 PASS-ON-CLAUSE / FAIL-ON-RATIONALE · G3 FAIL · G4 VOID.** `gates_ALL_must_be_cleared`
is not met, so the preregistered continuation de-prioritises the router branch and does **not** run
the HMM.

**The opportunity is real and it is selection, not exposure reduction.** 2,131 decisions, mean action
value **+$162.79**, sd **$2,123.55**, **59 % negative**. Activity-matched random abstention *loses*
money at every fraction and the oracle beats **40/40** random draws — the inverse of W121.

**Four facts closed it anyway:**

1. ⚠️ **RETIRED AS A CONTROL.** RR_W001 reported that ranking by the trade's own P&L recovers
   **68.8–85.5 %** of the causal oracle and read it as "the apparatus buys only 15–31 %". **Trade P&L
   is an OUTCOME, not decision-time information**, so it is not a live control. The finding stands as
   what it is — *a cheaper ex-post label is highly correlated with ΔU*, which bounds the value of the
   counterfactual machinery **for building a ledger** and says **nothing** about causal
   predictability. The right-tail observation stands (205/214 survive vs 213/214).
2. **The oracle is majority REGENERATION, not avoidance.** **63.8 %** of the f = 0.05 uplift is the
   P&L of trades the policy takes because the session box stops latching — a **box-policy** finding.
3. **Concentration is fatal for identification.** The top 107 events carry **104.9 %** of the total
   action-value sum; the other 2,024 sum to **−$16,872**.
4. **The sample cannot certify a router.** Smallest detectable per-decision gain **$41–80** vs a
   **$13.93** bar, so a router must capture **~15–28 %** of the ex-post oracle — at or above the only
   two level-3 recovery rates this repo owns (**16 %**, **20 %**).

> **A sequencing decision, not a kill — and narrower than first written.** What is de-prioritised is
> the **full economic router**. The **information** question was never asked in this wave and is now
> row 1. G3 is the single valid substantive failure; **G4 was VOID and therefore contributes no
> evidence in either direction**, so stability is neither established nor refuted.

## ✅ CLOSED-BY-DATA — event response (`DATAGATE_EVENTRESPONSE_20260827`)

**Closed without a wave being run.** That is what a data gate is for: one afternoon instead of a full
preregistered wave that could only have returned `UNDERPOWERED`.

A response feature exists only **after** its event, reaching **153 of 2,131** `P1/PCT` decisions
(**7.18 %**) on **71** effective event sessions — and directive §20 binds: twelve opportunities after
one CPI print are **one** event. MDE there is **$1,896.67** against a lane-scaled bar of **$194.06**
— **9.8× short**, i.e. only effects ≥ **0.665 sd** are visible. `XM_CONFLICT` is worse: **29 of 346**,
and FOMC at 14:00 is not in its 09:45 information set at all.

Closing the gap needs **~96× the effective N** ≈ **220 years** of calendar. **The constraint is the
calendar; no modelling choice moves it.** The only lever that does not require waiting is **more
event TYPES** — acquisition, not research (row 10, OQ-5).

> Marked **CLOSED-BY-DATA / UNDERPOWERED**, never `NULL`. **Not closed:** event response as a
> *standalone expert* (§29) — a different question at n = 96 CPI/NFP sessions, smaller than
> `XM_CONFLICT`'s 346. A search over event types × windows × directions on 96 rows would be a
> selection machine. It would need its own spec and a single frozen hypothesis.

---

## ✅ CLOSED — NULL — causal information does not predict action value (`RR_W002A`)

| | |
|---|---|
| **question** | Do causal features available **at** the `P1/PCT` decision event predict **full-horizon** `delta_action_value` better than simple causal controls and a dependence-preserving null? |
| **why it is first** | **RR_W001 fitted zero models.** This is the missing test, and until it runs, "current information cannot separate P1 action quality" is an assertion rather than a result |
| **what it is NOT** | a request to prove a profitable router. **No policy, no abstention, no sizing, no exits, no HMM.** Stage A information only |
| **primary target** | continuous **FULL-HORIZON** `delta_action_value` — the whole-object figure (mean +$115.30), not the session-scoped decomposition (+$162.79) |
| **budget** | **very small and preregistered.** Existing information families only; no inventing indicators; at most ONE shallow nonlinear challenger; no large hyperparameter search |
| **null** | the **entire modelling procedure re-fitted inside every dependence-preserving permutation/shift** — W110b's corrected construction, not a fixed-prediction shortcut |
| **validation** | expanding chronological / prequential, session-clustered, training-only scaling, no random row split, **no sealed ≥ 2026-08-01 data** |
| **power** | ⚠️ reported explicitly. RR_W001's G3 already establishes this sample cannot certify *small economic* improvements — an information result here does **not** overturn that |

**Three outcomes, fixed in advance:**

| outcome | classification | continuation |
|---|---|---|
| **A** no causal model beats simple controls or the null | current-data **ACTION-VALUE INFORMATION is NULL / LOW-EVI** | de-prioritise direct routing *confidently* → row 2 |
| **B** information exists, economics underpowered | **REAL INFORMATION / ECONOMIC POLICY UNRESOLVED** | **do not force a router** → row 2 |
| **C** strong information exists | — | **then and only then** preregister a separate economic router wave |

## ✅ CLOSED — NOT ADMITTED — `X9a`, and the premise was false (`RR_W003`)

W72's era table **reproduced exactly** — 3,948 / +$28.6 / t 1.83 / PF 1.105 and 950 / +$123.0 /
t 1.05 / PF 1.095, all four figures in both eras. The contract is well defined: a latched channel
with the same session box as `P1/PCT`, so RR_W001's replay applies unchanged.

**But two different objects carry the name `X9a`**, and `PAIR23` uses the one that contains the
incumbent. The stored `w72:X9a` is `long_obj(TG_for(X9a))` — **`P1`'s entire Solar ensemble with X9a
substituted for B-MOM as one additive term in the tilt** — weekly ρ with `P1/PCT` **+0.613**, net
$233,781. W72's *raw* channel is a different object: ρ **+0.07**, net $61,404. **Daily ρ between the
two is +0.15.**

> **The frontier's own premise — "`X9a` is the one component of `PAIR23` not already double-counted
> inside `P1/PCT`'s B-MOM OR-gate" — was FALSE. It is the MOST double-counted component.**
> Not admitted under either reading: the `PAIR23` member fails R3 by construction, and the raw
> channel passes R3 but is not the object the question asked about, so admitting it would not
> decompose `PAIR23`.
>
> **`PAIR23` keeps its `STRUCTURAL` status and all its economics.** What changed is what it is: a raw
> channel plus a `P1` variant — which also makes ρ(BMOM, X9a) = +0.009 a fact about **wrappers**.

## ✅ CLOSED — NULL — higher-timeframe adds nothing (`RR_W004`)

Six multi-session features added **incrementally** to RR_W002A's 18, with the pipeline certified
unchanged by reproducing its primary ρ to **−0.0302** exactly. `X+HTF` lands at the **61.5th**
percentile of its refitted null, `HTF` alone at the **71.0th**, and the **known-null negative control
at the 77.0th — higher than either real arm.** Adding HTF made fold-sign consistency *worse*,
54 % → 31 %.

> ⚠️ **Two of five gates "passed" and neither counts.** H1 (X+HTF beats X) is a pass at being
> *less negative than something already worse than chance*; H4 (increment positive in 62 % of folds)
> is an increment between two negative quantities. **The gates that test for information — H2 and
> H3, both against a refitted null — fail.** That shape invites "promising, needs tuning" and the
> reading is refused on the record.

**This was the last surface marked `LIGHT`.** The statement *"no tested current information surface
separates P1 action quality"* is now **complete rather than partial**.

| | |
|---|---|
| **question** | Does `X9a` have a reproducible decision-event contract and a coherent counterfactual, so it can be judged on its own rather than only inside the `PAIR23` basket? |
| **why it is here** | It is **independent of row 1** and needs no owner authorization, so it proceeds alongside `RR_W002A` rather than waiting on it |
| **why it matters** | `X9a` is the one component of `PAIR23` **not** already double-counted inside `P1/PCT`'s B-MOM OR-gate, and `PAIR23` is this campaign's only `STRUCTURAL` challenger — the one object beating `P1` over the 16 unseen years on money, maxDD, top-5, positive weeks *and* streak |
| **what it is NOT** | a revival of the withdrawn **92 %** claim. That figure is divisor-dependent; the defensible income-matched number is **~64 %** and must not be reinterpreted (§35) |
| **cost** | LOW-MEDIUM. Bounded engineering, no new data |
| **honest EVI** | **MEDIUM.** It unlocks a *decomposition*, not an edge. It creates no new information, and this campaign's record is that decompositions of existing objects have not produced promotions |

## ✅ CLOSED — the session box is worth keeping (`RR_W005`)

**Every uniform relaxation of the box adds raw dollars and destroys the scale-invariant headline.**

| vs baseline | raw | maxDD | **wk @ fixed DD** | exposure |
|---|---:|---:|---:|---:|
| no box at all | +44,806 | +27,664 | **−395 (−40.7 %)** | +25.7 % |
| no halt, keep target | +22,992 | +18,876 | −334 (−34.3 %) | +13.3 % |
| keep halt, no target | +27,048 | +8,787 | −155 (−16.0 %) | +11.3 % |
| box × 2 | +4,968 | +15,003 | −317 (−32.6 %) | +15.5 % |

Measured ex post, the latch itself "costs" **−$44,806** over 247 binding sessions and a perfect
selective un-latching would be worth **$283,856**. **Both numbers evaporate at fixed drawdown.** The
cost of latching is drawdown control being paid for, and `t` falls monotonically across the arms,
4.17 → 3.62.

> This also **explains** RR_W001's regeneration component rather than leaving it open — un-latching
> adds raw dollars *by adding exposure* — and **confirms W98** (a uniformly looser box, +$6/wk at
> p = 0.940) rather than contradicting it. The selective half needs identification, which `RR_W002A`
> and `RR_W004` have now measured as **NULL**.
>
> **Constraint added, the mirror of the leverage rule:** never read an exposure-funded raw-dollar
> gain as a cost avoided. Any finding in raw dollars must be re-expressed at fixed drawdown before
> it is believed.

## ✅ CLOSED — coverage is not a gap, and now it is measured (`RR_W006`)

`RR_W000` withdrew W119's `E_NO_ENGINE = 0` as a tautology, leaving coverage **UNMEASURED**. Measured
properly on the raw mask: of the **32** sessions where neither leg held a position while
\|RTH move\| was top-decile, **23 (71.9 %) were moves DOWN** — which a **long-only** book is right
to decline. Of the 24 that matched the substrate, **16 had the signal FIRE and get suppressed**,
which is a policy question, not coverage, and `RR_W005` closed its policy half.

> ### **The coverage gap, correctly scoped, is 4 sessions of 1,058 — 0.38 %.**
> 8 of the 32 did not match by date and are excluded; **even if all eight were UP-and-never-fired the
> gap would be 1.1 %.** Too few to support an engine, and unpriceable without a directional oracle
> (level 2, not available money).

W119's original conclusion was **right for the wrong reason**. It now has an argument instead of an
artifact of masking, and a number — 0.38 % — instead of a structurally guaranteed zero.

## 6–8. The economic router stack — de-prioritised, and the HMM is NOT RUN

Blocked behind new information, per RR_W001's continuation rule. Two independent reasons the prior
was already low before RR_W001 ran: the owner thesis's **own synthetic experiment** (best state
classifier ≠ best router; HMM routers recovered 4.6–4.9 % of oracle uplift against a direct utility
router's 7.0 %; BOCPD F1 0.251 at ~8 alarms/session), and this repo's record — **W109/W113** real
information with a null policy, twice, and **W99**, whose causal meta-router over 12 rules lost at
every K and never beat the best fixed rule (though it *did* beat random rule choice, so the honest
prior is **dominated, not worthless**).

**If `Router(X + α) ≤ Router(X)`, the latent layer is removed. It is not rescued with HSMM.**

## 9–11. Owner-gated acquisition — recorded once, not re-requested

| lane | what is needed | why it stays open |
|---|---|---|
| **BBO / order flow** | ~**300+** overlapping sessions | currently **71 of 2,131** P1 entries = **3.3 %**, MDE **$564/entry = 4× the mean**. Closed **by data before a feature was written** |
| **Options / dealer gamma** | $80–199/mo | top NQ-side unlock |
| **More event TYPES** | PPI, retail sales, claims, PCE, GDP, ISM, auctions | ~4× the event count → effective N ≈ 280, MDE ≈ 5× the bar. **Better, still short** |
| Market internals (TICK/ADD/TRIN) | — | **no data exists at all** |
| DOM / Level-II | — | owner risk-control **PAUSE** 2026-08-12, **not to be resumed autonomously** |

**These are not re-requested every wave** (§49). They sit here with their required sample size and
MDE stated. **1-minute volume is not order flow and will never be substituted for it.**

## 13. The sealed forward pool — a real constraint

| pool | span | status |
|---|---|---|
| 2022-07-01 → 2026-05-30 | ~200 weeks | **DISCOVERY_CONSUMED** (123 waves) |
| 2026-05-31 → 2026-07-31 | 9 weeks | **BURNED** |
| **≥ 2026-08-01** | **~19 sessions**, +1/day | **VIRGIN / SEALED** |

Opening needs all seven freezes (§4) and a **committed opening spec before any read**.
⚠️ **It can adjudicate a direction, not a magnitude.** Any plan needing the seal to *estimate* an
effect is not a plan. Nothing in this campaign has touched it.

## 14–15. Out of scope for V1

**Position-management routing** (early exit, reversal, stop rewrite) — §7; its own campaign if and
only if entry routing ever succeeds. **Integer-contract mapping of portfolio B** — an owner capital
decision; slot D is an `EXECUTABLE_COMPONENT_SET` and `EXECUTABLE_PORTFOLIO` remains **PENDING**.

---

## Autonomous continuation rule (§45) — pre-committed, so no result can be rescued

| if | then |
|---|---|
| an information lane is underpowered | mark **CLOSED-BY-DATA / UNDERPOWERED**, never NULL → next lane |
| a decomposition yields nothing | record it → next runnable row |
| a new expert succeeds | freeze it → re-freeze `EXPERT_UNIVERSE` → re-run the static comparison → **only then** reassess the router |
| the static portfolio beats every router | **keep the static portfolio.** A result, not a failure |
| `P1/PCT` or `XM_CONFLICT` is dominated | **demote it.** No sunk-cost protection |
| every runnable row is closed | produce the frontier and the **next unlock**, never "nothing else to do" |

## Change log

| date | change |
|---|---|
| 2026-08-28 | ⭐ **PROGRAM C: THE FREE TIER IS NOT EXHAUSTED, AND THREE RECORDED CONCLUSIONS ARE CORRECTED.** ⚠️ **"The free surfaces are exhausted" is RETRACTED.** (a) **Order-flow is closed on *"998 sessions needed, 713 exist in the entire universe"* — and 713 is the LOCAL NT8 STORE, not acquirable data**; Databento `GLBX.MDP3` carries CME NQ **MBO from 2017-05-21** (~2,300 unburned, unsealed sessions), so the **impossibility arithmetic is not established** (the closure may still hold on *evidence*). (b) **Internals `REGIME-LOCAL (2022+)` is true of the STORE, false of the FEED** — a probe returns 1-min `$TICK` at **2013 and 2015**, ~9–13 free years. (c) **VX/VXM futures — daily AND 1-minute, multiple contract months — are ALREADY IN NT8 at $0 and were never named in any repo data document.** Also: **MNQ tick (187 dates, 128 pre-burn, never read) is invisible only because `build_registry.py` hard-codes `symbol="NQ"`** — a bug, not an absence. **Third instance of "we do not have X" meaning "this repo has not fetched X".** ⛔ **`$0` spent; rank-1 paid candidate's exact price is obtainable for `$0`** · `research/information_frontier/` · `runs/INFORMATION_FRONTIER_00_20260828/` |
| 2026-08-28 | ✅ **PROSPECTIVE SHADOW PREFLIGHT: READY — and it found a real defect before the first row.** `shadow_ledger.py` compared timestamps as **strings**; across the Nov DST change `'…08:30:00-05:00'` sorts **before** `'…09:00:00-04:00'` while being the **later instant**, so a valid decision would have been refused as backfill. **Fixed to compare parsed INSTANTS, and a naive stamp with no UTC offset is now REFUSED.** Self-test **11/11**. All six preflight tests pass with every guard **demonstrated to reject**, incl. **ZERO ORDER PATH by AST** and a `health()` that is **structurally incapable** of returning P&L · `runs/PROSPECTIVE_SHADOW_PREFLIGHT_20260828/` |
| 2026-08-28 | ⭐ **PROGRAM B CLOSED ITS FIRST QUESTION, AND THE PREMISE WAS FALSE.** The incumbent does **not** under-re-enter (**3.340 trades/active session**, median 3, p90 7, max 19; its **5th–8th entries are its BEST bucket** at $180.88/trade, session-clustered CI excluding zero; capping at any K<8 loses money) and it does **not** ignore the overnight session (**23 of 24 hours**, **63.3 % of entries outside RTH**). ⚠️ **Two of my own claims were retracted in the process**: "P1 is RTH-only, 6.5 of 23 hours" (false — it propagated into an owner directive before being caught) and three population/unit errors on the campaign's own headline density. `research_sdk/test_session_unit.py` (6/6) now makes the `session_id`-vs-`session_date` class of error mechanical |
| 2026-08-28 | ❌ **`NQ_OPPORTUNITY00` — LANE A CLOSES AT `A-C2`; LANE B CLOSED BEFORE IT OPENED.** The 39.7 % flat-session hole is **REAL and NOT QUIET**: flat sessions carry **84 %** of active-session range, **92 %** of path length, **90 %** of 40-tick directional changes, and **100 % contain ≥3 ten-point reversals**. `A-C1` passed at **77.9 %** against a 40 % bar. But only **two** state families exist on that population and **both were disqualified in advance**: the **entry threshold** (3.0→1.0 takes flats 420→145 — forbidden threshold mining) and the **mirrored short leg** (armed on **343 of 420**, but falsified five times and listed **DEAD/FALSIFIED**). ⚠️ **NO THIRD ADMISSIBLE FAMILY WAS IDENTIFIED** *within the currently owned and examined information surface, under Program B's preregistered rules.* **This is NOT a proof that none exists.** Arming identity `K·g·(1+dL) ≥ 16` re-derived against the frozen `votes()` with **0 disagreements on 1,620,044 bars**; **60.0 %** of flat sessions never see any member set go long. ⚠️ **The reference trader is retired as a benchmark**: per **in-market hour** he earns **$42.79** ($33.47 re-costed) against P1's **$96.18** · `runs/NQ_OPPORTUNITY00_20260828/` |
| 2026-08-28 | ❌ **`VOLUME_LIQUIDITY_V1` FAILED 10 of 12 DEVELOPMENT GATES → CLOSED**, and the failure is unambiguous: **gross is −$17,033.50 BEFORE any cost**, net −$54,330.30, Sharpe −0.486, drawdown lasting **438 of 458 weeks**, **all 21** leave-one-root-out negative, and the object sits at the **56.5th / 39.8th** percentile of its own two nulls — *it is its own null*. **The mirror also loses**, so there is nothing to invert. Three gates recorded **NON-ADJUDICATIVE on a negative-total object** (the `ESNQ` lesson applied, not re-learned). `VOLUME00`'s declared ±1 roll near-miss (**1.481** vs a 1.5 gate) **materialised** — 5 % of rows carry 42.7 % of the loss — **and an embargo was NOT retro-fitted**. **Frontier rank 1 becomes PROSPECTIVE SHADOW**, promoted not because anything improved but because it is the only lane that manufactures an evidence class this project owns none of |
| 2026-08-28 | ✅ **`VOLUME00` → `DATA-CAPABLE`, and it answered a question that had only ever been answered for PRICE.** A **known-merged positive control** settles it: the same V2/V3 statistics that pass on `db/day` (**0.0101 %** duplicate share, deferred/front median **0.0011**) **fail completely** on the captured merge-back-adjusted payload (**98.86 %**, median **1.0000**, **96.14 %** of ratios exactly 1.000). **21 roots · 6 sectors · 17 years, nothing excluded.** ⚠️ **The roll entanglement BOUND**: the same-day contract-switch log-volume jump exceeds 1 MAD-unit on **87.2 %** of rolls, so the preregistered rule selected **`ROOT_TOTAL`** volume — a forced pre-expiry roll's downward jump would otherwise have manufactured a long signal out of the calendar |
| 2026-08-28 | **PHASE 0 engine hardening**: the int32-overflow class exists in **exactly one production site** (`bbo_v1.py:119`, already void); every other occurrence is a deliberate reproduction. `research_sdk/timegrid.py` + `causality.py` + `keysafe.py` + a pinned regression test make it unreachable prospectively. **0C: 30 sites, 2 flagged, 0 confirmed. 0D: 374 module-level writes → 10 imported → 3 confirmed.** |
| 2026-08-28 | **BBO RECENSUS — VERDICT B: a genuine blind BBO pool exists, 19 sessions**, frozen and hashed `84a8575a…0931`, **returns NOT read**. The 99-vs-123 gap is **entirely a definition difference** (97 both · 19 RTH-only · 2 full-session-only), and the old "no pool exists" verdict was **correct under its own 23-hour criterion** — what was wrong was applying a full-session criterion to an **RTH-only** strategy. The pool is a **FALSIFIER** (rejects a false +$5,125 claim at 5.7 σ) and **not** a validator (MDE $2,996/session at n=19). |
| 2026-08-28 | **ASSET CENSUS: ES BBO is 64 pre-seal sessions with ZERO outcome-consumed** — the largest fully-unread quote-bearing asset the project owns. **15 sessions have BOTH ES and NQ sides unread.** "Add more carry roots" is **CLOSED-BY-DATA** (10 of 13 extras are micros; none of the rest has ≥10 contracts). Frontier re-ranked around it. |
| 2026-08-28 | ⛔ **`MS-BBO-CANDIDATE-1` VOIDED — it read the future.** `np.arange(-30,0) * NS` overflows **int32** on Windows/NumPy 1.26; 15 of 30 feature offsets were positive, reaching **+2.065 s past the decision instant**. Leak **134.8 %** of the result; causal object **−$1,785.88/session**. Caught by an **independent streaming re-implementation** on its first run — no null, placebo or mirror could have caught it, because all three inherit a feature-construction leak. ⚠️ **`L2` had been signalling it all along** and was written up as "consistent with a fast-decaying signal". Blast radius checked: **one line, one file, no other run affected.** |
| 2026-08-28 | **`CARRY00` → CARRY-CAPABLE** (11 roots, 4 sectors; FX closed-by-data exactly as the SPEC predicted). **`CARRY_V1` → FAILED C6/C7 and CLOSED**: 6 of 8 gates passed at Sharpe 0.719, but SI alone is 84.1 % and metals 98.5 % of positive contribution. Validation and final holdout **not read**. `n_sector = 2` degenerates the centred rank to ±1 in three of four sectors — a structural finding for any future curve work. |
| 2026-08-28 | **`ESNQ00`**: 59 overlapping RTH-complete ES/NQ sessions exist (52 unexported), but §52's incremental question **lost its baseline** with BBO, and **power was deliberately left OPEN** rather than computed from a level variance that is the wrong denominator for a paired test. **Prospective shadow DEMOTED from rank 1** — its entire EVI rested on the void candidate. |
| 2026-08-27 | **TSMOM V1 FAILED its preregistered DEVELOPMENT gates (3 of 6)** and validation stays shut. Before that, a **binding data-contract finding**: `AddDataSeries` returns **merge-back-adjusted** series while `GetBars`/`db/day` return true unmerged contract data — the merged path makes a volume-crossover roll **undefined** and bakes the basis into prices. The `.ncd` daily format was decoded and validated, unlocking a local transport. **MS-LAST-V1's adjudication was repaired**: "martingale" retracted, a non-null (`np.roll(...).mean()`, invariant) replaced with a refitted session-block null, and equivalence tested against materiality declared in advance. |
| 2026-08-27 | **MS-LAST CLOSED — well-powered NULL at 60 s**, and the **141-session blind pool was NOT spent** (intersection asserted = 0). Two data-contract corrections fell out: the textbook **tick rule moves 274 %** under within-millisecond permutation and is blocked, and **MS01A's 69.6 % "inside" was same-millisecond contamination** — corrected to 8.9 %, with its cost conclusion surviving. **TSMOM depth is 2009, not 2016** (~17.6 years), and its chronology is frozen. |
| 2026-08-27 | **Split the microstructure program into MS-BBO and MS-LAST**, which carry different evidence ceilings. `MS01A` completed and is no longer a blocker — it PASSED freshness, FAILED ordering, and left quote size NOT CERTIFIED, which blocks a named list of features. **No blind BBO pool exists**; a genuine **141-session Last-only** pool does and is frozen. EVI re-ranked around the two lanes that can actually produce alpha. |
| 2026-08-27 | Created at Phase 0, pre-result. |
| 2026-08-27 | **RR_W005 closed SELECTIVE BOX UN-LATCHING** — every uniform relaxation is 16–41 % worse at fixed drawdown and 11–26 % higher exposure. The box is worth keeping. |
| 2026-08-27 | **RR_W004 closed HIGHER-TIMEFRAME: NULL** — the last `LIGHT` surface. Every information lane this repo can reach is now measured and closed. |
| 2026-08-27 | **RR_W003 closed `X9a`: NOT ADMITTED**, and found the frontier's own premise false — two objects share the name and `PAIR23` uses the one containing `P1`. HTF becomes row 1. |
| 2026-08-27 | **RR_W002A closed the information question: NULL.** Primary at the 51.0th percentile of its own refitted null; a known-null family scored higher (77.0th) than any real arm; top-decile AUC 0.4990. `X9a` becomes row 1. |
| 2026-08-27 | **RR_W001 closed the dispersion question** (router de-prioritised, HMM not run); **the event-response data gate closed row 2 without a wave**; `X9a` becomes the highest-EVI runnable item; selective box un-latching and book coverage added; more-event-types added as an acquisition row. |
