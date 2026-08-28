# RESEARCH FRONTIER — ranked by expected value of information

_Owner directive §44. **Rewritten after every wave, not appended to.** The next wave is always the
highest-EVI **runnable** row — not the most interesting one, and not the one a previous plan named._

**CURRENT AS OF 2026-08-27, after `MS01` · `MS01A` · `INT01` · `FWD_BOOTSTRAP_V2` ·
`DATA_ASSET_REGISTRY` · `RECENT_REGIME_PANEL` · `MICRO_DISCOVERY_CONFIRMATION_SPLIT`.** Any earlier "as of" wording below this line is historical narrative,
not a timestamp.

```
EVI  ~  economic ceiling x information novelty x P(learnable) x portfolio usefulness x data quality
        ---------------------------------------------------------------------------------------
                                  research + engineering cost
```

Inputs are **qualitative and labelled qualitative.** No fake precision.

---

## The ranking — as of 2026-08-27, after RR_W001 and the event-response data gate

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

## EVI RE-RANK — 2026-08-27, after `MS01A` and the blind-pool audit

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
| **1** | **LAST-ONLY microstructure → consumed discovery → candidate freeze → ONE-SHOT 141-session blind confirmation** | The **only** lane in this repo that can still produce a genuinely confirmed historical result. The blind pool is the most valuable confirmable microstructure asset here and it is spendable exactly once |
| **1=** | **Multi-market TSMOM V1** | 24 roots · 6 sectors at **$0**, and the only lane offering **economically independent** exposure. Runs in parallel — it does not wait on microstructure |
| **2** | **Internals → direct RTH NQ return** | cheap, data already built, and `INT01` closed only the *routing* mapping, not this target |
| **3** | **BBO microstructure — DISCOVERY ONLY** | richer information, but its ceiling is now a *prospective* shadow candidate, not a historical claim |
| **4** | **ES tick/BBO cross-market** (§32) | 103 sessions on disk; W122's NULL was a **1-minute** family and does not close tick-level ES/NQ interaction. After NQ |
| **5** | Prospective shadow / execution ledger | earns nothing on its own, but no new sleeve can be trusted without it |
| **—** | Portfolio-B weighting/selection optimism · incumbent adjudication v2 | **BOUNDED DIAGNOSTICS.** Real questions, capped effort. They must not become the product |

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

**Deliberately NOT ranked:** anything requiring owner spend, live enablement, or calendar time.

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
| 2026-08-27 | **Split the microstructure program into MS-BBO and MS-LAST**, which carry different evidence ceilings. `MS01A` completed and is no longer a blocker — it PASSED freshness, FAILED ordering, and left quote size NOT CERTIFIED, which blocks a named list of features. **No blind BBO pool exists**; a genuine **141-session Last-only** pool does and is frozen. EVI re-ranked around the two lanes that can actually produce alpha. |
| 2026-08-27 | Created at Phase 0, pre-result. |
| 2026-08-27 | **RR_W005 closed SELECTIVE BOX UN-LATCHING** — every uniform relaxation is 16–41 % worse at fixed drawdown and 11–26 % higher exposure. The box is worth keeping. |
| 2026-08-27 | **RR_W004 closed HIGHER-TIMEFRAME: NULL** — the last `LIGHT` surface. Every information lane this repo can reach is now measured and closed. |
| 2026-08-27 | **RR_W003 closed `X9a`: NOT ADMITTED**, and found the frontier's own premise false — two objects share the name and `PAIR23` uses the one containing `P1`. HTF becomes row 1. |
| 2026-08-27 | **RR_W002A closed the information question: NULL.** Primary at the 51.0th percentile of its own refitted null; a known-null family scored higher (77.0th) than any real arm; top-decile AUC 0.4990. `X9a` becomes row 1. |
| 2026-08-27 | **RR_W001 closed the dispersion question** (router de-prioritised, HMM not run); **the event-response data gate closed row 2 without a wave**; `X9a` becomes the highest-EVI runnable item; selective box un-latching and book coverage added; more-event-types added as an acquisition row. |
