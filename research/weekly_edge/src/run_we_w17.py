"""WE_W17 DEEPHISTORY (spec preregistered): the FROZEN stack on 2006-2021, never-touched data."""
from __future__ import annotations

import os
import sys
import time as _time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import run_we_w01 as W1                                                  # noqa: E402
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, week_table, summarize, sm14_1m
from run_we_w03 import fills, cd_signals                                 # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "research", "original_trader_reconstruction",
                                "solar_family", "src"))
from solarwave import SolarWaveParams                                    # noqa: E402
import inverse_core as IC                                                # noqa: E402
from run_r13_strict_master import run_master                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W17_DEEPHISTORY", "out")
os.makedirs(OUT, exist_ok=True)


def load_deep(a, b):
    df = pd.read_parquet(os.path.join(ROOT, "research", "scalping_lab", "substrate",
                                      "minute", "NQ", "nq1m_2005_202605.parquet"))
    df["time"] = pd.to_datetime(df["time"])
    df = df[(df["time"] >= a) & (df["time"] <= b)].sort_values("time").reset_index(drop=True)
    t = df["time"].values.astype("datetime64[s]")
    n = len(df)
    fb = np.zeros(n, bool); fb[0] = True
    fb[1:] = np.diff(t).astype("timedelta64[m]").astype(np.int64) > 60
    lb = np.zeros(n, bool); lb[:-1] = fb[1:]; lb[-1] = True
    sid = np.cumsum(fb) - 1
    n_sess = sid[-1] + 1
    idx = np.arange(n)
    last_of = np.zeros(n_sess, np.int64)
    last_of[sid[lb]] = idx[lb]
    sess_end = t[last_of] + np.timedelta64(60, "s")
    sess_date = sess_end.astype("datetime64[D]")
    iso = pd.Series(pd.to_datetime(sess_date)).dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).values
    return dict(df=df, t=t, o=df["open"].values.astype(float),
                h=df["high"].values.astype(float), l=df["low"].values.astype(float),
                c=df["close"].values.astype(float), v=df["volume"].values.astype(float),
                n=n, fb=fb, lb=lb, sid=sid, n_sess=n_sess, sess_end=sess_end,
                sess_date=sess_date, wk=wk)


def main():
    t0 = _time.time()
    D = load_deep("2006-01-05", "2021-12-31 17:00")
    print(f"deep bars {D['n']:,}  sessions {D['n_sess']:,}  "
          f"{D['t'][0]} -> {D['t'][-1]} [{_time.time()-t0:.0f}s]", flush=True)
    W1.DEV_END = pd.Timestamp("2021-12-31").date()      # everything here is 'dev' for summarize

    rng_, dmove, atr, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)
    ok08 = (norm <= 0) | (ratio >= 0.8)
    ok07 = (norm <= 0) | (ratio >= 0.7)
    mod = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)
    asia_m = (mod >= 1080) | (mod <= 179)

    def lag_b(a):
        return np.concatenate([[True], a[:-1]])
    _, cd_arr = cd_signals(D)
    dL, dS = lag_b(cd_arr >= 0), lag_b(cd_arr <= 0)
    tgn = sm14_1m(D, 460, return_targets=True, volmults=[6, 8, 10, 12, 14, 16])
    print(f"targets ready [{_time.time()-t0:.0f}s]", flush=True)
    bb = IC.prepare(D["df"], SolarWaveParams())
    s1 = [dict(d=x["d"], pnl=x["pnl"], et=str(bb["t"][x["ei"]]), xt=str(bb["t"][x["xi"]]))
          for x in run_master(bb, exit_strict=False, gate=True, comm=COMM_RT)]
    tarr = D["t"]
    s1t = [x for x in s1
           if ok07[int(min(np.searchsorted(tarr, np.datetime64(x["et"])), D["n"] - 1))]]
    s4 = fills(D, tgn, allow_long=dL & ok08, allow_short=dS & ok08)
    s4lo = fills(D, tgn, allow_long=dL & ok08, allow_short=np.zeros(D["n"], bool))
    asia = fills(D, tgn, allow_long=dL & ok08 & asia_m, allow_short=dS & ok08 & asia_m)
    print(f"sleeves ready [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "deep.txt"), "w", encoding="utf-8")

    def P(*a):
        print(*a, flush=True); print(*a, file=out)

    def wt_of(trl):
        return week_table(trl, D, lambda x: x["xt"])

    def merge(*wts):
        p = {}
        for w in wts:
            for s, (net, ntr) in w.items():
                a = p.setdefault(s, [0.0, 0]); a[0] += net; a[1] += ntr
        return p

    wt1, wt1t, wt4, wt4lo, wtA = (wt_of(x) for x in (s1, s1t, s4, s4lo, asia))
    PORT = merge(wt1t, wt4, wtA)
    PORTLO = merge(wt1t, wt4lo, wtA)
    objs = {"S1": wt1, "S4n": wt4, "S4n_LONGONLY": wt4lo, "ASIA": wtA,
            "PORT(S1q07+S4n+ASIA)": PORT, "PORT_LONGONLY_S4n": PORTLO}

    P("2006-2021 — SIXTEEN YEARS NEVER USED BY THIS CAMPAIGN")
    P("(judged on Sharpe / %positive / sign; dollars are NOT comparable across price eras)\n")
    P(f"{'object':<24}{'weeks':>7}{'wkMean':>9}{'pos%':>7}{'worst':>10}{'sharpe':>8}"
      f"{'tpw':>7}{'stress':>8}")
    rows = []
    wvs = {}
    for nm, wt in objs.items():
        r = summarize(wt, D, "dev")
        st = float((np.array(r["_net"]) - STRESS_RT * np.array(r["_ntr"])).mean())
        P(f"{nm:<24}{r['weeks']:>7}{r['mean']:>9,.0f}{r['pos']:>7.1f}{r['worst']:>10,.0f}"
          f"{r['sharpe']:>8.3f}{r['tpw']:>7.1f}{st:>8,.0f}")
        rows.append(dict(scope="pooled", object=nm, weeks=r["weeks"],
                         wk_mean=round(r["mean"]), pos=round(r["pos"], 1),
                         worst=round(r["worst"]), sharpe=round(r["sharpe"], 3),
                         stress=round(st)))
        d = {}
        for s, (net, _) in wt.items():
            d[D["wk"][s]] = d.get(D["wk"][s], 0.0) + net
        wvs[nm] = d

    P("\nPER-YEAR (Sharpe | %positive | net):")
    hdr = f"{'year':<7}" + "".join(f"{k[:16]:>22}" for k in objs)
    P(hdr)
    years = [str(y) for y in range(2006, 2022)]
    ycount = {k: 0 for k in objs}
    for yr in years:
        line = f"{yr:<7}"
        for nm in objs:
            v = np.array([x for w, x in wvs[nm].items() if w.startswith(yr)])
            if len(v) < 5:
                line += f"{'-':>22}"
                continue
            sh = v.mean() / v.std(ddof=1)
            if sh > 0:
                ycount[nm] += 1
            line += f"{sh:>7.3f}{100*(v>0).mean():>7.1f}{v.sum():>8,.0f}"
            rows.append(dict(scope=yr, object=nm, sharpe=round(sh, 3),
                             pos=round(100 * (v > 0).mean(), 1), net=round(v.sum())))
        P(line)

    P("\n=== PREREGISTERED VERDICTS ===")
    for nm in objs:
        r = summarize(objs[nm], D, "dev")
        ys = [rw["sharpe"] for rw in rows if rw["scope"] in years and rw["object"] == nm]
        worst_y = min(ys) if ys else float("nan")
        v = ("PASS" if (r["sharpe"] > 0 and ycount[nm] >= 11 and worst_y >= -0.35)
             else ("PARTIAL" if r["sharpe"] > 0 else "FAIL"))
        P(f"{nm:<24} pooled {r['sharpe']:>6.3f}  positive years {ycount[nm]:>2}/16  "
          f"worst year {worst_y:>6.3f}  -> {v}")
    lo = summarize(objs["S4n_LONGONLY"], D, "dev")["sharpe"]
    bo = summarize(objs["S4n"], D, "dev")["sharpe"]
    P(f"\nLONG-ONLY check: deep-sample long-only {lo:.3f} vs both-sides {bo:.3f} -> "
      f"{'STRUCTURAL (advantage repeats)' if lo > bo else 'DRIFT ARTIFACT (reverses) -> closed'}")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
