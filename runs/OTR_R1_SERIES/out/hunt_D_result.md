# FAMILY D result — risk/equity wrapper with hysteresis

Script: `hunt_D.py` (self-consistent gate replay over the base T1+reverse trade legs;
legs are independent of the gate — an entry gate only removes legs — so replay over the
base trade list with self-consistent equity state is exact).
Base: `WrapperPolicy(comm_side=2.09, entry_types=(1,), reverse_on_flip=True)` on
`t2_canonical_1m.csv` = 5403 trades, net 216,890.46 (cached in `hunt_D_base_trades.json`).

## BEST RULE (passes ALL 42 HARD labels)

State is keyed to the TRADING SESSION (resets at the 18:00 ET open). Realized basis;
a trade's PnL enters the state at its exit FILL bar (a reversal exit therefore counts
in the state seen by the entry that fills on the same bar).

```
per session: cum = 0; high = 0; consec[L] = consec[S] = 0
prior = realized net of the PREVIOUS session (self-consistent, i.e. of taken trades)

on each candidate entry (dir d, session-open-age m minutes, time-of-day tod):
  BLOCK if m < 3                                   # session-open guard (first 2 bars)
  BLOCK if m <= 360 and prior <= -C                # evening rule: after a red day,
                                                   # no entries 18:00 -> midnight
  if high >= X and tod >= 12:00:                   # "armed": day has been up >= X
      BLOCK if cum < 0                             # gave the green day back -> stop all
      BLOCK if consec[d] >= K                      # K straight losses on side d -> stop d
  else TAKE

after each taken trade: cum += pnl; high = max(high, cum);
                        consec[d] = consec[d]+1 if pnl<0 else 0
```

Chosen constants: **X = $1600, K = 3, C = $1000** (guard = 3 min, evening window = 360 min).
Label-feasible ranges (Jan evidence cannot narrow further):
X ∈ (1536.56, 1937.46]; K ∈ {2,3,4}; C ∈ (300.16, 1328.52]; evening window end ∈ (23:36, 02:52].
Hysteresis is implicit: once blocked, no trades occur, so the state freezes and the
block latches until the session reset (or until midnight for the evening rule).

## Per-label scorecard (X=1600, K=3, C=1000)

HARD 42/42 PASS. Attribution of every HARD skip:

| label | verdict | fired by |
|---|---|---|
| 01-03 skip L@12:37 | PASS | ARMED_DIRCONSEC (L had 4 straight losses; high 2486.64) |
| 01-03 skip L@13:28 | PASS | ARMED_DIRCONSEC (latched) |
| 01-03 take S@12:48, S@16:04, S@09:47, L@21:39 eve | PASS | shorts never hit K; cum stayed +79.02 > 0 |
| 01-05 skip S@21:07, L@23:36 (prev eve) | PASS | EVE_PRIOR_RED (01-04 session red) |
| 01-05 take S@02:52 .. L@11:47 | PASS | evening rule expires at midnight; 11:47 < noon |
| 01-05 skip S@12:21, L@13:24, S@14:16 | PASS | ARMED_RED (high 1937.46, cum −30.08 < 0) |
| 01-09 skip L@18:02 (Sun eve) | PASS | OPEN_GUARD (2nd minute of session) |
| 01-09 take S@02:42, L@04:27, S@12:46 | PASS | at 12:46 cum=+2316.64>0, S consec=1 |
| 01-10 / 01-11 take-all | PASS | high < X on 01-10 (1419.92); nothing fires |
| take L@21:39 on 01-02 eve (counter-example) | PASS | fresh session, high=0, not armed |

Critical interlock (raises confidence): skipping S@21:07/L@23:36 is REQUIRED for the
01-05 armed rule to fire — if those evening losers are taken, session high never
reaches X and 12:21/13:24/14:16 are wrongly taken. The evening rule and the armed rule
only work together, self-consistently.

SOFT 1/7: passes skip L@19:17 (01-12 eve, via evening rule). Fails the 01-04
FOMC-minutes cluster (5) and 01-12 L@13:39. NOTE: the 01-04 cluster is provably NOT a
time-window or monotone-equity phenomenon — S@14:04 (EPS TAKE) sits inside the skip
cluster (skip 13:25, take 14:04, skip 14:07/14:11/14:18/14:25), and the equity path is
monotone-worse at 14:04 than at 13:25. Tested an FOMC 13:00–14:30 calendar block: it
wrongly kills S@14:04 and cascades into 7 HARD failures via the changed session net —
refuted. The cluster pattern is exactly what slightly time-shifted signals (late
pullback mode) would produce; it does not look like a risk gate.

EPS 77/78: single failure = S@20:36 on 01-12 evening (wrongly skipped by the evening
rule; prior session −2956.88). Any monotone prior-day-PnL rule that blocks the 01-04
evening (−1328.52, HARD skips) and allows the 01-03 evening (−300.16, EPS take) must
also block 01-12's evening. A non-monotone band rule (block only −350 > prior > −2000)
would take both 01-12 evening trades (trading the SOFT 19:17 pass for the EPS 20:36
pass) but is fragile: it fails when the unreproduced 01-04 cluster losses push the
simulated prior net below the band. The 01-12 evening (skip L@19:17, take S@20:36 after
a −2957 day) is not resolvable by any per-day equity rule; direction-state carry-over
also fails (S was the much worse side that day, yet S was taken).

Missing −274.18 trade (01-16 eve short): NOT produced — the base signal stream cannot
generate it; it requires PullbackEarly=FALSE regenerated signals (outside family D).

## Master aggregate (2023-01-01 → 2025-02-02, $2.09/side)

| | trades | L/S | net | WR% | PF | DD | hold (L/S) | maxW | maxL |
|---|---|---|---|---|---|---|---|---|---|
| TARGET | 4351 | 2166/2185 | 292,172.82 | 40.29 | 1.18 | −32,677 | 94.15 (105.85/82.56) | 7705.82 | −4449.18 |
| base | 5403 | — | 216,890.46 | — | 1.132* | — | 96.24 | 7705.82 | −4449.18 |
| **D best (X1600,K3,C1000)** | **5008** | 2480/2528 | **244,266.56** | 39.84 | 1.127 | −29,077 | 92.81 (105.21/80.65) | 7705.82 | −4449.18 |
| D alt (K2,C1000) | 4909 | 2434/2475 | 227,890.38 | 39.76 | 1.12 | −28,873 | 93.62 (106.12/81.33) | 7705.82 | −4449.18 |
| D alt (K3,C500) | 4979 | 2470/2509 | 239,932.78 | 39.85 | 1.125 | −29,077 | 90.43 | 7705.82 | −4449.18 |

Best config removes 395 of the ~1052 excess trades and recovers +27.4k of the +75.3k
net gap; hold-time split (105.2/80.7 vs target 105.9/82.6) moves onto target almost
exactly. Direction mix stays balanced like the target. K=3 dominates K=2/K=4 on master
closeness at identical label score.

## Honest assessment

- The 42/42 HARD fit is real and the three sub-rules each carry multiple independent
  labels; the armed/evening interlock is a strong structural sign. But the rule was fit
  on ~20 sessions; X, K, C are only interval-identified, and the armed-noon rule fires
  on few Jan days (01-03, 01-05 do most of the work). Overfit risk is material.
- The razor-thin discriminations the rule relies on (cum +79.02 vs −30.08; X between
  1536.56 and 1937.46; C between 300 and 1329) are exactly reproduced, which is
  encouraging, but they would also be reproduced by MANY nearby formulations
  (e.g. "cum ≤ 0", X = 1750, points instead of dollars).
- Master gap: ~650 excess trades and ~48k net remain. The residuals (01-04 cluster
  incl. an inside-cluster take, 01-12 13:39, 01-12 evening asymmetry, and the missing
  late-mode T2 short) all point the same way: the trader's SIGNAL STREAM differs from
  our EARLY-pullback ledger (his panel hard-codes pullback mode; the missing trade is
  late-mode). I estimate family D explains the risk-wrapper layer but roughly half of
  the trade-count gap belongs to the signal-mode family, not to equity gating.
- Recommend: re-run this exact gate on a PullbackEarly=FALSE regenerated ledger before
  judging the master aggregate.

*base PF from full fingerprint of cached run.
