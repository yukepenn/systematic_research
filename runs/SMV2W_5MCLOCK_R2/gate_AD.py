"""SMV2W_5MCLOCK_R2 -- Gate A (dev paired moving-block bootstrap) + Gate D (right-tail
retention), on the DUAL-transformed legs (out/curves.csv: DUAL_ALL=3m incumbent,
DUAL_5M=5m challenger), built in step1_dual_htf.py.

Template reused verbatim from runs/SMV2T_NOFAST_R2/gate_AD.py (same bootstrap
construction, same battery/path_stats functions) -- only the challenger object and
Gate D's pass threshold change (this spec: right-tail retention >= 0.90, NOT SMV2T's
>= 1.00 -- per SMV2W spec.yaml D_right_tail).

Bootstrap: house convention -- paired moving-block, block=5, B=10000, seed=20260808,
circular index construction.
"""
import os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
RUN = os.path.join(ROOT, "runs", "SMV2W_5MCLOCK_R2")
OUT = os.path.join(RUN, "out")
SEED, BLOCK, NBOOT = 20260808, 5, 10000

curves = pd.read_csv(os.path.join(OUT, "curves.csv"), parse_dates=["sess"])
cal = curves["sess"]
x_all = curves["DUAL_ALL"].to_numpy()
x_5m = curves["DUAL_5M"].to_numpy()
n = len(x_all)
assert n == 1139, f"unexpected dev session count {n}"

# ---------------- Gate A: paired moving-block bootstrap ----------------
def battery(x):
    eqd = np.cumsum(x); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(x)))
    sd_ = x.std(ddof=1)
    return {"n_days": len(x), "net": x.sum(),
            "sharpe": x.mean() / sd_ * np.sqrt(252) if sd_ > 0 else np.nan,
            "maxDD_eod": dd.max(), "CDaR5": np.sort(dd)[::-1][:k].mean(), "k_worst_days": k}

st_all, st_5m = battery(x_all), battery(x_5m)
k5 = st_all["k_worst_days"]

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

shp_all, cdr_all = path_stats(x_all, idx)
shp_5m, cdr_5m = path_stats(x_5m, idx)
d_shp = shp_5m - shp_all          # statistic_1: delta_Sharpe = Sharpe(5M) - Sharpe(ALL)
d_cdr = cdr_all - cdr_5m          # statistic_2: delta_CDaR = CDaR(ALL) - CDaR(5M), + = challenger better

P_dSharpe_gt0 = float((d_shp > 0).mean())
P_dCDaR_gt0 = float((d_cdr > 0).mean())
gateA_pass = bool(P_dSharpe_gt0 >= 0.85 and P_dCDaR_gt0 >= 0.85)

gate_a = pd.DataFrame([{
    "leg_challenger": "DUAL_5M (5m clock, 13-member, VolPeriod=276 time-matched)",
    "leg_reference": "DUAL_ALL (3m incumbent clock, 13-member, VolPeriod=460)",
    "n_days": n, "k_worst_days": int(k5), "block": BLOCK, "n_boot": NBOOT, "seed": SEED,
    "sharpe_ALL": st_all["sharpe"], "sharpe_5M": st_5m["sharpe"],
    "point_delta_sharpe": st_5m["sharpe"] - st_all["sharpe"],
    "CDaR5_ALL": st_all["CDaR5"], "CDaR5_5M": st_5m["CDaR5"],
    "point_delta_CDaR": st_all["CDaR5"] - st_5m["CDaR5"],
    "P_dSharpe_gt0": P_dSharpe_gt0, "P_dCDaR_gt0": P_dCDaR_gt0,
    "dSharpe_q05": np.quantile(d_shp, 0.05), "dSharpe_q50": np.quantile(d_shp, 0.50),
    "dSharpe_q95": np.quantile(d_shp, 0.95),
    "dCDaR_q05": np.quantile(d_cdr, 0.05), "dCDaR_q50": np.quantile(d_cdr, 0.50),
    "dCDaR_q95": np.quantile(d_cdr, 0.95),
    "pass_P_dSharpe_ge_085": bool(P_dSharpe_gt0 >= 0.85),
    "pass_P_dCDaR_ge_085": bool(P_dCDaR_gt0 >= 0.85),
    "gateA_pass": gateA_pass,
    "net_ALL": st_all["net"], "net_5M": st_5m["net"],
}])
gate_a.to_csv(os.path.join(OUT, "gate_A.csv"), index=False)
print(gate_a.to_string(index=False), flush=True)

# ---------------- Gate D: right-tail retention on DUAL-transformed dev legs (bar >= 0.90) ----------------
base = pd.Series(x_all, index=cal)
chal = pd.Series(x_5m, index=cal)
top10 = base.nlargest(10)
on_base_days = float(chal.reindex(top10.index).sum())
retention = on_base_days / float(top10.sum())
own_top10 = chal.nlargest(10)
overlap = len(set(top10.index) & set(own_top10.index))

gate_d = pd.DataFrame([{
    "kind": "SUMMARY", "top10_ALL_sum": float(top10.sum()),
    "FIVEM_pnl_on_ALL_top10_days": on_base_days,
    "retention_ALL_top10": retention,
    "FIVEM_own_top10_sum": float(own_top10.sum()),
    "overlap_days": overlap,
    "pass_retention_ge_0.90": bool(retention >= 0.90),
}])
detail_rows = [{"date": d.date(), "ALL_pnl": float(base.loc[d]), "FIVEM_pnl": float(chal.loc[d])}
               for d in top10.index]
gate_d_detail = pd.DataFrame(detail_rows)
gate_d.to_csv(os.path.join(OUT, "gate_D.csv"), index=False)
gate_d_detail.to_csv(os.path.join(OUT, "gate_D_top10_detail.csv"), index=False)
print(gate_d.to_string(index=False), flush=True)

json.dump({
    "gateA_pass": gateA_pass, "gateD_pass": bool(retention >= 0.90),
    "n_dev_days": n,
}, open(os.path.join(OUT, "gate_AD_summary.json"), "w"), indent=2)
print("\ndone gate A/D", flush=True)
