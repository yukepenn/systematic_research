"""SMV2AJ_ATR_BLEND_R2 -- Gate B (chronology): LOYO dSharpe same sign >= 4/5
years AND fit 2022-24 -> eval 2025-26 point-positive, on the DUAL-transformed
dev legs from step0_verify.py (out/curves.csv: DUAL_CONTROL, DUAL_BLEND75).
Identical construction to runs/SMV2T_NOFAST_R2/gate_B.py.
"""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AJ_ATR_BLEND_R2")
OUT = os.path.join(RUN, "out")

curves = pd.read_csv(os.path.join(OUT, "curves.csv"))
curves["sess"] = pd.to_datetime(curves["sess"])
curves["year"] = curves["sess"].dt.year


def sharpe(x):
    x = np.asarray(x, dtype=float)
    sd = x.std(ddof=1)
    return x.mean() / sd * np.sqrt(252) if sd > 0 else np.nan


# ---------------- LOYO (per calendar year present in dev) ----------------
loyo_rows = []
for yr, g in curves.groupby("year"):
    shp_c = sharpe(g["DUAL_CONTROL"]); shp_b = sharpe(g["DUAL_BLEND75"])
    d_sharpe = shp_b - shp_c
    net_c = g["DUAL_CONTROL"].sum(); net_b = g["DUAL_BLEND75"].sum()
    loyo_rows.append({
        "year": int(yr), "n_days": len(g),
        "net_CONTROL": float(net_c), "net_BLEND75": float(net_b), "d_net": float(net_b - net_c),
        "sharpe_CONTROL": shp_c, "sharpe_BLEND75": shp_b, "d_sharpe": d_sharpe,
        "sign_d_sharpe": int(np.sign(d_sharpe)),
    })
loyo = pd.DataFrame(loyo_rows).sort_values("year").reset_index(drop=True)

n_years = len(loyo)
signs = loyo["sign_d_sharpe"].to_numpy()
pos_frac = float((signs > 0).sum()) / n_years
neg_frac = float((signs < 0).sum()) / n_years
dominant_frac = max(pos_frac, neg_frac)
dominant_sign = 1 if pos_frac >= neg_frac else -1
loyo_same_sign_pass = bool(dominant_sign > 0 and dominant_frac >= 0.8)  # need >=4/5 POSITIVE (favors challenger)
loyo.to_csv(os.path.join(OUT, "gate_B_loyo.csv"), index=False)
print(loyo.round(4).to_string(index=False))
print(f"\nLOYO years: {n_years}  same-sign(+) frac: {pos_frac:.3f}  "
      f"same-sign(-) frac: {neg_frac:.3f}  pass(>=4/5 positive): {loyo_same_sign_pass}", flush=True)

# ---------------- fit 2022-24 -> eval 2025-26 ----------------
fit = curves[curves["year"].isin([2022, 2023, 2024])]
ev = curves[curves["year"].isin([2025, 2026])]


def window_stats(g, label):
    shp_c = sharpe(g["DUAL_CONTROL"]); shp_b = sharpe(g["DUAL_BLEND75"])
    return {
        "window": label, "n_days": len(g),
        "net_CONTROL": float(g["DUAL_CONTROL"].sum()), "net_BLEND75": float(g["DUAL_BLEND75"].sum()),
        "d_net": float(g["DUAL_BLEND75"].sum() - g["DUAL_CONTROL"].sum()),
        "sharpe_CONTROL": shp_c, "sharpe_BLEND75": shp_b, "d_sharpe": shp_b - shp_c,
    }


fit_stats = window_stats(fit, "fit_2022_2024")
eval_stats = window_stats(ev, "eval_2025_2026")
eval_point_positive_sharpe = bool(eval_stats["d_sharpe"] > 0)
eval_point_positive_net = bool(eval_stats["d_net"] > 0)
fit_eval_pass = eval_point_positive_sharpe

fe = pd.DataFrame([fit_stats, eval_stats])
fe.to_csv(os.path.join(OUT, "gate_B_fit_eval.csv"), index=False)
print("\n" + fe.round(4).to_string(index=False), flush=True)

gateB_pass = bool(loyo_same_sign_pass and fit_eval_pass)

summary = pd.DataFrame([{
    "loyo_years": n_years, "loyo_pos_sign_frac": pos_frac, "loyo_neg_sign_frac": neg_frac,
    "loyo_same_sign_pass_ge_4of5_positive": loyo_same_sign_pass,
    "fit_window": "2022-2024", "eval_window": "2025-2026 (Jan-May, dev truncation)",
    "eval_d_sharpe": eval_stats["d_sharpe"], "eval_d_net": eval_stats["d_net"],
    "eval_point_positive_sharpe": eval_point_positive_sharpe,
    "eval_point_positive_net": eval_point_positive_net,
    "fit_eval_pass_on_dSharpe": fit_eval_pass,
    "gateB_pass": gateB_pass,
}])
summary.to_csv(os.path.join(OUT, "gate_B.csv"), index=False)
print("\n" + summary.to_string(index=False), flush=True)

json.dump({"gateB_pass": gateB_pass, "loyo_same_sign_pass": loyo_same_sign_pass,
           "fit_eval_pass": fit_eval_pass}, open(os.path.join(OUT, "gate_B_summary.json"), "w"), indent=2)
print("\ndone gate B", flush=True)
