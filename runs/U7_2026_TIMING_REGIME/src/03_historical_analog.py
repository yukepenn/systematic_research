"""U7 step3 -- historical analog search using the top-ranked variable (sigma460_atr_proxy_pts,
by far the dominant P1-vs-P0 effect size from step1/step2, d=1.06-1.11) plus a secondary check on
session-open gap size. Finds the 2022-2025 month(s)/quarter(s) whose level is closest to P1's
level, then runs the SAME lightweight delay-proxy diagnostic from step2 restricted to entries
falling in the analog window(s), and compares its benefit to P1's and to the P0 baseline.
"""
import os, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(ROOT, "runs", "U7_2026_TIMING_REGIME", "out")

df = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"))
df["period"] = np.select(
    [(~df["is_health_only_bar"]) & (df["year"] < 2026),
     (~df["is_health_only_bar"]) & (df["year"] == 2026),
     df["is_health_only_bar"]],
    ["P0", "P1", "P2"], default="?"
)
df["sess_date_dt"] = pd.to_datetime(df["sess_date"])
df["ym"] = df["sess_date_dt"].dt.to_period("M")
df["yq"] = df["sess_date_dt"].dt.to_period("Q")

P1_level = df.loc[df.period == "P1", "sigma460_atr_proxy_pts"].mean()
print(f"[U7] P1 (2026 canonical stub) mean sigma460_atr_proxy_pts = {P1_level:.4f}")

# ---------------------------------------------------------------- monthly analog search (2022-2025 only)
p0 = df[df.period == "P0"]
monthly = p0.groupby("ym")["sigma460_atr_proxy_pts"].agg(["mean", "median", "std", "count"])
monthly["dist_to_P1"] = np.abs(monthly["mean"] - P1_level)
monthly = monthly.sort_values("dist_to_P1")
monthly.to_csv(os.path.join(OUT, "step3_monthly_sigma460.csv"))
print("\n[U7] top-10 closest 2022-2025 MONTHS to P1's sigma460 level (nearest analog by month):")
print(monthly.head(10).to_string())

# ---------------------------------------------------------------- quarterly analog search
quarterly = p0.groupby("yq")["sigma460_atr_proxy_pts"].agg(["mean", "median", "std", "count"])
quarterly["dist_to_P1"] = np.abs(quarterly["mean"] - P1_level)
quarterly = quarterly.sort_values("dist_to_P1")
quarterly.to_csv(os.path.join(OUT, "step3_quarterly_sigma460.csv"))
print("\n[U7] 2022-2025 QUARTERS ranked by closeness to P1's sigma460 level:")
print(quarterly.to_string())

# ---------------------------------------------------------------- define analog window: top-3 closest months
analog_months = monthly.head(3).index.tolist()
print(f"\n[U7] ANALOG WINDOW selected: top-3 closest months = {[str(m) for m in analog_months]}")
analog_mask = df["ym"].isin(analog_months) & (df["period"] == "P0")
print(f"[U7] analog window: {analog_mask.sum()} bars, {df.loc[analog_mask, 'sess_date'].nunique()} sessions, "
      f"date range within each month (see step3_monthly_sigma460.csv for exact months)")

# cross-check: does the analog window overlap D7's own already-established analog
# (2025-04-25..2025-09-19, found via a DIFFERENT 7-variable market panel + Mahalanobis distance)?
d7_analog_start, d7_analog_end = pd.Timestamp("2025-04-25"), pd.Timestamp("2025-09-19")
overlap_months = [m for m in analog_months if
                   (m.to_timestamp() <= d7_analog_end) and (m.to_timestamp(how="end") >= d7_analog_start)]
print(f"[U7] D7's own market-panel analog (2025-04-25..2025-09-19) overlaps with sigma460-analog "
      f"months: {[str(m) for m in overlap_months]}")

# ---------------------------------------------------------------- also check secondary variable: session-open gap
gap_df = pd.read_csv(os.path.join(OUT, "step1_session_open_gap.csv"))
gap_df["sess_date_dt"] = pd.to_datetime(gap_df["sess_date"])
gap_df["ym"] = gap_df["sess_date_dt"].dt.to_period("M")
P1_gap_level = gap_df.loc[gap_df.period == "P1", "gap_atr"].mean()
print(f"\n[U7] P1 mean session-open gap_atr = {P1_gap_level:.4f}")
gap_monthly = gap_df[gap_df.period == "P0"].groupby("ym")["gap_atr"].agg(["mean", "count"])
gap_monthly["dist_to_P1"] = np.abs(gap_monthly["mean"] - P1_gap_level)
gap_monthly = gap_monthly.sort_values("dist_to_P1")
gap_monthly.to_csv(os.path.join(OUT, "step3_monthly_gap_atr.csv"))
print("[U7] top-10 closest 2022-2025 months by session-open gap_atr:")
print(gap_monthly.head(10).to_string())

# ---------------------------------------------------------------- lightweight delay-proxy diagnostic, restricted to analog window
tbl = pd.read_csv(os.path.join(OUT, "step2_entry_block_mechanism_table.csv"))
tbl["sess_date_dt"] = pd.to_datetime(tbl["sess_date"])
tbl["ym"] = tbl["sess_date_dt"].dt.to_period("M")

analog_entries = tbl[tbl["ym"].isin(analog_months) & (tbl["period"] == "P0")]
print(f"\n[U7] entries in analog window: {len(analog_entries)}")


def summarize(sub, label):
    n = len(sub)
    delay_sum = sub["delay_delta"].sum()
    delay_mean = sub["delay_delta"].mean() if n else np.nan
    qr_rate = sub["quick_reversal"].mean() if n else np.nan
    pb_mean = sub["pullback_atr_6bar"].mean() if n else np.nan
    print(f"  {label}: n={n}, delay_delta sum=${delay_sum:,.2f}, mean=${delay_mean:,.2f}, "
          f"quick_reversal_rate={qr_rate:.4f}, pullback_atr_6bar mean={pb_mean:.3f}")
    return dict(label=label, n=n, delay_sum=float(delay_sum), delay_mean=float(delay_mean) if n else None,
                quick_reversal_rate=float(qr_rate) if n else None, pullback_atr_mean=float(pb_mean) if n else None)


print("\n[U7] LIGHTWEIGHT DELAY-PROXY DIAGNOSTIC comparison:")
res_p0 = summarize(tbl[tbl.period == "P0"], "P0 (full 2022-2025)")
res_p0_ex_analog = summarize(tbl[(tbl.period == "P0") & (~tbl["ym"].isin(analog_months))], "P0 EXCLUDING analog months")
res_analog = summarize(analog_entries, "ANALOG WINDOW (2022-2025 months closest to P1 vol level)")
res_p1 = summarize(tbl[tbl.period == "P1"], "P1 (2026 canonical stub)")
res_p2 = summarize(tbl[tbl.period == "P2"], "P2 (health-only Jun-Jul 2026)")

# also: D7's own named analog window (2025-04-25..2025-09-19) -- only the P0 portion is usable
# here (P0 ends 2025-12-31, so entire D7 window minus any 2026 bars, but there are none since
# D7's window is fully within 2025)
d7_mask = (tbl["sess_date_dt"] >= d7_analog_start) & (tbl["sess_date_dt"] <= d7_analog_end) & (tbl.period == "P0")
res_d7 = summarize(tbl[d7_mask], "D7's own analog window (2025-04-25..2025-09-19)")

summary = {
    "P1_sigma460_level": float(P1_level),
    "analog_months": [str(m) for m in analog_months],
    "monthly_top10": monthly.head(10).reset_index().to_dict(orient="records"),
    "diagnostics": {
        "P0_full": res_p0, "P0_excluding_analog": res_p0_ex_analog,
        "analog_window": res_analog, "P1": res_p1, "P2": res_p2,
        "D7_named_analog": res_d7,
    },
}
with open(os.path.join(OUT, "step3_summary.json"), "w") as f:
    json.dump(summary, f, indent=2, default=str)

print("\n[U7] step3 complete.")
