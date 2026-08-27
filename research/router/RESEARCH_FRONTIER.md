# RESEARCH FRONTIER — ranked by expected value of information

_Created 2026-08-27 (owner directive §44). **Updated after every wave.** The next wave is always the
highest-EVI *runnable* row — not the most interesting one, and not the one a previous plan named._

```
EVI  ~  economic ceiling
         x  information novelty
         x  P(learnable)
         x  portfolio usefulness
         x  data quality
         ------------------------------------
         /  research + engineering cost
```

Inputs are **qualitative and are labelled qualitative.** No fake precision (directive §44).

---

## The ranking

_Re-ranked **2026-08-27 after RR_W001**. The router branch moved down; event response moved to the
top. Nothing below is a plan written in advance of evidence — this ordering is what RR_W001's
preregistered continuation produced._

| # | question | EVI | status | gate |
|---|---|:--:|---|---|
| ~~1~~ | ~~Is there enough ACTION-VALUE DISPERSION to justify routing?~~ | — | ✅ **CLOSED — `runs/RR_W001_ACTION_VALUE_LEDGER/`** | see §1 |
| **1** | **Does EVENT RESPONSE carry incremental action-value information?** | **HIGHEST** | **RUNNABLE NOW — the next wave** | — |
| 2 | Is `X9a` a coherent standalone expert? | MEDIUM | RUNNABLE, bounded | — |
| 3 | Can causal features predict action value better than trivial matched controls? | **LOW until new information exists** | **DE-PRIORITISED by RR_W001** | needs #1 |
| 4 | Does a soft allocation with cash beat the static book? | LOW | blocked on #3 | #3 verdict |
| 5 | Does latent state add information beyond raw features? | **—** | **NOT RUN** — RR_W001's continuation rule forbids it | — |
| 6 | Does transition uncertainty carry risk information? | — | blocked on #4 | #4 verdict |
| **6b** | **Is SELECTIVE box un-latching worth anything?** *(new, from RR_W001)* | **LOW** | RUNNABLE | — |
| 6c | **Is book COVERAGE actually a gap?** *(reopened by `RR_W000` audit)* | **LOW** | RUNNABLE | — |
| 7 | Does BBO / order flow separate P1 entry quality? | **HIGH ceiling** | **DATA-BLOCKED** | owner OQ-5 |
| 8 | Does options / dealer-gamma state carry NQ information? | MEDIUM | **OWNER-GATED** | owner OQ-5 |
| 9 | Does an individual-contract substrate change any verdict? | LOW | DEFERRED by design | directive §52 |
| 10 | Does the frozen architecture survive the sealed forward pool? | — | **CALENDAR-GATED** | architecture freeze |
| 11 | Can position management (exit/reversal) be routed? | UNKNOWN | **EXCLUDED from V1** | directive §7 |
| 12 | What integer-contract mapping implements portfolio B? | — | **OWNER CAPITAL DECISION** | OQ-6 |

## ✅ CLOSED — action-value dispersion (`RR_W001`, 2026-08-27)

**G1 PASS · G2 PASS-ON-CLAUSE / FAIL-ON-RATIONALE · G3 FAIL · G4 VOID.** `gates_ALL_must_be_cleared`
is not met, so the preregistered continuation de-prioritises the router branch.

**The opportunity is real:** 2,131 decisions, mean action value **+$162.79**, sd **$2,123.55**,
**59 % negative**; activity-matched random abstention **loses** money at every fraction and the
oracle beats **40/40** random draws, so it is **selection, not exposure reduction**.

**Four facts closed it anyway:**

1. **The counterfactual apparatus buys only 15–31 %** over ranking by the trade's own P&L — the label
   W122's simpler ledger already carried (own-net recovers **68.8–85.5 %** of the causal oracle) —
   and it **damages the right tail more** (205/214 top-decile winners survive vs **213/214**).
2. **The oracle is majority REGENERATION, not avoidance** — **63.8 %** of the f = 0.05 uplift is the
   P&L of trades the frozen policy takes because the session box stops latching. That is a
   **box-policy** finding, and W98 already measured a uniformly looser box at **+$6/wk, p = 0.940**.
3. **Concentration is fatal for identification** — the top 107 events carry **104.9 %** of the total
   action-value sum; the other 2,024 sum to **−$16,872**.
4. **The sample cannot certify a router** — smallest detectable per-decision gain **$41–80** against a
   **$13.93** materiality bar, so a router must capture **~15–28 %** of the ex-post oracle before its
   gain is distinguishable from zero. The only two level-3 recovery rates this repo owns are **16 %**
   and **20 %**.

> **This is a sequencing decision, not a kill.** New information at the decision event raises
> achievable capture, and the certified ledger now exists, so #3 becomes cheap the moment #1 lands.

---

## 1. Action-value dispersion — **RR_W001**, the next wave

| | |
|---|---|
| **question** | At P1/PCT's and XM's genuine decision events, how much does the **marginal action** actually vary in value — and is that dispersion large enough that *any* router could matter? |
| **information source** | none new. This is a **measurement of the existing objects**, not a search |
| **economic ceiling** | **the object being measured.** `LOCAL_MARGINAL_ACTION_ORACLE` (action-branch level A) |
| **current evidence** | **none — never measured in this repo.** W122 built a 2,131-row decision ledger but labelled each row with its **own trade PnL**, which directive §10 shows is *not* the action value when the intervention has downstream effects |
| **uncertainty** | high on the answer, **low on the method** |
| **sample / power** | 2,131 P1 in-window decisions; 346 XM; ~1,058 FOLLOW_MORNING |
| **implementation cost** | **LOW — measured, not estimated.** `gfills` full pass **0.23 s**; one full recompute chain **0.82 s**; all 2,401 toggles **≈ 33 min** |
| **data availability** | ✅ complete. Substrate unchanged. Seal untouched |
| **diversification potential** | n/a — this is the gate |
| **next falsifier** | a preregistered, economically meaningful dispersion gate **committed before the headline oracle is read** |
| **EVI** | **HIGHEST.** It is cheap, it is a *measurement* rather than a search, and **all four possible answers redirect the program** |

> **Why it must be first.** Directive §13: *no ML first.* If action value barely varies, no detector
> can help and every downstream row collapses. If it varies enormously, the question becomes whether
> any causal information identifies it — which is #2 and #3. **Either way the campaign learns where
> it is.** The one outcome that is *not* available is "inconclusive": dispersion is a property of the
> frozen objects and the realized path, and it is fully computable.

**The four pre-declared outcomes** (directive §13), each with its own continuation:

| outcome | meaning | what happens next |
|---|---|---|
| **1. LARGE ROUTABLE OPPORTUNITY** | wide dispersion, concentrated, stable across folds | proceed to #2 |
| **2. SMALL BUT TAIL-RELEVANT** | little mean dispersion, real downside structure | proceed to #2 but with a **risk**, not alpha, target |
| **3. OPPORTUNITY EXISTS, IDENTIFIABILITY UNKNOWN** | wide dispersion, no view yet on predictability | **the intended case** — proceed to #2 |
| **4. ROUTER LOW-EVI** | the static book is already near the action frontier | **de-prioritise the whole router branch**, move to #3 and #8. **Do not run the HMM.** |

> ### ⚠️ There is already one measured router precedent here, and it is negative
> **W99** built a causal meta-router over 12 simple rules — pick the rule with the best trailing
> record in that segment over the last *K* sessions. It **lost money at every K** (−$22 / −$193 /
> −$128 / −$195 per session at K = 10/20/40/80) and **never beat the single best fixed rule**.
> W99's report lists "a meta-router over simple causal rules" as an explicitly **forbidden
> construction**.
>
> **But the same run's CSV carries a column the report did not print:** the causal router beat a
> *random* rule choice at **every** K (+$191 / +$20 / +$85 / +$17 per session). So it held **some**
> information — just not enough to beat a static best. That is the honest shape of the prior:
> **routing over rules is not worthless, it is dominated.** Whether routing over *action values*
> behaves differently is exactly what #1 and #2 exist to find out, and the precedent says the bar to
> clear is **the best static configuration**, never the random one.

## 2. Direct action-value frontier — **RR_W002**

| | |
|---|---|
| **question** | `Router(X) vs` base rate `vs` expert-internal score `vs` vol-only `vs` signed-efficiency `vs` 2-D `vs` matched-random |
| **economic ceiling** | bounded above by #1's oracle; the real target is **`CAUSAL_ACTION_MODEL_FRONTIER` − `REAL_ROUTER_CAPTURE`** |
| **current evidence** | **W112 is the precedent and it is a negative** — ridge OOS **R² −0.024**, directional accuracy **53.58 %** *below* always-long's 55.04 %, best fitted cell **$229** beaten by an **unfitted $190 one-liner**. **W109 + W113**: real state information (AUC 0.613–0.621) with a **null policy, twice** |
| **P(learnable)** | **genuinely uncertain — and lower than it feels.** Every prior attempt predicted a *state*; none predicted the *action value*. That is a real change of target. It is also exactly how a dead family returns in a new costume |
| **sample / power** | P1 2,131 decisions / ~1,058 session clusters. XM **346 — linear models only** |
| **cost** | MEDIUM |
| **next falsifier** | must beat **all** matched controls, not just the base rate. Activity-matched, exposure-matched and time-matched random routers are **mandatory** |
| **EVI** | **HIGH conditional on #1**, near zero without it |

## 3. Event response — **RR_W003** (Stage A only)

| | |
|---|---|
| **question** | Does *how the market responded* to a scheduled release — before the decision — add action-value information **beyond** the event flag, NQ's own move, time-of-day and volatility? |
| **information source** | **the last named cheap surface that is genuinely UNTESTED** (`INFORMATION_COVERAGE`: event RESPONSE = untested; event **flag** = LIGHT) |
| **current evidence** | **W105b**: XM is *not* an event trade — 304 non-announcement trades earn **$408/trade at 54.9 %**. **W110**: the announcement flag *alone* reaches **AUC 0.498** — i.e. the flag is nothing, which is precisely why the *response* is a separate question |
| **data availability** | ✅ **committed and seal-clean** — `research/04_complementary_family/c01_announcement_calendar.csv` |
| **sample / power** | ⚠️ **effective N is distinct EVENT SESSIONS, not downstream P1 entries.** 12 P1 opportunities after one CPI print are **one** macro event |
| **cost** | MEDIUM |
| **next falsifier** | `Router(X)` vs `Router(X + EventResponse)` — **incremental, never standalone-vs-zero**. Controls: event flag, NQ's own pre-decision move, time, volatility, simple continuation. Cluster by event day |
| **EVI** | **HIGH.** Genuinely new information, already-owned data, and **four distinct useful outcomes** — NULL, UNDERPOWERED, router information, or a **standalone alpha lead that forks a new expert** (directive §29) |

> ⚠️ **If event response turns out to carry strong standalone directional information, it does NOT
> stay a router feature.** It forks its own expert wave. Do not contort a new information surface
> into a P1 filter.

## 5. `X9a` as a standalone expert

Bounded engineering: establish a reproducible decision-event contract and a coherent counterfactual
for the only component of `PAIR23` that is **not** already double-counted inside `P1/PCT`'s B-MOM
OR-gate. Unlocks a genuine decomposition of the campaign's one `STRUCTURAL` challenger.
**Deliberately not folded into RR_W001** — adding an expert while measuring the ledger would confound
both (directive §43).

## 5b. Book coverage — reopened by an audit, and ranked LOW on purpose

`runs/RR_W000_LEDGER_AUDIT/` found that W119's `E_NO_ENGINE = 0` was **forced by construction**: the
lens is "neither leg held a position", which makes `book_pnl == 0`, and it was counted *inside* the
`book_pnl < 0` population. **It was empty before any data was read.** On the raw mask there are
**32 sessions** where no engine was present while the session's \|RTH move\| was in its top decile
(mean **452 pts**).

So *"coverage is genuinely not the gap"* is **withdrawn**, and coverage is **UNMEASURED**, not closed.

> **Why it is nevertheless LOW EVI, and this is not a hedge.** `P1/PCT` is **long-only** and declines
> to trade for stated mechanical reasons — the range throttle, the delta gate, the box latch. "No
> engine was present" is therefore frequently the **correct** behaviour, not a miss. Pricing those
> 32 sessions requires knowing the direction in advance, which makes any figure attached to them
> `EX_POST_EXECUTION_FEASIBLE_ORACLE` — **level 2, not available money.** n = 32 is also far too few
> to support a new engine.
>
> **It is on the frontier because the claim was withdrawn, not because the opportunity looks real.**
> It is **not** the next wave.

## 6b. Selective box un-latching — new, from RR_W001, and ranked LOW on purpose

RR_W001 found that **35–64 % of its abstention oracle is REGENERATION**: trades the frozen policy
takes because the session box stops latching once a bad early decision is removed. Those entries are
the `r0+1` bars of latched-out runs and are not decision events at all.

That is a question about the **box policy**, not about routing — and it is a *different* object from
what W98 tested. W98 loosened the box **uniformly** and got **+$6/week at paired p = 0.940**.
Suppressing *specific* early losers so the box survives is not that experiment.

> **Why LOW anyway.** The selection is **ex-post** — the whole point of RR_W001's G3 is that we
> cannot identify which early decisions to suppress. Only **~247** of 1,058 in-window sessions hold a
> latched-out run, so the population is small, and W98's uniform result gives no encouragement.
> **It is named because it is new, not because it looks promising.**

## 5–6. Latent state and transition — NOT RUN, per RR_W001's continuation rule

Both are gated on #2 producing something. Two independent reasons the prior is low before we start:

- **The thesis's own synthetic experiment** (Part IX): the best state classifier (ARI 0.362) was
  **not** the best router, HMM routers recovered **4.6–4.9 %** of oracle uplift against a direct
  utility router's **7.0 %**, and BOCPD reached F1 **0.251** at ~8 alarms/session.
- **This repo's own record**: state information here is real and its policy is null, twice.

**If `Router(X + α) ≤ Router(X)`, the latent layer is removed. It is not rescued with HSMM.**

## 8–9. Data-blocked, owner-gated — recorded once, not re-requested

| | requirement | why it stays open |
|---|---|---|
| **BBO / order flow** | ~**300+ overlapping sessions** | currently **71 of 2,131 P1 entries = 3.3 %**, MDE **$564/entry = 4× the mean**. **CLOSED-BY-DATA before a feature was written** — the question is *unaskable*, not unanswered. OQ-5 |
| **Options / dealer gamma** | $80–199/mo | top NQ-side unlock. OQ-5 |
| **Market internals (TICK/ADD/TRIN)** | — | **no data exists at all** (`DATA_CENSUS`) |
| **DOM / Level-II** | — | owner risk-control **PAUSE** 2026-08-12. **Must not be resumed autonomously** |

> **These are not re-requested every wave** (directive §49). They sit here with their required sample
> size and MDE stated, and research continues on runnable rows.
> **1-minute volume is not order flow and will never be substituted for it.**

## 11. The sealed forward pool — a real constraint, not a formality

| pool | span | status |
|---|---|---|
| 2022-07-01 → 2026-05-30 | ~200 weeks | **DISCOVERY_CONSUMED** (123 waves) |
| 2026-05-31 → 2026-07-31 | 9 weeks | **BURNED** |
| **≥ 2026-08-01** | **~19 sessions today**, +1/day | **VIRGIN / SEALED** |

Opening requires **all seven** freezes (directive §4): architecture, features, experts, model family
+ selection procedure, router semantics, cost model, and a **committed opening spec before any read.**

> ⚠️ **The virgin pool is under a month long.** It can adjudicate a **direction**, not a
> **magnitude**. Any plan that needs the seal to *estimate* an effect size is not a plan. Nothing in
> the router campaign touches it.

## 12–13. Explicitly out of scope for V1

- **Position-management routing** (early exit, reversal, stop rewrite) — directive §7. Entry/action
  routing first; position management is its own campaign if and only if entry routing succeeds.
- **Integer-contract mapping of portfolio B** — an **owner capital decision**, not research.
  Slot D is an `EXECUTABLE_COMPONENT_SET`; `EXECUTABLE_PORTFOLIO` proper remains **PENDING**.

---

## Autonomous continuation rule (directive §45) — pre-committed, so no result can be rescued

| if | then |
|---|---|
| #1 dispersion is tiny | router de-prioritised → straight to **#3**, then **#8** |
| #1 large but #2 fails | current information is insufficient → **#3** and new surfaces rise |
| #3 is null | mark the surface **NULL** honestly → next surface |
| #6 adds nothing | **remove the latent layer.** No HSMM rescue |
| a new expert succeeds | freeze it → re-freeze `EXPERT_UNIVERSE` → re-run the static portfolio comparison → **only then** reassess the router |
| the static portfolio beats every router | **keep the static portfolio.** That is a result, not a failure |
| `P1/PCT` or `XM_CONFLICT` is dominated | **demote it.** No sunk-cost protection |

> **A negative result that removes a degree of freedom is progress.** The campaign stops only when
> every accessible high-EVI question is closed, or the remainder needs owner spend, data or
> permission — and even then it produces the frontier and the next unlock, never "nothing else to do."

---

## Change log

| date | change |
|---|---|
| 2026-08-27 | Created at Phase 0. Ranking is **pre-result**; no wave has run under this frontier. |
