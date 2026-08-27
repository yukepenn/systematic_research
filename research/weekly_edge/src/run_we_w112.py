"""WE_W112 - THE FIRST MEASUREMENT OF THE CAUSAL_MODEL_FRONTIER.

Spec: runs/WE_W112_FRONTIER/spec.yaml, committed BEFORE this ran (f678744).

`OPPORTUNITY_LANGUAGE.md` is binding and it says that of the four levels -
    EX_POST_PATH_ORACLE > EX_POST_EXECUTION_FEASIBLE_ORACLE > CAUSAL_MODEL_FRONTIER > REAL_SYSTEM_CAPTURE
- the THIRD has never been measured in this repo. Every capture ratio ever quoted here compares
real capture against an oracle that knows the future, so the gap has never been split into "money a
causal model could have reached" and "money no causal model could ever reach".

Walk-forward, expanding window, 63-session blocks. K-FOLD IS NOT USED ANYWHERE IN THIS WAVE and the
protocol travels with every number.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV, COMM_RT                                 # noqa: E402
from we_lanes import LaneBench, DDT                                      # noqa: E402
from we_fades import MORN_A, DEC, EXIT, session_vwap                     # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from run_we_w109 import build_detectors, trail                           # noqa: E402
from sklearn.linear_model import Ridge                                   # noqa: E402
from sklearn.ensemble import GradientBoostingRegressor                   # noqa: E402
from sklearn.preprocessing import StandardScaler                         # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W112_FRONTIER", "out")
os.makedirs(OUT, exist_ok=True)
CALF = os.path.join(ROOT, "research", "04_complementary_family", "c01_announcement_calendar.csv")
TICKV = 5.0
MINFIT, BLOCK = 250, 63
SEED = 112
ONSTART = 1081


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "frontier.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    L = LaneBench()
    rng = np.random.default_rng(SEED)
    NS = L.NS
    P_(f"    substrate {L.n:,} bars / {len(L.sess_in):,} in-window sessions [{_time.time()-t0:.0f}s]")

    # ------------------------------------------------------------------ target and cost
    pe = L.at(DEC + 1, use_open=True)
    px = L.at(EXIT)
    move = (px - pe) * PV
    cost = COMM_RT + TICKV * (float(L.prof.loc[DEC + 1]) + float(L.prof.loc[EXIT])) / 2.0

    # ------------------------------------------------------------------ the information set
    DET = build_detectors(L, None, P_)
    o0 = L.at(MORN_A, use_open=True)
    cD = L.at(DEC)
    hi = L.agg(MORN_A, DEC, "high"); lo = L.agg(MORN_A, DEC, "low")
    path = L.agg(MORN_A, DEC, "absmove")
    vol = L.agg(MORN_A, DEC, "vol")
    rngp = hi - lo
    prevc = np.full(NS, np.nan)
    lastc = L.at(1020)
    prevc[1:] = lastc[:-1]
    prev2 = np.full(NS, np.nan); prev2[2:] = lastc[:-2]
    onh = np.full(NS, -np.inf); onl = np.full(NS, np.inf)
    om = (L.mod >= ONSTART) | (L.mod < MORN_A)
    np.maximum.at(onh, L.sid[om], L.h[om]); np.minimum.at(onl, L.sid[om], L.l[om])
    onr = np.where(onh > -np.inf, onh - onl, np.nan)
    seg_vol = pd.Series(move).rolling(20, min_periods=10).std().shift(1).to_numpy()
    cal = pd.read_csv(CALF)
    cald = set(pd.to_datetime(cal["date"]).dt.date.tolist())
    ann = np.array([L.sdate[s].date() in cald for s in range(NS)], float)
    dow = np.array([L.sdate[s].dayofweek for s in range(NS)], float)

    FE = {
        "dir_eff": DET["D1_DIR_EFF"], "vwap_disp": DET["D4_VWAP_DISP"],
        "mr_fail": DET["D5_MR_FAIL"], "close_ext": DET["D2_CLOSE_EXT"],
        "range_exp": DET["D3_RANGE_EXP"], "xbreadth": DET["D6_XBREADTH"],
        "morn_net_pts": cD - o0,
        "morn_path_pts": path,
        "rng_pts": rngp,
        "vol_rel": vol / np.maximum(trail(vol, "median"), 1e-9),
        "pos_in_range": (cD - lo) / np.maximum(rngp, 1e-9),
        "on_range_rel": onr / np.maximum(trail(onr, "median"), 1e-9),
        "gap_pts": o0 - prevc,
        "prev_ret": (prevc - prev2) / np.maximum(np.abs(prev2), 1e-9) * 1e4,
        "seg_vol": seg_vol,
        "dow": dow,
        "is_ann": ann,
    }
    names = list(FE)
    Xall = np.column_stack([FE[k] for k in names])
    ok = (L.win & np.isfinite(move) & np.isfinite(pe) & np.isfinite(px)
          & np.all(np.isfinite(Xall), axis=1))
    idx = np.flatnonzero(ok)
    X, y = Xall[idx], move[idx]
    emove = float(np.abs(y).mean())
    pstar = 0.5 * (1 + cost / max(emove, 1e-9))
    P_(f"    {len(idx)} usable sessions, {len(names)} features, E|move| = ${emove:,.0f}, "
       f"cost ${cost:.2f}/RT, p* = {pstar:.4f}")
    P_(f"    features: {', '.join(names)}")

    # ------------------------------------------------------------------ walk-forward
    P_("")
    P_("=" * 122)
    P_(f"=== WALK-FORWARD, EXPANDING WINDOW. First fit at {MINFIT} sessions, {BLOCK}-session blocks.")
    P_("===   Every prediction is made by a model that never saw its own session or any later one.")
    P_("=" * 122)
    MODELS = {
        "M0_MEAN": None,
        "M1_RIDGE": lambda: Ridge(alpha=10.0),
        "M2_GBT": lambda: GradientBoostingRegressor(n_estimators=200, max_depth=2,
                                                    learning_rate=0.03, subsample=0.8,
                                                    random_state=SEED),
    }
    PRED = {k: np.full(len(y), np.nan) for k in MODELS}
    SCALE = {k: np.full(len(y), np.nan) for k in MODELS}
    starts = list(range(MINFIT, len(y), BLOCK))
    for a in starts:
        b = min(a + BLOCK, len(y))
        Xtr, ytr = X[:a], y[:a]
        for k, mk in MODELS.items():
            if mk is None:
                PRED[k][a:b] = float(ytr.mean())
                SCALE[k][a:b] = max(float(np.abs(ytr - ytr.mean()).mean()), 1e-9)
                continue
            sc = StandardScaler().fit(Xtr)
            m = mk(); m.fit(sc.transform(Xtr), ytr)
            PRED[k][a:b] = m.predict(sc.transform(X[a:b]))
            SCALE[k][a:b] = max(float(np.abs(m.predict(sc.transform(Xtr))).mean()), 1e-9)
    oos = np.arange(len(y)) >= MINFIT
    P_(f"    {len(starts)} blocks, {int(oos.sum())} out-of-sample sessions "
       f"({L.sdate[idx[MINFIT]].date()} onward)")

    # ------------------------------------------------------------------ the grid
    def econ(des, w=None):
        w = np.ones(len(des)) if w is None else w
        pnl = des * w * y[oos] - cost * w
        return pnl

    def summ(pnl, n_ctr=None):
        ser = np.zeros(NS); ser[idx[oos]] = pnl
        wv = pd.Series(ser[L.sess_in]).groupby(L.wk).sum().to_numpy()
        dp = dd_profile(wv)
        u = np.ones(len(pnl)) if n_ctr is None else n_ctr
        return dict(n=len(pnl), per_trade=float(pnl.sum() / max(u.sum(), 1e-9)),
                    net=float(pnl.sum()), wk=float(wv.mean()),
                    fixdd=float(wv.mean()) * DDT / max(dp["maxdd"], 1e-9),
                    poswk=100 * float((wv > 0).mean()), maxdd=dp["maxdd"],
                    t=float(wv.mean()) / max(wv.std(ddof=1) / np.sqrt(len(wv)), 1e-9))

    P_("")
    P_(f"{'cell':<26}{'N':>6}{'dir acc':>9}{'vs p*':>8}{'OOS R2':>9}{'$/ctr':>9}{'net $':>11}"
       f"{'wk$@fixDD':>11}{'pos wk%':>9}{'t':>7}")
    yo = y[oos]
    sse_mean = float(((yo - PRED["M0_MEAN"][oos]) ** 2).sum())
    rows, cells = [], []
    for k in MODELS:
        p = PRED[k][oos]
        s = np.sign(p); s[s == 0] = 1
        acc = float((np.sign(yo) == s)[np.sign(yo) != 0].mean())
        r2 = 1 - float(((yo - p) ** 2).sum()) / max(sse_mean, 1e-9)
        for pol in ("P_SIGN", "P_WEIGHT"):
            if pol == "P_SIGN":
                w = np.ones(len(p))
            else:
                w = np.clip(np.abs(p) / SCALE[k][oos], 0.0, 3.0)
            pnl = econ(s, w)
            st = summ(pnl, w)
            P_(f"{k + ' / ' + pol:<26}{st['n']:>6}{100*acc:>8.2f}%{100*(acc-pstar):>8.2f}"
               f"{r2:>9.4f}{st['per_trade']:>9,.0f}{st['net']:>11,.0f}{st['fixdd']:>11,.0f}"
               f"{st['poswk']:>8.1f}%{st['t']:>7.2f}")
            rows.append(dict(model=k, policy=pol, acc=acc, r2=r2, **st))
            if k != "M0_MEAN":
                cells.append((s, w))
        P_("")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "grid.csv"), index=False)

    # ------------------------------------------------------------------ controls, same wave
    P_("    UNCONDITIONAL CONTROLS on the SAME out-of-sample sessions (W111b's binding rule):")
    md = np.sign(L.at(689) - o0)[idx[oos]]
    for lab, s_ in (("always LONG", np.ones(int(oos.sum()))),
                    ("always SHORT", -np.ones(int(oos.sum()))),
                    ("FADE morning dir", -md), ("FOLLOW morning dir", md)):
        s_ = np.where(s_ == 0, 1, s_)
        acc = float((np.sign(yo) == s_)[np.sign(yo) != 0].mean())
        st = summ(econ(s_))
        P_(f"{'CONTROL ' + lab:<26}{st['n']:>6}{100*acc:>8.2f}%{100*(acc-pstar):>8.2f}"
           f"{'':>9}{st['per_trade']:>9,.0f}{st['net']:>11,.0f}{st['fixdd']:>11,.0f}"
           f"{st['poswk']:>8.1f}%{st['t']:>7.2f}")

    # ------------------------------------------------------------------ nulls
    prim = [r for r in rows if r["model"] == "M1_RIDGE" and r["policy"] == "P_SIGN"][0]
    nul = np.empty(2000)
    for b in range(2000):
        nul[b] = float((rng.choice([-1.0, 1.0], size=len(yo)) * yo - cost).mean())
    p95 = float(np.percentile(nul, 95))
    mx = np.empty(2000)
    for b in range(2000):
        vals = []
        for s_, w_ in cells:
            sg = rng.choice([-1.0, 1.0], size=len(yo))
            vals.append(float((sg * w_ * yo - cost * w_).sum() / w_.sum()))
        mx[b] = max(vals)
    p95x = float(np.percentile(mx, 95))
    P_("")
    P_("=" * 122)
    P_("=== THE PRIMARY: M1_RIDGE under P_SIGN, walk-forward")
    P_("=" * 122)
    P_(f"    real ${prim['per_trade']:,.0f}/contract   coin null mean ${nul.mean():,.0f} "
       f"p95 ${p95:,.0f}  -> {100*float((nul < prim['per_trade']).mean()):.1f}th percentile")
    P_(f"    directional accuracy {100*prim['acc']:.2f}% vs p* {100*pstar:.2f}%  -> "
       f"{'CLEARS' if prim['acc'] > pstar else 'does NOT clear'}")
    v = (prim["per_trade"] > 0 and prim["per_trade"] > p95 and prim["acc"] > pstar)
    P_(f"    VERDICT: {'PASSES' if v else 'FAILS'}     best-of-{len(cells)} bar ${p95x:,.0f}")

    # ------------------------------------------------------------------ the frontier number
    P_("")
    P_("=" * 122)
    P_("=== THE CAUSAL_MODEL_FRONTIER ESTIMATE for AFT 11:49 -> 15:44")
    P_("=" * 122)
    best = max([r for r in rows if r["model"] != "M0_MEAN"], key=lambda r: r["per_trade"])
    nsess = int(oos.sum())
    P_(f"{'level':<44}{'$/session':>13}{'source':>34}")
    P_(f"{'1. EX_POST_PATH_ORACLE':<44}{'not computed here':>13}{'':>34}")
    P_(f"{'2. EX_POST_EXECUTION_FEASIBLE_ORACLE':<44}{1170:>13,.0f}"
       f"{'W103 capture ledger v3, AFT':>34}")
    P_(f"{'3. CAUSAL_MODEL_FRONTIER (this wave)':<44}"
       f"{best['net']/max(nsess,1):>13,.0f}"
       f"{best['model'] + '/' + best['policy'] + ', walk-fwd':>34}")
    P_(f"{'4. REAL_SYSTEM_CAPTURE (P1/PCT)':<44}{3:>13,.0f}"
       f"{'W103 capture ledger v3, AFT':>34}")
    P_("")
    P_("    READ THIS WITH THE PROTOCOL ATTACHED: expanding-window walk-forward, 63-session")
    P_("    blocks, first fit at 250 sessions, hyperparameters frozen in the spec, no search.")
    P_("    It is a LOWER BOUND on the frontier - a better model could exist - and an estimate")
    P_("    from ONE feature set on ONE segment. It is not 'the' frontier.")

    # ------------------------------------------------------------------ stability
    P_("")
    P_("=" * 122)
    P_("=== STABILITY of the primary, by period. Recency is primary (section 5).")
    P_("=" * 122)
    dts = pd.to_datetime([L.sdate[s] for s in idx[oos]])
    p = PRED["M1_RIDGE"][oos]; s = np.sign(p); s[s == 0] = 1
    pnl = econ(s)
    P_(f"{'period':<16}{'N':>6}{'dir acc':>10}{'$/trade':>11}{'net $':>12}")
    for lab, m_ in ([(str(yy), dts.year == yy) for yy in sorted(set(dts.year))]
                    + [("t12m", dts >= dts.max() - pd.Timedelta(days=365)),
                       ("t6m", dts >= dts.max() - pd.Timedelta(days=182)),
                       ("t3m", dts >= dts.max() - pd.Timedelta(days=91))]):
        if m_.sum() < 5:
            continue
        acc = float((np.sign(yo[m_]) == s[m_])[np.sign(yo[m_]) != 0].mean())
        P_(f"{lab:<16}{int(m_.sum()):>6}{100*acc:>9.2f}%{pnl[m_].mean():>11,.0f}"
           f"{pnl[m_].sum():>12,.0f}")

    # ------------------------------------------------------------------ description
    sc = StandardScaler().fit(X)
    rg = Ridge(alpha=10.0).fit(sc.transform(X), y)
    P_("")
    P_("    RIDGE COEFFICIENTS on the full sample - DESCRIPTION ONLY, not a result:")
    for nm, cv in sorted(zip(names, rg.coef_), key=lambda t: -abs(t[1]))[:8]:
        P_(f"        {nm:<18}{cv:>10,.1f}")
    pd.DataFrame(dict(session=idx[oos], date=dts,
                      y=yo, pred_ridge=PRED["M1_RIDGE"][oos],
                      pred_gbt=PRED["M2_GBT"][oos])).to_csv(
        os.path.join(OUT, "predictions.csv"), index=False)
    P_(f"\n[done {_time.time()-t0:.0f}s]")
    out.close()


if __name__ == "__main__":
    main()
