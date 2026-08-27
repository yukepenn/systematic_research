# RESEARCH FRONTIER — ranked by expected value of information

_Owner directive §44. **Rewritten after every wave, not appended to.** The next wave is always the
highest-EVI **runnable** row — not the most interesting one, and not the one a previous plan named._

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
| **1** | Is SELECTIVE box un-latching worth anything? *(new, from RR_W001)* | **LOW** | RUNNABLE |
| **2** | Is book COVERAGE actually a gap? *(reopened by `RR_W000`)* | **LOW** | RUNNABLE |
| 6 | Does a soft allocation with cash beat the static book? | — | **DE-PRIORITISED by RR_W001** · gated on #1 |
| 7 | Does latent state add information beyond raw features? | — | **NOT RUN** — RR_W001's continuation rule forbids it |
| 8 | Does transition uncertainty carry risk information? | — | blocked on #6 |
| 9 | Does BBO / order flow separate P1 entry quality? | **HIGH ceiling** | **DATA-BLOCKED** · owner OQ-5 |
| 10 | Does options / dealer-gamma state carry NQ information? | MEDIUM | **OWNER-GATED** · owner OQ-5 |
| 11 | Do more event TYPES reopen the event-response lane? | MEDIUM | **DATA-BLOCKED** · owner OQ-5 |
| 12 | Does an individual-contract substrate change any verdict? | LOW | DEFERRED by design · directive §52 |
| 13 | Does the frozen architecture survive the sealed forward pool? | — | **CALENDAR-GATED** · needs an architecture freeze |
| 14 | Can position management (exit / reversal) be routed? | UNKNOWN | **EXCLUDED from V1** · directive §7 |
| 15 | What integer-contract mapping implements portfolio B? | — | **OWNER CAPITAL DECISION** · OQ-6 |

> ### ⚠️ **The action-value information question is now ASKED and ANSWERED: NULL.**
> `RR_W002A` fitted it directly against a refitted dependence-preserving null and every gate but the
> integrity check failed. Direct routing is de-prioritised **on evidence**, not on the letter of a
> power gate. The **HMM stays NOT RUN**.
>
> **This tests the information THIS REPO HOLDS.** Order flow, options and a wider event calendar are
> untested because they are **unavailable**, not because they failed — rows 8–10, all owner-gated,
> and the only rows left with genuinely high ceilings. **Higher-timeframe (row 2) also remains
> `LIGHT` and was never closed**; it is a transformation of an NQ path already `DEEP`, which is the
> lowest-prior category, but it is not swept away here.

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

## The remaining runnable rows — both LOW, both engineering

| | |
|---|---|
| **question** | Does `X9a` have a reproducible decision-event contract and a coherent counterfactual, so it can be judged on its own rather than only inside the `PAIR23` basket? |
| **why it is here** | It is **independent of row 1** and needs no owner authorization, so it proceeds alongside `RR_W002A` rather than waiting on it |
| **why it matters** | `X9a` is the one component of `PAIR23` **not** already double-counted inside `P1/PCT`'s B-MOM OR-gate, and `PAIR23` is this campaign's only `STRUCTURAL` challenger — the one object beating `P1` over the 16 unseen years on money, maxDD, top-5, positive weeks *and* streak |
| **what it is NOT** | a revival of the withdrawn **92 %** claim. That figure is divisor-dependent; the defensible income-matched number is **~64 %** and must not be reinterpreted (§35) |
| **cost** | LOW-MEDIUM. Bounded engineering, no new data |
| **honest EVI** | **MEDIUM.** It unlocks a *decomposition*, not an edge. It creates no new information, and this campaign's record is that decompositions of existing objects have not produced promotions |

### 1. Selective box un-latching — new, from RR_W001, ranked LOW on purpose

RR_W001 found **35–64 %** of its abstention oracle is **regeneration**: trades the policy takes
because the box stops latching once a bad early decision is removed. Those entries are the `r0+1`
bars of latched-out runs and are not decision events at all.

That is a **box-policy** question, and a *different* object from W98, which loosened the box
**uniformly** and got **+$6/week at paired p = 0.940**. Suppressing *specific* early losers so the box
survives is not that experiment.

> **Why LOW anyway.** The selection is **ex-post** — RR_W001's G3 is precisely the finding that we
> cannot identify which early decisions to suppress. Only ~**247** of 1,058 in-window sessions hold a
> latched-out run. **Named because it is new, not because it looks promising.**

### 2. Book coverage — reopened by an audit, ranked LOW on purpose

`runs/RR_W000_LEDGER_AUDIT/` found W119's `E_NO_ENGINE = 0` was **forced by construction** — the lens
is "neither leg held a position", which makes `book_pnl == 0`, and it was counted *inside* the
`book_pnl < 0` population. On the raw mask there are **32 sessions** where no engine was present while
\|RTH move\| was top-decile (mean **452 pts**). *"Coverage is genuinely not the gap"* is **withdrawn**;
coverage is **UNMEASURED**.

> **Why LOW.** `P1/PCT` is **long-only** and declines to trade for stated mechanical reasons, so "no
> engine present" is frequently correct behaviour. Pricing those 32 sessions needs a directional
> oracle — level 2, not available money. n = 32 cannot support a new engine.


`INFORMATION_COVERAGE` carries **higher-timeframe** at **`LIGHT`**, evidenced only by `HTFMECH01`
from **campaign #3** — a different campaign on a different object. It has never been tested at
`P1/PCT`'s own decision events, so calling it closed would be false.

> **Why LOW-MED and not higher.** HTF is a transformation of the NQ price path, which is already
> `DEEP`. The adaptation document's own test — *"what NEW observable information does this add?"* —
> answers "another transformation of NQ path already deeply measured", and that is explicitly the
> lowest-prior category. The same reasoning applies to the scheduled-event **flag**, which W110
> measured alone at **AUC 0.498**.
>
> **It is on the list because it is genuinely un-closed, not because it is promising.**

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
| 2026-08-27 | Created at Phase 0, pre-result. |
| 2026-08-27 | **RR_W004 closed HIGHER-TIMEFRAME: NULL** — the last `LIGHT` surface. Every information lane this repo can reach is now measured and closed. |
| 2026-08-27 | **RR_W003 closed `X9a`: NOT ADMITTED**, and found the frontier's own premise false — two objects share the name and `PAIR23` uses the one containing `P1`. HTF becomes row 1. |
| 2026-08-27 | **RR_W002A closed the information question: NULL.** Primary at the 51.0th percentile of its own refitted null; a known-null family scored higher (77.0th) than any real arm; top-decile AUC 0.4990. `X9a` becomes row 1. |
| 2026-08-27 | **RR_W001 closed the dispersion question** (router de-prioritised, HMM not run); **the event-response data gate closed row 2 without a wave**; `X9a` becomes the highest-EVI runnable item; selective box un-latching and book coverage added; more-event-types added as an acquisition row. |
