# EXECUTABLE OBJECT TRUTH — P1/PCT

**Status: RESOLVED, 2026-08-31.** `runs/G3_EXECTRUTH_02_20260831` reproduces the deployed C# object
at **100.000 % score agreement and 100.000 % size agreement, 0 disagreements out of 397 evaluated
entries**, against three named controls that all lose.

This is the authoritative statement of what the traded object is and how far the research
representation sits from it. Machine-readable tables: `runs/G3_EXECTRUTH_02_20260831/out/`.

---

## 1. THE ANSWER, IN ONE LINE

> **The research chain lags ATR twice. The executable lags it once. Removing exactly one line —
> `we_fastctx.py:81` — and changing nothing else reproduces the deployed object bit for bit.**

## 2. THE DEFECT, READ FROM SOURCE ON BOTH SIDES

```python
# research/weekly_edge/src/we_fastctx.py
:46   atr = np.concatenate([[atr[0]], atr[:-1]])          # FIRST lag, inside the feature builder
                                                          # whose own docstring (run_we_w09.py:26)
                                                          # already states "ATR14 at i-1"
:81   atr_l = np.concatenate([[atr14[0]], atr14[:-1]])    # lags the ALREADY-LAGGED array AGAIN
# research/weekly_edge/src/we_quality.py:44 — the identical double lag
```

⇒ `X['atr_l'][j]` is ATR through bar **`j−2`**, while `c_l[j]` and `vwap_l[j]` are bar **`j−1`**.
**The research object divides a bar-`j−1` numerator by a bar-`j−2` ATR denominator.**

```csharp
// research/weekly_edge/ninjascript/WeeklyEdgeP1PCT_v3.cs — CacheLagged(), runs LAST in OnBarUpdate
:1213-1216   tr = max(h-l, |h-lagClose|, |l-lagClose|);  trQ.Enqueue(tr);   // THIS bar's TR
:1218        lagAtr   = trSum / trQ.Count;                                   // ATR through bar b
:1237        lagClose = c;                                                   // close of bar b
```

⇒ `lagAtr` and `lagClose` are **frozen at the same bar**. Symmetric. **The executable has no such
asymmetry**, and it is the *correct* one.

## 3. THE DECIDING TABLE

397 evaluated entries. "Strictly beats" was defined before measurement — a tie counts as a loss.

| arm | construction | score | size | bad / 397 |
|---|---|---:|---:|---:|
| **H_CORRECTED** | ATR `b−1`, features `b−1` | **100.000 %** | **100.000 %** | **0** |
| C1 — the predecessor's best | ATR `b−2`, features `b−1` | 96.977 % | 98.992 % | 12 |
| C2 — fresh index shift | ATR `b−1`, features `b` | 87.909 % | 97.733 % | 48 |
| C3 — **both** ATR lags removed | ATR `b`, features `b−1` | 96.725 % | 99.496 % | 13 |

**C3 is the control that matters.** Removing *more* lag also loses. The answer is specifically a
**single consistent lag at `b−1`** — exactly what the source predicts — not "less lag is better".

**Why the first attempt could not have found this.** `G3_EXECTRUTH_01` tested a one-dimensional
family (which single index shift?) and its best arm plateaued at 96.977 %. The executable is a
**mixture**: `phase only $319,250`, `ATR only $331,388`, `both $324,674`. **Neither component alone
is the executable**, so no single index shift could express it. That failure is recorded FAILED and
is not reinterpreted.

## 4. HOW FAR THE RECORD WAS OFF

Same trade schedule — identical `(et, xt, dir)` asserted for all 2,401 trades under every size
vector. **95 trades (4.44 %) size differently.**

| | canonical 2022-07-01 → 2026-08-01 | pre-burn (< 2026-05-31) |
|---|---:|---:|
| research chain **as quoted** | $331,241 · $1,570/wk | $337,952 · $1,673/wk |
| **H_CORRECTED (the object we trade)** | $324,674 · $1,539/wk | $330,826 · $1,638/wk |
| **difference** | **−$6,567 · −$31/wk** | **−$7,126 · −$35/wk** |

> **Every P1 research figure this campaign has quoted sits ~2.0 % ABOVE the object that actually
> trades.** It does **not** concentrate in the burned window — the pre-burn gap is *larger*, so the
> burned period gives +$559 back. **87.1 % of the difference lives in the top decile by
> per-contract P&L**, which is exactly where P1's economics live.

## 5. WHAT THIS IS AND IS NOT

**IT IS** a correction to the record. Every Python-chain P1 number now carries a known −2.0 % offset.

**IT IS NOT** a P&L opportunity, and not a `P1_vNext`. **The deployed strategy never had the
defect** — it has always used the consistent lag. The research object was the optimistic one.

**`we_fastctx.py:81` HAS NOT BEEN PATCHED.** Patching it would silently change 100+ historical runs
and is its own decision with its own record. Any future patch must be a named, committed decision,
not a side effect.

**Agreement is not correctness.** This establishes *which object we trade*. It says nothing about
whether that object is good.

## 6. THE OTHER PARITY FACTS, FOR REUSE

- **The two price series are BIT-IDENTICAL.** Back-adjustment offset exactly 0.0000 (mean, median,
  sd) in 10 of 12 months; 2 bars differ out of 325,006. P0's tolerance never bound.
- **State/action parity holds on the WARM sub-span** (session ≥ 51, where the `.cs` `tilt`
  accumulator stops being identically zero — a split declared from source *before* computing):
  `voteOK 99.9207 %`, `t0..t3 ≥ 99.8187 %`, entry Jaccard `0.99065`, trade count `+0.313 %`.
  **VALIDATED on the WE_W52 band.**
- **The full-span entry Jaccard is 0.85176**, below the 0.90 line at which WE_W52 says "it is not
  the object". That is a **warm-up artifact of the executable itself**, not a parity failure, and it
  is recorded rather than argued away.
- **Residual disagreement: 95.316 % assigned to named causes, 4.684 % unexplained** — the weakest
  gate in the run, clearing its bar by 0.32 pp. The unexplained part is structured, not noise:
  `rngHist` coverage on 2026-07-21…07-30; one `tilt` session (2025-12-19, `close − SMA50` = −6.11 pt
  on 26,094.61 — the tightest sign decision in 239 sessions); and the export's first two sessions
  where the 13 virtual members are themselves cold.
- **The two volume series genuinely differ on 104 bars (0.032 %)**, none of them action-moving.

## 7. THE SUBSTRATE THAT MADE THIS POSSIBLE

`C:\NT8_ForwardLogs\export\we_p1pct_p1pct.csv` is **not** realtime-scoped. It carries the entire
`DaysToLoad = 365` warm-up replay — **353,878+ rows of the executable's own per-bar internal state**
(`nMem, nThr, dL, ratio, voteOK, size, score, qty, sessPnl, stopped, tilt, bmom, t0..t3`). Nobody
had recorded that it existed. Snapshot for this work:
`runs/G3_EXECTRUTH_01_20260831/out/cs_export_snapshot.csv`, sha256
`403131d10ab7027d7bbb904204f3409ff6b993daa0a947e703e26ff34ce99999` (kept on disk, gitignored — it
is **not** regenerable, the live file is appended to continuously).

⚠️ **One thing this does NOT establish.** The export's post-deployment rows are all ≥ 2026-08-01 and
the seal dropped every one. **100 % of the evidence here is NT8 historical replay.** Whether
realtime processing differs from historical processing is **unresolved**, and the first sealed-window
read that could settle it is a future scheduled read.
