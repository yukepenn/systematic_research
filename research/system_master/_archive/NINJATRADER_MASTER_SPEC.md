# NINJATRADER_MASTER_SPEC — Single Master Strategy Architecture

_2026-08-08. One consolidated NinjaScript strategy; no competing account strategies.
The Python twins of every component are SM01/sm_bmom-certified; Analyzer parity is
deterministic engineering per the E10Master precedent (0/540,232 bar diffs)._

## Architecture

```
virtual SOLAR engine (13 × V3 members, verbatim E10Master_v2 state machines)
      → integer base target T = round(10 · mean pending member pos), clamp ±10
virtual TILT layer: daily SMA50 state (session closes, prior session, causal)
      → T' = clamp(round(T · m · 0.9026), ±13), m = 1.25 if sign(vote)==state else 1.0
virtual BMOM engine (frozen W8-1: 14d slot bands + RTH VWAP; ±1 NQ ≡ ±10 MNQ units)
virtual B1 engine (long 16:45→09:30, 1 NQ ≡ 10 MNQ units)
allocator (frozen weights, MNQ contract space, dev-frozen scales):
      target_MNQ = round( w_s·T′ + w_m·0.6588·10·B_mom + w_b·0.8270·10·B_1 ) · f
      with (w_s, w_m, w_b) = (0.5·1.431·0.9904⁻¹-composited…) — see arithmetic note
      → ONE net-change MNQ order engine, 16:44 flatten on the Solar/BMOM legs,
        B1 leg exempt from the flatten (it IS the overnight position), 17:00 backstop
```

**Arithmetic note (binding).** The research portfolio is defined on daily P&L with
dev-frozen scalars: P = 1.431·[0.5·(0.9904·TILT) + 0.3·(0.6588·BMOM$) + 0.2·(0.8270·B1$)].
In contract space this is EXACTLY: Solar-leg contracts = 0.5·1.431·0.9904·T′ ≈ 0.7086·T′;
BMOM-leg = 0.3·1.431·0.6588·10 ≈ 2.83 MNQ; B1-leg = 0.2·1.431·0.8270·10 ≈ 2.37 MNQ.
Master target = round(0.7086·T′) + round-to-signed(2.83)·B_mom + round(2.37)·B_1 with
the rounding tracking error measured in the parity run (E10 precedent: rounding cost
≈ 9.4% of theory net; the parity gate is corr ≥ 0.998 and net ≥ 80% of the Python twin).
The global multiplier f scales all three legs (LEVERAGE_FRONTIER: f=0.5-equivalent
for P(DD25)≤5% on $100k; on other capital bases scale f linearly).

## Components already engine-proven

- F1 core: `src/ninjascript/SolarWaveE10Master_v2.cs` — Analyzer-runnable, parity
  0/540,232 vs audited simulator, costs to the cent. RUNNABLE TODAY.
- F2 delta on that file (~40 lines): per-session close ring buffer (50), prior-session
  SMA state, target transform T→T′ (constants above; TiltRescale=0.9026 frozen).
- BMOM virtual engine: per-3-min-slot trailing 14-day |close−open0930| means (needs
  per-slot ring buffers keyed by bar time-of-day, prior-days-only update at session
  end), RTH VWAP accumulator reset at 09:30, signal/flip/1557-closeout logic —
  certified constants in `src/analytics/sm_bmom.py` (1,333/1,333 reconciliation).
- B1 virtual engine: entry at the 16:45-stamped bar close, exit next session's first
  bar ≥09:30 (close), trivial.

## Parity protocol (before any operational use)

1. Compile master; run Analyzer 2022-01→2026-07 on NQ 09-26 3-min (signals) + MNQ
   execution series, Lifetime commissions, 1-tick slip, Standard fill.
2. Export per-bar leg positions + fills (AuditBarExport pattern); diff against the
   Python twin: leg positions exact; daily corr ≥ 0.998; net within rounding budget.
3. Freeze as `SolarWaveSMMaster_v1` (HOT-RELOAD rule: version the class name).

## Variants to expose as parameters

`WSolar/WBmom/WB1` (default 0.5/0.3/0.2; 1/0/0 = F1-F2-only "best simple" mode),
`TiltEnabled` (F1 vs F2), `GlobalF`, `Flatten1644` (Solar/BMOM legs), `B1Enabled`
(disable → fully flat overnight, day-margin eligible).
