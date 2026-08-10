# NT8/NinjaScript executable-feasibility audit — future AUCTION running-POC prototype

**Scope: infra/feasibility memo only.** No indicator/strategy `.cs` was written or compiled for
this pass. This is desk research over evidence already sitting in this repo (prior probes,
prior compiles, prior parity certificates) plus a few small, in-scope, already-built metadata/
probe files re-read for cross-checks. Per this campaign's standing convention (`RESEARCH_HANDOFF.md`
workflow diagram), an executable parity check is only justified once a frozen AUCTION candidate
survives research — AUCTION01/AUCTION02/AUCTION03's diagnostics are still diagnostic-only
(`runs/AUCTION01_VALUE_STATE/spec.yaml`: "status: diagnostic-only, no trading policy this pass").
This memo answers "could we, cheaply, when the time comes" — not "should we now."

**Disposition: FEASIBLE, with enumerated open validation items — not yet attempted.** The two
load-bearing capabilities (historical tick-level data inside NT8's backtest engine, and a working
compile-and-verify pipeline for new NinjaScript) are each already independently proven in this
repo, by direct probes, not by reading NinjaTrader documentation. Nobody has yet proven Python and
a NinjaScript running-POC agree number-for-number — that specific check has never been run and is
the correct next step **if and only if** an AUCTION candidate is frozen for promotion.

Sources read: `research/scalping_lab/src/ninjascript/SWScalpTickExport_v1/_v2/_v3.cs`,
`runs/AUCTION01_VALUE_STATE/spec.yaml`, `runs/PRICE01_PRODUCT_A_GENUINE_MNQ/{REPORT,spec}.yaml`,
`runs/U6B_PRODUCT_A_SCALE_RATE/src/02_genuine_mnq_repricing.py`, `runs/DOM01_LIQUIDITY_STATE/
{REPORT.md,collector/compile_evidence.json}`, `research/scalping_lab/runs/DATAPROBE01/{spec,
results}.md`, `runs/V1R4_NT8_PARITY/FULL_HISTORY_CERTIFICATION.md`, `research/scalping_lab/
CONTAMINATION_LEDGER.md`, `research/scalping_lab/CAMPAIGN_STATE.md`, `research/scalping_lab/
substrate/MANIFEST.csv`, `research/scalping_lab/src/python/csv_to_parquet.py`,
`research/scalping_lab/runs/EXPORT01/{grid_log,convert_log}.txt`, and (light head/tail spot-checks
only, format-verification, not analysis) the already-exported probe extracts at
`research/scalping_lab/runs/EXPORT01/p20250910_on|p20260123|p20260506/probe_ticks.csv` — all three
of those dates are inside the sanctioned DISCOVERY list. `RESEARCH_HANDOFF.md` supplied the
"early representative-window parity check, not late" workflow convention this task cites.

---

## 1. Does NT8/NinjaScript backtesting genuinely have access to historical Last trade-tick data?

**Yes, proven directly, twice, not assumed.**

- **The existing exporter is itself the evidence.** `SWScalpTickExport_v3` (and `_v1`/`_v2` before
  it) is a `Strategy` with `Calculate = Calculate.OnEachTick`, primary series = 1-tick Last
  (implicit default series), plus two explicit `AddDataSeries(null, new BarsPeriod {
  BarsPeriodType = BarsPeriodType.Tick, Value = 1, MarketDataType = MarketDataType.Bid/Ask })`
  calls in `State.Configure`. `OnBarUpdate()` fires once per tick per series and writes
  `Times[bip][0]`/`Closes[bip][0]`/`Volumes[bip][0]` — i.e. NT8 delivers individual trade prints
  (price, size, sub-second timestamp) to `OnBarUpdate` in historical/backtest mode exactly the way
  a live `OnMarketData`/`OnEachTick` handler would need them to compute a causal running state.
  This is not a doc-reading inference — it is the mechanism the campaign has been running in
  production since 2026-08-07.
- **DATAPROBE01 (`research/scalping_lab/runs/DATAPROBE01/{spec,results}.md`)** ran this exact
  probe deliberately, via two live `RunStrategyBacktest` jobs against NT8 8.1.8.1, and reflection-
  confirmed: millisecond-class timestamps (~4ms quantization, 250 distinct sub-second values/sec);
  historical Bid/Ask 1-tick series download on demand (NQ 2026-07-14/15: Bid 1.46M / Ask 1.44M
  events vs 98.5k Last ticks; NQ 2025-10-14/15: Bid 1.40M / Ask 1.41M — depth already this deep
  back to at least 2025-10); real per-tick volume (Last: min 1, max 50, mean 1.10, 0% zero-volume).
  Its own level table marks **L1 last-trade events: CONFIRMED, ms-class, ~12 months** and
  **L2 BBO quotes: CONFIRMED, same depth as L1.**
- **`runs/AUCTION01_VALUE_STATE/spec.yaml` step0_gate** independently re-confirmed this at the row
  level by direct parquet inspection (not re-derived here, cited as existing evidence): 413,850
  Last rows in one session at millisecond timestamps, volume distribution single-print-sized
  (median 1, IQR [1,1]), 66% of seconds contain more than one distinct traded price (up to 57
  distinct prices in one second) — "structurally impossible for a 1-second-aggregate-only source,"
  i.e. genuine trade-at-price prints, not synthesized bars.
- **Production scale, not a toy probe.** `research/scalping_lab/substrate/MANIFEST.csv` records
  40 already-exported sessions (341M rows total per `CAMPAIGN_STATE.md`), each with real Last/Bid/
  Ask event counts in the hundreds of thousands to millions, spanning 2025-08 through 2026-05 — the
  full DISCOVERY+CONFIRMATION date range this task is scoped to.

**Caveat on "over the relevant window."** This is NT8's own hosted historical-tick server via the
"Simulation" connection (`runs/DOM01_LIQUIDITY_STATE/collector/compile_evidence.json` step1: only
"Simulation" was Connected among 5 listed connections) — genuine trade prints, but **not**
order-book truth (no order-id/queue-rank field on `MarketDepthEventArgs`, confirmed by reflection
in the same file — this is MBP-class data at best, and DOM01 separately found no MBO/Market-Replay
history exists on this machine at all). More importantly, `CONTAMINATION_LEDGER.md` and
`CAMPAIGN_STATE.md` both flag that **the vendor's Bid/Ask server history is a rolling ~1-year
window that vanishes** — this is why the campaign already treats un-exported confirmation sessions
as an archival race ("archiving ≠ examining... data vanishes"). So: access is real and proven for
the current window, but it is not a permanent archive — a future AUCTION prototype's validation
sessions should be chosen from data already exported to disk (raw/NQ parquet), not re-pulled from
the live server assuming perpetual availability.

## 2. What an early NinjaScript prototype would need to validate before being trustworthy

The causal algorithm to reproduce is `runs/AUCTION01_VALUE_STATE/spec.yaml`'s `construction`
block: per session, sort Last prints by time; `tick_id = round(price/0.25)`; running
`cum_vol_at_price` (cumsum per tick_id bucket); `running_max_vol` (cummax across buckets); a new
POC record when `cum_vol_at_price[i] >= running_max_vol[i]`; `poc_tick` forward-filled from record
rows. Concretely, before trusting a NinjaScript version of this:

1. **Session reset semantics.** The Python construction is per-session by file boundary (one
   `raw/NQ/*.parquet` per session, so state trivially resets). A NinjaScript indicator running
   continuously across a multi-session historical load must explicitly zero `cum_vol_at_price`,
   `running_max_vol`, and the running VWAP accumulators at the campaign's frozen 18:00 ET session
   boundary (`CLAUDE.md`: "Sessions 18:00 → 17:00 ET"), not rely on an assumed bar-array reset —
   needs an explicit test against `Bars.IsFirstBarOfSession` (or session-iterator equivalent) on a
   multi-session historical run, diffed against Python's per-file reset.
2. **`tick_id` rounding to 0.25.** Must use `Instrument.MasterInstrument.TickSize` (confirmed 0.25
   for NQ throughout this campaign) and a rounding rule that matches Python's `round()`
   (round-half-to-even) — C#'s default `Math.Round` is also round-half-to-even, so the conventions
   *should* agree, but this is exactly the kind of assumption that must be tested on real prices,
   not asserted from language-spec reading, especially near any price landing exactly on a
   half-tick boundary.
3. **Running max-volume-bucket tracking.** Python does this with a `groupby(tick_id).cumsum()` +
   global `.cummax()` — vectorized, and the spec.yaml's own proof that a per-touched-bucket running
   max equals the true cross-bucket running max relies on monotone non-decreasing cumulative
   volume per bucket. A NinjaScript port would use an incrementally-updated
   `Dictionary<int,long>` keyed by `tick_id` plus one running-max scalar, updated once per tick —
   algorithmically equivalent, O(1) per tick instead of O(n log n) once, but **must be verified
   tick-by-tick against the Python series on a shared session**, not assumed equivalent from reading
   the algorithm.
4. **Contract-roll handling.** The frozen baseline already uses "NQ 09-26 (NQU6, back-adjusted
   merge)" (`CLAUDE.md`), and a light spot-check of already-exported probe extracts for three
   DISCOVERY dates spanning the campaign's timeline (`research/scalping_lab/runs/EXPORT01/
   p20250910_on`, `p20260123`, `p20260506` — head/tail only, format check) shows one continuous
   price series with no discontinuous jump across those dates (≈23898 in 2025-09, ≈25605 in
   2026-01, ≈28250 in 2026-05 — smooth drift, not a roll gap), consistent with the continuous
   back-adjusted contract already used for the frozen SolarWave baseline. What is **not** yet
   checked: whether the back-adjustment offset applied to historical prices is itself always a
   multiple of 0.25 — if it isn't, a `round(price/0.25)` tick_id computed on back-adjusted history
   could disagree, session to session, between two independently-adjusted price feeds even when
   both are "the same instrument." This is a concrete, testable, currently-open item, not
   previously checked anywhere in this repo.
5. **Bar/tick synchronization.** DATAPROBE01 explicitly flags this as open, not solved: 46%
   (Last) / 61% (Bid/Ask) of ticks share a millisecond timestamp, and "same-timestamp cross-series
   ordering must be treated as unknown (±4ms sync ambiguity)." The Python construction assumes
   "sort Last-trade prints by time" with ties presumably broken by row order in the exported CSV
   (== the exporter's own emission order, which is itself only as reliable as NT8's internal
   engine-delivery order — untested against true exchange sequence). A NinjaScript prototype
   consuming ticks live via `OnMarketData` needs to confirm its own delivery order agrees with
   what the exporter recorded, on the same session, before the two computations can be called
   "the same algorithm on the same data."

## 3. What's already de-risked vs. what's still unknown

**Already de-risked (evidence exists in this repo, not merely asserted):**

- **The C#-compile-and-verify pipeline works, right now, without a human at the keyboard for the
  compile step.** `runs/DOM01_LIQUIDITY_STATE/collector/compile_evidence.json` shows a fresh
  NinjaScript file (`Dom01DepthRecorder_v1.cs`) compiled **in-memory** via
  `mcp__crosstrade__CompileNinjaScript` against the live NT8 8.1.8.1 AppDomain (133 referenced
  assemblies, 0 errors, 0 warnings), then written to NT8's real `bin/Custom/Indicators/` source
  folder and confirmed present via `ListNinjaScriptFiles`. The remaining step — NT8 rebuilding its
  own `NinjaTrader.Custom.dll` (F5 in the editor, or a restart) — is explicitly disclosed there as
  an owner action, not yet done, and would be needed again for any AUCTION prototype.
- **Historical tick access is proven by direct probe, not by documentation.** DATAPROBE01 (two
  live NT8 backtest jobs) plus the production-scale `SWScalpTickExport_v1/_v3` runs (40 sessions,
  341M rows, `MANIFEST.csv`) already exercise exactly the `Calculate.OnEachTick` +
  `AddDataSeries(Tick,1,MarketDataType.X)` combination a running-POC indicator would need.
- **The dual-truth verification discipline this task should reuse already exists as working code**
  — `runs/PRICE01_PRODUCT_A_GENUINE_MNQ/src/01_dual_truth_repricing.py` and
  `runs/U6B_PRODUCT_A_SCALE_RATE/src/02_genuine_mnq_repricing.py` both run one decision formula
  twice against two independently-sourced price truths, assert the decision path is byte-identical
  between them (`assert identical, f"... STOP: exposure path differs ... price is leaking into the
  decision layer"`), and only then compare the *economics* that legitimately differ. The exact
  same pattern is directly reusable for Python-vs-NinjaScript POC parity: compute
  `running_poc`/`poc_share` in Python (already built, AUCTION01) and in a NinjaScript indicator on
  an identical session, export both, assert row-by-row numerical agreement (or a documented,
  bounded tolerance), halt-and-investigate on any disagreement. The harness discipline for "prove
  two pipelines agree" is not new work — only its NinjaScript-side input is.
- **Never touches the vendor boundary.** A fresh custom indicator (like `Dom01DepthRecorder_v1`,
  and like the proposed AUCTION prototype) is a new file, not a modification of the licensed
  RenkoKings `SolarWaveRK` assembly — same category DOM01 already established as safe.
- **Session/commission/fill conventions are already frozen and known** (`CLAUDE.md`: 18:00→17:00
  ET sessions, exit-on-session-close, Lifetime commission template, Standard fill) — a POC
  indicator doesn't need to re-derive these, only respect the same session boundary for its own
  resets (item 1 above).

**Still unknown / not yet attempted (this pass did not attempt them, by design):**

- **No NinjaScript running-POC code exists yet** — zero `.cs` written or compiled this pass, per
  task scope.
- **No row-by-row Python-vs-NinjaScript numerical parity check has ever been run for any tick-
  level causal statistic.** PRICE01/U6B's dual-truth pattern has only been applied Python-vs-
  Python (two independently-sourced price *series*, both consumed in Python). `runs/V1R4_NT8_
  PARITY` is real NT8-vs-Python parity work, but at the trade-count/net-P&L level for existing,
  already-frozen strategies (SolarWave, Product A) — never at the raw-tick causal-feature level
  AUCTION would need. This is the one genuinely novel verification this campaign hasn't done yet.
- **Items 4 and 5 above** (back-adjustment/tick-rounding interaction; true engine tick-delivery
  order vs ±4ms ambiguity) are open, concrete, and testable, not merely theoretical.
- **Bid/Ask "Volume" field semantics remain UNKNOWN** (DATAPROBE01: "could be BBO size, size
  delta, or update aggregation... L3 status stays UNKNOWN until a dedicated check"). Not needed for
  a Last-trade-only running POC, but would block any future extension that mixes BBO size into a
  value-state measure.
- **Coverage gaps inside the sanctioned DISCOVERY set itself.** Cross-checked directly from
  `MANIFEST.csv`: 13 of the 37 DISCOVERY sessions hit the exporter's row cap (12M rows) and are
  missing their afternoons — matches `CAMPAIGN_STATE.md`'s own count exactly ("13 high-vol sessions
  truncated at the 12M cap (afternoons missing)"). 11 of those 13 have a since-added, uncapped
  `_rth`-windowed re-export on disk, but **two — `20251117` and `20260519` — are still capped in
  both their full-session and RTH-windowed exports** (`s20251117_rth` and `s20260519_rth` both
  show `capped=1` too), consistent with the most recent commit's own note: "s20251117 re-export
  deferred to next natural restart" (`SWScalpTickExport_v3` staged but not yet re-run for it). Any
  future Python-vs-NinjaScript parity diff must avoid these two sessions, or it will show spurious
  disagreement in the missing afternoon window that is a Python-side export artifact, not a
  NinjaScript defect.

## 4. Specific red flags that could make Python and NinjaScript disagree

- **Timestamp resolution / same-millisecond ordering.** DATAPROBE01's own finding: ~4ms
  quantization, 46–61% duplicate-timestamp ticks. Any diff between Python's file-order tie-break
  and NinjaScript's live engine-delivery order is untested and could produce off-by-one POC-record
  timing near busy moments — exactly where a value-state signal matters most.
- **Shared-source blind spot.** The Python "ground truth" (`raw/NQ/*.parquet`) *is* NT8's own
  historical feed, exported via `SWScalpTickExport`. A live NinjaScript prototype reading the same
  feed live is not an independent cross-check of "did NT8 record the true exchange print correctly"
  — agreement between Python and NinjaScript here proves internal consistency of the campaign's
  pipeline, not fidelity to the real tape. That's an acceptable scope limit (matches how this
  campaign has always used NT8's data), but should be stated plainly, not implied away.
  Additionally, the exporter's own 3-series architecture (Last/Bid/Ask each on a separate
  `BarsInProgress` index, each firing its own `OnBarUpdate`) is not how a real single-series
  causal `OnMarketData` indicator would consume ticks — the exporter proves *that* ticks are
  visible, not that a differently-shaped consumer sees them in the identical order.
- **Row-cap truncation already contaminates 13/37 DISCOVERY sessions** (2 of them still, with no
  clean replacement on disk) — see item above; a naive parity check on the wrong session would
  misdiagnose an export artifact as a NinjaScript defect.
- **Known, already-quantified NT8-vs-Python economics residuals for existing strategies**
  (`runs/V1R4_NT8_PARITY/FULL_HISTORY_CERTIFICATION.md`): a synthetic 1-tick adverse-slip
  convention in Python's `_fill()` (deliberate, disclosed, not present in NT8's real Standard
  fill) and NT8's documented data-boundary serialization quirk (`CLAUDE.md`: a position open at
  the data boundary "may be missing from the serialized trade list, engine totals unaffected") —
  together explaining a persistent, direction-consistent NT8-vs-Python gap in every certified
  block (NQ +4.13%, MNQ +4.41% pooled; Product A +10.91%, only ~3.9% of which
  `runs/PRICE01_PRODUCT_A_GENUINE_MNQ` was able to attribute to price-basis choice, per its own
  REPORT.md — the rest stays "a plausibility argument, not a proof"). These are *execution-layer*
  gotchas, not feature-computation gotchas, but any AUCTION strategy built on top of a validated
  POC feature will inherit this same class of residual once it starts placing (simulated) fills —
  feature-level parity would not be the last parity gate needed.
- **Vendor server history is a rolling ~1-year window, not a permanent archive**
  (`CONTAMINATION_LEDGER.md`, `CAMPAIGN_STATE.md`) — a validation plan that assumes today's
  DISCOVERY-date tick data will still be re-pullable from the live server months from now is not
  safe; use the already-exported/archived sessions.
- **L3 (BBO size) semantics unresolved** — not a POC blocker today, but a landmine if a later
  AUCTION iteration folds BBO size into the running value-state measure without first resolving
  DATAPROBE01's open question.

## Bottom line

Both pillars this feasibility question turns on — genuine causal access to historical trade-tick
data inside NT8's engine, and a working, evidence-backed compile pipeline for new NinjaScript — are
already proven in this repo by direct, reproducible probes (DATAPROBE01; DOM01's compile_evidence.
json), not by inference from documentation. What has never been done, and is exactly what an early
prototype pass should do first (only once a candidate is frozen, per this campaign's own workflow
convention), is the one check nobody has run yet: reuse the PRICE01/U6B dual-truth harness pattern
to diff Python's `running_poc`/`poc_share` against a NinjaScript port of the identical algorithm,
row by row, on a clean (uncapped) DISCOVERY session — before building any strategy around it.
