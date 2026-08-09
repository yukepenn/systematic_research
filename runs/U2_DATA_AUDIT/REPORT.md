# U2 — microstructure / new-data-source audit

**Date:** 2026-08-09. **Type:** audit only, no `src/`, no candidate — same pattern R6 used for
its own audit-only closure. Per directive sec31-33: inventory already-owned data sources in this
repo, establish provenance/coverage/causal-availability, and decide whether a genuinely new
research family is justified BEFORE writing any code against it. No paid data was acquired; no
NT8/CrossTrade call was made — every fact below comes from reading files already in the repo.

## U2-A — `research/scalping_lab`'s tick/BBO substrate

**Source read:** `research/scalping_lab/DATA_INVENTORY.md`, `DATA_SUBSTRATE.md` (that campaign's
own, independently-maintained provenance docs — not re-derived here, per directive sec32's
explicit instruction not to assume another campaign's data is valid without its own audit).

| Property | Finding |
|---|---|
| Instrument / provider | NinjaTrader hosted historical servers, NQ/MNQ Last-tick, ms-class timestamps |
| Coverage | **2025-08-10 → 2026-08-06, continuous, ≈ 12 months** (L1 CONFIRMED). Deeper history was requested and is NOT present (empty shell folders for NQ contracts before 2025-08-10) — this is a genuine data-availability ceiling, not a scoping choice either campaign made. |
| L2 (BBO) | OPEN / probe-in-progress in that campaign (not yet CONFIRMED) |
| L3 (sizes) / L4 (depth) | UNKNOWN / BLOCKED_BY_DATA |
| Contract convention | **Single unadjusted contract per session** (`SWScalpTickExport_v1`), explicitly NOT the back-adjusted continuous merge this campaign's CLAUDE.md freezes as the canonical NQ convention |
| Holdout | That campaign's own constitution seals 2026-06-01 → 2026-07-31 as its holdout (separate from, and stricter than, this campaign's ≥2026-08-01 boundary) — absence of exported files is their enforcement mechanism, and this audit did not attempt to read past it |

**Compatibility verdict:** the coverage ceiling is the decisive fact. This system's dev window is
2022-01-03..2026-05-29 (4.4 years, ~1,100+ sessions); the tick/BBO substrate covers ≈ 205-247
sessions, all in the LAST ~10 months of that window. Any feature built from this data could be
diagnosed only on a short, entirely-recent slice — it structurally CANNOT clear this campaign's
own chronology gate (directive sec44: year-by-year, LOYO, rolling 60/120/252, "a candidate cannot
be promoted because one recent period is strong" — precisely the standard that already sank both
R2V1 and R2B's entry-timing candidates for being 2026-stub-only). A microstructure feature from
this substrate would be *unfalsifiable on stale-regime risk* by construction, not because of a
weak effect but because the data to test it elsewhere doesn't exist yet.

**Disposition: DOCUMENT AND SKIP for any promotion-track family**, exactly per directive sec32's
own fallback instruction. Recorded as a **bounded future diagnostic** only: once the tick
substrate itself accumulates 2-3 more years (i.e., in future research waves as time passes), a
microstructure-conditioning study becomes chronology-testable and should be revisited then. Doing
it now would repeat the exact mistake this campaign spent R2V1/R2B catching — a short-window
artifact mistaken for structure. Not merged into U0.

## U2-B — ES/RTY/YM context-market bars (`runs/W18_XINST_BARS/`)

**Source read:** `runs/W18_XINST_BARS/spec.yaml`, the 3 exported CSVs, and
`research/system_master/COMPLEMENTARY_ENGINE_FRONTIER.md`'s slate history.

| Property | Finding |
|---|---|
| Coverage | ES/RTY/YM 3-minute bars, 2022-01-02..2026-05-29, same back-adjusted-merge convention as NQ, same timestamp grid — **full chronology match**, no coverage ceiling |
| Provenance | Exported for `W18R2_M5_XINST` (mechanism-replication use, explicitly barred from ever being a traded leg per that spec's own `why_this_export_exists` note) |
| Prior use | **Already extensively tested as an Engine-3 signal source**: `COMPLEMENTARY_ENGINE_FRONTIER.md` slates 4-5 (seq 410-412, 479) ran 6 cross-market candidates (lead-lag, sweep-reversal, breadth/divergence forms) against this exact data — **all killed**, bringing the cumulative cross-market/Engine-3 record to **15/15 failures, axis explicitly declared exhausted**. R6 (this campaign's own prior-wave audit) independently re-confirmed no surviving candidate exists in that record. |

**Compatibility verdict:** the data itself is fully usable (no provenance or chronology problem
at all) — the constraint is *mechanism*, not data. Directive sec33 frames a legitimate, narrower
use than what's already been killed: ES/RTY/YM as a **context/conditioning feature on the
EXISTING Solar/B-MOM signal** (e.g., "does NQ-vs-RTY breadth divergence modulate the confidence of
an already-generated Solar/B-MOM signal", a soft multiplier) is mechanistically distinct from what
the 15 killed candidates tested (ES/RTY/YM patterns used as *independent, standalone*
directional/entry signals — lead-lag prediction, sweep-reversal, shock continuation). The
distinction matters: R4/R5 already established that features can carry real bulk information
while being useless or dangerous as standalone filters (CLV, direction_x_volume) yet remain
worth testing as *soft conditioning* on the incumbent decision (U5's exact framing). The same
logic could apply to a cross-market breadth/dispersion feature.

**Disposition: NOT tested this run** (no candidate manufactured to fill a slot, per directive
sec41's explicit prohibition — "the previous threshold almost worked, so try 17 nearby
thresholds" reasoning is exactly what would be needed to justify testing this today without a
prior empirical residual motivating it). Recorded as a candidate **feature source for a future
U5-adjacent soft-weighting family** IF and only if U5's within-system residual-information work
(CLV/VWAP/vol/rejection) finds a real but incomplete effect that a cross-market breadth term
might plausibly explain — i.e., this becomes live only when a genuine empirical residual (type A
per directive sec41) motivates it, not proactively. Not merged into U0 this run.

## U2-C — other data classes checked

- **NT8 local tick/minute cache beyond scalping_lab's read** (`DATA_INVENTORY.md`'s own census):
  NQ minute history to 2005 already fully consumed by this campaign (`AUDIT03_BARS`); NQ tick
  only ≈12 months deep (same ceiling as U2-A); Bid/Ask tick series NOT cached for NQ at all
  (`Not cached — zero .Bid.ncd/.Ask.ncd files`) — even a fresh NT8 pull could not backfill BBO
  history beyond what U2-A already found.
- **Volatility indices / market breadth / calendar data**: no such series found already present
  in this repo outside scalping_lab's own tick-derived proxies (which inherit U2-A's coverage
  ceiling) and the session-phase/calendar features already built directly into U0 from NQ's own
  timestamps. Acquiring an external VIX/breadth feed would be new paid/external data acquisition,
  explicitly barred by directive sec31.

## Summary

Two data classes were inventoried; **neither is merged into U0 this run**. Genuine tick/BBO
microstructure (U2-A) is compatible in principle but chronology-incompatible with this campaign's
own promotion standard for at least another 2-3 years of accumulation — a coverage problem, not a
mechanism problem. Cross-market context bars (U2-B) are fully chronology-compatible but the
*standalone-signal* form of this idea is already exhausted at 15/15; only a *soft-conditioning*
reformulation, motivated by a specific U5 finding, would be a genuinely new (not re-litigated)
hypothesis. Both dispositions match directive sec32's own instruction: document and skip rather
than manufacture a candidate to fill a slot.
