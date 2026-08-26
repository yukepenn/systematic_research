"""WE_W33 FLIPCOND (spec preregistered): condition the flip EVENT on non-Solar features.

R29's null-calibrated filter protocol: every candidate filter is compared against 200 RANDOM
count-matched subsets, so the credit for "dropping k trades" is controlled.
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
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT, sm14_1m             # noqa: E402
from run_we_w03 import cd_signals                                        # noqa: E402
from run_we_w09 import intraday_features                                 # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import MEMBERS, weekly, sharpe                           # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w30 import position_series                                   # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W33_FLIPCOND", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260833)
NDRAW = 200


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    c, o, h, l, v = D["c"], D["o"], D["h"], D["l"], D["v"]
    rng_, dmove, atr14, norm = intraday_features(D)
    ratio = np.where(norm > 0, rng_ / np.maximum(norm, 1e-9), 1.0)

    def lag_b(x):
        return np.concatenate([[True], x[:-1]])
    _, cd = cd_signals(D)
    dL = lag_b(cd >= 0)
    TG = {k: sm14_1m(D, 460, return_targets=True, volmults=MEMBERS[k]) for k in MEMBERS}
    vs = []
    for mem in MEMBERS:
        for q in (None, 0.7, 0.8, 0.9):
            okv = np.ones(n, bool) if q is None else ((norm <= 0) | (ratio >= q))
            for dg in (True, False):
                a = okv & (dL if dg else True)
                vs.append(np.where((TG[mem] > 0) & a, 1, 0).astype(np.int8))
    V = np.vstack(vs)
    frac = V.mean(axis=0)
    pos = (frac >= 0.5).astype(np.int8)
    trl = fills_daily(D, pos, halt=1300, target=1000)
    print(f"base object: {len(trl)} trades [{_time.time()-t0:.0f}s]", flush=True)

    # ---------------- HARNESS CHECK (the thing W32 lacked) --------------------------------
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), n - 1))
        return wkmap[int(D["sid"][i])]
    d0 = weekly(trl, wk_of, A, B)
    s0, _, wp0 = sharpe(d0)
    v0 = np.array(list(d0.values()))
    win = (tarr >= A) & (tarr < B)
    nsw = len(np.unique(D["sid"][win]))
    p0 = np.array([x["pnl"] for x in trl if A <= np.datetime64(x["et"]) < B])
    ok_h = abs(s0 - 0.305) < 0.02 and abs(p0.sum() / PV / nsw - 10.62) < 0.6
    print(f"HARNESS: Sharpe {s0:.3f} (expect 0.305), pts/session "
          f"{p0.sum()/PV/nsw:.2f} (expect 10.62) -> {'PASS' if ok_h else 'FAIL - VOID'}",
          flush=True)
    if not ok_h:
        return

    # ---------------- features at each entry bar ------------------------------------------
    mod = ((D["t"] - D["t"].astype("datetime64[D]")).astype("timedelta64[s]")
           .astype(np.int64) // 60)
    pv_ = 0.0; vv_ = 0.0
    vwap = np.full(n, np.nan)
    sopen = np.zeros(n)
    for i in range(n):
        if D["fb"][i]:
            pv_ = 0.0; vv_ = 0.0
        pv_ += c[i] * v[i]; vv_ += v[i]
        vwap[i] = pv_ / vv_ if vv_ > 0 else np.nan
    idx = np.arange(n)
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        sopen[m] = o[m[0]]
    atr_l = np.concatenate([[atr14[0]], atr14[:-1]])
    vwap_l = np.concatenate([[np.nan], vwap[:-1]])
    hh = pd.Series(c).rolling(240).max().values
    ll = pd.Series(c).rolling(240).min().values
    rpos = np.concatenate([[np.nan], ((c - ll) / np.maximum(hh - ll, 1e-9))[:-1]])
    up = np.concatenate([[0], np.sign(np.diff(c))])
    runlen = np.zeros(n)
    r = 0
    for i in range(1, n):
        r = r + 1 if up[i] == up[i - 1] and up[i] != 0 else (1 if up[i] != 0 else 0)
        runlen[i] = r * (1 if up[i] > 0 else -1)
    runlen_l = np.concatenate([[0], runlen[:-1]])
    sess_ret = np.zeros(D["n_sess"])
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        sess_ret[s] = c[m[-1]] - o[m[0]]
    prev_ret = np.concatenate([[0.0], sess_ret[:-1]])[D["sid"]]
    gap = (sopen - np.concatenate([[c[0]], c[:-1]])[
        np.concatenate([[0], idx[D["fb"]][:-1]])[D["sid"]]])
    flipcount = pd.Series((np.diff(V, axis=1, prepend=0) > 0).sum(axis=0)).rolling(
        31, center=False, min_periods=1).sum().values
    flipcount_l = np.concatenate([[0], flipcount[:-1]])
    volnorm = pd.Series(v).rolling(240, min_periods=30).mean().values
    volratio = np.concatenate([[1.0], (v / np.maximum(volnorm, 1e-9))[:-1]])
    sesshigh = np.zeros(n, bool)
    for s in range(D["n_sess"]):
        m = idx[D["sid"] == s]
        sesshigh[m] = c[m] >= np.maximum.accumulate(h[m])
    sesshigh_l = np.concatenate([[False], sesshigh[:-1]])

    ent = []
    for x in trl:
        if not (A <= np.datetime64(x["et"]) < B):
            continue
        i = int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
        ent.append((i, x["pnl"]))
    ii = np.array([e[0] for e in ent]); pnl = np.array([e[1] for e in ent])
    F = {
        "F1 range ratio": ratio[ii],
        "F2 |delta| vs vol": np.abs(cd[ii]) / np.maximum(volnorm[ii], 1e-9),
        "F3 delta sign agree": dL[ii].astype(float),
        "F4 dist to VWAP /ATR": (c[ii - 1] - vwap_l[ii]) / np.maximum(atr_l[ii], 1e-9),
        "F5 dist to open /ATR": (c[ii - 1] - sopen[ii]) / np.maximum(atr_l[ii], 1e-9),
        "F6 minute of day": mod[ii].astype(float),
        "F7 ATR vs norm": atr_l[ii] / np.maximum(np.median(atr_l), 1e-9),
        "F8 ATR 1h change": atr_l[ii] / np.maximum(atr_l[np.maximum(ii - 60, 0)], 1e-9),
        "F9 flip clustering": flipcount_l[ii],
        "F10 vote fraction": frac[ii - 1],
        "F11 prior sess ret": prev_ret[ii],
        "F12 gap /ATR": gap[ii] / np.maximum(atr_l[ii], 1e-9),
        "F13 range position": rpos[ii],
        "F14 run length": runlen_l[ii],
        "F15 at session high": sesshigh_l[ii].astype(float),
        "F16 volume ratio": volratio[ii],
    }
    print(f"features built on {len(ii)} entries [{_time.time()-t0:.0f}s]", flush=True)

    out = open(os.path.join(OUT, "flipcond.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    base_mean = pnl.mean()
    P_(f"base: {len(pnl)} entries, mean ${base_mean:.1f}/trade, "
       f"total ${pnl.sum():,.0f}, Sharpe {s0:.3f}, {p0.sum()/PV/nsw:.2f} pts/session\n")
    P_("Every filter is compared against 200 RANDOM count-matched subsets (R29 protocol):")
    P_(f"{'filter':<34}{'kept':>7}{'mean$':>9}{'delta$':>9}{'nullMean':>10}{'nullP95':>10}"
       f"{'pctile':>8}  verdict")
    rows = []
    tested = 0
    for nm, x in F.items():
        good = ~np.isnan(x)
        for tag, mask in (("top tercile", x >= np.nanquantile(x, 2 / 3)),
                          ("bottom tercile", x <= np.nanquantile(x, 1 / 3)),
                          ("top decile", x >= np.nanquantile(x, 0.9)),
                          ("bottom decile", x <= np.nanquantile(x, 0.1))):
            m = mask & good
            k = int(m.sum())
            if k < 100 or k > len(pnl) - 100:
                continue
            tested += 1
            obs = pnl[m].mean()
            nulls = np.array([pnl[RNG.choice(len(pnl), k, replace=False)].mean()
                              for _ in range(NDRAW)])
            pct = 100.0 * (nulls < obs).mean()
            verd = "EVIDENCE" if pct >= 95 else ("weak" if pct >= 80 else "-")
            if pct >= 80:
                P_(f"{nm + ' ' + tag:<34}{k:>7}{obs:>9.1f}{obs-base_mean:>+9.1f}"
                   f"{nulls.mean():>10.1f}{np.percentile(nulls,95):>10.1f}{pct:>8.1f}"
                   f"  {verd}")
            rows.append(dict(feature=nm, bucket=tag, kept=k, mean=round(obs, 1),
                             delta=round(obs - base_mean, 1),
                             null_mean=round(float(nulls.mean()), 1),
                             pctile=round(pct, 1), verdict=verd))
    ev = [r for r in rows if r["verdict"] == "EVIDENCE"]
    P_(f"\ntests run {tested}; at the 95th percentile the expected false-positive count is "
       f"{0.05*tested:.1f}; observed EVIDENCE count {len(ev)}")
    if len(ev) <= 0.05 * tested:
        P_("-> observed does not exceed chance: FALSIFIER FIRES. Solar flips are")
        P_("   UNCONDITIONALLY informative; no state at the flip predicts its quality.")
    else:
        P_("-> survivors exceed chance; applying the strongest to the full object:")
        best = max(ev, key=lambda r: r["pctile"])
        x = F[best["feature"]]
        thr = {"top tercile": np.nanquantile(x, 2 / 3), "bottom tercile": np.nanquantile(x, 1 / 3),
               "top decile": np.nanquantile(x, 0.9), "bottom decile": np.nanquantile(x, 0.1)}
        P_(f"   strongest: {best['feature']} {best['bucket']} "
           f"(pctile {best['pctile']}, delta ${best['delta']:+.1f}/trade)")
        keep = ((x >= thr[best["bucket"]]) if "top" in best["bucket"]
                else (x <= thr[best["bucket"]]))
        kept = [t for t, m in zip([t for t in trl if A <= np.datetime64(t["et"]) < B], keep) if m]
        d = weekly(kept, wk_of, A, B)
        s, net, wp = sharpe(d)
        vv = np.array(list(d.values()))
        pk = np.array([t["pnl"] for t in kept])
        P_(f"   applied: {len(kept)} trades, {pk.sum()/PV/nsw:.2f} pts/session "
           f"(base {p0.sum()/PV/nsw:.2f}), Sharpe {s:.3f} (base {s0:.3f}), "
           f"worst ${vv.min():,.0f} (base ${v0.min():,.0f})")
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
