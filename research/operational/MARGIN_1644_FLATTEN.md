# 16:44 ET Flatten — Margin-Cliff Cost Study & Operating Decision

**Date:** 2026-08-07
**Question (owner):** NinjaTrader reduced intraday margin ends at 4:45 PM ET (3:45 PM CT). MNQ: $100 intraday → $4,343.38 initial; NQ: $1,000 → $43,433.67 (ninjatrader.com/pricing/margins, numbers float with volatility — always use the page's current values at deployment). E10 is exit-on-session-close (17:00 ET), so the ONLY exposure to initial margin is the 15-minute window 16:45–17:00 ET. What does holding through that window earn, and should we flatten at 16:44 instead?

## Preregistered decision rule (declared before the number was read, this session)

Adopt 16:44 flatten as the live-operations default **iff** the 16:45→17:00 window's historical P&L contribution is ≤ 5% of net **or** not statistically distinguishable from zero. If the contribution is significantly positive and > 5%, keep holding to 17:00 and accept the initial-margin capital requirement. A negative window contribution is treated as noise, not advertised as an "improvement" (no re-tuning).

## Measurement

Source: `runs/E10MASTER_V1/out/e10m_v1_bars.csv` (540,232 3-min bars, per-bar physical MNQ position `phys`) joined to `runs/AUDIT03_BARS/nq_3m_2022_2026.csv` closes. Per-bar MTM = pos_prev × Δclose × $2/MNQ. Session-gap bars zeroed (strategy is flat at every session close; `phys` on the 17:00 bar records the pre-exit position, so the naive diff would wrongly carry 1,057 sessions across the overnight gap — corrected). Window = bars stamped 16:48–17:00 ET (covering 16:45→17:00). 2022-01-03 → 2026-07-31.

| Quantity | Value |
|---|---|
| Total intra-session MTM (frictionless, matches E10_round_session daily vector) | $210,830 |
| 16:45→17:00 window P&L | **$6,664** |
| Share of frictionless MTM / of engine after-cost net ($181,079) | **3.16% / 3.68%** |
| Mean per session (n=1,138 sessions with a full RTH close) | $5.86, **t = 1.08 (n.s.)** |
| Worst / best single-session window | −$924 / +$4,640 |
| By year (2022→2026) | $652 / $1,266 / −$556 / $4,172 / $1,131 |
| Sessions holding a position at 16:45 | 89.0% (mean \|pos\| 3.89 MNQ, max 10) |
| Contract-changes inside the window (suppressed under flatten → slightly fewer fills) | 109 total over 4.6 yr |

## Decision: ADOPT 16:44 FLATTEN (both clauses of the frozen rule satisfied)

Cost ≈ $1,460/yr on ≈ $46k/yr net, statistically indistinguishable from zero. What it buys:

1. **Capital floor collapses from initial to intraday margin.** Max position is 10 MNQ (E10 target = round(10×mean) ∈ [−10,+10] — not 13; the 13-cell/13-MNQ figure applies only to the per-member architecture we do not run). Worst-case margin: 10 × $4,343 = $43.4k initial → 10 × $100 = $1k intraday.
2. **The aggressive compounding tiers become margin-feasible.** At $4k-equity/MNQ the ladder was literally infeasible ($4,343 initial > $4,000 equity per contract); at $7.5k it was tight. With flatten, margin never binds at any tier we would consider — the binding constraint reverts to where it belongs: the Kelly/drawdown wall (see sizing discussion, 2026-08-07). Margin relief is NOT a license for more leverage.
3. **Removes forced-liquidation risk.** NT8's risk desk auto-flattens under-margined positions after the cutoff (with a fee, at their timing, not ours). A strategy that self-flattens at 16:44 never meets the risk desk.

## Implementation note (queued, not yet built)

`SolarWaveE10Master_v2` with `bool Flatten1644` (default true): force target 0 on bars stamped ≥ 16:45 ET; no re-entry until next session (automatic — session opens 18:00). Per hot-reload convention the class gets a new name. Requires a validation Analyzer run before designation; queued behind scalping-lab NT8 work. Until then, live deployment does not exist and the analysis above is the ruling record.

Analysis code: inline (this file is the record); inputs are committed artifacts.
