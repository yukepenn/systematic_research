"""PA0 sec31 -- exposure-path science + clamp-binding analysis. sec33 -- long/short asymmetry."""
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import pa0_substrate as P

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")

barpos = P.barpos_ctrl
bpnl = P.bpnl_ctrl
n = P.n

print("=" * 90, "\nSEC31 -- BAR-LEVEL P&L BY EXPOSURE-MAGNITUDE BAND\n", "=" * 90, sep="")
abs_pos = np.abs(barpos)
band = pd.cut(abs_pos, [-0.5, 0.5, 3.5, 6.5, 9.5, 13.5], labels=["0(flat)", "1-3", "4-6", "7-9", "10-13"])
band_df = pd.DataFrame({"band": band, "pnl": bpnl})
g = band_df.groupby("band", observed=True).agg(n_bars=("pnl", "size"), sum_pnl=("pnl", "sum"),
                                                  mean_pnl_per_bar=("pnl", "mean"))
g["mean_pnl_per_bar_per_contract"] = g["sum_pnl"] / (band_df.groupby("band", observed=True)["pnl"].apply(
    lambda x: abs_pos[x.index].sum()))
print(g.round(4))
g.to_csv(os.path.join(OUT, "sec31_pnl_by_exposure_band.csv"))

print("\n" + "=" * 90, "\nCLAMP BINDING: bars where the UNCONSTRAINED continuous M would exceed +-13\n", "=" * 90, sep="")
m_arr = np.where((P.T != 0) & (P.tilt_state != 0) & (np.sign(P.T) == P.tilt_state), P.TILTMULT, 1.0)
s_arr = np.where((P.T < 0) & (P.tilt_state > 0), P.SHORTHALF, 1.0)
Tpp_cont = P.T * m_arr * s_arr * P.TILTRESCALE
M_cont = P.KSOLAR * Tpp_cont + P.KBMOM * P.B
clamp_bind = np.abs(M_cont) > 13
print(f"bars where continuous M exceeds +-13 (clamp WOULD bind): {clamp_bind.sum()} "
      f"({100*clamp_bind.mean():.3f}% of all bars)")
# P&L on bars actually AT the clamp ceiling (|barpos|==13)
at_cap = abs_pos >= 13
print(f"bars where ACTUAL position is at the +-13 cap: {at_cap.sum()} ({100*at_cap.mean():.3f}% of all bars), "
      f"sum_pnl on those bars = {bpnl[at_cap].sum():.2f}, mean = {bpnl[at_cap].mean():.4f}/bar")
print(f"(for comparison, mean pnl/bar overall = {bpnl.mean():.4f})")

print("\n" + "=" * 90, "\nSEC31 -- EXPOSURE TRANSITION CLASSIFICATION\n", "=" * 90, sep="")
change_idx = np.where(np.diff(barpos) != 0)[0] + 1  # bar index where position CHANGED (new value)
prev_pos = barpos[change_idx - 1]
new_pos = barpos[change_idx]


def classify(prev, new):
    if prev == 0 and new > 0:
        return "FRESH_LONG"
    if prev == 0 and new < 0:
        return "FRESH_SHORT"
    if prev > 0 and new > prev:
        return "SCALE_IN_LONG"
    if prev > 0 and 0 < new < prev:
        return "SCALE_OUT_LONG"
    if prev > 0 and new == 0:
        return "FLAT_EXIT_LONG"
    if prev > 0 and new < 0:
        return "REVERSAL_LONG_TO_SHORT"
    if prev < 0 and new < prev:
        return "SCALE_IN_SHORT"
    if prev < 0 and prev < new < 0:
        return "SCALE_OUT_SHORT"
    if prev < 0 and new == 0:
        return "FLAT_EXIT_SHORT"
    if prev < 0 and new > 0:
        return "REVERSAL_SHORT_TO_LONG"
    return "OTHER"


trans = pd.DataFrame({"t_idx": change_idx, "prev_pos": prev_pos, "new_pos": new_pos})
trans["transition"] = [classify(p, nw) for p, nw in zip(prev_pos, new_pos)]
trans["contracts_changed"] = np.abs(new_pos - prev_pos)

# forward 20-bar P&L per unit contract changed, following each transition (a proxy for "was this
# specific size-change decision, on the margin, subsequently rewarded")
FWD = 20
fwd_pnl = []
for _, r in trans.iterrows():
    t0 = int(r["t_idx"])
    fwd = bpnl[t0: min(t0 + FWD, n)].sum()
    fwd_pnl.append(fwd)
trans["fwd20_pnl"] = fwd_pnl
trans["fwd20_pnl_per_contract"] = trans["fwd20_pnl"] / trans["contracts_changed"]

summary_trans = trans.groupby("transition").agg(
    n=("transition", "size"), total_contracts_changed=("contracts_changed", "sum"),
    mean_fwd20_pnl=("fwd20_pnl", "mean"), mean_fwd20_pnl_per_contract=("fwd20_pnl_per_contract", "mean"))
print(summary_trans.round(2))
summary_trans.to_csv(os.path.join(OUT, "sec31_transition_classes.csv"))
trans.to_csv(os.path.join(OUT, "sec31_all_transitions.csv"), index=False)

# initial unit vs scale-in unit value: compare FRESH_LONG/SHORT's per-contract fwd value to
# SCALE_IN_LONG/SHORT's per-contract fwd value
fresh = trans[trans["transition"].isin(["FRESH_LONG", "FRESH_SHORT"])]
scale_in = trans[trans["transition"].isin(["SCALE_IN_LONG", "SCALE_IN_SHORT"])]
scale_out = trans[trans["transition"].isin(["SCALE_OUT_LONG", "SCALE_OUT_SHORT"])]
print(f"\nFRESH entries: n={len(fresh)}, mean fwd20 pnl/contract = {fresh['fwd20_pnl_per_contract'].mean():.2f}")
print(f"SCALE_IN (adding to winners): n={len(scale_in)}, mean fwd20 pnl/contract = {scale_in['fwd20_pnl_per_contract'].mean():.2f}")
print(f"SCALE_OUT (reducing): n={len(scale_out)}, mean fwd20 pnl/contract = {scale_out['fwd20_pnl_per_contract'].mean():.2f}")

print("\n" + "=" * 90, "\nSEC33 -- LONG/SHORT EXPOSURE ASYMMETRY (Product A)\n", "=" * 90, sep="")
long_pnl = bpnl[barpos > 0].sum()
short_pnl = bpnl[barpos < 0].sum()
long_daily = pd.DataFrame({"sess": P.sd, "pnl": np.where(barpos > 0, bpnl, 0.0)}).groupby("sess")["pnl"].sum().reset_index()
long_daily.columns = ["sess", "net"]
short_daily = pd.DataFrame({"sess": P.sd, "pnl": np.where(barpos < 0, bpnl, 0.0)}).groupby("sess")["pnl"].sum().reset_index()
short_daily.columns = ["sess", "net"]
row_long = P.battery_row("A_LONG", long_daily)
row_short = P.battery_row("A_SHORT", short_daily)
print(f"LONG:  net={row_long['net']:.2f} sharpe={row_long['sharpe']:.3f} maxDD={row_long['maxDD_eod']:.2f} "
      f"CDaR95={row_long['CDaR95']:.2f} avg|exposure|={np.mean(barpos[barpos>0]) if (barpos>0).any() else 0:.3f}")
print(f"SHORT: net={row_short['net']:.2f} sharpe={row_short['sharpe']:.3f} maxDD={row_short['maxDD_eod']:.2f} "
      f"CDaR95={row_short['CDaR95']:.2f} avg|exposure|={np.mean(np.abs(barpos[barpos<0])) if (barpos<0).any() else 0:.3f}")

yby_ls = pd.DataFrame({"year": P.year_arr,
                        "long": np.where(barpos > 0, bpnl, 0.0),
                        "short": np.where(barpos < 0, bpnl, 0.0)}).groupby("year")[["long", "short"]].sum()
print("\nyear-by-year long vs short (Product A):")
print(yby_ls.round(2))
yby_ls.to_csv(os.path.join(OUT, "sec33_long_short_year_by_year.csv"))

json.dump({"long_battery": row_long, "short_battery": row_short,
           "clamp_bind_pct": float(clamp_bind.mean() * 100), "at_cap_pct": float(at_cap.mean() * 100),
           "at_cap_mean_pnl_per_bar": float(bpnl[at_cap].mean()) if at_cap.any() else None,
           "fresh_fwd20_per_contract": float(fresh["fwd20_pnl_per_contract"].mean()),
           "scale_in_fwd20_per_contract": float(scale_in["fwd20_pnl_per_contract"].mean()),
           "scale_out_fwd20_per_contract": float(scale_out["fwd20_pnl_per_contract"].mean())},
          open(os.path.join(OUT, "sec31_33_summary.json"), "w"), indent=2)

print("\nPA0 sec31/sec33 complete.")
