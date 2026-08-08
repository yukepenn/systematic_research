"""SMV2T_NOFAST_R2 — Gate A (dev paired moving-block bootstrap) + Gate D (right-tail
retention), on the DUAL-transformed legs.

DUAL_HTF transform applied EXACTLY as runs/SMV2H_ONECONTRACT/smv2h.py / rerank.py /
runs/SMV2H2_ONELOT_CONFIRM/confirm_gate_a.py build it (tilt x1.25 on HTF agreement,
c1_50 short-halving iff HTF-up, x0.9026, clip +-13, round-half-away-from-zero):
    agree = sign(T)!=0 & st_bar==sign(T)
    m = 1.25 if agree else 1.0
    s = 0.5 if (T<0 and st_bar>0) else 1.0
    Tpp = clip(rha(T * m * s * 0.9026), -13, 13)
applied to BOTH the ALL (13-member, incumbent) core and the no-FAST (9-member) core,
each already clip(+-10)-capped by e10_target (sm01_solarsim.e10_target, cap=10, mult=10).

Both DUAL legs are then run through the SAME MNQ E10 executor (common_exec.e10_exec,
verified engine, verbatim semantics) -- i.e. the DUAL-transformed value IS the target
position each bar (multi-lot, up to +-13 MNQ), not a one-lot hysteresis policy.

Bootstrap: house convention -- paired moving-block, block=5, B=10000, seed=20260808,
circular index construction (identical to confirm_gate_a.py's path_stats).
"""
import sys, os, json
import datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "SMV2R_SOLAR_CORE_1"))
import sm01_solarsim as sm
from common_exec import e10_exec

RUN = os.path.join(ROOT, "runs", "SMV2T_NOFAST_R2")
OUT = os.path.join(RUN, "out")
DEV_END = dt.date(2026, 5, 31)
SEED, BLOCK, NBOOT = 20260808, 5, 10000

def rha(x):
    return np.sign(x) * np.floor(np.abs(x) + 0.5)

# ---------------- substrate ----------------
bars = sm.load_bars_3m(os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"))
bars = bars[bars["sess_date"] <= DEV_END].reset_index(drop=True)

cache = np.load(os.path.join(OUT, "cache_dev_cores.npz"))
T_all = cache["tgt_all"].astype(float)
T_nofast = cache["tgt_nofast"].astype(float)

# HTF: prior-session close vs SMA50 of session closes (verbatim smv2h.py/confirm_gate_a.py)
sclose = bars.loc[bars["is_last_of_sess"], ["sess_date", "close"]].set_index("sess_date")["close"]
htf = np.sign(sclose - sclose.rolling(50).mean()).shift(1).to_dict()
st_bar = np.array([htf.get(d, np.nan) for d in bars["sess_date"]])

def dual_htf(T, st_bar):
    agree = (np.sign(T) != 0) & (st_bar == np.sign(T))
    m = np.where(agree, 1.25, 1.0)
    s = np.where((T < 0) & (st_bar > 0), 0.5, 1.0)
    return np.clip(rha(T * m * s * 0.9026), -13, 13)

Tpp_all = dual_htf(T_all, st_bar)
Tpp_nofast = dual_htf(T_nofast, st_bar)

# ---------------- integrity check: Tpp_all must equal SMV2H2 gate A's saved T-dd ----------------
tdd_ref_path = os.path.join(ROOT, "runs", "SMV2H2_ONELOT_CONFIRM", "out", "tdd_dev_from_tgt.npy")
tdd_ref = np.load(tdd_ref_path)
tpp_all_match = bool((Tpp_all == tdd_ref).all())
print("Tpp_all matches SMV2H2 gate-A saved T-dd on all dev bars:", tpp_all_match, flush=True)

# ---------------- execute both DUAL legs through the same MNQ E10 executor ----------------
daily_all, _, _ = e10_exec(bars, Tpp_all.astype(int))
daily_nofast, _, _ = e10_exec(bars, Tpp_nofast.astype(int))

# cross-check DUAL_all against rerank.py's saved solar_dual_htf_daily.csv (incumbent DUAL leg)
ref_dual = pd.read_csv(os.path.join(ROOT, "runs", "SMV2H_ONECONTRACT", "out",
                                     "solar_dual_htf_daily.csv"))
ref_dual.columns = ["sess", "net"]
ref_dual["sess"] = pd.to_datetime(ref_dual["sess"]).dt.date
da = daily_all.copy(); da["sess"] = pd.to_datetime(da["sess"]).dt.date
j = ref_dual.merge(da, on="sess", suffixes=("_ref", "_my"))
dual_all_max_dev = float(np.abs(j["net_ref"] - j["net_my"]).max())
print("DUAL_all dev daily max |dev| vs rerank.py solar_dual_htf_daily.csv:", dual_all_max_dev, flush=True)

assert (daily_all["sess"] == daily_nofast["sess"]).all(), "calendar mismatch between legs"
cal = pd.to_datetime(daily_all["sess"])
x_all = daily_all["net"].to_numpy()
x_nofast = daily_nofast["net"].to_numpy()
n = len(x_all)

curves = pd.DataFrame({
    "sess": daily_all["sess"], "DUAL_ALL": x_all, "DUAL_NOFAST": x_nofast,
    "diff_nofast_minus_all": x_nofast - x_all,
})
curves.to_csv(os.path.join(OUT, "curves.csv"), index=False)

# ---------------- Gate A: paired moving-block bootstrap ----------------
def battery(x):
    eqd = np.cumsum(x); pk = np.maximum.accumulate(eqd); dd = pk - eqd
    k = max(1, int(0.05 * len(x)))
    sd_ = x.std(ddof=1)
    return {"n_days": len(x), "net": x.sum(),
            "sharpe": x.mean() / sd_ * np.sqrt(252) if sd_ > 0 else np.nan,
            "maxDD_eod": dd.max(), "CDaR5": np.sort(dd)[::-1][:k].mean(), "k_worst_days": k}

st_all, st_nofast = battery(x_all), battery(x_nofast)
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
shp_nofast, cdr_nofast = path_stats(x_nofast, idx)
d_shp = shp_nofast - shp_all          # statistic_1: delta_Sharpe = Sharpe(noFAST) - Sharpe(ALL)
d_cdr = cdr_all - cdr_nofast          # statistic_2: delta_CDaR = CDaR(ALL) - CDaR(noFAST), + = challenger better

P_dSharpe_gt0 = float((d_shp > 0).mean())
P_dCDaR_gt0 = float((d_cdr > 0).mean())
gateA_pass = bool(P_dSharpe_gt0 >= 0.85 and P_dCDaR_gt0 >= 0.85)

gate_a = pd.DataFrame([{
    "leg_challenger": "DUAL_NOFAST (9-member, no vm6-12)", "leg_reference": "DUAL_ALL (13-member incumbent)",
    "n_days": n, "k_worst_days": int(k5), "block": BLOCK, "n_boot": NBOOT, "seed": SEED,
    "sharpe_ALL": st_all["sharpe"], "sharpe_NOFAST": st_nofast["sharpe"],
    "point_delta_sharpe": st_nofast["sharpe"] - st_all["sharpe"],
    "CDaR5_ALL": st_all["CDaR5"], "CDaR5_NOFAST": st_nofast["CDaR5"],
    "point_delta_CDaR": st_all["CDaR5"] - st_nofast["CDaR5"],
    "P_dSharpe_gt0": P_dSharpe_gt0, "P_dCDaR_gt0": P_dCDaR_gt0,
    "dSharpe_q05": np.quantile(d_shp, 0.05), "dSharpe_q50": np.quantile(d_shp, 0.50),
    "dSharpe_q95": np.quantile(d_shp, 0.95),
    "dCDaR_q05": np.quantile(d_cdr, 0.05), "dCDaR_q50": np.quantile(d_cdr, 0.50),
    "dCDaR_q95": np.quantile(d_cdr, 0.95),
    "pass_P_dSharpe_ge_085": bool(P_dSharpe_gt0 >= 0.85),
    "pass_P_dCDaR_ge_085": bool(P_dCDaR_gt0 >= 0.85),
    "gateA_pass": gateA_pass,
    "net_ALL": st_all["net"], "net_NOFAST": st_nofast["net"],
    "tpp_all_matches_smv2h2_tdd": tpp_all_match,
    "dual_all_max_abs_dev_vs_rerank_$": dual_all_max_dev,
}])
gate_a.to_csv(os.path.join(OUT, "gate_A.csv"), index=False)
print(gate_a.to_string(index=False), flush=True)

# ---------------- Gate D: right-tail retention on DUAL-transformed dev legs ----------------
base = pd.Series(x_all, index=cal)
chal = pd.Series(x_nofast, index=cal)
top10 = base.nlargest(10)
on_base_days = float(chal.reindex(top10.index).sum())
retention = on_base_days / float(top10.sum())
own_top10 = chal.nlargest(10)
overlap = len(set(top10.index) & set(own_top10.index))

gate_d = pd.DataFrame([{
    "kind": "SUMMARY", "top10_ALL_sum": float(top10.sum()),
    "NOFAST_pnl_on_ALL_top10_days": on_base_days,
    "retention_ALL_top10": retention,
    "NOFAST_own_top10_sum": float(own_top10.sum()),
    "overlap_days": overlap,
    "pass_retention_ge_1.00": bool(retention >= 1.00),
}])
detail_rows = [{"date": d.date(), "ALL_pnl": float(base.loc[d]), "NOFAST_pnl": float(chal.loc[d])}
               for d in top10.index]
gate_d_detail = pd.DataFrame(detail_rows)
gate_d.to_csv(os.path.join(OUT, "gate_D.csv"), index=False)
gate_d_detail.to_csv(os.path.join(OUT, "gate_D_top10_detail.csv"), index=False)
print(gate_d.to_string(index=False), flush=True)

json.dump({
    "gateA_pass": gateA_pass, "gateD_pass": bool(retention >= 1.00),
    "tpp_all_matches_smv2h2_tdd": tpp_all_match,
    "dual_all_max_abs_dev_vs_rerank_$": dual_all_max_dev,
    "n_dev_days": n,
}, open(os.path.join(OUT, "gate_AD_summary.json"), "w"), indent=2)

np.save(os.path.join(OUT, "tpp_all_dev.npy"), Tpp_all)
np.save(os.path.join(OUT, "tpp_nofast_dev.npy"), Tpp_nofast)
print("done gate A/D", flush=True)
