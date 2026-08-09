# V1R4_NT8_PARITY -- RESULTS: NOT CERTIFIED, blocked by tooling + one material open discrepancy

**Status: INCOMPLETE / NOT CERTIFIED.** Full multi-year parity for the 3 current objects could
not be completed this wave. This is reported honestly rather than forced to a false PASS, per
the addendum's own "no unexplained failures" rule -- the failure here is disclosed, its likely
partial cause is identified, and the remaining work is scoped for a follow-up.

> **UPDATE 2026-08-09 (same-day continuation, after the owner restarted NinjaTrader) -- the
> "material open discrepancy" below is RESOLVED as a warmup-state artifact, not a defect.**
> The original Q1-2025 spot-check ran NT8 fresh-starting at 2025-01-01 (zero prior tilt/B-MOM-
> band history) against a Python twin built from full 2022+ continuation state -- an
> apples-to-oranges comparison. A warmed-up re-test (NT8 running continuously from 2024-04-01,
> 9 months of warmup, far exceeding the 50-session/14-day state requirements) converges to
> within **0.71%** of the Python continuation-state figure for Product A -- clearing the 1%
> tolerance. BEST_ONE_NQ/MNQ improve substantially too (trade counts now match almost exactly,
> 106 vs 107) but retain a smaller, un-root-caused ~15-19% residual. Full certificates, per
> object: `PRODUCT_A_CERTIFICATE.md` (CERTIFIED, spot-check window), `ONE_NQ_CERTIFICATE.md`
> and `ONE_MNQ_CERTIFICATE.md` (both NOT CERTIFIED, open residual documented). The long-job
> CrossTrade<->NinjaTrader session/result-retrieval limitation described below is CONFIRMED to
> persist on the freshly-restarted NT8 instance (same failure mode before and after restart) --
> it is a genuine bridge characteristic for jobs beyond ~20-25s of NT8 compute, not a stale-
> connection artifact, and full multi-year certification remains open for that reason alone.

## What blocked the full run: a reproducible MCP session-expiry ceiling

`RunStrategyBacktest` against the full canonical dev window (2022-01-01 to 2026-05-29, ~1,130
sessions, 2-series strategies) is a genuine async NT8 Strategy Analyzer job. Confirmed working
end-to-end on a **short** job (`SolarWaveRKReplicaV0`, 1 week, 1 series): job completed in 72ms
and its full trade list/performance object was retrieved cleanly on the very next poll --
proving the mechanism, the instrument string (`NQ 09-26` -> resolves to `NQU6`), and the
commission template (`NinjaTrader Brokerage Lifetime`) are all correctly configured.

For the full multi-year, 2-series objects, every attempt hit `MCP server "crosstrade" session
expired` on `GetMcpJob` once the job's elapsed time passed roughly 30-40 seconds -- reproduced
4 times, including with continuous back-to-back polling (no added delay) and with an immediate
reconnect-then-repoll. `GetMcpCapabilities` always succeeds and reports `active_jobs: 0`
afterward, indicating the job's tracking handle is lost on the session churn, not merely slow to
answer. This is a session-management characteristic of the MCP bridge in this environment for
jobs that run longer than its apparent stability window, not a defect in the strategy code, the
request parameters, or something fixable by retrying the same call pattern again.

**Not attempted as a workaround:** splitting the multi-year window into shorter NT8 sub-period
calls to dodge the ~30s ceiling. These strategies carry real causal state across the whole
window (460-bar sigma, 50-session tilt SMA, 14-day B-MOM band) that only builds up correctly
from a single continuous `from` anchor -- an artificially short `from` window would silently
change the object under test, not just work around a client-side limitation. That is exactly the
kind of substitution this campaign's discipline prohibits.

## What DID complete: a Q1-2025 spot-check on Product A, and it does NOT pass

A shorter (~3-month) `SolarWaveSMMaster_v3` backtest over 2025-01-01 to 2025-03-31 completed
successfully:

| | NT8 Strategy Analyzer (real) | Python twin (`SMV2M_MASTER_BUILD/twin.py`) |
|---|---:|---:|
| Net profit | **$9,047.80** | **$11,781.50** |
| Trades / fills | 1,020 (TradesCount) | 1,417 (individual fills, not directly comparable to TradesCount) |
| Commission | $1,487.20 | (MNQ $0.65/side assumed) |

**Discrepancy: $2,733.70, ~23% relative to the Python figure -- well outside this run's own
pre-registered 1% tolerance.** This is reported as a genuine FAIL on this sub-period, not
smoothed over.

## A plausible, partially-identified cause -- not yet confirmed as the full explanation

The Python twin used for this comparison (`SMV2M_MASTER_BUILD/twin.py`) implements the
**pre-C4-fix hardcoded-clock** ops rule (`hm >= 163000` / `hm >= 163900`), not `_v3`'s
session-relative rule (`sessionEnd - 30min` / `sessionEnd - 21min`). `runs/W17_C4_COMPLIANCE/
REPORT.md` documents that **2025-01-09** (the National Day of Mourning) was a CME early-close
session ending at **09:30 ET** -- squarely inside this Q1-2025 window. On an abbreviated session
like that, the hardcoded clock's `hm >= 163000` condition never becomes true (the session ends
at 09:30, long before 16:30), so the Python twin's entry-block/forced-flat logic never engages
for that session at all, while `_v3`'s real session-relative logic correctly restricts new
entries and forces flat around 09:09-09:00 ET on that session. This is a mechanistically sound,
disclosed CANDIDATE explanation for at least part of the gap -- but no bar-by-bar or session-by-
session reconciliation was performed to confirm it accounts for the FULL $2,733.70, and other
contributors (commission-rate rounding, fill-price differences on the abbreviated session, or a
genuine second defect) have not been ruled out.

## Disposition: NOT CERTIFIED, root-cause open, does not block the rest of the campaign

Per spec.yaml's pre-registered disposition rule, this does not clear its own tolerance and is
**NOT CERTIFIED**. Per the addendum, Track E's parity item does not block Track R (already fully
closed this wave) or the final-selection/repo-consolidation work that follows -- V1-R4 is
carried forward as an explicit, disclosed open item for the next session with tool access to a
more stable NT8 bridge (or a chunked/patched polling approach), with a concrete first diagnostic
step already identified: **re-run the Q1-2025 comparison excluding 2025-01-09, and separately
build a proper `_v3`-exact Python twin (session-relative flatten, not the hardcoded v1 clock)
before re-attempting full-window certification.** No object's shipped status changes because of
this open item -- none of the 3 objects was ever claimed certified before this run, and this
run's finding is consistent with, not a new regression against, that pre-existing "not certified
(V1-R4 open)" status in `FINAL_CAMPAIGN_BASELINE.md`.
