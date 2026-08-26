# WE_W27 — MIXED-MODEL VOTE · REPORT

Three axes, three negatives, all informative. No improvement adopted.

## A — FALSIFIER FIRED: model concentration is irreducible with our signal library

Non-Solar signals added as **voters** (same 1 contract, zero tail cost by construction) —
the combination W25 never tried:

| vote | voters | trades | weekly | % weeks | worst | **Sharpe** | Solar share of winning votes |
|---|---|---|---|---|---|---|---|
| **PURE SOLAR** | 32 | 2,334 | $1,060 | 59.1 % | −$7,487 | **0.305** | 100 % |
| V_ALL | 38 | 3,134 | $738 | 55.9 % | **−$6,333** | 0.240 | 90.0 % |
| V_PROFITABLE | 36 | 2,562 | $760 | 54.2 % | −$7,160 | 0.231 | 90.6 % |
| V_HALF (model-balanced) | 22 | 2,937 | $732 | 57.4 % | −$6,383 | 0.244 | 82.1 % |

Every mixed vote trades **more** and has a **better tail** — and a much worse Sharpe. The
non-Solar voters add trades that are not as good, diluting the majority. **Model
concentration is therefore a permanent property of this system, not an open problem**, and
belongs in every summary as a stated risk rather than a to-do.

## B — the session profit target is DEMOTED to weak evidence

100 circular shifts of the position path, comparing the target's *gain* on the real path
against its gain on shifted paths of identical shape:

| target gain, real path | null gain mean | null p95 | percentile | p |
|---|---|---|---|---|
| **+0.032** (0.273 → 0.305) | −0.005 | +0.041 | **88.0** | **0.120** |

**It does not clear the 95th percentile.** Under the campaign's own standing rule it is
demoted from "adopted mechanism" to **weak evidence (p = 0.12)** — the same treatment given
to the `signal_wave` gate and the CLOSE-hour drop in W13. It is retained because it improves
four measured quantities at once, but it must never again be described as proven.
*(Note: the session HALT has also never been null-tested; its evidence is that both Sharpe
and tail improve together, which chance rarely delivers, but the test is now owed.)*

## C — the box destroys S1, and the reason is mechanistic

| S1 variant | weekly | % weeks | worst | Sharpe |
|---|---|---|---|---|
| **raw** | $1,388 | 54.1 % | −$20,957 | **0.172** |
| box −1300/+1000 | $279 | 47.5 % | −$10,789 | 0.068 |
| halt only | $433 | 46.6 % | −$10,789 | 0.072 |
| target only | $852 | 56.1 % | −$20,957 | 0.141 |

S1 already carries the **D-gate**, which is itself a session-level risk control. Adding the
box double-truncates the same process and destroys the sleeve. This is confirmation from the
opposite direction that the D-gate and the session box do the same job.

## D — the best object is unchanged

| portfolio | weekly | % weeks + | % days + | worst | Sharpe |
|---|---|---|---|---|---|
| **E5box + S1 raw + short box** | **$3,030** | **64.9 %** | 52.7 % | −$23,374 | 0.285 |
| E5box + S1 box + short box | $1,920 | 56.1 % | 48.6 % | −$16,682 | 0.275 |
