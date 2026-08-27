"""we_harness - the four validation primitives that each caught a real defect, plus their tests.

POST-W118 owner directive section 8 and 35. Three consecutive waves had harness defects, not market
findings, and each one would have corrupted a headline:

  W115  the causality CHECKER corrupted every session at once, so every trailing window moved and
        it reported LEAKAGE on three clean drivers.
  W116  the best-of-K null drew INDEPENDENT signs across fifteen highly-correlated timing cells,
        inflating the bar from $166 to $215 - enough to fail a real object.
  W118  an event gate was evaluated at a FIXED 12:00 clock instead of at the trigger bar, so the
        rule fired on the first two-point wiggle: median entry 09:32, 99.4 % of sessions.

Section 35 says: build these once, then stop. This module is deliberately small. It exports the
four primitives so future waves import them instead of re-deriving them, and `python we_harness.py`
runs the synthetic tests.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

__all__ = ["causal_trailing", "assert_causal_window", "family_null_shared_sign",
           "effective_k", "assert_event_gate", "run_all"]


# ---------------------------------------------------------------- A. causal features
def causal_trailing(x, k, q=None, minp=None):
    """Trailing statistic over the PRIOR k observations. The shift(1) is the whole point.

    q=None -> mean. Otherwise the q-quantile. Never includes observation i itself.
    """
    s = pd.Series(np.asarray(x, float)).rolling(k, min_periods=minp or max(10, k // 3))
    r = s.mean() if q is None else s.quantile(q)
    return r.shift(1).to_numpy()


def assert_causal_window(driver, raw, k, probes):
    """W115's REPAIRED check. Two tests, and the second must have teeth.

    (a) driver[i] must EQUAL the statistic of raw[i-k : i] - a window strictly preceding i.
    (b) perturbing raw[i] ALONE must leave driver[i] unchanged AND must move driver[i+1].

    The original check corrupted every observation at once, so (a) was untested and (b) could not
    distinguish a causal driver from a leaking one. Returns (ok, detail).
    """
    raw = np.asarray(raw, float)
    driver = np.asarray(driver, float)
    ident = all(
        (not np.isfinite(driver[i]))
        or np.isclose(driver[i], np.nanmean(raw[max(0, i - k):i]), rtol=1e-9, atol=1e-12)
        for i in probes)
    selfsafe = nextmoves = True
    for i in probes:
        c = raw.copy()
        c[i] = (c[i] if np.isfinite(c[i]) else 1.0) * 1e3 + 7.0
        d2 = causal_trailing(c, k)
        if np.isfinite(driver[i]) and not np.isclose(driver[i], d2[i], rtol=1e-12, atol=1e-15):
            selfsafe = False
        if i + 1 < len(driver) and np.isfinite(driver[i + 1]) \
                and np.isclose(driver[i + 1], d2[i + 1], rtol=1e-12, atol=1e-15):
            nextmoves = False
    return (ident and selfsafe and nextmoves), dict(window_identity=ident,
                                                    own_obs_cannot_move_it=selfsafe,
                                                    next_obs_does_move=nextmoves)


# ---------------------------------------------------------------- B. family-wise nulls
def effective_k(cell_pnls):
    """K / (1 + (K-1) * mean pairwise rho). W116b: 15 timing cells at rho +0.800 are 1.23 cells."""
    M = np.column_stack([np.asarray(c, float) for c in cell_pnls])
    C = pd.DataFrame(M).corr().to_numpy()
    iu = np.triu_indices(len(cell_pnls), 1)
    rbar = float(np.nanmean(C[iu]))
    K = len(cell_pnls)
    return K / (1.0 + (K - 1) * rbar), rbar


def family_null_shared_sign(cells, rng, nperm=2000):
    """W116b's CORRECTED best-of-K null: ONE coin flip per OBSERVATION, shared across all cells.

    `cells` is a list of (index_array, move_array, cost) - index_array indexes a common universe of
    size n_universe, so the same sign vector reaches every cell. Independent signs per cell destroy
    the family's dependence and inflate the maximum.
    Returns (max_distribution, mean_distribution).
    """
    n_uni = 1 + max(int(ix.max()) for ix, _, _ in cells if len(ix))
    mx = np.empty(nperm); mn = np.empty(nperm)
    for b in range(nperm):
        s = rng.choice([-1.0, 1.0], size=n_uni)
        vals = [float((s[ix] * mv - c).mean()) for ix, mv, c in cells if len(ix)]
        mx[b] = max(vals); mn[b] = float(np.mean(vals))
    return mx, mn


# ---------------------------------------------------------------- C. event-time gates
def assert_event_gate(trigger_times, gate_times, label=""):
    """W118's defect. A gate that is supposed to bind BEFORE the trigger must not be evaluated at a
    later fixed clock. Returns (ok, detail): ok iff every gate evaluation precedes or equals its own
    trigger. Also reports the realised trigger-time distribution, which is the cheapest tell that a
    supposedly-endogenous rule is actually firing at a fixed early minute."""
    t = np.asarray(trigger_times, float); g = np.asarray(gate_times, float)
    m = np.isfinite(t) & np.isfinite(g)
    ok = bool(np.all(g[m] <= t[m])) if m.sum() else False
    d = dict(n=int(m.sum()), gate_after_trigger=int((g[m] > t[m]).sum()),
             trig_p25=float(np.percentile(t[m], 25)) if m.sum() else np.nan,
             trig_median=float(np.median(t[m])) if m.sum() else np.nan,
             trig_p75=float(np.percentile(t[m], 75)) if m.sum() else np.nan, label=label)
    return ok, d


# ---------------------------------------------------------------- the tests
def run_all():
    rng = np.random.default_rng(0)
    P = print
    fails = []

    P("=" * 100)
    P("=== TEST A - CAUSAL FEATURE CHECKER")
    P("=" * 100)
    n = 800
    raw = rng.normal(0, 1, n)
    good = causal_trailing(raw, 60)                       # strictly prior: must PASS
    bad = pd.Series(raw).rolling(60, min_periods=20).mean().to_numpy()   # NO shift: must FAIL
    ahead = pd.Series(raw).rolling(60, min_periods=20).mean().shift(-1).to_numpy()  # future: FAIL
    probes = list(range(200, n - 2, 97))
    for lab, drv, want in (("causal (rolling+shift(1))", good, True),
                           ("no shift - includes own obs", bad, False),
                           ("shift(-1) - sees the future", ahead, False)):
        ok, d = assert_causal_window(drv, raw, 60, probes)
        good_ = (ok == want)
        fails.append(("A:" + lab, good_))
        P(f"    {lab:<32} -> {'PASS' if ok else 'FAIL'}   expected {'PASS' if want else 'FAIL'}"
          f"   {'OK' if good_ else '*** HARNESS BROKEN ***'}   {d}")

    P("")
    P("=" * 100)
    P("=== TEST B - MULTI-CANDIDATE NULL MUST PRESERVE DEPENDENCE")
    P("=" * 100)
    n_uni, K = 1000, 15
    base = rng.normal(0, 500, n_uni)
    cells = []
    for j in range(K):
        ix = np.arange(n_uni)
        mv = base + rng.normal(0, 150, n_uni)             # highly correlated by construction
        cells.append((ix, mv, 15.0))
    keff, rbar = effective_k([c[1] for c in cells])
    mx_s, _ = family_null_shared_sign(cells, rng, nperm=800)
    mx_i = np.empty(800)
    for b in range(800):
        mx_i[b] = max(float((rng.choice([-1.0, 1.0], size=n_uni) * mv - c).mean())
                      for _, mv, c in cells)
    p_s, p_i = float(np.percentile(mx_s, 95)), float(np.percentile(mx_i, 95))
    ok = p_i > p_s * 1.2
    fails.append(("B:independent-null-is-inflated", ok))
    P(f"    mean pairwise rho {rbar:+.3f}   effective K {keff:.2f} of {K}")
    P(f"    best-of-K p95, SHARED sign      ${p_s:,.1f}")
    P(f"    best-of-K p95, INDEPENDENT sign ${p_i:,.1f}   inflation x{p_i/max(p_s,1e-9):.2f}")
    P(f"    -> {'OK - the harness detects the inflation' if ok else '*** HARNESS BROKEN ***'}")

    P("")
    P("=" * 100)
    P("=== TEST C - EVENT GATE MUST BE EVALUATED AT THE TRIGGER, NOT A LATER CLOCK")
    P("=" * 100)
    trig = rng.integers(600, 860, 400).astype(float)
    ok1, d1 = assert_event_gate(trig, trig - rng.integers(0, 30, 400))     # gate before trigger
    ok2, d2 = assert_event_gate(trig, np.full(400, 720.0))                 # W118's bug: fixed 12:00
    fails.append(("C:gate-at-trigger-passes", ok1))
    fails.append(("C:fixed-clock-gate-fails", not ok2))
    P(f"    gate evaluated at/before trigger -> {'PASS' if ok1 else 'FAIL'}   expected PASS")
    P(f"    gate pinned to a fixed 12:00     -> {'PASS' if ok2 else 'FAIL'}   expected FAIL"
      f"   ({d2['gate_after_trigger']} of {d2['n']} gates land AFTER their trigger)")
    P(f"    realised trigger-time distribution is reported so an 'endogenous' rule firing at a")
    P(f"    fixed early minute is visible before any P&L: p25 {d1['trig_p25']:.0f} "
      f"median {d1['trig_median']:.0f} p75 {d1['trig_p75']:.0f}")

    P("")
    P("=" * 100)
    P("=== TEST D - SESSION ALIGNMENT with an early close and a missing session")
    P("=" * 100)
    sess, mods = [], []
    for s in range(5):
        last = 780 if s == 2 else 960                     # session 2 closes early at 13:00
        if s == 3:
            continue                                     # session 3 is missing entirely
        for m_ in range(571, last + 1):
            sess.append(s); mods.append(m_)
    sess = np.array(sess); mods = np.array(mods)
    NS = 5
    at944 = np.full(NS, np.nan)
    hit = (mods == 944)
    at944[sess[hit]] = 1.0
    have = np.isfinite(at944)
    ok = (not have[2]) and (not have[3]) and have[0] and have[1] and have[4]
    fails.append(("D:early-close-and-missing-session", ok))
    P(f"    sessions with a 15:44 bar: {sorted(np.flatnonzero(have).tolist())}   "
      f"expected [0, 1, 4]")
    P(f"    early-close session 2 correctly ABSENT: {not have[2]}")
    P(f"    missing session 3 correctly ABSENT:     {not have[3]}")
    P(f"    -> {'OK' if ok else '*** HARNESS BROKEN ***'}")

    P("")
    P("=" * 100)
    nf = [k for k, v in fails if not v]
    P(f"=== {len(fails) - len(nf)} of {len(fails)} checks OK"
      + ("" if not nf else f"   FAILURES: {nf}"))
    P("=" * 100)
    return len(nf) == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if run_all() else 1)
