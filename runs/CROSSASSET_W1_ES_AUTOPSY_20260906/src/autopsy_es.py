"""
MARKET AUTOPSY — ES (E-mini S&P 500), point value 50.
Cross-asset Wave 1, per research/cross_asset/NQ_RESEARCH_PLAYBOOK.md §9 + transfer-checklist step 6.

DESCRIPTIVE SCIENCE (a market autopsy), NOT a falsifiable test. DISCOVERY_CONSUMED.
No strategy, no P&L, no ledger trial. Every number here is a phenotype measurement.

DISCIPLINE (hard rules, enforced in code):
  * POINTS BASIS ONLY. Substrate is additively back-adjusted (DELEV01 law): absolute levels are
    shifted, so every return/range/threshold is a POINT difference, never % of price, never a
    level threshold. Point diffs are invariant to additive back-adjustment within a continuous
    chain (roll gaps removed by construction).
  * NATIVE SESSION determined from ES's OWN volume/bar-count profile by minute-of-day; NOT assumed.
  * Hard-drop any bar/session >= 2026-08-01 at load; print the retained boundary.

Substrate: runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet  (1-min OHLCV, ET END-stamped)
NQ cross:  runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet     (PV 20) for daily rho pre-read.
"""
import os
import sys
import numpy as np
import pandas as pd
from datetime import timedelta

REPO = r"D:/OneDrive - Washington University in St. Louis/TradingResearch/systematic_research"
ES_PARQUET = os.path.join(REPO, "runs/SM1M_ES_SUBSTRATE/out/es_1m_2022_2026.parquet")
NQ_PARQUET = os.path.join(REPO, "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet")
OUT = os.path.join(REPO, "runs/CROSSASSET_W1_ES_AUTOPSY_20260906/out")
os.makedirs(OUT, exist_ok=True)

SEAL = pd.Timestamp("2026-08-01")  # hard-drop >= this (session-date basis)
ES_PV = 50.0
NQ_PV = 20.0

# RTH window (ET). Bars are END-stamped: bar stamped 09:31 opens 09:30. So the RTH open price is
# the OPEN of the bar stamped 09:31 (opens 09:30); RTH close is the CLOSE of the bar stamped 16:00.
RTH_FIRST_STAMP = (9, 31)   # first RTH minute end-stamp (opens 09:30)
RTH_LAST_STAMP = (16, 0)    # last RTH minute end-stamp (closes 16:00)


def log(msg):
    print(msg, flush=True)


def session_date(ts_series):
    """runlib convention: sessions 18:00 ET (prior day) -> 17:00 ET; hour>=18 rolls to next
    calendar day; weekend evening opens roll forward to Monday. Vectorized."""
    d = ts_series.dt.normalize()
    roll = ts_series.dt.hour >= 18
    d = d + pd.to_timedelta(roll.astype(int), unit="D")
    # roll Sat/Sun forward to Monday
    for _ in range(3):
        wd = d.dt.weekday
        mask = wd >= 5
        if not mask.any():
            break
        d = d + pd.to_timedelta(mask.astype(int), unit="D")
    return d.dt.normalize()


def load(parquet, label):
    df = pd.read_parquet(parquet)
    df["time"] = pd.to_datetime(df["time"])
    n_raw = len(df)
    raw_last = df["time"].max()
    df["sess"] = session_date(df["time"])
    # HARD DROP >= seal on session basis (defensive; also drop by raw time)
    before = len(df)
    df = df[(df["sess"] < SEAL) & (df["time"] < SEAL)].copy()
    dropped = before - len(df)
    df = df.sort_values("time").reset_index(drop=True)
    df["mod"] = df["time"].dt.hour * 60 + df["time"].dt.minute  # minute-of-day (END stamp)
    log(f"[{label}] raw rows={n_raw} raw_last={raw_last}  dropped>=SEAL={dropped}  "
        f"retained rows={len(df)}")
    log(f"[{label}] retained sessions: {df['sess'].min().date()} .. {df['sess'].max().date()}  "
        f"n_sessions={df['sess'].nunique()}")
    return df


def minute_label(mod):
    return f"{mod // 60:02d}:{mod % 60:02d}"


# ----------------------------------------------------------------------------------------------
# SESSION / NATIVE-SESSION PROFILE
# ----------------------------------------------------------------------------------------------
def volume_profile(df, label, fh):
    """Bar-count & volume by minute-of-day to DETERMINE the native session (not assume it)."""
    g = df.groupby("mod").agg(n_bars=("volume", "size"), tot_vol=("volume", "sum"),
                              med_vol=("volume", "median")).reset_index()
    g["clock"] = g["mod"].map(minute_label)
    # Aggregate to 30-min buckets for the printed profile
    df2 = df.copy()
    df2["b30"] = (df2["mod"] // 30) * 30
    b = df2.groupby("b30").agg(n_bars=("volume", "size"), tot_vol=("volume", "sum")).reset_index()
    b["clock"] = b["b30"].map(minute_label)
    b["vol_share_%"] = 100 * b["tot_vol"] / b["tot_vol"].sum()
    fh.write(f"=== {label} VOLUME / BAR-COUNT PROFILE by 30-min bucket (ET, END-stamp) ===\n")
    fh.write("Determines the NATIVE session from the market's own activity, not an assumption.\n\n")
    fh.write(b[["clock", "n_bars", "tot_vol", "vol_share_%"]].to_string(index=False,
             formatters={"vol_share_%": lambda x: f"{x:5.2f}"}))
    fh.write("\n\n")
    # identify the continuous active span and the RTH core
    active = g[g["n_bars"] > 0]
    fh.write(f"Active minutes present: {len(active)} distinct minute-of-day stamps "
             f"(out of 1440).\n")
    # coverage per minute: fraction of sessions that have this minute
    nsess = df["sess"].nunique()
    g["coverage"] = g["n_bars"] / nsess
    dense = g[g["coverage"] >= 0.5].sort_values("mod")
    if len(dense):
        fh.write(f"Minutes present in >=50% of sessions span {minute_label(dense['mod'].min())} "
                 f"to {minute_label(dense['mod'].max())} (END-stamp).\n")
    # RTH-core volume share
    rth_mask = (df["mod"] > (9 * 60 + 30)) & (df["mod"] <= (16 * 60))
    rth_share = 100 * df.loc[rth_mask, "volume"].sum() / df["volume"].sum()
    fh.write(f"RTH core (09:30-16:00 ET) carries {rth_share:.1f}% of total volume "
             f"({rth_mask.mean()*100:.1f}% of bars).\n")
    # halt window 17:00-18:00
    halt_mask = (df["mod"] > 17 * 60) & (df["mod"] < 18 * 60)
    fh.write(f"Maintenance window 17:00-18:00 ET bar-count = {int(halt_mask.sum())} "
             f"(near-zero confirms the ETH break).\n\n")
    return b, rth_share


# ----------------------------------------------------------------------------------------------
# BUILD PER-SESSION FRAME (RTH open/high/low/close, overnight gap, ranges) -- points basis
# ----------------------------------------------------------------------------------------------
def per_session(df):
    rmin = RTH_FIRST_STAMP[0] * 60 + RTH_FIRST_STAMP[1]   # 571
    rmax = RTH_LAST_STAMP[0] * 60 + RTH_LAST_STAMP[1]      # 960
    rth = df[(df["mod"] >= rmin) & (df["mod"] <= rmax)].copy()
    rows = []
    for sess, gg in rth.groupby("sess"):
        gg = gg.sort_values("time")
        rows.append({
            "sess": sess,
            "rth_open": gg["open"].iloc[0],       # opens 09:30
            "rth_close": gg["close"].iloc[-1],    # closes 16:00
            "rth_high": gg["high"].max(),
            "rth_low": gg["low"].min(),
            "rth_nbars": len(gg),
        })
    ps = pd.DataFrame(rows).sort_values("sess").reset_index(drop=True)
    ps = ps[ps["rth_nbars"] >= 300]  # drop half-day/holiday shells (full RTH ~ 390 bars)
    ps["rth_ret"] = ps["rth_close"] - ps["rth_open"]                 # intraday (session) pt return
    ps["rth_range"] = ps["rth_high"] - ps["rth_low"]                 # intraday range (pt)
    ps["prev_close"] = ps["rth_close"].shift(1)
    ps["gap"] = ps["rth_open"] - ps["prev_close"]                    # overnight gap / ON return (pt)
    ps["prev_rth_ret"] = ps["rth_ret"].shift(1)
    ps["full_ret"] = ps["rth_close"] - ps["prev_close"]             # prev close -> today close (pt)
    return ps, rmin, rmax


def overnight_ranges(df, ps):
    """Overnight = prior RTH close (16:00) to today RTH open (09:30). Range over that span."""
    # bars that are NOT in RTH belong to the overnight/eth segment of their session
    rmin = RTH_FIRST_STAMP[0] * 60 + RTH_FIRST_STAMP[1]
    on = df[df["mod"] < rmin].copy()   # 18:00(prev)..09:30 of the session (end-stamp < 09:31)
    # careful: bars 16:01..17:00 and 18:01.. belong to session's overnight too; mod<571 covers
    # everything before 09:31, i.e. 00:00-09:30 AND (via session roll) the 18:00-24:00 block that
    # was rolled to this session. Both have mod<571? No: 18:00-24:00 has mod>=1080. Need both.
    on = df[(df["mod"] < rmin) | (df["mod"] >= 18 * 60) | (df["mod"] > 16 * 60)].copy()
    # Simpler & exact: overnight = all bars of the session EXCEPT the RTH window.
    rmax = RTH_LAST_STAMP[0] * 60 + RTH_LAST_STAMP[1]
    on = df[~((df["mod"] >= rmin) & (df["mod"] <= rmax))].copy()
    agg = on.groupby("sess").agg(on_high=("high", "max"), on_low=("low", "min"),
                                 on_nbars=("volume", "size")).reset_index()
    agg["on_range"] = agg["on_high"] - agg["on_low"]
    return agg


# ----------------------------------------------------------------------------------------------
# RETURNS
# ----------------------------------------------------------------------------------------------
def returns_by_tod(df, fh_csv_path):
    d = df.copy()
    d["ret"] = d["close"].diff()
    d.loc[d["sess"] != d["sess"].shift(1), "ret"] = np.nan  # no return across session boundary
    d = d.dropna(subset=["ret"])
    d["b30"] = (d["mod"] // 30) * 30
    g = d.groupby("b30").agg(n=("ret", "size"), mean_pt=("ret", "mean"), std_pt=("ret", "std"),
                             sum_pt=("ret", "sum")).reset_index()
    g["clock"] = g["b30"].map(minute_label)
    g["tstat"] = g["mean_pt"] / (g["std_pt"] / np.sqrt(g["n"]))
    g = g[["clock", "b30", "n", "mean_pt", "std_pt", "sum_pt", "tstat"]]
    g.to_csv(fh_csv_path, index=False, float_format="%.5f")
    return g


def returns_section(df, ps, onr, fh):
    fh.write("=== RETURNS (points basis; PV=$50/pt) ===\n\n")

    # by day-of-week
    ps2 = ps.copy()
    ps2["dow"] = pd.to_datetime(ps2["sess"]).dt.day_name()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    dw = ps2.groupby("dow").agg(n=("rth_ret", "size"), rth_mean=("rth_ret", "mean"),
                                rth_std=("rth_ret", "std"), gap_mean=("gap", "mean"),
                                gap_std=("gap", "std")).reindex(order)
    fh.write("--- RTH session return & overnight gap by day-of-week (pt) ---\n")
    fh.write(dw.to_string(float_format=lambda x: f"{x:8.3f}"))
    fh.write("\n\n")

    # session vs overnight decomposition
    fh.write("--- SESSION vs OVERNIGHT decomposition (pt) ---\n")
    rr = ps["rth_ret"].dropna()
    gg = ps["gap"].dropna()
    ff = ps["full_ret"].dropna()
    for name, s in [("RTH (09:30->16:00)", rr), ("Overnight gap (16:00->09:30)", gg),
                    ("Full (prevClose->close)", ff)]:
        fh.write(f"{name:32s} n={len(s):4d} mean={s.mean():8.3f} std={s.std():8.3f} "
                 f"sum={s.sum():10.1f} t={s.mean()/(s.std()/np.sqrt(len(s))):6.2f}\n")
    tot_abs = rr.abs().sum() + gg.abs().sum()
    fh.write(f"Share of gross absolute move: RTH={100*rr.abs().sum()/tot_abs:.1f}%  "
             f"overnight={100*gg.abs().sum()/tot_abs:.1f}%\n")
    fh.write(f"Directional drift split: sum(RTH)={rr.sum():.1f}pt  sum(overnight)={gg.sum():.1f}pt "
             f"(where does the trend live?)\n\n")

    # conditional on prior-day sign
    fh.write("--- CONDITIONAL EXPECTANCY: continuation vs reversal (pt) ---\n")
    p = ps.dropna(subset=["prev_rth_ret", "rth_ret", "gap"]).copy()
    for cond_name, cond in [("prior RTH up", p["prev_rth_ret"] > 0),
                            ("prior RTH down", p["prev_rth_ret"] < 0)]:
        sub = p[cond]
        fh.write(f"E[RTH ret | {cond_name:14s}] = {sub['rth_ret'].mean():7.3f}  "
                 f"E[gap | {cond_name:14s}] = {sub['gap'].mean():7.3f}  n={len(sub)}\n")
    fh.write("\n")
    for cond_name, cond in [("gap up", p["gap"] > 0), ("gap down", p["gap"] < 0)]:
        sub = p[cond]
        fh.write(f"E[RTH ret | {cond_name:14s}] = {sub['rth_ret'].mean():7.3f}  n={len(sub)}  "
                 f"(gap-fill vs gap-go)\n")
    # overnight sign -> RTH
    fh.write("\ncorr(prev RTH ret, gap)        = %.3f  (overnight continuation of the day move)\n"
             % p["prev_rth_ret"].corr(p["gap"]))
    fh.write("corr(gap, RTH ret same day)    = %.3f  (open drive persistence within RTH)\n"
             % p["gap"].corr(p["rth_ret"]))
    fh.write("corr(prev RTH ret, RTH ret)    = %.3f  (day-to-day RTH continuation)\n\n"
             % p["prev_rth_ret"].corr(p["rth_ret"]))


# ----------------------------------------------------------------------------------------------
# DISTRIBUTION
# ----------------------------------------------------------------------------------------------
def distribution_section(df, ps, onr, fh):
    from scipy import stats
    fh.write("=== DISTRIBUTION (points basis) ===\n\n")

    # 1-min returns within-session
    d = df.copy()
    d["ret"] = d["close"].diff()
    d.loc[d["sess"] != d["sess"].shift(1), "ret"] = np.nan
    r1 = d["ret"].dropna()
    fh.write("--- 1-min close-to-close return (within session) ---\n")
    fh.write(f"n={len(r1)} mean={r1.mean():.4f} std={r1.std():.4f} skew={stats.skew(r1):.3f} "
             f"exkurt={stats.kurtosis(r1):.2f}\n")
    qs = [0.001, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999]
    fh.write("quantiles(pt): " + "  ".join(f"{int(q*1000)/10}%={r1.quantile(q):.2f}" for q in qs) + "\n")
    for k in [2, 3, 5, 8]:
        fr = (r1.abs() > k).mean()
        fh.write(f"P(|1-min move| > {k}pt) = {fr*100:.3f}%  (~1 per {1/fr:.0f} bars)\n" if fr > 0
                 else f"P(|1-min move| > {k}pt) = 0\n")
    fh.write("\n")

    # daily RTH / overnight / gap
    fh.write("--- daily distributions (pt) ---\n")
    for name, s in [("RTH session ret", ps["rth_ret"].dropna()),
                    ("overnight gap", ps["gap"].dropna()),
                    ("full-day ret", ps["full_ret"].dropna())]:
        fh.write(f"{name:16s} n={len(s):4d} mean={s.mean():7.3f} std={s.std():7.3f} "
                 f"skew={stats.skew(s):6.3f} exkurt={stats.kurtosis(s):6.2f} "
                 f"min={s.min():8.2f} max={s.max():8.2f}\n")
    fh.write("\n")

    # gap distribution detail
    g = ps["gap"].dropna()
    fh.write("--- gap (overnight) distribution ---\n")
    fh.write(f"|gap| mean={g.abs().mean():.3f}pt median={g.abs().median():.3f}pt  "
             f"P(gap up)={100*(g>0).mean():.1f}%  P(|gap|>10pt)={100*(g.abs()>10).mean():.1f}%\n")
    fh.write("gap quantiles(pt): " + "  ".join(f"{int(q*100)}%={g.quantile(q):.2f}"
             for q in [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]) + "\n\n")

    # intraday vs overnight range
    m = ps.merge(onr, on="sess", how="left")
    fh.write("--- range: intraday (RTH) vs overnight (pt) ---\n")
    fh.write(f"RTH range      mean={m['rth_range'].mean():.2f} median={m['rth_range'].median():.2f} "
             f"p95={m['rth_range'].quantile(.95):.2f}\n")
    fh.write(f"overnight range mean={m['on_range'].mean():.2f} median={m['on_range'].median():.2f} "
             f"p95={m['on_range'].quantile(.95):.2f}\n")
    fh.write(f"overnight/RTH range ratio (median) = {(m['on_range']/m['rth_range']).median():.2f}\n\n")

    # realized vol per year (RTH), points
    d2 = d.dropna(subset=["ret"]).copy()
    rmin = RTH_FIRST_STAMP[0]*60+RTH_FIRST_STAMP[1]; rmax = RTH_LAST_STAMP[0]*60+RTH_LAST_STAMP[1]
    rthb = d2[(d2["mod"] >= rmin) & (d2["mod"] <= rmax)].copy()
    rv = rthb.groupby("sess")["ret"].apply(lambda x: np.sqrt((x**2).sum()))  # daily RTH RV (pt)
    rv = rv.reset_index(name="rv")
    rv["yr"] = pd.to_datetime(rv["sess"]).dt.year
    fh.write("--- realized vol: daily RTH RV = sqrt(sum sq 1-min ret), pt, by year ---\n")
    fh.write(rv.groupby("yr")["rv"].agg(["count", "mean", "median", "max"]).to_string(
             float_format=lambda x: f"{x:8.2f}"))
    fh.write("\n\n")

    # extreme move frequency by year (RTH range > threshold)
    m["yr"] = pd.to_datetime(m["sess"]).dt.year
    fh.write("--- extreme-day frequency: |RTH ret| by year (pt) ---\n")
    ex = m.groupby("yr")["rth_ret"].agg(n="size",
            p_big=lambda x: 100*(x.abs() > 60).mean(),
            worst=lambda x: x.min(), best=lambda x: x.max())
    fh.write(ex.to_string(float_format=lambda x: f"{x:8.2f}"))
    fh.write("\n(P(|RTH ret|>60pt) shown as %.)\n\n")
    return rv


# ----------------------------------------------------------------------------------------------
# DEPENDENCE
# ----------------------------------------------------------------------------------------------
def dependence_section(df, ps, rv, fh):
    fh.write("=== DEPENDENCE (points basis) ===\n\n")
    d = df.copy()
    d["ret"] = d["close"].diff()
    d.loc[d["sess"] != d["sess"].shift(1), "ret"] = np.nan
    rmin = RTH_FIRST_STAMP[0]*60+RTH_FIRST_STAMP[1]; rmax = RTH_LAST_STAMP[0]*60+RTH_LAST_STAMP[1]
    rthb = d[(d["mod"] >= rmin) & (d["mod"] <= rmax)].dropna(subset=["ret"]).copy()
    r = rthb["ret"].values

    # 1-min autocorrelation
    fh.write("--- 1-min RTH return autocorrelation (all lags on stacked series) ---\n")
    def acf(x, lag):
        x = x - x.mean()
        return np.sum(x[:-lag]*x[lag:]) / np.sum(x*x)
    for lag in [1, 2, 3, 5, 10, 30]:
        fh.write(f"  acf(lag={lag:3d}) = {acf(r, lag):+.4f}\n")
    # sign persistence 1-min
    s = np.sign(r); s = s[s != 0]
    same = (s[1:] == s[:-1]).mean()
    fh.write(f"1-min sign persistence P(same sign next) = {same*100:.2f}% "
             f"(50% = no persistence)\n\n")

    # variance ratio on 1-min RTH returns
    fh.write("--- variance ratio VR(q)=Var(q-sum)/(q*Var(1)) on 1-min RTH returns ---\n")
    fh.write("    VR<1 = mean-reversion / anti-persistence ; VR>1 = trending\n")
    rr = r.copy()
    var1 = np.var(rr)
    for q in [2, 5, 10, 30, 60]:
        cs = np.cumsum(rr)
        qsum = cs[q:] - cs[:-q]
        vr = np.var(qsum) / (q * var1)
        fh.write(f"  VR({q:3d}) = {vr:.3f}\n")
    fh.write("\n")

    # daily RTH return dependence
    dr = ps["rth_ret"].dropna().values
    fh.write("--- daily RTH return dependence ---\n")
    for lag in [1, 2, 3, 5]:
        fh.write(f"  acf(lag={lag}) = {acf(dr, lag):+.4f}\n")
    sd = np.sign(dr); sd = sd[sd != 0]
    fh.write(f"daily sign persistence P(same sign next) = {(sd[1:]==sd[:-1]).mean()*100:.2f}%\n")
    # daily variance ratio
    fh.write("daily VR: ")
    var1d = np.var(dr)
    for q in [2, 3, 5, 10]:
        cs = np.cumsum(dr); qs_ = cs[q:] - cs[:-q]
        fh.write(f"VR({q})={np.var(qs_)/(q*var1d):.3f}  ")
    fh.write("\n\n")

    # vol autocorrelation (abs 1-min ret and daily RV)
    fh.write("--- volatility autocorrelation ---\n")
    ar = np.abs(r)
    for lag in [1, 5, 30, 390]:
        fh.write(f"  |1-min ret| acf(lag={lag:3d}) = {acf(ar, lag):+.4f}\n")
    rvv = rv["rv"].values
    for lag in [1, 2, 5, 10]:
        fh.write(f"  daily RV acf(lag={lag:2d})     = {acf(rvv, lag):+.4f}\n")
    fh.write("\n")

    # conditional continuation vs reversal after a large 1-min move
    fh.write("--- conditional next-move after a LARGE 1-min move (RTH), pt ---\n")
    thr = np.quantile(np.abs(r), 0.99)
    fh.write(f"(large = |move| > 99th pct = {thr:.2f}pt)\n")
    idx = np.where(np.abs(r[:-1]) > thr)[0]
    nxt = r[idx + 1]
    prev = r[idx]
    cont = np.sign(nxt) == np.sign(prev)
    fh.write(f"  n large moves={len(idx)}  E[next same-dir move]={np.mean(nxt*np.sign(prev)):+.4f}pt "
             f"P(continue)={100*cont.mean():.1f}%\n")
    # small-move baseline
    idx2 = np.where(np.abs(r[:-1]) <= thr)[0]
    nxt2 = r[idx2 + 1]; prev2 = r[idx2]
    fh.write(f"  baseline (small moves): E[next same-dir]={np.mean(nxt2*np.sign(prev2)):+.4f}pt "
             f"P(continue)={100*(np.sign(nxt2)==np.sign(prev2)).mean():.1f}%\n\n")


# ----------------------------------------------------------------------------------------------
# PATH
# ----------------------------------------------------------------------------------------------
def path_section(df, ps, fh):
    fh.write("=== PATH GEOMETRY (points basis) ===\n\n")
    rmin = RTH_FIRST_STAMP[0]*60+RTH_FIRST_STAMP[1]; rmax = RTH_LAST_STAMP[0]*60+RTH_LAST_STAMP[1]
    rth = df[(df["mod"] >= rmin) & (df["mod"] <= rmax)].copy()
    recs = []
    for sess, gg in rth.groupby("sess"):
        gg = gg.sort_values("time")
        if len(gg) < 300:
            continue
        c = gg["close"].values
        o = gg["open"].iloc[0]
        step = np.abs(np.diff(c))
        pathlen = step.sum()
        disp = abs(c[-1] - o)
        er = disp / pathlen if pathlen > 0 else np.nan   # Kaufman efficiency ratio
        mfe = gg["high"].max() - o    # max favorable excursion for a long-from-open
        mae = o - gg["low"].min()     # max adverse excursion for a long-from-open
        recs.append({"sess": sess, "er": er, "tortuosity": pathlen/disp if disp > 0 else np.nan,
                     "pathlen": pathlen, "disp": c[-1]-o, "mfe": mfe, "mae": mae,
                     "rng": gg["high"].max()-gg["low"].min()})
    pa = pd.DataFrame(recs)
    fh.write("--- Kaufman efficiency ratio ER = |net| / sum|bar step|, per RTH session ---\n")
    fh.write(f"ER  mean={pa['er'].mean():.3f} median={pa['er'].median():.3f} "
             f"p25={pa['er'].quantile(.25):.3f} p75={pa['er'].quantile(.75):.3f}\n")
    fh.write("(low ER = choppy/mean-reverting path; high ER = directional/trending day)\n\n")
    fh.write("--- tortuosity = pathlen/|displacement| (inverse ER, capped view) ---\n")
    t = pa["tortuosity"].replace([np.inf, -np.inf], np.nan).dropna()
    fh.write(f"tortuosity median={t.median():.2f} p90={t.quantile(.90):.2f}\n\n")
    fh.write("--- MFE/MAE from RTH open (excursions, pt; 'long-from-open' framing) ---\n")
    fh.write(f"MFE mean={pa['mfe'].mean():.2f} median={pa['mfe'].median():.2f} "
             f"p95={pa['mfe'].quantile(.95):.2f}\n")
    fh.write(f"MAE mean={pa['mae'].mean():.2f} median={pa['mae'].median():.2f} "
             f"p95={pa['mae'].quantile(.95):.2f}\n")
    fh.write(f"MFE/MAE ratio (median) = {(pa['mfe']/pa['mae'].replace(0,np.nan)).median():.2f}\n")
    fh.write(f"net displacement mean={pa['disp'].mean():.2f} vs range mean={pa['rng'].mean():.2f} "
             f"-> captured fraction of range = {pa['disp'].abs().mean()/pa['rng'].mean():.2f}\n\n")

    # compression/expansion: range autocorrelation & NR-style clustering
    fh.write("--- compression / expansion (range clustering) ---\n")
    pa = pa.sort_values("sess").reset_index(drop=True)
    def acf1(x, lag):
        x = x - np.mean(x); return np.sum(x[:-lag]*x[lag:])/np.sum(x*x)
    for lag in [1, 2, 5]:
        fh.write(f"  RTH range acf(lag={lag}) = {acf1(pa['rng'].values, lag):+.3f}\n")
    # NR7: today's range is the narrowest of last 7; does an expansion follow?
    rng = pa["rng"].values
    nr7 = np.array([rng[i] == rng[max(0, i-6):i+1].min() for i in range(len(rng))])
    nxt_rng = np.append(rng[1:], np.nan)
    exp_after_nr7 = np.nanmean(nxt_rng[nr7]) / np.nanmean(rng)
    exp_after_oth = np.nanmean(nxt_rng[~nr7]) / np.nanmean(rng)
    fh.write(f"  next-day range after NR7 = {exp_after_nr7:.2f}x avg  vs after non-NR7 = "
             f"{exp_after_oth:.2f}x avg  (n_nr7={int(nr7.sum())})\n\n")
    return pa


# ----------------------------------------------------------------------------------------------
# SESSION STRUCTURE
# ----------------------------------------------------------------------------------------------
def session_structure_section(df, ps, onr, fh):
    fh.write("=== SESSION STRUCTURE (descriptive, points basis) ===\n\n")
    m = ps.merge(onr, on="sess", how="left").sort_values("sess").reset_index(drop=True)

    # overnight high/low taken out during RTH
    on_high_broken = (m["rth_high"] > m["on_high"]).mean()
    on_low_broken = (m["rth_low"] < m["on_low"]).mean()
    fh.write("--- overnight high/low behavior during RTH ---\n")
    fh.write(f"P(RTH takes out overnight HIGH) = {100*on_high_broken:.1f}%\n")
    fh.write(f"P(RTH takes out overnight LOW)  = {100*on_low_broken:.1f}%\n")
    fh.write(f"P(RTH takes out BOTH on/night extremes) = "
             f"{100*((m['rth_high']>m['on_high'])&(m['rth_low']<m['on_low'])).mean():.1f}%\n")
    fh.write(f"P(RTH stays INSIDE overnight range) = "
             f"{100*((m['rth_high']<=m['on_high'])&(m['rth_low']>=m['on_low'])).mean():.1f}%\n\n")

    # opening range (first 15/30/60 min of RTH)
    rmin = RTH_FIRST_STAMP[0]*60+RTH_FIRST_STAMP[1]
    rth = df[(df["mod"] >= rmin) & (df["mod"] <= RTH_LAST_STAMP[0]*60+RTH_LAST_STAMP[1])].copy()
    fh.write("--- opening range (OR), pt ---\n")
    for win in [15, 30, 60]:
        recs = []
        for sess, gg in rth.groupby("sess"):
            gg = gg.sort_values("time")
            if len(gg) < 300:
                continue
            orb = gg.iloc[:win]
            hi, lo = orb["high"].max(), orb["low"].min()
            rest = gg.iloc[win:]
            if len(rest) == 0:
                continue
            broke_up = rest["high"].max() > hi
            broke_dn = rest["low"].min() < lo
            recs.append({"or_range": hi-lo, "broke_up": broke_up, "broke_dn": broke_dn,
                         "day_high_in_or": gg["high"].idxmax() in orb.index,
                         "day_low_in_or": gg["low"].idxmin() in orb.index})
        rr = pd.DataFrame(recs)
        fh.write(f"OR{win:>2}min: range mean={rr['or_range'].mean():.2f}pt median="
                 f"{rr['or_range'].median():.2f}  P(break up later)={100*rr['broke_up'].mean():.1f}% "
                 f"P(break dn later)={100*rr['broke_dn'].mean():.1f}%  "
                 f"P(day-high in OR)={100*rr['day_high_in_or'].mean():.1f}% "
                 f"P(day-low in OR)={100*rr['day_low_in_or'].mean():.1f}%\n")
    fh.write("\n")

    # gap behavior / gap fill during RTH
    fh.write("--- gap behavior (pt) ---\n")
    g = m.dropna(subset=["gap", "prev_close"]).copy()
    # gap fill = price trades back to prev_close during RTH
    filled = ((g["gap"] > 0) & (g["rth_low"] <= g["prev_close"])) | \
             ((g["gap"] < 0) & (g["rth_high"] >= g["prev_close"]))
    fh.write(f"P(gap fills to prior close during RTH) = {100*filled.mean():.1f}%\n")
    up = g[g["gap"] > 2]; dn = g[g["gap"] < -2]
    fh.write(f"  gap-up (>2pt)  n={len(up)}  fill%={100*(up['rth_low']<=up['prev_close']).mean():.1f}  "
             f"E[RTH ret]={up['rth_ret'].mean():.2f}\n")
    fh.write(f"  gap-dn (<-2pt) n={len(dn)}  fill%={100*(dn['rth_high']>=dn['prev_close']).mean():.1f} "
             f"E[RTH ret]={dn['rth_ret'].mean():.2f}\n\n")

    # prior-day levels
    m["prev_high"] = m["rth_high"].shift(1); m["prev_low"] = m["rth_low"].shift(1)
    mm = m.dropna(subset=["prev_high", "prev_low"])
    fh.write("--- prior-day RTH level interaction ---\n")
    fh.write(f"P(today RTH touches prior-day HIGH) = "
             f"{100*(mm['rth_high']>=mm['prev_high']).mean():.1f}%\n")
    fh.write(f"P(today RTH touches prior-day LOW)  = "
             f"{100*(mm['rth_low']<=mm['prev_low']).mean():.1f}%\n")
    fh.write(f"P(today's RTH range engulfs prior-day range) = "
             f"{100*((mm['rth_high']>=mm['prev_high'])&(mm['rth_low']<=mm['prev_low'])).mean():.1f}%\n\n")


# ----------------------------------------------------------------------------------------------
# NQ CORRELATION (diversification pre-read)
# ----------------------------------------------------------------------------------------------
def nq_correlation(es_ps, fh):
    nq = load(NQ_PARQUET, "NQ")
    nq_ps, _, _ = per_session(nq)
    a = es_ps[["sess", "rth_ret", "gap", "full_ret"]].rename(
        columns={"rth_ret": "es_rth", "gap": "es_gap", "full_ret": "es_full"})
    b = nq_ps[["sess", "rth_ret", "gap", "full_ret"]].rename(
        columns={"rth_ret": "nq_rth", "gap": "nq_gap", "full_ret": "nq_full"})
    m = a.merge(b, on="sess", how="inner").dropna()
    fh.write("=== NQ CORRELATION (diversification pre-read; points-return basis) ===\n\n")
    fh.write(f"shared sessions n={len(m)}  ({m['sess'].min().date()}..{m['sess'].max().date()})\n\n")
    fh.write("Pearson rho on POINT returns (ES pt vs NQ pt; NOT dollar, NOT %):\n")
    fh.write(f"  RTH session return   rho = {m['es_rth'].corr(m['nq_rth']):.3f}\n")
    fh.write(f"  overnight gap        rho = {m['es_gap'].corr(m['nq_gap']):.3f}\n")
    fh.write(f"  full-day return      rho = {m['es_full'].corr(m['nq_full']):.3f}\n\n")
    # rank corr too
    fh.write(f"  RTH Spearman rho     = {m['es_rth'].corr(m['nq_rth'], method='spearman'):.3f}\n")
    # per-year
    m["yr"] = pd.to_datetime(m["sess"]).dt.year
    fh.write("\nRTH rho by year:\n")
    for yr, gg in m.groupby("yr"):
        if len(gg) > 20:
            fh.write(f"  {yr}: rho={gg['es_rth'].corr(gg['nq_rth']):.3f}  n={len(gg)}\n")
    # dollar-scaled interpretation note
    fh.write("\nNote: ES PV=$50, NQ PV=$20. Correlation is scale-free; the diversification verdict\n")
    fh.write("is that ES and NQ are the SAME equity-index factor -- a high rho here means an ES\n")
    fh.write("engine that merely re-expresses index direction adds little to the NQ book.\n\n")
    return m['es_rth'].corr(m['nq_rth']), len(m)


# ----------------------------------------------------------------------------------------------
def main():
    log("MARKET AUTOPSY — ES (E-mini S&P 500, PV=$50). DESCRIPTIVE / DISCOVERY_CONSUMED.")
    es = load(ES_PARQUET, "ES")
    ps, rmin, rmax = per_session(es)
    onr = overnight_ranges(es, ps)
    log(f"per-session frame: {len(ps)} full RTH sessions (>=300 bars); "
        f"RTH stamps [{minute_label(rmin)},{minute_label(rmax)}]")

    # session.txt (native session + structure)
    with open(os.path.join(OUT, "session.txt"), "w") as fh:
        fh.write("ES MARKET AUTOPSY — SESSION STRUCTURE & NATIVE-SESSION DETERMINATION\n")
        fh.write("="*78 + "\n")
        fh.write(f"Retained boundary: sessions < {SEAL.date()} (>=2026-08-01 hard-dropped).\n")
        fh.write(f"Data span: {es['sess'].min().date()} .. {es['sess'].max().date()}  "
                 f"n_full_RTH_sessions={len(ps)}\n\n")
        _, rth_share = volume_profile(es, "ES", fh)
        session_structure_section(es, ps, onr, fh)
    log("wrote session.txt")

    with open(os.path.join(OUT, "distribution.txt"), "w") as fh:
        fh.write("ES MARKET AUTOPSY — DISTRIBUTION\n" + "="*78 + "\n\n")
        rv = distribution_section(es, ps, onr, fh)
    log("wrote distribution.txt")

    with open(os.path.join(OUT, "dependence.txt"), "w") as fh:
        fh.write("ES MARKET AUTOPSY — DEPENDENCE\n" + "="*78 + "\n\n")
        dependence_section(es, ps, rv, fh)
    log("wrote dependence.txt")

    with open(os.path.join(OUT, "path.txt"), "w") as fh:
        fh.write("ES MARKET AUTOPSY — PATH GEOMETRY\n" + "="*78 + "\n\n")
        path_section(es, ps, fh)
    log("wrote path.txt")

    # returns.txt + returns_by_tod.csv
    g_tod = returns_by_tod(es, os.path.join(OUT, "returns_by_tod.csv"))
    with open(os.path.join(OUT, "returns.txt"), "w") as fh:
        fh.write("ES MARKET AUTOPSY — RETURNS\n" + "="*78 + "\n\n")
        fh.write("(full 30-min time-of-day table in returns_by_tod.csv)\n\n")
        # embed a compact ToD view: top movers by |mean| and the RTH open/close buckets
        fh.write("--- time-of-day 1-min mean point return, selected buckets (ET) ---\n")
        show = g_tod[g_tod["clock"].isin(["09:30", "09:00", "10:00", "15:30", "15:00", "16:00",
                                          "18:00", "03:00", "08:00", "09:29"])]
        fh.write(g_tod.to_string(index=False, float_format=lambda x: f"{x:.5f}",
                 max_rows=60))
        fh.write("\n\n")
        returns_section(es, ps, onr, fh)
    log("wrote returns.txt + returns_by_tod.csv")

    # NQ correlation appended into returns.txt tail file + its own note
    with open(os.path.join(OUT, "nq_correlation.txt"), "w") as fh:
        rho, nshared = nq_correlation(ps, fh)
    log(f"wrote nq_correlation.txt  rho_rth={rho:.3f} n={nshared}")

    log("DONE.")


if __name__ == "__main__":
    main()
