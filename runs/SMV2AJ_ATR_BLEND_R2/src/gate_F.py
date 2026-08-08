"""SMV2AJ_ATR_BLEND_R2 -- Gate F (NEW, disclosure-only, not pass/fail-gating):
re-run gate A's bootstrap at the two IMMEDIATELY ADJACENT untested blend
weights w=0.70 and w=0.80 (interpolating sig_arm the same way, no new grid
search) on the DUAL-transformed dev legs. Report whether P(dSharpe>0) and
P(dCDaR>0) stay above 0.75 at both neighbors, and disclose explicitly if
w=0.75 is a narrow, non-robust spike between two much worse neighbors.
"""
import sys, os, json
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SMV2AI_ATR_BLEND", "src"))
import sm01_solarsim as sm
from common import (load_dev_bars, build_pend, e10_exec, INCUMBENT_VMS, dual_htf, htf_state)

RUN = os.path.join(ROOT, "runs", "SMV2AJ_ATR_BLEND_R2")
OUT = os.path.join(RUN, "out")
AI_OUT = os.path.join(ROOT, "runs", "SMV2AI_ATR_BLEND", "out")
SEED, BLOCK, NBOOT = 20260808, 5, 10000

bars = load_dev_bars()
sigma460 = np.load(os.path.join(AI_OUT, "sigma460_dev.npy"))
sigma_ATR_eff = np.load(os.path.join(AI_OUT, "sigma_atr_eff_dev.npy"))
st_bar = htf_state(bars)

# ---------------- reuse already-built w=0.75 and w=1.00 (control) DUAL legs ----------------
curves = pd.read_csv(os.path.join(OUT, "curves.csv"))
x_control = curves["DUAL_CONTROL"].to_numpy()
x_075 = curves["DUAL_BLEND75"].to_numpy()
n = len(x_control)


def build_dual_leg(w):
    sig_arm = w * sigma460 + (1.0 - w) * sigma_ATR_eff
    pend = build_pend(bars, sig_arm, INCUMBENT_VMS, smax_ticks=1200.0, smin_ticks=40.0)
    tgt = sm.e10_target(pend)
    Tpp = dual_htf(tgt.astype(float), st_bar)
    daily, _, _ = e10_exec(bars, Tpp.astype(int))
    return daily["net"].to_numpy()


x_070 = build_dual_leg(0.70)
x_080 = build_dual_leg(0.80)


def battery(x):
    eqd = np.cumsum(x); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(x)))
    sd_ = x.std(ddof=1)
    return {"net": x.sum(), "sharpe": x.mean() / sd_ * np.sqrt(252) if sd_ > 0 else np.nan,
            "CDaR5": np.sort(dd)[::-1][:k].mean(), "k_worst_days": k}


st_control = battery(x_control)
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

rows = []
for w, x in [(0.70, x_070), (0.75, x_075), (0.80, x_080)]:
    st = battery(x)
    shp_w, cdr_w = path_stats(x, idx)
    d_shp = shp_w - shp_control
    d_cdr = cdr_control - cdr_w
    P_dSharpe = float((d_shp > 0).mean())
    P_dCDaR = float((d_cdr > 0).mean())
    rows.append({
        "w_sigma460_weight": w, "net": st["net"], "sharpe": st["sharpe"], "CDaR5": st["CDaR5"],
        "point_delta_sharpe_vs_control": st["sharpe"] - st_control["sharpe"],
        "point_delta_CDaR_vs_control": st_control["CDaR5"] - st["CDaR5"],
        "P_dSharpe_gt0": P_dSharpe, "P_dCDaR_gt0": P_dCDaR,
        "pass_soft_bar_075_both": bool(P_dSharpe >= 0.75 and P_dCDaR >= 0.75),
        "is_promotion_candidate_w": bool(w == 0.75),
    })

gate_f = pd.DataFrame(rows)
gate_f.to_csv(os.path.join(OUT, "gate_F_seed_robustness.csv"), index=False)
print(gate_f.to_string(index=False), flush=True)

# ---------------- fragile-spike disclosure check ----------------
r70 = gate_f[gate_f.w_sigma460_weight == 0.70].iloc[0]
r75 = gate_f[gate_f.w_sigma460_weight == 0.75].iloc[0]
r80 = gate_f[gate_f.w_sigma460_weight == 0.80].iloc[0]

neighbors_pass_soft_bar = bool(r70["pass_soft_bar_075_both"] and r80["pass_soft_bar_075_both"])
# "narrow spike between much worse neighbors": w=0.75's point Sharpe/CDaR much better than BOTH
# neighbors AND at least one neighbor fails the soft bar outright (P<0.75 on either prong)
spike_by_bootstrap = bool((not r70["pass_soft_bar_075_both"]) or (not r80["pass_soft_bar_075_both"]))
sharpe_monotone_neighbor_worse = bool(r75["sharpe"] > r70["sharpe"] and r75["sharpe"] > r80["sharpe"])
cdar_monotone_neighbor_worse = bool(r75["CDaR5"] < r70["CDaR5"] and r75["CDaR5"] < r80["CDaR5"])
is_narrow_spike = bool(spike_by_bootstrap or (sharpe_monotone_neighbor_worse and cdar_monotone_neighbor_worse
                                               and spike_by_bootstrap))

summary = {
    "w070_P_dSharpe_gt0": float(r70["P_dSharpe_gt0"]), "w070_P_dCDaR_gt0": float(r70["P_dCDaR_gt0"]),
    "w070_pass_075_bar": bool(r70["pass_soft_bar_075_both"]),
    "w075_P_dSharpe_gt0_from_gateA": None,  # filled from gate_A.csv below
    "w080_P_dSharpe_gt0": float(r80["P_dSharpe_gt0"]), "w080_P_dCDaR_gt0": float(r80["P_dCDaR_gt0"]),
    "w080_pass_075_bar": bool(r80["pass_soft_bar_075_both"]),
    "both_neighbors_pass_075_bar": neighbors_pass_soft_bar,
    "narrow_spike_flag": is_narrow_spike,
}
try:
    ga = pd.read_csv(os.path.join(OUT, "gate_A.csv")).iloc[0]
    summary["w075_P_dSharpe_gt0_from_gateA"] = float(ga["P_dSharpe_gt0"])
    summary["w075_P_dCDaR_gt0_from_gateA"] = float(ga["P_dCDaR_gt0"])
except FileNotFoundError:
    pass

json.dump(summary, open(os.path.join(OUT, "gate_F_summary.json"), "w"), indent=2)
print("\n" + json.dumps(summary, indent=2), flush=True)
print("\ndone gate F", flush=True)
