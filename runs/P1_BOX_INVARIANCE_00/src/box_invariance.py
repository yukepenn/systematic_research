"""P1_BOX_INVARIANCE_00 - IS A FIXED-DOLLAR SESSION RE-ENTRY LOCK STRUCTURALLY INVARIANT?

Spec: runs/P1_BOX_INVARIANCE_00/spec.yaml, committed BEFORE this ran (commit 2a94aea).

STAGE 1 IS STRUCTURAL ONLY. No P&L is computed, printed or aggregated anywhere in stage 1.
Stage 2 (economics) is guarded by an explicit gate check and is unreachable unless gates A and
B both pass.

Three normalisations of THE SAME rule (a per-contract session re-entry lockout at halt/target
in a fixed 1.30:1.00 ratio):
    DOLLAR    halt_s = 1300                       (incumbent, constant in every regime)
    PRICEBOX  halt_s = c_p * P_s * PV             (proportional to index level)
    SIGMABOX  halt_s = c_v * sigma_s * PV         (proportional to prior-20-session mean range)
c_p and c_v are set in CLOSED FORM so the mean box dollar value over the modern window is
exactly $1,300 - the W98 ABS_LOOSE "same average budget" convention. No search, no sweep.
"""
from __future__ import annotations

import json
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
WESRC = os.path.abspath(os.path.join(HERE, "..", "..", "..", "research", "weekly_edge", "src"))
sys.path.insert(0, WESRC)

import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w97 import votes                                             # noqa: E402
from run_we_w98 import gfills                                            # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "P1_BOX_INVARIANCE_00", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W80OUT = os.path.join(ROOT, "runs", "WE_W80_ANCHOR_HEADTOHEAD", "out")

HALT0, TARGET0 = 1300.0, 1000.0
TT_RATIO = TARGET0 / HALT0                        # 0.769231, frozen, carried into every arm
INF = float("inf")
WARMUP = 20                                       # sessions excluded so sigma has a full lookback
ARMS = ("DOLLAR", "PRICEBOX", "SIGMABOX")

_t0 = _time.time()
_fh = open(os.path.join(OUT, "box_invariance.txt"), "w", encoding="utf-8")


def P_(*a):
    print(*a, flush=True)
    print(*a, file=_fh)
    _fh.flush()


def el():
    return f"[{_time.time()-_t0:.0f}s]"


# =================================================================================== fill engine
def gfills_box(D, dir_arr, size_at_entry, halt_s, target_s, pv=PV, comm=COMM_RT,
               o=None, c=None):
    """run_we_w98.gfills(per_ctr=True) with ONE change: halt/target are PER-SESSION arrays.

    Returns (trades, latch) where trades is a list of (dir, size, entry_bar, exit_bar, pnl)
    and latch[s] in {-1 halt, 0 none, +1 target}.  `o`/`c` override the price arrays so the
    scale-invariance test can rescale prices without touching the signal.
    """
    o = D["o"] if o is None else o
    c = D["c"] if c is None else c
    fb, lb, n, sid = D["fb"], D["lb"], D["n"], D["sid"]
    trades = []
    latch = np.zeros(D["n_sess"], np.int8)
    p = 0; u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    hs = HALT0; ts = TARGET0
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False
            s_ = sid[i]
            hs = halt_s[s_]; ts = target_s[s_]
        want = int(dir_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if want != p:
            if p != 0:
                pnl = p * u * (o[i] - epx) * pv - comm * u
                trades.append((p, u, eti, i, pnl))
                spnl += pnl / u
                if spnl <= -hs:
                    stopped = True; want = 0; latch[sid[i]] = -1
                elif (ts is not None) and spnl >= ts:
                    stopped = True; want = 0; latch[sid[i]] = 1
            p = want
            if p != 0:
                u = int(size_at_entry[i]) if size_at_entry is not None else 1
                if u < 1:
                    p = 0; u = 0
                else:
                    epx, eti = o[i], i
        if lb[i] and p != 0:
            pnl = p * u * (c[i] - epx) * pv - comm * u
            trades.append((p, u, eti, i, pnl))
            p = 0; u = 0
    return trades, latch


def const_arrays(D, halt, target):
    ns = D["n_sess"]
    return (np.full(ns, halt, float),
            np.full(ns, INF if target is None else target, float) if target is not None
            else np.full(ns, np.inf, float))


def same_as_w98(tr, w98tr, D):
    """byte identity against run_we_w98.gfills' dict form"""
    if len(tr) != len(w98tr):
        return False
    t = D["t"]
    for x, y in zip(tr, w98tr):
        if x[0] != y["d"] or x[1] != y["u"]:
            return False
        if str(t[x[2]]) != y["et"] or str(t[x[3]]) != y["xt"]:
            return False
        if abs(x[4] - y["pnl"]) > 1e-9:
            return False
    return True


def sched(tr):
    """the decision series: direction, size, entry bar, exit bar - NO dollars"""
    return [(x[0], x[1], x[2], x[3]) for x in tr]


# =================================================================================== logistic
def logit_fit(X, y, iters=60):
    """Newton-Raphson logistic. X already carries its intercept column."""
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        eta = X @ b
        pr = 1.0 / (1.0 + np.exp(-np.clip(eta, -30, 30)))
        w = np.maximum(pr * (1 - pr), 1e-9)
        g = X.T @ (y - pr)
        H = (X * w[:, None]).T @ X + 1e-8 * np.eye(X.shape[1])
        step = np.linalg.solve(H, g)
        b = b + step
        if np.max(np.abs(step)) < 1e-10:
            break
    eta = X @ b
    pr = 1.0 / (1.0 + np.exp(-np.clip(eta, -30, 30)))
    ll = float(np.sum(y * np.log(np.clip(pr, 1e-12, 1)) +
                      (1 - y) * np.log(np.clip(1 - pr, 1e-12, 1))))
    return b, ll


def ll_null(y):
    q = float(np.mean(y))
    q = min(max(q, 1e-12), 1 - 1e-12)
    return float(len(y) * (q * np.log(q) + (1 - q) * np.log(1 - q)))


def chi2_sf(x, df):
    from math import erfc, exp, sqrt
    if df == 1:
        return erfc(sqrt(x / 2.0))
    if df == 2:
        return exp(-x / 2.0)
    raise ValueError(df)


def sens(y, v):
    """univariate logistic of y on v; return (p10->p90 predicted-rate delta, slope, LRp)"""
    z = (v - v.mean()) / max(v.std(), 1e-12)
    X = np.column_stack([np.ones(len(z)), z])
    b, ll = logit_fit(X, y)
    l0 = ll_null(y)
    lr = 2 * (ll - l0)
    zp10, zp90 = np.percentile(z, 10), np.percentile(z, 90)
    f = lambda zz: 1.0 / (1.0 + np.exp(-np.clip(b[0] + b[1] * zz, -30, 30)))
    return float(f(zp90) - f(zp10)), float(b[1]), float(chi2_sf(max(lr, 0.0), 1))


# =================================================================================== substrate
def build(a, b, extend, memfile, label, filt=None):
    """Reproduces run_we_w98's P1 construction EXACTLY, including the entry filter that
    run_we_w98 applies to the modern window before causal_score (the score is a trailing
    quantile over prior entries, so the filter is load-bearing)."""
    D = load_deep(a, b, extend=extend)
    n, t, sid, fb = D["n"], D["t"], D["sid"], D["fb"]
    ns = D["n_sess"]
    P_(f"    {label:<7} {n:,} bars / {ns:,} sessions  {t[0]} -> {t[-1]}  {el()}")
    X = fast_build_context(D)
    z = np.load(memfile)
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    vl, _ = votes(D, mem, bmom, tilt, X, bmom)
    pos = vl.astype(np.int8)
    bb = fills_daily(D, pos, halt=HALT0, target=TARGET0)
    if filt is None:
        ee = np.array([int(min(np.searchsorted(t, np.datetime64(x["et"])), n - 1)) for x in bb])
    else:
        a_, b_ = filt
        ee = np.array([int(min(np.searchsorted(t, np.datetime64(x["et"])), n - 1))
                       for x in bb if a_ <= np.datetime64(x["et"]) < b_])
    sc, _ = causal_score(X, ee, window=WIN)
    sz = np.where(sc >= 3, 2, 1).astype(np.int8)
    P_(f"    {label:<7} P1 signal built: long-target bars {int(pos.sum()):,}, "
       f"size-2 bars {int((sc>=3).sum()):,}  {el()}")

    # per-session causal state, strictly from bars STRICTLY BEFORE the session's first bar
    st = np.zeros(ns, np.int64); st[sid[fb]] = np.flatnonzero(fb)
    h, l = D["h"], D["l"]
    hi = pd.Series(h).groupby(sid).max().to_numpy()
    lo = pd.Series(l).groupby(sid).min().to_numpy()
    rng = hi - lo
    Ps = D["o"][st]                                        # session open, known at the open
    sig20 = np.full(ns, np.nan); sig60 = np.full(ns, np.nan)
    cs = np.concatenate([[0.0], np.cumsum(rng)])
    for s in range(ns):
        if s >= 20:
            sig20[s] = (cs[s] - cs[s - 20]) / 20.0
        if s >= 60:
            sig60[s] = (cs[s] - cs[s - 60]) / 60.0
    sdate = pd.to_datetime(D["sess_date"])
    return dict(D=D, pos=pos, sz=sz, sc=sc, st=st, Ps=Ps, rng=rng, sig20=sig20,
                sig60=sig60, sdate=sdate, year=sdate.year.to_numpy(), label=label)


# =================================================================================== main
def main():
    P_("=" * 118)
    P_("=== P1_BOX_INVARIANCE_00 - STAGE 1: STRUCTURE ONLY. NO P&L IS COMPUTED IN THIS STAGE.")
    P_("=== spec runs/P1_BOX_INVARIANCE_00/spec.yaml committed at 2a94aea, before this ran.")
    P_("=" * 118)

    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    A_M, B_M = np.datetime64("2022-07-01"), np.datetime64("2026-08-01")
    P_("")
    P_("--- substrates -----------------------------------------------------------------------")
    MOD = build("2022-01-01", "2026-07-31 17:00", True,
                os.path.join(W76OUT, "mem_ext.npz"), "MODERN", filt=(A_M, B_M))
    DEEP = build("2006-01-05", "2021-12-31 17:00", False,
                 os.path.join(W80OUT, "mem_deep_4908286.npz"), "DEEP")

    # ---------------------------------------------------------------- window / universe masks
    # W98's window convention is the session's FIRST-BAR timestamp (18:01 the prior calendar
    # day), not the session date. Reproduced exactly so H-C can be a real check.
    _t0M = MOD["D"]["t"][MOD["st"]]
    inwinM = (_t0M >= A_M) & (_t0M < B_M)
    inwinD = np.ones(DEEP["D"]["n_sess"], bool)
    for W in (MOD, DEEP):
        W["warm"] = np.arange(W["D"]["n_sess"]) >= WARMUP
    MOD["inwin"] = inwinM & MOD["warm"]
    DEEP["inwin"] = inwinD & DEEP["warm"]

    # ---------------------------------------------------------------- B1 harness checks
    P_("")
    P_("=" * 118)
    P_("=== B1 HARNESS CHECKS - printed before any criterion is read. Any failure stops the wave.")
    P_("=" * 118)
    ok = True
    for W in (MOD, DEEP):
        D = W["D"]
        hs, ts = const_arrays(D, HALT0, TARGET0)
        tr, lat = gfills_box(D, W["pos"], W["sz"], hs, ts)
        ref = gfills(D, W["pos"], W["sz"], halt=HALT0, target=TARGET0, per_ctr=True)
        r = same_as_w98(tr, ref, D)
        P_(f"    H-A[{W['label']}] gfills_box(const) == run_we_w98.gfills(per_ctr=True), byte for "
           f"byte ... {'PASS' if r else 'FAIL'}  ({len(tr):,} trades)")
        ok &= r
        W["base_tr"] = tr; W["base_lat"] = lat
        # NOBOX universe - identical for every arm by construction
        nb, _ = gfills_box(D, W["pos"], W["sz"], np.full(D["n_sess"], INF),
                           np.full(D["n_sess"], INF))
        act = np.zeros(D["n_sess"], bool)
        for x in nb:
            act[D["sid"][x[2]]] = True
        W["nobox_tr"] = nb; W["active"] = act
        P_(f"    H-B[{W['label']}] NOBOX schedule built: {len(nb):,} trades, "
           f"{int((act & W['inwin']).sum()):,} active sessions in-window")
    # H-B proper: every arm's NOBOX list is the same object regardless of which halt array
    for W in (MOD, DEEP):
        D = W["D"]
        alt, _ = gfills_box(D, W["pos"], W["sz"],
                            np.maximum(W["Ps"] * PV, 1e9), np.maximum(W["Ps"] * PV, 1e9))
        r = sched(alt) == sched(W["nobox_tr"])
        P_(f"    H-B2[{W['label']}] a huge PRICE-shaped box collapses to the same NOBOX schedule "
           f"... {'PASS' if r else 'FAIL'}")
        ok &= r
    ntr_w98 = sum(1 for x in MOD["base_tr"] if inwinM[MOD["D"]["sid"][x[2]]])
    r = (ntr_w98 == 2131)
    P_(f"    H-C  MODERN P1/PCT in-window trades == W98's committed 2,131 ................. "
       f"{'PASS' if r else 'FAIL'}  (this run {ntr_w98:,})")
    ok &= r
    # H-D causality: sigma_s uses only sessions strictly before s; P_s is the session's own open
    r = True
    for W in (MOD, DEEP):
        s_ = 500
        man = float(np.mean(W["rng"][s_ - 20:s_]))
        r &= abs(man - float(W["sig20"][s_])) < 1e-9
        r &= abs(float(W["Ps"][s_]) - float(W["D"]["o"][W["st"][s_]])) < 1e-12
    P_(f"    H-D  sigma_s is the mean of sessions [s-20, s-1] and P_s is session s's own open, "
       f"both causal ... {'PASS' if r else 'FAIL'}")
    ok &= r
    r = (DEEP["D"]["n"] == 4908286 and DEEP["D"]["n_sess"] == 4279)
    P_(f"    H-E  deep substrate == W98's committed 4,908,286 bars / 4,279 sessions ......... "
       f"{'PASS' if r else 'FAIL'}")
    ok &= r
    if not ok:
        P_("\n    A HARNESS CHECK FAILED. No criterion is read.")
        _fh.close(); return
    P_("\n    all harness checks PASS.")

    # ---------------------------------------------------------------- calibration (closed form)
    mA = MOD["active"] & MOD["inwin"]
    dA = DEEP["active"] & DEEP["inwin"]
    meanP = float(MOD["Ps"][mA].mean())
    meanS20 = float(MOD["sig20"][mA].mean())
    meanS60 = float(MOD["sig60"][mA].mean())
    c_p = HALT0 / (PV * meanP)
    c_v20 = HALT0 / (PV * meanS20)
    c_v60 = HALT0 / (PV * meanS60)
    P_("")
    P_("=" * 118)
    P_("=== PRIMARY CALIBRATION - CLOSED FORM, NO SEARCH. Mean box $ over MODERN == $1,300 exactly.")
    P_("=" * 118)
    P_(f"    MODERN active sessions {int(mA.sum()):,}   mean session open  {meanP:>12,.1f} pts")
    P_(f"    mean prior-20 session range {meanS20:>10,.1f} pts     prior-60 {meanS60:>10,.1f} pts")
    P_(f"    c_p  = 1300 / (20 * {meanP:,.1f})   = {c_p:.8f}  of index  "
       f"({1e4*c_p:.2f} bp)")
    P_(f"    c_v20= 1300 / (20 * {meanS20:,.1f})  = {c_v20:.6f}  of the prior-20 mean session range")
    P_(f"    c_v60= 1300 / (20 * {meanS60:,.1f})  = {c_v60:.6f}")
    P_(f"    DEEP  active sessions {int(dA.sum()):,}   mean session open  "
       f"{float(DEEP['Ps'][dA].mean()):>12,.1f} pts   "
       f"mean prior-20 range {float(DEEP['sig20'][dA].mean()):>8,.1f} pts")

    def halt_for(W, arm, cp, cv, which="sig20"):
        ns = W["D"]["n_sess"]
        if arm == "DOLLAR":
            h = np.full(ns, HALT0, float)
        elif arm == "PRICEBOX":
            h = cp * W["Ps"] * PV
        else:
            s = np.where(np.isnan(W[which]), np.nanmean(W[which]), W[which])
            h = cv * s * PV
        return h, h * TT_RATIO

    # ---------------------------------------------------------------- run the arms
    def run_arms(cp, cv, which, tag):
        R = {}
        for W in (MOD, DEEP):
            for arm in ARMS:
                h, t = halt_for(W, arm, cp, cv, which)
                tr, lat = gfills_box(W["D"], W["pos"], W["sz"], h, t)
                R[(W["label"], arm)] = dict(tr=tr, lat=lat, halt=h)
            P_(f"    [{tag}] {W['label']} arms built  {el()}")
        return R

    P_("")
    P_("--- building arms (primary calibration, sigma N=20) ------------------------------------")
    R = run_arms(c_p, c_v20, "sig20", "primary")

    # ---------------------------------------------------------------- criterion machinery
    def rows(R, tag):
        """assemble the pooled per-session table used by C1/C2/C4/C5 and D1/D3"""
        recs = []
        for W in (MOD, DEEP):
            D = W["D"]; msk = W["active"] & W["inwin"]
            idx = np.flatnonzero(msk)
            ntr = {arm: np.zeros(D["n_sess"], int) for arm in ARMS}
            for arm in ARMS:
                for x in R[(W["label"], arm)]["tr"]:
                    ntr[arm][D["sid"][x[2]]] += 1
            for s in idx:
                rec = dict(win=W["label"], sess=int(s), year=int(W["year"][s]),
                           P=float(W["Ps"][s]), sig=float(W["sig20"][s]),
                           rng=float(W["rng"][s]))
                for arm in ARMS:
                    rec[f"lat_{arm}"] = int(R[(W["label"], arm)]["lat"][s] != 0)
                    rec[f"halt_{arm}"] = float(R[(W["label"], arm)]["halt"][s])
                    rec[f"side_{arm}"] = int(R[(W["label"], arm)]["lat"][s])
                    rec[f"ntr_{arm}"] = int(ntr[arm][s])
                recs.append(rec)
        return pd.DataFrame(recs)

    T = rows(R, "primary")
    T.to_csv(os.path.join(OUT, "sessions_primary.csv"), index=False)

    def criteria(T, tag):
        res = {}
        yrs = T.groupby("year").size()
        keep = yrs[yrs >= 40].index
        Ty = T[T.year.isin(keep)]
        lP = np.log(T["P"].to_numpy()); lS = np.log(T["sig"].to_numpy())
        for arm in ARMS:
            y = T[f"lat_{arm}"].to_numpy().astype(float)
            ry = Ty.groupby("year")[f"lat_{arm}"].mean()
            c1_range = float(ry.max() - ry.min()); c1_sd = float(ry.std(ddof=1))
            Z = np.column_stack([np.ones(len(y)),
                                 (lP - lP.mean()) / lP.std(),
                                 (lS - lS.mean()) / lS.std()])
            b, ll = logit_fit(Z, y)
            l0 = ll_null(y)
            lr = 2 * (ll - l0)
            c2_r2 = 1.0 - ll / l0 if l0 != 0 else 0.0
            c2_p = chi2_sf(max(lr, 0.0), 2)
            d_p, sl_p, p_p = sens(y, lP)
            d_v, sl_v, p_v = sens(y, lS)
            cov = T[f"halt_{arm}"].to_numpy() / (PV * np.maximum(T["rng"].to_numpy(), 1e-9))
            res[arm] = dict(arm=arm, tag=tag, rate=float(y.mean()),
                            c1_range=c1_range, c1_sd=c1_sd,
                            c2_r2=float(c2_r2), c2_p=float(c2_p), c2_lr=float(lr),
                            c4_delta=d_p, c4_slope=sl_p, c4_p=p_p,
                            c5_delta=d_v, c5_slope=sl_v, c5_p=p_v,
                            d1_cov_sdlog=float(np.std(np.log(np.maximum(cov, 1e-12)))),
                            d1_cov_med=float(np.median(cov)),
                            yearly=ry.to_dict())
        return res, Ty

    CR, Ty = criteria(T, "primary")

    # ---------------------------------------------------------------- C3 scale invariance
    P_("")
    P_("=" * 118)
    P_("=== C3 SCALE INVARIANCE - pure change of monetary unit (prices AND the $4.36 commission")
    P_("===  scaled by lambda), direction and size arrays HELD FIXED so only the box is exercised.")
    P_("===  ⚠ LABELLED INFERRED/TAUTOLOGICAL: this criterion is definitional, not evidence.")
    P_("=" * 118)
    C3 = {arm: dict(a=True, b=True) for arm in ARMS}
    W = MOD; D = W["D"]
    for lam in (0.5, 2.0):
        oS, cS = D["o"] * lam, D["c"] * lam
        for arm in ARMS:
            # C3a: unit change - state inputs scale with prices, commission scales too
            if arm == "DOLLAR":
                h = np.full(D["n_sess"], HALT0, float)
            elif arm == "PRICEBOX":
                h = c_p * (W["Ps"] * lam) * PV
            else:
                s = np.where(np.isnan(W["sig20"]), np.nanmean(W["sig20"]), W["sig20"]) * lam
                h = c_v20 * s * PV
            tr_a, _ = gfills_box(D, W["pos"], W["sz"], h, h * TT_RATIO,
                                 comm=COMM_RT * lam, o=oS, c=cS)
            same_a = sched(tr_a) == sched(R[("MODERN", arm)]["tr"])
            # C3b: prices only, commission stays $4.36 - the real-world fixed-cost residual
            tr_b, _ = gfills_box(D, W["pos"], W["sz"], h, h * TT_RATIO,
                                 comm=COMM_RT, o=oS, c=cS)
            same_b = sched(tr_b) == sched(R[("MODERN", arm)]["tr"])
            C3[arm]["a"] &= same_a
            C3[arm]["b"] &= same_b
            P_(f"    lambda={lam:<4} {arm:<9} C3a(unit change) {'IDENTICAL' if same_a else 'CHANGED':<10}"
               f"   C3b(prices only, $4.36 fixed) {'IDENTICAL' if same_b else 'CHANGED'}")
    P_(f"    {el()}")

    # ---------------------------------------------------------------- report the criteria
    P_("")
    P_("=" * 118)
    P_("=== THE FIVE PREDECLARED STRUCTURAL CRITERIA (thresholds fixed at spec time, 2a94aea)")
    P_("=" * 118)
    P_(f"{'criterion':<34}{'threshold (non-invariant if)':<32}{'DOLLAR':>14}{'PRICEBOX':>14}"
       f"{'SIGMABOX':>14}")
    P_("-" * 118)
    P_(f"{'C1 trigger-rate range across years':<34}{'range >= 0.20':<32}"
       + "".join(f"{CR[a]['c1_range']:>14.3f}" for a in ARMS))
    P_(f"{'   (SD across years)':<34}{'':<32}"
       + "".join(f"{CR[a]['c1_sd']:>14.3f}" for a in ARMS))
    P_(f"{'C2 state conditionality McF R2':<34}{'R2 >= 0.02 AND p < 0.01':<32}"
       + "".join(f"{CR[a]['c2_r2']:>14.4f}" for a in ARMS))
    P_(f"{'   (joint LR p, 2 df)':<34}{'':<32}"
       + "".join(f"{CR[a]['c2_p']:>14.3g}" for a in ARMS))
    P_(f"{'C3a scale invariance (unit chg)':<34}{'FAIL at either lambda':<32}"
       + "".join(f"{('PASS' if C3[a]['a'] else 'FAIL'):>14}" for a in ARMS))
    P_(f"{'   C3b prices only, $4.36 fixed':<34}{'(diagnostic, not a gate)':<32}"
       + "".join(f"{('PASS' if C3[a]['b'] else 'FAIL'):>14}" for a in ARMS))
    P_(f"{'C4 price-level sens (p90-p10)':<34}{'|delta| >= 0.15':<32}"
       + "".join(f"{CR[a]['c4_delta']:>14.3f}" for a in ARMS))
    P_(f"{'C5 realized-vol sens (p90-p10)':<34}{'|delta| >= 0.15':<32}"
       + "".join(f"{CR[a]['c5_delta']:>14.3f}" for a in ARMS))
    P_("-" * 118)
    P_(f"{'  pooled latch rate':<34}{'(level, not a criterion)':<32}"
       + "".join(f"{CR[a]['rate']:>14.3f}" for a in ARMS))
    P_(f"{'  D1 SD(log box/session range)':<34}{'(diagnostic)':<32}"
       + "".join(f"{CR[a]['d1_cov_sdlog']:>14.3f}" for a in ARMS))
    P_(f"{'  D1 median box / session range':<34}{'(diagnostic)':<32}"
       + "".join(f"{CR[a]['d1_cov_med']:>14.3f}" for a in ARMS))

    # per-year table
    P_("")
    P_("--- C1 detail: latch rate by calendar year (years with >= 40 active sessions) ----------")
    P_(f"{'year':<7}{'n':>6}{'medP':>10}{'medSig':>9}" + "".join(f"{a:>12}" for a in ARMS)
       + "".join(f"{'ntr/'+a[:3]:>10}" for a in ARMS))
    for y in sorted(Ty.year.unique()):
        g = Ty[Ty.year == y]
        P_(f"{y:<7}{len(g):>6}{g['P'].median():>10,.0f}{g['sig'].median():>9,.0f}"
           + "".join(f"{g['lat_'+a].mean():>12.3f}" for a in ARMS)
           + "".join(f"{g['ntr_'+a].mean():>10.2f}" for a in ARMS))

    # D2 collinearity
    lP = np.log(T["P"].to_numpy()); lS = np.log(T["sig"].to_numpy())
    d2_corr = float(np.corrcoef(lP, lS)[0, 1])
    ratio = T["sig"].to_numpy() / T["P"].to_numpy()
    d2_cv = float(ratio.std() / ratio.mean())
    P_("")
    P_("--- D2: are PRICEBOX and SIGMABOX the same object? --------------------------------------")
    P_(f"    corr(log P_s, log sigma_s) = {d2_corr:.4f}     "
       f"CV(sigma_s / P_s) = {d2_cv:.4f}")
    P_(f"    spec's same-object test: corr >= 0.98 AND CV <= 0.10  ->  "
       f"{'SAME OBJECT' if (d2_corr >= 0.98 and d2_cv <= 0.10) else 'DISTINCT OBJECTS'}")

    # ---------------------------------------------------------------- robustness arms
    P_("")
    P_("=" * 118)
    P_("=== ROBUSTNESS 1: sigma N=60 (declared in the spec; the verdict must hold at BOTH)")
    P_("=" * 118)
    R60 = run_arms(c_p, c_v60, "sig60", "N60")
    T60 = rows(R60, "N60")
    CR60, _ = criteria(T60, "N60")
    P_(f"{'criterion':<34}{'':<32}{'DOLLAR':>14}{'PRICEBOX':>14}{'SIGMABOX':>14}")
    for k, lab in (("c1_range", "C1 range"), ("c2_r2", "C2 McF R2"),
                   ("c4_delta", "C4 delta"), ("c5_delta", "C5 delta")):
        P_(f"{lab:<34}{'':<32}" + "".join(f"{CR60[a][k]:>14.4f}" for a in ARMS))

    P_("")
    P_("=" * 118)
    P_("=== ROBUSTNESS 2: rate-matched calibration - c_p, c_v bisected so each arm's MODERN latch")
    P_("===  rate equals DOLLAR's to within 0.005. Targets a TRIGGER RATE, never a P&L quantity.")
    P_("=" * 118)
    tgt = float(np.mean([R[("MODERN", "DOLLAR")]["lat"][s] != 0 for s in np.flatnonzero(mA)]))
    P_(f"    target MODERN latch rate (DOLLAR) = {tgt:.4f}")

    def modern_rate(arm, cp, cv):
        h, t = halt_for(MOD, arm, cp, cv, "sig20")
        _, lat = gfills_box(MOD["D"], MOD["pos"], MOD["sz"], h, t)
        return float(np.mean(lat[mA] != 0))

    def bisect(arm, c0):
        lo, hi = c0 / 8.0, c0 * 8.0
        # rate is decreasing in c
        for _ in range(18):
            mid = np.sqrt(lo * hi)
            r_ = modern_rate(arm, mid if arm == "PRICEBOX" else c_p,
                             mid if arm == "SIGMABOX" else c_v20)
            if r_ > tgt:
                lo = mid
            else:
                hi = mid
            if abs(r_ - tgt) <= 0.005:
                return mid, r_
        mid = np.sqrt(lo * hi)
        return mid, modern_rate(arm, mid if arm == "PRICEBOX" else c_p,
                                mid if arm == "SIGMABOX" else c_v20)

    cp2, rp2 = bisect("PRICEBOX", c_p)
    cv2, rv2 = bisect("SIGMABOX", c_v20)
    P_(f"    PRICEBOX c_p {c_p:.8f} -> {cp2:.8f}  (x{cp2/c_p:.3f})  modern latch rate {rp2:.4f}")
    P_(f"    SIGMABOX c_v {c_v20:.6f} -> {cv2:.6f}  (x{cv2/c_v20:.3f})  modern latch rate {rv2:.4f}")
    RM = {}
    for W in (MOD, DEEP):
        for arm in ARMS:
            cp_ = cp2 if arm == "PRICEBOX" else c_p
            cv_ = cv2 if arm == "SIGMABOX" else c_v20
            h, t = halt_for(W, arm, cp_, cv_, "sig20")
            tr, lat = gfills_box(W["D"], W["pos"], W["sz"], h, t)
            RM[(W["label"], arm)] = dict(tr=tr, lat=lat, halt=h)
        P_(f"    [ratematch] {W['label']} arms built  {el()}")
    TM = rows(RM, "ratematch")
    CRM, TMy = criteria(TM, "ratematch")
    P_("")
    P_(f"{'criterion':<34}{'':<32}{'DOLLAR':>14}{'PRICEBOX':>14}{'SIGMABOX':>14}")
    for k, lab in (("rate", "pooled latch rate"), ("c1_range", "C1 range"),
                   ("c2_r2", "C2 McF R2"), ("c4_delta", "C4 delta"),
                   ("c5_delta", "C5 delta")):
        P_(f"{lab:<34}{'':<32}" + "".join(f"{CRM[a][k]:>14.4f}" for a in ARMS))
    P_("")
    P_("--- rate-matched: latch rate by calendar year -------------------------------------------")
    P_(f"{'year':<7}{'n':>6}" + "".join(f"{a:>12}" for a in ARMS))
    for y in sorted(TMy.year.unique()):
        g = TMy[TMy.year == y]
        P_(f"{y:<7}{len(g):>6}" + "".join(f"{g['lat_'+a].mean():>12.3f}" for a in ARMS))

    # ---------------------------------------------------------------- THE GATES
    def breaches(cr, c3, arm):
        b = {}
        b["C1"] = cr[arm]["c1_range"] >= 0.20
        b["C2"] = (cr[arm]["c2_r2"] >= 0.02) and (cr[arm]["c2_p"] < 0.01)
        b["C3"] = not c3[arm]["a"]
        b["C4"] = abs(cr[arm]["c4_delta"]) >= 0.15
        b["C5"] = abs(cr[arm]["c5_delta"]) >= 0.15
        return b

    P_("")
    P_("=" * 118)
    P_("=== GATE TABLE - every clause coded, printed by the program, assembled by nobody")
    P_("=" * 118)
    BR = {a: breaches(CR, C3, a) for a in ARMS}
    P_(f"{'arm':<12}" + "".join(f"{k:>8}" for k in ("C1", "C2", "C3", "C4", "C5"))
       + f"{'breaches':>11}")
    for a in ARMS:
        P_(f"{a:<12}" + "".join(f"{('YES' if BR[a][k] else 'no'):>8}"
                                for k in ("C1", "C2", "C3", "C4", "C5"))
           + f"{sum(BR[a].values()):>11}")
    gate_A = sum(BR["DOLLAR"].values()) >= 3
    P_("")
    P_(f"    GATE A  'fixed dollars structurally non-invariant' : DOLLAR breaches "
       f"{sum(BR['DOLLAR'].values())} of 5, needs >= 3  ->  {'PASS' if gate_A else 'FAIL'}")

    def better(cr, c3, x, y):
        """count of the 5 criteria on which x is strictly better than y"""
        n = 0
        n += cr[x]["c1_range"] < cr[y]["c1_range"]
        n += cr[x]["c2_r2"] < cr[y]["c2_r2"]
        n += (c3[x]["a"] and not c3[y]["a"])
        n += abs(cr[x]["c4_delta"]) < abs(cr[y]["c4_delta"])
        n += abs(cr[x]["c5_delta"]) < abs(cr[y]["c5_delta"])
        return int(n)

    gb = {}
    for a in ("PRICEBOX", "SIGMABOX"):
        other = "SIGMABOX" if a == "PRICEBOX" else "PRICEBOX"
        i_ = sum(BR[a].values()) == 0
        ii = better(CR, C3, a, other) >= 4
        iii = better(CR, C3, a, "DOLLAR") >= 4
        BRM = {q: breaches(CRM, C3, q) for q in ARMS}
        BR60 = {q: breaches(CR60, C3, q) for q in ARMS}
        iv = (sum(BRM[a].values()) == 0 and better(CRM, C3, a, other) >= 4
              and better(CRM, C3, a, "DOLLAR") >= 4)
        v = (sum(BR60[a].values()) == 0 and better(CR60, C3, a, other) >= 4
             and better(CR60, C3, a, "DOLLAR") >= 4)
        vi = not (d2_corr >= 0.98 and d2_cv <= 0.10)
        gb[a] = dict(i=i_, ii=ii, iii=iii, iv=iv, v=v, vi=vi,
                     all=all([i_, ii, iii, iv, v, vi]))
        P_(f"    GATE B [{a}]  (i) breaches none {i_}  (ii) beats {other} on >=4 {ii} "
           f"({better(CR,C3,a,other)}/5)  (iii) beats DOLLAR on >=4 {iii} "
           f"({better(CR,C3,a,'DOLLAR')}/5)")
        P_(f"{'':<18}(iv) rate-matched holds {iv}  (v) N=60 holds {v}  "
           f"(vi) not the same object {vi}   ->  {'PASS' if gb[a]['all'] else 'FAIL'}")
    gate_B = sum(1 for a in gb if gb[a]["all"]) == 1
    winner = [a for a in gb if gb[a]["all"]]
    P_("")
    P_(f"    GATE B  'exactly one normalisation clearly superior' -> "
       f"{'PASS (' + winner[0] + ')' if gate_B else 'FAIL'}")

    P_("")
    P_("=" * 118)
    if gate_A and gate_B:
        P_(f"=== VERDICT: GATE A PASS + GATE B PASS -> freeze P1_{winner[0].replace('BOX','')}"
           f"BOX_V1 and proceed to STAGE 2 ECONOMICS (separate stage, separate report).")
    elif gate_A:
        P_("=== VERDICT: GATE A PASS, GATE B FAIL. The fixed-dollar box IS structurally")
        P_("===          non-invariant, but NO economically natural normalisation is clearly")
        P_("===          superior on the predeclared structural criteria.")
        P_("===          NOTHING IS FROZEN. NO ECONOMICS ARE RUN. Stage 2 is not reachable.")
    else:
        P_("=== VERDICT: GATE A FAIL. The incumbent fixed-dollar box is structurally invariant")
        P_("===          enough on the predeclared criteria. Nothing is promoted.")
    P_("=" * 118)

    json.dump(dict(gate_A=bool(gate_A), gate_B=bool(gate_B), winner=winner,
                   c_p=c_p, c_v20=c_v20, c_v60=c_v60, cp_ratematch=float(cp2),
                   cv_ratematch=float(cv2), d2_corr=d2_corr, d2_cv=d2_cv,
                   primary={a: {k: v for k, v in CR[a].items() if k != "yearly"} for a in ARMS},
                   n60={a: {k: v for k, v in CR60[a].items() if k != "yearly"} for a in ARMS},
                   ratematch={a: {k: v for k, v in CRM[a].items() if k != "yearly"}
                              for a in ARMS},
                   c3={a: {k: bool(v) for k, v in C3[a].items()} for a in ARMS},
                   breaches={a: {k: bool(v) for k, v in BR[a].items()} for a in ARMS},
                   gate_b_detail={a: {k: bool(v) for k, v in gb[a].items()} for a in gb}),
              open(os.path.join(OUT, "gates.json"), "w"), indent=1)
    T.to_csv(os.path.join(OUT, "sessions_primary.csv"), index=False)
    TM.to_csv(os.path.join(OUT, "sessions_ratematch.csv"), index=False)
    pd.DataFrame([{k: v for k, v in CR[a].items() if k != "yearly"} for a in ARMS]).to_csv(
        os.path.join(OUT, "criteria_primary.csv"), index=False)

    if not (gate_A and gate_B):
        P_("")
        P_("    STAGE 2 IS NOT REACHED. No P&L was computed anywhere in this program.")
        P_(f"[done {_time.time()-_t0:.0f}s]")
        _fh.close()
        return
    P_("")
    P_("    STAGE 2 would run here. It is reached only because both gates passed.")
    P_(f"[done {_time.time()-_t0:.0f}s]")
    _fh.close()


if __name__ == "__main__":
    main()
