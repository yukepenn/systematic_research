# W1-0b BBO_INTEGRITY_AUDIT — VERDICT (2026-08-08)

Spec: `specs/W1-0b_bbo_integrity_audit.md` (frozen 12407fd before readout). 6 frozen
sessions, RTH only. Table: `w10b_bbo_audit.csv`.

## T2 — ordering sensitivity (decisive): **SPREAD CLAIM CONFIRMED**
Sync-only reconstruction (exact same-timestamp Bid∧Ask pairs = plausible true book
snapshots, 20-26% of events) vs unrestricted asof: **median spread IDENTICAL on all 6
sessions** (2t=2t on 4, 3t=3t on 2); P(1-tick) differs only 1-5pp (sync even lower).
Per the frozen rule (agreement within 0.5t): **"NQ is a 2-3 tick market" is
CONFIRMED-PENDING-T4** — not a reconstruction artifact. The cruel cost floor is real.

## T1/T3 — the reconstruction is mostly synchronized and fresh
87-92% of Bid events share exact timestamps with Ask events (paired book updates);
99.3-99.7% of trades share a timestamp with a quote; 98-99% of book-time has counter-side
quote age ≤ 50ms; fresh-conditional medians unchanged. Staleness does NOT drive the wide
spread.

## T3b — trade-level BBO pairing FAILS the clean-state criterion
Outside-[Bid,Ask] rate in the FRESH (≤50ms) stratum: **6.4-9.5% — above the 2% PASS bar.**
Since staleness is excluded, the cause is same-millisecond ordering ambiguity: within one
ms, a trade may print against the pre-update book while the join supplies the post-update
quote. Trade-time exact BBO therefore carries ~±1 tick uncertainty. (Stale-stratum outside
rates are erratic — 0% to 66% — but stale moments are <2% of time.)

## Ruling (per spec outcomes)
1. **Spread-REGIME statistics (time-weighted distributions, I-1 map) are TRUSTED** —
   ms-ordering noise cannot move time-weighted medians; claim frozen PROVISIONAL-pending-T4
   (Tick Replay cross-check, owner-run, queued as optional).
2. **BBO_EXEC stays DIAGNOSTIC** (T3b fail): fill-level BBO truth is ±1 tick at same-ms
   moments. Where BBO_EXEC is reported, quotes are taken as-of t−1ms AND results carry a
   ±1-tick uncertainty band. **BENCHMARK_C1/C2 remains promotion truth** (per Amendment 3).
3. Practical synthesis for scalp economics: honest RT friction = spread-map-based
   (2-3t median crossing cost + commission) with C2 as the stress — C1 (2.872t) sits at
   the optimistic edge of the confirmed range; net-tick targets should clear ~4t to be
   ROBUST_MARGIN.

Registry: audit rows S0-I3b. No constants tuned after readout.
