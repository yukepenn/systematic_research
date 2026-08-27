# RR_W001 — THE ACTION-VALUE LEDGER

| | |
|---|---|
| spec | `spec.yaml`, committed **`f3dd814`** before this code existed · `prereg_guard --run-class DIAGNOSTIC` **PASS** |
| code | `run_rr_w001.py` (ledger) · `_b` (oracles + gates) · `_c` (bootstrap) · `_d` (matched-random placebo) |
| window | 2022-07-01 → 2026-08-01 · **the ≥ 2026-08-01 VIRGIN seal was not touched** |
| evidence status | **`DISCOVERY_CONSUMED`** throughout · 2026-05-31 → 07-31 is **`DIRECTLY_BURNED`** (67 events, 3.14 %) |
| model trials | **0.** Nothing was fitted, selected or tuned |
| promoted | **nothing** |

---

## 0. Verdict

> ### **GATES: G1 PASS · G2 PASS-ON-CLAUSE / FAIL-ON-RATIONALE · G3 FAIL · G4 VOID**
> ### The preregistered rule is `gates_ALL_must_be_cleared`. **It is not met.**
> ### Per `outcomes_fixed_in_advance`, the router branch is **DE-PRIORITISED**, the next wave is
> ### **EVENT RESPONSE**, and **the HMM is not run.**

**Only one of four gates is a clean pass**, and an independent five-lens adversarial audit found the
other three compromised in ways that all point the same direction. The reason for de-prioritising is
not merely the letter of a failed gate — §4 gives the substantive case.

**But the object was worth building.** The ledger is certified correct, and it produced findings no
cheaper instrument could have produced, including two that revise how this repo should read its own
incumbent.

---

## 1. The replay is correct — and this was attacked hard

Five independent auditors were told to refute, not to agree. All five returned
`SURVIVES_WITH_CAVEATS`; **none found a defect in the replay itself.** What they confirmed:

| check | result |
|---|---|
| ABSTAIN is a clean bijection | **no run carries two baseline trades** — 3,368 runs, 2,401 trades, 967 latched-out, 0 runs with two |
| no boundary leak | 0 runs cross a session boundary; 0 extend outside their session |
| the intervention starts exactly at the cutoff | **`r0 == entry_bar − 1` on all 2,401 trades**; bars zeroed strictly before the cutoff: **max 0** |
| pre-decision behaviour unchanged | 35 full-engine replays (random + largest \|ΔU\| + largest cross-session): **0 non-identical pre-decision trades** |
| session-scoped replay == full pass | **bit-equal**, not merely within 1e-9 |
| sign convention | max error **2.05e-12** across all 2,401 rows |
| information cutoff | substrate rebuilt truncated at 2025-12-31: **`p` identical on all 1,413,487 prefix bars**, all five size-score features max\|diff\| **0.000e+00** |
| the linear re-pricing shortcut | exactly equal to a full re-replay on all 35 sampled rows |

**Two real bugs were found and both are fixed**, with the corrected figures used throughout below:

1. **XM double-charged the modelled spread.** `export_xm_reference.py:117` already charges
   `COMM_RT + $12.50 = $16.86` — verified as a constant `$16.8600` gross-minus-net on all 346 rows.
   An earlier version of `_b` subtracted $12.50 again. **XM net is $199,766 / $577.36 per trade, not
   $195,441 / $564.86.** The ~$0.95 gap between the file's two P&L columns that prompted the error is
   the **15:45-close vs 15:46-open exit convention**, not a missing spread.
2. **The level-B multiple mixed populations** — the enumerated-session *gain* was divided by the
   *all-session* net. **Like-for-like it is 3.244×, not 3.624×.**

---

## 2. What the ledger measured

### 2.1 The action-value distribution — `LOCAL_MARGINAL_ACTION_ORACLE` (level A)

| | |
|---|---|
| decisions | **2,131** in-window (session-start filter, the one that produced every published headline) |
| realized net | **$296,911** = **$1,393.95/wk** over 213 weeks — reconciles to `CURRENT_BASELINE`'s `$1,394/wk raw` |
| mean action value | **+$162.79** · sd **$2,123.55** · median **−$64.36** |
| sign | **40.92 % positive, 59.03 % negative** |
| quantiles | p1 −$4,996 · p10 −$906 · p50 −$64 · p90 +$1,488 · p99 +$7,655 |

> ### **59 % of `P1/PCT`'s individual decisions have negative causal marginal value.**
> The object is profitable because a minority of very large positives carries it. That is a
> structural fact about the incumbent that no previous wave could have stated, because no previous
> wave measured the value of the *action*.

Three arms, all reported (the spec required both; the audit found the frozen arm had been computed
and not printed, and that is fixed):

| arm | mean | sd | sum | % positive |
|---|---:|---:|---:|---:|
| **SELF-CONSISTENT** (primary) | $162.79 | $2,123.55 | $346,915 | 40.92 % |
| FROZEN-SCORE (sensitivity) | $166.16 | $1,986.03 | — | — |
| FULL-HORIZON (both channels) | $115.30 | $2,196.37 | $245,698 | 44.30 % |

⚠️ **The spec's justification for truncating at session end was wrong.** It said "the engine carries
no cross-session position state" — true of *position*, false of the trailing-250-entry **size** state.
The cross-session channel is worth **−$101,217** and flips the sign of 226 events (10.6 %).
**Every session-scoped dollar figure here is ~29 % higher than its full-horizon counterpart.** No gate
verdict changes (G1 rises to 47.07 %, G2 to 35.13 %, G3 still fails), but the full-horizon column is
the honest one for magnitude.

### 2.2 Path dependence — where it lives

| | share |
|---|---:|
| ΔU **exactly equals** the trade's own net — path dependence inert | **76.91 %** |
| differs by > $50 | 22.90 % |
| **differs in SIGN** | **10.37 %** (median \|ΔU\| $439; 98 of 221 above $500) |
| abstaining removes exactly the toggled trade | 77.10 % |
| abstaining removes *more* | 3.14 % |
| **abstaining ADDS trades** (the box never latches) | **9.01 %** |

⚠️ **The audit showed the effect is not broad — it is co-extensive with the box latch.**
In sessions holding ≥ 1 latched-out run the divergence rate is **56.70 %**; in the other 63.6 % of
events it is **3.54 %**, *below the gate's own 10 % bar*. 440 of the 488 divergent events (90.2 %)
sit in latch sessions. **"Path dependence is broad" is not supported; "path dependence is a
box-latch phenomenon" is.**

### 2.3 The abstention curve — and the control that reframes it

Computed by **joint replay**, not by summing marginals (marginals are not additive within a session:
they sum to $346,915 against a realized net of $296,911).

**Ranked by CAUSAL action value:**

| f | net | uplift | AVOIDED | **CREATED** | REPRICED | **created %** | top-decile winners kept |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 634,613 | +337,702 | 117,316 | **215,480** | 4,906 | **63.8 %** | 205/214 |
| 0.10 | 765,150 | +468,239 | 214,471 | **243,121** | 10,647 | **51.9 %** | 201/214 |
| 0.20 | 901,816 | +604,905 | 343,512 | **244,800** | 16,593 | **40.5 %** | 197/214 |
| 0.30 | 974,416 | +677,505 | 415,085 | **238,599** | 23,820 | **35.2 %** | 194/214 |

**Ranked by the trade's OWN net — the label W122's ledger already carried:**

| f | net | uplift | **as % of the causal oracle** | created % | top-decile winners kept |
|---:|---:|---:|---:|---:|---:|
| 0.05 | 529,298 | +232,387 | **68.8 %** | 12.2 % | 213/214 |
| 0.10 | 642,596 | +345,685 | **73.8 %** | 7.7 % | 213/214 |
| 0.20 | 788,624 | +491,713 | **81.3 %** | 5.0 % | 212/214 |
| 0.30 | 876,134 | +579,224 | **85.5 %** | 3.2 % | 210/214 |

> ### ⚠️ **THE CURVE IS MAJORITY REGENERATION, NOT ABSTENTION.**
> `CREATED` is the P&L of trades the frozen policy takes **because the session box no longer
> latches** once a bad early decision is removed. Every one of those entries is the `r0+1` bar of a
> latched-out run — **they are not decision events in the ledger at all.** At f = 0.05 they are
> **63.8 %** of the headline uplift. **That is a finding about the BOX POLICY, not about
> action-value routing.**

> ### ⚠️ **THE COUNTERFACTUAL APPARATUS BUYS 15–31 % OVER A LABEL WE ALREADY HAD.**
> A ranking that uses only the trade's own P&L recovers **68.8 – 85.5 %** of the causal oracle.
> Incremental value of the entire replay machinery for *choosing which actions to drop*:
> **+$105,315 at f = 0.05, falling to +$98,281 at f = 0.30.** And it **damages the right tail more**
> — 205/214 top-decile winners survive under the causal ranking against **213/214** under the naive one.

⚠️ **The previously-reported "96–100 % right-tail retention" is withdrawn.** That metric credited
whatever trade now started at a baseline winner's entry bar **at its new size**, so it was not a
retention rate and could exceed 100 % — proved: it returns **101.2 %** on the own-net ranking. The
table above reports **counts of winners that survive as the same trade**.

### 2.4 It is NOT exposure reduction — the W121 check

| f | ORACLE net | RANDOM mean | percentile | selection $ | **selection share** | **exposure vs base** |
|---:|---:|---:|---:|---:|---:|---:|
| 0.05 | 634,613 | 283,579 | **100.0 %** | 351,034 | **103.9 %** | **105.0 %** |
| 0.10 | 765,150 | 264,600 | **100.0 %** | 500,550 | **106.9 %** | **101.5 %** |
| 0.20 | 901,816 | 231,500 | **100.0 %** | 670,316 | **110.8 %** | 98.1 % |
| 0.30 | 974,416 | 221,644 | **100.0 %** | 752,772 | **111.1 %** | 93.0 % |

> **Activity-matched random abstention LOSES money at every fraction** — net falls monotonically from
> $296,911 to $221,644. The oracle beats **40 of 40** random draws at every f, selection accounts for
> **more than 100 %** of the uplift, and at f ≤ 0.10 the oracle arm carries **more** contract-minutes
> than baseline. **This is the exact inverse of the W121 failure mode.** Trading less is not free
> here; it is strictly costly.

### 2.5 Ceilings (`OPPORTUNITY_LANGUAGE` — all EX-POST, never "opportunity")

| level | value |
|---|---|
| **B** `SESSION_POLICY_ORACLE`, frozen-size arm | **3.244×** baseline over 570 enumerable sessions (68 skipped, > 8 runs, holding 508 trades) |
| **C** `CONSTRAINED_PORTFOLIO_ORACLE` | C − (B + XM + FM as run) = **$1,099,601** — additive, the three experts share no state |
| **D / E** | **NOT COMPUTED.** D needs a fitted model, E needs a router. This wave fits nothing |

### 2.6 The one-shot experts

| expert | decisions | net | mean | % positive |
|---|---:|---:|---:|---:|
| `XM_CONFLICT` | **346** | **$199,766** | **$577.36** | 54.62 % |
| `FOLLOW_MORNING` | 1,009 | $180,651 | $179.04 | 55.00 % |

For both, **action value equals the trade's P&L exactly** — one shot, no box, no latch, size 1. That
is a structural fact, not a measurement. Book weights: w(P1/PCT) **0.4728** / w(XM) **0.5272**,
weekly ρ **0.0977**.

---

## 3. The gates, and what the audit found wrong with them

| gate | observed | verdict |
|---|---|---|
| **G1** \|ΔU − own net\| > $50 on more than 10 % | **22.90 %** | **PASS** |
| **G2** top 5 % hold < 80 % of \|action value\| | 39.28 % | **PASS on clause · FAIL on rationale** |
| **G3** session-clustered Q5−Q1 MDE ≤ bar | $564.63 vs $13.93 | **FAIL** |
| **G4** f = 20 % value positive in ≥ 3 buckets | 5 of 5 | **VOID** |

**G4 is VOID — it cannot fail.** Its statistic is minus the sum of the most-negative 20 % of action
values, and 59.03 % of all action values are negative, so every bucket's bottom quintile is entirely
negative (largest element: −$609 / −$509 / −$419 / −$484 / −$1,029) and the statistic is positive by
arithmetic. **"5 of 5" carries zero evidential content.** This is precisely the un-failable-gate error
the spec's own `why_the_raw_oracle_is_NOT_the_gate` section forbids, committed in a different gate.
**Stability is NOT established by this wave.**

**G2 fails its own rationale.** The clause measures the top-5 % share of total *absolute* action
value. The rationale asks whether "essentially all of it sits in ~100 events" — a question about the
**sum a router would earn**:

- top 107 events contribute **$363,787 = 104.9 %** of the $346,915 sum
- the remaining **2,024 events sum to −$16,872** (−$8.34 per decision)
- the single largest event is **12.39 %** of the total

**By the economically relevant measure the concentration condition is met.** G2 must not be quoted as
a clean pass.

**G3 fails robustly, and the coded version was too generous.**

| MDE for the per-decision policy gain | value | vs $13.93 bar |
|---|---:|---:|
| symmetric (as coded) | $56.46 | 4.1× |
| **assumption-free** (0.2·Z·sd/√(N_eff/5)) | **$79.85** | **5.7×** |
| session bootstrap (4,000 draws) | $41.44 | 3.0× |

Two audit caveats, neither of which rescues it: the **ICC 0.3929 is ~88 % a heteroskedasticity
artifact** (a null test permuting within same-size sessions, where true ICC = 0, still returns a
large ICC), and the "**session block bootstrap**" is effectively iid (SE $147.92 against $143.58 for
a fully iid event bootstrap) because its permutation re-mixes events across sessions. Correcting the
ICC downward *raises* N_eff and *lowers* the MDE to roughly $61 assumption-free — **still 4.4× the
bar.**

> ### **A router must capture ~15–28 % of the ex-post action oracle before its gain can be
> ### distinguished from zero at this sample size.**
> The only two calibrations of level-3 recovery this repo possesses are **≈16 %** (AFT, W112/W114)
> and **≈20 %** (RTH open, `XM_CONFLICT`, W104). **The requirement sits at or above the best this
> campaign has ever achieved.**

---

## 4. Why de-prioritising is right on the merits, not only on the letter

The preregistered rule already decides this. Four independent facts agree with it:

1. **The apparatus buys 15–31 %** over a label W122's simpler ledger already carried — and costs a
   full counterfactual simulator to obtain.
2. **The oracle it reveals is majority a box-policy effect** (35–64 % regeneration), and a
   *uniformly* looser box was already measured at **+$6/week, paired p = 0.940** (W98).
3. **~100 events carry everything.** The other 2,024 sum to −$16,872. A model must find needles, and
   G2's own rationale says a model cannot be expected to.
4. **The sample cannot certify the answer anyway** — G3, robustly, under four different estimators.

Running RR_W002 on current information would risk producing exactly the W112 outcome: a fitted model
that clears a numerical bar while a trivial control beats it, on a sample that could not have
distinguished the two. **That is a trial spent on an uninterpretable result.**

**What would reopen it:** genuinely new information at the decision event. That raises achievable
capture, and the ledger now exists, so RR_W002 becomes cheap. **This is a sequencing decision, not a
kill.**

---

## 5. What this wave leaves behind

**Durable, reusable:**
- A **certified counterfactual replay** of the frozen `P1/PCT` engine — bit-equal to the full pass,
  0.82 s per toggle, and now the standing instrument for any action-value question on this object.
- A **2,401-row action-value ledger** (`out/ledger_p1pct.csv`, 36 columns) with both arms, the
  cross-session channel, MAE/MFE, session box state and cascade flags.
- Ledgers for `XM_CONFLICT` (346) and `FOLLOW_MORNING` (1,009).
- The **activity-matched random abstention placebo** as a reusable control.

**Binding constraints this wave adds:**
1. **A gate whose statistic is a one-sided sum over a majority-negative distribution cannot fail.**
   Check the sign structure of every gate statistic before committing the spec — G4 is the record of
   not doing so.
2. **A concentration gate must be stated on the SUM, not on total absolute value.** They can disagree
   by a factor of three, and only the sum is what a router earns.
3. **A "retention" metric that matches on entry bar credits re-priced survivors and can exceed
   100 %.** Retention must be a count of surviving trades, reported alongside dollars.
4. **`P1/PCT`'s cross-session SIZE channel is real** — worth −$101,217 and 226 sign flips. Any future
   counterfactual on this engine must state whether it is session-scoped or full-horizon.
5. **For ranking which `P1/PCT` actions to drop, the trade's own P&L recovers 69–86 %** of the causal
   oracle. Do not pay for a counterfactual simulator to get the last 15–31 % unless that margin is
   the object of study.

**New frontier item:** **SELECTIVE box un-latching.** W98 tested a *uniformly* looser box (+$6/wk,
p = 0.940). The regeneration finding is a *different* object — suppressing specific early losers so
the box survives. It is recorded on the frontier at **LOW EVI** (the selection is ex-post, n ≈ 247
latch sessions, and W98's result is not encouraging), but it is new and it is named.

---

## 6. Continuation

Per `outcomes_fixed_in_advance` and directive §45:

| | |
|---|---|
| **router branch** | **DE-PRIORITISED** |
| **HMM / latent state** | **NOT RUN** |
| **next wave** | **EVENT RESPONSE** — `RESEARCH_FRONTIER.md` row 3, the last named cheap untested information surface |
| **promoted / demoted** | **nothing.** `P1/PCT` remains the base, `XM_CONFLICT` the active component |
| **seal** | untouched |
