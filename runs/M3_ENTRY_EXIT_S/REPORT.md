# M3_ENTRY_EXIT_S — RESULTS

Run against `spec.yaml` (frozen `7565d1d`). Parity assertion (entry_mult=exit_mult=1.0 vs
`sm01_solarsim.member_states`/`member_trades` original, all 13 VolMults): **PASS**. Control
cross-check against the frozen reference curve: **PASS**. Code: `src/m3_common.py`, `src/run.py`.

**Process note**: the first implementation attempt crashed the parity assertion — module-name
collision (`common.py` imported under the same bare name from two different `src/` directories;
Python's module cache silently returned the wrong one) — fixed by renaming the local module. The
fix then *revealed a second, more serious bug the crash had been masking*: the initial port used
`member_trades`'s realized-position array (`pos`) where every other run in this program's
aggregation pipeline (`common.build_pend`, confirmed by reading it) uses the forward-looking
*pending*-position array (`pend_pos`) — using the wrong one would have silently produced a
plausible-looking but structurally wrong result. Caught only because the parity assertion is a
hard `assert`, not a warning. Both fixes are in `m3_common.py` with dated inline notes.

## Headline: CONFIRMED-NOT-BENEFICIAL — a real, mechanically-working effect that is neither
chronologically robust nor a plateau

| cell | Sharpe | ΔSharpe | CDaR | top10 | GATE_A | flips vs control |
|---|---:|---:|---:|---:|---|---:|
| E1.0 X0.75 (tighter exit only) | 0.232 | −0.477 | $36,693 | 66.8% | FAIL | 100% |
| E1.0 X1.0 (control) | 0.709 | 0.000 | $27,162 | 100.0% | — | 100% |
| E1.0 X1.25 (looser exit only) | 0.710 | +0.0003 | $27,161 | 100.5% | pass (negligible) | 100% |
| E1.25 X0.75 | 0.295 | −0.414 | $30,453 | 60.2% | FAIL | 70% |
| E1.25 X1.0 (harder entry only) | 0.628 | −0.081 | $26,639 | 76.8% | FAIL | 70% |
| **E1.25 X1.25** | **0.770** | **+0.061** | **$25,726** | 100.4% | **pass** | 70% |
| E1.5 X0.75 | 0.477 | −0.232 | $24,340 | 59.1% | FAIL | 53% |
| E1.5 X1.0 (hardest entry only) | 0.632 | −0.077 | $22,475 | 73.5% | FAIL | 53% |
| E1.5 X1.25 | 0.695 | −0.014 | $22,798 | 84.5% | FAIL | 53% |

**Tightening the exit alone is uniformly disastrous** (X0.75 column: Sharpe collapses to
0.23–0.48 at every entry level, roughly a third to two-thirds of control) — a tighter stop on
this construction behaves like every other stop-loss-engineering idea this program has closed
(`STOP_OVERLAY_FRONTIER.md`: "Solar's own reversal already acts as a stop"). **Making entry alone
harder (X1.0 column, E1.25/E1.5) also hurts** — Sharpe 0.628–0.632 vs control 0.709, even though
flip count drops mechanically exactly as intended (70%/53% of control's flips — the "harder to
establish a new directional state" mechanism works exactly as designed at the flip-count level).
**Only the single cell (1.25, 1.25) — harder entry AND looser exit together — beats control**, and
by a real margin (ΔSharpe +0.061, CDaR $1,436 better, top-10 retention 100.4%).

## Why this is not a CANDIDATE

**Gate B (chronology): FAILS badly.** Only 2 of 5 years positive (2024: +0.282, 2026 stub: +0.464;
2022: −0.124, 2023: −0.003, 2025: −0.043). The entire gain is carried by one very strong year and
the already-scrutinized 106-session stub; three of five years are flat-to-negative. Does not
survive excising the final 106 sessions.

**Gate C (plateau): FAILS.** Of the best cell's 5 in-grid neighbors, only 1 (E1.0/X1.25 — itself a
near-noise-level cell) shows both Sharpe and CDaR moving the same direction. The other four
neighbors (E1.25/X1.0, E1.5/X1.0, E1.5/X1.25, and implicitly the X0.75 column) are clearly worse.
**This is a single isolated cell on a ridge, not a region** — exactly the pattern directive §6
says to reject ("if the optimum is an isolated cell, reject it").

Per the frozen verdict rule, failing gate B (not gate C alone) means this is **CONFIRMED-NOT-
BENEFICIAL**, not the softer REGIME-LOCAL/ISOLATED-OPTIMUM label reserved for an otherwise-robust
result that only fails the plateau check.

## What this establishes

1. **The entry/exit decoupling mechanism works exactly as mechanically intended** — a higher
   ENTRY_MULT genuinely and predictably reduces flip count (100%→70%→53% as entry goes
   1.0→1.25→1.5) — but the resulting trade-off is not favorable except at one narrow, unstable
   combination.
2. **Tight exits are closed as a direction, joining the existing stop-loss-engineering family** —
   this is a new construction (member-state-machine level, not a P&L-triggered overlay) reaching
   the same conclusion as every prior stop/exit idea in this program.
3. **A capital-map/parity R2 is not warranted** — this result does not clear the frozen bar and,
   per program discipline, no threshold adjacent to (1.25, 1.25) should be fished for a better
   cell; the grid was bounded and preregistered and stays closed at these 9 cells.

No red team required (V7 §G — a clean CONFIRMED-NOT-BENEFICIAL proposes no promotion).
Self-check: parity assertion and control cross-check both independently verified before any grid
cell was scored.
