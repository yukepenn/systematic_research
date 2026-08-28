# PHASE 0 — engine hardening. **The int32-overflow class exists in exactly ONE production site,
# and it is already void.**

| | |
|---|---|
| **scope** | the three silent-failure **classes** survived on 2026-08-28. **Not** a general code review |
| files scanned | **802** python files |
| **0A** integer overflow in time arithmetic | **4 sites overflow on this interpreter — 1 real, 3 deliberate reproductions** |
| **0C** `datetime64` vs `Timestamp` keys | **30 sites, 2 flagged at-risk, 0 confirmed** |
| **0D** import-time destructive handles | **374 module-level writes, 10 imported elsewhere, 3 confirmed hazardous** |
| shipped | `research_sdk/timegrid.py` · `causality.py` · `keysafe.py` · `audit_defect_classes.py` · `test_timegrid.py` |

---

## 0A. Integer overflow in time arithmetic — blast radius is **one line**

The scanner is not textual. For every `np.arange(...) * <time scale>` it **executes the constructor
on this interpreter** and round-trips the product, so it reports whether a site *actually* overflows
here rather than whether it looks suspicious.

| site | verdict |
|---|---|
| `runs/MSBBO_V1_20260828/src/bbo_v1.py:119` | ⛔ **THE ORIGINAL DEFECT.** `int32`, overflows. Object already **VOID**; file deliberately unedited so the refuted object stays readable |
| `runs/MSBBO_DEPLOYMENT_FREEZE_20260828/src/void_audit.py:112, :163` | ✅ **deliberate** — the audit reproduces the bug to prove it |
| `research_sdk/test_timegrid.py:37` | ✅ **deliberate** — the pinned regression |

> ### **Answer to "does this class exist anywhere else": NO.**
> Zero unknown production sites. Every other `np.arange` in the repo indexes **bars or rows**, not
> nanoseconds. Four sites that *look* like the pattern carry an explicit `dtype=np.int64` and are
> verified safe by execution.

**`research_sdk/timegrid.py`** makes the class unreachable prospectively. Every constructor returns
`int64` and verifies its own output against **declared** intent — count, exact min, exact max, sign:

```python
lookback_offsets_s(30, 1)   # 30 offsets, all strictly < 0, exactly [-30e9, -1e9] ns
horizon_offsets_s(60)       # strictly > 0
safe_scale(v, NS_PER_S)     # round-trip division PROVES no wrap; not a bound estimate
assert_strictly_before(max_source_ts, decision_ts)   # row-by-row
```

Both bounds of a lookback are given as **positive seconds-into-the-past**, so a sign slip cannot
silently produce a future read. `lookback_offsets_s(1, 30)` is rejected, not reinterpreted.

## 0E. The permanent regression test — 7 of 7 pass

`python research_sdk/test_timegrid.py` reproduces the failure **deterministically on any platform**
(it emulates `int32` explicitly rather than depending on the host's default int width, so it cannot
become silently vacuous on Linux or NumPy 2):

```
native           dtype int32  range [-2.115098s, +2.064771s]  positive: 15/30
emulated int32   dtype int64  range [-2.115098s, +2.064771s]  positive: 15/30
safe             dtype int64  exactly 30 offsets, [-30.000000s, -1.000000s], 0 positive
```

The final test feeds the **real historical offsets** through the guard and requires the rejection
message to name the **+2.06 s** encroachment. This test exists because the bug was economically
material — it turned a **−$1,785.88/session** loser into a **+$5,124.76/session** "candidate" that
passed 7 gates, 4 leak probes and a genuine refitted null at the 100.0th percentile.

## 0B. Causality probe standard — now a **pre-candidate gate**

`research_sdk/causality.py` implements the two-sided contract:

| clause | requirement |
|---|---|
| **NEGATIVE** | corrupt every source event **strictly after** the cutoff → features bit-identical (default tolerance `0.0`) |
| **POSITIVE** | perturb an input **inside** each family's declared information set → **that family must move** |

**The positive clause is the one that matters.** A one-sided probe cannot distinguish a causal
engine from one that has silently stopped reading its inputs — an engine returning constants passes
the negative clause perfectly. `two_sided_probe` reports **per-family** which families responded, and
names any that did not as *"not being certified by this probe"*.

`probe_rolling_path` closes the specific hole that let the real bug through. `MS-BBO-V1`'s `L1`
asserted `feature_ts < t < execution_ts` for the lookups **at `t`** and passed correctly with zero
violations — it never examined the thirty **rolling-path offsets**, which is exactly where the
overflow lived. The new function requires an engine to **emit the min and max source timestamp it
actually consumed**, then asserts row-by-row that `max_source_ts < decision_ts` *and* that the window
reaches as far back as declared. A path feature whose window silently collapsed is rejected too.

> **"The helper function uses `side='left'`" is not proof.** Emit the timestamps you touched.

## 0C. Key/type safety — 30 sites, **2 flagged, 0 confirmed**

The scan flags any column both `.unique()`'d and `.groupby()`'d. Most are **not this class**:
`.unique()` on int64 or object returns `numpy.int64` / `str`, which **hash equal** to their Python
counterparts. Only `np.datetime64` vs `pd.Timestamp` fails to hash equal.

Both date-like flags were traced by hand and are **false positives**:

| flagged | why it is not the defect |
|---|---|
| `research/scalping_lab/src/python/w8_bmom.py` | the bootstrap keys on `sess` via `.to_numpy()` on **both** sides — type-consistent. The `date` column's `unique`/`groupby` uses are never cross-referenced as dict keys |
| `runs/SMV2AK_VOLUME_BARS/src/step1_volume_bars.py` | `cal_1m` and `cal_3m` are **both** built from `.unique()`, so the set operations compare `datetime64` to `datetime64` |

**The only confirmed instance in repo history is `CARRY00` run 1**, which reported zero paired days
for all 25 roots and would have returned a completely plausible `CLOSED-BY-DATA`. It is fixed and
guarded. `research_sdk/keysafe.py` provides `canon_ts`, `build_lookup` (uniqueness-asserted),
`assert_resolves` (the guard CARRY00 lacked), `safe_merge` (dtype-checked, unmatched-counted,
empty-result-rejecting) and `known_match_control` — a deliberate externally-known key that **must**
be present, because a probe on data alone can be vacuous.

## 0D. Import-time destructive handles — **374 → 10 → 3**

The first version of this scanner reported **638** sites because it descended into function bodies,
which do not execute on import. Corrected, it reports **374 module-level writes** — and most of those
are flat scripts where the write **is** the purpose, which is not a hazard.

**The hazard is a module another module imports.** Cross-referencing imports leaves **10**, of which
**3 are confirmed** to have real importers:

| module | imported by | status |
|---|---|---|
| `runs/MSBBO_V1_20260828/src/bbo_v1.py:45` | `deploy_fit` · `stream_engine` · `stream_parity` · `void_audit` | ⛔ **the confirmed instance** — it zeroed `out/bbo_v1.txt` |
| `runs/R1_ADAPTIVE_EXIT/src/construct.py:257` | 4 modules | historical, recorded |
| `runs/W18R2_M5_XINST/src/run_m5.py` ×4 | `A1A2_ATR_AUDIT/src/run.py` | historical, recorded |

**Historical run objects are NOT rewritten for cleanliness** — that is the standing rule, and
editing `bbo_v1.py` would break the hash the void record depends on. The defects are recorded and
the corrected pattern is used prospectively. **All five new `research_sdk` modules have zero
module-level writes**, verified by running the scanner against themselves.

## What this phase does and does not buy

| | |
|---|---|
| **does** | makes the exact economically-material failure **unreachable** in new engines, and pins it with a test that cannot go vacuous |
| **does** | converts "the helper is causal" from an assertion into an **emitted, asserted measurement** |
| **does not** | make any historical result more trustworthy. `MS-BBO-CANDIDATE-1` stays **VOID**; `CARRY_V1` stays **CLOSED** |
| **does not** | constitute alpha progress. **Infrastructure is not alpha** |
