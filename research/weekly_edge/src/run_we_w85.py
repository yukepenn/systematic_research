"""WE_W85 - the rolling gate used in W78-W84 has no power. Fix it, prove the fix, re-adjudicate.

Spec: runs/WE_W85_GATEFIX/spec.yaml, committed before this ran.

x3 was `mean_top5_drawdown * DD_TARGET / maxdd` - a SHAPE RATIO, not a level, sharing its
denominator with the money leg. An object handed free money that shrinks its drawdown scores
WORSE on it. Oracle battery, re-derived by me: "P1 + $200 every session" scores ALL-THREE 0 %
while its raw max drawdown is better in 100 % of windows.
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
from run_we_w01 import ROOT                                              # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W85_GATEFIX", "out")
os.makedirs(OUT, exist_ok=True)
DDT = 20245.0
MEAS_RT = 14.65


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "gatefix.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    # ---------------------------------------------------------------- assemble every object
    d = pd.read_csv(os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out",
                                 "streams_extended.csv"))
    d["date"] = pd.to_datetime(d["date"])
    ds = d["date"]
    iso = ds.dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    keys = sorted(set(wk)); wi = np.array([keys.index(x) for x in wk]); NW = len(keys)
    cl = pd.read_csv(os.path.join(ROOT, "runs", "WE_W79_CLIQUE", "out", "members.csv"))
    q = pd.read_csv(os.path.join(ROOT, "runs", "WE_W84_Q3", "out", "ledgers.csv"))
    P1 = d["P1"].to_numpy(); SH = d["SHORT"].to_numpy()
    AX = cl["AXISB"].to_numpy(); BM = cl["BMOM"].to_numpy(); X9 = cl["X9a"].to_numpy()
    sds = np.array([AX.std(), BM.std(), X9.std()]); ivw = (1 / sds) / (1 / sds).sum()

    OBJ = {
        "P1 (champion)":            (P1, 11.15),
        "W78 pair w=0.30":          (0.70 * P1 + 0.30 * SH, 11.02),
        "W78 pair 2:1 (w=1/3)":     ((2 * P1 + SH) / 3, 11.00),
        "W79 clique equal":         ((AX + BM + X9) / 3, 9.0),
        "W79 clique inverse-vol":   (ivw[0] * AX + ivw[1] * BM + ivw[2] * X9, 9.0),
        "W80 X9a":                  (X9, 11.0),
        "W83 Q1 layer OFF":         (q["Q1"].to_numpy(), 10.00),
        "W84 Q3 score>=4":          (q["Q3"].to_numpy(), 10.32),
        "W83 Q4 size 3":            (q["Q4"].to_numpy(), 12.13),
    }
    P_(f"=== {len(d)} sessions, {NW} weeks; {len(OBJ)} objects re-adjudicated "
       f"[{_time.time()-t0:.0f}s]")

    def wkv(v, m):
        w_ = wi[m]
        c = np.bincount(w_, minlength=NW) > 0
        return np.bincount(w_, weights=v[m], minlength=NW)[c]

    def pan(v, m, rt_wk=0.0):
        w = wkv(v, m) - rt_wk
        if len(w) < 8:
            return None
        dp = dd_profile(w)
        k = DDT / max(dp["maxdd"], 1e-9)
        stk = max((len(list(g)) for c, g in itertools.groupby(w < 0) if c), default=0)
        return dict(wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    weekly_dd=float(w.mean()) * k,
                    dd5_OLD=dp["dd_mean_top5"] * k,          # the defective leg
                    dd5_RAW=dp["dd_mean_top5"],              # the corrected leg
                    maxdd=float(dp["maxdd"]), wstreak=int(stk), worst=float(w.min()))

    ends = pd.date_range(ds.min() + pd.DateOffset(months=24), ds.max(), freq="ME")

    def score(v, rt_v, base, rt_b, corrected):
        c = dict(m=0, w=0, d=0, a=0, n=0)
        for e in ends:
            msk = np.asarray((ds > e - pd.DateOffset(months=24)) & (ds <= e))
            if msk.sum() < 300:
                continue
            a_ = pan(v, msk, rt_v * MEAS_RT); b_ = pan(base, msk, rt_b * MEAS_RT)
            if a_ is None or b_ is None:
                continue
            c["n"] += 1
            x1 = a_["weekly_dd"] > b_["weekly_dd"]
            x2 = a_["wkpos"] > b_["wkpos"]
            x3 = (a_["dd5_RAW"] < b_["dd5_RAW"]) if corrected else (a_["dd5_OLD"] < b_["dd5_OLD"])
            c["m"] += x1; c["w"] += x2; c["d"] += x3; c["a"] += (x1 and x2 and x3)
        nn = max(c["n"], 1)
        return {k: 100 * v_ / nn for k, v_ in c.items() if k != "n"} | {"n": c["n"]}

    # ---------------------------------------------------------------- PHASE 0: power check
    P_(f"\n{'='*120}")
    P_("=== PHASE 0 (MANDATORY, RUNS FIRST): ORACLE BATTERY. A gate that cannot pass a strictly")
    P_("===          dominant object cannot reject anything.")
    P_(f"{'='*120}")
    ORACLES = {
        "P1 + $200 every session":   P1 + 200.0,
        "P1 with every loss halved": np.where(P1 < 0, P1 * 0.5, P1),
        "P1 + $500 every session":   P1 + 500.0,
        "P1 with losses x0.75":      np.where(P1 < 0, P1 * 0.75, P1),
    }
    P_(f"{'oracle':<30}{'OLD gate ALL3':>16}{'CORRECTED ALL3':>17}"
       f"{'raw maxDD better':>19}")
    pw = []
    for k, v in ORACLES.items():
        so = score(v, 11.15, P1, 11.15, False)
        sn = score(v, 11.15, P1, 11.15, True)
        ddw = 0; nn = 0
        for e in ends:
            msk = np.asarray((ds > e - pd.DateOffset(months=24)) & (ds <= e))
            if msk.sum() < 300:
                continue
            nn += 1
            ddw += pan(v, msk)["maxdd"] < pan(P1, msk)["maxdd"]
        P_(f"{k:<30}{so['a']:>15.0f}%{sn['a']:>16.0f}%{100*ddw/max(nn,1):>18.0f}%")
        pw.append(dict(oracle=k, old=so["a"], corrected=sn["a"], raw_dd=100 * ddw / max(nn, 1)))
    PW = pd.DataFrame(pw); PW.to_csv(os.path.join(OUT, "power.csv"), index=False)
    ok = bool((PW["corrected"] >= 75).all())
    P_(f"\n   OLD gate on strictly-dominant objects: {PW['old'].min():.0f}-{PW['old'].max():.0f} %"
       f"   -> BROKEN")
    P_(f"   CORRECTED gate:                        "
       f"{PW['corrected'].min():.0f}-{PW['corrected'].max():.0f} %   -> "
       f"{'USABLE' if ok else 'ALSO BROKEN - NO VERDICTS ISSUED'}")
    if not ok:
        P_("\n   *** the corrected gate also fails its power check. No object is scored. ***")
        out.close(); return

    # ---------------------------------------------------------------- PHASE 1: re-adjudicate
    P_(f"\n{'='*120}")
    P_(f"=== PHASE 1: RE-ADJUDICATION at the measured ${MEAS_RT}/RT. "
       f"OLD vs CORRECTED, side by side.")
    P_(f"{'='*120}")
    P_(f"{'object':<26}{'money':>8}{'wk+%':>8}| {'OLD dd-leg':>12}{'OLD ALL3':>10} | "
       f"{'NEW dd-leg':>12}{'NEW ALL3':>10}{'  verdict change':>18}")
    rows = []
    for k, (v, rtw) in OBJ.items():
        if k.startswith("P1 ("):
            continue
        so = score(v, rtw, P1, 11.15, False)
        sn = score(v, rtw, P1, 11.15, True)
        chg = ("PASS <- was FAIL" if (sn["a"] > 50 and so["a"] <= 50)
               else ("still FAIL" if sn["a"] <= 50 else "PASS (was PASS)"))
        P_(f"{k:<26}{so['m']:>7.0f}%{so['w']:>7.0f}%| {so['d']:>11.0f}%{so['a']:>9.0f}% | "
           f"{sn['d']:>11.0f}%{sn['a']:>9.0f}%{chg:>18}")
        rows.append(dict(obj=k, money=so["m"], wkpos=so["w"], old_dd=so["d"], old_all3=so["a"],
                         new_dd=sn["d"], new_all3=sn["a"], change=chg))
    R = pd.DataFrame(rows); R.to_csv(os.path.join(OUT, "readjudication.csv"), index=False)

    # ---------------------------------------------------------------- PHASE 2: raw panel
    P_(f"\n{'='*120}\n=== PHASE 2: the RAW drawdown numbers the old leg was hiding "
       f"(full window, ${MEAS_RT}/RT)")
    P_(f"{'='*120}")
    P_(f"{'object':<26}{'wk+%':>7}{'wStrk':>7}{'weekly$':>10}{'wk$@DD':>10}"
       f"{'RAW top5DD':>13}{'RAW maxDD':>12}{'worst wk':>11}")
    for k, (v, rtw) in OBJ.items():
        r = pan(v, np.ones(len(v), bool), rtw * MEAS_RT)
        P_(f"{k:<26}{r['wkpos']:>6.1f}%{r['wstreak']:>7}{r['weekly']:>10,.0f}"
           f"{r['weekly_dd']:>10,.0f}{r['dd5_RAW']:>13,.0f}{r['maxdd']:>12,.0f}"
           f"{r['worst']:>11,.0f}")

    # ---------------------------------------------------------------- verdict
    P_(f"\n{'='*120}\n=== VERDICT\n{'='*120}")
    flipped = R[R["change"] == "PASS <- was FAIL"]
    P_(f"   objects whose verdict CHANGES when the gate is fixed: "
       f"{len(flipped)} of {len(R)}")
    for _, r in flipped.iterrows():
        P_(f"      {r['obj']:<26} all-three {r['old_all3']:.0f} % -> {r['new_all3']:.0f} %")
    if len(flipped) == 0:
        P_(f"      NONE. Every object that failed the broken gate also fails the corrected one.")
        P_(f"      The verdicts stand - but they stood by luck, not by measurement, and the")
        P_(f"      META-FINDING built on the broken gate is retracted regardless.")
    else:
        P_(f"\n   -> THIS IS THE LARGEST ERROR OF THE CAMPAIGN: candidates were rejected with a")
        P_(f"      broken instrument. Each flipped object goes to a fresh champion-vs-challenger")
        P_(f"      with its own null and walk-forward. NONE is promoted on this re-score.")
    P_(f"\n   RETRACTED UNCONDITIONALLY: 'seven consecutive objects failed sub-period testing,")
    P_(f"   always on the drawdown sub-metric'. That was the instrument, not the data.")
    P_(f"\n=== STATUS: NOTHING ADOPTED. [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
