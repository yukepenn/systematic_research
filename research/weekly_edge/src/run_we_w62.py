"""WE_W62 - is the short sleeve INSURANCE, TIMEABLE, or just DECAYING?

W61 recommended waiting for the short sleeve to recover. That recommendation assumes it is a
decaying edge. If instead it is insurance - negatively loaded on market direction - then waiting
is exactly wrong, because you do not buy insurance after the fire.

Three readings, three different signatures:
  INSURANCE  contemporaneous negative loading on market direction, P1 positive  -> HOLD ALWAYS
  TIMEABLE   a LAGGED causal regime variable forecasts it                       -> conditional
  DECAY      no regime relation at all                                          -> W61 stands

Runs off W61's persisted ledger and the NQ substrate. No re-simulation.
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

OUT = os.path.join(ROOT, "runs", "WE_W62_INSURANCE", "out")
os.makedirs(OUT, exist_ok=True)
LEDGER = os.path.join(ROOT, "runs", "WE_W61_SHORTSLEEVE", "out", "ledger.csv")
PARQ = os.path.join(ROOT, "research", "scalping_lab", "substrate", "minute", "NQ",
                    "nq1m_2005_202605.parquet")
DD_TARGET = 20245.0
RNG = np.random.default_rng(20260862)


def main():
    t0 = _time.time()
    out = open(os.path.join(OUT, "insurance.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    L = pd.read_csv(LEDGER, parse_dates=["date"]).set_index("date")
    p1, sh = L["p1"].values, L["short"].values
    dates = L.index
    P_(f"=== loaded W61's ledger: {len(L)} sessions {dates.min().date()} -> "
       f"{dates.max().date()} | P1 net ${p1.sum():,.0f}, short net ${sh.sum():,.0f}")

    # ---- daily NQ closes for the regime variables ---------------------------------------
    df = pd.read_parquet(PARQ, columns=["time", "close"])
    df["time"] = pd.to_datetime(df["time"])
    px = df.set_index("time")["close"].resample("D").last().dropna()
    P_(f"   NQ daily closes {px.index.min().date()} -> {px.index.max().date()} ({len(px)})")

    iso = dates.isocalendar()
    wkkey = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    keys_w = sorted(set(wkkey))
    wk_idx = np.array([keys_w.index(k) for k in wkkey])
    NW = len(keys_w)

    # =====================================================================================
    # PHASE 1/2 - rolling windows, performance and regime, contemporaneous
    # =====================================================================================
    ends = pd.date_range(dates.min() + pd.DateOffset(months=24), dates.max(), freq="ME")
    rows = []
    for e in ends:
        b = e - pd.DateOffset(months=24)
        m = (dates > b) & (dates <= e)
        if m.sum() < 200:
            continue
        a_, s_ = p1[m], sh[m]
        sea = a_.std(ddof=1) / np.sqrt(len(a_))
        ses = s_.std(ddof=1) / np.sqrt(len(s_))
        pw = px[(px.index > b) & (px.index <= e)]
        pw6 = px[(px.index > e - pd.DateOffset(months=6)) & (px.index <= e)]
        r6 = float(pw6.iloc[-1] / pw6.iloc[0] - 1) if len(pw6) > 5 else np.nan
        r24 = float(pw.iloc[-1] / pw.iloc[0] - 1) if len(pw) > 5 else np.nan
        dret = pw.pct_change().dropna()
        rows.append(dict(end=e, n=int(m.sum()),
                         t_p1=float(a_.mean() / sea) if sea > 0 else 0.0,
                         t_sh=float(s_.mean() / ses) if ses > 0 else 0.0,
                         pts_p1=float(a_.sum() / PV / len(a_)),
                         pts_sh=float(s_.sum() / PV / len(s_)),
                         M1_ret24=r24, M2_ret6=r6,
                         M3_vol=float(dret.std() * np.sqrt(252)) if len(dret) > 20 else np.nan,
                         M4_upshare=float((dret > 0).mean()) if len(dret) > 20 else np.nan))
    R = pd.DataFrame(rows)
    R.to_csv(os.path.join(OUT, "regimes.csv"), index=False)
    eff = max(1, int(round(len(R) / 24.0)))
    P_(f"\n{'='*112}\n=== PHASE 2: CONTEMPORANEOUS loadings - is it insurance?")
    P_(f"{'='*112}")
    P_(f"{len(R)} rolling 24-month windows stepped monthly, which overlap by 23/24. The")
    P_(f"EFFECTIVE number of independent observations is about {eff}. Every correlation below")
    P_(f"must be read against that, not against {len(R)}.\n")
    P_(f"{'regime variable':<20}{'corr with P1 t':>18}{'corr with SHORT t':>20}"
       f"{'signature':>28}")
    load = []
    for v in ("M1_ret24", "M2_ret6", "M3_vol", "M4_upshare"):
        ok = R[v].notna()
        c1 = float(R.loc[ok, "t_p1"].corr(R.loc[ok, v]))
        c2 = float(R.loc[ok, "t_sh"].corr(R.loc[ok, v]))
        sig = ("INSURANCE shape" if (c1 > 0.2 and c2 < -0.2) else
               ("both same sign" if c1 * c2 > 0 else "weak / mixed"))
        P_(f"{v:<20}{c1:>18.3f}{c2:>20.3f}{sig:>28}")
        load.append(dict(var=v, corr_p1=c1, corr_short=c2, sig=sig))
    P_(f"\n   the INSURANCE signature is: P1 loads POSITIVELY on market direction, the short")
    P_(f"   sleeve loads NEGATIVELY, and the magnitudes are comparable.")
    P_(f"\n   direct correlation of the two performance series across windows: "
       f"corr(t_P1, t_SHORT) = {float(R['t_p1'].corr(R['t_sh'])):+.3f}")

    # =====================================================================================
    # PHASE 3 - PREDICTIVE, with a permutation null on the overlapping structure
    # =====================================================================================
    P_(f"\n{'='*112}\n=== PHASE 3: PREDICTIVE - could it be timed, and should it be?")
    P_(f"{'='*112}")
    P_("The regime variable LAGGED a full 24-month window, so it is knowable before the period")
    P_("it would predict. A permutation null on the same overlapping structure is required,")
    P_("because 22 overlapping windows produce large-looking correlations by chance.\n")
    P_(f"{'regime variable (lagged)':<26}{'corr with SHORT t':>20}{'perm p':>10}"
       f"{'verdict':>28}")
    for v in ("M1_ret24", "M2_ret6", "M3_vol", "M4_upshare"):
        lagv = R[v].shift(24)
        ok = lagv.notna() & R["t_sh"].notna()
        if ok.sum() < 8:
            P_(f"{v:<26}{'too few windows':>20}"); continue
        c = float(R.loc[ok, "t_sh"].corr(lagv[ok]))
        # permutation preserving the overlapping structure: circularly shift the regime series
        null = []
        arr = lagv[ok].values
        for k in range(1, ok.sum()):
            null.append(float(pd.Series(R.loc[ok, "t_sh"].values).corr(
                pd.Series(np.roll(arr, k)))))
        null = np.array([x for x in null if np.isfinite(x)])
        p = float((np.abs(null) >= abs(c)).mean()) if len(null) else 1.0
        P_(f"{v:<26}{c:>20.3f}{p:>10.3f}"
           f"{('predictive' if p < 0.05 else 'NOT predictive'):>28}")
    pd.DataFrame(load).to_csv(os.path.join(OUT, "loadings.csv"), index=False)

    # =====================================================================================
    # PHASE 4 - THE DECISION, priced
    # =====================================================================================
    P_(f"\n{'='*112}\n=== PHASE 4: split by regime and price the combination against P1 alone")
    P_(f"{'='*112}")
    # causal regime label per SESSION: trailing 6-month NQ return, known before the session
    r6d = px.pct_change(126).reindex(dates, method="ffill")
    up = (r6d > 0).values
    v1 = np.bincount(wk_idx, weights=p1, minlength=NW)
    vs = np.bincount(wk_idx, weights=sh, minlength=NW)
    shn = sh * (v1.std(ddof=1) / max(vs.std(ddof=1), 1e-9))

    def met(sp, mask=None):
        s = sp if mask is None else sp[mask]
        wi = wk_idx if mask is None else wk_idx[mask]
        if len(s) < 40:
            return None
        v = np.bincount(wi, weights=s, minlength=NW)
        v = v[np.bincount(wi, minlength=NW) > 0]
        dp = dd_profile(v)
        k = DD_TARGET / max(dp["maxdd"], 1e-9)
        tr = s != 0
        return dict(weekly=float(v.mean()) * k, wkpos=100 * float((v > 0).mean()),
                    trdpos=100 * float((s[tr] > 0).mean()) if tr.any() else 0.0,
                    dd_top5=dp["dd_mean_top5"] * k, n=int(len(s)))
    P_(f"   regime label: trailing 6-month NQ return > 0, known before each session (causal).")
    P_(f"   UP-regime sessions {int(up.sum())} ({100*up.mean():.1f} %), "
       f"DOWN {int((~up).sum())} ({100*(~up).mean():.1f} %)\n")
    P_(f"{'regime':<12}{'arm':<22}{'sessions':>10}{'weekly$':>10}{'wk+%':>8}{'trdD+%':>9}"
       f"{'top5DD':>10}")
    deltas = {}
    for lab, mk in (("UP", up), ("DOWN", ~up)):
        for w in (0.0, 0.30):
            comb = (1 - w) * p1 + w * shn if w > 0 else p1
            r = met(comb, mk)
            if r is None:
                continue
            nm = "P1 alone" if w == 0 else "P1 + short w=0.30"
            P_(f"{lab:<12}{nm:<22}{r['n']:>10}{r['weekly']:>10,.0f}{r['wkpos']:>8.1f}"
               f"{r['trdpos']:>9.1f}{r['dd_top5']:>10,.0f}")
            deltas[(lab, w)] = r
        P_("")
    if ("UP", 0.0) in deltas and ("DOWN", 0.0) in deltas:
        du = deltas[("UP", 0.30)]["weekly"] - deltas[("UP", 0.0)]["weekly"]
        dd = deltas[("DOWN", 0.30)]["weekly"] - deltas[("DOWN", 0.0)]["weekly"]
        P_(f"   weekly-dollar delta from adding the sleeve at w=0.30:")
        P_(f"      in UP regimes   {du:>+10,.0f} $/wk  ({int(up.sum())} sessions)")
        P_(f"      in DOWN regimes {dd:>+10,.0f} $/wk  ({int((~up).sum())} sessions)")
        P_(f"   -> "
           + ("INSURANCE THAT PAYS FOR ITSELF: it gains more in DOWN than it gives up in UP"
              if (dd > 0 and dd > -du) else
              ("a HEDGE WITH A POSITIVE COST - the premium is the UP-regime figure above"
               if dd > du else "NOT regime-shaped at all")))
    P_(f"\n=== STATUS: diagnostic. The output is which reading the data supports. ===")
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
