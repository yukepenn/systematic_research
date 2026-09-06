# CROSS-ASSET FUTURES RESEARCH EXPANSION — campaign state

**Opened 2026-09-06 by owner supplemental directive.** Continues (does not reset) WEEKLY_EDGE /
GENESIS II. State document — wave history lives in `runs/`, this file links.

## The reframe that defines this campaign

> We are NOT porting P1 to other markets. We are transferring the **research PROCESS** that
> produced the NQ system, and letting **each market grow its own native engine**.

- **P1 transfer is ONE lane (Lane A, the Transfer Benchmark), not the campaign.** Its failure on a
  market means "P1 is not universal", never "this market has no alpha".
- **Orthogonality is a first-class product objective.** A Sharpe-0.8 engine with ~0 correlation to
  NQ can beat pushing NQ from 1.2→1.25. The prize is a **multi-engine low-correlation portfolio**.
- Accepted prior result (not reopened without new evidence): free incremental alpha *inside the
  existing NQ information surface* is credibly exhausted (56 trials, 0 live candidates).
- 🔴 **SUCCESS BAR (owner, 2026-09-06): a "good engine" is one proven the way P1/PCT was — strong
  across MANY robustness bases on the history we have** (circular-shift/block nulls, the fixed-DD
  random-thinning placebo, weekly-vol lead, parameter neighborhood, chronology-WITHIN-sample
  walk-forward, cost stress, class-conditional-with-control) **plus portfolio orthogonality.**
  P1 itself is DISCOVERY_CONSUMED, in-sample, and live — that is the standard. **We do NOT gate an
  engine behind a frozen forward holdout or "wait and observe the future."** Use the full available
  history aggressively; the only reserve is the repo-wide ≥2026-08-01 seal (a standing safety rule,
  ~5 weeks, not a discovery holdout). A forward read, if it happens, is a bonus, never the gate.
- 🔴 **Owner decision, already made: DO NOT buy data/subscriptions.** Use extracted/extractable
  repo data, existing infra, free public data (with §24 rules), current tools. No purchase blocks
  this campaign. Live-book safety rules (CLAUDE.md §1) unchanged; nothing here touches `2047681`.

## The three durable assets this campaign must produce

1. **`FUTURES_ALPHA_MAP.md`** — per market: best mechanism, status, standalone quality, NQ corr,
   portfolio value. Populated ONLY from verified experiments; never invented cells.
2. **`MECHANISM_TRANSFER_MATRIX.md`** — which effects are universal / asset-class / market-native.
3. **The multi-engine portfolio** — the real prize; built from low-corr survivors under simple
   risk-budget rules (equal-risk / fixed-vol), evaluated vs NQ-alone.

## Four lanes per Tier-1 instrument

- **A — NQ mechanism transfer** (benchmark, minimal DoF, dimensionless transforms).
- **B — native market discovery** (first-principles; the market's own sessions/economics; may
  produce a completely different engine).
- **C — cross-asset / relative state** (strict chronology; predictor must precede the decision).
- **D — portfolio value** (vs NQ under simple fixed risk allocation).

## Data reality (CONFIRMED — Wave-0 inventory, `DATA_INVENTORY.md`, 2026-09-06; every parquet opened)

⚠️ Prior session counts were calendar-FILE counts; these are true trading sessions (end 2026-07-31).

| root | class | local 1-min (extracted) | daily on disk | status for intraday P1-depth |
|---|---|---|---|---|
| NQ | equity idx | ✅ 1,184 ext + 2006+ deep spine | ✅ | ANCHOR (live P1) |
| ES | equity idx | ✅ **1,184** sess 2022+ | ✅ ~2009+ | intraday-ready · DISCOVERY_CONSUMED |
| RTY | equity idx | ✅ **1,177** sess 2022+ | ✅ | intraday-ready · DISCOVERY_CONSUMED |
| YM | equity idx | ✅ **1,177** sess 2022+ | ✅ | intraday-ready · DISCOVERY_CONSUMED |
| ZB | rates | ✅ **923** sess 2022-12+ (back-adj) | ✅ | 🎯 intraday-ready, orthogonal class · DISCOVERY_CONSUMED |
| MNQ | equity idx | ✅ 1,189 sess | ✅ | EXCLUDED (= NQ/10, not a diversifier) |
| **CL** | energy | ✅ **EXTRACTED 2026-09-06** (1,182 sess 2022-01-03→2026-07-31, `runs/SM1M_CL_SUBSTRATE/`) | ✅ | 🎯 intraday-ready · **full window is discovery** (holdout freeze RETIRED by owner — judge like P1, in-sample+robust; only ≥2026-08-01 stays sealed) |
| ZN | rates | ⚠️ ~190 files only (2025-12+, thin) | ✅ | daily-only for now |
| GC | metals | 🔴 **ABSENT** (only micro MGC, thin) | ✅ ~2009+ | **DAILY-ONLY** |
| 6E | FX | 🔴 **ABSENT** (only 6J, thin) | ✅ | **DAILY-ONLY** |
| SI/HG/NG/6A/6B/6C/6S/ZF/ZT/ZC/ZW/ZL/ZM | metals/energy/FX/rates/ags | 🔴 absent 1-min | ✅ per-contract day .ncd 2009+ | DAILY-ONLY / Tier-2 |

**Roll (the fake-alpha axis):** all six extracted substrates are NT8 **additive back-adjusted**
continuous front-month chains. **Intraday continuity is CLEAN** (no roll-gap contamination —
verified), so intraday signals are safe — **BUT absolute price LEVELS are shifted** (MNQ early-2022
≈ +3,378 pt), so **every level/return/ratio feature must be POINT-difference, never % or a level
threshold** (G2_F13 did ZB in points correctly). ES/RTY/YM roll treatment is INFERRED not
annotated — document before any level use. Daily store is per-contract (no continuous) → needs a
causal roll.

**Cost:** only NQ ($4.36) / MNQ ($1.30) RT are MEASURED. Every other root's commission is MODELED
(~$4.36 full / ~$1.30 micro, FLAGGED); no measured non-NQ commission or spread exists in-repo.
Tick/point values are published CME specs (reliable). Use the optimistic/base/conservative/stress
band; a candidate dead at +1 tick is fragile.

**Honesty rule:** metals & FX (GC/6E/SI/NG/…) get a **daily-resolution** autopsy + native/daily-swing
engine lane (legit — each market teaches its own mechanism); intraday P1-depth is reserved for the
deep-1-min markets (ES/RTY/YM/ZB now; CL after extraction). Do not fake intraday history that isn't
there. The **ESNQ_V1 blind ES∩NQ 15-session tick pool remains UNSPENT** (do not consume).

## Wave tracker

| wave | scope | status |
|---|---|---|
| **XINST01** (Lane A benchmark) | P1 transfer → ES/RTY/YM/ZB, no-mining, NQ-reproduction gate, orthogonality | ✅ DONE (G00056-59): **P1 does NOT transfer** — 0/4 info-supported; port reproduced NQ 0.0000%; ES/YM underpowered whisper (high-corr), RTY cost-fragile, ZB inverts (but ρ −0.05 orthogonal → native ZB engine is the target). **Thesis confirmed: value is native, not transfer.** |
| **Wave 0** (infra) | NQ Research Playbook ✅ · data/roll/cost inventory ✅ · Tier-1 rank ✅ | DONE (`NQ_RESEARCH_PLAYBOOK.md`, `DATA_INVENTORY.md`) |
| **Wave 1** (autopsies, all 7 markets) | ES/RTY/YM/ZB (intraday) + CL (intraday) + GC/6E (daily) | ✅ DONE. ⭐ **NQ is the momentum OUTLIER — everything else MEAN-REVERTS.** ρ-to-NQ: ES 0.94, RTY 0.75, YM 0.74, **ZB 0.06, GC 0.07, CL 0.05** (orthogonal prizes), 6E 0.15 regime-varying. Native engines must be MR / vol-regime, not trend. |
| **Wave 2** (native money-engines) | GC-MR, ES-NQ residual, ZB-native | ✅ DONE (G00060-62): **0/3 cleared.** GC=DRIFT-EXPLAINED, ES-resid=FAIL (β-hedge kills signal), ZB=COST-FRAGILE. ⭐ LEAD surfaced: **raw-ES MR = Sharpe 0.78** (the residual control). Banked law: scheduled-macro = powered vol, zero direction (3 instruments). |
| **Wave 2b** | raw-ES MR (PnL-ρ-to-P1); GC vol-sleeve | ✅ DONE (G00063-64): EQMR real Sharpe-0.78 timing edge but UNDERPOWERED at family bar + POSITIVELY corr to P1 (not a diversifier); GCVOL NEUTRAL (no better than buy-hold). |
| **Wave 2c** | CL multi-day MR (last orthogonal shot) | ✅ DONE (G00065): UNDERPOWERED — orthogonal but no establishable edge. |

## 🔴 FRONTIER ASSESSMENT (2026-09-06): the $0 cross-asset DIRECTIONAL frontier is EXHAUSTED-FOR-NOW

**Comprehensive negative, honestly.** Across the futures universe we have $0 data for, **no
orthogonal engine cleared the P1 bar.** MR tested on all four asset classes (equity — real timing
edge but underpowered + positively corr to P1; gold — drift; rates — cost-fragile; energy —
underpowered); P1-transfer (NQ-specific); macro-vol (powered vol, zero direction, 3 instruments);
gold vol-sleeve (no better than buy-hold). The liquid futures are efficient at the daily/intraday
directional scale; their edges are small-vs-cost / drift / non-directional / non-orthogonal.

**This is a legitimate scientific result + the three durable assets the owner wanted** (Futures
Alpha Map, Mechanism Transfer Matrix, and the load-bearing law: NQ is the momentum outlier of the
complex — everything else mean-reverts, which is exactly why P1 is special and doesn't port).

**What remains (all LOW-EV — grinding these would be the "mutate until green" trap):** cost-fragile
intraday MR on GC/CL; thin/illiquid secondaries (SI/HG/NG/6J/ZN, daily-only); passive long-only
diversification sleeves (gold ρ0.10 / ZB ρ0.06 — mild, not "engines"); session/auction geometry
(ES showed it's mostly geometry).

**The genuine forks (owner decision):** (1) spend on a NEW surface (Databento order-flow /
GAMMA00 options) — the only path to alpha the $0 search cannot reach; (2) accept NQ-P1 stands
alone and shift effort to protecting its realized edge (09-21 ENFORCE deploy, roll/MNQ-spread);
(3) a different research direction the owner names. **Not launching more low-EV cross-asset waves
autonomously — that would be activity, not EV.**

> ### ⚠️ SCOPE RIDER (GENESIS III, owner directive 2026-09-06) — the closure above is REPRESENTATION-SCOPED
> "Exhausted-for-now" covers ONLY the enumerated tested objects: the P1-transfer construction,
> raw daily/multi-day MR (ES/RTY/YM z-score family, the GC washout formulation, ZB intraday MR,
> CL multi-day z-score MR), the ES-NQ β-residual construction, scheduled-macro **pre-event
> direction**, and the gold vol-managed long sleeve. It must NOT be read as "these markets contain
> no tradeable alpha." Untested axes: **event-conditioned representations, relative value / curve /
> carry, session mechanics, conditional continuation, regime-local objects, execution/policy
> engines, cross-sectional structure** — see `REPRESENTATION_COVERAGE_MATRIX.md`. The owner's
> GENESIS III directive reopens the campaign on those axes (the NQ lesson: the flip EVENT carried
> ~24× the per-bar expectancy of the generic trend state — search each market's flip-event
> analogue, not its indicator).
| **CL extraction + freeze** | ✅ DONE — 1,182 sess, no recompile (exporter pre-installed, P1 verified intact), holdout frozen | DONE (`SM1M_CL_SUBSTRATE`, `CL_HOLDOUT_FREEZE_20260906`) |
| Wave 1 (CL autopsy) | descriptive science on CL DISCOVERY (≤2025-06-30) — add to the ES/RTY/YM/ZB batch | 🟡 queued (next) |
| Wave 1b | daily autopsies GC/6E (+SI/NG…) after daily extraction | pending |
| Wave 2 | cheap screening: transfer + native mechanism families per market | pending |
| Wave 3 | deepen survivors (rules, neighborhood, chronology, cost stress) | pending |
| Wave 4 | independent engine construction (1-2 strong mechanisms, not 10 weak) | pending |
| Wave 5 | cross-asset skeptic (adversarial, per winner) | pending |
| Wave 6 | portfolio test (simple allocation; Sharpe/DD/tail/capital) | pending |
| Wave 7+ | secondary instruments by EV; implementation for strong candidates | pending |

## Discipline (non-negotiable, inherited)

- One hash-chained ledger (`research/genesis/SEARCH_LEDGER.jsonl`), cross-asset families; count
  failed searches, report all not just winners; family-wise correction across instruments.
- eval_battery led by weekly-vol; fixed-DD only with its random-thinning placebo.
- Roll/back-adjustment audit MANDATORY (§10) — a candidate resting on roll artifacts is invalid.
- Market-specific cost (tick/point/commission/spread) with an optimistic/base/conservative/stress
  band; a candidate that dies at +1 tick is fragile.
- Instrument-native sessions — **never copy NQ 09:30-16:00 to other futures.**
- Move HORIZONTALLY when a family is exhausted; never mutate a consumed dataset until it turns green.
- No promotion / no live deploy / no sizing change from research runs. $0.

## GENESIS III — NATIVE ENGINE BREAKOUT (opened 2026-09-06, owner directive)

**Objective: more real, explainable, robust, deployable engines** — three admission classes
(S standalone · P portfolio · X execution/policy). Search unit = **EVENT → state → action**, not
indicator. Horizon is a first-class dimension. Family-wise verdicts stay; ECONOMIC value under
shrinkage is computed separately (never rewriting a failed statistical verdict). Failed objects
stay closed; adjacent questions with genuinely different targets are legitimate.

### GENESIS III wave tracker

| wave | object | status |
|---|---|---|
| **A — SI/GC carry confirmation** | frozen switch, 9-pair family, one-shot | ✅ DONE (G00070 DEFECT/INVALID-RUN, adjudicated **EFFECTIVELY CLOSED**): dev-repro perfect (Phase A 6/6), but the switching relation did NOT persist — 97.5% long-SI (dev 66.3), 4 flips (dev 75), switch≈static-SI control, both nulls at 63-74 pct (bar 95). The $157k headline is the silver rally. **Windows SPENT; no rerun; the 9-pair family table (ZC/ZW rank 1) is selection-pricing evidence, never a discovery surface.** |
| **B — ES MR portfolio adjudication** | exact W2B_EQMR rule, shrunk marginal economics vs P1 | ✅ DONE (G00066 NULL): **CLOSED-PORTFOLIO-INERT** — s*>1, λ=0.5 book never beats P1-alone even unshrunk (marg Sharpe −0.056 at s=1); 2/30 cells positive, shrinkage kills both; tails fine, kill is mean-side. G00063 FAIL untouched. |
| **C — ZB event diagnostic** | 6-event preregistered catalog | ✅ DONE (G00067 PASS): **ONE LEAD** — E1 macro-response-path: NFP/CPI DOWN first-response (08:30→08:45) continues to settlement, δ −$238/ct vs null, p_corr .0441, n=40, release-specific p .015, direction-concentrated. E3/E4 descriptive, E2/E5/E6 dead. |
| **C2 — ZB E1 graduation falsifier** | frozen E1 object | ✅ DONE (G00072 **PASS, selected**): ⭐ **ZBMACRO01 — the campaign's first cleared orthogonal engine object.** 10/10 gates: +$177.7/ct after cost (CI +45..+411), nulls 0.5/1.6 pct agreeing, both halves, drop-2 +$91, 15/18 plateau, NFP+CPI both, 2-tick +$115, weekly-vol Sharpe 0.86, **ρ-P1 daily −0.006**. Honest: DISCOVERY_CONSUMED, near power edge, small (~$2k/yr/ct, 11 tr/yr). → Class-S/P assessment. |
| **D — CL event diagnostic** | 7-event preregistered catalog | ✅ DONE (G00068 NULL): **all DEAD** — 1/52 cells at raw p<.05 vs 2.6 expected; EIA response-path flat 12/12. CL pit returns are a random walk; structure is vol only. |
| **E — GC event diagnostic (daily)** | 6-event catalog, drift-matched controls mandatory | ✅ DONE (G00069 NULL): **all DEAD vs drift control** — 0/33 cells; GC−SI divergence ANTI-convergent; G00060 lesson generalizes. Byproduct: SI daily built via certified causal roll (identity 0.0). |
| **F — LIQREV01 re-adjudication** | exact post-2020 object, D1-D8, binary | ✅ DONE (G00071 FAIL): **DEAD — PERMANENT CLOSURE.** Standalone economics real (W2020 CI_lo +$693/tr, regime ON, worst-rung cost PASS) but the no-harm portfolio gates failed: worst combined day 1.604× (bar 1.5×), daily ρ +0.365 / **active-day +0.614** — its stress regime IS P1's bad-day regime. The 3-week zombie is terminated. Shadow-retirement recommendation → owner packet. |
| **G — representation world scan** | 6 mechanism scouts + graveyard skeptic | ✅ DONE: 48 raw → **34 survive**, 14 killed with citations (`runs/G3_WORLDSCAN_20260906/`). Top EVI: auction concession cycle, P1 passive-entry policy, corr-gated FTQ, ZN/ZB slope RV, basis-momentum. |
| **H — micro/execution surface census** | causal materialized surfaces only | ✅ DONE: `MICRO_SURFACE_CENSUS.md` — 6 candidates ranked; top = **H-X1 MNQSPREAD01** (measure live MNQ spread — the roll-quote sampling in flight covers it) and **H-X2 spread-state entry routing for P1** (Class-X EXECUTION); micro info-alpha lane honestly LOW-MED (4 consecutive prior negatives). |
| **Wave 3 — world-scan falsifiers** | 5 falsifiers + Class-P | ✅ DONE — **5 kills, 1 confirmation**: AUCT01 rebound FAIL powered (alive only in the LYZ era, sign-flipped since; concession half preregistered-secondary, era UNREAD → G00080); ZN/ZB slope RV FAIL (gross-negative; ⭐ both OUTRIGHT carry-timing controls positive ZN 0.61/ZB 0.70 → G00081); basis-mom FAIL (data collapse: full strip only 2009-15 → DATA-GATED); corr-gated FTQ FAIL powered INVERTED; month-end rebalance FAIL (both legs wrong-signed). ⭐ **G00078 PASS: ZBMACRO01 = STACK MEMBER at k=2** (book Sharpe 2.187→2.280, tails SHRINK, +$46/wk on P1 losing weeks) → engine construction licensed. |
| **Wave 4** | ZBMACRO01 engine+skeptic (G00079, delay-curve decisive) · AUCTCONC01 (G00080) · RATESCARRY01 (G00081, 97.5-pct debt bar) · P1 entry-policy governance pre-check | 🔒 PREREGISTERED → executing |

Discipline unchanged (ledger, spec-first, matched controls, dependence-preserving nulls, DELEV01
points basis, market-native sessions, cost bands, no promotion from research, live book untouched).
