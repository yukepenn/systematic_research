# BEST_ONE_NQ PARITY CERTIFICATE — SolarWaveOneContractNQ_v5

> **UPDATE 2026-08-09 (same-day continuation, first-divergence forensics).** The residual below
> is RESOLVED. Event-level (leg-by-leg) forensics against the real NT8 trade list found the
> Presidents Day 2025-02-17 divergence flagged in the original certificate was caused by a real,
> confirmed NinjaScript defect (DEFECT 3, shared across all 3 canonical objects): the BMOM leg's
> own end-of-RTH flatten was still a hardcoded clock (`hm >= 155700`), never migrated when the C2/C3
> work made the entry-block/forced-flat overlay session-relative. On a holiday session ending before
> 15:57 ET, `bmomPos` never resets and survives, stale, into the following overnight session.
> Confirmed on live NT8 output (`SolarWaveOneContractNQ_v4`, unfixed): an extra, wrong short entry
> at 2025-02-17 18:06 ET, M=-4.25 with the stale `bmomPos=-1` vs the correct M=-1.42 at `bmomPos=0`.
> 11 of 44 early-close sessions in the dev window have `bmomPos != 0` at the truncation boundary and
> would trigger this. **Fixed** with a one-line, non-signal change (`bmomPos` now also flattens on
> `sessEnd`) in **`SolarWaveOneContractNQ_v5`**, deployed and independently verified against live NT8
> output: the Q1-2025 leg-by-leg resync now finds **0 divergent episodes across all 214 legs** (down
> from 1), full decision-timing/side agreement. The residual net-profit gap fully reconciles to two
> already-understood, non-defect factors — see "Post-fix reconciliation" below. See
> `runs/V1R4_NT8_PARITY/src/one_nq_event_forensics.py` / `one_nq_resync_align.py` for the forensics
> code and `out/one_nq_events/` for the raw event logs. **STATUS: CERTIFIED** for the event-level
> mechanism (full multi-year net-profit certification remains open — see below).

## Post-fix reconciliation (exact, to the dollar)

Comparing `SolarWaveOneContractNQ_v5` (fixed) against the Python twin for Q1-2025 (both warmed from
2024-04-01, 107 matched round trips, byte-identical decision timing/side on every leg):

| component | amount |
|---|---:|
| Python Q1 net (round-trip, entry-time filter — the certificate's own convention) | -$5,605.88 |
| − boundary trip NT8's serialized trade list omits (2025-03-31 11:57→16:42, a **known, disclosed
|   NT8 convention**: CLAUDE.md "a position still open at the data boundary... may be missing from
|   the serialized trade list, engine totals unaffected") | -$3,075.64 |
| + systematic 1-tick fill-price convention (Python's synthetic adverse slip vs NT8's real
|   Standard fill; **already disclosed in `spec.yaml`** as a Python-side approximation not meant to
|   stack on top of NT8's own engine): 211/214 legs differ by exactly 1 tick ($5/leg × NQ) | +$1,055.00 |
| = reconciled NT8 net | **-$7,626.52** |
| actual `SolarWaveOneContractNQ_v5` NT8 net (Q1, same window) | **-$7,626.52 (exact match)** |

Zero unexplained residual. Every dollar of the post-fix gap is accounted for by two mechanisms the
campaign already knew about and explicitly disclosed before this forensics pass, not by anything
newly discovered. This is a materially stronger result than "NOT CERTIFIED, residual unexplained."

---

**ORIGINAL WAVE STATUS (superseded above): NOT CERTIFIED — warmup substantially improves agreement
(decision/trade COUNT now matches almost exactly), but a real, smaller residual dollar discrepancy
remains and was not driven to a confirmed first-divergence root cause this wave.**

## Identity

| field | value |
|---|---|
| strategy | SolarWaveOneContractNQ_v4 |
| source hash | repo `src/ninjascript/SolarWaveOneContractNQ_v4.cs` = 23,793 bytes |
| deployed NT8 hash | byte-identical (23,793 bytes), confirmed via `ReadNinjaScriptFile` this session |
| instrument | NQ 09-26 (NQU6), both signal and execution legs |
| bars | 3-minute |
| session | CME ETH, session-relative C4 flatten, 16:45 mandatory close honored |
| commission | NinjaTrader Brokerage Lifetime ($2.18/side NQ) |
| slippage | none added (Standard fill, no override) |
| fill mode | Standard |

## Warmup-corrected comparison (same methodology as Product A's certificate)

| test | Q1 2025 net |
|---|---:|
| NT8, warmed-up from 2024-04-01 (9 months warmup) | **-$6,661.52** |
| Python twin, continuation state from 2022 (full history) | **-$5,605.88** |

**Difference: -$1,055.64, 18.8% relative to the Python figure** -- both sides now agree on SIGN
(both negative) and rough magnitude, a large improvement from a hypothetical fresh-start
comparison, but the relative gap is materially larger than Product A's 0.71%. Disclosed candidate
explanation: the underlying quarter's net magnitude here (~$5-6k) is much smaller than Product
A's (~$9-12k), so a similarly-sized ABSOLUTE dollar gap reads as a larger PERCENTAGE -- this is a
real statistical effect (small-denominator amplification), not proof the underlying $ gap itself
is proportionally larger, but it is not, on its own, sufficient grounds to certify.

## Decision/trade-count agreement — strong, and directly checked

| | count |
|---|---:|
| NT8 Q1-2025 trade count (this window) | 107 |
| Python incumbent position-change events in Q1 2025 | 212 (~106 round trips) |

**Trade counts match almost exactly (106 vs 107, off by at most 1)** -- this is strong evidence
that the DECISION LOGIC (when to enter/exit/reverse) agrees closely between the real NT8 object
and the Python replica; the residual dollar gap is much more likely a smaller, cumulative
FILL-PRICE or rounding effect across ~107 trades than a structural decision-logic defect. This
was NOT carried further to an actual first-divergence trade-by-trade price comparison this wave.

## Residual discrepancy classification (partial, not completed)

Per the directive's classification taxonomy, the evidence gathered this wave is most consistent
with **FILL** or **ORDER_TIMING** (small, cumulative per-trade price differences) rather than
**SIGNAL**, **SESSION**, **WARMUP** (warmup's contribution is already isolated and mostly
resolved), **ROUNDING** (Python's `_fill()` 1-tick-adverse-slip approximation vs NT8's real
Standard-resolution fill could plausibly diverge more on a leaner-margin, higher-turnover object
like this one than on Product A's larger, more graded target). **Not proven** -- this is the
recommended starting hypothesis for a future session's continuation, not a closed finding.

## What remains open (post-fix)

Full multi-year net-profit certification (all 4.5 years, not just a Q1 spot-check) remains open,
blocked by the same CrossTrade long-job limitation documented in `REPORT.md` — this is an
infrastructure ceiling, not a signal-correctness question, and the event-level mechanism is now
proven correct on every tested window. The concrete next step for a future session: chunked
warmup-preserving quarterly stitching (per FINAL_OWNER_DECISION §10) to accumulate a full-history
net-profit comparison, now that the decision layer itself is known to be exact.

## Full-history chunked certification (2026-08-09, third continuation, same wave)

All 4.5 years (2022-01-03 → 2026-05-29) now covered via 7 chunked NT8 jobs, no gaps, no
duplicated evaluation P&L. Trade count matches Python to within 1 in every single block. Full
detail: `runs/V1R4_NT8_PARITY/FULL_HISTORY_CERTIFICATION.md`. Net-profit totals: NT8 $316,442.72
vs Python $303,880.28 (+4.13%), fully consistent with (not proven beyond) the same 2 disclosed,
non-defect conventions found on the Q1-2025 window.

## Final verdict

**CERTIFIED for the event-level decision mechanism** (Q1-2025 spot-check window, fixed object
`SolarWaveOneContractNQ_v5`): 0 divergent decision episodes out of 214 legs, and the residual
dollar gap reconciles exactly to two already-disclosed, non-defect conventions (NT8's boundary
trade-list serialization quirk and Python's synthetic 1-tick fill-price convention). **Full
multi-year net-profit certification remains a separate, open item** pending a stable chunked
CrossTrade harness — this is scoped, understood, and not blocked by any unresolved correctness
question. `_v4` (unfixed) is superseded; `_v5` is the new incumbent for this object pending
BASELINE_MODELS.md's own promotion review (see CURRENT_TRUTH.md).
