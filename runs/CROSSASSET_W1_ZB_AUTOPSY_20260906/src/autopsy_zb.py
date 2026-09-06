"""
MARKET AUTOPSY -- ZB (CBOT 30-year US Treasury bond future, point value $1,000).

Cross-asset campaign Wave 1, descriptive science (Lane B). NOT a falsifiable test:
no ledger trial, no strategy, no P&L. Evidence status: DISCOVERY_CONSUMED.

DISCIPLINE (hard rules, enforced in-code):
  * POINTS BASIS ONLY. The substrate is ADDITIVELY back-adjusted continuous front-month:
    absolute levels are shifted, so every return / range / threshold is a POINT difference,
    never a percent of price and never a level threshold. (DELEV01 law; ZB especially.)
  * NATIVE SESSION determined from ZB's OWN volume profile -- NOT assumed to be NQ 09:30-16:00.
  * Hard-drop sessions >= 2026-08-01 at load; retained boundary printed.
  * Bars are END-stamped ET. Session (trade date) runs 18:00 ET -> 17:00 ET next day:
    a bar with hour >= 18 belongs to the NEXT calendar day's trade date.

Substrate:
  ZB: runs/SM1M_ZB_SUBSTRATE/out/zb_1m_2023_2026.parquet  (1/32 grid, $31.25/tick, $1000/pt)
  NQ: runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet      ($5/tick, $20/pt) -- for corr only
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import timedelta

pd.options.mode.chained_assignment = None

ROOT = Path(r"D:/OneDrive - Washington University in St. Louis/TradingResearch/systematic_research")
ZB_PARQUET = ROOT / "runs/SM1M_ZB_SUBSTRATE/out/zb_1m_2023_2026.parquet"
NQ_PARQUET = ROOT / "runs/SM1M_SUBSTRATE/out/nq_1m_2022_2026.parquet"
OUT = ROOT / "runs/CROSSASSET_W1_ZB_AUTOPSY_20260906/out"
OUT.mkdir(parents=True, exist_ok=True)

SEAL = pd.Timestamp("2026-08-01")     # drop trade-dates >= this
TICK = 1.0 / 32.0                     # 0.03125 pt
TICK_USD = 31.25
PT_USD_ZB = 1000.0
PT_USD_NQ = 20.0

# ---------------------------------------------------------------------------
def load_1m(path: Path, label: str) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df = df.sort_values("time").reset_index(drop=True)
    t = df["time"]
    # trade-date (session date): CME session 18:00 ET -> 17:00 ET next day.
    # END-stamped ET. hour >= 18 -> belongs to next calendar day's session.
    sess = t.dt.normalize()
    roll = t.dt.hour >= 18
    sess = sess.where(~roll, sess + pd.Timedelta(days=1))
    df["session"] = sess
    # HARD-DROP seal: sessions >= 2026-08-01
    n0 = len(df)
    df = df[df["session"] < SEAL].copy()
    dropped = n0 - len(df)
    df["clock_min"] = t.dt.hour * 60 + t.dt.minute
    df["dow"] = df["session"].dt.dayofweek  # 0=Mon .. 6=Sun (trade date; Sat/Sun should be empty)
    print(f"[{label}] rows={n0:,} retained={len(df):,} seal-dropped={dropped:,} "
          f"first_session={df['session'].min().date()} last_session={df['session'].max().date()}")
    assert df["session"].max() < SEAL, "SEAL VIOLATION"
    return df

# ---------------------------------------------------------------------------
def write(fname: str, text: str):
    p = OUT / fname
    p.write_text(text, encoding="utf-8")
    print(f"  wrote {p.name} ({len(text)} bytes)")

def acf(x: np.ndarray, lags: int) -> list[float]:
    x = x - np.nanmean(x)
    denom = np.nansum(x * x)
    out = []
    for k in range(1, lags + 1):
        num = np.nansum(x[:-k] * x[k:])
        out.append(num / denom if denom > 0 else np.nan)
    return out

def variance_ratio(r: np.ndarray, q: int) -> float:
    """Lo-MacKinlay style VR(q): var of q-period sums / (q * var of 1-period). >1 trend, <1 MR."""
    r = r[~np.isnan(r)]
    n = len(r)
    if n < q * 2:
        return np.nan
    mu = r.mean()
    var1 = np.sum((r - mu) ** 2) / (n - 1)
    # overlapping q-sums
    cs = np.cumsum(np.insert(r, 0, 0.0))
    qsum = cs[q:] - cs[:-q]
    m = len(qsum)
    varq = np.sum((qsum - q * mu) ** 2) / (m * q)  # unbiased-ish normalization by m*q
    return varq / var1 if var1 > 0 else np.nan

# ===========================================================================
def main():
    hdr = []
    hdr.append("=" * 96)
    hdr.append("ZB MARKET AUTOPSY -- descriptive science (Lane B), DISCOVERY_CONSUMED, POINTS BASIS")
    hdr.append("=" * 96)

    zb = load_1m(ZB_PARQUET, "ZB")
    # ------- meta / seal boundary line for the record -------
    boundary = (f"SEAL: hard-drop trade-dates >= {SEAL.date()}. "
                f"RETAINED window {zb['session'].min().date()} -> {zb['session'].max().date()} "
                f"({zb['session'].nunique()} sessions, {len(zb):,} 1-min bars).")
    print(boundary)

    # =====================================================================
    # (0) NATIVE SESSION -- volume profile by clock minute (ET)
    # =====================================================================
    vp = zb.groupby("clock_min")["volume"].agg(["sum", "mean", "count"]).reset_index()
    vp["hhmm"] = vp["clock_min"].apply(lambda m: f"{m//60:02d}:{m%60:02d}")
    total_vol = vp["sum"].sum()
    vp["vol_share"] = vp["sum"] / total_vol
    # hour-of-day profile
    zb["hour"] = zb["clock_min"] // 60
    hprof = zb.groupby("hour")["volume"].sum()
    hprof_share = (hprof / hprof.sum())
    # Find contiguous core window capturing bulk of volume: rank minutes by volume,
    # then report the smallest contiguous [a,b] clock window covering >= 80% of volume.
    order = vp.sort_values("sum", ascending=False)
    cum = order["vol_share"].cumsum()
    core_minutes = set(order.loc[cum <= 0.80, "clock_min"]) | {order.iloc[0]["clock_min"]}
    core_sorted = sorted(core_minutes)
    # contiguity summary: min/max of the 80% mass
    core_lo, core_hi = min(core_sorted), max(core_sorted)
    # peak minute
    peak = vp.loc[vp["sum"].idxmax()]

    sess_lines = []
    sess_lines.append("=" * 96)
    sess_lines.append("NATIVE SESSION DETERMINATION -- ZB volume profile by clock-minute (ET), all retained sessions")
    sess_lines.append("=" * 96)
    sess_lines.append(f"Full electronic container (data span): 18:00 ET -> 17:00 ET next day (maintenance 17:00-18:00).")
    sess_lines.append(f"Total volume = {total_vol:,.0f} contracts over {zb['session'].nunique()} sessions.")
    sess_lines.append("")
    sess_lines.append("Volume share by HOUR of day (ET):")
    for h in range(24):
        if h in hprof_share.index:
            bar = "#" * int(hprof_share[h] * 300)
            sess_lines.append(f"  {h:02d}:00  {hprof_share[h]*100:5.2f}%  {bar}")
    sess_lines.append("")
    sess_lines.append(f"Peak 1-min volume clock: {peak['hhmm']} ET (share {peak['vol_share']*100:.3f}%, mean {peak['mean']:.0f}/session)")
    sess_lines.append(f"Smallest set of clock-minutes covering 80% of volume spans {core_lo//60:02d}:{core_lo%60:02d} "
                      f".. {core_hi//60:02d}:{core_hi%60:02d} ET.")
    # top 15 minutes
    sess_lines.append("")
    sess_lines.append("Top 15 single clock-minutes by total volume (identifies data-release / open / close spikes):")
    for _, r in order.head(15).iterrows():
        sess_lines.append(f"  {r['hhmm']} ET  share {r['vol_share']*100:5.3f}%  mean/session {r['mean']:7.0f}")
    # decide the RTH-equivalent window from the profile:
    # US Treasury cash & pit liquidity => report the found window explicitly.
    sess_lines.append("")

    # Choose RTH-equivalent window = contiguous clock block [RTH_LO,RTH_HI) that we will use
    # for "session vs overnight". Derived from profile below (printed) not assumed.
    # We compute cumulative volume by clock and find the tightest 90%-mass contiguous window.
    vp_sorted = vp.sort_values("clock_min")
    vols = vp_sorted.set_index("clock_min")["sum"].reindex(range(0, 1440), fill_value=0).values
    best = None
    target = 0.90 * total_vol
    csum = np.cumsum(vols)
    # sliding contiguous window in clock space (wrap not needed: RTH is a daytime block)
    for a in range(0, 1440):
        # find minimal b>=a with window mass >= target
        need = (csum[a-1] if a > 0 else 0) + target
        b = np.searchsorted(csum, need)
        if b < 1440:
            width = b - a
            if best is None or width < best[2]:
                best = (a, b, width)
    W90_LO, W90_HI = best[0], best[1]
    sess_lines.append(f"Tightest contiguous clock window holding 90% of volume: "
                      f"{W90_LO//60:02d}:{W90_LO%60:02d} -> {W90_HI//60:02d}:{W90_HI%60:02d} ET "
                      f"(width {best[2]} min).")
    sess_lines.append("  ^ FINDING: this window is ~13h wide -- ZB is a genuine near-24h market with")
    sess_lines.append("    real European-hours liquidity (02:00-07:00 ET carries ~15% of volume), UNLIKE")
    sess_lines.append("    the equity indices whose overnight is nearly dead. The 'overnight' is NOT empty.")
    sess_lines.append("")
    # ADOPTED partition: the US cash-Treasury / CBOT day session. The hour profile makes the
    # choice unambiguous: volume steps 3.7% (07h) -> 11.8% (08h) at 08:00 ET and stays >6.5%
    # through 16:00 ET (~73% of all volume in this 8h block), bracketing the 08:20 pit open,
    # the 08:30 data releases (highest-vol minutes), and the settlement runup into 16:00 ET.
    RTH_LO, RTH_HI = 8 * 60, 16 * 60 + 1      # stamps 08:00..16:00 ET (incl. 16:00 settlement bar)
    sess_lines.append("ADOPTED SESSION PARTITION for this autopsy (economically grounded in the profile):")
    sess_lines.append(f"  RTH-equivalent (US cash-Treasury day) session : [08:00, 16:00) ET  "
                      f"(~73% of volume in 8h; brackets 08:20 pit open, 08:30 data, 16:00 settlement)")
    sess_lines.append(f"  Overnight (ETH)                               : complement within the 18:00->17:00 container")
    sess_lines.append(f"  NOTE: unlike NQ 09:30-16:00, ZB's day session STARTS at 08:00 ET (data-release driven)")
    sess_lines.append(f"        and its overnight is materially liquid -- both facts drive the structure below.")
    write("session_native.txt", "\n".join(hdr + [boundary, ""] + sess_lines))

    # tag each bar RTH vs overnight
    zb["is_rth"] = (zb["clock_min"] >= RTH_LO) & (zb["clock_min"] < RTH_HI)

    # =====================================================================
    # Per-session aggregates (points basis)
    # =====================================================================
    zb["ret1"] = zb["close"].diff()  # 1-min close-to-close point return (masked at session breaks below)
    # mask first bar of each session
    first_mask = zb["session"] != zb["session"].shift(1)
    zb.loc[first_mask, "ret1"] = np.nan

    g = zb.groupby("session")
    sess_df = pd.DataFrame({
        "open": g["open"].first(),
        "high": g["high"].max(),
        "low": g["low"].min(),
        "close": g["close"].last(),
        "vol": g["volume"].sum(),
        "n": g["close"].count(),
    })
    sess_df["dow"] = sess_df.index.dayofweek
    sess_df["cc_ret"] = sess_df["close"].diff()          # close-to-close point return
    sess_df["oc_ret"] = sess_df["close"] - sess_df["open"]
    sess_df["range"] = sess_df["high"] - sess_df["low"]
    sess_df["prev_close"] = sess_df["close"].shift(1)

    # RTH sub-session aggregates
    grth = zb[zb["is_rth"]].groupby("session")
    rth_df = pd.DataFrame({
        "rth_open": grth["open"].first(),
        "rth_high": grth["high"].max(),
        "rth_low": grth["low"].min(),
        "rth_close": grth["close"].last(),
        "rth_vol": grth["volume"].sum(),
        "rth_n": grth["close"].count(),
    })
    gon = zb[~zb["is_rth"]].groupby("session")
    on_df = pd.DataFrame({
        "on_high": gon["high"].max(),
        "on_low": gon["low"].min(),
        "on_close": gon["close"].last(),
        "on_vol": gon["volume"].sum(),
        "on_n": gon["close"].count(),
    })
    S = sess_df.join(rth_df).join(on_df)
    S["rth_range"] = S["rth_high"] - S["rth_low"]
    S["rth_ret"] = S["rth_close"] - S["rth_open"]                # RTH open->close
    S["prev_rth_close"] = S["rth_close"].shift(1)
    S["overnight_ret"] = S["rth_open"] - S["prev_rth_close"]     # prior RTH close -> today RTH open (gap+ETH)
    S["on_range"] = S["on_high"] - S["on_low"]

    # =====================================================================
    # (1) RETURNS
    # =====================================================================
    R = []
    R.append("=" * 96)
    R.append("RETURNS (POINTS). $/pt(ZB)=1000; 1 tick=1/32=0.03125 pt=$31.25.")
    R.append("=" * 96)

    # ---- point-return by time of day (hour bucket): mean 1-min ret, sum, std ----
    tod = zb.dropna(subset=["ret1"]).groupby("hour")["ret1"].agg(["mean", "std", "sum", "count"])
    R.append("\n[1a] Mean 1-min point-return by HOUR of day (ET) -- drift concentration:")
    R.append(f"{'hour':>5} {'mean_pt':>10} {'std_pt':>10} {'sum_pt':>12} {'n':>9} {'mean_usd':>10}")
    for h, row in tod.iterrows():
        R.append(f"{h:5d} {row['mean']:10.6f} {row['std']:10.5f} {row['sum']:12.3f} {int(row['count']):9d} {row['mean']*PT_USD_ZB:10.4f}")
    # 30-min TOD table -> CSV
    zb["b30"] = (zb["clock_min"] // 30) * 30
    tod30 = zb.dropna(subset=["ret1"]).groupby("b30")["ret1"].agg(["mean", "std", "sum", "count"]).reset_index()
    tod30["hhmm"] = tod30["b30"].apply(lambda m: f"{m//60:02d}:{m%60:02d}")
    tod30["mean_usd"] = tod30["mean"] * PT_USD_ZB
    tod30 = tod30[["b30", "hhmm", "mean", "std", "sum", "count", "mean_usd"]]
    tod30.columns = ["clock_min_start", "hhmm_et", "mean_ret_pt", "std_ret_pt", "sum_ret_pt", "n_bars", "mean_ret_usd"]
    tod30.to_csv(OUT / "returns_by_tod.csv", index=False)
    print(f"  wrote returns_by_tod.csv ({len(tod30)} rows)")

    # ---- by day-of-week (session close-to-close) ----
    R.append("\n[1b] Session close-to-close point-return by DAY-OF-WEEK (trade date):")
    R.append(f"{'dow':>10} {'mean_pt':>10} {'std_pt':>10} {'n':>6} {'mean_usd':>10} {'t':>7}")
    dows = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    ccd = S.dropna(subset=["cc_ret"])
    for d in range(7):
        sub = ccd[ccd["dow"] == d]["cc_ret"]
        if len(sub) == 0:
            continue
        t = sub.mean() / (sub.std() / np.sqrt(len(sub))) if sub.std() > 0 else np.nan
        R.append(f"{dows[d]:>10} {sub.mean():10.4f} {sub.std():10.4f} {len(sub):6d} {sub.mean()*PT_USD_ZB:10.2f} {t:7.2f}")

    # ---- session (RTH open->close) vs overnight (prior RTH close -> RTH open) ----
    R.append("\n[1c] RTH-day return (open->close) vs OVERNIGHT return (prior RTH close -> RTH open), points:")
    for name, col in [("RTH day (open->close)", "rth_ret"), ("Overnight (ETH+gap)", "overnight_ret"),
                      ("Full session (close->close)", "cc_ret")]:
        sub = S[col].dropna()
        t = sub.mean() / (sub.std() / np.sqrt(len(sub))) if sub.std() > 0 else np.nan
        R.append(f"  {name:32s} mean {sub.mean():8.4f} pt  (${sub.mean()*PT_USD_ZB:8.2f})  std {sub.std():7.3f}  n {len(sub):4d}  t {t:6.2f}  sum {sub.sum():9.2f}")

    # ---- conditional on prior-day sign ----
    R.append("\n[1d] Today session cc-return CONDITIONAL on PRIOR-session cc-return sign (persistence vs reversal):")
    ccd2 = S.dropna(subset=["cc_ret"]).copy()
    ccd2["prev_cc"] = ccd2["cc_ret"].shift(1)
    ccd2 = ccd2.dropna(subset=["prev_cc"])
    for lbl, cond in [("prior UP  (>0)", ccd2["prev_cc"] > 0), ("prior DOWN (<0)", ccd2["prev_cc"] < 0)]:
        sub = ccd2.loc[cond, "cc_ret"]
        t = sub.mean() / (sub.std() / np.sqrt(len(sub))) if sub.std() > 0 else np.nan
        R.append(f"  after {lbl:16s}: next cc mean {sub.mean():8.4f} pt  n {len(sub):4d}  t {t:6.2f}")
    # correlation prev->next
    rho_pp = ccd2[["prev_cc", "cc_ret"]].corr().iloc[0, 1]
    R.append(f"  corr(prev_cc, next_cc) = {rho_pp:+.4f}  (daily return autocorr lag-1)")

    # ---- conditional on overnight sign -> RTH day return ----
    R.append("\n[1e] RTH-day return CONDITIONAL on OVERNIGHT return sign (does the gap continue or fade in RTH?):")
    ov = S.dropna(subset=["overnight_ret", "rth_ret"])
    for lbl, cond in [("overnight UP  (>0)", ov["overnight_ret"] > 0), ("overnight DOWN (<0)", ov["overnight_ret"] < 0)]:
        sub = ov.loc[cond, "rth_ret"]
        t = sub.mean() / (sub.std() / np.sqrt(len(sub))) if sub.std() > 0 else np.nan
        R.append(f"  {lbl:20s}: RTH mean {sub.mean():8.4f} pt  n {len(sub):4d}  t {t:6.2f}")
    rho_on = ov[["overnight_ret", "rth_ret"]].corr().iloc[0, 1]
    R.append(f"  corr(overnight_ret, rth_ret) = {rho_on:+.4f}")
    write("returns.txt", "\n".join(R))

    # =====================================================================
    # (2) DISTRIBUTION
    # =====================================================================
    from scipy import stats as st
    D = []
    D.append("=" * 96)
    D.append("DISTRIBUTION (POINTS). All figures point differences; NO percent-of-price (DELEV01).")
    D.append("=" * 96)

    r1 = zb["ret1"].dropna().values
    rd = S["cc_ret"].dropna().values

    def dist_block(name, x, unit_usd):
        b = []
        q = np.percentile(x, [0.1, 1, 5, 25, 50, 75, 95, 99, 99.9])
        b.append(f"\n[{name}]  n={len(x):,}")
        b.append(f"  mean {x.mean():.6f} pt   std {x.std():.5f} pt   (std ${x.std()*unit_usd:,.2f})")
        b.append(f"  skew {st.skew(x):+.4f}   excess-kurtosis {st.kurtosis(x):+.4f}")
        b.append(f"  min {x.min():+.4f}  max {x.max():+.4f}  pt")
        b.append(f"  quantiles pt [0.1,1,5,25,50,75,95,99,99.9]:")
        b.append("    " + "  ".join(f"{v:+.4f}" for v in q))
        return b

    D += dist_block("1-min close-to-close point return", r1, PT_USD_ZB)
    D += dist_block("Daily (session) close-to-close point return", rd, PT_USD_ZB)

    # tails: extreme 1-min move frequency (in ticks)
    D.append("\n[2a] Extreme 1-min move frequency (|point ret| thresholds):")
    tot1 = len(r1)
    for th_ticks in [2, 4, 8, 16, 32]:
        th = th_ticks * TICK
        cnt = int((np.abs(r1) >= th).sum())
        D.append(f"  |ret| >= {th_ticks:3d} ticks ({th:6.4f} pt = ${th*PT_USD_ZB:7.2f}): "
                 f"{cnt:7d} bars  {cnt/tot1*100:7.4f}%  ~1 per {tot1/cnt:,.0f} bars" if cnt else
                 f"  |ret| >= {th_ticks:3d} ticks: 0")

    # tail ratio vs normal
    for x, nm in [(r1, "1-min"), (rd, "daily")]:
        sd = x.std()
        emp99 = np.percentile(np.abs(x), 99)
        norm99 = 2.576 * sd
        D.append(f"  {nm}: empirical |99th| = {emp99:.4f} pt vs Gaussian 2.576*sd = {norm99:.4f} pt  "
                 f"(fat-tail ratio {emp99/norm99:.2f}x)")

    # ---- gap distribution (overnight_ret = prior RTH close -> RTH open) ----
    gap = S["overnight_ret"].dropna().values
    D.append("\n[2b] OVERNIGHT GAP distribution (prior RTH close -> today RTH open), points:")
    gq = np.percentile(gap, [1, 5, 25, 50, 75, 95, 99])
    D.append(f"  mean {gap.mean():+.4f}  std {gap.std():.4f}  skew {st.skew(gap):+.3f}  kurt {st.kurtosis(gap):+.3f}  n {len(gap)}")
    D.append(f"  quantiles pt [1,5,25,50,75,95,99]: " + "  ".join(f"{v:+.4f}" for v in gq))
    # gap as fraction of RTH range
    gr = (np.abs(S["overnight_ret"]) / S["rth_range"]).replace([np.inf], np.nan).dropna()
    D.append(f"  median |gap| / RTH-range = {gr.median():.3f}")

    # ---- intraday (RTH) range vs overnight range ----
    D.append("\n[2c] RTH-day range vs OVERNIGHT range (points):")
    for nm, col in [("RTH range", "rth_range"), ("Overnight range", "on_range"), ("Full-session range", "range")]:
        sub = S[col].dropna()
        D.append(f"  {nm:20s} mean {sub.mean():7.4f}  median {sub.median():7.4f}  std {sub.std():7.4f}  p95 {np.percentile(sub,95):7.4f}")
    frac = (S["rth_range"] / S["range"]).dropna()
    D.append(f"  median RTH-range / full-session-range = {frac.median():.3f}  (share of daily range made in RTH)")

    # ---- realized vol (daily, from 1-min pt returns) ----
    rv = zb.dropna(subset=["ret1"]).groupby("session")["ret1"].apply(lambda s: np.sqrt(np.sum(s.values**2)))
    D.append("\n[2d] Daily realized volatility (sqrt sum of 1-min squared point returns), points:")
    D.append(f"  mean {rv.mean():.4f}  median {rv.median():.4f}  std {rv.std():.4f}  "
             f"p5 {np.percentile(rv,5):.4f}  p95 {np.percentile(rv,95):.4f}  n {len(rv)}")
    D.append(f"  in $: mean daily RV ~= ${rv.mean()*PT_USD_ZB:,.0f}")
    write("distribution.txt", "\n".join(D))

    # =====================================================================
    # (3) DEPENDENCE
    # =====================================================================
    DE = []
    DE.append("=" * 96)
    DE.append("DEPENDENCE (POINTS).")
    DE.append("=" * 96)

    DE.append("\n[3a] Return autocorrelation:")
    ac1 = acf(r1, 10)
    DE.append("  1-min ret ACF lags 1..10:")
    DE.append("    " + "  ".join(f"{v:+.4f}" for v in ac1))
    acd = acf(rd, 10)
    DE.append("  daily ret ACF lags 1..10:")
    DE.append("    " + "  ".join(f"{v:+.4f}" for v in acd))

    DE.append("\n[3b] Sign persistence P(next same sign | this sign):")
    for x, nm in [(r1, "1-min"), (rd, "daily")]:
        s = np.sign(x)
        s = s[s != 0]
        same = np.mean(s[1:] == s[:-1])
        pu = np.mean(x > 0)
        DE.append(f"  {nm}: P(same sign) = {same:.4f}   P(up) = {pu:.4f}   base-rate if iid = "
                  f"{pu**2 + (1-pu)**2:.4f}")

    DE.append("\n[3c] Volatility autocorrelation (ACF of |ret|):")
    av1 = acf(np.abs(r1), 10)
    DE.append("  |1-min ret| ACF lags 1..10:")
    DE.append("    " + "  ".join(f"{v:+.4f}" for v in av1))
    avd = acf(np.abs(rd), 10)
    DE.append("  |daily ret| ACF lags 1..10:")
    DE.append("    " + "  ".join(f"{v:+.4f}" for v in avd))
    # daily RV autocorr
    acrv = acf(rv.values, 10)
    DE.append("  daily RV ACF lags 1..10 (vol clustering):")
    DE.append("    " + "  ".join(f"{v:+.4f}" for v in acrv))

    DE.append("\n[3d] Variance ratio VR(q) (Lo-MacKinlay; >1 trend, <1 mean-revert):")
    DE.append("  1-min returns:  " + "  ".join(f"VR({q})={variance_ratio(r1,q):.3f}" for q in [2,5,10,30,60]))
    DE.append("  daily returns:  " + "  ".join(f"VR({q})={variance_ratio(rd,q):.3f}" for q in [2,3,5,10,20]))

    DE.append("\n[3e] Conditional continuation vs reversal after a LARGE 1-min move (top-decile |ret|):")
    thr = np.percentile(np.abs(r1), 90)
    # build next-bar return within same session
    zz = zb.dropna(subset=["ret1"]).copy()
    zz["next"] = zz.groupby("session")["ret1"].shift(-1)
    big = zz.dropna(subset=["next"])
    up = big[(big["ret1"] >= thr)]
    dn = big[(big["ret1"] <= -thr)]
    DE.append(f"  large-move threshold (90th pct |1-min ret|) = {thr:.4f} pt")
    DE.append(f"  after large UP  : next-bar mean {up['next'].mean():+.5f} pt  (n {len(up)})  "
              f"[continuation if >0]")
    DE.append(f"  after large DOWN: next-bar mean {dn['next'].mean():+.5f} pt  (n {len(dn)})  "
              f"[continuation if <0]")
    # signed continuation measure
    cont = np.concatenate([up["next"].values, -dn["next"].values])
    DE.append(f"  signed continuation (dir-aligned next-bar mean) = {cont.mean():+.5f} pt  "
              f"(>0 momentum, <0 reversal)")
    write("dependence.txt", "\n".join(DE))

    # =====================================================================
    # (4) PATH
    # =====================================================================
    P = []
    P.append("=" * 96)
    P.append("PATH (POINTS). Efficiency, MFE/MAE, tortuosity, compression/expansion.")
    P.append("=" * 96)

    # efficiency ratio per RTH session = |close-open| / sum|1-min moves|
    def path_stats(sub_df, label):
        recs = []
        for sess, grp in sub_df.groupby("session"):
            c = grp["close"].values
            o = grp["open"].values[0]
            if len(c) < 5:
                continue
            moves = np.abs(np.diff(np.concatenate([[o], c])))
            path_len = moves.sum()
            net = c[-1] - o
            hi = grp["high"].max(); lo = grp["low"].min()
            er = abs(net) / path_len if path_len > 0 else np.nan
            # MFE/MAE from open, long perspective
            mfe = hi - o
            mae = o - lo
            rng = hi - lo
            recs.append((er, net, path_len, mfe, mae, rng))
        arr = np.array(recs)
        return arr

    rth_bars = zb[zb["is_rth"]]
    A = path_stats(rth_bars, "RTH")
    er, net, plen, mfe, mae, rng = A[:,0], A[:,1], A[:,2], A[:,3], A[:,4], A[:,5]
    P.append(f"\n[4a] Kaufman EFFICIENCY RATIO over RTH day (|net|/path-length), n={len(A)}:")
    P.append(f"  mean {np.nanmean(er):.4f}  median {np.nanmedian(er):.4f}  "
             f"p25 {np.nanpercentile(er,25):.4f}  p75 {np.nanpercentile(er,75):.4f}")
    P.append(f"  (near 0 = choppy/mean-reverting path; near 1 = clean directional path)")
    P.append(f"\n[4b] TORTUOSITY = path-length/|net| (RTH), higher = more winding:")
    tort = plen / np.abs(net)
    tort = tort[np.isfinite(tort)]
    P.append(f"  median {np.median(tort):.2f}  mean {np.mean(tort):.2f}  "
             f"(reciprocal of efficiency; median path is ~{np.median(tort):.1f}x the net displacement)")

    P.append(f"\n[4c] MFE / MAE from RTH open (long perspective), points:")
    P.append(f"  MFE (open->high): mean {mfe.mean():.4f}  median {np.median(mfe):.4f}  p95 {np.percentile(mfe,95):.4f}")
    P.append(f"  MAE (open->low) : mean {mae.mean():.4f}  median {np.median(mae):.4f}  p95 {np.percentile(mae,95):.4f}")
    P.append(f"  MFE/MAE symmetry ratio (mean) = {mfe.mean()/mae.mean():.3f}  (>1 favors long, <1 favors short from open)")
    P.append(f"  median RTH range = {np.median(rng):.4f}; net move as frac of range: "
             f"median {np.median(np.abs(net)/rng):.3f}")

    # compression/expansion: does small RTH range predict large next range?
    P.append("\n[4d] COMPRESSION -> EXPANSION (range autocorr & NR-style conditioning):")
    rr = S["rth_range"].dropna()
    acr = acf(rr.values, 5)
    P.append("  RTH-range ACF lags 1..5: " + "  ".join(f"{v:+.4f}" for v in acr))
    # bottom-quartile range day -> next-day range vs top-quartile
    tmp = S[["rth_range"]].dropna().copy()
    tmp["next_range"] = tmp["rth_range"].shift(-1)
    tmp = tmp.dropna()
    q1 = tmp["rth_range"].quantile(0.25); q3 = tmp["rth_range"].quantile(0.75)
    lo_next = tmp.loc[tmp["rth_range"] <= q1, "next_range"]
    hi_next = tmp.loc[tmp["rth_range"] >= q3, "next_range"]
    P.append(f"  after BOTTOM-quartile range day: next-day RTH range mean {lo_next.mean():.4f}")
    P.append(f"  after TOP-quartile    range day: next-day RTH range mean {hi_next.mean():.4f}")
    P.append(f"  (expansion-after-compression would show LOWER-after-low; clustering shows the opposite)")
    write("path.txt", "\n".join(P))

    # =====================================================================
    # (5) SESSION STRUCTURE
    # =====================================================================
    SS = []
    SS.append("=" * 96)
    SS.append("SESSION STRUCTURE (POINTS). Overnight levels, opening range, gap, prior-day levels.")
    SS.append("=" * 96)

    # overnight high/low takeout by RTH
    ov2 = S.dropna(subset=["on_high", "on_low", "rth_high", "rth_low"])
    took_hi = (ov2["rth_high"] > ov2["on_high"]).mean()
    took_lo = (ov2["rth_low"] < ov2["on_low"]).mean()
    took_both = ((ov2["rth_high"] > ov2["on_high"]) & (ov2["rth_low"] < ov2["on_low"])).mean()
    took_neither = ((ov2["rth_high"] <= ov2["on_high"]) & (ov2["rth_low"] >= ov2["on_low"])).mean()
    SS.append("\n[5a] Overnight (ETH) high/low TAKEOUT by the RTH day:")
    SS.append(f"  RTH takes out overnight HIGH: {took_hi*100:.2f}%   overnight LOW: {took_lo*100:.2f}%")
    SS.append(f"  takes out BOTH: {took_both*100:.2f}%   NEITHER (RTH inside ON range): {took_neither*100:.2f}%")

    # opening range: first 30 & 60 min of RTH
    def or_stats(minutes):
        recs = []
        for sess, grp in rth_bars.groupby("session"):
            if len(grp) < minutes + 5:
                continue
            org = grp.iloc[:minutes]
            or_hi = org["high"].max(); or_lo = org["low"].min()
            rest = grp.iloc[minutes:]
            r_hi = rest["high"].max(); r_lo = rest["low"].min()
            day_hi = grp["high"].max(); day_lo = grp["low"].min()
            broke_up = r_hi > or_hi
            broke_dn = r_lo < or_lo
            or_is_dayhi = (or_hi >= day_hi - 1e-9)
            or_is_daylo = (or_lo <= day_lo + 1e-9)
            recs.append((or_hi - or_lo, broke_up, broke_dn, or_is_dayhi, or_is_daylo))
        arr = np.array(recs, dtype=float)
        return arr

    for mins in [30, 60]:
        a = or_stats(mins)
        SS.append(f"\n[5b] OPENING RANGE (first {mins} min of RTH), n={len(a)}:")
        SS.append(f"  OR width: mean {a[:,0].mean():.4f} pt  median {np.median(a[:,0]):.4f} pt")
        SS.append(f"  rest-of-day breaks OR high: {a[:,1].mean()*100:.2f}%   breaks OR low: {a[:,2].mean()*100:.2f}%")
        SS.append(f"  OR high == day high: {a[:,3].mean()*100:.2f}%   OR low == day low: {a[:,4].mean()*100:.2f}%")
        SS.append(f"  (session extreme set inside the OR => opening range holds the day extreme)")

    # gap fill rate: does RTH trade back to prior RTH close?
    gp = S.dropna(subset=["overnight_ret", "rth_low", "rth_high", "prev_rth_close"]).copy()
    up_gap = gp[gp["overnight_ret"] > 0]
    dn_gap = gp[gp["overnight_ret"] < 0]
    # gap fills if RTH trades back through prior close
    up_fill = (up_gap["rth_low"] <= up_gap["prev_rth_close"]).mean()
    dn_fill = (dn_gap["rth_high"] >= dn_gap["prev_rth_close"]).mean()
    SS.append("\n[5c] GAP FILL (RTH trades back to prior RTH close), points basis:")
    SS.append(f"  up-gap  fill rate: {up_fill*100:.2f}%  (n {len(up_gap)}, mean gap {up_gap['overnight_ret'].mean():.4f} pt)")
    SS.append(f"  down-gap fill rate: {dn_fill*100:.2f}%  (n {len(dn_gap)}, mean gap {dn_gap['overnight_ret'].mean():.4f} pt)")

    # prior-day level interaction: RTH takes out prior day RTH high/low
    pl = S.dropna(subset=["rth_high", "rth_low"]).copy()
    pl["pdh"] = pl["rth_high"].shift(1)
    pl["pdl"] = pl["rth_low"].shift(1)
    pl["pdc"] = pl["rth_close"].shift(1)
    pl = pl.dropna(subset=["pdh", "pdl"])
    took_pdh = (pl["rth_high"] > pl["pdh"]).mean()
    took_pdl = (pl["rth_low"] < pl["pdl"]).mean()
    inside = ((pl["rth_high"] <= pl["pdh"]) & (pl["rth_low"] >= pl["pdl"])).mean()
    SS.append("\n[5d] PRIOR-DAY LEVEL interaction (today RTH vs prior-day RTH high/low):")
    SS.append(f"  takes out prior-day HIGH: {took_pdh*100:.2f}%   prior-day LOW: {took_pdl*100:.2f}%")
    SS.append(f"  INSIDE prior-day range (neither): {inside*100:.2f}%")
    write("session.txt", "\n".join(SS))

    # =====================================================================
    # (6) CORRELATION TO NQ (diversification pre-read) -- points-return basis
    # =====================================================================
    C = []
    C.append("=" * 96)
    C.append("DAILY POINT-RETURN CORRELATION TO NQ (diversification pre-read)")
    C.append("=" * 96)
    nq = load_1m(NQ_PARQUET, "NQ")
    nq_cc = nq.groupby("session")["close"].last().diff().rename("nq_cc")
    zb_cc = S["cc_ret"].rename("zb_cc")
    join = pd.concat([zb_cc, nq_cc], axis=1).dropna()
    rho = join["zb_cc"].corr(join["nq_cc"])
    rho_sp = join["zb_cc"].corr(join["nq_cc"], method="spearman")
    # also RTH-window aligned (both use their own RTH? here NQ RTH is 09:30-16:00 std; ZB uses its own)
    C.append(f"  shared trade-dates: {len(join)}  ({join.index.min().date()} -> {join.index.max().date()})")
    C.append(f"  Pearson rho(daily cc point-return, ZB vs NQ)  = {rho:+.4f}")
    C.append(f"  Spearman rho                                  = {rho_sp:+.4f}")
    # sign co-movement
    both_up = ((join["zb_cc"] > 0) & (join["nq_cc"] > 0)).mean()
    opp = ((join["zb_cc"] > 0) != (join["nq_cc"] > 0)).mean()
    C.append(f"  P(both up) {both_up*100:.1f}%   P(opposite sign) {opp*100:.1f}%")
    # rolling stability
    join["yr"] = join.index.year
    C.append("  per-year Pearson rho:")
    for yr, sub in join.groupby("yr"):
        if len(sub) > 20:
            C.append(f"    {yr}: rho {sub['zb_cc'].corr(sub['nq_cc']):+.4f}  (n {len(sub)})")
    C.append(f"\n  READ: |rho| ~ {abs(rho):.2f} -> {'strongly diversifying (near-zero/negative)' if abs(rho)<0.2 else 'partially correlated'}")
    write("correlation_nq.txt", "\n".join(C))

    print("\nDONE. Outputs in", OUT)
    # return key numbers for the report
    return {
        "boundary": boundary, "RTH_LO": RTH_LO, "RTH_HI": RTH_HI, "rho_nq": rho,
        "n_sessions": int(zb["session"].nunique()),
    }

if __name__ == "__main__":
    main()
