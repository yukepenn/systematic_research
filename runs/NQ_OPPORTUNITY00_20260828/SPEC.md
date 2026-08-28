# SPEC — `NQ_OPPORTUNITY00` · DATA / STATE CAPABILITY ONLY

**COMMIT E. Committed before any measurement.** Executes the Program-B amendment.

| | |
|---|---|
| **run class** | `DIAGNOSTIC` — state capability, **zero alpha budget** |
| **question** | What informational / market-state space exists where the incumbent is **absent**? |
| **LIVE ENABLED** | **NO** |

> ## ⛔ **`OPPORTUNITY00` MAY NOT:** compute candidate strategy P&L · rank candidate rules by
> subsequent return · choose a threshold from a forward outcome · optimise stops or entries · fit
> any model · evaluate feature→future-return correlation · compare event definitions by
> profitability.
> ## ⛔ **AND IT MAY NOT USE THE WORDS** alpha · edge · candidate · profitable · Sharpe · expected
> return **of any state it finds.** Not yet.

---

## 1. Lane status entering this run

| lane | status |
|---|---|
| **A · FLAT-SESSION COVERAGE** | ✅ **LIVE.** The population is `420 / 1,058 = 39.7 %` |
| ⛔ ~~**B · SESSION-LENGTH COVERAGE**~~ | **CLOSED BEFORE MEASUREMENT** — see §2. The premise was false |

## 2. ⛔ LANE B IS CLOSED, on activity facts and on prior power closures

**B-bar (price/volume off-hours) — the lane was never open, because the object already trades there.**

| | evidence |
|---|---|
| substrate | **1,620,044 bars / 1,187 sessions**, median **1,380 bars = 23 h**; **1,380 of 1,440** minutes-of-day present; the only missing 60 are **17:01–18:00 ET**, the CME maintenance break. **Non-zero volume in all 24 hour buckets** |
| P1's clock | **there is no RTH gate anywhere in `votes()`.** The entire window spec is two lines — `blocked` (last 30 min) and `flatm` (last 21 min) measured back from `sess_end`, covering **2.20 %** and **1.54 %** of bars. `gfills` has **no `block` parameter at all** |
| the tape | **1,349 of 2,131 in-window entries (63.3 %) already fill outside RTH** — 20.6 % in 18:00–23:59, 27.9 % in 00:00–06:59. Entries span **943 distinct minutes** and all 23 traded hours |

**B-quote (BBO-conditioned off-hours) — `CLOSED-BY-DATA` and independently `CLOSED-BY-POWER`.**
Only **104 of 1,058** sessions have materialized NQ quotes (**9.8 %**); the earliest NQ quote date is
**2025-08-10**, so **~96 % of P1's evaluated history has no bid/ask and cannot acquire any**; order
flow → P1 action value is already recorded **`CLOSED-BY-POWER`** (*needs 998 sessions; 713 exist —
unreachable at any coverage*); and ⚠️ **the one protected falsifier has the wrong hours** — all 19
blind-pool sessions carry day labels 01–17 only, covering ET 00:00–16:59 and **none of 18:00–23:59**,
so it **physically cannot falsify an evening mechanism**, quite apart from its MDE being ~12× short.

> ### **RECORDED, NOT PROMOTED — the one thing that survives from Lane B.**
> Overnight, `bmom` is hard-pinned to zero outside **09:32–15:56**, and its **2.830** contribution
> falls **0.170 short** of the **3.000** entry threshold in any case. **So ~63 % of P1's decisions
> are taken with one of its two combiner inputs structurally dead.** Off-hours is not un-tradable —
> it is **under-informed**. ⛔ **This is a FUTURE HYPOTHESIS requiring its own preregistration. It is
> not a lane in this run, and it may not be acted on here.**

## 3. LANE A — the exact population, derived not hardcoded

`P1_ACTIVE` / `P1_FLAT` partition of the canonical **1,058** in-window trading sessions, keyed on
**`session_id`** (⚠️ never `session_date` — NQ sessions span two calendar dates;
`research_sdk/test_session_unit.py` enforces this). Sources: `runs/RR_W001_ACTION_VALUE_LEDGER/out/
ledger_p1pct.csv` (`in_window_session == True`) and `runs/WE_W119_BOOKLOSS/out/book_loss_ledger.csv`.

**Asserted in code:** total = 1,058 · active = 638 · flat = 420 · every active session ∈ the book
session set · the book's own `p1_pnl != 0` count independently equals 638. ⛔ Portfolio-B flatness is
**not** used. ⛔ No session is classified using a future outcome.

## 4. A1 — why does P1 not arm? Mechanically, from the code

The arming test is a single identity, hard-coded in `votes()` and not overridable by any caller:

```
K · g · (1 + dL)  >=  16          # 32 voters = 4 MEMBERS x 4 QS x 2 delta-gate
   K  = member sets with tg > 0                  (0..4)   -- per-set hysteresis, entry M >= 3.0
   g  = throttle rungs passing                   (1..4)   -- QS = [None, 0.7, 0.8, 0.9]
   dL = lagged delta gate                        (0 or 1)
```

Feasible arming tuples: `(2,4,2) (3,3,2) (3,4,2) (4,2,2) (4,3,2) (4,4,1) (4,4,2)`.

**Deliverable `P1_FLAT_CAUSE_DECOMPOSITION.csv`** — for each of the 420 flat sessions, the
session-max `(K, g, dL)` and the **mutually exclusive** binding cause, in this fixed precedence:

1. `K_max == 0` — no member set ever long
2. `K_max == 1` — one set only; max attainable vote is `1·4·2 = 8/32 = 0.25`
3. `g_max == 1` — throttle wall (`ratio < 0.7` with `norm > 0`) all session
4. `NEAR` — `K_max ≥ 2` and `g_max ≥ 2` but the product never reached 16
5. `OTHER` — none of the above; enumerated individually, not bucketed

Report exclusive counts, overlaps, first minute each prerequisite came closest, and time spent one
condition short. **Descriptive only. No returns.**

## 5. A2 — arming distance

The trigger sits on continuous quantities, so a distance **is** mathematically definable and is
**frozen here** as the two the code actually uses:

```
vote_max(session)   = max over bars of  K·g·(1+dL) / 16        # 1.0 = armed
M_max(session)      = max over bars and member sets of  M      # entry threshold is 3.0
                      M = 0.7086*Tp + 2.83*chan
```

⛔ **No alternative distance definition is compared, and none is selected by looking at returns.**
Reported for flat vs active: closest approach, minutes within 10 % of the boundary, time-of-day of
nearest approach.

> ### ⛔ **A5 — THIS AUTHORISES NO THRESHOLD CHANGE.**
> It is already **measured** that lowering the hysteresis entry from **3.0 → 1.0** takes flats
> **420 → 145** and trades **2,401 → 4,840**, i.e. **275 of the 420 flat sessions are caused by the
> entry threshold itself.** That figure is recorded as **`P1_NEAR_ARM_STATE EXISTS`** and is
> **the single most tempting number in this campaign.** It authorises **NOTHING** — no 0.95× /
> 0.90× / 0.75× threshold, no different box, no different sigma, no "P1 aggressive mode". Acting on
> it would be the cleanest possible post-hoc threshold mining, and it is **forbidden**.

## 6. A3 / A4 — is there anything there? (the only genuinely unmeasured question)

Already-certified causal descriptors only — ⛔ **no new feature zoo**: realised range, realised
variation, directional path length, causal swing-transition count, overnight range, opening range,
count of ≥ `T`-tick excursions.

**`T` is frozen NOW, before any flat-vs-active comparison: `T = 40 ticks = 10.00 NQ points = $200`.**
Rationale, economic and outcome-free: P1's realised mean net is **$139.33/trade** on top of
**$18.80/ctrRT** of modelled friction, so an opportunity must offer ≳ **$158 gross ≈ 31.6 ticks** of
capture; **40 ticks** is the next round figure above it. **Chosen from the incumbent's cost and edge
structure, not from any flat-session statistic.**

⛔ **Forbidden outright:** "profit available if perfectly traded" · future-aware ZigZag · oracle
entry/exit · maximum achievable P&L · best possible trade count · any hindsight turning point.

## 7. Continuation rules — frozen BEFORE the result

Lane A proceeds to an economic V1 **only if ALL FIVE hold**:

| | rule |
|---|---|
| **A-C1** | **≥ 40 % of P1-flat sessions reach ≥ 60 % of the median P1-ACTIVE-session realised high-low range.** *Economic meaning:* below 60 % of a typical opportunity-bearing session's path, a session cannot host one P1-sized opportunity; and if fewer than 2 in 5 flat sessions clear that, the flat population is **structurally quiet** and searching it is not economically rational. Both numbers are anchored to **active-session path geometry**, never to future P&L |
| **A-C2** | a clearly identifiable state family exists that is **NOT** equivalent to loosening an existing P1 parameter **AND is NOT the already-falsified mirrored short leg** |
| **A-C3** | it is computable **causally** from certified fields |
| **A-C4** | it occurs on **≥ 85 of the 1,058 sessions (8.0 %)**. *Economic meaning:* at P1's own ~$465/active-session economics, 85 newly active sessions is ≈ **$185/week** before any dilution — >13 % of P1's $1,393.57 raw weekly. Below that, even a perfect engine cannot move the frontier |
| **A-C5** | a distinct economic **mechanism** can be stated **before** seeing its future return |

⚠️ **A-C2 IS EXPECTED TO BE THE BINDING CONSTRAINT, AND THAT IS RECORDED IN ADVANCE.** The two
largest measured explanations of flatness are already disqualified: the **entry threshold** (§5,
forbidden) and the **mirrored short leg** — armed on **343 of the 420 flat sessions**, but
**already falsified five times** (W38/39/61/75/78), building `NETFUSE_1`, which is listed
**DEAD / FALSIFIED**, and with W91 measuring *"the mirrored Solar vote is worth NOTHING short."*
**Neither may be resurrected.** If nothing else survives, Lane A closes — that is a legitimate,
cheap result, not a failure to try.

## 8. Allowed verdicts

**Lane A:** `FLAT-SESSIONS STRUCTURALLY QUIET` · `FLAT-SESSIONS CONTAIN MATERIAL MOVEMENT BUT P1
DOES NOT ARM` · `P1 NEAR-ARM STATES COMMON` · `P1-FLAT STATE SPACE DISTINCT` · `DATA INSUFFICIENT`.
**Lane B:** pre-closed — `OFF-HOURS ALREADY TRADED (NOT A GAP)` + `B-QUOTE CLOSED-BY-DATA/POWER`.

## 9. Protected assets — untouched by this run

⛔ ≥2026-08-01 seal (asserted `max(date) < 2026-08-01` in code) · `ESNQ_BLIND_EFFECTIVE_14` ·
NQ BBO **19** (⚠️ `EFFECTIVE_14` is a **strict subset** — spending the BBO pool consumes 15/19 of the
ESNQ asset; **they are not two independent shots**) · 20 unread ES BBO · 141-session Last-only pool ·
**the 21 ungoverned evening-only quote dates**, newly identified and **not** to be globbed.

**`OPPORTUNITY00` reads only the 1-minute Last substrate and the two certified ledgers. It opens no
quote file.**

## 10. Required answers (§40)

**Q1** why exactly is P1 flat on 420 sessions · **Q2** are those sessions objectively quieter, or is
there movement without a trigger · **Q3** how many spend substantial time near the arming boundary ·
**Q4** is there a genuinely distinct causal state family worth an alpha test · **Q5** what fraction
of the 39.7 % hole could it plausibly address **before** knowing returns · **Q6–Q9** answered
pre-emptively in §2 (Lane B closed) · **Q10** which lanes, if any, may proceed.

**No alpha claims. `LIVE ENABLED = NO`.**
