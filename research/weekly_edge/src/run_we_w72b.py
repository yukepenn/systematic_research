"""WE_W72 amendment 1 - THE ANCHOR. Is the object's fragility B-MOM, or the ANCHOR CHOICE?

Read 1 found that the ONLY durable occupant of the OR slot is the same displacement rule
measured from the 18:00 SESSION open instead of the 09:31 RTH open (pre-2022 t = 1.83 vs the
incumbent's 0.93 over the same sixteen years) - and that it costs modern production.

That is a signature of the CHOICE, not of the mechanism. This runs the arms that stop choosing.
Spec: runs/WE_W72_ORCHANNEL/amendment_1.yaml, committed before this ran.
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
from run_we_w01 import ROOT, PV                                          # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import QS                                                # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from run_we_w51 import A, B                                              # noqa: E402
from run_we_w51c import setup, dd_profile                                # noqa: E402
from run_we_w66 import WIDE                                              # noqa: E402
from we_channels import build_channels, shift_channel                    # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W72_ORCHANNEL", "out")
W66OUT = os.path.join(ROOT, "runs", "WE_W66_INNER", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
CUTS = (14, 16, 18, 10 ** 9)
DD_TARGET = 20245.0
SPLIT = pd.Timestamp("2022-01-01")
NDRAW = 40


def combos(ch, bmom):
    """The six arms. sign(a+b) fires if either anchor fires and abstains when they conflict."""
    x9, x2 = ch["X9a_disp_sessanchor"], ch["X2_disp"]
    return {
        "A0_incumbent": bmom,
        "A1_sess": x9,
        "A2_or_both": np.sign(bmom.astype(np.int16) + x9.astype(np.int16)).astype(np.int8),
        "A3_or_disp_both": np.sign(x2.astype(np.int16) + x9.astype(np.int16)).astype(np.int8),
        "A4_disp_rth": x2,
        "A5_and_both": np.where(bmom == x9, bmom, 0).astype(np.int8),
    }


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "anchor.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    D, X, TG, st, en = setup()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    NS = len(sess_in)
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True
    sess_wk = np.array([wkmap[s] for s in range(D["n_sess"])])
    keys_w = sorted(set(sess_wk[sess_in]))
    wk_idx = np.array([keys_w.index(sess_wk[s]) for s in sess_in])
    NW = len(keys_w)
    sdate = pd.to_datetime(D["sess_date"])[sess_in]
    yrs = sorted(set(sdate.year))
    sess_yr = sdate.year.to_numpy()

    z = np.load(os.path.join(W66OUT, f"mem460_clamp_{D['n']}.npz"))
    mem, bmom, tilt = z["mem"], z["bmom"], z["tilt"]
    idx_of = {v: k for k, v in enumerate(WIDE)}
    cols13 = {c: [idx_of[v] for v in L13 if v <= c] for c in CUTS}
    fb, sess_end = D["fb"], D["sess_end"]
    blocked = tarr >= sess_end[sid] - np.timedelta64(30 * 60, "s")
    flat = tarr >= sess_end[sid] - np.timedelta64(21 * 60, "s")
    CH = build_channels(D, which=["X9a_disp_sessanchor", "X2_disp"])
    ARMS = combos(CH, bmom)
    P_(f"=== substrate {n:,} bars, {NS} sessions in window, {NW} weeks "
       f"[{_time.time()-t0:.0f}s]")

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        tgt = np.zeros(n, np.int8)
        for i in range(n):
            p = 0 if (i == 0 or fb[i]) else tgt[i - 1]
            g = p
            if flat[i]:
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

    def object_from(chan, w=2.83):
        vs = []
        for c in CUTS:
            cols = cols13[c]
            if len(cols) < 3:
                continue
            s = mem[:, cols].sum(axis=1).astype(np.int32)
            T = np.clip(ra(s / float(len(cols)) * 10.0), -10, 10)
            ag = (np.sign(s) == tilt) & (s != 0) & (tilt != 0)
            Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
            tg = hyst(0.7086 * Tp + w * chan.astype(float))
            for q in QS:
                okv = np.ones(n, bool) if q is None else ((X["norm"] <= 0) | (X["ratio"] >= q))
                for dg in (True, False):
                    a = okv & (X["dL"] if dg else True)
                    vs.append(np.where((tg > 0) & a, 1, 0).astype(np.int8))
        pos = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
        base = fills_daily(D, pos, halt=1300, target=1000)
        e = np.array([i_of(x["et"]) for x in base if A <= np.datetime64(x["et"]) < B])
        if len(e) < 150:
            return None
        sc, _ = causal_score(X, e, window=WIN)
        sz = np.where(sc >= 3, 2, 1).astype(np.int8)
        trl = [x for x in fills_qexit(D, pos, sz, sc) if in_win[int(sid[i_of(x["et"])])]]
        sp = np.zeros(D["n_sess"])
        for x in trl:
            sp[int(sid[i_of(x["et"])])] += x["pnl"]
        return sp[sess_in], len(trl)

    def wkser(sp, mask=None):
        s_ = sp if mask is None else sp[mask]
        wi = wk_idx if mask is None else wk_idx[mask]
        cnt = np.bincount(wi, minlength=NW) > 0
        return np.bincount(wi, weights=s_, minlength=NW)[cnt]

    def met(sp, ntr, name, mask=None):
        s_ = sp if mask is None else sp[mask]
        v = wkser(sp, mask)
        if len(v) < 12:
            return None
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        tr = s_ != 0
        stk = max((len(list(g)) for kk, g in itertools.groupby(v < 0) if kk), default=0)
        return dict(arm=name, ntr=ntr, pts=float(s_.sum() / PV / max(len(s_), 1)),
                    daypos=100 * float((s_ > 0).mean()),
                    trdpos=100 * float((s_[tr] > 0).mean()) if tr.any() else 0.0,
                    wkpos=100 * float((v > 0).mean()), wstreak=int(stk),
                    medwk=float(np.median(v)) * k, weekly=float(v.mean()) * k,
                    dd_top5=dp["dd_mean_top5"] * k, ulcer=dp["ulcer"] * k,
                    worst=float(v.min()) * k)

    HDR = (f"{'arm':<22}{'trds':>7}{'pts':>7}{'day+%':>7}{'trdD+%':>8}{'wk+%':>7}"
           f"{'wStrk':>7}{'medWk$':>9}{'weekly$':>10}{'top5DD':>9}{'ulcer':>8}{'worst$':>9}")

    def show(r, tag=""):
        P_(f"{r['arm']:<22}{r['ntr']:>7}{r['pts']:>7.2f}{r['daypos']:>7.1f}"
           f"{r['trdpos']:>8.1f}{r['wkpos']:>7.1f}{r['wstreak']:>7}{r['medwk']:>9,.0f}"
           f"{r['weekly']:>10,.0f}{r['dd_top5']:>9,.0f}{r['ulcer']:>8,.0f}"
           f"{r['worst']:>9,.0f}{tag}")

    P_(f"\n{'='*128}\n=== PHASE 1: THE SIX ARMS. Only the OR-slot occupant differs.")
    P_(f"{'='*128}")
    P_(HDR)
    rows, led = [], {}
    for name, chan in ARMS.items():
        r = object_from(chan)
        if r is None:
            P_(f"{name:<22}   (skipped)"); continue
        sp, ntr = r
        m_ = met(sp, ntr, name)
        show(m_, "   <- INCUMBENT" if name == "A0_incumbent" else "")
        rows.append(m_); led[name] = sp
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "anchor_arms.csv"), index=False)
    inc = led["A0_incumbent"]
    b1 = inc.sum() / PV / NS
    P_(f"\n   B1 GATE: {b1:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(b1 - 14.72) < 0.6 else 'FAIL - VOID'} [{_time.time()-t0:.0f}s]")

    P_(f"\n=== PER YEAR (pts/session) ===")
    P_(f"{'arm':<22}" + "".join(f"{y:>9}" for y in yrs) + f"{'yrs>0':>8}")
    for name, sp in led.items():
        d = [sp[sess_yr == y].sum() / PV / max((sess_yr == y).sum(), 1) for y in yrs]
        P_(f"{name:<22}" + "".join(f"{x:>9.2f}" for x in d)
           + f"{sum(1 for x in d if x > 0):>8}")

    # ============================================================ PHASE 2: ROLLING WINDOWS
    P_(f"\n{'='*128}")
    P_("=== PHASE 2: ROLLING 24-MONTH WINDOWS vs A0. The test that has killed four candidates.")
    P_(f"{'='*128}")
    ends = pd.date_range(sdate.min() + pd.DateOffset(months=24), sdate.max(), freq="ME")
    wins = [(e - pd.DateOffset(months=24), e) for e in ends]
    P_(f"   {len(wins)} windows, {wins[0][0].date()} -> {wins[-1][1].date()}")
    P_(f"\n{'arm':<22}{'weekly$ win%':>15}{'wk+% win%':>12}{'top5DD win%':>14}"
       f"{'ALL THREE':>12}")
    roll_rows = []
    for name, sp in led.items():
        if name == "A0_incumbent":
            continue
        w1 = w2 = w3 = wa = 0
        for a_, b_ in wins:
            m = (sdate >= a_) & (sdate < b_)
            if m.sum() < 100:
                continue
            r_c, r_i = met(sp, 0, name, m), met(inc, 0, "i", m)
            if r_c is None or r_i is None:
                continue
            c1 = r_c["weekly"] > r_i["weekly"]
            c2 = r_c["wkpos"] > r_i["wkpos"]
            c3 = r_c["dd_top5"] < r_i["dd_top5"]
            w1 += c1; w2 += c2; w3 += c3; wa += (c1 and c2 and c3)
        nn = sum(1 for a_, b_ in wins if ((sdate >= a_) & (sdate < b_)).sum() >= 100)
        P_(f"{name:<22}{100*w1/nn:>14.0f}%{100*w2/nn:>11.0f}%{100*w3/nn:>13.0f}%"
           f"{100*wa/nn:>11.0f}%")
        roll_rows.append(dict(arm=name, n_windows=nn, money=100 * w1 / nn,
                              wkpos=100 * w2 / nn, dd=100 * w3 / nn, all3=100 * wa / nn))
    pd.DataFrame(roll_rows).to_csv(os.path.join(OUT, "anchor_rolling.csv"), index=False)

    # ============================================================ PHASE 3: ERA TEST
    P_(f"\n{'='*128}\n=== PHASE 3: THE COMBINED CHANNELS STANDALONE, BOTH ERAS")
    P_(f"{'='*128}")
    DD = load_deep("2006-01-05", "2026-05-29 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    flat_d = DD["t"] >= DD["sess_end"][DD["sid"]] - np.timedelta64(21 * 60, "s")
    CHD = build_channels(DD, which=["X9a_disp_sessanchor", "X2_disp"])
    zb = None
    # the deep-window bmom must be recomputed: build_channels' X0v matched the engine at
    # 99.992 %, which read 1 established is close enough to carry the era comparison
    CHD_all = build_channels(DD, which=["X0v_bmom", "X9a_disp_sessanchor", "X2_disp"])
    ARMS_D = combos(CHD_all, CHD_all["X0v_bmom"])
    sd_d = pd.to_datetime(DD["sess_date"])
    P_(f"   deep {DD['n']:,} bars, {DD['n_sess']:,} sessions [{_time.time()-t0:.0f}s]")
    P_(f"\n{'arm':<22}{'era':<12}{'trades':>9}{'net $':>13}{'$/trd':>9}{'t':>8}"
       f"{'win%':>7}{'PF':>7}")
    era_rows = []
    for name, chan in ARMS_D.items():
        trl = sfills(DD, np.where(flat_d, 0, chan).astype(np.int8), halt=1300.0, target=1000.0)
        if len(trl) < 100:
            continue
        df = pd.DataFrame(dict(et=pd.to_datetime([x["et"] for x in trl]),
                               pnl=np.array([x["pnl"] for x in trl])))
        for lab, m in (("2006-2021", df["et"] < SPLIT), ("2022-2026", df["et"] >= SPLIT)):
            q = df[m]
            if len(q) < 50:
                continue
            se = q["pnl"].std(ddof=1) / np.sqrt(len(q))
            gw = q.loc[q["pnl"] > 0, "pnl"].sum(); gl = -q.loc[q["pnl"] < 0, "pnl"].sum()
            P_(f"{name:<22}{lab:<12}{len(q):>9,}{q['pnl'].sum():>13,.0f}"
               f"{q['pnl'].mean():>9,.1f}{q['pnl'].mean()/se:>8.2f}"
               f"{100*float((q['pnl']>0).mean()):>6.1f}%{(gw/gl if gl else np.nan):>7.3f}")
            era_rows.append(dict(arm=name, era=lab, trades=len(q),
                                 net=float(q["pnl"].sum()), per_trade=float(q["pnl"].mean()),
                                 t=float(q["pnl"].mean() / se),
                                 pf=float(gw / gl) if gl else np.nan))
        # trailing-24-month recency check on the channel itself
        rr = []
        for e in pd.date_range(df["et"].min() + pd.DateOffset(months=24), df["et"].max(),
                               freq="ME"):
            q = df[(df["et"] > e - pd.DateOffset(months=24)) & (df["et"] <= e)]
            if len(q) < 60:
                continue
            se = q["pnl"].std(ddof=1) / np.sqrt(len(q))
            rr.append(float(q["pnl"].mean() / se) if se > 0 else 0.0)
        if rr:
            P_(f"{'':<22}{'roll24':<12}{len(rr):>9,} windows, median t {np.median(rr):+.2f}, "
               f"latest t {rr[-1]:+.2f} at the "
               f"{100*float(np.mean(np.array(rr) < rr[-1])):.0f}th pctile of its own history")
        P_("")
    pd.DataFrame(era_rows).to_csv(os.path.join(OUT, "anchor_eras.csv"), index=False)

    # ============================================================ PHASE 4: NULL
    P_(f"\n{'='*128}\n=== PHASE 4: N_shift NULL ({NDRAW} draws) on A0 and on the best challenger")
    P_(f"{'='*128}")
    P_("   session-wise circular shift of the occupant's path: preserves firing rate, latch-run")
    P_("   distribution and intraday shape EXACTLY; destroys only which day the path lands on.")
    cand = [r for r in rows if r["arm"] != "A0_incumbent"]
    best = max(cand, key=lambda r: r["weekly"])["arm"]
    P_(f"   best challenger by weekly $ at a fixed drawdown: {best}\n")
    rng = np.random.default_rng(20260872)
    P_(f"{'arm':<22}{'real pts':>10}{'null mean':>11}{'null p95':>10}{'pctile':>9}"
       f"{'real wk$':>11}{'null wk$':>11}{'pctile':>9}")
    null_rows = []
    for name in ("A0_incumbent", best):
        ks = rng.choice(np.arange(3, 1100), size=NDRAW, replace=False)
        pv, wv = [], []
        for k in ks:
            r = object_from(shift_channel(ARMS[name], D, int(k)))
            if r is None:
                continue
            sp2, ntr2 = r
            m2 = met(sp2, ntr2, "null")
            pv.append(m2["pts"]); wv.append(m2["weekly"])
        pv, wv = np.array(pv), np.array(wv)
        rp = [r for r in rows if r["arm"] == name][0]
        P_(f"{name:<22}{rp['pts']:>10.2f}{pv.mean():>11.2f}"
           f"{np.percentile(pv,95):>10.2f}{100*float((pv<rp['pts']).mean()):>8.0f}%"
           f"{rp['weekly']:>11,.0f}{wv.mean():>11,.0f}"
           f"{100*float((wv<rp['weekly']).mean()):>8.0f}%")
        null_rows.append(dict(arm=name, n=len(pv), real_pts=rp["pts"],
                              null_pts_mean=float(pv.mean()),
                              pctile_pts=100 * float((pv < rp["pts"]).mean()),
                              real_weekly=rp["weekly"], null_weekly_mean=float(wv.mean()),
                              pctile_weekly=100 * float((wv < rp["weekly"]).mean())))
    pd.DataFrame(null_rows).to_csv(os.path.join(OUT, "anchor_nulls.csv"), index=False)
    P_(f"\n=== STATUS: diagnostic. NOTHING ADOPTED. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
