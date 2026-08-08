"""SMV2AF_1MIN_RESCALE_R2 -- Gate B (chronology): LOYO same-sign Sharpe >= 4/5 years AND
fit-2022-24/eval-2025-26 point-positive, on the rescaled arm's OWN daily PnL (identical
per-calendar-year convention to runs/SMV2T_NOFAST_R2/gate_B.py and
runs/SMV2W_5MCLOCK_R2/gate_B.py -- adapted from a paired-diff object to a single-arm object
per this spec's own object: "LOYO same-sign Sharpe >= 4/5 years" of the arm itself, not a
diff vs a reference leg).
"""
import os, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AF_1MIN_RESCALE_R2")
OUT = os.path.join(RUN, "out")

curves = pd.read_csv(os.path.join(OUT, "dev_daily_curves.csv"), parse_dates=["sess"])
curves["year"] = curves["sess"].dt.year

def sharpe(v):
    v = np.asarray(v, dtype=float)
    sd = v.std(ddof=1)
    return v.mean() / sd * np.sqrt(252) if sd > 0 else np.nan

# ---------------- per-calendar-year Sharpe/sign ----------------
loyo_rows = []
for yr, g in curves.groupby("year"):
    shp = sharpe(g["net_1m_rescaled"])
    net = g["net_1m_rescaled"].sum()
    loyo_rows.append({
        "year": int(yr), "n_days": len(g), "net": float(net), "sharpe": shp,
        "sign_sharpe": int(np.sign(shp)) if np.isfinite(shp) else 0,
    })
loyo = pd.DataFrame(loyo_rows).sort_values("year").reset_index(drop=True)

n_years = len(loyo)
signs = loyo["sign_sharpe"].to_numpy()
pos_frac = float((signs > 0).sum()) / n_years
neg_frac = float((signs < 0).sum()) / n_years
dominant_frac = max(pos_frac, neg_frac)
dominant_sign = 1 if pos_frac >= neg_frac else -1
# full-sample sign is positive (Sharpe 0.4394); "same-sign" pass requires >=4/5 years matching
# that positive full-sample sign (identical bar to SMV2T/SMV2W: >=0.8 dominant-frac, dominant
# direction must be the challenger-favoring / here full-sample-matching direction)
loyo_same_sign_pass = bool(dominant_sign > 0 and dominant_frac >= 0.8)

loyo.to_csv(os.path.join(OUT, "gate_B_loyo.csv"), index=False)
print(loyo.round(4).to_string(index=False))
print(f"\nLOYO years: {n_years}  pos-sign frac: {pos_frac:.3f}  neg-sign frac: {neg_frac:.3f}  "
      f"pass(>=4/5 positive): {loyo_same_sign_pass}", flush=True)

# ---------------- fit 2022-24 -> eval 2025-26 (partial, dev truncation Jan-May 2026) ----------------
fit = curves[curves["year"].isin([2022, 2023, 2024])]
ev = curves[curves["year"].isin([2025, 2026])]

def window_stats(g, label):
    shp = sharpe(g["net_1m_rescaled"])
    return {"window": label, "n_days": len(g), "net": float(g["net_1m_rescaled"].sum()), "sharpe": shp}

fit_stats = window_stats(fit, "fit_2022_2024")
eval_stats = window_stats(ev, "eval_2025_2026")
eval_point_positive_sharpe = bool(eval_stats["sharpe"] > 0)
eval_point_positive_net = bool(eval_stats["net"] > 0)
fit_eval_pass = eval_point_positive_sharpe

fe = pd.DataFrame([fit_stats, eval_stats])
fe.to_csv(os.path.join(OUT, "gate_B_fit_eval.csv"), index=False)
print("\n" + fe.round(4).to_string(index=False), flush=True)

gateB_pass = bool(loyo_same_sign_pass and fit_eval_pass)

summary = pd.DataFrame([{
    "loyo_years": n_years, "loyo_pos_sign_frac": pos_frac, "loyo_neg_sign_frac": neg_frac,
    "loyo_same_sign_pass_ge_4of5": loyo_same_sign_pass,
    "fit_window": "2022-2024", "eval_window": "2025-2026 (Jan-May, dev truncation)",
    "eval_sharpe": eval_stats["sharpe"], "eval_net": eval_stats["net"],
    "eval_point_positive_sharpe": eval_point_positive_sharpe,
    "eval_point_positive_net": eval_point_positive_net,
    "fit_eval_pass_on_sharpe": fit_eval_pass,
    "gateB_pass": gateB_pass,
}])
summary.to_csv(os.path.join(OUT, "gate_B_summary.csv"), index=False)
print("\n" + summary.to_string(index=False), flush=True)

json.dump({"gateB_pass": gateB_pass, "loyo_same_sign_pass": loyo_same_sign_pass,
           "fit_eval_pass": fit_eval_pass, "loyo_pos_sign_frac": pos_frac,
           "eval_sharpe": eval_stats["sharpe"], "eval_net": eval_stats["net"]},
          open(os.path.join(OUT, "gate_B_verdict.json"), "w"), indent=2)
print("\ndone gate B")
