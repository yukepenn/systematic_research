# W16_V0_HYGIENE — REPORT

Owner directive: MEGA PROMPT V5 rev2, §6 (W0, blocking) + two mid-turn addenda narrowing
V1 to a broker-fact-driven session-template question. Orchestrator-executed directly
(reads/computation only; no NT8 backtest re-run, no code changes, no order submission).

## V1 / V1a — the actual flatten time per object, empirically measured

Both `SolarWaveOneContractNQ_Final.cs` and `SolarWaveOneContractMNQ_Final.cs` contain a
**primary** forced-flatten branch, byte-identical between the two files:
```
bool entryBlocked = (hm >= 163000 && hm <= 180000);
if (hm >= 163900 && hm < 180000) { tgt = 0; }   // forced flat, decided at 16:39 close
```
`IsExitOnSessionCloseStrategy=true; ExitOnSessionCloseSeconds=30` is present in both files
too, but per the code's own header comment it is a **backstop** for early-close/holiday
sessions, not the primary mechanism. `SolarWaveSMMaster_v2.cs` (Product A master) uses the
same pattern with its own decision bar (16:39 per its header comment) and was already
measured for its 16:42-fill / -5.35% net-cost tradeoff in `MARGIN_1644_FLATTEN.md`.

Reading the code alone cannot tell you whether the primary branch actually **fires and
fills** — for that, the real NT8 trade lists already exported to
`runs/PRODUCTB_ONECONTRACT_FINAL/out/{nt_trades_nq,nt_trades_mnq}.csv` were audited
directly (`src/v1_flatten_audit.py`).

### NQ — compliant

| | value |
|---|---:|
| exits in the 16:00-17:00 ET window | 933 / 1,975 (47.2%) |
| exits clustering exactly at 16:42 ET | 668 |
| exits after 16:45 ET | 16 / 1,975 (**0.81%**) |

The 16:42 spike is exactly what "decided at the 16:39-close bar, fills on the next 3-min
bar" predicts. **The 16 residual late exits are NOT an early-close-backstop pattern** —
they land at scattered, odd, late-evening times (19:57, 20:03, 20:21, 21:03, 21:42, 21:51,
21:54, 22:12 ×2, 22:54, 23:27, 23:30, plus one at 18:39 on 2026-04-07) spread across 2022,
2024, 2025, 2026 — not clustered on the documented US-holiday early-close dates. **Flagged
as an open, unexplained, low-priority residual** (0.81% of trades) — not investigated
further this run; existing NQ parity-PASS is judged not to require a re-run because the
underlying flatten mechanism these 16 trades represent has not changed between the
parity-certified run and this audit (same artifact, same code, no re-run performed — this
audit reads the SAME already-existing trade file the parity check used).

### MNQ — CONFIRMED BROKEN, not a compliant artifact

| | value |
|---|---:|
| exits in the 16:00-16:30 ET window (normal signal-driven exits) | 90 |
| exits in the 16:30-17:00 ET window | **0** |
| exits at exactly 17:00 ET | **1,056 / 1,561 (67.7%)** |

There is a complete dead zone from 16:27 to 17:00 — the 16:39-decide branch never
successfully closes a position in that window for MNQ. The 17:00-exact stamp is consistent
with the `ExitOnSessionCloseSeconds=30` backstop firing at ~16:59:30 and filling on the
3-minute bar that closes at 17:00:00 (NT8 stamps fills at the fill bar's END, documented
elsewhere in this repo). **Conclusion: the coded 16:39 forced-flatten branch computes the
correct target (0) for MNQ — verified by direct code comparison, identical to NQ's — but
the resulting exit order is not filling before the backstop.** Root cause not isolated this
run (candidates: the cross-series order-routing arrangement — signal series index 1 (NQ),
execution/primary series index 0 (MNQ), `SubmitTarget` calls `ExitLong(0, c, "XL", "")` /
`ExitShort(0, -c, "XS", "")` — is structurally the mirror image of
`SolarWaveSMMaster_v2`'s known-good arrangement (signal index 0, execution index 1,
`barsInProgressIndex=1`), and `SolarWaveSMMaster_v1` had a documented bug in exactly this
class of cross-series arrangement (KNOWN_ERRORS #7) that v2 fixed — plausible this is a
related-but-distinct instance, not yet proven).

**Consequence**: `runs/PRODUCTB_ONECONTRACT_FINAL/`'s BEST_ONE_MNQ numbers (net $28,900.70,
Sharpe 0.921, full metric battery, capital map) are real NT8-engine outputs but reflect a
**policy that violates C4** (day-only, flat by 16:45) on two-thirds of its trades. They must
not be presented as the compliant Product B MNQ deliverable until this is fixed and the
object is rebuilt + re-parity'd (satisfies V1c's requirement not to carry over a stale
parity certification — MNQ's was never actually a full PASS in the first place, so there is
no certification being invalidated, but the same discipline applies going forward).

## V1b — origin of "16:39"

`research/operational/day_margin_variant/MARGIN_RULES.md`: "**Flatten deadline with
buffer**: hard external deadline 16:45:00 ET. Recommended internal deadline **16:40:00 ET**
(submit flatten no later than ~16:38 ET) — a 5-7 minute buffer for order routing, partial
fills, and clock skew." 16:39 ET is the nearest 3-minute-bar boundary (bars close on
:00/:03/.../:39/:42...) to that recommendation. **Deliberate safety buffer, documented
before this wave, not an error and not invented this run.**

## V1c (session-template question) — resolved empirically, not just by config-reading

Live NinjaTrader margin pages (fetched 2026-08-09) plus this repo's existing frozen
convention (`CLAUDE.md`: "Sessions 18:00 → 17:00 ET") both confirm the CME Globex 17:00 ET
close is the governing session template — not an RTH 16:00 ET template. The empirical MNQ
17:00-exact exit clustering is fully consistent with a Globex-template backstop firing at
~16:59:30 and filling on the bar closing at 17:00 (not with an RTH-16:00 template, which
would show clustering at 15:59-16:00 instead — it does not). No ambiguity found; reported
both possibilities were checked against data, not inferred.

## V1d — near-cutoff-entry diagnostic

Computed as "entries in the final N minutes before the 17:00 ET session close" (a proxy —
entries are blocked from 16:30 ET onward by `entryBlocked`, so this window in practice only
ever captures entries in 16:00-16:30 ET once N ≥ 30; for N < 30 it is empty by construction
since no entry can be closer than 30 min to 17:00 while still being before the 16:30 block).
Flat commission-only friction proxy (RT $4.36 NQ / $1.30 MNQ, no per-trade slippage
breakout available from this trade-list format — disclosed limitation).

**NQ** (1,975 trades total):
| N (min before 17:00) | count | net P&L | P&L/trade | win rate | friction share |
|---:|---:|---:|---:|---:|---:|
| ≤5/10/15/20 | 0 | — | — | — | — |
| ≤30 | 3 | $10,006.92 | $3,335.64 | 33.3% | 0.001 |
| ≤45 | 17 | $3,030.88 | $178.29 | 29.4% | 0.024 |
| ≤60 | 152 | −$3,977.72 | −$26.17 | 41.4% | −0.200 (net negative denominator) |

**MNQ** (1,561 trades total):
| N | count | net P&L | P&L/trade | win rate |
|---:|---:|---:|---:|---:|
| ≤30 | 1 | −$12.30 | −$12.30 | 0% |
| ≤45 | 6 | −$281.30 | −$46.88 | 0% |
| ≤60 | 98 | −$1,243.40 | −$12.69 | 40.8% |

Small samples (N≤45 has single-digit-to-teens counts for both objects), but the N≤60 cells
(the only ones with real sample size) are **net negative for both instruments** — directionally
consistent with the "pays full friction, no time to work" hypothesis V1d posed, not yet
strong enough (n=152/98) to set a `no_new_entry_after` cutoff. **No cutoff chosen or fit
this run** — the directive's own rule is not to fit until the evidence is in, and this
sample is too thin to choose from confidently. Flagged to revisit once MNQ is fixed (its
diagnostic is currently computed on the broken-flatten trade list and should be re-run
after the fix, since a working flatten changes which trades even reach a forced exit).

## V2 — overshoot ratio r, trailing-120-session window

Same engine as `MONITOR01_PROTOCOL.md` / `monitor01_reading001.md` (theta=179, 1-min causal
sigma, rolling 460 bars, band edges [2.0, 3.0, 4.3, 6.4, 9.4]), window changed from
trailing-4-quarters to trailing-120-sessions (`src/v2_r120.py`).

| band | r (trailing-120-sess) | se | n |
|---|---:|---:|---:|
| (2.0,3.0] | 1.2492 | 0.1174 | 178 |
| (3.0,4.3] | 1.2354 | 0.0616 | 639 |
| (4.3,6.4] | 1.2208 | 0.0368 | 1,597 |
| (6.4,9.4] | 1.2165 | 0.0416 | 1,156 |
| **pooled** | **1.2235** | 0.0246 | 3,570 |

Full-history recomputation (sanity check) reproduces reading #1's pooled r=1.2072 exactly.
**No alarm on any window or basis** (floor is 1.05; every cell is ≥1.20). Note for the
record: the directive states MONITOR-01 was "not recomputed in at least 15 waves" — reading
#1 is dated 2026-08-07, i.e. one day before this directive was authored, not 15 waves —
a premise correction, stated per the directive's own honesty requirements rather than
silently accepted.

## V3 — repo exposure status

`git rev-list --objects --all` on the current repo (branch `main`, the only branch, local
and origin identical per a clean non-force push moments earlier) returns **zero objects**
matching `RenkoKings_SolarWaveRK_NT8.dll` or any `.dll` at all. The original blob-adding
commit hash (`35901db`, per `README.md` §6b) does not exist in local history. Repo object
count (2,542 objects, ~350KB total) is inconsistent with a 4.5MB binary ever having been
present. **Conclusion: the vendor DLL is not reachable anywhere in the current public
repository history.** `README.md` §6b ("CONTAINED, NOT ERASED... has NOT been performed")
is stale — the remediation the old root `NEXT_HANDOFF.md` described as blocked only on the
owner's force-push has evidently already happened and is already live on `origin/main`.
No history rewrite performed or required this run.

## V4a (partial) — live margin/commission verification

`https://ninjatrader.com/pricing/margins/` (fetched 2026-08-09) confirms NQ day/initial
margin $1,000.00 / $43,433.67 and MNQ $100.00 / $4,343.38 — **exact match** to the existing
`MARGIN_1644_FLATTEN.md` figures. `https://ninjatrader.com/pricing/commissions/` confirms
the schedule is dated 2026-07-01 and "updated quarterly" (matching the owner's claim
exactly), and gives generic Lifetime-plan per-side minimums ($0.09 Micro / $0.59 Standard,
broker-fee-only, pre-exchange/NFA add-ons) but the instrument-filtered NQ/MNQ all-in table
did not render through the fetch. **The existing repo convention (NQ $2.18/side, MNQ
$0.65/side, all-in) is neither independently confirmed nor contradicted this run.**
Per the directive's own fallback, this is flagged rather than guessed at — full V4
(friction-share ledger + sensitivity band) is deferred pending either a working fetch or
owner-supplied figures.

## Explicitly not done this run (see spec.yaml `not_in_scope_this_run`)

V1e, V1f, V1g, full V4, V5, O1/O1a, and all of W1-W4.
