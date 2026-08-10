"""U6B risk_panel Part 3 (sec7), capital-dependent leg. Two sweeps, both reusing
primary_objective_v2.primary_objective -- no separate bootstrap machinery is written.

(A) INTRADAY (bar-level) barrier check at R1=25%, across the FULL preregistered capital grid
    (same grid as Part 2), for CONTROL/F0.5/F0.7. This gives objective_J_intraday_barrier,
    p_ruin_intraday_barrier, and the bar-level CDaR at every capital level, directly comparable
    to Part 2's daily-close numbers at the same capital.

(B) Crossing-fraction probabilities (P_ruin at ruin_dd_frac in {0.10,0.20,0.30}, i.e. probability
    of a peak-to-trough drawdown crossing 10%/20%/30% of capital within the H=504-session
    horizon), at TWO representative capital levels ($100,000 headline; $150,000, inside the house
    capital-map's own $115k-$212k band from Part 1). DAILY-CLOSE only, for tractability --
    disclosed scope limitation (the bar-level barrier is already checked, at the R1=25%
    threshold, across the full capital grid in sweep A; extending the bar-level check to every
    (capital, threshold) pair would be a further ~18 x 30s of compute not repeated here).
"""
import os, sys, json, time
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
import primary_objective_v2 as PO2

RUN = os.path.join(ROOT, "runs", "U6B_PRODUCT_A_SCALE_RATE")
OUT = os.path.join(RUN, "risk_panel", "out")
os.makedirs(OUT, exist_ok=True)

CAPITAL_GRID = [50_000.0, 75_000.0, 100_000.0, 150_000.0, 200_000.0, 300_000.0, 500_000.0]
REPRESENTATIVE_CAPITALS = [100_000.0, 150_000.0]
CROSS_FRAC_GRID = [0.10, 0.20, 0.30]
CANDIDATES = {
    "CONTROL": os.path.join(RUN, "out", "CONTROL_daily_GENUINE_MNQ.csv"),
    "F0.5": os.path.join(RUN, "out", "F0.5_daily_GENUINE_MNQ.csv"),
    "F0.7": os.path.join(RUN, "out", "F0.7_daily_GENUINE_MNQ.csv"),
}
BARLEVEL = {
    name: os.path.join(RUN, "risk_panel", "out", f"{name}_barlevel_GENUINE_MNQ_canonical.parquet")
    for name in CANDIDATES
}

print("=" * 100)
print("SWEEP A -- intraday (bar-level) barrier at R1=25%, full capital grid")
print("=" * 100)
rows_a = []
t_start = time.time()
for name, path in CANDIDATES.items():
    idf = pd.read_parquet(BARLEVEL[name])
    for c in CAPITAL_GRID:
        t0 = time.time()
        r = PO2.primary_objective(
            path, capital=c, leverage=1.0, leverage_mode="fixed_fraction", label=f"{name}_C{c:.0f}",
            intraday_path=idf, intraday_col="mtm_from_open",
            intraday_sess_col="sess_date", intraday_last_col="is_last_of_sess")
        dt = time.time() - t0
        row = {
            "candidate": name, "capital": c,
            "J_daily": r["primary"]["objective_J"], "J_worst_daily": r["primary"]["J_worst_over_methods"],
            "ce_g_daily": r["primary"]["ce_log_growth_ann"], "p_ruin_daily": r["primary"]["p_ruin"],
            "J_intraday": r["primary"]["objective_J_intraday_barrier"],
            "ce_g_intraday": r["primary"]["ce_log_growth_ann_intraday_barrier"],
            "p_ruin_intraday": r["primary"]["p_ruin_intraday_barrier"],
            "J_worst_intraday": r["primary"]["J_worst_over_methods_intraday_barrier"],
            "p_ruin_gap_abs": r["ruin"]["gap"]["headline_abs"],
            "p_ruin_gap_rel": r["ruin"]["gap"]["headline_rel"],
            "p_ruin_gap_material": r["ruin"]["gap"]["material"],
            "cdar_matched_ratio_mixture": r["tail"]["gap"]["cdar_matched_ratio_mixture"],
            "cdar_eod_dollar_at_capital": r["tail"]["daily_close"]["moving5"]["cdar_dollar_at_capital"],
            "cdar_intraday_matched_dollar_at_capital": r["tail"]["intraday"]["moving5"]["cdar_dollar_daymax_at_capital"],
            "compute_seconds": dt,
        }
        rows_a.append(row)
        print(f"  [{time.time()-t_start:6.1f}s elapsed] {name} C=${c:>9,.0f}  "
              f"P_ruin daily={row['p_ruin_daily']:.4f}  intraday={row['p_ruin_intraday']:.4f}  "
              f"gap_abs={row['p_ruin_gap_abs']:+.4f}  material={row['p_ruin_gap_material']}  "
              f"({dt:.1f}s)", flush=True)
        with open(os.path.join(OUT, f"part3_full_result_{name}_C{int(c)}.json"), "w") as f:
            json.dump(r, f, indent=2, default=str)

sweepA = pd.DataFrame(rows_a)
sweepA.to_csv(os.path.join(OUT, "part3_sweepA_intraday_capital_grid.csv"), index=False)
print(f"\nSWEEP A total elapsed: {time.time()-t_start:.1f}s")

print()
print("=" * 100)
print("SWEEP B -- crossing-fraction probabilities (P_ruin at 10%/20%/30% of capital), "
      "daily-close, representative capitals " + str(REPRESENTATIVE_CAPITALS))
print("=" * 100)
rows_b = []
for name, path in CANDIDATES.items():
    for c in REPRESENTATIVE_CAPITALS:
        for thr in CROSS_FRAC_GRID:
            r = PO2.primary_objective(path, capital=c, leverage=1.0, leverage_mode="fixed_fraction",
                                       ruin_dd_frac=thr, label=f"{name}_C{c:.0f}_thr{thr}")
            rows_b.append({
                "candidate": name, "capital": c, "loss_fraction_threshold": thr,
                "p_cross_daily_close_mixture": r["primary"]["p_ruin"],
                "p_cross_daily_close_worst_of_three": r["ruin"]["daily_close"]["worst_of_three"],
            })
sweepB = pd.DataFrame(rows_b)
sweepB.to_csv(os.path.join(OUT, "part3_sweepB_crossing_fractions.csv"), index=False)
print(sweepB.to_string(index=False))

print("\n[risk_panel] Part 3 capital-dependent sweeps complete.")
