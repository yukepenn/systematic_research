"""SMV2AJ_ATR_BLEND_R2 -- Gate A: paired moving-block bootstrap (block=5 daily,
B=10000, seed=20260808) on daily diffs of the DUAL-transformed legs
(DUAL_BLEND75 - DUAL_CONTROL), identical construction to
runs/SMV2T_NOFAST_R2/gate_AD.py's path_stats(). Also reports Newey-West
(lag=5, Bartlett) t-stat on the diff series as a house-convention disclosure
statistic (runs/SMV2AF_1MIN_RESCALE_R2/src/gate_A.py's nw_stats(), verbatim).

Bar: P(dSharpe>0) >= 0.85 AND P(dCDaR_0.95>0) >= 0.85.
"""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2AJ_ATR_BLEND_R2")
OUT = os.path.join(RUN, "out")
SEED, BLOCK, NBOOT = 20260808, 5, 10000

curves = pd.read_csv(os.path.join(OUT, "curves.csv"))
x_control = curves["DUAL_CONTROL"].to_numpy()
x_blend75 = curves["DUAL_BLEND75"].to_numpy()
n = len(x_control)


def battery(x):
    eqd = np.cumsum(x); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(x)))
    sd_ = x.std(ddof=1)
    return {"n_days": len(x), "net": x.sum(),
            "sharpe": x.mean() / sd_ * np.sqrt(252) if sd_ > 0 else np.nan,
            "maxDD_eod": dd.max(), "CDaR5": np.sort(dd)[::-1][:k].mean(), "k_worst_days": k}


st_control, st_blend75 = battery(x_control), battery(x_blend75)
k5 = st_control["k_worst_days"]

rng = np.random.default_rng(SEED)
nb = int(np.ceil(n / BLOCK))
starts = rng.integers(0, n, size=(NBOOT, nb))
idx = ((starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % n).reshape(NBOOT, -1)[:, :n]


def path_stats(x, idx, chunk=2000):
    shp = np.empty(len(idx)); cdr = np.empty(len(idx))
    for i in range(0, len(idx), chunk):
        X = x[idx[i:i + chunk]]
        mu = X.mean(axis=1); sd_ = X.std(axis=1, ddof=1)
        shp[i:i + chunk] = mu / sd_ * np.sqrt(252)
        eq = np.cumsum(X, axis=1)
        dd = np.maximum.accumulate(eq, axis=1) - eq
        cdr[i:i + chunk] = (-np.partition(-dd, k5 - 1, axis=1)[:, :k5]).mean(axis=1)
    return shp, cdr


shp_control, cdr_control = path_stats(x_control, idx)
shp_blend75, cdr_blend75 = path_stats(x_blend75, idx)
d_shp = shp_blend75 - shp_control          # delta_Sharpe = Sharpe(BLEND75) - Sharpe(CONTROL)
d_cdr = cdr_control - cdr_blend75          # delta_CDaR = CDaR(CONTROL) - CDaR(BLEND75), + = challenger better

P_dSharpe_gt0 = float((d_shp > 0).mean())
P_dCDaR_gt0 = float((d_cdr > 0).mean())
gateA_pass = bool(P_dSharpe_gt0 >= 0.85 and P_dCDaR_gt0 >= 0.85)


def nw_stats(x, lag=5):
    x = np.asarray(x, dtype=float); n_ = len(x)
    xbar = x.mean()
    z = x - xbar
    S0 = float((z ** 2).sum())
    Snw = S0
    L = min(lag, n_ - 1)
    for l in range(1, L + 1):
        w = 1.0 - l / (lag + 1.0)
        Snw += 2.0 * w * float((z[l:] * z[:-l]).sum())
    t_nw = xbar / (np.sqrt(Snw) / n_) if Snw > 0 else np.nan
    sd = x.std(ddof=1)
    t_iid = xbar / (sd / np.sqrt(n_)) if sd > 0 else np.nan
    return {"mean": xbar, "t_nw_lag5": t_nw, "t_iid": t_iid, "n": n_}


diff = x_blend75 - x_control
nw = nw_stats(diff, lag=5)

gate_a = pd.DataFrame([{
    "leg_challenger": "DUAL_BLEND75 (ATR-blended w=0.75 core, DUAL-transformed)",
    "leg_reference": "DUAL_CONTROL (sigma460-only incumbent, DUAL-transformed)",
    "n_days": n, "k_worst_days": int(k5), "block": BLOCK, "n_boot": NBOOT, "seed": SEED,
    "sharpe_CONTROL": st_control["sharpe"], "sharpe_BLEND75": st_blend75["sharpe"],
    "point_delta_sharpe": st_blend75["sharpe"] - st_control["sharpe"],
    "CDaR5_CONTROL": st_control["CDaR5"], "CDaR5_BLEND75": st_blend75["CDaR5"],
    "point_delta_CDaR": st_control["CDaR5"] - st_blend75["CDaR5"],
    "P_dSharpe_gt0": P_dSharpe_gt0, "P_dCDaR_gt0": P_dCDaR_gt0,
    "dSharpe_q05": np.quantile(d_shp, 0.05), "dSharpe_q50": np.quantile(d_shp, 0.50),
    "dSharpe_q95": np.quantile(d_shp, 0.95),
    "dCDaR_q05": np.quantile(d_cdr, 0.05), "dCDaR_q50": np.quantile(d_cdr, 0.50),
    "dCDaR_q95": np.quantile(d_cdr, 0.95),
    "pass_P_dSharpe_ge_085": bool(P_dSharpe_gt0 >= 0.85),
    "pass_P_dCDaR_ge_085": bool(P_dCDaR_gt0 >= 0.85),
    "gateA_pass": gateA_pass,
    "net_CONTROL": st_control["net"], "net_BLEND75": st_blend75["net"],
    "nw_lag5_mean_daily_diff_$": nw["mean"], "nw_lag5_t_stat": nw["t_nw_lag5"],
    "iid_t_stat_diff": nw["t_iid"],
}])
gate_a.to_csv(os.path.join(OUT, "gate_A.csv"), index=False)
print(gate_a.to_string(index=False), flush=True)

json.dump({"gateA_pass": gateA_pass, "P_dSharpe_gt0": P_dSharpe_gt0, "P_dCDaR_gt0": P_dCDaR_gt0,
           "nw_lag5_t_stat": float(nw["t_nw_lag5"])},
          open(os.path.join(OUT, "gate_A_summary.json"), "w"), indent=2)
print("\ndone gate A", flush=True)
