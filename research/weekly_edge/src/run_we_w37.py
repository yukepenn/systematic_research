"""WE_W37 (spec preregistered): a fully CAUSAL, PARAMETER-FREE quality layer.

Two fixes: (1) score thresholds come from a trailing window of PRIOR entries only - the earlier
full-sample quantiles were a look-ahead; (2) the size rule is "a majority of the five features
agree", so k=3 is derived from the feature count rather than selected.
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
from run_we_w01 import ROOT, PV, COMM_RT, STRESS_RT                      # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly, sharpe                                    # noqa: E402
from run_we_w26 import fills_daily, daily_stats                          # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from we_quality import build_context, long_vote                          # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W37_PARAMFREE", "out")
os.makedirs(OUT, exist_ok=True)
A = np.datetime64("2022-07-01")
B = np.datetime64("2026-08-01")
RNG = np.random.default_rng(20260837)
MINHIST = 100


def causal_score(X, ent_i, window=250):
    """Score each entry using quantiles of the PRIOR `window` entries only.

    Returns a per-bar array (0 outside entries) so the fill layer can read it at the entry bar.
    """
    feats = [("dist_open", +1), ("prev_ret", -1), ("runlen", +1),
             ("dist_vwap", +1), ("delta_mag", +1)]
    q = {"dist_open": 2 / 3, "prev_ret": 1 / 3, "runlen": 0.9,
         "dist_vwap": 2 / 3, "delta_mag": 2 / 3}
    vals = {k: X[k][ent_i] for k, _ in feats}
    n_ent = len(ent_i)
    sc_ent = np.zeros(n_ent)
    for j in range(n_ent):
        lo = max(0, j - window)
        if j < MINHIST:
            sc_ent[j] = np.nan
            continue
        s = 0
        for k, sgn in feats:
            hist = vals[k][lo:j]
            thr = np.nanquantile(hist, q[k])
            v = vals[k][j]
            s += (v >= thr) if sgn > 0 else (v <= thr)
        sc_ent[j] = s
    out = np.zeros(len(X["ratio"]))
    ok = ~np.isnan(sc_ent)
    out[ent_i[ok]] = sc_ent[ok]
    return out, sc_ent


def full_score(X, ent_i):
    """The contaminated version: quantiles over ALL entries (kept only as a reference)."""
    feats = [("dist_open", +1, 2 / 3), ("prev_ret", -1, 1 / 3), ("runlen", +1, 0.9),
             ("dist_vwap", +1, 2 / 3), ("delta_mag", +1, 2 / 3)]
    out = np.zeros(len(X["ratio"]))
    for k, sgn, qq in feats:
        thr = np.nanquantile(X[k][ent_i], qq)
        out += (X[k] >= thr) if sgn > 0 else (X[k] <= thr)
    return out


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    X = build_context(D)
    pos = (long_vote(D, X) >= 0.5).astype(np.int8)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def wk_of(ts):
        i = int(min(np.searchsorted(tarr, ts), n - 1))
        return wkmap[int(D["sid"][i])]
    win = (tarr >= A) & (tarr < B)
    nsw = len(np.unique(D["sid"][win]))
    base = fills_daily(D, pos, halt=1300, target=1000)
    base_in = [x for x in base if A <= np.datetime64(x["et"]) < B]
    ent_i = np.array([int(min(np.searchsorted(tarr, np.datetime64(x["et"])), n - 1))
                      for x in base_in])
    holds = np.array([(np.datetime64(x["xt"]) - np.datetime64(x["et"]))
                      / np.timedelta64(1, "m") for x in base_in])
    out = open(os.path.join(OUT, "pf.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)
    rows = []

    def rep(nm, trl, ref=None):
        d = weekly(trl, wk_of, A, B)
        s, net, wp = sharpe(d)
        v = np.array(list(d.values()))
        p = np.array([x["pnl"] for x in trl if A <= np.datetime64(x["et"]) < B])
        u = np.array([x.get("u", 1) for x in trl if A <= np.datetime64(x["et"]) < B])
        eff = v.mean() / abs(v.min())
        st = float((v - STRESS_RT * len(p) / max(len(v), 1)).mean())
        tag = ""
        if ref is not None:
            ok = (p.sum() / PV / nsw > ref["pts"] and eff > ref["eff"]
                  and v.min() >= ref["worst"] * 1.02 and st > 0)
            tag = "  ADOPT" if ok else "  reject"
        P_(f"{nm:<34}{len(p):>7}{u.mean():>7.2f}{p.sum()/PV/nsw:>9.2f}{p.mean():>9.1f}"
           f"{v.mean():>9,.0f}{wp:>7.1f}{v.min():>10,.0f}{s:>8.3f}{eff:>8.3f}{st:>8,.0f}{tag}")
        r = dict(arm=nm, n=len(p), pts=p.sum() / PV / nsw, per_trade=round(p.mean(), 1),
                 wk=round(v.mean()), pos=round(wp, 1), worst=float(v.min()),
                 sharpe=round(s, 3), eff=round(eff, 3), stress=round(st))
        rows.append(r)
        return r

    P_(f"{'arm':<34}{'n':>7}{'avgSz':>7}{'pts/ses':>9}{'$/tr':>9}{'wkMean':>9}{'pos%':>7}"
       f"{'worst':>10}{'sharpe':>8}{'wk/|wst|':>8}{'stress':>8}")
    r0 = rep("P0 BASE (no quality)", base)

    P_("\n=== P4 CONTAMINATED REFERENCE (full-sample quantiles - look-ahead) ===")
    scf = full_score(X, ent_i)
    szf = np.where(scf >= 3, 2, 1).astype(np.int8)
    rep("P4 full-sample quantiles", fills_qexit(D, pos, szf, scf))
    rep("P4 + cut 120 + bigT (=A3)",
        fills_qexit(D, pos, szf, scf, big_target=2000, cut_bars=120))

    P_("\n=== P1/P3 CAUSAL SCORE, MAJORITY RULE (k=3 derived from 5 features) ===")
    for w in (100, 250, 500):
        sc, sc_ent = causal_score(X, ent_i, window=w)
        sz = np.where(sc >= 3, 2, 1).astype(np.int8)
        nm = f"P1 causal w={w}" if w == 250 else f"P3 causal w={w}"
        r = rep(nm, fills_qexit(D, pos, sz, sc), r0)
        if w == 250:
            best_sc, best_sz, best_r = sc, sz, r
        print(f"   window {w} done [{_time.time()-t0:.0f}s]", flush=True)

    P_("\n=== P2 CAUSAL SCORE + CAUSAL CUT (trailing median hold of the base object) ===")
    med_hold = np.zeros(n)
    run_med = []
    for j, i_ in enumerate(ent_i):
        run_med.append(holds[j])
        if j >= MINHIST:
            med_hold[i_] = float(np.median(run_med[-250:]))
    cutbars = int(np.median([m for m in med_hold[ent_i] if m > 0]))
    P_(f"   trailing median hold of the base object = {cutbars} bars (data-derived)")
    rep(f"P2 causal + cut@{cutbars}b",
        fills_qexit(D, pos, best_sz, best_sc, cut_bars=cutbars), r0)

    P_("\n=== HOW MUCH OF THE OLD GAIN WAS THE LOOK-AHEAD? ===")
    a3 = [r for r in rows if "=A3" in r["arm"]][0]
    p1 = [r for r in rows if r["arm"] == "P1 causal w=250"][0]
    P_(f"   A3 (contaminated) {a3['pts']:.2f} pts / Sharpe {a3['sharpe']:.3f}")
    P_(f"   causal equivalent {p1['pts']:.2f} pts / Sharpe {p1['sharpe']:.3f}")
    P_(f"   look-ahead was worth {a3['pts']-p1['pts']:+.2f} pts/session and "
       f"{a3['sharpe']-p1['sharpe']:+.3f} Sharpe")

    adopted = [r for r in rows if r["arm"].startswith(("P1", "P2")) and
               r["pts"] > r0["pts"] and r["eff"] > r0["eff"] and
               r["worst"] >= r0["worst"] * 1.02 and r["stress"] > 0]
    if adopted:
        best = max(adopted, key=lambda r: r["eff"])
        P_(f"\n=== NULL (binding) on {best['arm']}: 100 circular shifts of the score ===")
        nulls = []
        for j in range(100):
            off = int(RNG.integers(20_000, n - 20_000))
            scn = np.roll(best_sc, off)
            szn = np.where(scn >= 3, 2, 1).astype(np.int8)
            trl = fills_qexit(D, pos, szn, scn)
            d = weekly(trl, wk_of, A, B)
            v = np.array(list(d.values()))
            nulls.append(v.mean() / abs(v.min()))
            if (j + 1) % 50 == 0:
                print(f"   nulls {j+1}/100 [{_time.time()-t0:.0f}s]", flush=True)
        nulls = np.array(nulls)
        pct = 100.0 * (nulls < best["eff"]).mean()
        P_(f"real wk/|worst| {best['eff']:.3f} | null mean {nulls.mean():.3f} | p95 "
           f"{np.percentile(nulls,95):.3f} | percentile {pct:.1f} | "
           f"p {(nulls>=best['eff']).mean():.3f} -> "
           f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")
    else:
        P_("\nNONE adopted -> falsifier: the quality finding was threshold look-ahead.")
    pd.DataFrame([{k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}
                  for r in rows]).to_csv(os.path.join(OUT, "summary.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
