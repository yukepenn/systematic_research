"""WE_W79 - the three-stream clique {AXISB, BMOM, X9a}, tested the way W78 tested the pair.

Spec: runs/WE_W79_CLIQUE/spec.yaml, committed before this ran.

W75 found this is the best risk-adjusted object in the repo (max DD $7,810 vs P1's $20,245,
$2,346/wk at a matched drawdown vs $1,475). It has never faced a null, a rolling-window test, a
walk-forward, or the extended window. W78 is the cautionary example.
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
from run_we_w01 import ROOT, PV, STRESS_RT                               # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w38 import sfills                                            # noqa: E402
from run_we_w40 import axis_volexp                                       # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402
from we_quality import build_context                                     # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W79_CLIQUE", "out")
os.makedirs(OUT, exist_ok=True)
W76OUT = os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out")
DD_TARGET = 20245.0
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
SPLIT = pd.Timestamp("2026-05-30")
RNG = np.random.default_rng(20260879)
NDRAW = 200


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "clique.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    d = pd.read_csv(os.path.join(W76OUT, "streams_extended.csv"))
    d["date"] = pd.to_datetime(d["date"])
    iso = d["date"].dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    keys = sorted(set(wk)); wi = np.array([keys.index(x) for x in wk]); NW = len(keys)
    ds = d["date"]; yr = ds.dt.year.to_numpy()
    HELD = np.asarray(ds >= SPLIT)
    P_(f"=== {len(d)} sessions, {NW} weeks, {ds.min().date()} -> {ds.max().date()} "
       f"(EXTENDED; the last {int(HELD.sum())} were W76's held-out window)")

    # ---------------------------------------------------------------- rebuild AXISB
    D = load_deep("2022-01-01", "2026-07-31 17:00", extend=True)
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr, sid = D["n"], D["t"], D["sid"]
    X = build_context(D)
    st = np.zeros(D["n_sess"], np.int64); st[sid[D["fb"]]] = np.flatnonzero(D["fb"])
    sess_in = np.array([s for s in range(D["n_sess"]) if A <= tarr[st[s]] < B])
    in_win = np.zeros(D["n_sess"], bool); in_win[sess_in] = True

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    pb = axis_volexp(D, X, up=1.6, down=1.0, look=15)
    trb = [x for x in sfills(D, pb.astype(np.int8), halt=1300.0, target=1000.0)
           if in_win[int(sid[i_of(x["et"])])]]
    sp = np.zeros(D["n_sess"])
    for x in trb:
        sp[int(sid[i_of(x["et"])])] += x["pnl"]
    axisb = sp[sess_in]
    P_(f"    AXISB rebuilt on the extended window at FROZEN (1.6, 1.0, 15): {len(trb):,} trades, "
       f"net ${axisb.sum():,.0f} [{_time.time()-t0:.0f}s]")

    S = {"AXISB": axisb, "BMOM": d["BMOM"].to_numpy(), "X9a": d["w72:X9a"].to_numpy()}
    P1 = d["P1"].to_numpy()
    NT = {"AXISB": len(trb), "BMOM": 1044, "X9a": 2000}
    pd.DataFrame({"date": d["date"].dt.strftime("%Y-%m-%d"), "held_out": HELD,
                  "P1": P1, **S}).to_csv(os.path.join(OUT, "members.csv"), index=False)

    names = list(S)
    C = np.corrcoef(np.array([S[k] for k in names] + [P1]))
    P_(f"\n=== pairwise daily rho on the EXTENDED window (W75 measured these on the truncated "
       f"one) ===")
    lab = names + ["P1"]
    P_(f"{'':<8}" + "".join(f"{k:>9}" for k in lab))
    for i, k in enumerate(lab):
        P_(f"{k:<8}" + "".join(f"{C[i,j]:>9.3f}" for j in range(len(lab))))
    mx = max(abs(C[i, j]) for i, j in itertools.combinations(range(3), 2))
    P_(f"\n   max pairwise |rho| among the three members: {mx:.3f} "
       f"-> {'still a clique at 0.20' if mx < 0.20 else 'NO LONGER A CLIQUE at 0.20'}")

    # ---------------------------------------------------------------- panel
    def wkv(v, m=None):
        m = np.ones(len(v), bool) if m is None else m
        w_ = wi[m]
        cnt = np.bincount(w_, minlength=NW) > 0
        return np.bincount(w_, weights=v[m], minlength=NW)[cnt]

    def pan(v, m=None):
        w = wkv(v, m)
        if len(w) < 8:
            return None
        dp = dd_profile(w)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        stk = max((len(list(g)) for kk, g in itertools.groupby(w < 0) if kk), default=0)
        return dict(nwk=len(w), net=float(v[m].sum() if m is not None else v.sum()),
                    wkpos=100 * float((w > 0).mean()), wstreak=int(stk),
                    medwk=float(np.median(w)), weekly=float(w.mean()),
                    weekly_dd=float(w.mean()) * k, dd5=dp["dd_mean_top5"] * k,
                    maxdd=float(dp["maxdd"]), worst=float(w.min()), ulcer=dp["ulcer"] * k)

    sds = np.array([S[k].std() for k in names])
    W_EQ = np.ones(3) / 3
    W_IV = (1 / sds) / (1 / sds).sum()
    PORT = {"clique equal-weight": (W_EQ[:, None] * np.array([S[k] for k in names])).sum(axis=0),
            "clique inverse-vol": (W_IV[:, None] * np.array([S[k] for k in names])).sum(axis=0)}
    P_(f"\n   inverse-vol weights: " + ", ".join(f"{k} {w:.3f}" for k, w in zip(names, W_IV)))

    HDR = (f"{'object':<24}{'net $':>11}{'wk+%':>7}{'wStrk':>7}{'medWk$':>9}{'weekly$':>9}"
           f"{'wk$@DD':>9}{'top5DD':>9}{'maxDD':>9}{'worst':>9}")
    P_(f"\n{'='*128}\n=== PHASE 1: THE PANEL, extended window")
    P_(f"{'='*128}\n{HDR}")
    for k in names:
        r = pan(S[k])
        P_(f"{k:<24}{r['net']:>11,.0f}{r['wkpos']:>6.1f}%{r['wstreak']:>7}{r['medwk']:>9,.0f}"
           f"{r['weekly']:>9,.0f}{r['weekly_dd']:>9,.0f}{r['dd5']:>9,.0f}{r['maxdd']:>9,.0f}"
           f"{r['worst']:>9,.0f}")
    P_("")
    for k, v in PORT.items():
        r = pan(v)
        P_(f"{k:<24}{r['net']:>11,.0f}{r['wkpos']:>6.1f}%{r['wstreak']:>7}{r['medwk']:>9,.0f}"
           f"{r['weekly']:>9,.0f}{r['weekly_dd']:>9,.0f}{r['dd5']:>9,.0f}{r['maxdd']:>9,.0f}"
           f"{r['worst']:>9,.0f}")
    r = pan(P1)
    P_(f"{'P1 (reference)':<24}{r['net']:>11,.0f}{r['wkpos']:>6.1f}%{r['wstreak']:>7}"
       f"{r['medwk']:>9,.0f}{r['weekly']:>9,.0f}{r['weekly_dd']:>9,.0f}{r['dd5']:>9,.0f}"
       f"{r['maxdd']:>9,.0f}{r['worst']:>9,.0f}")

    # ---------------------------------------------------------------- rolling
    P_(f"\n{'='*128}\n=== PHASE 2: ROLLING 24-MONTH WINDOWS vs P1. The gate that killed W78.")
    P_(f"{'='*128}")
    ends = pd.date_range(ds.min() + pd.DateOffset(months=24), ds.max(), freq="ME")
    P_(f"{'portfolio':<24}{'n':>5}{'weekly$@DD':>13}{'wk+%':>9}{'top5DD':>10}{'ALL THREE':>12}")
    roll = []
    for k, v in list(PORT.items()) + [(f"drop {x}", (np.array(
            [S[y] for y in names if y != x]).mean(axis=0))) for x in names]:
        c1 = c2 = c3 = ca = nn = 0
        for e in ends:
            m = (ds > e - pd.DateOffset(months=24)) & (ds <= e)
            if m.sum() < 300:
                continue
            a_, b_ = pan(v, m.to_numpy()), pan(P1, m.to_numpy())
            if a_ is None or b_ is None:
                continue
            nn += 1
            x1 = a_["weekly_dd"] > b_["weekly_dd"]; x2 = a_["wkpos"] > b_["wkpos"]
            x3 = a_["dd5"] < b_["dd5"]
            c1 += x1; c2 += x2; c3 += x3; ca += (x1 and x2 and x3)
        P_(f"{k:<24}{nn:>5}{100*c1/max(nn,1):>12.0f}%{100*c2/max(nn,1):>8.0f}%"
           f"{100*c3/max(nn,1):>9.0f}%{100*ca/max(nn,1):>11.0f}%")
        roll.append(dict(arm=k, n=nn, money=100 * c1 / max(nn, 1), wkpos=100 * c2 / max(nn, 1),
                         dd=100 * c3 / max(nn, 1), all3=100 * ca / max(nn, 1)))
    RO = pd.DataFrame(roll); RO.to_csv(os.path.join(OUT, "rolling.csv"), index=False)
    a3 = float(RO[RO["arm"] == "clique equal-weight"]["all3"].iloc[0])
    P_(f"\n   BAR: all three in a MAJORITY. equal-weight scores {a3:.0f} % -> "
       f"{'PASS' if a3 > 50 else 'FAIL'}")

    # ---------------------------------------------------------------- per year
    P_(f"\n{'='*128}\n=== PHASE 3: PER YEAR (weekly $ | positive-week %)")
    P_(f"{'='*128}")
    yrs = sorted(set(yr))
    P_(f"{'object':<24}" + "".join(f"{y:>18}" for y in yrs))
    for k, v in list(S.items()) + list(PORT.items()) + [("P1 (reference)", P1)]:
        line = f"{k:<24}"
        for y in yrs:
            r = pan(v, yr == y)
            line += f"{(f'{r[chr(119)+chr(101)+chr(101)+chr(107)+chr(108)+chr(121)]:,.0f} | {r[chr(119)+chr(107)+chr(112)+chr(111)+chr(115)]:.0f}%' if r else '-'):>18}"
        P_(line)

    P_(f"\n   W76's held-out 46 sessions (OBSERVATION - 9 weeks ranks nothing):")
    for k, v in list(S.items()) + list(PORT.items()) + [("P1 (reference)", P1)]:
        r = pan(v, HELD)
        P_(f"      {k:<24} net ${r['net']:>9,.0f}   positive weeks {r['wkpos']:>5.1f} %   "
           f"worst ${r['worst']:>8,.0f}")

    # ---------------------------------------------------------------- null
    P_(f"\n{'='*128}")
    P_("=== PHASE 4: N1 NULL - shift each member independently; keep every marginal exactly.")
    P_(f"{'='*128}")
    real = pan(PORT["clique equal-weight"])
    nv = []
    for _ in range(NDRAW):
        sh = [np.roll(S[k], int(RNG.integers(20, len(P1) - 20))) for k in names]
        nv.append(pan(np.mean(sh, axis=0)))
    nv = [x for x in nv if x]
    P_(f"\n{'metric':<20}{'real':>12}{'null mean':>12}{'null p95':>12}{'pctile':>9}{'':>10}")
    nrows = []
    for key, lb, hi in (("weekly_dd", "weekly $ @ DD", True), ("wkpos", "positive-week %", True),
                        ("dd5", "mean top-5 DD", False), ("wstreak", "weekly streak", False)):
        vals = np.array([x[key] for x in nv])
        pct = 100 * float((vals < real[key]).mean()) if hi else \
            100 * float((vals > real[key]).mean())
        P_(f"{lb:<20}{real[key]:>12,.1f}{vals.mean():>12,.1f}"
           f"{np.percentile(vals, 95 if hi else 5):>12,.1f}{pct:>8.0f}%"
           f"{('SPECIFIC' if pct >= 95 else 'generic'):>10}")
        nrows.append(dict(metric=lb, real=real[key], null_mean=float(vals.mean()), pctile=pct))
    pd.DataFrame(nrows).to_csv(os.path.join(OUT, "nulls.csv"), index=False)

    # ---------------------------------------------------------------- walk-forward
    P_(f"\n{'='*128}\n=== PHASE 5: WALK-FORWARD over the weight vector")
    P_(f"{'='*128}")
    CAND = {"equal": W_EQ, "invvol": W_IV, "AXISB": np.array([1., 0, 0]),
            "BMOM": np.array([0, 1., 0]), "X9a": np.array([0, 0, 1.])}
    M = np.array([S[k] for k in names])
    qs = pd.date_range(ds.min() + pd.DateOffset(months=12), ds.max(), freq="QS")
    wf = np.zeros(len(P1)); picks = []
    for q in qs:
        tr = ((ds >= q - pd.DateOffset(months=12)) & (ds < q)).to_numpy()
        te = ((ds >= q) & (ds < q + pd.DateOffset(months=3))).to_numpy()
        if tr.sum() < 150 or te.sum() < 20:
            continue
        best, bk = -1e18, "equal"
        for k, w_ in CAND.items():
            r = pan((w_[:, None] * M).sum(axis=0), tr)
            if r and r["weekly_dd"] > best:
                best, bk = r["weekly_dd"], k
        wf[te] = (CAND[bk][:, None] * M).sum(axis=0)[te]; picks.append(bk)
    m = wf != 0
    rw, rf, rp = pan(wf, m), pan(PORT["clique equal-weight"], m), pan(P1, m)
    churn = 100 * float(np.mean(np.array(picks[1:]) != np.array(picks[:-1]))) if len(picks) > 1 \
        else np.nan
    P_(f"   {len(picks)} refits: {picks}")
    P_(f"   choice churn {churn:.0f} %")
    P_(f"\n{'':<24}{'wk+%':>8}{'weekly$':>10}{'wk$@DD':>10}{'top5DD':>10}{'worst':>10}")
    for lb2, r in (("walk-forward", rw), ("fixed equal-weight", rf), ("P1 alone", rp)):
        P_(f"{lb2:<24}{r['wkpos']:>7.1f}%{r['weekly']:>10,.0f}{r['weekly_dd']:>10,.0f}"
           f"{r['dd5']:>10,.0f}{r['worst']:>10,.0f}")
    ret = 100 * rw["weekly_dd"] / rf["weekly_dd"]
    P_(f"\n   retention {ret:.0f} % (W29 bar 80 %) -> {'PASS' if ret >= 80 else 'FAIL'}")

    # ---------------------------------------------------------------- verdict
    y26 = pan(PORT["clique equal-weight"], yr == 2026)
    P_(f"\n{'='*128}\n=== PREREGISTERED VERDICT\n{'='*128}")
    g1, g2, g3 = a3 > 50, ret >= 80, y26["net"] > 0
    drops = RO[RO["arm"].str.startswith("drop")]["all3"].to_numpy()
    g4 = bool(len(drops)) and float(drops.max()) <= a3 + 1e-9
    P_(f"   (1) all three in a majority of rolling windows : {a3:>5.0f} %   -> "
       f"{'PASS' if g1 else 'FAIL'}")
    P_(f"   (2) walk-forward retention >= 80 %             : {ret:>5.0f} %   -> "
       f"{'PASS' if g2 else 'FAIL'}")
    P_(f"   (3) positive in 2026 (extended)                : ${y26['net']:>8,.0f} -> "
       f"{'PASS' if g3 else 'FAIL'}")
    P_(f"   (4) not carried by one member (no 2-member subset beats the 3) -> "
       f"{'PASS' if g4 else 'FAIL'}")
    if g1 and g2 and g3 and g4:
        P_(f"\n   -> ALL FOUR PASS. Promoted to challenger-confirmed.")
    else:
        P_(f"\n   -> DOES NOT CLEAR THE BAR. The best full-sample object in the repo does not")
        P_(f"      survive sub-period testing either. That is now the SIXTH such case, and it")
        P_(f"      says something structural: full-sample dominance is nearly uninformative")
        P_(f"      here, and only the rolling and walk-forward tests carry information.")
    P_(f"\n=== STATUS: NOTHING ADOPTED. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
