"""WE_W86 - the rematch, and the money table.

Spec: runs/WE_W86_REMATCH/spec.yaml, committed before this ran.

W85 un-rejected the pair and the clique by fixing a gate that could not pass free money. This
wave applies a STRICTER promotion rule than the one they originally failed, and answers the
owner's actual question - what does this earn, at what size, at what drawdown - in dollars.
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

OUT = os.path.join(ROOT, "runs", "WE_W86_REMATCH", "out")
os.makedirs(OUT, exist_ok=True)
DDT = 20245.0
MEAS_RT = 14.65
RNG = np.random.default_rng(20260886)
NDRAW = 200


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "rematch.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    d = pd.read_csv(os.path.join(ROOT, "runs", "WE_W76_FORWARD2026", "out",
                                 "streams_extended.csv"))
    d["date"] = pd.to_datetime(d["date"]); ds = d["date"]
    iso = ds.dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    keys = sorted(set(wk)); wi = np.array([keys.index(x) for x in wk]); NW = len(keys)
    yr = ds.dt.year.to_numpy()
    cl = pd.read_csv(os.path.join(ROOT, "runs", "WE_W79_CLIQUE", "out", "members.csv"))
    P1 = d["P1"].to_numpy(); SH = d["SHORT"].to_numpy()
    AX, BM, X9 = cl["AXISB"].to_numpy(), cl["BMOM"].to_numpy(), cl["X9a"].to_numpy()
    sds = np.array([AX.std(), BM.std(), X9.std()]); ivw = (1 / sds) / (1 / sds).sum()

    OBJ = {
        "P1 (champion)":      (P1, 11.15),
        "PAIR w=0.30":        (0.70 * P1 + 0.30 * SH, 11.02),
        "PAIR 2:1":           ((2 * P1 + SH) / 3, 11.00),
        "CLIQUE equal":       ((AX + BM + X9) / 3, 9.00),
        "CLIQUE inv-vol":     (ivw[0] * AX + ivw[1] * BM + ivw[2] * X9, 9.00),
    }
    P_(f"=== {len(d)} sessions, {NW} weeks, {ds.min().date()} -> {ds.max().date()}  "
       f"[all in-sample; 2026-05-31..07-31 is BURNED per W85]")

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
        return dict(nwk=len(w), wkpos=100 * float((w > 0).mean()), weekly=float(w.mean()),
                    medwk=float(np.median(w)), weekly_dd=float(w.mean()) * k,
                    top5=dp["dd_mean_top5"], maxdd=float(dp["maxdd"]),
                    wstreak=int(stk), worst=float(w.min()))

    ALL = np.ones(len(P1), bool)
    ends = pd.date_range(ds.min() + pd.DateOffset(months=24), ds.max(), freq="ME")

    def gate(v, rtv, base, rtb):
        c = dict(m=0, w=0, d=0, a=0, n=0)
        for e in ends:
            msk = np.asarray((ds > e - pd.DateOffset(months=24)) & (ds <= e))
            if msk.sum() < 300:
                continue
            a_ = pan(v, msk, rtv * MEAS_RT); b_ = pan(base, msk, rtb * MEAS_RT)
            if a_ is None or b_ is None:
                continue
            c["n"] += 1
            x1 = a_["weekly_dd"] > b_["weekly_dd"]; x2 = a_["wkpos"] > b_["wkpos"]
            x3 = a_["top5"] < b_["top5"]
            c["m"] += x1; c["w"] += x2; c["d"] += x3; c["a"] += (x1 and x2 and x3)
        nn = max(c["n"], 1)
        return {k: 100 * v_ / nn for k, v_ in c.items() if k != "n"} | {"n": c["n"]}

    # ------------------------------------------------------------ PHASE 0: power
    P_(f"\n{'='*124}\n=== PHASE 0 (PRECONDITION): oracle battery on THIS wave's gate")
    P_(f"{'='*124}")
    orc = {"P1 + $200/session": P1 + 200.0, "P1 losses halved": np.where(P1 < 0, P1 * .5, P1),
           "P1 + $500/session": P1 + 500.0, "P1 losses x0.75": np.where(P1 < 0, P1 * .75, P1)}
    okall = True
    for k, v in orc.items():
        g = gate(v, 11.15, P1, 11.15)
        P_(f"   {k:<24} ALL-THREE {g['a']:>5.0f} %")
        okall &= g["a"] >= 75
    P_(f"   -> gate is {'USABLE' if okall else 'BROKEN - NO VERDICTS ISSUED'}")
    if not okall:
        out.close(); return

    # ------------------------------------------------------------ PHASE 1: the gate
    P_(f"\n{'='*124}\n=== PHASE 1: CORRECTED ROLLING GATE vs P1, at ${MEAS_RT}/RT")
    P_(f"{'='*124}")
    P_(f"{'object':<20}{'n':>5}{'money':>9}{'wk+%':>9}{'raw top5DD':>13}{'ALL THREE':>12}")
    G = {}
    for k, (v, rt) in OBJ.items():
        if k.startswith("P1"):
            continue
        g = gate(v, rt, P1, 11.15); G[k] = g
        P_(f"{k:<20}{g['n']:>5}{g['m']:>8.0f}%{g['w']:>8.0f}%{g['d']:>12.0f}%{g['a']:>11.0f}%")
    pd.DataFrame(G).T.to_csv(os.path.join(OUT, "gate.csv"))

    # ------------------------------------------------------------ PHASE 2: walk-forward x3
    P_(f"\n{'='*124}\n=== PHASE 2: WALK-FORWARD, THREE OBJECTIVES. W78 used money only, which is")
    P_(f"===          the wrong objective under the owner's stated ordering.")
    P_(f"{'='*124}")
    qs = pd.date_range(ds.min() + pd.DateOffset(months=12), ds.max(), freq="QS")
    P_(f"{'challenger':<20}{'objective':<16}{'churn':>8}{'chosen':>9}"
       f"{'WF wk+%':>10}{'WF wk$@DD':>12}{'WF top5':>10}")
    wfr = []
    for k, (v, rt) in OBJ.items():
        if k.startswith("P1"):
            continue
        for obj_, key, hi in (("positive weeks", "wkpos", True),
                              ("raw top-5 DD", "top5", False),
                              ("money @ fixed DD", "weekly_dd", True)):
            wf = np.zeros(len(P1)); picks = []
            for q in qs:
                tr = np.asarray((ds >= q - pd.DateOffset(months=12)) & (ds < q))
                te = np.asarray((ds >= q) & (ds < q + pd.DateOffset(months=3)))
                if tr.sum() < 150 or te.sum() < 20:
                    continue
                a_ = pan(v, tr, rt * MEAS_RT); b_ = pan(P1, tr, 11.15 * MEAS_RT)
                if a_ is None or b_ is None:
                    continue
                better = (a_[key] > b_[key]) if hi else (a_[key] < b_[key])
                wf[te] = (v if better else P1)[te]; picks.append("C" if better else "P1")
            m = wf != 0
            ch = 100 * float(np.mean(np.array(picks[1:]) != np.array(picks[:-1]))) \
                if len(picks) > 1 else np.nan
            r = pan(wf, m, ((rt + 11.15) / 2) * MEAS_RT)
            P_(f"{k:<20}{obj_:<16}{ch:>7.0f}%{picks.count('C'):>5}/{len(picks):<3}"
               f"{r['wkpos']:>9.1f}%{r['weekly_dd']:>12,.0f}{r['top5']:>10,.0f}")
            wfr.append(dict(obj=k, objective=obj_, churn=ch, chosen=picks.count("C"),
                            n=len(picks), wkpos=r["wkpos"], weekly_dd=r["weekly_dd"],
                            top5=r["top5"]))
    WF = pd.DataFrame(wfr); WF.to_csv(os.path.join(OUT, "walkforward.csv"), index=False)

    # ------------------------------------------------------------ PHASE 3: nulls
    P_(f"\n{'='*124}\n=== PHASE 3: NULLS on the RAW drawdown leg (W78 measured the OLD metric)")
    P_(f"{'='*124}")
    P_(f"{'object':<20}{'metric':<18}{'real':>12}{'null mean':>12}{'pctile':>9}{'':>10}")
    nl = []
    for k in ("PAIR w=0.30", "CLIQUE inv-vol"):
        v, rt = OBJ[k]
        real = pan(v, ALL, rt * MEAS_RT)
        vals = []
        for _ in range(NDRAW):
            if k.startswith("PAIR"):
                nv = 0.70 * P1 + 0.30 * np.roll(SH, int(RNG.integers(20, len(P1) - 20)))
            else:
                nv = (ivw[0] * np.roll(AX, int(RNG.integers(20, len(P1) - 20)))
                      + ivw[1] * np.roll(BM, int(RNG.integers(20, len(P1) - 20)))
                      + ivw[2] * np.roll(X9, int(RNG.integers(20, len(P1) - 20))))
            r = pan(nv, ALL, rt * MEAS_RT)
            vals.append((r["wkpos"], r["weekly_dd"], r["top5"]))
        V = np.array(vals)
        for j, (lab, rv, hi) in enumerate((("positive-week %", real["wkpos"], True),
                                           ("money @ fixed DD", real["weekly_dd"], True),
                                           ("RAW top-5 DD", real["top5"], False))):
            col = V[:, j]
            pct = 100 * float((col < rv).mean()) if hi else 100 * float((col > rv).mean())
            P_(f"{k:<20}{lab:<18}{rv:>12,.1f}{col.mean():>12,.1f}{pct:>8.0f}%"
               f"{('SPECIFIC' if pct >= 95 else 'generic'):>10}")
            nl.append(dict(obj=k, metric=lab, real=rv, null_mean=float(col.mean()), pctile=pct))
        P_("")
    pd.DataFrame(nl).to_csv(os.path.join(OUT, "nulls.csv"), index=False)

    # ------------------------------------------------------------ PHASE 4: THE MONEY TABLE
    P_(f"{'='*124}\n=== PHASE 4: THE MONEY TABLE. Everything at the measured ${MEAS_RT}/RT.")
    P_(f"{'='*124}")
    PER = {"full 2022-07..2026-07": ALL,
           "trailing 12 months": np.asarray(ds >= pd.Timestamp("2025-08-01")),
           "2026 YTD": yr == 2026}
    for pl, msk in PER.items():
        P_(f"\n--- {pl} ---")
        P_(f"{'object':<20}{'wk+%':>7}{'strk':>6}{'weekly$':>10}{'annualised':>12}"
           f"{'max DD':>10}{'top5 DD':>10}{'worst wk':>10}")
        for k, (v, rt) in OBJ.items():
            r = pan(v, msk, rt * MEAS_RT)
            if r is None:
                continue
            P_(f"{k:<20}{r['wkpos']:>6.1f}%{r['wstreak']:>6}{r['weekly']:>10,.0f}"
               f"{52*r['weekly']:>12,.0f}{r['maxdd']:>10,.0f}{r['top5']:>10,.0f}"
               f"{r['worst']:>10,.0f}")

    P_(f"\n=== WHAT $150,000/YEAR COSTS, at the TRAILING-12-MONTH rate ===")
    P_("    Two risk units, because max drawdown is ONE observation (method rule 15) while the")
    P_("    mean of the top five is what a trader actually lives through more than once.")
    P_(f"\n{'object':<20}{'units':>8}{'NQ contracts':>14}{'implied max DD':>17}"
       f"{'implied top5 DD':>18}{'implied worst wk':>19}")
    t12 = PER["trailing 12 months"]
    rows = []
    for k, (v, rt) in OBJ.items():
        r = pan(v, t12, rt * MEAS_RT)
        ann = 52 * r["weekly"]
        if ann <= 0:
            P_(f"{k:<20}{'negative - not investable':>60}"); continue
        u = 150000 / ann
        P_(f"{k:<20}{u:>8.2f}{u*1.27:>14.2f}{r['maxdd']*u:>17,.0f}"
           f"{r['top5']*u:>18,.0f}{r['worst']*u:>19,.0f}")
        rows.append(dict(obj=k, units=u, contracts=u * 1.27, maxdd=r["maxdd"] * u,
                         top5=r["top5"] * u, worst=r["worst"] * u, ann_per_unit=ann))
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "money.csv"), index=False)

    P_(f"\n=== AT A MATCHED TOP-5 DRAWDOWN (P1's ${pan(P1, t12, 11.15*MEAS_RT)['top5']:,.0f}) ===")
    base_t5 = pan(P1, t12, 11.15 * MEAS_RT)["top5"]
    P_(f"{'object':<20}{'scale':>8}{'NQ contracts':>14}{'weekly $':>11}{'annualised':>13}"
       f"{'max DD':>11}")
    for k, (v, rt) in OBJ.items():
        r = pan(v, t12, rt * MEAS_RT)
        s = base_t5 / max(r["top5"], 1e-9)
        P_(f"{k:<20}{s:>8.2f}{s*1.27:>14.2f}{r['weekly']*s:>11,.0f}"
           f"{52*r['weekly']*s:>13,.0f}{r['maxdd']*s:>11,.0f}")

    # ------------------------------------------------------------ PHASE 5: per year
    P_(f"\n{'='*124}\n=== PHASE 5: PER YEAR at ${MEAS_RT}/RT (positive-week % | weekly $)")
    P_(f"{'='*124}")
    yrs = sorted(set(yr))
    P_(f"{'object':<20}" + "".join(f"{y:>17}" for y in yrs))
    for k, (v, rt) in OBJ.items():
        line = f"{k:<20}"
        for y in yrs:
            r = pan(v, yr == y, rt * MEAS_RT)
            line += f"{(f'{r[chr(119)+chr(107)+chr(112)+chr(111)+chr(115)]:.0f}% | {r[chr(119)+chr(101)+chr(101)+chr(107)+chr(108)+chr(121)]:,.0f}' if r else '-'):>17}"
        P_(line)

    # ------------------------------------------------------------ VERDICT
    P_(f"\n{'='*124}\n=== PREREGISTERED VERDICT (four conditions, stricter than W78's two)")
    P_(f"{'='*124}")
    for k in G:
        g = G[k]
        c1 = (g["m"] > 50) and (g["w"] > 50) and (g["d"] > 50)
        w_ = WF[WF["obj"] == k]
        stable = int((w_["churn"] < 35).sum())
        c2 = stable >= 2
        nn = pd.DataFrame(nl); nn = nn[(nn["obj"] == k) & (nn["metric"] == "RAW top-5 DD")]
        c3 = bool(len(nn)) and float(nn.iloc[0]["pctile"]) >= 95
        r26 = pan(OBJ[k][0], yr == 2026, OBJ[k][1] * MEAS_RT)
        c4 = r26["weekly"] > 0
        P_(f"\n   {k}")
        P_(f"      (1) all three legs, majority        : {g['a']:>5.0f} %   -> "
           f"{'PASS' if c1 else 'FAIL'}")
        P_(f"      (2) choice stable under >=2 of 3    : {stable}/3 objectives churn<35 % -> "
           f"{'PASS' if c2 else 'FAIL'}")
        P_(f"      (3) drawdown null SPECIFIC          : "
           f"{(float(nn.iloc[0]['pctile']) if len(nn) else float('nan')):>5.0f} %   -> "
           f"{'PASS' if c3 else 'FAIL (generic)'}")
        P_(f"      (4) positive in 2026                : ${r26['weekly']:>7,.0f}/wk -> "
           f"{'PASS' if c4 else 'FAIL'}")
        P_(f"      => {'PROMOTED to recommended object, with its full cost stated' if (c1 and c2 and c3 and c4) else 'NOT promoted'}")
    P_(f"\n=== STATUS: [{_time.time()-t0:.0f}s] ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
