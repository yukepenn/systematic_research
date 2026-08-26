"""WE_W74 amendment 1 - the same question, with the moment model removed.

Read 1's Cornish-Fisher machinery has NEGATIVE R^2 and under-predicts P1 alone by 9.8 pp, so
every CF number in it is withdrawn (see amendment_1.yaml). What survives is the empirical
cross-sectional exchange rate. This re-runs the requirement, the short-sleeve question and the
stream count with no distributional assumption anywhere.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W74_WEEKMATH", "out")
TARGET = 76.0
RNG = np.random.default_rng(20260874)


def main():
    out = open(os.path.join(OUT, "weekmath_b.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    R = pd.read_csv(os.path.join(OUT, "objects.csv"))
    cells = R[R["obj"].str.startswith("cell:")].copy()
    held = R[~R["obj"].str.startswith("cell:")].copy()
    P_(f"=== {len(cells)} cells in the fit, {len(held)} objects held out\n")

    # ---------------------------------------------------------------- 2b hold-out
    P_("=" * 112)
    P_("=== PHASE 2b: does the exchange rate survive a hold-out? Fit on the 216 cells ONLY.")
    P_("=" * 112)
    Xf = np.column_stack([np.ones(len(cells)), cells["sharpe"], cells["skew"]])
    beta, *_ = np.linalg.lstsq(Xf, cells["wkpos"].to_numpy(), rcond=None)
    P_(f"   wk+%  =  {beta[0]:.2f}  +  {beta[1]:.2f} * weekly Sharpe  {beta[2]:+.2f} * weekly skew")
    Xh = np.column_stack([np.ones(len(held)), held["sharpe"], held["skew"]])
    pred = Xh @ beta
    err = pred - held["wkpos"].to_numpy()
    ss = 1 - (err ** 2).sum() / ((held["wkpos"] - held["wkpos"].mean()) ** 2).sum()
    P_(f"\n   HELD OUT ({len(held)} objects never seen by the fit): "
       f"MAE {np.abs(err).mean():.2f} pp, bias {err.mean():+.2f} pp, R2 {ss:+.3f}")
    P_(f"   -> {'the exchange rate SURVIVES its hold-out and may be quoted as algebra' if ss > 0 else 'the exchange rate FAILS its hold-out and is WITHDRAWN'}")
    held = held.assign(pred=pred)
    P_(f"\n{'object':<26}{'Sharpe':>9}{'skew':>8}{'real wk+%':>11}{'predicted':>11}{'err':>8}")
    for _, r in held.sort_values("wkpos", ascending=False).iterrows():
        P_(f"{r['obj']:<26}{r['sharpe']:>9.3f}{r['skew']:>8.2f}{r['wkpos']:>10.1f}%"
           f"{r['pred']:>10.1f}%{r['pred']-r['wkpos']:>+8.1f}")
    held.to_csv(os.path.join(OUT, "heldout.csv"), index=False)

    need_S_at_skew = lambda g: (TARGET - beta[0] - beta[2] * g) / beta[1]   # noqa: E731
    p1 = R[R["obj"] == "P1"].iloc[0]
    P_(f"\n   P1: weekly Sharpe {p1['sharpe']:.3f}, skew {p1['skew']:+.2f}, "
       f"real {p1['wkpos']:.1f} % positive weeks")
    P_(f"   76 % at P1's skew needs weekly Sharpe {need_S_at_skew(p1['skew']):.3f} "
       f"= {need_S_at_skew(p1['skew'])/p1['sharpe']:.2f}x what we have")
    P_(f"   76 % at ZERO skew        needs weekly Sharpe {need_S_at_skew(0.0):.3f} "
       f"= {need_S_at_skew(0.0)/p1['sharpe']:.2f}x")

    # ---------------------------------------------------------------- 3b shuffle null
    P_(f"\n{'='*112}")
    P_("=== PHASE 3b: is the short sleeve's consistency gain GENERIC? The assumption-free test.")
    P_("=" * 112)
    L = pd.read_csv(os.path.join(ROOT, "runs", "WE_W61_SHORTSLEEVE", "out", "ledger.csv"))
    d = pd.to_datetime(L["date"]); iso = d.dt.isocalendar()
    wk = (iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)).to_numpy()
    v1 = pd.Series(L["p1"].to_numpy()).groupby(wk).sum().to_numpy()
    v2 = pd.Series(L["short"].to_numpy()).groupby(wk).sum().to_numpy()
    P_(f"   {len(v1)} weeks. Re-pairing the short sleeve's weekly outcomes with P1's destroys")
    P_(f"   alignment and preserves BOTH marginal distributions exactly. 1,000 draws.")
    P_(f"\n{'w':<8}{'REAL wk+%':>12}{'shuffled mean':>16}{'shuffled p95':>14}"
       f"{'percentile':>12}{'verdict':>12}")
    rows = []
    for w in (0.10, 0.20, 0.30, 0.40, 0.50):
        real = 100 * float((((1 - w) * v1 + w * v2) > 0).mean())
        draws = np.array([100 * float((((1 - w) * v1 + w * RNG.permutation(v2)) > 0).mean())
                          for _ in range(1000)])
        pct = 100 * float((draws < real).mean())
        P_(f"{w:<8.2f}{real:>11.1f}%{draws.mean():>15.1f}%{np.percentile(draws,95):>13.1f}%"
           f"{pct:>11.0f}%{('SPECIFIC' if pct >= 95 else 'GENERIC'):>12}")
        rows.append(dict(w=w, real=real, null_mean=float(draws.mean()),
                         null_p95=float(np.percentile(draws, 95)), pctile=pct))
    N3 = pd.DataFrame(rows); N3.to_csv(os.path.join(OUT, "shuffle_null.csv"), index=False)
    P_(f"\n   base rate: P1 alone is {100*float((v1>0).mean()):.1f} % positive weeks.")
    if (N3["pctile"] < 95).all():
        P_(f"   -> GENERIC at every weight. The sleeve's consistency gain comes from ADDING AN")
        P_(f"      INDEPENDENT STREAM WITH THAT MARGINAL DISTRIBUTION, not from when it trades.")
        P_(f"      Any stream of that shape and size buys the same thing. The campaign's")
        P_(f"      remaining consistency work is STREAM-COUNTING, not the hunt for a specially")
        P_(f"      decorrelated engine - and that reframes W40, W56, W57, W61 and W65 together.")

    # ---------------------------------------------------------------- 5b bootstrap
    P_(f"\n{'='*112}")
    P_("=== PHASE 5b: HOW MANY INDEPENDENT STREAMS REACH 76 %? Bootstrap, no model.")
    P_("=" * 112)
    P_("   Each stream has P1's OWN empirical weekly distribution EXACTLY. Correlation is")
    P_("   imposed with a Gaussian copula - equicorrelated normal scores mapped back through")
    P_("   P1's empirical quantile function - so every marginal is identical at every rho and")
    P_("   K = 1 must therefore reproduce P1's own rate in every column. (An earlier draft mixed")
    P_("   a common and an idiosyncratic DRAW, which convolves the distribution and inflated the")
    P_("   K = 1 rate from 58.6 % to 64.7 %; that construction is discarded.)")
    ND = 20000
    q = np.sort(v1)
    from scipy import stats as _st
    P_(f"\n{'K':<5}" + "".join(f"{f'rho={r}':>12}" for r in (0.0, 0.1, 0.2, 0.3)))
    boot = []
    for K in (1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24):
        line, rec = f"{K:<5}", dict(K=K)
        for rho in (0.0, 0.1, 0.2, 0.3):
            a = np.sqrt(rho); b = np.sqrt(1 - rho)
            zc = RNG.standard_normal((ND, 1)); zi = RNG.standard_normal((ND, K))
            g = a * zc + b * zi                                  # equicorrelated N(0,1)
            u = _st.norm.cdf(g)
            x = q[np.clip((u * len(q)).astype(int), 0, len(q) - 1)]
            r_ = 100 * float((x.mean(axis=1) > 0).mean())
            line += f"{r_:>11.1f}%"; rec[f"rho{rho}"] = r_
        P_(line); boot.append(rec)
    BT = pd.DataFrame(boot); BT.to_csv(os.path.join(OUT, "bootstrap_streams.csv"), index=False)
    P_(f"\n{'rho':<8}{'K needed for 76 %':>22}")
    for rho in (0.0, 0.1, 0.2, 0.3):
        got = BT[BT[f"rho{rho}"] >= TARGET]["K"]
        P_(f"{rho:<8.1f}{(str(int(got.min())) if len(got) else '> 24 (or never)'):>22}")

    P_(f"\n   NOTE, and it is the whole point: contracts do NOT appear anywhere in this table.")
    P_(f"   The positive-week rate is scale-invariant, so no amount of size moves it. Only more")
    P_(f"   INDEPENDENT streams do - and in 74 waves this campaign has found exactly one stream")
    P_(f"   with rho near zero (the short sleeve, daily rho -0.003), which is currently in the")
    P_(f"   worst year of its own history.")
    P_(f"\n=== STATUS: planning instrument. NOTHING ADOPTED. ===")
    out.close()


if __name__ == "__main__":
    main()
