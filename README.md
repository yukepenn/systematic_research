> **⚠️ This describes the ORIGINAL Solar Wave campaign only (closed 2026-08-07).**
> Two further campaigns have run since and are now the active work:
> **`research/system_master/CURRENT_TRUTH.md`** (SYSTEM_MASTER — portfolio + one-contract
> construction, active, updated continuously) and **`research/scalping_lab/CAMPAIGN_STATE.md`**
> (short-horizon scalp search, phase complete). For overall repo orientation start at
> **[`MAP.md`](MAP.md)**. This file is kept exactly as the original campaign left it — its own
> content below is accurate for what it covers, just not the whole repo anymore.

# NQ Solar Wave campaign — START HERE

_Status: **CLOSED** at the formal stop condition, 2026-08-07. Last integrity audit: 2026-08-07._

This file is the only entry point you need. Everything else is either evidence behind a claim
made here, or a historical record kept because the campaign constitution forbids deleting
failed work.

---

## 1. Where we are, in five lines

- The vendor indicator was **fully reverse-engineered**. That part is finished and certain.
- A real but **very thin** edge exists in NQ. It is a ~3 % deviation from a no-alpha null.
- **No single parameter is selectable.** The deliverable is an unselected ensemble, not a config.
- **Nothing is promotable.** It failed its one external portability test (ES) and cannot be
  certified by deflation on 4.6 years.
- The campaign **stopped on its own rule**, not because it ran out of ideas: three consecutive
  waves produced no robust improvement, and every remaining question is data-limited.

**Nothing here has ever been traded, deployed, or connected to an account. It never should be
without new data.**

## 2. The final result

**Recommended architecture: R5** — a volatility-normalised directional-change ensemble on
3-minute NQ, Type-1 signals only, 13 members at equal risk.

| | value |
|---|---|
| Sharpe (daily, all days) | **0.977** |
| net, 2022-01 → 2026-07, 1 contract avg exposure | $198,059 |
| max drawdown | −$39,126 |
| positive years | 5 / 5 |
| P(Sharpe ≤ 0), circular block bootstrap | **0.0020** |
| top 1 % of trades as share of net profit | **160 %** ← the dominant risk |

Full spec: [`reports/final_system_design.md`](reports/final_system_design.md) §7.
Ranked alternatives: [`reports/final_pareto.csv`](reports/final_pareto.csv).

**Read §6 of the design document before §3.** The risk disclosures matter more than the returns:
the bottom 99 % of trades lose money in aggregate, the short side has no standalone edge, and
removing the top 10 days takes R5 from $198k to $72k.

## 3. What to read, in order

| # | file | what it answers |
|---|---|---|
| 1 | [`reports/final_system_design.md`](reports/final_system_design.md) | **The decision package.** What was found, what it is worth, what would break it |
| 2 | [`reports/final_pareto.csv`](reports/final_pareto.csv) | The candidate set with status flags |
| 3 | [`research/CAMPAIGN_STATE.md`](research/CAMPAIGN_STATE.md) | Wave-by-wave verdicts and the stop condition |
| 4 | [`research/06_red_team/RED_TEAM_WAVE1C_WAVE2.md`](research/06_red_team/RED_TEAM_WAVE1C_WAVE2.md) | The independent audit that overturned two headline claims |
| 5 | [`research/03_reverse_engineering/SOLARWAVE_MATH.md`](research/03_reverse_engineering/SOLARWAVE_MATH.md) | The recovered indicator, in full |
| 6 | [`reports/robustness.md`](reports/robustness.md) | Cost stress, stability, concentration, known fragilities |

Everything else is supporting evidence. You do not need it unless you are checking a number.

## 4. Folder map

```
reports/          THE DELIVERABLES — current, audited, mutually consistent
research/
  00_truth/       Phase 0 — frozen baseline, parity, determinism
  01_diagnostics/ Phase 1 — attribution, null control, 2022 regime, external review
  02_solar_refinements/  Wave 1 / 1b / 1c — parameter mapping, PBO, the ensemble finding
  03_reverse_engineering/  THE RECOVERY — recovered math, Type-2 spec + proof
  04_execution/   H-011 — can the 89 % friction be executed away? (no)
  05_open_axes/   Wave 2 — axes the vendor never exposed (H-006/007/008/012)
  06_red_team/    THE AUDIT — four independent reviewers vs my own results
  07_h014_price/  Wave 3 — the decisive volatility-vs-price control
  08_es_portability/  The external test. It failed
  09_sleeves/     Wave 3 — C2 / C4 / wave conditioning. All rejected
  deep_research/  DR-01..07 — 32 preregistered hypotheses (INPUTS, not results) + DC01/DC02
  registry/       Hypothesis log, tested configs, the preregistered trial rule
  CAMPAIGN_STATE.md, frontier.yaml, Research_Thesis*.
src/analytics/    The code. ensembles.py is the ONLY source of ensemble numbers
runs/             Immutable Phase-0/1 run dirs (see §6 — this convention lapsed later)
SolarWaveRK/      Vendor material. Unmodified, never redistributed
```

## 5. Chronology — how this actually unfolded

One continuous line; no abandoned branches. All timestamps 2026-08-06/07.

| when | commit | what changed the picture |
|---|---|---|
| 20:48 | `5f9cf7e` | Baseline frozen and proven deterministic |
| 21:13 | `25e0923` | Entry timing shown to be real (null rejected, p = 0.032) |
| 21:44 | `229fd07` | Type-1 collapses to **one** parameter; 3-minute is the better timeframe |
| 22:18 | `e866c77` | **Open reconstruction matches the vendor exactly** — vendor dependency ends |
| 23:36 | `562c426` | **Parameter selection proven impossible**; the ensemble becomes the deliverable |
| 00:08 | `9097c04` | **Indicator 100 % recovered** (1.4 M bars, 0 mismatches); Wave-2 axes |
| 00:36 | `851cdef` | **Red team overturns H-006 and withdraws every DSR figure** |
| 00:43 | `b4c1816` | R4 redefined as the full 21-cell range — better on Sharpe *and* drawdown |
| 05:01 | `9bc3d9b` | Mechanism confirmed (p = 0.009); **ES portability fails** |
| 05:07 | `fbe267b` | Last sleeve rejected — frontier closed |
| 05:08 | `0660f74` | Stop condition declared |

The two turning points are `851cdef` (my own best result did not survive audit) and `9bc3d9b`
(the system did not travel to a second instrument). Both are negative, and both are load-bearing.

## 6. Known bookkeeping defects — found by audit 2026-08-07, all disclosed

These are documentation and provenance gaps, not research errors. None changes the
recommendation. They are listed here rather than quietly fixed, because the constitution
forbids silently changing the record.

| defect | status |
|---|---|
| `reports/latest.md`, `leaderboard.md`, `robustness.md`, `portfolio.md` were stale by a full campaign (Wave-1 era) | **FIXED** — rewritten to current truth |
| `final_pareto.csv` mixed calendars, and its C2 row used a skipna mean instead of the binding strict-1/N rule | **FIXED** — rebuilt on one stated calendar; C2 was the rejected candidate, so no ranking changed |
| `registry/tested_configs.csv` stops at Wave 1b (seq 90 of ~316 configs); `experiments.yaml` has 2 of ~12 entries | **OPEN** — raw evidence survives as ~300 execution ledgers under `research/`, but the "spec before results" guarantee is not verifiable for Waves 1c-3 |
| `runs/<run_id>/` convention lapsed after `RE01_open_parity`; later waves wrote ledgers under `research/` instead | **OPEN** — same cause, same mitigation |
| Daily P&L is bucketed by **calendar date**, not NT8 session date (18:00 ET roll) | **DISCLOSED** — the published basis is ~6 % *conservative*; both are now reported in `final_pareto.csv` |
| `hypotheses.md` still recorded H-006 as PASS with a withdrawn DSR | **FIXED** — corrected and Wave-3 verdicts appended |
| The R5 spec named `SolarWaveOpenV4`; every R5 figure was measured on `SolarWaveOpenV3`, and the two are **not** equivalent | **FIXED** — verified fill-by-fill, spec corrected to V3, no published number changed ([analysis](research/10_v3v4_equivalence/V3_V4_EQUIVALENCE.md)) |
| **No NinjaScript source was in the repo at all** — R5 was not reproducible from a clone | **FIXED** — all 11 strategies added under [`src/ninjascript/`](src/ninjascript/) with provenance and a reproduction recipe |
| **The licensed vendor DLL was committed to a PUBLIC GitHub repo** | **CONTAINED, NOT ERASED** — see §6b |

### 6b. Vendor-binary exposure — disclosed in full

`SolarWaveRK/RenkoKings_SolarWaveRK_NT8.dll` (4.5 MB) was committed in `35901db`
(2026-08-06 22:16) and pushed to a **public** repository. This violated the campaign's own hard
boundary — *never redistribute vendor binaries*. It was found by the 2026-08-07 audit, not by
design.

**Exposure window:** repository created 2026-08-06 23:46 UTC, set **private** 2026-08-07 ~12:15 UTC
— roughly **12.5 hours public**. At the time of remediation: **0 forks, 0 stars.**

**Residual risk, stated plainly:** making the repository private removes public access but **does
not remove the blob from git history**. It remains reachable inside the repo and in any clone taken
during the exposure window. Fully erasing it requires `git filter-repo` plus a force-push and a
GitHub Support request to garbage-collect the unreachable object — a history rewrite, which the
constitution otherwise forbids and which has **not** been performed. The vendor `Info.xml` and the
two `templates/*.xml` are in the same position. (`RenkoKings_SolarWaveRK_NT8.cs` is NT8's
auto-generated wrapper stub and contains no vendor logic.)

This entry is deliberately not deleted after remediation. The constitution forbids erasing failures,
and a redistribution incident is exactly the kind of thing that should stay on the record.

## 7. If work ever resumes

In priority order, from `final_system_design.md` §10:

1. **Monitor the overshoot ratio `r` quarterly.** Free, needs no trading, and is the system's own
   early-warning statistic. If `r` returns to 1.0 the edge is gone.
2. **A third instrument** (RTY / YM / CL). One ES failure is a data point, not a distribution.
   Portability is the only promotion criterion still open.
3. **Complementary families.** The only route to a portfolio that is not more of the same factor.
4. **Genuinely forward data, after a freeze.** No clean historical out-of-sample window remains —
   all data through 2026-07-31 was examined during discovery.

## 8. Safety boundary (permanent)

Research and backtesting only. Never place, modify or cancel an order; never enable or deploy a
strategy; never touch Sim101 or a real account; never alter connections, credentials or
licensing; never modify or redistribute the vendor assembly. The indicator was recovered by
**behavioural observation of its own published output only** — no decryption, unpacking, patching
or memory dumping was performed at any point.
