# Type-0 attribution — summary

_Full report: [`research/01_diagnostics/TYPE0_ATTRIBUTION_REPORT.md`](../research/01_diagnostics/TYPE0_ATTRIBUTION_REPORT.md)_

**`Signal_Trade = 0` is not a signal.** It means no event on that bar. The wrapper's
`EntrySignalType = 0` is a different thing — *first non-zero signal while flat wins* — a
path-dependent state machine, so `PnL(Type 0) ≠ PnL(T1) + PnL(T2) + PnL(T3)`.

## Result

| architecture | status | net | Sharpe | max DD | worst year |
|---|---|--:|--:|--:|--:|
| **C0** raw first-signal-wins | run (Wave 1, analytic slip-1) | ≈$123k | — | — | — |
| **C1** Type-1 core | run | $180,479 | 0.784 | −$53,689 | +$7,796 |
| **C2** + one Type-3 re-entry | **REJECTED** | $233,628 | 0.862 | −$47,413 | +$19,801 |
| **C4** + Type-2 or Type-3 | run | $141,303 | 0.450 | −$64,621 | +$9,988 |
| C3 / C5 / C6 | **NOT BUILT** | | | | |

- **Raw Type-0 loses to the Type-1 core it contains** (≈$123k vs ≈$162k). A cheap Type-2 occupies
  the position and displaces the Type-1 flip that would have caught the whole trend.
- **C2 had the best point estimates in the campaign** — better return *and* drawdown *and* worst
  year — and was still rejected: block-bootstrap P(mean ≤ 0) = 0.115, and its sign **flips** on an
  adaptive core (ΔSharpe −0.402, P = 0.879). An effect that reverses when the core changes is an
  interaction, not an edge.
- **C4 is decisively worse** — adding Type 2 costs 0.33 Sharpe, confirming Wave 1's "unconditional
  Type 2 is cost-fragile" from an independent direction.
- **Wave-index conditioning**, the last available selector, gave 0.54–0.93 non-monotone in the
  engine despite a clean monotone Python screen ($26 → $53 → $76 → $151 by wave). No usable signal.
- **C3, C5, C6 were never implemented** — reported as not-run, not as failures. With Type-2 dead
  (C4) and the wave selector dead, they had no remaining mechanism to test.

**The Type-1 core stands alone. Signal arbitration is closed.**
