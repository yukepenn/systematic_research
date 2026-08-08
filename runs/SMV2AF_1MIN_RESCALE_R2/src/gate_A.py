"""SMV2AF_1MIN_RESCALE_R2 -- Gate A: paired moving-block bootstrap (block=5 daily,
B=10000, seed=20260808) on the rescaled arm's OWN daily PnL (single-series bootstrap of
the Sharpe statistic -- NOT a paired diff vs a reference leg, per spec.yaml's exact wording
"on the rescaled arm's own daily PnL"). Circular block-index construction identical to
runs/SMV2T_NOFAST_R2/gate_AD.py's path_stats() (house convention). Also reports Newey-West
(lag=5, Bartlett weights) t-stat on the daily mean per house statistical conventions,
using the identical nw_stats() formula as runs/SMV2K_ENGINE3_S1/smv2k.py.
"""
import os, json
import numpy as np
import pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AF_1MIN_RESCALE_R2")
OUT = os.path.join(RUN, "out")
SEED, BLOCK, NBOOT = 20260808, 5, 10000

curves = pd.read_csv(os.path.join(OUT, "dev_daily_curves.csv"), parse_dates=["sess"])
x = curves["net_1m_rescaled"].to_numpy()
n = len(x)

def sharpe(v):
    sd = v.std(ddof=1)
    return v.mean() / sd * np.sqrt(252) if sd > 0 else np.nan

point_sharpe = sharpe(x)
print(f"point-estimate Sharpe (rescaled arm, full dev {n} days) = {point_sharpe:.4f}")

# ---------------- moving-block circular bootstrap (identical construction to gate_AD.py) ----------------
rng = np.random.default_rng(SEED)
nb = int(np.ceil(n / BLOCK))
starts = rng.integers(0, n, size=(NBOOT, nb))
idx = ((starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % n).reshape(NBOOT, -1)[:, :n]

def path_sharpe(x, idx, chunk=2000):
    shp = np.empty(len(idx))
    for i in range(0, len(idx), chunk):
        X = x[idx[i:i + chunk]]
        mu = X.mean(axis=1); sd_ = X.std(axis=1, ddof=1)
        shp[i:i + chunk] = mu / sd_ * np.sqrt(252)
    return shp

boot_sharpe = path_sharpe(x, idx)
P_sharpe_gt0 = float((boot_sharpe > 0).mean())
q05, q50, q95 = np.quantile(boot_sharpe, [0.05, 0.50, 0.95])

gateA_pass = bool(P_sharpe_gt0 >= 0.85)

# ---------------- Newey-West t-stat (lag=5, Bartlett), house convention, disclosure stat ----------------
def nw_stats(x, lag=5):
    x = np.asarray(x, dtype=float); n = len(x)
    xbar = x.mean()
    z = x - xbar
    S0 = float((z ** 2).sum())
    Snw = S0
    L = min(lag, n - 1)
    for l in range(1, L + 1):
        w = 1.0 - l / (lag + 1.0)
        Snw += 2.0 * w * float((z[l:] * z[:-l]).sum())
    t_nw = xbar / (np.sqrt(Snw) / n) if Snw > 0 else np.nan
    sd = x.std(ddof=1)
    t_iid = xbar / (sd / np.sqrt(n)) if sd > 0 else np.nan
    return {"mean": xbar, "t_nw_lag5": t_nw, "t_iid": t_iid, "n": n}

nw = nw_stats(x, lag=5)

gate_a = pd.DataFrame([{
    "arm": "1m_time_matched_RESCALED_R (SMV2AE seq 419)", "n_days": n,
    "block": BLOCK, "n_boot": NBOOT, "seed": SEED,
    "point_sharpe": point_sharpe,
    "boot_sharpe_q05": q05, "boot_sharpe_q50": q50, "boot_sharpe_q95": q95,
    "P_sharpe_gt0": P_sharpe_gt0, "gate_bar": 0.85,
    "gateA_pass": gateA_pass,
    "nw_lag5_mean_daily_$": nw["mean"], "nw_lag5_t_stat": nw["t_nw_lag5"],
    "iid_t_stat": nw["t_iid"],
}])
gate_a.to_csv(os.path.join(OUT, "gate_A_bootstrap.csv"), index=False)
print(gate_a.to_string(index=False))

json.dump({
    "point_sharpe": point_sharpe, "boot_sharpe_q05": float(q05), "boot_sharpe_q50": float(q50),
    "boot_sharpe_q95": float(q95), "P_sharpe_gt0": P_sharpe_gt0, "gateA_pass": gateA_pass,
    "nw_lag5_t_stat": float(nw["t_nw_lag5"]), "iid_t_stat": float(nw["t_iid"]),
}, open(os.path.join(OUT, "gate_A_summary.json"), "w"), indent=2)
print("\ndone gate A")
