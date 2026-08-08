"""SMV2I shared lib — leg reconstruction EXACTLY as runs/SMV2H_ONECONTRACT/rerank.py,
plus risk objectives (CDaR_a, EDaR_a entropic, Ulcer on $100k base) and bootstrap engines.

Frozen spec: runs/SMV2I_CURVE_READS/spec.yaml (seq 361-365). Seed 20260808 house default.
HARD: dev sessions <= 2026-05-31 only; no data >= 2026-08-01 is ever read (inputs end 2026-05-29).
"""
import os
import sys

import numpy as np
import pandas as pd

REPO = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(REPO, "runs", "SMV2I_CURVE_READS")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(REPO, "src", "analytics"))

SEED = 20260808
DEV_END = pd.Timestamp("2026-05-31")
FIT_END = pd.Timestamp("2024-12-31")   # fit 2022-01-01..2024-12-31, eval 2025-01-01..2026-05-31


def load_legs():
    """Reconstruct (DUAL, vmBM, SIG, vm, cal) exactly as rerank.py lines 45-53 did.

    DUAL   : SOLAR_DUAL_HTF daily $ (MNQ basis), from the published CSV artifact.
    BM     : BMOM E2 daily $ = sum(net_c1_ticks)*5.0 per sess, reindexed to DUAL calendar, 0-fill.
    SIG    : DUAL.std(ddof=1) over full dev window.
    vm(x)  : x * SIG / x.std(ddof=1)   (full-dev-window vol match, rerank convention).
    """
    dual = pd.read_csv(
        os.path.join(REPO, "runs", "SMV2H_ONECONTRACT", "out", "solar_dual_htf_daily.csv"),
        index_col=0)
    dual.index = pd.to_datetime(dual.index)
    DUAL = dual.iloc[:, 0].astype(float)
    assert DUAL.index.max() <= DEV_END, "VIRGIN guard: solar leg extends past dev window"
    cal = DUAL.index

    bm2 = pd.read_parquet(
        os.path.join(REPO, "runs", "SMV2B_BMOM_EXEC_AUDIT", "out", "ledger_E2_next_open.parquet"))
    BM = (bm2.groupby("sess")["net_c1_ticks"].sum() * 5.0)
    BM.index = pd.to_datetime(BM.index)
    assert BM.index.max() <= DEV_END, "VIRGIN guard: bmom ledger extends past dev window"
    BM = BM.reindex(cal).fillna(0.0)

    SIG = DUAL.std(ddof=1)

    def vm(x):
        return x * (SIG / x.std(ddof=1))

    return DUAL, BM, SIG, vm, cal


def champion(DUAL, BM, vm, w_solar=0.60):
    """Published champion construction: vm(w*DUAL + (1-w)*vm(BM))."""
    return vm(w_solar * DUAL + (1.0 - w_solar) * vm(BM))


def repro_gate(atol=1e-6):
    """MANDATORY: reproduce published 60/40 curve vs rerank_curves.csv to atol. Returns dict."""
    DUAL, BM, SIG, vm, cal = load_legs()
    rc = pd.read_csv(os.path.join(REPO, "runs", "SMV2H_ONECONTRACT", "out", "rerank_curves.csv"),
                     parse_dates=["sess"]).set_index("sess")
    out = {"n_days": len(cal), "cal_match": bool((rc.index == cal).all())}
    champ = champion(DUAL, BM, vm, 0.60)
    for col, series in [("60_40", champ), ("DUAL", DUAL), ("BM_E2", BM)]:
        d = np.abs(series.values - rc[col].values)
        out[f"maxabs_{col}"] = float(d.max())
    # full four published weights as extra confidence
    for wname, ws in [("80_20", .8), ("70_30", .7), ("50_50", .5)]:
        p = champion(DUAL, BM, vm, ws)
        out[f"maxabs_{wname}"] = float(np.abs(p.values - rc[wname].values).max())
    out["gate_60_40_atol1e-6"] = bool(out["maxabs_60_40"] <= atol)
    return out, DUAL, BM, SIG, vm, cal, champ


# ---------------------------------------------------------------- risk objectives

def dd_series(net):
    """EOD drawdown series in $ from daily net (window treated standalone)."""
    eq = np.cumsum(np.asarray(net, dtype=float))
    return np.maximum.accumulate(eq) - eq


def cdar(net, alpha=0.90):
    """Mean of the worst (1-alpha) fraction of the daily EOD drawdown distribution."""
    dd = np.sort(dd_series(net))[::-1]
    k = max(1, int((1.0 - alpha) * len(dd)))
    return float(dd[:k].mean())


def edar(net, alpha=0.90):
    """Entropic drawdown-at-risk: EDaR_a = min_{z>0} z*ln((1/(1-a)) * mean(exp(d_t/z))).
    1-D minimization over log z (scipy bounded), logsumexp for stability."""
    from scipy.optimize import minimize_scalar
    from scipy.special import logsumexp
    dd = dd_series(net)
    n = len(dd)
    la = np.log(1.0 - alpha)

    def f(u):
        z = np.exp(u)
        return z * (logsumexp(dd / z) - np.log(n) - la)

    r = minimize_scalar(f, bounds=(np.log(1e-2), np.log(1e9)), method="bounded",
                        options={"xatol": 1e-10, "maxiter": 500})
    return float(r.fun)


def ulcer_100k(net, base=100_000.0):
    """Ulcer index = sqrt(mean(d_pct^2)), d_pct = 100 * dd$/base ($100k notional base)."""
    dd = dd_series(net)
    return float(np.sqrt(np.mean((100.0 * dd / base) ** 2)))


def max_dd(net):
    return float(dd_series(net).max())


def tuw_series(net):
    """Days since the leg's own EOD equity high (0 at each new high)."""
    eq = np.cumsum(np.asarray(net, dtype=float))
    peak = np.maximum.accumulate(eq)
    tuw = np.zeros(len(eq), dtype=int)
    c = 0
    for i in range(len(eq)):
        c = 0 if eq[i] >= peak[i] - 1e-9 else c + 1
        tuw[i] = c
    return tuw


def rtc_ratio(policy, champ):
    """RTC floor read: policy PnL summed over champion top-decile up-days / champion's own sum.
    Top decile = the ceil(0.10*n) largest champion daily PnL days over the full dev window."""
    ch = np.asarray(champ, dtype=float)
    po = np.asarray(policy, dtype=float)
    k = int(np.ceil(0.10 * len(ch)))
    idx = np.argsort(ch)[::-1][:k]
    return float(po[idx].sum() / ch[idx].sum()), k


# ---------------------------------------------------------------- bootstrap engines

def maxdd_dist_moving(x, path_len=504, block=5, B=5000, seed=SEED):
    """Circular moving-block bootstrap: fixed block length, uniform starts."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    n = len(x)
    nb = int(np.ceil(path_len / block))
    starts = rng.integers(0, n, size=(B, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]).reshape(B, -1)[:, :path_len] % n
    paths = x[idx]
    eq = np.cumsum(paths, axis=1)
    dd = np.maximum.accumulate(eq, axis=1) - eq
    return dd.max(axis=1)


def maxdd_dist_stationary(x, path_len=504, mean_block=20, B=5000, seed=SEED,
                          joint_loss=None, oversample=2.0):
    """Politis-Romano stationary bootstrap: geometric block lengths (mean mean_block),
    uniform circular starts. If joint_loss (bool array len n) is given, block start
    probability is multiplied by `oversample` when the drawn block's circular window
    contains at least one joint-loss day."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    n = len(x)
    p = 1.0 / mean_block
    cache = {}
    if joint_loss is not None:
        J = np.asarray(joint_loss, dtype=float)
        cJ = np.concatenate([[0.0], np.cumsum(np.tile(J, 2))])

        def weights_for_len(L):
            w = cache.get(L)
            if w is None:
                s = np.arange(n)
                contains = (cJ[s + L] - cJ[s]) > 0
                w = np.where(contains, oversample, 1.0)
                w = np.cumsum(w)
                w /= w[-1]
                cache[L] = w
            return w

    out = np.empty(B)
    for b in range(B):
        pieces = []
        filled = 0
        while filled < path_len:
            L = int(min(rng.geometric(p), path_len))
            if joint_loss is None:
                s = int(rng.integers(0, n))
            else:
                cdf = weights_for_len(L)
                s = int(np.searchsorted(cdf, rng.random(), side="right"))
                s = min(s, n - 1)
            take = min(L, path_len - filled)
            pieces.append((np.arange(s, s + take)) % n)
            filled += take
        idx = np.concatenate(pieces)
        path = x[idx]
        eq = np.cumsum(path)
        out[b] = float((np.maximum.accumulate(eq) - eq).max())
    return out
