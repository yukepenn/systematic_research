"""R2V1 -- formal chronology battery (year/quarter/LOYO/rolling) + block bootstrap on paired
daily delta, per the owner directive's binding sec4/5/6. Fixed candidate (confirm_bars=2) vs
control, NQ economics (MNQ shares the same decision sequence, already shown directionally
identical in REPORT.md)."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
from smv2_common import dd_battery

OUT = os.path.join(ROOT, "runs", "R2_ENTRY_TIMING", "out")

ctrl = pd.read_csv(os.path.join(ROOT, "runs", "R1_ADAPTIVE_EXIT", "out", "daily_CONTROL_NQ.csv"))
cand = pd.read_csv(os.path.join(OUT, "daily_CONFIRM2_NQ.csv"))
m = ctrl.merge(cand, on="sess", suffixes=("_ctrl", "_cand"))
m["sess"] = pd.to_datetime(m["sess"])
m["year"] = m["sess"].dt.year
m["quarter"] = m["sess"].dt.to_period("Q").astype(str)
m["delta"] = m["net_cand"] - m["net_ctrl"]

print("=" * 90, "\nYEAR-BY-YEAR\n", "=" * 90, sep="")
yr_rows = []
for yr, g in m.groupby("year"):
    bc = dd_battery(g["sess"], g["net_ctrl"].to_numpy(), label=f"ctrl_{yr}")
    bd = dd_battery(g["sess"], g["net_cand"].to_numpy(), label=f"cand_{yr}")
    row = {"year": yr, "n_days": len(g), "net_ctrl": g["net_ctrl"].sum(), "net_cand": g["net_cand"].sum(),
           "delta_net": g["delta"].sum(), "sharpe_ctrl": bc["sharpe"], "sharpe_cand": bd["sharpe"],
           "maxDD_ctrl": bc["maxDD_eod"], "maxDD_cand": bd["maxDD_eod"],
           "CDaR95_ctrl": bc["CDaR5"], "CDaR95_cand": bd["CDaR5"]}
    yr_rows.append(row)
    print(f"{yr}: net ctrl={row['net_ctrl']:.2f} cand={row['net_cand']:.2f} delta={row['delta_net']:.2f} | "
          f"sharpe ctrl={row['sharpe_ctrl']:.3f} cand={row['sharpe_cand']:.3f} | "
          f"CDaR95 ctrl={row['CDaR95_ctrl']:.2f} cand={row['CDaR95_cand']:.2f}")
yr_df = pd.DataFrame(yr_rows)
yr_df.to_csv(os.path.join(OUT, "r2v1_year_by_year.csv"), index=False)

print("\n" + "=" * 90, "\nQUARTER-BY-QUARTER\n", "=" * 90, sep="")
q_rows = []
for q, g in m.groupby("quarter"):
    q_rows.append({"quarter": q, "n_days": len(g), "net_ctrl": g["net_ctrl"].sum(),
                    "net_cand": g["net_cand"].sum(), "delta_net": g["delta"].sum()})
q_df = pd.DataFrame(q_rows)
q_df.to_csv(os.path.join(OUT, "r2v1_quarter_by_quarter.csv"), index=False)
print(q_df.to_string(index=False))

print("\n" + "=" * 90, "\n2022-2025-ONLY vs 2026-STUB\n", "=" * 90, sep="")
m2225 = m[m["year"] <= 2025]
m2026 = m[m["year"] == 2026]
b2225_ctrl = dd_battery(m2225["sess"], m2225["net_ctrl"].to_numpy(), label="ctrl_2022_2025")
b2225_cand = dd_battery(m2225["sess"], m2225["net_cand"].to_numpy(), label="cand_2022_2025")
delta_2225 = m2225["delta"].sum()
delta_2026 = m2026["delta"].sum()
print(f"2022-2025 ONLY: ctrl net={m2225['net_ctrl'].sum():.2f} sharpe={b2225_ctrl['sharpe']:.3f} | "
      f"cand net={m2225['net_cand'].sum():.2f} sharpe={b2225_cand['sharpe']:.3f} | delta={delta_2225:.2f}")
print(f"2026 stub only: delta={delta_2026:.2f}  (n_days={len(m2026)})")
print(f"full-history delta = {m['delta'].sum():.2f} "
      f"({delta_2225:.2f} from 2022-2025 + {delta_2026:.2f} from the 2026 stub)")

print("\n" + "=" * 90, "\nLOYO (leave-one-year-out)\n", "=" * 90, sep="")
loyo_rows = []
for yr in sorted(m["year"].unique()):
    g = m[m["year"] != yr]
    bc = dd_battery(g["sess"], g["net_ctrl"].to_numpy(), label=f"ctrl_loyo_{yr}")
    bd = dd_battery(g["sess"], g["net_cand"].to_numpy(), label=f"cand_loyo_{yr}")
    row = {"loyo_removed_year": yr, "n_days": len(g), "net_ctrl": g["net_ctrl"].sum(),
           "net_cand": g["net_cand"].sum(), "delta_net": g["delta"].sum(),
           "sharpe_ctrl": bc["sharpe"], "sharpe_cand": bd["sharpe"],
           "sharpe_delta": bd["sharpe"] - bc["sharpe"],
           "CDaR95_ctrl": bc["CDaR5"], "CDaR95_cand": bd["CDaR5"]}
    loyo_rows.append(row)
    print(f"LOYO-{yr} (removed): delta_net={row['delta_net']:.2f}  sharpe ctrl={row['sharpe_ctrl']:.3f} "
          f"cand={row['sharpe_cand']:.3f} (delta={row['sharpe_delta']:+.3f})  "
          f"CDaR95 ctrl={row['CDaR95_ctrl']:.2f} cand={row['CDaR95_cand']:.2f}")
loyo_df = pd.DataFrame(loyo_rows)
loyo_df.to_csv(os.path.join(OUT, "r2v1_loyo.csv"), index=False)

print("\n" + "=" * 90, "\nROLLING WINDOWS (candidate-minus-incumbent cumulative delta trajectory)\n", "=" * 90, sep="")
m_sorted = m.sort_values("sess").reset_index(drop=True)
roll_rows = []
for w in [60, 120, 252]:
    roll_sum = m_sorted["delta"].rolling(w).sum()
    roll_rows.append({"window": w, "min_rolling_delta": float(roll_sum.min()),
                       "max_rolling_delta": float(roll_sum.max()),
                       "pct_windows_positive": float((roll_sum.dropna() > 0).mean() * 100),
                       "final_rolling_delta": float(roll_sum.iloc[-1]) if len(roll_sum.dropna()) else None})
    print(f"rolling {w}-session delta: min={roll_rows[-1]['min_rolling_delta']:.2f} "
          f"max={roll_rows[-1]['max_rolling_delta']:.2f} "
          f"%windows positive={roll_rows[-1]['pct_windows_positive']:.1f}%")
roll_df = pd.DataFrame(roll_rows)
roll_df.to_csv(os.path.join(OUT, "r2v1_rolling.csv"), index=False)

print("\n" + "=" * 90, "\nBLOCK BOOTSTRAP on paired daily delta (block=5, seed=20260809, matching S2_SELTIME R2 convention)\n", "=" * 90, sep="")
def block_bootstrap(x, block=5, n_boot=10000, seed=20260809):
    rng = np.random.default_rng(seed)
    n = len(x)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=(n_boot, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    samples = x[idx.reshape(n_boot, -1)[:, :n]]
    return samples

delta = m_sorted["delta"].to_numpy()
samples = block_bootstrap(delta)
boot_net = samples.sum(axis=1)
boot_sharpe = samples.mean(axis=1) / samples.std(axis=1, ddof=1) * np.sqrt(252)

# CDaR improvement: recompute per-bootstrap-sample synthetic candidate series = ctrl + resampled delta,
# using the ORIGINAL (non-resampled) ctrl trajectory paired with the resampled delta block-for-block
# is not well-posed path-wise; instead report CDaR improvement via the bootstrap's own drawdown proxy
# on the delta series' cumulative path (a standard block-bootstrap CDaR-of-delta diagnostic).
def cdar_of_path(x):
    eq = np.cumsum(x)
    peak = np.maximum.accumulate(eq)
    dd = peak - eq
    ddpos = np.sort(dd[dd > 0])[::-1]
    return ddpos[:max(1, int(0.05 * len(dd)))].mean() if len(ddpos) else 0.0

boot_cdar_of_delta = np.array([cdar_of_path(-s) for s in samples])  # drawdown of the delta path itself
actual_cdar_of_delta = cdar_of_path(-delta)

results = {
    "n_boot": 10000, "block": 5, "seed": 20260809,
    "P_delta_net_gt_0": float((boot_net > 0).mean()),
    "P_delta_sharpe_gt_0": float((boot_sharpe > 0).mean()),
    "median_delta_net": float(np.median(boot_net)),
    "delta_net_percentiles": {str(q): float(np.percentile(boot_net, q)) for q in [5, 25, 50, 75, 95]},
    "median_delta_sharpe": float(np.median(boot_sharpe)),
    "delta_sharpe_percentiles": {str(q): float(np.percentile(boot_sharpe, q)) for q in [5, 25, 50, 75, 95]},
    "actual_delta_net": float(delta.sum()),
    "actual_delta_sharpe_proxy": float(delta.mean() / delta.std(ddof=1) * np.sqrt(252)),
    "note_cdar": "CDaR-of-delta-path measures how bad the WORST drawdown episodes of "
                 "(candidate-incumbent) get, treating the delta series as its own equity path; "
                 "lower is better (less concentrated left tail in the outperformance itself).",
    "actual_cdar_of_delta_path": float(actual_cdar_of_delta),
    "median_boot_cdar_of_delta_path": float(np.median(boot_cdar_of_delta)),
}
print(json.dumps(results, indent=2))
json.dump(results, open(os.path.join(OUT, "r2v1_bootstrap.json"), "w"), indent=2)
print("\nsaved r2v1_year_by_year.csv, r2v1_quarter_by_quarter.csv, r2v1_loyo.csv, r2v1_rolling.csv, r2v1_bootstrap.json")
