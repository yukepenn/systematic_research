# ZBMACRO01 — FROZEN ENGINE (FT0) — G3_ZBMACRO_FT_20260906 (ledger G00083)

**Status: FT0 FROZEN.** Licensed by G00079 (`runs/G3_ZBMACRO_ENGINE_20260906/`, ledger PASS,
FROZEN-READY). The text below is the FT0 engine **verbatim from the committed spec**
(`runs/G3_ZBMACRO_FT_20260906/spec.yaml`). ANY deviation later = new class name +
re-certification.

## FT0 — the engine, verbatim

- **name:** ZBMACRO01
- **calendar:** NFP_DAY / CPI_DAY per GENESIS_H2_CALENDAR_20260828 (BLS schedule; maintained as
  a calendar CSV — an OPERATIONAL DEPENDENCY documented in the packet)
- **signal:** r1 = close(08:45) - close(08:30) on ZB 1-min (END-stamped, ET). Trade iff r1 < 0.
- **action:** SHORT k=2 ZB filled at the close of the 08:46 bar (one full minute of latency
  charged in research); EXIT buy at the 15:00 bar close. No overnight. No other conditions.
- **cost_basis:** MODELED ALL_IN $66.86/RT PRIMARY, $129.36 STRESS.

## Binding riders (travel with every quote of this engine)

1. **n=40 tail-carried fragility statement** (skeptic Lens 2, G00079, verbatim in substance):
   the single most likely way this is nothing is a tail-carried n=40 object below its own
   80%-power MDE (|mean| 0.1777 pt < MDE_80 0.2641 pt), drawn from the G00067 event-screen
   family — three good CPI mornings in 2023 doing 66% of the work, the rest near noise. Every
   passed clause is a point-in-time in-sample statement on the same consumed substrate. This
   risk is IRREDUCIBLE at n=40 and is discharged only by forward trades.
2. **Forward chronology monitor (KILL rule, preregistered here for the FT stage):** maintain
   the cumulative FORWARD after-cost mean at the executable 08:46 entry; evaluate at every
   10th forward trade; **KILL if at n_fwd >= 20 the cumulative forward after-cost mean <= 0**;
   REVIEW (owner packet) if at n_fwd >= 10 it is below -$100/ct. At ~11 trades/yr the kill
   point arrives in ~2 years — this is not a fast-falsifying object.
3. **Regime label: REGIME-ADJACENT (2023+ inflation-attention era).** Regime indicator:
   rolling median |r1| over the trailing 12 events vs the sample median (0.656 pt on the 40);
   a sustained fall below HALF that level says the conditioning regime has left.

## Evidence status

Every number above is **DISCOVERY_CONSUMED** (G00072 → G00078 → G00079 chain on the sealed
2022-12-27..2026-07-31 substrate). Nothing here is forward evidence. The engine's own numbers
at the executable entry (08:46, PRIMARY cost): net **+$186.3/ct**, CI95 [+44.8, +432.4],
STRESS +$123.8/ct; k=2 ≈ **$4,148/yr** on ~11.3 trades/yr; weekly-vol Sharpe 0.91 (k-invariant).

## What this run adds (offline FT stages only)

FT1 clean-room reproduction (`src/ft1_repro.py`, bar: 40/40 dates exact, fills < 1e-9 pt);
FT4 NinjaScript class **written in this run directory only** (`src/ZbMacroResponse_v1.cs` —
never copied to any NinjaTrader directory by this run); FT4b offline certification
(`src/ft4b_cert.py`, 923-session replay, 100.000% agreement + zero phantom entries required);
FT9 safety audit (REPORT.md); FT10 deployment packet draft (`DEPLOYMENT_PACKET.md`).
NT8 compile / Strategy Analyzer parity / enablement are DEFERRED to the ≥2026-09-21 window
and are owner actions.
