# DOM01 Prospective Research Protocol — SPEC ONLY, NO ALPHA RUN

**UPDATE 2026-08-12: DOM01 collection PAUSED** (owner risk-control decision, workstation
resource-instability incident — see `research/system_master/DOM_PAUSE_CLEANUP_20260812.md`). This
frozen protocol remains valid and unchanged; it simply has no active data source feeding it until
collection is explicitly re-authorized. No session ever reached this protocol's readiness
threshold before the pause.

**Status: frozen before any outcome/predictive analysis of DOM01 data. Zero DOM sessions have
been read for any price-response, markout, or predictive purpose as of this commit.** This
document exists to freeze the hypothesis and the exact evaluation procedure *before* that
analysis happens, not because the dataset itself didn't exist yet (it does — collection started
2026-08-11, see `runs/DOM01_LIQUIDITY_STATE/collector/`). The defensible claim here is narrower
and correct: **the hypothesis/protocol is frozen before any alpha/outcome analysis of this data**,
not "before the dataset existed."

Companion document: `DOM01_DATA_GOVERNANCE.md` (chronological data states, readiness rule,
protected-pool reservation). Read both before touching any DOM01 session for research purposes.

---

## 0. Session classification — what "already collected" means for this protocol

As of this commit, exactly one DOM01 collector run exists:

| RunId | StartUtc | Status |
|---|---|---|
| `5c8ca242e2d24960a3f2863876541488` | 2026-08-11T22:03:50Z | in progress (`EndUtc` null) |

**This run, and every DOM01 run whose manifest `StartUtc` predates the commit that lands this
document, is classified `ENGINEERING_BURNIN` and is permanently excluded from any future
discovery-pool or confirmation-pool tally — regardless of whether it later passes QC.** This is
the conservative, correct treatment, not merely a formality: while building
`runs/DOM01_LIQUIDITY_STATE/collector/qc/dom01_qc_monitor.py` this same session, this run's actual
structural field values were directly inspected (observed `Level` range 0–29, `Operation`
vocabulary, ~0.28%/0.26% crossed/locked top-of-book incidence, the `RecordedUtc`−`EventTime`
offset). No price-response, forward-return, or outcome quantity was ever computed from it — the
QC monitor is structurally incapable of that (see its own scope statement) — but structural
familiarity with a specific run's own characteristics is exactly the kind of engineering exposure
this document's own instruction says must not be quietly laundered into "pristine confirmation
evidence" later. `ENGINEERING_BURNIN` sessions may still be used for what they were actually used
for — QC-tool development and this protocol's own feed-semantics verification (section 1) — never
for discovery or confirmation.

The cutover rule going forward: **a DOM01 run counts as prospective (eligible for
`DOM01_DATA_GOVERNANCE.md`'s state machine) only if its manifest `StartUtc` is strictly after the
commit timestamp of this document.**

---

## 1. Feed semantics, verified before any hypothesis is built on top of them

Per this task's own instruction, the protocol must verify actual feed capabilities before
proposing a mechanism that assumes something the feed doesn't provide. Verified against
`runs/DOM01_LIQUIDITY_STATE/collector/SCHEMA.md`, the live manifest, and
`dom01_qc_monitor.py`'s own output against the one real `ENGINEERING_BURNIN` run (not treated as
research evidence, only as a feed-capability check):

| Question | Verified answer | Source |
|---|---|---|
| Provider / connection | `NinjaTrader.Cbi.TradovateOptions`, live, `Connected` at init | manifest |
| MBP or MBO | **MBP (price-level aggregated)**, confirmed by reflection against this NT8 install, not assumed | `SCHEMA.md`, manifest `DepthLevelClass` |
| Available levels | Empirically 0–29 (30 levels) observed this run — **not a fixed architectural guarantee**; a future run could show a different range; any construction must not hardcode a specific level count | QC monitor `depth:level_validity` |
| Event/update semantics | `Operation` ∈ {Add, Update, Remove} per (Side, Level); `Remove` rows carry `Price=0, Size=0` structurally (confirmed: 271,714/554,500 depth rows this run, 100% `Operation=Remove`) — a real value must never be read off a `Remove` row | `SCHEMA.md`; verified via QC monitor `depth:price_sanity` scope note |
| Timestamp semantics | `RecordedUtc` is UTC, timezone-aware, monotonic-verified by the QC monitor (`depth:recorded_utc_monotonic`). `EventTime` is naive with `EventTimeKind=Unspecified`; QC monitor found a **tight, consistent** empirical offset (`RecordedUtc` − `EventTime` ≈ +4:00:00, spread 0.3s over the sampled rows) consistent with `EventTime` being naive ET during EDT — **hedged as an empirical observation, not confirmed**, per `SCHEMA.md`'s own disclosed limitation. **This protocol uses `RecordedUtc` exclusively for all causal-ordering and decision-timestamp purposes** — never `EventTime` — precisely because it is the field with an independently mechanically verified (not just inferred) timezone and monotonicity guarantee. |
| Synchronized Bid/Ask/Last | Yes, via `_topofbook.csv` (`Type` ∈ {Bid, Ask, Last}), same `RecordedUtc` clock as `_depth.csv`. Sequential best-bid/best-ask reconstruction shows a small (~0.3%) crossed/locked incidence from real-time update-ordering — expected and handled (section 3), not treated as a data defect | QC monitor `topofbook:crossed_locked_incidence` |
| Queue position / order identity | **Not available.** No order IDs, no queue-rank field exists in the source API (`SCHEMA.md` sec on disclosed limitations). **No hypothesis in this protocol claims or requires queue position** — every construction below uses only aggregate `Size` per price level, which the feed genuinely provides. |

---

## 2. Mechanisms reviewed, and why exactly one is frozen

Per instruction: do not blindly adopt a hypothesis from the owner's prompt; review existing
repo information-state results, Auction M5's actual surviving finding, ACTIONMAP01's
identifiability failure, true feed semantics, and established microstructure mechanism, then
choose at most two, and prefer the most defensible one or two — not necessarily two just because
two are allowed.

**Reviewed and NOT frozen this pass:**

- **Replenishment/absorption + poor price progress conditional on aggressive pressure.** A real,
  literature-grounded (Kyle-lambda-adjacent) mechanism, but it requires *two* new causal
  constructions at once (an absorption ratio and a price-progress measure) rather than one — a
  compound-feature shape closer to what made ACTIONMAP01 hard to identify cleanly. Deferred as a
  natural *second-wave* DOM mechanism once the single-feature construction below has actually been
  built, run through the QC/governance pipeline once, and shown tractable. Not opened this pass.
- **Auction distance-from-value × liquidity response.** Genuinely high-EVI in principle —
  `value_dist_ticks_action_relevance` (`STATE_INFORMATION_LIBRARY.csv` row 25) is explicitly
  flagged `reusable_for_interaction=YES` for exactly this kind of future DOM interaction, and
  Auction M5's own finding (far-from-POC predicts deterioration of the incumbent's aligned forward
  return, direction-robust, significance-fragile) is the cleanest surviving Auction result. But
  freezing it now would (a) require joining two families' raw data (`NQ_VOLUME_AT_PRICE` trade
  prints + DOM01 depth) in a single construction, (b) touch the same
  `PROTECTED_EVIDENCE_BUDGET.md` governance surface ACTIONMAP01 just closed null on, at exactly
  the moment ACTIONMAP01 demonstrated this substrate is easy to over-decompose past what the data
  can actually identify. Deferred, not abandoned — it is the natural next step once DOM01 has its
  own single-family finding to interact *with*, per sec146's own framing (state preserved for
  future interaction, not spent prematurely on a compound first attempt).

**Frozen this pass — exactly one mechanism (DOM-M1):**

Classic adverse-selection / quote-fade liquidity supply response (Glosten–Milgrom-style informed-
flow inference; the empirically well-documented "flickering liquidity" effect in electronic
limit-order-book markets): when aggressive order flow arrives on one side, resting liquidity
providers on the **opposite** side rationally reduce posted size, because continuing to quote at
the same depth exposes them to adverse selection from a possibly-informed aggressor. This is
mechanically distinct from the trivial, definitional depletion of the *same*-side book (that side
is depleted by the trade itself, by construction, and is not informative). The interesting,
non-mechanical question is whether the **opposite** side also thins — a genuine liquidity-supply
response, not an execution artifact — and whether that thinning itself carries forward-looking
information beyond what the triggering trade flow already implies.

Chosen over the other two because: (a) it needs exactly one new causal feature, not two; (b) it
uses only `Size` aggregated by level — nothing the feed doesn't actually provide (no queue
position, no per-order data required); (c) it touches no protected-pool data and no other family's
substrate — pure DOM01, self-contained; (d) it is orthogonal to (not a restatement of) every
existing `STATE_INFORMATION_LIBRARY.csv` row — none of the 27 currently-closed/open states use
Level-II liquidity at all; (e) it reuses the exact same conditioning/outcome convention Auction M5
already established and this campaign already trusts (aligned-forward-return of the incumbent's
own held direction), so results will be directly comparable rather than requiring a new evaluation
language.

---

## 3. DOM-M1 — frozen specification

### 3.1 Raw information used

- `_depth.csv`: `Side, Level, Price, Size, Operation, RecordedUtc` — reconstructed into a running
  per-side aggregate resting size across the top `K=5` levels (0-indexed 0–4; a small, fixed,
  pre-specified constant, not swept or tuned).
- `_topofbook.csv`: `Type=Last` rows (trade prints) for flow classification, `Type∈{Bid,Ask}` rows
  for the prevailing quote at classification time.
- The incumbent Product A's own already-existing `target_exposure_A` (read-only, unmodified,
  exactly as currently computed by the live decision object — DOM state feeds nothing back into
  any decision this pass).
- `sigma460` (existing, already-public OHLCV-derived volatility state — used only in
  `DOM01_DATA_GOVERNANCE.md`'s sample-size planning, and as the one permitted interaction term
  below; **not** derived from or influenced by any DOM01 observation).

All four sources are read strictly through `RecordedUtc` for causal ordering (section 1's
rationale). No field from `_events.csv`/`_heartbeat.csv` is used as a research input — those are
QC-only streams.

### 3.2 Exact causal feature construction

For each 3-minute bar close `t` (same cadence as the incumbent Solar13 decision object, chosen for
direct comparability, not a new arbitrary clock):

1. **Trade-side classification** (standard quote rule, no new invention): a `Last` print is
   buy-initiated if `Price ≥` prevailing `Ask`, sell-initiated if `Price ≤` prevailing `Bid`, else
   unclassified (excluded).
2. **Flow imbalance** `flow(t)` = (buy-initiated volume − sell-initiated volume) over the trailing
   3-minute window ending at `t`. This is the ONE fixed window used everywhere in this
   construction — no horizon/window sweep.
3. **Opposite side** `opp(t)` = `Bid` if `flow(t) > 0` (net buy pressure) else `Ask`. Defined as the
   side **not** hit by the window's net flow — by construction this side cannot be mechanically
   depleted by the classified trades themselves, so any depletion observed on it is not a trivial
   execution artifact.
4. **Opposite-side depletion** `depl(t)` = −Δ(aggregate `Size` on `opp(t)`, top `K=5` levels) over
   the same 3-minute window, net across all `Add/Update/Remove` operations (a positive value means
   net withdrawal; a negative value means net replenishment — both are retained, not thresholded).
5. **Eligibility filter**: `t` is an in-domain decision point only if `target_exposure_A(t) ≠ 0`
   AND `flow(t) ≠ 0` AND at least one classifiable trade occurred in the window (mirrors
   `ACTIONMAP01`'s own precedent of restricting to bars where the question is actually askable,
   avoiding that diagnostic's flat-state degenerate-population problem).

### 3.3 Decision timestamp / causality assertion

Decision timestamp = the 3-minute bar-close `RecordedUtc`. Every input to `depl(t)` and `flow(t)`
uses only rows with `RecordedUtc ≤ t`. **Max source timestamp ≤ decision timestamp is asserted
mechanically** by construction of the windowed aggregation (a strictly trailing window ending at
`t`, computed from a `RecordedUtc`-sorted stream) — no field with unconfirmed timezone semantics
(`EventTime`) enters this computation at any point.

### 3.4 Primary outcome

`aligned_fwd_return(t, H)` = `sign(flow(t)) × (close(t+H) − close(t)) / TICK` — the identical
outcome convention Auction M5 already uses (`signed_markout_H`), for direct cross-family
comparability.

### 3.5 Horizons

`H ∈ {1, 3, 20}` bars (3-minute bars) — reused verbatim from Auction M5's own preregistered
horizon set. Not swept, not re-chosen for this construction.

### 3.6 Independent inference unit / clustering unit

**Session.** Matches every other Auction/DOM construction in this campaign
(AUCTION03/04's dual-clustered session+event bootstrap convention). Decision points within a
session are not independent (overlapping windows, autocorrelated order flow).

### 3.7 Minimum economically meaningful effect / cost hurdle

**C1 = 2.872 ticks round-trip**, reused verbatim from `ACTIONMAP01`/`AUCTION03`'s own frozen
hurdle — not a new number invented for this construction.

### 3.8 Primary sign prediction

`depl(t) > 0` (net opposite-side withdrawal) predicts `aligned_fwd_return(t, H) > 0` on average
(continuation) — the adverse-selection story. The opposite sign (withdrawal predicting reversion)
is a real, different, and still-interesting finding if observed — see section 3.10,
`OPPOSITE_SIGN`.

### 3.9 Falsification criteria

Primary test at `H=3` (the mechanistically central horizon — not the first horizon tried, chosen
in advance): a dual-clustered session-block bootstrap (block=5, B=10,000 — identical method and
parameters to `AUCTION03`/`AUCTION04`) 90% CI on the `depl(t)` vs. `aligned_fwd_return(t,3)`
relationship must exclude zero **and** have the predicted sign to avoid `CLEAN_NULL`.

### 3.10 Concentration / influence tests

- Leave-one-session-out sign stability (report % sign-stable — same method as M5's own 100%/36
  result).
- Top-3-most-influential-session removal test (same stress precedent as M5/AUCTION03/04).

### 3.11 Allowed low-order interaction — exactly one, pre-specified

`depl(t) × sigma460(t)` (volatility-regime interaction) — reusing an existing, already-public,
non-DOM state column, exactly mirroring M5's own control set (|M|/sigma460/session-phase). No
other interaction term is authorized without a new, separate preregistration.

### 3.12 Exact failure / closure taxonomy

Reusing this campaign's existing verdict vocabulary (`STATE_INFORMATION_LIBRARY.csv` /
`TESTING_LEDGER.csv`), not inventing new terms:

| Verdict | Condition |
|---|---|
| `DATA_LIMITED` | Session count below `DOM01_DATA_GOVERNANCE.md`'s readiness threshold at read time |
| `MECHANICALLY_UNIDENTIFIABLE` | `depl(t)` collapses to a trivial identity, or `\|corr(depl, existing state)\| ≥ 0.4` against any `STATE_INFORMATION_LIBRARY.csv` column (redundancy threshold reused from row 25's own precedent) |
| `CLEAN_NULL` | H=3 dual-clustered 90% CI includes zero, adequately powered |
| `OPPOSITE_SIGN` | CI excludes zero, wrong sign — a real, different finding; documented, not chased further without new preregistration |
| `REAL_BUT_FRAGILE` | CI excludes zero, correct sign, but fails LOSO or top-3-removal stress (same disposition class as Auction M2/M3/M5) — preserved `USEFUL_STATE_ONLY`, no construction attempted |
| `CONFIRMED_ROBUST` | CI excludes zero, correct sign, survives both stress tests — eligible for a **separate**, later-preregistered construction attempt; not automatic promotion |

No ML, no feature sweep, no trading strategy is authorized under this protocol regardless of
verdict. A `CONFIRMED_ROBUST` result opens a queue slot for a new, separately-preregistered
construction spec — it does not itself constitute one.

---

## 4. What this document does NOT do

Does not read any DOM01 session for outcome purposes. Does not compute `flow`, `depl`, or
`aligned_fwd_return` for any real bar. Does not authorize opening `LOCKED_FORWARD.md`'s ≥2026-08-01
boundary for DOM data — see `DOM01_DATA_GOVERNANCE.md` sec2 for why that remains a separate,
explicit, owner-gated decision even after every readiness condition below is met. Does not
retune, reopen, or re-adjudicate Auction, ACTIONMAP01, B1, or any current baseline.
