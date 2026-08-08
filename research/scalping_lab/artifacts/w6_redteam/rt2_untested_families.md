# RT-2 — "What remains untested": independent red-team enumeration for Zone-F closure

Charter: `specs/W6_fss10_redteam.md` §RT (RT-2 lens). Date: 2026-08-08. Reviewer: independent
adversarial subagent, no access to RT-1 output, no access to FSS-10 T1/T2/T3 readouts.
Scope: causal information families NOT yet tested in Zone F (5–120 s holds, NQ), judged
against MANDATE_V2 §10 primitives + §11 family list, Amendment 1 roles A/B/C, Amendment 4
§8 FSS-1..10 + §11 feature library, Amendment 6 §7/§9, HYPOTHESES.md open queue, and the
actual data inventory (DATA_INVENTORY.md, DATAPROBE01, substrate/ contents).
Everything below is labeled FACT / INFERENCE / HYPOTHESIS / EXTERNAL PRIOR per the
anti-hallucination constitution (Amendment 4 §28). All numbers were re-derived or read
directly from the cited committed artifacts; verification commands ran read-only on
`substrate/` and `artifacts/` (no sealed dates ≥ 2026-06-01 touched; announcement-calendar
aggregation used dev-window dates only).

---

## 0. The crux: what the C5 ceiling does and does not bound

FACT (verified against `artifacts/w5_c5/w5c5_dataset.parquet` schema and
`w5c5_report.md`): the C5 predictability ceiling was measured on EXACTLY these 27
features — tod, ret5/10/30/60/300, rv60/300, tv60, eff60, range300, dist_hi, dist_lo,
secs_since_hi, secs_since_lo, trades10/60, vol10/60, upd10/60, sflow10/60, act_accel,
nsflow60, spread, spread60 — on a 30 s all-RTH clock, 36 effective sessions. Best
top-decile lift +2.42 pp [+0.15, +4.63] vs a 7.0–9.1 pp C1 gap; all Brier skills
negative; importances dominated by vol/activity ("models learn vol not direction").

INFERENCE (the bounding rule I apply below): C5 bounds ANY state — however cleverly
constructed, including vetoes and interactions up to HGB depth-3 — that is a function of
those 27 features on that clock. It does NOT bound information that is absent from the
matrix. Verified ABSENT from the 27 columns (vs the Amendment 4 §11 CONTEXT/CROSS-MARKET
blocks and MANDATE_V2 §10 AUCTION block):

- VWAP distance / any volume-acceptance or value-area feature
- PDH/PDL distance (prior-day levels), OR-position, ONH/ONL distance as *features*
- overnight gap, prior-session direction
- scheduled-event state (calendar flag)
- every ES/cross-market feature (FSS-10, in flight in this same wave)
- signed BBO/quote-move direction ("bid move / ask move / quote-change direction /
  quote age / BBO persistence" from §11 — grid1s carries only unsigned upd counts)
- book size (L3) and depth (L4)

C5's own caveat says this: "A richer library (deep book, cross-asset) or
event-conditioned clocks are outside this measurement" (`w5c5_report.md` Caveats).
Additionally the entire tested program — census, W3-1, W4 A–D, W5 C1–C4, C5 — ran on
RTH-only decision clocks (FACT: every spec/report says "RTH quote-alive"), so the 18:00
reopen and, critically, the 08:30 ET pre-RTH release windows were structurally outside
every readout, even though the substrate holds full 18:00→17:00 sessions (FACT:
`substrate/MANIFEST.csv` t_min/t_max = 18:00:00 → 16:59:59).

Also relevant everywhere below — cost-side sensitivity of the viability gap (derived
from frozen costs, `EXECUTION_MODEL.md`): BE = (B + C1)/(A+B), so dBE/dC = 1/(A+B) =
3.125 pp per tick saved on (24,8) and 2.38 pp per tick on (32,10). I use this to bound
role-C candidates.

---

## 1. Family-by-family assessment (mandate lists × data inventory)

Legend: TESTABLE = with current data (37-session NQ tick/BBO discovery substrate,
39-session ES tick archive, 2005+ minute cache, c01 announcement calendar);
BOUNDED = information already represented in the C5 matrix and/or directly killed at
trade-rule level; ≥7pp-PLAUSIBLE = a coherent mechanism could deliver ≥7 pp conditional
lift on 24–32t brackets where 14 families delivered ≤ +2.4 pp.

### 1.1 FSS-9 — VWAP / volume-acceptance / prior-day levels — **UNTESTED, MAJOR**

- FACT: no spec, artifact, or registry row ever computed a VWAP or value-area feature in
  Zone F (repo grep: VWAP appears only in mandate text, DR notes, and the Zone-B
  minute-scale B-momentum build permission). The only level classes ever tested are
  ONH/ONL and OR15 (W4-C sweep reclaim AND continuation, 0/144, killed). PDH/PDL was
  skipped for a stated *convenience* reason: "prior-day levels unavailable in the
  non-contiguous discovery [substrate]" (`specs/W4_alpha_wave1.md` line 36).
- TESTABLE NOW: yes, fully. Session VWAP is exactly computable from grid1s (`last`,
  `vol` per second — FACT, schema verified); volume-profile acceptance (HVN/LVN, value
  area) from the same columns; PDH/PDL levels are EXACT from the 2005+ minute cache
  (minute-bar highs/lows give prior-day extremes; tick contiguity is not required). Not
  data-blocked in any respect.
- BOUNDED BY C5? **No.** No VWAP/value/PDH-PDL feature is in the matrix. The FSS-5 kill
  covers a *different* level class (static session extremes) under one interaction
  template (pierce-and-reclaim / pierce-and-continue).
- ≥7pp-PLAUSIBLE? Mechanism (HYPOTHESIS + EXTERNAL PRIOR): VWAP is the dominant
  institutional execution benchmark; algo participation clusters around it and
  value-area edges, creating conditional initiative/responsive flow at level
  interactions that static extremes do not carry. MANDATE_V2 names it twice (§10
  AUCTION "VWAP acceptance / value rejection", §11 M1) and Amendment 4 §8 FSS-9 names
  it explicitly. Honest prior: LOW-to-MODERATE — every level-reaction analog tested so
  far produced −2 to +2 pp, and the strongest measured directional effect anywhere in
  this data inverts to only +1–2 pp forward. But "low prior" is exactly what Amendment 6
  §2–3 forbids using as a closure argument for a mandate-named, cheap, fully-testable
  family.
- **EVI rank 1.**

### 1.2 E1 — calendar-event-anchored windows with pre-RTH releases — **UNTESTED, MAJOR**

- FACT: the announcement calendar exists and is usable
  (`research/04_complementary_family/c01_announcement_calendar.csv`, 145 rows,
  2022-01-07 → 2026-07-29, events = NFP 54 / CPI 54 / FOMC 37; times 08:30 ×108,
  14:00 ×37 — re-verified by direct read). The ONLY event-conditioned readout in the
  campaign is the H-B5 near_news cell: n=8 episodes, 1 session, disqualified by frozen
  gates (`w4_hb5/w4d_report.md`), and its report states the structural reason: "NFP/CPI
  at 08:30 ET are pre-RTH so only FOMC 14:00 windows can overlap RTH spikes." Every
  other analysis excluded these windows by construction (RTH clock starts 09:30; the
  ±2 min news guardrail pushes them to C2-or-excluded).
- FACT (verified): the 37-session discovery substrate contains only **3** pre-RTH
  release mornings (2025-09-05 NFP, 2025-09-11 CPI, 2026-02-11 NFP) and **1** in-RTH
  FOMC (2025-10-29). The full dev tick window holds 23 calendar events, but those
  sessions sit in the internal-confirmation pool.
- TESTABLE NOW: yes, in a degraded-but-honest form. (a) The tick substrate covers
  18:00→17:00, so 08:30 windows ARE in the data — n=3 at Tier-0 is descriptive-only;
  (b) the 2005+ minute cache gives ~50 events/yr × 20 yr for a coarse (1-min bar)
  version of post-release reaction-direction continuation — powered, though it sits at
  the Zone F/S boundary (60–120 s holds ≈ 1–2 bars); (c) a near-parameter-free
  preregistered rule (direction = sign of first N-seconds reaction; fixed bracket;
  C2 costs) can legitimately earn confirmation-pool access under Tier-1 rules without
  Tier-0 tuning, because there is almost nothing to tune. Calendar extension (PPI,
  retail sales, ISM 10:00, GDP — public dates) is cheap and unblocked.
- BOUNDED BY C5? **No.** No event flag in the matrix; the windows are literally outside
  the analysis clock.
- ≥7pp-PLAUSIBLE? This is the single most plausible remaining ≥7 pp mechanism
  (HYPOTHESIS + EXTERNAL PRIOR): scheduled releases are the one state where the
  *magnitude* regime is guaranteed (8:30 CPI/NFP moves routinely dwarf 24–32t, so
  p_neither→0 fast) and post-announcement drift/initial-reaction continuation is a
  documented directional effect at seconds-to-minutes. Honest counterweights: mandatory
  C2 in news windows raises the (32,10) gap from ~7 pp to ~12 pp (BE_C2 = 0.354 vs base
  0.233 — derived from census + frozen costs); spread blowout at 08:30 may exceed even
  C2; and local n at tick resolution is tiny. It cannot be claimed — but it has not
  been measured, and it is mandate-named (MANDATE_V2 §11 E1; Amendment 4 §11 CONTEXT
  "scheduled event state"; FSS-8's own kill note points here: "exogenous-event-anchored
  spikes… new spec").
- **EVI rank 2.**

### 1.3 FSS-10 sub-gap — ES *signed flow* (H-D1 proper) — **SPEC GAP in the in-flight family**

- FACT: hypothesis H-D1 (open in `registry/hypothesis_ledger.csv`) is "trailing ES
  **signed flow** predicts NQ continuation 30 s–5 min" — DR-D's claim was specifically
  that flow, not price, survives. The frozen W6 T2 feature set is price/vol only:
  es_ret30/60/300, es_z_ret60, es_rv60, nq_es_z_diff60, sign-agree, es_spread_t
  (`specs/W6_fss10_redteam.md` §T2). The ES sechilo input carries mid only
  (schema verified: time, mid_last, mid_high, mid_low, n_ev). So even after FSS-10
  completes as specced, the flow variant of the cross-market family remains unmeasured.
- TESTABLE NOW: yes — `substrate/raw/ES/` holds full trade streams (e.g. 832k trades
  per session, MANIFEST verified, 39 sessions); tick-rule signed ES volume at 10/60 s
  is a one-day pipeline addition. The frozen W6 spec must NOT be edited mid-wave; this
  belongs in a preregistered T2b/W7 addendum.
- BOUNDED? Partially: NQ's own sflow10/60/nsflow60 are in C5 and contributed ~nothing,
  and if FSS-10's price-state T2 increment reads ~0, correlated-flow increments are
  likely small (INFERENCE). But "flow ≠ price" is precisely the H-D1 mechanism, so the
  family is not closed by a price-only test of itself.
- ≥7pp-PLAUSIBLE? Low-to-moderate (EXTERNAL PRIOR: index lead-lag flow effects at
  retail lags are small; but this is the named surviving variant of the only family
  Amendment 6 required that is being tested this wave).
- **EVI rank 3** (cheapest closure-relevant addition; without it the §9 claim "FSS-10
  tested" is only three-quarters true).

### 1.4 Opening-drive / first-15-minutes states (Z5 / M2) — **PARTIALLY BOUNDED, moderate**

- FACT: Z5 (RTH-open liquidity transition) and M2 (opening auction/ORB) are still open
  in HYPOTHESES.md. What HAS been tested nearby: OR15 sweep-reclaim AND
  sweep-continuation (killed, 0/144, W4-C); breakout-acceptance at 15 s/30 s/60 s/1 min
  clocks (killed, W5-C2 + W4-B); and `tod` is in the C5 matrix, whose census time-of-day
  mix was flat ("midday slightly higher than open — not an open-auction artifact",
  census_report).
- BOUNDED BY C5? Partially. An opening-drive signal expressible as tod × ret300 ×
  dist_hi/lo interactions was learnable by HGB depth-3 and did not appear. BUT the open
  contributes only ~30 of ~780 rows/session at the 30 s clock — a first-15-min-only
  effect is weakly powered inside a pooled top-decile readout (INFERENCE), and
  gap/overnight-direction context (the natural conditioning of an opening drive) is
  absent from the matrix.
- TESTABLE NOW: yes (37 opens at tick resolution; 20 yr of opens at minute resolution
  for the coarse version).
- ≥7pp-PLAUSIBLE: low-moderate (ORB folklore is heavily arbed; its two nearest
  constructions are already dead here).
- **EVI rank 4.** Not independently MAJOR, but it is cheaply absorbed by the augmented
  ceiling re-run (§2) via gap/ON-direction/OR-position features plus an opening-block
  interaction, which would convert "partially bounded" into "measured".

### 1.5 Session-gap-conditioned states — **UNTESTED as a feature, low prior**

- FACT: overnight gap and prior-session direction are Amendment 4 §11 CONTEXT features,
  absent from the C5 matrix; never used as a Zone-F conditioner. The only gap-adjacent
  work is Zone-A W5-B1 (overnight premium, not promising) with a prior-RTH-direction
  conditional in its spec.
- TESTABLE NOW: trivially (prior close/gap from minute cache).
- BOUNDED? Not formally. INFERENCE: a session-constant is a slow state; C5's clearest
  lesson is that slow states (vol regime, tod) move P(both barriers), not direction —
  a per-day constant shifting target-first by ≥7 pp at second scale would be visible as
  massive day-clustered heterogeneity in the census, which was not reported. Low prior,
  but strictly speaking unmeasured.
- **EVI rank 5** — absorb into the augmented ceiling; do not spend a standalone wave.

### 1.6 H-B1 anti-chase (role C, execution) — **UNTESTED, NON-BLOCKING for closure — arithmetic bound**

- FACT: open in the ledger since 2026-08-07, never run. Claim: delaying marketable
  entries 1–3 s after a flow burst saves 0.3–1.0 ticks (EXTERNAL PRIOR).
- Why it cannot flip the Zone-F verdict (INFERENCE, from frozen numbers): execution
  saving moves the break-even, not the signal. Best case 1.0 t/RT saved ⇒ gap shrinks
  by 3.125 pp (24,8) / 2.38 pp (32,10). Stack that on the best measured conditional
  lift anywhere (+2.42 pp, C5) and the shortfall is still ≥ +3.2 pp (24,8) and
  ≥ +2.2 pp (32,10). Realistically the saving applies to the entry side only
  (≤ ~1.6 pp on 24/8). Separately, W4-A measured the passive-side reality: passive
  gross was WORSE than market gross (−1.50 vs −0.93; adverse selection > spread
  saving), and W3-1's 1 s-delay column changed nothing (−2.32..−2.90).
- Charter classification: execution, not direction — per the frozen RT charter this is
  not a "causal information family" for the closure list. It RETAINS standing value as
  role-C research for Family-A/E10 execution and any future engine, and should be run
  eventually on those grounds (EVI moderate, outside Zone-F closure).

### 1.7 Book-size / L3 semantics, depth, queue, absorption (S6/S7/S8, H-B3-size variants) — **DATA-BLOCKED**

- FACT: L3 = "PLAUSIBLE-size (coarse use only)", semantics unvalidated (DATAPROBE01:
  Bid/Ask `Volume` field could be size, delta, or aggregation; "L3 status stays UNKNOWN
  until a dedicated check"); Amendment 4 §11: do not use size fields as alpha until
  validated. L4 depth: no replay recordings, paid data banned — BLOCKED_BY_DATA.
- The semantics *check itself* is a legitimate open instrumentation item (cheap:
  compare vs Last trade sizes at identical stamps). Even if it validates, top-of-book
  size at retail lag is a seconds-horizon sub-tick-to-~1-tick class signal
  (EXTERNAL PRIOR + every local micro measurement) — nowhere near 7 pp on 24–32t
  brackets. Per the §9 verdict logic, data-blocked items do not bar closure. H-B3
  (fragility veto) in its size-free form is bounded: its observables (spread, spread60,
  upd10/60) are in the C5 matrix, and a direction-free veto cannot create direction.

### 1.8 Cross-asset beyond ES on minute data — **NOT MAJOR for Zone F**

- FACT: no non-ES cross-asset tick data archived; DR-E's GC/CL/RTY/ZN screen belongs to
  Program B (30 min+ horizons). For Zone F, a 1-min-lagged cross-asset state is a slow
  regime variable (INFERENCE: same class C5 showed learns vol-not-direction), and ES —
  the overwhelmingly dominant co-movement channel for NQ — is being tested THIS WAVE at
  second resolution. If FSS-10's ceiling increment reads ~0, lower-correlation
  instruments at 60× coarser resolution cannot plausibly carry ≥7 pp second-scale
  direction (INFERENCE). Testable-in-principle (NT minute downloads), EVI low. Program-B
  relevance unaffected and out of scope here.

### 1.9 Remaining HYPOTHESES.md open items (completeness sweep)

| Item | Status vs Zone F |
|---|---|
| H-A2 noise-area breakout | Zone A/B (30 min+); routed to B-momentum build spec (gate passed). Out of Zone-F scope. |
| H-A3 Roll-bounce guardrail | Instrumentation; effectively addressed for Zone F by mid-price substrate (census: "mid is clean per I-2"). Not an alpha family. |
| H-B3 book-fragility veto | Bounded (§1.7): direction-free + observables in C5 matrix. |
| H-D3 cash-close 1-min retest | Reserved; 5–10 min horizon = Zone S/A, not Zone F. |
| Z2 speed-conditional continuation | BOUNDED: FSS-7 (18,962 episodes, lift −0.79..+0.53 pp, killed) + eff60/tv60/act_accel in C5. |
| Z3 round-number grid levels | Untested; same level-reaction template killed twice at other level classes; folklore risk acknowledged in its own entry. Fold into FSS-9 level block as one extra level class (cheap), not standalone-major. |
| Z6 18:00 reopen micro-drift | Untested, testable (full-session substrate), ETH ⇒ C2-or-excluded; thin-book spread very likely fatal by construction (its own entry predicts this). Low EVI, not major. |
| Signed BBO/quote-move flow (§11 BBO block) | Untested (grid1s upd counts are unsigned — FACT). Micro-horizon class, but absent from C5 matrix; absorb into augmented ceiling (cheap), not standalone-major. |
| Volume-time / event-time representations (MANDATE_V2 §15) | Untested as clocks (all work on 1 s/30 s clock or event triggers). A representation, not an information family; noted for completeness. |

---

## 2. Efficient discharge design (recommendation, not a mandate)

The two MAJOR families plus items 1.3–1.5 and the signed-BBO block share one cheap,
decisive instrument: **C5b — augmented predictability ceiling**. Re-run the frozen C5
protocol exactly (same clock, labels, folds, models, guards) with the 27 features PLUS a
preregistered context block: vwap_dist (+side/age), va_pos/HVN-LVN dist, pdh_dist,
pdl_dist, onh/onl_dist, or_pos, gap_ticks, prior_day_ret, round_number_dist,
event_flag/time-since-event, opening-block indicator, signed-BBO-move flow, and (post-W6,
if negative there) es_sflow60. Frozen readout: Δ(top-decile lift) vs the 27-feature
reproduction control, same 5 pp bar. One measurement bounds five currently-unbounded
families symmetric-risk (it can also REVEAL, not just kill). Alongside it, two
preregistered trade-rule tests: (a) FSS-9-VWAP reaction rule (rejection/acceptance/
reclaim at VWAP ± value edges, 24–32t brackets); (b) E1 event-window reaction rule
(near-parameter-free, C2 costs, minute-history version 2005+ first, tick version
descriptive at n=3 with confirmation-pool promotion path). If C5b Δ < ~2 pp and both
rules fail their frozen gates, RT-2's list empties to data-blocked-only and §9 closure
is supported in the "not found in tested universe" form.

---

## 3. VERDICT

**The major-untested list is NOT empty. Closure is NOT yet supported under the
Amendment 6 §9 letter** ("independent red team agrees no major untested causal
information family remains"). Two mandate-named, mechanism-coherent, fully-testable
families have zero Zone-F measurements, and neither is bounded by the C5 ceiling because
their information is absent from the 27-feature matrix:

| # | Family | One-line mechanism | Testable now? | ≥7pp plausible? | EVI |
|---|---|---|---|---|---|
| 1 | **FSS-9-VWAP/value-acceptance + prior-day levels** (M1; incl. PDH/PDL, value-area; round-numbers as sub-class) | Institutional execution-benchmark anchoring creates conditional initiative/responsive flow at dynamic value levels, unlike the killed static extremes | YES (grid1s vol+last → exact VWAP; minute cache → exact PDH/PDL) | LOW-MODERATE | 1 |
| 2 | **E1 calendar-event-anchored windows, pre-RTH handled** (08:30 NFP/CPI, 14:00 FOMC) | Guaranteed-magnitude regime + documented initial-reaction continuation; the only state where p(≥24–32t move) is near-certain and only direction is at issue | YES-degraded (n=3 tick events at Tier-0; 2005+ minute powered; preregistration→confirmation path; calendar extension cheap) | MODERATE (best remaining), C2 gap ~12pp is the honest bar | 2 |
| 3 | **ES signed-flow variant of FSS-10 (H-D1 proper)** — spec gap: frozen W6 T2 is price-only | Cross-market flow (not price) impact at retail lags | YES (raw ES trade streams archived, 39 sessions) | LOW-MODERATE | 3 |

Conditional/minor (test via C5b absorption, not standalone waves): opening-drive
first-15-min states (partially bounded, weakly powered); session-gap conditioning
(slow-state, low prior); signed-BBO flow block. Non-blocking by charter: H-B1 anti-chase
(role C — arithmetic-bounded: ≤3.1 pp BE relief + 2.42 pp measured ceiling < every gap;
retains Family-A execution value). Data-blocked (do not bar closure): L3 size semantics
(validation check itself still open), L4 depth/queue/absorption. Bounded/closed: Z2,
H-B3, cross-asset-on-minute (post-FSS-10), and all 14 killed families.

Estimated cost to discharge: ONE bounded wave (W7 = C5b + two preregistered rules). If
all three read negative, this reviewer would sign an empty-list verdict with only
data-blocked items remaining.

— RT-2, 2026-08-08
