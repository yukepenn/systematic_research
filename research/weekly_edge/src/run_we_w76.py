"""WE_W76 - THE 44 SESSIONS OF 2026 NOBODY HAS EVER READ.

Spec: runs/WE_W76_FORWARD2026/spec.yaml, committed BEFORE this ran.

`load_deep` hardcoded a substrate ending 2026-05-29 while every caller asked for 2026-07-31, so
the campaign has been silently truncated for its entire life. The newer substrate is bit-exact on
all 1,558,497 overlapping rows and carries 61,547 more bars to 2026-07-31.

Nothing has ever been fitted, screened or looked at on those sessions. They are a genuine
out-of-sample window for every object and every decision made up to today, and this wave reads
them ONCE, with the full challenger set at FROZEN parameters, so the read cannot be repeated
selectively later.
"""
from __future__ import annotations

import itertools
import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, sm14_1m             # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_channels import build_channels                                   # noqa: E402
from we_quality import build_context                                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
os.makedirs(OUT, exist_ok=True)
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
SPLIT = pd.Timestamp("2026-05-30")      # first session never seen by any prior wave
CACHE = os.path.join(OUT, "mem_ext.npz")


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "forward.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    X = build_context(D)
    P_(f"=== EXTENDED substrate {n:,} bars, {D['n_sess']:,} sessions, "
       f"{D['t'][0]} -> {D['t'][-1]} [{_time.time()-t0:.0f}s]")
    P_(f"    overlap with the old substrate asserted BIT-EXACT at load time on all six columns.")

    st = np.zeros(D["n_sess"], np.int64)
    st[sid[D["fb"]]] = np.flatnonzero(D["fb"])
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sess_wk = np.array([D["wk"][s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    HELD = np.asarray(sdate >= SPLIT)      # DatetimeIndex comparison is already an ndarray
    P_(f"    window {sdate.min().date()} -> {sdate.max().date()}: {NS} sessions, {NW} weeks")
    P_(f"    IN-SAMPLE  (seen by all 75 prior waves): {int((~HELD).sum())} sessions")
    P_(f"    HELD OUT   (never read by any code):     {int(HELD.sum())} sessions "
       f"/ {len(set(sess_wk[sess_in][HELD]))} weeks, {sdate[HELD].min().date()} -> "
       f"{sdate[HELD].max().date()}")

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def daily(trl):
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in]

    # ------------------------------------------------------- one engine pass, frozen params
    if os.path.exists(CACHE):
        z = np.load(CACHE); mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
        P_(f"    member matrix from cache [{_time.time()-t0:.0f}s]")
    else:
        _, mem, bmom, tilt = sm14_1m(D, 460, volmults=L13, return_members=True)
        np.savez_compressed(CACHE, mem=mem, bmom=bmom, tilt=tilt)
        P_(f"    member matrix built on the extended window [{_time.time()-t0:.0f}s]")

    fb, sess_end = D["fb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flatm = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    idx_l13 = {v: k for k, v in enumerate(L13)}

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        tgt = np.zeros(n, np.int8)
        for i in range(n):
            p = 0 if (i == 0 or fb[i]) else tgt[i - 1]
            g = p
            if flatm[i]:
                g = 0
            elif p == 0:
                if not blocked[i]:
                    g = 1 if M[i] >= 3.0 else (-1 if M[i] <= -3.0 else p)
            elif p > 0:
                g = -1 if (M[i] <= -3.0 and not blocked[i]) else (0 if M[i] <= 1.0 else p)
            else:
                g = 1 if (M[i] >= 3.0 and not blocked[i]) else (0 if M[i] >= -1.0 else p)
            tgt[i] = g
        return tgt

    def TG_for(chan):
        d = {}
        for name, vols in MEMBERS.items():
            cols = [idx_l13[v] for v in vols]
            s_ = mem[:, cols].sum(axis=1).astype(np.int32)
            T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
            ag = (np.sign(s_) == tilt) & (s_ != 0) & (tilt != 0)
            Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
            d[name] = hyst(0.7086 * Tp + 2.83 * chan.astype(float))
        return d

    def vote_(TGx, side):
        vs = []
        for m_ in MEMBERS:
            tg = TGx[m_]
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a_ = okv & (X["dL"] if side > 0 else X["dS"]) if dg else okv
                    hit = (tg > 0) if side > 0 else (tg < 0)
                    vs.append(np.where(hit & a_, 1, 0).astype(np.int8))
        return np.vstack(vs).mean(axis=0)

    def long_obj(TGx):
        p = (vote_(TGx, +1) >= 0.5).astype(np.int8)
        bb = fills_daily(D, p, halt=1300, target=1000)
        ee = np.array([i_of(x["et"]) for x in bb if A <= np.datetime64(x["et"]) < B])
        s_, _ = causal_score(X, ee, window=WIN)
        tr = [x for x in fills_qexit(D, p, np.where(s_ >= 3, 2, 1).astype(np.int8), s_)
              if in_win[int(sid[i_of(x["et"])])]]
        return tr

    S, NT = {}, {}
    TG0 = TG_for(bmom)
    tr = long_obj(TG0); S["P1"] = daily(tr); NT["P1"] = len(tr)
    p = -(vote_(TG0, -1) >= 0.5).astype(np.int8)
    tr = [x for x in sfills(D, p, halt=1300.0, target=1000.0)
          if in_win[int(sid[i_of(x["et"])])]]
    S["SHORT"] = daily(tr); NT["SHORT"] = len(tr)
    tr = [x for x in sfills(D, np.where(flatm, 0, bmom).astype(np.int8),
                            halt=1300.0, target=1000.0) if in_win[int(sid[i_of(x["et"])])]]
    S["BMOM"] = daily(tr); NT["BMOM"] = len(tr)
    P_(f"    P1 / SHORT / BMOM rebuilt on the extended window [{_time.time()-t0:.0f}s]")

    CH = build_channels(D)
    for k, v in CH.items():
        if k.startswith("X0"):
            continue
        tr = long_obj(TG_for(v))
        S["w72:" + k.split("_", 1)[0]] = daily(tr); NT["w72:" + k.split("_", 1)[0]] = len(tr)
    P_(f"    {len(CH)-1} W72 channel arms rebuilt [{_time.time()-t0:.0f}s]")
    pd.DataFrame({"date": sdate.strftime("%Y-%m-%d"), "held_out": HELD, **S}).to_csv(
        os.path.join(OUT, "streams_extended.csv"), index=False)

    # ------------------------------------------------------- the panel
    def wkv(v, m):
        wi = wk_idx[m]
        cnt = np.bincount(wi, minlength=NW) > 0
        return np.bincount(wi, weights=v[m], minlength=NW)[cnt]

    def pan(v, m, ntr_frac):
        w = wkv(v, m)
        dp = dd_profile(w)
        return dict(nsess=int(m.sum()), nwk=len(w), net=float(v[m].sum()),
                    pts=float(v[m].sum() / PV / max(m.sum(), 1)),
                    stress=float(v[m].sum() - STRESS_RT * ntr_frac),
                    daypos=100 * float((v[m] > 0).mean()),
                    wkpos=100 * float((w > 0).mean()), wmean=float(w.mean()),
                    wse=float(w.std(ddof=1) / np.sqrt(len(w))) if len(w) > 1 else np.nan,
                    worst=float(w.min()), maxdd=float(dp["maxdd"]))

    P_(f"\n{'='*150}")
    P_("=== THE FORWARD READ. Frozen parameters. Nothing re-derived, nothing selected.")
    P_(f"{'='*150}")
    P_(f"{'object':<16}| {'IN-SAMPLE 2022-07 -> 2026-05-29':^52} | "
       f"{'HELD OUT 2026-05-30 -> 2026-07-31':^58} |{'retain':>8}")
    P_(f"{'':<16}| {'pts':>7}{'net $':>11}{'wk+%':>7}{'wk mean':>10}{'worst':>9} | "
       f"{'pts':>7}{'net $':>10}{'stress$':>10}{'wk+%':>7}{'wk mean':>9}{'(SE)':>8}"
       f"{'worst':>8} |{'':>8}")
    rows = []
    for nm, v in S.items():
        fr = NT[nm] * float(HELD.sum()) / max(NS, 1)
        i_ = pan(v, ~HELD, NT[nm] * float((~HELD).sum()) / max(NS, 1))
        h_ = pan(v, HELD, fr)
        ret = 100 * h_["pts"] / i_["pts"] if i_["pts"] > 0 else np.nan
        P_(f"{nm:<16}| {i_['pts']:>7.2f}{i_['net']:>11,.0f}{i_['wkpos']:>6.1f}%"
           f"{i_['wmean']:>10,.0f}{i_['worst']:>9,.0f} | "
           f"{h_['pts']:>7.2f}{h_['net']:>10,.0f}{h_['stress']:>10,.0f}{h_['wkpos']:>6.1f}%"
           f"{h_['wmean']:>9,.0f}{h_['wse']:>8,.0f}{h_['worst']:>8,.0f} |"
           f"{(f'{ret:.0f}%' if ret == ret else '-'):>8}")
        rows.append(dict(obj=nm, **{f"is_{k}": vv for k, vv in i_.items()},
                         **{f"oos_{k}": vv for k, vv in h_.items()}, retain=ret))
    R = pd.DataFrame(rows); R.to_csv(os.path.join(OUT, "forward.csv"), index=False)

    p1 = R[R["obj"] == "P1"].iloc[0]
    P_(f"\n=== THE PREREGISTERED VERDICT (W29's standing bar: >= 80 % retention) ===")
    P_(f"   P1 in-sample {p1['is_pts']:.2f} pts/session -> held out {p1['oos_pts']:.2f} "
       f"= {p1['retain']:.0f} % retention over {int(p1['oos_nsess'])} sessions "
       f"/ {int(p1['oos_nwk'])} weeks")
    P_(f"   weekly mean ${p1['oos_wmean']:,.0f} +- ${p1['oos_wse']:,.0f} (SE), "
       f"positive weeks {p1['oos_wkpos']:.1f} %, worst week ${p1['oos_worst']:,.0f}")
    if p1["retain"] >= 80:
        P_(f"\n   -> PASS. The object's recorded numbers survive their first genuine forward")
        P_(f"      test. The campaign's headline figures stand.")
    else:
        P_(f"\n   -> FAIL. The headline figures are PROVISIONAL and must be re-quoted with the")
        P_(f"      forward window folded in. Stated plainly regardless of how it reads.")
    bestc = R[R["obj"] != "P1"].sort_values("oos_pts", ascending=False).head(3)
    P_(f"\n   best challengers on the held-out window (OBSERVATION ONLY - explicitly NOT")
    P_(f"   promoted; {int(p1['oos_nwk'])} weeks cannot rank anything):")
    for _, r in bestc.iterrows():
        P_(f"      {r['obj']:<14} {r['oos_pts']:>7.2f} pts/session, "
           f"weekly ${r['oos_wmean']:,.0f} +- ${r['oos_wse']:,.0f}")

    # ------------------------------------------------------- 2026 full-year ledger
    P_(f"\n{'='*150}\n=== 2026 AS IT NOW STANDS (all sessions, extended window)")
    P_(f"{'='*150}")
    y = sdate.year.to_numpy()
    m26 = y == 2026
    nw26 = len(set(sess_wk[sess_in][m26]))
    P_(f"   2026 now has {int(m26.sum())} sessions / {nw26} weeks "
       f"(was 106 / 22 before the extension - a {100*int(m26.sum())/106-100:.0f} % larger sample)")
    P_(f"\n{'object':<16}{'2026 net $':>13}{'pts/sess':>10}{'per week':>11}{'wk+%':>8}"
       f"{'worst wk':>11}{'max DD':>10}")
    for nm, v in S.items():
        w = wkv(v, m26); dp = dd_profile(w)
        P_(f"{nm:<16}{v[m26].sum():>13,.0f}{v[m26].sum()/PV/max(m26.sum(),1):>10.2f}"
           f"{w.mean():>11,.0f}{100*float((w>0).mean()):>7.1f}%{w.min():>11,.0f}"
           f"{dp['maxdd']:>10,.0f}")
    v = S["P1"]; w26 = wkv(v, m26); dd26 = dd_profile(w26)["maxdd"]
    ann = v[m26].sum() / max(m26.sum(), 1) * 252
    P_(f"\n   P1's 2026 RATE, ANNUALISED, at N contracts "
       f"(net $4.36/RT; the C1 stress line costs ~$95/wk/contract):")
    P_(f"{'contracts':<12}{'annualised $':>16}{'2026 max DD':>15}{'2026 worst wk':>16}"
       f"{'weekly $':>12}")
    for cN in (1, 2, 3, 4, 7):
        P_(f"{cN:<12}{ann*cN:>16,.0f}{dd26*cN:>15,.0f}{w26.min()*cN:>16,.0f}"
           f"{w26.mean()*cN:>12,.0f}")
    P_(f"\n=== STATUS: forward measurement. NOTHING ADOPTED, NOTHING SELECTED. "
       f"[{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
