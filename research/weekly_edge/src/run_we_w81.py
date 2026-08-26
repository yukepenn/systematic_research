"""WE_W81 - is P1's advantage over X9a confined to P1's own development window?

Spec: runs/WE_W81_DEVWINDOW/spec.yaml, committed before this ran.

W80 measured that X9a beats P1 on both sides of 2022-2026 and loses inside it. If the 09:31
anchor is fitted to the middle of the development sample, P1's advantage should be a function of
distance from that window and nothing else. The placebo arm (X2) and the regime-variable
regression are what stop that from being a story.
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
from run_we_w01 import ROOT, PV, sm14_1m                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, QS                                       # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w39 import WIN                                               # noqa: E402
from we_channels import build_channels                                   # noqa: E402
from we_fastctx import fast_build_context                                # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W81_DEVWINDOW", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
W80OUT = os.path.join(ROOT, "runs", "WE_W80_ANCHOR_HEADTOHEAD", "out")
L13 = [6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30]
DEV_A, DEV_B = pd.Timestamp("2022-07-01"), pd.Timestamp("2026-08-01")


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "devwindow.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    # ------------------------------------------------ deep: P1 and X9a from W80, X2 built here
    DD = load_deep("2006-01-05", "2021-12-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    nd, td, sidd = DD["n"], DD["t"], DD["sid"]
    XD = fast_build_context(DD)
    z = np.load(os.path.join(W80OUT, f"mem_deep_{nd}.npz"))
    memd, bmomd, tiltd = z["mem"], z["bmom"], z["tilt"]
    P_(f"=== deep {nd:,} bars, {DD['n_sess']:,} sessions [{_time.time()-t0:.0f}s]")
    fbd, sed = DD["fb"], DD["sess_end"]
    blocked = td >= sed[sidd] - np.timedelta64(30 * 60, "s")
    flatm = td >= sed[sidd] - np.timedelta64(21 * 60, "s")
    idx_l13 = {v: k for k, v in enumerate(L13)}

    def ra(x):
        return np.where(x >= 0, np.floor(x + 0.5), np.ceil(x - 0.5))

    def hyst(M):
        tgt = np.zeros(nd, np.int8)
        for i in range(nd):
            p = 0 if (i == 0 or fbd[i]) else tgt[i - 1]
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

    def deep_daily(chan, tag):
        f = os.path.join(OUT, f"deep_{tag}.csv")
        if os.path.exists(f):
            q = pd.read_csv(f); q["et"] = pd.to_datetime(q["et"]); return q
        TG = {}
        for name, vols in MEMBERS.items():
            cols = [idx_l13[v] for v in vols]
            s_ = memd[:, cols].sum(axis=1).astype(np.int32)
            T = np.clip(ra(s_ / float(len(cols)) * 10.0), -10, 10)
            ag = (np.sign(s_) == tiltd) & (s_ != 0) & (tiltd != 0)
            Tp = np.clip(ra(T * np.where(ag, 1.25, 1.0) * 0.9026), -13, 13)
            TG[name] = hyst(0.7086 * Tp + 2.83 * chan.astype(float))
        vs = []
        for name in MEMBERS:
            tg = TG[name]
            for q_ in QS:
                okv = np.ones(nd, bool) if q_ is None else \
                    ((XD["norm"] <= 0) | (XD["ratio"] >= q_))
                for dg in (True, False):
                    vs.append(np.where((tg > 0) & (okv & (XD["dL"] if dg else True)), 1,
                                       0).astype(np.int8))
        pos = (np.vstack(vs).mean(axis=0) >= 0.5).astype(np.int8)
        del vs
        base = fills_daily(DD, pos, halt=1300, target=1000)
        ee = np.array([int(min(np.searchsorted(td, np.datetime64(x["et"])), nd - 1))
                       for x in base])
        sc, _ = causal_score(XD, ee, window=WIN)
        trl = fills_qexit(DD, pos, np.where(sc >= 3, 2, 1).astype(np.int8), sc)
        q = pd.DataFrame(dict(et=pd.to_datetime([x["et"] for x in trl]),
                              pnl=[x["pnl"] for x in trl]))
        q.to_csv(f, index=False)
        P_(f"   deep {tag}: {len(q):,} trades [{_time.time()-t0:.0f}s]")
        return q

    CH = build_channels(DD, which=["X9a_disp_sessanchor", "X2_disp"])
    deep = {"P1": deep_daily(bmomd, "P1"),
            "X9a": deep_daily(CH["X9a_disp_sessanchor"], "X9a"),
            "X2": deep_daily(CH["X2_disp"], "X2")}
    dsd = pd.to_datetime(DD["sess_date"])
    nsess_deep = pd.Series(1, index=dsd).groupby(pd.Grouper(freq="6MS")).sum()

    # ------------------------------------------------ modern
    md = pd.read_csv(os.path.join(W76OUT, "streams_extended.csv"))
    md["date"] = pd.to_datetime(md["date"])
    MODERN = {"P1": md[["date", "P1"]].rename(columns={"P1": "v"}),
              "X9a": md[["date", "w72:X9a"]].rename(columns={"w72:X9a": "v"}),
              "X2": md[["date", "w72:X2"]].rename(columns={"w72:X2": "v"})}

    # ------------------------------------------------ blocks
    def blocks(name):
        q = deep[name].copy()
        q["date"] = q["et"].dt.normalize()
        a = q.groupby(pd.Grouper(key="et", freq="6MS"))["pnl"].sum()
        b = MODERN[name].groupby(pd.Grouper(key="date", freq="6MS"))["v"].sum()
        b.index.name = "et"
        return pd.concat([a, b])

    def block_n(name):
        a = deep[name].groupby(pd.Grouper(key="et", freq="6MS"))["pnl"].count()
        m = MODERN[name].copy()
        m["nz"] = (m["v"] != 0).astype(int)
        b = m.groupby(pd.Grouper(key="date", freq="6MS"))["nz"].sum()
        b.index.name = "et"
        return pd.concat([a, b])

    def block_se(name):
        q = deep[name]
        a = q.groupby(pd.Grouper(key="et", freq="6MS"))["pnl"].agg(
            lambda x: x.std(ddof=1) / np.sqrt(max(len(x), 1)) * len(x))
        m = MODERN[name].copy()
        b = m[m["v"] != 0].groupby(pd.Grouper(key="date", freq="6MS"))["v"].agg(
            lambda x: x.std(ddof=1) / np.sqrt(max(len(x), 1)) * len(x))
        b.index.name = "et"
        return pd.concat([a, b])

    B = pd.DataFrame({k: blocks(k) for k in ("P1", "X9a", "X2")}).sort_index()
    NB = pd.DataFrame({k: block_n(k) for k in ("P1", "X9a", "X2")}).sort_index()
    SE = pd.DataFrame({k: block_se(k) for k in ("P1", "X9a", "X2")}).sort_index()
    B = B[NB["P1"] >= 40]
    NB = NB.loc[B.index]; SE = SE.loc[B.index]

    # regime variables per block, from the price series themselves
    def regime_frame(D):
        sid, fb, lb = D["sid"], D["fb"], D["lb"]
        ns = D["n_sess"]
        st = np.zeros(ns, np.int64); st[sid[fb]] = np.flatnonzero(fb)
        en = np.zeros(ns, np.int64); en[sid[lb]] = np.flatnonzero(lb)
        hi = pd.Series(D["h"]).groupby(sid).max().to_numpy()
        lo = pd.Series(D["l"]).groupby(sid).min().to_numpy()
        op, cl = D["c"][st], D["c"][en]
        rng = hi - lo; net = cl - op
        up = (np.abs(net) > 0.6 * np.maximum(rng, 1e-9)) & (net > 0)
        return pd.DataFrame(dict(date=pd.to_datetime(D["sess_date"]), rng=rng,
                                 net=net, trendup=up.astype(float)))

    RD = regime_frame(DD)
    MD_ = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    RM = regime_frame(MD_)
    R = pd.concat([RD, RM[RM["date"] > RD["date"].max()]]).groupby(
        pd.Grouper(key="date", freq="6MS")).agg(med_rng=("rng", "median"),
                                                mean_net=("net", "mean"),
                                                trendup=("trendup", "mean"))
    R = R.reindex(B.index)

    B["dev"] = [(DEV_A <= i < DEV_B) for i in B.index]
    B["d_P1_X9a"] = (B["P1"] - B["X9a"]) / np.maximum(NB["P1"], 1)
    B["d_P1_X2"] = (B["P1"] - B["X2"]) / np.maximum(NB["P1"], 1)
    B["se_d"] = np.sqrt(SE["P1"] ** 2 + SE["X9a"] ** 2) / np.maximum(NB["P1"], 1)
    B = B.join(R)
    B.to_csv(os.path.join(OUT, "blocks.csv"))

    P_(f"\n{'='*126}\n=== THE ADVANTAGE CURVE: (P1 - X9a) per trade, in 6-month blocks")
    P_(f"{'='*126}")
    P_(f"{'block':<12}{'in dev?':>9}{'trades':>8}{'P1 $/trd':>11}{'X9a $/trd':>11}"
       f"{'P1-X9a':>10}{'(SE)':>9}{'|t|>2?':>8}{'PLACEBO P1-X2':>15}{'med rng':>10}"
       f"{'trendUp%':>10}")
    for i, r in B.iterrows():
        n_ = max(NB.loc[i, "P1"], 1)
        t_ = abs(r["d_P1_X9a"]) / max(r["se_d"], 1e-9)
        P_(f"{str(i.date()):<12}{('DEV' if r['dev'] else ''):>9}{int(n_):>8}"
           f"{r['P1']/n_:>11,.1f}{r['X9a']/n_:>11,.1f}{r['d_P1_X9a']:>10,.1f}"
           f"{r['se_d']:>9,.1f}{('yes' if t_ > 2 else ''):>8}{r['d_P1_X2']:>15,.1f}"
           f"{r['med_rng']:>10,.0f}{100*r['trendup']:>9.0f}%")

    dv, nd_ = B[B["dev"]], B[~B["dev"]]
    P_(f"\n=== THE FOUR PREREGISTERED CONDITIONS ===")
    c1 = float((dv["d_P1_X9a"] > 0).mean())
    c2 = float((nd_["d_P1_X9a"] <= 0).mean())
    P_(f"   (a) P1 ahead in a MAJORITY of the {len(dv)} DEV blocks        : "
       f"{100*c1:>5.0f} %  -> {'yes' if c1 > 0.5 else 'no'}")
    P_(f"   (b) P1 NOT ahead in a majority of the {len(nd_)} non-dev blocks: "
       f"{100*c2:>5.0f} %  -> {'yes' if c2 > 0.5 else 'no'}")
    pl_dev = float((dv["d_P1_X2"] > 0).mean()); pl_non = float((nd_["d_P1_X2"] <= 0).mean())
    P_(f"   (c) PLACEBO X2 does NOT show the same pattern                : "
       f"dev {100*pl_dev:.0f} % / non-dev {100*pl_non:.0f} %  -> "
       f"{'placebo is CLEAN' if not (pl_dev > 0.5 and pl_non > 0.5) else 'PLACEBO SHOWS IT TOO'}")
    ok = B.dropna(subset=["med_rng", "trendup"])
    xs = np.column_stack([np.ones(len(ok)), ok["dev"].astype(float)])
    b1, *_ = np.linalg.lstsq(xs, ok["d_P1_X9a"], rcond=None)
    r1 = 1 - ((ok["d_P1_X9a"] - xs @ b1) ** 2).sum() / \
        ((ok["d_P1_X9a"] - ok["d_P1_X9a"].mean()) ** 2).sum()
    best_r2, best_v = -9, None
    for v in ("med_rng", "mean_net", "trendup"):
        x2 = np.column_stack([np.ones(len(ok)), ok[v]])
        b2, *_ = np.linalg.lstsq(x2, ok["d_P1_X9a"], rcond=None)
        r2 = 1 - ((ok["d_P1_X9a"] - x2 @ b2) ** 2).sum() / \
            ((ok["d_P1_X9a"] - ok["d_P1_X9a"].mean()) ** 2).sum()
        P_(f"       regime variable {v:<10} R2 = {r2:+.3f}")
        if r2 > best_r2:
            best_r2, best_v = r2, v
    P_(f"   (d) dev-window dummy R2 = {r1:+.3f}  vs best regime variable "
       f"({best_v}) R2 = {best_r2:+.3f}  -> "
       f"{'dev-window wins' if r1 > best_r2 else 'A REGIME VARIABLE EXPLAINS IT BETTER'}")
    nsig = int((B["d_P1_X9a"].abs() / B["se_d"].clip(lower=1e-9) > 2).sum())
    P_(f"\n   sample adequacy: {nsig} of {len(B)} block differences are individually |t| > 2.")
    if nsig <= 2:
        P_(f"   -> almost none are. The curve is a SHAPE, not a set of measurements. It can")
        P_(f"      motivate further work and cannot settle anything.")
    H = (c1 > 0.5) and (c2 > 0.5) and (not (pl_dev > 0.5 and pl_non > 0.5)) and (r1 > best_r2)
    P_(f"\n=== VERDICT: H is {'SUPPORTED' if H else 'FALSIFIED'} ===")
    if H:
        P_("   P1's advantage over X9a IS concentrated in P1's own development window, the")
        P_("   placebo arm does not reproduce it, and no regime variable explains it better.")
        P_("   Every number P1 has produced must be re-quoted with this attached.")
    else:
        P_("   At least one condition fails. The P1/X9a difference is regime-conditional or")
        P_("   noise; W80's verdict stands and the anchor question is closed.")
    P_(f"\n=== STATUS: diagnostic. NOTHING ADOPTED. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
