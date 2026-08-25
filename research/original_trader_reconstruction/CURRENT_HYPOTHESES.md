# CURRENT_HYPOTHESES — OTR campaign #6

**Authority**: derived from `CLAIM_REGISTRY.csv` (141 rows, 2026-08-24).
**Scope**: every claim whose status is `INFERENCE` (30) or `UNKNOWN` (30) — 60 open claims,
grouped by the object they are about.

**Three rules this file enforces (directive v4.0)**
1. Where two readings cannot be separated by evidence now available, **both are kept and the
   inseparability is stated in words**. Sections that do this are marked ⚖ **INSEPARABLE**.
2. **A better backtest fit, a better PnL, or a better distance never selects a reading.** Where
   such a preference exists in the record it is reported as a measurement and explicitly refused
   as an arbiter. (The general form of that error is FALSIFIED as V-057.)
3. A falsifier that does not exist in the fixed 164-image corpus is written as *not available*,
   not as "future work".

Each entry gives: **live readings** → **what the evidence currently favours** → **FALSIFIER**.

---

# PART A — Early era (2023-01 … 2026-01): Solar / CAND2 objects

## A1. Strategy identity of `SolarWindRKSelTime`

**E-002 (INFERENCE)** — Because the full visible Parameters group exposes exactly six boxes
(A1..A5 + Quantity) and no time-of-day box, any session/time window used by the strategy is
hard-coded in the author's own NinjaScript rather than configured through a parameter.
- Live rivals: the window is imposed by a **TradingHours template** rather than code; `SelTime`
  names something that is **not a time window**; time parameters exist **below the visible crop**
  in a scrolled pane.
- Favouring: the panel read (E-001, FACT) shows the group header→next-group-header run complete,
  and TradingHours reads "Use instrument settings". Nothing rules out the scrolled-crop rival.
- **FALSIFIER**: any frame of this strategy showing a time parameter box inside the Parameters
  group, or a TradingHours setting other than "Use instrument settings".

**E-003 (INFERENCE)** — The engine behind `SolarWindRKSelTime` is a Solar Wave RK-family trend
engine.
- Live rivals: numeric coincidence; a different indicator sharing the same defaults; the author
  re-implemented the geometry himself (his own claim, OTRIMG-0004: "self-developed momentum
  indicator") — in which case "family" is a lineage claim, not a code claim.
- Favouring: A1..A5 = 90/179/5/10/10 is numerically identical to the campaign-#1 vendor baseline
  quintuple, and the visible name is `SolarWind…` against vendor product `Solar Wave RK`.
- **FALSIFIER**: a recovered SolarWind stream our Solar Wave implementation cannot produce on the
  same bars.

## A2. Does his engine compute the vendor mathematics?

**E-005 (UNKNOWN)** — Whether the trader's engine computes the same mathematics as the vendor
Solar Wave RK indicator we recovered (E-004, REPRODUCED) is unresolved.
- Live readings: same math under a renamed wrapper | his own re-implementation with identical
  parameters but different **event emission** | a genuinely different engine that happens to share
  the quintuple.
- Favouring: nothing decisive. No frame shows his indicator output, his source body, or any
  per-bar series of his. `TRACK_S_REPORT.md` notes the residual is consistent with a re-entry
  event-emission difference.
- **FALSIFIER**: his source code, a frame showing his `Signal_*` series, or per-trade timestamps
  for any day.

## A3. What the 2023–2025 master report actually covers

**E-007 (INFERENCE)** — That OTRIMG-0002 describes the trader's **entire** trading over
2023-01..2025-02, rather than one of several concurrently running strategies, is not established.
- Live readings: in Feb-2025 only one strategy existed and the multi-strategy statement (V-081,
  Dec-2025) postdates it | the master frame is one sleeve of several already in 2023–2024 | the
  master frame is a research backtest, not a record of what actually traded.
- Favouring: V-081 (FACT, author verbatim) is the strongest single constraint and pushes toward
  the sleeve reading, but it is dated ~10 months after the capture.
- **FALSIFIER**: a frame showing two concurrent 2023–2025 strategies, or an account-level Trade
  Performance report covering the same window.

## A4. CAND2's model status ⚖ **INSEPARABLE**

**E-010 (UNKNOWN)** — Whether CAND2 is the original trader's early-family strategy. **ORIGINAL_
PARITY has never been tested**, because no test in this campaign has the trader as an endpoint:
the only original-side quantities are pixel-read report aggregates and one per-day table.
- Live readings: CAND2 **is** his build | CAND2 is a **behavioural mimic** sharing aggregates
  without sharing mechanism | CAND2 is **one sleeve of several**.
- Favouring: E-008/E-015/E-022 (REPRODUCED) put CAND2 close to his aggregates on some windows and
  far on others. IMPLEMENTATION_PARITY (E-009) is about three of our own artifacts and **does not
  transfer**.
- **FALSIFIER**: his source code, per-trade timestamps, or a Trade Performance export for any
  2023–2025 day. None exists in the corpus.

**E-012 (INFERENCE)** — CAND2 is a T1-flip / A2-driven skeleton plus a session-equity wrapper, and
is **not parameter-faithful** to the panel-visible A1–A5 = 90/179/5/10/10 strategy: per the code
read (E-011, FACT) A1 does not materially participate in trading decisions, the weak state
generates no T3 signal, and A5 is not exposed at all.
- Live rivals for what that means about him: the trader's A1 is **also inert** (a vestigial vendor
  knob he never removed) | A1 drives a **TrendVector-referenced layer** CAND2 omits | A1 affects
  **display only** | the panel labels are **not positionally aligned** with vendor parameter order.
- Favouring: `runs/OTR_R12_PARAM_INTERVENTION/out/event_family_deltas.csv` (OPEN run, no REPORT.md)
  shows A3/A4 move T3 counts 3,466 → 3,896/4,056 and A5 moves T2 counts 6,286 → 6,489 in the
  recovered core, i.e. the knobs are **not** inert in the vendor mathematics.
- **FALSIFIER**: a CAND2 variant in which A1 and A5 materially participate and which still
  reconstructs the Jan-2023 daily aggregates; or a frame revealing the un-obfuscated labels.

## A5. The January-2023 "42/42" assignments

**E-014 (INFERENCE)** — The so-called "42/42 cent-exact labels" are **CONDITIONAL_LATENT_LABELS**,
not observed trade labels. `run_r1e_subsetdiff.py` generates **our** candidate trade universe
(`WrapperPolicy comm_side=2.09, entry_types=(1,3), reverse_on_flip=True`) and then searches, per
day, which subset of **our own** trades must be REMOVED so the day's six aggregates reconstruct
exactly. Every TAKE/SKIP assignment is a latent variable conditional on that universe being his.
The phrase "ground-truth trade labels" is retired.
- Live rivals: his true trade set contains trades our universe never generates (in which case the
  assignments are wrong even though the aggregates reconstruct) | for some days several subsets
  reconstruct the same six aggregates | his commission basis differs from the assumed $2.09/side.
- Favouring the conditionality reading, strongly: `runs/OTR_R11_INVERSE/out/solution_counts.json`
  (OPEN run) shows **six different candidate universes** (U1_T1, U2_T1_T2E, U3_T1_T2L, U4_T1_T3,
  U5_T1_T2E_T3, U6_T1_T2L_T3) each admit **exactly one** removal solution on 2023-01-09/10/11 —
  the aggregates do not discriminate the universe. The same run records that CAND2 produces
  **fewer** trades than target on 2023-01-13 and 2023-01-17 (4 vs 6), which structurally falsifies
  a removal-only solver as a global explanation.
- **FALSIFIER**: a per-trade list (timestamps and prices) for any January-2023 session.

## A6. The session-equity D-gate ⚖ **INSEPARABLE**

**E-017 (UNKNOWN)** — The trader's actual session-gate constants. **None of the 164 corpus frames
shows any of them**; the gate is not a panel group. X is interval-identified only (≈[1425,1925]);
C is weakly identified; cap=20 and cooldown=3 came from a gap-localisation refinement, not from
evidence.
- Live readings: **K3** (block a side after 3 consecutive same-side losses) vs **ALT_loss_side_K4**
  (block the side after 4 **total** same-side session losses) | **no equity gate at all**, with the
  trade-count excess explained instead by our engine emitting entries his does not | a gate
  configured in a panel group below the visible crop | per-machine or per-era different constants.
- Favouring: neither K3 nor K4. **K4 yields a *better* master net (≈$252k vs our $264.9k against a
  $292.2k target) and that is explicitly refused as a selection criterion** — the directive forbids
  choosing by PnL, and both members stay live.
- **FALSIFIER**: per-day rows for **2023-02-02, 2023-02-07, 2023-07-20 or 2023-08-25** would
  separate K3 from K4. **Those days are not in the corpus.** Any panel frame exposing a
  session-equity group would settle the rest.

**E-018 (INFERENCE)** — The four-component gate **structure** (prior-red evening block; arming on a
session equity high-water threshold with an earlier pre-noon threshold; blocking a side after K
same-side losses; a session trade cap plus re-entry cooldown) is a reading consistent with the
daily aggregates. It is **not** a confirmed structure: its entire support is the
CONDITIONAL_LATENT_LABELS of E-014 plus an independent re-implementation that reproduces the same
latent assignments.
- Live rivals: the "necessity" of the four components is necessity **within our candidate
  universe**, not in general | a single unmodelled signal-layer difference could absorb all four |
  the gate mimics an external cause (his machine off, a manual stand-down — disfavoured by V-096
  "fully automated").
- **FALSIFIER**: a per-trade record for any 2023 session showing entries at times the gate forbids.

## A7. The `Bars.IsFirstBarOfSession` fragment

**E-020 (INFERENCE)** — That the visible line (E-019, FACT) implements a first-bar-of-session
**entry/signal drop** — the B1 rule at `OriginalTraderSolarCAND2_v2.cs` lines 290–291 — is an
inference. The fragment proves only that his source contains session-boundary logic; its body is
unseen.
- Live rivals (all consistent with the same predicate): session state / counter reset |
  prior-session net roll-forward | daily P&L reset | warmup or BarsRequired handling | time-window
  arming | a session-open **breakout trigger** (an entry, not a drop) | logging.
- Favouring: nothing. **Our own file uses that same predicate for two different purposes** — lines
  236–247 (session state reset) and lines 290–291 (the B1 drop) — which is precisely the ambiguity.
- **FALSIFIER**: a frame showing the body of the if-block, or a per-trade record showing whether
  first-bar entries ever occur.

## A8. The hp vs dev machine split

**E-023 (INFERENCE)** — "hp = a sibling build with stronger suppression and winner extension" is a
reading, not a proven partition. **A visible counterexample is on record**: OTRIMG-0081 (week
2025-10-26..10-31, annotated machine `hp`) is fitted almost exactly by CAND2 — 50 simulated vs 50
target trades, net −$3,310 vs −$3,330, weighted distance 0.153.
- Live rivals: **era confound** rather than machine (ERA_A comprises 14 hp frames and 1 dev frame)
  | per-week market character (12/21 is a holiday week, 9 target vs 17 simulated) | the same build
  posted from different machines against different feeds or contract rolls | a different strategy
  among several concurrent ones being sliced per machine (V-081) | different commission/settings
  templates per machine.
- Favouring the measurement (E-022 / V-091, REPRODUCED): the within-era-B contrast (hp |Δn| ≈31% vs
  dev ≈11%) is the cleaner part, because it removes the era confound.
- **FALSIFIER**: a dev-machine week that overtrades like the hp group, or a frame showing a
  different strategy name on one machine.
- See also **V-090 (UNKNOWN)**, which holds the machine→build mapping open at the account layer.

## A9. The A3–A5 retune and the layer it controls

**E-026 (INFERENCE)** — Because a trader does not retune knobs that do nothing, his build most
likely contains an **active layer that A3–A5 control** and that our T1-only model lacks.
- **The layer must not be called a "pullback" layer.** Nothing in the evidence names it, and in the
  recovered core A3 and A4 move **T3** (strengthening) far more than they move T2 (pullback).
- Eight live candidate mechanisms, none preferred: T2 pullback-priced entries | T3 re-entries /
  strengthening events after touch exits | the weak-vs-strong state machine (weak duty cycle moves
  66.1% → 73.9% under the retune) | Signal_Wave-based entries | TrendVector-referenced entries or
  exits (A1-driven, absent from CAND2) | re-entry and cooldown machinery | exit gating or
  trailing-stop arming | **a cosmetic or abandoned retune with no behavioural effect** | a shared
  panel serving a different strategy.
- Favouring: E-024 (FACT — the values changed) plus E-025 (REPRODUCED — they are inert in our
  T1-only model). The step from those two to "his build contains an active layer" carries a hidden
  premise that the retune was deliberate and behavioural; the cosmetic-retune rival is not excluded
  and **"MUST" is not supported**.
- **FALSIFIER**: a per-trade stream for any post-2025-11-07 week, or a frame revealing the
  un-obfuscated parameter labels, would name the layer.

## A10. The 2025-02-27 ninety-trade day

**E-029 (UNKNOWN)** — Which build produced the 2025-02-27 row. No frame shows the strategy panel of
that day's run, and the surrounding era shows near-daily experimentation: a Quantity-3 experiment
2/6-8, commission-template churn ($4.18 → $12.54 → $0 → $5.68 → $0), LossLimit 4000 first seen 2/13
and 2500 by 2/18, and the class rename to `RKSelTimeDSTMa` by 2/18.
- Live readings: a transitional DSTMa build with an extra tight-risk entry layer | a one-off
  experiment build | a different concurrently running strategy posted that day | a different bar
  type or instrument for that run.
- **FALSIFIER**: any frame showing the settings pane of the 2/27 run.

**E-030 (INFERENCE)** — "The 2/27 row is a one-off experiment build rather than a persistent fast
layer" is an inference only. Its support is the R10 side-finding that a plain T1 control's
average-loss profile tracks the whole Feb–Mar daily series at the same hold scale
(sim/target −840/−945, −808/−869, −717/−742, −588/−596, −682/−704, −658/−619), leaving 2/27 as the
single unexplained row.
- Live rivals: a genuine additional tight-risk entry layer that only fires on high-volatility days
  (2/27 was the NVDA-aftermath session) | a different concurrent strategy posted that day | a
  manual or intervened session (disfavoured by V-096, "fully automated") | a different bar type |
  a data or transcription artefact in the 90 count.
- **FALSIFIER**: any bounded member that produces ≈90 trades on 2/27 **without** exploding on
  3/4-5 and 3/12-14.

## A11. Which St row changed 65 → 75 ⚖ **INSEPARABLE**

**E-035 (INFERENCE)** — The St row that changed 65 → 75 on 2025-11-14 is **not** the initial-stop
row (row 1) but a second stop tier; and the short-side stop is time-varying between 65 and 75
within era B. **Both members are kept and no unique rule is forced.**
- Live readings: row 3 is a short-side-specific stop | a second contract-unit stop (relevant once
  Entries-per-direction goes 1 → 2 in mid-Jan-2026) | a re-entry stop | a stop belonging to a
  different sleeve or machine | the trader toggled the value back and forth between captures | row
  3 is not a stop at all and the −1,500 has another cause.
- Favouring: E-033 (FACT) — exact −1,300.00 caps persist **after** 11/14 (weeks of 11/9, 12/14,
  1/18) while −1,385.00 / −1,500.00 appear in other era-B weeks, predominantly short-side; plus
  E-034 (REPRODUCED) — the 75-point long control collapses the long column (2/11 vs 8/11 hits).
- **FALSIFIER**: any panel frame captured between 2025-12-14 and 2026-01-18 showing the St row
  values. No such frame is in the corpus.

---

# PART B — 2026 era: VWAP-Flux, account and method objects

## B1. The 2026 parameter panel

**V-004 (INFERENCE)** — The trader's 13-field block is a VWAP Flux **parameter surface**
(identification at parameter-layout level only). Reading of V-001 + V-002 + V-003 together: exact
vocabulary, exact order, exact enum literal.
- Live rival: a different ninZa-ecosystem product re-declaring the same 13 labels in the same
  order (no such product found in the 17-product fingerprint DB).
- **Do not read this row as "the licensed component is embedded"** — that is V-013/V-014.
- **FALSIFIER**: a vendor product with an identical 13-label ordered surface.

**V-009 (UNKNOWN)** — Whether a 14th VWAP-Flux-family field exists among the never-labelled rows
**above** `Volume Base`. Every frame crops or scrolls past the head labels.
- Live readings: (a) a 14th vendor field hides in the head | (b) the head is entirely
  trader-authored (see V-074).
- **FALSIFIER**: a capture showing the strategy NAME row or labelled head rows. **No such frame
  exists in the corpus, and corpus label-surface exhaustion is on record (V-028), so this cannot be
  closed from the fixed corpus.**

## B2. What the trader's 2026 computing engine is ⚖ **INSEPARABLE — five live hypotheses**

**V-014 (UNKNOWN)** — *the* central open question of the 2026 half. No image, artifact, statement
or measurement in evidence identifies the engine. This row **supersedes both** the earlier "custom
strategy embedding licensed ninZa VWAP Flux" wording **and** the later "own-implementation (H3/H4)
now leads" wording.

| id | hypothesis | FOR | AGAINST |
|---|---|---|---|
| **V-015 (H1)** | official licensed component inside a custom wrapper / hosting arrangement | verbatim 13 labels incl. the `BidAskPrice_RealVolume` enum literal and compound label punctuation — most economical as pass-through of an existing type | V-013 |
| **V-016 (H2)** | official component's signal outputs consumed, but the trader supplies his own historical volume handling so the stack computes on history | explains V-011/V-012 without requiring reimplementation of the cloud/signal math | — |
| **V-017 (H3)** | part of the concept set reimplemented, vendor component or vocabulary for the rest | — | panel-level evidence **cannot separate H2 from H3**: a caller must surface the inputs it sets either way |
| **V-018 (H4)** | full clean-room private implementation using vendor-style parameter names | he demonstrably writes NinjaScript (code editor visible in OTRIMG-0053-era frames — *second-hand citation, see caveat below*; years of self-modified panels); omission of zone controls fits a needed-subset build | verbatim label/enum replication |
| **V-019 (H5)** | vendor/version/hosting behaviour not fully understood by us; the apparent contradiction dissolves under facts we do not have | five changelog entries, **none** about historical calculation | — |

**V-013 (INFERENCE)** — V-011 and V-012 are jointly inconsistent with the trader's historical
backtests having been produced by a **directly-embedded licensed VWAP Flux running in the displayed
mode**. NARROWED per directive v4.0: this rules out **one** embedding scenario. It does **not**
establish reimplementation (that over-claim is FALSIFIED as V-022).
- Conditional on: the manual sentence applying to the build he ran; hosting context possibly
  changing historical behaviour (H5).
- **FALSIFIER for the whole object**: a Signal_Trade-timestamp-bearing frame, a strategy-name row,
  a vendor-branded dialog, or an author statement about the component. For H1 specifically: proof
  that no hosting arrangement computes historically in the displayed mode. For H4: any direct
  observation of a licensed VWAP Flux assembly in his environment.
- ⚠ **Sourcing caveat on V-018's FOR clause**: "code editor visible in OTRIMG-0053-era frames" was
  carried from `screenshot_forensics/VF_PANEL_COMPLETENESS_NOTE.md §1 H4` and **was not verified
  against `IMAGE_MASTER.csv` or the image** in this pass. E-019 (FACT) independently establishes a
  code editor in OTRIMG-0053; the "era-frames" plural is the unverified part.
- **What must never be cited here**: V-021 (FALSIFIED) — the absence of vendor artifacts on **our**
  machine is not evidence about what the trader owned or ran.

## B3. VWAP layer lifecycle ⚖ **INSEPARABLE — REOPENED 2026-08-24**

**V-024 (UNKNOWN)** — ACTIVE-ANCHOR (all retained layers keep updating every bar) vs SEGMENT/BLOCK
(completed segments freeze; VWAP recalculated per segment). The prior "solved-to-class / ACTIVE
incumbent (strong)" status is **WITHDRAWN**.
- **FOR ACTIVE-ANCHOR**: V-025 (width 47.0 vs 106.0 pts), V-026 (movers 5.00 vs 1.34; boundary
  jumps 11.1 vs 21.2 pts) — both REPRODUCED morphology on our substrate; plus V-027 and the only
  public precedent, LuxAlgo Rolling VWAP Channel.
- **FOR SEGMENT/BLOCK**: V-023 — the vendor's own product-page natural language ("divides the
  market into smaller time segments and recalculates VWAP for each segment"). **That row carries a
  provenance gap** (see CURRENT_KNOWN §1.6): the verbatim string is not archived in this repo. The
  reopening rests on it, so the gap is load-bearing.
- Morphology measurements are retained as **evidence for** active, not as a class decision.
- **FALSIFIER**: a licensed-oracle bar-by-bar rail series; or a chart frame with a readable frozen-
  rail staircase (or its demonstrated absence at hour boundaries).

**V-027 (INFERENCE)** — The manual's own embedded chart PNGs (pp.3/8, NQ MAR26 1-min and 3-min,
Anchor 60) show hourly rail steps with smooth drift between them.
- Live rival: BLOCK geometry could also show hourly steps; "smooth drift between steps" is the
  discriminating part and is **an eyeball judgement on low-resolution PNGs**.
- **FALSIFIER**: a pixel-metric extraction of the manual chart rails disagreeing with the eyeball
  reading.

**V-029 (UNKNOWN)** — Price input for the VWAP layers: `close × volume` vs `hlc3 × volume`.
- Second-order: the two differ by mean 0.75 pt (p95 2.4) on our substrate — too small to matter for
  the current residual. `close` was used throughout R7/R7b/R8.
- **FALSIFIER**: an oracle rail series, or chart geometry at sufficient resolution.

## B4. Rail formula ⚖ **INSEPARABLE at two levels**

**V-035 (INFERENCE)** — The rail formula is in the **percentile family** (min-max rejected) **at
the vendor level**. Downgraded from the earlier "RESOLVED at vendor level without purchase".
- Built from: V-033 (REPRODUCED discriminator — min-max forces FVP to the cloud midspan by
  construction; percentile FVP deviates by mean 8.9 pts) applied to **V-034 (INFERENCE)** — on the
  manual's chart PNGs the FairValue plot hugs the price-side cloud edge through sustained trends
  and never sits at the stretched-range midpoint.
- Live rivals: min-max on a population whose extremes move together would also keep FVP near price
  (not observed, but **not pixel-tested**). Min-max remains **live for the trader's build** (V-036).
- Inherits the V-024 lifecycle caveat: V-033 was computed under ANCHOR.
- **FALSIFIER**: an oracle rail series showing FVP at midspan; or a re-derivation under BLOCK
  showing the discriminator is not diagnostic; or a pixel-metric extraction of FVP position between
  Min and Max across the manual charts.

**V-038 (INFERENCE)** — The Fair Value Plot equals the **Median (50%) rail** of the layer
population (FVP = Q50). Vendor level.
- Live rivals, all documented and undiscriminated: volume-weighted centre of the layer set |
  recency-weighted centre | a combined 5-segment VWAP.
- Used as FairValue in **every** OTR-VF-CAND1 member.
- **FALSIFIER**: an oracle FVP series vs our Q50 series bar-by-bar.

**V-037 (UNKNOWN)** — Percentile-**linear** vs **nearest-rank** interpolation. Separable only on
the outer rails; never attempted against any observed series. Inner rails are near-identical; outer
rails differ by ≈1.7 pts on our data. `percentile_linear` was used in all runs — **an assumption
inside those runs, not a finding of them**.
- **FALSIFIER**: an oracle rail series at the 95/5 levels.

**V-036 (UNKNOWN)** — Whether the **trader's** build uses the same rail formula as the vendor's
product. Depends entirely on V-014.
- Live readings: same-as-vendor (assumes V-102) | trader-specific formula.
- **FALSIFIER**: Signal_Trade timestamps or per-day 2026 labels from his build.

## B5. Trend state ⚖ **INSEPARABLE cluster**

**V-042 (UNKNOWN)** — Which trend construction his build uses. `T_A` (close beyond Max/Min rails),
`T_C` and `T_D` (EMA20-vs-FairValue cross) sit in **one cluster with mean-distance spread ≤ 0.04**.
Structurally diverse trend members all plateau at 0.48–0.52, so the trend layer is not what drives
the residual. **V-041 (REPRODUCED, T_C leads 13/17 LOWO) is a ranking, not a selection.**
- **FALSIFIER**: a `Signal_Trend` series from an oracle, or per-day 2026 labels.

**V-043 (UNKNOWN)** — Whether the 4-state strength dimension of `Signal_Trend` is used. Not
identifiable from weekly aggregates on 1-min bars. Side-fact (REPRODUCED): adding a bar-level
CVD-slope strength gate moves the leader's mean distance 0.476 → 0.492 (mild degradation).
- Live readings: strength gate present | absent.
- **FALSIFIER**: per-day or per-trade 2026 labels.

**V-040 (INFERENCE)** — The vendor's 2026-02-24 upgrade was the 2-state → 4-state (strong/weak)
change of `Signal_Trend`. Bracketing between two documented endpoints (V-039, FACT); the vendor
never states the mechanism.
- Live rival: some other change to `Signal_Trend` that coincidentally preceded the observed 4-state
  documentation.
- **FALSIFIER**: a vendor statement of what changed on 2026-02-24.

## B6. The 2026 entry trigger ⚖ **INSEPARABLE — cluster, not a model**

**V-051 (UNKNOWN)** — Which member of OTR-VF-CAND1 (if any) corresponds to the trader's build.
**Declared inseparable on available labels.**
- Members kept live: `T_C|P_MED|C_DIR|H1a|X_OPP` (leader) | the same **+strong_only** |
  `T_C|P_Q75|C_REC|H1a|X_OPP` | `T_D|P_IN|C_REC|H1c|X_FLIP` (**demoted**, not removed — it swung
  −32,500 on a +8,630 target week (V-050) but retains the best failure-week catastrophe geometry
  (V-052)) | **none of them**.
- Cluster membership is an assignment under **our own** candidate universe, not an observation.
- **FALSIFIER**: Signal_Trade timestamps for any single day, or a per-day 2026 Analyzer table of
  the OTRIMG-0003 kind. **Neither exists in the fixed corpus (V-104), and with V-060 open, member
  separation is additionally blocked until QtyPerTrend/Split is re-implemented at signal level.**

**V-046 (INFERENCE)** — The common structure of the surviving cluster is: trend episode → pullback
toward the cloud core (Median or a rail) → close-quality confirmation → entry; SAR-or-flip exit.
This is a description of what **our survivors** share; his actual trigger has never been observed.
- Live rival: any two-stage trigger family we did not enumerate — **the grid is bounded by our own
  hypothesis space.**
- Favouring: qualitatively consistent with the vendor manual's own chart arrows (EV-040), which
  fire on pullbacks toward FVP/cloud in trend direction.
- **FALSIFIER**: Signal_Trade timestamps showing entries that are not pullback-to-core events.

## B7. Signal filters ⚖ **INSEPARABLE — and the fit is explicitly refused as arbiter**

**V-055 (UNKNOWN)** — The orientation of the CloseThreshold filter. Two live readings; **the manual
wording and the empirical fit point opposite ways.**
- **H-MANUAL (= H1c)**, manual-verbatim: for a sell, `(Close − Low) ≥ T%` of range; at T=10 this
  excludes only the extreme-against 10%, so the filter barely binds (≈90% of candles pass).
- **H-STRICT (= H1a)**: require the close in the extreme 10% **toward** the signal.
- What the evidence says: V-054 (FACT) fixes the trader's value at 10 and every vendor preset at
  70 — a deliberate customization under **either** reading. V-056 (REPRODUCED) ranks H1a above H1c.
  **V-057 FALSIFIES the step from that ranking to vendor semantics**: the fit is joint over trend
  construction, pullback depth, confirmation, orientation and exit, all carrying the V-060 defect,
  and the manual's own wording is the inverse of H1a.
- **At T=10 the two readings are maximally different, which is exactly why the panel value cannot
  arbitrate. Both stay alive.**
- **FALSIFIER**: an oracle Signal_Trade series on a day with candles that separate the readings.

**V-061 (UNKNOWN)** — The QtyPerTrend reset rule (what ends an "episode"). Implemented as a
trend-state-run reset; alternatives are not separable on weekly aggregates.
- Live readings: episode = trend-state run | episode = S/R-zone occupancy (the manual names
  "trend / S-R-zone episode") | episode = some vendor-internal state.
- Coupled to V-072: the trader exposes no `Zone Period`, so the zone half of the definition may be
  inert in his build — or not.
- **FALSIFIER**: an oracle Signal_Trade series across a trend reversal.
- ⚠ Blocked behind **V-060 (FALSIFIED)**: our counters gate executed entries and SAR flips, not
  indicator signals, so no current measurement bears on this question.

## B8. The 130-point stop layer

**V-065 (INFERENCE)** — The 130-pt stop is a **wrapper / account-level risk layer** rather than a
VWAP-Flux module property. Reading of V-064 (it pre-dates the first VF frame by one week) plus
V-066 (no vendor material documents any such stop).
- Live rival: a coincidence in which his VF-era wrapper stop happened to match a pre-VF S-era
  wrapper stop.
- **FALSIFIER**: vendor documentation of a 130-pt / 520-tick / $2,600 stop, or evidence the
  2026-02-01..06 week already ran the 2026 build.
- Note the ceiling on this object: V-063 (REPRODUCED) tested **two** candidates; that one 130-pt
  stop rather than any other configuration yielding the same row is the inferential step.

**V-069 (INFERENCE)** — −3,046.18 is a 130-pt stop plus ≈22 pts of live slippage, and −1,426.18 is
a 65-pt-class stop plus slippage, so **both** a 130-pt-stop sleeve and a 65-pt-stop sleeve were live
in June 2026.
- Live rivals: MNQ sizing or a different contract mix could produce the same dollar figures under
  other point stops (checked; does not resolve) | a single sleeve with a time-varying stop.
- Tension on record: this sits against the count-based reading that the S-family was retired by
  June (V-090). Recorded as an open decomposition; **no weights fitted**.
- **FALSIFIER**: a TP per-instrument breakdown frame.

## B9. Zones

**V-071 (INFERENCE)** — The trader did not **expose** the zone module in any captured panel.
Reading of V-006 (no zone label anywhere) plus V-010 (block closed at both boundaries).
- Live rival: a `Zone Period` row could sit in the never-labelled head above `Volume Base` (V-009).
- **"Did not expose" is weaker than "did not use".**
- **FALSIFIER**: a labelled head capture.

**V-072 (UNKNOWN)** — Whether zone logic operates inside his engine without an exposed parameter.
Unobservable from panels; depends on V-014.
- Live readings: zones inert in his build | zones active with a hard-coded period | no zone code at
  all.
- **FALSIFIER**: oracle comparison, or a Signal_Trade series showing zone-anchored behaviour.

## B10. Panel variants and the February-2026 shift

**V-074 (INFERENCE)** — The mutating head rows above the VF block are the **trader's own controls**
rather than vendor fields: a vendor panel does not gain, lose or retype rows between weekly runs.
- Live rival: an unlogged vendor GUI-library change could alter panel appearance (`ninZaResources`
  has its own changelog).
- Favouring: the 2026-02-20 checkbox banks have **no** vendor event in either changelog (product gap
  02-09..02-24; ninZaResources gap 01-06..03-24).
- **FALSIFIER**: a vendor changelog entry matching a head-mutation date.

**V-076 (INFERENCE)** — The two odd weeks (V-075, FACT) were temporary variant or parallel-test
builds rather than a permanent migration, read from the revert pattern.
- Live rival: parallel concurrent sleeves whose SA slices were posted in alternation.
- **FALSIFIER**: an SA slice frame showing both stacks in the same week.
- ⚠ **New competing evidence, not yet a registry row**: `vwap_flux_family/2026_PANEL_TOPOLOGY.md`
  (2026-08-24) reads OTRIMG-0138 and OTRIMG-0150 as **top/middle scroll slices of one growing
  list** rather than distinct builds, and states that the "sibling build" readings
  VAR2026-BANKS-0220, VAR2026-GATED-0429 and VAR2026-V2-0605 in `2026_VARIANT_LEDGER.csv` are not
  supported by scroll evidence. That analysis must be reconciled with V-076/V-077 in the next pass.

**V-077 (UNKNOWN)** — Whether OTRIMG-0119's checkbox banks are the hidden **top** of the flagship
composite panel or a **sibling build** run that week. No single frame shows both the banks and the
VF block.
- Live readings: same composite panel, scroll-position hypothesis | separate sibling build.
- Favouring the scroll reading: 0119 carries the same −$2,600 stop signature as the flagship weeks;
  and the topology pass (above) measures 0119 at scroll 0 with N=7.28 against 0117's N=7.13 one week
  earlier.
- **FALSIFIER**: a frame showing both.

**V-079 (UNKNOWN)** — Whether the 4-day gap in V-078 indicates when the trader installed or updated
VWAP Flux. An install date cannot be distinguished from a screenshot-coverage gap.
- Live readings: install in the 02-09..02-13 window | earlier ownership with no earlier panel frame.
- **FALSIFIER**: an author statement, or a dated earlier panel frame.

**V-080 (INFERENCE)** — The late-February 2026 behaviour shift was caused by the vendor's
2026-02-24 `Signal_Trend` upgrade breaking a wrapper that tested `Signal_Trend == 1`. Date-aligned
mechanism only; **no proof his wrapper reads `Signal_Trend` that way, and under V-014 he may not
consume the vendor series at all.**
- Live rivals: a trader-side parameter change coinciding in time | market-regime change | no real
  shift (aggregate noise).
- **FALSIFIER**: a `Signal_Trend`-consuming code observation, or a behaviour shift dated away from
  02-24.

## B11. The account layer — six mandatory UNKNOWNs

**V-084 (UNKNOWN)** — Which strategies / sleeves produced the June-2026 Trade Performance totals.
No SA slice frame overlaps the 6/7–6/18 TP weeks, so no direct sleeve subtraction is possible.
- Live readings: any partition of {VF flagship, a 65-pt-stop sleeve, an unidentified fast/tight
  sleeve, further unknown sleeves}. **Prior wording that named specific carriers is downgraded to
  hypothesis.**
- **FALSIFIER**: an SA slice screenshot for 6/7–6/18, or a TP per-instrument breakdown frame.

**V-085 (UNKNOWN)** ⚖ — How posted weekly SA numbers map onto account results.
- H1 each sleeve qty 1 independently, account gross = sum | H2 account-level net capped at ±1
  (netting) | H3 sleeves mutually exclusive by time/state | H4 a common execution wrapper
  arbitrates. **H1 was previously described as "favored"; that preference is not evidence.** TP
  report filters are themselves unknown.
- **FALSIFIER**: a Trade Performance execution list showing (or excluding) simultaneous 2-lot
  exposure moments.

**V-086 (UNKNOWN)** — Whether the June-2026 TP frames are LIVE or SIMULATED. No account tag is
visible in any frame. Real commission columns ($141.20 / $96.76) are consistent with live but do
not prove it — NT8 sim accounts can carry a commission template.
- **FALSIFIER**: a frame showing the NT8 account selector or an account tab with balances.

**V-088 (UNKNOWN)** — Account-level PnL for any period. No account statements, no NT8 account tab
with balances. **Open contradiction C-3 on record**: the author's stated 2025 "~$150k+" does not
equal the posted slice sum (~$232.1k) — consistent with V-089 (the slices are $0-commission
single-strategy views) but not resolved by it.
- **FALSIFIER**: an account statement frame.

**V-090 (UNKNOWN)** — The machine→build mapping (creator / hp / dev / mimi). Machine tags are
readable per frame (E-021, FACT); what they imply about distinct builds is not established.
- Live readings: one build run on several machines | per-machine build variants | machine tag
  correlates with **era** rather than build.
- ⚠ Competing evidence, not yet a registry row: the 2026 topology pass finds panel **extent is
  machine-independent** (0127 "hp" N=10.35 sits between 0125 "dev" 9.82 and 0129 "dev" 10.12),
  which cuts against "different machine, different build" for the 2026 frames.
- **FALSIFIER**: per-day 2025–2026 labels, or an author statement about the machines.

**V-095 (UNKNOWN)** — What produces the $1.04/RT-basis commission (V-094, FACT).
- Live readings: some sleeves trade MNQ | a partial/discounted commission template | the TP
  commission column is per-side, not per-RT.
- Matters because MNQ sizing would change every dollar-based stop inference (V-069).
- **FALSIFIER**: a TP per-instrument breakdown frame.

**V-087 (INFERENCE)** — Live execution is evidenced at three points: 2025-02-03 (SolarWindRK
running on NQ MAR25, tab visible, day after the master backtest) and the two June-2026 TP frames
with populated commission columns; author statements corroborate continuous live operation between
them. **No account statement exists anywhere in the corpus.**
- Live rival: sustained simulation with a commission template.
- Distinct from V-086: this is about the **program** being live, not about which account produced a
  given report.
- **FALSIFIER**: an account statement, or a frame showing a Sim account tag.

**V-092 (INFERENCE)** — The June TP profile (23–33 trades/day, 20–34 min holds, WR 42–50%) exceeds
any single observed SA sleeve, so at least two concurrent sleeves ran beside the VF flagship.
- Live rivals: one sleeve we have never observed could carry the whole profile | the TP view
  aggregates instruments (MNQ) we have not accounted for.
- Consistent with V-081 but **not entailed by it**.
- **FALSIFIER**: a single-sleeve SA slice matching the TP profile.

**V-097 (INFERENCE)** — There is no **runtime** discretionary layer in the trader's system, read
from V-096 (FACT, "fully automated").
- Live rival: "fully automated" could describe order placement while entry selection is
  periodically re-tuned by hand — which V-098 (FACT) shows he does.
- Excludes discretion at runtime; **does not exclude between-run re-tuning**.
- **FALSIFIER**: evidence of intra-week manual intervention.

## B12. The purchase gate

**V-100 (INFERENCE)** — The EVI-downgrade rationale — that a vendor oracle would answer **vendor**
semantics rather than **his build's** — is **conditional on V-014 remaining UNKNOWN**.
- Live rival: under H1 or H2 (V-015/V-016) the oracle **would** answer the trader's build directly,
  and the EVI rises sharply.
- The previous gate wording asserted "his stack is most plausibly his OWN implementation" as the
  ground for the downgrade. Under directive v4.0 that ground is itself UNKNOWN, so **the downgrade
  is provisional**. (Gate state itself is V-099, FACT: CLOSED with three reopen triggers.)
- **FALSIFIER**: any evidence bearing on H1/H2 vs H3/H4.

## B13. Method-level assumptions

**V-102 (INFERENCE)** — Vendor-level resolutions (rail family, FVP = Q50, cloud lifecycle) transfer
to the trader's build **only under the assumption that he mirrored what the vendor plots showed
him**. A load-bearing transfer assumption used throughout the VF work, never tested.
- Live rivals: he may have reimplemented with different conventions (V-014 H3/H4) | he may never
  have inspected the plots closely | his frozen VF-13 panel is consistent with either.
- Flagged explicitly because V-035, V-038 and V-024's evidence base are **all vendor-level**.
- **FALSIFIER**: Signal_Trade timestamps or per-day labels from his build compared against a
  vendor-convention replica.

**V-105 (UNKNOWN)** — That the 2026 flagship is a **single** strategy running one
VWAP-Flux-family model whose weekly SA slices are the posted numbers. Assumed throughout the VF
fitting work; never established. The strategy NAME is never visible in any 2026 frame.
- Live readings: the posted 2026 weekly slices may come from more than one strategy over the series
  | the flagship panel may host a composite with legacy machinery above the VF block (V-077).
- **Every OTR-VF-CAND1 distance is computed against targets whose provenance rests on this
  assumption.**
- **FALSIFIER**: a frame showing the strategy-name row, or an SA slice with a named strategy.

---

## Cross-check

| Status | Count |
|---|---|
| INFERENCE | 30 |
| UNKNOWN | 30 |
| **Total in this file** | **60** |

Sections marked ⚖ INSEPARABLE: A4, A6, A11, B2, B3, B4 (two levels), B5, B6, B7, B11 (V-085).
In every one of them the rival readings are kept and no PnL, fit or distance was used to choose.
