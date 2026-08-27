# EXPERT UNIVERSE — decision-event contracts for the action-value router

_Created 2026-08-27, Phase 0 of the causal-monetization campaign (owner directive §8).
**Inventory and admission decisions only. No result, no economics is produced here.**_

Economics quoted below are **copied** from [`CURRENT_BASELINE.md`](../weekly_edge/CURRENT_BASELINE.md);
that file remains authoritative and nothing here restates it as a new finding.

---

## 0. The admission rule (directive §8)

An object enters the router only if **all five** hold. Existing ≠ admissible.

| | requirement |
|---|---|
| R1 | **Deterministic, frozen rule** — no parameter is re-chosen inside this campaign |
| R2 | **Reproducible opportunity timestamps** — the decision events can be regenerated exactly |
| R3 | **Meaningful economic distinctness** — not a re-weighting of an object already present |
| R4 | **Enough observations for its proposed role** — measured, not asserted |
| R5 | **A coherent counterfactual** — "what if this action had not been taken" is well defined |

> **A dead or falsified family stays out** unless a genuinely new *information surface* changes the
> premise. Being cheap to add is not a reason.

## 1. Verdicts

| object | status | N (decisions) | R1 | R2 | R3 | R4 | R5 | **admitted to RR_W001?** |
|---|---|---|:--:|:--:|:--:|:--:|:--:|---|
| **`P1/PCT`** | INCUMBENT / BASE | **2,401** total · **2,131** in-window | ✅ | ✅ | ✅ | ✅ | ⚠️ needs replay | **YES — PRIMARY** |
| **`XM_CONFLICT`** | ACTIVE COMPONENT | **346** (sequential) / 348 (canonical) | ✅ | ✅ | ✅ | ⚠️ small | ✅ trivial | **YES — SECONDARY** |
| **`FOLLOW_MORNING`** | WATCHLIST | ~**1,058** (1/session) | ✅ | ✅ | ✅ | ✅ | ✅ trivial | **YES — SHADOW EXPERT** |
| **`MIRROR_CONT`** | WATCHLIST / standing control | **21 weeks**, event-driven | ✅ | ✅ | ⚠️ | ❌ **too few** | ✅ | **NO — retained as MANDATORY CONTROL** |
| **`PAIR23`** (2 BMOM : 3 X9a) | STRUCTURAL CHALLENGER | basket, not an event stream | ✅ | ⚠️ | ❌ **fails R3 as one object** | — | ⚠️ | **NOT AS A UNIT** — see §3 |
| `BMOM` (channel) | inside P1/PCT's OR-gate | — | ✅ | ⚠️ | ❌ **already inside P1/PCT** | — | ⚠️ | **NO — double-counting** |
| `X9a` | uncertified sleeve | — | ✅ | ⚠️ | ✅ | ? | ? | **DEFERRED** — see §3 |
| **`CASH`** | — | every event | ✅ | ✅ | ✅ | ✅ | ✅ | **YES — cash is a real expert** |
| `NETFUSE_1` · `VWAP_RECLAIM` · trend-day state layer · volume exhaustion · AFT-as-target · cross-market intraday support · turnover | **DEAD / FALSIFIED** | — | — | — | — | — | — | **NO** |
| campaign #3 Products A/B, Solar Wave objects | HISTORICAL, closed Aug 2026 | — | — | — | — | — | — | **NO** — different campaign, different substrate |

---

## 2. Decision-event contracts (directive §6)

### 2.1 `P1/PCT` — the hard case, and the reason RR_W001 exists

| field | value |
|---|---|
| `expert_id` | `P1PCT` |
| `family_id` | `SOLAR_RATCHET_ENSEMBLE` |
| **eligibility** | the desired-direction array changes to a new non-zero value **and** the session box has not latched |
| **decision timestamp** | the **open of bar `i`** |
| **information cutoff** | **bar `i−1` close.** `gfills` reads `dir_arr[i-1]`; bars are END-stamped, so the bar stamped `i−1` closed before bar `i` opened |
| **allowed actions (V1)** | `ACCEPT` (baseline) · `ABSTAIN` |
| **allowed actions (V1 diagnostic only)** | qty ∈ {0, 1, 2} where the baseline state makes 2 mechanically reachable |
| **internal state at decision** | `spnl` (session box P&L **per contract**), `stopped` (a **latch**), `p`, `u`, `epx`, entry ordinal, causal quality score, `size_at_entry` |
| **exit semantics** | **FROZEN.** Box halt −$1,300 / target +$1,000 per contract; forced flat at `lb` (session last bar). The router never touches an open position (directive §7) |
| **does intervention change future eligibility?** | **YES, through two independent channels** — see below |
| **counterfactual replay required?** | **YES. A trade's historical PnL is NOT its action value.** |
| direction | **long-only** — measured: `p == −1` on **0.00 %** of bars |

> #### The two path-dependence channels, both measured — and they are ONE-WAY, which matters
>
> **Channel 1 — the session box latch. Changes the SCHEDULE. Within-session only.**
> `gfills` (`research/weekly_edge/src/run_we_w98.py:59`) carries `spnl` and `stopped` across bars and
> resets only at `fb[i]`. Once `stopped` latches, `want` is forced to 0 for the rest of the session.
> **Measured: there are 3,368 contiguous same-sign signal runs but only 2,401 trades — 967 runs
> (28.7 %) never become trades because the box had already latched.** Removing an earlier entry
> changes `spnl`, which changes whether later runs in that session survive.
>
> **Channel 2 — the causal quality score. Changes SIZE only. Propagates across sessions.**
> `causal_score` (`run_we_w37.py:34`) scores entry *j* from the quantiles of the **prior 250 entries**
> (`WIN = 250`, exclusive of *j*). Deleting an entry shifts every later entry's window membership and
> can change its **size**. This is the mechanism behind the parity run's "sizing warm-up" residual.
>
> #### ⚠️ Channel 2 does NOT feed back into Channel 1, and that is an algebraic fact
> Under `per_ctr=True` the box accumulates `spnl += pnl/u`, and
> `pnl/u = p·(o[i] − epx)·PV − COMM_RT` **contains no `u`.** The session box is therefore
> **size-invariant**, so the trade *schedule* cannot depend on the size array.
> **Verified numerically: `fills_daily` (which has no sizing at all) and `gfills` (which does)
> produce the same 2,401 trades.**
>
> **Consequence for the ledger design — the two channels are cleanly separable:**
> toggling an action changes the **schedule** through Channel 1 only, and the changed schedule then
> changes **sizes** through Channel 2 downstream. There is no circular dependence to resolve, so a
> single forward recompute is exact rather than a fixed point.

**The `ABSTAIN` intervention is defined as follows and is preregistered, not chosen from results:**

> Zero the desired-direction array over **the entire contiguous same-sign, session-bounded run** that
> the entry belongs to, then **recompute the whole downstream chain** — `fills_daily` → `causal_score`
> → `size_at_entry` → `gfills` — on the same realized price path.
>
> **Why the whole run and not one bar.** Zeroing a single bar would let the expert re-enter one bar
> later, which is a *delay*, not an abstention. Zeroing the run means "the expert did not act on this
> signal"; the next change of desired direction is a genuinely new decision event.

**One further convention must be fixed in the spec, because the incumbent has a choice here.**
The certified chain builds `causal_score` from the **size-1 `fills_daily` schedule** and then reuses
it — W98 declares this an isolation choice and ran the self-consistent rebuild as its own falsifier
(result: identical to the last dollar **on the baseline**). On a *counterfactual* the two diverge.

| arm | quality score | status in RR_W001 |
|---|---|---|
| **SELF-CONSISTENT** | recomputed from the **counterfactual** entry schedule | **PRIMARY** — it is what the strategy would actually have done |
| **FROZEN** | held at its baseline values | **SENSITIVITY** — isolates Channel 1 from Channel 2 |

Reporting both is what makes the Channel-1 / Channel-2 decomposition an *observation* rather than an
assumption. **Neither is chosen after seeing the result.**

**Feasibility is measured, not assumed** (engineering reconnaissance, 2026-08-27):

| | |
|---|---|
| `load_deep` substrate | 1,620,044 bars · 1,187 sessions |
| **`gfills` full pass** | **0.23 s** · byte-identical on repeat (`same()` returns `True`) |
| **one full recompute chain** (`fills_daily` + `causal_score` + `gfills`) | **0.82 s** |
| **all 2,401 toggles, FULL recompute** | **≈ 33 minutes** |

> ### **No approximation is required.** Full-horizon replay is cheap enough to run for every entry,
> so **both** channels propagate exactly and no session-scoping compromise enters the ledger.

**Baseline-replay certification (mandatory before any interpretation, directive §10):**
the replay harness must reproduce the frozen engine **byte-identically**. The checker already exists
— `run_we_w98.same()` compares direction, size, entry, exit and P&L to 1e-9. **If baseline replay
does not reproduce, the simulator is fixed and nothing is interpreted.**

> ⚠️ **Two in-window counts exist in the certified chain and they are NOT interchangeable.**
> The **entry-timestamp** filter (`A ≤ et < B`) yields **2,139** trades and is what feeds
> `causal_score`. The **session-start** filter (`in_win[sid[entry_bar]]`) yields **2,131** and is what
> produced every published P1/PCT headline. **RR_W001 reports on 2,131 for continuity with
> `CURRENT_BASELINE` and W122, and states the filter by name in every table.**

### 2.2 `XM_CONFLICT` — the easy case

| field | value |
|---|---|
| `expert_id` | `XM_CONFLICT` |
| `family_id` | `CROSS_MARKET_OPENING_AUCTION` |
| **eligibility** | at 09:45 ET, the ES/RTY/YM composite has the **opposite** sign to NQ's opening drive (~34 % of sessions) **and** a 15:45/15:46 exit bar exists |
| **decision timestamp** | **09:45 ET** |
| **information cutoff** | 09:45 close — `sign(close₀₉₄₅ − open of the 09:31 bar)` |
| **allowed actions (V1)** | `ACCEPT` at qty 1 · `ABSTAIN` |
| **internal state** | none. No box, no latch, no prior-trade dependence |
| **exit semantics** | fill at the 09:46 open, hold to 15:45, **no stop** |
| **changes future eligibility?** | **NO** |
| **counterfactual** | **trivial and exact** — `ABSTAIN` ⇒ 0. `ΔU = −(realized trade PnL)` |
| **existing artifact** | `research/weekly_edge/ninjascript/reference/xm_reference_decisions.csv` is **already a per-decision ledger**: `session_date, anchor_px, decision_px, entry_px, exit_px_close1545, exit_px_open1546, nq_drive, broad_composite, conflict_flag, desired_direction, disqualified, pnl_research, pnl_nt8_convention` |

> ⚠️ **Sizing is NOT a V1 action for XM.** Directive §11 is explicit: conditional larger sizing is a
> later capital-allocation question and **must not be data-mined from 346 observations.**
> ⚠️ **The early-close guard is part of the frozen object.** Sessions with no 15:45 exit bar are
> declined — that is what `_v2` fixed and what `_v1` got wrong at −$225/trade over 15 holidays.

### 2.3 `FOLLOW_MORNING` — admitted as a shadow expert, not as a promotion

| field | value |
|---|---|
| `expert_id` | `FOLLOW_MORNING` |
| `family_id` | `INTRADAY_CONTINUATION` |
| **eligibility** | every session with the required bars |
| **decision timestamp** | **11:49 open** (signal read at the **11:29 close** vs the 09:31 open) |
| **allowed actions (V1)** | `ACCEPT` (long if 11:29 close > 09:31 open, else short) · `ABSTAIN` |
| **exit semantics** | 15:44, size 1 |
| **changes future eligibility?** | **NO** — one shot per session |
| **counterfactual** | trivial |

> **Why admitted despite failing portfolio promotion.** Its standalone evidence is CONFIRMED
> ($179/trade, 55.00 %, 96.3rd percentile against the corrected best-of-15 shared-sign bar), it has
> ~1,058 clean decisions, and it is **economically the opposite of XM**: `XM_CONFLICT` diversifies the
> book's **losses**; `FOLLOW_MORNING` diversifies its **wins** (+$66 on book-losing weeks where chance
> gives +$842 — the **9.9th percentile**). That contrast is precisely what an action-value router
> claims to be able to exploit, so it is the sharpest available test of whether the router adds
> anything. **Admitting it as a shadow expert is not a promotion and does not change its status.**
> Its known portfolio failure is the null the router must beat, not a problem to be routed away.

### 2.4 `MIRROR_CONT` — excluded as an expert, mandatory as a control

Fails **R4**: its value is **tail, not average** (tail beta −1.861, 0.9th percentile) and it rests on
**21 weeks**. Routing an object whose entire claim is a 21-week tail would be a sample-size error, and
directive §20 requires classifying that as `UNDERPOWERED`, not as information.

> It is retained as the standing **`MIRROR_CONTINUATION_CONTROL`** — the same-trigger continuation
> mirror that **every** future fade/reversal construction must be measured against (W118: reversal
> **−$405/trade** vs mirror **+$374** at the identical trigger bars).

### 2.5 `CASH`

Cash is an explicit action at every decision event with `ΔU = 0` by construction, zero cost and zero
exposure. It is what `ABSTAIN` allocates to. Making it an expert rather than an absence is what lets
the router's abstentions be scored on the same footing as its acceptances.

---

## 3. `PAIR23`, and why it is not admitted as one object

`PAIR23` is a **fixed-weight static basket — 2 `BMOM` : 3 `X9a`, 5 nominal contracts** — not a
distinct decision-event generator. Admitting it as a single "expert" would put a *portfolio* inside
the router and make the router's own allocation unattributable (directive §43 forbids exactly this
kind of joint retune).

**Three separate facts, kept separate:**

1. **Its status is real.** It is the one object beating `P1` over the 16 unseen years on money,
   maxDD, top-5, positive weeks *and* streak. `STRUCTURAL` is earned.
2. **Its headline is withdrawn.** The old "**92 %**" figure is **divisor-dependent**; the defensible
   income-matched number is **~64 %**, and a separate error once put the **1:2** row's numbers under
   the **2:3** label. **Do not reinterpret or resurrect the 92 % claim** (directive §35).
3. **`BMOM` is already inside `P1/PCT`** — P1/PCT is OR-gated with the B-MOM channel. Adding `BMOM`
   as an independent expert would double-count it, and ρ(XM, B-MOM) = **+0.446** is already a known
   coupling.

**Disposition.** `X9a` is the only genuinely un-double-counted component. It is **DEFERRED, not
rejected**: admitting it requires first establishing a reproducible decision-event contract and a
coherent counterfactual, which no committed artifact currently supplies. **That is a bounded
engineering task, and it is recorded on the frontier rather than done inside RR_W001** — adding a new
expert while measuring the ledger would confound the two.

---

## 4. Sample-size discipline (directive §20) — the binding N for each role

**Raw minute rows are not the sample size.** What follows is the *economic* N.

| expert | decisions | independent clusters | modelling licence |
|---|---|---|---|
| `P1/PCT` | **2,131** in-window | ~**1,058 sessions** / **213 weeks**; multiple entries per session are **not** independent | regularized linear **and** a bounded shallow nonlinear challenger |
| `XM_CONFLICT` | **346** | 346 sessions, ≈1.6/week | **regularized linear only.** A depth-3 tree search on 346 rows is prohibited |
| `FOLLOW_MORNING` | ~**1,058** | 1,058 sessions | regularized linear; shallow nonlinear only if P1's arm justifies it |
| event-response subsets | *effective N = distinct event sessions* | **not** downstream P1 entries | severe shrinkage; cluster by event day |

> ⚠️ **12 P1 opportunities after one CPI print are one macro event, not twelve.** Every inference
> that conditions on a scheduled release clusters at the **event session**.

---

## 5. What is NOT in the universe, and why that is a decision

- **No new expert is invented in this campaign phase.** Directive §43 requires alternating freezes:
  freeze the expert set → test the router. Discovering a new expert *while* measuring the router
  would make both unattributable.
- **Dead families stay dead.** `NETFUSE_1`, `VWAP_RECLAIM`, the trend-day state layer, volume
  exhaustion, AFT-as-a-target, cross-market intraday support and turnover are closed. A **new
  information surface** — not a new model — is the only thing that reopens any of them.
- **Campaign #3 / Solar Wave / OTR objects are out.** Different campaign, different substrate,
  closed. Mixing them in would violate directive §52's substrate rule.

## 6. Frozen for RR_W001

```
EXPERTS  = { P1PCT (primary), XM_CONFLICT (secondary), FOLLOW_MORNING (shadow), CASH }
CONTROLS = { MIRROR_CONTINUATION_CONTROL, matched-random router, matched-exposure,
             always-accept, always-cash, expert-internal score }
DEFERRED = { X9a }
SUBSTRATE = load_deep(..., extend=True)   -- UNCHANGED (directive §52)
WINDOW    = 2022-07-01 -> 2026-08-01      -- the seal is NOT touched
COST      = $4.36/ctrRT commission + candidate-specific modelled spread (P1 $14.44, XM $12.50)
```

**Nothing above changes any object's status.** `P1/PCT` remains the base, `XM_CONFLICT` the active
component, `PAIR23` a structural challenger, `MIRROR_CONT` and `FOLLOW_MORNING` watchlist.
Admission to a research ledger is not promotion.
