"""
CROSSASSET Wave-1 MARKET AUTOPSY — YM (E-mini Dow, CBOT/Globex, point value $5).

DESCRIPTIVE SCIENCE per NQ_RESEARCH_PLAYBOOK.md transfer-checklist step 6 (§9 protocol).
NOT a falsifiable test: no ledger trial, no strategy, no P&L, no promotion. DISCOVERY_CONSUMED.

MANDATORY DISCIPLINE enforced in code:
 - POINTS BASIS ONLY (DELEV01 law): the substrate is ADDITIVELY back-adjusted, so absolute
   levels are shifted. Every return/range/threshold is a POINT DIFFERENCE (close_t - close_{t-1}),
   never a % of price, never a level threshold.
 - NATIVE SESSION determined FROM YM's OWN VOLUME PROFILE (not assumed NQ 09:30-16:00).
 - HARD-DROP every row with time >= 2026-08-01 at load; print the retained boundary.

Session convention (CLAUDE.md/session_boundary.py): CME session runs 18:00 ET -> 17:00 ET next
calendar day; a bar with hour>=18 belongs to the NEXT calendar day's session label. Bars are
END-stamped (bar stamped 09:31 covers 09:30:00-09:31:00).
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
from scipy import stats

YM_PV = 5.0     # $ per point (spec) — used ONLY for a $-context note, never in a return calc
NQ_PV = 20.0
SEAL = pd.Timestamp("2026-08-01")   # hard-drop >= this instant

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
YM_PATH = os.path.abspath(os.path.join(RUN, "..", "SM1M_YM_SUBSTRATE", "out", "ym_1m_2022_2026.parquet"))
NQ_PATH = os.path.abspath(os.path.join(RUN, "..", "SM1M_SUBSTRATE", "out", "nq_1m_2022_2026.parquet"))

RTH_START = 9 * 60 + 31   # first END-stamp inside RTH (bar 09:31 opens 09:30)  = 571
RTH_END = 16 * 60         # last END-stamp inside RTH (bar 16:00 opens 15:59)   = 960


def load(path, name):
    df = pd.read_parquet(path)
    n0 = len(df)
    df = df[df["time"] < SEAL].copy()
    n1 = len(df)
    print(f"[{name}] loaded {n0:,} rows; hard-dropped {n0-n1:,} rows >= {SEAL.date()} "
          f"(seal >= 2026-08-01); retained {n1:,}; last retained bar {df['time'].max()}")
    df.sort_values("time", inplace=True, kind="mergesort")
    df.reset_index(drop=True, inplace=True)
    t = df["time"]
    df["mod"] = t.dt.hour * 60 + t.dt.minute
    # session label: hour>=18 -> next calendar day
    sd = t.dt.normalize()
    roll = t.dt.hour >= 18
    sd = sd + pd.to_timedelta(roll.astype("int64"), unit="D")
    df["sdate"] = sd.dt.date
    df["dow"] = pd.to_datetime(df["sdate"]).dt.dayofweek  # 0=Mon session
    return df


def acf(x, lags):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    x = x - x.mean()
    n = len(x)
    denom = np.dot(x, x)
    out = []
    for k in lags:
        if k >= n:
            out.append(np.nan); continue
        out.append(np.dot(x[:-k], x[k:]) / denom)
    return out


def variance_ratio(ret, q):
    """Lo-MacKinlay VR(q) with overlapping windows, heteroskedasticity-robust z (M2)."""
    r = np.asarray(ret, float)
    r = r[~np.isnan(r)]
    n = len(r)
    if n < q + 2:
        return np.nan, np.nan
    mu = r.mean()
    var1 = np.sum((r - mu) ** 2) / (n - 1)
    # overlapping q-sums
    csum = np.cumsum(np.insert(r, 0, 0.0))
    qs = csum[q:] - csum[:-q]           # length n-q+1
    m = q * (n - q + 1) * (1 - q / n)
    varq = np.sum((qs - q * mu) ** 2) / m
    vr = varq / var1
    # heteroskedastic-robust variance of VR (Lo-MacKinlay 1988 M2 statistic):
    #   delta_j = sum_t (r_t-mu)^2 (r_{t-j}-mu)^2 / [ sum_t (r_t-mu)^2 ]^2
    #   theta   = sum_{j=1}^{q-1} [2(q-j)/q]^2 * delta_j ;  z = (VR-1)/sqrt(theta)
    dev2 = (r - mu) ** 2
    denom2 = np.sum(dev2) ** 2
    theta = 0.0
    for j in range(1, q):
        w = 2 * (q - j) / q
        delta_j = np.sum(dev2[j:] * dev2[:-j]) / denom2
        theta += (w ** 2) * delta_j
    z = (vr - 1) / np.sqrt(theta) if theta > 0 else np.nan
    return vr, z


def main():
    lines_dist, lines_dep, lines_path, lines_sess = [], [], [], []

    ym = load(YM_PATH, "YM")
    print(f"[YM] point value ${YM_PV}/pt (spec); ALL returns below are POINT DIFFERENCES "
          f"(additive back-adj -> DELEV01: never %, never level).")

    # ============================ NATIVE SESSION (volume profile) ============================
    vp = ym.groupby("mod").agg(bars=("volume", "size"), vol=("volume", "sum")).reset_index()
    vp["hhmm"] = vp["mod"].map(lambda m: f"{m//60:02d}:{m%60:02d}")
    vp.to_csv(os.path.join(OUT, "volume_profile_by_minute.csv"), index=False)
    total_vol = vp["vol"].sum()
    # minute-of-day coverage: which minutes actually trade
    present = set(ym["mod"].unique())
    missing = [m for m in range(1440) if m not in present]
    # RTH vs ETH share
    rth_mask = (ym["mod"] >= RTH_START) & (ym["mod"] <= RTH_END)
    rth_vol = int(ym.loc[rth_mask, "volume"].sum())
    eth_vol = int(ym.loc[~rth_mask, "volume"].sum())
    # maintenance-break occupancy (17:00-18:00 = mod 1021..1080)
    maint = ym[(ym["mod"] > RTH_END) & (ym["mod"] >= 17 * 60 + 1) & (ym["mod"] <= 18 * 60)]
    # top volume minutes
    top = vp.sort_values("vol", ascending=False).head(15)

    ls = []
    ls.append("YM NATIVE SESSION — determined from YM's OWN 1-min volume/bar profile")
    ls.append("=" * 78)
    ls.append(f"total volume {total_vol:,}; total bars {len(ym):,}; distinct sessions {ym['sdate'].nunique():,}")
    ls.append(f"minutes-of-day with ANY bar: {len(present)}/1440; minutes never traded: {len(missing)}")
    if missing:
        # summarize contiguous missing ranges
        miss = sorted(missing); rng = []
        s = p = miss[0]
        for m in miss[1:]:
            if m == p + 1: p = m
            else: rng.append((s, p)); s = p = m
        rng.append((s, p))
        ls.append("  contiguous NON-traded minute ranges (mod, HH:MM):")
        for a, b in rng:
            ls.append(f"    {a:4d}-{b:4d}  {a//60:02d}:{a%60:02d}-{b//60:02d}:{b%60:02d}")
    ls.append("")
    ls.append(f"RTH (09:31-16:00 END-stamp = 09:30:00-16:00:00) volume share: "
              f"{rth_vol/total_vol:6.2%}  ({rth_vol:,})")
    ls.append(f"ETH-overnight (all other) volume share:                     "
              f"{eth_vol/total_vol:6.2%}  ({eth_vol:,})")
    ls.append(f"maintenance window 17:01-18:00 bars present: {len(maint)} "
              f"(expect ~0 if closed 17:00-18:00 ET)")
    ls.append("")
    ls.append("Top 15 highest-volume minutes-of-day (END-stamp ET):")
    ls.append(f"  {'HH:MM':>6} {'mod':>5} {'bars':>7} {'sum_vol':>14} {'%oftot':>8}")
    for _, r in top.iterrows():
        ls.append(f"  {r['hhmm']:>6} {int(r['mod']):5d} {int(r['bars']):7d} {int(r['vol']):14,d} "
                  f"{r['vol']/total_vol:7.3%}")
    # hourly volume profile
    ym["hour"] = ym["mod"] // 60
    hv = ym.groupby("hour")["volume"].sum()
    ls.append("")
    ls.append("Volume by clock hour (ET, END-stamp):")
    for h in range(24):
        v = int(hv.get(h, 0))
        ls.append(f"  {h:02d}:00-{h:02d}:59  {v:14,d}  {v/total_vol:7.3%}  " + "#" * int(round(40 * v / hv.max())))
    session_txt_head = "\n".join(ls)

    # ============================ BUILD DAILY (SESSION) FRAME ============================
    g = ym.groupby("sdate", sort=True)
    rows = []
    for sd, blk in g:
        mod = blk["mod"].values
        o = blk["open"].values; h = blk["high"].values
        lo = blk["low"].values; c = blk["close"].values
        v = blk["volume"].values
        rmask = (mod >= RTH_START) & (mod <= RTH_END)
        n_rth = int(rmask.sum())
        rec = {"sdate": sd, "n_bars": len(blk), "n_rth": n_rth,
               "eth_open": o[0], "eth_close": c[-1],
               "eth_high": h.max(), "eth_low": lo.min(), "vol": int(v.sum())}
        if n_rth >= 300:  # require a substantially complete RTH (390 full)
            ro = o[rmask]; rh = h[rmask]; rl = lo[rmask]; rc = c[rmask]
            rec.update({
                "rth_open": ro[0], "rth_close": rc[-1],
                "rth_high": rh.max(), "rth_low": rl.min(),
                "rth_ret": rc[-1] - ro[0],
                "rth_range": rh.max() - rl.min(),
            })
            # opening ranges (first 15/30/60 min of RTH)
            for w, tag in [(15, "or15"), (30, "or30"), (60, "or60")]:
                sub = rmask & (mod <= RTH_START + w - 1)
                if sub.sum() >= w * 0.8:
                    rec[f"{tag}_hi"] = h[sub].max(); rec[f"{tag}_lo"] = lo[sub].min()
                    rec[f"{tag}_range"] = h[sub].max() - lo[sub].min()
            # efficiency ratio / tortuosity over RTH
            steps = np.abs(np.diff(rc))
            path_len = steps.sum()
            disp = abs(rc[-1] - ro[0])
            rec["rth_er"] = disp / path_len if path_len > 0 else np.nan
            rec["rth_pathlen"] = path_len
            rec["rth_disp"] = disp
            # excursions from RTH open (points)
            rec["up_exc"] = rh.max() - ro[0]
            rec["dn_exc"] = ro[0] - rl.min()
            # realized vol over RTH (points): sqrt sum sq 1-min returns
            rr = np.diff(rc)
            rec["rth_rv"] = np.sqrt(np.sum(rr ** 2))
        rows.append(rec)
    D = pd.DataFrame(rows).sort_values("sdate").reset_index(drop=True)
    Dr = D.dropna(subset=["rth_ret"]).reset_index(drop=True)  # full-RTH sessions

    # overnight & prior-day linkage on the full-RTH frame
    Dr["prev_rth_close"] = Dr["rth_close"].shift(1)
    Dr["prev_rth_high"] = Dr["rth_high"].shift(1)
    Dr["prev_rth_low"] = Dr["rth_low"].shift(1)
    Dr["prev_eth_open"] = Dr["eth_open"].shift(1)
    Dr["gap"] = Dr["rth_open"] - Dr["prev_rth_close"]           # overnight gap (points)
    Dr["on_ret"] = Dr["rth_open"] - Dr["prev_rth_close"]        # overnight return (same as gap here)
    Dr["cc_ret"] = Dr["rth_close"] - Dr["prev_rth_close"]       # RTH close-to-close daily return
    Dr["overnight_range"] = np.nan
    # overnight range = range of the ETH bars between prior RTH close and this RTH open
    # recompute per session using the ETH-window bars (mod<RTH_START within this session +
    # mod>RTH_END of the PRIOR session). Simpler robust proxy: session eth extremes excluding RTH.
    on_hi = []; on_lo = []
    grp = {sd: blk for sd, blk in ym.groupby("sdate", sort=True)}
    for sd in Dr["sdate"]:
        blk = grp[sd]
        mod = blk["mod"].values
        pre = (mod < RTH_START)  # the overnight run leading INTO this session's RTH
        if pre.sum() > 0:
            on_hi.append(blk["high"].values[pre].max())
            on_lo.append(blk["low"].values[pre].min())
        else:
            on_hi.append(np.nan); on_lo.append(np.nan)
    Dr["on_high"] = on_hi; Dr["on_low"] = on_lo
    Dr["overnight_range"] = Dr["on_high"] - Dr["on_low"]

    D.to_csv(os.path.join(OUT, "daily_session_frame.csv"), index=False)
    n_sess = len(D); n_full = len(Dr)

    # ============================ RETURNS BY TIME-OF-DAY / DOW / SIGN ============================
    # bar-level within-session point returns (drop first bar of each session)
    ym["ret"] = ym["close"].diff()
    first_of_sess = ym["sdate"] != ym["sdate"].shift(1)
    ym.loc[first_of_sess, "ret"] = np.nan
    # by minute-of-day
    tod = ym.dropna(subset=["ret"]).groupby("mod")["ret"].agg(
        n="size", mean_pt="mean", sum_pt="sum", std_pt="std").reset_index()
    tod["hhmm"] = tod["mod"].map(lambda m: f"{m//60:02d}:{m%60:02d}")
    # by hour
    hourly = ym.dropna(subset=["ret"]).groupby("hour")["ret"].agg(
        n="size", mean_pt="mean", sum_pt="sum", std_pt="std").reset_index()
    hourly["seg"] = hourly["hour"].map(lambda h: "RTH" if 9 <= h <= 15 else "ETH")
    # save the merged returns_by_tod
    tod_out = tod.copy()
    tod_out.to_csv(os.path.join(OUT, "returns_by_tod.csv"), index=False)

    # DOW on RTH close-close return and on full-session eth return
    Dr["dow"] = pd.to_datetime(Dr["sdate"]).dt.dayofweek  # 0=Mon session
    Dr["eth_ret"] = Dr["eth_close"] - Dr["eth_open"]
    dow_rth = Dr.groupby("dow")["rth_ret"].agg(n="size", mean="mean", sum="sum", std="std")
    dow_cc = Dr.dropna(subset=["cc_ret"]).groupby("dow")["cc_ret"].agg(n="size", mean="mean", sum="sum", std="std")
    dow_on = Dr.dropna(subset=["on_ret"]).groupby("dow")["on_ret"].agg(n="size", mean="mean", sum="sum", std="std")

    # session vs overnight decomposition
    rth_sum = Dr["rth_ret"].sum(); on_sum = Dr["on_ret"].sum(skipna=True)
    rth_mean = Dr["rth_ret"].mean(); on_mean = Dr["on_ret"].mean()
    rth_std = Dr["rth_ret"].std(); on_std = Dr["on_ret"].std()

    # conditional on prior-day sign / overnight sign
    Dr["prev_rth_ret"] = Dr["rth_ret"].shift(1)
    def cond_mean(cond_col, tgt):
        sub = Dr.dropna(subset=[cond_col, tgt])
        pos = sub[sub[cond_col] > 0][tgt]; neg = sub[sub[cond_col] < 0][tgt]
        return (len(pos), pos.mean(), len(neg), neg.mean())

    DOW = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri"}
    L = []
    L.append("YM RETURNS AUTOPSY — POINTS BASIS (point diffs; additive back-adj; DELEV01)")
    L.append("=" * 78)
    L.append(f"full-RTH sessions used: {n_full} of {n_sess} session-dates "
             f"(RTH>=300 of 390 bars required)")
    L.append("")
    L.append("--- Point return by CLOCK HOUR (within-session 1-min diffs) ---")
    L.append(f"  {'hour':>5} {'seg':>4} {'n':>8} {'mean_pt':>10} {'sum_pt':>12} {'std_pt':>9}")
    for _, r in hourly.iterrows():
        L.append(f"  {int(r['hour']):02d}:00 {r['seg']:>4} {int(r['n']):8d} {r['mean_pt']:10.5f} "
                 f"{r['sum_pt']:12.1f} {r['std_pt']:9.4f}")
    L.append("")
    L.append("--- RTH-open-to-close point return by SESSION DAY-OF-WEEK ---")
    L.append(f"  {'dow':>4} {'n':>6} {'mean_pt':>10} {'sum_pt':>11} {'std_pt':>9}")
    for d, r in dow_rth.iterrows():
        L.append(f"  {DOW.get(d,d):>4} {int(r['n']):6d} {r['mean']:10.4f} {r['sum']:11.1f} {r['std']:9.3f}")
    L.append("")
    L.append("--- Overnight (prevRTHclose->RTHopen) point return by SESSION DOW ---")
    L.append(f"  {'dow':>4} {'n':>6} {'mean_pt':>10} {'sum_pt':>11} {'std_pt':>9}")
    for d, r in dow_on.iterrows():
        L.append(f"  {DOW.get(d,d):>4} {int(r['n']):6d} {r['mean']:10.4f} {r['sum']:11.1f} {r['std']:9.3f}")
    L.append("")
    L.append("--- SESSION (RTH) vs OVERNIGHT decomposition (points) ---")
    L.append(f"  RTH  open->close : n={Dr['rth_ret'].notna().sum():4d}  mean={rth_mean:8.4f}  "
             f"sum={rth_sum:10.1f}  std={rth_std:8.3f}")
    L.append(f"  OVN  pc->open    : n={Dr['on_ret'].notna().sum():4d}  mean={on_mean:8.4f}  "
             f"sum={on_sum:10.1f}  std={on_std:8.3f}")
    L.append(f"  (context in $: x{YM_PV:.0f}/pt -> RTH sum ${rth_sum*YM_PV:,.0f}, OVN sum ${on_sum*YM_PV:,.0f})")
    L.append("")
    L.append("--- CONDITIONAL MEAN point return (continuation vs reversal read) ---")
    for cc, tt, lab in [("prev_rth_ret", "rth_ret", "prior-RTH sign -> today RTH ret"),
                        ("on_ret", "rth_ret", "overnight sign -> today RTH ret"),
                        ("prev_rth_ret", "on_ret", "prior-RTH sign -> tonight OVN ret"),
                        ("gap", "rth_ret", "gap sign -> today RTH ret (gap fill/go)")]:
        npos, mpos, nneg, mneg = cond_mean(cc, tt)
        L.append(f"  {lab:38s}:  after>0 n={npos:4d} mean={mpos:8.4f} | after<0 n={nneg:4d} mean={mneg:8.4f}")
    lines_ret_extra = "\n".join(L)

    # ============================ DISTRIBUTION ============================
    def desc(x, name, unit="pt"):
        x = np.asarray(pd.Series(x).dropna(), float)
        q = np.percentile(x, [0.5, 1, 5, 25, 50, 75, 95, 99, 99.5])
        return (f"  {name:24s} n={len(x):5d} mean={x.mean():9.4f} sd={x.std():9.4f} "
                f"skew={stats.skew(x):7.3f} exkurt={stats.kurtosis(x):8.3f}\n"
                f"    pctl[{unit}] 0.5/1/5/25/50/75/95/99/99.5: "
                + " ".join(f"{v:.2f}" for v in q))
    bar_ret = ym["ret"].dropna().values
    Ld = []
    Ld.append("YM DISTRIBUTION AUTOPSY — POINTS BASIS")
    Ld.append("=" * 78)
    Ld.append(desc(bar_ret, "1-min ret (all sess)"))
    Ld.append(desc(ym.loc[rth_mask, "ret"].dropna().values, "1-min ret (RTH only)"))
    Ld.append(desc(Dr["rth_ret"], "daily RTH ret (o->c)"))
    Ld.append(desc(Dr["cc_ret"], "daily RTH close-close"))
    Ld.append(desc(Dr["on_ret"], "overnight ret"))
    Ld.append(desc(Dr["gap"], "overnight GAP"))
    Ld.append(desc(Dr["rth_range"], "RTH range (hi-lo)"))
    Ld.append(desc(Dr["overnight_range"], "overnight range"))
    Ld.append(desc(Dr["rth_rv"], "RTH realized vol (pt)"))
    Ld.append("")
    # intraday vs overnight range ratio
    rr_ratio = (Dr["rth_range"] / Dr["overnight_range"]).replace([np.inf, -np.inf], np.nan).dropna()
    Ld.append(f"  intraday/overnight range ratio: median={rr_ratio.median():.3f} "
              f"mean={rr_ratio.mean():.3f} (>1 => RTH range dominates)")
    # gap fill: fraction of sessions whose RTH trades back through prior close
    gp = Dr.dropna(subset=["gap", "prev_rth_close", "rth_high", "rth_low"])
    filled = (((gp["gap"] > 0) & (gp["rth_low"] <= gp["prev_rth_close"])) |
              ((gp["gap"] < 0) & (gp["rth_high"] >= gp["prev_rth_close"])))
    Ld.append(f"  overnight-gap FILL rate (RTH revisits prior close): {filled.mean():.3%} of {len(gp)} sessions")
    # extreme moves
    Ld.append("")
    Ld.append("  extreme 1-min move frequency (|ret| in points):")
    for thr in [10, 20, 30, 50, 75, 100]:
        cnt = int((np.abs(bar_ret) >= thr).sum())
        Ld.append(f"    |ret|>={thr:4d}pt: {cnt:7d} bars  ({cnt/len(bar_ret):.4%})  "
                  f"~1 per {len(bar_ret)/max(cnt,1):,.0f} bars")
    # tail asymmetry daily
    dd = Dr["cc_ret"].dropna()
    Ld.append("")
    Ld.append(f"  daily close-close tail: worst={dd.min():.1f}pt best={dd.max():.1f}pt "
              f"P(down)={(dd<0).mean():.3%}  |mean_down|/mean_up="
              f"{abs(dd[dd<0].mean())/dd[dd>0].mean():.3f}")
    lines_dist = "\n".join(Ld)

    # ============================ DEPENDENCE ============================
    Lp = []
    Lp.append("YM DEPENDENCE AUTOPSY — POINTS BASIS")
    Lp.append("=" * 78)
    # 1-min return autocorr (within session)
    minr = ym["ret"].values
    lags = [1, 2, 3, 5, 10, 20, 30, 60]
    ac_min = acf(minr, lags)
    Lp.append("  1-min return autocorr (within-session diffs):")
    Lp.append("    lag: " + " ".join(f"{k}={a:+.4f}" for k, a in zip(lags, ac_min)))
    # 1-min |ret| (vol) autocorr
    ac_vol = acf(np.abs(ym["ret"].values), lags)
    Lp.append("  1-min |return| (vol) autocorr:")
    Lp.append("    lag: " + " ".join(f"{k}={a:+.4f}" for k, a in zip(lags, ac_vol)))
    # daily RTH ret autocorr
    dlags = [1, 2, 3, 5, 10]
    ac_d = acf(Dr["rth_ret"].values, dlags)
    Lp.append("  daily RTH-ret autocorr:")
    Lp.append("    lag: " + " ".join(f"{k}={a:+.4f}" for k, a in zip(dlags, ac_d)))
    # daily RV autocorr (vol clustering at daily scale)
    ac_rv = acf(Dr["rth_rv"].values, dlags)
    Lp.append("  daily RTH realized-vol autocorr:")
    Lp.append("    lag: " + " ".join(f"{k}={a:+.4f}" for k, a in zip(dlags, ac_rv)))
    Lp.append("")
    # sign persistence
    def sign_persist(x):
        s = np.sign(np.asarray(pd.Series(x).dropna(), float))
        s = s[s != 0]
        same = (s[1:] == s[:-1]).mean()
        base_up = (s > 0).mean()
        return same, base_up, len(s)
    sp_m, bu_m, nm = sign_persist(minr)
    sp_d, bu_d, nd = sign_persist(Dr["rth_ret"].values)
    Lp.append(f"  sign persistence 1-min: P(same sign next)={sp_m:.4f}  (n={nm}, P(up)={bu_m:.4f})")
    Lp.append(f"  sign persistence daily: P(same sign next)={sp_d:.4f}  (n={nd}, P(up)={bu_d:.4f})")
    Lp.append("")
    # variance ratio
    Lp.append("  Variance Ratio (VR(q)>1 trending, <1 mean-reverting; z het-robust):")
    Lp.append("   1-min within-session returns:")
    for q in [2, 5, 15, 30, 60]:
        vr, z = variance_ratio(minr, q)
        Lp.append(f"     q={q:3d}: VR={vr:.4f}  z={z:+.2f}")
    Lp.append("   daily RTH returns:")
    for q in [2, 3, 5, 10]:
        vr, z = variance_ratio(Dr["rth_ret"].values, q)
        Lp.append(f"     q={q:3d}: VR={vr:.4f}  z={z:+.2f}")
    Lp.append("")
    # conditional continuation vs reversal by magnitude terciles (daily RTH)
    Lp.append("  Conditional continuation vs reversal — daily RTH ret magnitude terciles:")
    sub = Dr.dropna(subset=["prev_rth_ret", "rth_ret"]).copy()
    sub["absprev"] = sub["prev_rth_ret"].abs()
    try:
        sub["terc"] = pd.qcut(sub["absprev"], 3, labels=["small", "mid", "large"])
        for t_ in ["small", "mid", "large"]:
            s2 = sub[sub["terc"] == t_]
            cont = np.sign(s2["prev_rth_ret"]) == np.sign(s2["rth_ret"])
            Lp.append(f"    |prevRTH| {t_:5s} (n={len(s2):4d}): P(continue)={cont.mean():.3%}  "
                      f"E[next RTH]={s2['rth_ret'].mean():+.3f}pt  "
                      f"E[signed cont]={(np.sign(s2['prev_rth_ret'])*s2['rth_ret']).mean():+.3f}pt")
    except Exception as e:
        Lp.append(f"    (tercile split failed: {e})")
    lines_dep = "\n".join(Lp)

    # ============================ PATH ============================
    La = []
    La.append("YM PATH AUTOPSY — POINTS BASIS (RTH session paths)")
    La.append("=" * 78)
    er = Dr["rth_er"].dropna()
    La.append(f"  RTH efficiency ratio (|net|/pathlen): median={er.median():.4f} "
              f"mean={er.mean():.4f} p25={er.quantile(.25):.4f} p75={er.quantile(.75):.4f}")
    La.append(f"    (ER->1 = straight/trending; ER->0 = choppy/mean-reverting. tortuosity=1/ER)")
    La.append(f"  RTH path length: median={Dr['rth_pathlen'].median():.1f}pt  "
              f"displacement median={Dr['rth_disp'].median():.1f}pt  "
              f"tortuosity(median pathlen/disp)={Dr['rth_pathlen'].median()/max(Dr['rth_disp'].median(),1e-9):.2f}")
    La.append("")
    La.append("  MFE/MAE from RTH open (points):")
    La.append(f"    up-excursion (max fav for long): median={Dr['up_exc'].median():.1f} "
              f"mean={Dr['up_exc'].mean():.1f} p90={Dr['up_exc'].quantile(.9):.1f}")
    La.append(f"    dn-excursion (max adv for long): median={Dr['dn_exc'].median():.1f} "
              f"mean={Dr['dn_exc'].mean():.1f} p90={Dr['dn_exc'].quantile(.9):.1f}")
    updn = (Dr["up_exc"] / (Dr["up_exc"] + Dr["dn_exc"])).replace([np.inf, -np.inf], np.nan).dropna()
    La.append(f"    up/(up+dn) excursion share: median={updn.median():.3f} mean={updn.mean():.3f} "
              f"(0.5 = symmetric)")
    La.append("")
    # compression/expansion: RTH range vs trailing-20 median RTH range
    Dr2 = Dr.copy()
    Dr2["rr_med20"] = Dr2["rth_range"].rolling(20, min_periods=10).median().shift(1)
    Dr2["expand"] = Dr2["rth_range"] / Dr2["rr_med20"]
    exp = Dr2["expand"].dropna()
    La.append(f"  RTH range / trailing-20d median range: median={exp.median():.3f} "
              f"P(range<0.7x)={ (exp<0.7).mean():.3%} P(range>1.5x)={(exp>1.5).mean():.3%}")
    # NR-style: does a compressed day precede an expansion? (descriptive, autocorr of range)
    ac_rng = acf(Dr["rth_range"].values, [1, 2, 3, 5])
    La.append(f"  RTH range autocorr (compression clusters): "
              + " ".join(f"lag{k}={a:+.3f}" for k, a in zip([1, 2, 3, 5], ac_rng)))
    # OR range vs full RTH range
    orr = (Dr["or30_range"] / Dr["rth_range"]).replace([np.inf, -np.inf], np.nan).dropna()
    La.append(f"  opening-30min range as fraction of full RTH range: median={orr.median():.3%} "
              f"mean={orr.mean():.3%}")
    lines_path = "\n".join(La)

    # ============================ SESSION STRUCTURE ============================
    Ls = []
    Ls.append("YM SESSION-STRUCTURE AUTOPSY — POINTS BASIS")
    Ls.append("=" * 78)
    ss = Dr.dropna(subset=["on_high", "on_low", "rth_high", "rth_low", "prev_rth_high",
                           "prev_rth_low", "or30_range"]).copy()
    # overnight high/low takeout by RTH
    to_onh = (ss["rth_high"] >= ss["on_high"]).mean()
    to_onl = (ss["rth_low"] <= ss["on_low"]).mean()
    both = ((ss["rth_high"] >= ss["on_high"]) & (ss["rth_low"] <= ss["on_low"])).mean()
    neither = ((ss["rth_high"] < ss["on_high"]) & (ss["rth_low"] > ss["on_low"])).mean()
    Ls.append(f"  RTH takes out OVERNIGHT high: {to_onh:.2%}   overnight low: {to_onl:.2%}")
    Ls.append(f"  RTH takes out BOTH ON extremes: {both:.2%}   NEITHER (inside ON range): {neither:.2%}")
    Ls.append("")
    # prior-day high/low takeout
    pdh = (ss["rth_high"] >= ss["prev_rth_high"]).mean()
    pdl = (ss["rth_low"] <= ss["prev_rth_low"]).mean()
    Ls.append(f"  RTH takes out PRIOR-DAY RTH high: {pdh:.2%}   prior-day RTH low: {pdl:.2%}")
    Ls.append("")
    # opening range breakout stats (descriptive): does price leave OR30 and where does it close
    or_hi = ss["or30_hi"]; or_lo = ss["or30_lo"]
    broke_up = (ss["rth_high"] > or_hi)
    broke_dn = (ss["rth_low"] < or_lo)
    Ls.append(f"  OR30 broken to upside: {broke_up.mean():.2%}  to downside: {broke_dn.mean():.2%}  "
              f"both: {(broke_up & broke_dn).mean():.2%}")
    # close location within RTH range (0=at low,1=at high)
    clloc = ((ss["rth_close"] - ss["rth_low"]) / (ss["rth_high"] - ss["rth_low"])).replace([np.inf,-np.inf],np.nan).dropna()
    Ls.append(f"  RTH close location in range (0=low,1=high): median={clloc_med if False else clloc.median():.3f} "
              f"mean={clloc.mean():.3f}  P(close in top 20%)={ (clloc>0.8).mean():.2%} "
              f"P(close in bot 20%)={(clloc<0.2).mean():.2%}")
    Ls.append("")
    # gap behaviour by size
    Ls.append("  Gap (overnight, prevRTHclose->RTHopen) behaviour:")
    gg = Dr.dropna(subset=["gap", "rth_ret"]).copy()
    Ls.append(f"    P(gap up)={ (gg['gap']>0).mean():.2%}  median|gap|={gg['gap'].abs().median():.1f}pt  "
              f"P(|gap|>50pt)={(gg['gap'].abs()>50).mean():.2%}")
    Ls.append(f"    corr(gap, same-day RTH ret) = {gg['gap'].corr(gg['rth_ret']):+.3f} "
              f"(+ => gap continuation; - => fade)")
    lines_sess = session_txt_head + "\n\n" + "\n".join(Ls)

    # ============================ NQ CORRELATION (diversification pre-read) ============================
    nq = load(NQ_PATH, "NQ")
    nq["ret"] = nq["close"].diff()
    nq.loc[nq["sdate"] != nq["sdate"].shift(1), "ret"] = np.nan
    nqg = nq.groupby("sdate", sort=True)
    nq_rows = []
    nq_er = []
    for sd, blk in nqg:
        mod = blk["mod"].values
        rmask2 = (mod >= RTH_START) & (mod <= RTH_END)
        if rmask2.sum() >= 300:
            rc = blk["close"].values[rmask2]; ro = blk["open"].values[rmask2]
            nq_rows.append({"sdate": sd, "nq_rth_ret": rc[-1] - ro[0], "nq_rth_close": rc[-1]})
            steps = np.abs(np.diff(rc)); pl = steps.sum()
            nq_er.append(abs(rc[-1] - ro[0]) / pl if pl > 0 else np.nan)
    NQd = pd.DataFrame(nq_rows)
    # NATIVE-vs-NQ structural contrast (justifies "materially different" for the MR family)
    nq_min = nq["ret"].values
    nq_vr_daily = variance_ratio(NQd["nq_rth_ret"].values, 5)[0]
    nq_vr_min = variance_ratio(nq_min, 30)[0]
    nq_er_med = float(np.nanmedian(nq_er))
    ym_vr_daily = variance_ratio(Dr["rth_ret"].values, 5)[0]
    ym_vr_min = variance_ratio(minr, 30)[0]
    NQd["nq_cc"] = NQd["nq_rth_close"].diff()
    merged = pd.merge(Dr[["sdate", "rth_ret", "cc_ret"]], NQd[["sdate", "nq_rth_ret", "nq_cc"]], on="sdate", how="inner")
    rho_rth = merged["rth_ret"].corr(merged["nq_rth_ret"])
    rho_cc = merged.dropna(subset=["cc_ret", "nq_cc"])["cc_ret"].corr(merged.dropna(subset=["cc_ret", "nq_cc"])["nq_cc"])
    # per-year
    merged["yr"] = pd.to_datetime(merged["sdate"]).dt.year
    yr_rho = merged.groupby("yr").apply(lambda d: d["rth_ret"].corr(d["nq_rth_ret"]))
    Lc = []
    Lc.append("YM<->NQ DAILY POINT-RETURN CORRELATION (diversification pre-read)")
    Lc.append("=" * 78)
    Lc.append(f"  shared full-RTH session-dates: {len(merged)}")
    Lc.append(f"  rho(YM RTH o->c , NQ RTH o->c)   = {rho_rth:+.4f}   [POINTS basis]")
    Lc.append(f"  rho(YM RTH close-close, NQ c-c)  = {rho_cc:+.4f}   [POINTS basis]")
    Lc.append(f"  NOTE: correlation is scale-invariant -> points-basis rho == dollar-basis rho "
              f"(YM ${YM_PV}/pt, NQ ${NQ_PV}/pt).")
    Lc.append("  per-year rho(YM,NQ) RTH o->c:")
    for y, r in yr_rho.items():
        Lc.append(f"    {y}: {r:+.4f}")
    Lc.append("")
    Lc.append("  STRUCTURAL CONTRAST (is YM a more mean-reverting regime than NQ?):")
    Lc.append(f"    daily RTH VR(q=5):  YM={ym_vr_daily:.4f}   NQ={nq_vr_daily:.4f}   "
              f"(both <1 => MR; lower = stronger)")
    Lc.append(f"    1-min VR(q=30):     YM={ym_vr_min:.4f}   NQ={nq_vr_min:.4f}")
    Lc.append(f"    RTH efficiency ratio median: YM={er.median():.4f}   NQ={nq_er_med:.4f} "
              f"(lower = choppier/more reversion)")
    corr_txt = "\n".join(Lc)

    # ============================ WRITE ============================
    lines_ret = lines_ret_extra + "\n"
    with open(os.path.join(OUT, "returns_summary.txt"), "w", encoding="utf-8") as f:
        f.write(lines_ret)
    with open(os.path.join(OUT, "distribution.txt"), "w", encoding="utf-8") as f:
        f.write(lines_dist + "\n")
    with open(os.path.join(OUT, "dependence.txt"), "w", encoding="utf-8") as f:
        f.write(lines_dep + "\n\n" + corr_txt + "\n")
    with open(os.path.join(OUT, "path.txt"), "w", encoding="utf-8") as f:
        f.write(lines_path + "\n")
    with open(os.path.join(OUT, "session.txt"), "w", encoding="utf-8") as f:
        f.write(lines_sess + "\n")

    # console echo (the return-value substance)
    print("\n" + lines_ret)
    print("\n" + lines_dist)
    print("\n" + lines_dep)
    print("\n" + lines_path)
    print("\n" + lines_sess)
    print("\n" + corr_txt)

    # machine digest for the schema
    print("\n===DIGEST_JSON===")
    import json
    digest = {
        "n_sessions_all": int(n_sess), "n_full_rth": int(n_full),
        "last_bar": str(ym["time"].max()),
        "rth_vol_share": rth_vol / total_vol, "eth_vol_share": eth_vol / total_vol,
        "rth_ret_mean": float(rth_mean), "rth_ret_sum": float(rth_sum),
        "on_ret_mean": float(on_mean), "on_ret_sum": float(on_sum),
        "min_ret_skew": float(stats.skew(bar_ret)), "min_ret_exkurt": float(stats.kurtosis(bar_ret)),
        "daily_cc_skew": float(stats.skew(dd)), "daily_cc_exkurt": float(stats.kurtosis(dd)),
        "ac_min_lag1": ac_min[0], "sign_persist_min": sp_m, "sign_persist_daily": sp_d,
        "vr_min_q30": variance_ratio(minr, 30)[0], "vr_daily_q5": variance_ratio(Dr["rth_ret"].values, 5)[0],
        "rth_er_median": float(er.median()), "gap_fill_rate": float(filled.mean()),
        "rho_ym_nq_rth": float(rho_rth), "rho_ym_nq_cc": float(rho_cc),
    }
    print(json.dumps(digest, indent=2))


if __name__ == "__main__":
    main()
