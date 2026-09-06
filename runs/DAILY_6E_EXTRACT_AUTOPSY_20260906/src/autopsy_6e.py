"""STEP 2 — 6E DAILY autopsy (§9 protocol, daily resolution).

Primary return = ret_pct (RATIO-STITCHED, cross-era percent-safe per DELEV01). Level/range work
uses close_add / raw OHLC (point-difference). Purely DESCRIPTIVE — no ledger trial, no P&L claim.
Every table is written from the program; nothing is assembled by hand.
"""
from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(HERE)
OUT = os.path.join(RUN, "out")
SEAL = pd.Timestamp("2026-08-01")

_fh = open(os.path.join(OUT, "autopsy.txt"), "w", encoding="utf-8")


def P(*a):
    print(*a, flush=True)
    print(*a, file=_fh)


def tstat(x):
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    if len(x) < 2:
        return np.nan, len(x)
    return float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))), len(x)


def variance_ratio(r, q):
    """Lo-MacKinlay overlapping VR(q) with heteroskedasticity-robust z (their eq. for M2)."""
    r = np.asarray(r, dtype=float)
    r = r[~np.isnan(r)]
    n = len(r)
    if n < q + 2:
        return np.nan, np.nan
    mu = r.mean()
    var1 = np.sum((r - mu) ** 2) / (n - 1)
    # q-period overlapping returns
    rq = np.convolve(r, np.ones(q), mode="valid")            # length n-q+1
    m = q * (n - q + 1) * (1 - q / n)
    varq = np.sum((rq - q * mu) ** 2) / m
    vr = varq / var1
    # heteroskedasticity-robust variance of VR (Lo-MacKinlay 1988)
    theta = 0.0
    for j in range(1, q):
        num = np.sum(((r[j:] - mu) ** 2) * ((r[:n - j] - mu) ** 2))
        den = (np.sum((r - mu) ** 2)) ** 2
        delta = num / den
        theta += (2.0 * (q - j) / q) ** 2 * delta
    z = (vr - 1.0) / np.sqrt(theta) if theta > 0 else np.nan
    return float(vr), float(z)


def efficiency_ratio(price, w):
    """Kaufman ER over rolling window w: |net change| / sum |bar change|."""
    p = np.asarray(price, dtype=float)
    net = np.abs(p[w:] - p[:-w])
    absd = np.abs(np.diff(p))
    vol = np.array([absd[i:i + w].sum() for i in range(len(p) - w)])
    er = np.where(vol > 0, net / vol, np.nan)
    return er


def main():
    s = pd.read_parquet(os.path.join(OUT, "6e_daily.parquet"))
    s = s[s["date"] < SEAL].reset_index(drop=True)
    assert s["date"].max() < SEAL
    s["dow"] = s["date"].dt.dayofweek           # 0=Mon
    s["month"] = s["date"].dt.month
    s["year"] = s["date"].dt.year
    r = s["ret_pct"]
    rlog = np.log1p(r)
    valid = r.dropna()

    P("=" * 100)
    P("=== 6E DAILY AUTOPSY  (CME Euro FX, ratio-stitched % returns; DESCRIPTIVE, DISCOVERY_CONSUMED)")
    P("=" * 100)
    P(f"    sessions {len(s):,}   {s['date'].min().date()} -> {s['date'].max().date()}   "
      f"seal-clean (< {SEAL.date()})")
    ann = np.sqrt(252)
    P(f"    daily ret_pct: mean {r.mean():+.3e}  sd {r.std():.4e}  "
      f"ann.vol {r.std()*ann:.3%}  ann.mean {r.mean()*252:+.3%}")
    P(f"    17y drift: close 1.3164 (2009) -> 1.1550 (2026)  = EUR depreciated vs USD "
      f"({(1.1550/1.3164-1):.1%} total)")

    # ============================================================= 1  RETURNS
    P("\n--- 1. RETURNS -----------------------------------------------------------------")
    dow_names = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri", 5: "Sat", 6: "Sun"}
    dow_rows = []
    P("  (a) by day-of-week")
    P(f"      {'dow':<5}{'n':>7}{'mean%':>10}{'t':>8}{'sd%':>9}{'%up':>8}")
    for k in range(5):
        x = s.loc[s["dow"] == k, "ret_pct"].dropna()
        t, n = tstat(x)
        dow_rows.append(dict(dow=dow_names[k], n=n, mean_pct=float(x.mean()), t=t,
                             sd_pct=float(x.std()), share_up=float((x > 0).mean())))
        P(f"      {dow_names[k]:<5}{n:>7,}{x.mean()*100:>10.4f}{t:>8.2f}{x.std()*100:>9.4f}"
          f"{(x>0).mean():>8.1%}")
    pd.DataFrame(dow_rows).to_csv(os.path.join(OUT, "autopsy_dow.csv"), index=False)

    mo_rows = []
    P("  (b) by calendar month")
    P(f"      {'mo':>4}{'n':>7}{'mean%':>10}{'t':>8}")
    for m in range(1, 13):
        x = s.loc[s["month"] == m, "ret_pct"].dropna()
        t, n = tstat(x)
        mo_rows.append(dict(month=m, n=n, mean_pct=float(x.mean()), t=t))
        P(f"      {m:>4}{n:>7,}{x.mean()*100:>10.4f}{t:>8.2f}")
    pd.DataFrame(mo_rows).to_csv(os.path.join(OUT, "autopsy_month.csv"), index=False)

    P("  (c) conditional on PRIOR-day sign  (persistence vs reversal, daily)")
    prev = r.shift(1)
    for lab, mask in [("prior UP", prev > 0), ("prior DOWN", prev < 0), ("prior FLAT", prev == 0)]:
        x = r[mask].dropna()
        t, n = tstat(x)
        P(f"      next | {lab:<10} n {n:>6,}  mean {x.mean()*100:+.4f}%  t {t:+.2f}  "
          f"%up {(x>0).mean():.1%}")
    # unconditional control
    t, n = tstat(r)
    P(f"      next | UNCONDITIONAL n {n:>6,}  mean {r.mean()*100:+.4f}%  t {t:+.2f}  "
      f"%up {(r>0).mean():.1%}")

    # ============================================================= 2  DISTRIBUTION
    P("\n--- 2. DISTRIBUTION ------------------------------------------------------------")
    from scipy import stats as st
    sk = float(st.skew(valid)); ku = float(st.kurtosis(valid))          # excess kurtosis
    P(f"  skew {sk:+.3f}   excess-kurtosis {ku:+.3f}   (Gaussian: 0, 0)")
    jb = st.jarque_bera(valid)
    P(f"  Jarque-Bera {jb.statistic:.1f}  p {jb.pvalue:.2e}  -> non-normal (expected)")
    qs = [0.001, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999]
    P("  percentiles of daily ret_pct:")
    P("    " + "  ".join(f"p{int(q*1000)/10}:{valid.quantile(q)*100:+.3f}%" for q in qs))
    z = (valid - valid.mean()) / valid.std()
    for thr in (2, 3, 4):
        emp = float((z.abs() > thr).mean()); gau = 2 * (1 - st.norm.cdf(thr))
        P(f"  |z|>{thr}: empirical {emp:.4%}  gaussian {gau:.4%}  ratio {emp/gau:.1f}x")
    # gap / segment decomposition (overnight vs intraday, in points and as % of total var)
    on = s["overnight_points"].dropna(); intr = s["intraday_points"].dropna()
    P(f"  overnight vs intraday (points): var(overnight) {on.var():.3e}  var(intraday) "
      f"{intr.var():.3e}  overnight var-share {on.var()/(on.var()+intr.var()):.1%}")
    P(f"    mean overnight {on.mean():+.3e}  mean intraday {intr.mean():+.3e}  "
      f"(daily point-return decomposition; FX is a ~24h market so 'overnight' = prior-close->open)")
    # realized vol regimes
    rv21 = r.rolling(21).std() * ann
    P(f"  realized vol (21d ann.): min {rv21.min():.1%}  median {rv21.median():.1%}  "
      f"p95 {rv21.quantile(.95):.1%}  max {rv21.max():.1%}")
    dist = dict(skew=sk, excess_kurtosis=ku, jb_stat=float(jb.statistic), jb_p=float(jb.pvalue),
                overnight_var_share=float(on.var()/(on.var()+intr.var())),
                rv21_median=float(rv21.median()), rv21_p95=float(rv21.quantile(.95)))
    json.dump(dist, open(os.path.join(OUT, "autopsy_distribution.json"), "w"), indent=2)

    # ============================================================= 3  DEPENDENCE
    P("\n--- 3. DEPENDENCE --------------------------------------------------------------")
    rv = valid.values
    P("  (a) return autocorrelation (log ret):")
    rl = rlog.dropna().values
    ac_rows = []
    for lag in (1, 2, 3, 4, 5, 10, 21):
        ac = float(np.corrcoef(rl[:-lag], rl[lag:])[0, 1])
        se = 1 / np.sqrt(len(rl))
        ac_rows.append(dict(kind="ret", lag=lag, acf=ac, z=ac / se))
        P(f"      lag {lag:>3}: acf {ac:+.4f}   z {ac/se:+.2f}   (|z|>1.96 => sig)")
    P("  (b) VOLATILITY autocorrelation (|log ret|):")
    al = np.abs(rl)
    for lag in (1, 2, 5, 10, 21, 63):
        ac = float(np.corrcoef(al[:-lag], al[lag:])[0, 1])
        se = 1 / np.sqrt(len(al))
        ac_rows.append(dict(kind="absret", lag=lag, acf=ac, z=ac / se))
        P(f"      lag {lag:>3}: acf {ac:+.4f}   z {ac/se:+.2f}")
    pd.DataFrame(ac_rows).to_csv(os.path.join(OUT, "autopsy_autocorr.csv"), index=False)

    P("  (c) sign persistence:")
    sgn = np.sign(rv)
    up = sgn > 0
    puu = float((up[1:] & up[:-1]).sum() / up[:-1].sum())
    pdd = float((~up[1:] & ~up[:-1]).sum() / (~up[:-1]).sum())
    P(f"      P(up)={up.mean():.3f}  P(up|up)={puu:.3f}  P(down|down)={pdd:.3f}  "
      f"P(up|up)-P(up)={puu-up.mean():+.3f}")

    P("  (d) variance ratio (Lo-MacKinlay, het-robust z; VR>1 trend, VR<1 reversal):")
    vr_rows = []
    for q in (2, 5, 10, 21, 63):
        vr, zz = variance_ratio(rl, q)
        vr_rows.append(dict(q=q, VR=vr, z=zz))
        P(f"      VR({q:>3}) {vr:.4f}   z {zz:+.2f}")
    pd.DataFrame(vr_rows).to_csv(os.path.join(OUT, "autopsy_varratio.csv"), index=False)

    P("  (e) trend vs reversal: OLS forward-k return on trailing-k return (log, non-overlap step=k):")
    tr_rows = []
    cr = pd.Series(rl)
    for k in (1, 5, 21, 63, 126, 252):
        trail = cr.rolling(k).sum()
        fwd = cr[::-1].rolling(k).sum()[::-1].shift(-1)   # sum of NEXT k, causal (no overlap w/ trail)
        # align, subsample every k to avoid overlap
        df = pd.DataFrame({"x": trail, "y": fwd}).dropna()
        df = df.iloc[::k]
        if len(df) < 10:
            continue
        x = df["x"].values; y = df["y"].values
        b1, b0 = np.polyfit(x, y, 1)
        rr = np.corrcoef(x, y)[0, 1]
        tval = rr * np.sqrt((len(df) - 2) / max(1 - rr ** 2, 1e-12))
        tr_rows.append(dict(k=k, n=len(df), beta=float(b1), corr=float(rr), t=float(tval)))
        P(f"      k={k:>4} n {len(df):>4}  beta {b1:+.4f}  corr {rr:+.4f}  t {tval:+.2f}  "
          f"-> {'TREND' if rr>0 else 'REVERSAL'}")
    pd.DataFrame(tr_rows).to_csv(os.path.join(OUT, "autopsy_trend_reversal.csv"), index=False)

    # ============================================================= 4  PATH
    P("\n--- 4. PATH --------------------------------------------------------------------")
    price = s["close_ratio"].values          # ratio-adjusted (percent-safe path)
    P("  (a) Kaufman efficiency ratio (how directional is a window):")
    er_rows = []
    for w in (10, 21, 63):
        er = efficiency_ratio(price, w)
        er = er[~np.isnan(er)]
        er_rows.append(dict(window=w, mean_ER=float(er.mean()), median_ER=float(np.median(er)),
                            share_gt_0p5=float((er > 0.5).mean())))
        P(f"      ER({w:>2}): mean {er.mean():.3f}  median {np.median(er):.3f}  "
          f"share>0.5 {(er>0.5).mean():.1%}   (1=pure trend, 0=pure chop; random-walk ~ 1/sqrt(w))")
    pd.DataFrame(er_rows).to_csv(os.path.join(OUT, "autopsy_efficiency.csv"), index=False)

    P("  (b) trend maturation: forward 21d return by TRAILING 63d return tercile:")
    trail63 = pd.Series(rl).rolling(63).sum()
    fwd21 = pd.Series(rl)[::-1].rolling(21).sum()[::-1].shift(-1)
    df = pd.DataFrame({"trail": trail63, "fwd": fwd21}).dropna()
    df["terc"] = pd.qcut(df["trail"], 3, labels=["bottom", "mid", "top"])
    for terc in ["bottom", "mid", "top"]:
        x = df.loc[df["terc"] == terc, "fwd"]
        t, n = tstat(x)
        P(f"      trailing63 {terc:<7} -> fwd21 mean {x.mean()*100:+.3f}%  t {t:+.2f}  n {n:,}")
    P("      (top>bottom monotone => momentum; inverted => reversal at the swing scale)")

    # ============================================================= 5  STRUCTURE (FX-specific)
    P("\n--- 5. STRUCTURE (FX turn-of-week / turn-of-month; NO intraday session data) ----")
    # turn-of-month: last trading day of month, and window
    s2 = s.dropna(subset=["ret_pct"]).copy()
    s2["ym"] = s2["date"].dt.to_period("M")
    s2["tom_rank_from_end"] = s2.groupby("ym").cumcount(ascending=False)   # 0 = last td of month
    s2["tom_rank_from_start"] = s2.groupby("ym").cumcount()                # 0 = first td of month
    P("  turn-of-month (rank 0 = last trading day; -k means k days before):")
    tom_rows = []
    for lab, mask in [
        ("last td (0)", s2["tom_rank_from_end"] == 0),
        ("last-1", s2["tom_rank_from_end"] == 1),
        ("ToM window [-2..0]", s2["tom_rank_from_end"] <= 2),
        ("first td", s2["tom_rank_from_start"] == 0),
        ("first 3 td", s2["tom_rank_from_start"] <= 2),
        ("rest of month", (s2["tom_rank_from_end"] > 2) & (s2["tom_rank_from_start"] > 2)),
    ]:
        x = s2.loc[mask, "ret_pct"]
        t, n = tstat(x)
        tom_rows.append(dict(bucket=lab, n=n, mean_pct=float(x.mean()), t=t))
        P(f"      {lab:<20} n {n:>6,}  mean {x.mean()*100:+.4f}%  t {t:+.2f}")
    pd.DataFrame(tom_rows).to_csv(os.path.join(OUT, "autopsy_turn_of_month.csv"), index=False)
    P("  turn-of-week: Fri->Mon carry vs within-week (see DOW table 1a; Mon/Fri means above)")

    # ============================================================= 6  CORRELATION TO NQ
    P("\n--- 6. CROSS-ASSET: 6E vs NQ daily-return correlation (the diversification prize) ---")
    nq = pd.read_parquet(os.path.join(OUT, "nq_daily_for_corr.parquet"))
    m = s[["date", "ret_pct"]].merge(nq[["date", "ret_pct"]], on="date", suffixes=("_6e", "_nq"))
    m = m.dropna()
    rho = float(m["ret_pct_6e"].corr(m["ret_pct_nq"]))
    rho_sp = float(m["ret_pct_6e"].corr(m["ret_pct_nq"], method="spearman"))
    P(f"  shared sessions {len(m):,}   Pearson rho {rho:+.4f}   Spearman {rho_sp:+.4f}")
    yr = m.assign(year=m["date"].dt.year).groupby("year").apply(
        lambda g: g["ret_pct_6e"].corr(g["ret_pct_nq"]))
    P("  by year: " + "  ".join(f"{int(y)}:{v:+.2f}" for y, v in yr.items()))
    P(f"  rho range across years: {yr.min():+.2f} .. {yr.max():+.2f}")
    m.assign(year=m["date"].dt.year).groupby("year").apply(
        lambda g: pd.Series(dict(n=len(g), rho=g["ret_pct_6e"].corr(g["ret_pct_nq"])))
    ).to_csv(os.path.join(OUT, "autopsy_corr_nq_by_year.csv"))
    json.dump(dict(pearson=rho, spearman=rho_sp, shared_sessions=int(len(m)),
                   rho_min_year=float(yr.min()), rho_max_year=float(yr.max())),
              open(os.path.join(OUT, "autopsy_corr_nq.json"), "w"), indent=2)

    P("\n" + "=" * 100)
    P("=== AUTOPSY COMPLETE — descriptive only, no P&L, no ledger trial. DISCOVERY_CONSUMED.")
    P("=" * 100)
    _fh.close()


if __name__ == "__main__":
    main()
