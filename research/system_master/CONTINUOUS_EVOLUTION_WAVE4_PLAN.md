# CONTINUOUS SYSTEM EVOLUTION — Wave 4 plan

**Status: COMPLETE.** Full queue (P0-P8 plus the multimodal addendum, including COMBO01) closed
2026-08-09. See `CONTINUOUS_EVOLUTION_WAVE4_SYNTHESIS.md` for the full wrap-up. ENGINE-C1/C2 not
reached — COMBO01 found no synergy to build on. Master Directive v3 (2026-08-09) plus its same-day addendum
("MULTIMODAL MARKET-MICROSTRUCTURE / AUCTION / SEQUENCE SCIENCE"). This doc is the sec10-required
plan artifact; updated as each item resolves. Per both directives: do not voluntarily stop, do
not lower the promotion bar, do not force a baseline promotion.

## Governing correction from v3 (sec0)

Many prior CONTINUOUS SYSTEM EVOLUTION closures (giveback, weak-M, CLV, volume, VWAP
displacement, entropy, organization transition, skewness, volatility transforms, efficiency
transforms, slope) are deterministic transforms of the **same** NQ_OHLCV path — many failed
constructions ≠ many independent proofs of no alpha. Correct conclusion: the **local single-
feature OHLCV transform/filter paradigm** shows diminishing EVI. It does NOT mean the
information/policy/convexity/external-state/microstructure/options frontiers are exhausted.

## Governing correction from the addendum (A0)

Failure of one **trading representation** ≠ failure of the **information itself**. A feature
that fails as a standalone strategy/binary filter/early-exit rule may still be useful as a
continuous sizing variable, a HOLD-state variable, an interaction term, or an execution-timing
variable. `CLOSED_INFORMATION_CLASS` is a high bar (sec A2) — most prior OHLCV closures should be
reviewed for *scope*, not reopened. This does not authorize retuning dead constructions (U8's
binary filter, U4B's exit mapping, etc. stay dead).

## Priority queue (v3 P0-P9, addendum tasks folded in per Q0)

| # | Family | Status | Notes |
|---|---|---|---|
| P0 | SPEC01 (evening-session audit) | **CLOSED** | Already resolved pre-freeze (W17 V1h). Not a defect. `runs/SPEC01_SESSION_LEAK_AUDIT/` |
| sec13 | PRICE01 (Product-A genuine-MNQ dual truth) | **INFRA COMPLETE** | +0.43% effect, no verdict flips, flagged U6B for O2. `runs/PRICE01_PRODUCT_A_GENUINE_MNQ/` |
| — | Wave-4 truth audit | **COMPLETE** | Confirmed BASELINE_MODELS.md is current canonical record; discovered large prior `research/system_master/` campaign (O1/O2, W17, V1R4_NT8_PARITY, HOLDOUT_DETERMINATION); confirmed repo-safety clean; confirmed D3/B9 don't exist |
| — | Frontier+O2+GAMMA00 audit | **IN PROGRESS** (background) | O2/O1 blocking-issue deep-dive, `*_FRONTIER.md` overlap audit, GAMMA00 literature+data feasibility |
| P1 | O2 (owner-utility re-adjudication) | pending, blocked on audit | Existing O1/O2 apparatus never ran (blocked on unreviewed aggregation choice) — audit before duplicating |
| P2 | ADD01 (participation expansion) | pending, blocked on audit | Must first confirm not already covered by `ONE_CONTRACT_FRONTIER.md` etc. |
| P3 | WIN01 (winner-side exit relaxation) | pending, blocked on audit | D3/B9 confirmed not to exist — no prior art on the exact question; check `STOP_OVERLAY_FRONTIER.md` overlap |
| P4 | SOFT01 (nonzero continuous weighting) | pending, blocked on audit | U5's diagnostic is closed (confounded) but Stage-2 policy never built — family unresolved; likely folds into O2/U6B |
| P5 | VAR01 (multi-scale variance signature) | pending, blocked on audit | Check `LEVERAGE_FRONTIER.md`/`INDICATOR_FEATURE_FRONTIER.md` overlap first |
| P6 | GAMMA00 (dealer-gamma literature+data) | pending, in progress | Literature scout + local options-data feasibility running now |
| P7 | MICRO02 (hold/reversal microstructure) | pending | Supersedes/extends by addendum's FLOW01 (decision-checkpoint framing folded in) |
| P8 | REL01 (conditional cross-market) | pending | Requires a motivating mechanism — check `PORTFOLIO_FRONTIER.md`/`RECENT_REGIME_BMOM.md` first |
| P9 | POLICY01 (bounded action-value) | deferred | Only if simpler mechanisms leave a persistent HOLD/EXIT residual |

## Addendum tasks (multimodal microstructure program)

| # | Family | Status | Notes |
|---|---|---|---|
| A1-A5 | Governance vocab + `STATE_INFORMATION_LIBRARY.csv` + `MULTIMODAL_RESEARCH_MAP.md` | pending | Reclassify prior closures by `closure_scope` without changing verdicts |
| DATA02 | Full microstructure/NT8 data inventory | **IN PROGRESS** (background) | Established directly: local NT8 `db/tick/` has genuine hourly Bid/Ask/Last `.ncd` files for NQ/MNQ/ES across multiple 2020-2026 contract months — a source not yet used by any research in this repo. `db/replay/` and `db/snapshot/` are both **empty** — no genuine Level-II data exists locally at all. DOM01 is provisionally data-blocked pending this being confirmed and pending any forward-collection decision. |
| ICT01+ICT02 | Event-sequence science (sweep/MSS/FVG, PDH/PDL) | pending, blocked on frontier audit | `NQ_OHLCV` info class — no new data needed, can start once frontier audit rules out duplication |
| FLOW01 | Aggressive participation | pending, blocked on DATA02 | `NQ_TRADE_TICKS`/`NQ_BIDASK_TICKS` — DATA02 confirms genuine Bid/Ask tick coverage exists; export tooling feasibility TBD |
| AUCTION01 | Accepted value state / POC | pending, blocked on DATA02 | `NQ_VOLUME_AT_PRICE` — needs genuine trade-at-price ticks, not 3-min bar proxy |
| DOM01 | Level-II liquidity state | provisionally DATA_LIMITED | No genuine L2/Market Replay data found locally so far — likely resolves to a forward-collection spec rather than a historical test |
| COMBO01 | Multimodal synergy | pending, blocked on individual modality gates | Low-dimensional preregistered 2-way interactions only |
| ENGINE-C1/C2 | Independent orthogonal-alpha engine | pending, blocked on COMBO01 | Only if multimodal evidence supports it |

## Key facts established so far (truth audit)

- **BASELINE_MODELS.md** (repo root) is the current canonical record for Product A
  (`SolarWaveSMMaster_v4`, net $177,924.40) and Product B-NQ/-MNQ (`SolarWaveOneContractNQ_v5`/
  `_MNQ_v5`, nets $301,915.92/$28,587.10) — a *different* object/window from CLAUDE.md's frozen
  vendor-replica baseline (`SolarWaveRKReplicaV0`, net $146,440.60); both stand as separate frozen
  truths, no contradiction.
- **LOCKED_FORWARD.md** lives at `research/operational/LOCKED_FORWARD.md`. Boundary: ≥2026-08-01
  = VIRGIN (untouchable except MONITOR-01/annual frozen-champion eval); ≤2026-07-31 = research-
  consumed, including the former June-July 2026 "holdout" (consumed via `SM11_HOLDOUT_READ`,
  2026-08-08). Only ≥2026-08-01 remains genuinely untouched as of today.
- **O2 has never run** — blocked on "the aggregation choice that raised the score has not been
  independently reviewed" (mixture vs Γ-minimax; 4 unanswered blind-reviewer items). Deep-dive in
  progress.
- **D3 and B9 do not exist anywhere in this repository** — confirmed via exhaustive search. The
  owner's recollection of these as a winner-qualification/exit-relaxation diagnostic pair appears
  mistaken; WIN01 has no prior art to reconcile against on this specific question.
- **U5's Stage-2 policy (nonzero continuous weighting) was never built** — only the diagnostic
  (confounded, closed) was tested. The policy-mapping question remains open.
- **Product-A Python substrate priced on an NQ-proxy, not genuine MNQ, this entire campaign** —
  confirmed and now fixed via dual-truth infrastructure (PRICE01). Small, stable effect (+0.43%),
  no prior verdict flips, but flagged for explicit repricing of `U6B_PRODUCT_A_SCALE_RATE` before
  any O2 reconsideration verdict (its near-miss margin is the same order of magnitude).
- **Repo safety: clean.** No RenkoKings paths or `.dll` files ever committed anywhere in git
  history (344 commits, all refs). No credential/secret files in the working tree. Local `main`
  synced with `origin/main`.

## Next steps

Await the Frontier+O2+GAMMA00 and DATA02 background audits, synthesize, then construct the
highest-EVI unblocked families first (likely O2/U6B reconsideration and ICT01/ICT02, both of
which need no new external data and are closest to ready). Continue the EVI loop without pausing
for confirmation between families, per standing owner instruction.
