# SKEPTIC VERDICTS — GENESIS II World Scan Wave 2 (MC-38..MC-56)

Role: adversarial audit of `out/mechanism_cards_w2.md` (19 new cards) against
`research/genesis2/FAILURE_MEMORY.md` and the EXEC01 cost truth
(`runs/G2_EXEC01_P1_EXECUTION_20260828/REPORT.md`). Written 2026-08-29. No git action taken.

## 0. Standing attack context (applies to multiple cards)

**Cost truth (EXEC01, measured, not modeled):** contract-weighted mean **$20.65/ctrRT spread**
(median $20.00, p90 **$35.00**) + $4.36 commission ≈ **$25/RT pooled**; 2026 Jun–Jul regime
**$28.69 + $4.36 ≈ $33/RT**. Consequences the cards did not fully absorb:

- **Stressed-tape shorts/fades pay p90, not the mean.** Any card whose entries cluster on
  vol-spike days (MC-39, MC-40 cascade leg, MC-56) must gate at a **$40/RT stress cost**, not $33.
- **Overnight holds are not $33/RT.** EXEC01 E2: overnight quoted spread runs **4.5–6 ticks**
  (vs 2–2.9 RTH-afternoon) → ON round trips ≈ $27–34/RT before any event premium. MC-48/MC-50
  overnight falsifiers must use a **$35/RT floor** plus the $5.25 ON friction tax.
- E4: passive limits available at ≤1-tick spread only 0.7% of the time — no card may assume
  "just use limits" to duck the cost bar.

**Pristine-window register (protect; flag every falsifier that touches these):**
- **P-1: 2022+ implied-vol-daily (VX/VXN family) joined to NQ outcomes** — H1 consumed the
  pre-2022 discovery value of that join; the 2022+ join is reserve. Discovery on it is barred;
  at most ONE preregistered confirmation read for a leg that survived pre-2022 discovery.
  Affected: **MC-52 (directly), MC-56 (fatally — see card), MC-39 daily fallback, MC-38 VXN add-on.**
- **P-2: 2019+ multi-market daily** — H3 (XSMOM) consumed 2009–2018; the 2019+ multi-market
  panel is reserve. Affected: **MC-53** (Mahalanobis covariance, stock-bond corr legs).

**Evidence hygiene:** WebSearch was exhausted before the wave; several CLAIM fields are
title/venue-level (scouts flagged). No magnitude from a title-level source (e.g. S4-10 Iwanaga)
is quotable in any spec. Verdicts below discount those legs accordingly.

---

## 1. Per-card verdicts

### MC-38 — Sharper realized-vol state · VERDICT: **TRIAGE-MED**
Attack: the forecast improvements are so well replicated that the horse race itself has LOW
information value — we already believe the answer. The card's own admission ("only pays where a
gate binds on a noisy vol estimate") is the problem: **no live engine currently gates on next-day
RV**; standalone this is a forecasting paper. Also the VXN-in-HAR add-on joins implied-vol daily
to an NQ outcome → P-1 exposure on 2022+.
Tightened falsifier: run ONLY as the nested vol-input arm of the MC-51 sizing harness (input
∈ {plain 21d RV, HAR-RV, HAR+RS−+ON}); **drop the VXN add-on** from v1; cross-market leg
(ES/RTY/YM 1-min, owned, not the H3 daily panel — no P-2 issue) as a nested extra.
**FROZEN PRIMARY:** Diebold-Mariano on QLIKE, HAR+RS−+ON-terms vs HAR-RV, next-day NQ RV,
frozen split (train 2006–2017 / test 2018–2026-05-31, pre-burn), NQ 1-min. PASS = QLIKE improves,
DM p<0.05. Decision use: selects MC-51's vol input; nothing else.

### MC-39 — Intraday VX-spike → close spillover · VERDICT: **DATA-GATED**
Attack: (a) untestable as specced — the observable (VX 1-min) is unextracted; the "certified VX
daily fallback" would spend the P-1 pristine join and is **rejected**. (b) Single primary source
(BIS) + an era story that argues against itself: post-2018 the ETP complex deleveraged (XIV dead)
— the mechanism's best evidence is from a regime that no longer exists; 2023–26 is the only cell
that matters and it is the thinnest. (c) Cost illusion: front-VX ≥ +5% by 15:00 days are exactly
the p90-spread tape — $33/RT is optimistic, gate at $40/RT. (d) TICK lesson: print events/yr per
era BEFORE any table; if the 2023–26 cell has <15 events/yr, the falsifier cannot move the prior.
Gate: VX/VXM 1-min extraction task ($0, but a task — queue it); then the card's falsifier with
era-split, event-count print first, $40/RT, one shared draw with the MC-13 family (S1 declared
S1-02/03/04 one family — binding).

### MC-40 — Forced-deleveraging continuation band · VERDICT: **TRIAGE-HIGH**
Attack (survives, but the falsifier needed teeth): the "84% touch below trigger within 3d" stat
is **geometry-friendly** — a 2.5–5% drop mechanically elevates vol, widening the 3-day range, so
touching below the trigger is partly a range artifact. The card's "matched unconditional control"
is not enough; PDH/PDL died to exactly this. Control must be **vol-matched** (same trailing-RV
decile), not merely unfiltered. Second attack: effective N concentrates in 2008/2020/2022 —
per-era event counts BEFORE gating, and the 2022 bear is in-sample for the band numbers' author
era, so treat Hanna's magnitudes as unquotable priors, not benchmarks. Third: the cascade
(minutes) leg trades stressed tape → $40/RT there.
Tightened falsifier: card's (a)/(b)/(c) with the touch-probability control replaced by
vol-matched control; MFE-path leg (b) is the mechanism's sharpest discriminator (positive early,
negative late = spiral-then-reversal); S1-10 gap-down veto binds all entry designs.
**FROZEN PRIMARY:** net 3-session close-to-close short return after bear-filtered (close < 200d
MA) [2.5,5)% down days, $33/RT, vs (i) circular-shift null and (ii) vol-matched drop-day control,
one shared draw; MDE and per-era event counts printed before the table. NQ 1-min 2006→2026-05-31.

### MC-41 — Failed-rally breadth divergence · VERDICT: **TRIAGE-MED**
Attack: one author, one observable family, 2003–07 screenshot-grade stats, N=32 in the key cell.
The S1-07 daily leg on 4.5y of owned internals will have ~40 up-day×bottom-tercile events — the
MDE print will likely kill it before it runs; do not let it anchor the card. The S1-08 intraday
leg has ~1,100 session-scale observations and is the real test. TICK regime-collapse lesson
binds: print events/yr (internals population shifted 2022→2026).
**FROZEN PRIMARY:** Δ = P(afternoon takes out morning low | bottom-tercile 11:00 cumulative
adjusted TICK) − matched unconditional P, internals minute 2022→2026-05-31, circular-shift null
shared with the MC-23 prereg family; MDE printed first; the next-1-4d leg runs only if its
event count clears its own printed MDE. $TICK-to-2013 extension stays owner-gated (governance).

### MC-42 — EOD short-covering headwind · VERDICT: **TRIAGE-MED** (free rider)
Attack: the era claim rests on ~340 down-day observations for 2023–26 — a raw sign flip on that N
is noise; the card's "sign flip = adopt exit rule" clause is too loose and would install a
permanent policy off an unsignificant coefficient. Index-level version untested anywhere (the
stock-level result may be entirely cross-sectional attention/covering that nets out at index level).
Tightened: adopt exit-before-15:30 only on a **significant** era break, not a sign.
**FROZEN PRIMARY:** down-day 15:30→16:00 continuation coefficient 2023–26 with block-bootstrap
95% CI vs the 2006–15 coefficient, one extra column in the MC-13 harness; adopt the exit rule
only if the 2023–26 CI excludes the 2006–15 point estimate AND the sign flips. Either outcome banked.

### MC-43 — DC intrinsic-time structure · VERDICT: **METHODS**
Measurement, not trading — grade it as such. Attack: Olsen-school scaling laws are replicated on
FX/crypto by the school itself; the only fully independent line is the analytic Brownian null,
which is also the card's saving grace (partially self-controlling). The banked ON-touch/IB
anomalies "pointing the same direction" is soft — they are 5pp level-relevance facts, not
overshoot measurements; do not let them inflate the prior. Run as specced (the three-leg frozen
audit with the 0.632 conditional's matched control); the likeliest outcome (laws hold, no
conditional lift) closes duration-timing cheaply and is the honest EVI. No pristine exposure
(NQ 1-min only). Gate MC-44/MC-45 sequencing on this result.

### MC-44 — DC-event trading policies · VERDICT: **TRIAGE-LOW** (contingent on MC-43)
Attack: ~1.5 effective sources for 8 apparent leads (the card admits it); every positive number is
FX/equities at ~0.5–1bp spread vs our $33/RT — a 30-60x cost gap; GA/GP results are selection-luck
machines even with the learner stripped; counter-trend variants collide with the fade graveyard.
The single fixed-rule falsifier and the clock-swap check are nearly free AFTER MC-43 — run only
then, only the no-learner variants, expected FAIL banked as "where gross edge peaks."

### MC-45 — Swing-sequence grammar · VERDICT: **TRIAGE-LOW**
Attack: one source, 26-year-old daily single-stock data, and the paper itself claims distributional
information, not profit; "information at zero cost" cards historically die at the $33/RT
conversion. The KS-vs-matched-control single table is cheap and the observable genuinely carries
no levels (materially different from the MC-07/SWEEP01 closures — passes the anti-rescue gate).
One table, one wave, no learner; dies or earns a conditioning role only.

### MC-46 — Closing-auction imbalance / dislocation reversion · VERDICT: **TRIAGE-MED**
Attack: (a) the proxy break at 15:50 can be produced by mechanical volume seasonality (MOC agency
flow ramps) without ANY tradable information — a break alone must not be read as edge; the
dislocation-reversion table is the actual claim. (b) Index-aggregation dilution is real: 500-1000
single-stock imbalances mostly cancel; the surviving aggregate signal may be far under the cost
floor (card admits). (c) 16:00→18:00 reversion trades the thin post-close tape — ON spread costs
apply ($35/RT floor). The negative-space claim ("no public measurement") checked out in the scout
file and makes this an original test with closure value.
**FROZEN PRIMARY:** structural-break test at exactly 15:50 ET in {|1-min ret|, volume, lag-1
autocorr} vs 15:40/15:45 placebo anchors, NQ 1-min 2006→2026-05-31, shared draw; the
dislocation-decile reversion table (with 2006-15/16-26 era split) runs ONLY if the break exists.
No imbalance-feed purchase decision before that.

### MC-47 — Liquidity-state execution-cost policy · VERDICT: **TRIAGE-HIGH**
Attack attempted, little sticks: foundational replicated results + in-house EXEC01 corroboration,
zero governance risk, no seal exposure, no trades of its own, and it reprices every other card's
denominator. Two real cautions: (1) BestEx is ONE vendor family across two leads (card flags it) —
weight QB/academic legs above it; (2) the shadow-book validation leg depends on the 2026-09-01
shadow actually accumulating fills — do not let the cost-model fit go unvalidated into the
scoreboard; until validated it is a MODEL row, not a measurement row.
**FROZEN PRIMARY:** second-of-minute effective-spread/markout profile on owned 2025-26 NQ tick+BBO
(pre-burn slices); PASS = boundary-second (sec-0/sec-30) penalty ≥ 0.25 tick vs mid-minute →
re-time 1-min-bar-close entries and price the saving in $/wk on P1's frozen action set.
Secondary columns (same run): OFI→mid slope by EXEC01 spread/depth state; matched-vol
10:00-vs-15:00 cost. Then fit cost = f(spread, depth, hour); >20% divergence from the measured
$25–33/RT band forces a cost-model revision. Feeds the stress-cost floors used across this file.

### MC-48 — Session-handoff sign structure · VERDICT: **TRIAGE-LOW**
Attack: the tradable residue after the overnight-drift kill is very plausibly nil (card concedes);
the Asia-leg source is title-level (magnitudes unquotable — hygiene rule above); ON legs pay the
$35/RT floor, which devours session-scale sign effects. Redeeming feature: it is one conditional
table sharing a wave and draw with the MC-12 update, and a clean negative closes the handoff axis.
Run only as the co-tenant of the MC-12-update wave; no standalone wave slot.

### MC-49 — Overnight sub-session partition (killzones) · VERDICT: **KILL**
This is the rescue shape FAILURE_MEMORY exists to stop. G2_F2_SWEEP01's finding was not merely
"prior-RTH sweeps are null" — it was that the post-cross response is **generic mean-reversion
carrying no level information**. If crossing a level tells you nothing about which level it was,
then partitioning the overnight into Asia/London sub-levels cannot add information — the closure's
mechanism finding already predicts this card's outcome. The sole evidence is a 59-day self-flagged
Yahoo-5-min repo from the ICT node (SOURCE_GRAPH #1), whose unfiltered signals LOSE on 3 of 4
symbols. The banked ON-extreme touch fact (95.3% vs 90.0%) is already recorded and does not need
this card. Entry style (reversal-at-extreme, 09:30-11:00) is also the graveyard's favorite meal.
If the EVENTTIME family (MC-43) ever validates path structure on NQ, level-free representations
supersede this anyway. Killed as rescue-adjacent with a measured-mechanism prediction of NULL;
re-openable only with genuinely new evidence class (not more ICT derivatives).

### MC-50 — Event-conditioned overnight holds · VERDICT: **TRIAGE-MED** (macro leg only; earnings leg demoted)
Attack: (a) Cost illusion — the card prices $5.25 ON tax + $33/RT, but EXEC01 measured overnight
spreads at 4.5–6 ticks: release-night RTs realistically cost ≥$35/RT before the event premium on
the spread. Reprice the falsifier at $35/RT + $5.25. (b) Hanna sells overnight subscriptions and
his employment-day claim is 2015-era, pre-lockup-tightening — vendor-conflicted AND stale; use
only as motivation. (c) The earnings leg has an unprinted N (top-10-weight × large-|surprise|
cells may be ~30-60 events) and an index-aggregation gap the card underweights: the Gamm effect is
single-stock overnight drift; NDX transmission at 40% weight is a hypothesis, not evidence.
Demote the earnings leg to contingent-on-N-print.
**FROZEN PRIMARY:** NQ 18:00→08:29 net return on NFP/CPI nights at $35/RT + $5.25 ON tax vs
matched same-weekday non-release nights, eras split 2017/2023, circular-shift shared draw,
NQ 1-min pre-burn (~450 events — adequate). Earnings-leg tables only after cell counts clear
their printed MDE, with the both-signs cell as the discriminator.

### MC-51 — Index vol-managed sizing · VERDICT: **TRIAGE-HIGH**
Attack, mostly absorbed by the card's own design (the critics are merged into the falsifier —
correct): remaining sharp edges: (1) §4 leverage-masquerade is the historic failure mode of this
literature — the matched-mean-exposure clause must be enforced in the program-printed gate table,
not prose; (2) single-instrument NQ Sharpe gains will be smaller than the diversified-factor
papers suggest — the honest deliverable is geometric growth + tail, and the card says so; hold it
to that (no Sharpe headline); (3) the expanding-window c (Cederburg clause) must be the ONLY
calibration — any full-sample c anywhere in the harness voids the run. Drawdown-throttle leg
stays as the preregistered expected-FAIL (closes folklore cheaply).
**FROZEN PRIMARY:** extremes-only variant (bottom/top RV-decile → 1.5x/0.5x): net geometric
growth AND maxDD vs constant-exposure control at matched mean exposure, real-time expanding
calibration only, $33/RT on rebalance contracts, NQ daily-from-1-min 2006→2026-05-31, era split,
circular-shift null on the timing component. Classification locked: RISK SPECIFICATION.

### MC-52 — VRP / VIX-curve states · VERDICT: **TRIAGE-LOW** + PRISTINE FLAG (P-1)
Attack: (a) The card's "one family wave 2006-2026" **burns the pristine 2022+ implied-vol→NQ
join** — the exact reserve window. The "cheap family closure" is not cheap; it spends reserve.
(b) Monthly/quarterly horizons on 20y = ~240/80 observations, era-split halves that — the VRP
return-predictability leg cannot clear any honest MDE and is a known replication battleground.
(c) Adjacency to the H1 kill is closer than the card admits: "forecast-adjusted premium" still
reduces to VX-curve-shape → NQ, the axis H1 wrong-signed.
Tightened: if run at all, DISCOVERY on 2006–2021 only; 2022+ join reserved for ONE preregistered
confirmation of a leg that survived discovery vs both its null AND the raw-basis nested control.
The RV-forecast leg (c: nested next-5d RV, no NQ-return join) is the only leg worth its slot.
No wave-3 slot.

### MC-53 — Cross-asset regime states for sizing · VERDICT: **TRIAGE-MED** + PRISTINE FLAG (P-2)
Attack: (a) Mahalanobis/stock-bond legs on multi-market daily touch the **2019+ pristine
multi-market panel** — and the stock-bond-corr regime's entire modern evidence IS 2022+
(N-bound: one episode). Discovery restricted to 2006–2018 covariance data; 2019+ reserved for one
preregistered confirmation. That guts the corr-sign leg (its episode is inside the reserve) —
demote it to the confirmation-only shelf. (b) The honest expected outcome is total collapse into
the RV-only throttle; the design pre-prices this — good — but then MC-53 must run AFTER MC-51 so
the RV throttle control is already frozen. (c) HMM monthly refit is a look-ahead vector — freeze
2 states and the refit calendar in the spec. (d) BEX index / FRED legs are owner-gated
acquisitions → OWNER_QUEUE, not this wave.
**FROZEN PRIMARY:** turbulence >90th-pctile → 0.5x throttle vs the MC-51-frozen RV-only throttle
at matched mean exposure, geometric growth + maxDD gates, discovery covariance from 2006–2018
multi-market + full-history NQ; PASS only where the cross-asset term adds beyond univariate RV.

### MC-54 — Diurnal vol-curve state / 0DTE era-break · VERDICT: **TRIAGE-HIGH**
Attack: legs 3–4 are luxury riders — the volume-time leg has a published negative
(Gillemot-Farmer-Lillo bound, cited on MC-34) predicting weak lift, and the lunch-conditional is
self-declared unsourced folklore; both are contingent, not core. The core (era-break arbiter) is
the single highest-leverage cheap measurement in the wave: it decides whether ANY pre-2022
intraday-vol statistic is an admissible prior, which gates MC-38/52/55/56 and every future vol
card. Someone (Brogaard or Cboe) is wrong in print — either answer re-prices the shelf. NQ 1-min
only; no pristine exposure.
**FROZEN PRIMARY:** break test at 2022-05: minute-of-session RV profile + last-30-min RV share,
2016-19 vs 2023-26, program-printed break statistic with circular-shift shared null. Legs (2)/(3)
run only after the break answer fixes the admissible training era; leg (4) only after its MDE
print (folklore permanently banned on failure, per card — hold it to that).

### MC-55 — Post-FOMC vol crush · VERDICT: **TRIAGE-LOW** (downgrade from card's MED-HIGH/MED)
Attack: existence of the post-14:00 RV contraction is near-tautological (uncertainty resolution
is textbook; even the card calls it that) — confirming it has LOW information value. The policy
expression is a suppression rule for expansion/breakout entries 14:00–16:00 on 8 days/yr — but
**no live engine currently trades that window**: the falsifier would produce a fact with no
application surface. N≈160 with an MDE gate is fine, but EVI, not feasibility, is the constraint.
The ΔVX confirmation leg joins VX daily to FOMC dates (not NQ outcomes) — P-1 tolerable, but
keep the leg descriptive. Park until an engine exists with FOMC-window trades; then it is one
cheap table + one A/B. Banked as a shelf card, not a wave-3 slot.

### MC-56 — Implied-move overstatement shadow · VERDICT: **TRIAGE-LOW** + PRISTINE FLAG (P-1, decisive)
Attack: (a) **The card's decisive era IS the pristine window.** The whole mechanism is 0DTE-era
(2022-05+), and the falsifier joins VXN-daily-implied sigma to NQ outcomes exactly there — the
protected reserve. Running it as discovery spends P-1 on an EXAMPLES-grade (unreviewed preprint)
lead adjacent to the fade graveyard (TICK fade, seven 2022-era fade geometries, W118). That is a
bad trade of reserve for prior. (b) Cost: beyond-sigma late-day fades are stressed-tape entries —
$40/RT, and the fade graveyard's base rate at this exact shape is 0-for-7. (c) The pre-2022 era
is admissible for leg (1) (pure measurement of P(range < k·sigma)) but the mechanism says the
effect only exists post-2022 — so the admissible window can't confirm and the confirming window
is reserve. Verdict: hold. Sequence: MC-54's era-break first; if the owner ever budgets a P-1
confirmation read, this card competes with MC-52 for it and currently loses (weaker evidence class).

---

## 2. Verdict counts

| Verdict | N | Cards |
|---|---|---|
| KILL | 1 | MC-49 |
| TRIAGE-HIGH | 4 | MC-40, MC-47, MC-51, MC-54 |
| TRIAGE-MED | 6 | MC-38, MC-41, MC-42, MC-46, MC-50, MC-53 |
| TRIAGE-LOW | 6 | MC-44, MC-45, MC-48, MC-52, MC-55, MC-56 |
| METHODS | 1 | MC-43 |
| DATA-GATED | 1 | MC-39 |

Pristine-window flags: MC-52 (P-1, direct), MC-56 (P-1, decisive-era conflict), MC-39 (P-1 if
daily fallback used — fallback rejected), MC-38 (P-1, VXN add-on dropped), MC-53 (P-2, discovery
restricted to 2006–2018), MC-55 (P-1, tolerable descriptive use only).

## 3. TOP-6 BY EVI (expected value of information per unit cost/risk)

1. **MC-47** — near-certain replication that reprices every card's cost denominator; zero
   governance risk; validates against the 2026-09-01 shadow. The only HIGH-prior card, and it
   compounds through everything else.
2. **MC-54 (era-break leg)** — one cheap table that decides which eras are admissible priors for
   the entire VOL family and settles a published contradiction; every outcome is decision-relevant.
3. **MC-51 (+MC-38 nested)** — strongest-pedigree sizing family in the literature, with its own
   critics built into the falsifier; honest outcome (geometric/tail improvement, RISK SPEC) is
   valuable and cleanly classified.
4. **MC-40** — the only genuinely new information-alpha axis (short-side, explicitly NOT closed)
   with 4 independent evidence lines including account-level causal work; 2022 bear in-sample;
   vol-matched control now installed against the geometry trap.
5. **MC-43** — one measurement run that opens or closes the entire EVENTTIME family (3 cards +
   future leads) with a partially analytic null; the likeliest outcome is itself a bankable
   structural null on duration-timing.
6. **MC-46** — original test (verified negative space), free proxies, clear kill condition before
   any data purchase decision.

## 4. FORMAL WAVE 3 PICK (mechanism/evidence reasoning only)

**Pick 4: MC-47, MC-54(leg 1), MC-51 (with MC-38 as its nested vol-input arm), MC-40.**

- **MC-47** because measured cost truth ($20.65 mean / $28.69 recent spread) is the binding
  constraint on every alpha claim in the program; the mechanism (impact ∝ 1/depth; clock-mark
  clustering) is among the most replicated in microstructure and is already corroborated in-house
  by EXEC01. Evidence class: peer-reviewed + live-verified + in-house measurement — the best in
  the wave.
- **MC-54 leg 1** because the 0DTE era-break question logically PRECEDES every other vol-family
  test: it determines the admissible training era. Two credible sources contradict each other in
  print; either resolution re-prices the shelf. Pure measurement, owned data, no reserve spent.
- **MC-51+MC-38** because vol forecastability without return forecastability is the single most
  robust exploitable asymmetry in the index literature, it survived its own adversarial referees
  net of costs at the index level, and the classification (RISK SPECIFICATION) is locked in
  advance — no §4 masquerade possible. MC-38 rides inside as the input horse race, which is the
  only place its answer has decision value.
- **MC-40** because the wave must carry exactly one new-information shot, and this is the best
  evidenced: four independent lines (trader-era tables, RFS-canonical spiral theory, account-level
  causal fire-sale evidence, audit-trail cascade physics) converging on a band-limited,
  self-limiting continuation — a sharp, falsifiable shape (early MFE positive, late negative)
  that is NOT a fade and therefore not a graveyard rescue. The vol-matched control neutralizes
  the geometry failure mode that killed PDH/PDL.

Held out deliberately: MC-43 (next in line — run when a measurement slot opens; it gates MC-44/45
anyway), MC-46 (queue behind the wave), everything touching P-1/P-2 reserve.

## 5. DISAGREEMENTS with the card author's implied triage

| Card | Author's prior | Skeptic verdict | Why |
|---|---|---|---|
| MC-49 | LOW (kept as cheap test) | **KILL** | SWEEP01's mechanism finding (post-cross response carries no level information) already predicts the outcome; sole evidence is a 59-day ICT-node repo. Not cheap — negative EVI (spends a wave slot to learn a measured thing). |
| MC-55 | MED-HIGH exist / MED policy | **TRIAGE-LOW** | Existence is near-tautological (low EVI) and there is no engine trading the 14:00–16:00 FOMC window to apply the suppression rule to. A fact with no application surface. |
| MC-52 | LOW-MED, "closure value is real" | **TRIAGE-LOW + P-1** | The "cheap closure" spends the pristine 2022+ implied-vol join; closure priced at reserve is not cheap. Discovery restricted to pre-2022 if ever run. |
| MC-56 | MED | **TRIAGE-LOW + P-1** | Decisive era (2022-05+) IS the reserve window; evidence class EXAMPLES; shape is 0-for-7 in the fade graveyard; stress cost $40/RT not $33. |
| MC-39 | MED | **DATA-GATED** | Observable unextracted; daily fallback rejected (P-1); post-2018 mechanism decay makes the only relevant cell the thinnest; stressed-tape cost $40/RT. |
| MC-38 | MED-HIGH | **TRIAGE-MED** | Replication near-certainty makes the standalone horse race LOW-information; value exists only nested in MC-51. VXN add-on dropped (P-1). |
| MC-50 | LOW-MED (both legs) | **TRIAGE-MED macro / demoted earnings** | Macro-night leg upgraded (N≈450, genuinely untested window, H2 closure doesn't cover it) but repriced at $35/RT + ON tax; earnings leg N-gated before any table. |
| MC-42 | MED | **TRIAGE-MED, clause tightened** | "Sign flip = adopt" on ~340 obs would install policy off noise; significance clause added. |

## 6. Method notes for the Wave-3 spec writer

- Family/null declarations from the scouts are binding: S1-02/03/04 one draw (MC-13/39/42
  columns); S5-06/08/13 one family; S6-02/03 one family; S1-07/08 one family; MC-23/MC-41 one
  family. Effective-K correction per CLAUDE.md §4 everywhere.
- Every conditional table ships its matched unconditional (and where flagged, vol-matched)
  control in the same wave — no exceptions survived this review.
- MDE and event-count prints come BEFORE result tables for: MC-39, MC-40, MC-41, MC-50 (earnings),
  MC-54 (leg 4), MC-55. The macro-surprise N-bound lesson and the TICK regime-collapse lesson are
  the operative precedents.
- Cost floors by tape: $33/RT baseline (recent regime) · $40/RT stressed-tape entries ·
  $35/RT + $5.25 tax overnight holds. Source: EXEC01 measured distribution (mean $20.65 spread,
  p90 $35.00, ON spread 4.5–6 ticks) + $4.36 Lifetime commission. NT8 template nets are a
  different quantity and may not be substituted.
- All falsifiers above run on pre-burn data only (≤2026-05-31); nothing touches the BURNED
  (2026-06-01→07-31) or VIRGIN (≥2026-08-01) seals; P-1/P-2 reserves as registered in §0.
