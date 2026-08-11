# B1_NT8_IMPLEMENTATION_PARITY — PASS, construction verified correct

**Verdict: implementation-certified.** `SolarWaveOneContractNQ_B1_v1.cs` /
`SolarWaveOneContractMNQ_B1_v1.cs` correctly implement the frozen SIMPLE01 B1 rung inside the
real NT8 engine. This does **not** change B1's frozen historical verdict (still blocked on one
INCONCLUSIVE Sharpe read per the SIMPLE01 completion pass, commit `e5e03bf`) and does **not**
authorize opening any protected or locked-forward data — per `B1_FUTURE_CONFIRMATION_SPEC.md`,
both remain separately gated, unopened by this run.

## Primary comparison: NT8 B1 vs NT8 incumbent v5 (same engine, same instrument, unambiguous)

Two windows (same as `EQV04_NT8_CANONICAL_PARITY`, see that report for the DST-boundary process
note):

- **Smoke** (2026-06-01 → 2026-07-31, 45 sessions): B1 and incumbent produced **byte-identical**
  trade lists for both NQ and MNQ (81/81 trades, net matching to the cent, fills CSVs diff to
  zero). Initially concerning, but fully explained: `TiltSma=50` requires 50 *sessions* of
  in-backtest history before `tiltState` can leave zero, and this window only contains 45. With
  `tiltState` structurally stuck at 0 for the whole window, `mm`'s ternary evaluates to `1.0`
  regardless of whether the real code or B1's forced constant is used — the one-line change had
  no bar to actually exercise. This is a genuine null result about the window, not evidence B1
  is broken.

- **Long** (2025-01-01 → 2026-05-31, ~369 sessions, matching `SIMPLE01`'s own dev-window choice):
  genuine divergence appears, as expected once `tiltState` has real history to work with.

| | NQ incumbent | NQ B1 | MNQ incumbent | MNQ B1 |
|---|---:|---:|---:|---:|
| Trades | 629 | 593 | 629 | 593 |
| Net incl. comm. | $81,777.56 | $85,474.52 | $7,819.30 | $8,216.10 |

**Fills-log diff (long window):** both NQ and MNQ B1 fills match the incumbent's **exactly**
(byte-for-byte) for the first 175 fill lines, then diverge starting at fill #176 —
**2025-03-18T09:36:00 for both NQ and MNQ, the identical date and fill number** — with entry
timing/price differing but trade structure otherwise consistent (e.g.
`176,2025-03-18T09:36:00,S,...,21071.75,...` incumbent vs `176,2025-03-18T09:39:00,S,...,21011.5,...`
B1 for NQ; the MNQ pair shows the identical 09:36→09:39 shift on the same date). This is exactly
the expected signature of the one-line change (`mm` forced to `1.0` instead of the real
`tiltState`-gated ternary): identical behavior on every bar where the real code's `mm` would
already equal `1.0`, divergence appearing only once the real code's `mm` first evaluates to
`1.25`. The two objects diverging at the *identical* fill index and date independently confirms
they share one decision core exactly as designed (master directive sec19 — no independent MNQ
alpha).

## Secondary comparison: rough sanity check vs. SIMPLE01's Python B1 (not a strict pass/fail, per spec)

Not reconciled to the cent, per the spec's own disclosed caveats (NQ/MNQ ambiguity in the Python
output; Python vs. NT8 Strategy Analyzer fill-timing/slippage convention differences). Directionally
consistent: both show B1 outperforming B_FULL/incumbent over the comparable window in this
particular sample (Python: B1 net $65,400.76 vs B_FULL for 2026-01-01→2026-07-31; NT8: B1 nets
more than incumbent on both NQ and MNQ over 2025-01-01→2026-05-31) — no sign disagreement, no
investigation triggered per the spec's own rule.

## What this proves and doesn't

Proves: the NT8 B1 objects are a correct, minimal, verified implementation of SIMPLE01's frozen
B1 definition — structurally sound, diverges from the incumbent only and exactly where the
construction says it should.

Does not: re-adjudicate B1's historical performance verdict, authorize any protected-pool or
locked-forward data access, or promote anything. Per `B1_FUTURE_CONFIRMATION_SPEC.md` sec10, the
only two paths to resolving B1's remaining INCONCLUSIVE Sharpe blocker are a future locked-forward
monitoring reading or a separately-preregistered protected-pool batch — neither opened here.

## Governance

Spec committed (`0f2e09e`) before this run. Both `.cs` objects committed 2026-08-10 (`12341ab`).
Same NT8 F5-in-editor requirement as EQV04 (see that report). ENGINEERING_ONLY, zero alpha budget.
