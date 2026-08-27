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
| **1** | **Is `X9a` a coherent standalone expert?** | **MEDIUM** | **RUNNABLE — the highest-EVI runnable item** |
| 2 | Is SELECTIVE box un-latching worth anything? *(new, from RR_W001)* | LOW | RUNNABLE |
| 3 | Is book COVERAGE actually a gap? *(reopened by `RR_W000`)* | LOW | RUNNABLE |
| 4 | Can causal features predict action value better than matched controls? | LOW until new information exists | **DE-PRIORITISED by RR_W001** |
| 5 | Does a soft allocation with cash beat the static book? | LOW | blocked on #4 |
| 6 | Does latent state add information beyond raw features? | — | **NOT RUN** — RR_W001's continuation rule forbids it |
| 7 | Does transition uncertainty carry risk information? | — | blocked on #5 |
| 8 | Does BBO / order flow separate P1 entry quality? | **HIGH ceiling** | **DATA-BLOCKED** · owner OQ-5 |
| 9 | Does options / dealer-gamma state carry NQ information? | MEDIUM | **OWNER-GATED** · owner OQ-5 |
| 10 | Do more event TYPES reopen the event-response lane? | MEDIUM | **DATA-BLOCKED** · owner OQ-5 |
| 11 | Does an individual-contract substrate change any verdict? | LOW | DEFERRED by design · directive §52 |
| 12 | Does the frozen architecture survive the sealed forward pool? | — | **CALENDAR-GATED** · needs an architecture freeze |
| 13 | Can position management (exit / reversal) be routed? | UNKNOWN | **EXCLUDED from V1** · directive §7 |
| 14 | What integer-contract mapping implements portfolio B? | — | **OWNER CAPITAL DECISION** · OQ-6 |

> ### ⚠️ **Every information lane reachable from data this repo currently holds is now measured.**
> Rows 1–3 are engineering and decomposition, not discovery. Rows 8–10 are the only rows with a
> genuinely high ceiling, and **all three are owner-gated acquisition.** That is the honest state of
> the frontier and it should not be dressed up.

---

## ✅ CLOSED — action-value dispersion (`RR_W001`)

**G1 PASS · G2 PASS-ON-CLAUSE / FAIL-ON-RATIONALE · G3 FAIL · G4 VOID.** `gates_ALL_must_be_cleared`
is not met, so the preregistered continuation de-prioritises the router branch and does **not** run
the HMM.

**The opportunity is real and it is selection, not exposure reduction.** 2,131 decisions, mean action
value **+$162.79**, sd **$2,123.55**, **59 % negative**. Activity-matched random abstention *loses*
money at every fraction and the oracle beats **40/40** random draws — the inverse of W121.

**Four facts closed it anyway:**

1. **The counterfactual apparatus buys only 15–31 %** over ranking by the trade's own P&L — the label
   W122 already had (own-net recovers **68.8–85.5 %**) — and it **damages the right tail more**
   (205/214 top-decile winners survive vs **213/214**).
2. **The oracle is majority REGENERATION, not avoidance.** **63.8 %** of the f = 0.05 uplift is the
   P&L of trades the policy takes because the session box stops latching — a **box-policy** finding.
3. **Concentration is fatal for identification.** The top 107 events carry **104.9 %** of the total
   action-value sum; the other 2,024 sum to **−$16,872**.
4. **The sample cannot certify a router.** Smallest detectable per-decision gain **$41–80** vs a
   **$13.93** bar, so a router must capture **~15–28 %** of the ex-post oracle — at or above the only
   two level-3 recovery rates this repo owns (**16 %**, **20 %**).

> **A sequencing decision, not a kill.** New information at the decision event raises achievable
> capture, and the certified ledger now exists, so this becomes cheap the moment a new surface lands.

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

## 1. `X9a` as a standalone expert — the highest-EVI RUNNABLE item

| | |
|---|---|
| **question** | Does `X9a` have a reproducible decision-event contract and a coherent counterfactual, so it can be judged on its own rather than only inside the `PAIR23` basket? |
| **why it is first** | **Not because it rose — because everything above it closed.** It is the only remaining item that is neither owner-gated nor already measured |
| **why it matters** | `X9a` is the one component of `PAIR23` **not** already double-counted inside `P1/PCT`'s B-MOM OR-gate, and `PAIR23` is this campaign's only `STRUCTURAL` challenger — the one object beating `P1` over the 16 unseen years on money, maxDD, top-5, positive weeks *and* streak |
| **what it is NOT** | a revival of the withdrawn **92 %** claim. That figure is divisor-dependent; the defensible income-matched number is **~64 %** and must not be reinterpreted (§35) |
| **cost** | LOW-MEDIUM. Bounded engineering, no new data |
| **honest EVI** | **MEDIUM.** It unlocks a *decomposition*, not an edge. It creates no new information, and this campaign's record is that decompositions of existing objects have not produced promotions |

## 2. Selective box un-latching — new, from RR_W001, ranked LOW on purpose

RR_W001 found **35–64 %** of its abstention oracle is **regeneration**: trades the policy takes
because the box stops latching once a bad early decision is removed. Those entries are the `r0+1`
bars of latched-out runs and are not decision events at all.

That is a **box-policy** question, and a *different* object from W98, which loosened the box
**uniformly** and got **+$6/week at paired p = 0.940**. Suppressing *specific* early losers so the box
survives is not that experiment.

> **Why LOW anyway.** The selection is **ex-post** — RR_W001's G3 is precisely the finding that we
> cannot identify which early decisions to suppress. Only ~**247** of 1,058 in-window sessions hold a
> latched-out run. **Named because it is new, not because it looks promising.**

## 3. Book coverage — reopened by an audit, ranked LOW on purpose

`runs/RR_W000_LEDGER_AUDIT/` found W119's `E_NO_ENGINE = 0` was **forced by construction** — the lens
is "neither leg held a position", which makes `book_pnl == 0`, and it was counted *inside* the
`book_pnl < 0` population. On the raw mask there are **32 sessions** where no engine was present while
\|RTH move\| was top-decile (mean **452 pts**). *"Coverage is genuinely not the gap"* is **withdrawn**;
coverage is **UNMEASURED**.

> **Why LOW.** `P1/PCT` is **long-only** and declines to trade for stated mechanical reasons, so "no
> engine present" is frequently correct behaviour. Pricing those 32 sessions needs a directional
> oracle — level 2, not available money. n = 32 cannot support a new engine.

## 4–7. The router stack — de-prioritised, and the HMM is NOT RUN

Blocked behind new information, per RR_W001's continuation rule. Two independent reasons the prior
was already low before RR_W001 ran: the owner thesis's **own synthetic experiment** (best state
classifier ≠ best router; HMM routers recovered 4.6–4.9 % of oracle uplift against a direct utility
router's 7.0 %; BOCPD F1 0.251 at ~8 alarms/session), and this repo's record — **W109/W113** real
information with a null policy, twice, and **W99**, whose causal meta-router over 12 rules lost at
every K and never beat the best fixed rule (though it *did* beat random rule choice, so the honest
prior is **dominated, not worthless**).

**If `Router(X + α) ≤ Router(X)`, the latent layer is removed. It is not rescued with HSMM.**

## 8–10. Owner-gated acquisition — recorded once, not re-requested

| lane | what is needed | why it stays open |
|---|---|---|
| **BBO / order flow** | ~**300+** overlapping sessions | currently **71 of 2,131** P1 entries = **3.3 %**, MDE **$564/entry = 4× the mean**. Closed **by data before a feature was written** |
| **Options / dealer gamma** | $80–199/mo | top NQ-side unlock |
| **More event TYPES** | PPI, retail sales, claims, PCE, GDP, ISM, auctions | ~4× the event count → effective N ≈ 280, MDE ≈ 5× the bar. **Better, still short** |
| Market internals (TICK/ADD/TRIN) | — | **no data exists at all** |
| DOM / Level-II | — | owner risk-control **PAUSE** 2026-08-12, **not to be resumed autonomously** |

**These are not re-requested every wave** (§49). They sit here with their required sample size and
MDE stated. **1-minute volume is not order flow and will never be substituted for it.**

## 12. The sealed forward pool — a real constraint

| pool | span | status |
|---|---|---|
| 2022-07-01 → 2026-05-30 | ~200 weeks | **DISCOVERY_CONSUMED** (123 waves) |
| 2026-05-31 → 2026-07-31 | 9 weeks | **BURNED** |
| **≥ 2026-08-01** | **~19 sessions**, +1/day | **VIRGIN / SEALED** |

Opening needs all seven freezes (§4) and a **committed opening spec before any read**.
⚠️ **It can adjudicate a direction, not a magnitude.** Any plan needing the seal to *estimate* an
effect is not a plan. Nothing in this campaign has touched it.

## 13–14. Out of scope for V1

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
| 2026-08-27 | **RR_W001 closed row 1** (router de-prioritised, HMM not run); **the event-response data gate closed row 2 without a wave**; `X9a` becomes the highest-EVI runnable item; selective box un-latching and book coverage added; more-event-types added as an acquisition row. |
