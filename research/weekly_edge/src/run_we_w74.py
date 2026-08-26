"""WE_W74 - WHAT DOES 76 % POSITIVE WEEKS ACTUALLY REQUIRE?

Spec: runs/WE_W74_WEEKMATH/spec.yaml (committed before this ran).

CAMPAIGN_STATE fixes the success criterion at >76 % positive weeks and >$8,583/week. We are at
58.3 %, and W71 measured that the best of 216 parameter cells reaches 64.8 %. Seventy-three waves
have attacked this by looking for better signals. None has asked what the target REQUIRES.

No new data, no engine runs, no parameter search - only the daily series already persisted.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats as sst

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from run_we_w01 import ROOT                                             # noqa: E402

OUT = os.path.join(ROOT, "runs", "WE_W74_WEEKMATH", "out")
os.makedirs(OUT, exist_ok=True)
TARGET_WK = 0.76


def cf_pos_rate(S, g):
    """P(week > 0) under a Cornish-Fisher expansion with weekly Sharpe S and skew g.

    Solve for the standard-normal deviate w whose CF-adjusted quantile is zero:
        w + (w^2 - 1) * g/6 = -S
    then P(X > 0) = Phi(-w). With g = 0 this collapses to Phi(S), i.e. model M0."""
    S = np.asarray(S, float); g = np.asarray(g, float)
    a = g / 6.0
    w = np.where(np.abs(a) < 1e-9, -S, 0.0)
    with np.errstate(invalid="ignore", divide="ignore"):
        disc = 1.0 - 4.0 * a * (S - a)
        alt = (-1.0 + np.sqrt(np.maximum(disc, 0.0))) / (2.0 * np.where(a == 0, 1.0, a))
    w = np.where(np.abs(a) < 1e-9, w, alt)
    w = np.where(np.isfinite(w), w, -S)
    return sst.norm.cdf(-w)


def weekly_stats(dates, pnl, name, trades_per_wk=np.nan):
    d = pd.to_datetime(dates)
    iso = d.isocalendar()
    wk = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
    v = pd.Series(np.asarray(pnl, float)).groupby(wk.to_numpy()).sum().to_numpy()
    if len(v) < 20 or v.std(ddof=1) <= 0:
        return None
    S = float(v.mean() / v.std(ddof=1))
    g = float(sst.skew(v))
    return dict(obj=name, nweeks=len(v), mean=float(v.mean()), sd=float(v.std(ddof=1)),
                sharpe=S, skew=g, kurt=float(sst.kurtosis(v)),
                wkpos=100.0 * float((v > 0).mean()),
                m0=100.0 * float(sst.norm.cdf(S)), m1=100.0 * float(cf_pos_rate(S, g)),
                trades_wk=trades_per_wk, ac1=float(pd.Series(v).autocorr(1)))


def main():
    out = open(os.path.join(OUT, "weekmath.txt"), "w", encoding="utf-8")

    def P_(*a):
        print(*a, flush=True); print(*a, file=out); out.flush()

    # ---------------------------------------------------------------- gather every object
    rows = []
    C = pd.read_parquet(os.path.join(ROOT, "runs", "WE_W59_REOPTIM", "out",
                                     "cells_daily.parquet"))
    dates = C["date"].to_numpy()
    for col in C.columns:
        if col == "date":
            continue
        r = weekly_stats(dates, C[col].to_numpy(), f"cell:{col}")
        if r:
            rows.append(r)
    ncell = len(rows)
    L = pd.read_csv(os.path.join(ROOT, "runs", "WE_W61_SHORTSLEEVE", "out", "ledger.csv"))
    p1, sh, ld = L["p1"].to_numpy(), L["short"].to_numpy(), L["date"].to_numpy()
    rows.append(weekly_stats(ld, p1, "P1", 1942 / 204))
    rows.append(weekly_stats(ld, sh, "SHORT", 2225 / 204))
    for w in (0.10, 0.20, 0.30, 0.40, 0.50):
        rows.append(weekly_stats(ld, (1 - w) * p1 + w * sh, f"P1+SHORT w={w:.2f}",
                                 ((1 - w) * 1942 + w * 2225) / 204))
    z = np.load(os.path.join(ROOT, "runs", "WE_W72_ORCHANNEL", "out",
                             "ledgers_1558497.npz"))
    for k in z.files:
        r = weekly_stats(ld, z[k], f"w72:{k}")
        if r:
            rows.append(r)
    R = pd.DataFrame([r for r in rows if r])
    R.to_csv(os.path.join(OUT, "objects.csv"), index=False)
    P_(f"=== {len(R)} objects on disk: {ncell} W59 cells, P1, the short sleeve, 5 blends, "
       f"{len(z.files)} W72 channel arms")

    # ---------------------------------------------------------------- PHASE 1
    P_(f"\n{'='*112}\n=== PHASE 1: does the positive-week rate FOLLOW from the weekly moments?")
    P_(f"{'='*112}")
    F = R[np.abs(R["skew"]) < 2.0].copy()
    P_(f"   {len(F)} of {len(R)} objects have |skew| < 2 and enter the fit "
       f"(spec: Cornish-Fisher is unreliable outside that).")
    for lab, col in (("M0  Phi(weekly Sharpe)", "m0"),
                     ("M1  Cornish-Fisher with skew", "m1")):
        err = F[col] - F["wkpos"]
        P_(f"   {lab:<32} MAE {np.abs(err).mean():>5.2f} pp   bias {err.mean():>+6.2f} pp   "
           f"R2 {1 - (err**2).sum()/((F['wkpos']-F['wkpos'].mean())**2).sum():>6.3f}")
    mae1 = float(np.abs(F["m1"] - F["wkpos"]).mean())
    mae0 = float(np.abs(F["m0"] - F["wkpos"]).mean())
    best = "m1" if mae1 <= mae0 else "m0"
    P_(f"\n   -> the wave uses {'M1 (skew-corrected)' if best=='m1' else 'M0 (normal)'}; "
       f"MAE {min(mae0, mae1):.2f} pp")
    if min(mae0, mae1) > 5.0:
        P_("   *** SPEC FALSIFIER FIRED: neither model predicts within 5 pp. The arithmetic in")
        P_("       phases 2-5 is VOID and only the empirical surface below may be quoted. ***")

    P_(f"\n   where things sit:")
    P_(f"{'object':<26}{'weeks':>7}{'weekly $':>11}{'sd':>10}{'Sharpe':>8}{'skew':>7}"
       f"{'kurt':>7}{'wk+% real':>11}{'M0':>7}{'M1':>7}{'ac1':>7}")
    for nm in ("P1", "SHORT", "P1+SHORT w=0.30", "P1+SHORT w=0.50"):
        q = R[R["obj"] == nm]
        if not len(q):
            continue
        r = q.iloc[0]
        P_(f"{r['obj']:<26}{r['nweeks']:>7}{r['mean']:>11,.0f}{r['sd']:>10,.0f}"
           f"{r['sharpe']:>8.3f}{r['skew']:>7.2f}{r['kurt']:>7.2f}{r['wkpos']:>10.1f}%"
           f"{r['m0']:>7.1f}{r['m1']:>7.1f}{r['ac1']:>7.2f}")
    cq = R[R["obj"].str.startswith("cell:")]
    P_(f"{'216 cells: best wk+%':<26}{'':>7}{'':>11}{'':>10}"
       f"{cq.loc[cq['wkpos'].idxmax(),'sharpe']:>8.3f}"
       f"{cq.loc[cq['wkpos'].idxmax(),'skew']:>7.2f}{'':>7}"
       f"{cq['wkpos'].max():>10.1f}%")
    P_(f"{'216 cells: median':<26}{'':>7}{'':>11}{'':>10}{cq['sharpe'].median():>8.3f}"
       f"{cq['skew'].median():>7.2f}{'':>7}{cq['wkpos'].median():>10.1f}%")

    # ---------------------------------------------------------------- PHASE 2
    P_(f"\n{'='*112}\n=== PHASE 2: THE REQUIREMENT. What buys 76 % positive weeks?")
    P_(f"{'='*112}")
    p1r = R[R["obj"] == "P1"].iloc[0]
    S_p1, g_p1 = float(p1r["sharpe"]), float(p1r["skew"])

    def need_sharpe(g):
        lo, hi = 0.0, 5.0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if cf_pos_rate(mid, g) < TARGET_WK:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    def need_skew(S):
        lo, hi = -3.0, 3.0
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if cf_pos_rate(S, mid) > TARGET_WK:
                lo = mid
            else:
                hi = mid
        return 0.5 * (lo + hi)

    P_(f"   P1 today: weekly Sharpe {S_p1:.3f}, weekly skew {g_p1:+.2f}, "
       f"positive weeks {p1r['wkpos']:.1f} %")
    ns = need_sharpe(g_p1)
    P_(f"\n   (a) AT OUR CURRENT SKEW ({g_p1:+.2f}), 76 % needs weekly Sharpe "
       f"{ns:.3f} - that is {ns/S_p1:.2f}x what we have.")
    nk = need_skew(S_p1)
    P_(f"   (b) AT OUR CURRENT SHARPE ({S_p1:.3f}), 76 % needs weekly skew "
       f"{nk:+.2f} - we are at {g_p1:+.2f}.")
    if nk < -2.5:
        P_(f"       (a skew that negative is not reachable by any truncation of this object; "
           f"the skew lever ALONE cannot get there.)")
    P_(f"\n   iso-76 % curve - the weekly Sharpe required at each level of weekly skew:")
    P_(f"{'weekly skew':<14}" + "".join(f"{g:>9.1f}" for g in
                                        (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0)))
    P_(f"{'Sharpe needed':<14}" + "".join(f"{need_sharpe(g):>9.3f}" for g in
                                          (-1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0)))

    P_(f"\n   (c) HOW MANY INDEPENDENT STREAMS of our own quality reach it?")
    P_(f"       K streams at pairwise rho: Sharpe_K = S*sqrt(K)/sqrt(1+(K-1)*rho), and for")
    P_(f"       independent sums the skew shrinks as 1/sqrt(K), which helps a second time.")
    P_(f"\n{'rho':<8}" + "".join(f"{f'K={k}':>10}" for k in (1, 2, 3, 4, 6, 8, 12, 16))
       + f"{'K for 76%':>12}")
    need_rows = []
    for rho in (0.0, 0.1, 0.3, 0.5):
        vals = []
        for k in (1, 2, 3, 4, 6, 8, 12, 16):
            Sk = S_p1 * np.sqrt(k) / np.sqrt(1 + (k - 1) * rho)
            vals.append(100 * float(cf_pos_rate(Sk, g_p1 / np.sqrt(k))))
        kneed = np.nan
        for k in range(1, 2001):
            Sk = S_p1 * np.sqrt(k) / np.sqrt(1 + (k - 1) * rho)
            if cf_pos_rate(Sk, g_p1 / np.sqrt(k)) >= TARGET_WK:
                kneed = k; break
        P_(f"{rho:<8.1f}" + "".join(f"{v:>9.1f}%" for v in vals)
           + (f"{kneed:>12}" if kneed == kneed else f"{'never':>12}"))
        need_rows.append(dict(rho=rho, k_needed=kneed))
    pd.DataFrame(need_rows).to_csv(os.path.join(OUT, "streams_needed.csv"), index=False)

    # ---------------------------------------------------------------- PHASE 3
    P_(f"\n{'='*112}")
    P_("=== PHASE 3: is the short sleeve's consistency gain FREQUENCY or DIVERSIFICATION?")
    P_(f"{'='*112}")
    shr = R[R["obj"] == "SHORT"].iloc[0]
    rho = float(np.corrcoef(p1, sh)[0, 1])
    P_(f"   daily rho(P1, short) = {rho:+.4f}   |   P1 Sharpe {S_p1:.3f} skew {g_p1:+.2f}"
       f"   |   SHORT Sharpe {shr['sharpe']:.3f} skew {shr['skew']:+.2f}")
    P_(f"\n   THE PREDICTION IS MADE FROM PORTFOLIO ALGEBRA ONLY, before comparison:")
    P_(f"{'w':<8}{'pred Sharpe':>13}{'real Sharpe':>13}{'pred wk+% (P1 skew)':>22}"
       f"{'pred wk+% (real skew)':>24}{'REAL wk+%':>12}")
    ph3 = []
    dW = pd.to_datetime(ld).isocalendar()
    wkl = (dW["year"].astype(str) + "-W" + dW["week"].astype(str).str.zfill(2)).to_numpy()
    v1 = pd.Series(p1).groupby(wkl).sum().to_numpy()
    v2 = pd.Series(sh).groupby(wkl).sum().to_numpy()
    s1, s2 = v1.std(ddof=1), v2.std(ddof=1)
    rw = float(np.corrcoef(v1, v2)[0, 1])
    for w in (0.10, 0.20, 0.30, 0.40, 0.50):
        mu = (1 - w) * v1.mean() + w * v2.mean()
        sd = np.sqrt(((1 - w) * s1) ** 2 + (w * s2) ** 2 + 2 * (1 - w) * w * s1 * s2 * rw)
        Sp = mu / sd
        real = R[R["obj"] == f"P1+SHORT w={w:.2f}"].iloc[0]
        P_(f"{w:<8.2f}{Sp:>13.3f}{real['sharpe']:>13.3f}"
           f"{100*float(cf_pos_rate(Sp, g_p1)):>21.1f}%"
           f"{100*float(cf_pos_rate(Sp, real['skew'])):>23.1f}%{real['wkpos']:>11.1f}%")
        ph3.append(dict(w=w, pred_sharpe=Sp, real_sharpe=float(real["sharpe"]),
                        pred_wk_p1skew=100 * float(cf_pos_rate(Sp, g_p1)),
                        pred_wk_realskew=100 * float(cf_pos_rate(Sp, real["skew"])),
                        real_wk=float(real["wkpos"])))
    P3 = pd.DataFrame(ph3); P3.to_csv(os.path.join(OUT, "phase3.csv"), index=False)
    res = float((P3["real_wk"] - P3["pred_wk_realskew"]).abs().mean())
    P_(f"\n   mean |real - predicted(from Sharpe and skew alone)| = {res:.2f} pp")
    P_(f"   -> {'the gain is fully explained by the weekly moments: it is GENERIC, and any' if res < 3 else 'the gain EXCEEDS what the moments explain: genuine shape/dependence value'}")
    if res < 3:
        P_(f"      independent stream of this size would buy the same consistency. The campaign")
        P_(f"      should be COUNTING STREAMS, not hunting for a specially-decorrelated engine.")

    # ---------------------------------------------------------------- PHASE 4
    P_(f"\n{'='*112}\n=== PHASE 4: the SKEW lever priced - what the session target actually buys")
    P_(f"{'='*112}")
    cc = R[R["obj"].str.startswith("cell:")].copy()
    cc["halt"] = cc["obj"].str.extract(r"h(\d+|inf)")[0]
    cc["targ"] = cc["obj"].str.extract(r"_t(\d+|inf)")[0]
    P_(f"{'target':<10}{'cells':>7}{'med Sharpe':>12}{'med skew':>11}{'med wk+%':>11}"
       f"{'med weekly $':>15}")
    for t in sorted(cc["targ"].dropna().unique(),
                    key=lambda x: (x == "inf", 0 if x == "inf" else int(x))):
        q = cc[cc["targ"] == t]
        P_(f"{t:<10}{len(q):>7}{q['sharpe'].median():>12.3f}{q['skew'].median():>11.2f}"
           f"{q['wkpos'].median():>10.1f}%{q['mean'].median():>15,.0f}")
    cc.to_csv(os.path.join(OUT, "cells.csv"), index=False)
    if len(cc) > 30:
        Xm = np.column_stack([np.ones(len(cc)), cc["sharpe"], cc["skew"]])
        bta, *_ = np.linalg.lstsq(Xm, cc["wkpos"].to_numpy(), rcond=None)
        P_(f"\n   wk+%  =  {bta[0]:.1f}  +  {bta[1]:.1f} * Sharpe  {bta[2]:+.2f} * skew"
           f"      (216 cells, OLS)")
        P_(f"   -> one unit of weekly skew costs {abs(bta[2]):.2f} pp of positive weeks; one")
        P_(f"      0.10 of weekly Sharpe buys {bta[1]*0.10:.2f} pp. The exchange rate between")
        P_(f"      the owner's consistency goal and the 'positive skew is his money structure'")
        P_(f"      design prior is now a number.")

    # ---------------------------------------------------------------- PHASE 5
    P_(f"\n{'='*112}\n=== PHASE 5: the honest ceiling from cloning our own engine")
    P_(f"{'='*112}")
    ac = float(pd.Series(v1).autocorr(1))
    P_(f"   P1 weekly lag-1 autocorrelation {ac:+.3f} -> effective independent weeks "
       f"{len(v1)*(1-ac)/(1+ac):.0f} of {len(v1)}")
    P_(f"\n   scaling P1 by contracts changes NOTHING here: the positive-week rate is")
    P_(f"   scale-invariant. Only adding streams or reshaping the distribution moves it.")
    for rho in (0.0, 0.1, 0.3):
        cap = 100 * float(cf_pos_rate(S_p1 * np.sqrt(1e6) / np.sqrt(1 + (1e6 - 1) * rho),
                                      0.0)) if rho > 0 else 100.0
        P_(f"   at pairwise rho = {rho:.1f}, the K -> infinity ceiling is "
           f"{cap:.1f} % positive weeks")
    P_(f"\n=== STATUS: planning instrument. NOTHING ADOPTED. ===")
    out.close()


if __name__ == "__main__":
    main()
