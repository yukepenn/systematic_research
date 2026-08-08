"""W9-1 — B1 overnight premium: the 2006+ resolution (amended decay-aware verdict).

Frozen spec: research/scalping_lab/specs/W9_nq_minute_resolutions.md (frozen d7dfdad,
INCLUDING the 2026-08-08 decay amendment, committed before any readout).

Construction identical to W5-B1 (src/python/w5_b1_overnight.py), ported to the 1-min
substrate research/scalping_lab/substrate/minute/NQ/nq1m_2005_202605.parquet
(NT8 cache, ACTUAL range 2006-01-05 .. 2026-05-29 — the study is "2006+"):
  long 1 NQ at the LAST bar end-stamped <= 16:45 ET of session S (close),
  exit at session S+1's FIRST bar end-stamped >= 09:30 ET (close, <= 17:00 guard).
Friction 2.0t primary / 2.872t stress; 1 tick = 0.25 pt = $5.
8-sigma roll/outlier detector (full-sample sigma of gross ticks) with WITH/WITHOUT rows.

Minute-substrate adaptation (disclosed): pre-Nov-2012 Fridays closed 16:15 ET, so the
last bar <= 16:45 on those days is the genuine pre-weekend close stamped ~16:15.
Entry accepted iff staleness (16:45 - entry stamp) <= 30 min; sessions whose last
bar <= 16:45 is staler (13:00/13:15 holiday early closes etc.) are dropped, matching
W5-B1's exclusion of early-close sessions.

AMENDED verdict (ALL four required; any failure => B1 CLOSED, adequate power):
 (a) full-sample net(2.0t) >= +4 t/night with night-clustered bootstrap CI_lo > 0;
 (b) NO significant negative time trend: nightly net regressed on night index,
     HC1-robust t; FAIL iff slope < 0 and t <= -1.96. Rolling 2-year (730D) mean
     series saved to CSV;
 (c) the most recent 4-year block (2022 -> 2026-05) POINT estimate > 0;
 (d) rho (Pearson) vs Solar net_v1 on the 2022+ overlap < 0.3.
A pass driven by pre-2015 with a dying trend = FAIL — the binding clause is stated.

Also reported: 4-year-block table with by-era medians, down-prior-RTH conditional,
top-10-nights-removed sensitivity, per-year table, W5-B1 2022+ reconciliation
(must match +17.211 t/night within tolerance).

Contamination rule: NOTHING beyond 2026-05-31 is read into analysis (bars and Solar
ledger truncated at load). Seed 20260808; 1000 bootstrap reps; night-clustered CIs.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]  # systematic_research/
BARS_PARQUET = ROOT / "research" / "scalping_lab" / "substrate" / "minute" / "NQ" / "nq1m_2005_202605.parquet"
SOLAR_CSV = ROOT / "runs" / "E10MASTER_V2" / "out" / "daily_v1_v2.csv"
ART = ROOT / "research" / "scalping_lab" / "artifacts" / "w9_b1"

DEV_CUTOFF = pd.Timestamp("2026-06-01 00:00:00")  # exchange ET, exclusive
SEED = 20260808
N_BOOT = 1000                       # per W9 task directive (W5 used 10k)
FRICTION_PRIMARY_T = 2.0
FRICTION_STRESS_T = 2.872
TICKS_PER_PT = 4.0
USD_PER_TICK = 5.0
OUTLIER_SIGMA = 8.0
MAX_ENTRY_STALE_MIN = 30.0          # accepts pre-Nov-2012 Friday 16:15 closes; drops holiday early closes

# W5-B1 frozen reference (research/scalping_lab/artifacts/w5_b1/w5b1_summary.csv, ALL row)
W5_REF_MEAN_T = 17.210622710622711
W5_REF_N = 1092
RECON_TOL_T = 1.5                   # declared tolerance on the 2022+ subset mean


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)

    def flush(self):
        for st in self.streams:
            st.flush()


def boot_ci(x: np.ndarray, rng: np.random.Generator, n_boot: int = N_BOOT):
    """Night-clustered 95% CI on the mean: each night is one cluster; resample
    nights with replacement."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    if n == 0:
        return np.nan, np.nan, np.nan
    if n == 1:
        return float(x[0]), np.nan, np.nan
    idx = rng.integers(0, n, size=(n_boot, n))
    means = x[idx].mean(axis=1)
    return float(x.mean()), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def group_stats(name, net2, net2872, gross, rng):
    m2, lo2, hi2 = boot_ci(net2, rng)
    m2872, lo2872, hi2872 = boot_ci(net2872, rng)
    return {
        "group": name,
        "n_nights": len(net2),
        "gross_mean_t": float(np.mean(gross)) if len(gross) else np.nan,
        "net2.0_mean_t": m2,
        "net2.0_ci_lo": lo2,
        "net2.0_ci_hi": hi2,
        "net2.872_mean_t": m2872,
        "net2.872_ci_lo": lo2872,
        "net2.872_ci_hi": hi2872,
        "hit_rate_net2.0": float(np.mean(net2 > 0)) if len(net2) else np.nan,
        "std_gross_t": float(np.std(gross, ddof=1)) if len(gross) > 1 else np.nan,
        "median_net2.0_t": float(np.median(net2)) if len(net2) else np.nan,
    }


def ols_hc1(y: np.ndarray, x: np.ndarray):
    """OLS y = a + b*x with HC1 heteroskedasticity-robust SE on b.
    Each night is one observation = one cluster, so HC == cluster-robust here."""
    y = np.asarray(y, float)
    x = np.asarray(x, float)
    n = len(y)
    X = np.column_stack([np.ones(n), x])
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ (X.T @ y)
    e = y - X @ beta
    k = X.shape[1]
    meat = (X * (e ** 2)[:, None]).T @ X * (n / (n - k))
    cov = XtX_inv @ meat @ XtX_inv
    se_b = float(np.sqrt(cov[1, 1]))
    return float(beta[0]), float(beta[1]), se_b, float(beta[1] / se_b)


def main():
    ART.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("W9-1  B1 overnight premium — the 2006+ resolution (amended decay-aware verdict)")
    print("Spec frozen at d7dfdad (incl. decay amendment) BEFORE this readout.")
    print("=" * 78)

    # ---- Load 1-min bars; enforce contamination rule immediately at load ----
    df = pd.read_parquet(BARS_PARQUET)
    df["time"] = pd.to_datetime(df["time"])
    n_raw = len(df)
    df = df[df["time"] < DEV_CUTOFF].sort_values("time").reset_index(drop=True)
    print(f"Bars loaded: {n_raw} rows raw; {len(df)} kept after dev-window truncation at "
          f"{DEV_CUTOFF} (exclusive); {n_raw - len(df)} rows dropped unread.")
    print(f"Bar stamp range kept: {df['time'].iloc[0]} -> {df['time'].iloc[-1]} "
          f"(exchange ET, END-stamped; verified: evening opens stamp 18:01, closes 17:00)")

    # ---- Sessions: END-stamped bar with stamp > 17:00 belongs to next day's session ----
    tod_min = df["time"].dt.hour * 60 + df["time"].dt.minute
    df["session_date"] = df["time"].dt.normalize() + pd.to_timedelta(
        (tod_min > 17 * 60).astype(int), unit="D")
    sess_dates = np.sort(df["session_date"].unique())
    sid_map = pd.Series(np.arange(len(sess_dates)), index=sess_dates)
    df["sid"] = sid_map.loc[df["session_date"]].values
    n_sessions = len(sess_dates)
    print(f"Sessions: {n_sessions} (18:00 ET prior day -> 17:00 ET session date; "
          f"stamp>17:00 => next session date)")

    # ---- Entry: LAST bar end-stamped <= 16:45 of the session (afternoon only) ----
    aft = df[(tod_min >= 12 * 60) & (tod_min <= 16 * 60 + 45)]
    e = aft.loc[aft.groupby("sid")["time"].idxmax(),
                ["sid", "session_date", "time", "close"]].rename(
        columns={"time": "entry_time", "close": "entry_close"})
    e["entry_stale_min"] = ((e["session_date"] + pd.Timedelta(hours=16, minutes=45))
                            - e["entry_time"]).dt.total_seconds() / 60.0
    n_cand = len(e)
    stale_dropped = e[e["entry_stale_min"] > MAX_ENTRY_STALE_MIN]
    e = e[e["entry_stale_min"] <= MAX_ENTRY_STALE_MIN].copy()
    print(f"\nEntry construction: last bar <= 16:45 ET, staleness <= {MAX_ENTRY_STALE_MIN:.0f} min.")
    print(f"  sessions with an afternoon bar: {n_cand}; accepted entries: {len(e)}; "
          f"dropped for staleness (early closes): {len(stale_dropped)}")
    sd = e["entry_stale_min"]
    print(f"  entry staleness: exactly 16:45 stamp {(sd == 0).sum()} | (0,5] min {((sd > 0) & (sd <= 5)).sum()} "
          f"| (5,30] min {((sd > 5) & (sd <= 30)).sum()}  "
          f"(the (5,30] block is dominated by pre-Nov-2012 Fridays closing 16:15 ET)")
    yr_stale = e[sd > 5].groupby(e["session_date"].dt.year).size()
    print(f"  (5,30]-stale entries by year: "
          + ", ".join(f"{y}:{c}" for y, c in yr_stale.items()))

    # ---- Exit: first bar >= 09:30 on the session's own RTH date (<= 17:00 guard) ----
    rth = df[(df["time"] >= df["session_date"] + pd.Timedelta(hours=9, minutes=30))
             & (df["time"] <= df["session_date"] + pd.Timedelta(hours=17))]
    r = rth.loc[rth.groupby("sid")["time"].idxmin(),
                ["sid", "session_date", "time", "close"]].rename(
        columns={"time": "exit_time", "close": "exit_close"})
    print(f"Sessions with a bar stamped >= 09:30 on the session date: {len(r)}")

    # ---- Nights: entry in session sid, exit in session sid+1 ----
    e["next_sid"] = e["sid"] + 1
    nights = e.merge(
        r.rename(columns={"sid": "exit_sid", "session_date": "exit_session_date"}),
        left_on="next_sid", right_on="exit_sid", how="inner").drop(columns=["next_sid"])
    # prior RTH reference: entry session's own first >=09:30 bar close
    nights = nights.merge(
        r[["sid", "exit_close", "exit_time"]].rename(
            columns={"exit_close": "rth0930_close", "exit_time": "rth0930_time"}),
        on="sid", how="left").drop(columns=["rth0930_time"])
    nights["prior_rth_ret_pts"] = nights["entry_close"] - nights["rth0930_close"]

    nights["gross_pts"] = nights["exit_close"] - nights["entry_close"]
    nights["gross_t"] = nights["gross_pts"] * TICKS_PER_PT
    nights["net2.0_t"] = nights["gross_t"] - FRICTION_PRIMARY_T
    nights["net2.872_t"] = nights["gross_t"] - FRICTION_STRESS_T
    nights["net2.0_usd"] = nights["net2.0_t"] * USD_PER_TICK
    nights["hold_hours"] = (nights["exit_time"] - nights["entry_time"]).dt.total_seconds() / 3600.0
    nights["weekend_span"] = nights["hold_hours"] > 24.0
    nights["year"] = nights["exit_session_date"].dt.year
    blocks = [(2006, 2009), (2010, 2013), (2014, 2017), (2018, 2021), (2022, 2026)]
    block_lbl = {b: f"{b[0]}-{min(b[1], 2026)}" + ("-05" if b[1] == 2026 else "") for b in blocks}
    nights["block"] = pd.cut(nights["year"], [b[0] - 1 for b in blocks] + [2026],
                             labels=[block_lbl[b] for b in blocks]).astype(str)
    nights = nights.sort_values("exit_time").reset_index(drop=True)
    nights["night_idx"] = np.arange(len(nights))

    sigma = nights["gross_t"].std(ddof=1)
    nights["outlier_8sig"] = nights["gross_t"].abs() > OUTLIER_SIGMA * sigma

    print(f"\nNights formed: {len(nights)} "
          f"({nights['exit_session_date'].iloc[0].date()} -> {nights['exit_session_date'].iloc[-1].date()})")
    print(f"  weekend/holiday spans (>24h hold): {int(nights['weekend_span'].sum())}")
    print(f"  gross per-night sigma (FULL sample): {sigma:.3f} t; "
          f"8-sigma threshold: {OUTLIER_SIGMA * sigma:.1f} t")
    out_rows = nights[nights["outlier_8sig"]]
    print(f"  8-sigma roll/outlier nights flagged: {len(out_rows)}")
    for _, rr in out_rows.iterrows():
        print(f"    {rr['entry_time']} -> {rr['exit_time']}: gross {rr['gross_t']:+.1f} t "
              f"(hold {rr['hold_hours']:.1f} h)")

    # ---- Grouped stats, night-clustered bootstrap CIs (fixed order, one rng) ----
    rng = np.random.default_rng(SEED)
    rows = []

    def add(name, mask):
        sub = nights[mask]
        rows.append(group_stats(name, sub["net2.0_t"].values, sub["net2.872_t"].values,
                                sub["gross_t"].values, rng))

    all_mask = pd.Series(True, index=nights.index)
    clean_mask = ~nights["outlier_8sig"]
    add("ALL nights (unconditional)", all_mask)
    add("ALL excl. 8-sigma outliers", clean_mask)
    for b in blocks:
        add(f"block {block_lbl[b]}", nights["block"] == block_lbl[b])
        add(f"block {block_lbl[b]} excl. outliers", (nights["block"] == block_lbl[b]) & clean_mask)
    add("pre-2015 (exit < 2015-01-01)", nights["year"] < 2015)
    add("2015+ (exit >= 2015-01-01)", nights["year"] >= 2015)
    for y in sorted(nights["year"].unique()):
        add(f"year {y}", nights["year"] == y)
    cond_ok = nights["prior_rth_ret_pts"].notna()
    cond = cond_ok & (nights["prior_rth_ret_pts"] < 0)
    add("COND prior RTH ret < 0", cond)
    add("COND prior RTH ret < 0, excl. outliers", cond & clean_mask)
    add("complement: prior RTH ret >= 0", cond_ok & (nights["prior_rth_ret_pts"] >= 0))

    # top-10-nights-removed sensitivity (10 largest net2.0 nights removed)
    top10_idx = nights.nlargest(10, "net2.0_t").index
    sens_mask = ~nights.index.isin(top10_idx)
    add("SENS: top-10 best nights removed", pd.Series(sens_mask, index=nights.index))
    total_net = nights["net2.0_t"].sum()
    top10_net = nights.loc[top10_idx, "net2.0_t"].sum()

    summary = pd.DataFrame(rows)
    pd.set_option("display.width", 220)
    print(f"\n--- Per-night expectancy (ticks/night), night-clustered 95% bootstrap CI, "
          f"{N_BOOT} draws, seed {SEED} ---")
    print(summary.to_string(index=False,
                            float_format=lambda v: f"{v:.3f}" if pd.notna(v) else "nan"))
    print(f"\n(prior-RTH conditional defined on nights whose ENTRY session has a >=09:30 bar: "
          f"{int(cond_ok.sum())}/{len(nights)} nights)")
    print(f"Top-10 best nights sum: {top10_net:+.1f} t = {100 * top10_net / total_net:.1f}% of "
          f"total net {total_net:+.1f} t")

    # ---- W5-B1 reconciliation: 2022+ subset must match +17.211 t/night ----
    sub22 = nights[nights["exit_session_date"] >= pd.Timestamp("2022-01-01")]
    m22 = float(sub22["net2.0_t"].mean())
    diff = m22 - W5_REF_MEAN_T
    recon_ok = abs(diff) <= RECON_TOL_T
    print("\n--- RECONCILIATION vs W5-B1 (3-min substrate, artifacts/w5_b1/w5b1_summary.csv) ---")
    print(f"W5-B1 frozen ALL row : net(2.0t) mean = {W5_REF_MEAN_T:+.3f} t/night on n = {W5_REF_N}")
    print(f"W9 2022+ subset      : net(2.0t) mean = {m22:+.3f} t/night on n = {len(sub22)} "
          f"(hit rate {float((sub22['net2.0_t'] > 0).mean()):.4f}, median {float(sub22['net2.0_t'].median()):.1f} t)")
    print(f"difference = {diff:+.3f} t (declared tolerance +/-{RECON_TOL_T} t): "
          f"{'RECONCILED' if recon_ok else 'NOT RECONCILED — investigate before trusting the readout'}")
    recon_df = pd.DataFrame([{
        "w5_mean_t": W5_REF_MEAN_T, "w5_n": W5_REF_N,
        "w9_2022p_mean_t": m22, "w9_2022p_n": len(sub22),
        "diff_t": diff, "tolerance_t": RECON_TOL_T, "reconciled": recon_ok,
    }])

    # ---- (b) Time-trend regression, HC1-robust ----
    a0, slope, se, tstat = ols_hc1(nights["net2.0_t"].values, nights["night_idx"].values)
    a0c, slope_c, se_c, tstat_c = ols_hc1(nights.loc[clean_mask, "net2.0_t"].values,
                                          nights.loc[clean_mask, "night_idx"].values)
    print("\n--- Time trend: nightly net(2.0t) ~ night index, OLS with HC1-robust t ---")
    print(f"ALL nights      : slope = {slope:+.6f} t/night-step ({slope * 252:+.3f} t/yr-of-nights), "
          f"HC1 t = {tstat:+.3f}, intercept = {a0:+.3f} t")
    print(f"excl. outliers  : slope = {slope_c:+.6f} t/night-step ({slope_c * 252:+.3f} t/yr-of-nights), "
          f"HC1 t = {tstat_c:+.3f}, intercept = {a0c:+.3f} t")
    sig_neg_trend = (slope < 0) and (tstat <= -1.96)
    print(f"significant NEGATIVE trend (slope<0 and t<=-1.96) on ALL nights: {sig_neg_trend}")
    trend_df = pd.DataFrame([
        {"sample": "ALL", "n": len(nights), "intercept_t": a0, "slope_t_per_night": slope,
         "slope_t_per_252nights": slope * 252, "hc1_se": se, "hc1_t": tstat,
         "sig_neg_trend": sig_neg_trend},
        {"sample": "excl_outliers", "n": int(clean_mask.sum()), "intercept_t": a0c,
         "slope_t_per_night": slope_c, "slope_t_per_252nights": slope_c * 252,
         "hc1_se": se_c, "hc1_t": tstat_c,
         "sig_neg_trend": (slope_c < 0) and (tstat_c <= -1.96)},
    ])

    # rolling 2-year (730D) mean series
    ser = nights.set_index("exit_session_date")["net2.0_t"]
    roll = ser.rolling("730D", min_periods=200).mean()
    roll_df = pd.DataFrame({"exit_session_date": roll.index, "rolling_730d_mean_net2.0_t": roll.values,
                            "n_in_window": ser.rolling("730D", min_periods=200).count().values})
    rv = roll.dropna()
    print(f"Rolling 730D mean of net(2.0t): first {rv.index[0].date()} = {rv.iloc[0]:+.3f} t; "
          f"min {rv.min():+.3f} t ({rv.idxmin().date()}); max {rv.max():+.3f} t ({rv.idxmax().date()}); "
          f"last {rv.index[-1].date()} = {rv.iloc[-1]:+.3f} t")
    neg_share = float((rv < 0).mean())
    print(f"Share of rolling-mean observations below zero: {neg_share:.3f}")

    # ---- (d) Solar correlation (2022+ overlap) ----
    solar = pd.read_csv(SOLAR_CSV, parse_dates=["sess"])
    solar = solar[solar["sess"] < DEV_CUTOFF]
    print(f"\nSolar ledger: {SOLAR_CSV.relative_to(ROOT)} — net_v1 (E10MASTER_V1 frozen research "
          f"champion); {len(solar)} sessions kept < {DEV_CUTOFF.date()}.")
    j = nights.merge(solar, left_on="exit_session_date", right_on="sess", how="inner")
    print(f"Overlapping dates (night exit session == Solar sess): {len(j)} "
          f"({j['sess'].min().date()} -> {j['sess'].max().date()})")

    def corr_block(tag, sub):
        if len(sub) < 3:
            return {"subset": tag, "n": len(sub), "pearson_rho": np.nan, "spearman_rho": np.nan}
        return {"subset": tag, "n": len(sub),
                "pearson_rho": float(np.corrcoef(sub["net2.0_usd"], sub["net_v1"])[0, 1]),
                "spearman_rho": float(sub["net2.0_usd"].rank().corr(sub["net_v1"].rank()))}

    corr_rows = [
        corr_block("full overlap", j),
        corr_block("Solar losing days (net_v1 < 0)", j[j["net_v1"] < 0]),
        corr_block("full overlap excl. 8-sigma outliers", j[~j["outlier_8sig"]]),
        corr_block("Solar losing days excl. outliers", j[(j["net_v1"] < 0) & (~j["outlier_8sig"])]),
    ]
    corr_df = pd.DataFrame(corr_rows)
    print("\n--- Correlation: overnight nightly P&L (net 2.0t, $/night, 1 NQ) vs Solar daily P&L "
          "(net_v1, $) ---")
    print(corr_df.to_string(index=False,
                            float_format=lambda v: f"{v:.4f}" if pd.notna(v) else "nan"))

    # ---- AMENDED VERDICT (all four clauses required) ----
    head = summary.iloc[0]                       # ALL nights unconditional
    blk22 = summary[summary["group"] == f"block {block_lbl[(2022, 2026)]}"].iloc[0]
    rho_full = float(corr_df.iloc[0]["pearson_rho"])
    c_a = (head["net2.0_mean_t"] >= 4.0) and (head["net2.0_ci_lo"] > 0.0)
    c_b = not sig_neg_trend
    c_c = blk22["net2.0_mean_t"] > 0.0
    c_d = rho_full < 0.3
    verdict = "PROMISING" if (c_a and c_b and c_c and c_d) else "B1 CLOSED (adequate power, permanent)"
    print("\n--- AMENDED VERDICT RULE (frozen d7dfdad; ALL four clauses required) ---")
    print(f"(a) power   : full-sample net(2.0t) = {head['net2.0_mean_t']:+.3f} t/night (need >= +4.0), "
          f"CI_lo = {head['net2.0_ci_lo']:+.3f} t (need > 0): {'PASS' if c_a else 'FAIL'}")
    print(f"(b) trend   : slope = {slope:+.6f} t/night-step, HC1 t = {tstat:+.3f} "
          f"(FAIL iff slope<0 and t<=-1.96): {'PASS' if c_b else 'FAIL'}")
    print(f"(c) recency : 2022->2026-05 block point estimate = {blk22['net2.0_mean_t']:+.3f} t/night "
          f"(need > 0): {'PASS' if c_c else 'FAIL'}")
    print(f"(d) overlap : Pearson rho vs Solar net_v1 (2022+ overlap) = {rho_full:+.4f} "
          f"(need < 0.3): {'PASS' if c_d else 'FAIL'}")
    binding = [nm for nm, ok in [("(a) power", c_a), ("(b) trend", c_b),
                                 ("(c) recency", c_c), ("(d) overlap", c_d)] if not ok]
    print(f"VERDICT: {verdict}" + (f"  — binding clause(s): {', '.join(binding)}" if binding else ""))
    pre15 = summary[summary["group"] == "pre-2015 (exit < 2015-01-01)"].iloc[0]
    post15 = summary[summary["group"] == "2015+ (exit >= 2015-01-01)"].iloc[0]
    print(f"Decay context: pre-2015 mean {pre15['net2.0_mean_t']:+.3f} t vs 2015+ mean "
          f"{post15['net2.0_mean_t']:+.3f} t; a pass driven by pre-2015 with a dying trend = FAIL.")

    # ---- Fragility diagnostic (NON-VERDICT; the frozen rule is seed 20260808 / 1000 reps) ----
    # Clause (a)'s CI_lo is close to zero: quantify bootstrap-seed sensitivity so the
    # marginality is on the record. Does not alter the verdict computed above.
    x_all = nights["net2.0_t"].values
    frag_rows = []
    for s in range(1, 11):
        _, lo_s, hi_s = boot_ci(x_all, np.random.default_rng(s), N_BOOT)
        frag_rows.append({"diagnostic": f"seed {s}, 1000 reps", "ci_lo": lo_s, "ci_hi": hi_s})
    _, lo10k, hi10k = boot_ci(x_all, np.random.default_rng(SEED), 10_000)
    frag_rows.append({"diagnostic": "frozen seed 20260808, 10000 reps", "ci_lo": lo10k, "ci_hi": hi10k})
    frag_df = pd.DataFrame(frag_rows)
    n_lo_pos = int((frag_df["ci_lo"] > 0).sum())
    print("\n--- Fragility diagnostic (non-verdict): full-sample net(2.0t) CI_lo across seeds ---")
    print(frag_df.to_string(index=False, float_format=lambda v: f"{v:+.3f}"))
    print(f"CI_lo > 0 in {n_lo_pos}/{len(frag_df)} diagnostic draws "
          f"(frozen-rule CI_lo = {head['net2.0_ci_lo']:+.3f} t governs the verdict)")
    t_naive = float(x_all.mean() / (x_all.std(ddof=1) / np.sqrt(len(x_all))))
    print(f"Plain t-stat of the full-sample mean: {t_naive:+.3f} "
          f"(mean {x_all.mean():+.3f} t, sd {x_all.std(ddof=1):.3f} t, n {len(x_all)}) — "
          f"the clause-(a) boundary sits inside Monte-Carlo noise of the 95% CI edge.")

    # ---- Persist artifacts ----
    keep = ["sid", "session_date", "entry_time", "entry_close", "entry_stale_min", "exit_sid",
            "exit_session_date", "exit_time", "exit_close", "rth0930_close", "prior_rth_ret_pts",
            "gross_pts", "gross_t", "net2.0_t", "net2.872_t", "net2.0_usd", "hold_hours",
            "weekend_span", "year", "block", "night_idx", "outlier_8sig"]
    nightly_out = nights[keep].merge(solar, left_on="exit_session_date", right_on="sess",
                                     how="left").drop(columns=["sess", "net_v2"], errors="ignore")
    nightly_out.to_csv(ART / "w9b1_nightly.csv", index=False)
    summary.to_csv(ART / "w9b1_summary.csv", index=False)
    summary[summary["group"].str.startswith("block ")].to_csv(ART / "w9b1_blocks.csv", index=False)
    trend_df.to_csv(ART / "w9b1_trend.csv", index=False)
    roll_df.to_csv(ART / "w9b1_rolling_2y.csv", index=False)
    corr_df.to_csv(ART / "w9b1_correlation.csv", index=False)
    recon_df.to_csv(ART / "w9b1_reconcile_w5.csv", index=False)
    frag_df.to_csv(ART / "w9b1_ci_fragility.csv", index=False)
    print(f"\nArtifacts written to {ART.relative_to(ROOT)}: w9b1_nightly.csv, w9b1_summary.csv, "
          f"w9b1_blocks.csv, w9b1_trend.csv, w9b1_rolling_2y.csv, w9b1_correlation.csv, "
          f"w9b1_reconcile_w5.csv, w9b1_ci_fragility.csv, w9b1_stdout.txt")
    return summary, trend_df, corr_df, recon_df, verdict


if __name__ == "__main__":
    ART.mkdir(parents=True, exist_ok=True)
    with open(ART / "w9b1_stdout.txt", "w", encoding="utf-8") as f:
        sys.stdout = Tee(sys.__stdout__, f)
        try:
            main()
        finally:
            sys.stdout = sys.__stdout__
