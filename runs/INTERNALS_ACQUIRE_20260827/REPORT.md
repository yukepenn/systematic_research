# MARKET INTERNALS — acquired at $0, and it is the best-covered new surface yet

| | |
|---|---|
| **run class** | **DATA ACQUISITION + GATE** — no model, no feature, no hypothesis, nothing promoted |
| date | 2026-08-27 |
| code | `src/build_and_gate.py` · `SWBarExport_v1` |
| product | `research/data_internals/` |
| evidence | `out/gate.txt` · `out/gate.csv` · `research/data_internals/MANIFEST.csv` |
| seal | untouched — hard drop of anything ≥ 2026-08-01, and none was present |
| cost | **$0** |

> ### **`INFORMATION_COVERAGE` recorded market internals as `✗ no data`.**
> ### **`$TICK`, `$TRIN` and `$VIX` are all served at 1-minute across the entire research window.**
> ### **They cover 35.7 % of P1 decisions — 5.4× the order-flow lane.**

---

## 1. What was acquired

| symbol | bars | span | sessions |
|---|---:|---|---:|
| `$TICK` | 445,625 | 2022-01-03 09:31 → 2026-07-31 15:59 | 1,147 |
| `$TRIN` | 445,235 | 2022-01-03 09:31 → 2026-07-31 15:59 | 1,146 |
| `$VIX` | 444,640 | 2022-01-03 09:32 → 2026-07-31 15:59 | 1,148 |

**1.34 M bars**, one parquet per symbol, hash-stamped, in `research/data_internals/`.

⚠️ **These are indices, not traded contracts. `volume` is 0 on every bar and must never be treated
as flow.** Recorded in the manifest so a later reader cannot mistake it.

⚠️ **A correction to my own earlier probe.** I recorded `$VIX` daily depth as "~2–3 years" because
a **daily** request for 2021 returned empty. At **1-minute** it covers the full 2022–2026 window.
The daily and minute stores have different retention, and I generalised from the wrong one.

## 2. Coverage — the thing that closed the order-flow lane

| | entries | share |
|---|---:|---:|
| P1 scoring entries | 2,139 | — |
| inside RTH 09:31–15:59 | 765 | 35.8 % |
| **AND on a session internals cover** | **764** | **35.7 %** |
| *order-flow lane, for contrast* | *141* | *6.6 %* |

**Internals cover 5.4× more P1 decisions than order flow**, and the reason is structural: internals
exist for **every** RTH session, so coverage is not the binding constraint the way it is for tick data.

> ### ⚠️ **But P1 is a 64 %-overnight book.** Only 35.8 % of its decisions happen in RTH at all.
> **Internals can never speak to the other 64 %.** That is a permanent ceiling on this lane, it is
> a property of the strategy rather than of the data, and no acquisition changes it.

## 3. The gate — same yardstick as both order-flow gates

`MDE = 2.80 × sd / √n` at ~80 % power, two-sided 5 %.

| target | n | mean on covered | sd | MDE | × mean | verdict |
|---|---:|---:|---:|---:|---:|---|
| session-scoped | 764 | $226.07 | $2,383.94 | $241.49 | **1.07** | **UNDERPOWERED** |
| **FULL-HORIZON (primary)** | 764 | $190.66 | $2,457.77 | $248.97 | **1.31** | **UNDERPOWERED** |

**Marginal, not passing.** At 1.07× the covered mean the session-scoped target sits essentially on
the boundary: an effect **7 % larger than the covered mean** would be detectable. Compare the
order-flow lane at **3.11×** and **4.61×**.

**A descriptive fact, not a tested claim:** RTH entries carry a higher mean action value than the
book overall ($226 vs $160 session-scoped; $191 vs $112 full-horizon). That is a property of *when*
P1 trades, **not** evidence that internals predict anything, and it must not be quoted as if it were.

## 4. Verdict

| | |
|---|---|
| **`INFORMATION_COVERAGE`** | *market internals: ✗ no data* → **FALSIFIED.** `$TICK`/`$TRIN`/`$VIX` exist, free. Only `$ADD` and `$VXN` are genuinely absent, on failed probes |
| **lane status** | **MARGINAL — the closest any new surface has come.** Underpowered at the strict mean-scale yardstick, by 7 % on the session-scoped target |
| **information test** | **NOT RUN.** It requires its own preregistration — features, causality gate, walk-forward, refitted dependence-preserving nulls — and inventing it after seeing a coverage number is exactly the failure mode `CLAUDE.md` §4 forbids |
| **promoted / demoted** | **nothing** |

> **A passing power gate would only say a mean-scale effect *would be detectable*. It says nothing
> about whether one *exists*.** This gate does not even say that much — it says the lane is close
> enough to be worth a properly preregistered wave, and nothing more.

## 5. Continuation

The **next** wave — and the highest-EVI runnable row now — is a preregistered **Stage-A information
test on internals**: does breadth/volatility state predict full-horizon `delta_action_value`
incrementally beyond `RR_W002A`'s existing 18 causal features, on the RTH subset, against a
refitted dependence-preserving null, with the same self-validating causality gate (injected leak
must be dropped, injected lag must be kept) and a matched known-null control?

**It must be preregistered before it is run, and its population is the 764 RTH entries — declared
now, in advance, so it cannot be redefined after a result.**
