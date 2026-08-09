"""H0 sec6 -- exposure-band P&L contribution (mirrors PA0 sec31's band table), computed on the
CANONICAL window (must reconcile against PA0's own published sec31_pnl_by_exposure_band.csv
numbers) and on the health-only extension (does the pattern continue or break). sec7 -- scale-in
vs fresh-entry forward-20-bar value (mirrors PA0 sec31's transition-class table), same canonical
reconciliation + extension check."""
import os, sys, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
PA0_OUT = os.path.join(ROOT, "runs", "PA0_PRODUCT_A_STRUCTURE", "out")

u0 = pd.read_parquet(os.path.join(ROOT, "runs", "U0_UNIFIED_STATE", "out", "u0_state_table.parquet"),
                      columns=["t_idx", "sess_date", "target_exposure_A", "bar_pnl_A_dollars",
                               "is_health_only_bar"])
u0 = u0.sort_values("t_idx").reset_index(drop=True)
barpos = u0["target_exposure_A"].to_numpy()
bpnl = u0["bar_pnl_A_dollars"].to_numpy()
is_health = u0["is_health_only_bar"].to_numpy()
n = len(u0)

# ============================================================== SEC6 -- EXPOSURE-BAND P&L (canonical + extension)
print("=" * 90, "\nSEC6 -- BAR-LEVEL P&L BY EXPOSURE-MAGNITUDE BAND\n", "=" * 90, sep="")


def band_table(mask, label):
    abs_pos = np.abs(barpos[mask]); pnl = bpnl[mask]
    band = pd.cut(abs_pos, [-0.5, 0.5, 3.5, 6.5, 9.5, 13.5], labels=["0(flat)", "1-3", "4-6", "7-9", "10-13"])
    d = pd.DataFrame({"band": band, "pnl": pnl, "abs_pos": abs_pos})
    g = d.groupby("band", observed=True).agg(n_bars=("pnl", "size"), sum_pnl=("pnl", "sum"),
                                              mean_pnl_per_bar=("pnl", "mean"))
    g["mean_pnl_per_bar_per_contract"] = g["sum_pnl"] / d.groupby("band", observed=True)["abs_pos"].sum()
    g["window"] = label
    print(f"\n-- {label} --")
    print(g.round(4))
    return g.reset_index()


canon_mask = ~is_health
health_mask = is_health
full_mask = np.ones(n, dtype=bool)

g_canon = band_table(canon_mask, "CANONICAL (<=2026-05-29)")
g_health = band_table(health_mask, "HEALTH-ONLY EXTENSION (2026-06-01..2026-07-31)")
g_full = band_table(full_mask, "FULL HISTORY")
band_all = pd.concat([g_canon, g_health, g_full], ignore_index=True)
band_all.to_csv(os.path.join(OUT, "sec6_pnl_by_exposure_band.csv"), index=False)

# reconciliation vs PA0's own published numbers
pa0_band = pd.read_csv(os.path.join(PA0_OUT, "sec31_pnl_by_exposure_band.csv"))
print("\n-- RECONCILIATION vs PA0's published sec31_pnl_by_exposure_band.csv (canonical window) --")
recon_cmp = g_canon.set_index("band")[["n_bars", "sum_pnl"]].join(
    pa0_band.set_index("band")[["n_bars", "sum_pnl"]], lsuffix="_H0", rsuffix="_PA0")
recon_cmp["n_bars_diff"] = recon_cmp["n_bars_H0"] - recon_cmp["n_bars_PA0"]
recon_cmp["sum_pnl_diff"] = recon_cmp["sum_pnl_H0"] - recon_cmp["sum_pnl_PA0"]
print(recon_cmp.round(2))
recon_cmp.to_csv(os.path.join(OUT, "sec6_reconciliation_vs_PA0.csv"))
max_abs_diff = recon_cmp["sum_pnl_diff"].abs().max()
print(f"\nmax |sum_pnl diff| across bands (H0 canonical vs PA0 published): {max_abs_diff:.2f} "
      f"-> {'EXACT MATCH (rounding only)' if max_abs_diff < 1.0 else 'DIVERGES -- investigate'}")

# ============================================================== SEC7 -- TRANSITION CLASSES (scale-in vs fresh)
print("\n" + "=" * 90, "\nSEC7 -- EXPOSURE TRANSITION CLASSIFICATION (fwd-20-bar P&L per contract changed)\n",
      "=" * 90, sep="")


def classify(prev, new):
    if prev == 0 and new > 0: return "FRESH_LONG"
    if prev == 0 and new < 0: return "FRESH_SHORT"
    if prev > 0 and new > prev: return "SCALE_IN_LONG"
    if prev > 0 and 0 < new < prev: return "SCALE_OUT_LONG"
    if prev > 0 and new == 0: return "FLAT_EXIT_LONG"
    if prev > 0 and new < 0: return "REVERSAL_LONG_TO_SHORT"
    if prev < 0 and new < prev: return "SCALE_IN_SHORT"
    if prev < 0 and prev < new < 0: return "SCALE_OUT_SHORT"
    if prev < 0 and new == 0: return "FLAT_EXIT_SHORT"
    if prev < 0 and new > 0: return "REVERSAL_SHORT_TO_LONG"
    return "OTHER"


def transition_table(mask_name, t_start, t_end, bpnl_full):
    """t_start/t_end delimit the bar-index sub-range (inclusive) this window covers; fwd-20 P&L is
    still measured against the FULL bar series (bpnl_full) so a transition near a window boundary
    isn't artificially truncated -- matches PA0's own convention of measuring forward value in the
    engine's own bar sequence, not window-clipped."""
    sub_idx = np.arange(t_start, t_end + 1)
    sub_pos = barpos[sub_idx]
    change_idx_local = np.where(np.diff(sub_pos) != 0)[0] + 1
    change_idx = sub_idx[change_idx_local]
    prev_pos = barpos[change_idx - 1]
    new_pos = barpos[change_idx]
    trans = pd.DataFrame({"t_idx": change_idx, "prev_pos": prev_pos, "new_pos": new_pos})
    trans["transition"] = [classify(p, nw) for p, nw in zip(prev_pos, new_pos)]
    trans["contracts_changed"] = np.abs(trans["new_pos"] - trans["prev_pos"])
    FWD = 20
    fwd_pnl = [bpnl_full[t0: min(t0 + FWD, len(bpnl_full))].sum() for t0 in trans["t_idx"]]
    trans["fwd20_pnl"] = fwd_pnl
    trans["fwd20_pnl_per_contract"] = trans["fwd20_pnl"] / trans["contracts_changed"]
    summ = trans.groupby("transition").agg(
        n=("transition", "size"), total_contracts_changed=("contracts_changed", "sum"),
        mean_fwd20_pnl=("fwd20_pnl", "mean"), mean_fwd20_pnl_per_contract=("fwd20_pnl_per_contract", "mean"))
    print(f"\n-- {mask_name} --")
    print(summ.round(2))
    fresh = trans[trans["transition"].isin(["FRESH_LONG", "FRESH_SHORT"])]
    scale_in = trans[trans["transition"].isin(["SCALE_IN_LONG", "SCALE_IN_SHORT"])]
    scale_out = trans[trans["transition"].isin(["SCALE_OUT_LONG", "SCALE_OUT_SHORT"])]
    r = {"window": mask_name,
         "fresh_n": len(fresh), "fresh_fwd20_per_contract": float(fresh["fwd20_pnl_per_contract"].mean()) if len(fresh) else np.nan,
         "scale_in_n": len(scale_in), "scale_in_fwd20_per_contract": float(scale_in["fwd20_pnl_per_contract"].mean()) if len(scale_in) else np.nan,
         "scale_out_n": len(scale_out), "scale_out_fwd20_per_contract": float(scale_out["fwd20_pnl_per_contract"].mean()) if len(scale_out) else np.nan}
    r["scale_in_multiple_of_fresh"] = (r["scale_in_fwd20_per_contract"] / r["fresh_fwd20_per_contract"]
                                        if r["fresh_fwd20_per_contract"] not in (0, np.nan) and not np.isnan(r["fresh_fwd20_per_contract"]) else np.nan)
    return summ, r


canon_idx = np.where(canon_mask)[0]
health_idx = np.where(health_mask)[0]
summ_canon, r_canon = transition_table("CANONICAL (<=2026-05-29)", canon_idx.min(), canon_idx.max(), bpnl)
summ_health, r_health = transition_table("HEALTH-ONLY EXTENSION (2026-06-01..2026-07-31)", health_idx.min(), health_idx.max(), bpnl)
summ_full, r_full = transition_table("FULL HISTORY", 0, n - 1, bpnl)

trans_summary = pd.DataFrame([r_canon, r_health, r_full])
print("\n-- summary across windows --")
print(trans_summary.round(3).to_string(index=False))
trans_summary.to_csv(os.path.join(OUT, "sec7_transition_summary.csv"), index=False)
summ_canon.to_csv(os.path.join(OUT, "sec7_transition_classes_canonical.csv"))
summ_health.to_csv(os.path.join(OUT, "sec7_transition_classes_health.csv"))

# reconciliation vs PA0's own published transition numbers (FRESH +2.03, SCALE_IN +14.43)
pa0_summary = json.load(open(os.path.join(PA0_OUT, "sec31_33_summary.json")))
print(f"\n-- RECONCILIATION vs PA0 published: FRESH fwd20/contract = "
      f"{pa0_summary['fresh_fwd20_per_contract']:.2f} (PA0) vs {r_canon['fresh_fwd20_per_contract']:.2f} (H0 canonical)")
print(f"   SCALE_IN fwd20/contract = {pa0_summary['scale_in_fwd20_per_contract']:.2f} (PA0) vs "
      f"{r_canon['scale_in_fwd20_per_contract']:.2f} (H0 canonical)")

json.dump({"pa0_fresh": pa0_summary["fresh_fwd20_per_contract"], "h0_canon_fresh": r_canon["fresh_fwd20_per_contract"],
           "pa0_scale_in": pa0_summary["scale_in_fwd20_per_contract"], "h0_canon_scale_in": r_canon["scale_in_fwd20_per_contract"],
           "h0_health_fresh": r_health["fresh_fwd20_per_contract"], "h0_health_scale_in": r_health["scale_in_fwd20_per_contract"]},
          open(os.path.join(OUT, "sec7_pa0_reconciliation.json"), "w"), indent=2)

print("\n[H0] sec6/sec7 exposure-band + transition-class analysis complete.")
