"""causality.py -- the MACHINE-ENFORCED TWO-SIDED CAUSALITY PROBE.  ENGINEERING_ONLY / ZERO_ALPHA.

No alpha engine's P&L is admissible until it passes this. That is a change in the order of
operations, adopted 2026-08-28 after `MS-BBO-CANDIDATE-1` was voided.

WHY TWO SIDES, AND WHY THE POSITIVE CLAUSE IS THE ONE THAT MATTERS.

    NEGATIVE CLAUSE   corrupt every source event STRICTLY AFTER the information cutoff.
                      Causal features must be bit-identical (or inside a declared tolerance).
    POSITIVE CLAUSE   perturb an input INSIDE each feature family's declared information set.
                      That family MUST move.

A one-sided probe cannot distinguish a causal engine from one that has silently stopped reading its
inputs, or from one whose perturbation never reached the code path being tested. An engine that
returns constants passes the negative clause perfectly.

WHY THE OLD PROBE MISSED THE REAL BUG. `MS-BBO-V1`'s L1 asserted `feature_ts < t < execution_ts`
for the quote lookups AT t, and passed with 0 violations -- correctly. It never examined the
thirty ROLLING-PATH offsets, which is where the overflow lived. Hence `probe_rolling_path` below:
for path features the engine must EMIT the min and max source timestamp it actually consumed, and
`max_source_ts < decision_ts` is asserted ROW BY ROW.

    "The helper uses side='left'" is not proof. Emit the timestamps you actually touched.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from timegrid import TimeArithmeticError, assert_strictly_before


@dataclass
class ProbeResult:
    name: str
    negative_pass: bool
    positive_pass: bool
    negative_max_delta: float
    positive_moved: dict = field(default_factory=dict)
    notes: str = ""

    @property
    def ok(self) -> bool:
        return self.negative_pass and self.positive_pass

    def report(self, emit=print) -> None:
        emit(f"    {self.name}")
        emit(f"      NEGATIVE  corrupt events AFTER cutoff -> max |dfeature| "
             f"{self.negative_max_delta:.3e}   "
             f"{'PASS' if self.negative_pass else '*** FAIL - LOOK-AHEAD ***'}")
        moved = sum(1 for v in self.positive_moved.values() if v)
        emit(f"      POSITIVE  perturb inside the information set -> "
             f"{moved}/{len(self.positive_moved)} families responded   "
             f"{'PASS' if self.positive_pass else '*** FAIL - PROBE HAS NO TEETH ***'}")
        for fam, mv in sorted(self.positive_moved.items()):
            if not mv:
                emit(f"        {fam:<24} DID NOT MOVE -- this family is not being tested")
        if self.notes:
            emit(f"      {self.notes}")


def two_sided_probe(recompute, events, cutoff_ts, families, *, corrupt,
                    tol: float = 0.0, name: str = "causality") -> ProbeResult:
    """Run both clauses.

    recompute(events) -> dict[str, np.ndarray]   feature name -> values at the decision grid
    events                                       whatever `recompute` consumes; opaque here
    cutoff_ts                                    the information cutoff (int64 ns)
    families    dict[str, list[str]]             feature-family name -> the feature names in it
    corrupt(events, mask_side, families_or_None) -> events
                mask_side in {"after", "before"}; must return a MODIFIED COPY, never mutate
    tol         allowed |delta| under the negative clause. Default 0.0 = bit-identical.
    """
    base = recompute(events)
    allnames = [f for fs in families.values() for f in fs]

    ev_after = corrupt(events, "after", None)
    got = recompute(ev_after)
    dmax = 0.0
    for f in allnames:
        a, b = np.asarray(base[f], float), np.asarray(got[f], float)
        m = ~(np.isnan(a) | np.isnan(b))
        if m.any():
            dmax = max(dmax, float(np.max(np.abs(a[m] - b[m]))))
        if (np.isnan(a) != np.isnan(b)).any():
            dmax = float("inf")
    neg = dmax <= tol

    moved = {}
    for fam, feats in families.items():
        ev_before = corrupt(events, "before", [fam])
        got = recompute(ev_before)
        mv = False
        for f in feats:
            a, b = np.asarray(base[f], float), np.asarray(got[f], float)
            m = ~(np.isnan(a) | np.isnan(b))
            if m.any() and float(np.max(np.abs(a[m] - b[m]))) > 0:
                mv = True
                break
        moved[fam] = mv
    pos = all(moved.values()) and len(moved) > 0
    return ProbeResult(name, neg, pos, dmax, moved,
                       "" if pos else "A family that does not respond to its own inputs is not "
                                      "being certified by this probe.")


def probe_rolling_path(min_source_ts, max_source_ts, decision_ts, *,
                       declared_lookback_s: float, label: str = "rolling path") -> dict:
    """For PATH features: assert row-by-row that the source window is strictly past AND that the
    window actually reaches as far back as declared.

    This is the assertion `bbo_v1.py` never made. It would have failed instantly.
    """
    lo = np.asarray(min_source_ts, dtype=np.int64)
    hi = np.asarray(max_source_ts, dtype=np.int64)
    d = np.asarray(decision_ts, dtype=np.int64)
    assert_strictly_before(hi, d, label)                        # the causality clause
    if np.any(lo > hi):
        raise TimeArithmeticError(f"{label}: min source ts exceeds max source ts")
    reach_s = (d - lo) / 1e9
    span_s = (hi - lo) / 1e9
    # the window must actually be a window: if it collapsed, the feature is not what it claims
    if float(np.median(span_s)) <= 0:
        raise TimeArithmeticError(f"{label}: source window has zero span -- not a path feature")
    if float(np.median(reach_s)) < 0.5 * declared_lookback_s:
        raise TimeArithmeticError(
            f"{label}: declared lookback {declared_lookback_s:.1f}s but the median window only "
            f"reaches {float(np.median(reach_s)):.3f}s back. Declared and actual must agree.")
    return {"n": int(d.size),
            "max_future_encroachment_s": float(np.max((hi - d) / 1e9)),
            "median_reach_s": float(np.median(reach_s)),
            "median_span_s": float(np.median(span_s)),
            "declared_lookback_s": float(declared_lookback_s)}
