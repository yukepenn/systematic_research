"""WE_W43 INSTRUMENTS (spec preregistered): re-derive, do not transplant.

W11 ran the NQ engine on ES/RTY/YM and it lost on all three, and the campaign has since said
"the edge is NQ-specific". Two of the transplanted quantities are not dimensionless:
  * the reversal threshold clamp is [40, 1200] TICKS - in relative terms [0.05 %, 1.5 %] of
    price on NQ but [0.18 %, 5.5 %] on ES and RTY and [0.09 %, 2.7 %] on YM
  * the session box is -$1,300 / +$1,000 in DOLLARS against point values 20 / 50 / 50 / 5
So W11 established that NQ's tick- and dollar-denominated constants do not transplant, which
is a much weaker claim. Here both are re-derived from each instrument's OWN data, as the same
multiple of its own sigma and the same fraction of its own session dollar range, and the
question is asked again. Everything dimensionless is untouched.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, COMM_RT, STRESS_RT, sm14_1m                 # noqa: E402
from run_we_w03 import cd_signals                                        # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS, weekly                               # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W43_INSTRUMENTS", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260843)
INST = {"NQ": (None, 20.0), "ES": ("es_1m_2022_2026.parquet", 50.0),
        "RTY": ("rty_1m_2022_2026.parquet", 50.0), "YM": ("ym_1m_2022_2026.parquet", 5.0)}


def load_inst(sym):
    if sym == "NQ":
        return load_deep("2022-01-01", "2026-07-31 17:00")
    fn = INST[sym][0]
    d = pd.read_parquet(os.path.join(ROOT, "runs", f"SM1M_{sym}_SUBSTRATE", "out", fn))
    d["time"] = pd.to_datetime(d["time"])
    d = d.sort_values("time").reset_index(drop=True)
    t = d["time"].values.astype("datetime64[s]")
    n = len(d)
    fb = np.zeros(n, bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(n, bool); lb[:-1] = fb[1:]; lb[-1] = True
    sid = np.cumsum(fb) - 1
    n_sess = sid[-1] + 1
    idx = np.arange(n)
    last_of = np.zeros(n_sess, np.int64); last_of[sid[lb]] = idx[lb]
    sess_end = t[last_of] + np.timedelta64(60, "s")
    sess_date = sess_end.astype("datetime64[D]")
    iso = pd.Series(pd.to_datetime(sess_date)).dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    return dict(df=d, t=t, o=d["open"].values.astype(float), h=d["high"].values.astype(float),
                l=d["low"].values.astype(float), c=d["close"].values.astype(float),
                v=d["volume"].values.astype(float), n=n, fb=fb, lb=lb, sid=sid,
                n_sess=n_sess, sess_end=sess_end, sess_date=sess_date, wk=wk)


def sigma_med(D, vp=460):
    s = pd.Series(np.abs(np.diff(D["c"], prepend=D["c"][0]))).rolling(
        vp, min_periods=30).mean().values
    return float(np.nanmedian(s))


def sess_dollar_range(D, pv):
    idx = np.arange(D["n"])
    r = np.array([D["h"][D["sid"] == s].max() - D["l"][D["sid"] == s].min()
                  for s in range(D["n_sess"])])
    return float(np.median(r) * pv)


def ctx(D):
    n = D["n"]
    rng_, dmove, atr14, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)
    _, cd = cd_signals(D)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    dL = lag_b(cd >= 0)
    atr_l = np.concatenate([[atr14[0]], atr14[:-1]])
    idx = np.arange(n)
    pv_ = vv_ = 0.0
    vwap = np.full(n, np.nan)
    sopen = np.zeros(n)
    for i in range(n):
        if D["fb"][i]:
            pv_ = vv_ = 0.0
        pv_ += D["c"][i] * D["v"][i]; vv_ += D["v"][i]
        vwap[i] = pv_ / vv_ if vv_ > 0 else np.nan
    sess_ret = np.zeros(D["n_sess"])
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        sopen[m] = D["o"][m[0]]
        sess_ret[s] = D["c"][m[-1]] - D["o"][m[0]]
    c_l = np.concatenate([[D["c"][0]], D["c"][:-1]])
    vwap_l = np.concatenate([[np.nan], vwap[:-1]])
    up = np.concatenate([[0], np.sign(np.diff(D["c"]))])
    rl = np.zeros(n); r = 0
    for i in range(1, n):
        r = r + 1 if up[i] == up[i - 1] and up[i] != 0 else (1 if up[i] != 0 else 0)
        rl[i] = r * (1 if up[i] > 0 else -1)
    volnorm = pd.Series(D["v"]).rolling(240, min_periods=30).mean().values
    return dict(ratio=ratio, norm=norm, dL=dL, atr_l=atr_l,
                dist_open=(c_l - sopen) / np.maximum(atr_l, 1e-9),
                dist_vwap=(c_l - vwap_l) / np.maximum(atr_l, 1e-9),
                prev_ret=np.concatenate([[0.0], sess_ret[:-1]])[D["sid"]],
                runlen=np.concatenate([[0], rl[:-1]]),
                delta_mag=np.concatenate([[0.0],
                                          (np.abs(cd) / np.maximum(volnorm, 1e-9))[:-1]]))


def fills_pv(D, pos_arr, pv, halt, target, size_arr=None, comm=COMM_RT):
    """Identical semantics to fills_qexit: DIRECTION from bar i-1, SIZE read at the entry bar.

    W43 amendment 1: read 1 conflated direction and size into one array, so a bar where the
    vote had just turned off suppressed an entry the incumbent would have taken. That broke
    the built-in identity check (NQ 're-derived' must reproduce the incumbent exactly) and
    voided read 1.
    """
    t, o, c = D["t"], D["o"], D["c"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    trades = []
    u = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False
        want = int(pos_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped:
            want = 0
        if (want > 0) != (u > 0):
            if u > 0:
                pnl = u * (o[i] - epx) * pv - comm * u
                trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += pnl
                if spnl <= -halt or (target is not None and spnl >= target):
                    stopped = True; want = 0
            if want > 0:
                u = int(size_arr[i]) if size_arr is not None else 1
                if u < 1:
                    u = 0
                else:
                    epx, eti = o[i], i
            else:
                u = 0
        if lb[i] and u > 0:
            pnl = u * (c[i] - epx) * pv - comm * u
            trades.append(dict(d=1, u=u, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            u = 0
    return trades


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "instruments.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    # ---- NQ reference constants -------------------------------------------------------
    DN = load_inst("NQ")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    sN = sigma_med(DN)
    rN = sess_dollar_range(DN, 20.0)
    mult_lo, mult_hi, mult_stop = 10.0 / sN, 300.0 / sN, 44.75 / sN
    P_(f"=== RE-DERIVATION CONSTANTS (from NQ, applied to each instrument's OWN units) ===")
    P_(f"   NQ median sigma {sN:.3f} pts -> clamp multiples "
       f"[{mult_lo:.2f}, {mult_hi:.2f}] x sigma, initial stop {mult_stop:.2f} x sigma")
    P_(f"   NQ median session $ range (1 contract) ${rN:,.0f} -> halt is "
       f"{1300/rN*100:.2f} % of it, target {1000/rN*100:.2f} %")
    rows = []
    series = {}
    hdr = (f"{'arm':<26}{'n':>6}{'$/tr':>9}{'wk$':>9}{'wk+%':>7}{'worst':>10}{'CVaR5':>10}"
           f"{'shrp':>8}{'eff':>8}{'stress':>9}")

    for sym, (fn, pv) in INST.items():
        D = load_inst(sym) if sym != "NQ" else DN
        sX = sigma_med(D)
        rX = sess_dollar_range(D, pv)
        smin, smax = mult_lo * sX, mult_hi * sX
        stopm = mult_stop * sX
        halt = 1300.0 * rX / rN
        tgt = 1000.0 * rX / rN
        X = ctx(D)
        n = D["n"]
        P_(f"\n=== {sym}: sigma {sX:.3f} pts | clamp [{smin:.2f}, {smax:.2f}] pts | "
           f"box -${halt:,.0f} / +${tgt:,.0f} | PV ${pv:.0f} [{_time.time()-t0:.0f}s] ===")
        wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}
        tarr = D["t"]

        def wk_of(ts, tarr=tarr, D=D, wkmap=wkmap, n=n):
            i = int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))
            return wkmap[int(D["sid"][i])]
        NS = len(np.unique(D["sid"][(tarr >= A) & (tarr < B)]))
        for tag, kw in (("re-derived", dict(smin_pts=smin, smax_pts=smax, stopm_pts=stopm)),
                        ("W11 transplant", {})):
            if sym == "NQ" and tag == "W11 transplant":
                continue
            vs = []
            for mem in MEMBERS:
                tg = sm14_1m(D, 460, return_targets=True, volmults=MEMBERS[mem], **kw)
                for q in QS:
                    okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0)
                                                              | (X["ratio"] >= q))
                    for dg in (True, False):
                        a = (okv & X["dL"]) if dg else okv
                        vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
            pos = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
            base = fills_pv(D, pos, pv, halt if tag == "re-derived" else 1300.0,
                            tgt if tag == "re-derived" else 1000.0)
            bl = [x for x in base if A <= np.datetime64(x["et"]) < B]
            ent = np.array([int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
                            for x in bl])
            if len(ent) < 200:
                P_(f"   {tag}: only {len(ent)} trades, skipped")
                continue
            sc, _ = causal_score(X, ent, window=WIN)
            trl = fills_pv(D, pos, pv,
                           halt if tag == "re-derived" else 1300.0,
                           tgt if tag == "re-derived" else 1000.0,
                           size_arr=np.where(sc >= 3, 2, 1).astype(np.int8))
            d = weekly(trl, wk_of, A, B)
            ks = sorted(d)
            v = np.array([d[k] for k in ks])
            p = np.array([x["pnl"] for x in trl if A <= np.datetime64(x["et"]) < B])
            nw = max(1, int(np.ceil(0.05 * len(v))))
            cv = float(np.sort(v)[:nw].mean())
            s_ = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
            eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
            st = float(v.mean() - STRESS_RT * len(p) / len(v))
            P_(hdr if tag == "re-derived" else "")
            P_(f"{sym + ' ' + tag:<26}{len(p):>6}{p.mean():>9.1f}{v.mean():>9,.0f}"
               f"{(v>0).mean()*100:>7.1f}{v.min():>10,.0f}{cv:>10,.0f}{s_:>8.3f}"
               f"{eff:>8.3f}{st:>9,.0f}")
            rows.append(dict(inst=sym, arm=tag, n=len(p), per_trade=round(float(p.mean()), 1),
                             wk=round(float(v.mean())), worst=round(float(v.min())),
                             cvar5=round(cv), sharpe=round(s_, 3), eff=round(eff, 3),
                             stress=round(st)))
            if sym == "NQ":
                okid = abs(float(v.mean()) - 1470.0) < 25 and abs(eff - 0.198) < 0.01
                P_(f"   B1 IDENTITY (NQ re-derived must equal the incumbent "
                   f"$1,470/wk, eff 0.198): {'PASS' if okid else 'FAIL - RUN VOID'}")
                if not okid:
                    out.close(); return
            if tag == "re-derived":
                series[sym] = dict(zip(ks, v))
            # per year
            for y in (2022, 2023, 2024, 2025, 2026):
                a_ = max(A, np.datetime64(f"{y}-01-01"))
                b_ = min(B, np.datetime64(f"{y+1}-01-01"))
                if a_ >= b_:
                    continue
                dy = weekly(trl, wk_of, a_, b_)
                if len(dy) < 8:
                    continue
                vy = np.array(list(dy.values()))
                py = np.array([x["pnl"] for x in trl if a_ <= np.datetime64(x["et"]) < b_])
                sty = float(vy.mean() - STRESS_RT * len(py) / len(vy))
                rows.append(dict(inst=sym, arm=f"{tag} {y}", n=len(py),
                                 wk=round(float(vy.mean())), worst=round(float(vy.min())),
                                 stress=round(sty)))
                if tag == "re-derived":
                    P_(f"     {y}: ${vy.mean():>8,.0f}/wk  worst ${vy.min():>10,.0f}  "
                       f"stress ${sty:>8,.0f}")

    # ---- correlations + equal-risk basket ---------------------------------------------
    P_(f"\n=== WEEKLY P&L CORRELATIONS (re-derived arms) [{_time.time()-t0:.0f}s] ===")
    syms = [s for s in INST if s in series]
    allk = sorted(set().union(*[set(series[s]) for s in syms]))
    M = np.array([[series[s].get(k, 0.0) for k in allk] for s in syms])
    P_("        " + "".join(f"{x:>8}" for x in syms))
    for i, s in enumerate(syms):
        P_(f"{s:<8}" + "".join(f"{np.corrcoef(M[i], M[j])[0,1]:>8.2f}"
                               for j in range(len(syms))))
    vN = M[0]
    dd = np.argsort(vN)[:max(3, len(vN) // 10)]
    P_("   inside NQ's worst-decile weeks:")
    P_(f"{'NQ':<8}" + "".join(f"{np.corrcoef(M[0][dd], M[j][dd])[0,1]:>8.2f}"
                              for j in range(len(syms))))

    P_(f"\n=== EQUAL-RISK BASKET vs NQ alone at the SAME total weekly sigma ===")
    sd = M.std(axis=1, ddof=1)
    keep = [i for i in range(len(syms)) if M[i].mean() > 0]
    P_(f"   sleeves with positive mean weekly P&L: {[syms[i] for i in keep]}")
    P_(f"{'basket':<26}{'wk$':>10}{'wk+%':>7}{'worst':>10}{'CVaR5':>10}{'shrp':>8}"
       f"{'eff':>8}{'cvEff':>8}")

    def rep(nm, v):
        nw = max(1, int(np.ceil(0.05 * len(v))))
        cv = float(np.sort(v)[:nw].mean())
        s_ = float(v.mean() / v.std(ddof=1)) if v.std(ddof=1) > 0 else 0.0
        eff = float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9
        cve = float(v.mean() / abs(cv)) if cv < 0 else 9.9
        P_(f"{nm:<26}{v.mean():>10,.0f}{(v>0).mean()*100:>7.1f}{v.min():>10,.0f}"
           f"{cv:>10,.0f}{s_:>8.3f}{eff:>8.3f}{cve:>8.3f}")
        rows.append(dict(inst="BASKET", arm=nm, wk=round(float(v.mean())),
                         worst=round(float(v.min())), cvar5=round(cv),
                         sharpe=round(s_, 3), eff=round(eff, 3), cveff=round(cve, 3)))
        return v
    if keep:
        w = np.array([1.0 / sd[i] for i in keep])
        bask = sum(w[j] * M[i] for j, i in enumerate(keep))
        tot_sd = bask.std(ddof=1)
        rep(f"equal-risk {'+'.join(syms[i] for i in keep)}", bask)
        rep("NQ alone at same sigma", vN * (tot_sd / sd[0]))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
