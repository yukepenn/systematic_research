"""W5-B1 — Overnight 16:44->09:30 premium, first pass + MEASURED Solar correlation.

Frozen spec: research/scalping_lab/specs/W5_programs_wave.md section B1.

Position: long 1 NQ at the 16:42-16:45 3-min bar close (bar end-stamped 16:45:00),
exit at the NEXT session's first bar with stamp >= 09:30, at its CLOSE.
Friction: 2.0 ticks RT primary, 2.872 ticks RT stress. NQ tick = 0.25 pt = $5.
Reports: per-night expectancy (ticks), by year, post-2024 subsample, ONE frozen
conditional (prior RTH return < 0), day-clustered 95% CI (bootstrap nights, seed
20260808). Then measured correlation of overnight nightly P&L vs Solar Family-A
daily P&L (E10MASTER v1 frozen research champion ledger, net_v1 column of
runs/E10MASTER_V2/out/daily_v1_v2.csv), full-sample + Solar-losing-day.
Verdict frozen: promising iff unconditional >= +4t/night net of 2.0t with
CI_lo > 0 AND |rho| < 0.3.

Contamination rule: minute-history dev window ends 2026-05-31 — all rows with
timestamp >= 2026-06-01 are dropped at load, before ANY analysis (sealed holdout).

Roll caution: the 3-min CSV is a back-adjusted merge; overnight returns spanning a
roll date may embed an adjustment step. Nights with |gross ticks| > 8*sigma are
flagged and all headline stats are reported with AND without them.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]  # systematic_research/
BARS_CSV = ROOT / "runs" / "AUDIT03_BARS" / "nq_3m_2022_2026.csv"
SOLAR_CSV = ROOT / "runs" / "E10MASTER_V2" / "out" / "daily_v1_v2.csv"
ART = ROOT / "research" / "scalping_lab" / "artifacts" / "w5_b1"

DEV_CUTOFF = pd.Timestamp("2026-06-01 00:00:00")  # exchange ET, exclusive
SEED = 20260808
N_BOOT = 10_000
FRICTION_PRIMARY_T = 2.0
FRICTION_STRESS_T = 2.872
TICKS_PER_PT = 4.0
USD_PER_TICK = 5.0
OUTLIER_SIGMA = 8.0


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
    """Day-clustered 95% CI on the mean: each night is one cluster; resample
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


def main():
    ART.mkdir(parents=True, exist_ok=True)

    print("=" * 78)
    print("W5-B1 Overnight 16:44->09:30 premium, first pass (frozen spec)")
    print("=" * 78)

    # ---- Load 3-min bars; enforce contamination rule immediately at load ----
    df = pd.read_csv(BARS_CSV, parse_dates=["time"])
    n_raw = len(df)
    df = df[df["time"] < DEV_CUTOFF].reset_index(drop=True)
    print(f"Bars loaded: {n_raw} rows raw file; {len(df)} rows kept after dev-window "
          f"truncation at {DEV_CUTOFF} (exclusive); {n_raw - len(df)} sealed rows dropped unread.")
    print(f"Bar stamp range kept: {df['time'].iloc[0]} -> {df['time'].iloc[-1]} (exchange ET, end-stamped)")

    # ---- Sessions ----
    df["sid"] = df["first_bar_of_session"].cumsum()
    sess_date = df.groupby("sid")["time"].max().dt.normalize().rename("session_date")
    df = df.merge(sess_date, on="sid")
    n_sessions = df["sid"].nunique()
    print(f"Sessions: {n_sessions} (18:00 ET prior day -> 17:00 ET session date)")

    tod = df["time"].dt.time

    # Entry bar: the 16:42-16:45 bar, end-stamped exactly 16:45:00
    e = df[tod == pd.Timestamp("16:45:00").time()][["sid", "session_date", "time", "close"]]
    e = e.rename(columns={"time": "entry_time", "close": "entry_close"})
    assert e["sid"].is_unique
    # First bar with stamp >= 09:30 of the session's own RTH date. The upper
    # bound (<= 17:00) guards partial/truncated sessions (e.g. the dev-cutoff
    # tail session whose bars are Sunday-evening only): the exit must be an
    # RTH-morning bar, never an evening bar misdated by the max-stamp rule.
    rth = df[(df["time"] >= df["session_date"] + pd.Timedelta(hours=9, minutes=30))
             & (df["time"] <= df["session_date"] + pd.Timedelta(hours=17))]
    r = rth.sort_values("time").groupby("sid").first().reset_index()[
        ["sid", "session_date", "time", "close"]
    ].rename(columns={"time": "exit_time", "close": "exit_close"})

    print(f"Sessions with a 16:45-stamped bar (entry available): {len(e)} "
          f"({n_sessions - len(e)} sessions without: early closes / partial sessions)")
    print(f"Sessions with a bar stamped >= 09:30 on the session date: {len(r)}")

    # ---- Nights: entry in session sid, exit in session sid+1 ----
    e = e.copy()
    e["next_sid"] = e["sid"] + 1
    nights = e.merge(
        r.rename(columns={"sid": "exit_sid", "session_date": "exit_session_date"}),
        left_on="next_sid", right_on="exit_sid", how="inner",
    ).drop(columns=["next_sid"])
    # prior RTH morning reference: session sid's own >=09:30 first-bar close
    nights = nights.merge(
        r[["sid", "close" if False else "exit_close", "exit_time"]].rename(
            columns={"exit_close": "rth0930_close", "exit_time": "rth0930_time"}),
        on="sid", how="left",
    )
    nights["prior_rth_ret_pts"] = nights["entry_close"] - nights["rth0930_close"]

    nights["gross_pts"] = nights["exit_close"] - nights["entry_close"]
    nights["gross_t"] = nights["gross_pts"] * TICKS_PER_PT
    nights["net2.0_t"] = nights["gross_t"] - FRICTION_PRIMARY_T
    nights["net2.872_t"] = nights["gross_t"] - FRICTION_STRESS_T
    nights["net2.0_usd"] = nights["net2.0_t"] * USD_PER_TICK
    nights["hold_hours"] = (nights["exit_time"] - nights["entry_time"]).dt.total_seconds() / 3600.0
    nights["weekend_span"] = nights["hold_hours"] > 24.0
    nights["year"] = nights["exit_session_date"].dt.year

    sigma = nights["gross_t"].std(ddof=1)
    nights["outlier_8sig"] = nights["gross_t"].abs() > OUTLIER_SIGMA * sigma

    n_weekend = int(nights["weekend_span"].sum())
    print(f"\nNights formed: {len(nights)} (entry 16:45 close -> next-session first >=09:30 bar close)")
    print(f"  weekend/holiday spans (>24h hold): {n_weekend}")
    print(f"  gross per-night sigma: {sigma:.3f} t; 8-sigma outlier threshold: {OUTLIER_SIGMA * sigma:.1f} t")
    out_rows = nights[nights["outlier_8sig"]]
    print(f"  outlier nights (|gross| > 8 sigma): {len(out_rows)}")
    for _, rr in out_rows.iterrows():
        print(f"    {rr['entry_time']} -> {rr['exit_time']}: gross {rr['gross_t']:+.1f} t "
              f"(hold {rr['hold_hours']:.1f} h)")

    # ---- Grouped stats with day-clustered bootstrap CIs (fixed order, one rng) ----
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
    for y in sorted(nights["year"].unique()):
        add(f"year {y}", nights["year"] == y)
    post24 = nights["exit_session_date"] >= pd.Timestamp("2025-01-01")
    add("post-2024 (exit >= 2025-01-01)", post24)
    add("post-2024 excl. outliers", post24 & clean_mask)
    cond_ok = nights["prior_rth_ret_pts"].notna()
    cond = cond_ok & (nights["prior_rth_ret_pts"] < 0)
    add("COND prior RTH ret < 0", cond)
    add("COND prior RTH ret < 0, excl. outliers", cond & clean_mask)
    add("complement: prior RTH ret >= 0", cond_ok & (nights["prior_rth_ret_pts"] >= 0))

    summary = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print("\n--- Per-night expectancy (ticks/night), day-clustered 95% bootstrap CI, "
          f"{N_BOOT} draws, seed {SEED} ---")
    print(summary.to_string(index=False,
                            float_format=lambda v: f"{v:.3f}" if pd.notna(v) else "nan"))
    print(f"\n(prior-RTH conditional defined on nights whose ENTRY session has a >=09:30 bar: "
          f"{int(cond_ok.sum())}/{len(nights)} nights; ret = entry-day 16:45 close minus "
          f"entry-day first >=09:30 bar close)")

    # ---- Solar correlation (E10MASTER v1 frozen research champion ledger) ----
    solar = pd.read_csv(SOLAR_CSV, parse_dates=["sess"])
    solar = solar[solar["sess"] < DEV_CUTOFF]  # same dev truncation for symmetry
    print(f"\nSolar ledger: {SOLAR_CSV.relative_to(ROOT)} — using net_v1 "
          f"(E10MASTER_V1, frozen research champion per runs/E10MASTER_V2/results.md); "
          f"{len(solar)} sessions kept <= dev cutoff.")

    # Align a night to the Solar session it lives inside: the overnight hold
    # 16:45 D -> 09:30 D+1 is marked within Solar session dated D+1 (18:00 D ->
    # 17:00 D+1), so join on exit_session_date == sess.
    j = nights.merge(solar, left_on="exit_session_date", right_on="sess", how="inner")
    print(f"Overlapping dates (night exit session == Solar sess): {len(j)}")

    def corr_block(tag, sub):
        if len(sub) < 3:
            return {"subset": tag, "n": len(sub), "pearson_rho": np.nan, "spearman_rho": np.nan}
        return {
            "subset": tag,
            "n": len(sub),
            "pearson_rho": float(np.corrcoef(sub["net2.0_usd"], sub["net_v1"])[0, 1]),
            "spearman_rho": float(sub["net2.0_usd"].rank().corr(sub["net_v1"].rank())),
        }

    corr_rows = [
        corr_block("full overlap", j),
        corr_block("Solar losing days (net_v1 < 0)", j[j["net_v1"] < 0]),
        corr_block("full overlap excl. 8-sigma outliers", j[~j["outlier_8sig"]]),
        corr_block("Solar losing days excl. outliers", j[(j["net_v1"] < 0) & (~j["outlier_8sig"])]),
    ]
    corr_df = pd.DataFrame(corr_rows)
    print("\n--- Correlation: overnight nightly P&L (net 2.0t, $/night, 1 NQ) vs Solar daily "
          "P&L (net_v1, $) ---")
    print(corr_df.to_string(index=False,
                            float_format=lambda v: f"{v:.4f}" if pd.notna(v) else "nan"))

    # ---- Frozen verdict ----
    head = summary.iloc[0]  # ALL nights unconditional
    rho_full = corr_df.iloc[0]["pearson_rho"]
    c_mean = head["net2.0_mean_t"] >= 4.0
    c_ci = head["net2.0_ci_lo"] > 0.0
    c_rho = abs(rho_full) < 0.3
    verdict = "PROMISING" if (c_mean and c_ci and c_rho) else "NOT PROMISING"
    print("\n--- FROZEN VERDICT RULE ---")
    print(f"unconditional net(2.0t) mean = {head['net2.0_mean_t']:+.3f} t/night "
          f"(need >= +4.0): {'PASS' if c_mean else 'FAIL'}")
    print(f"CI_lo = {head['net2.0_ci_lo']:+.3f} t (need > 0): {'PASS' if c_ci else 'FAIL'}")
    print(f"|rho_full| = {abs(rho_full):.4f} (need < 0.3): {'PASS' if c_rho else 'FAIL'}")
    print(f"VERDICT: {verdict}  (2005+ extension only if PROMISING)")

    # ---- Persist artifacts ----
    keep = ["sid", "session_date", "entry_time", "entry_close", "exit_sid",
            "exit_session_date", "exit_time", "exit_close", "rth0930_close",
            "prior_rth_ret_pts", "gross_pts", "gross_t", "net2.0_t", "net2.872_t",
            "net2.0_usd", "hold_hours", "weekend_span", "year", "outlier_8sig"]
    nightly_out = nights[keep].merge(solar, left_on="exit_session_date", right_on="sess",
                                     how="left").drop(columns=["sess", "net_v2"])
    nightly_out.to_csv(ART / "w5b1_nightly.csv", index=False)
    summary.to_csv(ART / "w5b1_summary.csv", index=False)
    corr_df.to_csv(ART / "w5b1_correlation.csv", index=False)
    print(f"\nArtifacts written to {ART.relative_to(ROOT)}: w5b1_nightly.csv, "
          f"w5b1_summary.csv, w5b1_correlation.csv, w5b1_stdout.txt")
    return summary, corr_df, verdict


if __name__ == "__main__":
    ART.mkdir(parents=True, exist_ok=True)
    with open(ART / "w5b1_stdout.txt", "w", encoding="utf-8") as f:
        sys.stdout = Tee(sys.__stdout__, f)
        try:
            main()
        finally:
            sys.stdout = sys.__stdout__
