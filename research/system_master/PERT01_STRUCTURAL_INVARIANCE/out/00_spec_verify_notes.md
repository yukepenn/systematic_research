# PERT01/GRID01/GRID02 — infrastructure verification notes

Pre-diagnostic wiring check only. No diagnostic run happened in this pass. Diagnostic science
per campaign directive sec97-98: report all results, select no winner, promote nothing. GRID/PERT
results alone can never create a new baseline candidate.

Files read in full this session:
- `src/analytics/sm01_solarsim.py`
- `runs/W18R1_M1_VOLSEASON/src/common.py`
- `src/analytics/sm_bmom.py`
- `runs/SA0_SYSTEM_STRUCTURE/current_health/src/health_substrate.py`
- `src/analytics/smv2_common.py`
- `BASELINE_MODELS.md` (repo root, canonical) + `research/system_master/BASELINE_MODELS.md` (stub,
  redirects to root) + `research/system_master/FINAL_CAMPAIGN_BASELINE.md` + `research/system_master/CONVENTIONS.md`
- Grepped every `src/ninjascript/*.cs` for `VolMult` (all 20+ member-machine files)

---

## 1. Solar member ensemble — exact call surface

`src/analytics/sm01_solarsim.py`:

```python
VMS = list(range(6, 31, 2))   # incumbent 13 members: 6,8,...,30 — module-level, NOT a function arg

def sigma_series(close: np.ndarray, vol_period: int = 460, min_count: int = 30) -> np.ndarray
def member_states(close: np.ndarray, sigma: np.ndarray, vol_mult: float,
                   stop_mult_ticks: float = 179.0, smin_ticks: float = 40.0,
                   smax_ticks: float = 1200.0, start_up: bool = False)
                   -> (is_up, flip, s_eff, anchor)      # all np.ndarray, len n_bars
def member_trades(bars: pd.DataFrame, is_up, flip, s_eff, anchor,
                   bars_required: int = 20, comm_side: float = NQ_COMM_SIDE,
                   point_value: float = NQ_POINT_VALUE, stop_mult: float | None = None)
                   -> (fills: pd.DataFrame, pos: np.ndarray, pend_pos: np.ndarray)
```

Note: `member_trades`'s docstring header says "Returns (fills, pos)" but the function actually
returns a 3-tuple `(f, pos, pend_pos)` (confirmed at the `return` statement, line 273, and at every
call site, which all unpack 3 values). Pre-existing doc/code drift, not something this task should
"fix" — just flagging so the diagnostic script unpacks 3 values, matching every existing caller.

`runs/W18R1_M1_VOLSEASON/src/common.py`:

```python
INCUMBENT_VMS = list(sm.VMS)   # 6..30 step 2, 13 members — copied once at import time

def build_pend(bars, sig, vms=None, smax_ticks=1200.0, smin_ticks=40.0) -> np.ndarray  # (n_bars, n_members)
    """Verbatim SMV2AI common.build_pend. member_states/member_trades UNMODIFIED; only the
    sigma array fed in is varied."""
    # loops: for vm in (vms or INCUMBENT_VMS): sm.member_states(close, sig, float(vm), ...); sm.member_trades(...)
    # stacks each member's pend_pos column -> PEND

def build_pend_with_flips(bars, sig, vms=None, ...) -> (PEND, FLIPS)   # same + per-member flip array
```

**Exact mechanism confirmed**: `build_pend`'s own docstring already states the intended reuse
pattern for these three workstreams — vary `vms` (the list of VolMult values) and/or vary the
`sig` array fed in (produced by `sigma_series` with a different `vol_period`) — and NOTHING else
in `member_states`/`member_trades` changes. This is precisely GRID01 (vary ensemble resolution),
GRID02 (vary endpoints of the same 6-30 span), and PERT01's VolPeriod axis (vary `sig`).

- **GRID01/GRID02 call pattern**: `sig = sm.sigma_series(close)` (vol_period=460, unchanged) →
  `PEND = build_pend(bars, sig, vms=<candidate_list>)` → `T = sm.e10_target(PEND)` → feed into
  whichever downstream Product A/B formula is being tested (KSolar/KBmom etc. held at the EXACT
  current EQV01 values per the governance note — this workflow does not touch those).
- **PERT01 VolPeriod axis call pattern**: `sig = sm.sigma_series(close, vol_period=368)` (or 552)
  → `PEND = build_pend(bars, sig)` (vms defaults to INCUMBENT_VMS, unchanged) → same downstream.
  This isolates the VolPeriod axis exactly: only the causal-sigma trailing window moves; the
  member list, the threshold arithmetic, the fill/exit rules are untouched.

`e10_target(member_pos: np.ndarray, mult: int = 10, cap: int = 10) -> np.ndarray[int]` — consumes
the `PEND` stack, is completely agnostic to `len(vms)` or its values (just does
`member_pos.mean(axis=1)`), so any candidate `vms` list of any length/spacing/integrality works
without modification. This is the reason GRID01/02/PERT01 can share this one aggregation function
unmodified.

---

## 2. B-MOM (BAND_DAYS) and HTF (rolling window) — exact call surface

`src/analytics/sm_bmom.py`:

```python
BAND_DAYS = 14   # module-level constant, referenced as a bare global INSIDE bmom_trades' body
                 # (line 82: `if day_count >= BAND_DAYS:`; line 94: `past[-BAND_DAYS:]`) —
                 # NOT a default-arg bound at import time, so `sm_bmom.BAND_DAYS = 11` before a
                 # call WOULD technically work (Python resolves bare globals at call time), but
                 # this workflow does NOT recommend that route: mutating a shared module global is
                 # fragile under any future parallelism/reentrancy and isn't the pattern the repo
                 # already uses.

def bmom_trades(bars3: pd.DataFrame) -> pd.DataFrame        # trade ledger, BAND_DAYS hardcoded
def bmom_daily(trades: pd.DataFrame, cost: str = "net_c1_ticks") -> pd.Series
```

The repo's OWN established convention for parametrizing this axis is already visible in
`health_substrate.py`: it does not monkeypatch `sm_bmom.BAND_DAYS`; instead it imports the
constant once (`from sm_bmom import rth_3m, BAND_DAYS`, line 26) and writes its own **local
re-implementation** `bmom_pos_series(bars3)` (lines 60-91) that is byte-for-byte the same
band/VWAP logic as `bmom_trades`, just restructured to emit a per-bar position array instead of a
trade ledger. It still hardcodes `BAND_DAYS` via the module import rather than exposing it as a
parameter.

**PERT01's plan for the BAND_DAYS axis**: write a small local copy —
`bmom_pos_series(bars3, band_days=14)` — mirroring `health_substrate.py`'s existing local
reimplementation exactly, but with `BAND_DAYS` replaced by a `band_days` function parameter used
everywhere the constant currently appears (`day_count >= band_days`, `past[-band_days:]`). Verify
it reproduces `health_substrate.py`'s own `bmom_pos_series` output bar-for-bar when
`band_days=14` before trusting it for 11/17. Nothing about the entry/exit signal definition
(bands, VWAP, force-flat clock) changes — only the trailing-day count for the noise band.

`runs/W18R1_M1_VOLSEASON/src/common.py`:

```python
def htf_state(bars) -> np.ndarray
    """Verbatim SMV2T gate_AD.py HTF construction."""
    sclose = bars.loc[bars["is_last_of_sess"], ["sess_date","close"]].set_index("sess_date")["close"]
    htf = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
    return np.array([htf.get(d, np.nan) for d in bars["sess_date"]])
```

`rolling(50)` is hardcoded (no window kwarg) — matches `health_substrate.py`'s own independent
copy (lines 54-57), which is byte-identical except it additionally does
`tilt_state = np.where(np.isnan(tilt_state), 0.0, tilt_state)` after the dict lookup (needed
there because `build_pos_seq`'s `m_arr` construction does `tilt_state != 0` and NaN≠0 is True in
numpy — an un-filled NaN would silently leak into the Product-B tilt-agree flag; `common.py`'s own
downstream `dual_htf` doesn't need this because `st_bar == np.sign(T)` is naturally False for
NaN). **PERT01's plan for the HTF axis**: write a local `htf_state(bars, window=50)` matching
whichever of these two callers is the actual target (Product A path -> no fillna, matching
`common.py`; Product B/health-substrate path -> with fillna, matching `health_substrate.py`),
parametrizing only the `.rolling(N)` call, `.shift(1)` and the `np.sign` comparison held fixed
(causality-preserving). Verify byte-identical to the frozen file at `window=50` before trusting
40/60.

`common.dual_htf(T, st_bar)` — the m=1.25/s=0.5/rescale=0.9026 constants stay EXACTLY as currently
frozen (per governance note, that's EQV01's axis, not this workflow's); only the `st_bar` input
(built from a perturbed-window `htf_state`) would vary for a PERT01 HTF-horizon test.

---

## 3. G49 (uniformly-spaced NONINTEGER VolMult thresholds, 6-30) — mechanical validity

**Searched for integer-only assumptions in the signal definition itself** (not just historical
convention):

- Python (`sm01_solarsim.py`): `member_states(..., vol_mult: float, ...)` — already typed `float`.
  The only use of `vol_mult` is `resolve_s()`: `min(max(vol_mult * s, lo), hi)` — a pure continuous
  float multiply-then-clamp against float bounds (`lo = smin_ticks*0.25`, `hi = smax_ticks*0.25`).
  No array indexing, no dict/lookup-table keyed by `vol_mult`, no integer cast anywhere in
  `member_states` or `member_trades`. `build_pend` does `float(vm)` explicitly before calling
  `member_states` — i.e. the code proactively coerces to float rather than assuming int.
- NinjaScript (grepped every `VolMult`/`VolMults` occurrence across `src/ninjascript/*.cs`,
  20+ files): the strategy property is declared `public double VolMult { get; set; }`
  (`SolarWaveOpenV3.cs:405`, same pattern in `SolarWaveOpenV4.cs`, `SolarWaveSleeveV1.cs`), and
  every per-member ensemble master (`SolarWaveE10Master_v1/v2.cs`, `SolarWaveSMMaster_v1..v4.cs`,
  `SolarWaveOneContract{NQ,MNQ}_*.cs`) stores members in `private static readonly double[]
  VolMults` / `private double[] mVolMult`, populated as `6.0 + 2.0*m` (double arithmetic) and
  consumed only via `ResolveS(mVolMult[m])`, itself `VolMult * sig` (double multiply). The **only**
  integer cast anywhere in this search is `(int)mVolMult[m]` in `SolarWaveE10Master_v1.cs:399` and
  `_v2.cs:406`, and in both cases it feeds a debug/label string
  (`h.Append(",p").Append((int)mVolMult[m])`) — cosmetic column-header text, never read back into
  any trading decision.

**Conclusion: G49 IS mechanically valid.** VolMult/vol_mult is a genuine continuous double/float
in both the certified Python replica and the underlying NinjaScript source across every version
inspected; integers 6,8,...,30 are an incumbent CHOICE (a deliberately spaced 13-member ensemble),
not a computational requirement. `VolMult=8.5` would run through `resolve_s`/`ResolveS` identically
to `VolMult=8` or `VolMult=9` — same sigma-based stop-distance formula, same clamp, same flip
logic.

**G49 candidate list (disclosed)**: 24 uniformly-spaced NON-integer values spanning the incumbent
6-30 range, deliberately the half-integer offset of the incumbent grid (so none coincide with the
13 incumbent members, and none coincide with any plausible "endpoint perturbation" integer set
either):

```
6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5, 16.5, 17.5,
18.5, 19.5, 20.5, 21.5, 22.5, 23.5, 24.5, 25.5, 26.5, 27.5, 28.5, 29.5
```
(`np.arange(6.5, 30.0, 1.0)`, 24 values, step 1.0, uniformly spaced over [6.5, 29.5] ⊂ [6, 30].)

---

## 4. Existing metrics helpers — reuse plan

**`src/analytics/smv2_common.py`** is the house-frozen, currently-live metrics module:

```python
def dd_battery(dates, net, bar_eq=None, label="") -> dict
    # n_days, net, daily_vol, ann_vol, sharpe (ann. mean/std*sqrt(252)),
    # maxDD_eod, sortino (mean/downside-std*sqrt(252)), calmar (ann_ret/maxDD),
    # CDaR5 (mean of worst 5% of the drawdown series), avgDD, ulcer,
    # longest_TUW_days, median/p95_recovery, worst_{20,40,60,120}D,
    # worst_month, worst_quarter, pos_day_pct, pos_week_pct, pos_month_pct,
    # losing_month_streak, losing_week_streak, rolling60_min

def boot_ci_mean(net, block=5, n_boot=10000, seed=20260808, q=(0.05,0.95)) -> (lo, hi, p_pos)
    # circular block bootstrap CI for the daily mean
```

This is not merely "an existing implementation somewhere" — it is the function ALREADY imported
live by both files this task centers on: `runs/W18R1_M1_VOLSEASON/src/common.py:14`
(`from smv2_common import dd_battery`) and
`runs/SA0_SYSTEM_STRUCTURE/current_health/src/health_substrate.py:27` (same import). Both wrap it
in a thin `battery_row`/`metric_row` that just reshapes the dict into a report row — that wrapper
pattern is worth copying too (health_substrate.py:173-178, common.py:188-201), but the actual
Sharpe/Sortino/Calmar/CDaR/max-DD math lives in `dd_battery` alone.

A grep for `def .*(sharpe|sortino|calmar|cdar|drawdown|battery)` across the repo found ~67 files
with local matches, but almost all are per-run copy-pasted variants (the repo's own convention,
per `common.py`'s header: "verbatim reuse... every formula and constant... cross-checked by
hand") — e.g. `runs/SMV2A_DD_RECONCILE/smv2a.py:68` has its own `dd_battery` (likely the ancestor
that `smv2_common.py`'s version was promoted from). **Plan: import `dd_battery`/`boot_ci_mean`
from `src/analytics/smv2_common.py` directly** (as the two target files already do) rather than
reimplementing or copy-pasting yet another local variant.

---

## 5. Canonical commission figures

`BASELINE_MODELS.md` (repo root) itself only NAMES the commission template in prose
("Commission | MNQ, NinjaTrader Brokerage Lifetime", line 256) without spelling out the per-side
dollar figure in that particular table. The exact numeric figures are spelled out in
`research/system_master/FINAL_CAMPAIGN_BASELINE.md` (frozen 2026-08-08), in TWO places, both
identical:

```
line 47-48:  Solar member (NQ, from ledgers) | Lifetime $2.18/side + 1 tick/execution embedded
             E10 executable (MNQ)             | $0.65/side + 1 tick/execution on net target changes
line 176-177: Solar member (NQ) | $2.18/side ($4.36/RT), Lifetime commission, 1 tick/execution embedded
              E10 executable (MNQ) | $0.65/side ($13.00/RT per 10-MNQ)
```

`$13.00/RT per 10-MNQ` = `$0.65/side * 2 sides * 10 contracts`, i.e. the E10 aggregate context
(±10 MNQ units), NOT a per-single-contract figure — a single MNQ contract round-trip is
`$0.65 * 2 = $1.30`.

Cross-checked against the actually-executing code constants (triple confirmation):
- `src/analytics/sm01_solarsim.py:40-42`: `NQ_COMM_SIDE = 2.18`, `MNQ_COMM_SIDE = 0.65`
- `runs/SA0_SYSTEM_STRUCTURE/current_health/src/health_substrate.py:30-31`:
  `PV_MNQ, COMM_MNQ = 2.0, 0.65`; `PV_NQ, COMM_NQ = 20.0, 2.18`

**NQ**: $2.18/side -> **$4.36/RT**, exactly matching CLAUDE.md's frozen baseline commission figure
($4.36/RT, NinjaTrader Brokerage Lifetime) — same number, independently corroborated by 3 sources.
**MNQ**: $0.65/side -> **$1.30/RT per single contract**. This is the figure this workflow's
governance note already assumed ("$0.65/side per prior campaign findings") — now verified, not
merely assumed.

---

## 6. Data loading — window slicing convention (for completeness)

`sm.load_bars_3m(path)` returns the FULL available 3-min bar history with `sess_date`/
`is_last_of_sess` columns already computed; callers slice with a boolean mask on `sess_date`
(e.g. `common.py`'s `load_dev_bars`: `bars[bars["sess_date"] <= DEV_END]`). Same pattern applies
for GRID/PERT: load once, then produce BOTH a canonical-window slice (2023-01-01 .. 2025-02-02,
respecting the `to = D` "last session ending <= D" convention from CLAUDE.md) and a fuller-history
report (repo's existing dev window runs 2022-01-03..2026-05-29 per `DEV_END` in `common.py`, with
an already-vetted current-health extension to 2026-07-31 in `health_substrate.py` — 2026-08-01
onward remains sealed per `research/operational/LOCKED_FORWARD.md`). No new data pull is needed;
this is purely a slicing choice over the already-loaded `nq_3m_2022_2026.csv` substrate.

---

## Summary: nothing here blocks the diagnostic phase

All four axes (GRID01 ensemble resolution, GRID02 endpoint perturbation, PERT01 VolPeriod, PERT01
BAND_DAYS, PERT01 HTF horizon) have a confirmed, non-invasive call path that varies exactly one
input to an otherwise-unmodified, already-certified function. G49 (noninteger VolMult) is
mechanically valid and its candidate list is specified above. The "B evidence units" axis
(candidate values 3/4/5) remains UNMAPPABLE in current code per this session's exhaustive grep
(no `evidence`/`min_agree`/`AgreeCount`/`vote.?count`/`ConfirmBars`-shaped parameter exists
anywhere) — per campaign directive sec33/sec120, this specific PERT01 axis should be SKIPPED and
documented as such, not invented.
