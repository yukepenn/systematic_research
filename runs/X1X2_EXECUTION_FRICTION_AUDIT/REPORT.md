# X1X2_EXECUTION_FRICTION_AUDIT -- RESULTS

Descriptive audit per frozen spec.yaml. Reference: SOLAR_E10 control. Baseline (k=0 extra lag,
1-tick slip, $0.65/side commission): net $119,008.90, Sharpe 0.7092, CDaR₀.₉₅ $27,161.82.
Code: `src/run.py`.

## X1 -- decision-lag degradation: real, and non-monotonic

| extra lag | net | % of baseline | Sharpe | % of baseline |
|---:|---:|---:|---:|---:|
| 0 (baseline) | $119,008.90 | 100.0% | 0.709 | 100.0% |
| +1 bar (3min) | $97,957.70 | 82.3% | 0.581 | 81.9% |
| +2 bars (6min) | $111,901.20 | 94.0% | 0.666 | 94.0% |
| +4 bars (12min) | $78,319.80 | 65.8% | 0.465 | 65.6% |
| +8 bars (24min) | $94,994.70 | 79.8% | 0.543 | 76.6% |

Latency clearly costs edge -- by 12 minutes of extra decision lag, Sharpe is down to 66% of
baseline -- but the decay is **not monotonic** (the +2-bar point partially recovers from the
+1-bar point before falling again at +4). This is a genuine, disclosed finding about the target
series' own autocorrelation structure, not smoothed over: the edge is real and latency-sensitive,
but a simple "smooth decay curve" model of execution risk would be wrong. **Practical
implication: the system needs its already-assumed 1-bar (3-minute) decide-then-fill discipline
to hold; degradation beyond a few minutes of added latency is material (15-35% of Sharpe by
12-24 minutes), not negligible.**

## X2 -- friction stress: graceful, no breakeven found within a generous stress range

| slip (ticks) | net | Sharpe | || comm multiple | net | Sharpe |
|---:|---:|---:||---:|---:|---:|
| 1 (baseline) | $119,008.90 | 0.709 || 1.0x ($0.65) | $119,008.90 | 0.709 |
| 2 | $95,256.90 | 0.568 || 1.5x ($0.975) | $102,770.60 | 0.612 |
| 3 | $72,065.90 | 0.429 || 2.0x ($1.30) | $86,532.30 | 0.515 |
| 4 | $49,421.90 | 0.294 || 3.0x ($1.95) | $54,055.70 | 0.322 |

**Neither axis reaches Sharpe=0 within the tested grid** (up to 4x baseline slip, up to 3x
baseline commission) -- the breakeven-multiple interpolation is reported as "not found" rather
than extrapolated past what was actually tested, per this campaign's standing no-extrapolation
discipline. Joint stress (2-tick slip AND 1.5x commission together, a plausible "thin liquidity"
scenario): Sharpe 0.471, still comfortably positive (66% of baseline). **The edge is not fragile
to the specific $0.65/side, 1-tick friction assumption** -- it degrades gracefully and stays
positive well past any friction level plausible for MNQ's actual liquidity profile.

## Disposition

Both audits complete, no new construction proposed (descriptive per spec). X1's finding
(latency matters, non-monotonically) and X2's finding (friction robustness, no breakeven found
up to 4x slip / 3x commission) both carry forward directly into the final BASELINE_MODELS.md
"what would invalidate this baseline" disclosure. This closes the 8th and final named research
family in the FINAL OPTIMIZATION DIRECTIVE. No red team required (audit, no promotion).
