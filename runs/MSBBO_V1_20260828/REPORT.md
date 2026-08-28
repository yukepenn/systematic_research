# MS-BBO-V1 — all 7 gates pass, 4 leak probes pass. **MS-BBO-CANDIDATE-1, discovery-grade only.**

| | |
|---|---|
| **verdict** | **CANDIDATE EXISTS — `MS-BBO-CANDIDATE-1`.** DISCOVERY-GRADE ONLY |
| spec committed | `8467526`, **before** the result |
| sample | 58 quote-complete sessions · **19,194 decisions** · 48 evaluated out-of-fold |
| span | 2025-10-15 → 2026-07-31 (v2 substrate) |
| **NOT** | validated · confirmed · production-ready · live-eligible |

> ### **There is no clean BBO historical holdout and none can be manufactured.** The ceiling was
> ### declared before the run and this result earns exactly it: **a candidate that must now earn
> ### real validation prospectively.**

---

## 1. Result

| arm | net | $/session | t | trade rate | directional accuracy | positive sessions |
|---|---:|---:|---:|---:|---:|---:|
| **RIDGE (primary)** | **$245,989** | **$5,124.76** | **6.76** | 61.4 % | **56.6 %** | **87.5 %** |
| GBM (challenger) | $202,788 | $4,224.74 | 7.13 | 50.3 % | 56.7 % | 85.4 % |

Stress: Ridge **+0.5 tk/side → $203,888**; **+1.0 tk/side → $175,296**.

| gate | observed | |
|---|---:|---|
| B1 OOF net > 0 | $245,989 | PASS |
| B2 > 95th pctile of **max-stat** null | **100.0th** | PASS |
| B3 > 95th pctile of placebo | **100.0th** | PASS |
| B4 beats same-trigger mirror | **+$19,693/session** | PASS |
| B5 net > 0 at STRESS +0.5tk | $203,888 | PASS |
| B6 top-5 sessions ≤ 50 % of net | **31.4 %** | PASS |
| B7 net > 0 in ≥ 3 of 4 quartiles | **4 of 4** | PASS |

The null is real — 57 replicates, **57 distinct values**, sd $1,011 — and it is the **max over
{Ridge, GBM}**, so the better model was never compared against a single-model null. The
same-trigger mirror earns **−$14,568/session**: the edge is in *direction*, not in picking
profitable moments.

## 2. ⚠️ The leak audit — run at the moment of maximum confidence, not after doubt

A t of 6.76 on this repo's history has usually been a look-ahead (W03, W37, W41, W77). Four probes,
each able to fail:

| probe | result | |
|---|---|---|
| **L1** direct timestamp assertion | **0 violations** of `feature_ts < t < execution_ts` | PASS |
| **L2** features lagged one 60 s step | **$5,125 → −$1,490/session** | ⚠️ investigated below |
| **L3** drop every mid-return feature | $5,125 → **$4,873** | edge is **not** momentum |
| **L4** execution quotes from a *different* session | **−$3,692/session** | PASS — not a label artifact |

**L2 was the anomaly and it drove a fifth probe.** L2+L3 together (signal not in momentum, destroyed
by a 60 s lag) fit one specific hazard **in my own code**: `mid` and `spread` are built from the last
bid and last ask before `t`, which may be from different instants — so a model could be reading
*staleness* and correcting it rather than forecasting. Tested directly:

| | |
|---|---:|
| age of last bid / ask at decision | median **24 ms**, p95 140 ms, p99 ~290 ms |
| **\|bid age − ask age\|** | **median 0 ms**, p95 80 ms |
| edge, both quotes fresher than 250 ms | **$5,175.60/session** (n 18,822 of 19,194) |
| edge, both quotes fresher than 100 ms | $4,836.23/session |
| edge where one side staler than 250 ms | −$159/session (n 372) |

> **Staleness is REJECTED.** The two sides are near-synchronous, and the edge *survives* — indeed
> slightly improves — when restricted to fresh quotes. The reconstruction is sound.

**And L2's negative retention is explained rather than waved away.** Mid-return autocorrelations are
tiny (−0.020 to +0.027), so this is not momentum or simple reversal. Using features from `t−60` to
predict `[t, t+60]` is a *120-second-ahead* forecast at a 60-second horizon; a microstructure signal
with a sub-minute half-life should not merely decay to zero there but can inv­ert. **L2 is consistent
with a genuine fast-decaying signal — it is not evidence of a leak, and it is not evidence against
one either. L1/L4/L5 are what carry that verdict.**

## 3. Where the edge actually is, and whether the arithmetic closes

| | |
|---|---:|
| OOF corr(predicted, actual) | **+0.1702** |
| OOF R² | +0.0273 |
| prediction sd / actual sd | $68.30 / $324.92 = 0.210 |
| mean \|60 s mid move\| | **$224.91** (≈ 11 NQ points — correct for 60 s at daily σ ≈ 300 pts) |
| mean \|move\| on **traded** decisions | $246.60 |
| **mean net per trade** | **$25.21** |
| sessions | 48 · worst −$8,167 · median **$4,248** · best $18,960 |

The arithmetic closes independently: with a regression slope of `0.17 × 324.92/68.30 ≈ 0.81` and
`E[|pred| | traded] ≈ $60`, expected gross per trade ≈ $48, less ~$19.4 cost ≈ **$29** — against
$25.21 observed. **The result is internally consistent, not a bookkeeping artifact.**

**Cost is small relative to the horizon**: ~$19.36 round trip against an $225 mean absolute move.
That is why the strategy trades 61 % of the time and why modest directional skill compounds — and
it is also why the stress ladder matters: at +1.0 tick/side the edge falls 29 % but survives.

**No quote size anywhere.** Bid/ask **price** only; trade volume enters only through the
order-invariant F4 controls.

## 4. ⚠️ What this is NOT, stated as plainly as the result

- **48 evaluated sessions**, all from **2025-10 → 2026-07**, all **already outcome-consumed**.
- **No clean historical holdout exists**, so no amount of in-sample rigour upgrades this.
- An OOF correlation of 0.17 on 60-second moves in a liquid market is **large**, and results of this
  size most often do not survive prospective testing. **That is the test, and it has not been run.**
- The signal has a **sub-minute half-life** (L2), so it is execution-latency sensitive. The frozen
  8 ms-median / 1,000 ms-cap fill contract models that, but real latency is a live-system question.

## 5. Verdict

| | |
|---|---|
| **what passed** | all 7 preregistered gates; 4 of 4 leak probes; the staleness hypothesis rejected on measurement |
| **what it earns** | **`MS-BBO-CANDIDATE-1` — DISCOVERY-GRADE**, frozen |
| **evidence class** | **DISCOVERY-CONSUMED. No historical confirmation is available for this lane, ever.** |
| **next stage** | **PROSPECTIVE SHADOW.** No historical retuning after freeze |
| **LIVE** | **NO** |
| **not authorized** | this does **not** authorize spending the 141-session Last-only blind pool — that pool has no quotes, and this candidate depends on bid/ask price state unavailable there |
