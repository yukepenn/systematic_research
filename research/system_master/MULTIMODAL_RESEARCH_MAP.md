# MULTIMODAL_RESEARCH_MAP — governance for information-class-aware research (addendum A0-A9)

**Purpose.** Prevent two specific failure modes the addendum's Master Directive v3 addendum
(2026-08-09) identified: (1) losing useful causal state because it failed as a *filter* when it
might still work as a *sizing variable, interaction term, or hold-state signal*; (2) accidentally
repeating a dead construction because a prior closure's language was broader than what was
actually tested. This is a navigation aid, not a new summary document — see
`STATE_INFORMATION_LIBRARY.csv` (same directory) for the full per-feature ledger.

## The governing correction

**Failure of one trading representation ≠ failure of the information itself.** A feature that
fails as a standalone strategy, binary entry filter, or early-exit rule may remain useful as a
continuous sizing variable, a HOLD-state variable, a conjunction with another modality, an
execution-timing variable, or an independent orthogonal engine input. `CLOSED_INFORMATION_CLASS`
is reserved for strong evidence that (a) the data contains no economically meaningful residual
information, or (b) all economically plausible mappings are redundant/non-causal, or (c) the
available data fundamentally cannot support the hypothesis (`DATA_LIMITED`) — **not** for "one
threshold failed" or "one filter destroyed winners."

## Information classes in use (addendum A5)

| class | what it covers | status in this campaign |
|---|---|---|
| `NQ_OHLCV` | Bars, volume, session clock, and every deterministic transform of them (giveback, CLV, VWAP displacement, organization, skewness, volatility/efficiency transforms, slope) | Heavily explored across ~2 independent sub-campaigns (~40+ constructions total, see below) — diminishing EVI for *new single-feature transforms specifically*, not exhausted for policy-mapping or event-sequence questions |
| `NQ_TRADE_TICKS` / `NQ_BIDASK_TICKS` | Genuine trade prints, bid/ask ticks | `DATA_LIMITED` for broad-sample discovery: real data exists (~12mo NQ, bursty/40%-density Bid/Ask), but the usable substrate is a governance-limited 37/40-session Tier-0 subset (see below) |
| `NQ_BBO` | Top-of-book bid/ask state | Same substrate/limitation as above |
| `NQ_LEVEL2_DOM` | Multi-level order-book depth | `DATA_LIMITED` — no historical recordings exist anywhere, cannot be recovered retroactively; forward-collection only (DOM01, not yet built) |
| `NQ_VOLUME_AT_PRICE` | True trade-at-price volume profile / POC | Not yet tested (AUCTION01, pending) — genuine trade-price data exists in the same tick substrate as NQ_TRADE_TICKS |
| `CROSS_MARKET_PRICE` | ES/RTY/YM standalone or conditional state | Standalone signals: 15/15 killed (COMPLEMENTARY_ENGINE_FRONTIER.md). Conditional/relative state: genuinely untested, zero coverage anywhere (REL01, pending, needs a motivating mechanism) |
| `OPTIONS_DEALER_STATE` | SPX/NDX options chain, dealer gamma | `DATA_LIMITED` — zero local data, ~$80-199/mo would unblock (GAMMA00, deferred pending owner decision) |
| `SESSION_CALENDAR` | Documented session-time taxonomy (ETH/RTH/etc.) | Live, reusable, already a first-class column in the shared state table |
| `POLICY_MAPPING` | How causal state translates into position/exposure decisions (not new raw information) | O1/O2 owner-utility framework; U6B's scale-rate mapping |
| `MARKET_ENVIRONMENT` | Regime-level facts about the instrument itself (e.g. the leverage effect) | Confirmed real, not directly tradeable so far |
| `EXECUTION` | Fill/pricing convention questions (e.g. genuine-MNQ vs NQ-proxy) | PRICE01 |
| `SPECIFICATION_DEFECT` | Implementation bugs, not alpha | SPEC01 |

**Do not count multiple deterministic transforms of one class as independent proofs.** The
~20-construction `INDICATOR_FEATURE_FRONTIER.md`/`INDICATOR_FRONTIER.md` sub-campaign and the
~15-construction `R4/R5/U5/U8/U8B/SKEW01/LEV01/LEV02` sub-campaign are **both** `NQ_OHLCV` —
their near-total DEAD/tail-unsafe convergence is two independent confirmations of the *same*
underlying claim (single-feature OHLCV transforms are exhausted), not ~35 independent proofs.

## The tick-data governance wall (read before proposing a bigger FLOW01/AUCTION01 sample)

`scalping_lab`'s `grid1s` substrate and the newly-inventoried local NT8 `db/tick/` cache trace to
the **same** underlying source (NT8's own hosted historical-data "Simulation" connection, DATA02
finding). The 37/40-session sample U9B and any FLOW01/AUCTION01 construction draws from is **not**
a hard data ceiling — it is a deliberate 40-of-~208-session stratified discovery subsample, with
the remaining ~168 sessions frozen by a prior owner directive (`AMENDMENT_3.txt`,
`CONTAMINATION_LEDGER.md`) as a protected **internal confirmation pool**, explicitly not to be
exported or examined for discovery. **Respect this wall** — it exists precisely so any candidate
that survives a Tier-0 discovery pass has a genuine, uncontaminated out-of-sample check waiting
for it. Requesting more sessions for *discovery* would defeat that purpose; the correct sequence
is: find something on the 37/40, then ask the owner to release (part of) the confirmation pool to
validate it.

## Reading `STATE_INFORMATION_LIBRARY.csv`

One row per tested feature/state family. Key columns: `closure_scope` (what specifically closed —
`CLOSED_BINARY_FILTER`/`CLOSED_EXIT_MAPPING`/`CLOSED_ENTRY_MAPPING`/`CLOSED_EXACT_CONSTRUCTION`
mean *that construction* is dead, not the information); `reusable_as_state` / `reusable_for_
interaction` (addendum A1 fields — does this remain a legitimate input to a future sizing/HOLD/
interaction construction); `verdict` (the addendum's expanded taxonomy: `PROMOTION_CANDIDATE`,
`USEFUL_STATE_ONLY`, `OPEN_FOR_INTERACTION`, `DATA_LIMITED`, `NO_LARGE_EFFECT_DETECTED`,
`CLEAN_NULL`, or one of the `CLOSED_*` scoped-closure types).

**Coverage note:** this first pass covers the CONTINUOUS SYSTEM EVOLUTION sub-campaign's own
tested features (U0-EXP01) in full detail, plus the prior SYSTEM_MASTER campaign's O1/O2 and
price-truth findings. It does **not** yet have per-row entries for every construction in the much
larger prior `R2/R3/R4/R5/R6/SA0/PA0/PA1/INDICATOR_FEATURE_FRONTIER/INDICATOR_FRONTIER` body of
work (~35+ additional constructions, summarized qualitatively above and in
`CONTINUOUS_EVOLUTION_WAVE4_PLAN.md`, but not yet itemized row-by-row). Extending the CSV to that
full inventory is flagged as a follow-up, not fabricated here.

## Currently reusable states worth carrying into new combination work (per addendum G0-G3)

Highest-confidence `reusable_as_state`/`reusable_for_interaction` entries right now:
`giveback_ratio` (cleanest right-tail correlate in the campaign), `session_phase` (already a
first-class shared-state column), `scale_in_quality_state` (U6B — zero right-tail damage, now has
O2 evidence favoring it under both aggregation conventions), `organization`/`organization_
transition` (orthogonal to other features, real interaction with |M|, just tail-unsafe as a
*filter* specifically). None of these should be re-tested as a binary filter again — that
construction is dead for each of them. They remain candidates for a **mechanistically-motivated**
two-way interaction (per addendum A6-A7) once a new modality (FLOW/AUCTION/ICT) is built.
