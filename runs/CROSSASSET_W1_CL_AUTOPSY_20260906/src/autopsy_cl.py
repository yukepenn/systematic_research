"""
MARKET AUTOPSY -- CL (NYMEX WTI light-sweet crude oil future, point value $1,000/pt = $10/tick).

Cross-asset campaign Wave 1, descriptive science (Lane B / NQ_RESEARCH_PLAYBOOK.md sec.9).
This is DESCRIPTIVE SCIENCE, NOT a falsifiable test: no ledger trial, no strategy, no P&L.
Evidence status: DISCOVERY_CONSUMED.

HARD DISCIPLINE (enforced in code):
  * FREEZE: CL discovery window is 2022-01-03 -> 2025-06-30 ONLY. The loader HARD-DROPS every
    session > 2025-06-30 and ASSERTS max session <= 2025-06-30. The frozen holdout
    (2025-07-01 -> 2026-07-31) and global virgin (>= 2026-08-01) are NEVER read.
    (runs/CL_HOLDOUT_FREEZE_20260906/SPEC.md)
  * POINTS BASIS ONLY. Substrate is additively back-adjusted continuous front-month (DELEV01 law):
    absolute price LEVELS are shifted, so every return / range / threshold is a POINT difference,
    never a percent of price and never a level threshold. Point diffs are invariant to additive
    back-adjustment (intraday continuity verified clean at build; roll gaps removed).
    Context: CL point value = $1,000/pt ($10/tick, tick $0.01) -- a "point" is a $1 oil move.
  * NATIVE SESSION determined from CL's OWN volume profile by clock-minute -- NEVER assumed to be
    NQ 09:30-16:00. CL (NYMEX energy) trades ~Sun 18:00 -> Fri 17:00 ET, maintenance 17:00-18:00.
  * Bars are END-stamped ET. Session (trade date) 18:00 ET -> 17:00 ET next day: a bar with
    hour >= 18 belongs to the NEXT calendar day's trade date.

Substrate:
  CL: runs/SM1M_CL_SUBSTRATE/out/cl_1m_2022_2026.parquet   (OHLCV, ET END-stamped, tick $0.01)
  NQ: runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet       (PV $20) -- for daily rho pre-read only
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
from scipy import stats

pd.options.mode.chained_assignment = None

ROOT = r"D:/OneDrive - Washington University in St. Louis/TradingResearch/systematic_research"
CL_PARQUET = os.path.join(ROOT, "runs/SM1M_CL_SUBSTRATE/out/cl_1m_2022_2026.parquet")
NQ_PARQUET = os.path.join(ROOT, "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet")
OUT = os.path.join(ROOT, "runs/CROSSASSET_W1_CL_AUTOPSY_20260906/out")
os.makedirs(OUT, exist_ok=True)

DISCOVERY_LAST = pd.Timestamp("2025-06-30")   # FREEZE: hard-drop sessions AFTER this
CL_PV = 1000.0
NQ_PV = 20.0

# CL NATIVE PIT / DAY SESSION (determined empirically from the volume profile below):
#   pit open 09:00 ET ; settlement 14:30 ET.
# END-stamped: pit-open price = OPEN of the bar stamped 09:01 (opens 09:00);
#              settlement close = CLOSE of the bar stamped 14:30 (covers 14:29->14:30).
PIT_FIRST_STAMP = (9, 1)     # mod 541 (opens 09:00)
PIT_LAST_STAMP = (14, 30)    # mod 870 (settles 14:30)
PIT_MIN = PIT_FIRST_STAMP[0] * 60 + PIT_FIRST_STAMP[1]   # 541
PIT_MAX = PIT_LAST_STAMP[0] * 60 + PIT_LAST_STAMP[1]      # 870
FULL_PIT_BARS = PIT_MAX - PIT_MIN + 1                     # 330
MIN_PIT_BARS = 250                                        # drop half-day / holiday shells


def log(m):
    print(m, flush=True)


def minute_label(mod):
    return f"{int(mod)//60:02d}:{int(mod)%60:02d}"


def session_date(ts):
    """CME trade-date: session 18:00 ET (prior day) -> 17:00 ET; hour>=18 rolls forward one
    calendar day; weekend evening opens roll forward to Monday. Vectorized."""
    d = ts.dt.normalize()
    d = d + pd.to_timedelta((ts.dt.hour >= 18).astype(int), unit="D")
    for _ in range(3):
        m = d.dt.weekday >= 5
        if not m.any():
            break
        d = d + pd.to_timedelta(m.astype(int), unit="D")
    return d.dt.normalize()


def load(parquet, label, apply_freeze):
    df = pd.read_parquet(parquet)
    df["time"] = pd.to_datetime(df["time"])
    n_raw = len(df)
    raw_last = df["time"].max()
    df = df.sort_values("time").reset_index(drop=True)
    df["sess"] = session_date(df["time"])
    if apply_freeze:
        before = len(df)
        df = df[df["sess"] <= DISCOVERY_LAST].copy()
        dropped = before - len(df)
        # ---- MANDATORY FREEZE ASSERTION ----
        assert df["sess"].max() <= DISCOVERY_LAST, "FREEZE VIOLATION: session > 2025-06-30 retained"
        log(f"[{label}] FREEZE ok. raw rows={n_raw:,} raw_last={raw_last} "
            f"dropped(sess>{DISCOVERY_LAST.date()})={dropped:,} retained={len(df):,}")
    else:
        log(f"[{label}] raw rows={n_raw:,} raw_last={raw_last} (no freeze applied)")
    df["mod"] = df["time"].dt.hour * 60 + df["time"].dt.minute
    df = df.sort_values("time").reset_index(drop=True)
    log(f"[{label}] retained sessions {df['sess'].min().date()} .. {df['sess'].max().date()} "
        f"n={df['sess'].nunique()}")
    return df


# =====================================================================================
# NATIVE-SESSION DETERMINATION  -> session.txt
# =====================================================================================
def native_session(df, fh):
    nsess = df["sess"].nunique()
    fh.write("=" * 92 + "\n")
    fh.write("CL MARKET AUTOPSY -- NATIVE SESSION DETERMINATION (from CL's own volume, not assumed)\n")
    fh.write("=" * 92 + "\n")
    fh.write(f"FREEZE: discovery window ONLY, sessions <= {DISCOVERY_LAST.date()} "
             f"(holdout 2025-07-01->2026-07-31 and virgin >=2026-08-01 NOT read).\n")
    fh.write(f"Retained: {df['sess'].min().date()} .. {df['sess'].max().date()}  "
             f"n_sessions={nsess}  n_bars={len(df):,}\n")
    fh.write("Container: CME energy 18:00 ET -> 17:00 ET next day, maintenance halt 17:00-18:00.\n")
    fh.write("Point value $1,000/pt ($10/tick, tick $0.01). ALL stats below are POINT differences.\n\n")

    # hour-of-day volume share
    df = df.copy()
    df["hour"] = df["mod"] // 60
    hp = df.groupby("hour")["volume"].sum()
    hp = hp / hp.sum() * 100
    fh.write("--- volume share by HOUR of day (ET) ---\n")
    for h in range(24):
        if h in hp.index:
            fh.write(f"  {h:02d}:00  {hp[h]:5.2f}%  {'#' * int(hp[h] * 4)}\n")
    fh.write("\n")

    # single clock-minute leaders (open / settle / EIA spikes)
    vp = df.groupby("mod")["volume"].agg(["sum", "mean", "count"])
    vp["share"] = vp["sum"] / vp["sum"].sum() * 100
    vp["cov"] = vp["count"] / nsess * 100
    top = vp.sort_values("sum", ascending=False).head(12)
    fh.write("--- top 12 single clock-minutes by total volume (open / settlement / release spikes) ---\n")
    for m, r in top.iterrows():
        fh.write(f"  {minute_label(m)}  share {r['share']:.3f}%  mean/sess {r['mean']:7.0f}  "
                 f"coverage {r['cov']:5.1f}%\n")
    fh.write("\n")

    # smallest contiguous window holding 90% of volume
    order = vp.sort_values("sum", ascending=False)
    cum = order["share"].cumsum()
    core = sorted(set(order.loc[cum <= 90.0].index) | {order.index[0]})
    fh.write(f"Clock-minutes covering 90% of volume span {minute_label(min(core))} .. "
             f"{minute_label(max(core))} ET.\n")

    # settlement / pit-open evidence
    fh.write("\n--- settlement clock evidence (14:28-14:32 ET) ---\n")
    for m in range(14 * 60 + 27, 14 * 60 + 33):
        if m in vp.index:
            fh.write(f"  {minute_label(m)} share {vp.loc[m, 'share']:.3f}% mean/sess {vp.loc[m, 'mean']:7.0f}\n")
    peak = vp["sum"].idxmax()
    fh.write(f"Peak single clock-minute = {minute_label(peak)} ET -> CL SETTLEMENT is 14:30 ET.\n")
    fh.write("\n--- pit-open evidence (08:59-09:04 ET) ---\n")
    for m in range(8 * 60 + 59, 9 * 60 + 5):
        if m in vp.index:
            fh.write(f"  {minute_label(m)} share {vp.loc[m, 'share']:.3f}% mean/sess {vp.loc[m, 'mean']:7.0f}\n")
    fh.write("Volume steps up sharply at 09:01 (opens 09:00) -> CL PIT OPEN is 09:00 ET.\n\n")

    pit_mask = (df["mod"] >= PIT_MIN) & (df["mod"] <= PIT_MAX)
    pit_share = 100 * df.loc[pit_mask, "volume"].sum() / df["volume"].sum()
    eu_mask = (df["mod"] > 3 * 60) & (df["mod"] <= 8 * 60)
    eu_share = 100 * df.loc[eu_mask, "volume"].sum() / df["volume"].sum()
    halt = df[(df["mod"] > 17 * 60) & (df["mod"] < 18 * 60)]
    fh.write("--- ADOPTED SESSION PARTITION (economically grounded in the profile above) ---\n")
    fh.write(f"  PIT / US day session (RTH-equivalent) : [09:00, 14:30] ET  "
             f"(pit open 09:00 -> settlement 14:30); carries {pit_share:.1f}% of volume in 5.5h.\n")
    fh.write(f"  European overlap (03:00-08:00 ET)     : {eu_share:.1f}% of volume "
             f"(materially liquid -- CL overnight is NOT dead, unlike equity indices).\n")
    fh.write(f"  Overnight / inter-pit                 : complement (prev 14:30 settle -> today 09:00 open).\n")
    fh.write(f"  Maintenance halt 17:00-18:00 ET bar-count = {len(halt)} (confirms the daily break).\n")
    fh.write("  NOTE: CL's day session opens at 09:00 ET and closes at a hard 14:30 ET SETTLEMENT --\n")
    fh.write("        this is NOT NQ's 09:30-16:00. Settlement concentrates hedger/physical flow.\n\n")
    return pit_share


# =====================================================================================
# PER-SESSION FRAME (pit open/high/low/close, overnight gap, ranges) -- points basis
# =====================================================================================
def per_session(df):
    pit = df[(df["mod"] >= PIT_MIN) & (df["mod"] <= PIT_MAX)].copy()
    rows = []
    for sess, gg in pit.groupby("sess"):
        gg = gg.sort_values("time")
        rows.append({
            "sess": sess,
            "pit_open": gg["open"].iloc[0],      # opens 09:00
            "pit_close": gg["close"].iloc[-1],   # settles 14:30
            "pit_high": gg["high"].max(),
            "pit_low": gg["low"].min(),
            "pit_nbars": len(gg),
        })
    ps = pd.DataFrame(rows).sort_values("sess").reset_index(drop=True)
    ps = ps[ps["pit_nbars"] >= MIN_PIT_BARS].copy()
    ps["pit_ret"] = ps["pit_close"] - ps["pit_open"]        # pit session point return
    ps["pit_range"] = ps["pit_high"] - ps["pit_low"]        # pit range (pt)
    ps["prev_close"] = ps["pit_close"].shift(1)
    ps["gap"] = ps["pit_open"] - ps["prev_close"]           # inter-pit / overnight move (pt)
    ps["prev_pit_ret"] = ps["pit_ret"].shift(1)
    ps["full_ret"] = ps["pit_close"] - ps["prev_close"]     # prev settle -> settle (pt) = gap+pit
    ps["dow"] = pd.to_datetime(ps["sess"]).dt.dayofweek
    return ps


def overnight_ranges(df):
    """Overnight range = PRE-PIT segment leading into the 09:00 open (Globex overnight):
    session bars with end-stamp before 09:01 or in the evening block (18:01..24:00).
    (post-settlement 14:31-17:00 tail is thin and excluded from this range measure.)"""
    pre = df[(df["mod"] < PIT_MIN) | (df["mod"] >= 18 * 60)].copy()
    agg = pre.groupby("sess").agg(on_high=("high", "max"), on_low=("low", "min"),
                                  on_nbars=("volume", "size")).reset_index()
    agg["on_range"] = agg["on_high"] - agg["on_low"]
    return agg


# =====================================================================================
# RETURNS  -> returns_by_tod.csv + returns.txt
# =====================================================================================
def returns_by_tod(df, csv_path):
    d = df.copy()
    d["ret"] = d["close"].diff()
    d.loc[d["sess"] != d["sess"].shift(1), "ret"] = np.nan
    d = d.dropna(subset=["ret"])
    d["b30"] = (d["mod"] // 30) * 30
    g = d.groupby("b30").agg(n=("ret", "size"), mean_pt=("ret", "mean"),
                             std_pt=("ret", "std"), sum_pt=("ret", "sum")).reset_index()
    g["clock"] = g["b30"].map(minute_label)
    g["tstat"] = g["mean_pt"] / (g["std_pt"] / np.sqrt(g["n"]))
    g = g[["clock", "b30", "n", "mean_pt", "std_pt", "sum_pt", "tstat"]]
    g.to_csv(csv_path, index=False, float_format="%.6f")
    return g


def returns_section(df, ps, onr, g_tod, fh):
    fh.write("CL MARKET AUTOPSY -- RETURNS  (points basis; PV=$1,000/pt)\n")
    fh.write("=" * 92 + "\n\n")
    fh.write("--- 1-min mean point return by 30-min bucket (ET, END-stamp); full table in "
             "returns_by_tod.csv ---\n")
    fh.write(g_tod.to_string(index=False, float_format=lambda x: f"{x:.6f}"))
    fh.write("\n\n")

    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    ps2 = ps.copy()
    ps2["dname"] = pd.to_datetime(ps2["sess"]).dt.day_name()
    dw = ps2.groupby("dname").agg(n=("pit_ret", "size"), pit_mean=("pit_ret", "mean"),
                                  pit_std=("pit_ret", "std"), gap_mean=("gap", "mean"),
                                  gap_std=("gap", "std")).reindex(order)
    fh.write("--- pit session return & overnight gap by DAY-OF-WEEK (pt) ---\n")
    fh.write("(Wednesday carries the EIA 10:30 petroleum-inventory release -- watch its dispersion)\n")
    fh.write(dw.to_string(float_format=lambda x: f"{x:8.4f}"))
    fh.write("\n\n")

    fh.write("--- SESSION vs OVERNIGHT decomposition (pt) ---\n")
    rr = ps["pit_ret"].dropna(); gg = ps["gap"].dropna(); ff = ps["full_ret"].dropna()
    for name, s in [("PIT (09:00->14:30 settle)", rr),
                    ("Overnight/inter-pit (14:30->09:00)", gg),
                    ("Full (prev settle->settle)", ff)]:
        fh.write(f"  {name:36s} n={len(s):4d} mean={s.mean():8.4f} std={s.std():7.3f} "
                 f"sum={s.sum():9.1f} t={s.mean()/(s.std()/np.sqrt(len(s))):6.2f}\n")
    tot = rr.abs().sum() + gg.abs().sum()
    fh.write(f"  Share of gross absolute move: PIT={100*rr.abs().sum()/tot:.1f}%  "
             f"overnight={100*gg.abs().sum()/tot:.1f}%\n")
    fh.write(f"  Directional drift: sum(PIT)={rr.sum():.1f}pt  sum(overnight)={gg.sum():.1f}pt\n\n")

    fh.write("--- CONDITIONAL EXPECTANCY: continuation vs reversal (pt) ---\n")
    p = ps.dropna(subset=["prev_pit_ret", "pit_ret", "gap"]).copy()
    for cn, c in [("prior PIT up", p["prev_pit_ret"] > 0), ("prior PIT down", p["prev_pit_ret"] < 0)]:
        sub = p[c]
        fh.write(f"  E[PIT ret | {cn:14s}] = {sub['pit_ret'].mean():8.4f}  "
                 f"E[gap | {cn:14s}] = {sub['gap'].mean():8.4f}  n={len(sub)}\n")
    fh.write("\n")
    for cn, c in [("gap up", p["gap"] > 0), ("gap down", p["gap"] < 0)]:
        sub = p[c]
        fh.write(f"  E[PIT ret | {cn:8s}] = {sub['pit_ret'].mean():8.4f}  n={len(sub)}  (gap-fill vs gap-go)\n")
    fh.write("\n")
    fh.write("  corr(prev PIT ret, gap)      = %+.3f  (overnight continuation of the pit move)\n"
             % p["prev_pit_ret"].corr(p["gap"]))
    fh.write("  corr(gap, PIT ret same day)  = %+.3f  (open-drive persistence within the pit)\n"
             % p["gap"].corr(p["pit_ret"]))
    fh.write("  corr(prev PIT ret, PIT ret)  = %+.3f  (day-to-day pit continuation)\n\n"
             % p["prev_pit_ret"].corr(p["pit_ret"]))

    # around the settlement clock: pre-settlement (14:00-14:30) drift
    d = df.copy(); d["ret"] = d["close"].diff()
    d.loc[d["sess"] != d["sess"].shift(1), "ret"] = np.nan
    pre_settle = d[(d["mod"] > 14 * 60) & (d["mod"] <= PIT_MAX)].groupby("sess")["ret"].sum()
    fh.write("--- around the SETTLEMENT clock (pt) ---\n")
    fh.write(f"  pre-settlement drift 14:00->14:30  mean={pre_settle.mean():+.4f} "
             f"std={pre_settle.std():.3f} t={pre_settle.mean()/(pre_settle.std()/np.sqrt(len(pre_settle))):+.2f} "
             f"n={len(pre_settle)}\n")
    post_settle = d[(d["mod"] > PIT_MAX) & (d["mod"] <= 15 * 60)].groupby("sess")["ret"].sum()
    fh.write(f"  post-settlement drift 14:30->15:00 mean={post_settle.mean():+.4f} "
             f"std={post_settle.std():.3f} t={post_settle.mean()/(post_settle.std()/np.sqrt(len(post_settle))):+.2f} "
             f"n={len(post_settle)}\n\n")


# =====================================================================================
# DISTRIBUTION  -> distribution.txt
# =====================================================================================
def distribution_section(df, ps, onr, fh):
    fh.write("CL MARKET AUTOPSY -- DISTRIBUTION  (points basis; PV=$1,000/pt)\n")
    fh.write("=" * 92 + "\n\n")

    d = df.copy(); d["ret"] = d["close"].diff()
    d.loc[d["sess"] != d["sess"].shift(1), "ret"] = np.nan
    r1 = d["ret"].dropna()
    fh.write("--- 1-min close-to-close return (within session, all hours) ---\n")
    fh.write(f"  n={len(r1):,} mean={r1.mean():.5f} std={r1.std():.5f} "
             f"skew={stats.skew(r1):.3f} exkurt={stats.kurtosis(r1):.1f}\n")
    qs = [0.001, 0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999]
    fh.write("  quantiles(pt): " + "  ".join(f"{q*100:g}%={r1.quantile(q):+.3f}" for q in qs) + "\n")
    for k in [0.05, 0.10, 0.20, 0.50]:
        fr = (r1.abs() > k).mean()
        fh.write(f"  P(|1-min move| > {k:.2f}pt) = {fr*100:.3f}%"
                 + (f"  (~1 per {1/fr:.0f} bars)\n" if fr > 0 else "\n"))
    fh.write("\n")

    fh.write("--- daily distributions (pt) ---\n")
    for name, s in [("PIT session ret", ps["pit_ret"].dropna()),
                    ("overnight gap", ps["gap"].dropna()),
                    ("full-day ret", ps["full_ret"].dropna())]:
        fh.write(f"  {name:16s} n={len(s):4d} mean={s.mean():7.4f} std={s.std():7.3f} "
                 f"skew={stats.skew(s):6.3f} exkurt={stats.kurtosis(s):6.2f} "
                 f"min={s.min():8.3f} max={s.max():8.3f}\n")
    fh.write("\n")

    g = ps["gap"].dropna()
    fh.write("--- overnight gap distribution ---\n")
    fh.write(f"  |gap| mean={g.abs().mean():.4f}pt median={g.abs().median():.4f}pt  "
             f"P(gap up)={100*(g>0).mean():.1f}%  P(|gap|>0.50pt)={100*(g.abs()>0.5).mean():.1f}%\n")
    fh.write("  gap quantiles(pt): " + "  ".join(f"{int(q*100)}%={g.quantile(q):+.3f}"
             for q in [0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]) + "\n\n")

    m = ps.merge(onr, on="sess", how="left")
    fh.write("--- range: intraday (PIT) vs overnight (pt) ---\n")
    fh.write(f"  PIT range       mean={m['pit_range'].mean():.3f} median={m['pit_range'].median():.3f} "
             f"p95={m['pit_range'].quantile(.95):.3f} max={m['pit_range'].max():.3f}\n")
    fh.write(f"  overnight range mean={m['on_range'].mean():.3f} median={m['on_range'].median():.3f} "
             f"p95={m['on_range'].quantile(.95):.3f} max={m['on_range'].max():.3f}\n")
    fh.write(f"  overnight/PIT range ratio (median) = {(m['on_range']/m['pit_range']).median():.2f}\n\n")

    # realized vol per year (pit), points
    d2 = d.dropna(subset=["ret"])
    pitb = d2[(d2["mod"] >= PIT_MIN) & (d2["mod"] <= PIT_MAX)]
    rv = pitb.groupby("sess")["ret"].apply(lambda x: np.sqrt((x ** 2).sum())).reset_index(name="rv")
    rv["yr"] = pd.to_datetime(rv["sess"]).dt.year
    fh.write("--- realized vol: daily PIT RV = sqrt(sum sq 1-min ret), pt, by year ---\n")
    fh.write(rv.groupby("yr")["rv"].agg(["count", "mean", "median", "max"]).to_string(
             float_format=lambda x: f"{x:8.3f}"))
    fh.write("\n\n")

    # extreme-day frequency by year (physical-commodity shock characterization)
    m["yr"] = pd.to_datetime(m["sess"]).dt.year
    big = m["pit_range"].quantile(0.90)
    fh.write(f"--- extreme-day frequency by year (pt); 'big pit range' = >90th pct = {big:.2f}pt ---\n")
    ex = m.groupby("yr").agg(n=("pit_ret", "size"),
                             pit_ret_std=("pit_ret", "std"),
                             p_bigrange=("pit_range", lambda x: 100 * (x > big).mean()),
                             worst_ret=("pit_ret", "min"), best_ret=("pit_ret", "max"),
                             max_range=("pit_range", "max"))
    fh.write(ex.to_string(float_format=lambda x: f"{x:8.3f}"))
    fh.write("\n\n")
    return rv


# =====================================================================================
# DEPENDENCE  -> dependence.txt
# =====================================================================================
def acf(x, lag):
    x = x - np.nanmean(x)
    den = np.nansum(x * x)
    return np.nansum(x[:-lag] * x[lag:]) / den if den > 0 else np.nan


def dependence_section(df, ps, rv, fh):
    fh.write("CL MARKET AUTOPSY -- DEPENDENCE  (points basis)\n")
    fh.write("=" * 92 + "\n\n")
    d = df.copy(); d["ret"] = d["close"].diff()
    d.loc[d["sess"] != d["sess"].shift(1), "ret"] = np.nan
    pitb = d[(d["mod"] >= PIT_MIN) & (d["mod"] <= PIT_MAX)].dropna(subset=["ret"])
    r = pitb["ret"].values

    fh.write("--- 1-min PIT return autocorrelation ---\n")
    for lag in [1, 2, 3, 5, 10, 30]:
        fh.write(f"  acf(lag={lag:3d}) = {acf(r, lag):+.4f}\n")
    s = np.sign(r); s = s[s != 0]
    fh.write(f"  1-min sign persistence P(same sign next) = {(s[1:]==s[:-1]).mean()*100:.2f}% "
             f"(50% = none)\n\n")

    fh.write("--- variance ratio VR(q)=Var(q-sum)/(q*Var(1)) on 1-min PIT returns ---\n")
    fh.write("    VR<1 = mean-reversion/anti-persistence ; VR>1 = trending\n")
    var1 = np.var(r)
    for q in [2, 5, 10, 30, 60]:
        cs = np.cumsum(r); qsum = cs[q:] - cs[:-q]
        fh.write(f"  VR({q:3d}) = {np.var(qsum)/(q*var1):.3f}\n")
    fh.write("\n")

    dr = ps["pit_ret"].dropna().values
    fh.write("--- daily PIT return dependence ---\n")
    for lag in [1, 2, 3, 5]:
        fh.write(f"  acf(lag={lag}) = {acf(dr, lag):+.4f}\n")
    sd = np.sign(dr); sd = sd[sd != 0]
    fh.write(f"  daily sign persistence P(same sign next) = {(sd[1:]==sd[:-1]).mean()*100:.2f}%\n")
    var1d = np.var(dr)
    fh.write("  daily VR: ")
    for q in [2, 3, 5, 10]:
        cs = np.cumsum(dr); qs_ = cs[q:] - cs[:-q]
        fh.write(f"VR({q})={np.var(qs_)/(q*var1d):.3f}  ")
    fh.write("\n\n")

    fh.write("--- volatility autocorrelation ---\n")
    ar = np.abs(r)
    for lag in [1, 5, 30, 330]:
        fh.write(f"  |1-min ret| acf(lag={lag:3d}) = {acf(ar, lag):+.4f}\n")
    rvv = rv["rv"].values
    for lag in [1, 2, 5, 10]:
        fh.write(f"  daily PIT RV acf(lag={lag:2d})   = {acf(rvv, lag):+.4f}\n")
    fh.write("\n")

    fh.write("--- conditional next 1-min move after a LARGE 1-min PIT move (pt) ---\n")
    thr = np.quantile(np.abs(r), 0.99)
    fh.write(f"  (large = |move| > 99th pct = {thr:.3f}pt)\n")
    idx = np.where(np.abs(r[:-1]) > thr)[0]
    nxt = r[idx + 1]; prev = r[idx]
    fh.write(f"  n large moves={len(idx)}  E[next same-dir]={np.mean(nxt*np.sign(prev)):+.4f}pt "
             f"P(continue)={100*(np.sign(nxt)==np.sign(prev)).mean():.1f}%\n")
    idx2 = np.where(np.abs(r[:-1]) <= thr)[0]
    nxt2 = r[idx2 + 1]; prev2 = r[idx2]
    fh.write(f"  baseline (small moves): E[next same-dir]={np.mean(nxt2*np.sign(prev2)):+.4f}pt "
             f"P(continue)={100*(np.sign(nxt2)==np.sign(prev2)).mean():.1f}%\n")
    fh.write("  (detailed multi-horizon shock continuation/reversal is in shock_response.txt)\n\n")


# =====================================================================================
# PATH  -> path.txt
# =====================================================================================
def path_section(df, ps, fh):
    fh.write("CL MARKET AUTOPSY -- PATH GEOMETRY  (points basis)\n")
    fh.write("=" * 92 + "\n\n")
    pit = df[(df["mod"] >= PIT_MIN) & (df["mod"] <= PIT_MAX)].copy()
    recs = []
    for sess, gg in pit.groupby("sess"):
        gg = gg.sort_values("time")
        if len(gg) < MIN_PIT_BARS:
            continue
        c = gg["close"].values; o = gg["open"].iloc[0]
        step = np.abs(np.diff(c)); pathlen = step.sum(); disp = c[-1] - o
        er = abs(disp) / pathlen if pathlen > 0 else np.nan
        recs.append({"sess": sess, "er": er,
                     "tort": pathlen / abs(disp) if disp != 0 else np.nan,
                     "disp": disp, "mfe": gg["high"].max() - o, "mae": o - gg["low"].min(),
                     "rng": gg["high"].max() - gg["low"].min()})
    pa = pd.DataFrame(recs).sort_values("sess").reset_index(drop=True)
    fh.write("--- Kaufman efficiency ratio ER = |net| / sum|1-min step|, per PIT session ---\n")
    fh.write(f"  ER mean={pa['er'].mean():.3f} median={pa['er'].median():.3f} "
             f"p25={pa['er'].quantile(.25):.3f} p75={pa['er'].quantile(.75):.3f}\n")
    fh.write("  (low ER = choppy/mean-reverting path; high ER = directional/trending day)\n\n")
    t = pa["tort"].replace([np.inf, -np.inf], np.nan).dropna()
    fh.write(f"--- tortuosity = pathlen/|displacement| : median={t.median():.2f} p90={t.quantile(.90):.2f}\n\n")
    fh.write("--- MFE/MAE from PIT open (excursions, pt; 'long-from-open' framing) ---\n")
    fh.write(f"  MFE mean={pa['mfe'].mean():.3f} median={pa['mfe'].median():.3f} p95={pa['mfe'].quantile(.95):.3f}\n")
    fh.write(f"  MAE mean={pa['mae'].mean():.3f} median={pa['mae'].median():.3f} p95={pa['mae'].quantile(.95):.3f}\n")
    fh.write(f"  MFE/MAE median ratio = {(pa['mfe']/pa['mae'].replace(0,np.nan)).median():.2f}\n")
    fh.write(f"  net displacement mean(|.|)={pa['disp'].abs().mean():.3f} vs range mean={pa['rng'].mean():.3f} "
             f"-> captured range fraction = {pa['disp'].abs().mean()/pa['rng'].mean():.2f}\n\n")

    fh.write("--- compression / expansion (pit range clustering) ---\n")
    rng = pa["rng"].values
    for lag in [1, 2, 5]:
        fh.write(f"  PIT range acf(lag={lag}) = {acf(rng, lag):+.3f}\n")
    nr7 = np.array([rng[i] == rng[max(0, i-6):i+1].min() for i in range(len(rng))])
    nxt = np.append(rng[1:], np.nan)
    fh.write(f"  next-day pit range after NR7 = {np.nanmean(nxt[nr7])/np.nanmean(rng):.2f}x avg "
             f"vs non-NR7 = {np.nanmean(nxt[~nr7])/np.nanmean(rng):.2f}x avg (n_nr7={int(nr7.sum())})\n\n")


# =====================================================================================
# SESSION STRUCTURE  (appended into session.txt)
# =====================================================================================
def session_structure_section(df, ps, onr, fh):
    fh.write("=" * 92 + "\n")
    fh.write("CL SESSION STRUCTURE (descriptive, points basis)\n")
    fh.write("=" * 92 + "\n\n")
    m = ps.merge(onr, on="sess", how="left").sort_values("sess").reset_index(drop=True)

    fh.write("--- overnight (Globex, pre-09:00) high/low behavior during the PIT session ---\n")
    fh.write(f"  P(PIT takes out overnight HIGH) = {100*(m['pit_high']>m['on_high']).mean():.1f}%\n")
    fh.write(f"  P(PIT takes out overnight LOW)  = {100*(m['pit_low']<m['on_low']).mean():.1f}%\n")
    fh.write(f"  P(PIT takes out BOTH)           = "
             f"{100*((m['pit_high']>m['on_high'])&(m['pit_low']<m['on_low'])).mean():.1f}%\n")
    fh.write(f"  P(PIT stays INSIDE overnight range) = "
             f"{100*((m['pit_high']<=m['on_high'])&(m['pit_low']>=m['on_low'])).mean():.1f}%\n\n")

    pit = df[(df["mod"] >= PIT_MIN) & (df["mod"] <= PIT_MAX)].copy()
    fh.write("--- opening range (OR) from the 09:00 pit open, pt ---\n")
    for win in [15, 30, 60]:
        recs = []
        for sess, gg in pit.groupby("sess"):
            gg = gg.sort_values("time")
            if len(gg) < MIN_PIT_BARS:
                continue
            orb = gg.iloc[:win]; hi, lo = orb["high"].max(), orb["low"].min()
            rest = gg.iloc[win:]
            if len(rest) == 0:
                continue
            recs.append({"or_range": hi - lo, "broke_up": rest["high"].max() > hi,
                         "broke_dn": rest["low"].min() < lo,
                         "day_high_in_or": gg["high"].idxmax() in orb.index,
                         "day_low_in_or": gg["low"].idxmin() in orb.index})
        rr = pd.DataFrame(recs)
        fh.write(f"  OR{win:>2}min: range mean={rr['or_range'].mean():.3f}pt median={rr['or_range'].median():.3f} "
                 f"P(break up later)={100*rr['broke_up'].mean():.1f}% P(break dn later)={100*rr['broke_dn'].mean():.1f}%  "
                 f"P(day-high in OR)={100*rr['day_high_in_or'].mean():.1f}% "
                 f"P(day-low in OR)={100*rr['day_low_in_or'].mean():.1f}%\n")
    fh.write("\n")

    fh.write("--- gap behavior vs prior settlement (pt) ---\n")
    g = m.dropna(subset=["gap", "prev_close"]).copy()
    filled = ((g["gap"] > 0) & (g["pit_low"] <= g["prev_close"])) | \
             ((g["gap"] < 0) & (g["pit_high"] >= g["prev_close"]))
    fh.write(f"  P(gap fills to prior settle during PIT) = {100*filled.mean():.1f}%\n")
    up = g[g["gap"] > 0.1]; dn = g[g["gap"] < -0.1]
    fh.write(f"  gap-up (>0.10pt)  n={len(up)}  fill%={100*(up['pit_low']<=up['prev_close']).mean():.1f}  "
             f"E[PIT ret]={up['pit_ret'].mean():+.4f}\n")
    fh.write(f"  gap-dn (<-0.10pt) n={len(dn)}  fill%={100*(dn['pit_high']>=dn['prev_close']).mean():.1f} "
             f"E[PIT ret]={dn['pit_ret'].mean():+.4f}\n\n")

    m["prev_high"] = m["pit_high"].shift(1); m["prev_low"] = m["pit_low"].shift(1)
    mm = m.dropna(subset=["prev_high", "prev_low"])
    fh.write("--- prior-day PIT level interaction ---\n")
    fh.write(f"  P(today PIT touches prior-day HIGH) = {100*(mm['pit_high']>=mm['prev_high']).mean():.1f}%\n")
    fh.write(f"  P(today PIT touches prior-day LOW)  = {100*(mm['pit_low']<=mm['prev_low']).mean():.1f}%\n")
    fh.write(f"  P(today PIT range engulfs prior-day range) = "
             f"{100*((mm['pit_high']>=mm['prev_high'])&(mm['pit_low']<=mm['prev_low'])).mean():.1f}%\n\n")


# =====================================================================================
# SHOCK RESPONSE  -> shock_response.txt   (the CL-specific deliverable)
# =====================================================================================
def shock_response_section(df, ps, fh):
    fh.write("CL MARKET AUTOPSY -- SHOCK RESPONSE  (points basis)\n")
    fh.write("=" * 92 + "\n")
    fh.write("CL is a physical-commodity market with information shocks (EIA inventories, OPEC,\n")
    fh.write("geopolitics, outages). This section characterizes (A) large-bar / vol-burst frequency,\n")
    fh.write("(B) the EIA Wednesday 10:30 ET scheduled shock, and (C) shock CONTINUATION vs REVERSAL\n")
    fh.write("after large bars / abnormal volume -- the key energy question.\n")
    fh.write("=" * 92 + "\n\n")

    d = df.copy(); d["ret"] = d["close"].diff()
    d.loc[d["sess"] != d["sess"].shift(1), "ret"] = np.nan
    pitb = d[(d["mod"] >= PIT_MIN) & (d["mod"] <= PIT_MAX)].copy()

    # ------- (A) large-bar / volatility-burst frequency -------
    r = pitb["ret"].dropna()
    fh.write("--- (A) large 1-min bar / volatility-burst frequency (PIT) ---\n")
    for q in [0.99, 0.995, 0.999]:
        thr = np.quantile(r.abs(), q)
        fr = (r.abs() > thr).mean()
        fh.write(f"  {q*100:.1f}th pct |1-min move| = {thr:.3f}pt  -> ~1 per {1/fr:.0f} bars "
                 f"(~{fr*330:.2f} per pit session)\n")
    # jump share of daily variance: sum of sq of top-1% bars vs total
    pitb["yr"] = pd.to_datetime(pitb["sess"]).dt.year
    fh.write("\n  jump-vs-diffusion by year: share of daily PIT sum-sq-return contributed by the\n")
    fh.write("  largest 1% of 1-min bars (high share = jumpy/shock-driven; low = diffusive):\n")
    for yr, gg in pitb.dropna(subset=["ret"]).groupby("yr"):
        rr = gg["ret"].values; sq = rr ** 2
        thr = np.quantile(np.abs(rr), 0.99)
        share = sq[np.abs(rr) > thr].sum() / sq.sum() * 100
        fh.write(f"    {yr}: top-1% bars carry {share:5.1f}% of PIT variance  (n_bars={len(rr):,})\n")
    fh.write("\n")

    # ------- (B) EIA Wednesday 10:30 ET scheduled shock -------
    fh.write("--- (B) EIA weekly petroleum-inventory shock (Wednesday 10:30 ET release) ---\n")
    d["dow"] = pd.to_datetime(d["sess"]).dt.dayofweek
    # release bar = 10:31 end-stamp (covers 10:30->10:31, i.e. the first minute AFTER 10:30 print).
    # Also report the 10:30 end-stamp bar (10:29->10:30) for symmetry.
    for stamp_lbl, mod in [("10:30->10:31 (release bar)", 10 * 60 + 31),
                           ("10:29->10:30", 10 * 60 + 30)]:
        wed = d[(d["dow"] == 2) & (d["mod"] == mod)]["ret"].dropna()
        oth = d[(d["dow"] != 2) & (d["mod"] == mod)]["ret"].dropna()
        fh.write(f"  |move| at {stamp_lbl}: WED mean|r|={wed.abs().mean():.4f}pt (n={len(wed)}) "
                 f"vs non-WED {oth.abs().mean():.4f}pt (n={len(oth)}) "
                 f"-> ratio {wed.abs().mean()/oth.abs().mean():.2f}x\n")
    # RV in the 10:30-11:00 window Wed vs non-Wed
    win = d[(d["mod"] > 10 * 60 + 30) & (d["mod"] <= 11 * 60)].dropna(subset=["ret"])
    rvw = win.groupby(["sess"]).agg(rv=("ret", lambda x: np.sqrt((x ** 2).sum()))).reset_index()
    rvw["dow"] = pd.to_datetime(rvw["sess"]).dt.dayofweek
    wed_rv = rvw[rvw["dow"] == 2]["rv"]; oth_rv = rvw[rvw["dow"] != 2]["rv"]
    fh.write(f"  RV(10:30-11:00): WED mean={wed_rv.mean():.4f}pt vs non-WED {oth_rv.mean():.4f}pt "
             f"-> expansion {wed_rv.mean()/oth_rv.mean():.2f}x  "
             f"(Welch t={stats.ttest_ind(wed_rv, oth_rv, equal_var=False).statistic:+.2f})\n")
    # EIA-day pit range vs non-EIA
    ew = ps.copy(); ew["dow"] = pd.to_datetime(ew["sess"]).dt.dayofweek
    fh.write(f"  PIT range: WED mean={ew[ew['dow']==2]['pit_range'].mean():.3f}pt vs "
             f"non-WED {ew[ew['dow']!=2]['pit_range'].mean():.3f}pt\n")
    # post-release continuation: sign of release bar -> rest-of-window (10:31->11:00) move
    rel = d[(d["dow"] == 2) & (d["mod"] == 10 * 60 + 31)][["sess", "ret"]].rename(columns={"ret": "rel"})
    rest = d[(d["dow"] == 2) & (d["mod"] > 10 * 60 + 31) & (d["mod"] <= 11 * 60)] \
        .groupby("sess")["ret"].sum().reset_index().rename(columns={"ret": "rest"})
    ev = rel.merge(rest, on="sess").dropna()
    ev = ev[ev["rel"] != 0]
    cont = np.sign(ev["rel"]) == np.sign(ev["rest"])
    fh.write(f"  post-release continuation (Wed): release-bar sign -> 10:31-11:00 move  "
             f"P(continue)={100*cont.mean():.1f}%  E[rest*sign(rel)]={np.mean(ev['rest']*np.sign(ev['rel'])):+.4f}pt "
             f"(n={len(ev)})\n")
    # release sign -> rest of PIT (to settlement)
    restpit = d[(d["dow"] == 2) & (d["mod"] > 10 * 60 + 31) & (d["mod"] <= PIT_MAX)] \
        .groupby("sess")["ret"].sum().reset_index().rename(columns={"ret": "restpit"})
    ev2 = rel.merge(restpit, on="sess").dropna(); ev2 = ev2[ev2["rel"] != 0]
    fh.write(f"  release-bar sign -> 10:31-14:30 (rest of pit): "
             f"P(continue)={100*(np.sign(ev2['rel'])==np.sign(ev2['restpit'])).mean():.1f}%  "
             f"E[restpit*sign(rel)]={np.mean(ev2['restpit']*np.sign(ev2['rel'])):+.4f}pt (n={len(ev2)})\n\n")

    # ------- (C) shock continuation vs reversal after large bars / abnormal volume -------
    fh.write("--- (C) continuation vs reversal after a LARGE 1-min bar (PIT), multi-horizon ---\n")
    fh.write("    (event = |1-min move| > threshold; forward k-min = cumulative move over next k bars,\n")
    fh.write("     within the same session only; sign-projected onto the event direction) ---\n")
    g = pitb.dropna(subset=["ret"]).reset_index(drop=True)
    ret = g["ret"].values
    same = g["sess"].values
    for q in [0.99, 0.995]:
        thr = np.quantile(np.abs(ret), q)
        ev_idx = np.where(np.abs(ret) > thr)[0]
        fh.write(f"\n  large = >{q*100:.1f}th pct (={thr:.3f}pt), n_events={len(ev_idx)}:\n")
        for k in [1, 3, 5, 15]:
            proj = []
            for i in ev_idx:
                if i + k >= len(ret):
                    continue
                if same[i + k] != same[i]:
                    continue
                fwd = ret[i + 1:i + 1 + k].sum()
                proj.append(fwd * np.sign(ret[i]))
            proj = np.array(proj)
            # baseline: same horizon after a NON-large bar
            base_idx = np.where(np.abs(ret) <= thr)[0]
            base = []
            for i in base_idx[::7]:  # subsample for speed
                if i + k >= len(ret) or same[i + k] != same[i]:
                    continue
                base.append(ret[i + 1:i + 1 + k].sum() * np.sign(ret[i]) if ret[i] != 0 else 0.0)
            base = np.array(base)
            tag = "CONTINUATION" if proj.mean() > 0 else "REVERSAL"
            fh.write(f"    fwd {k:2d}-min: E[proj]={proj.mean():+.4f}pt (n={len(proj)})  "
                     f"baseline={base.mean():+.4f}pt  -> {tag}\n")

    fh.write("\n--- (C2) abnormal-VOLUME bar -> next-move (PIT) ---\n")
    g["vmed"] = g.groupby("sess")["volume"].transform("median")
    g["vratio"] = g["volume"] / g["vmed"].replace(0, np.nan)
    for kmult in [3.0, 5.0, 10.0]:
        idx = np.where((g["vratio"] > kmult).values)[0]
        idx = idx[idx + 1 < len(g)]
        idx = idx[same[idx + 1] == same[idx]]
        prev = ret[idx]; nxt = ret[idx + 1]
        nz = prev != 0
        proj = nxt[nz] * np.sign(prev[nz])
        fh.write(f"  vol > {kmult:.0f}x session-median: n={len(idx)}  "
                 f"E[next 1-min proj]={proj.mean():+.4f}pt  P(continue)={100*(np.sign(nxt[nz])==np.sign(prev[nz])).mean():.1f}%\n")
    fh.write("\nREADING: VR<1 + reversal-after-large-bar => intraday shocks tend to OVER-shoot and\n")
    fh.write("partially revert at the 1-min scale; a positive multi-minute projection at longer k\n")
    fh.write("would indicate genuine continuation. Compare (C) horizons and (B) EIA persistence.\n\n")


# =====================================================================================
# NQ CORRELATION  -> nq_correlation.txt (also summarized in REPORT)
# =====================================================================================
def nq_correlation(cl_ps, fh):
    nq = load(NQ_PARQUET, "NQ", apply_freeze=True)  # restrict NQ to CL discovery window too
    # NQ native RTH = 09:30-16:00 (END-stamps 09:31..16:00)
    NQ_MIN, NQ_MAX = 9 * 60 + 31, 16 * 60
    rth = nq[(nq["mod"] >= NQ_MIN) & (nq["mod"] <= NQ_MAX)].copy()
    rows = []
    for sess, gg in rth.groupby("sess"):
        gg = gg.sort_values("time")
        rows.append({"sess": sess, "nq_open": gg["open"].iloc[0], "nq_close": gg["close"].iloc[-1],
                     "nq_nbars": len(gg)})
    nqp = pd.DataFrame(rows)
    nqp = nqp[nqp["nq_nbars"] >= 300]
    nqp["nq_rth"] = nqp["nq_close"] - nqp["nq_open"]
    nqp["nq_full"] = nqp["nq_close"] - nqp["nq_close"].shift(1)

    a = cl_ps[["sess", "pit_ret", "gap", "full_ret"]].rename(
        columns={"pit_ret": "cl_pit", "gap": "cl_gap", "full_ret": "cl_full"})
    b = nqp[["sess", "nq_rth", "nq_full"]]
    m = a.merge(b, on="sess", how="inner").dropna(subset=["cl_full", "nq_full"])

    fh.write("CL x NQ CORRELATION -- diversification pre-read (POINT-return basis; scale-free)\n")
    fh.write("=" * 92 + "\n\n")
    fh.write(f"shared discovery sessions n={len(m)}  ({m['sess'].min().date()}..{m['sess'].max().date()})\n")
    fh.write("NOTE: correlation is scale-free, so PV (CL $1,000 vs NQ $20) does not affect rho.\n")
    fh.write("Sessions differ: CL settles 14:30 ET, NQ closes 16:00 ET -- daily 'full' returns are\n")
    fh.write("each market's own prev-close->close, aligned by trade date.\n\n")
    rho_full = m["cl_full"].corr(m["nq_full"])
    fh.write(f"  daily FULL return   rho = {rho_full:+.3f}  (CL prev-settle->settle vs NQ prev-close->close)\n")
    fh.write(f"  intraday session    rho = {m['cl_pit'].corr(m['nq_rth']):+.3f}  (CL pit vs NQ RTH)\n")
    fh.write(f"  Spearman (full)     rho = {m['cl_full'].corr(m['nq_full'], method='spearman'):+.3f}\n\n")
    m["yr"] = pd.to_datetime(m["sess"]).dt.year
    fh.write("daily FULL rho by year:\n")
    for yr, gg in m.groupby("yr"):
        if len(gg) > 20:
            fh.write(f"  {yr}: rho={gg['cl_full'].corr(gg['nq_full']):+.3f}  n={len(gg)}\n")
    fh.write("\nDIVERSIFICATION VERDICT: CL is an energy/physical-commodity market; a low |rho| to NQ\n")
    fh.write("(an equity index) is the portfolio value -- a CL engine expresses a different factor.\n")
    return rho_full, m["cl_pit"].corr(m["nq_rth"]), len(m)


# =====================================================================================
def main():
    log("MARKET AUTOPSY -- CL (WTI crude, PV=$1,000/pt). DESCRIPTIVE / DISCOVERY_CONSUMED.")
    cl = load(CL_PARQUET, "CL", apply_freeze=True)
    ps = per_session(cl)
    onr = overnight_ranges(cl)
    log(f"per-session frame: {len(ps)} full pit sessions (>={MIN_PIT_BARS} bars); "
        f"pit stamps [{minute_label(PIT_MIN)},{minute_label(PIT_MAX)}]")

    # session.txt : native session + structure
    with open(os.path.join(OUT, "session.txt"), "w", encoding="utf-8") as fh:
        pit_share = native_session(cl, fh)
        session_structure_section(cl, ps, onr, fh)
    log("wrote session.txt")

    # returns
    g_tod = returns_by_tod(cl, os.path.join(OUT, "returns_by_tod.csv"))
    with open(os.path.join(OUT, "returns.txt"), "w", encoding="utf-8") as fh:
        returns_section(cl, ps, onr, g_tod, fh)
    log("wrote returns.txt + returns_by_tod.csv")

    with open(os.path.join(OUT, "distribution.txt"), "w", encoding="utf-8") as fh:
        rv = distribution_section(cl, ps, onr, fh)
    log("wrote distribution.txt")

    with open(os.path.join(OUT, "dependence.txt"), "w", encoding="utf-8") as fh:
        dependence_section(cl, ps, rv, fh)
    log("wrote dependence.txt")

    with open(os.path.join(OUT, "path.txt"), "w", encoding="utf-8") as fh:
        path_section(cl, ps, fh)
    log("wrote path.txt")

    with open(os.path.join(OUT, "shock_response.txt"), "w", encoding="utf-8") as fh:
        shock_response_section(cl, ps, fh)
    log("wrote shock_response.txt")

    with open(os.path.join(OUT, "nq_correlation.txt"), "w", encoding="utf-8") as fh:
        rho_full, rho_pit, nshared = nq_correlation(ps, fh)
    log(f"wrote nq_correlation.txt  rho_full={rho_full:+.3f} rho_pit={rho_pit:+.3f} n={nshared}")

    # machine summary line for REPORT cross-check
    log(f"SUMMARY nsess={ps['sess'].nunique()} pit_share={pit_share:.1f}% "
        f"rho_full={rho_full:+.3f} rho_pit={rho_pit:+.3f} nshared={nshared}")
    log("DONE.")


if __name__ == "__main__":
    main()
