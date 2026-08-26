"""WE_W63 - the weight at which the short sleeve is carryable, tested by leave-one-year-out.

W62 refuted the insurance READING at w=0.30 (2026: -65 % money, -9.1 pp positive weeks, +28 %
drawdown) while establishing that the sleeve's contribution IS regime-shaped with real sample
(2022: +139 % money, -57 % drawdown). Both scale with the weight, so the open question is
whether a smaller unconditional weight is carryable.

The trap is named in the spec: choosing w to make the worst year tolerable is choosing on ONE
observation out of five. So this file does not report a chosen w as a result - it reports both
curves in full and tests the CHOICE PROCEDURE by leave-one-year-out.

Pure arithmetic on W61's persisted ledger.
"""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT, PV                                          # noqa: E402
from run_we_w51c import dd_profile                                       # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W63_WEIGHT", "out")
os.makedirs(OUT, exist_ok=True)
LEDGER = os.path.join(ROOT, "runs", "WE_W61_SHORTSLEEVE", "out", "ledger.csv")
DD_TARGET = 20245.0
WGRID = np.round(np.arange(0.0, 0.601, 0.01), 3)
NDRAW = 300
RNG = np.random.default_rng(20260863)


def streak(a):
    b = m = 0
    for z in a:
        b = b + 1 if z < 0 else 0
        m = max(m, b)
    return int(m)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "weight.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    L = pd.read_csv(LEDGER, parse_dates=["date"]).set_index("date")
    p1, sh = L["p1"].values, L["short"].values
    dates = L.index
    iso = dates.isocalendar()
    wkkey = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    keys_w = sorted(set(wkkey))
    wk_idx = np.array([keys_w.index(k) for k in wkkey])
    NW = len(keys_w)
    yrs = sorted(set(dates.year))
    v1 = np.bincount(wk_idx, weights=p1, minlength=NW)
    vs = np.bincount(wk_idx, weights=sh, minlength=NW)
    shn = sh * (v1.std(ddof=1) / max(vs.std(ddof=1), 1e-9))
    P_(f"=== B1: {len(L)} sessions {dates.min().date()} -> {dates.max().date()} | "
       f"P1 net ${p1.sum():,.0f} | short net ${sh.sum():,.0f} | "
       f"vol-normalisation factor {v1.std(ddof=1)/max(vs.std(ddof=1),1e-9):.3f}")

    def met(sp, mask=None):
        s = sp if mask is None else sp[mask]
        wi = wk_idx if mask is None else wk_idx[mask]
        if len(s) < 40:
            return None
        cnt = np.bincount(wi, minlength=NW) > 0
        v = np.bincount(wi, weights=s, minlength=NW)[cnt]
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        return dict(weekly=float(v.mean()) * k, wkpos=100 * float((v > 0).mean()),
                    medwk=float(np.median(v)) * k, wstreak=streak(v),
                    dd_top5=dp["dd_mean_top5"] * k, ulcer=dp["ulcer"] * k,
                    raw_dd=dp["maxdd"], worst=float(v.min()) * k)

    def comb(w):
        return (1 - w) * p1 + w * shn
    base = met(p1)
    yb = {y: met(p1, (dates.year == y)) for y in yrs}

    # =====================================================================================
    # PHASE 1 - THE TWO CURVES
    # =====================================================================================
    P_(f"\n{'='*118}\n=== PHASE 1: the two curves. No argmax is taken.")
    P_(f"{'='*118}")
    rows = []
    for w in WGRID:
        c = comb(w)
        r = met(c)
        if r is None:
            continue
        deltas = {}
        for y in yrs:
            m = (dates.year == y)
            a_ = met(c, m)
            if a_ and yb[y]:
                deltas[y] = a_["weekly"] - yb[y]["weekly"]
        r.update(w=w, worst_year=min(deltas.values()) if deltas else np.nan,
                 worst_year_name=min(deltas, key=deltas.get) if deltas else "",
                 **{f"d{y}": deltas.get(y, np.nan) for y in yrs})
        rows.append(r)
    C = pd.DataFrame(rows)
    C.to_csv(os.path.join(OUT, "curves.csv"), index=False)
    P_(f"{'w':<7}{'weekly$':>10}{'vs P1':>9}{'wk+%':>7}{'medWk$':>9}{'wStrk':>7}{'top5DD':>9}"
       f"{'ulcer':>8}{'WORST-YEAR delta':>18}{'which':>8}")
    for w in (0.00, 0.02, 0.04, 0.05, 0.06, 0.08, 0.10, 0.12, 0.15, 0.20, 0.30, 0.40, 0.50):
        q = C[np.isclose(C["w"], w)]
        if not len(q):
            continue
        r = q.iloc[0]
        P_(f"{w:<7.2f}{r['weekly']:>10,.0f}{r['weekly']-base['weekly']:>+9,.0f}"
           f"{r['wkpos']:>7.1f}{r['medwk']:>9,.0f}{int(r['wstreak']):>7}{r['dd_top5']:>9,.0f}"
           f"{r['ulcer']:>8,.0f}{r['worst_year']:>+18,.0f}{str(r['worst_year_name']):>8}")
    zero = C[C["worst_year"] >= 0]
    if len(zero):
        wmax = float(zero["w"].max())
        rz = C[np.isclose(C["w"], wmax)].iloc[0]
        P_(f"\n   the worst-year delta stays >= 0 up to w = {wmax:.2f}; there the full-sample")
        P_(f"   benefit is {rz['weekly']-base['weekly']:+,.0f} $/wk "
           f"({100*(rz['weekly']/base['weekly']-1):+.1f} %), positive weeks "
           f"{rz['wkpos']:.1f} % vs {base['wkpos']:.1f} %, weekly streak "
           f"{int(rz['wstreak'])} vs {int(base['wstreak'])}")
    else:
        wmax = 0.0
        P_(f"\n   the worst-year delta is NEGATIVE at every w > 0. No unconditional weight")
        P_(f"   leaves every year unharmed.")
    P_(f"\n   per-year delta at a few weights (each year rescaled to the fixed drawdown within itself):")
    P_(f"{'w':<7}" + "".join(f"{y:>12}" for y in yrs))
    for w in (0.02, 0.05, 0.10, 0.20, 0.30):
        q = C[np.isclose(C["w"], w)]
        if not len(q):
            continue
        r = q.iloc[0]
        P_(f"{w:<7.2f}" + "".join(f"{r[f'd{y}']:>+12,.0f}" for y in yrs))

    # =====================================================================================
    # PHASE 2 - LEAVE-ONE-YEAR-OUT on the CHOICE PROCEDURE
    # =====================================================================================
    P_(f"\n{'='*118}\n=== PHASE 2: leave-one-year-out on the PROCEDURE, not on the weight")
    P_(f"{'='*118}")
    P_("Rule, fixed in advance: choose the LARGEST w whose worst delta among the TRAINING years")
    P_("is >= 0. Then evaluate that w on the held-out year. If the procedure only works when the")
    P_("bad year is in training, it is a fit.\n")
    P_(f"{'held-out year':<16}{'w chosen on the other 4':>26}{'held-out delta $/wk':>22}"
       f"{'verdict':>12}")
    loyo = []
    for y in yrs:
        tr = [z for z in yrs if z != y]
        okw = [float(r["w"]) for _, r in C.iterrows()
               if min(r[f"d{z}"] for z in tr) >= 0]
        wsel = max(okw) if okw else 0.0
        m = (dates.year == y)
        a_ = met(comb(wsel), m)
        d = (a_["weekly"] - yb[y]["weekly"]) if (a_ and yb[y]) else np.nan
        P_(f"{y:<16}{wsel:>26.2f}{d:>+22,.0f}"
           f"{('holds' if d >= 0 else 'FAILS'):>12}")
        loyo.append(dict(year=y, w=wsel, delta=d))
    Lf = pd.DataFrame(loyo)
    Lf.to_csv(os.path.join(OUT, "loyo.csv"), index=False)
    nok = int((Lf["delta"] >= 0).sum())
    P_(f"\n   {nok} of {len(Lf)} held-out years hold -> "
       + ("MAJORITY: the procedure survives leave-one-year-out"
          if nok > len(Lf) / 2 else
          "MINORITY: the procedure is a fit and no unconditional weight is defensible"))
    P_(f"   in-sample control (w chosen on all five years): w = {wmax:.2f}, which by")
    P_(f"   construction has a non-negative delta everywhere - that is the gap to compare against.")

    # =====================================================================================
    # PHASE 3 - NULLS at the small weights
    # =====================================================================================
    P_(f"\n{'='*118}\n=== PHASE 3: nulls, scan-matched over the same w grid")
    P_(f"{'='*118}")

    def best_w(series, grid=WGRID):
        b = None
        for w in grid:
            if w == 0:
                continue
            r = met((1 - w) * p1 + w * series)
            if r and (b is None or r["weekly"] > b["weekly"]):
                b = r
        return b
    real = best_w(shn)
    n1, n2 = [], []
    mu, sg = shn.mean(), shn.std(ddof=1)
    rho1 = float(pd.Series(shn).autocorr(1))
    rho1 = 0.0 if not np.isfinite(rho1) else float(np.clip(rho1, -0.9, 0.9))
    for _ in range(NDRAW):
        b = best_w(np.roll(shn, int(RNG.integers(20, len(shn) - 20))))
        if b:
            n1.append(b["weekly"])
        e = RNG.normal(0, sg * np.sqrt(1 - rho1 ** 2), len(shn))
        syn = np.empty(len(shn)); syn[0] = e[0]
        for j in range(1, len(shn)):
            syn[j] = rho1 * syn[j - 1] + e[j]
        syn = syn - syn.mean() + mu
        b = best_w(syn)
        if b:
            n2.append(b["weekly"])
    a1, a2 = np.array(n1), np.array(n2)
    P_(f"{'':<20}{'real best $':>14}{'N1 mean':>11}{'N1 pct':>9}{'N2 mean':>11}{'N2 pct':>9}"
       f"{'verdict':>10}")
    p1p = 100 * float((a1 < real["weekly"]).mean())
    p2p = 100 * float((a2 < real["weekly"]).mean())
    P_(f"{'short sleeve':<20}{real['weekly']:>14,.0f}{a1.mean():>11,.0f}{p1p:>8.1f}%"
       f"{a2.mean():>11,.0f}{p2p:>8.1f}%"
       f"{('PASS' if (p1p >= 95 and p2p >= 95) else 'fail'):>10}")
    pd.DataFrame(dict(n1=a1[:min(len(a1), len(a2))],
                      n2=a2[:min(len(a1), len(a2))])).to_csv(
        os.path.join(OUT, "nulls.csv"), index=False)

    # =====================================================================================
    # PHASE 4 - WHAT IT COSTS AND BUYS
    # =====================================================================================
    P_(f"\n{'='*118}\n=== PHASE 4: what each weight costs and buys, in the owner's units")
    P_(f"{'='*118}")
    m22 = (dates.year == 2022)
    P_(f"{'w':<7}{'cost $/wk':>12}{'wk+% delta':>13}{'wStrk':>8}{'top5DD delta':>15}"
       f"{'2022 maxDD':>13}{'2026 delta $/wk':>18}")
    for w in (0.02, 0.04, 0.05, 0.08, 0.10, 0.15, 0.20, 0.30):
        q = C[np.isclose(C["w"], w)]
        if not len(q):
            continue
        r = q.iloc[0]
        r22 = met(comb(w), m22)
        P_(f"{w:<7.2f}{r['weekly']-base['weekly']:>+12,.0f}"
           f"{r['wkpos']-base['wkpos']:>+13.1f}{int(r['wstreak']):>8}"
           f"{r['dd_top5']-base['dd_top5']:>+15,.0f}"
           f"{r22['raw_dd']:>13,.0f}{r['d2026']:>+18,.0f}")
    P_(f"\n   P1 alone: 2022 raw max drawdown ${yb[2022]['raw_dd']:,.0f}, "
       f"weekly streak {int(base['wstreak'])}, positive weeks {base['wkpos']:.1f} %")
    P_(f"\n=== STATUS: nothing adopted. The curve and the LOYO folds are the deliverable. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
