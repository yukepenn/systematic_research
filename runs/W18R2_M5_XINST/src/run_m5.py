"""W18R2_M5_XINST — ATR-blend (w = 0.75, FROZEN) cross-instrument replication.

RUN ONCE. No weight search anywhere in this file. Per the frozen spec, ES/RTY/YM are
MECHANISM-REPLICATION SAMPLES ONLY (C2) and nothing here proposes trading them.
"""
import os, sys, json, datetime as dt
import numpy as np, pandas as pd

ROOT = r"D:\OneDrive - Washington University in St. Louis\TradingResearch\systematic_research"
sys.path.insert(0, os.path.join(ROOT, "src", "analytics"))
sys.path.insert(0, os.path.join(ROOT, "runs", "W18R1_M1_VOLSEASON", "src"))
import sm01_solarsim as sm
from smv2_common import dd_battery
import common as C1                      # reuse the validated e10_exec / build_pend helpers

RUN = os.path.join(ROOT, "runs", "W18R2_M5_XINST")
OUT = os.path.join(RUN, "out")
os.makedirs(OUT, exist_ok=True)
DEV_END = dt.date(2026, 5, 29)
W = 0.75                                  # FROZEN. Never varied in this run.
SEED, BLOCK, NBOOT = 20260808, 5, 10000
COMM_SIDE = 2.18                          # stated assumption, applied identically to both arms

INST = {
    #        path,                                        tick,  point_value
    "NQ":  (os.path.join(ROOT, "runs", "AUDIT03_BARS", "nq_3m_2022_2026.csv"), 0.25, 20.0),
    "ES":  (os.path.join(ROOT, "runs", "W18_XINST_BARS", "es_3m_2022_2026.csv"), 0.25, 50.0),
    "RTY": (os.path.join(ROOT, "runs", "W18_XINST_BARS", "rty_3m_2022_2026.csv"), 0.10, 50.0),
    "YM":  (os.path.join(ROOT, "runs", "W18_XINST_BARS", "ym_3m_2022_2026.csv"), 1.00, 5.00),
}
NEW_INSTRUMENTS = ["ES", "RTY", "YM"]      # NQ is the KNOWN cell, excluded from the sign count


def atr_series(bars, vol_period=460, min_count=30):
    """Verbatim runs/SMV2AI_ATR_BLEND/src/common.py atr_series()."""
    high = bars["high"].to_numpy(); low = bars["low"].to_numpy(); close = bars["close"].to_numpy()
    n = close.size
    prev_close = np.empty(n); prev_close[0] = close[0]; prev_close[1:] = close[:-1]
    tr = np.maximum(high - low, np.maximum(np.abs(high - prev_close), np.abs(low - prev_close)))
    tr[0] = high[0] - low[0]
    csum = np.cumsum(tr); t = np.arange(n)
    with np.errstate(invalid="ignore", divide="ignore"):
        exp_mean = csum / np.where(t.astype(float) > 0, t.astype(float), np.nan)
    roll = np.full(n, np.nan)
    if n > vol_period:
        roll[vol_period:] = (csum[vol_period:] - csum[:-vol_period]) / vol_period
    atr = np.where(t <= vol_period, exp_mean, roll)
    atr[t < min_count] = np.nan
    return atr


def battery(x):
    eqd = np.cumsum(x); dd = np.maximum.accumulate(eqd) - eqd
    k = max(1, int(0.05 * len(x)))
    sd = x.std(ddof=1)
    return {"n_days": len(x), "net": float(x.sum()),
            "sharpe": float(x.mean() / sd * np.sqrt(252)) if sd > 0 else np.nan,
            "maxDD": float(dd.max()),
            "CDaR_0.95": float(np.sort(dd)[::-1][:k].mean()), "k": k}


def path_stats(x, idx, k5, chunk=2000):
    """Verbatim runs/SMV2AJ_ATR_BLEND_R2/src/gate_A.py path_stats()."""
    shp = np.empty(len(idx)); cdr = np.empty(len(idx))
    for i in range(0, len(idx), chunk):
        X = x[idx[i:i + chunk]]
        mu = X.mean(axis=1); sd = X.std(axis=1, ddof=1)
        shp[i:i + chunk] = mu / sd * np.sqrt(252)
        eq = np.cumsum(X, axis=1)
        dd = np.maximum.accumulate(eq, axis=1) - eq
        cdr[i:i + chunk] = (-np.partition(-dd, k5 - 1, axis=1)[:, :k5]).mean(axis=1)
    return shp, cdr


# ------------------------------------------------------------------ substrate gate
sub = []
nq_bars = sm.load_bars_3m(INST["NQ"][0]); nq_bars = nq_bars[nq_bars["sess_date"] <= DEV_END]
nq_sess = set(nq_bars["sess_date"])
BARS = {}
for name, (path, tick, pv) in INST.items():
    b = sm.load_bars_3m(path)
    b = b[b["sess_date"] <= DEV_END].reset_index(drop=True)
    common_sess = len(set(b["sess_date"]) & nq_sess)
    row = {"instrument": name, "n_bars": len(b), "n_sessions": b["sess_date"].nunique(),
           "bar_ratio_vs_NQ": len(b) / len(nq_bars),
           "session_coverage_vs_NQ": common_sess / len(nq_sess),
           "monotone": bool(b["time"].is_monotonic_increasing),
           "dup_timestamps": int(b["time"].duplicated().sum()),
           "first": str(b["time"].min()), "last": str(b["time"].max())}
    row["PASS"] = bool(row["monotone"] and row["dup_timestamps"] == 0
                       and abs(row["bar_ratio_vs_NQ"] - 1) <= 0.15
                       and row["session_coverage_vs_NQ"] >= 0.95)
    sub.append(row)
    BARS[name] = b
sub = pd.DataFrame(sub)
sub.to_csv(os.path.join(OUT, "substrate_check.csv"), index=False)
print("=== SUBSTRATE GATE (applied BEFORE any P&L) ===")
print(sub.to_string(index=False), flush=True)
EXCLUDED = [r["instrument"] for _, r in sub.iterrows() if not r["PASS"]]
USE = [k for k in INST if k not in EXCLUDED]
print(f"excluded by name: {EXCLUDED or 'none'}   using: {USE}", flush=True)

# ------------------------------------------------------------------ per instrument
rows, curves, Rs = [], {}, {}
for name in USE:
    path, tick, pv = INST[name]
    b = BARS[name]
    close = b["close"].to_numpy()
    sig460 = sm.sigma_series(close)
    atr = atr_series(b)
    ok = np.isfinite(sig460) & np.isfinite(atr) & (sig460 > 0)
    R = float(np.median(atr[ok] / sig460[ok]))          # whole-dev MEDIAN, per instrument
    Rs[name] = R
    sig_atr_eff = atr / R
    blend = W * sig460 + (1.0 - W) * sig_atr_eff

    old_tick = sm.TICK
    sm.TICK = tick                                      # scales clamp, fallback and slippage
    try:
        for arm, sig in (("CONTROL", sig460), ("BLEND75", blend)):
            PEND = C1.build_pend(b, sig)
            tgt = sm.e10_target(PEND)
            daily, _, _ = C1.e10_exec(b, tgt, comm_side=COMM_SIDE, point_value=pv)
            daily0, _, _ = C1.e10_exec(b, tgt, comm_side=0.0, point_value=pv)
            curves[(name, arm)] = daily.set_index(daily["sess"].astype(str))["net"]
            curves[(name, arm, "nocomm")] = daily0.set_index(daily0["sess"].astype(str))["net"]
            st = battery(daily["net"].to_numpy())
            rows.append({"instrument": name, "arm": arm, "tick": tick, "point_value": pv,
                         "R_atr_over_sigma": R, "flip_free_turnover_pct":
                             float((np.diff(tgt) != 0).mean() * 100), **st})
            print(f"  {name:4s} {arm:8s} net {st['net']:>14,.0f}  sharpe {st['sharpe']:.4f}  "
                  f"CDaR {st['CDaR_0.95']:>12,.0f}", flush=True)
    finally:
        sm.TICK = old_tick
per_arm = pd.DataFrame(rows)
per_arm.to_csv(os.path.join(OUT, "per_arm_raw.csv"), index=False)
json.dump(Rs, open(os.path.join(OUT, "R_per_instrument.json"), "w"), indent=2)

# ------------------------------------------------------------------ paired stats
rng = np.random.default_rng(SEED)
res, diffs = [], {}
for name in USE:
    c = curves[(name, "CONTROL")]; t = curves[(name, "BLEND75")]
    cal = c.index.intersection(t.index)
    xc, xt = c.reindex(cal).to_numpy(), t.reindex(cal).to_numpy()
    diffs[name] = pd.Series(xt - xc, index=cal)
    bc, bt = battery(xc), battery(xt)
    k5 = bc["k"]
    n = len(xc); nb = int(np.ceil(n / BLOCK))
    r2 = np.random.default_rng(SEED)
    starts = r2.integers(0, n, size=(NBOOT, nb))
    idx = ((starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % n).reshape(NBOOT, -1)[:, :n]
    sc, dc = path_stats(xc, idx, k5)
    st_, dt_ = path_stats(xt, idx, k5)
    d_sh = st_ - sc
    d_cdr_ratio = (dc - dt_) / dc
    # zero-commission sensitivity (sign only)
    xc0 = curves[(name, "CONTROL", "nocomm")].reindex(cal).to_numpy()
    xt0 = curves[(name, "BLEND75", "nocomm")].reindex(cal).to_numpy()
    b0c, b0t = battery(xc0), battery(xt0)
    res.append({
        "instrument": name, "role": "KNOWN" if name == "NQ" else "NEW",
        "n_days": n,
        "sharpe_CONTROL": bc["sharpe"], "sharpe_BLEND75": bt["sharpe"],
        "dSharpe": bt["sharpe"] - bc["sharpe"],
        "CDaR_CONTROL": bc["CDaR_0.95"], "CDaR_BLEND75": bt["CDaR_0.95"],
        "dCDaR_ratio": (bc["CDaR_0.95"] - bt["CDaR_0.95"]) / bc["CDaR_0.95"],
        "P_dSharpe_gt0": float((d_sh > 0).mean()),
        "P_dCDaR_ratio_gt0": float((d_cdr_ratio > 0).mean()),
        "net_CONTROL": bc["net"], "net_BLEND75": bt["net"],
        "sign_agreement": bool((bt["sharpe"] - bc["sharpe"]) > 0
                               and (bc["CDaR_0.95"] - bt["CDaR_0.95"]) > 0),
        "nocomm_dSharpe": b0t["sharpe"] - b0c["sharpe"],
        "nocomm_dCDaR_ratio": (b0c["CDaR_0.95"] - b0t["CDaR_0.95"]) / b0c["CDaR_0.95"],
        "nocomm_sign_agreement": bool((b0t["sharpe"] - b0c["sharpe"]) > 0
                                      and (b0c["CDaR_0.95"] - b0t["CDaR_0.95"]) > 0),
    })
per_inst = pd.DataFrame(res)
per_inst.to_csv(os.path.join(OUT, "per_instrument.csv"), index=False)
print("\n=== PER INSTRUMENT ===")
print(per_inst.to_string(index=False), flush=True)

# ------------------------------------------------------------------ dependence
D = pd.DataFrame(diffs).dropna()
corr = D.corr()
corr.to_csv(os.path.join(OUT, "dep_corr.csv"))
Rm = corr.to_numpy(); k = Rm.shape[0]
ESS = float(k ** 2 / Rm.sum())
# raw-P&L correlation, for contrast
raw = pd.DataFrame({nm: curves[(nm, "CONTROL")] for nm in USE}).dropna()
raw_corr = raw.corr()
raw_corr.to_csv(os.path.join(OUT, "dep_corr_raw_pnl.csv"))
ess = {"k_instruments": int(k), "ESS": ESS, "preregistered_disclosure_bar": 2.0,
       "ESS_below_2": bool(ESS < 2.0),
       "mean_offdiag_corr_diff_series": float((Rm.sum() - k) / (k * k - k)),
       "mean_offdiag_corr_raw_pnl": float((raw_corr.to_numpy().sum() - k) / (k * k - k)),
       "n_common_sessions": int(len(D))}
json.dump(ess, open(os.path.join(OUT, "ess.json"), "w"), indent=2)
print("\n=== DEPENDENCE ===\n" + json.dumps(ess, indent=2))
print(corr.to_string(), flush=True)

# ------------------------------------------------------------ pooled joint-date bootstrap
cal = D.index
n = len(cal); nb = int(np.ceil(n / BLOCK))
r3 = np.random.default_rng(SEED)
starts = r3.integers(0, n, size=(NBOOT, nb))
idx = ((starts[:, :, None] + np.arange(BLOCK)[None, None, :]) % n).reshape(NBOOT, -1)[:, :n]
acc_sh, acc_cd = [], []
for name in USE:
    xc = curves[(name, "CONTROL")].reindex(cal).to_numpy()
    xt = curves[(name, "BLEND75")].reindex(cal).to_numpy()
    k5 = max(1, int(0.05 * n))
    sc, dc = path_stats(xc, idx, k5)
    st_, dt_ = path_stats(xt, idx, k5)
    acc_sh.append(st_ - sc)
    acc_cd.append((dc - dt_) / dc)
mean_sh = np.mean(acc_sh, axis=0); mean_cd = np.mean(acc_cd, axis=0)
pooled = {
    "instruments": USE, "n_common_sessions": int(n), "block": BLOCK, "n_boot": NBOOT,
    "seed": SEED,
    "point_mean_dSharpe": float(np.mean([r["dSharpe"] for r in res])),
    "point_mean_dCDaR_ratio": float(np.mean([r["dCDaR_ratio"] for r in res])),
    "P_mean_dSharpe_gt0": float((mean_sh > 0).mean()),
    "P_mean_dCDaR_ratio_gt0": float((mean_cd > 0).mean()),
    "q05_mean_dSharpe": float(np.quantile(mean_sh, 0.05)),
    "q95_mean_dSharpe": float(np.quantile(mean_sh, 0.95)),
    "q05_mean_dCDaR_ratio": float(np.quantile(mean_cd, 0.05)),
    "q95_mean_dCDaR_ratio": float(np.quantile(mean_cd, 0.95)),
    "bar": 0.85,
}
pooled["POOLED_PASS"] = bool(pooled["P_mean_dSharpe_gt0"] >= 0.85
                             and pooled["P_mean_dCDaR_ratio_gt0"] >= 0.85)
json.dump(pooled, open(os.path.join(OUT, "pooled.json"), "w"), indent=2)
print("\n=== POOLED (joint-date block bootstrap; dependence preserved by construction) ===")
print(json.dumps(pooled, indent=2), flush=True)

# ------------------------------------------------------------------ verdict
new_ok = [r["instrument"] for r in res if r["role"] == "NEW" and r["sign_agreement"]]
sign_pass = len(new_ok) >= 2
if sign_pass and pooled["POOLED_PASS"]:
    v = "REPLICATES"
elif sign_pass or pooled["POOLED_PASS"]:
    v = "PARTIAL"
else:
    v = "FAILS_TO_REPLICATE"
verdict = {"VERDICT": v,
           "new_instruments_with_sign_agreement": new_ok,
           "n_new_sign_agree": len(new_ok), "sign_bar": "2 of 3", "sign_pass": sign_pass,
           "pooled_pass": pooled["POOLED_PASS"], "ESS": ESS,
           "excluded_instruments": EXCLUDED,
           "note": ("PARTIAL is NOT a pass and does not re-queue the R2. "
                    "A REPLICATES verdict re-queues an R2; it does NOT promote anything.")}
json.dump(verdict, open(os.path.join(OUT, "verdict.json"), "w"), indent=2)
pd.DataFrame(curves).to_csv(os.path.join(OUT, "curves_all.csv"))
print("\n=== VERDICT ===\n" + json.dumps(verdict, indent=2), flush=True)
