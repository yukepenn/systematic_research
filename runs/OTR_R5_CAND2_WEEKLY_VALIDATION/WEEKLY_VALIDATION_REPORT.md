# OTR_R5 — CAND2 vs the 28 late-2025 weekly fingerprints (2026-08-24)

Version-aware, full-fingerprint validation per directive v3.0 §2-§4. Matrices:
`out/WEEKLY_FINGERPRINT_MATRIX.csv` (29 metrics × 12 variants × 28 windows + targets),
`out/WEEKLY_ERROR_MATRIX.csv` (§40-weighted normalized errors). Raw trade streams:
`out/trades_*.json`. No parameter was tuned in this run.

## Headline: the residual is MACHINE-correlated, not era-correlated

The weekly reports come from two machines (target CSV `notes`): **hp** and **dev**.

| group | mean Δn | mean \|Δn\| | mean \|Δhold\| | n |
|---|---|---|---|---|
| **dev, CAND2 noDM** | **+6.6%** | **11.1%** | **6.8 min** | 9 |
| dev, +literal D/M halts | −27.6% | 29.3% | 11.8 | 9 |
| hp, CAND2 noDM | +39.5% | 41.8% | 18.2 | 19 |
| hp, +literal D/M halts | +13.5% | 30.0% | 23.9 | 19 |

- **CAND2 (noDM) generalizes to every dev-machine week at ±7% mean count error**
  across BOTH parameter eras — 9 windows, all fully out-of-sample w.r.t. CAND2's
  identification data (2023-01→2025-02 master + Jan-2023 labels). Best weeks:
  10/26 (n 50/50, net −3,310 vs −3,330, dist 0.153), 11/23 (60/64, −15,405 vs
  −15,365, dist 0.149), 1/4/2026 (66/52 noDM; 51/52 with DM, dist 0.121).
- **hp-machine reports are a different build/strategy instance**: 20-70% fewer
  trades than the raw CAND2 stream, longer holds, larger average winners
  (Δavg_win up to −510), and the two +$18.5k trend weeks (11/2, 11/16 — both hp)
  that CAND2 misses by −20k/−25k net. EV-035 (author: several strategies run
  simultaneously) makes a per-machine build split natural.

## Verdicts (preregistered questions)

1. **D/M literal semantics (M=+2000 profit halt / D=−4500 loss halt on session
   cum): REJECTED for the dev/CAND2 build** (over-suppresses, −27.6%);
   **partially explanatory for hp** (+39.5%→+13.5%) but erratic per-week
   (72.7% one week, −29.7% another) → hp suppression is NOT literally (2000,4500),
   or hp posts a different strategy. OPEN, evidence recorded.
2. **A3-A5 retune (5/10/10→3/6/9) is INVISIBLE to a T1-flip-only model** — the
   `old` and `new179` streams are bit-identical (A3/A4/A5 only drive T2/T3/weak
   states). Yet the trader retuned them on 11/7 — strong evidence his build has an
   **active pullback (T2-class) layer** whose frequency those params control.
   Directly supports the master-residual interpretation (+247 trades = sparse
   signal layer). A2 179→180 changes the stream only marginally (dist 0.346 vs
   0.341 era-B mean — inconclusive on its own).
3. **Stop 65→75 reading corrected**: exact −1,300.00 largest-loss rows persist in
   targets through Dec/Jan (11/9, 12/14, 1/18 weeks) while −1,500.00 exact appears
   1/4 week (long −1300 / short −1500) — so the St-group row that changed 65→75 on
   11/14 (row 3) is NOT the same field as row 1 (Initial 65). Initial ≈65 pts
   likely persisted; the 75 belongs to a second stop-tier field (row-3 "I…"),
   semantics OPEN (short-side-specific? second-unit? re-entry stop?). Era-B
   targets show LL>1300 mostly on the SHORT side (−1410/−1490/−1500/−1385) while
   longs cap at −1300 — a directional-stop hypothesis worth one focused test.
4. **Version-aware era assignment carries little signal at the T1 level**
   (expected, given (2)): era-B distance means 0.340-0.346 across all param sets.

## §4 error-shape classification

- hp ERA_A weeks: Δn≫0, Δhold<0, Δavg_win<0 → **missing entry gating/suppression
  + winner extension** in that build (not stop semantics: LL matches at −1300).
- dev weeks: counts/holds/LL fit; small negative Δnet on most weeks (−3.4k..−5.2k)
  → CAND2 lacks a thin extra-edge layer, same signature as the master −27k.
- 12/21 Christmas week (hp): tgt 9 trades vs sim 17 — holiday stand-down evidence.
- 1/18 week: expected undercount from entries/direction=2 change NOT observed
  (sim −6.6%) — either the setting rarely binds or it offsets other churn.

## §51 answers (this pass)

**A. How well does CAND2 generalize?** On dev-machine windows: ±7% mean count
error, holds within ~7 min, LL structure correct, several near-cent weeks — PASS
at band edge. On hp-machine windows: does NOT match; those reports belong to a
sibling build with stronger suppression and longer winners.
**B. Which weeks/metrics fail?** 11/2 and 11/16 (both hp, both +18.5k): net
missed by −20k/−25k with avg_win far too small — winner-riding mechanism absent.
12/7 and 1/4 dev weeks: +25% count (churn segments). Short-side LL>1300 rows
unexplained by a 65-pt stop.

## Limitations
Resume latch not simulated (no early-close-evening arms material here); NT8
trades_per_day convention unverified; hp/dev classification rests on audited
`machine` annotations in per-image records. The machine split is partly
CONFOUNDED with era (ERA_A is 14 hp / 1 dev) and with week character: 10/26 is
an hp week that fits CAND2 almost exactly (dist 0.153), and 12/21 is a holiday
anomaly — so "hp = sibling build" is the leading hypothesis, not a proven
partition. Within-ERA_B contrast (hp |Δn| ~31% vs dev ~11%) is the cleanest
supporting evidence.
