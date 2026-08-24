# TRACK V — Volume/VWAP family report (proxy passes closed 2026-08-23)

**Classification (directive §40): V-EXACT = BLOCKED BY MISSING DATA. V-PROXY =
BEHAVIORALLY MATCHED — PARTIAL / MECHANISM UNIDENTIFIED (architecture-level match only).**

## Proxy identification result (3 bounded passes, frozen success rule met on pass 3)

Winning proxy interpretation `PREV|T_LVL|X_MED|C2` (D=2.431 vs frozen success line 5.203):
**breakout of the PREVIOUS completed hour's volume-percentile ladder (P75 up / P25 down),
in the direction of the EMA20 (1m closes) trend, entry only if the close is NOT extended
more than 10% of the ladder depth beyond the line, exit on close crossing the ladder
median (P50), ≤3 signals per trend, ≥5 bars apart, session-close flat.**

vs identification window A (2026-05-10→22, confirmed-parameter screenshot):

| Fingerprint | Target | Proxy | Verdict |
|---|---|---|---|
| Trades | 183 | 189 | ✓ +3.3% |
| Trades/day | 18.3 | 18.9 | ✓ |
| Net | −$4,055 | −$5,445 | ✓ sign+magnitude |
| PF | 0.95 | 0.918 | ✓ |
| Avg hold | 39.8m | 36.1m | ✓ −9% |
| Avg win | +$1,236 | +$1,083 | ✓ −12% |
| Avg loss | −$784 | −$497 | ✗ −37% |
| Win rate | 37.7% | 29.6% | ✗ −8.1pp |
| Max DD | −$12,700 | −$15,445 | edge +22% |

Structural findings: the RUNNING intra-hour ladder is falsified (churn: 600-750 trades,
2-15m holds); the ladder must be effectively STATIC per anchor period; ladder-line exits
at the median reproduce the 40m hold geometry; the hourly-EMA20 slow-trend reading
(T_H1) is falsified for window A (turns the week strongly profitable — wrong sign).

## Honest limits

- WR −8pp with avg-loss too small: the proxy takes more tiny losers — consistent with
  the missing bid/ask-real-volume information changing ladder placement, or an
  unidentified stop/scratch rule. NOT resolvable at proxy level.
- Cross-window (report-only): W20260308 sign ✓ (+5,690 vs +9,325); **W20260322 (crash
  week) sign ✗ (+4,655 vs −42,235); W20260419 sign ✗ (−8,865 vs +9,215).** Either the
  proxy is wrong in those weeks or those weeks belong to a different family (B) — family
  membership of March/April weeks is UNKNOWN (only windows A and B have confirmed V
  parameters). Unresolvable with current evidence; recorded, not excused.
- Per §17: this is NOT the exact algorithm. "VWAP Amount = 5", the exact ranked
  distribution, and the true close-threshold semantics remain Class D.

## What would upgrade this

Bid/ask-classified volume for window A (NT8 cache re-export — CrossTrade excluded this
campaign; escalation-gated), or window B after LOCKED_FORWARD clears via governance.

Artifacts: runs/OTR_V1_PROXY, OTR_V2_PROXY_PREVHOUR, OTR_V3_PROXY_FINAL
(sweep_results.json + scorecard.csv each). Ledger rows OTR-V1..V3.
