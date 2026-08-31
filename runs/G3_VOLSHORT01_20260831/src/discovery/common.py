"""G3_VOLSHORT01 discovery helpers -- shared by every agent in this wave.

Import these rather than re-deriving them; the point is that all agents in this wave use the
SAME tercile convention, the SAME episode definition and the SAME cost ladder, so their tables
are comparable and a skeptic has one place to attack.

    import sys, os
    sys.path.insert(0, os.path.join(ROOT, "runs", "G3_VOLSHORT01_20260831", "src", "discovery"))
    import common as C

Everything here is DISCOVERY_CONTAMINATED machinery for building a RULE PROPOSAL. It never
reads data; it only transforms arrays you hand it. The 2022-01-01 wall is enforced in panel.py.

Self-test:  python runs/G3_VOLSHORT01_20260831/src/discovery/common.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------------
# constants
# ----------------------------------------------------------------------------------
PV = 20.0                       # NQ dollars per point

COST_FLOOR = 4.36               # commission only -- a FLOOR, never a headline
COST_PRIMARY = 20.65            # G2_EXEC01 measured all-in, 113 real round turns
COST_STRESS = 25.01
COSTS = (COST_FLOOR, COST_PRIMARY, COST_STRESS)
COST_NAMES = ("net_$4.36_FLOOR", "net_$20.65_PRIMARY", "net_$25.01_STRESS")

# a full-session 09:30->16:00 round turn must clear this many NQ points at the primary cost
BREAKEVEN_PTS_PRIMARY = COST_PRIMARY / PV      # = 1.0325


# ----------------------------------------------------------------------------------
# 1. causal tercile
# ----------------------------------------------------------------------------------
def causal_tercile(series, window: int = 252, min_obs: int | None = None) -> np.ndarray:
    """0 / 1 / 2 (low / mid / high) using ONLY strictly prior observations.

    For each position i the cutoffs are the 1/3 and 2/3 quantiles of ``values[i-window:i]``
    -- the value at i is classified but never contributes to its own cutoff. This is the
    only tercile any agent in this wave may use.

    window   trailing length in OBSERVATIONS (not calendar days). None -> expanding.
    min_obs  minimum non-NaN prior observations required; default = window (strict), so the
             first ``window`` positions are NaN by construction.

    Tie convention (stated, not discovered): ``v >= q67 -> 2`` is tested FIRST, then
    ``v <= q33 -> 0``, else 1. The high state takes precedence in a degenerate window.

    Returns float array with NaN where the state is undefined. NaN input -> NaN output.
    """
    v = np.asarray(pd.Series(series).astype(float).values, dtype=float)
    n = len(v)
    if min_obs is None:
        min_obs = window if window is not None else 2
    if min_obs < 2:
        raise ValueError("min_obs must be >= 2")
    out = np.full(n, np.nan)
    for i in range(n):
        if np.isnan(v[i]):
            continue
        lo = 0 if window is None else max(0, i - window)
        hist = v[lo:i]                                   # STRICTLY prior -- excludes i
        hist = hist[~np.isnan(hist)]
        if len(hist) < min_obs:
            continue
        q33, q67 = np.quantile(hist, [1.0 / 3.0, 2.0 / 3.0])
        if v[i] >= q67:
            out[i] = 2.0
        elif v[i] <= q33:
            out[i] = 0.0
        else:
            out[i] = 1.0
    return out


# ----------------------------------------------------------------------------------
# 2. episodes
# ----------------------------------------------------------------------------------
def episodes(mask, dates=None, gap_days: int = 10):
    """Maximal runs of a boolean state, separated by >= ``gap_days`` CALENDAR days.

    High-vol sessions arrive in episodes (2008, 2010, 2011, 2015, 2018, 2020 ...). Roughly
    600 raw high-VIX sessions cluster into perhaps 8-14 independent episodes, so the episode
    count -- not the session count -- is the sample size.

    mask   boolean array-like, or a pandas Series with a DatetimeIndex (index used as dates).
    dates  datetime array-like aligned to mask; required unless mask carries a DatetimeIndex.

    Returns a list of (start_date, end_date) pandas Timestamps, in chronological order.
    Two consecutive True sessions join the same episode iff their calendar gap is < gap_days.
    """
    m = pd.Series(mask)
    if dates is None:
        if not isinstance(m.index, pd.DatetimeIndex):
            raise ValueError("episodes(): pass dates=, or a Series with a DatetimeIndex")
        d = pd.DatetimeIndex(m.index)
    else:
        d = pd.DatetimeIndex(pd.to_datetime(pd.Series(dates).values))
    m = m.fillna(False).astype(bool).values
    if len(m) != len(d):
        raise ValueError(f"episodes(): mask len {len(m)} != dates len {len(d)}")

    sel = d[m]
    if len(sel) == 0:
        return []
    order = np.argsort(sel.values)
    sel = sel[order]
    out, start, prev = [], sel[0], sel[0]
    for cur in sel[1:]:
        if (cur - prev).days >= gap_days:
            out.append((start, prev))
            start = cur
        prev = cur
    out.append((start, prev))
    return out


def episode_ids(mask, dates=None, gap_days: int = 10) -> np.ndarray:
    """Integer episode id per position; -1 where mask is False. Aligned to ``mask``."""
    m = pd.Series(mask)
    if dates is None:
        if not isinstance(m.index, pd.DatetimeIndex):
            raise ValueError("episode_ids(): pass dates=, or a Series with a DatetimeIndex")
        d = pd.DatetimeIndex(m.index)
    else:
        d = pd.DatetimeIndex(pd.to_datetime(pd.Series(dates).values))
    mb = m.fillna(False).astype(bool).values
    eps = episodes(mb, d, gap_days=gap_days)
    ids = np.full(len(mb), -1, dtype=int)
    for k, (a, b) in enumerate(eps):
        ids[mb & np.asarray(d >= a) & np.asarray(d <= b)] = k
    return ids


def episode_table(mask, dates=None, gap_days: int = 10, values=None) -> pd.DataFrame:
    """Per-episode summary: id, start, end, span in calendar days, session count, and -- if
    ``values`` is given -- the episode's mean and sum of that value."""
    eps = episodes(mask, dates, gap_days=gap_days)
    ids = episode_ids(mask, dates, gap_days=gap_days)
    rows = []
    for k, (a, b) in enumerate(eps):
        sel = ids == k
        r = dict(episode=k, start=a, end=b, span_days=int((b - a).days) + 1,
                 n_sessions=int(sel.sum()))
        if values is not None:
            v = np.asarray(pd.Series(values).astype(float).values)[sel]
            v = v[~np.isnan(v)]
            r["mean"] = float(np.mean(v)) if len(v) else np.nan
            r["sum"] = float(np.sum(v)) if len(v) else np.nan
        rows.append(r)
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------------------
# 3. whole-episode block bootstrap
# ----------------------------------------------------------------------------------
def block_bootstrap_by_episode(values, ep_ids, n_draws: int = 10000,
                               seed: int = 0) -> np.ndarray:
    """Distribution of the MEAN under resampling WHOLE EPISODES with replacement.

    Sessions inside an episode are not independent, so the resampling unit is the episode.
    K episodes are drawn K times with replacement, their sessions pooled, and the pooled mean
    recorded. Longer episodes therefore carry more weight, which is correct for a per-session
    mean.

    Returns ndarray of length n_draws. Session-level t-statistics are BANNED as inference in
    this wave; this is the substitute.
    """
    v = np.asarray(pd.Series(values).astype(float).values, dtype=float)
    e = np.asarray(pd.Series(ep_ids).values)
    if len(v) != len(e):
        raise ValueError(f"values len {len(v)} != ep_ids len {len(e)}")
    ok = (~np.isnan(v)) & (e >= 0)
    v, e = v[ok], e[ok].astype(int)
    if len(v) == 0:
        return np.full(n_draws, np.nan)
    groups = [v[e == k] for k in np.unique(e)]
    groups = [g for g in groups if len(g)]
    K = len(groups)
    if K == 0:
        return np.full(n_draws, np.nan)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, K, size=(n_draws, K))
    out = np.empty(n_draws)
    for j in range(n_draws):
        out[j] = np.concatenate([groups[i] for i in idx[j]]).mean()
    return out


def bootstrap_summary(draws, observed: float | None = None, alpha: float = 0.05) -> dict:
    """Percentile CI and a two-sided 'is zero in the distribution' p-value."""
    d = np.asarray(draws, dtype=float)
    d = d[~np.isnan(d)]
    if len(d) == 0:
        return dict(n_draws=0, mean=np.nan, se=np.nan, ci_lo=np.nan, ci_hi=np.nan,
                    p_two_sided=np.nan, excludes_zero=False, observed=observed)
    lo, hi = np.quantile(d, [alpha / 2.0, 1.0 - alpha / 2.0])
    p = 2.0 * min((d <= 0).mean(), (d >= 0).mean())
    return dict(n_draws=len(d), mean=float(d.mean()), se=float(d.std(ddof=1)),
                ci_lo=float(lo), ci_hi=float(hi), p_two_sided=float(min(p, 1.0)),
                excludes_zero=bool(lo > 0 or hi < 0), observed=observed)


# ----------------------------------------------------------------------------------
# 4. effective sample size
# ----------------------------------------------------------------------------------
def k_eff(K: int, rho_bar: float) -> float:
    """K_eff = K / (1 + (K-1) * rho_bar).  rho_bar MUST be printed wherever this is used."""
    if K <= 0:
        return 0.0
    return float(K) / (1.0 + (K - 1) * float(rho_bar))


def icc_rho(values, ep_ids) -> float:
    """Intraclass correlation = between-episode variance share. This is the rho_bar to feed
    k_eff() when the correlated family is 'sessions inside one episode'. Clamped to [0, 1]."""
    v = np.asarray(pd.Series(values).astype(float).values, dtype=float)
    e = np.asarray(pd.Series(ep_ids).values)
    ok = (~np.isnan(v)) & (e >= 0)
    v, e = v[ok], e[ok].astype(int)
    if len(v) < 2:
        return np.nan
    grand = v.mean()
    ks = np.unique(e)
    if len(ks) < 2:
        return np.nan
    between = sum(len(v[e == k]) * (v[e == k].mean() - grand) ** 2 for k in ks)
    total = float(((v - grand) ** 2).sum())
    if total <= 0:
        return np.nan
    return float(min(max(between / total, 0.0), 1.0))


# ----------------------------------------------------------------------------------
# 5. money
# ----------------------------------------------------------------------------------
def net_per_session(returns_pts, cost_per_ctrRT: float, traded=None,
                    pv: float = PV) -> np.ndarray:
    """Dollars per session for ONE contract: pts * $20 - cost, one round turn per session.

    returns_pts  ALREADY SIGNED by the position (short sessions carry the negated move).
    traded       boolean; sessions where False pay no cost and earn nothing (flat).
                 Default: traded wherever returns_pts is not NaN.

    A session is one round turn (enter 09:30, exit 16:00, flat overnight), so the cost is
    charged once per traded session regardless of direction.
    """
    r = np.asarray(pd.Series(returns_pts).astype(float).values, dtype=float)
    t = (~np.isnan(r)) if traded is None else \
        np.asarray(pd.Series(traded).fillna(False).astype(bool).values)
    out = np.where(t, np.nan_to_num(r, nan=0.0) * pv - float(cost_per_ctrRT), 0.0)
    return out


# ----------------------------------------------------------------------------------
# 6. the three arms
# ----------------------------------------------------------------------------------
def three_arms(panel: pd.DataFrame, state_col: str, high_state=2, low_state=0,
               ret_col: str = "rth_ret_pts", date_col: str = "session_date",
               gap_days: int = 10, costs=COSTS) -> pd.DataFrame:
    """The (R)/(F)/(S) table. Print all three or the result is INADMISSIBLE.

      BASE  always-long on every valid session          (context, not one of the three)
      R     ROUTER : long on the long leg, SHORT on high_state
      F     FILTER : long on the long leg, FLAT on high_state (removed, no short taken)
      S     SHORT  : short on high_state ALONE, nothing else

    Two long-leg conventions are reported because they answer different questions and
    picking one silently is how this gets fudged:
      long_leg='low_only'  long only in low_state, flat in mid  (the literal router)
      long_leg='non_high'  long on every non-high session       (the honest long-only baseline
                                                                 a filter would be compared to)
    By construction R = F + S in gross points for BOTH conventions; the identity is asserted.

    THE DIAGNOSTIC: if net(R) ~ net(F), the 'router' is exposure reduction wearing a costume
    -- the short leg adds nothing and the candidate is dead under this repo's closed
    anti-filter family (ten for ten against random controls). Equivalently: net(S) ~ 0.

    Sessions with a NaN state or a NaN return are excluded from EVERY arm, so all arms see the
    identical population.
    """
    p = panel
    st = pd.Series(p[state_col]).astype(float).values
    r = pd.Series(p[ret_col]).astype(float).values
    dates = pd.DatetimeIndex(pd.to_datetime(p[date_col]))

    valid = (~np.isnan(st)) & (~np.isnan(r))
    hi = valid & (st == float(high_state))
    lo = valid & (st == float(low_state))
    nonhi = valid & ~hi

    eps = episodes(hi, dates, gap_days=gap_days)
    eids = episode_ids(hi, dates, gap_days=gap_days)
    short_pnl = np.where(hi, -r, np.nan)
    rho = icc_rho(short_pnl, eids)
    K = len(eps)

    rows = []

    def add(arm, long_leg, pos):
        """pos: +1 long, -1 short, 0 flat, per session."""
        traded = valid & (pos != 0)
        signed = np.where(traded, pos * np.nan_to_num(r, nan=0.0), np.nan)
        rec = dict(
            arm=arm, long_leg=long_leg,
            n_sessions=int(valid.sum()), n_trades=int(traded.sum()),
            n_long=int((valid & (pos > 0)).sum()), n_short=int((valid & (pos < 0)).sum()),
            gross_pts=float(np.nansum(signed)),
            mean_pts_per_trade=float(np.nanmean(signed)) if traded.any() else np.nan,
        )
        for c, nm in zip(costs, COST_NAMES):
            rec[nm] = float(net_per_session(signed, c, traded=traded).sum())
        rec["high_episodes_K"] = K
        rec["rho_bar"] = rho
        rec["K_eff"] = k_eff(K, rho) if not np.isnan(rho) else np.nan
        rows.append(rec)
        return signed

    z = np.zeros(len(r))
    add("BASE_always_long", "-", np.where(valid, 1.0, 0.0))

    g = {}
    for leg, longmask in (("low_only", lo), ("non_high", nonhi)):
        pos_f = np.where(longmask, 1.0, 0.0)
        pos_r = np.where(longmask, 1.0, np.where(hi, -1.0, 0.0))
        g[("F", leg)] = add("F_filter", leg, pos_f)
        g[("R", leg)] = add("R_router", leg, pos_r)
    g["S"] = add("S_short_only", "-", np.where(hi, -1.0, z))

    tab = pd.DataFrame(rows)
    tab = tab.set_index(["arm", "long_leg"]).loc[
        [("BASE_always_long", "-"),
         ("R_router", "low_only"), ("F_filter", "low_only"),
         ("R_router", "non_high"), ("F_filter", "non_high"),
         ("S_short_only", "-")]].reset_index()

    # identity check: R = F + S in gross points, for both long-leg conventions
    tab.attrs["identity"] = {}
    for leg in ("low_only", "non_high"):
        d = abs(np.nansum(g[("R", leg)])
                - (np.nansum(g[("F", leg)]) + np.nansum(g["S"])))
        tab.attrs["identity"][leg] = float(d)
    tab.attrs["episodes"] = eps
    tab.attrs["K"] = K
    tab.attrs["rho_bar"] = rho
    return tab


def format_arms(tab: pd.DataFrame) -> str:
    """Fixed-width render of a three_arms() table, identity check included."""
    cols = ["arm", "long_leg", "n_trades", "n_long", "n_short", "gross_pts",
            "mean_pts_per_trade"] + list(COST_NAMES) + ["high_episodes_K", "rho_bar", "K_eff"]
    L = [f"{'arm':<17s} {'long_leg':<9s} {'trades':>7s} {'long':>6s} {'short':>6s} "
         f"{'gross_pts':>11s} {'pts/trade':>10s} {'net$4.36':>12s} {'net$20.65':>12s} "
         f"{'net$25.01':>12s} {'K':>4s} {'rho':>6s} {'K_eff':>6s}"]
    for _, r in tab.iterrows():
        L.append(f"{r['arm']:<17s} {r['long_leg']:<9s} {r['n_trades']:>7,} {r['n_long']:>6,} "
                 f"{r['n_short']:>6,} {r['gross_pts']:>11,.1f} "
                 f"{r['mean_pts_per_trade']:>10.3f} {r[COST_NAMES[0]]:>12,.0f} "
                 f"{r[COST_NAMES[1]]:>12,.0f} {r[COST_NAMES[2]]:>12,.0f} "
                 f"{r['high_episodes_K']:>4d} {r['rho_bar']:>6.3f} {r['K_eff']:>6.2f}")
    ident = tab.attrs.get("identity", {})
    for leg, d in ident.items():
        L.append(f"  identity check  R = F + S  ({leg}): |diff| = {d:.9f}  "
                 f"-> {'PASS' if d < 1e-6 else 'FAIL'}")
    L.append("  DIAGNOSTIC: if net(R) ~ net(F) the router is exposure reduction in a costume.")
    return "\n".join(L)


# ==================================================================================
# SELF-TEST
# ==================================================================================
def _selftest() -> int:
    res = []

    def chk(name, ok, detail=""):
        res.append((name, bool(ok), detail))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))

    print("=" * 92)
    print("common.py SELF-TEST")
    print("=" * 92)

    # ---- 1. causal_tercile, hand-computable ----------------------------------
    print("\n[1] causal_tercile -- hand-computable")
    v = [10, 20, 30, 40, 50, 5, 60]
    got = causal_tercile(v, window=5, min_obs=5)
    # i=0..4: fewer than 5 prior obs -> NaN
    # i=5: hist=[10,20,30,40,50] -> q33=23.333, q67=36.667; v=5  <= q33 -> 0
    # i=6: hist=[20,30,40,50,5]  -> q33=23.333, q67=36.667; v=60 >= q67 -> 2
    chk("first `window` positions are NaN", bool(np.all(np.isnan(got[:5]))), f"{got[:5]}")
    chk("v=5 after [10..50] -> state 0 (low)", got[5] == 0.0, f"got {got[5]}")
    chk("v=60 after [20,30,40,50,5] -> state 2 (high)", got[6] == 2.0, f"got {got[6]}")
    q33, q67 = np.quantile([10, 20, 30, 40, 50], [1 / 3, 2 / 3])
    chk("cutoffs are the strictly-prior 1/3 and 2/3 quantiles",
        abs(q33 - 23.3333333) < 1e-6 and abs(q67 - 36.6666667) < 1e-6,
        f"q33={q33:.4f} q67={q67:.4f}")
    mid = causal_tercile([10, 20, 30, 40, 50, 30], window=5, min_obs=5)
    chk("v=30 (between cutoffs) -> state 1 (mid)", mid[5] == 1.0, f"got {mid[5]}")

    # ---- 2. causal_tercile uses NO future observation -------------------------
    print("\n[2] causal_tercile -- future-shuffle invariance (the leak test)")
    rng = np.random.default_rng(7)
    x = rng.normal(size=500).cumsum() + 50
    base = causal_tercile(x, window=100)
    CUT = 300
    y = x.copy()
    tail = y[CUT + 1:].copy()
    rng.shuffle(tail)
    y[CUT + 1:] = tail
    shuf = causal_tercile(y, window=100)
    same = np.array_equal(np.nan_to_num(base[:CUT + 1], nan=-9),
                          np.nan_to_num(shuf[:CUT + 1], nan=-9))
    chk("shuffling the FUTURE tail leaves every earlier output unchanged", same,
        f"compared {CUT+1} positions")
    chk("the shuffle actually changed the future (test is not vacuous)",
        not np.array_equal(np.nan_to_num(base[CUT + 1:], nan=-9),
                           np.nan_to_num(shuf[CUT + 1:], nan=-9)))
    y2 = x.copy()
    y2[400] += 1000.0
    chk("perturbing x[400] does not change output[399]",
        np.nan_to_num(causal_tercile(y2, window=100)[399], nan=-9)
        == np.nan_to_num(base[399], nan=-9))
    chk("perturbing x[400] DOES change output[400] (not vacuous)",
        causal_tercile(y2, window=100)[400] == 2.0 and base[400] != 2.0)

    # ---- 3. episodes ---------------------------------------------------------
    print("\n[3] episodes -- hand-computable, gap boundary")
    d = pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-04", "2020-01-05",
                        "2020-01-20", "2020-01-21", "2020-01-22", "2020-01-25",
                        "2020-03-01"])
    m = [True] * 9 + [False]
    eps = episodes(m, d, gap_days=10)
    chk("3 runs with a 15-day and a 3-day gap -> 2 episodes", len(eps) == 2, f"{eps}")
    chk("episode 1 = 01-01 .. 01-05",
        eps[0][0] == pd.Timestamp("2020-01-01") and eps[0][1] == pd.Timestamp("2020-01-05"))
    chk("episode 2 = 01-20 .. 01-25 (3-day gap does NOT split)",
        eps[1][0] == pd.Timestamp("2020-01-20") and eps[1][1] == pd.Timestamp("2020-01-25"))
    chk("False sessions never join an episode",
        len(episode_table(m, d)) == 2
        and int(episode_table(m, d)["n_sessions"].sum()) == 9)
    d2 = pd.to_datetime(["2020-01-05", "2020-01-15"])       # gap exactly 10 -> splits
    d3 = pd.to_datetime(["2020-01-05", "2020-01-14"])       # gap 9          -> joins
    chk("gap of exactly 10 days SPLITS (>= gap_days)",
        len(episodes([True, True], d2, gap_days=10)) == 2)
    chk("gap of 9 days JOINS", len(episodes([True, True], d3, gap_days=10)) == 1)
    ids = episode_ids(m, d, gap_days=10)
    chk("episode_ids: -1 off-state, 0/1 on-state",
        list(ids) == [0, 0, 0, 0, 0, 1, 1, 1, 1, -1], f"{list(ids)}")
    chk("empty mask -> no episodes", episodes([False] * 5, d[:5]) == [])

    # ---- 4. block bootstrap: planted effect MUST be detected -------------------
    print("\n[4] block_bootstrap_by_episode -- planted effect must be DETECTED")
    K, NPE = 12, 30
    eff = np.full(K, 1.0)
    vals = np.concatenate([e + 0.01 * np.sin(np.arange(NPE) + i)
                           for i, e in enumerate(eff)])
    ids4 = np.repeat(np.arange(K), NPE)
    s4 = bootstrap_summary(block_bootstrap_by_episode(vals, ids4, 4000, seed=1))
    chk("12 episodes all at +1.0 -> CI excludes zero", s4["excludes_zero"],
        f"mean={s4['mean']:.4f} CI=[{s4['ci_lo']:.4f},{s4['ci_hi']:.4f}] p={s4['p_two_sided']:.4f}")

    # ---- 5. block bootstrap: pure noise MUST NOT be detected -------------------
    print("\n[5] block_bootstrap_by_episode -- pure noise must NOT be detected")
    eff0 = np.array([-1.1, -0.9, -0.7, -0.5, -0.3, -0.1, 0.1, 0.3, 0.5, 0.7, 0.9, 1.1])
    chk("planted null is exactly mean-zero by construction", abs(eff0.mean()) < 1e-12)
    vals0 = np.concatenate([e + 0.01 * np.sin(np.arange(NPE) + i)
                            for i, e in enumerate(eff0)])
    s5 = bootstrap_summary(block_bootstrap_by_episode(vals0, ids4, 4000, seed=1))
    chk("mean-zero episode effects -> CI CONTAINS zero", not s5["excludes_zero"],
        f"mean={s5['mean']:.4f} CI=[{s5['ci_lo']:.4f},{s5['ci_hi']:.4f}] p={s5['p_two_sided']:.4f}")

    # ---- 6. clustering actually widens the interval ---------------------------
    print("\n[6] the episode block is doing work -- clustered SE >> naive SE")
    rng6 = np.random.default_rng(3)
    shared = rng6.normal(size=K)
    clustered = np.concatenate([s + 0.01 * rng6.normal(size=NPE) for s in shared])
    se_naive_c = clustered.std(ddof=1) / np.sqrt(len(clustered))
    se_block_c = bootstrap_summary(
        block_bootstrap_by_episode(clustered, ids4, 4000, seed=2))["se"]
    iid = rng6.normal(size=K * NPE)
    se_naive_i = iid.std(ddof=1) / np.sqrt(len(iid))
    se_block_i = bootstrap_summary(
        block_bootstrap_by_episode(iid, ids4, 4000, seed=2))["se"]
    chk("clustered data: block SE is >3x the naive session-level SE",
        se_block_c / se_naive_c > 3.0,
        f"block={se_block_c:.4f} naive={se_naive_c:.4f} ratio={se_block_c/se_naive_c:.2f}")
    chk("i.i.d. data: block SE ~ naive SE (block is not just inflating everything)",
        0.5 < se_block_i / se_naive_i < 2.0,
        f"block={se_block_i:.4f} naive={se_naive_i:.4f} ratio={se_block_i/se_naive_i:.2f}")
    chk("icc_rho ~ 1 on clustered data", icc_rho(clustered, ids4) > 0.98,
        f"rho={icc_rho(clustered, ids4):.4f}")
    chk("icc_rho ~ 0 on i.i.d. data", icc_rho(iid, ids4) < 0.10,
        f"rho={icc_rho(iid, ids4):.4f}")

    # ---- 7. k_eff -------------------------------------------------------------
    print("\n[7] k_eff -- hand-computable")
    chk("K=10, rho=0.5 -> 10/(1+9*0.5) = 1.8182", abs(k_eff(10, 0.5) - 1.8181818) < 1e-6,
        f"{k_eff(10, 0.5):.6f}")
    chk("rho=0 -> K_eff == K", k_eff(10, 0.0) == 10.0)
    chk("rho=1 -> K_eff == 1", abs(k_eff(10, 1.0) - 1.0) < 1e-12)

    # ---- 8. net_per_session ---------------------------------------------------
    print("\n[8] net_per_session -- hand-computable, PV=20")
    n8 = net_per_session([2.0, -1.0, 0.0], COST_PRIMARY)
    chk("+2.00 pts @ $20.65 -> 2*20 - 20.65 = $19.35", abs(n8[0] - 19.35) < 1e-9, f"{n8[0]}")
    chk("-1.00 pts @ $20.65 -> -1*20 - 20.65 = -$40.65", abs(n8[1] + 40.65) < 1e-9, f"{n8[1]}")
    chk("0 pts still pays the round turn -> -$20.65", abs(n8[2] + 20.65) < 1e-9, f"{n8[2]}")
    n8b = net_per_session([2.0, -1.0, 0.0], COST_PRIMARY, traded=[True, True, False])
    chk("an untraded session costs nothing and earns nothing", n8b[2] == 0.0, f"{n8b[2]}")
    chk("breakeven at the primary cost is 1.0325 pts, not 0.9",
        abs(BREAKEVEN_PTS_PRIMARY - 1.0325) < 1e-9, f"{BREAKEVEN_PTS_PRIMARY}")

    # ---- 9. three_arms --------------------------------------------------------
    print("\n[9] three_arms -- hand-computable 6-session panel")
    tp = pd.DataFrame({
        "session_date": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03",
                                        "2020-06-01", "2020-06-02", "2020-06-03"]),
        "state": [0.0, 1.0, 2.0, 0.0, 1.0, 2.0],
        "rth_ret_pts": [10.0, 4.0, -6.0, 2.0, -3.0, -8.0],
    })
    t9 = three_arms(tp, "state", high_state=2, low_state=0)
    row = lambda a, l: t9[(t9["arm"] == a) & (t9["long_leg"] == l)].iloc[0]
    # BASE = 10+4-6+2-3-8 = -1 ; S = -(-6) + -(-8) = +14
    # F[low_only] = 10+2 = 12 ; R[low_only] = 12+14 = 26
    # F[non_high] = 10+4+2-3 = 13 ; R[non_high] = 13+14 = 27
    chk("BASE gross = -1.0", abs(row("BASE_always_long", "-")["gross_pts"] + 1.0) < 1e-9)
    chk("S (short the 2 high sessions) gross = +14.0",
        abs(row("S_short_only", "-")["gross_pts"] - 14.0) < 1e-9)
    chk("F[low_only] gross = 12.0", abs(row("F_filter", "low_only")["gross_pts"] - 12.0) < 1e-9)
    chk("R[low_only] gross = 26.0", abs(row("R_router", "low_only")["gross_pts"] - 26.0) < 1e-9)
    chk("F[non_high] gross = 13.0",
        abs(row("F_filter", "non_high")["gross_pts"] - 13.0) < 1e-9)
    chk("R[non_high] gross = 27.0",
        abs(row("R_router", "non_high")["gross_pts"] - 27.0) < 1e-9)
    chk("identity R = F + S holds for both long legs",
        all(v < 1e-9 for v in t9.attrs["identity"].values()), f"{t9.attrs['identity']}")
    chk("S trades exactly the 2 high sessions",
        row("S_short_only", "-")["n_trades"] == 2
        and row("S_short_only", "-")["n_short"] == 2)
    # net(S) at $20.65 = 14*20 - 2*20.65 = 280 - 41.30 = 238.70
    chk("net(S) @ $20.65 = 14*20 - 2*20.65 = $238.70",
        abs(row("S_short_only", "-")[COST_NAMES[1]] - 238.70) < 1e-9,
        f"{row('S_short_only','-')[COST_NAMES[1]]}")
    chk("high state is 2 episodes (Jan and Jun)", t9.attrs["K"] == 2, f"K={t9.attrs['K']}")
    chk("all three required arms are present in the table",
        {"R_router", "F_filter", "S_short_only"} <= set(t9["arm"]))

    # NaN state / NaN return must drop from EVERY arm identically
    tp2 = tp.copy()
    tp2.loc[1, "state"] = np.nan
    tp2.loc[4, "rth_ret_pts"] = np.nan
    t9b = three_arms(tp2, "state", 2, 0)
    chk("NaN state or NaN return excluded from every arm (same population)",
        t9b["n_sessions"].nunique() == 1 and int(t9b["n_sessions"].iloc[0]) == 4,
        f"n_sessions={int(t9b['n_sessions'].iloc[0])}")

    # ---- 10. the two stated death conditions are ONE condition -----------------
    print("\n[10] net(R) - net(F) == net(S) EXACTLY, in net dollars, costs included")
    print("     (an algebraic identity, asserted -- not a discovery. Its consequence is what")
    print("      matters: 'net(R) ~ net(F)' and 'net(S) ~ 0' are the SAME test, so the wave")
    print("      cannot pass one death condition and fail the other.)")
    rng10 = np.random.default_rng(11)
    n = 900
    dts = pd.bdate_range("2010-01-01", periods=n)
    state = np.tile([0.0, 1.0, 2.0], n // 3)
    ret = rng10.normal(0.0, 10.0, n)                 # high state has NO edge, only noise
    ret[state == 2] -= 0.0
    t10 = three_arms(pd.DataFrame({"session_date": dts, "state": state,
                                   "rth_ret_pts": ret}), "state", 2, 0)
    r10 = t10[(t10["arm"] == "R_router") & (t10["long_leg"] == "non_high")].iloc[0]
    f10 = t10[(t10["arm"] == "F_filter") & (t10["long_leg"] == "non_high")].iloc[0]
    s10 = t10[t10["arm"] == "S_short_only"].iloc[0]
    diff = r10[COST_NAMES[1]] - f10[COST_NAMES[1]]
    chk("net(R) - net(F) == net(S) exactly, on 900 sessions, costs included",
        abs(diff - s10[COST_NAMES[1]]) < 1e-6,
        f"R-F={diff:,.2f}  S={s10[COST_NAMES[1]]:,.2f}")
    chk("SUBSTANTIVE: with no planted short edge, net(S) < 0 once the short leg pays "
        "the real $20.65 round turn",
        s10[COST_NAMES[1]] < 0, f"net(S)=${s10[COST_NAMES[1]]:,.0f} on "
        f"{int(s10['n_trades'])} shorts")
    # and the converse: a REAL planted short edge must survive the same cost
    ret10b = ret.copy()
    ret10b[state == 2] -= 3.0                        # +3 pts to a short, > the 1.03 pt floor
    t10b = three_arms(pd.DataFrame({"session_date": dts, "state": state,
                                    "rth_ret_pts": ret10b}), "state", 2, 0)
    s10b = t10b[t10b["arm"] == "S_short_only"].iloc[0]
    chk("SUBSTANTIVE: a planted -3.0 pt drift in the high state DOES survive $20.65",
        s10b[COST_NAMES[1]] > 0, f"net(S)=${s10b[COST_NAMES[1]]:,.0f}")

    print("\n" + "-" * 92)
    print(format_arms(t9))
    print("-" * 92)

    n_ok = sum(1 for _, ok, _ in res if ok)
    print(f"\nSELF-TEST TALLY: {n_ok}/{len(res)} PASS, {len(res)-n_ok} FAIL")
    if n_ok != len(res):
        print("FAILED CHECKS:")
        for nm, ok, det in res:
            if not ok:
                print(f"  - {nm}  {det}")
    return 0 if n_ok == len(res) else 1


if __name__ == "__main__":
    raise SystemExit(_selftest())
