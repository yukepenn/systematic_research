"""R2B validation battery -- SAME rigor R2V1 applied to the confirm=2 candidate (which looked
promising on headline metrics and turned out to be a 2026-stub artifact). Year-by-year, quarter,
2022-2025 vs 2026-stub split, LOYO, rolling windows, block bootstrap (block=5, seed=20260809,
matching S2_SELTIME R2 / R2V1 convention), exact top/bottom-20 trade mapping, 2-tick cost stress.
No new favorable threshold invented after seeing results."""
import os, sys, json
import numpy as np, pandas as pd

SA0_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                        "SA0_SYSTEM_STRUCTURE", "src")
sys.path.insert(0, SA0_SRC)
import substrate as S
sys.path.insert(0, os.path.join(S.ROOT, "src", "analytics"))
from smv2_common import dd_battery

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

ctrl = pd.read_csv(os.path.join(OUT, "daily_FULL_NQ.csv"))
cand = pd.read_csv(os.path.join(OUT, "daily_R2B_RECLAIM_K6_NQ.csv"))
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
           "CDaR95_ctrl": bc["CDaR5"], "CDaR95_cand": bd["CDaR5"]}
    yr_rows.append(row)
    print(f"{yr}: net ctrl={row['net_ctrl']:.2f} cand={row['net_cand']:.2f} delta={row['delta_net']:.2f} | "
          f"sharpe ctrl={row['sharpe_ctrl']:.3f} cand={row['sharpe_cand']:.3f}")
yr_df = pd.DataFrame(yr_rows)
yr_df.to_csv(os.path.join(OUT, "r2b_year_by_year.csv"), index=False)

print("\n" + "=" * 90, "\n2022-2025-ONLY vs 2026-STUB\n", "=" * 90, sep="")
m2225 = m[m["year"] <= 2025]
m2026 = m[m["year"] == 2026]
delta_2225 = m2225["delta"].sum()
delta_2026 = m2026["delta"].sum()
b2225_ctrl = dd_battery(m2225["sess"], m2225["net_ctrl"].to_numpy(), label="ctrl_2225")
b2225_cand = dd_battery(m2225["sess"], m2225["net_cand"].to_numpy(), label="cand_2225")
print(f"2022-2025 ONLY: ctrl net={m2225['net_ctrl'].sum():.2f} sharpe={b2225_ctrl['sharpe']:.3f} | "
      f"cand net={m2225['net_cand'].sum():.2f} sharpe={b2225_cand['sharpe']:.3f} | delta={delta_2225:.2f}")
print(f"2026 stub only: delta={delta_2026:.2f} (n_days={len(m2026)})")
print(f"full-history delta = {m['delta'].sum():.2f} ({delta_2225:.2f} from 2022-2025 + {delta_2026:.2f} from 2026 stub)")

print("\n" + "=" * 90, "\nLOYO (leave-one-year-out)\n", "=" * 90, sep="")
loyo_rows = []
for yr in sorted(m["year"].unique()):
    g = m[m["year"] != yr]
    bc = dd_battery(g["sess"], g["net_ctrl"].to_numpy(), label=f"ctrl_loyo_{yr}")
    bd = dd_battery(g["sess"], g["net_cand"].to_numpy(), label=f"cand_loyo_{yr}")
    row = {"loyo_removed_year": yr, "delta_net": g["delta"].sum(),
           "sharpe_ctrl": bc["sharpe"], "sharpe_cand": bd["sharpe"],
           "sharpe_delta": bd["sharpe"] - bc["sharpe"]}
    loyo_rows.append(row)
    print(f"LOYO-{yr} (removed): delta_net={row['delta_net']:.2f}  sharpe ctrl={row['sharpe_ctrl']:.3f} "
          f"cand={row['sharpe_cand']:.3f} (delta={row['sharpe_delta']:+.3f})")
loyo_df = pd.DataFrame(loyo_rows)
loyo_df.to_csv(os.path.join(OUT, "r2b_loyo.csv"), index=False)

print("\n" + "=" * 90, "\nROLLING WINDOWS\n", "=" * 90, sep="")
m_sorted = m.sort_values("sess").reset_index(drop=True)
roll_rows = []
for w in [60, 120, 252]:
    roll_sum = m_sorted["delta"].rolling(w).sum()
    roll_rows.append({"window": w, "min_rolling_delta": float(roll_sum.min()),
                       "max_rolling_delta": float(roll_sum.max()),
                       "pct_windows_positive": float((roll_sum.dropna() > 0).mean() * 100)})
    print(f"rolling {w}-session delta: min={roll_rows[-1]['min_rolling_delta']:.2f} "
          f"max={roll_rows[-1]['max_rolling_delta']:.2f} "
          f"%windows positive={roll_rows[-1]['pct_windows_positive']:.1f}%")
pd.DataFrame(roll_rows).to_csv(os.path.join(OUT, "r2b_rolling.csv"), index=False)

print("\n" + "=" * 90, "\nBLOCK BOOTSTRAP (block=5, seed=20260809, matching R2V1/S2_SELTIME R2 convention)\n", "=" * 90, sep="")
def block_bootstrap(x, block=5, n_boot=10000, seed=20260809):
    rng = np.random.default_rng(seed)
    n = len(x)
    nb = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=(n_boot, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    return x[idx.reshape(n_boot, -1)[:, :n]]

delta = m_sorted["delta"].to_numpy()
samples = block_bootstrap(delta)
boot_net = samples.sum(axis=1)
boot_sharpe = samples.mean(axis=1) / samples.std(axis=1, ddof=1) * np.sqrt(252)
results = {
    "P_delta_net_gt_0": float((boot_net > 0).mean()),
    "P_delta_sharpe_gt_0": float((boot_sharpe > 0).mean()),
    "median_delta_net": float(np.median(boot_net)),
    "delta_net_percentiles": {str(q): float(np.percentile(boot_net, q)) for q in [5, 25, 50, 75, 95]},
    "actual_delta_net": float(delta.sum()),
}
print(json.dumps(results, indent=2))
json.dump(results, open(os.path.join(OUT, "r2b_bootstrap.json"), "w"), indent=2)

print("\n" + "=" * 90, "\nEXACT TOP-20/BOTTOM-20 TRADE MAPPING\n", "=" * 90, sep="")
ledger = pd.read_parquet(S.LEDGER_PATH, columns=["t_idx", "block_id"])
block_sum = pd.read_csv(S.BLOCKSUM_PATH)
bpnl_cand = np.load(os.path.join(OUT, "pos_R2B_RECLAIM_K6.npy"))  # placeholder read to confirm exists
pos_r2b = np.load(os.path.join(OUT, "pos_R2B_RECLAIM_K6.npy"))
_, _, bpnl_r2b_nq = S.onelot_exec(pos_r2b, S.COMM_NQ, S.PV_NQ, S.open_, S.high, S.low, S.close)

def exact_span_pnl(block_id):
    idx = ledger.loc[ledger["block_id"] == block_id, "t_idx"].to_numpy()
    return float(bpnl_r2b_nq[idx].sum())

top20 = block_sum.nlargest(20, "net_pnl").copy()
bot20 = block_sum.nsmallest(20, "net_pnl").copy()
top20["r2b_same_span_pnl"] = top20["block_id"].apply(exact_span_pnl)
bot20["r2b_same_span_pnl"] = bot20["block_id"].apply(exact_span_pnl)
top20.to_csv(os.path.join(OUT, "r2b_top20_mapping.csv"), index=False)
bot20.to_csv(os.path.join(OUT, "r2b_bottom20_mapping.csv"), index=False)
print(f"top-20 retention: {100*top20['r2b_same_span_pnl'].sum()/top20['net_pnl'].sum():.1f}% "
      f"(incumbent {top20['net_pnl'].sum():.2f} -> R2B {top20['r2b_same_span_pnl'].sum():.2f})")
print(f"bottom-20 change: incumbent {bot20['net_pnl'].sum():.2f} -> R2B {bot20['r2b_same_span_pnl'].sum():.2f}")

print("\n" + "=" * 90, "\n2-TICK COST STRESS\n", "=" * 90, sep="")
# adverse-slip stress: reuse onelot_exec but with commission bumped to simulate 2-tick extra slip
# (NQ tick=$5, so 2-tick round-trip extra cost = 2*5=$10 per contract per side, matching this
# repo's standing 1-tick-baseline -> 2-tick-stress convention: add 1 extra tick of adverse slip
# per side beyond the already-embedded 1-tick synthetic fill, i.e. +$5/side additional)
EXTRA_SLIP_PER_SIDE = 5.0  # 1 extra tick, NQ $5/tick, added on top of the existing 1-tick convention
_, _, bpnl_ctrl_stress = S.onelot_exec(S.build_pos_seq(S.M, S.ENTRY_LEVEL, S.EXIT_LEVEL),
                                        S.COMM_NQ + EXTRA_SLIP_PER_SIDE, S.PV_NQ, S.open_, S.high, S.low, S.close)
_, _, bpnl_r2b_stress = S.onelot_exec(pos_r2b, S.COMM_NQ + EXTRA_SLIP_PER_SIDE, S.PV_NQ, S.open_, S.high, S.low, S.close)
ctrl_stress_net = float(bpnl_ctrl_stress.sum())
r2b_stress_net = float(bpnl_r2b_stress.sum())
print(f"2-tick stress: ctrl net={ctrl_stress_net:.2f}  R2B net={r2b_stress_net:.2f}  "
      f"delta={r2b_stress_net-ctrl_stress_net:.2f}")

stress_2225 = pd.DataFrame({"sess": S.sess_arr, "year": S.year_arr,
                             "ctrl": bpnl_ctrl_stress, "cand": bpnl_r2b_stress})
stress_yby = stress_2225.groupby("year").apply(lambda g: (g["cand"] - g["ctrl"]).sum())
print("2-tick stress delta by year:")
print(stress_yby)

json.dump({
    "extra_slip_per_side": EXTRA_SLIP_PER_SIDE,
    "ctrl_stress_net": ctrl_stress_net, "r2b_stress_net": r2b_stress_net,
    "delta": r2b_stress_net - ctrl_stress_net,
    "delta_2022_2025_only": float(stress_yby[stress_yby.index <= 2025].sum()),
    "delta_2026_stub": float(stress_yby.get(2026, 0.0)),
}, open(os.path.join(OUT, "r2b_cost_stress.json"), "w"), indent=2)

print("\nR2B validation battery complete.")
