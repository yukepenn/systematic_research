"""PA0 sec30 -- alpha vs sizing decomposition. Risk-normalized comparisons throughout."""
import os, sys, json
import numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import pa0_substrate as P

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "out")
os.makedirs(OUT, exist_ok=True)


def avg_abs_exposure(barpos):
    return float(np.mean(np.abs(barpos)))


print("=" * 90, "\nSEC30 -- ALPHA vs SIZING DECOMPOSITION\n", "=" * 90, sep="")

# (a) FULL control, already computed in substrate
row_full = P.battery_row("FULL", P.daily_ctrl)
avg_exp_full = avg_abs_exposure(P.barpos_ctrl)
print(f"FULL (actual Product A): net={row_full['net']:.2f} sharpe={row_full['sharpe']:.3f} "
      f"avg|exposure|={avg_exp_full:.3f} contracts  sharpe/avg_exposure={row_full['sharpe']/avg_exp_full:.4f}")

# (b) DECISION ALPHA proxy: sign(continuous M) traded at exactly 1 contract, same lag/C4 logic
m_arr = np.where((P.T != 0) & (P.tilt_state != 0) & (np.sign(P.T) == P.tilt_state), P.TILTMULT, 1.0)
s_arr = np.where((P.T < 0) & (P.tilt_state > 0), P.SHORTHALF, 1.0)
Tpp_cont = P.T * m_arr * s_arr * P.TILTRESCALE
M_cont = P.KSOLAR * Tpp_cont + P.KBMOM * P.B
sign_target = np.sign(M_cont).astype(int)  # {-1,0,1}, continuous-M-derived direction


def sign_only_exec(tgt_seq):
    cash = 0.0; p = 0; pend = 0; prev_eq = 0.0
    n = P.n
    bar_pos = np.zeros(n, dtype=int); bar_pnl = np.zeros(n)
    for t in range(n):
        if pend != p:
            d = pend - p
            side = 1 if d > 0 else -1
            px = P._fill(P.open_[t], P.high[t], P.low[t], side)
            cash -= d * px * P.PV_MNQ
            cash -= abs(d) * P.COMM_MNQ
            p = pend
        if P.last[t] and p != 0:
            side = -1 if p > 0 else 1
            px = P._fill(P.open_[t], P.high[t], P.low[t], side, at_close=P.close[t])
            cash += p * px * P.PV_MNQ
            cash -= abs(p) * P.COMM_MNQ
            p = 0; pend = 0
        else:
            tgt_raw = int(tgt_seq[t])
            if P.forced_flat_c4[t]:
                tgt = 0
            elif P.entry_blocked_c4[t]:
                tgt = 0 if (tgt_raw == 0 or p == 0 or np.sign(tgt_raw) != np.sign(p)) else tgt_raw
            else:
                tgt = tgt_raw
            pend = tgt
        eq = cash + p * P.close[t] * P.PV_MNQ
        bar_pnl[t] = eq - prev_eq; prev_eq = eq
        bar_pos[t] = p
    dd = pd.DataFrame({"sess": P.bars["sess_date"], "pnl": bar_pnl}).groupby("sess")["pnl"].sum().reset_index()
    dd.columns = ["sess", "net"]
    return dd, bar_pos, bar_pnl


daily_sign, barpos_sign, bpnl_sign = sign_only_exec(sign_target)
row_sign = P.battery_row("SIGN_ONLY_1CONTRACT", daily_sign)
avg_exp_sign = avg_abs_exposure(barpos_sign)
print(f"SIGN_ONLY (1-contract decision-alpha proxy): net={row_sign['net']:.2f} "
      f"sharpe={row_sign['sharpe']:.3f} avg|exposure|={avg_exp_sign:.3f} "
      f"sharpe/avg_exposure={row_sign['sharpe']/avg_exp_sign:.4f}")

# (c) CONTINUOUS UNROUNDED/UNCLAMPED proxy: same weights, no round()/clip() -- isolates the
# rounding+clamp mechanism's OWN contribution vs the actual integer-contract FULL object.
daily_cont, barpos_cont, bpnl_cont, M_cont2 = P.product_a_exec(P.T, "CONTINUOUS", apply_round_clamp=False)
row_cont = P.battery_row("CONTINUOUS_NO_ROUND_CLAMP", daily_cont)
avg_exp_cont = avg_abs_exposure(barpos_cont)
print(f"CONTINUOUS (no round/clamp): net={row_cont['net']:.2f} sharpe={row_cont['sharpe']:.3f} "
      f"avg|exposure|={avg_exp_cont:.3f} sharpe/avg_exposure={row_cont['sharpe']/avg_exp_cont:.4f}")

decomp = pd.DataFrame([row_full, row_sign, row_cont])
decomp["avg_abs_exposure"] = [avg_exp_full, avg_exp_sign, avg_exp_cont]
decomp["sharpe_per_unit_exposure"] = decomp["sharpe"] / decomp["avg_abs_exposure"]
decomp.to_csv(os.path.join(OUT, "sec30_alpha_vs_sizing.csv"), index=False)
print("\n" + decomp[["tag", "net", "sharpe", "maxDD_eod", "avg_abs_exposure", "sharpe_per_unit_exposure"]].round(4).to_string(index=False))

# year-by-year for each of the 3
yby = {}
for tag, bpnl in [("FULL", P.bpnl_ctrl), ("SIGN_ONLY", bpnl_sign), ("CONTINUOUS", bpnl_cont)]:
    yby[tag] = pd.DataFrame({"year": P.year_arr, "pnl": bpnl}).groupby("year")["pnl"].sum().to_dict()
yby_df = pd.DataFrame(yby)
print("\nyear-by-year net by construction:")
print(yby_df.round(2))
yby_df.to_csv(os.path.join(OUT, "sec30_year_by_year.csv"))

summary = {
    "FULL_net": row_full["net"], "SIGN_ONLY_net": row_sign["net"], "CONTINUOUS_net": row_cont["net"],
    "FULL_sharpe": row_full["sharpe"], "SIGN_ONLY_sharpe": row_sign["sharpe"], "CONTINUOUS_sharpe": row_cont["sharpe"],
    "net_added_by_sizing_beyond_sign": row_full["net"] - row_sign["net"],
    "net_added_by_rounding_clamp_vs_continuous": row_full["net"] - row_cont["net"],
    "sharpe_per_unit_exposure_FULL": row_full["sharpe"] / avg_exp_full,
    "sharpe_per_unit_exposure_SIGN_ONLY": row_sign["sharpe"] / avg_exp_sign,
}
json.dump(summary, open(os.path.join(OUT, "sec30_summary.json"), "w"), indent=2)
print("\n" + json.dumps(summary, indent=2))
print("\nPA0 sec30 complete.")
