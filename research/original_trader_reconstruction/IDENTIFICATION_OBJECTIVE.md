# IDENTIFICATION OBJECTIVE — reconstruction-distance score

Central principle (§4): SYSTEM IDENTIFICATION, NOT RETURN MAXIMIZATION. Closer to
Approximate Bayesian Computation / simulation-based inference than strategy optimization.
A candidate becomes credible only when it simultaneously approaches MANY independent
fingerprints. Do not overfit one headline number. Retain the SIMPLEST mechanism that
reproduces many characteristics at once.

## Fingerprint priorities (§11 S7, §32)

PRIMARY (HIGH): trade count, trades/day, win rate, profit factor, avg holding time,
avg winner, avg loser, max drawdown.
SECONDARY (MEDIUM): total net, largest win/loss, long/short split, equity-path shape.

Explicit anti-goal (§47): a candidate with better PnL but wrong count/WR/hold geometry is
a WORSE reconstruction and must not be promoted inside this campaign.

## Tolerance bands (guidelines, not sacred gates — §32)

| Fingerprint | Acceptance region |
|---|---|
| trade count | within ~5–10% |
| win rate | within ~2 pp |
| profit factor | within ~0.05–0.10 |
| avg hold | within ~10–20% |
| avg winner / avg loser | within ~10–20% |
| max DD | within ~15–25% |
| net | within ~10–20% |

## Score definition (frozen for Track S, OTR-S runs)

For window w and fingerprint f with target T_f and replica value R_f:
normalized error e_f = |R_f − T_f| / scale_f, where scale_f = the tolerance band midpoint
above (e.g. trade count scale = 0.075·T). Report the full error vector ALWAYS; a scalar
D = mean(primary e_f) + 0.5·mean(secondary e_f) is used only for ranking, never as a
sole verdict. Complexity is reported alongside (number of free wrapper choices); prefer
lower complexity at similar D (§32: simpler model with slightly worse fit may be more
credible).

## Cross-window discipline (§33)

One frozen rule set per candidate, evaluated across ALL family-associated windows.
Leave-one-window-out / chronological splits / plateau + perturbation checks. If a model
needs different rules every week it is not a reconstruction. Failure windows (esp.
2026-03-22→03-27) carry equal weight to winners.

## Diagnostic iteration (§48)

Mismatch → identify WHICH fingerprint is wrong → generate next mechanism specifically to
explain that mismatch → test. (count low + WR right + hold long → re-entry/event types;
count right + PF wrong + losses big → exit/risk semantics; good weeks match + crash week
doesn't → missing regime exposure.)

## Multiple-testing control (§34)

Every tested hypothesis gets a HYPOTHESIS_LEDGER.csv row (ID, family, code version,
params, reason tested, windows, distance, complexity, result, verdict). No forgotten
losers.
