"""WE_W39 amendment 2 (declared in amendment_2.yaml before this run).

The amendment-1 short arm passed the circular-shift null at the 100th percentile and then
FAILED the count-matched random-sizing null at the 69th. The long quality layer -- the
campaign's single largest adopted improvement -- has only ever been tested against the
circular-shift null (W34, W37). Two controls it has never faced:

  C1 COUNT-MATCHED RANDOM SIZING: size up the SAME NUMBER of entries, chosen at random.
     Answers "is the gain from sizing up the RIGHT flips, or merely from sizing up k flips?"
  C2 RANDOM FIVE FEATURES: build the identical causal binary score from five features drawn
     at random from the 42-feature universe with random signs.
     Answers "is the gain from THESE five features, or from the SHAPE of the rule?"
     (The incumbent five were chosen on the full sample in W33; that contamination has never
     been controlled, only bypassed by W36/W37 showing the SHAPE survives honest refitting.)

Whatever these return is reported. If C1 fails, the quality layer is leverage.
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
from run_we_w01 import ROOT, PV, STRESS_RT                               # noqa: E402
from run_we_w17 import load_deep                                         # noqa: E402
from run_we_w19 import weekly, sharpe                                    # noqa: E402
from run_we_w26 import fills_daily                                       # noqa: E402
from run_we_w35 import fills_qexit                                       # noqa: E402
from run_we_w37 import causal_score                                      # noqa: E402
from run_we_w38 import targets, vote                                     # noqa: E402
from run_we_w39 import OUT, A, B, WIN, bin_score                         # noqa: E402
from we_quality import build_context                                     # noqa: E402
from we_features import build_universe                                   # noqa: E402

RNG = np.random.default_rng(2026392)
NDRAW = 100


def main():
    t0 = _time.time()
    D = load_deep("2022-01-01", "2026-07-31 17:00")
    W1.DEV_END = pd.Timestamp("2026-07-31").date()
    n, tarr = D["n"], D["t"]
    X = build_context(D)
    TG = targets(D)
    wkmap = {s: D["wk"][s] for s in range(D["n_sess"])}

    def i_of(ts):
        return int(min(np.searchsorted(tarr, np.datetime64(ts)), n - 1))

    def wk_of(ts):
        return wkmap[int(D["sid"][i_of(ts)])]
    NS = len(np.unique(D["sid"][(tarr >= A) & (tarr < B)]))
    out = open(os.path.join(OUT, "controls.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out)

    posL = (vote(TG, D, X, +1) >= 0.5).astype(np.int8)
    baseL = fills_daily(D, posL, halt=1300, target=1000)
    bl = [x for x in baseL if A <= np.datetime64(x["et"]) < B]
    entL = np.array([i_of(x["et"]) for x in bl])
    scQ0, _ = causal_score(X, entL, window=WIN)
    szQ0 = np.where(scQ0 >= 3, 2, 1).astype(np.int8)

    def stats(trl):
        d = weekly(trl, wk_of, A, B)
        v = np.array(list(d.values()))
        p = np.array([x["pnl"] for x in trl if A <= np.datetime64(x["et"]) < B])
        s, _, _ = sharpe(d)
        return dict(pts=float(p.sum() / PV / NS), wk=float(v.mean()),
                    worst=float(v.min()), sharpe=float(s),
                    eff=float(v.mean() / abs(v.min())) if v.min() < 0 else 9.9)
    real = stats(fills_qexit(D, posL, szQ0, scQ0))
    base = stats(baseL)
    nbig = int((szQ0[entL] > 1).sum())
    P_(f"=== B1: {real['pts']:.2f} pts/session (expect 14.72) -> "
       f"{'PASS' if abs(real['pts']-14.72) < 0.6 else 'FAIL - VOID'}")
    if abs(real["pts"] - 14.72) >= 0.6:
        out.close(); return
    P_(f"   real quality layer : pts {real['pts']:.2f} | eff {real['eff']:.3f} | "
       f"Sharpe {real['sharpe']:.3f} | worst {real['worst']:,.0f}")
    P_(f"   base (all size 1)  : pts {base['pts']:.2f} | eff {base['eff']:.3f} | "
       f"Sharpe {base['sharpe']:.3f}")
    P_(f"   entries {len(entL)} | sized up {nbig} ({100*nbig/len(entL):.1f} %)")

    def summarize(tag, draws):
        P_(f"\n--- {tag} ({len(draws)} draws) ---")
        for m in ("pts", "eff", "sharpe"):
            nu = np.array([d[m] for d in draws])
            pct = 100.0 * (nu < real[m]).mean()
            P_(f"   {m:<7} real {real[m]:>7.3f} | null mean {nu.mean():>7.3f} | "
               f"p95 {np.percentile(nu,95):>7.3f} | pctile {pct:>5.1f} | "
               f"p {(nu>=real[m]).mean():.3f} -> "
               f"{'EVIDENCE' if pct>=95 else ('weak' if pct>=80 else 'NOT EVIDENCE')}")

    # ---- C1 count-matched random sizing ---------------------------------------------
    P_(f"\n=== C1 COUNT-MATCHED RANDOM SIZING [{_time.time()-t0:.0f}s] ===")
    dr = []
    for j in range(NDRAW):
        szn = np.ones(n, np.int8)
        szn[entL[RNG.choice(len(entL), size=nbig, replace=False)]] = 2
        dr.append(stats(fills_qexit(D, posL, szn, scQ0)))
        if (j + 1) % 25 == 0:
            print(f"   C1 {j+1}/{NDRAW} [{_time.time()-t0:.0f}s]", flush=True)
    summarize("C1 random subset of the same size", dr)

    # ---- C2 random five features ------------------------------------------------------
    P_(f"\n=== C2 RANDOM FIVE FEATURES, identical rule shape [{_time.time()-t0:.0f}s] ===")
    F, CLS = build_universe(D)
    names = list(F)
    dr2 = []
    for j in range(NDRAW):
        pick = RNG.choice(len(names), size=5, replace=False)
        feats = [(names[k], int(RNG.choice([-1, 1]))) for k in pick]
        sc = bin_score(F, entL, feats)
        sb = np.zeros(n); m = ~np.isnan(sc); sb[entL[m]] = sc[m]
        szn = np.where(sb >= 3, 2, 1).astype(np.int8)
        dr2.append(stats(fills_qexit(D, posL, szn, sb)))
        if (j + 1) % 25 == 0:
            print(f"   C2 {j+1}/{NDRAW} [{_time.time()-t0:.0f}s]", flush=True)
    summarize("C2 five random features, same rule", dr2)
    P_("\n   reading rule (declared): C1 answers whether the gain comes from sizing up the")
    P_("   RIGHT flips; C2 answers whether it comes from THESE features or from the rule's")
    P_("   SHAPE. A C2 failure with a C1 pass would mean the shape pays and the specific")
    P_("   five do not - which changes what we defend, not whether the layer is kept.")
    pd.DataFrame([dict(control="C1", **{f"null_{k}": float(np.mean([d[k] for d in dr]))
                                        for k in ("pts", "eff", "sharpe")}),
                  dict(control="C2", **{f"null_{k}": float(np.mean([d[k] for d in dr2]))
                                        for k in ("pts", "eff", "sharpe")}),
                  dict(control="REAL", **{f"null_{k}": real[k]
                                          for k in ("pts", "eff", "sharpe")})]).to_csv(
        os.path.join(OUT, "controls.csv"), index=False)
    out.close()
    print(f"done [{_time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
