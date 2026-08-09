# U9 — true microstructure provenance + prequential infrastructure (Track C): infrastructure only

Persisted here by the orchestrating session from the subagent's returned text — its Write tool
blocked direct creation of this file.

**Type:** infrastructure/provenance only, per `CONTINUOUS_EVOLUTION_WAVE2_EVI.md`'s own scoping.
No alpha feature, P&L, or candidate was tested — confirmed explicitly in spec.yaml. Does not
reopen or contradict `runs/U2_DATA_AUDIT/REPORT.md` (still correctly closed for its own, different
question — Track-L LOYO compatibility); this family answers the new Track-C question.

## Correctness gate

Not implicated — this family built no `pos_seq`/exec path and computed no P&L.

## Step 1 — per-layer provenance disposition (all facts verified on disk 2026-08-09, not assumed from docs)

| Layer | Disposition | Key evidence |
|---|---|---|
| **L1 (last-trade ticks)** | **PROVENANCE PASS** | 40 stratified sessions, 2025-08-11→2026-05-20 (not continuous — monthly density 1-7 sessions); ms-class ET timestamps verified from raw file boundaries; `bip`∈{0,1,2}={Last,Bid,Ask} cross-verified exactly against MANIFEST counts; no anomalous intra-session price jumps (max 7.0pt near a contract-expiry session). Caveat: 13-53% of raw rows are exact byte-for-byte duplicates (95% immediately-adjacent repeats, likely exporter artifact) — must de-dup before any event-COUNT feature; price/OHLC features unaffected. |
| **L2 (BBO quotes)** | **PROVENANCE PASS, with caveats** | **Updates U2's "OPEN" finding to CONFIRMED** — citing `research/scalping_lab/runs/DATAPROBE01/results.md` (2026-08-07) and `DATA_INVENTORY.md`'s current status line, both written after U2 but apparently not cross-read by it. Verified on disk: 37/40 sessions have BBO (3 L1-only "server holes" match `CAMPAIGN_STATE.md`'s own named list exactly). Inherited caveat: ±4ms same-timestamp cross-series ordering is unresolved, so that campaign's own W1-0b audit keeps BBO_EXEC diagnostic-only, C1/C2 as promotion truth — this family adopts that ruling rather than re-litigating it. |
| **L3 (top-of-book sizes)** | **PROVENANCE PARTIAL** | Field populated, non-degenerate, but semantics unresolved between size-level/size-delta/update-count — inherits scalping_lab's own I-4 pilot ruling ("PLAUSIBLE-size, coarse only"), not independently re-tested here. |
| **L4 (multi-level depth)** | **PROVENANCE FAIL** | `db\replay\` empty, paid data barred, already exhaustively confirmed by the source campaign across multiple waves. |

## New findings from this family's own disk inspection (not previously documented at this specificity)

1. Duplicate-row artifact in L1 ticks (above).
2. `sechilo`'s price fields = `grid1s.mid` × 4 (NQ's 0.25pt tick expressed as integer ticks) —
   verified by session-level join, corr=0.9999995 — any future work combining both layers must
   apply this scale factor or get a silent 4x price error.
3. 6/40 grid1s sessions don't reach 16:59:59 close — diagnosed individually: 2 genuine exchange
   early-closes (Labor Day, day-after-Thanksgiving), 2 trivial 1-second shortfalls, 1
   already-known ~105min gap (s20251117, campaign's own W9 re-export queued), and **1 fresh
   finding**: s20260519 has a genuine ~33min gap (16:27-17:00 ET) that overlaps this campaign's
   own C4 pre-close mechanism window.

## Locked-forward cross-check (both boundaries respected)

Materialized substrate (through 2026-05-20) sits cleanly inside both scalping_lab's 2026-06-01
holdout and this campaign's 2026-08-01 LOCKED_FORWARD boundary — verified by absence-on-disk,
not just doc claim. One disclosed nuance: DATAPROBE01's raw (gitignored, uncommitted)
capability-probe dumps touched 2026-07-14/15 (inside the scalp holdout) for timestamp/count
characterization only, already self-disclosed and ruled non-contaminating by scalping_lab's own
`CONTAMINATION_LEDGER.md` (2026-08-07). This family independently agrees but adds 2026-07-14/15
to the frozen design's exclusion list anyway as a hygiene margin.

## Step 2 — frozen prequential design (spec.yaml, ready for a future U9-alpha family)

Expanding-origin, calendar-month blocks with a floor-3-sessions merge rule (Dec-2025+Jan-2026
merged to clear the floor). Result: 9 blocks (1 training seed + 8 scored), 37 scored sessions,
spanning 9 calendar months. Minimum bar for a defensible verdict set at ≥6 scored blocks/≥25
sessions — current coverage clears it but not comfortably (any real model needing >2 blocks of
warmup will fail this bar on today's substrate). Within-block clustering: SESSION is the unit of
independence (never tick/quote); mandatory session→block collapse before any cross-session
pooling; block-level bootstrap/sign-test only, explicit prohibition on tick-pooled t-stats.
Required future reporting: forward-only C1-costed net/Sharpe/Sortino/MaxDD/CDaR95/pct-positive-
blocks/pct-positive-months/worst-block/median-block/turnover/right-tail-capture plus session/day/
block counts (never tick count as sample-size proxy). Explicit scope fork documented for two
different future-construction types (standalone scalp strategy vs. Product-A/B conditioning
overlay), since the latter faces a much thinner, non-random-overlap evidentiary problem
structurally similar to what closed U2's Track-L attempt.

**No alpha work occurred**: no feature-outcome correlation, P&L, or candidate construction was
computed at any point in this family.

## Disposition

Infrastructure investment complete. L1/L2 pass (with caveats), L3 partial, L4 fails (unchanged).
A future, separately preregistered U9-alpha family may now consume this frozen prequential
design — this family does not itself authorize or predict what that family will find.
