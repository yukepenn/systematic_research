"""GENESIS null-construction guard — circular-shift nulls that provably have teeth.

CLAUDE.md §4: "Nulls must preserve dependence... circular shifts for time series."
This module makes the null CONSTRUCTION itself structural, closing the repo's four
recorded null incidents:

  1. LEAKY-RECOMPUTE null — a null pipeline that recomputed features from unshifted
     (or otherwise leaky) inputs. Countermeasure: the shift is applied AT LOAD, to the
     raw input frame the features are built from; the frozen decision_fn is run as a
     BLACK BOX on the shifted frame, so features can only be recomputed from shifted
     inputs. Nothing downstream of the decision function is ever shifted.
  2. SHIFT-INVARIANT null — np.roll(x, k).mean() style: a statistic invariant under
     rotation, so every "null draw" equals the real value and the null band has zero
     width. Countermeasure: verify_null_sensitivity RAISES NullInvarianceError when the
     statistic does not move across shifts.
  3. ORACLE null — the null path could still see the true answer (e.g. a captured
     unshifted frame), again collapsing the null onto the real statistic.
     Countermeasure: same sensitivity check — an oracle null cannot move, so it is
     refused before any p-value is quoted.
  4. OVER-EASY PERMUTATION null — i.i.d. row permutation destroys within-session
     dependence, making the null far too easy to beat. Countermeasure: shifts move
     WHOLE UNITS (sessions): within-unit row order and contiguity are preserved
     exactly; only the unit-block sequence rotates.

Contract shared by both entry points:
  loader()                       -> the raw input pd.DataFrame (called ONCE).
  decision_fn(frame)             -> opaque decisions, computed only from `frame`.
  statistic_fn(decisions, base)  -> float; evaluates decisions against the ORIGINAL
                                    (unshifted) frame `base`, so shifted-input
                                    decisions are scored against real outcomes.
Alignment of decisions to `base` rows is statistic_fn's responsibility (with
equal-length units it is positional; per-unit statistics work for unequal lengths).

Run verify_null_sensitivity BEFORE quoting any percentile from run_circular_null:
a null that cannot move has no teeth, and a p-value from it is not evidence.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


class NullGuardError(RuntimeError):
    """Misuse of the null machinery (bad shifts, missing unit column, too few units)."""


class NullInvarianceError(NullGuardError):
    """The statistic is (near-)identical across circular shifts: the null cannot move,
    so it cannot reject anything. Quoting a p-value from it would be incident class
    2/3 above. Raising (not warning) is deliberate — a toothless null must stop the
    run, not decorate it."""


def _unit_blocks(frame: pd.DataFrame, unit: str) -> list[np.ndarray]:
    """Positional index blocks, one per unit, in order of first appearance.
    Requires each unit's rows to be contiguous (a time series grouped by session is);
    non-contiguous units would silently break dependence, so they are refused."""
    if unit not in frame.columns:
        raise NullGuardError(f"unit column {unit!r} not in frame — cannot shift whole units")
    codes, _ = pd.factorize(frame[unit], sort=False)
    change = np.flatnonzero(np.diff(codes) != 0)
    starts = np.concatenate(([0], change + 1))
    ends = np.concatenate((change + 1, [len(codes)]))
    if len(starts) != codes.max() + 1:
        raise NullGuardError(f"unit column {unit!r} is not contiguous — rows of one unit are interleaved with another")
    return [np.arange(s, e) for s, e in zip(starts, ends)]


def circular_shift_units(frame: pd.DataFrame, k: int, unit: str = "session") -> pd.DataFrame:
    """Rotate the sequence of whole unit-blocks by k (block k becomes first).

    Within-unit row order, contiguity and content are preserved EXACTLY — only the
    order of the blocks changes — so within-unit dependence survives (incident 4).
    Unit labels travel with their rows. Returns a fresh positional-indexed copy.
    """
    blocks = _unit_blocks(frame, unit)
    m = len(blocks)
    if m < 2:
        raise NullGuardError(f"only {m} unit(s) — cannot circular-shift")
    k = int(k) % m
    order = np.concatenate(blocks[k:] + blocks[:k])
    return frame.iloc[order].reset_index(drop=True)


def _stat_per_shift(frame, decision_fn, statistic_fn, shifts, unit, label):
    stats = []
    n = len(shifts)
    for i, k in enumerate(shifts, 1):
        shifted = circular_shift_units(frame, k, unit)
        stats.append(float(statistic_fn(decision_fn(shifted), frame)))
        if n >= 10 and (i % max(1, n // 10) == 0 or i == n):
            print(f"null_guard: {label} shift {i}/{n}")
    return stats


def verify_null_sensitivity(loader, decision_fn, statistic_fn, shifts,
                            unit: str = "session", rtol: float = 1e-9, atol: float = 1e-12) -> dict:
    """Prove the null CAN move before it is used. Applies circular shifts AT LOAD (to
    the input frame — never to decisions or outcomes), runs the frozen decision_fn as
    a black box per shift, and RAISES NullInvarianceError if the statistic is
    (near-)identical across the real run and every shifted run.

    `shifts` must be nonzero ints (0 is the real alignment, not a null). Returns
    {'real_stat', 'shift_stats', 'spread'} on success for the caller's gate table.
    """
    shifts = [int(k) for k in shifts]
    if not shifts:
        raise NullGuardError("no shifts supplied — cannot verify sensitivity")
    if any(k == 0 for k in shifts):
        raise NullGuardError("shift 0 is the REAL alignment, not a null draw — remove it")
    frame = loader()
    m = len(_unit_blocks(frame, unit))
    if any(k % m == 0 for k in shifts):
        raise NullGuardError(f"a shift is 0 mod {m} units — it reproduces the real alignment, not a null")
    real_stat = float(statistic_fn(decision_fn(frame), frame))
    shift_stats = _stat_per_shift(frame, decision_fn, statistic_fn, shifts, unit, "sensitivity")
    all_stats = np.asarray([real_stat] + shift_stats, dtype=float)
    spread = float(np.nanmax(all_stats) - np.nanmin(all_stats))
    tol = atol + rtol * float(np.nanmax(np.abs(all_stats)))
    if not np.isfinite(spread) or spread <= tol:
        raise NullInvarianceError(
            f"null has NO TEETH: statistic spread {spread:.3g} <= tol {tol:.3g} across "
            f"{len(shifts)} circular shift(s) (real={real_stat:.6g}). A shift-invariant "
            f"or oracle statistic cannot form a null — fix the construction before "
            f"quoting any percentile."
        )
    return {"real_stat": real_stat, "shift_stats": shift_stats, "spread": spread}


def run_circular_null(loader, decision_fn, statistic_fn, n_shifts: int,
                      unit: str = "session", seed: int = 0) -> dict:
    """Build the circular-shift null distribution and locate the real statistic in it.

    Shifts whole units (sessions) to preserve within-unit dependence; the shifted
    frame feeds the frozen decision_fn, and statistic_fn scores those decisions
    against the ORIGINAL frame. Distinct nonzero shifts are drawn without replacement
    (seeded — one shared draw per family belongs to the caller's seed discipline);
    n_shifts >= m-1 uses every possible shift exactly once.

    Returns {'real_stat', 'null_stats', 'shifts', 'n_units',
             'percentile'  (fraction of null draws <= real, higher = better for a
                            higher-is-better statistic),
             'p_ge'        (fraction of null draws >= real, add-one corrected:
                            (1 + #{null >= real}) / (1 + n))}.
    """
    if n_shifts < 1:
        raise NullGuardError("n_shifts must be >= 1")
    frame = loader()
    m = len(_unit_blocks(frame, unit))
    if m < 3:
        raise NullGuardError(f"only {m} unit(s) — a circular null needs at least 3")
    all_shifts = np.arange(1, m)
    if n_shifts >= m - 1:
        shifts = all_shifts
    else:
        shifts = np.sort(np.random.default_rng(seed).choice(all_shifts, size=n_shifts, replace=False))
    shifts = [int(k) for k in shifts]
    real_stat = float(statistic_fn(decision_fn(frame), frame))
    null_stats = _stat_per_shift(frame, decision_fn, statistic_fn, shifts, unit, "null")
    arr = np.asarray(null_stats, dtype=float)
    return {
        "real_stat": real_stat,
        "null_stats": null_stats,
        "shifts": shifts,
        "n_units": m,
        "percentile": float(np.mean(arr <= real_stat)),
        "p_ge": float((1 + np.sum(arr >= real_stat)) / (1 + len(arr))),
    }


# --- selftest ----------------------------------------------------------------------
def _selftest():
    """Positive tests: every guard is shown to FIRE (charter §8/J). Synthetic data only."""
    ok = 0
    rng = np.random.default_rng(42)
    m, rows = 8, 5
    sessions = np.repeat([f"S{i}" for i in range(m)], rows)
    x = rng.standard_normal(m * rows)
    frame = pd.DataFrame({"session": sessions, "x": x, "y": np.sign(x)})  # y perfectly predictable from aligned x
    loader = lambda: frame.copy()
    decide = lambda f: np.sign(f["x"].to_numpy())                    # frozen black box: features from the (shifted) input
    score = lambda d, base: float(np.mean(d == np.sign(base["y"].to_numpy())))  # scored against ORIGINAL outcomes

    # 1. unit shifting preserves within-unit rows exactly and only rotates block order
    sh = circular_shift_units(frame, 3, "session")
    assert len(sh) == len(frame); ok += 1
    for s in [f"S{i}" for i in range(m)]:
        assert np.array_equal(sh.loc[sh["session"] == s, "x"].to_numpy(),
                              frame.loc[frame["session"] == s, "x"].to_numpy()), f"unit {s} rows mangled"
    ok += 1
    assert list(dict.fromkeys(sh["session"])) == [f"S{i}" for i in list(range(3, m)) + list(range(3))]; ok += 1
    # 2. a shift-SENSITIVE statistic is accepted (does not raise) and really moved
    res = verify_null_sensitivity(loader, decide, score, shifts=[1, 2, 5], unit="session")
    assert res["real_stat"] == 1.0 and res["spread"] > 0.05; ok += 1
    # 3. guard FIRES: shift-INVARIANT statistic (global mean of decisions — the
    #    np.roll().mean() incident) is REFUSED
    inv_score = lambda d, base: float(np.mean(d))
    try:
        verify_null_sensitivity(loader, decide, inv_score, shifts=[1, 2, 5]); raise AssertionError("guard 3 silent")
    except NullInvarianceError:
        ok += 1
    # 4. guard FIRES: oracle null — decision_fn ignores its (shifted) input and reads
    #    a captured original frame, so the null collapses onto the real statistic
    oracle_decide = lambda _f: np.sign(frame["x"].to_numpy())
    try:
        verify_null_sensitivity(loader, oracle_decide, score, shifts=[1, 2, 5]); raise AssertionError("guard 4 silent")
    except NullInvarianceError:
        ok += 1
    # 5. guard FIRES: shift 0 (the real alignment) refused as a null draw
    try:
        verify_null_sensitivity(loader, decide, score, shifts=[0, 1]); raise AssertionError("guard 5 silent")
    except NullGuardError:
        ok += 1
    # 6. guard FIRES: shift == m (0 mod units) refused — it is the real alignment in disguise
    try:
        verify_null_sensitivity(loader, decide, score, shifts=[m]); raise AssertionError("guard 6 silent")
    except NullGuardError:
        ok += 1
    # 7. run_circular_null: full distribution, real stat dominates every misaligned draw
    out = run_circular_null(loader, decide, score, n_shifts=m - 1, unit="session")
    assert out["n_units"] == m and len(out["null_stats"]) == m - 1; ok += 1
    assert sorted(out["shifts"]) == list(range(1, m)); ok += 1
    assert out["real_stat"] == 1.0 and max(out["null_stats"]) < 1.0; ok += 1
    assert out["percentile"] == 1.0 and abs(out["p_ge"] - 1 / m) < 1e-12; ok += 1
    # 8. subsampled shifts are distinct, nonzero, and seeded-reproducible
    o1 = run_circular_null(loader, decide, score, n_shifts=4, unit="session", seed=7)
    o2 = run_circular_null(loader, decide, score, n_shifts=4, unit="session", seed=7)
    assert o1["shifts"] == o2["shifts"] and len(set(o1["shifts"])) == 4 and 0 not in o1["shifts"]; ok += 1
    # 9. guard FIRES: missing unit column
    try:
        run_circular_null(lambda: frame.rename(columns={"session": "sess"}), decide, score, 3); raise AssertionError("guard 9 silent")
    except NullGuardError:
        ok += 1
    # 10. guard FIRES: non-contiguous unit rows (interleaved sessions would fake dependence)
    inter = pd.DataFrame({"session": ["A", "B", "A"], "x": [1.0, 2.0, 3.0], "y": [1, 1, 1]})
    try:
        circular_shift_units(inter, 1, "session"); raise AssertionError("guard 10 silent")
    except NullGuardError:
        ok += 1
    # 11. guard FIRES: too few units for a null
    tiny = frame[frame["session"].isin(["S0", "S1"])].reset_index(drop=True)
    try:
        run_circular_null(lambda: tiny, decide, score, 1); raise AssertionError("guard 11 silent")
    except NullGuardError:
        ok += 1

    print(f"null_guard selftest: {ok}/16 PASS (7 guards shown to fire)")


if __name__ == "__main__":
    _selftest()
