"""WE_W26 DAILY (spec preregistered): the daily truth, and whether it can be improved."""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT                      # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly, sharpe                                    # noqa: E402
from run_we_w23 import signed_fills, build_side_paths                    # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W26_DAILY", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")


def fills_daily(D, size_arr, halt=1300.0, target=None, flat_min=None, partial_pts=None):
    """Signed fills with session halt, optional session profit target, optional early flat,
    and optional partial profit (half off at +partial_pts, simulated as 2 x 1-lot legs)."""
    t, o, c, h, l = D["t"], D["o"], D["c"], D["h"], D["l"]
    fb, lb, n = D["fb"], D["lb"], D["n"]
    mod = ((t - t.astype("datetime64[D]")).astype("timedelta64[s]").astype(np.int64) // 60)
    trades = []
    legs = 0; p = 0; epx = 0.0; eti = -1; spnl = 0.0; stopped = False; took = False
    for i in range(n):
        if fb[i]:
            spnl = 0.0; stopped = False
        want = int(size_arr[i - 1]) if i > 0 and not fb[i] else 0
        if stopped or (flat_min is not None and mod[i] >= flat_min):
            want = 0
        # partial profit on the remaining legs
        if p != 0 and legs == 2 and partial_pts is not None and not took:
            tg = epx + p * partial_pts
            if (h[i] >= tg) if p > 0 else (l[i] <= tg):
                px = o[i] if ((o[i] >= tg) if p > 0 else (o[i] <= tg)) else tg
                pnl = p * (px - epx) * PV - COMM_RT
                trades.append(dict(d=p, u=1, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += pnl; legs = 1; took = True
                if spnl <= -halt:
                    stopped = True; want = 0
                elif target is not None and spnl >= target:
                    stopped = True; want = 0
        if want != p:
            if p != 0:
                pnl = p * legs * (o[i] - epx) * PV - COMM_RT * legs
                trades.append(dict(d=p, u=legs, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
                spnl += pnl
                if spnl <= -halt:
                    stopped = True; want = 0
                elif target is not None and spnl >= target:
                    stopped = True; want = 0
            p = want
            if p != 0:
                epx, eti = o[i], i
                legs = 2 if partial_pts is not None else 1
                took = False
        if lb[i] and p != 0:
            pnl = p * legs * (c[i] - epx) * PV - COMM_RT * legs
            trades.append(dict(d=p, u=legs, et=str(t[eti]), xt=str(t[i]), pnl=pnl))
            p = 0; legs = 0
    return trades


def daily_stats(D, trl, tarr):
    per = {}
    for x in trl:
        i = int(min(np.searchsorted(tarr, np.datetime64(x["et"])), D["n"] - 1))
        s = int(D["sid"][i])
        per[s] = per.get(s, 0.0) + x["pnl"]
    v = np.array(list(per.values()))
    n_all = D["n_sess"]
    srt = np.sort(v)[::-1]
    top5 = srt[:max(1, len(srt) // 20)].sum()
    # losing-day streaks over the traded days in order
    ks = sorted(per)
    run = mx = 0
    for k in ks:
        if per[k] <= 0:
            run += 1; mx = max(mx, run)
        else:
            run = 0
    return dict(traded_days=len(v), all_sessions=n_all,
                pos_of_traded=100 * (v > 0).mean(),
                pos_of_all=100 * (v > 0).sum() / n_all,
                mean=v.mean(), median=float(np.median(v)), worst=v.min(), best=v.max(),
                top5_share=100 * top5 / v.sum() if v.sum() else np.nan, max_loss_streak=mx)


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    tarr = D["t"]
    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)
    ok = (norm <= 0) | (ratio >= 0.8)
    pl, _, _, _ = build_side_paths(D, "long")
    ps, _, _, _ = build_side_paths(D, "short")
    fl = np.vstack([pl[k] for k in pl]).mean(axis=0)
    fs = -np.vstack([ps[k] for k in ps]).mean(axis=0)
    L = (fl >= 0.5).astype(np.int8)
    S = -(fs >= 0.5).astype(np.int8)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), D["n"] - 1))
        return wkmap[int(D["sid"][i])]

    bb = IC.prepare(D["df"], SolarWaveParams())
    s1 = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]), xt=str(bb["t"][x["xi"]]))
          for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    print(f"bases ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "daily.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    rows = []

    def rep(nm, trl, extra=None):
        ds = daily_stats(D, trl + (extra or []), tarr)
        d = weekly(trl + (extra or []), wk_of, A, B)
        s, net, wpos = sharpe(d)
        v = np.array(list(d.values()))
        P(f"{nm:<30}{ds['traded_days']:>7}{ds['pos_of_traded']:>8.1f}{ds['pos_of_all']:>8.1f}"
          f"{ds['mean']:>9,.0f}{ds['median']:>9,.0f}{ds['worst']:>10,.0f}"
          f"{ds['top5_share']:>8.1f}{ds['max_loss_streak']:>7}{wpos:>8.1f}{s:>8.3f}"
          f"{v.min():>10,.0f}")
        rows.append(dict(name=nm, **{k: (round(v_, 1) if isinstance(v_, float) else v_)
                                     for k, v_ in ds.items()},
                         wk_pos=round(wpos, 1), wk_sharpe=round(s, 3),
                         wk_worst=round(v.min())))
        return ds, s, v.min()

    P("M1/M2 — daily truth. 'pos%all' counts every session in the sample; a no-trade day is")
    P("       neither a win nor a loss but is included in the denominator, as declared.\n")
    P(f"{'object':<30}{'tdDays':>7}{'pos%td':>8}{'pos%all':>8}{'mean':>9}{'median':>9}"
      f"{'worst':>10}{'top5%':>8}{'strk':>7}{'wkPos%':>8}{'wkShrp':>8}{'wkWorst':>10}")
    e5 = fills_daily(D, L)
    base_ds, base_s, base_w = rep("E5halt1300 (1 contract)", e5)
    rep("E5halt + S1 (<=2)", e5, extra=s1)
    sh = fills_daily(D, S)
    rep("E5halt + S1 + short (<=3)", e5 + sh, extra=s1)

    P("\nM3 — daily hit-rate levers on E5halt1300 (guards: weekly Sharpe, worst week)")
    P(f"{'lever':<30}{'tdDays':>7}{'pos%td':>8}{'pos%all':>8}{'mean':>9}{'median':>9}"
      f"{'worst':>10}{'top5%':>8}{'strk':>7}{'wkPos%':>8}{'wkShrp':>8}{'wkWorst':>10}")
    res = {}
    for X in (30, 60):
        res[f"L1 partial +{X}pts"] = rep(f"L1 partial +{X}pts (2 legs)",
                                        fills_daily(D, L, partial_pts=X))
    for T in (1000, 2000):
        res[f"L2 daily target {T}"] = rep(f"L2 daily target +${T}",
                                          fills_daily(D, L, target=T))
    res["L3 flat 15:00"] = rep("L3 early flat 15:00 ET", fills_daily(D, L, flat_min=900))

    P("\n=== ADOPTION: daily pos% up AND weekly Sharpe not down AND worst week not worse ===")
    any_ok = False
    for nm, (ds, s, w) in res.items():
        ok_ = (ds["pos_of_traded"] > base_ds["pos_of_traded"] and s >= base_s
               and w >= base_w)
        if ok_:
            any_ok = True
            P(f"  ADOPT  {nm}: daily {ds['pos_of_traded']:.1f}% vs "
              f"{base_ds['pos_of_traded']:.1f}%, Sharpe {s:.3f} vs {base_s:.3f}")
    if not any_ok:
        P("  NONE -> falsifier fires: daily consistency is not improvable in this")
        P("  architecture without paying for it; the objective is honestly a WEEKLY one.")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
