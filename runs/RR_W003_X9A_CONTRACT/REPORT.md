# RR_W003 — X9a: TWO OBJECTS, ONE NAME, AND THE FRONTIER'S PREMISE WAS FALSE

| | |
|---|---|
| **run class** | **ENGINEERING_ONLY / AUDIT** — nothing selected, tuned or promoted; no alpha budget consumed |
| date | 2026-08-27 |
| code | `run_rr_w003_x9a.py` (rebuild + reproduction gate + contract) · `_b` (provenance reconciliation + admission) |
| question | frontier row 1 — does `X9a` have a reproducible decision-event contract and a coherent counterfactual, so it can be judged on its own rather than only inside `PAIR23`? |
| seal | untouched |

> ### **VERDICT: `X9a` is NOT ADMITTED as a standalone expert — under either of the two readings
> ### of that name.**
> ### And the frontier's premise — *"`X9a` is the one component of `PAIR23` not already
> ### double-counted inside `P1/PCT`'s B-MOM OR-gate"* — **is false. It is the MOST
> ### double-counted component: it contains the incumbent's entire ensemble by construction.**

---

## 1. The reproduction gate passed exactly

W72's committed era table, rebuilt from `build_channels` and `sfills` on the deep 2006–2026
substrate (6,466,783 bars / 5,420 sessions):

| era | trades | W72 | $/trade | W72 | t | W72 | PF | W72 | |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2006-2021 | **3,948** | 3,948 | **28.6** | 28.6 | **1.83** | 1.83 | **1.105** | 1.105 | **OK** |
| 2022-2026 | **950** | 950 | **123.0** | 123.0 | **1.05** | 1.05 | **1.095** | 1.095 | **OK** |

**All four figures in both eras reproduce to the printed precision.** The channel is the object W72
measured.

## 2. The decision-event contract — for the raw channel

`X9a_disp_sessanchor` is a **latched per-bar direction channel**, structurally identical to
`P1/PCT`'s signal array, so RR_W001's replay machinery applies unchanged.

| field | value |
|---|---|
| `expert_id` | `X9A_DISP_SESSANCHOR` |
| `family_id` | `DISPLACEMENT_CHANNEL` |
| eligibility | the latched channel changes to a new non-zero value |
| decision timestamp | the **open of bar `i`** |
| information cutoff | close of bar `i−1` — `sfills` reads `dir_arr[i-1]`, exactly as `gfills` does |
| allowed actions | ACCEPT / ABSTAIN |
| exits | **FROZEN** — session box halt −$1,300 / target +$1,000; flat 21 minutes before session end |
| path dependent | **YES** — the same session-box latch as `P1/PCT` |
| counterfactual | **WELL DEFINED** — suppress the contiguous run, replay the frozen policy |

**Measured:** 5,105 contiguous same-sign session-bounded runs → 4,898 trades (207 runs never become
trades because the box had already latched); **842 trades in the campaign-#7 window**; direction
balance **52.7 % long / 47.3 % short — two-sided, unlike long-only `P1/PCT`.**

## 3. The finding — there are two objects named `X9a`

RR_W003 measured weekly ρ(`P1/PCT`, `X9a`) = **+0.07**. W88 recorded **+0.613** and called it *"too
correlated"*. **Both numbers are correct. They describe different objects.**

W88's figures reproduce exactly from its own source (`WE_W79_CLIQUE/out/members.csv`): daily
**+0.6732** vs W88's +0.673, weekly **+0.6131** vs +0.613, BMOM–X9a **+0.0094** vs +0.009.

| | **STORED** `w72:X9a` | **REBUILT** W72 raw channel |
|---|---:|---:|
| net over 1,058 campaign sessions | **$233,781** | **$61,404** |
| sessions active | 580 | 842 |
| daily sd | 2,077.8 | 3,137.6 |
| **weekly ρ with `P1/PCT`** | **+0.6131** | **+0.0697** |
| weekly ρ with `BMOM` | +0.0094 | — |

> ### **Daily ρ between the two objects called `X9a` is +0.1527.** They are not the same thing.

### Why they differ: the execution wrapper, not the signal

```
run_we_w76.py:167-172   every w72 stream is built as   long_obj(TG_for(channel))
run_we_w76.py:123-132   TG_for(chan) = hyst(0.7086 * Tp + 2.83 * chan)
run_we_w76.py:146-153   long_obj(TGx) = the 13-member Solar ensemble vote, the tilt,
                        fills_daily, causal_score, quality sizing, fills_qexit
run_we_w76.py:156-157   S['P1'] = long_obj(TG_for(bmom))        <- the SAME function
```

> ### **The stored `w72:X9a` is `P1`'s ENTIRE MACHINERY with `X9a` substituted for B-MOM as one
> ### additive term inside the tilt.** It is a **`P1` variant**, not a standalone strategy.

W72's era table — the one this run reproduced on all four figures — measured something else
entirely: the **raw two-sided channel through `sfills`** with a session box
(`run_we_w72b.py:251`). That is the whole explanation for +0.613 versus +0.07. The stored object
shares the Solar ensemble with the incumbent, so of course it correlates with it.

## 4. What this means for `PAIR23`

`PAIR23` is *"2 BMOM : 3 X9a"*, and its members come from `WE_W79_CLIQUE/out/members.csv`:

| member | source | what it actually is |
|---|---|---|
| `BMOM` | `d['BMOM']` = `sfills(raw B-MOM channel)` | **a raw channel** |
| `X9a` | `d['w72:X9a']` = `long_obj(TG_for(X9a))` | **a `P1` variant** |

> ### **`PAIR23` is not a basket of two independent channel sleeves.** It is a **raw B-MOM channel
> ### plus a full `P1`-variant.** And ρ(BMOM, X9a) = **+0.009 "INDEPENDENT"** is exactly what one
> ### expects when comparing a two-sided raw channel against a long-only Solar ensemble — **it is a
> ### statement about the two WRAPPERS, not about two signals.**

**Nothing measured about `PAIR23` is withdrawn.** Its economics stand, its `STRUCTURAL` label stands,
and the 16-unseen-year result stands. What changes is **what it is**, and therefore what a
decomposition of it could ever have meant.

## 5. Admission verdict — `EXPERT_UNIVERSE` criterion R3

| candidate | weekly ρ with `P1/PCT` | R3 distinct? | admitted? |
|---|---:|---|---|
| **STORED `w72:X9a`** — the actual `PAIR23` member | **+0.6131** | **NO** | **NO** |
| REBUILT W72 raw channel | +0.0697 | yes | **NO — see below** |

**The `PAIR23` member fails R3 decisively.** R3 requires that a candidate not be a re-weighting of an
object already present. This one **contains the incumbent's entire ensemble by construction**, and
+0.613 measures that fact.

**The raw channel passes R3 but is not the object the question asked about.** Admitting it would not
decompose `PAIR23`, because `PAIR23` does not contain it. On its own it earns **$61,404** over the
campaign window at **t = 1.05** in W72's own 2022–26 era row — that is a channel, not a candidate.

## 6. Constraints this wave adds

1. **A NAME IS NOT AN OBJECT.** Two economically different objects carried the identifier `X9a` for
   many waves — one correlating **+0.07** with the incumbent, the other **+0.613**. Any future
   reference to a stream by name must resolve to a **construction**: signal *and* wrapper *and*
   cost model *and* window.
2. **A stored daily stream is not the strategy whose name it carries.** `streams_extended.csv`'s
   `w72:*` columns are all `long_obj(TG_for(·))` — every one of them is a `P1` variant with a
   different channel in the tilt, not the channel standalone. **The same caution applies to
   `w72:X1 … X9b`, which were never audited here.**
3. **A low correlation between two objects can be a fact about their WRAPPERS.** ρ(BMOM, X9a) =
   +0.009 was read as evidence of two independent signals. It is at least as consistent with one raw
   two-sided channel versus one long-only ensemble.

## 7. Continuation

| | |
|---|---|
| **outcome** | `X9a` **NOT ADMITTED**; frontier row 1 **closed** |
| **`PAIR23`** | status unchanged (`STRUCTURAL` challenger), **description corrected** in `CURRENT_BASELINE` and `EXPERT_UNIVERSE` |
| **next** | frontier row 2 — **higher-timeframe state**, the last surface still marked `LIGHT` |
| **promoted / demoted** | **nothing** |
